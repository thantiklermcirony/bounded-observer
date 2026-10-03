"""Model-free residual noise and measurement dependence for the 210 DECREASE blocks used by H1.

Stage-1 audit input for H1 (experiments/h1-decrease). Writes, under /tmp/claude-0/stage1/h1/:
  noise_modelfree.csv            one row per block (src, pid, sigma_estimate, ...)
  noise_modelfree_summary.json   pooled statistics, estimator self-check, dependence tests
  replicate_pairs.csv            single-agent series measured more than once (same drug, cell, doses)

No composition law and no Hill form is used to estimate noise. Estimators per block (8x8 = 64 wells):
  W  : tensor-product discrete smoothing spline on the dose-index grid (second-difference penalty
       along each dose axis, separate smoothing parameter per axis = Whittaker / P-spline with a knot
       per dose). Residual = leave-one-out (LOO) prediction error with the smoothing parameters chosen
       by an inner LOO on the other 63 wells only (nested CV, so the held-out well never influences the
       choice). sigma_estimate := this nested-CV RMSE on H1's clipped effect scale.
  T  : isotropic thin-plate smoothing spline on the same grid, same nested-CV protocol.
  I  : 2-D isotonic regression (effect non-decreasing in both doses), no tuning; LOO prediction = midpoint
       of the interval the monotone fit on the other 63 wells allows at the held-out well.
  D  : difference-based estimators (Laplacian pseudo-residual; second differences), no fit at all.
Also: df-corrected in-sample residual SDs for W, T, I; replicate single-agent series across blocks; the
untreated (0,0) control well, whose true effect is 0 by definition of the normalisation.

READ THIS BEFORE USING THE NUMBERS. A cross-validated residual from a flexible fit is NOT a pure noise
estimate. In expectation, LOO MSE = sigma^2 + Var(prediction at the held-out well) + bias^2: it exceeds
the noise variance even when the smoother is unbiased, and any real structure the smoother cannot follow
(sharp sigmoids on a 3-fold grid, hormesis, plate artefacts) is added on top. It is an upper-bound-ish mix
of noise and unexplained structure. The df-corrected in-sample SD removes the first excess but keeps bias.
Difference estimators keep curvature bias. The estimators are calibrated against synthetic truth below.
"""
import json, os, pathlib, itertools
import numpy as np, pandas as pd
import quadprog
from scipy.stats import spearmanr, ttest_1samp, wilcoxon

OUT = pathlib.Path('/tmp/claude-0/stage1/h1'); OUT.mkdir(parents=True, exist_ok=True)
H1DIR = pathlib.Path('/home/user/bounded-observer/experiments/h1-decrease')
DATA_PARENT = '/tmp/claude-0/h1run'          # contains DECREASE/ (github.com/IanevskiAleksandr/DECREASE)
rng = np.random.default_rng(20261003)

# ---- data loading, LEVEL, hill, fit_hill, dial, fit_alpha: H1's own code, unchanged --------------------
_cwd = os.getcwd(); os.chdir(DATA_PARENT)
_ns = {}; exec((H1DIR / 'h1_dial.py').read_text().split('rows = []')[0], _ns)
os.chdir(_cwd)
df, LEVEL, hill, fit_hill, dial = _ns['df'], _ns['LEVEL'], _ns['hill'], _ns['fit_hill'], _ns['dial']
# H1's effect is clipped to [0,1]; keep the unclipped value too (192 file: % viability, often > 100).
df['e_raw'] = np.where(df.src == '192', 1 - df.Response / 100, df.Response / 100)
HB = pd.read_csv(H1DIR / 'h1_blocks.csv', dtype={'src': str})
N = 8; n = N * N
IJ = np.array([(i, j) for i in range(N) for j in range(N)], float)
INTERIOR = np.array([(i > 0 and j > 0) for i in range(N) for j in range(N)])

# ---- linear smoothers H(lambda) = (I + lambda*Omega)^-1, shared by every block (same 8x8 index grid) ----
def d2(m):
    D = np.zeros((m - 2, m))
    for r in range(m - 2): D[r, r:r + 3] = [1, -2, 1]
    return D.T @ D
s, V = np.linalg.eigh(d2(N)); s = np.clip(s, 0, None)
VV = np.kron(V, V)                                   # eigenbasis shared by both axis penalties
LAMS_W = np.logspace(-4, 4, 33)
GRID_W = [(lr, lc) for lr in LAMS_W for lc in LAMS_W]
def hat_whit(lr, lc):
    g = 1.0 / (1.0 + lr * np.kron(s, np.ones(N)) + lc * np.kron(np.ones(N), s))   # row index i = Conc1
    return (VV * g) @ VV.T
H_W = np.stack([hat_whit(lr, lc) for lr, lc in GRID_W])

