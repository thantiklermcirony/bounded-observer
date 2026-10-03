# T1: could H1's design tell the laws apart?

**Question.** H1 was refuted: the fitted dial position α did not track mechanistic overlap
(`../h1-decrease/`). Was that a result about the dial, or was the experiment unable to tell the
laws apart at all?

**Why it matters.** Near rest every lawful composition is flat. Two dial laws differ, to leading
order, by (α₁ − α₂)·a·b (capstone Theorem 8, expanded; review 2026-10-03, D1). If the single-agent
effects a and b are small, the laws predict almost the same surface, and α is fitted to noise.

**Plan, stated before the run.** The hypothesis, its test and its loss condition were written
into `registry/review-2026-10-03.md` (§4, D1) and pushed in commit `3cbd55f` before this script
existed:

> [H] H1 and H2 lacked the power to separate the charts they compared. Loss condition: if the
> median predicted inter-law gap across the 210 blocks is at least 3 times the replicate SE,
> lack of power does not explain H1.

**One deviation, stated plainly.** DECREASE has single wells, with no replicates. The noise used
is each block's single-agent Hill-fit residual (RMS of the two), which is measured without any
combination law. The combination-surface misfit is reported as well, as a second yardstick.

**Data.** DECREASE validation set (Ianevski et al.), 210 blocks of 8×8 dose matrices, from
`github.com/IanevskiAleksandr/DECREASE`. This is the same data and the same fitting code as H1:
the script loads H1's own functions from `../h1-decrease/h1_dial.py`, unchanged.

## Result: the loss condition was not met. The design could not separate the laws.

| Quantity (median over 210 blocks) | Value |
| --- | --- |
| Single-agent noise σ | 0.0198 |
| RMS predicted gap, Bliss (α=0) vs Loewe end (α=1) | 0.0102 |
| Gap / noise, Bliss vs Loewe | **0.50** (loss condition needed ≥ 3) |
| Gap / noise, Bliss vs α = −3 | 0.97 |
| Blocks with gap / noise ≥ 3 | 5.2% |
| Cells per block where the gap exceeds 2σ | 0 |
| Mean product of single-agent effects a·b | 0.016 |
| Gap / misfit of the Bliss surface (misfit 0.065) | 0.14 |
| Blocks where the gap exceeds the misfit | 1.0% |

In words:
- **The laws barely differ here.** The single agents have small effects at these doses, so
  Bliss and Loewe predict nearly the same surface, with a median gap of about one percentage
  point.
- **The gap is buried.** It is half the single-agent noise, and a seventh of the amount by which
  every law misses the measured surface. In the median block, not one of the 64 cells separates
  the two laws by more than twice the noise.
- **So the fitted α mostly measured noise and misfit.** That fits the H1 record: α sat at a
  fitting bound in 65% of blocks.

## What this changes, and what it does not

- **H1 stays refuted as stated.** Its pre-registered prediction failed, and that record is kept.
- **The refutation carries little weight against the dial reading.** H1 could not have succeeded
  on this design, whatever the truth about mechanism and α.
- **The D1 diagnosis passed its first test.** [H], supported here on one dataset. It is not
  promoted beyond that. H2's half of the claim is separate and untested; for H2 the same
  argument is shown arithmetically in `papers/capstone/ERRATA_v2.1.md`, E3.
- **The design rule for every future chart test.** Before freezing, compute the predicted gap
  between the rival laws on the planned design. Proceed only where it exceeds 3σ in a
  pre-stated share of cells. On data like this, that means doses high enough for the single
  agents to act strongly.

## Run it

```bash
git clone --depth 1 https://github.com/IanevskiAleksandr/DECREASE
python power_audit.py      # writes power_audit.json and power_audit_blocks.csv
```

Needs numpy, pandas, scipy and openpyxl. Run on 3 October 2026. Before this, the H1 script was
rerun on the same download, and it reproduced `h1_results.json`, `h1_blocks.csv` and
`h1_pairs.csv` byte for byte.
