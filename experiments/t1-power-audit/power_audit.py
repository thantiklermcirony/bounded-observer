"""T1 power audit (review 2026-10-03, D1): could H1's design separate the dial laws it compared?
Loss condition, stated in the review before this ran: if the median predicted gap between the
compared laws, across the 210 blocks, is at least 3x the noise, lack of power does not explain H1.
Noise: per-block single-agent Hill-fit residual RMSE (DECREASE has no replicate wells)."""
import numpy as np, pandas as pd, json, re
import pathlib
src = (pathlib.Path(__file__).resolve().parents[1] / 'h1-decrease' / 'h1_dial.py').read_text()
exec(src.split('rows = []')[0])          # data loading, LEVEL, hill, fit_hill, dial, fit_alpha: unchanged
out = []
for (s, pid), blk in df.groupby(['src', 'PairIndex']):
    c1 = np.sort(blk.Conc1.unique()); c2 = np.sort(blk.Conc2.unique())
    M = blk.pivot_table(index='Conc1', columns='Conc2', values='e').loc[c1, c2].values
    (emA, ecA, nA), rmA = fit_hill(c1[1:], M[1:, 0]); (emB, ecB, nB), rmB = fit_hill(c2[1:], M[0, 1:])
    EA, EB = np.meshgrid(hill(c1[1:], emA, ecA, nA), hill(c2[1:], emB, ecB, nB), indexing='ij')
    ok = ~np.isnan(M[1:, 1:]); a, b = EA[ok], EB[ok]
    sig = np.sqrt((rmA**2 + rmB**2) / 2)
    g_BL = dial(a, b, 0) - dial(a, b, 1)           # Bliss vs Loewe end
    g_Bm = dial(a, b, 0) - dial(a, b, -3)          # Bliss vs the negative side H1 also used
    out.append(dict(src=s, pid=pid, sigma=sig, rms_BL=np.sqrt(np.mean(g_BL**2)), rms_Bm=np.sqrt(np.mean(g_Bm**2)),
                    frac_cells_BL_gt_2sig=np.mean(np.abs(g_BL) > 2 * sig), max_e=float(np.nanmax(M)),
                    mean_ab=float(np.mean(a * b))))
R = pd.DataFrame(out)
R['ratio_BL'] = R.rms_BL / R.sigma; R['ratio_Bm'] = R.rms_Bm / R.sigma
res = dict(blocks=len(R), median_sigma=R.sigma.median(), median_rms_gap_bliss_loewe=R.rms_BL.median(),
           median_ratio_bliss_loewe=R.ratio_BL.median(), median_ratio_bliss_alpha_minus3=R.ratio_Bm.median(),
           frac_blocks_ratio_BL_ge_3=float((R.ratio_BL >= 3).mean()), frac_blocks_ratio_BL_lt_1=float((R.ratio_BL < 1).mean()),
           median_frac_cells_gap_gt_2sigma=R.frac_cells_BL_gt_2sig.median(), median_mean_ab=R.mean_ab.median(),
           loss_condition_met=bool(R.ratio_BL.median() >= 3))
H = pd.read_csv(pathlib.Path(__file__).resolve().parents[1] / 'h1-decrease' / 'h1_blocks.csv', dtype={'src': str})
m = R.merge(H[['src', 'pid', 'rmse', 'rmse_bliss']], on=['src', 'pid'])
res['median_gap_over_bliss_misfit'] = float((m.rms_BL / m.rmse_bliss).median())
res['frac_blocks_gap_exceeds_misfit'] = float((m.rms_BL > m.rmse_bliss).mean())
R.to_csv('power_audit_blocks.csv', index=False); json.dump(res, open('power_audit.json', 'w'), indent=1, default=float)
print(json.dumps(res, indent=1, default=float))
print(R[['ratio_BL','ratio_Bm','sigma','rms_BL','mean_ab']].describe().round(3).to_string())
