# Method records, verbatim

These are the two estimating agents' own statements of method, contents, dependence and caveats,
copied verbatim from the stopped workflow's journal (run wf_303dafb2-606, 3 October 2026).
They are records of what was claimed, not findings accepted by the programme.

## noise_modelfree.py

### method

Each of the 210 DECREASE blocks is an 8x8 grid with 64 wells. I used H1's own loader by exec of h1_dial.py, so the effect is H1's clipped e. I estimated noise with no composition law and no Hill form, in five ways.

(W) PRIMARY, sigma_estimate. A tensor-product discrete smoothing spline on the dose-index grid. It penalises second differences along each dose axis, with a separate smoothing parameter per axis (a 33x33 log grid, 1e-4 to 1e4). The residual is the leave-one-out (LOO) prediction error under NESTED CV: for each held-out well, the smoothing parameters are chosen by an inner LOO on the other 63 wells only. Exact rank-one downdates make this cheap. They were verified against brute-force refits to 1e-15 (check_formulas.py).

(T) An isotropic thin-plate smoothing spline with the same nested-CV protocol. Its hat matrix matches scipy's RBFInterpolator to 2e-14.

(I) 2-D isotonic regression, monotone in both doses, solved as a QP with quadprog. It has no tuning. The LOO prediction is the midpoint of the interval that the monotone fit on the other 63 wells allows at the held-out well.

(D) Difference estimators with no fit at all: a Laplacian pseudo-residual and second differences.

(R) Replicate single-agent series. The same drug, cell line and dose vector were measured in different blocks: 1116 series pairs, which are not independent.

