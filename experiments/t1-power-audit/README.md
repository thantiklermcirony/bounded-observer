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

## Result: the stated loss condition was not met. What that does and does not show

> **Narrowed 3 October 2026, after review.** An earlier version of this page said the design
> "could not separate the laws" and that H1 "could not have succeeded". That overstated what
> this comparison measures, for four reasons:
> 1. **The noise figure is a proxy, not a validated noise estimate.** The single-agent Hill-fit
>    residual mixes measurement noise with Hill-model error.
> 2. **Small per-cell gaps can add up.** Across 49 cells per block and 210 blocks, they can
>    become detectable. This page compares per-cell sizes only.
> 3. **It covers two models out of many.** It compares Bliss (α = 0) with the Loewe end of the
>    dial (α = 1). H1 concerns the whole dial, including Einstein composition (α = −1), and
>    conventional rivals.
> 4. **It does not compute the power of H1's actual test,** the ordinal test across 36 pairs, nor
>    does it account for calibration uncertainty or dependence between measurements.
>
> A full audit covering all four is in progress. Until it lands, read the table below as a
> per-cell description of the design, not as a power result.

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

In words, and only per cell:
- **Bliss and the Loewe end differ little per cell here.** The single agents have small effects at these doses, so
  Bliss and Loewe predict nearly the same surface, with a median gap of about one percentage
  point.
- **Per cell, the gap is small next to the noise proxy and the misfit.** It is half the
  single-agent residual proxy, and a seventh of the amount by which every dial law misses the
  measured surface. In the median block, no single cell separates the two laws by more than
  twice the proxy. Aggregated over cells the comparison may still have power; that is not
  computed here.
- **This is consistent with α being weakly identified per block.** That matches the H1 record,
  where α sat at a fitting bound in 65% of blocks. It does not show it.

## What this changes, and what it does not

- **H1 stays refuted as stated.** Its pre-registered prediction failed, and that record is kept.
- **How much the refutation tells us about the dial reading is not settled here.** That needs the
  power of H1's actual test, which is being audited. Low power, if found, would narrow what the
  failure tells us. It would never be evidence for the framework.
- **D1 has a first, partial check that is consistent with it.** [H], not promoted. This page does
  not test the power of the H1 statistic. H2's half of the claim is separate and untested; for H2 the same
  argument is shown arithmetically in `papers/capstone/ERRATA_v2.1.md`, E3.
- **The design rule for every future chart test.** Before freezing, compute the power of the
  planned primary test on the planned design: model the predicted gaps between all rival laws,
  use a validated noise estimate, and account for calibration uncertainty and dependence between
  measurements. Proceed only if the power is adequate. Being near saturation is often needed, but
  it is not enough on its own to make laws distinguishable.

## Run it

```bash
git clone --depth 1 https://github.com/IanevskiAleksandr/DECREASE
python power_audit.py      # writes power_audit.json and power_audit_blocks.csv
```

Needs numpy, pandas, scipy and openpyxl. Run on 3 October 2026. Before this, the H1 script was
rerun on the same download, and it reproduced `h1_results.json`, `h1_blocks.csv` and
`h1_pairs.csv` byte for byte.
