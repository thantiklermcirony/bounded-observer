# Gate 6 · Prediction

**Does any of this win on data it has never seen?**

The five gates above are mathematics. This one is the only gate that can go wrong in a way the
mathematics cannot repair, and it is where the programme is honest or it is nothing.

## The register

`registry/atlas.csv` places every work in the programme as a chart of the law: its bounded
quantity, its chart, its status, and — the column that matters — **its next test**. 39 rows,
across nine layers:

| Layer | Rows |
| --- | --- |
| Core (the capstone) | 1 |
| Foundations | 4 |
| Observer and state | 9 |
| Physics charts | 4 |
| Life: pharmacology | 5 |
| Life: homeostasis | 6 |
| Life: evolution and ecology | 3 |
| Mind charts | 4 |
| **Outside UHL** | **3** |

That last row is deliberate. Three works are listed as *outside* the law — their conditions are
not met, and saying so is what keeps "universal" from meaning "unfalsifiable". The law is
universal **over its four conditions**. Outside them it says nothing.

## What has been tested

### Replicated: the correspondence prediction

If bounded quantities compose in rapidity and flat description is the infinite-ceiling limit,
then across trials the *flat* scale should be the least consistent one — because it is the
approximation, and it degrades near the limits.

Across 19 public meta-analyses, 14 showed heterogeneity between trials. **In 11 of those 14 the
flat risk difference was the least consistent effect scale.** Reproduce with
`experiments/h2-effect-scales/`.

This is a replication of a prediction, not a proof of the law. Effect-scale heterogeneity has
other explanations, and the comparison here is against three alternatives, not all of them.

### Refuted: H1, the dial against mechanism

Pre-registered before any fit: drugs sharing a mechanism sit near the Loewe end of the
one-horizon dial; independent mechanisms near the Bliss end.

**Refuted.** $\rho = -0.12$, $p = 0.76$, on 210 blocks and 36 pairs. Direction opposite to the
prediction. Independently reproduced to five decimals by an external reviewer, who also found
and helped correct a reversed bisection in a separate post-hoc calibration.

The prediction is restated — as a claim about the Bliss and Loewe *surfaces* computed from each
block's own Hill fits, not about a single dial position — because Loewe additivity only sits on
the dial at Hill slope 1 with full efficacy, and real screens are mostly not that. The restated
version awaits a larger dataset with many same-target pairs.

Everything is in `experiments/h1-decrease/`: the pre-registration written first, the code, the
data, the report, and the superseded output kept for provenance.

### Published

- **Hormesis as a geometric necessity of bounded adaptive systems** —
  [SSRN 6858819](https://papers.ssrn.com/abstract=6858819). A zero-free-parameter prediction
  checked against Calabrese's database of more than 10,000 dose-responses.
- **A dynamical model of glutathione homeostasis** —
  [SSRN 6754498](https://papers.ssrn.com/abstract=6754498). Recovers G6PD severe-deficiency
  contraindications and forecasts a phase II NSCLC trial outcome.

### In review

- **Finite rescue windows and supply-limited redox commitment in NRF2-active cancer** —
  major revision. Its second revision reports a negative result about its own earlier proposed
  experiment: that design could not have distinguished the model from a simple power law even
  if the model were exactly correct.

## What is open, and what would settle it

| Hypothesis | Test | Loss condition |
| --- | --- | --- |
| **H1 restated** | Bliss and Loewe surfaces from per-block Hill fits, on NCI-ALMANAC or DrugComb | Overlap does not predict surface position |
| **H5** | IDA read gate: do return features beat static, dynamic and simple-recovery baselines on a held-out behavioural outcome? | They do not, over 20 sessions after the freeze |
| **H7** | Gromov $\delta$ and best-fit curvature of perturbation-response and neural state spaces | Flat or spherical fits are as good or better |
| **Theorem 25 item 3** | Reassociation defects and sectional curvature in a qutrit or covariance-tracking system | Defects vanish, or fitted curvature is constant |
| **The classification** | Predict boundary exponent and cone type from a pre-specified mechanism; compare against a flexible alternative on held-out measurements | The flexible alternative predicts as well or better |

## The rule this gate enforces

A chart is promoted only when its test has run. A claim with no loss condition is not a
hypothesis. And a refuted prediction stays in the record with its data and its code — because a
programme that keeps only its wins has no evidence at all, and because the register's meaning
comes entirely from the fact that entries can leave it.

## On the site

[**Evidence**](../site/evidence.html) — the whole atlas, filterable, failures included.

## Sources

- Capstone v2.1, §13 (the seven-step protocol) and §15 (the claim register) — `papers/capstone/`
- `registry/atlas.csv`, `experiments/`
- `toolkit/bounded/protocol.py` — the protocol as runnable functions

**Back to:** [Access](1-access.md) · [README](../README.md)