r = np.sqrt(((IJ[:, None, :] - IJ[None, :, :])**2).sum(-1))
K = np.where(r > 0, r**2 * np.log(np.where(r > 0, r, 1)), 0.0)
T = np.column_stack([np.ones(n), IJ])
Qf, _ = np.linalg.qr(T, mode='complete'); Q2 = Qf[:, 3:]
e_tps, U = np.linalg.eigh(Q2.T @ K @ Q2)
assert e_tps.min() > 0, 'thin-plate kernel not positive on the complement of the affine null space'
QU = Q2 @ U
LAMS_T = np.logspace(-3, 5, 49)
def hat_tps(lam): return np.eye(n) - (QU * (lam / (e_tps + lam))) @ QU.T
H_T = np.stack([hat_tps(l) for l in LAMS_T])

def nested_prep(H):
    d = np.einsum('lkk->lk', H)
    # leverage of well j in the smoother fitted without well k (Sherman-Morrison): G_jj = H_jj + H_jk^2/(1-H_kk)
    Gd = d[:, None, :] + H**2 / (1 - d)[:, :, None]
    return d, Gd
PREP = {'W': (H_W, *nested_prep(H_W)), 'T': (H_T, *nested_prep(H_T))}
OFFDIAG = ~np.eye(n, dtype=bool)

def linear_smoother_cv(y, key):
    """Nested LOO for a family of linear smoothers. Returns dict of estimates and fitted pieces."""
    H, d, Gd = PREP[key]
    u = H @ y                                        # (L, n) fits on all 64 wells
    loo = (y - u) / (1 - d)                          # exact LOO residuals for each lambda
    # fit without well k, all lambda: F[l,k,j] = u[l,j] - H[l,k,j]*loo[l,k]  (rank-one downdate)
    F = u[:, None, :] - H * loo[:, :, None]
    inner = ((y[None, None, :] - F) / (1 - Gd))**2   # LOO residual of well j inside the 63-well problem
    S = np.where(OFFDIAG[None], inner, 0).sum(-1) / (n - 1)       # (L, k): inner CV score
    lk = S.argmin(0)                                 # lambda chosen without seeing well k
    outer = loo[lk, np.arange(n)]                    # nested-CV residual of well k
    lsel = (loo**2).mean(1).argmin()                 # ordinary LOO selection on all 64 (optimistic)
    res_in = y - u[lsel]; Hs = H[lsel]
    dof_res = n - np.trace(2 * Hs - Hs @ Hs.T)
    gcv = n * ((y - u)**2).sum(1) / (n - np.einsum('lkk->l', H))**2
    return dict(cv=np.sqrt(np.mean(outer**2)), cv_int=np.sqrt(np.mean(outer[INTERIOR]**2)),
                loo_sel=np.sqrt((loo[lsel]**2).mean()), dfcorr=np.sqrt((res_in**2).sum() / dof_res),
                edf=float(np.trace(Hs)), lsel=lsel, gcv_sel=int(gcv.argmin()), outer=outer, fit=u[lsel],
                res_in=res_in, Hsel=Hs, lam_spread=float(np.std(lk)))

# ---- 2-D isotonic regression (non-decreasing in both doses) ---------------------------------------------
EDGES = []
for i in range(N):
    for j in range(N):
        if i + 1 < N: EDGES.append((i * N + j, (i + 1) * N + j))
        if j + 1 < N: EDGES.append((i * N + j, i * N + j + 1))
def iso_fit(y, keep):
    idx = np.flatnonzero(keep); pos = {v: c for c, v in enumerate(idx)}
    drop = set(np.flatnonzero(~keep))
    E = [(a, b) for a, b in EDGES if a not in drop and b not in drop]
    for k in drop:                                   # keep the order transitive through a removed well
        preds = [a for a, b in EDGES if b == k]; succs = [b for a, b in EDGES if a == k]
        E += [(p, q) for p in preds for q in succs]
    C = np.zeros((len(idx), len(E)))
    for c, (a, b) in enumerate(E): C[pos[b], c] = 1; C[pos[a], c] = -1
    f = quadprog.solve_qp(np.eye(len(idx)), y[idx].astype(float), C, np.zeros(len(E)))[0]
    out = np.full(n, np.nan); out[idx] = f; return out
LOWER = [[a for a in range(n) if IJ[a, 0] <= IJ[k, 0] and IJ[a, 1] <= IJ[k, 1] and a != k] for k in range(n)]
UPPER = [[a for a in range(n) if IJ[a, 0] >= IJ[k, 0] and IJ[a, 1] >= IJ[k, 1] and a != k] for k in range(n)]
def iso_cv(y):
    full = iso_fit(y, np.ones(n, bool))
    nlev = len(np.unique(np.round(full, 9)))
    pred = np.empty(n)
    for k in range(n):
        keep = np.ones(n, bool); keep[k] = False
        f = iso_fit(y, keep)
        lo = max(f[LOWER[k]]) if LOWER[k] else None; hi = min(f[UPPER[k]]) if UPPER[k] else None
        pred[k] = (lo + hi) / 2 if (lo is not None and hi is not None) else (lo if hi is None else hi)
    outer = y - pred
    return dict(cv=np.sqrt(np.mean(outer**2)), cv_int=np.sqrt(np.mean(outer[INTERIOR]**2)),
                dfcorr=np.sqrt(((y - full)**2).sum() / max(n - nlev, 1)), nlev=nlev, res_in=y - full, outer=outer)

