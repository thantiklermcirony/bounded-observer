# Gate 5 · Geometry

**What shape is the room inside the horizon?**

In one dimension the rapidity makes the interval infinitely long, and that is all. In two or
more, something else happens: the order of changes can be stored, and the space acquires
curvature.

## Order becomes rotation

In two or more dimensions, bounded composition need not be associative. Proposition 8 gives the
dichotomy: under isometric reassociation defects, either the law is associative everywhere, or
one failure of associativity anywhere forces the whole space into branch (H) — negatively
curved, with a horizon.

In branch (H), the holonomy around a small loop equals curvature times enclosed area
(Theorem 26). For $n = 2$ it lies in $SO(2)$; for $n \ge 3$ in $SO(n)$, which is non-abelian.

This is not an analogy. It is the Levi-Civita connection of hyperbolic space, and the physical
instance is the Thomas–Wigner rotation: an electron's spin precesses in its orbit because
velocity composition is non-associative. Status: **[P]**.

`toolkit/tests/test_theorems.py::test_gyration_equals_triangle_area` checks the identity
numerically: for $a = 0.4 + 0.2i$ and $b = 0.7e^{2i}$ the gyration angle is 0.600 rad and the
hyperbolic triangle area is the same to six decimals.

## What the cone decides

The geometry is not a matter of taste. Theorem 25: suppose the world is a linear system on
$n+1$ channels whose states form a convex cone, observed scale-blind as ratios. Then the
available invariant geometry is fixed by the algebra of those channels.

| Cone | Reversible updates give | Geometry |
| --- | --- | --- |
| Lorentz cone | $\mathbb{R}^+\cdot O(1,n)$ | $\mathbb{H}^n$; composition is Einstein gyro-addition; updates do not commute |
| Positive orthant | positive diagonal × permutations | flat normed space in log-ratio coordinates; boundary still unreachable |
| Positive-definite matrices | symmetric-space isometries | nonpositive but **non-constant** curvature |

Lorentz cones and positive-definite cones exhaust the irreducible symmetric cones
(Koecher–Vinberg); the orthant is the reducible case. A Hilbert geometry is hyperbolic only for
an ellipsoid, and isometric to a normed space only for a simplex.

So: multi-hypothesis Bayesian updating is the orthant, and is flat. Velocity and qubit
filtering are the Lorentz cone, and are hyperbolic. Qutrits and covariance tracking are the
third row, and predict order-memory *without* constant curvature — which is hypothesis **[H]**,
with the test and loss condition in §13 step 8.

### Two cautions that matter

**Forward-only updates are different in kind.** A linear map that sends the cone *into* itself
does not increase the Hilbert projective distance, and if its image has finite projective
diameter $\Delta$ it contracts every distance by at least $\tanh(\Delta/4)$ (Birkhoff 1957;
Bushell 1973). Such maps reduce distinguishability, need not commute even on the orthant, and
preserve no continuous metric — every orbit converges to one ray. Reversible and forward-only
are not two settings of one thing.

**The cone does not fix the physical distance.** An invariant geometry exists only relative to
an admissible group. The qubit's Bloch ball carries the Hilbert metric — hyperbolic, invariant
under every cone automorphism — *and* the Bures metric, invariant only under unitary
conjugation, with finite diameter and positive curvature. Before deriving a curvature, state
the admissible updates and the comparison. This correction was made after an external review;
an earlier version of the theorem treated positive maps as automorphisms.

## The room inside

Here is what being hyperbolic actually changes: **the amount of room.**

In $\mathbb{H}^2$ a circle of radius $r$ has circumference $2\pi\sinh r$ against $2\pi r$ in the
plane. At $r = 1$: 7.4 against 6.3. At $r = 5$: 466 against 31. At $r = 10$: $6.9\times10^4$
against 63.

From outside, the object is small and bounded. From inside, it holds an exponentially large
space of distinctions, and its edge is a horizon.

**Why branching lives there.** A tree with branching factor $b \ge 2$ has $b^r$ nodes at depth
$r$. In Euclidean space of fixed dimension $d$, an embedding with distortion at most $D$ places
these at pairwise distance $\ge 1$ inside a ball of radius about $Dr$, which holds at most
$(CDr)^d$ points — fewer than $b^r$ for large $r$. No such embedding exists. In $\mathbb{H}^2$
every finite tree embeds with distortion arbitrarily close to 1 (Sarkar 2012). Status: **[P]**,
with its assumptions stated: fixed dimension, bounded distortion.

**Where it has been measured** — by others, not by this programme:

- Complex networks: heterogeneous degree distributions and strong clustering follow from a
  hidden hyperbolic geometry, because node taxonomies are approximately trees (Krioukov 2010).
- Smell: natural odour mixtures occupy a low-dimensional hyperbolic space (Zhou 2018).
- Place: rat hippocampal CA1 represents space in a three-dimensional hyperbolic geometry whose
  size grows logarithmically with exploration time (Zhang 2023).
- Development: single-cell hierarchies are better represented on Poincaré maps than flat ones
  (Klimovskaia 2020).

**Hypothesis H7** — an observer storing a branching history in fixed low dimension with bounded
distortion represents it in a negatively curved space whose edge is a horizon, growing with the
logarithm of the history's size. Test: Gromov $\delta$-hyperbolicity and best-fit curvature of
perturbation-response spaces, against flat and spherical alternatives. **Loss condition:** flat
or spherical fits are as good or better. Status: **[H]**.

Two routes reach the same geometry: composition (this paper) and branching (H7). Whether they
are two views of one fact is open.

## On the site

- [**The room inside**](https://thantiklermcirony.github.io/bounded-observer/#sim-room) — grow circles and a branching tree.
- [**Round and back, turned**](https://thantiklermcirony.github.io/bounded-observer/#sim-holonomy) — walk a loop, return rotated.
- [**Channels that forget**](https://thantiklermcirony.github.io/bounded-observer/#sim-channels) — reversible against forward-only.

## Sources

- Capstone v2.1, §5.2, §8, Theorems 24–28, Propositions 8 and 10 — `papers/capstone/`
- `toolkit/bounded/disk.py`, `toolkit/bounded/cones.py`
- Birkhoff 1957; Bushell 1973; Faraut and Korányi 1994; Sarkar 2012; Bourgain 1986

**Next gate:** [Prediction](6-prediction.md) — does any of it win on data it has never seen?
