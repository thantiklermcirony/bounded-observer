# Arc Virtual Cell Challenge

This is the **Arc Virtual Cell Challenge** branch. The earlier [Observatory cell-response flights](../cell-flights/README.md) are a distinct GitHub laboratory line with separate models, records and outcomes.

## Arc Virtual Cell Challenge

The **Arc competition predictor** is a separate project using Bounded Observer work for single-cell perturbation-response prediction. Its official submissions, scores and ranking are competition evidence for that implementation. They are not the Observatory flights.

The non-neural, rule-based **31-EchoFull** predictor achieved a recorded **validation-panel leaderboard entry rank of 221 among 1,416**, observed on 10 October 2026, an overall normalized challenge score of **0.2102**, and normalized perturbation-discrimination score of **0.7815**. It generated 360,000 predicted cells across 900 perturbation–context groups and 18,533 genes. Its construction uses empirical source effects, explicit guide/cis rules, bounded profile updates and count-preserving rendering.

The rank and scores are the author's preserved official dashboard/email result at that date, rather than a final standing. An independent upload log identifies the entry; the pasted score notice does not itself name that ID. The overall score is not an accuracy percentage.

| Competition entry | Overall score | Observed rank | Result date (Sydney) |
| --- | --- | --- | --- |
| 31 — EchoFull | 0.2102 | 221 / 1,416 entries | 10 October 2026 |
| 32 — ProgrammeQuarter64 | 0.2092347518 | 227 | 10 October 2026 |
| 33 — NT20-KL | 0.1377975900 | 558 | 11 October 2026 |
| 34 — SourceSpecificQuarter64 | 0.2097282273 | 246 | 12 October 2026 |
| 35 — EchoRoad | 0.2082 | Not retained in the inspected result | 12 October 2026 |
| 36 — EchoRoadShared | 0.2090 | Not retained in the inspected result | 12 October 2026 |

The [dated competition receipt](../../registry/receipts/vcc-competition-results-2026-10-13.json) preserves exact scores, provenance and source hashes. Later variants include fitted ridge or least-squares components; each method is described separately. Future candidates retain the established competition control and its achieved results.

## Competition operational contract

| Item | Specification |
| --- | --- |
| Record | Raw counts, controls, perturbation identities, available sources and frozen folds |
| Normalizer | Full supplied-axis per-cell normalization before equal-cell averaging; any common-axis reclosure is separate, with retained masses |
| Readings | Gene means, detection probabilities, signed logFC, response profiles and official scores, each with its own transform |
| Operations | Genetic perturbations, declared response-transfer model and separately fixed count renderer |
| Retained state | Destination, source and control information, gene support, target identity and unavailable fields |
| Composition | Population averaging and the specified response/count construction |
| Time | Assay endpoint and acquisition provenance; training runtime is a different clock |
| Bridge | Compatible observation conventions plus whole-context and target holdouts |
| Evidence | Official submission receipts, held-out comparisons and dated candidate decisions |

A resemblance between normalized controls is a control-bridge result. It does not establish biological identity or portability of perturbation responses.

## Latest candidate review

The 12 October 2026 independent biological review rejected the signed-logFC L1 head proposed for submission 35. All-axis profile errors improved, while confirmed up/down errors and arithmetic mean MSE worsened in every primary context against the old-GP comparator. Independent numerical execution and prediction replay passed; biological promotion failed.

That rejected head was one research candidate family. A separate EchoRoad candidate line produced the successfully uploaded **35-EchoRoad** and **36-EchoRoadShared** later on 12 October. Their official results belong to the competition history above. A built 37-EchoShared archive has no scored or upload receipt in the inspected records. The [dated candidate-family receipt](../../registry/receipts/vcc-review-2026-10-12.json) records the decision and source hash.

[Project map](../../docs/project-structure.md) · [Branch contract](../../docs/branch-contract.md)
