"""Noise forensics for DECREASE (H1 audit, stage 1).

Goal: estimate MEASUREMENT noise in the DECREASE 210-block validation set separately from model
error, and quantify the dependence (shared block-level error) between wells of one block.

Facts established from the files (printed by section A):
  * every block is a single 8x8 matrix; no (conc1, conc2) cell is repeated inside a block;
  * no (drug1, drug2, cell line) block is repeated, within or across the two files;
  * the two files use disjoint cell lines, so no well is repeated across files;
  * BUT the same drug at the same concentration in the same cell line appears as a single-agent
    well in many blocks (the anchor drugs Trametinib / Dactolisib in every 192-file block; several
    drugs in two blocks each).  These are genuine independent wells (no two are identical), so
    they are replicates -- across blocks, not within a block.
  * In the 192 file the (0,0) wells of each cell line average 100.00 % (to <=0.2 %), i.e. the
    (0,0) wells of a cell line were normalised jointly.  A (0,0) deviation from 100 is therefore a
    single-well deviation from the cell-line control mean.

Estimators (all on the viability scale v in %, reported in effect units e = 1 - v/100, UNCLIPPED;
H1 used e clipped to [0,1]):
  A. zero-dose replicates: the (0,0) wells of one cell line (12 or 30 per line in the 192 file) are
     model-free replicates at e = 0; their sd is TOTAL single-well error at zero dose (block-level +
     well-level), column sigma_00_cell_total.
  B. replicate decomposition per (file, cell line), three nested models:
       none : v_bg = m_g + eps                 -> total cross-block replicate sd
       block: v_bg = s_b * m_g + eps           -> s_b multiplicative factor shared by all wells of block b
       axis : v_bg = s_(b,axis) * m_g + eps    -> one factor per single-agent axis of a block
     g = (drug, conc) group (or the (0,0) group), Var(eps) = a^2 + (c*m)^2 (heteroscedastic),
     weighted ALS + grid ML, squared residuals df-corrected by n/(n-p) per stratum.
     sigma_estimate (headline) = 'block' well sd, evaluated at the block's interior viability levels
     (RMS over the 49 interior wells): random error of one well around its block's own calibrated
     surface.  sd(s_b) (bias-corrected for estimation error) = block-level calibration error.
  C. model-free within-block bounds on the full 8x8 matrix:
     iso_lb  : RMS residual of the bivariate isotonic (monotone in both doses) projection.  If the
               true surface is monotone, ||y - P(y)|| <= ||y - f|| = ||eps||, so iso_lb is a hard
               lower bound on the realised RMS of the well errors in that block (block-scale
               errors are invisible to it because they preserve monotonicity).
     iso_cal : sigma at which the simulated expected iso RMS (truth = plug-in isotonic fit) equals
               the observed one; a point estimate, biased low (plug-in truth is flatter).
     d2_ub   : second-difference pseudo-residual sd along both log-dose axes; upper-biased by
               surface curvature.
  D. H1's own Hill residual (clipped, divided by 7) and the same residual unclipped with df 7-3.
  E. dependence: intra-block correlation of replicate deviations; agreement of block factors
     estimated from axis 1 vs axis 2 vs the (0,0) well; does s_b carry into the interior wells.
Outputs: noise_forensic.csv (per block), noise_forensic.json (summary).
"""
import json, pathlib, os
import numpy as np, pandas as pd
from scipy.optimize import isotonic_regression, least_squares
from scipy.stats import spearmanr, pearsonr

DATA = pathlib.Path('/tmp/claude-0/h1run/DECREASE/210_Novel_Anticancer_combinations')
OUT = pathlib.Path('/tmp/claude-0/stage1/h1')
H1 = pathlib.Path('/home/user/bounded-observer/experiments/h1-decrease/h1_blocks.csv')
rng = np.random.default_rng(20261003)

a = pd.read_excel(DATA / '192_Combinations_.xlsx').assign(src='192')
b = pd.read_excel(DATA / '18_combinations_.xlsx').assign(src='18')
df = pd.concat([a, b], ignore_index=True)
# viability-like scale in %: 192 file is % viability; 18 file is % inhibition (0..100, clipped at source)
df['v'] = np.where(df.src == '192', df.Response, 100 - df.Response)
S = {}

