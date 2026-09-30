# For AI agents working in this repository

You are reading the source of a research programme, not a codebase with a product to ship.
The rules below exist because the programme's value is entirely in the discipline of its
claims. Breaking them silently damages it more than any bug would.

## The one rule

**Nothing is asserted without a status tag, and nothing is promoted without a test that ran.**

- `[P]` proven here, or classical with a citation you have checked.
- `[D]` derived, awaiting independent checking.
- `[H]` a hypothesis, with a stated test *and* a stated loss condition — the observation that
  would make it wrong.

If you cannot tag a claim, you cannot add it. If you want to move a claim from `[H]` to `[D]`
or `[P]`, point to the test and its output. A claim with no loss condition is not a hypothesis;
it is an opinion, and it does not belong here.

## What this programme is

An observer with finite access, inside the world it measures. From that: predictive state,
bounded composition, horizons, hyperbolic geometry. The central theorem is the Universal
Hyperbolic Law; `papers/capstone/` has the proofs. `docs/` walks the six gates in order.

## Where to look before you write anything

| You want to | Read |
| --- | --- |
| Know what a theorem actually says | `papers/capstone/` (numbered; cite by number) |
| Check a piece of maths | `toolkit/bounded/` — the module docstrings name the theorem each implements |
| Know whether something is already claimed | `registry/atlas.csv` — 39 rows, every work placed |
| Trace an earlier paper or prediction | `registry/legacy/README.md` — dated identifiers and source receipts, not current verdicts |
| Know what failed | `experiments/` — failures are kept, not deleted |
| Know what is still open | `registry/atlas.csv`, column `next_test` |

## Running the checks

```bash
pip install -e toolkit
pytest toolkit/tests -q
```

Every test names the theorem it checks. If you change `toolkit/bounded/`, the tests must still
pass, and a new function needs a new test that names what it is checking.

## Things that look like improvements and are not

- **Rounding a bound into a claim.** "The exponent is between 1/2 and 1" is the result.
  "The exponent is about 0.7" is not.
- **Dropping a failed test.** H1 was pre-registered, run, and refuted. It stays, with its data
  and its code. A programme that only keeps its wins has no evidence at all.
- **Smoothing a hedge.** "Status: [D]" is load-bearing. So is "loss condition:".
- **Generalising a measured number.** A rescue window measured in one cell line under one
  condition is not a constant of biology.
- **Inventing a citation.** If you cannot open the source, say so rather than writing a
  plausible reference. Unverifiable citations are the fastest way to discredit the whole
  repository.
- **Making the law sound more universal than its conditions.** The UHL is universal *over its
  four conditions* (C1–C4). Outside them it says nothing, and `registry/atlas.csv` has a whole
  category for work whose conditions it does not meet.

## If you find an error

Open an issue using the error-report template, or send a pull request that states plainly what
is wrong, what the correct statement is, and what evidence settles it. Corrections to the
author's own work are the most valuable contribution here; several are already in the record.

## Style

Plain words. Short sentences. No jargon where a common word will do. Say what is true, then say
how confident you are and why. The reader is assumed to be intelligent and to have no patience
for padding.
