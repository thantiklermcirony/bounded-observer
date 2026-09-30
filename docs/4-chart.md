# Gate 4 · Chart and boundary

**How do bounded changes combine, and can the edge ever be reached?**

This is the Universal Hyperbolic Law.

## The law

Take a real quantity with:

- **C1** a continuous way of combining changes,
- **C2** associativity — the order you group them in does not matter,
- **C3** strict monotonicity — more is more,
- **C4** a neutral state — a change that does nothing.

Then (Theorem 1) there is a continuous increasing bijection $\psi$ from the interval to the
whole real line, unique up to a positive scale, with

$$a \oplus b = \psi^{-1}\big(\psi(a) + \psi(b)\big)$$

$\psi$ is the **rapidity**. In it, the law is ordinary addition. And both ends of the interval
sit at $\psi = \pm\infty$. Three things follow immediately:

- No finite sequence of changes reaches either end.
- No change other than the neutral one returns to neutral by repetition.
- Every change generates a flow that approaches the ends only as $t \to \pm\infty$.

**The ceiling is a horizon.** Status: **[P]**. This is Aczél's representation theorem, and the
programme's contribution is not the theorem but the insistence on taking it literally
everywhere its four conditions hold.

## Exactly three laws are possible

For the projective family $u \oplus v = (u+v)/(1 + \kappa uv)$ the generator is
$X(u) = 1 - \kappa u^2$, and there are three cases (Theorem 4):

| $\kappa$ | Fixed points | Type | Behaviour |
| --- | --- | --- | --- |
| $> 0$ | two, at $\pm\kappa^{-1/2}$ | hyperbolic | bounded, two horizons |
| $= 0$ | a double point at $\infty$ | parabolic | unbounded, flat addition |
| $< 0$ | none | elliptic | compact, wraps through $\infty$ |

Every projective composition is conjugate to a rotation, a translation or a dilation. **Flat
addition is not the general case; it is the codimension-one boundary between the other two.**
That is the correspondence principle stated precisely: Euclidean description is the
infinite-ceiling limit, accurate near rest and wrong by a computable amount near any limit.

Status: **[P]** — this is the Cayley–Klein classification and the classification of
one-parameter subgroups of $PSL(2,\mathbb{R})$.

## Arrival or horizon: the boundary exponent

Theorem 18 says that if a real system *does* reach a limit, one of the four conditions failed,
or the drive was unbounded, or the law changed. Proposition 9 says which measurable feature
decides it.

Let the quantity approach its ceiling under $\dot e = X(e)$ with $X(e) \sim (1-e)^\gamma$ near
the ceiling.

- **Deterministic.** The ceiling is reached in finite time if and only if $\gamma < 1$
  (Osgood 1898). Since $\psi = \int de/X$, the horizon theorem *is* Osgood's criterion read
  backwards.
- **Stochastic.** With noise $\sigma(e) \sim (1-e)^\beta$ and drift vanishing at least linearly
  ($\gamma \ge 1$), the boundary is attainable if and only if $\beta < 1$ (Feller 1952).
  Wright–Fisher sampling has $\beta = \tfrac12$, which is why finite populations fix.
- **Maximum-entropy averages have $\gamma \ge 1$** (Proposition 3), so they never arrive under
  finite drive.

Status: **[P]** for the two classical criteria; **[D]** for unifying them under one exponent.

**The physical reading.** $\gamma \ge 1$ means the rate of change vanishes at least as fast as
the room runs out: the drive scales with what is left. That is mass action, first-order
kinetics, every self-limiting process. $\gamma < 1$ means the drive stays finite at the
boundary: a saturated pump, a hard cap imposed from outside, a discrete count.

> In nature, smooth averages have horizons; countable events cross boundaries.

## The far side

The horizon is not the end of the space (Theorem 19). On the projective line the lawful
interval and the outside meet at the horizon points, and:

1. **The law acts on both sides.** $0.5 \oplus 2 = 1.25$. Composition with an inside change
   never carries a state across.
2. **Crossing is inversion plus a quarter turn.** For $|x| > 1$,
   $\operatorname{artanh} x = \operatorname{artanh}(1/x) + i\pi/2$.
3. **In $n$ dimensions the two sides differ in kind.** Inside is hyperbolic space; outside is
   de Sitter space, with the same projective automorphism group. Crossing the light cone
   exchanges timelike and spacelike.

A physical instance: an observer at velocity $v$ has its line of simultaneity at slope $1/v$,
and a boost $u$ sends $1/v$ to $1/(v \oplus u)$ — by the *same* law. Inside the horizon are
observers' velocities; outside are the slopes of their simultaneity lines; one law moves both.

Status: **[P]**, classical.

An earlier hypothesis (H6) proposed testing this at biological boundary events. It has been
**withdrawn**: the reciprocal continuation maps a point just past a horizon back near the
*same* horizon ($1/1.01 = 0.99$), so a variable restarting near zero after fixation does not
test it. Recorded as an open question, not a hypothesis.

## On the site

- [**The horizon**](https://thantiklermcirony.github.io/bounded-observer/#sim-horizon) — add equal steps, watch the value crowd the
  limit while the rapidity climbs evenly.
- [**Three laws**](https://thantiklermcirony.github.io/bounded-observer/#sim-trichotomy) — choose no ceiling, one, or two.
- [**Arrival or horizon**](https://thantiklermcirony.github.io/bounded-observer/#sim-exponent) — turn $\gamma$ through 1.
- [**Beyond the horizon**](https://thantiklermcirony.github.io/bounded-observer/#sim-farside) — push past the edge.

## Sources

- Capstone v2.1, Theorems 1, 2, 4, 7, 8, 17, 18, 19, Propositions 3 and 9 — `papers/capstone/`
- `toolkit/bounded/law.py`, `toolkit/bounded/boundary.py`
- Aczél 1966; Luce and Narens 1976; Osgood 1898; Feller 1952

**Next gate:** [Geometry](5-geometry.md) — the shape of the room inside the horizon.