# ---------------- A. inventory of replication ----------------
blocks = df.groupby(['src', 'PairIndex']).agg(d1=('Drug1', 'first'), d2=('Drug2', 'first'), cell=('Cell', 'first')).reset_index()
A = dict(
    n_blocks=len(blocks),
    within_block_duplicate_cells=int(df.duplicated(['src', 'PairIndex', 'Conc1', 'Conc2']).sum()),
    duplicate_pair_cell_blocks=int(blocks.assign(p=blocks[['d1', 'd2']].apply(lambda r: tuple(sorted(r)), axis=1))
                                   .duplicated(['p', 'cell']).sum()),
    cell_lines_shared_between_files=sorted(set(a.Cell) & set(b.Cell)),
    frac_18file_wells_censored_at_0_or_100=float(((b.Response <= 0) | (b.Response >= 100)).mean()),
    frac_18file_00_wells_at_0=float((b[(b.Conc1 == 0) & (b.Conc2 == 0)].Response <= 0).mean()),
    frac_192file_integer_responses=float(np.isclose(a.Response, a.Response.round()).mean()),
)
z00 = df[(df.Conc1 == 0) & (df.Conc2 == 0)]
A['zero_well_by_cell'] = {f'{s}|{c}': dict(n=int(len(g)), mean=float(g.v.mean()), sd=float(g.v.std(ddof=1)))
                          for (s, c), g in z00.groupby(['src', 'Cell'])}

# single-agent + (0,0) long table
rows = []
for (s, p), blk in df.groupby(['src', 'PairIndex']):
    for ax, (dcol, ccol, ocol) in enumerate([('Drug1', 'Conc1', 'Conc2'), ('Drug2', 'Conc2', 'Conc1')], start=1):
        r = blk[(blk[ocol] == 0) & (blk[ccol] > 0)]
        rows.append(pd.DataFrame(dict(src=s, pid=p, cell=r.Cell, grp=r[dcol] + '@' + r[ccol].astype(str), v=r.v, axis=ax)))
    z = blk[(blk.Conc1 == 0) & (blk.Conc2 == 0)]
    rows.append(pd.DataFrame(dict(src=s, pid=p, cell=z.Cell, grp='CTRL(0,0)', v=z.v, axis=0)))
L = pd.concat(rows, ignore_index=True)
L['n'] = L.groupby(['src', 'cell', 'grp']).v.transform('size')
rep = L[(L.n > 1) & (L.axis > 0)]
gstat = rep.groupby(['src', 'cell', 'grp']).v.agg(['size', 'nunique'])
A['replicate_groups_single_agent'] = {s: dict(groups=int((gstat.loc[s]['size'] > 1).sum()), wells=int(gstat.loc[s]['size'].sum()))
                                      for s in ('192', '18')}
A['replicate_groups_with_identical_values'] = int((gstat['nunique'] == 1).sum())
S['A_inventory'] = A