def diff_estimators(Y):
    lap = Y[1:-1, 1:-1] - (Y[:-2, 1:-1] + Y[2:, 1:-1] + Y[1:-1, :-2] + Y[1:-1, 2:]) / 4
    sd2 = np.concatenate([(Y[:, :-2] - 2 * Y[:, 1:-1] + Y[:, 2:]).ravel(), (Y[:-2] - 2 * Y[1:-1] + Y[2:]).ravel()])
    return np.sqrt(np.mean(lap**2) / 1.25), np.sqrt(np.mean(sd2**2) / 6)

def lag1(R):
    """Lag-1 autocorrelation of a residual matrix along rows (adjacent Conc2) and columns (adjacent Conc1)."""
    R = R - R.mean(); v = np.mean(R**2)
    return np.mean(R[:, :-1] * R[:, 1:]) / v, np.mean(R[:-1, :] * R[1:, :]) / v
def rowcol_frac(R):
    R = R - R.mean(); m = R.shape[0]
    return (m * (R.mean(1)**2).sum() + m * (R.mean(0)**2).sum()) / (R**2).sum()
def null_stats(Hs, nsim=2000, loo=False):
    Z = rng.standard_normal((n, nsim)); Rs = Z - Hs @ Z
    if loo: Rs = Rs / (1 - np.diag(Hs))[:, None]
    Rs = Rs.T.reshape(nsim, N, N); Rs = Rs - Rs.mean((1, 2), keepdims=True); v = (Rs**2).mean((1, 2))
    rr = (Rs[:, :, :-1] * Rs[:, :, 1:]).mean((1, 2)) / v; rc = (Rs[:, :-1, :] * Rs[:, 1:, :]).mean((1, 2)) / v
    rcf = (N * (Rs.mean(2)**2).sum(1) + N * (Rs.mean(1)**2).sum(1)) / (Rs**2).sum((1, 2))
    return rr, rc, rcf