I also report:
- df-corrected in-sample SDs for W, T and I. W and T use RSS/(n - tr(2H - HH')); I uses n minus the number of level sets.
- The untreated (0,0) well, whose expected raw effect is 0.
- Every estimator on the unclipped raw scale.

I checked the estimators against known truth. The truth was each block's H1 dial surface (60 blocks), with iid Gaussian noise added at sigma = 0.02, 0.05 and 0.10, with and without clipping. H1's Hill-residual proxy was rerun on the same synthetic data.

Comparators come from h1_blocks.csv:
- the T1 proxy, sqrt((hillrmA^2 + hillrmB^2)/2);
- the dial misfit rmse. Recomputing it from the residuals reproduces h1_blocks.csv to within 1e-6.

Dependence:
- Within blocks: lag-1 row and column autocorrelation of the residuals, and the share of residual sum of squares explained by additive row and column effects. Each is compared with a null simulated per block from the same smoother under iid noise (2000 draws). Excess is tested across blocks and at pair level (Wilcoxon, n = 36).
- Across blocks: one-way ICC by drug pair and by cell line, with permutation p-values, for alpha, mean Bliss excess, sigma, dial rmse and log(dial rmse/sigma). Also the correlation of 64-well residual patterns between blocks, by relation class, with a pair-label permutation test within each file.

### what_this_estimate_contains

It is not noise alone. It is noise plus some unexplained structure, and on this data it reads high relative to the true noise.

A cross-validated residual from a flexible fit is an upper-bound-ish mix of noise and unexplained structure. In expectation, LOO MSE = sigma^2 + Var(the held-out prediction) + bias^2. It therefore exceeds the noise variance even for an unbiased smoother, and any real structure the smoother cannot follow is added on top: sharp sigmoids on a 3-fold grid, hormesis, plate artefacts.

The synthetic test calibrates the gap. W nested CV overstates the realised noise by:
- 1.36x at sigma = 0.02 (0.02718 vs 0.01995);
- 1.21x at sigma = 0.05 (0.06023 vs 0.04976);
- 1.15x at sigma = 0.10 (0.11451 vs 0.0994).

The df-corrected W is within about 6% of truth: 0.02121, 0.04963 and 0.09804 against the same three values.

On the real data the medians are:
- W nested-CV RMSE: 0.03662344, IQR 0.02974 to 0.05373.
- W CV on interior wells only: 0.03436.
- W df-corrected: 0.02666.
- T CV: 0.03800.
- I CV: 0.05349. Midpoint prediction is crude, so I CV is the most inflated; I df-corrected is 0.02720.
- Difference estimators: 0.03818 and 0.04233.
- Replicate-series sigma: 0.03577 (n = 42) and 0.04083 (n = 204).

Evidence that part of the CV residual is reproducible structure rather than noise: the residuals correlate across separate blocks (see dependence_findings). Plausible range for per-well noise on H1's clipped scale: roughly 0.027 (df-corrected) to 0.037 (nested CV).

Clipping shapes all of this. H1's clip to [0,1] truncates 27.75% of wells, raw e < 0, because the 192 file has viability above 100%. On the raw scale the median W CV is 0.04755 and df-corrected 0.03531. The noise is strongly heteroscedastic:
- Clipped e: pooled CV residual RMS is 0.0239 where the fitted effect is below 0.02, and 0.0703 for fitted effects between 0.1 and 0.3.
- Raw e: about 0.074 at low effect and 0.034 above 0.9.

### dependence_findings

WITHIN BLOCKS. The residuals are positively dependent beyond what iid noise allows.

W smoother residuals are negatively autocorrelated by construction. The question is whether they are less negative than the iid null:
- Lag-1 along rows: median observed -0.2632 vs null -0.3473. Mean excess +0.1504; one-sided t across blocks p = 6.4e-25; pair-level Wilcoxon p = 2.9e-11 (n = 36). 37.1% of blocks have p < 0.05.
- Lag-1 along columns: excess +0.1444, p = 1.3e-15 and 9.3e-09. 30.0% of blocks have p < 0.05.
- Additive row and column effects explain a median 0.2399 of residual SS against a null of 0.1218. Excess +0.1341, p = 1.3e-36. 41.4% of blocks have p < 0.05.

This is either correlated measurement error, such as dispensing or row/column artefacts, or smooth structure the smoother left behind. These data cannot separate the two. The grid is the dose grid, and the physical plate layout is unknown.

Dial residuals, on the 49 interior wells, are strongly spatially structured: lag-1 median 0.4518 along rows and 0.4596 along columns. Bliss residuals are similar, 0.4794 and 0.4915. The dial misfit is therefore systematic model error, not noise.

The effective number of wells per block is well below 49.

ACROSS BLOCKS. Blocks are not 210 independent observations.

ICC for alpha:
- By drug pair: 0.1273 (permutation p = 0.0075), design effect 1.61.
- By cell line: 0.1551 (p = 0.0005), design effect 3.28.

Other quantities:
- log(dial rmse / model-free sigma) clusters by pair: ICC 0.2752, p = 0.0005.
- Dial rmse: ICC 0.1228 by pair (p = 0.0145) and 0.3953 by cell line.
- Model-free sigma is a cell-line property: ICC 0.6016 by cell line (0.7965 on raw e), but 0.0105 by pair (p = 0.368).
- Mean Bliss excess: ICC 0.2734 by cell line, 0.0735 by pair (p = 0.070).

Residual-pattern correlation between blocks.

Model-free CV residuals:

| Relation between blocks | Mean correlation |
|---|---|
| Same pair, different cell line | 0.0969 |
| Same cell line, shared drug | 0.1186 |
| Same cell line, no shared drug | 0.0544 |
| Unrelated, same file | 0.0431 |

The same-pair excess has permutation p = 0.001 (null mean 0.0457).

Dial residuals:

| Relation between blocks | Mean correlation |
|---|---|
| Same pair, different cell line | 0.1449 |
| Same cell line, shared drug | 0.0944 |
| Unrelated, same file | 0.0258 |

The same-pair excess has p = 0.001.

So the dial misfit pattern is partly reproducible per drug pair. That is systematic model error, or compound-specific dose or dispensing error, and it is not averaged away by adding cell lines.

CALIBRATION. These quantities bear on calibration uncertainty. They are not a full audit of it.
- The untreated (0,0) well in the 192-file blocks has raw e mean -0.0000927, SD 0.1185 and MAD-SD 0.0775, although its expected value is 0. That is about twice the within-block noise, which points to block-level offsets.
- Replicate single-agent series split into a between-plate offset and a within-series part:
  - Clipped e: offset SD 0.0363, within-series 0.0409.
  - Raw e: offset SD 0.0621, within-series 0.0573.
- A shared offset moves every well in a block together, so it acts as correlated, calibration-type error on the single-agent curves that feed every law's prediction.

### caveats

1. This tightens the T1 audit's noise yardstick. It does not confirm it.

The T1 proxy (median 0.01981) is biased low, for three reasons:
- In 27.1% of blocks the drug-A Hill RMSE is below 1e-4, because clipping leaves flat all-zero series that a Hill curve fits exactly. The figure is 4.8% for drug B.
- RMSE divides by n = 7 while ignoring 3 fitted parameters per curve; df-corrected, the median is 0.02620.
- On synthetic truth with clipping, the proxy recovers only 0.61 to 0.65 of the realised noise (0.01128/0.01839, 0.02907/0.04578, 0.05571/0.08545).

Model-free sigma exceeds the Hill proxy in 91.9% of blocks, with a median ratio of 1.865. Spearman correlation with the proxy is only 0.445.

2. What this does to "the test could never distinguish the laws". The statement is not supported as a statement about noise, and needs narrowing in a different direction.

Per well, the rival laws differ by little relative to the model-free noise. Median RMS gaps over the 49 interior wells, using H1's Hill marginals:
- Bliss vs Loewe end: 0.01020, which is 0.263x the interior CV sigma and 0.336x the df-corrected sigma. It exceeds the interior CV sigma in only 11.4% of blocks.
- Einstein vs Bliss: 0.00803, which is 0.210x the interior CV sigma.
- Einstein vs Loewe: 0.01842.

But small gaps accumulate. Under iid noise, known marginals and one law exactly true:
- The per-block separation, sqrt(sum gap^2)/sigma, has median 1.84 for Bliss vs Loewe and 1.47 for Einstein vs Bliss.
- Pooled over 210 blocks it would be 65.77 and 42.04 sigma.

So noise alone does not make the laws indistinguishable on this data. The binding limits are three:
- Model error. The dial misfit exceeds model-free interior noise in 89.5% of blocks (96.2% against the df-corrected value). The implied model-error RMS has a median of at least about 0.0418, which is larger than the Bliss-Loewe gap in 77.1% of blocks and than the Einstein-Loewe gap in 67.6%.
- Structured, reproducible misfit and dependence, both within and across blocks.
- Calibration. Block offsets are large, and the Hill marginals that define every law's prediction are uncertain.

The separation figures fix the marginals and ignore all three limits. They are a ceiling, not H1's power. A power calculation that propagates the marginal-fit uncertainty, the alpha fit and the dependence is still owed by the full audit.

3. None of this is evidence for the framework, and H1's refutation stands as recorded: rho = -0.12075, p = 0.75582. At most it narrows what the failure says. Alpha here is fitted against structured misfit that is larger than the gaps between laws, so alpha mostly reflects how that misfit projects onto the a·b direction. That reading is a hypothesis. It is not shown here.

4. Limits of the estimators:
- Smoothers on the dose-index grid treat the zero dose as one step below the lowest dose. Spacing is not always uniform: some Trametinib series run 0.003, 0.1, ...
- Isotonic regression assumes monotone effect, so any hormesis inflates it.
- GCV and LOO picked the same smoothing parameters in only 11.9% of blocks. In 29.0% of blocks at least one axis's parameter sat at the grid minimum, i.e. near-interpolation along that axis. Nested CV keeps this honest for prediction error.
- Positive residual correlation biases GCV/LOO toward undersmoothing. That would pull CV sigma down and hide some correlation.
- Replicate pairs come from groups of up to 15 series, so they are not independent, and their differences include potency shifts.
- The 18-file blocks appear to be clipped and normalised differently by the authors: the control well's median raw e is 0.000546.
- The plate layout is unknown, so "neighbouring wells" means neighbours on the dose grid.
- Numbers are exactly as computed with seed 20261003. The run takes about 3.5 minutes.

Other outputs: /tmp/claude-0/stage1/h1/noise_modelfree_summary.json (pooled statistics, synthetic check, dependence tests) and /tmp/claude-0/stage1/h1/replicate_pairs.csv. /tmp/claude-0/stage1/h1/check_formulas.py verifies the formulas against brute force.

Nothing in any repository was modified.

Reported median_sigma: 0.03662344479259927; IQR: [0.029737239330674764, 0.053732673263038794]

## noise_forensic.py

### method

Data: the two DECREASE files in /tmp/claude-0/h1run/DECREASE (192_Combinations_.xlsx with % viability, and 18_combinations_.xlsx with % inhibition, converted to viability as 100-Response). Everything was computed on the unclipped effect scale e = 1 - v/100. H1 itself used e clipped to [0,1].

STEP 1, what replication exists. Inside a block there is none: 0 duplicate cells, 0 repeated (pair, cell line) blocks, and the two files share no cell lines (they share no pairs either). description.txt cites the paper as "[to be filled]", and nature.com is blocked here (HTTP 403), so the replicate design and plate layout are not documented in any source I could reach.

There are, however, genuine replicates ACROSS blocks:
- Single-agent wells with the same drug, dose and cell line: 224 groups / 1578 wells in the 192 file and 84 groups / 168 wells in the 18 file. These come mostly from the anchors Trametinib and Dactolisib, which appear in every 192-file block. No group has identical values, so these wells were not copied between blocks.
- The (0,0) wells: one per block, giving 12 or 30 per cell line in the 192 file. Their per-line mean equals 100.00 in 4 lines and lies within 0.17 of 100 in the rest. Every line that misses exactly 100 except HCC1599 contains one of the 6 blocks whose values are whole-number %. This points to normalisation against the jointly pooled (0,0) wells of each line, but that is an inference, not documented.

STEP 2, estimate noise from those replicates. Within each (file, cell line) stratum I fitted v_bg = s_unit * m_g + eps with Var(eps) = a^2 + (c*m)^2, using weighted ALS plus maximum likelihood, with squared residuals df-corrected by n/(n-p). I fitted three nested versions:
- no factor: the total spread across blocks;
- one multiplicative factor per block: this removes a block-level calibration error;
- one factor per single-agent axis of a block.

The headline sigma_estimate is the per-block-factor well SD, taken from the stratum's variance function evaluated at the block's 49 interior viability levels (RMS over the 49).

STEP 3, model-free checks inside each block (no replicates needed):
- **Isotonic lower bound (iso_lb).** This is the RMS residual of the exact bivariate isotonic projection of the full 8x8 matrix (Dykstra with a vectorised PAVA, checked against scipy). If the true surface is monotone in both doses, it is a deterministic lower bound on the realised RMS of the well errors. I computed it on both the unclipped scale and H1's clipped scale.
- **Calibrated isotonic estimate (iso_cal).** This is the sigma at which simulated isotonic RMS matches the observed value, using the block's own isotonic fit as the plug-in truth. In simulation under iid noise it recovers the true sigma within about 5% for flat, typical and steep surfaces (noise_forensic_validate_iso.py).
- **Second differences.** Pseudo-residuals from second differences along each log-dose axis, which are biased upward by surface curvature.

STEP 4, comparison with H1's yardstick. H1's single-agent Hill residual was reproduced exactly (median 0.01981).

STEP 5, dependence and calibration:
- Share of replicate variance removed by the block and axis factors.
- Agreement of the scale estimated separately from axis 1, axis 2 and the (0,0) well.
- Whether low-dose margin deviations carry into the lowest-dose interior wells, using deviations from the cell-line mean.
- Lag-1 correlation of isotonic residuals, compared with an iid null simulated at iso_cal.

### what_this_estimate_contains

**Short answer:** this is measurement noise, not model error. It is built only from deviations between wells that should share one true value (same drug, dose and cell line, in different blocks), so no combination law or single-agent curve enters it. Two independent instruments agree with it:
- the within-block isotonic estimate iso_cal: median 0.04666 overall, 0.04847 in the 192 file; Spearman 0.744 with sigma_estimate across the 210 blocks;
- the robust second-difference estimate: median 0.03911.

**What it still contains:**
- Well-to-well error, including reading noise and seeding noise.
- Any block-by-dose deviation that a single multiplicative block factor cannot absorb. Two parts of this are measurable:
  - Axis-specific shared deviations: adding per-axis factors lowers the median to 0.03653 overall (0.03768 in the 192 file).
  - Potency drift between blocks, which looks small: the replicate SD does not peak at mid-range viability (192 file, axis model: 3.40 at 30-50%, 4.78 at 50-70%, 7.06 at ≥90% viability, in % points).

**What it excludes:**
- The block-level calibration factor, reported separately as sigma_block_calib_stratum (192 median 0.04682).
- Any plate-position bias that is the same in every block. That is absorbed into the group means and invisible to this method.

**How it reaches the interior wells:** it is carried there through the variance function fitted on single-agent and (0,0) wells, which assumes interior wells share it.

**Scale:** it is on the unclipped scale. On H1's clipped scale the effective error differs, because roughly half the errors at e≈0 are censored and the clipping adds bias.

**Total per-well error at e=0:** the model-free SD of the (0,0) wells per cell line is 0.0480 to 0.1513 (median per 192-file block 0.10013), with MDAMB-436 at 0.3408. This includes the block-level component.

### dependence_findings

**1. A shared block-level error is large.** Across blocks, a single multiplicative factor per block removes 49.1% (192 file) and 50.3% (18 file) of the single-agent replicate variance. Per-axis factors remove 52.5% and 43.2%. The bias-corrected SD of the block factor by stratum is:
- 0.0404 to 0.0857 in the regular 192-file lines;
- 0.1996 in MDAMB-436 and 0 in HCC1599 (where it is swamped by well noise of about 16%);
- 0.0190 to 0.0678 in the 18 file.

Rough intra-block correlation at e≈0, from the medians: 0.04682^2 / (0.04682^2 + 0.05011^2) = 0.466. This is an approximate value.

**2. The block error carries into the combination wells.** In the 192 file (n=192), deviations from the cell-line mean correlate as follows:
- (0,0) vs low-dose margin: r = 0.804
- (0,0) vs the 2x2 lowest-dose interior wells: r = 0.542
- margin vs interior: r = 0.754

Scale estimated from axis 1 vs axis 2: r = 0.335 (n=39). From (0,0) vs axis 2: r = 0.427 (n=202). From (0,0) vs axis 1: r = 0.529 (n=46). So the 49 interior wells of a block are not independent observations. A shared calibration error of about 0.047 x (1-e) moves the whole block, single agents and combinations together.

**3. A systematic baseline offset.** In the 192 file the (0,0) wells average 100.01. The two lowest single-agent doses average 103.67 and the lowest-dose interior wells average 105.94 (interior minus margin: mean 2.27, SD 6.28). This means a zero-effect reference that sits 3.7 to 5.9 points above the normalisation control, or low-dose hormesis; these data cannot tell the two apart. H1's Hill fits force e(0)=0, so this offset becomes model or calibration error inside every dial fit. In the 18 file the low doses are not inactive (margin 87.77, interior 77.86), so this check does not apply there.

**4. Neighbouring wells inside a block are correlated.** The median lag-1 correlation of isotonic residuals is 0.0856, against an iid-null median of -0.112 (90% interval -0.299 to 0.050). 55.7% of blocks exceed the null's 95th percentile. This is either positively correlated well errors or smooth non-monotone structure (for example hormesis), and I cannot separate the two. Either way, treating the 49 cells as independent overstates the effective sample size. Positive correlation would also bias iso_cal low.

### caveats

1. **Scope.** This task is noise forensics only. It narrows the T1 audit; it is not a power result and not evidence for the framework. H1 remains refuted as recorded (rho = -0.12075, p = 0.75582).

2. **T1's noise yardstick was too small.** T1 used H1's Hill residual, median 0.01981. That is below:
   - the block's own replicate-based single-agent SD in 82.4% of blocks;
   - iso_cal in 89.0% of blocks;
   - the hard monotone lower bound in 80.5% of blocks, and 61.4% even on H1's own clipped scale.

   The median ratio of sigma_estimate to the Hill residual is 2.193. Hill residuals here understate measurement noise because of clipping at e=0, dividing by 7 rather than 4 degrees of freedom, and the bounded Emax. Unclipped with 4 degrees of freedom, the median Hill residual is 0.06895, which then includes curve-model error.

   In the 18 file the Hill residual (0.03316) exceeds the replicate noise (0.02562). There it does mix in model error, which is the author's point (i).

   This makes T1's per-cell gap/noise ratios smaller still. But per the author's point (ii), a per-cell ratio does not decide whether the laws can be told apart. That needs aggregation over cells and blocks, using the dependence structure above (shared block factor, neighbour correlation) and calibration uncertainty, across every rival on the dial including alpha = -1. That analysis is not done here.

3. **Not verified from the original source.** The paper was unreachable (nature.com returns HTTP 403), so the replicate design, plate layout and normalisation are inferred from the data. The pooled (0,0) normalisation in particular is an inference.

4. **The 18 file is censored.** Its values are bounded at 0 and 100% inhibition: 8.2% of wells sit at a bound and 50% of its (0,0) wells are exactly 0. Noise estimates near e=0 are biased low there.

5. **Small data quirks.**
   - 6 blocks in the 192 file are whole-number % (pids 1, 3, 59, 87, 131, 141). The rounding adds about 0.29 points of SD, which is negligible.
   - The lowest Trametinib dose is labelled 0.003 in the 15-block lines and 0.03 in the 8-block lines. It is consistent within each line, so the replicate grouping is unaffected; the label itself remains unresolved.

6. **Statistical approximations.** The df correction is applied per stratum (n/(n-p)) rather than per observation. The likelihood is Gaussian, with a two-parameter variance function fitted by grid search (some strata hit grid edges, a = 0.05 or c = 0). Robust SDs are given in the JSON and are similar.

7. **Two very noisy cell lines.** HCC1599 (sigma_estimate 0.1624) and MDAMB-436 (0.1834; (0,0) SD 0.3408) are extreme. Any pooled analysis should report results with and without them.

8. **Per-block values are mostly per-stratum.** sigma_estimate is a cell-line value evaluated at each block's interior levels. The per-block replicate column (sigma_well_rep_block_own, with n_own wells) and iso_cal give genuinely block-specific values but are noisier.

9. **Other files in the output folder are not mine.** noise_modelfree.*, replicate_pairs.csv and check_formulas.py in /tmp/claude-0/stage1/h1 were not written by this task, and I did not inspect or reconcile them.

Full numbers are in /tmp/claude-0/stage1/h1/noise_forensic.json and the iso validation script is /tmp/claude-0/stage1/h1/noise_forensic_validate_iso.py.

Reported median_sigma: 0.04191; IQR: [0.03557, 0.04914]