# ---------------- B. replicate decomposition ----------------
def fit_stratum(D, mode='block', n_iter=8):
    """D: rows of one (src, cell) stratum restricted to groups with n>=2.
    mode 'none' : v = m_g + eps                      (total cross-block replicate scatter)
    mode 'block': v = s_b * m_g + eps                (one multiplicative factor per block)
    mode 'axis' : v = s_(b,axis) * m_g + eps         (one factor per single-agent axis of a block; (0,0) rows dropped)
    Var(eps) = a^2 + (c*m)^2.  Weighted ALS + grid ML for (a, c) on df-corrected squared residuals."""
    D = D.copy()
    if mode == 'axis': D = D[D.axis > 0].copy()
    unit = D.pid.astype(str) + ('_' + D.axis.astype(str) if mode == 'axis' else '')
    gi = pd.factorize(D.grp)[0]; bi = pd.factorize(unit)[0]; G, B = gi.max() + 1, bi.max() + 1
    v = D.v.values.astype(float)
    m = np.bincount(gi, v) / np.bincount(gi); s = np.ones(B); av, cv = 3.0, 0.08
    p = G + (B - 1 if mode != 'none' else 0)
    infl = len(v) / max(len(v) - p, 1)              # df correction applied to squared residuals
    for _ in range(n_iter):
        for _ in range(30):
            w = 1 / (av**2 + (cv * m[gi])**2)
            m = np.bincount(gi, w * s[bi] * v) / np.bincount(gi, w * s[bi]**2)
            if mode != 'none':
                s = np.bincount(bi, w * m[gi] * v, minlength=B) / np.bincount(bi, w * m[gi]**2, minlength=B)
                s = s / np.mean(s)
        fit = s[bi] * m[gi]; res = v - fit
        r2 = res**2 * infl; mm = m[gi]
        best = None
        for a0 in np.geomspace(0.05, 30, 40):
            for c0 in np.linspace(0, 0.4, 41):
                q = a0**2 + (c0 * mm)**2; val = np.sum(np.log(q) + r2 / q)
                if best is None or val < best[0]: best = (val, a0, c0)
        av, cv = best[1], best[2]
    w = 1 / (av**2 + (cv * m[gi])**2)
    se_s = 1 / np.sqrt(np.bincount(bi, w * m[gi]**2, minlength=B)) if mode != 'none' else np.zeros(B)
    D['res'] = res; D['m'] = m[gi]; D['s'] = s[bi]; D['se_s'] = se_s[bi]; D['infl'] = infl
    return D, dict(a=av, c=cv, n_obs=len(v), n_params=p, df=len(v) - p, n_units=B, n_groups=G,
                   sd_factor=float(np.std(s, ddof=1)) if mode != 'none' else 0.0,
                   sd_factor_corrected=float(np.sqrt(max(np.var(s, ddof=1) - np.mean(se_s**2), 0))) if mode != 'none' else 0.0,
                   rms_res_dfcorr=float(np.sqrt(np.sum(res**2) / max(len(v) - p, 1))),
                   robust_sd_dfcorr=float(1.4826 * np.median(np.abs(res)) * np.sqrt(infl)))


def sig_v(av=None, cv=None, m=None, a=None, c=None):
    if a is not None: av, cv = a, c  # noise sd in % viability at mean level m
    return np.sqrt(av**2 + (cv * np.asarray(m))**2)


LR = L[L.n > 1]   # replicate groups incl. CTRL(0,0)
MODES = ('none', 'block', 'axis')
strata, FIT = {}, {m_: [] for m_ in MODES}
for (s_, c), D in LR.groupby(['src', 'cell']):
    strata[f'{s_}|{c}'] = {}
    for m_ in MODES:
        Dm, pm = fit_stratum(D, m_); strata[f'{s_}|{c}'][m_] = pm; FIT[m_].append(Dm)
FIT = {m_: pd.concat(v_, ignore_index=True) for m_, v_ in FIT.items()}
F = FIT['block']
S['B_strata'] = strata


def pooled_vfun(s_, mode):
    X = FIT[mode][FIT[mode].src == s_]
    r2 = X.res.values**2 * X.infl.values; mm = X.m.values
    best = None
    for a0 in np.geomspace(0.05, 30, 60):
        for c0 in np.linspace(0, 0.4, 81):
            q = a0**2 + (c0 * mm)**2; val = np.sum(np.log(q) + r2 / q)
            if best is None or val < best[0]: best = (val, a0, c0)
    return dict(a=float(best[1]), c=float(best[2]), n_obs=int(len(X)))


S['B_pooled_variance_function_percent'] = {s_: {m_: pooled_vfun(s_, m_) for m_ in MODES} for s_ in ('192', '18')}
binned = {}
for m_ in MODES:
    X = FIT[m_].copy(); X['mbin'] = pd.cut(X.m, [-1, 10, 30, 50, 70, 90, 300])
    for (s_, mb), Y in X.groupby(['src', 'mbin'], observed=True):
        binned.setdefault(f'{s_}|{mb}', {'n': int(len(Y))})[f'sd_{m_}'] = float(np.sqrt(np.mean(Y.res**2 * Y.infl)))
S['B_binned_sd_percent_viability'] = binned