# ---- per-block analysis ---------------------------------------------------------------------------------
rows, keep_res = [], {}
for (src, pid), blk in df.groupby(['src', 'PairIndex']):
    d1, d2_, cell = blk.Drug1.iloc[0], blk.Drug2.iloc[0], blk.Cell.iloc[0]
    c1 = np.sort(blk.Conc1.unique()); c2 = np.sort(blk.Conc2.unique())
    M = blk.pivot_table(index='Conc1', columns='Conc2', values='e').loc[c1, c2].values
    Mr = blk.pivot_table(index='Conc1', columns='Conc2', values='e_raw').loc[c1, c2].values
    assert M.shape == (N, N) and not np.isnan(M).any()
    y, yr = M.ravel(), Mr.ravel()
    hb = HB[(HB.src == src) & (HB.pid == pid)].iloc[0]
    row = dict(src=src, pid=pid, d1=d1, d2=d2_, cell=cell, level=int(hb.level))
    W = linear_smoother_cv(y, 'W'); Tt = linear_smoother_cv(y, 'T'); I = iso_cv(y)
    Wr = linear_smoother_cv(yr, 'W'); Tr = linear_smoother_cv(yr, 'T'); Ir = iso_cv(yr)
    lap, sec = diff_estimators(M); lapr, secr = diff_estimators(Mr)
    row.update(sigma_estimate=W['cv'], sigma_W_cv=W['cv'], sigma_W_cv_interior=W['cv_int'], sigma_W_loo_selected=W['loo_sel'],
               sigma_W_dfcorr=W['dfcorr'], edf_W=W['edf'], lam_row_W=GRID_W[W['lsel']][0], lam_col_W=GRID_W[W['lsel']][1],
               W_lambda_choice_spread=W['lam_spread'], W_gcv_equals_loo_choice=bool(W['gcv_sel'] == W['lsel']),
               sigma_T_cv=Tt['cv'], sigma_T_cv_interior=Tt['cv_int'], sigma_T_loo_selected=Tt['loo_sel'], sigma_T_dfcorr=Tt['dfcorr'],
               edf_T=Tt['edf'], lam_T=LAMS_T[Tt['lsel']],
               sigma_I_cv=I['cv'], sigma_I_cv_interior=I['cv_int'], sigma_I_dfcorr=I['dfcorr'], iso_levelsets=I['nlev'],
               sigma_diff_laplacian=lap, sigma_diff_second=sec,
               sigma_W_cv_raw=Wr['cv'], sigma_W_cv_interior_raw=Wr['cv_int'], sigma_W_dfcorr_raw=Wr['dfcorr'],
               sigma_T_cv_raw=Tr['cv'], sigma_I_cv_raw=Ir['cv'], sigma_I_dfcorr_raw=Ir['dfcorr'],
               sigma_diff_laplacian_raw=lapr, sigma_diff_second_raw=secr,
               frac_wells_clipped_low=float((yr < 0).mean()), frac_wells_clipped_high=float((yr > 1).mean()),
               control_well_e_raw=float(Mr[0, 0]), max_e=float(M.max()))
    # comparators from H1 (single-agent Hill residual RMSE as used by the T1 audit; dial misfit)
    sig_hill = np.sqrt((hb.hillrmA**2 + hb.hillrmB**2) / 2)
    row.update(sigma_hill_T1=sig_hill, sigma_hill_dfcorr=sig_hill * np.sqrt(14 / 8),   # 14 wells, 6 Hill parameters
               rmse_dial=hb.rmse, rmse_bliss=hb.rmse_bliss, rmse_loewe=hb.rmse_loewe, alpha=hb.alpha)
    # dial / Bliss residuals on the 49 interior wells, with H1's Hill marginals and H1's fitted alpha
    (emA, ecA, nA), _ = fit_hill(c1[1:], M[1:, 0]); (emB, ecB, nB), _ = fit_hill(c2[1:], M[0, 1:])
    EA, EB = np.meshgrid(hill(c1[1:], emA, ecA, nA), hill(c2[1:], emB, ecB, nB), indexing='ij')
    Eo = M[1:, 1:]
    Rd = Eo - dial(EA, EB, hb.alpha); Rb = Eo - dial(EA, EB, 0.0)
    row['rmse_dial_recomputed'] = float(np.sqrt(np.mean(Rd**2)))
    row['bliss_excess_mean'] = float(Rb.mean())
    # model-error variance implied if the noise were sigma_W_cv_interior (negative => misfit within noise)
    row['dial_excess_var'] = hb.rmse**2 - W['cv_int']**2
    row['ratio_mf_over_hill'] = W['cv'] / sig_hill if sig_hill > 0 else np.inf
    row['ratio_dial_over_mf_interior'] = hb.rmse / W['cv_int']
    # law gaps on this design (Hill marginals fixed; no calibration uncertainty) in model-free noise units
    for name, (a1, a2) in dict(BL=(0, 1), EB=(-1, 0), EL=(-1, 1)).items():
        g = dial(EA, EB, a1) - dial(EA, EB, a2)
        row[f'rms_gap_{name}'] = float(np.sqrt(np.mean(g**2)))
        row[f'sep_iid_{name}'] = float(np.sqrt(np.sum(g**2)) / W['cv_int'])   # sqrt(sum gap^2)/sigma over 49 wells
    # dependence within block
    RW = W['res_in'].reshape(N, N); RL = W['outer'].reshape(N, N)
    row['lag1_row_W'], row['lag1_col_W'] = lag1(RW); row['rowcol_frac_W'] = rowcol_frac(RW)
    nr, nc, nf = null_stats(W['Hsel'])
    row['lag1_row_W_null'], row['lag1_col_W_null'], row['rowcol_frac_W_null'] = nr.mean(), nc.mean(), nf.mean()
    row['lag1_row_W_p'] = float((1 + (nr >= row['lag1_row_W']).sum()) / (1 + len(nr)))
    row['lag1_col_W_p'] = float((1 + (nc >= row['lag1_col_W']).sum()) / (1 + len(nc)))
    row['rowcol_frac_W_p'] = float((1 + (nf >= row['rowcol_frac_W']).sum()) / (1 + len(nf)))
    row['lag1_row_W_cvres'], row['lag1_col_W_cvres'] = lag1(RL)
    row['lag1_row_iso'], row['lag1_col_iso'] = lag1(I['res_in'].reshape(N, N))
    row['lag1_row_dial'], row['lag1_col_dial'] = lag1(Rd)
    row['lag1_row_bliss'], row['lag1_col_bliss'] = lag1(Rb)
    rows.append(row)
    keep_res[(src, pid)] = dict(cvres=W['outer'], dialres=Rd.ravel(), fit=W['fit'], y=y, yr=yr, fit_raw=Wr['fit'], cvres_raw=Wr['outer'])
    if len(rows) % 30 == 0: print(len(rows), 'blocks', flush=True)

R = pd.DataFrame(rows)
assert np.allclose(R.rmse_dial_recomputed, R.rmse_dial, atol=1e-6), 'dial residual reconstruction differs from h1_blocks.csv'

# ---- replicate single-agent series across blocks (same drug, cell line and dose vector) ----------------
ser = []
for (src, pid), blk in df.groupby(['src', 'PairIndex']):
    c1 = np.sort(blk.Conc1.unique()); c2 = np.sort(blk.Conc2.unique())
    for col in ('e', 'e_raw'):
        M = blk.pivot_table(index='Conc1', columns='Conc2', values=col).loc[c1, c2].values
        ser.append((src, pid, col, 'A', blk.Drug1.iloc[0], tuple(c1[1:]), blk.Cell.iloc[0], M[1:, 0]))
        ser.append((src, pid, col, 'B', blk.Drug2.iloc[0], tuple(c2[1:]), blk.Cell.iloc[0], M[0, 1:]))
