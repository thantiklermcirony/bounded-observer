# Gate 3 · Action

**Which interventions act the same way from every state?**

A state is only a state relative to a set of admissible interventions (gate 2). So before any
law is fitted, the set has to be named — and not every intervention qualifies.

## The action gate

An intervention passes if **its endpoint from rest fixes its action from every state**.

That is a strong requirement and a testable one. Take an intervention, apply it from the
neutral state, and record where it lands. Now apply it from somewhere else. If knowing the
first result is enough to predict the second, the intervention composes lawfully and can be
written as an element of the law. If it is not, the endpoint label does not identify the
intervention's action from every state. The action representation must be repaired before a
chart is fitted; this result alone does not identify hidden state.

The action gate makes composition by endpoint labels well defined (Appendix A.3). If that
composition also passes the regular-closure conditions at gate 4, Theorem 12 makes each
fixed-element action a translation in rapidity. Status: **[P]**, conditional on those gates.

## The bracket test: does order matter?

Two flows, $f$ and $g$. Run $f$ for a small time $\varepsilon$, then $g$ for $\eta$. Now do it
the other way round. To leading order the two results differ by

$$\varepsilon\eta\,(fg' - gf')$$

If that vanishes everywhere, then $g = cf$ for a constant $c$, and both flows share the same
rapidity $\psi = \int dx/f$. One chart serves both.

If it does not vanish, these two flows do not share one additive rapidity. Even a complete
one-dimensional state can have noncommuting flows, so this result alone does not require
another state dimension. Gate 5 treats structures that independently earn a higher-dimensional
description. For example, on $0<x<1$, $f=x(1-x)$ and $g=x(1-x)(1+x)$ give
$fg'-gf'=x^2(1-x)^2>0$ while $x$ is still a complete scalar state for these flows.

This is cheap to run and diagnostic of a proposed common-chart or order-blind encoding. An
order effect can arise from the intervention maps themselves, the endpoint encoding, feedback,
or an incomplete state. To attribute it to missing state, use gate 2's matched-present test:
different histories at the same proposed state must separate under the same future challenge.
`toolkit/bounded/coupling.py` implements the bracket measurement and leading-order prediction;
`test_bracket_predicts_order_effect` checks that they agree. Status: **[P]** for the conditional
flow calculation and state criterion, not for an empirical diagnosis.

## Where this bites: drug combinations

Two drugs, each with an effect. What is the effect of both?

Theorem 8 says that if the combination law is projective, rests at zero and has its horizon at
one, then it lies on a one-parameter family — a **dial**:

$$a \oplus b = \frac{a + b - (1+\alpha)ab}{1 - \alpha ab}, \qquad \alpha \le 1$$

with named landmarks: $\alpha = 0$ is Bliss independence (the chances of *not* acting
multiply), $\alpha \to 1$ is Loewe additivity (the odds add), $\alpha = -1$ is the Einstein
t-conorm. Status: **[P]** for the family.

## The test that failed

**H1**, pre-registered: drugs sharing a mechanism should sit near the Loewe end of the dial;
drugs with independent mechanisms near the Bliss end.

Run on DECREASE — 210 blocks, 36 drug pairs, 13 cell lines, with the mechanistic annotation
fixed in writing before any fit. **Refuted.** Spearman $\rho = -0.12$, one-sided permutation
$p = 0.76$. Same-axis pairs were *more* synergistic than distinct-mechanism pairs: the opposite
of the prediction. The single shared-target pair split between the two ends of the dial.

The failure is partly structural, and that part is instructive. Loewe additivity sits on the
dial only for Hill slope 1 with full efficacy. At slope 2 the true Loewe surface is at
$\alpha = -3.5$; at slope 3 it leaves the dial's range entirely. In this dataset the median
slopes were 2.0 and 1.3, and only 32% of blocks had both slopes in $[0.5, 2]$. So the
prediction as stated was only ever correct for a minority of real drug pairs.

H1 is therefore restated as a claim about the Bliss and Loewe *surfaces* computed from each
block's own fitted curves, not about a single dial position. The original is kept, refuted, in
`experiments/h1-decrease/`, with its pre-registration, its code and its data.

An external reviewer reran the analysis and reproduced the primary result exactly
($\rho = -0.12075$, $p = 0.75582$), and in doing so found a reversed bisection step in a
separate post-hoc calibration. That line is corrected; every primary and sensitivity statistic
is identical to five decimals.

## On the site

[**The dial**](https://thantiklermcirony.github.io/bounded-observer/#sim-dial) — mix two drugs, move $\alpha$ from Bliss to Loewe and
watch the combination surface deform. Then see the real data, and where the prediction broke.

## Sources

- Capstone v2.1, Theorems 8 and 12, §4.3, §13.3 — `papers/capstone/`
- `experiments/h1-decrease/` — pre-registration, code, data, report
- *From Predictive State to Viable Action* — [SSRN 7427100](https://papers.ssrn.com/abstract=7427100)
- *Aczél-Family Composition in Bounded Pharmacology* — [SSRN 7426978](https://papers.ssrn.com/abstract=7426978)

**Next gate:** [Chart and boundary](4-chart.md) — how bounded changes combine, and the horizon.