# ---------------- C. model-free within-block bounds ----------------
def iso_last(Y):
    """Exact isotonic (nondecreasing) regression along the last axis (short vectors), vectorised:
    x_i = max_{j<=i} min_{k>=i} mean(y_j..y_k)."""
    n = Y.shape[-1]
    cs = np.concatenate([np.zeros(Y.shape[:-1] + (1,)), np.cumsum(Y, -1)], -1)
    J, K = np.meshgrid(np.arange(n), np.arange(n), indexing='ij')
    valid = K >= J
    M = (cs[..., K + 1] - cs[..., J]) / np.where(valid, K - J + 1, 1)          # (..., j, k)
    out = np.empty_like(Y)
    for i in range(n):
        mk = np.where((K >= i) & valid, M, np.inf).min(-1)                       # (..., j): min over k>=i
        out[..., i] = np.where(np.arange(n) <= i, mk, -np.inf).max(-1)
    return out


_t = np.random.default_rng(5).standard_normal((20, 8))   # self-test of the vectorised PAVA against scipy
assert np.allclose(iso_last(_t), np.vstack([isotonic_regression(r).x for r in _t]))


def iso2d(Y, n_iter=500, tol=1e-10):
    """Projection onto {nondecreasing along both axes} by Dykstra's algorithm; Y may be (..., r, c)."""
    X = Y.copy(); P = np.zeros_like(Y); Q = np.zeros_like(Y)
    for _ in range(n_iter):
        Z = X + P; Rr = iso_last(Z); P = Z - Rr
        Z2 = Rr + Q; C = np.swapaxes(iso_last(np.swapaxes(Z2, -1, -2)), -1, -2); Q = Z2 - C
        if np.max(np.abs(C - X)) < tol: X = C; break
        X = C
    return X


def d2_sd(Y):
    """pseudo-residuals (y_{i-1} - 2 y_i + y_{i+1})/sqrt(6) along both axes; returns (rms, robust-median) sd."""
    r = np.concatenate([((Y[:-2] - 2 * Y[1:-1] + Y[2:]) / np.sqrt(6)).ravel(),
                        ((Y[:, :-2] - 2 * Y[:, 1:-1] + Y[:, 2:]) / np.sqrt(6)).ravel()])
    return float(np.sqrt(np.mean(r**2))), float(np.median(np.abs(r)) / 0.6745)


def iso_cal(Y, obs_rms, nsim=40):
    T = iso2d(Y)
    sig = np.geomspace(1e-3, 0.5, 22)
    Zs = T[None, None] + sig[:, None, None, None] * rng.standard_normal((len(sig), nsim) + T.shape)
    e_rms = np.sqrt(((Zs - iso2d(Zs, tol=1e-7)) ** 2).mean(axis=(-1, -2))).mean(1)
    e_rms = np.maximum.accumulate(e_rms)
    if obs_rms <= e_rms[0]: return float(sig[0])
    if obs_rms >= e_rms[-1]: return float(sig[-1])
    return float(np.exp(np.interp(obs_rms, e_rms, np.log(sig))))