S = pd.DataFrame(ser, columns=['src', 'pid', 'scale', 'arm', 'drug', 'conc', 'cell', 'e'])
rep_rows, rep_summary = [], {}
for scale in ('e', 'e_raw'):
    D, Dw, mids, blockdev = [], [], [], {}
    for (drug, cell, conc), G in S[S.scale == scale].groupby(['drug', 'cell', 'conc']):
        if len(G) < 2: continue
        E = np.stack(G.e.values)
        for a, b in itertools.combinations(range(len(E)), 2):
            dd = E[a] - E[b]; D.append(dd); Dw.append(dd - dd.mean()); mids.append((E[a] + E[b]) / 2)
            if scale == 'e':
                rep_rows.append(dict(drug=drug, cell=cell, conc=str(conc), src_a=G.src.iloc[a], pid_a=G.pid.iloc[a],
                                     src_b=G.src.iloc[b], pid_b=G.pid.iloc[b], rms_diff=float(np.sqrt(np.mean(dd**2))),
                                     mean_diff=float(dd.mean()), identical=bool(np.allclose(E[a], E[b]))))
        mu = E.mean(0); m = len(E)
        for t, (_, g) in enumerate(G.iterrows()):   # per-series deviation from the mean of the OTHER replicates
            other = (mu * m - E[t]) / (m - 1); dev = E[t] - other
            # Var(e_t - mean_others) = sigma^2 (1 + 1/(m-1)) under iid noise
            blockdev.setdefault((g.src, g.pid), {})[g.arm] = (float(np.sqrt(np.mean(dev**2) / (1 + 1 / (m - 1)))), m)
    D, Dw, mids = np.array(D), np.array(Dw), np.array(mids)
    bins = [-np.inf, 0.05, 0.2, 0.5, 0.8, np.inf]
    lab = np.digitize(mids.ravel(), bins[1:-1])
    rep_summary[scale] = dict(
        n_series_pairs=int(len(D)), n_identical_pairs=int(sum(np.allclose(x, 0) for x in D)),
        sigma_total=float(D.std() / np.sqrt(2)), sigma_total_mad=float(1.4826 * np.median(np.abs(D - np.median(D))) / np.sqrt(2)),
        sigma_within_series=float(np.sqrt((Dw**2).sum() / (len(Dw) * 6) / 2)),   # offset removed (6 df per pair)
        sigma_offset_between_plates=float(np.sqrt(max(np.var(D.mean(1)) - (Dw**2).sum() / (len(Dw) * 6) / 7, 0) / 2)),
        sigma_by_mean_effect={f'[{bins[k]},{bins[k+1]})': dict(n=int((lab == k).sum()), sd=float(D.ravel()[lab == k].std() / np.sqrt(2)))
                              for k in range(len(bins) - 1)},
        caveat='pairs from groups with >2 replicates are not independent; differences include plate-to-plate potency shifts')
    if scale == 'e':
        for key, arms in blockdev.items():
            m_ = (R.src == key[0]) & (R.pid == key[1])
            for arm, (v, mm) in arms.items():
                R.loc[m_, f'rep_sigma_{arm}'] = v; R.loc[m_, f'rep_n_{arm}'] = mm
pd.DataFrame(rep_rows).to_csv(OUT / 'replicate_pairs.csv', index=False)

# ---- dependence across blocks ---------------------------------------------------------------------------
R['pair'] = R.d1 + '/' + R.d2
def icc1(x, g):
    d = pd.DataFrame(dict(x=x, g=g)).dropna(); k = d.g.nunique(); N_ = len(d)
    ni = d.groupby('g').size(); gm = d.groupby('g').x.mean(); mu = d.x.mean()
    msb = (ni * (gm - mu)**2).sum() / (k - 1); msw = ((d.x - d.g.map(gm))**2).sum() / (N_ - k)
    n0 = (N_ - (ni**2).sum() / N_) / (k - 1)
    return (msb - msw) / (msb + (n0 - 1) * msw), n0
def icc_perm(x, g, nperm=2000):
    obs, n0 = icc1(x, g); g = np.asarray(g, dtype=str)
    null = np.array([icc1(x, rng.permutation(g))[0] for _ in range(nperm)])
    return dict(icc=float(obs), p_perm=float((1 + (null >= obs).sum()) / (1 + nperm)), mean_group_size=float(n0),
                design_effect=float(1 + (n0 - 1) * max(obs, 0)))
