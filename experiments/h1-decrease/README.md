# H1 on DECREASE: refuted as stated

**Dated local analysis plan:** `preregistration.md` says it was written before fitting. The
repository has no independent external timestamp for that sequence. Read the plan first.

**Claim.** For drug pairs, the position `alpha` on the one-horizon dial (capstone Theorem 8)
tracks mechanistic overlap: shared target near the Loewe end, independent mechanisms near Bliss.

**Result.** Refuted three ways. Primary test, per-pair median alpha against overlap level:
Spearman rho = **-0.12075**, one-sided permutation p = **0.75582**, n = 36 pairs. The direction
is opposite to the prediction, and the single shared-target pair split between the two ends of
the dial. The plan's loss condition (rho <= 0 or p >= 0.05) was met.

**Data.** DECREASE validation set (Ianevski et al. 2019): 210 blocks, 8x8 matrices, 36 drug
pairs, 13 cell lines. NCI-ALMANAC and DrugComb were unreachable from the analysis environment;
this was the largest set of full matrices available.

**Why it failed, in part structurally.** Loewe additivity sits on the dial only for Hill slope 1
with full efficacy. At slope 2 the true Loewe surface is at alpha = -3.5; at slope 3 it leaves
the dial's range. Median slopes here were 2.0 and 1.3, and only 32% of blocks had both slopes in
[0.5, 2]. The dial remains a valid classification of projective laws; it is not a general
synergy scale.

**Independent reproduction and a correction.** An external reviewer reran `h1_dial.py` on the
public files and reproduced the primary result exactly. The same review found that a separate
post-hoc Loewe calibration used a reversed bisection step. That line is corrected; the original
output is kept as `h1_results_v1_uncorrected_calibration.json`. After correction every primary
and sensitivity statistic is identical to five decimals.

**What replaced it.** H1 is restated as a claim about the Bliss and Loewe surfaces computed from
each block's own fitted single-agent curves, rather than about a single dial position. The
restated version awaits a dataset with many same-target pairs and replicates.

**Power, checked afterwards (3 October 2026).** On this design the Bliss and Loewe surfaces differ
by a median 0.010, half the single-agent noise and a seventh of the misfit of every law
(`../t1-power-audit/`). The refutation stands as stated, but this design could not have
separated the laws, so it carries little weight against the dial reading. The restated H1 faces
the same limit: any dataset used for it must first pass the power check there.

## Files

| File | What it is |
|---|---|
| `preregistration.md` | Dated local plan, stated to precede fitting |
| `h1_dial.py` | The analysis, with the bisection correction |
| `h1_blocks.csv` | 210 rows: alpha, Hill slopes, RMSEs |
| `h1_pairs.csv` | Per-pair medians and overlap annotation |
| `h1_results.json` | Primary and sensitivity statistics |
| `h1_posthoc_blocks.csv` | Loewe calibration and the model-free Bliss-to-Loewe index |
| `h1_results_v1_uncorrected_calibration.json` | Superseded output, kept for provenance |
| `H1_report.md` | The full report |

The DECREASE source files are not redistributed here; `h1_dial.py` names them and they are
available from the original publication.
