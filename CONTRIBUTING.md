# Contributing

A refutation is worth more than a confirmation. That is not modesty; it is how the register
in `registry/atlas.csv` earns its meaning.

## The four kinds of contribution

**1. A new chart.** A bounded quantity somewhere in the world that meets conditions C1–C4, with
its rapidity, its horizon and at least one consequence that could fail. Open an issue with the
"new chart" template. You will be asked for: the quantity and its ceiling, the neutral state,
the composition operation, the chart, and one prediction with a loss condition.

**2. A replication.** Re-run something in `experiments/` and report what you get. Agreement and
disagreement are equally publishable here; both go into the registry row's `last_result`.

**3. A refutation.** Show that a claim is false, or that a test does not test what it says.
State what is wrong, what the correct statement is, and what evidence settles it. If the claim
is one of the author's own, so much the better — several corrections already in the record are
exactly that.

**4. A correction.** An error in a proof, a wrong citation, a number that does not reproduce.
Use the error-report template. Please say whether you checked the source yourself.

## What every contribution needs

- **A status tag.** `[P]`, `[D]` or `[H]`. See `AGENTS.md`.
- **A loss condition**, for anything tagged `[H]`. What observation would make this wrong? A
  hypothesis without one is not accepted.
- **Reproducibility.** Code that runs, with its seed. If you supply a number, supply what
  produced it.
- **Sources you actually opened.** If you could not open something, say so.

## Running the checks

```bash
pip install -e toolkit
pytest toolkit/tests -q
```

Each test names the theorem it checks. A new function in `toolkit/bounded/` needs a new test
that names what it is checking.

## What will be declined

Claims without tags. Hypotheses without loss conditions. Generalisations of a number measured
under one set of conditions. Citations that cannot be opened. Changes that make the law sound
more universal than its four conditions allow.

## Licence of contributions

Code contributions are under MIT; text and figures under CC BY 4.0. By opening a pull request
you agree to those terms for your contribution.