R['log_dial_over_mf'] = np.log(R.ratio_dial_over_mf_interior)
icc = {}
for var in ('alpha', 'bliss_excess_mean', 'sigma_estimate', 'sigma_W_cv_raw', 'rmse_dial', 'log_dial_over_mf', 'sigma_hill_T1'):
    icc[var] = dict(by_pair=icc_perm(R[var].values, R.pair.values), by_cell_line=icc_perm(R[var].values, R.cell.values))

def pattern_corr(key):
    keys = list(zip(R.src, R.pid)); X = np.stack([keep_res[k][key] for k in keys])
    X = X - X.mean(1, keepdims=True); X = X / np.linalg.norm(X, axis=1, keepdims=True); C = X @ X.T
    iu = np.triu_indices(len(R), 1)
    PR, CL, SR = (R[c].to_numpy(dtype=str) for c in ('pair', 'cell', 'src'))
    same_pair = (PR[:, None] == PR[None, :])[iu]
    same_cell = (CL[:, None] == CL[None, :])[iu]
    same_src = (SR[:, None] == SR[None, :])[iu]
    drugs = [set([a, b]) for a, b in zip(R.d1, R.d2)]
    share_drug = np.array([[len(drugs[i] & drugs[j]) > 0 for j in range(len(R))] for i in range(len(R))])[iu]
    c = C[iu]
    cls = {'same_pair_diff_cell': same_pair & ~same_cell,
           'same_cell_shared_drug_diff_pair': same_cell & share_drug & ~same_pair,
           'same_cell_no_shared_drug': same_cell & ~share_drug,
           'diff_cell_diff_pair_same_file': ~same_cell & ~same_pair & same_src}
    out = {k: dict(n=int(v.sum()), mean_corr=float(c[v].mean())) for k, v in cls.items()}
    # permutation of pair labels within file: is the same-pair mean larger than chance?
    obs = c[cls['same_pair_diff_cell']].mean(); null = []
    for _ in range(1000):
        lab = PR.copy()
        for sname in ('18', '192'):
            m = SR == sname; lab[m] = rng.permutation(lab[m])
        sp = (lab[:, None] == lab[None, :])[iu] & ~same_cell
        null.append(c[sp].mean())
    out['same_pair_perm_p'] = float((1 + (np.array(null) >= obs).sum()) / 1001)
    out['same_pair_perm_null_mean'] = float(np.mean(null))
    return out
patt = {'model_free_cv_residuals': pattern_corr('cvres'), 'dial_residuals_interior': pattern_corr('dialres')}

# ---- pooled heteroscedasticity: model-free CV residual SD by fitted effect level -----------------------
def by_level(fitkey, reskey):
    f = np.concatenate([keep_res[k][fitkey] for k in keep_res]); e = np.concatenate([keep_res[k][reskey] for k in keep_res])
    bins = [-np.inf, 0.02, 0.1, 0.3, 0.5, 0.7, 0.9, np.inf]; lab = np.digitize(f, bins[1:-1])
    return {f'[{bins[k]},{bins[k+1]})': dict(n=int((lab == k).sum()), rms=float(np.sqrt(np.mean(e[lab == k]**2))))
            for k in range(len(bins) - 1)}
hetero = {'clipped_e': by_level('fit', 'cvres'), 'raw_e': by_level('fit_raw', 'cvres_raw')}

# ---- estimator self-check against synthetic truth ------------------------------------------------------
# Truth = each block's H1 dial surface (Hill marginals on the edges, fitted alpha in the interior, e=0 at
# the control well): sharp sigmoids the smoothers must chase, which is the realistic bias case.
sim = []
sub = R.sample(60, random_state=1)
for _, b in sub.iterrows():
    blk = df[(df.src == b.src) & (df.PairIndex == b.pid)]
    c1 = np.sort(blk.Conc1.unique()); c2 = np.sort(blk.Conc2.unique())
    M = blk.pivot_table(index='Conc1', columns='Conc2', values='e').loc[c1, c2].values
    (emA, ecA, nA), _ = fit_hill(c1[1:], M[1:, 0]); (emB, ecB, nB), _ = fit_hill(c2[1:], M[0, 1:])
    a_ = np.r_[0, hill(c1[1:], emA, ecA, nA)]; b_ = np.r_[0, hill(c2[1:], emB, ecB, nB)]
    EA, EB = np.meshgrid(a_, b_, indexing='ij'); truth = dial(EA, EB, b.alpha).ravel()
    for sig in (0.02, 0.05, 0.10):
        for clip in (False, True):
            yy = truth + sig * rng.standard_normal(n)
            if clip: yy = np.clip(yy, 0, 1)
            eff = np.sqrt(np.mean((yy - truth)**2))       # realised noise actually added (after clipping)
            w = linear_smoother_cv(yy, 'W'); t = linear_smoother_cv(yy, 'T'); i = iso_cv(yy); l, s2 = diff_estimators(yy.reshape(N, N))
            sim.append(dict(sigma_true=sig, clipped=clip, realised=eff, W_cv=w['cv'], W_dfcorr=w['dfcorr'], W_loo_sel=w['loo_sel'],
                            T_cv=t['cv'], I_cv=i['cv'], I_dfcorr=i['dfcorr'], diff_lap=l, diff_second=s2))
