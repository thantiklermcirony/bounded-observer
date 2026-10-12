# Working on The Bounded Observer

This repository is the canonical entrance and branch registry for a research programme. Read the current mathematics before changing a scientific claim.

## Sources of authority

| Task | Source |
| --- | --- |
| Current operational framework | `papers/library-2026-10-12/papers/capstone.md` |
| A mathematical result | The relevant paper in `papers/library-2026-10-12/papers/`, with its premises |
| Identity and branch relationships | `docs/project-structure.md` and `registry/branches.json` |
| A new extension | `docs/branch-contract.md` |
| Publication and correction status | `papers/PUBLICATION_STATUS_2026-10-13.md` |
| Earlier composition theorems | Frozen `papers/capstone/`, version 2.1 |
| Historical claims and failures | `registry/atlas.csv`, `registry/legacy/` and `experiments/` |
| A component's scientific outcome | Its authoritative dated result, not a stale README |

## Claims and evidence

Use **[P]** for a proof under explicit premises or a checked cited theorem, **[D]** for a derivation awaiting checking, and **[H]** for a hypothesis with a test and loss condition. Record numerical verification, software behavior and empirical outcome separately. A test that ran is not a universal promotion rule.

A claim is scoped by its actual model and operation class. Boundedness alone does not select all physics. Classical or general predictive-state applications need not use complex record premises. A physical interpretation requires its own bridge.

Distinguish projective/rank boundaries, supplied boundary data and spacetime horizons. Boundary attainment must use the resource and clock conditions of the stated dynamics. Do not turn a post-hoc numerical observation into a derived precision prediction.

## Preserve the record

The October snapshot and its manifest are frozen. Reproduce checks or builds in a separate working copy; `run_checks.py` writes receipts. A mathematical revision needs a new dated release, checks, PDF inspection and a new manifest.

Keep v2.1 sources, original identifiers, failed tests and dated corrections. SSRN completeness review is not peer review. Proposed author corrections are not journal-issued corrigenda. Keep private author/editor materials, raw physiological recordings, credentials and deployment configuration out of public files.

The old atlas classifies earlier composition work. New branch membership is tracked separately; outside the C1–C4 conditions does not mean refuted or outside the whole programme.

## Checks

```sh
pip install -e "toolkit[test]"
pytest toolkit/tests -q
python registry/validate_programme.py
python site/build_evidence.py
python site/build_programme.py
python registry/legacy/validate_inventory.py
```

Code changes need checks appropriate to their behavior. Documentation changes need accurate dependencies, functioning links and source-supported statements. Do not write mirrored tests for simple prose edits.

## Contribute

Use the common branch contract. State the problem, premises, result, verification and loss condition where appropriate. Plain words and precise claims are part of the work.
