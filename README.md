# The Bounded Observer

*Science from within.*

The Bounded Observer studies what an observer can **record, read, retain, combine and change**. An observer here is defined by its access and allowed operations. The same questions can be asked of a detector, an experiment, a cell model or a computational system.

**UHL**, the Universal Hyperbolic Law, supplies the operational mathematics of positive records and bounded normalized readings. **SIH**, the Singularity Hypothesis, studies regularity and boundary concentration in specified field models. **IDA, VCC and the other branches** turn the programme's questions into instruments, models and experiments.

Daniel John Murray · [ORCID 0009-0005-1794-5945](https://orcid.org/0009-0005-1794-5945)

## One project, a common foundation

The mathematical library closes a precise operational loop:

```text
record → reading or intervention → updated record
   ↕                                   ↕
combine parts → joint record → retain part → next record
```

**[P, conditional]** In the finite complex record model, effects, completely positive instruments, tensor composition, marginals, purification and environment dilation remain within the declared record class. This is operational closure. The cone classification and complex composition use the named premises in [the capstone](papers/library-2026-10-12/papers/capstone.md) and [Paper 1](papers/library-2026-10-12/papers/paper1.md).

An application specifies what its records mean, which operations are available, what information must be retained, and how change is measured. It can use the general predictive-state question, the positive two-weight model, or the complex record model according to its own assumptions. The biological line model is self-contained; it does not require a quantum or gravitational interpretation.

The [project structure](docs/project-structure.md) gives the dependency map. The [branch contract](docs/branch-contract.md) states what a new extension must specify.

The common task is to identify **which distinctions matter**. If two histories have the same summary but different conditional future readings under the same allowed intervention, that summary is insufficient. If every declared future reading agrees, the distinction can be forgotten for those tasks. The geometry describes lawful changes within a model; the branches establish which records and changes are useful in their subjects.

## Explore the project

| Purpose | Start here |
| --- | --- |
| Understand the whole programme | [Project and branches](https://thantiklermcirony.github.io/bounded-observer/project.html) · [source map](docs/project-structure.md) |
| Join or run the research | [Working lab](LAB.md) · [Research board](docs/research-board.md) · [Usable toolkit](toolkit/README.md) |
| Read the current mathematics | [Capstone PDF](papers/library-2026-10-12/pdf/capstone.pdf) · [nine-manuscript library](papers/README.md) · [SSRN record](https://papers.ssrn.com/abstract=7603080) |
| Read the field programme | [SIH and physical models](branches/physics/README.md) |
| Explore the earlier composition model | [Six-gate walk](https://thantiklermcirony.github.io/bounded-observer/) · [frozen capstone v2.1](papers/capstone/) |
| Work on measurements and useful action | [IDA](branches/ida/README.md) |
| Work on cellular perturbation prediction | [Arc competition](branches/vcc/README.md) · [Earlier cell-response flights](branches/cell-flights/README.md) |
| Work on adaptation, hormesis, redox or population models | [Living systems](branches/adaptation/README.md) |
| Work on evidence, memory and scientific AI | [Scientific AI](branches/scientific-ai/README.md) |
| Follow arithmetic or domain evidence research | [Arithmetic](branches/arithmetic/README.md) · [Evidence and decisions](branches/evidence-decisions/README.md) |
| Follow the human and philosophical journey | [The World That Made You](https://thantiklermcirony.github.io/bounded-observer/philosophy/) · [branch contract](branches/philosophy/README.md) |
| Check the project as an AI agent | [AGENTS.md](AGENTS.md) · [llms.txt](llms.txt) |

## The branches and their relationships

| Branch | Shared question | Additional structure |
| --- | --- | --- |
| Geometry and physical models | What geometry and operations follow from the specified record system? | Cone/correspondence premises; physical clocks, signals, fields and actions where used |
| SIH | Where can a specified field remain regular or concentrate? | The PDE, target space, energy convention and initial/boundary data |
| IDA | Which measured distinctions change a useful intervention? | Signal calibration, intervention protocol and independently assessed later outcomes |
| Arc Virtual Cell Challenge | Which retained cellular distinctions predict a perturbation response? | Assay normalization, response model, held-context evaluation and challenge metrics |
| Earlier cell-response flights | Does the selected model improve the specified cellular response comparison? | Separate archived flight protocols, assay records and failed outcomes |
| Adaptation and biology | What can a bounded response and its history predict? | Growth, binding, repair/damage or resource dynamics, plus a declared clock and endpoint |
| Scientific AI | Which records preserve the warrant for a future answer or action? | Typed evidence, source versions, dependency rules, trusted checks and workload comparisons |
| Arithmetic | Which distinctions survive projection or refinement? | Exact divisibility and wheel constructions; approximation bounds when predicting primes |
| Evidence and decisions | Which evidence warrants a particular decision? | Domain-specific sources, applicability and decision rules; no full UHL model is established for every historical review |

These are relationships to a common operational programme. A branch's mathematical theorem, physical interpretation, implementation and empirical outcome have separate records in the [branch registry](registry/branches.json).

## Current library and corrections

The 12 October library contains a capstone, eight supporting papers, a hormesis amendment and two proposed author corrections. The twelve public manuscripts were received by SSRN on 13 October 2026 and await completeness review. See the [dated publication receipt](papers/PUBLICATION_STATUS_2026-10-13.md).

**[P, conditional]** The current hormesis amendment gives exact onset and peak laws for its specified response models. It replaces the unrestricted necessity and universal peak claims. The earlier deformed-kinematics uniqueness claim also has a dedicated proposed correction. Original versions remain available with their correction links.

The checked publication snapshot is preserved under [papers/library-2026-10-12](papers/library-2026-10-12/). The 30 September [v2.1 composition capstone](papers/capstone/) remains a separate, frozen source. The [earlier catalogue](registry/atlas.csv) and [dated legacy inventory](registry/legacy/README.md) retain the historical programme.

## Evidence and checks

Proof, numerical agreement, software behavior and empirical prediction are different forms of evidence. **[P]** identifies a scoped proof or cited theorem; **[D]** identifies a derivation awaiting checking; **[H]** identifies a hypothesis with a test and loss condition. Empirical outcomes are recorded separately as supported, failed, mixed or untested. A passing simulation does not establish biological or physical validity.

The [evidence atlas](https://thantiklermcirony.github.io/bounded-observer/evidence.html), [laboratories](https://thantiklermcirony.github.io/bounded-observer/labs.html) and current branch pages retain failed outcomes, including H1, Recovery Lab, the two earlier Virtual Cell flights and the rejected VCC candidate. The October library preserves T15/T15b failures and the separate cosmological test outcomes.

```sh
pip install -e "toolkit[test]"
pytest toolkit/tests -q
python registry/validate_programme.py
```

Toolkit v1.1 preserves the original v2.1 composition modules and adds selected current [record operations](toolkit/RECORDS.md) and [hormesis models](toolkit/HORMESIS.md), with their premises stated at the API. The frozen library includes thirteen independent mathematical check modules and their receipts. Its reproduction instructions explain how to run them in a separate working copy.

## Repository roles

This repository is the canonical project entrance, current mathematical library and branch registry. Existing repositories remain component stores:

- [empirical-architecture](https://github.com/thantiklermcirony/empirical-architecture): earlier foundations, manuscripts and certificates.
- [empirical-observatory](https://github.com/thantiklermcirony/empirical-observatory): experiments, software, data routes and frozen laboratory results.
- [ida-stateatlas](https://github.com/thantiklermcirony/ida-stateatlas): the StateAtlas instrument application.
- [boundedness-atlas](https://github.com/thantiklermcirony/boundedness-atlas): the earlier public synthesis and its source history.
- Engineering forks and upstream pull requests: their own code and review histories.

Future research begins as a branch here. An independently maintained application or large data workflow may need a component repository; that changes its storage, not its place in the programme.

The [research board](docs/research-board.md) names concrete proof, replication and instrument tasks. The [incubation register](docs/incubation.md) keeps earlier and proposed lines visible while their source and model bindings are established.

## Contribute and reuse

Use the [branch contract](docs/branch-contract.md) and [contribution guide](CONTRIBUTING.md). Preserve sources, assumptions, corrections and failed tests.

Original code is MIT; original text and figures are CC BY 4.0. The twelve new public manuscripts use the author-approved CC BY 4.0 option. The [dated receipt](papers/PUBLICATION_STATUS_2026-10-13.md) explains the historical snapshot notices. Linked manuscripts, datasets, third-party material and component repositories retain their own terms.