# null for lag-1 correlation of isotonic residuals under iid noise on a flat-ish surface
H1B = pd.read_csv(H1, dtype={'src': str})
out = []
for (s, p), blk in df.groupby(['src', 'PairIndex']):
    c1 = np.sort(blk.Conc1.unique()); c2 = np.sort(blk.Conc2.unique())
    V = blk.pivot_table(index='Conc1', columns='Conc2', values='v').loc[c1, c2].values
    E = 1 - V / 100                                     # unclipped effect
    Ti = iso2d(E); Ri = E - Ti
    lb = float(np.sqrt(np.mean(Ri**2)))
    Ec = np.clip(E, 0, 1); lbc = float(np.sqrt(np.mean((Ec - iso2d(Ec))**2)))   # same bound on H1's clipped scale
    d2r, d2m = d2_sd(E)
    lag = np.concatenate([(Ri[:, :-1] * Ri[:, 1:]).ravel(), (Ri[:-1] * Ri[1:]).ravel()]).mean() / max(np.mean(Ri**2), 1e-12)
    cell = blk.Cell.iloc[0]; key = f'{s}|{cell}'
    st = strata[key]['block']; stn = strata[key]['none']; sta = strata[key]['axis']
    Fi = F[(F.src == s) & (F.pid == p)]
    sb = Fi.s.iloc[0] if len(Fi) else np.nan; se_sb = Fi.se_s.iloc[0] if len(Fi) else np.nan
    # level for heteroscedastic noise: interior wells' observed viability, clipped to [0,100] as a mean proxy
    lev = np.clip(V[1:, 1:], 0, 100).ravel()
    sw_int = float(np.sqrt(np.mean(sig_v(st['a'], st['c'], lev)**2)) / 100)
    pv = S['B_pooled_variance_function_percent'][s]['block']
    sw_int_pooled = float(np.sqrt(np.mean(sig_v(pv['a'], pv['c'], lev)**2)) / 100)
    sind_int = float(np.sqrt(np.mean(sig_v(sta['a'], sta['c'], lev)**2)) / 100)
    own = Fi[Fi.axis > 0]
    sw_own = float(np.sqrt(np.mean(own.res**2 * own.infl)) / 100) if len(own) else np.nan
    stot_int = float(np.sqrt(np.mean(sig_v(stn['a'], stn['c'], lev)**2)) / 100)
    sw_0 = float(sig_v(st['a'], st['c'], 100) / 100)    # well noise at zero effect
    # hill residuals: H1 (clipped e, /7) and unclipped with df 4
    out.append(dict(src=s, pid=p, d1=blk.Drug1.iloc[0], d2=blk.Drug2.iloc[0], cell=cell,
                    v00=float(V[0, 0]), sigma_00_cell_total=A['zero_well_by_cell'][key]['sd'] / 100,
                    n_single_agent_wells_replicated=int(((Fi.axis > 0)).sum()),
                    block_factor_s=float(sb), block_factor_se=float(se_sb),
                    sigma_well_rep_interior=sw_int, sigma_well_rep_interior_pooledfile=sw_int_pooled,
                    sigma_indep_rep_interior_axisfactor=sind_int, sigma_well_rep_block_own=sw_own, n_own=int(len(own)),
                    sigma_well_rep_at_e0=sw_0, sigma_total_rep_interior_noblock=stot_int,
                    sigma_block_calib_stratum=float(st['sd_factor_corrected']),
                    sigma_axis_calib_stratum=float(sta['sd_factor_corrected']),
                    sigma_iso_lb=lb, sigma_iso_lb_clipped=lbc, sigma_d2_rms_upper=d2r, sigma_d2_robust=d2m,
                    iso_resid_lag1_corr=float(lag), mean_e_interior=float(np.mean(E[1:, 1:]))))
R = pd.DataFrame(out)

# hill residuals recomputed (H1 functions reproduced verbatim to avoid importing a script with side effects)
def hill(d, emax, ec50, n): return emax * d**n / (ec50**n + d**n)
def fit_hill(d, e):
    best = None
    for n0 in (0.5, 1, 2):
        for ec0 in (np.median(d), d.min(), d.max()):
            try:
                r = least_squares(lambda q: hill(d, *q) - e, [min(max(e.max(), 0.05), 1), ec0, n0],
                                  bounds=([0, d.min() / 100, 0.1], [1, d.max() * 100, 10]))
                if best is None or r.cost < best.cost: best = r
            except Exception: pass
    return best
hr = []
for (s, p), blk in df.groupby(['src', 'PairIndex']):
    c1 = np.sort(blk.Conc1.unique()); c2 = np.sort(blk.Conc2.unique())
    V = blk.pivot_table(index='Conc1', columns='Conc2', values='v').loc[c1, c2].values
    E = 1 - V / 100; Ec = np.clip(E, 0, 1)
    rc = [fit_hill(c1[1:], Ec[1:, 0]), fit_hill(c2[1:], Ec[0, 1:])]
    ru = [fit_hill(c1[1:], E[1:, 0]), fit_hill(c2[1:], E[0, 1:])]   # unclipped; Emax still bounded [0,1]
    hr.append(dict(src=s, pid=p,
                   sigma_hill_h1=float(np.sqrt(np.mean([2 * r.cost / 7 for r in rc]))),
                   sigma_hill_unclipped_df4=float(np.sqrt(np.mean([2 * r.cost / 4 for r in ru])))))
