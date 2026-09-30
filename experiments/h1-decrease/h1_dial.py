"""H1: does the dial position alpha track mechanistic overlap? DECREASE 210-block set.
v2 (30 Sept 2026): corrected the reversed bisection step in the post-hoc Loewe calibration (found by an external reviewer). The primary test does not use it and is unchanged."""
import numpy as np, pandas as pd, json
from scipy.optimize import least_squares, minimize_scalar
from scipy.stats import spearmanr

rng = np.random.default_rng(0)
a = pd.read_excel('DECREASE/210_Novel_Anticancer_combinations/192_Combinations_.xlsx').assign(src='192')
b = pd.read_excel('DECREASE/210_Novel_Anticancer_combinations/18_combinations_.xlsx').assign(src='18')
df = pd.concat([a, b], ignore_index=True)
df['e'] = np.where(df.src == '192', 1 - df.Response / 100, df.Response / 100).clip(0, 1)

LEVEL = {
 ('ABT-199','Trametinib'):0, ('AVN944','Dactolisib'):0, ('BGB324','Everolimus'):1, ('BIIB021','Dactolisib'):0,
 ('BMS-754807','LY3009120'):1, ('BMS-754807','Trametinib'):1, ('Cisplatin','Everolimus'):0, ('Cisplatin','Ipatasertib'):0,
 ('Danusertib','Dactolisib'):0, ('Dasatinib','Dactolisib'):1, ('Dinaciclib','Dactolisib'):0, ('Entinostat','Trametinib'):0,
 ('Everolimus','Dactolisib'):2, ('Everolimus','Trametinib'):0, ('Floxuridine','Dactolisib'):0, ('GDC-0068','Dactolisib'):1,
 ('GDC-0068','Trametinib'):0, ('GSK269962','Trametinib'):0, ('Indibulin','Dactolisib'):0, ('Iniparib','Trametinib'):0,
 ('KX2-391','Trametinib'):1, ('Linsitinib','Trametinib'):1, ('NVP-LCL161','Trametinib'):0, ('Navitoclax','Dactolisib'):0,
 ('Navitoclax','Trametinib'):0, ('Nintedanib','Trametinib'):1, ('Olaparib','Trametinib'):0, ('Pictilisib','Trametinib'):0,
 ('Ponatinib','Trametinib'):1, ('Refametinib','Dactolisib'):0, ('SCH772984','Trametinib'):1, ('SNS-032','Dactolisib'):0,
 ('TAK-901','Dactolisib'):0, ('Teniposide','Dactolisib'):0, ('Tosedostat','Trametinib'):0, ('Trametinib','Dactolisib'):0}

def hill(d, emax, ec50, n): return emax * d**n / (ec50**n + d**n)
def fit_hill(d, e):
    d = np.asarray(d, float); e = np.asarray(e, float)
    best = None
    for n0 in (0.5, 1, 2):
        for ec0 in (np.median(d), d.min(), d.max()):
            try:
                r = least_squares(lambda p: hill(d, *p) - e, [min(max(e.max(),0.05),1), ec0, n0],
                                  bounds=([0, d.min()/100, 0.1], [1, d.max()*100, 10]))
                if best is None or r.cost < best.cost: best = r
            except Exception: pass
    return best.x, np.sqrt(2*best.cost/len(d))

def dial(a_, b_, al):
    den = 1 - al * a_ * b_
    return (a_ + b_ - (1 + al) * a_ * b_) / np.where(np.abs(den) < 1e-9, 1e-9, den)

def fit_alpha(ea, eb, eobs, lo=-5, hi=1):
    f = lambda al: np.mean((dial(ea, eb, al) - eobs)**2)
    r = minimize_scalar(f, bounds=(lo, hi), method='bounded')
    # guard against local minima: coarse grid check
    grid = np.linspace(lo, hi, 121); g = np.array([f(x) for x in grid]); k = g.argmin()
    if g[k] < r.fun: r = minimize_scalar(f, bounds=(max(lo, grid[k]-0.1), min(hi, grid[k]+0.1)), method='bounded')
    return r.x, np.sqrt(r.fun)