SIM = pd.DataFrame(sim)
simsum = SIM.groupby(['sigma_true', 'clipped']).median().round(5).reset_index().to_dict('records')
# null check of the hill-residual proxy on the same synthetic truth, H1's estimator unchanged
hsim = []
for _, b in sub.iterrows():
    blk = df[(df.src == b.src) & (df.PairIndex == b.pid)]
    c1 = np.sort(blk.Conc1.unique()); c2 = np.sort(blk.Conc2.unique())
    M = blk.pivot_table(index='Conc1', columns='Conc2', values='e').loc[c1, c2].values
    (emA, ecA, nA), _ = fit_hill(c1[1:], M[1:, 0]); (emB, ecB, nB), _ = fit_hill(c2[1:], M[0, 1:])
    for sig in (0.02, 0.05, 0.10):
        ya = np.clip(hill(c1[1:], emA, ecA, nA) + sig * rng.standard_normal(7), 0, 1)
        yb = np.clip(hill(c2[1:], emB, ecB, nB) + sig * rng.standard_normal(7), 0, 1)
        hsim.append(dict(sigma_true=sig, hill_T1=np.sqrt((fit_hill(c1[1:], ya)[1]**2 + fit_hill(c2[1:], yb)[1]**2) / 2)))
hillsim = pd.DataFrame(hsim).groupby('sigma_true').hill_T1.median().round(5).to_dict()

# ---- pooled summaries ----------------------------------------------------------------------------------
def q(x): x = pd.Series(x).replace([np.inf, -np.inf], np.nan).dropna(); return dict(median=float(x.median()), q25=float(x.quantile(.25)), q75=float(x.quantile(.75)), n=int(len(x)))
pairmean = lambda col: R.groupby('pair')[col].mean()
dep_within = {}
for nm in ('lag1_row_W', 'lag1_col_W', 'rowcol_frac_W'):
    ex = R[nm] - R[nm + '_null']; exp_ = (R.assign(ex=ex).groupby('pair').ex.mean())
    dep_within[nm] = dict(observed=q(R[nm]), null_mean=q(R[nm + '_null']), excess_mean=float(ex.mean()),
                          blocks_t_p=float(ttest_1samp(ex, 0, alternative='greater').pvalue),
                          pair_level_n=int(len(exp_)), pair_level_wilcoxon_p=float(wilcoxon(exp_, alternative='greater').pvalue),
                          frac_blocks_p_lt_05=float((R[nm + '_p'] < 0.05).mean()))
for nm in ('lag1_row_W_cvres', 'lag1_col_W_cvres', 'lag1_row_iso', 'lag1_col_iso', 'lag1_row_dial', 'lag1_col_dial', 'lag1_row_bliss', 'lag1_col_bliss'):
    dep_within[nm] = q(R[nm])

