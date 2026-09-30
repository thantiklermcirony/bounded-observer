# H2: the flat effect scale is the least consistent across trials

**Claim.** If bounded quantities compose in rapidity and flat (Euclidean) description is the
infinite-ceiling limit, then across trials of the same intervention the flat risk difference
should be the least consistent effect scale — because it is the approximation, and it degrades
near the limits.

**Result. Replicated.** Across 19 public meta-analyses, 14 showed heterogeneity between trials.
In **11 of those 14** the flat risk difference had the highest I-squared of the four scales
compared: risk difference (flat), log risk ratio (multiplicative), log odds ratio (logit) and
the Bliss difference.

**Run it.** `python h2test.py`. Results in `h2_results.csv`.

**What this is not.** A replication of a prediction, not a proof of the law. Effect-scale
heterogeneity has other explanations — differing baseline risk, differing populations, differing
follow-up — and the comparison here is against three alternative scales, not against every
possible account. Three of the fourteen went the other way and are reported as such.

The four scales are implemented in `toolkit/bounded/protocol.py::invariance_i2`.
