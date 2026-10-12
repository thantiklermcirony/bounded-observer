# Exact response laws for the hormesis laboratory

`bounded.hormesis` implements three different models from the mathematical
amendment [*Exact Onset and Peak Laws for Bounded Adaptive Responses*](../papers/library-2026-10-12/papers/hormesis_amendment.md)
and [Paper 2](../papers/library-2026-10-12/papers/paper2.md). It supplies
a working interface for measuring the components first and testing the response
on held-out doses. It does not select biological parameters or establish a
therapeutic optimum.

| Class | Response construction | Amplitude meaning |
| --- | --- | --- |
| `AdditiveLinearLogistic` | Equal-slope occupancies in linear dose, added in rapidity; zero-dose tails are subtracted | `repair`, `harm`: rapidity increments |
| `AdditiveHill` | Common-exponent Hill occupancies, added in rapidity | `repair`, `harm`: rapidity increments |
| `MultiplicativeHill` | Fractional benefit multiplied by a survival factor | `benefit`: fractional functional gain |

All dose inputs must be finite and nonnegative. All thresholds are positive with
`activation < toxicity`. The additive models require `0 < p0 < 1` and
`harm > repair > 0`; the multiplicative model permits `benefit >= 0`. Slopes and
Hill exponents are positive. Unequal slopes or unequal Hill exponents require
their own analysis and are outside these peak theorems.

```python
from bounded.hormesis import AdditiveHill

model = AdditiveHill(p0=0.5, repair=0.6, harm=1.5,
                     activation=1.0, toxicity=10.0, exponent=2.0)
print(model([0, 1, 2, 5, 10]))    # response relative to the actual control
print(model.has_beneficial_interval)
print(model.peak())
print(model.return_to_control())
print(model.detectable_interval(gain=0.05))  # strict interval R > 1.05
```

`peak()` includes the control boundary: without a beneficial interval it returns
`Peak(dose=0, response=1)`. `return_to_control()` returns `None` in that case.
`detectable_interval()` returns both positive assay crossings, or `None` when the
cutoff equals/exceeds the peak or there is no beneficial interval. A cutoff is an
operational response criterion; statistical power additionally needs a noise
and replication model. `DoseInterval.fold_width` uses both crossings, not the
zero-gain return dose.

`series_flux_fold(steps, molecular_gain)` separately implements the exact finite
fold for changing one rate in an equal-resistance series chain with a fixed
driving drop. Its kinetics are an explicit model assumption. The local
metabolic-control summation theorem alone does not choose that finite law.

The library works in floating-point arithmetic. Log-domain formulas avoid many
large-dose overflows and small-root cancellations; responses too close to the
control to resolve can still be invisible numerically. Analytic doses or
distinct assay edges that cannot be represented raise `ArithmeticError`.

These models have different onset, peak and amplitude laws. Threshold ordering
and bounded composition alone do not guarantee hormesis, a peak at twice the
activation threshold, or a generally conservative product approximation.

Run the independent definition, optimization, assay crossing, dose-unit,
counterexample and network checks with:

```text
python -m pytest toolkit/tests/test_hormesis.py
```