summary = dict(
    blocks=int(len(R)),
    noise_estimates_clipped_e_H1_scale={c: q(R[c]) for c in ['sigma_estimate', 'sigma_W_cv_interior', 'sigma_W_loo_selected', 'sigma_W_dfcorr',
        'sigma_T_cv', 'sigma_T_dfcorr', 'sigma_I_cv', 'sigma_I_dfcorr', 'sigma_diff_laplacian', 'sigma_diff_second', 'rep_sigma_A', 'rep_sigma_B']},
    noise_estimates_raw_e_unclipped={c: q(R[c]) for c in ['sigma_W_cv_raw', 'sigma_W_cv_interior_raw', 'sigma_W_dfcorr_raw', 'sigma_T_cv_raw',
        'sigma_I_cv_raw', 'sigma_I_dfcorr_raw', 'sigma_diff_laplacian_raw', 'sigma_diff_second_raw']},
    comparators=dict(sigma_hill_T1=q(R.sigma_hill_T1), sigma_hill_dfcorr=q(R.sigma_hill_dfcorr), rmse_dial=q(R.rmse_dial),
                     rmse_bliss=q(R.rmse_bliss), frac_blocks_hillA_rmse_below_1em4=float((HB.hillrmA < 1e-4).mean()),
                     frac_blocks_hillB_rmse_below_1em4=float((HB.hillrmB < 1e-4).mean()),
                     ratio_mf_over_hill=q(R.ratio_mf_over_hill), frac_mf_gt_hill=float((R.sigma_estimate > R.sigma_hill_T1).mean()),
                     ratio_dial_over_mf_interior=q(R.ratio_dial_over_mf_interior),
                     frac_dial_rmse_gt_mf_interior=float((R.rmse_dial > R.sigma_W_cv_interior).mean()),
                     frac_dial_rmse_gt_mf_dfcorr=float((R.rmse_dial > R.sigma_W_dfcorr).mean()),
                     dial_excess_var=q(R.dial_excess_var),
                     spearman_mf_vs_hill=float(spearmanr(R.sigma_estimate, R.sigma_hill_T1).statistic),
                     spearman_mf_vs_dial=float(spearmanr(R.sigma_W_cv_interior, R.rmse_dial).statistic)),
    clipping=dict(frac_wells_raw_e_below_0=float(R.frac_wells_clipped_low.mean()), frac_wells_raw_e_above_1=float(R.frac_wells_clipped_high.mean()),
                  control_well_raw_e_192file=dict(mean=float(R[R.src == '192'].control_well_e_raw.mean()),
                                                  sd=float(R[R.src == '192'].control_well_e_raw.std()),
                                                  mad_sd=float(1.4826 * (R[R.src == '192'].control_well_e_raw - R[R.src == '192'].control_well_e_raw.median()).abs().median())),
                  control_well_raw_e_18file=q(R[R.src == '18'].control_well_e_raw)),
    replicate_single_agent_series=rep_summary,
    heteroscedasticity_model_free_cv_residual_rms_by_fitted_effect=hetero,
    smoothing_choice=dict(edf_W=q(R.edf_W), edf_T=q(R.edf_T), iso_levelsets=q(R.iso_levelsets),
                          frac_W_gcv_equals_loo=float(R.W_gcv_equals_loo_choice.mean()),
                          frac_W_lambda_at_grid_min=float(((R.lam_row_W == LAMS_W[0]) | (R.lam_col_W == LAMS_W[0])).mean()),
                          frac_W_lambda_at_grid_max=float(((R.lam_row_W == LAMS_W[-1]) & (R.lam_col_W == LAMS_W[-1])).mean())),
    law_gaps_in_model_free_noise_units=dict(rms_gap_BL=q(R.rms_gap_BL), rms_gap_EB=q(R.rms_gap_EB), rms_gap_EL=q(R.rms_gap_EL),
        sep_iid_BL=q(R.sep_iid_BL), sep_iid_EB=q(R.sep_iid_EB), sep_iid_EL=q(R.sep_iid_EL),
        note='sep = sqrt(sum over 49 wells of gap^2)/sigma_W_cv_interior: the separation of two FIXED surfaces under iid noise with '
             'known single-agent curves. Ignores calibration uncertainty, the alpha fit, model error and within-block correlation; '
             'it is an optimistic ceiling, not the power of H1.'),
    dependence_within_block=dep_within,
    dependence_across_blocks=dict(icc=icc, residual_pattern_correlation=patt),
    estimator_self_check_synthetic=dict(medians=simsum, hill_T1_proxy_median_on_synthetic_clipped_truth=hillsim,
                                        n_blocks=int(len(sub)), truth='H1 dial surface per block, iid Gaussian noise, optional clip to [0,1]'),
)
R['model_error_rms_est'] = np.sqrt(R.dial_excess_var.clip(lower=0))
summary['gap_vs_noise_vs_model_error'] = dict(
    model_error_rms_est=q(R.model_error_rms_est),
    note='model_error_rms_est = sqrt(max(rmse_dial^2 - sigma_W_cv_interior^2, 0)); conservative (CV sigma is upper-ish, so this is lower-ish)',
    frac_blocks_gapBL_gt_sigma_interior=float((R.rms_gap_BL > R.sigma_W_cv_interior).mean()),
    frac_blocks_gapBL_gt_sigma_dfcorr=float((R.rms_gap_BL > R.sigma_W_dfcorr).mean()),
    frac_blocks_gapBL_gt_model_error=float((R.rms_gap_BL > R.model_error_rms_est).mean()),
    frac_blocks_gapEL_gt_model_error=float((R.rms_gap_EL > R.model_error_rms_est).mean()),
    median_gapBL_over_sigma_interior=float((R.rms_gap_BL / R.sigma_W_cv_interior).median()),
    median_gapBL_over_sigma_dfcorr=float((R.rms_gap_BL / R.sigma_W_dfcorr).median()),
    median_gapEB_over_sigma_interior=float((R.rms_gap_EB / R.sigma_W_cv_interior).median()),
    pooled_sep_iid_BL=float(np.sqrt((R.sep_iid_BL**2).sum())), pooled_sep_iid_EB=float(np.sqrt((R.sep_iid_EB**2).sum())),
    pooled_note='sqrt of the sum over 210 blocks of per-block squared separations: what iid noise alone would allow if one law were '
                'exactly true everywhere with known marginals. It is NOT achievable here: every law misfits by more than its gap '
                '(see model_error_rms_est), residuals are spatially dependent, and blocks share pair and cell-line effects.')
R.drop(columns=['pair']).to_csv(OUT / 'noise_modelfree.csv', index=False)
json.dump(summary, open(OUT / 'noise_modelfree_summary.json', 'w'), indent=1, default=float)
print(json.dumps(summary, indent=1, default=float))
