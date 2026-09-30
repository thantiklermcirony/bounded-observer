# The Bounded Observer

*Science from within.*

An observer with finite access, standing inside the world it measures, cannot see everything.
That premise starts the programme. Each later result has its own assumptions and tests.

Finite access makes **predictive state** a question: what must be kept so the rest of the past
can be forgotten safely? A bounded quantity has a lawful **composition** only after its
changes pass separate state and action tests. When composition satisfies C1–C4 below, an
additive coordinate puts a finite bound at an unreachable **horizon**. A multidimensional
**geometry** needs further structure, including the observer's comparison and channel cone.

The central theorem is the **Universal Hyperbolic Law**. Status: [P] under C1–C4. For a bounded
real quantity, these conditions require continuous, associative, strictly monotone composition
with a neutral state. They give an additive coordinate, its *rapidity*, in which the bound sits at
infinity. Boundedness alone gives neither that law nor a particular geometric curvature.

Daniel John Murray · [ORCID 0009-0005-1794-5945](https://orcid.org/0009-0005-1794-5945)

## Start here

| If you are | Start at |
| --- | --- |
| A person | [the website](https://thantiklermcirony.github.io/bounded-observer/) — twelve simulations you can touch |
| Curious what finite observation feels like | [Inside](https://thantiklermcirony.github.io/bounded-observer/inside.html) — a playable constructed world; its outcomes illustrate chosen rules, not empirical evidence |
| Tracing the wider research | [research library](https://thantiklermcirony.github.io/bounded-observer/library.html) — dated manuscript and prediction records; [laboratories](https://thantiklermcirony.github.io/bounded-observer/labs.html) — results and failure gates |
| An AI agent | [`AGENTS.md`](AGENTS.md), then [`llms.txt`](llms.txt) |
| A mathematician | [`papers/capstone/`](papers/capstone/) — *Bounded Composition and Its Horizons*, v2.1 |
| Here to check the maths | [`toolkit/`](toolkit/) — `pip install -e toolkit && pytest toolkit/tests` |
| Looking for what is untested | [`registry/atlas.csv`](registry/atlas.csv) — every claim, its status, its next test |
| Here for the instrument | [`apps/ida-live/`](apps/ida-live/) — the law running on a living mind |

## The six gates

Every chapter, folder and simulation follows the same order. Each gate needs the one above it:
a claim about geometry means nothing until the state and the admissible actions are fixed.

| Gate | The question | Where |
| --- | --- | --- |
| 1 · Access | What can an observer reach from inside? | [`docs/1-access.md`](docs/1-access.md) |
| 2 · State | What must be kept so the rest can be forgotten? | [`docs/2-state.md`](docs/2-state.md) |
| 3 · Action | Which interventions act the same way from every state? | [`docs/3-action.md`](docs/3-action.md) |
| 4 · Chart and boundary | How do bounded changes combine, and can the edge be reached? | [`docs/4-chart.md`](docs/4-chart.md) |
| 5 · Geometry | What shape is the room inside the horizon? | [`docs/5-geometry.md`](docs/5-geometry.md) |
| 6 · Prediction | Does it win on data it has never seen? | [`docs/6-prediction.md`](docs/6-prediction.md) |

## Status tags

Every claim in this repository carries one:

- **[P]** proven here, or classical with a citation.
- **[D]** derived and awaiting independent checking.
- **[H]** a hypothesis with a stated test and a stated loss condition.

A claim is promoted only when its test has run. Failures stay in the record: see
[`experiments/h1-decrease/`](experiments/h1-decrease/), a prediction in a dated local analysis plan of this
programme that was tested and refuted as stated.

## What has been tested

| Result | Status |
| --- | --- |
| Across 19 public meta-analyses, 14 showed heterogeneity between trials; in 11 of those 14 the flat risk difference was the least consistent effect scale | replication of the correspondence prediction |
| H1, mechanistic overlap against the one-horizon dial position, specified in a dated local plan and tested on DECREASE (210 blocks, 36 pairs) | **refuted as stated**; restated as a statement about surfaces, not a single dial position |
| Hormesis as a geometric necessity | published, [SSRN 6858819](https://papers.ssrn.com/abstract=6858819) |
| Glutathione two-failure-mode model | published, [SSRN 6754498](https://papers.ssrn.com/abstract=6754498) |

## Layout

```
docs/        six chapters, one per gate
site/        the website, Inside experience, interactive models, research library and laboratories
toolkit/     the Python package `bounded`: the maths, with tests that check each theorem
registry/    the current claim atlas and dated source inventory
papers/      programme paper guide and the capstone source
experiments/ dated local analysis plans with their data and code
apps/        IDA Live, the instrument
```

## Contributing

New charts, replications and refutations are all welcome, and a refutation is worth more than
a confirmation. See [`CONTRIBUTING.md`](CONTRIBUTING.md). The one rule: nothing is claimed
without a status tag, and nothing is promoted without a test.

## Licence

Code is MIT (see [`LICENSE`](LICENSE)). Text and figures are CC BY 4.0
(see [`LICENSE-CONTENT`](LICENSE-CONTENT)). Third-party material is listed in each folder's
`NOTICE.md`. The dated source inventory preserves original identifiers and links; its
underlying manuscripts, datasets, art and source repositories retain their own terms.
