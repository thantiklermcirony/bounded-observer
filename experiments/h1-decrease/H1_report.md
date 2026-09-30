# H1 run: does the dial position track mechanistic overlap?

*30 Sept 2026. Pre-registered in `preregistration.md` before any fit. Code: `h1_dial.py` (primary) and the post-hoc block at the end of this file's companion CSVs. Data: DECREASE validation set (Ianevski et al. 2019), 210 blocks, 8x8 matrices, 36 drug pairs, 13 cell lines. NCI-ALMANAC and DrugComb were unreachable from this environment; this was the largest set of full matrices reachable.*

## Result: H1 fails the pre-registered test on this dataset

| Test | Spearman rho (overlap level vs alpha) | permutation p (one-sided, positive) | n |
|---|---|---|---|
| Primary: per-pair median alpha | **-0.12** | 0.76 | 36 pairs |
| Secondary: per-block alpha | -0.11 | 0.94 | 210 blocks |
| Raw single agents instead of Hill fits | -0.11 | 0.74 | 36 pairs |
| Slope-restricted (both Hill slopes in [0.5, 2]) | -0.13 | 0.75 | 30 pairs, 67 blocks |

Median alpha by overlap level (per pair): level 0 (distinct mechanisms) **0.24**; level 1 (same axis, different node) **-0.60**; level 2 (shared target, one pair, Everolimus/Dactolisib) **0.10**, with its ten cell lines split between alpha = -5 (four lines, strongly beyond Bliss) and alpha = 1 (five lines).

The direction is the opposite of H1 for level 1 versus level 0, and the single shared-target pair does not sit near 1. The pre-registered loss condition (rho <= 0 or p >= 0.05) is met three ways.

## What the dial can and cannot do here

- **Fit quality.** The dial's one parameter beats both fixed anchors in 60% of blocks, but only just: median RMSE 0.059 against 0.065 (Bliss) and 0.066 (odds-additive Loewe). The single-well noise floor is of that order.
- **Bounds.** Alpha sat at a bound in 65% of blocks (25% at the lower bound, 40% at alpha = 1). The dial is too narrow for these matrices: many are more antagonistic than odds-additivity, and many more synergistic than the range allows.
- **The Loewe landmark leaves the dial.** Checked on exact sham combinations: for Hill slope 1 the true Loewe surface is alpha = 1; for slope 2 the dial assigns it alpha = -3.5; for slope 3 it runs off the lower bound; for slope 0.5 it sits at 1 but fits poorly. With unequal maximal effects, Loewe is capped at the weaker drug's Emax and falls below every dial surface. In this dataset the median Hill slopes are 2.0 and 1.3, and only 32% of blocks have both slopes in [0.5, 2]. So the prediction "shared target implies alpha near 1" is only correct for full-efficacy, slope-1 agents, which are rare here.

## Reading

1. **As stated in the capstone (section 4.5), H1 is refuted on this dataset.** It should be reported as such, not softened.
2. **The failure is partly structural, not only empirical.** The dial is the complete one-horizon *projective* family. Real dose-response curves have Hill slopes away from 1 and partial efficacy, and Loewe additivity is projective only at slope 1 with full efficacy (capstone 4.3 already says this). The correct mechanistic prediction is therefore a statement about the Bliss and Loewe *surfaces* computed with each block's own Hill parameters, not about a single alpha. The dial remains a valid classification of projective laws; it is not a general synergy scale.
3. **The mechanistic annotation is mine, from primary targets, fixed before fitting.** Two pairs were flagged as ambiguous in advance. Changing them does not change the sign of the result.
4. **Dataset limits.** Chosen by its authors as novel combinations, so enriched for synergy; one shared-target pair only; single replicates. A run on NCI-ALMANAC or DrugComb, with many same-target pairs and replicates, is still worth doing, but H1 must be restated first, per point 2.

## What changes in the manuscript

- Section 4.5, H1: replace with a surface-level statement: "for agents with the same target, the combination surface follows Loewe additivity computed from the fitted single-agent curves; for independent mechanisms it follows Bliss; the dial position alpha is the correct summary only when both agents have Hill slope near 1 and full efficacy." Report this run as a first, failed test of the alpha form.
- Section 10.2 and section 13.3: cite this run; move H1 from [H] to "tested, failed in alpha form; restated".
- Section 15 register: H1 row becomes "refuted as stated (DECREASE); restated".
- Programme decision: the dial paper (Paper 2) is no longer the quick win. Either it becomes a negative-result-plus-restatement paper, or it waits for the restated H1 on a larger set.

## Files

`preregistration.md`, `h1_dial.py`, `h1_blocks.csv` (210 rows: alpha, slopes, RMSEs), `h1_pairs.csv`, `h1_results.json`, `h1_posthoc_blocks.csv` (Loewe calibration and the model-free Bliss-to-Loewe index t, which also shows no relation to overlap: rho = -0.11).

## Correction and independent reproduction (30 Sept 2026)

An external reviewer reran `h1_dial.py` on the public DECREASE files and reproduced the primary result exactly: Spearman rho = -0.12075, one-sided permutation p = 0.75582, 36 pairs. The same review found that the script's separate post-hoc Loewe calibration used a reversed bisection step (a dose-equivalence sum above 1 should raise the lower bound). That line is corrected in the current script; the original output is kept as `h1_results_v1_uncorrected_calibration.json`. After correction every primary and sensitivity statistic is identical to five decimals, and the calibration output still sits at the fitting bound alpha = 1, because with unequal maximal effects the Loewe surface lies below every dial surface. The calibration is therefore not used to support any mechanistic reading. The sham-combination values quoted in the manuscript (alpha = 1 at slope 1, -3.5 at slope 2, off the scale at slope 3) come from a separate solver that was already correct. The earlier statement in this report that four Everolimus/Dactolisib lines sat at alpha = -5 was also wrong: five lines are at alpha = 1 and five below zero, two of them at -5.
