# The Bounded Observer research lab

The lab develops records, models and instruments that can change a prediction or an action. Its working cycle is **question → specified model or candidate → frozen comparison → independent check → result → revision**.

[Project map](docs/project-structure.md) · [Branch contracts](docs/branch-contract.md) · [Current papers](papers/README.md) · [Existing laboratory component](https://github.com/thantiklermcirony/empirical-observatory)

[Research board and completion criteria](docs/research-board.md) · [Runnable toolkit](toolkit/README.md) · [Incubation and outreach](docs/incubation.md)

## Current work

| Line | Established checkpoint | Next discriminating task | Working home |
| --- | --- | --- | --- |
| Record mathematics | Conditional closure and classification proofs; thirteen check modules | Extend a named model or prove a scoped conjecture with its required premises | [Current library](papers/library-2026-10-12/); live current-record modules and the separately labeled v2.1 composition toolkit |
| SIH and fields | Specified regularity and concentration results | Resolve the horizon-fluid pressure/margin conjecture in its actual PDE | [Physical models](branches/physics/README.md), Paper 5 |
| Arc competition | Non-neural 31-EchoFull recorded validation-panel leaderboard entry rank 221 of 1,416 and score 0.2102, observed on 10 October 2026; later variants and outcomes retained | Improve actual perturbation response against the established competition control, preserving the protocol and official score | [Competition branch and receipts](branches/vcc/README.md); implementation currently in the author's working archive; no public source release yet |
| IDA | Two distinct research prototypes; chosen feature map, synthetic lab and engineering baseline | Independent matched-present/common-future read/action test against a fixed comparator | [IDA branch](branches/ida/README.md), IDA Live and StateAtlas |
| Hormesis and recovery | Exact amended response laws; failed recovery comparison retained | Independently calibrate components, baseline and endpoint before testing untouched responses | [Adaptation](branches/adaptation/README.md), Observatory |
| Evidence and scientific AI | Typed evidence tools and finite checks; Active Context's first comparison tied its baseline | Measure consequential errors and work saved on a fixed independent workload | [Scientific AI](branches/scientific-ai/README.md), Observatory automation |
| Arithmetic | Source-specific exact refinement constructions | Establish controlled approximation and independent enumeration where prediction is claimed | [Arithmetic](branches/arithmetic/README.md) |

These are work routes, not announcements that new experiments have run. Each task names its branch, model, retained information, clock/resource, comparator and loss condition before interpreting its outcome.

## Run the public models

The existing composition modules implement frozen v2.1. New current-record and response modules have their own source-scoped documentation. Install the toolkit and its test dependencies:

```sh
python -m pip install -e "toolkit[test]"
python -m pytest toolkit/tests -q
```

Explore the public models locally:

```sh
python -m http.server 8000 --directory site
```

Open http://127.0.0.1:8000/project.html for the programme, or the root page for the interactive composition walk. The stories and synthetic simulations expose chosen rules; empirical records have their own sources.

Check the browser's implemented mathematics:

```sh
node site/bo.test.mjs
node --test site/inside-core.test.mjs
node --test site/valley-world.test.mjs
node --test site/radiation-model.test.mjs
```

For IDA Live source mode, create a virtual environment, install [its requirements](apps/ida-live/requirements.txt), then run the simulator from `apps/ida-live`:

```sh
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m ida_live --sim
```

A minimal cross-platform simulator route uses the existing numpy/aiohttp implementation without optional headband dependencies:

```sh
cd apps/ida-live
python -m pip install numpy aiohttp pytest
python -m pytest tests -q
python -m ida_live --sim
```

The first block contains Windows source-mode commands. On other platforms, use the corresponding virtual environment's Python. This route does not require headband hardware; physiological validation is a separate branch task.

StateAtlas has its own [setup and reproduction instructions](https://github.com/thantiklermcirony/ida-stateatlas). The laboratory component has task-specific reproduction routes. Large cellular datasets and competition submission archives remain in their existing working homes. The public competition receipt is evidence of performance, not a complete source release.

## Reproduce a library check

The October library is a frozen publication snapshot. Copy it into a separate working directory, install its requirements, then run `python run_checks.py` there. The runner writes receipts; keep those generated outputs separate from the published manifest.

For a changed model, retain the old source and receipt, name the new candidate, state its premises and run the applicable independent checks. A physical prediction also needs its observation bridge and empirical comparison.

## Start or join a task

Use the research-task issue form, or submit a scoped contribution through [CONTRIBUTING.md](CONTRIBUTING.md). A runnable model or instrument, mathematical counterexample, replication or failure can all move a task.

Attach the source version, dependency, protocol, output and conclusion. Preserve unsuccessful candidates beside later revisions. Changes to the result must update the source record and its public branch status together.