R = R.merge(pd.DataFrame(hr), on=['src', 'pid'])
R = R.merge(H1B[['src', 'pid', 'hillrmA', 'hillrmB', 'rmse', 'rmse_bliss', 'alpha']], on=['src', 'pid'], how='left')
R['sigma_hill_h1_check'] = np.sqrt((R.hillrmA**2 + R.hillrmB**2) / 2)

# iso calibration (point estimate) for every block
R['sigma_iso_cal'] = np.nan
for i, row in R.iterrows():
    blk = df[(df.src == row.src) & (df.PairIndex == row.pid)]
    c1 = np.sort(blk.Conc1.unique()); c2 = np.sort(blk.Conc2.unique())
    E = 1 - blk.pivot_table(index='Conc1', columns='Conc2', values='v').loc[c1, c2].values / 100
    R.at[i, 'sigma_iso_cal'] = iso_cal(E, row.sigma_iso_lb) if not os.environ.get('FAST') else 0.02

# headline: replicate-based within-block well noise at the block's interior effect levels
R['sigma_estimate'] = R.sigma_well_rep_interior
# null lag-1 correlation of isotonic residuals under iid noise (simulated on each block's iso fit)
lagnull = []
for _, row in R.sample(8 if os.environ.get('FAST') else 40, random_state=1).iterrows():
    blk = df[(df.src == row.src) & (df.PairIndex == row.pid)]
    c1 = np.sort(blk.Conc1.unique()); c2 = np.sort(blk.Conc2.unique())
    E = 1 - blk.pivot_table(index='Conc1', columns='Conc2', values='v').loc[c1, c2].values / 100
    T = iso2d(E)
    for _ in range(5):
        Z = T + row.sigma_iso_cal * rng.standard_normal(T.shape); Rz = Z - iso2d(Z)
        lagnull.append(np.concatenate([(Rz[:, :-1] * Rz[:, 1:]).ravel(), (Rz[:-1] * Rz[1:]).ravel()]).mean() / max(np.mean(Rz**2), 1e-12))

# ---------------- E. dependence ----------------
E_ = {}
# (i) share of cross-block single-agent replicate variance removed by a block factor / an axis factor
for s_ in ('192', '18'):
    tot = FIT['none']; tot = tot[(tot.src == s_) & (tot.axis > 0)]; vt = np.mean(tot.res**2 * tot.infl)
    for m_ in ('block', 'axis'):
        X = FIT[m_]; X = X[(X.src == s_) & (X.axis > 0)]
        E_[f'{s_}_var_share_removed_by_{m_}_factor'] = float(1 - np.mean(X.res**2 * X.infl) / vt)
# (ii) scale estimated separately from axis 1, axis 2 and the (0,0) well of the same block (wells with m > 50 %)
def s_from(Xb):
    w = 1 / sig_v(3, 0.08, Xb.m)**2
    return np.sum(w * Xb.m * Xb.v) / np.sum(w * Xb.m**2)
sv = []
for (s_, p), Xb in F.groupby(['src', 'pid']):
    d = dict(src=s_, pid=p)
    for ax in (0, 1, 2):
        Y = Xb[(Xb.axis == ax) & (Xb.m > 50)]
        d[f's_ax{ax}'] = s_from(Y) if len(Y) else np.nan
    sv.append(d)
sv = pd.DataFrame(sv)
for x, y in [('s_ax1', 's_ax2'), ('s_ax0', 's_ax2'), ('s_ax0', 's_ax1')]:
    k = sv[[x, y]].dropna()
    if len(k) > 5:
        E_[f'corr_{x}_{y}'] = dict(n=len(k), pearson=float(pearsonr(k[x], k[y]).statistic), spearman=float(spearmanr(k[x], k[y]).statistic))
