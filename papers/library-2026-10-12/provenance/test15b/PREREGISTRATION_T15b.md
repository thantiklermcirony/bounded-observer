# T15b confirmatory pre-registration: clock plus hidden variety, on new data

Frozen 12 Oct 2026, about 15:46 AEDT (file-system time records the exact moment), before any curvature was computed on these data. Only column names, read depths and lineage labels were inspected.

**Data.** Kinsler, Geiler-Samerotte and Petrov (2020), *eLife* 9:e61271: barcode counts in `data/BarcodeCounts_merged+flaskswapcorrected_092519_withBCinfo.csv` from github.com/grantkinsler/1BigBatch (commit `ffdda5d1`; file SHA-256 prefix `bab7e6fce5547267`). There are 550 barcoded yeast lineages, of which the single `Ancestor` barcode is excluded. These data were never used in developing the model.

**Frozen code.** `run_t15b.py` (SHA-256 prefix `b93ad69fc474060f`), which imports `../test15/logit_curvature.py` (SHA-256 prefix `47578ba2bcf72dc2`). The code runs once. Any later change is reported as a deviation.

**Model under test**, frozen from Doc 12 exploratory E2: one common selection clock per experiment, plus a constant fitness per lineage. These are fitted by count-weighted least squares on the training replicate cultures. The prediction is $D_{\rm pred}$, the second differences of $\log\sum_{i\in A}N_i(0)e^{s_i\tau_t}-\log\sum_{i\notin A}N_i(0)e^{s_i\tau_t}$ in the held-out culture, compared with $D_{\rm obs}$ from the held-out culture's aggregate group reads.

**Decision set (primary).** Experiments 3, 6, 13, 18, 20, 21 and 23, each with 3 replicate cultures. Each culture is held out in turn and the other two train.

- Experiments with a T0 column use T0 to T4; experiments 18 and 20 use T1 to T4.
- An (experiment, replicate) pair is excluded if any column has fewer than 100,000 reads (the depth rule).

**Groups**, predefined from the annotations, each against the rest of the pool:

- `class` values with at least 8 lineages: Diploid, NotSequenced, PKA, other, ExpNeutral, Adaptive Diploid;
- `gene` values with at least 10 lineages: Diploid, NotSequenced, other, IRA1, GPB2, PDE2, IRA2.

**Verdict.**

- **PASS** if the slope of $D_{\rm obs}$ on $D_{\rm pred}$ is in $[0.7,\,1.3]$, Pearson $r\ge0.7$, and $\mathrm{RMSE}_{\rm hidden\ variety}\le0.7\times\mathrm{RMSE}_{\rm clock\text{-}only\ two\text{-}type}$. These are Doc 12's thresholds, unchanged.
- **FAIL** otherwise.
- **INCONCLUSIVE** if the observed curvature does not reproduce between replicate cultures (mean pairwise $r_{\rm rep}<0.5$). In that case there is no signal to predict. This rule was added now, before analysis.

**Secondary (reported, not decisive).** The nine 2-replicate environments (1.4% to 2.5% and Ben0.4, Ben2, Ben10), trained on one culture and tested on the other.

**Deviation from Doc 12, §12.7, declared in advance.** Doc 12 specified at least 3 replicates; the primary set satisfies this. The secondary set has 2, which is why it is not decisive.

**Pipeline validation on synthetic data** (real labels, simulated counts; `simulate_t15b.py`):

| Synthetic world | Result |
|---|---|
| The law is true (clock plus hidden variety) | PASS: slope 0.995, $r$ 0.982, 58% better than clock-only |
| No selection | INCONCLUSIVE: $r_{\rm rep}$ 0.10 |
| A systematic violation (class-specific clocks) | FAIL: slope 1.66 |
| Per-lineage clock deviations that average out within groups | PASS |

**Declared power limit.** The test is sensitive to group-level violations of the law, not to lineage-level deviations that cancel within groups.

**What a PASS would mean.** On new data, aggregate group shares bend by the hidden fitness variance once each experiment's shared clock is used. This would be the first confirmation of a quantitative UHL prediction (Doc 11, Thm 11.6, in Doc 2's clock-relative form). It would **not** confirm hyperbolic geometry as such, since the law is Fisher's theorem in a fitted clock.
