# Exploratory noise estimates for DECREASE (3 October 2026) — archive only

> **Read this before using anything in this folder.**
> - **Post hoc and exploratory.** These estimates were made after H1 had failed, by agents
>   working on an audit that was then stopped. They were not planned before H1 ran.
> - **Not automatically a replicate standard error.** DECREASE has no replicate wells within a
>   block. One estimate uses wells repeated *across* blocks. The other uses flexible fits within
>   a block. Each carries assumptions, listed below and in `METHOD_RECORDS.md`.
> - **Not a power calculation.** Nothing here computes the power of H1's pre-registered
>   statistic (Spearman ρ between overlap level and per-pair median α across 36 pairs).
> - **H1's result is unchanged.** H1 failed as pre-registered (ρ = −0.12075, one-sided
>   permutation p = 0.75582) and stays failed. Nothing here alters that.
> - **Not accepted as a programme claim.** No conclusion anywhere in the repository has been
>   changed because of these files.

## What is here

| File | What it is |
| --- | --- |
| `noise_forensic.py` | Replicate forensics: replication structure, and a noise estimate from single-agent and (0,0) wells repeated across blocks, with per-block calibration factors |
| `noise_forensic_validate_iso.py` | Check of the isotonic projection used by `noise_forensic.py` |
| `noise_forensic.csv`, `noise_forensic.json` | Its per-block output (210 rows) and summary |
| `run_full.log` | Console log of the `noise_forensic.py` run |
| `noise_modelfree.py` | Model-free estimates within each block (no composition law, no Hill form): smoothing spline with nested leave-one-out, thin-plate spline, 2-D isotonic regression, difference estimators, and replicate single-agent series |
| `check_formulas.py` | Check of the rank-one downdate formulas used by `noise_modelfree.py` |
| `noise_modelfree.csv`, `noise_modelfree_summary.json` | Its per-block output (210 rows) and summary |
| `replicate_pairs.csv` | Pairs of single-agent series repeated across blocks (1,116 pairs; derived differences) |
| `METHOD_RECORDS.md` | The two estimating agents' own statements of method, contents, dependence and caveats, verbatim |
| `SHA256SUMS` | Hashes of every file above as archived |
| `NOTICE.md` | Third-party data provenance (DECREASE, GPL-3.0) |

The scripts and outputs are archived exactly as produced. The scripts keep their original
absolute paths (`/tmp/claude-0/h1run/DECREASE`, `/tmp/claude-0/stage1/h1`,
`/home/user/bounded-observer/...`). To re-run them, point those paths at a local copy.

## Inputs, with hashes

| Input | Identity |
| --- | --- |
| DECREASE repository | `https://github.com/IanevskiAleksandr/DECREASE` at commit `0f5871cad64fb8c43a88242e02baac175ed98d0e` |
| `210_Novel_Anticancer_combinations/192_Combinations_.xlsx` | SHA-256 `fd2049147919a4120d8e92aa5691ed6c3ca9fdc43be232b88f4634a2a919fcc0` |
| `210_Novel_Anticancer_combinations/18_combinations_.xlsx` | SHA-256 `363850481d9ef8999ab48af279c4538bf4fea0135d4274a5241a41cfe7bfd698` |
| `experiments/h1-decrease/h1_dial.py` (loader and fits, executed unchanged) | git blob `99f1ed52cac7d98b696b4721d0fea81c124c6e06`, SHA-256 `6e4f8ca6b6912c980eda6cd4b7ce6c2684512c0a4f69d98ef563e03c07786037` |
| `experiments/h1-decrease/h1_blocks.csv` (comparators) | SHA-256 `ea98c9b70d3a5551fff8b65c881307502b26a1e0b7a2386f570c90e2d080e180`, last changed in commit `947094523c0b55e49d1f5a73aab1904cff9d8278` |

## What the estimates say, as reported (not adopted)

These are the agents' reported numbers. They are recorded so that the work is not lost, not
endorsed.
- **Replicate-based, unclipped scale** (`noise_forensic`): median 0.04191, IQR 0.03557–0.04914.
  It rests on several things:
  - wells repeated across blocks;
  - a multiplicative block factor;
  - a fitted variance function carried to the interior wells;
  - an inferred, undocumented normalisation.
- **Model-free, H1's clipped scale** (`noise_modelfree`): nested-CV median 0.03662, and
  df-corrected 0.02666. A cross-validated residual mixes noise with unexplained structure and
  reads high on synthetic tests.
- **Both report dependence:**
  - a shared block-level calibration error;
  - positive correlation between neighbouring wells;
  - residual patterns that recur across blocks of the same pair or cell line.

  So the 49 interior wells of a block, and the 210 blocks, are not independent observations.

**Assumptions that matter most.**
- The replicate design, plate layout and normalisation are inferred from the data. The DECREASE
  paper could not be reached.
- H1 clipped the effect to [0, 1], which truncates about 28% of wells. Noise differs between
  the clipped and unclipped scales, and with effect level.
- Estimates near zero effect in the 18-combination file are censored.

## Where this would be used

Nowhere, in this repair pass. Any future power analysis of H1's statistic would have to choose
and justify its noise model, dependence model and calibration uncertainty in a plan written
before running. These files are candidate inputs to that plan, nothing more.