rows = []
for (src, pid), blk in df.groupby(['src', 'PairIndex']):
    d1, d2, cell = blk.Drug1.iloc[0], blk.Drug2.iloc[0], blk.Cell.iloc[0]
    c1 = np.sort(blk.Conc1.unique()); c2 = np.sort(blk.Conc2.unique())
    M = blk.pivot_table(index='Conc1', columns='Conc2', values='e').loc[c1, c2].values
    eA_raw = M[1:, 0]; eB_raw = M[0, 1:]
    (emA, ecA, nA), rmA = fit_hill(c1[1:], eA_raw); (emB, ecB, nB), rmB = fit_hill(c2[1:], eB_raw)
    eA = hill(c1[1:], emA, ecA, nA); eB = hill(c2[1:], emB, ecB, nB)
    EA, EB = np.meshgrid(eA, eB, indexing='ij'); Eobs = M[1:, 1:]
    ok = ~np.isnan(Eobs)
    al, rmse = fit_alpha(EA[ok], EB[ok], Eobs[ok])
    EAr, EBr = np.meshgrid(eA_raw, eB_raw, indexing='ij'); al_raw, _ = fit_alpha(EAr[ok], EBr[ok], Eobs[ok])
    rm_bliss = np.sqrt(np.mean((dial(EA[ok], EB[ok], 0) - Eobs[ok])**2))
    rm_loewe = np.sqrt(np.mean((dial(EA[ok], EB[ok], 1) - Eobs[ok])**2))
    # the alpha that the dial assigns to a true Loewe surface with these Hill curves (slope calibration)
    def loewe_e(dA, dB):
        # solve dA/DA(e)+dB/DB(e)=1 with DA(e)=ecA*(e/(emA-e))^(1/nA) (Emax-scaled Hill), by bisection on e
        lo_, hi_ = 0.0, min(emA, emB) - 1e-9
        if hi_ <= 0: return 0.0
        for _ in range(60):
            mid = (lo_ + hi_) / 2
            DA = ecA * (mid / (emA - mid))**(1/nA) if mid < emA else np.inf
            DB = ecB * (mid / (emB - mid))**(1/nB) if mid < emB else np.inf
            s = dA / DA + dB / DB
            # s falls as the trial effect rises: s > 1 means the doses exceed what effect `mid` needs, so the true effect is larger
            if s > 1: lo_ = mid
            else: hi_ = mid
        return (lo_ + hi_) / 2
    EL = np.array([[loewe_e(x, y) for y in c2[1:]] for x in c1[1:]])
    al_L, _ = fit_alpha(EA[ok], EB[ok], EL[ok], lo=-5, hi=1)
    key = (d1, d2) if (d1, d2) in LEVEL else (d2, d1)
    rows.append(dict(src=src, pid=pid, d1=d1, d2=d2, cell=cell, level=LEVEL[key], alpha=al, alpha_raw=al_raw, rmse=rmse,
                     rmse_bliss=rm_bliss, rmse_loewe=rm_loewe, nA=nA, nB=nB, emaxA=emA, emaxB=emB, hillrmA=rmA, hillrmB=rmB,
                     alpha_loewe_calib=al_L, mean_e=float(np.nanmean(Eobs))))
R = pd.DataFrame(rows)
R.to_csv('h1_blocks.csv', index=False)

def perm_p(x, y, n=10000):
    obs = spearmanr(x, y).statistic
    cnt = sum(spearmanr(rng.permutation(x), y).statistic >= obs for _ in range(n))
    return obs, (cnt + 1) / (n + 1)

P = R.groupby(['d1', 'd2']).agg(level=('level', 'first'), alpha=('alpha', 'median'), alpha_raw=('alpha_raw', 'median'),
                                 n=('cell', 'size'), nA=('nA', 'median'), nB=('nB', 'median')).reset_index()
P.to_csv('h1_pairs.csv', index=False)
out = {}
rho, p = perm_p(P.level.values, P.alpha.values); out['primary_pairs'] = dict(rho=rho, p=p, n=len(P))
rho2, p2 = perm_p(R.level.values, R.alpha.values); out['secondary_blocks'] = dict(rho=rho2, p=p2, n=len(R))
rhor, pr = perm_p(P.level.values, P.alpha_raw.values); out['raw_single_agents_pairs'] = dict(rho=rhor, p=pr)
sub = R[(R.nA.between(0.5, 2)) & (R.nB.between(0.5, 2))]
Ps = sub.groupby(['d1', 'd2']).agg(level=('level', 'first'), alpha=('alpha', 'median')).reset_index()
rhos, ps = perm_p(Ps.level.values, Ps.alpha.values); out['slope_restricted_pairs'] = dict(rho=rhos, p=ps, n_pairs=len(Ps), n_blocks=len(sub))
def boot_med(x, n=4000):
    x = np.asarray(x); return np.percentile([np.median(rng.choice(x, len(x))) for _ in range(n)], [2.5, 97.5])
lev = {}
for L in (0, 1, 2):
    x = P[P.level == L].alpha.values; xb = R[R.level == L].alpha.values
    lev[L] = dict(pairs=len(x), median_pair_alpha=float(np.median(x)) if len(x) else None,
                  ci=list(map(float, boot_med(x))) if len(x) > 1 else None, blocks=len(xb), median_block_alpha=float(np.median(xb)),
                  block_ci=list(map(float, boot_med(xb))))
out['levels'] = lev
out['fit_quality'] = dict(median_rmse_dial=float(R.rmse.median()), median_rmse_bliss=float(R.rmse_bliss.median()),
                          median_rmse_loewe=float(R.rmse_loewe.median()),
                          frac_dial_beats_both=float(((R.rmse < R.rmse_bliss) & (R.rmse < R.rmse_loewe)).mean()),
                          frac_alpha_at_lower_bound=float((R.alpha <= -4.99).mean()), frac_alpha_at_upper_bound=float((R.alpha >= 0.999).mean()))
out['everolimus_dactolisib_blocks'] = R[R.level == 2][['cell', 'alpha', 'alpha_loewe_calib', 'nA', 'nB', 'rmse']].round(3).to_dict('records')
out['hill_slopes'] = dict(median_nA=float(R.nA.median()), median_nB=float(R.nB.median()), frac_both_in_half_two=float(((R.nA.between(.5, 2)) & (R.nB.between(.5, 2))).mean()))
out['loewe_calibration'] = dict(median_alpha_dial_assigns_to_true_loewe=float(R.alpha_loewe_calib.median()), iqr=list(map(float, R.alpha_loewe_calib.quantile([.25, .75]))))
json.dump(out, open('h1_results.json', 'w'), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
print(P.sort_values(['level', 'alpha']).to_string())