# (iii) does the block-level deviation carry into the interior?  lowest-dose wells, which every law predicts nearly
#       inactive: margin = mean of the 2 lowest single-agent doses of each drug; interior = the 2x2 lowest-dose combos.
#       Deviations are taken from the cell-line mean so cell-line differences do not create correlation.
mi = []
for (s_, p), blk in df.groupby(['src', 'PairIndex']):
    c1 = np.sort(blk.Conc1.unique()); c2 = np.sort(blk.Conc2.unique())
    V = blk.pivot_table(index='Conc1', columns='Conc2', values='v').loc[c1, c2].values
    mi.append(dict(src=s_, pid=p, cell=blk.Cell.iloc[0], v00=V[0, 0], margin=np.mean(np.r_[V[1:3, 0], V[0, 1:3]]), interior=V[1:3, 1:3].mean()))
mi = pd.DataFrame(mi)
for s_ in ('192', '18'):
    X = mi[mi.src == s_].copy()
    d = dict(mean_v00=float(X.v00.mean()), mean_margin=float(X.margin.mean()), mean_interior=float(X.interior.mean()),
             mean_interior_minus_margin=float((X.interior - X.margin).mean()), sd_interior_minus_margin=float((X.interior - X.margin).std()),
             mean_margin_minus_v00=float((X.margin - X.v00).mean()))
    for c_ in ('v00', 'margin', 'interior'): X[c_] = X[c_] - X.groupby('cell')[c_].transform('mean')
    d.update(corr_v00_margin=float(pearsonr(X.v00, X.margin).statistic), corr_v00_interior=float(pearsonr(X.v00, X.interior).statistic),
             corr_margin_interior=float(pearsonr(X.margin, X.interior).statistic), n=int(len(X)))
    E_[f'{s_}_lowdose_margin_vs_interior'] = d
E_['iso_residual_lag1_corr'] = dict(observed_median=float(R.iso_resid_lag1_corr.median()), iid_null_median=float(np.median(lagnull)),
                                     iid_null_q05_q95=[float(np.quantile(lagnull, .05)), float(np.quantile(lagnull, .95))])
S['E_dependence'] = E_

# ---------------- summaries ----------------
def qs(x): x = pd.Series(x).dropna(); return dict(median=float(x.median()), q25=float(x.quantile(.25)), q75=float(x.quantile(.75)), n=int(len(x)))
cols = ['sigma_estimate', 'sigma_00_cell_total', 'sigma_well_rep_interior_pooledfile', 'sigma_indep_rep_interior_axisfactor', 'sigma_well_rep_block_own',
        'sigma_well_rep_at_e0', 'sigma_total_rep_interior_noblock',
        'sigma_block_calib_stratum', 'sigma_axis_calib_stratum', 'sigma_iso_lb', 'sigma_iso_lb_clipped', 'sigma_iso_cal', 'sigma_d2_robust', 'sigma_d2_rms_upper',
        'sigma_hill_h1', 'sigma_hill_h1_check', 'sigma_hill_unclipped_df4', 'block_factor_s', 'v00']
S['per_block_summary'] = {s: {c: qs(R[R.src == s][c]) for c in cols} for s in ('192', '18')}
S['per_block_summary']['all'] = {c: qs(R[c]) for c in cols}
S['frac_blocks_iso_lb_exceeds_hill_h1'] = float((R.sigma_iso_lb > R.sigma_hill_h1).mean())
S['frac_blocks_iso_lb_clipped_exceeds_hill_h1'] = float((R.sigma_iso_lb_clipped > R.sigma_hill_h1).mean())
S['frac_blocks_own_replicate_sd_exceeds_hill_h1'] = float((R.sigma_well_rep_block_own > R.sigma_hill_h1).mean())
S['frac_blocks_iso_cal_exceeds_hill_h1'] = float((R.sigma_iso_cal > R.sigma_hill_h1).mean())
S['frac_blocks_iso_lb_exceeds_h1_dial_rmse'] = float((R.sigma_iso_lb > R.rmse).mean())
S['median_ratio_sigma_estimate_over_hill_h1'] = float((R.sigma_estimate / R.sigma_hill_h1).median())
S['block_factor_sd_all_192'] = float(R[R.src == '192'].block_factor_s.std())
R.drop(columns=['hillrmA', 'hillrmB']).to_csv(OUT / 'noise_forensic.csv', index=False)
json.dump(S, open(OUT / 'noise_forensic.json', 'w'), indent=1, default=float)
print(json.dumps(S, indent=1, default=float))
