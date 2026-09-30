---
title: "Bounded Composition and Its Horizons: when a bounded quantity earns an additive chart, a horizon and a geometry"
author:
  - "Daniel John Murray — Independent Researcher, Melbourne, Victoria, Australia. ORCID 0009-0005-1794-5945. Correspondence: danber1515@gmail.com"
date: "30 September 2026 — version 2.1"
abstract: |
  A bounded quantity whose changes combine continuously, associatively, monotonically and with a resting state has an additive coordinate, its rapidity, in which the bound is a horizon that no finite sequence of such changes reaches. The representation is classical (Hölder; Aczél; Luce and Marley; Luce and Narens; representable uninorms). We state it as a conditional law, the Universal Hyperbolic Law (UHL), and ask the question that decides its use: which real systems earn a chart, a horizon and a geometry. Gates come in order: physical access, a predictive state, admissible actions whose effect from rest fixes their effect everywhere, a composition law with its chart and boundary rate, an operational geometry, and held-out prediction. Maximum-entropy averages over a bounded variable never reach their ceilings; their boundary exponent is at least 1 and is set by the microscopic reference measure (1 for an isolated end state, 2 for a power-law density, every value between for an end state beside a density, and larger values for densities that vanish faster than any power), and the remaining gap obeys an explicit lower bound. Two small interventions share one rapidity exactly when their order effect $fg'-gf'$ vanishes at every state. When an observer reads a linear world through ratios, transitions are projective; two horizons force the logit law and one horizon the Hamacher family. The same law acts on the far side of a horizon, with the value reciprocated; in relativity the far side is the set of simultaneity slopes. In two or more dimensions, reversible updates of the observer's channel cone preserve a projective geometry (flat for the orthant, hyperbolic for the Lorentz cone), while forward-only positive updates contract it and, under repetition, erase distinguishability; which physical distance is measured depends on the observer's comparison. We read the law across relativity, optics, evolution, pharmacology and belief, sort 38 puzzles by which condition holds (12 re-read, 11 turned into tests, 15 outside), give a test protocol, and report a replication of effect-measure heterogeneity across 19 meta-analyses and a pre-registered drug-combination prediction that failed as stated, reproduced independently. Every claim carries its status.
keywords: "bounded composition; rapidity; hyperbolic geometry; uninorms; measurement theory; symmetric cones; observer"
---

# 1. Introduction: the flat default, and what this paper claims

Much of quantitative science inherits one assumption from Euclid: quantities extend without limit, and limits are added afterwards. Ceilings enter models as caps, clipping, saturation terms or constraints. The default space is flat, and a bound is an exception to it.

Yet the quantities we measure are very often bounded. Speeds are bounded by $c$. Fractions, probabilities and occupancies are bounded by 0 and 1. Concentrations are bounded by the pools they are drawn from, beliefs by certainty, and reflection coefficients by total reflection.

This paper takes the opposite default. The limit comes first, and together with a lawful way of combining changes it generates the structure.

## 1.1 The claim, stated with its scope

**The law.** If a quantity is bounded and its changes combine continuously, associatively, monotonically and with a resting state, then there is a coordinate in which changes add, and the bound sits at infinity in that coordinate (Theorems 1–2). We call this the Universal Hyperbolic Law. It is universal in the sense every theorem is universal: it holds without exception for every system that satisfies its conditions. Which real systems satisfy them is an empirical question, answered system by system (§13). No prevalence across nature is claimed or measured here.

**What is classical.** The ingredients are old, and we use them as such.

- **Ordered structures.** Hölder (1901) showed that an Archimedean ordered group embeds in $(\mathbb R,+)$. Aczél (1949, 1966) proved that every continuous, associative, strictly monotone operation on an interval has an additive coordinate. In measurement theory, Luce and Marley (1969) axiomatised bounded concatenation with a maximal element, with relativistic velocity as the motivating example; Luce and Narens (1976) gave the first qualitative characterisation of the relativistic addition law; Krantz, Luce, Suppes and Tversky (1971) built the general programme of earning a numerical scale from qualitative axioms. In fuzzy aggregation the same operations are the representable uninorms (Dombi 1982; Fodor, Yager and Rybalov 1997), and the rational one-horizon laws are Hamacher's family (Hamacher 1978; Klement, Mesiar and Pap 2000).
- **Relativity and geometry.** Einstein (1905), Varićak (1910), Ignatowski (1910), Bacry and Lévy-Leblond (1968), Lévy-Leblond (1976), Anker and Ziegler (2020); the Cayley–Klein classification (Yaglom 1979); Ungar (2008) for gyrogroups; Friedman (2005) for physics on bounded balls; Kay (1967) and Foertsch and Karlsson (2005) for which bounded domains are hyperbolic or flat; Faraut and Korányi (1994) for symmetric cones.
- **Bounded addition beyond velocity.** Vigoureux (1992) and Giust, Vigoureux and Lages (2009) for reflection coefficients; Monzón et al. (2002) and Barriuso et al. (2004) for the classification and the Wigner angle of multilayers; Hájek (1985) and Heckerman (1986) for certainty degrees; Amari and Nagaoka (2000) for the Legendre duality behind Theorem 3; Osgood (1898) and Feller (1952) for arrival at a boundary.
- **Measured hyperbolic information spaces.** Krioukov et al. (2010) for networks; Zhou, Smith and Sharpee (2018) for olfaction; Zhang, Rich, Lee and Sharpee (2023) for the hippocampus; Klimovskaia et al. (2020) for single cells.

**What is new here.** Five things, each modest, each testable:

1. **A conditions-based law across domains**, with a protocol that tests the conditions (§13) and a register that sorts known puzzles by which condition holds or fails (§12).
2. **Where the law applies and where it stops.** A scalar summary of history has three fates (Proposition 1); interventions must also pass an action gate (§5.1); maximum-entropy averages have horizons, with a boundary exponent of at least 1 set by the reference measure and an explicit lower bound on the remaining gap (Proposition 3); two mechanisms share a rapidity exactly when their order effect vanishes (Proposition 6); arrival at a ceiling is decided by a boundary exponent (Theorem 18, Proposition 9); and the far side of the horizon carries the same law (Theorem 19).
3. **The observer's route to projectivity, and what the cone of the observer's channels decides** in higher dimensions: which reversible updates preserve a geometry, which forward-only updates contract it, and why the measured distance also depends on the observer's comparison (Theorems 6 and 25).
4. **An interaction law in rapidity**, and the conditions under which detailed balance forces a sinh coupling (Theorems 13–16).
5. **The classical drug-combination laws placed on one Hamacher dial** (Theorem 8), together with a pre-registered test of the mechanistic reading of that dial, which failed as stated (§13.3).

**The name.** "Universal Hyperbolic Law" is unrelated to Wildberger's *Universal Hyperbolic Geometry* (Wildberger 2013).

**Words.** "Lawful" means satisfying conditions C1–C4 of §2.1, and nothing more. "Horizon" means an end of the interval that sits at infinite rapidity. In one dimension we speak of the *nonlinearity of a chart*, never of curvature; geometric curvature enters only in two or more dimensions (§8).

## 1.2 Order of the argument, and corrections to earlier work

**Logical order.** The order of gates is: physical access → predictive state → admissible actions → chart and boundary kinetics → operational geometry → held-out prediction. A quantity can obey a composition law only if it is first a *state*: histories it identifies must have the same future under every admissible intervention (Theorem 10; Murray 2026a, 2026h). Its interventions must then pass a separate gate: an intervention's endpoint from rest must determine its action from every state (§5.1). Predictive closure is therefore logically prior to this law, and the law begins where a scalar summary has earned regular closure (Proposition 1). We present the law first because it is the object of this paper, but every application goes through the state and action tests first (§13, steps 0 and 2).

**Where this paper corrects the author's earlier work.**

- Boundedness alone does not select the artanh chart (§2.4). This corrects Murray (2026c) and the one-dimensional step of Murray (2026r).
- The rapidity is unique up to positive scale, with zero fixed by the neutral state, not "up to positive affine" maps as stated in Murray (2026g, 2026k).
- Bounded gyro-associative composition does not by itself force Einstein addition, as Murray (2026s) and Murray (2026d, §8) suggested. A rigidity condition or a holonomy selector is needed (§8).
- Bliss independence is hyperbolic, not parabolic, as stated in Murray (2026t).
- The "exactly five classes" of Möbius drug-combination laws (Murray 2026b) hold only when fixed points are restricted to $\{0,1,\infty\}$ (Murray 2026e, Theorem B); Theorem 8 gives a continuum.
- Version 1.0 of this paper claimed that the dial position measures mechanistic overlap. That prediction was tested and failed (§13.3); it is restated here.
- An earlier draft of version 2.0 credited Luce and Marley (1969) with deriving the relativistic addition law. They did not; Luce and Narens (1976) did.
- Version 2.0 treated every positive update of a cone as an automorphism, stated observer centrality for all bounded laws, gave a fixation test (H6) that does not probe the far side of the horizon, and stated H7 without dimension or distortion assumptions. Version 2.1 corrects all four (Theorems 25 and 29, §7.4, §8.4), following an external review whose mathematical claims were each checked here.

**Plan.** Part I states and proves the law (§2–§8). Part II reads it in physics, life and mind and sorts known puzzles (§9–§12). Part III gives the protocol, the two empirical results and the claim register (§13–§15). Appendix A holds proofs; Appendix B the verification record.

**Status tags.** Every claim carries one of three tags:

- **[P]:** proven here; or a classical result with a citation; or proved in full in a cited paper by the author, in which case §15 names the paper and the result awaits independent checking like a [D].
- **[D]:** derived here, with the proof in the text or in Appendix A. It awaits independent checking.
- **[H]:** a hypothesis, with a stated test and a stated loss condition.

# Part I — The Law

# 2. When a bounded quantity has a law, and what the law says

## 2.1 Conditions

Let a quantity $x$ take values in an interval $I$ with at least one finite end. Let changes combine by an operation $\oplus: I \times I \to I$. The law requires four conditions:

- **C1 (continuity).** Small changes in the inputs give small changes in the result.
- **C2 (associativity).** $(a\oplus b)\oplus c = a\oplus(b\oplus c)$. How past changes are grouped does not matter.
- **C3 (strict monotonicity).** Increasing either input strictly increases the result.
- **C4 (neutral state).** There is an element $e$ with $a\oplus e = e\oplus a = a$.

Boundedness alone forces nothing. The law is boundedness together with lawful combining. C3 is the condition that does the most work: it is what distinguishes a *strict* operation, whose generator diverges at the bound, from a *nilpotent* one, whose generator is finite there and whose bound is reached (Ling 1965; Klement, Mesiar and Pap 2000). The bounded sum $\min(1,a+b)$ is associative, continuous and monotone, but not strictly so at the bound; it reaches its ceiling. Section 7 says what decides, physically, which kind a system is.

## 2.2 The three fates of a scalar summary

**Proposition 1 (closure trichotomy; Murray 2026a).** Suppose a scalar summary $L(h)$ of a history $h$ is proposed as a state, and suppose sequential histories combine by $L(h_1;h_2)=F(L(h_1),L(h_2))$. Then exactly one of three cases holds:

- **Case I (no closure).** No single-valued $F$ exists. Equal values of $L$ support different futures, so $L$ is not a state.
- **Case II (lawful closure outside the regular class).** $F$ exists and is associative, but a regularity condition fails: continuity (C1), strict monotonicity (C3), the neutral state (C4), or cancellativity. Idempotent, absorbing, max-like and min-like laws are examples. They erase distinctions irreversibly while remaining lawful.
- **Case III (regular closure).** $F$ satisfies C1–C4. The law of this paper applies.

Status: [P]. Associativity follows because concatenation of histories is associative.

This paper is the theory of Case III. Theorem 18 locates every arrival at a boundary in Case I or II, in an unbounded drive, or in a change of law.

## 2.3 The horizon theorem

**Theorem 1 (group case: neutral state inside).** Suppose $e$ lies inside $I$. Then there is a continuous increasing bijection $\psi: I \to \mathbb{R}$ with $\psi(e)=0$, the *rapidity*, such that
$$a\oplus b = \psi^{-1}\big(\psi(a)+\psi(b)\big).$$
$\psi$ is unique up to a positive scale factor. Both ends of $I$ lie at $\psi = \pm\infty$, and three consequences follow:

- No finite sequence of changes reaches either end.
- No change other than $e$ returns to $e$ by repetition.
- Every change generates a flow $t\mapsto\psi^{-1}(t\psi(a))$ that approaches the ends only as $t\to\pm\infty$.

Status: [P]. Aczél's theorem gives $\psi$ onto an interval $K \ni 0$ closed under addition; an interval closed under addition that contains $0$ in its interior is all of $\mathbb{R}$, and $0=\psi(e)$ is interior because $e$ is. In measurement theory this is a bounded extensive structure (Luce and Marley 1969); in fuzzy aggregation, a representable uninorm (Fodor, Yager and Rybalov 1997). The operation is commutative, so a single associative scalar law cannot encode the order of its inputs (§5.1).

**Theorem 2 (monoid case: neutral state at an end).** Suppose $e$ sits at the finite end $\alpha$ of $I=[\alpha,\beta)$. Then there is a continuous increasing bijection $\psi: I\to[0,\infty)$ with the same additive law. The far end $\beta$ is at $\psi=+\infty$, and no finite sequence of changes reaches it.

Status: [P]. Aczél's theorem applies on $[\alpha,\beta)$, because C3 gives cancellativity. Ling (1965) covers the weakly monotone Archimedean case, which is where the nilpotent laws live.

The **group case** has two horizons and a resting state between them: velocity, belief, the logit law. The **monoid case** has one horizon and a resting state at the other end: dose effects that start from zero, survival under independent hazards, accumulating damage.

![Equal steps in rapidity crowd toward a horizon they never reach. Top: eight equal rapidity steps of 0.3. Bottom: the same steps as read by an interior observer, $x=\tanh\psi$.](fig1_horizon.png){width=90%}

## 2.4 What the law fixes, and what the system supplies

The law has two layers:

- **Universal layer:** a rapidity exists, the horizons sit at infinite rapidity, and change is additive in rapidity. C1–C4 force these.
- **Local layer:** the system's own physics supplies which rapidity applies, through the definition of the quantity, its microscopic states and its mechanism.

Boundedness does not select the chart. A tangent-based law and Einstein's law both satisfy C1–C4 on $(-1,1)$, yet they combine 0.3 and 0.5 differently: 0.63 against 0.70. Any increasing bijection $\psi:(-1,1)\to\mathbb R$ defines a lawful bounded group, and for generic $\psi$ its maps are not fractional-linear (Murray 2026a). The axioms cannot tell these laws apart; only the system can. Sections 3 and 4 show how the system decides.

# 3. Which chart: maximum entropy, and the flat limit

## 3.1 The rapidity is the gradient of negentropy

When a bounded quantity is the average of a microscopic variable at maximum entropy, its natural coordinate is forced. That coordinate is the slope of the negentropy. The neutral state is the maximum-entropy state, and the horizons are where fluctuations vanish.

**Setting.** Let a microscopic variable $s$ take values in a bounded set $S\subset[s_{\min},s_{\max}]$ with reference measure $\mu$, finite and not concentrated at one point. Take the distribution of maximum entropy with a given mean $m$: $p_\theta(s)\propto e^{\theta s}$ relative to $\mu$.

**Theorem 3 (negentropy).**

1. The map $\theta\mapsto m(\theta)$ is an increasing bijection from $\mathbb{R}$ onto the interior of the convex hull of $\operatorname{supp}\mu$.
2. $\theta = dJ/dm$, where $J(m)$ is the negentropy: the entropy deficit, relative to $\mu$, below its maximum.
3. The generator of the flow $\theta\mapsto m$ is $X(m) = dm/d\theta = \mathrm{Var}_\theta(s)$. Horizons are exactly the states where fluctuations vanish.
4. $\theta=0$ is the maximum-entropy state. As $m$ approaches either end, $\theta\to\pm\infty$ and the entropy decreases to a limit: $\ln\mu(\{s_{\mathrm{end}}\})$ when the end value is an atom of $\mu$, and $-\infty$ when it is not.

Status: [P], classical (Barndorff-Nielsen 1978; Amari and Nagaoka 2000; Wainwright and Jordan 2008). The contribution is the reading: the rapidity of a maximum-entropy bounded quantity is the slope of its negentropy.

**Proposition 2 (negentropy in rapidity).** For two states, $J(\theta)=\theta\tanh\theta-\ln\cosh\theta$, which is $\approx\theta^2/2$ near rest and rises to $\ln2$ at either horizon; along any motion $dJ/dt=\theta(1-m^2)\dot\theta$. Status: [P], the Legendre dual of item 2 (A.15). Perfect order is a horizon: each unit of rapidity near it buys an exponentially smaller gain in negentropy. Near rest the negentropy is the quadratic excess in rapidity, which is the energetic reading used for recovery after perturbation in Murray (2026k); away from rest the two correspond only monotonically.

**Proposition 3 (maximum-entropy averages never reach their ceiling).** Under the setting above, with $L=s_{\max}-s_{\min}$,
$$X(m)=\mathrm{Var}_\theta(s)\le L\,(s_{\max}-m),$$
so the generator vanishes at least linearly at the ceiling, and $\int^{s_{\max}}dm/X(m)=\infty$. A finite drive in $\theta$, or any dynamics $\dot m=k\,X(m)$ with $k$ bounded, therefore never reaches the ceiling. In the three commonest cases the exponent is exact: $X\sim(s_{\max}-m)^\gamma$ with $\gamma=1$ when $\mu$ has an isolated atom at $s_{\max}$ (two states, the logit chart), $\gamma=2$ when $\mu$ has no atom at the end and a density $\sim u^a$, $a>-1$, there (the Langevin chart, and every density continuous and positive at the end), and, when an atom at $s_{\max}$ meets a density $\sim c\,u^a$ ($a>-1$) beside it, $\gamma=1+1/(a+2)$, which runs continuously from 2 ($a\to-1$) to 1 ($a\to\infty$) and equals $3/2$ for a density positive at the end. Every reference measure gives $\gamma\ge1$. There is no upper bound: a density $e^{-1/u}$ at the end gives $X\approx(s_{\max}-m)^3/2$, so $\gamma=3$.

**Corollary (the cost of approach).** Along any motion driven by a nonnegative rate $k(t)=\dot\theta$, the remaining gap $\delta=s_{\max}-m$ obeys
$$\delta(t)\ge\delta(0)\exp\Big[-L\int_0^t k\,dt'\Big].$$
This turns "cannot arrive under finite drive" into a number an experiment can challenge: a measured gap below the bound refutes the maximum-entropy reading of that quantity.

Status: [P] for the bound, the divergence and the corollary (A.16); the exponents are derived in A.16 and verified numerically (Appendix B), [D]. A measured local exponent that drifts down from 2 toward $1+1/(a+2)$ as the ceiling is approached ($3/2$ for a density positive at the end; 1 only if the endpoint state is isolated) signals a rare endpoint state beside a continuum; a local exponent above 2 signals a density vanishing faster than any power.

**Consequence.** A bounded quantity that is reached in finite time is not a maximum-entropy average. Arrival needs a hard external cap, a saturated flux, or a discrete count (§7).

**When is $\theta$ a composition rapidity?** Contributions that add to the energy difference add in $\theta$: external fields on one variable, modulators that each multiply an affinity. These multiply the Boltzmann ratio, so $\theta$ satisfies C1–C4 with neutral state $\theta=0$. Contributions that add Boltzmann *weights* do not add in $\theta$; competing ligands at one site are the standard example, and they give Loewe additivity instead (§4.5). Status: [D].

| Microscopic states | Mean | Generator $X(m)$ | Chart | $\gamma$ |
|---|---|---|---|---|
| Two states $\{-1,1\}$ | $m=\tanh\theta$ | $1-m^2$ | Einstein, $\theta=\operatorname{artanh} m$ | 1 |
| Continuum $[-1,1]$, uniform | $m=\coth\theta-1/\theta$ | $1/\theta^2 - \operatorname{csch}^2\theta$ | Langevin | 2 |

In thermal systems $\theta$ is an energy in units of $k_BT$: for a two-state occupancy with gap $\Delta G$, $\operatorname{logit}p=-\Delta G/k_BT$. In belief, $\theta$ is accumulated evidence (§11).

**A caution on distance.** "Infinitely far" refers to rapidity. In the Fisher information metric the two-state interval has finite length $\pi$; for the Langevin continuum it is infinite. What holds in every metric is that no finite sequence of lawful changes reaches a horizon.

## 3.2 The correspondence principle: flat as a limit

Flat, additive description is the member of the composition family whose ceiling is sent to infinity. For velocities derived from linear, homogeneous, isotropic transformations, Ignatowski (1910) and Lévy-Leblond (1976) leave one family,
$$u\oplus v=\frac{u+v}{1+\kappa uv},\qquad \kappa\in\mathbb{R},$$
with $\kappa=0$ flat and $\kappa>0$ bounded by $\ell=\kappa^{-1/2}$. Status: [P] for velocity.

In the two-horizon chart the rapidity is $\psi=\ell\operatorname{artanh}(x/\ell)=x+x^3/3\ell^2+\cdots$, so a flat model under-reads rapidity by $\approx\tfrac13(x/\ell)^2$:

| Fraction of the ceiling | Rapidity excess over flat, $\psi/x-1$ |
|---|---|
| 10% | 0.3% |
| 50% | 10% |
| 90% | 64% |
| 99% | 167% |

Status: [P] in the Einstein chart. The error has a fixed sign: near a limit, flat models underestimate how much further push is needed. This is the source of diminishing returns and ceiling effects, and of the failure of averages taken across people at different distances from their limits.

**Proposition 4 (the lawful mean; Kolmogorov 1930, Nagumo 1930; applied in Murray 2026g).** An average that commutes with lawful composition is the quasi-arithmetic mean in rapidity, $\bar x_\psi=\psi^{-1}(\mathbb E\,\psi(x))$; the only other quasi-arithmetic means with this property are the exponential means in rapidity, $\psi^{-1}(k^{-1}\log\mathbb E\,e^{k\psi(x)})$, which reduce to $\bar x_\psi$ as $k\to0$ (Hardy, Littlewood and Pólya 1934, Thm 84). For values spread with variance $\sigma^2$ about $\mu$, $\bar x_\psi-\mu\approx\psi''(\mu)\sigma^2/2\psi'(\mu)$. In the two-horizon chart $\psi''/\psi'=2x/(\ell^2-x^2)$, so above rest the arithmetic mean lies below the lawful mean, by $\approx\sigma^2/2(\ell-\mu)$ near the ceiling, never exceeding the headroom. Status: [P] (A.17).

## 3.3 The trichotomy, and a parameter that crosses it

**Theorem 4 (trichotomy).** For $u\oplus v=(u+v)/(1+\kappa uv)$ the generator is $X(u)=1-\kappa u^2$:

| $\kappa$ | Real fixed points of $X$ | Type | Behaviour |
|---|---|---|---|
| $\kappa>0$ | two, at $\pm\kappa^{-1/2}$ | hyperbolic | bounded, two horizons |
| $\kappa=0$ | a double point at $\infty$ | parabolic | unbounded, flat addition |
| $\kappa<0$ | none | elliptic | compact: $u\oplus v=\tan(\arctan u+\arctan v)$ wraps through $\infty$ |

Status: [P]. This is the classification of one-parameter subgroups of $PSL(2,\mathbb{R})$, the Cayley–Klein classification (Yaglom 1979), and the classification of lossless multilayers (Monzón et al. 2002). For velocity, causality excludes $\kappa<0$: with $\kappa=-1$, $2\oplus2=-4/3$.

Every projective composition is conjugate to a rotation (no fixed point; compact), a translation (one fixed point; Loewe additivity, or flat addition when the point is at $\infty$), or a dilation (two fixed points; Einstein when both bound the interval, the one-horizon family when one lies outside). Flat is the codimension-one boundary between the hyperbolic and elliptic ranges. Status: [P] for the classification; the reading beyond kinematics and optics is [D].

**A parameter can carry a system through the trichotomy.** In $\dot x=M(\mu-x^2)$, $\mu>0$ gives two fixed points, $\mu=0$ a double point, and $\mu<0$ none, with finite passage time $[\arctan(x_i/\sqrt{-\mu})-\arctan(x_f/\sqrt{-\mu})]/(M\sqrt{-\mu})$. Murray (2026l) uses this for finite rescue windows in redox biology. When fixed points annihilate the law itself has changed: case 5 of Theorem 18.

**Theorem 5 (the compact case).** Replace C3 by cyclic monotonicity on a circle: each map $x\mapsto a\oplus x$ is an orientation-preserving homeomorphism of the circle. Then inverses exist, the circle is a topological group, and a connected topological group that is a one-dimensional manifold is $(\mathbb{R},+)$ or $U(1)$ (Pontryagin 1939; Montgomery and Zippin 1955). The circle is compact, so there is an angle $\vartheta$, unique up to sign, with $a\oplus b=\vartheta^{-1}(\vartheta(a)+\vartheta(b)\bmod 2\pi)$. A full turn is a built-in unit, and repeated changes return arbitrarily close to the neutral state. Phases and angles live here, and so do the $U(1)$ factors of rotation and gauge groups. For the elliptic law of Theorem 4, $\vartheta=2\arctan(\sqrt{-\kappa}\,u)$. Status: [P].

![Left: the three generators of Theorem 4. Right: the projective line closed into a circle. The lawful interval $|x|<1$ (blue) and the far side $|x|>1$ (brown) meet at the two horizons, the far side closing through $\infty$; §7.4 shows that one law acts on both arcs.](fig2_trichotomy.png){width=100%}


# 4. Classification by horizon count

Once composition is projective, the number of horizons fixes the law. Two horizons force Einstein composition uniquely. One horizon allows exactly one continuous family, and each classical drug-combination law with Hill slope 1 sits on it.

## 4.1 The projective condition and where it comes from

A composition is **projective** when each partial map $x\mapsto a\oplus x$ is a Möbius map, that is, a ratio of linear functions. Boundedness does not make a law projective (§2.4). Projectivity has to be earned, and the following theorem says how.

**Theorem 6 (observation projection; Murray 2026a).** Suppose the world carries two channels that update linearly, $z'=Mz$ with $M\in GL(2,\mathbb R)$. Suppose the observer identifies all common rescalings $z\sim\lambda z$ and reads only $q=z_1/z_2$ on the chart $z_2\ne0$. Then:

1. **Forward.** Every observed transition is fractional-linear on states with $cq+d\neq0$, and cross-ratios of any four states are preserved:
$$q'=\frac{aq+b}{cq+d},\qquad ad-bc\neq0.$$
2. **Converse.** Let a map from a real interval into the projective line be continuous and injective, and let it preserve all cross-ratios. Then it is the restriction of a fractional-linear map, and it has a two-dimensional homogeneous linear representative that is unique up to a nonzero scalar.
3. **Continuous form.** If the world evolves as $\dot z=Az$ with $A=\begin{pmatrix}a&b\\c&d\end{pmatrix}$, then $q$ obeys the Riccati equation $\dot q=b+(a-d)q-cq^2$.

Status: [P]. All three items are classical: projectivisation $GL(2)\to PGL(2)$; the converse, since a cross-ratio-preserving map is fixed by the images of three points; and the linear–Riccati correspondence. Murray (2026a) states the converse in this observational form and uses cross-ratio as a parameter-free empirical test.

Invertibility gives injectivity but not positivity. For $q$ to stay in a positive chart, $M$ must also preserve the positive cone.

**Proposition 5 (the generator is the observer's Riccati field).** On $[0,1]$ a projective law is generated by a quadratic vector field, and its rapidity satisfies $\psi' X=1$:
$$X(e)=A+Be+Ce^2,\qquad \psi(e)=\int\frac{de}{X(e)}.$$
This is item 3 of Theorem 6 with $A=b$, $B=a-d$ and $C=-c$. A horizon is an end where the field vanishes. Theorems 7 and 8 therefore classify the continuous observer laws of Theorem 6 by where their fixed points sit. Status: [P].

A Möbius *transition* becomes a projective *composition law* when two further things hold:

- the admissible updates form a one-parameter group acting simply transitively on $I$;
- each state is the image of $e$ under exactly one update.

So the projective condition reduces to three assumptions:

- a linear two-channel world;
- a ratio-reading observer;
- updates that form a one-parameter group.

Examples are common:

- **Velocity** is the ratio of two linearly transformed channels, $x$ and $t$.
- **Odds** are a ratio of two likelihood channels.
- **Occupancy** is fixed by the ratio of bound to free.

**Corollary (projective equivalence; Murray 2026a).** Suppose two domains independently read scale-blind coordinates of homogeneous linear processes. Then their transformation families belong to the same projective class. The same observational constraint gives the same mathematics, but the same mathematics does not imply the same physics. Status: [P].

This corollary is why one law recurs in relativity, multilayer optics, the Smith chart, binary inference and two-allele selection. Its converse caution also matters. A scalar can close perfectly well in a non-projective chart, so a failure of cross-ratio preservation does not by itself imply hidden state (Murray 2026a).

## 4.2 Two horizons force Einstein

**Theorem 7 (two horizons).** A projective group law on the open interval $(0,1)$ (both ends are then horizons, Theorem 1) has $X(e)=c\,e(1-e)$. Its rapidity, up to scale, is the logit measured from the resting state $e_0$, $\psi(e)=\log[e/(1-e)]-\log[e_0/(1-e_0)]$. When $e_0=\tfrac12$, the maximum-entropy point, $s=2e-1$ gives $\psi=2\operatorname{artanh}s$, which is Einstein composition on $(-1,1)$; any other $e_0$ gives the same law conjugated by a rapidity shift.

Status: [P]. The condition $X(0)=X(1)=0$ forces $A=0$ and $B=-C$.

The resulting operation, $xy/[xy+(1-x)(1-y)]$ on $(0,1)$ (it is undefined at the endpoint pair $(0,1)$), is the standard logit uninorm of fuzzy aggregation (Dombi 1982; Fodor, Yager and Rybalov 1997). What Theorem 7 adds is uniqueness: under projectivity, the logit law is, up to the position of its resting state, the only law whose resting state lies between two horizons. This is the precise sense in which Einstein composition is canonical.

**Physical origin.** By Theorem 3, maximum entropy over two microscopic states gives the Einstein chart for energy-additive contributions: spins in fields, and binding sites modulated through their affinity. Status: [D]. Weight-additive contributions give Loewe additivity instead (§4.5).

## 4.3 One horizon gives one dial

**Theorem 8 (one horizon).** Suppose a projective law rests at $e=0$, has its horizon at $e=1$, and has no interior fixed point. Then for some $\alpha\le1$:
$$X(e)=(1-e)(1-\alpha e),\qquad \psi_\alpha(e)=\frac{1}{1-\alpha}\log\frac{1-\alpha e}{1-e},\qquad a\oplus b=\frac{a+b-(1+\alpha)ab}{1-\alpha ab}.$$
The classical laws are points on this dial:

- **$\alpha=0$: Bliss independence.** $1-e$ combines by multiplication.
- **$\alpha\to1$: Loewe additivity.** This limit is parabolic, and odds add. It is the parabolic boundary of the dial, as flat addition is in Theorem 4.
- **$\alpha=-1$: the Einstein t-conorm** $(a+b)/(1+ab)$ restricted to $[0,1)$. On $[0,1)$ it rests at 0 and has one horizon. The same formula on $(-1,1)$ rests at 0 between two horizons (Theorem 7). The formula is shared, but the laws are different.
- **$\alpha\to-\infty$: a limit, not the logit law.** The rescaled field tends to $e(1-e)$, but the operations tend to the discontinuous drastic sum. The logit law is not a member of this family; it is the two-horizon case of Theorem 7.

Status: [P] for the family; [D] for the placement of the drug laws. $\psi_\alpha$ is the additive generator of the Hamacher t-conorm with parameter $\lambda=1-\alpha\ge0$. Hamacher (1978) showed that these are the only t-norms and t-conorms that are rational functions (Klement, Mesiar and Pap 2000).

![The one-horizon dial: combined effect of two equal single-agent effects for four values of $\alpha$. Loewe (odds-additive) and Bliss are its two named landmarks; $\alpha=-1$ is the Einstein t-conorm on $[0,1)$.](fig5_dial.png){width=62%}

Three remarks place the dial:

- **Tsallis composition.** The Tsallis $q$-sum $x+y+(1-q)xy$ with $q>1$ is the Bliss point after rescaling. With $e=(q-1)x$ it becomes $e_1+e_2-e_1e_2$, with ceiling $1/(q-1)$. Status: [P].
- **The marked triple.** Murray (2026e, Theorem B) found exactly four boundary-identity Möbius flows when fixed points are restricted to $\{0,1,\infty\}$. On the dial these are $\alpha\in\{0,1\}$ and their mirror images (§4.4). Every other $\alpha$ has its second fixed point at $1/\alpha\notin\{0,1,\infty\}$. So the "exactly five classes" of Murray (2026b) require that restriction, and Theorem 8 gives the full one-horizon family.
- **Hill slope.** Loewe additivity sits on the dial only for Hill slope 1. For slope $n$, Loewe additivity adds $[e/(1-e)]^{1/n}$, which is not projective for $n\neq1$ (Murray 2026z).

## 4.4 Duality

The exchange $e\leftrightarrow1-e$ maps the family resting at 0 onto the family resting at 1:

- Inverse-odds combination is Loewe read from the other side.
- Multiplicative combination is Bliss read from the other side.

The five classical drug-combination laws are therefore five landmarks:

- two points on one dial: Bliss at $\alpha=0$, and its parabolic end, Loewe;
- their two mirror images;
- the separate, self-dual two-horizon logit law.

## 4.5 How the system chooses its point

Mass action selects the landmark (Murray 2026b, 2026z). Status: [D].

- **Two agonists at one shared site** add Boltzmann weights, which gives Loewe additivity.
- **Independent mechanisms** give Bliss independence.
- **Two modulators that each multiply an affinity** add energies, which gives the logit law.

Existing frameworks also unify Bliss and Loewe by fitting interaction surfaces: Greco, Bravo and Parsons (1995), BRAID (Twarog et al. 2016) and MuSyC (Meyer et al. 2019). The dial differs from these in one respect. It is not a fitted surface; it is the complete one-horizon family forced by projectivity, and its parameter has a mechanistic reading.

**Hypothesis H1 (restated).** For two agents that act on the same molecular target, the combination surface follows Loewe additivity computed from the fitted single-agent curves; for agents with independent mechanisms it follows Bliss independence. The dial position $\alpha$ is a valid one-number summary of that prediction only when both agents have Hill slope near 1 and full efficacy, because Loewe additivity leaves the projective dial otherwise (§4.3). Version 1.0 stated H1 as "$\alpha$ measures mechanistic overlap"; that form was tested and failed (§13.3). Loss condition for the restated form: across a screen with replicates and many shared-target pairs, the Loewe surface fits shared-target pairs no better than the Bliss surface does.

# 5. Associativity is the compression of history

C2 says that a lawful bounded system's present state summarises its past. Changes drawn from one law forget their order. When the associativity of a multi-dimensional law fails, the order is kept as holonomy.

## 5.1 The present is the sum of the past

**Theorem 9.** Let a system receive changes $a_1,\dots,a_n$ that combine under one law satisfying C1–C4. Then its state is
$$x_n=\psi^{-1}\Big(\sum_i\psi(a_i)\Big).$$
The state carries the net effect of the past but not its grouping. The law is commutative (Theorem 1), so the order of events is also forgotten. Status: [P]. Murray (2026o, Theorem 3) proves the same result as "terminal additive compression is order-free".

**Proposition 6 (when one dimension remembers order).** Order is forgotten in one dimension exactly when the maps representing the changes commute. This holds in particular when every change acts by composing with a fixed element of one law, that is, by a translation in one rapidity (Theorem 12). Changes that act by non-commuting maps keep order in a single bounded scalar. Two examples:

- **Affine maps.** Take $x=\tanh z$ with changes $T_d:z\mapsto qz+b(d)$, $q\ne1$. Then "$a$ then $b$" minus "$b$ then $a$" equals $(q-1)[b(a)-b(b)]\neq0$ (Murray 2026p).
- **Different composition classes.** Generators from different classes do not commute in $\mathfrak{sl}(2,\mathbb R)$, so they give order effects between classes (Murray 2026b).

**A test for a shared rapidity.** Let two small interventions act as flows of the vector fields $f(x)\partial_x$ and $g(x)\partial_x$, with sizes $\varepsilon$ and $\eta$. Then "$f$ then $g$" minus "$g$ then $f$" equals $\varepsilon\eta\,(fg'-gf')+O(3)$. If $fg'-gf'=0$ on an interval where $f\neq0$, then $(g/f)'=0$, so $g=cf$ and both interventions are translations in the one rapidity $\psi=\int dx/f$. The order effect measured across states is therefore a direct test of whether two mechanisms share a composition law, before any chart is fitted.

Status: [P] (A.18).

More generally, order effects probe the commutator of two change generators, and effects of waiting probe the commutator of a generator with the free evolution. Neither is forced by the other (Murray 2026o).

**Proposition 7 (dynamic closure; Murray 2026n).** Suppose waiting forms one autonomous semigroup $r_\Delta$ on states. Then the time $T_R$ to reach a threshold obeys
$$T_R\big(r_\Delta(a)\big)=T_R(a)-\Delta.$$
C2 covers the grouping of changes; this is its analogue for the passage of time. A failure of this identity shows that waiting is not one autonomous semigroup on this state: either the law changed over time (case 5 of Theorem 18) or the state is incomplete (Case I of Proposition 1). Status: [P].

**Theorem 10 (state–law descent).** A future law exists on a proposed present $x$ if and only if the conditional distribution of futures is the same, under every admissible intervention, for all histories that $x$ identifies. Status: [P]. This is the classical construction of causal and predictive states (Nerode 1958; Crutchfield and Young 1989; Shalizi and Crutchfield 2001; Littman, Sutton and Singh 2002). Murray (2026a, 2026h, 2026i, 2026m) applies it to biological state and to experimental action.

Two corollaries follow:

- **Matched presents refute statehood.** Two systems at the same present with different futures under the same intervention show that $x$ is not a state.
- **No reparameterisation can rescue a failed state.** A transform of $x$ cannot recover a distinction that $x$ has already erased.

**Statehood and composition are separate gates.** A sufficient predictive state does not by itself supply a binary composition on values. Two interventions can send the rest state to the same value yet act differently from another starting value. A composition law on values exists only if the **action gate** holds: *an intervention's endpoint from rest determines its action from every state*. The gate is tested by preparing two interventions with equal endpoints from rest and applying each from a second starting state (§13, step 2). Status: [P] (A.3).

Three objects must also be kept apart. Order dependence of action maps, reassociation defects of a reduced composition law, and curvature of an independently justified smooth structure are different things; composition of functions is always associative, and which of the three a measurement probes must be stated.

Associativity is the scalar, compositional case of state–law descent (A.3). A measured failure of grouping-independence does not by itself say what failed. It rejects at least one of the following:

- the context-free encoding of the changes;
- associativity of the underlying maps;
- the endpoint model;
- the predictive sufficiency of the scalar.

Pooling over latent types can also produce an apparent failure (Murray 2026p). Attributing the failure to hidden state requires a matched-present test (Theorem 10; §13, step 0). Status: [P].

## 5.2 Two or more dimensions: order can be stored as holonomy

In two or more dimensions, bounded composition may be associative or not. The author's classification decides which structures are possible.

**Proposition 8 (the bounded-composition dichotomy; Murray 2026f, Theorem 6.3).** Let $\oplus$ act on the open ball $B^n$, $n\ge2$, with the following properties:

- it is smooth, with an identity, left inverses and the left inverse property;
- it is $O(n)$-equivariant;
- on each line through 0 it restricts to $(s+t)/(1+st)$;
- its reassociation defects preserve Euclidean distances.

Then exactly one of two branches holds:

- **(F) Flat.** $\oplus$ is associative, every defect is the identity, and $u\oplus v=\Phi^{-1}(\Phi u+\Phi v)$ with $\Phi(u)=\operatorname{artanh}(|u|)\,\hat u$.
- **(H) Hyperbolic.** $\oplus$ is not associative. It is a rapidity-scaled Einstein gyro-addition of constant curvature $-\lambda^2$, and every defect is a Thomas–Wigner rotation.

No positively curved law exists: completeness together with Bonnet–Myers would force compactness, and the ball is not compact. The equivariance hypothesis is sharp:

- for $n\ge4$, $SO(n)$ suffices;
- for $n=3$, parity is needed, since otherwise there is a family of chiral laws;
- for $n=2$, the $SO(2)$ case is open.

Status: [P].

**Corollary (the selector; Murray 2026f).** Under these conditions, one failure of associativity anywhere forces hyperbolic geometry everywhere. Status: [P].

Holonomy is therefore not a consequence of boundedness. It is an empirical selector between the two branches. In branch (H), changes composed in either order agree up to a rotation, the gyration:
$$a\oplus b=\operatorname{gyr}[a,b]\,(b\oplus a).$$
Composing around a closed loop returns the system with a residual rotation. In the Poincaré disk, the angle of $\operatorname{gyr}[a,b]$ equals the area of the hyperbolic triangle with vertices $0$, $a$ and $a\oplus b$ (equivalently $0$, $-a$ and $b$), by the angle-defect (Gauss–Bonnet) formula. It is not in general the area of the triangle $0$, $a$, $b$; the two agree when $a\perp b$. For $a=0.5$, $b=0.5i$ both areas are $0.48996$ and the gyration is $-0.48996$ rad (clockwise for a counterclockwise loop); for $a=0.4+0.2i$, $b=0.7e^{2i}$ the gyration is $-0.60035$ rad, the area of $(0,a,a\oplus b)$ is $0.60035$ and that of $(0,a,b)$ is $0.61264$. Status: [P] (Ungar 2008).

So in branch (H), a bounded lawful system stores two things:

- its net state, which is the sum of its past;
- a rotation, which records the order of that past.

The record is compressed but not erased, and its size is the area the history swept out. Status: [D] for this reading. In branch (F), order is forgotten, as in one dimension.

Two measured systems are in branch (H):

- **Relativity:** Thomas precession.
- **Multilayer optics:** composing two lossless multilayers produces a Wigner rotation, equal to the anholonomy of the closed circuit in the unit disk (Barriuso et al. 2004; Murray 2026r). This is the $SU(1,1)$ analogue of, and distinct from, the Pancharatnam phase on the Poincaré sphere, which is holonomy on $S^2$ and belongs to the compact case of Theorem 27.

The general statement is that curvature is the obstruction to forgetting order. An ordered sequence of actions factors through its multiplicities if and only if the generating actions commute. Status: [P] (Murray 2026h, Theorem 5).

The flat simplex (A.12) has its own way of keeping order. With more than two types, order can be carried by a divergence-free probability current, and only time-reversal asymmetry can detect it (Murray 2026y).

# 6. Motion: inertia, invariance and interaction

## 6.1 The inertial law

**Theorem 11.** Under a constant drive $k$, $\psi(x(t))=\psi(x_0)+kt$. Status: [P].

The same motion looks different in each chart:

| Chart | Rapidity | Uniform motion looks like |
|---|---|---|
| Two horizons (logit) | $\log[e/(1-e)]$ | the logistic curve |
| One horizon, $\alpha=0$ (Bliss) | $-\log(1-e)$ | first-order saturation, $1-e^{-kt}$ |
| One horizon, $\alpha\to1$ (Loewe) | $e/(1-e)$ | the hyperbola $kt/(1+kt)$ |

So the logistic curve, first-order saturation and the Michaelis–Menten hyperbola are one inertial law seen through three charts. None of them requires a force.

**Corollary (feedback detector).** Under nominally constant drive, plot $\psi(x(t))$. A straight line means no feedback and a state-independent increment. A bend means one of three things:

- feedback;
- a changing drive;
- an increment that depends on the state.

Diploid selection with dominance is an example of the third. Its logit increment is $a_0+a_1x+\cdots$, with $a_0=\ln(1+hs)$, and the bend involves no feedback (Murray 2026x). Status: [D].

## 6.2 The invariance principle

**Theorem 12.** Composing with a fixed element $m$ is a translation by $\psi(m)$ in rapidity, whatever the starting point. Status: [P].

A mechanism that acts by composition therefore has one baseline-free effect size: the rapidity shift in its own chart.

- **Two-horizon mechanisms:** the log odds ratio.
- **Independent-hazard mechanisms:** $-\log[(1-e_1)/(1-e_0)]$.
- **Multiplicative mechanisms:** the log risk ratio.
- **Shared-site mechanisms:** the difference in odds.

The exact empirical test of Theorem 12 is kinematic closure (Murray 2026n, Theorem 1). A challenge acts by composition if and only if every challenge curve's derivative is a translate of one function $h'$.

Clinical epidemiology still debates which effect measure is portable across baseline risk. Engels et al. (2000), Deeks (2002) and Zhao et al. (2022), the last across 64,929 Cochrane meta-analyses, found the risk difference more often heterogeneous. Poole, Shrier and VanderWeele (2015) argue that this may partly reflect power. Wang (2022) shows that which measure looks homogeneous depends on the coordinates chosen. See also Doi et al. (2022) and Colnet et al. (2023).

UHL's answer is that mechanism picks the coordinate. No single measure is universally portable. But the flat risk difference should be the least portable of all, because it ignores the nonlinearity of every chart near the horizons.

**Hypothesis H2.** Across trials of one intervention at many baseline risks, the rapidity shift in the chart predicted by mechanism is constant, and the flat risk difference is not. Because the log odds ratio is non-collapsible, H2 must be tested on stratum-level effects. Test and first result: §13. Loss condition: on stratum-level data, the flat risk difference is as homogeneous across baselines as the mechanism-predicted rapidity shift.

## 6.3 Coupled rapidities: the interaction law

Take two bounded quantities with rapidities $\psi$ and $\varphi$ that drive each other. Assume:

- **A0 (state).** $(\psi,\varphi)$ is a state and its motion is autonomous and $C^1$: $\dot\psi=F(\psi,\varphi)$, $\dot\varphi=G(\psi,\varphi)$.
- **A1 (inertia).** With the coupling switched off, $F=k_1$ and $G=k_2$.
- **A2 (lawful coupling).** The law is unchanged when one fixed mechanism acts on both quantities: $\psi\to\psi+a$, $\varphi\to\varphi+ca$, with $c\neq0$.

**Theorem 13 (interaction law).**

- (a) If the law is unchanged under *separate* shifts of $\psi$ and $\varphi$, then $F$ and $G$ are constant. Full invariance forbids state-dependent interaction: coupling can at most shift the drives by constants.
- (b) Under A0 and A2, rescale $\varphi$ by $1/|c|$. Then $F=f(\Delta)$ and $G=g(\Delta)$, with $\Delta=\psi-\sigma\varphi$ and $\sigma=\operatorname{sign}c$. The relative rapidity obeys a closed one-dimensional law.
- (c) At a zero $\Delta^*$ of $\dot\Delta$ the pair is **locked**: both move uniformly in rapidity, with $\dot\varphi=\sigma\dot\psi$ (one common speed when $c>0$).

Status: [P]. Invariance gives $\partial_\psi F+c\,\partial_\varphi F=0$, whose solutions are functions of $c\psi-\varphi$. A1 is not used here; it fixes the drives in Theorem 14.

So lawful interaction acts through relative state, the observer equation of §11 written in rapidity. It requires a shared mechanism and therefore a shared rapidity unit. The same reduction to a relative coordinate is standard in phase-oscillator theory (Kuramoto 1984; Pikovsky, Rosenblum and Kurths 2001). What is new is its derivation from lawful composition and its transfer to bounded quantities.

**Theorem 14 (symmetry).** Take $c>0$, so $\Delta=\psi-\varphi$. Write $F=k_1+h_1(\Delta)$ and $G=k_2+h_2(\Delta)$, with $h_i$ independent of the drives. Add three assumptions:

- **A3 (exchange symmetry):** invariance under $(\psi,\varphi,k_1,k_2)\to(\varphi,\psi,k_2,k_1)$, that is, $h_2(\Delta)=h_1(-\Delta)$.
- **A4:** the coupling conserves $\psi+\varphi$: $h_1+h_2=0$.
- **A4′ (attraction):** the coupling reduces $|\Delta|$ near 0.

Then $\dot\Delta=\Phi-2\beta u(\Delta)$, where $\Phi=k_1-k_2$, $\beta\ge0$, and $u=-h_1/\beta$ is odd. $u$ is normalised by $u'(0)=1$ when $h_1'(0)\neq0$. Every odd $u$ is admissible, so invariance does not choose among linear, tanh, sin and sinh couplings.

Now relax A3–A4 to unequal strengths $\beta_1$ and $\beta_2$. Whenever a lock exists, meaning $\Phi/(\beta_1+\beta_2)$ lies in the range of $u$, the locked speed is $(\beta_2k_1+\beta_1k_2)/(\beta_1+\beta_2)$ for every $u$. Status: [P].

**Theorem 15 (what forces sinh).** Add two more assumptions:

- **A5:** the coupling is the net of two opposing fluxes in detailed balance, $r_+/r_-=e^{\Delta}$.
- **A6:** a rapidity shift multiplies each one-way rate by a factor that does not depend on the starting point.

Assume also that $r_+$ is continuous and positive, and that exchange symmetry acts on rates as $r_-(\Delta)=r_+(-\Delta)$. Then $r_\pm=r_0e^{\pm\Delta/2}$, and the net coupling is $2r_0\sinh(\Delta/2)$.

A5 fixes the rapidity unit: $\Delta$ is a free-energy difference in units of $k_BT$. Without the rate form of exchange symmetry, the exponent $a$ in $r_+=r_0e^{a\Delta}$ is free, and the net coupling is $2r_0e^{(a-1/2)\Delta}\sinh(\Delta/2)$. Status: [P] given these assumptions.

Without A6, detailed balance and the rate form of exchange symmetry force only $2q(\Delta)\sinh(\Delta/2)$, with $q$ even and positive. Glauber kinetics (a tanh coupling) and linear coupling are both members of that family. So a sinh coupling is the signature of exponential, Arrhenius-type exchange, not of invariance. This corrects Murray (2026u), where the sinh form was postulated by analogy.

**Theorem 16 (locking).** For $\dot\Delta=\Phi-2\beta u(\Delta)$, the function $V=2\beta\int_0^\Delta u-\Phi\Delta$ satisfies $\dot V=-\dot\Delta^2\le0$. Three cases follow:

- **Strictly increasing, unbounded $u$ (linear, sinh), $\beta>0$.** A unique, globally stable lock exists for every $\Phi$. Unboundedness alone is not enough: a non-monotone unbounded $u$ can have several locks. For $u=\sinh\Delta$ it sits at $\Delta^*=\operatorname{arsinh}(\Phi/2\beta)$. For the detailed-balance form of Theorem 15, $u=2\sinh(\Delta/2)$, it sits at $\Delta^*=2\operatorname{arsinh}(\Phi/4\beta)$.
- **Bounded $u$ (tanh).** A lock exists only if $|\Phi|<2\beta$. As $|\Phi|\to2\beta$ the locked gap $\Delta^*=\operatorname{artanh}(\Phi/2\beta)$ diverges and the relaxation rate $2\beta[1-(\Phi/2\beta)^2]$ falls to zero (critical slowing). The speeds do not jump: the locked speed $(k_1+k_2)/2$ equals both unlocked speeds at $|\Phi|=2\beta$, and beyond it the long-run drift of the gap rises linearly from zero, $\operatorname{sgn}\Phi\,(|\Phi|-2\beta)$, a kink in $\Phi$, against the square-root onset of the periodic case. Beyond that, $|\Delta|\to\infty$ and the pair unlocks, with asymptotic speeds $k_1-\beta\,\mathrm{sgn}\Phi$ and $k_2+\beta\,\mathrm{sgn}\Phi$. They head to opposite horizons only if these speeds have opposite signs.
- **Periodic $u$ (sin).** A stable lock exists if and only if $|\Phi|<2\beta$; at equality it is semi-stable. Beyond that, the phase slips with period $2\pi/\sqrt{\Phi^2-4\beta^2}$ (Adler 1946).

Status: [P]. As a reading [D], the unbounded, linear and periodic couplings mirror Theorem 4: sinh is hyperbolic, linear is parabolic, and sin is elliptic.

**Corollary (trajectory alphabet).** Take piecewise-constant parameters $k_1$, $k_2$ and $\beta$. Then $\psi(t)$ is $C^1$ except at parameter changes, where its slope jumps; between changes its slope varies smoothly as $\Delta$ evolves. Lock and unlock are consequences of parameter changes, not independent causes.

After each change, $\Delta$ does one of three things:

- it relaxes exponentially to a new lock, at rate $2\beta u'(\Delta^*)$;
- if there is no lock and $u$ is periodic, it slips;
- if there is no lock and $u$ is bounded, it splits.

So within each stretch $\psi(t)$ becomes asymptotically linear after a lock or a split. During a slip it is linear plus a periodic ripple of period $2\pi/\sqrt{\Phi^2-4\beta^2}$. The approach to a lock is a smooth transient of duration about $1/(2\beta u'(\Delta^*))$, not a sharp breakpoint. In raw coordinates each asymptotically linear stretch is one sigmoid (Theorem 11).

In the deterministic model, a trajectory is therefore a word in three letters: coast or lock, slip, and split. Its letters change only at parameter changes. Status: [D].

Two limits of scope apply:

- **Inertia is required.** The alphabet requires A1. Any restoring term bends $\psi(t)$ inside a stretch.
- **It is not a history.** A sigmoid is a response shape, not a history representation (Murray 2026p).

This commuting alphabet is distinct from what Murray (2026h) calls Temporal Grammar, which is the non-abelian branch of predictive closure.


# 7. Horizons: measured from inside, crossed only by a jump, and what lies beyond

## 7.1 Measuring the ceiling from inside

**Theorem 17.** In the two-horizon chart with ceiling $\ell$:
$$a\oplus b=\frac{a+b}{1+ab/\ell^2}=a+b-\frac{ab(a+b)}{\ell^2}+O(5),\qquad \ell^2=\frac{ab\,(a\oplus b)}{a+b-a\oplus b}.$$
Status: [P]; the right-hand identity is exact in this chart (A.8).

Small changes combined near rest reveal the ceiling through their shortfall from plain addition. In other charts the third-order coefficient fixes the ceiling only once the chart family is specified.

**Hypothesis H3 (ceiling consistency).** In a system obeying the Einstein chart, the ceiling inferred from small combinations equals the ceiling measured directly. Loss condition: the two estimates disagree beyond their errors.

## 7.2 Arriving at a boundary means a condition failed

**Theorem 18 (boundary arrival).** Suppose a real system reaches a horizon after finitely many changes, or in finite time under finite drive. Then at least one of the following holds:

1. **The quantity was not a closed state, or associativity failed** (Case I of Proposition 1): feedback, memory, an unobserved variable, or pooling over heterogeneous compartments.
2. **Strict monotonicity failed** (Case II): a switch, bistability, a reversal, or saturation at the boundary, as in zero-order depletion.
3. **Continuity failed** (Case II): a discrete jump, finite-number noise, or an irreversible absorbing event.
4. **The drive was unbounded.**
5. **The law itself changed over time:** fixed points annihilating (§3.3), or a failure of dynamic closure (Proposition 7).

Status: [P] that some condition fails or the rapidity sum diverges, the contrapositive of Theorems 1, 2 and 11 (A.9); [D] for identifying each failure with a mechanism.

Failure is broader than arrival. In bounded adaptive systems only one of four failure modes is an arrival at a boundary; the others are failures of sensing, of surveillance range, or of the controller (Murray 2026v). Theorem 18 speaks only about arrivals.

## 7.3 What decides arrival: the boundary exponent

Theorem 18 says a condition failed. The following says which measurable feature decides it.

**Proposition 9 (boundary exponent).** Let a bounded quantity approach its ceiling under $\dot e=X(e)$ with $X(e)\sim(1-e)^\gamma$ near $e=1$.

- (a) **Deterministic.** The ceiling is reached in finite time if and only if $\int^1 de/X(e)<\infty$, that is, if and only if $\gamma<1$ (Osgood 1898). Since the rapidity is $\psi=\int de/X$, the horizon theorem is Osgood's criterion read backwards: the ceiling is a horizon exactly when the rapidity integral diverges.
- (b) **Stochastic.** For $de=X(e)\,dt+\sigma(e)\,dW$ with $\sigma(e)\sim(1-e)^\beta$, when the drift vanishes at least linearly ($\gamma\ge1$), the boundary is attainable if and only if the noise vanishes slower than linearly, $\beta<1$, by Feller's classification (Feller 1952); when $\gamma<1$ the drift alone can reach it whatever $\beta$ is. Wright–Fisher sampling has $\beta=\tfrac12$, which is why finite populations fix.
- (c) **Maximum-entropy averages have $\gamma\ge1$** (Proposition 3), so they never arrive under finite drive.

Status: [P] for (a) and (b), classical; (c) is Proposition 3. The unification of the two criteria under one exponent is [D].

**Physical reading.** $\gamma\ge1$ means the rate of change vanishes at least linearly as the room runs out: the drive scales with what is left. That is mass action, first-order kinetics, and every self-limiting process; irreversible first-order kinetics is strict (it is the Bliss chart, $\gamma=1$). $\gamma<1$ means the drive stays finite at the boundary: a saturated pump or enzyme (zero-order kinetics, $\gamma=0$), a hard cap imposed from outside, or a discrete count. In nature, smooth averages have horizons; countable events cross boundaries.

Every projective chart in this paper has $\gamma=1$ at its ceiling (logit, Bliss, the Hamacher dial for $\alpha<1$); the Loewe limit has $\gamma=2$; zero-order depletion has $\gamma=0$ (Appendix B).

![Left: time to reach the ceiling under $\dot e=(1-e)^\gamma$, finite for $\gamma<1$ and infinite for $\gamma\ge1$ (Osgood). Right: the maximum-entropy generator against distance to the ceiling, on log axes: slope 1 for two states (an atom at the end), slope 2 for a continuum (Proposition 3).](fig3_exponent.png){width=100%}

## 7.4 The far side of the horizon

The horizon is not the end of the space. On the projective line the lawful interval $(-1,1)$ and the outside $|x|>1$, whose two half-lines join through $\infty$, meet at the two horizon points (Fig. 2, right).

**Theorem 19 (the same law on the far side).**

1. **The law acts on both sides.** Einstein composition with any inside change maps outside states to outside states: $0.5\oplus2=1.25$, $-0.9\oplus3=-1.235$. The horizon separates two orbits of one group; composition with an inside change never carries a state across it.
2. **Crossing is inversion plus a quarter turn in rapidity.** For $|x|>1$, $\operatorname{artanh}x=\operatorname{artanh}(1/x)+i\pi/2$. An outside state is the reciprocal of an inside state with rapidity shifted by $i\pi/2$, and the real part of rapidity keeps adding: $\operatorname{artanh}(0.5)+\operatorname{artanh}(2)=\operatorname{artanh}(1.25)=1.0986+i\pi/2$.
3. **In $n$ dimensions the two sides differ in kind.** The inside of the absolute quadric is hyperbolic space $\mathbb H^n$; the outside is de Sitter space $dS^n$ (its antipodal quotient), Lorentzian, with the same projective automorphism group $PO(1,n)$. In spacetime language, crossing the light cone exchanges timelike and spacelike.

Status: [P], classical: the Cayley–Klein absolute; analytic continuation of rapidity; the meta-relativity of Bilaniuk, Deshpande and Sudarshan (1962). Verified numerically (Appendix B).

**A physical instance: simultaneity.** In $1+1$ dimensions with $c=1$, an observer moving at velocity $v$ has its time axis at slope $dx/dt=v$ and its line of simultaneity at slope $1/v$. A boost $u$ sends $v$ to $v\oplus u$ and sends the simultaneity slope $1/v$ to $(1/v)\oplus u=1/(v\oplus u)$, by the same Einstein law (checked: $v=0.3$, $u=0.5$ gives $1.4375$ both ways). So the inside of the horizon holds observers' velocities, the far side holds the slopes of their simultaneity lines, the reciprocal pairs each observer with its own simultaneity, and one law moves both. Status: [P], classical (the Minkowski diagram).

**Corollary (what a crossing must be).** Since the interior group preserves each side, a real system that crosses a horizon does so by a map outside the group, which requires one of the failures listed in Theorem 18. Status: [D].

**Open question (formerly H6).** Do nature's discrete boundary events, such as fixation, extinction and commitment, have a far-side reading? Theorem 19 does not supply one. For quantities whose physical range is exactly the interval, such as frequencies and probabilities, the far side contains no physical states. And the reciprocal continuation maps a point just past a horizon back near the *same* horizon ($1/1.01=0.99$), not to the opposite one, so a new variable starting near zero after fixation does not test it. Version 2.0's test for H6 is withdrawn. A test would need a measurable map across the event that an ordinary reset-and-restart model does not predict; none is proposed here, so this is recorded as an open question, not a hypothesis.

## 7.5 Stochastic composition

Noise is lawful when it enters in rapidity: $d\psi=k\,dt+\sigma\,dW$.

**Theorem 20 (charts).** By Itô's lemma, in the logit chart $dp=p(1-p)[k+\tfrac12\sigma^2(1-2p)]dt+\sigma p(1-p)\,dW$, and in the artanh chart $ds=(1-s^2)(k-\sigma^2s)\,dt+\sigma(1-s^2)\,dW$. Status: [P]. The extra Itô drift pulls raw averages toward the neutral state. It is not a force; in rapidity it does not exist.

**Theorem 21 (transient law).** $\psi(t)\sim N(\psi_0+kt,\sigma^2t)$, so $p(t)$ is logit-normal. Each quantile of $p$ is the logistic of the matching quantile of $\psi$; the median follows the deterministic logistic exactly, the mean does not. Sigmoids should be fitted to medians. Status: [P] (A.10).

**Stationary density.** For $d\Delta=(\Phi-2\beta u(\Delta))\,dt+\sigma\,dW$ (Theorem 16 with noise in the relative rapidity), the stationary density is $\propto\exp[-(2/\sigma^2)(2\beta\int_0^\Delta u-\Phi\Delta)]$ whenever normalisable: always for linear and sinh $u$ with $\beta>0$; for tanh only when $|\Phi|<2\beta$; for sin on the circle only at $\Phi=0$, a probability current otherwise. At $\Phi=0$: linear $u$ gives Ornstein–Uhlenbeck, sinh a $\cosh$-exponential law, sin von Mises with concentration $4\beta/\sigma^2$. Status: [P].

**Theorem 22 (no horizon in finite time).** If the rapidity drift and noise are locally Lipschitz with linear growth, solutions exist for all $t$ and stay finite almost surely (Øksendal 2003, Thm 5.2.1). Brownian motion with drift in $\psi$ never reaches a horizon. Status: [P].

**Theorem 23 (fixation is a discreteness event).**

- (a) In the logit chart the Wright–Fisher drift is $s+(2p-1)/(2Np(1-p))$, and with the noise it grows without bound near the ends, so Theorem 22 does not apply. For every $s$ the ends are exit boundaries reached in finite time (Feller 1952): the noise exponent is $\beta=\tfrac12$ (Proposition 9b). That unbounded noise is the continuum trace of sampling a finite population.
- (b) In a discrete population of $N$ gene copies, every unfixed state has rapidity at most $\ln(N-1)$. Fixation is a one-generation jump from a finite rapidity to $+\infty$; from $\ln(N-1)$ its neutral probability is $(1-1/N)^N\approx e^{-1}$ per generation. This is case 3 of Theorem 18.

Status: [P] for (a) and the classical quantities; [D] for the reading. For $N$ gene copies, in generations (for $N$ diploids replace $N$ by $2N$): fixation probability $u(p)=(1-e^{-2Nsp})/(1-e^{-2Ns})$ (Kimura 1962); neutral mean absorption time $-2N[p\ln p+(1-p)\ln(1-p)]$ (Kimura and Ohta 1969); neutral conditional fixation time $-2N(1-p)\ln(1-p)/p$; conditional fixation time $\approx(2/s)[\ln(2Ns)+\gamma_E]$ for a beneficial allele from one copy, $Ns\gg1$. Simulation matched the neutral quantities (Appendix B). With two-way mutation at $2N\mu\ge1$ ($4N\mu\ge1$ for $N$ diploids) the boundaries become entrance boundaries and are no longer reached (Appendix B).

# 8. Higher dimensions: the cone of the observer's channels

In two or more dimensions geometric curvature becomes meaningful. There are two routes by which bounded composition forces hyperbolic geometry: rigidity (a round bound with projective extension, Theorem 24 and item 1 of Theorem 25) and selection (isometric reassociation defects with one measured failure of associativity, Proposition 8). Without one of them nothing is forced: bounded, associative, flat composition remains possible, and so does the simplex.

## 8.1 Rigidity, and what the cone decides

Let the quantity live in a bounded region of $\mathbb{R}^n$, $n\ge2$. Let composition satisfy C1 and C4, be gyro-associative with non-trivial gyration, commute with rotations, and preserve the boundary. Let each left translation extend to a projective or conformal map of the closed ball; this is the **rigidity condition**.

**Theorem 24.** Under these conditions the space is hyperbolic space $\mathbb{H}^n$ of constant curvature $-1/\ell^2$; the projective automorphisms of the ball form $PO(1,n)\cong O^+(1,n)$, and $\mathbb{H}^n=SO^+(1,n)/SO(n)$. Status: [P] given rigidity (Ungar 2008; Friedman 2005; Murray 2026e, Theorem A, for $n\le3$).

**Proposition 10 (the dial is one-dimensional; Murray 2026e, Prop. 5.1).** For $n\ge2$, continuous rotational covariance forces the neutral state into the interior, so the one-horizon dial exists only in one dimension. Status: [P]; the proof holds for every $n\ge2$.

**Theorem 25 (the cone of the observer's channels).** Suppose the world is a linear system on $n+1$ channels whose states form a convex cone $C$, $z'=Mz$, observed scale-blind as ratios, so that the observed states fill the projectivisation of $C$. Distinguish two classes of update. A **reversible** update maps $C$ *onto* itself (a cone automorphism). A **forward-only** update maps $C$ *into* itself but not onto it. Then:

1. **Lorentz cone** $z_0^2>|z|^2$ (the channels carry an $O(n)$ symmetry that leaves the bounding form invariant), reversible updates. $M\in\mathbb{R}^+\cdot O(1,n)$, the observed states fill the round ball, the Hilbert geometry is $\mathbb{H}^n$ in the Beltrami–Klein model, and composition of observed boosts is Einstein gyro-addition. Updates do not commute.
2. **Positive orthant** (the channels are labelled alternatives constrained only by positivity), reversible updates. The automorphisms are positive diagonal maps times permutations of the labels. The connected component of the identity, the positive diagonal maps, commute, compose by vector addition in log-ratio coordinates, and leave invariant a Hilbert geometry that is a normed, flat space; the boundary is still unreachable. Permutations do not commute with them.
3. **Positive-definite matrices** (the channels form a matrix algebra, as for quantum states of dimension $\ge3$ or covariance matrices of three or more variables), reversible updates. Updates do not commute; the invariant Riemannian metric of the symmetric space (Faraut and Korányi 1994) has nonpositive, non-constant sectional curvature, and the Hilbert metric is neither hyperbolic nor normed.
4. **Any cone, forward-only updates.** A linear map that sends $C$ into itself does not increase the Hilbert projective distance, and if the image has finite projective diameter $\Delta$ it contracts every distance by at least the factor $\tanh(\Delta/4)$ (Birkhoff 1957; Bushell 1973). Such maps reduce distinguishability, need not commute even on the orthant (for example $\bigl(\begin{smallmatrix}2&1\\1&2\end{smallmatrix}\bigr)$ and $\bigl(\begin{smallmatrix}3&1\\1&1\end{smallmatrix}\bigr)$), and, when the image has finite diameter, preserve no continuous metric, since every orbit converges to one ray.

Lorentz cones and the positive-definite cones (real, complex, quaternionic, and one exceptional 27-dimensional cone) exhaust the irreducible symmetric cones (Koecher–Vinberg; Faraut and Korányi 1994); the orthant is the reducible case, a product of half-lines. A Hilbert geometry is hyperbolic only for an ellipsoid (Kay 1967) and isometric to a normed space only for a simplex (de la Harpe 1993; Foertsch and Karlsson 2005). The qubit's Bloch ball is round because $2\times2$ Hermitian matrices form a Lorentz cone (Chen and Ungar 2002).

**The cone does not fix the physical distance.** An invariant geometry exists only relative to an admissible group, and the distance an observer measures depends on how it compares states. The qubit ball carries the Hilbert metric, hyperbolic and invariant under every cone automorphism (including filtering operations), and also the Bures metric, which is invariant only under unitary (and antiunitary) conjugations, has finite diameter (a pure state lies at Bures geodesic distance, the Bures angle $\arccos\sqrt F$, of $\pi/4$ from the centre) and positive curvature (Hübner 1992; Bengtsson and Życzkowski 2006). Before deriving a curvature, state the admissible updates and the comparison.

Status: [P], classical mathematics (A.11 for item 1, A.12 for item 2, Faraut and Korányi 1994 for item 3, Birkhoff 1957 for item 4). What is new is the reading: given its admissible reversible updates, the invariant geometry available to a ratio-reading observer is decided by the algebra of its channels, and whether an intervention preserves, contracts or erases distinguishability is a measurable property that sorts interventions before any chart is fitted. Multi-hypothesis Bayesian updating is item 2 (its reversible part) and is flat; velocity and qubit filtering are item 1. Item 3 predicts order-memory without constant curvature for qutrits and for covariance updating [H]. Test: measure reassociation defects and estimate sectional curvature in a qutrit or covariance-tracking system (§13, step 8). Loss condition: defects vanish, or the fitted curvature is constant.

**Proposition 8 revisited.** The two-branch theorem of §5.2 is the selection route: under isometric reassociation defects, one failure of associativity anywhere forces branch (H) everywhere, and no positively curved law exists on the ball. Rigidity and selection are independent hypotheses that reach the same space.

## 8.2 A gauge connection is forced in branch (H)

**Theorem 26 (holonomy).** In branch (H) the holonomy of bounded composition around a small loop equals curvature times enclosed area. For $n=2$ it lies in $SO(2)$; for $n\ge3$ in $SO(n)$, which is non-abelian. Two gyrations from Einstein addition in three dimensions, $\operatorname{gyr}[u,v]$ and $\operatorname{gyr}[v,w]$ with $u=0.6e_1$, $v=0.6e_2$, $w=0.6e_3$, are proper rotations with commutator of Frobenius norm 0.069. Status: [P]; this is the Levi-Civita connection of $\mathbb{H}^n$, the Thomas–Wigner rotation read as anholonomy (Aravind 1997).

**Theorem 27 (compact isotropy and duality).** In $\mathfrak{so}(1,n)=\mathfrak{so}(n)\oplus\mathfrak{p}$ the bracket of two boosts is a rotation: with real generators $(J_k)_{ij}=-\epsilon_{kij}$ and $K_i=E_{0i}+E_{i0}$, $[K_1,K_2]=-J_3$. Replacing $\mathfrak p$ by $i\mathfrak p$ gives $\mathfrak{so}(n+1)$ and $S^n$, and the sign flips. $\mathbb{H}^n$ carries horizons, $\mathbb{R}^n$ is flat, $S^n$ is compact; all three share isotropy $SO(n)$ (Helgason 1978). What boundedness adds over flat composition is non-trivial holonomy; the sign of the curvature separates horizons from wrapping. Status: [P].

## 8.3 A curvature threshold in the spectrum, and what does not follow

**Theorem 28 (McKean 1970).** On $\mathbb{H}^n$ with curvature $-1/\ell^2$, $\operatorname{spec}(-\Delta)\subset[(n-1)^2/4\ell^2,\infty)$. A minimally coupled scalar wave has frequency threshold $\omega\ge(n-1)/2\ell$. This is not a mass, it depends on the field, and it vanishes for conformally coupled scalars and for Maxwell fields on $\mathbb{H}^3$ (Donnelly 1981). A compact positively curved space has a gap (Lichnerowicz 1958), and so does a flat torus, so that gap comes from compactness. Status: [P].

**What does not follow.** Boundedness does not force a mass gap. This paper does not construct quantum Yang–Mills, prove a mass gap, or derive a gauge group. The one classical fact it touches is that positive energy requires the gauge algebra to be compact (Weinberg 1996, section 15.2), which places gauge symmetry on the gyrating, compact side of Theorem 27. Nothing further is claimed.

## 8.4 The room inside: hyperbolic information space

What being hyperbolic changes about an object is the amount of room inside it. In $\mathbb H^2$ a circle of radius $r$ has circumference $2\pi\sinh r$ against $2\pi r$ in the plane: 7.4 against 6.3 at $r=1$, 466 against 31 at $r=5$, $6.9\times10^4$ against 63 at $r=10$. In the Poincaré disk this whole space fits inside a finite outline, and almost all of its room lies near the edge. From outside the object is small and bounded; from inside it holds an exponentially large space of distinctions, and its edge is a horizon. This needs two or more dimensions: in one dimension the rapidity makes an interval infinitely long but not exponentially wide.

**Why branching lives there.** A tree with branching factor $b\ge2$ has $b^r$ nodes at depth $r$. In Euclidean space of fixed dimension $d$, an embedding with distortion at most $D$ places these nodes at pairwise distance at least 1 inside a ball of radius about $Dr$, which holds at most $(CDr)^d$ such points; for large $r$ this is fewer than $b^r$, so no such embedding exists. In $\mathbb H^2$ every finite tree embeds with distortion arbitrarily close to 1 (Sarkar 2012). Without the dimension bound, Euclidean space still needs distortion growing like $\sqrt{\log r}$ for the complete binary tree of depth $r$ (Bourgain 1986). The statement needs its assumptions: at fixed dimension and bounded distortion, branching history fits in hyperbolic space and not in flat space. Status: [P] (A.20).

**Where it has been measured.** Heterogeneous degree distributions and strong clustering in complex networks follow from a hidden hyperbolic geometry, because node taxonomies are approximately trees (Krioukov et al. 2010). Natural odour mixtures occupy a low-dimensional hyperbolic space (Zhou, Smith and Sharpee 2018). Rat hippocampal CA1 represents space in a three-dimensional hyperbolic geometry whose size grows logarithmically with exploration time, matching the maximal possible gain in information (Zhang, Rich, Lee and Sharpee 2023). Developmental hierarchies in single-cell data are better represented on Poincaré maps than in flat embeddings (Klimovskaia et al. 2020). Status: [P], measured or inferred by others.

**Hypothesis H7 (branching histories under finite resources).** An observer that stores a branching history in a representation of fixed low dimension, with bounded distortion of the history's tree distances, represents it in a negatively curved space whose edge is a horizon, and the space grows with the logarithm of the history's size. Test: Gromov $\delta$-hyperbolicity and best-fit curvature of perturbation-response spaces in single-cell data and of neural state spaces, compared against the flat and spherical alternatives, with the prediction that $\delta$ is small relative to the diameter and the fitted curvature is negative. Loss condition: flat or spherical fits are as good or better. Status: [H].

Two routes reach the same geometry. The composition route of this paper arrives at $\mathbb H^n$ through bounded, lawful combining under a round bound. The branching route arrives there through exponentially many histories stored in finite room. Whether they are two views of one fact is open; H7 tests only the branching route.

![Left: room grows exponentially with radius in hyperbolic space. Centre: a binary tree of depth 5 with equal hyperbolic edge lengths fits in the Poincaré disk without crowding. Right: the gyration $\operatorname{gyr}[a,b]$ equals the area of the hyperbolic triangle $(0,a,a\oplus b)$, here of magnitude 0.600 rad for $a=0.4+0.2i$, $b=0.7e^{2i}$.](fig4_room.png){width=100%}


# Part II — The Charts

Each chart names a bounded quantity, its horizons and its local form, then reads Part I in that setting. Charts are instances, not evidence for universality; each carries its own status.

# 9. Physics

## 9.1 Relativity: velocity

- **Quantity:** velocity, with horizons at $\pm c$.
- **Chart:** two-horizon (Theorem 7). Composition is Einstein's law, and rapidity is $c\operatorname{artanh}(v/c)$.
- **Correspondence:** Newtonian addition is the limit $c\to\infty$ (§3).
- **Memory:** in three dimensions the gyration is Thomas precession, which contributes the factor of ½ in atomic spin–orbit coupling (Thomas 1926). This is a measured instance of Theorem 26, and it places velocity in branch (H) of Proposition 8.

Status: [P]. This is the chart in which the law was first seen, long before it was recognised as a law about limits.

## 9.2 Reflection: waves at an interface

- **Quantity:** the reflection coefficient $\Gamma$, with $|\Gamma|<1$. The horizon is total reflection.
- **Chart:** two-dimensional. Cascaded reflections compose by Möbius addition, $(\Gamma_1+\Gamma_2)/(1+\bar\Gamma_1\Gamma_2)$, on the Poincaré disk.

The standing-wave ratio is $e^{2\eta}$, where $\eta=\operatorname{artanh}|\Gamma|$.

A quarter-wave mirror is inertial motion in rapidity (Theorem 11). Each high/low index pair adds $\ln(n_H/n_L)$, so with matched outer media
$$R_N=\tanh^2\big(N\ln(n_H/n_L)\big).$$
At $N=30$ and $n_H/n_L=1.5$ the shortfall is $1-R\approx1.1\times10^{-10}$. A mirror approaches perfect reflection without reaching it. The gyration of this Möbius addition is the Wigner angle of a compound multilayer, and it equals the anholonomy of the closed circuit in the disk (Barriuso et al. 2004). It is a second measured holonomy of branch (H), and it is distinct from the Pancharatnam phase, which is holonomy on the Poincaré sphere.

Status: [P], classical: Einstein and Möbius addition of reflection coefficients (Vigoureux 1992; Giust, Vigoureux and Lages 2009), and the trichotomy of lossless multilayers (Monzón et al. 2002).

# 10. Life

## 10.1 Evolution: selection is inertia in rapidity

- **Quantity:** the frequency $p$ of a variant. Its horizons are loss (0) and fixation (1).
- **Chart:** two-horizon, for two types.

Under constant selection $s$ in the genic (haploid) case, the replicator equation $\dot p=sp(1-p)$ is inertial motion in the logit:
$$\log\frac{p(t)}{1-p(t)}=\log\frac{p_0}{1-p_0}+st.$$
Status: [P] (Haldane 1924).

Two cases fall outside this simple form:

- **Diploid selection with dominance.** The logit increment depends on the state, $g(x)=a_0+a_1x+\cdots$ with $a_0=\ln(1+hs)$, so $\psi(t)$ bends without any feedback. Near the rare-allele boundary only $hs$ is identifiable, so tests must sample the bend at mid-frequencies (Murray 2026x).
- **More than two types.** Composition lives on the flat log-ratio simplex (A.12), not in the two-horizon chart. Order can then hide in a divergence-free probability current (Murray 2026y).

Three consequences follow:

- **The present encodes history.** A population's current log-odds is its integrated history of selection (Theorem 9).
- **Fixation needs a broken condition.** Deterministic selection never fixes a variant. Fixation happens through the discreteness of a finite population (Theorem 23).
- **Organism and environment bound each other.** Treat trait and environment as coupled rapidities (Theorem 13).

**Hypothesis H4.** In a locked phase, the rapidity gap between trait and environment is constant. The joint speed is $(\beta_2k_1+\beta_1k_2)/(\beta_1+\beta_2)$, with $\beta_1$ the strength of adaptation and $\beta_2$ that of niche construction. H4 is falsified if the gap drifts while both drives stay constant. A lock is one special case of a forward-invariant viable regime (Murray 2026o); H4 does not claim that every persistent organism is locked.

## 10.2 Pharmacology, dose and homeostasis

- **Quantity:** fractional effect $e\in[0,1]$.
- **Chart:** the one-horizon dial of Theorem 8, with its position set by mechanism (§4.5).

For two equipotent Hill-slope-1 agents, each producing effect $e$ alone, the gap between Bliss and Loewe is $g(e)=e^2(1-e)/(1+e)$. It peaks at $e^*=(\sqrt5-1)/2\approx0.618$, with $g\approx0.090$ (Murray 2026e). Status: [P].

For other Hill slopes the shape changes, and Loewe additivity leaves the projective dial (§4.3). For slope ½ the peak moves to 0.52. For slope 2 the gap changes sign at $e=2/3$.

A small public illustration exists. On four SynergyFinder matrices, a Bliss-chart model had the lowest held-out error among the coordinates compared (Murray 2026g). No triple combinations were available, so associativity was not tested.

**Hormesis.** The published model (Murray 2026c) treats repair and damage as independent, additive rapidity increments, with no coupling. It makes zero-fit predictions:

- a peak of 127–175% of control;
- a hormetic zone 8–80-fold wide;
- peak dose about twice the repair activation EC50.

These are to be compared with the Calabrese database without fitting. Two companion predictions are independent tests:

- **P6.** Adaptive amplitude scales with $1-x_0^2$, the Einstein-chart generator of Theorem 3, with no free parameters (Murray 2026w).
- **P11.** Hormesis depends on timescale: acute exposures give larger peaks than chronic ones (Murray 2026v).

Coupling repair to damage through Theorem 16 is an extension of that paper, not one of its results. It predicts a threshold dose, $|\Phi|=2\beta$, beyond which saturable repair loses its lock. The model gives no jump there; its signatures are a locked gap that grows as $\operatorname{artanh}(\Phi/2\beta)$, a recovery rate that falls as $2\beta[1-(\Phi/2\beta)^2]$, and beyond the threshold a drift of the gap that grows linearly from zero as $|\Phi|-2\beta$ (Theorem 16). Test: recovery-rate measurements across doses approaching the threshold. Loss condition: the recovery rate does not fall toward zero near the dose at which adaptation is lost. [H]

**Collapse.** In the calibrated glutathione model (Murray 2026j), collapse of the pool is a boundary-equilibrium bifurcation that requires a push across a saddle. It is the one failure mode that is an arrival (case 2 of Theorem 18). The reductive fade is a failure without arrival (§7.2). The model's forecast for NAC in NRF2-active lung cancer is of that second kind. Abundance is not recoverability: a pool can be depleted without loss of viability (Murray 2026l).

**Rescue windows.** The finite time to commitment in supply-limited redox failure is the elliptic passage of §3.3 (Murray 2026l). Test and loss condition: the depth-by-duration design of Murray (2026l); loss if the depth–duration exponent leaves $(\tfrac12,1)$. Status: [H].

## 10.3 Two proposed charts

The following two charts are proposed here. They are not claims of the source papers. Each is tagged [H], with a test.

- **Exoplanet atmospheres.**
  - *The source paper's coordinate:* Murray (2026aa) uses a log slack $\Lambda_i=-\ln\Pi_i$ combined by a minimum over loss channels. A minimum is idempotent, which is Case II of Proposition 1, so that coordinate is not a UHL chart.
  - *Proposed chart:* the retained envelope fraction $f\in(0,1]$. It is a monoid in the multiplicative chart $\psi=-\ln f$, with complete stripping as its horizon.
  - *Prediction:* stripping in finite time requires zero-order, energy-limited loss (case 2) or radius-inflation feedback (case 1). Loss condition: stripped planets are found whose loss is first-order in the retained fraction with no feedback.
- **Rotary ATP synthase.**
  - *Proposed chart:* the forward-step fraction $r_+/(r_++r_-)$ is logistic in the per-cycle affinity $A/RT$, which is a two-horizon chart by detailed balance (A5).
  - *Prediction:* under A5–A6 with exchange-symmetric rates the net flux is proportional to $\sinh(A/2RT)$ (Theorem 15). Loss condition: net flux against affinity is fitted better by a bounded (tanh) or linear coupling than by $\sinh(A/2RT)$. The boundary-binding regime of Murray (2026ab), $q_{\mathrm{eff}}\approx D_{\mathrm{env}}$, is the neutral state $A\to0$ of this chart (forward-step fraction ½, zero net flux), not a horizon. The horizons $A/RT\to\pm\infty$ are fully irreversible stepping. Maximal efficiency $\eta\to1$ is therefore reached only as the net flux vanishes.

# 11. Mind: belief, the observer's law and observer centrality

## 11.1 Belief: certainty is a horizon

- **Quantity:** belief in a proposition, $P\in(0,1)$, or $s=2P-1$.
- **Chart:** two-horizon.

Bayes' rule adds log-likelihood ratios to log-odds (Good 1950). In $s$ this is exactly Einstein composition:
$$s'=\frac{s+\lambda}{1+s\lambda},\qquad \lambda=\tanh\big(\tfrac12\log\mathrm{LR}\big).$$
Status: [P], classical. It is the ordered group of certainty degrees in expert systems (Hájek 1985; Heckerman 1986), and it also appears as the rule for optimal forecast betting (Piotrowski and Łuczka 2007).

Finite evidence never produces certainty. Conversely, a prior of exactly 0 or 1 can never be revised; this is Cromwell's rule (Lindley 1985).

Human perception of bounded quantities follows the same chart. Across frequency estimation, confidence, risk and signal detection, perceived probability is linear in log-odds (Zhang and Maloney 2012):
$$\operatorname{logit}\pi=\gamma\operatorname{logit}p+(1-\gamma)\operatorname{logit}p_0.$$
Two features stand out:

- The slope $\gamma$ is typically below 1.
- The crossover $p_0$ is often near $1/m$ for $m$ categories. That is the maximum-entropy point, which Theorem 3 identifies as the neutral state.

Colour science already knows that a perceptual bound can give Lorentz structure. Yilmaz (1962) derived Lorentz transformations for changes of illuminant from bounded saturation, and Resnikoff (1974) derived a hyperbolic colour space (reviewed by Prencipe, Garcin and Provenzi 2020).

**Hypothesis H5.** The slope $\gamma$ is the perceiver's own rapidity scale. It should be stable within a person across tasks and shift with state, for example arousal or fatigue. Test: fit $\gamma$ per person across two or more of Zhang and Maloney's task types. Loss condition: within-person variation in $\gamma$ across tasks is as large as between-person variation.

**Coupled belief.** Two interacting perceivers are coupled rapidities (Theorems 13–16). Murray (2026u) proposes a dual-EEG test of relative-rapidity locking. Theorem 15 shows that the sinh form proposed there needs A5–A6 and exchange-symmetric rates, and then has argument $\Delta/2$; a test should fit the coupling function rather than assume it.

## 11.2 The observer's law

Theorem 6 and its higher-dimensional form, Theorem 25, are the observer's law. An observer that reads a linear world through ratios must see fractional-linear dynamics. With a round bound and reversible updates, it must see Lorentz transformations up to scale; forward-only updates contract instead (Theorem 25, item 4). The converse of Theorem 6 makes this testable: cross-ratio preservation on observed transitions is the fingerprint of a scale-blind linear world (Murray 2026a).

In a homogeneous space, the symmetry that carries an observer at state $o$ to the centre gives the form in which it sees any other state $x$:
$$x_{\text{seen}}=(\ominus o)\oplus x.$$
In one dimension this is $(x-o)/(1-ox/\ell^2)$, the relativistic relative velocity. In two dimensions it is $(x-o)/(1-\bar ox)$, the Möbius map of the disk.

So an observer does not see reality's raw state. It sees reality composed with the inverse of its own position.

**Theorem 29 (observer centrality).** For every observer whose composition law is a group (Theorem 1), or a gyrogroup in two or more dimensions whose gyrations preserve $|\psi|$ (as in Proposition 8 and Theorem 24):

1. It is at the centre of its own space.
2. Different observers see different raw values of the same state.
3. All observers agree on rapidity distances, $d(x,y)=|\psi((\ominus x)\oplus y)|$.
4. It can measure its horizons (Theorem 17) but never reach them (Theorem 1).
5. In branch (H), in two or more dimensions, carrying a viewpoint around a loop of observers returns it rotated by an angle equal to the enclosed area divided by $\ell^2$ (Theorem 26).

The one-horizon monoids of Theorem 2 have no inverses, so an observer there cannot be recentred and items 1–3 do not apply; only the horizon statement survives.

Status: [P]. Items 1–3 hold in any homogeneous space, flat ones included. What boundedness adds is item 4: horizons that can be measured but not reached. What non-associativity adds is item 5: perspective with holonomy.

Murray (2026m) gives a second, predictive sense of observer centrality. There is a minimal exact state for each jurisdiction of admissible tests, and a finer jurisdiction refines it. An interior observer is therefore limited both by its horizons and by the tests it can run.

# 12. Seeing the law from inside: a register of puzzles

An interior observer reads invariant facts through its own chart. Many familiar puzzles are exactly that: an invariant read from inside, then judged with flat intuition. Others are not, and saying which is part of the law.

Each puzzle below gets one verdict:

- **R (resolved):** a horizon or chart effect. In every such case the classical resolution already exists, and UHL re-reads it as one structure.
- **L (located):** UHL turns the debate into a definite question with a test, but does not settle it.
- **O (outside):** a named condition of the law fails, so the law does not apply.

| Puzzle | Verdict | The law from inside, the question it poses, or the condition that fails |
|---|---|---|
| Velocity addition; cannot catch light | R | Rapidities add, and $c$ is at infinite rapidity |
| Twin paradox | R | The traveller's rapidity path goes from $+\psi$ to $-\psi$, while the stay-at-home twin's does not move; proper time $=\int dt/\cosh\psi$ |
| Bell's spaceship | R | Equal lab rapidities give proper separation $L\cosh\psi$, so the string breaks |
| Ehrenfest (rotating disk) | R, partial | Co-rotating circumference $2\pi r\cosh\psi(r)$ diverges at the light cylinder, a horizon. Born rigidity is outside |
| Thomas–Wigner rotation (Mocanu 1986) | R | The mismatch in non-collinear composition is the gyration (Ungar 1989) |
| Invisible length contraction (Terrell–Penrose) | R | In a photograph, Lorentz maps act on the sky as Möbius maps, so circles stay circles (Terrell 1959; Penrose 1959) |
| Railway horizon (perspective) | R | Stepping forward maps image height $y\mapsto y/(1-cy)$: parabolic Möbius, with the horizon as its only fixed point |
| Third law: absolute zero unattainable | R, reading | Inverse temperature is the natural parameter, so the ground state is at infinite rapidity. The proof itself rests on finite resources (Masanes and Oppenheim 2017) |
| Cromwell's rule | R | Certainty is a horizon of belief |
| Odds-ratio non-collapsibility | R | Pooling averages in $p$, not in $\psi$ (Greenland, Robins and Pearl 1999). With an odds ratio of 3 in two equal strata at baselines 0.2 and 0.8, the pooled ratio is 2.08 |
| Levinthal's paradox | R, classifies | Unbiased search reaches the low-entropy corner only on astronomical timescales; a drift, i.e. a broken condition, is needed for biological times (Zwanzig, Szabo and Bagchi 1992) |
| Zeno's dichotomy | O | For a runner at constant speed the flat chart is physical and the runner arrives; the halvings add $\ln2$ each only in a one-horizon chart that the physics does not select |
| Diminishing returns; ceiling effects | R | The correspondence error of §3.2 |
| Measurement problem | L | A definite outcome is a jump to the pure-state boundary of the state space (round only for a qubit, Theorem 25), which lawful composition cannot make (Theorems 1–2, 19); which condition of Theorem 18 fails, and whether the jump is physical, is the open question. Test: collapse-noise searches |
| Flatness problem (cosmology) | O | No bounded quantity is being composed; Theorem 27 names the three spatial geometries and predicts nothing about which nature chose |
| Fermi paradox | L | The Drake fractions are bounded and compose in log; is $f_\ell$ near its lower horizon? Test: biosignature statistics |
| Weber–Fechner vs Stevens | L | Unbounded magnitudes do not select log over power. For bounded magnitudes, perception is linear in log-odds with neutral point $1/m$. Test: new tasks |
| Allais paradox | L | Do log-odds weighting parameters from perception predict the same person's choices? |
| Hormesis vs linear no-threshold | L | Does split-dose composition add associatively on the $-\log S$ (Bliss) scale? In the linear-quadratic class, grouping and order hold even with incomplete repair, so a pass does not exclude repair (Murray 2026n). A failure needs a matched-present test before it is read as memory |
| Peto's paradox | L | Under the multistage model, cloglog risk rises with slope 1 in $\ln$(cell number). Test: the compensating shift across species |
| Niche vs neutral (plankton) | L | With more than two types, composition lives on the flat log-ratio simplex. Neutral means exchangeable drift, possibly with a reversible current, not zero drift. Niche means frequency-dependent drift. Tests: frequency dependence for the gradient part, and time-reversal asymmetry for the circulating part (Murray 2026y) |
| Exoplanet radius valley | L | Retained envelope fraction in the multiplicative chart (§10.3). Is complete stripping explained by zero-order loss or by feedback? |
| ATP synthase efficiency | L | Is the forward-step fraction logistic in the per-cycle affinity, with sinh net flux (§10.3)? |
| Easterlin paradox | L | Is the income effect a constant shift on an ordered-logit scale across countries? |
| St Petersburg paradox | L | A finite ceiling is the bounded-utility resolution, but its legitimacy is the point in dispute |
| Bell nonlocality | O | The question is factorisation of joint distributions, not composition of a bounded scalar |
| Black-hole information | O | Unitarity of evaporation is not addressed by C1–C4 |
| Gibbs paradox | O | Continuity fails: distinguishability is binary |
| Maxwell's demon | O | Feedback, resolved by Landauer–Bennett accounting (Bennett 1982) |
| Arrow of time (Loschmidt) | O | Monotonicity fails for reversible microdynamics |
| Olbers' paradox | O | Finite age, a causal fact, not a composition law |
| Cosmological constant; hierarchy | O | No bounded quantity being composed |
| Dark matter vs MOND | O | No ceiling; an empirical question |
| Yang–Mills existence and mass gap | O | The classification carries no spectral information (§8.3) |
| Banach–Tarski; Russell; Gödel | O | Non-measurable sets or discrete self-reference |
| Simpson's reversal; obesity and French paradoxes | O | Causal structure (confounding, selection), not a chart effect |
| Ellsberg paradox | O | A set of priors, not a single bounded scalar |
| Equity premium; C-value; hard problem of consciousness | O | No ceiling or no composition law |

The register has 38 entries: 12 re-read, 11 located, 15 outside. The pattern:

- Every **R** is a re-reading. These cluster where UHL's mathematics simply *is* the physics (relativity, optics, belief, odds).
- The **L** entries cluster in bounded probabilities and frequencies across biology, psychology and economics. There UHL fixes the coordinate and turns a debate into a test.
- The deepest open problems of physics and of mind are **O**. The law says so because its conditions are explicit, and it claims nothing about them.


# Part III — The Test

# 13. The protocol, and two results

One protocol checks any bounded quantity against the law, often with data that already exist. Each step either confirms a condition in that system or locates the one that fails.

## 13.1 Protocol

0. **Earn the state.** Prepare the same present by different histories and apply the same intervention (Theorem 10). Different futures mean the quantity is not a state (Case I), and nothing below applies. Before fitting a projective point map, check that repeated preparations under one action give a next state within measurement error (the Point-Map Gate of Murray 2026a).
1. **Name the quantity and its horizons.** State the ceiling(s), the resting state, and whether the resting state is interior (group) or at an end (monoid).
2. **Test the action gate, grouping and waiting.** Prepare two interventions with equal endpoints from rest and apply each from a second state; different results fail the action gate (§5.1). Compare $(a\oplus b)\oplus c$ with $a\oplus(b\oplus c)$; test waiting with dynamic closure (Proposition 7). Measure the order effect of pairs of small interventions across states; a vanishing $fg'-gf'$ shows a shared rapidity (Proposition 6). Disagreement rejects the encoding, associativity, the endpoint model or sufficiency (§5.1); use step 0 to decide which.
3. **Identify the chart.** Fit the one-horizon dial or the two-horizon logit and compare with the chart mechanism predicts (§3.1, §4.5). Where projectivity is claimed, test it with cross-ratio (Theorem 6). A failed cross-ratio test rules out projectivity, not closure.
4. **Test inertia.** Under nominally constant drive, check that $\psi(x(t))$ is straight; read a bend as feedback, a changing drive or a state-dependent increment (§6.1). Fit medians (Theorem 21).
5. **Test invariance.** Check which chart's rapidity shift is constant across baselines, on stratum-level effects (§6.2); the exact form is kinematic closure (Murray 2026n).
6. **Measure the boundary exponent and the cost of approach.** From the approach to the ceiling under known drive, estimate $\gamma$ (and, for noisy systems, the noise exponent $\beta$). $\gamma\ge1$ predicts a horizon; $\gamma<1$ predicts arrival (Proposition 9). For a maximum-entropy average, predict $\gamma$ from the reference measure (Proposition 3: 1 for an isolated atom, 2 for a power-law density with no atom, $1+1/(a+2)$ for an atom beside a density $\sim u^a$, larger than 2 for a density vanishing faster than any power) and check the remaining gap against $\delta(0)e^{-L\int k}$.
7. **Audit boundary arrivals.** For every observed arrival identify the broken condition (Theorem 18).
8. **In two or more dimensions, identify the cone, the update class and the comparison.** Decide from the channels whether the cone is orthant, Lorentz or matrix, whether each intervention is reversible or forward-only (does it preserve, contract or erase projective distances?), and which distance the observer measures (Theorem 25); test commutation of updates; estimate signed curvature from reassociation defects (Murray 2026f, App. B); for state spaces built from history, compute Gromov $\delta$ and best-fit curvature (H7).

**A caution on power.** In the linear-quadratic dose class, agreement across challenge amplitudes and zero-gap order tests has exactly zero power against hidden state (Murray 2026n, Theorem 2). A pass in such a class is not evidence of a closed state.

Pre-register the predicted chart, dial position, ceiling, exponent and cone before any held-out data are examined, together with the loss condition.

## 13.2 First result: which effect scale travels?

We ran step 5 in its weakest form on 19 public meta-analyses of two-arm trials with binary outcomes (*metadat*; White et al. 2026), control-group risks 0.02% to 89%, computing $I^2$ for four effect measures.

| Measure | Median $I^2$ | Lower $I^2$ than the risk difference | Wilcoxon $p$ vs risk difference |
|---|---|---|---|
| Risk difference (flat) | 0.52 | — | — |
| Log risk ratio | 0.17 | 14 of 19 | 0.001 |
| Log odds ratio | 0.19 | 14 of 19 | 0.001 |
| Bliss-chart difference | 0.50 | 11 of 19 | 0.019 |

In five meta-analyses all measures had $I^2=0$. Among the other 14, the flat risk difference was the least consistent in 11. This is a small replication of Engels et al. (2000), Deeks (2002) and Zhao et al. (2022, 64,929 Cochrane meta-analyses); Poole, Shrier and VanderWeele (2015) caution that part of the excess may reflect power. It cannot distinguish the log risk ratio from the log odds ratio, which nearly coincide for rare events, so it does not test the mechanism-specific form of H2.

## 13.3 Second result: a pre-registered test of the dial reading, which failed

Version 1.0 stated H1 as: the dial position $\alpha$ measures mechanistic overlap, near 0 for independent agents and near 1 for a shared target. We tested it on the largest set of full dose-response matrices available to us, the DECREASE validation set (Ianevski et al. 2019): 210 blocks, 8×8 matrices, 36 drug pairs, 13 cell lines. The mechanistic overlap of every pair (0 distinct, 1 same signalling axis, 2 shared target), the effect definition, the fitting procedure and the loss condition were written down before any fit (supplementary `h1_decrease/preregistration.md`). For each block, single agents were fitted by Hill curves, and $\alpha\in[-5,1]$ was fitted by least squares over the 49 interior wells.

| Test | Spearman $\rho$ (overlap vs $\alpha$) | permutation $p$ | $n$ |
|---|---|---|---|
| Primary: per-pair median $\alpha$ | $-0.12$ | 0.76 | 36 pairs |
| Per-block $\alpha$ | $-0.11$ | 0.94 | 210 blocks |
| Raw single agents | $-0.11$ | 0.74 | 36 pairs |
| Both Hill slopes in $[0.5,2]$ | $-0.13$ | 0.75 | 30 pairs |

Median per-pair $\alpha$: distinct mechanisms $0.24$; same axis $-0.60$; the one shared-target pair (everolimus with dactolisib) $0.10$, five of its ten cell lines at the upper bound $\alpha=1$ and the other five below zero, two of them at the lower bound $\alpha=-5$. Both clauses of the pre-registered loss condition were met ($\rho<0$ and $p>0.05$), in the primary test and in every sensitivity analysis. **H1 as stated in version 1.0 is refuted on this dataset.**

The failure is partly structural. Checked on exact sham combinations: the true Loewe surface sits at $\alpha=1$ only for Hill slope 1 with full efficacy; at slope 2 the dial assigns it about $\alpha=-3.5$ to $-4$, depending on the dose grid, at slope 3 it leaves the scale, and with unequal maximal effects it falls below every dial surface. In this screen the median slopes were 2.0 and 1.3, and $\alpha$ sat at a bound in 65% of blocks. The dial is the complete classification of projective one-horizon laws (Theorem 8); it is not a general synergy scale. H1 is restated in §4.5 as a claim about the two surfaces. An independent reviewer reran the analysis on the public files and reproduced the primary result exactly ($\rho=-0.12075$, one-sided $p=0.75582$, 36 pairs). The same review found a reversed bisection step in the original script's post-hoc Loewe calibration; it has been corrected; every primary and sensitivity statistic is unchanged to five decimals, and the sham-combination values quoted here come from a separate solver that did not contain the error. Limits of the run: the set was chosen by its authors as novel combinations, so it is enriched for synergy; there is one shared-target pair; wells are single replicates; the mechanistic annotations are the author's, fixed in advance, with two flagged as ambiguous.

![Left: median $I^2$ across 19 meta-analyses by effect scale. Right: dial position by mechanistic overlap in the DECREASE screen; the pre-registered prediction was an increase from left to right.](fig6_empirical.png){width=100%}

## 13.4 Next tests

| Dataset | Steps | Hypotheses |
|---|---|---|
| Combination screens with replicates and many shared-target pairs (NCI-ALMANAC, Holbeck et al. 2017; DrugComb, Zagidullin et al. 2019) | 2, 3, 6 | H1 restated, H3 |
| Stratum-level trial data spanning mid-range baselines | 5 | H2, mechanism-specific |
| Approach-to-ceiling kinetics with known mechanism (zero-order and first-order elimination; saturable transport) | 6 | Proposition 9, the exponent prediction |
| Single-cell perturbation spaces; neural state spaces | 8 | H7, item 3 of Theorem 25 |
| The Calabrese hormesis database (Calabrese and Blain 2005) | 4, 5 | zero-fit predictions of Murray (2026c); P6; P11 |
| Probability judgments across tasks within persons | 3, 4 | H5 |

## 13.5 What would refute the law

The mathematics cannot be refuted, given its conditions. What can be refuted is that a real system obeys it, and that the conditions can be told apart from outside:

- a quantity passes the grouping test (step 2) and is described systematically better by flat addition near its ceiling than by any rapidity;
- a horizon is reached with every condition intact;
- a maximum-entropy average is measured with $\gamma<1$;
- a ratio-read system with a continuous channel symmetry shows commuting reversible updates, or an orthant system shows holonomy under reversible updates;
- the two estimates of the ceiling disagree beyond error.

# Part IV — Interpretation

# 14. What the theorems license, and no more

**Limits as horizons.** For anything bounded that changes lawfully, the limit is a horizon: approachable without end, reached only by a jump that a named condition permits (Theorems 18–19). The speed of light, certainty and complete order are usually treated as separate facts; under the law they are one kind of fact. Fixation and extinction are the other kind: crossings by a discrete jump (Theorem 23).

**Why flat description felt true.** Everyday experience happens near rest, where flat and rapidity descriptions agree to within a fraction of a percent. The view was not wrong; it was local.

**The interior observer.** Homogeneity puts every observer at the centre of its own space. What a bound adds is a horizon that can be measured but not reached (Theorem 29), and, in branch (H), a perspective that carries holonomy. What the cone of the observer's channels and its admissible updates add is the invariant geometry, and forward-only updates erase distinguishability instead (Theorem 25). What finite resources add, if H7 holds, is that the space of remembered histories is negatively curved and grows with experience. These are statements about the interface between an observer and the world, not about the whole.

**History and prediction.** Lawful bounded systems compress their history into their present (Theorems 9–10). When changes come from one law the order is forgotten; when the law is non-associative in two or more dimensions, the order is kept as holonomy. Whether a biological present is a sufficient state is an empirical question (Murray 2026i), and what an observer needs in order to act is coarser still (Murray 2026q).

**Structure and bounds.** Within the lawful composition laws, flat is the parabolic boundary case. Persistent structures are forward-invariant regimes of bounded lawful dynamics, with interior fixed points as the simplest case (Murray 2026d, Cor. 7.1; 2026o). This is stated as interpretation.

# 15. Scope and claim register

The law applies wherever C1–C4 hold, or their gyro-associative form in more dimensions. Where they fail, it says only that the failure is informative (§7). The local chart is always supplied by the system (§2.4).

| Claim | Section | Status | Novelty | Check or test |
|---|---|---|---|---|
| Closure trichotomy (Prop 1) | §2.2 | P | Murray 2026a | Matched presents |
| Horizon theorem, group and monoid (Thms 1–2) | §2.3 | P | Classical (Aczél; Luce–Marley; uninorms) | — |
| Rapidity as the gradient of negentropy (Thm 3, Prop 2) | §3.1 | P | Classical, reinterpreted | Exponential families |
| Max-ent averages never reach their ceiling; exponent continuum; cost of approach (Prop 3) | §3.1 | P / D | New (bound, divergence, cost bound P; exponents D) | Step 6 |
| Energy- vs weight-additivity criterion | §3.1 | D | New | Binding assays |
| Flat as the infinite-ceiling limit; lawful mean (Prop 4) | §3.2 | P | Classical | Series; Kolmogorov–Nagumo |
| Trichotomy; flat as the parabolic boundary (Thm 4); compact case (Thm 5) | §3.3 | P / D | Classical; extension beyond kinematics D | $PSL(2,\mathbb R)$ |
| Observation projection, converse, Riccati (Thm 6, Prop 5) | §4.1 | P | Classical; observational use Murray 2026a | Cross-ratio test |
| Two horizons force the logit (Thm 7) | §4.2 | P | Small lemma (cf. Murray 2026z) | A.1 |
| One-horizon dial = Hamacher; drug laws on the dial (Thm 8) | §4.3 | P / D | Mathematics classical; placement new | A.2 |
| H1, restated (surfaces) | §4.5 | H | New; α-form refuted §13.3 | Screens with replicates |
| Present sums the past; order in 1D; shared-rapidity test; action gate; dynamic closure (Thm 9, Props 6–7) | §5.1 | P | Murray 2026n, 2026o, 2026p; bracket test and action gate stated here | Order, action and waiting tests |
| State–law descent (Thm 10) | §5.1 | P | Classical | Matched presents |
| Bounded-composition dichotomy; holonomy selects (Prop 8); abelianization | §5.2 | P | Murray 2026f, 2026h | Defect tomography |
| Inertial law; feedback detector (Thm 11) | §6.1 | P / D | Classical / new | Time series |
| Invariance; portable effect scale (Thm 12, H2) | §6.2 | P / H | Question classical; reason new | §13.2 |
| Interaction law; sinh from detailed balance; locking (Thms 13–16) | §6.3 | P | Transfer to rapidity new | A.4–A.7, B |
| Trajectory alphabet | §6.3 | D | New | Piecewise-drive experiments |
| Ceiling measurable from inside (Thm 17, H3) | §7.1 | P / H | New reading | Ceiling consistency |
| Boundary arrival (Thm 18) | §7.2 | P / D | New | Boundary audit |
| Boundary exponent unifies Osgood and Feller (Prop 9) | §7.3 | P / D | Classical parts P; unification D | Step 6 |
| Stochastic charts; no finite-time horizon; fixation (Thms 20–23) | §7.5 | P / D | Classical; reading new | B |
| The far side of the horizon (Thm 19); simultaneity instance; crossings (open) | §7.4 | P / D | Mathematics and instance classical; far-side reading of natural events open | — |
| Hyperbolic geometry given rigidity (Thm 24); dial 1D (Prop 10) | §8.1 | P | Classical; Murray 2026e | — |
| The cone and update class decide the geometry; forward-only updates contract (Thm 25) | §8.1 | P / H | Mathematics classical; reading new; item 3 prediction H | Commutation; contraction; curvature |
| Holonomy; compact isotropy (Thms 26–27) | §8.2 | P | Classical | Computed |
| Spectral threshold, not a mass gap (Thm 28) | §8.3 | P | Classical | McKean; Donnelly |
| Hyperbolic information space; trees do not fit flat space at fixed dimension and bounded distortion, and fit $\mathbb H^2$ (H7) | §8.4 | P / H | Measured by others; embedding bound P (A.20; Sarkar 2012); H7 new | Gromov $\delta$; curvature |
| Reflection chart | §9.2 | P | Classical | Optics |
| Selection as inertia; H4 | §10.1 | P / H | Classical / new | Experimental evolution |
| Bliss–Loewe gap; hormesis predictions; rescue windows | §10.2 | P / H | Murray 2026c, 2026e, 2026l | Dose data |
| Exoplanet and ATP-synthase charts | §10.3 | H | Proposed here | Loss-regime audit; affinity scans |
| Bayes as Einstein composition; H5 | §11.1 | P / H | Classical / new | Perception tasks |
| Observer centrality, group and gyrogroup cases (Thm 29) | §11.2 | P | Reading new | Geometry |
| Puzzle register (38 entries: 12 R, 11 L, 15 O) | §12 | as marked | New as a register | Sources cited |

**Completion rule.** The programme is complete when every [D], and every [P] resting on the author's own preprints, has been independently checked; every [H] has met data with its loss condition; and no row of this register is untested. This version reports one replication (§13.2) and one refutation (§13.3).


# Appendix A. Proofs of derived results

**A.1 Theorem 7 (two horizons).** A projective law on $(0,1)$ is generated by $X(e)=A+Be+Ce^2$. Both ends being horizons means $X(0)=X(1)=0$. This gives $A=0$ and $B+C=0$, so $X=c\,e(1-e)$ with $c=-C$. Integrating $\psi'=1/X$ with $\psi(e_0)=0$ gives $\psi=c^{-1}\{\log[e/(1-e)]-\log[e_0/(1-e_0)]\}$; take $e_0=\tfrac12$. Substituting $s=2e-1$ gives $\psi=2c^{-1}\operatorname{artanh}s$. Addition in $\psi$ is therefore $s\oplus s'=(s+s')/(1+ss')$. $\square$

**A.2 Theorem 8 (one horizon).** Normalise so that $X(0)=1$ (the rest is not a fixed point) and $X(1)=0$ (the horizon). Then $A=1$ and $C=-(1+B)$.

Write $\alpha=-(1+B)$. Then $X=1+Be-(1+B)e^2=(1-e)(1+(1+B)e)=(1-e)(1-\alpha e)$. The requirement of no interior fixed point is $1/\alpha\notin(0,1)$, that is, $\alpha\le1$. Integrating $\psi'=1/X$ gives $\psi_\alpha=(1-\alpha)^{-1}\log[(1-\alpha e)/(1-e)]$.

For $\alpha\to1$ the limit is $e/(1-e)$ (Loewe). For $\alpha\to-\infty$ the operations converge pointwise to the drastic sum, which is discontinuous. $\square$

**A.3 The action gate and associativity (§5.1).** Suppose each intervention $b$ acts on states by a map $T_b$ and is recorded by its endpoint from rest, $\bar b=T_b(e)$. A binary operation $x\oplus\bar b:=T_b(x)$ on values is well defined if and only if $\bar b=\bar b'$ implies $T_b=T_{b'}$: the action gate. Without it, two interventions with the same recorded value act differently from some state, and no composition law on values represents the interventions by their endpoints from rest, even when $x$ is a sufficient predictive state.

 Let the history be a sequence of changes, and let the present be $x_n=a_1\oplus\cdots\oplus a_n$. The future under a further change $b$ is $x_n\oplus b$.

Suppose the future under $b$ depends on the history only through a single-valued operation $x_n\oplus b$ (compositional descent). Then any two histories with the same $x_n$ have the same future under every $b$, so $x_n$ is a state in the sense of Theorem 10. Single-valuedness, not C2, carries this step. C2 is then what makes the present independent of how the history is grouped, since concatenation of histories is associative (Proposition 1).

Conversely, suppose futures depend on the history only through $x_n$, so that appending a change acts by a single-valued map $F$ on presents. Since concatenation of histories is associative, $F(F(a_1,a_2),b)=F(a_1,F(a_2,b))$, which is C2 (Proposition 1). $\square$

**A.4 Theorem 13 (interaction law).**

- (a) Invariance under separate shifts gives $\partial_\psi F=\partial_\varphi F=0$, so $F$ is constant. The same holds for $G$.
- (b) Only A0 and A2 are used. Invariance under the joint shift gives $\partial_\psi F+c\,\partial_\varphi F=0$. The characteristics of this equation are the lines $c\psi-\varphi=\text{const}$, so $F=f(c\psi-\varphi)$, and likewise for $G$. Rescaling $\varphi$ by $1/|c|$ gives $F=f(\Delta)$ and $G=g(\Delta)$, with $\Delta=\psi-\sigma\varphi$. Then $\dot\Delta=f(\Delta)-\sigma g(\Delta)$ is closed.
- (c) At a zero $\Delta^*$, $\dot\psi=f(\Delta^*)$ and $\dot\varphi=g(\Delta^*)$ are constants with $f(\Delta^*)=\sigma g(\Delta^*)$, so $\Delta$ stays fixed.

$\square$

**A.5 Theorem 14.** With $c>0$ and drive-independent $h_i$, A4 gives $h_2=-h_1$, and A3 gives $h_2(\Delta)=h_1(-\Delta)$. Together, $h_1(-\Delta)=-h_1(\Delta)$, so $h_1$ is odd. Neither assumption alone forces oddness. Write $h_1=-\beta u$ with $\beta\ge0$; A4′ fixes the sign. Then $\dot\Delta=k_1-k_2+h_1-h_2=\Phi-2\beta u(\Delta)$.

Relaxing A3–A4 to strengths $\beta_1\ne\beta_2$, a lock exists when $u^*=\Phi/(\beta_1+\beta_2)$ lies in the range of $u$, and the common speed is $k_1-\beta_1u^*=(\beta_2k_1+\beta_1k_2)/(\beta_1+\beta_2)$. $\square$

**A.6 Theorem 15.** A6 with continuity and positivity is Cauchy's multiplicative equation, so $r_+(\Delta)=r_0e^{a\Delta}$. The rate form of exchange symmetry gives $r_-(\Delta)=r_+(-\Delta)$. Detailed balance, $r_+/r_-=e^{\Delta}$, then requires $e^{2a\Delta}=e^\Delta$, so $a=\tfrac12$. The net flux is $r_+-r_-=2r_0\sinh(\Delta/2)$. Without the rate form of exchange symmetry, detailed balance gives $r_-=r_0e^{(a-1)\Delta}$, and the net flux is $2r_0e^{(a-1/2)\Delta}\sinh(\Delta/2)$. $\square$

**A.7 Theorem 16.** Take $V(\Delta)=2\beta\int_0^\Delta u-\Phi\Delta$. Then $V'=2\beta u-\Phi=-\dot\Delta$, so $\dot V=V'\dot\Delta=-\dot\Delta^2\le0$.

A lock exists exactly when $\Phi/2\beta$ lies in the range of $u$. For unbounded increasing $u$ and $\beta>0$, $V$ is coercive with a single critical point, so the lock is globally stable. For sinh the lock is at $\operatorname{arsinh}(\Phi/2\beta)$. For tanh with $|\Phi|>2\beta$, $\dot\Delta$ keeps the sign of $\Phi$ and is bounded away from zero, so $|\Delta|\to\infty$ and $\tanh\Delta\to\mathrm{sgn}\Phi$. The speeds then tend to $k_1-\beta\,\mathrm{sgn}\Phi$ and $k_2+\beta\,\mathrm{sgn}\Phi$. For sin, the period of slip is $\int_0^{2\pi}d\Delta/(\Phi-2\beta\sin\Delta)=2\pi/\sqrt{\Phi^2-4\beta^2}$. $\square$

**A.8 Theorem 17.** From $a\oplus b=(a+b)/(1+ab/\ell^2)$ we get $(a+b)/(a\oplus b)=1+ab/\ell^2$. Hence $\ell^2=ab(a\oplus b)/(a+b-a\oplus b)$. Expanding the first identity to third order gives $a+b-ab(a+b)/\ell^2$. $\square$

**A.9 Theorem 18.** Suppose C1–C4 hold throughout, the law is fixed, and each change has finite rapidity. Then after $n$ changes the rapidity is a finite sum (Theorems 1–2). Under a finite, integrable drive it is a finite integral (Theorem 11). Both are finite, so no horizon is reached. Arrival therefore requires a failed condition, a divergent sum, or a changed law. $\square$

**A.10 Theorem 21.** $\psi(t)$ is Gaussian and the map $\psi\mapsto p$ is strictly increasing, so the $q$-quantile of $p(t)$ is $\operatorname{logistic}$ applied to the $q$-quantile of $\psi(t)$. The median of $\psi(t)$ is $\psi_0+kt$, so the median of $p$ is the deterministic logistic. The mean is a nonlinear average, so it is not. $\square$

**A.11 Theorem 25, item 1.** Suppose an invertible $M$ maps the open ball, the projectivisation of the cone $Q(z)=z_0^2-|z|^2>0$, onto itself. Then it maps the boundary quadric to itself. For $n\ge2$ the real cone $Q=0$ is Zariski-dense in the irreducible complex quadric. So $Q\circ M$, which vanishes wherever $Q$ does and has the same degree, equals $\lambda Q$: $M^TJM=\lambda J$. For $n=1$ ($Q=uv$ in null coordinates), $M$ is diagonal or antidiagonal in $(u,v)$, with the same conclusion.

Mapping the interior onto the interior requires the sign of $Q$ to be preserved, so $\lambda>0$. Hence $M/\sqrt\lambda\in O(1,n)$. Since $O(1,n)=O^+(1,n)\cup(-I)O^+(1,n)$, we have $\mathbb R^+\cdot O(1,n)=\mathbb R^\times\cdot O^+(1,n)$. $-I$ acts trivially on ratios, so a time-reversing $M$ acts on the ball as the orthochronous $-M$.

Boosts act on ratio coordinates by the Einstein gyro-addition formula (Ungar 2008). $\square$

**A.12 Theorem 25, item 2 (the simplex).** Take positive channels $z_i>0$ and diagonal updates $M=\operatorname{diag}(m_0,\dots,m_n)$ with $m_i>0$. These map the open simplex $\{z/\sum_j z_j\}$ (projectively, the positive orthant) onto itself and commute. Every projective automorphism of the simplex is such a map times a vertex permutation, so every continuous family of updates has this form. In log-ratio coordinates $y_i=\log(z_i/z_0)$ they act by translation, so composition is vector addition and the invariant geometry is flat. The boundary lies at $|y|=\infty$, so it is unreachable. $\square$

**A.13 Theorem 29.** Items 1–3 follow from homogeneity: the map $x\mapsto(\ominus o)\oplus x$ is an isometry sending $o$ to $0$. Item 4 is Theorems 1, 2 and 17. Item 5 is Theorem 26 applied to the loop of base points. $\square$

**A.14 Energy-additivity (§3.1).** For two states the Boltzmann ratio is $p_+/p_-=e^{2\theta}$. Contributions that each multiply this ratio (additive energy differences) add in $\theta$.

Competing ligands $L_1$ and $L_2$ at one site add Boltzmann weights instead. The occupancy is $([L_1]/K_1+[L_2]/K_2)/(1+[L_1]/K_1+[L_2]/K_2)$, whose odds add: this is Loewe additivity, the parabolic ($\alpha\to1$) end of Theorem 8. $\square$

**A.15 Proposition 2.** For two states with counting measure, the log-partition function is $A(\theta)=\ln(2\cosh\theta)$ and the entropy is $H=A-\theta m$. The negentropy relative to the maximum $\ln2$ is $J=\ln2-H=\theta\tanh\theta-\ln\cosh\theta$. As $\theta\to\infty$, $\ln\cosh\theta=\theta-\ln2+o(1)$, so $J\to\ln2$. Near 0, $J=\theta^2-\theta^2/2+O(\theta^4)=\theta^2/2+O(\theta^4)$. Differentiating, $dJ/d\theta=\theta\operatorname{sech}^2\theta=\theta(1-m^2)$. $\square$

**A.16 Proposition 3.** Let $s\in[s_{\min},s_{\max}]$ $\mu$-almost surely and write $u=s_{\max}-s\ge0$, so $u\le L$. Then $\mathrm{Var}_\theta(s)=\mathrm{Var}_\theta(u)\le\mathbb E_\theta[u^2]\le L\,\mathbb E_\theta[u]=L\,(s_{\max}-m)$. Hence $X(m)\le L(s_{\max}-m)$ and $\int^{s_{\max}}dm/X(m)\ge L^{-1}\int^{s_{\max}}dm/(s_{\max}-m)=\infty$; by Osgood's criterion (Proposition 9a) no dynamics $\dot m=kX(m)$ with bounded $k$ reaches $s_{\max}$ in finite time. For the exponents: under the tilt $e^{\theta s}=e^{\theta s_{\max}}e^{-\theta u}$, if $\mu$ has an isolated atom at $u=0$ with the rest of its mass at $u\ge\Delta>0$, then $\Delta\,\mathbb E u\le\mathbb E u^2\le L\,\mathbb E u$ and $(\mathbb Eu)^2=o(\mathbb E u^2)$, so $X\asymp(s_{\max}-m)$ and $\gamma=1$ (with $X\sim\Delta(s_{\max}-m)$ when the remaining mass is an atom at $\Delta$); if $\mu$ has density $\sim u^a$ near $u=0$, the tilted law of $u$ is asymptotically Gamma$(a+1,\theta)$, so $\mathbb Eu\sim(a+1)/\theta$ and $\mathrm{Var}\,u\sim(a+1)/\theta^2=(s_{\max}-m)^2/(a+1)$, giving $\gamma=2$; if an atom of mass $p$ at $u=0$ meets a density $c\,u^a$ ($a>-1$), then $\mathbb Eu\sim c\,\Gamma(a+2)/(p\theta^{a+2})$ and $\mathrm{Var}\,u\sim\mathbb Eu^2\sim c\,\Gamma(a+3)/(p\theta^{a+3})$, so $X\propto(s_{\max}-m)^{(a+3)/(a+2)}$ and $\gamma=1+1/(a+2)$; $a=0$ gives $3/2$. If instead the density near the end is $e^{-1/u}$ with no atom, Laplace's method puts the tilted law at $u\approx\theta^{-1/2}$ with mean $\approx\theta^{-1/2}$ and variance $\approx\theta^{-3/2}/2$, so $X\approx(s_{\max}-m)^3/2$ and $\gamma=3$; $e^{-1/u^k}$ gives $\gamma=k+2$. For the corollary, $\dot\delta=-\dot m=-k\,X(m)\ge-kL\delta$ for $k\ge0$, and Grönwall's inequality gives $\delta(t)\ge\delta(0)\exp(-L\int_0^tk)$. The numerical checks are in Appendix B. $\square$

**A.17 Proposition 4.** Averaging in rapidity commutes with composition: $\psi(\overline{x\oplus m}_\psi)=\mathbb E\psi(x)+\psi(m)$. For the bias, expand $\mathbb E\psi(x)=\psi(\mu)+\tfrac12\psi''(\mu)\sigma^2+O(\sigma^3)$ and invert: $\bar x_\psi=\mu+\psi''(\mu)\sigma^2/(2\psi'(\mu))+O(\sigma^3)$. For $\psi=\ell\operatorname{artanh}(x/\ell)$, $\psi''/\psi'=2x/(\ell^2-x^2)$. $\square$

**A.18 Proposition 6.** For the bracket test: to second order the flow of $f$ for time $\varepsilon$ is $x\mapsto x+\varepsilon f+\tfrac12\varepsilon^2ff'$; composing with the flow of $g$ in both orders and subtracting leaves $\varepsilon\eta(fg'-gf')$ at order $\varepsilon\eta$ (checked symbolically). If $fg'-gf'=0$ where $f\neq0$, then $(g/f)'=(g'f-gf')/f^2=0$, so $g=cf$, and $\psi=\int dx/f$ turns both flows into translations. For the affine example, with $T_d(z)=qz+b(d)$, $T_b(T_a(z))-T_a(T_b(z))=(q-1)[b(a)-b(b)]$. Since $\tanh$ is injective, the two orders give different bounded states whenever $q\neq1$ and $b(a)\neq b(b)$. $\square$

**A.19 Theorem 19.** (1) The map $x\mapsto(x+a)/(1+ax)$ with $|a|<1$ is a Möbius transformation of the projective line that fixes $\pm1$; being orientation-preserving ($1-a^2>0$) and fixing $\pm1$, it maps each of the two arcs cut out by $\{-1,+1\}$ to itself, so it maps $|x|<1$ to itself and $|x|>1$ to itself. (2) For $|x|>1$, $\operatorname{artanh}x=\tfrac12\log\frac{1+x}{1-x}$ has negative argument; taking the principal branch, $\tfrac12\log\frac{1+x}{1-x}=\tfrac12\log\frac{x+1}{x-1}+\tfrac{i\pi}{2}=\operatorname{artanh}(1/x)+\tfrac{i\pi}{2}$, and $\operatorname{artanh}$ of a Möbius image is the sum of the artanh values because the identity $\operatorname{artanh}(x\oplus a)=\operatorname{artanh}x+\operatorname{artanh}a$ holds modulo $i\pi$ for the multivalued artanh, and with the branch above the imaginary part is $i\pi/2$ on the whole far side and $0$ inside, so it holds exactly because (1) preserves each side. (3) The complement of the closed ball in $\mathbb{RP}^n$ is the projectivised exterior of the cone $z_0^2-|z|^2>0$, on which the induced metric of signature $(1,n-1)$ is that of de Sitter space modulo the antipodal map, with the same projective automorphism group $PO(1,n)$ (O'Neill 1983, Ch. 4; Ratcliffe 2006). $\square$

**A.20 §8.4 (trees in fixed dimension).** Let $\phi$ embed the complete $b$-ary tree of depth $r$ into $\mathbb R^d$ with $\|\phi(x)-\phi(y)\|\ge\rho\,d_T(x,y)$ and $\le\rho D\,d_T(x,y)$. Leaves are at tree distance at least 2 from each other and exactly $r$ from the root, so their images are $2\rho$-separated points in the ball of radius $\rho Dr$ about the root's image; disjoint balls of radius $\rho$ around them fit in a ball of radius $\rho(Dr+1)$, so their number $b^r\le(Dr+1)^d$, which fails for large $r$ at fixed $d$ and $D$. $\square$

# Appendix B. Verification record

All numerical and symbolic checks were run in Python (NumPy, SciPy, SymPy).

| Claim | Check | Result |
|---|---|---|
| §2.4 non-Einstein admissible law | tangent law, $0.3\oplus0.5$ | 0.628 vs Einstein 0.696 |
| §3.1 negentropy slope | $dJ/dm$ symbolic | $\operatorname{artanh}m$ |
| §3.1 Fisher length, two states | $\int_0^1 dp/\sqrt{p(1-p)}$ | $\pi$ |
| §3.2 error table | $\operatorname{artanh}(f)/f-1$ | 0.3%, 9.9%, 63.6%, 167.3% |
| Theorem 4 generator | symbolic | $1-\kappa u^2$; $2\oplus2=-4/3$ at $\kappa=-1$ |
| Theorem 7 | symbolic | $X\propto e(1-e)$ |
| Theorem 8 drastic limit | $0.1\oplus0.2$ at $\alpha=-1,-10,-10^3$ | 0.294, 0.400, 0.966 |
| §5.2 gyration = area of $(0,a,a\oplus b)$ | $(a,b)=(0.5,0.5i)$; $(0.4+0.2i,\,0.7e^{2i})$; $(0.3+0.1i,\,-0.2+0.5i)$ | 0.48996 / 0.48996; 0.60035 / 0.60035 (area of $(0,a,b)$ 0.61264); 0.34012 / 0.34012 |
| Theorem 16 locks | $\Phi=2.5$, $2\beta=2$ | sinh lock 1.048; sin slip period 4.18880 vs 4.18879 |
| Theorem 16 tanh unlock | $k_1=10$, $k_2=5$, $\beta=1$ | asymptotic speeds 9.0 and 6.0 (both toward $+\infty$) |
| Theorem 15 without rate symmetry | symbolic | net flux $2r_0e^{(a-1/2)\Delta}\sinh(\Delta/2)$ |
| Proposition 2 | symbolic | $J=\theta\tanh\theta-\ln\cosh\theta$; limit $\ln2$; $dJ/d\theta=\theta(1-m^2)$ |
| Proposition 4 | $10^6$ draws, $\mu=0.8$, $\sigma=0.03$ | lawful-mean bias 0.00205 vs predicted 0.00200 |
| Proposition 5 | symbolic | $\dot q=b+(a-d)q-cq^2$ |
| Proposition 6 | symbolic | order defect $(q-1)[b(a)-b(b)]$ |
| Theorem 8 landmarks | symbolic | $\alpha=-1$ gives $(a+b)/(1+ab)$; Tsallis $q>1$ rescales to $e_1+e_2-e_1e_2$ |
| Theorem 17 | exact identity at $a=0.1$, $b=0.2$ | $\ell^2=1.000000$ |
| Theorem 22 | $10^6$ paths at $t=5$ | no path reached 0 or 1 |
| Theorem 23 | Wright–Fisher, $N=100$, 40,000 runs | $P_{\text{fix}}=0.0097$ (theory 0.0100); $T_1=199.9$ (theory 199.0) |
| Theorem 23 beneficial allele | $(2/s)[\ln(2Ns)+\gamma_E]$ vs Kimura–Ohta (1969) integral from $p=1/N$, four cases with $Ns\ge100$ | approximation high by 1.0–2.0 generations in each case |
| Theorem 23(a) | Feller test in the logit chart | both ends exit boundaries for every $s$ |
| Theorem 27 | $\mathfrak{so}(1,3)$ brackets | $[K_1,K_2]=-J_3$; compact dual $[P_1,P_2]=+J_3$ |
| Theorem 25 item 1 | 3D boost image vs Einstein $u\oplus v$ | agreement to $10^{-10}$ |
| Theorem 26 | commutator of $\operatorname{gyr}[0.6e_1,0.6e_2]$ and $\operatorname{gyr}[0.6e_2,0.6e_3]$ | Frobenius norm 0.069; both proper rotations |
| §9.2 mirror | $N=30$, ratio 1.5 | $1-R=1.09\times10^{-10}$ |
| §10.2 Bliss–Loewe | peak | $e^*=0.618$, $g=0.0902$ |
| §11.1 Bayes | exact | $\lambda=\tanh(\tfrac12\log\mathrm{LR})$ |
| §12 non-collapsibility | odds ratio 3 in strata 0.2 and 0.8 | pooled 2.085 |
| §13.2 data | 19 meta-analyses | see §13.2 |
| Proposition 3 exponents | tilted means and variances, $\theta=20,60$ | $\mathrm{Var}/(1-m)^2\to1/(a+1)$ for densities $u^a$, $a=0,1,2$ (1.0000, 0.5000, 0.3333); two-point $\mathrm{Var}/(1-m)\to2$; Langevin ratio 1.0000 |
| Proposition 9a (Osgood) | $\dot e=(1-e)^\gamma$ from 0 | arrival at $T=1,2,10$ for $\gamma=0,0.5,0.9$; no arrival for $\gamma=1,1.5,2$ |
| Proposition 9b (Feller) | Wright–Fisher $N=200$, 400 runs, 2000 generations | at a boundary in 100% of runs with $\mu=0$; 0% with two-way mutation $4N\mu=4$ |
| Ceiling exponents of the charts | lowest power of $1-e$ in $X$ | logit 1, Bliss 1, dial ($\alpha<1$) 1, Loewe 2, zero-order 0 |
| Theorem 19, simultaneity | $v=0.3,u=0.5$; $v=0.8,u=-0.6$ | $1/(v\oplus u)=(1/v)\oplus u=1.4375$; $2.6000$ |
| Proposition 3 continuum | atom of mass 0.3 plus density $u^a$ (constant 1), local exponent of $\mathrm{Var}$ against the gap between $\theta=10^3$ and $10^5$ | 1.6747, 1.5000, 1.3333, 1.2000 for $a=-0.5,0,1,3$ vs $1+1/(a+2)$ = 1.6667, 1.5000, 1.3333, 1.2000 (the $a=-0.5$ value converges slowly) |
| Proposition 3, no upper bound | density $e^{-1/u}$, no atom | local exponent 2.9555, 2.9859 at $\theta=10^3,10^4$; $\mathrm{Var}/\delta^3\to0.5$ |
| Theorem 16, beyond the tanh threshold | $\beta=1$, $\Phi=2.1,2.2,2.4$ | long-run drift of the gap 0.1000, 0.2000, 0.4000 $=|\Phi|-2\beta$ |
| Proposition 3 corollary | two-state motion, $L=2$ | $\min\delta(t)/[\delta(0)e^{-L\theta}]=1.0000$ (bound holds, tight at start) |
| Proposition 6 bracket | symbolic, second order | order difference $\varepsilon\eta(fg'-gf')$ |
| Theorem 25 item 4 | $M=\bigl(\begin{smallmatrix}2&1\\1&2\end{smallmatrix}\bigr)$, 2000 random pairs | maximum Hilbert contraction 0.3333 $=\tanh(\ln4/4)$; $AB-BA\neq0$ for the two orthant maps |
| Theorem 25, Bures | radial Bures length centre to pure state | $\pi/4$ |
| Theorem 16 tanh near threshold | $\Phi=1.0,1.8,1.98$, $\beta=1$ | locked gap 0.549, 1.472, 2.647; relaxation rate 1.500, 0.380, 0.040 |
| Theorem 19 | Einstein composition across the horizon | $0.5\oplus2=1.25$; $-0.9\oplus3=-1.2353$; $0.3\oplus(-1.5)=-2.1818$; $\operatorname{artanh}(0.5)+\operatorname{artanh}(2)=\operatorname{artanh}(1.25)=1.0986+1.5708i$ |
| Theorem 25 items 1–2 | commutators | diagonal simplex updates: 0; two boosts of speed 0.5: 0.504 |
| §8.4 room | circumference ratio $\sinh r/r$ | 1.18, 15, 1100 at $r=1,5,10$ |
| §13.3 H1 | DECREASE, 210 blocks | $\rho=-0.12$, $p=0.76$ (pairs); see supplementary |


# Declarations

**Funding.** None.

**Competing interests.** The author declares no competing interests.

**Data and code availability.** The meta-analysis data are public (*metadat*, CRAN); the combination screen is public (DECREASE, GitHub). Analysis code, the H1 pre-registration and all verification scripts are provided as supplementary material.

**Author contributions.** D.J.M. conceived the framework and the programme, and wrote and approved the manuscript.

**Ethics approval and consent.** Not applicable.

**Use of AI tools.** Drafting, literature checking, symbolic and numerical verification, and independent critical review of the manuscript were assisted by an AI system (Claude, Anthropic). The author directed the work and takes full responsibility for the content. Some bibliographic details of secondary sources were confirmed through citing works rather than the originals and will be checked against the originals at proof stage.


# References

Aczél J (1949) Sur les opérations définies pour nombres réels. Bull Soc Math France 76:59–64

Aczél J (1966) Lectures on Functional Equations and Their Applications. Academic Press, New York

Adler R (1946) A study of locking phenomena in oscillators. Proc IRE 34:351–357

Amari S, Nagaoka H (2000) Methods of Information Geometry. American Mathematical Society, Providence

Anker J-P, Ziegler F (2020) Relativity without light: a new proof of Ignatowski's theorem. arXiv:2007.09301

Aravind PK (1997) The Wigner angle as an anholonomy in rapidity space. Am J Phys 65:634–636

Bacry H, Lévy-Leblond J-M (1968) Possible kinematics. J Math Phys 9:1605–1614

Barndorff-Nielsen O (1978) Information and Exponential Families in Statistical Theory. Wiley, Chichester

Barriuso AG, Monzón JJ, Sánchez-Soto LL, Cariñena JF (2004) A vectorlike representation of multilayers. J Opt Soc Am A 21:2386–2391 (arXiv:physics/0403140)

Bengtsson I, Życzkowski K (2006) Geometry of Quantum States: An Introduction to Quantum Entanglement. Cambridge University Press

Bennett CH (1982) The thermodynamics of computation—a review. Int J Theor Phys 21:905–940

Bilaniuk OMP, Deshpande VK, Sudarshan ECG (1962) "Meta" relativity. Am J Phys 30:718–723

Birkhoff G (1957) Extensions of Jentzsch's theorem. Trans Amer Math Soc 85:219–227

Bourgain J (1986) The metrical interpretation of superreflexivity in Banach spaces. Israel J Math 56:222–230

Bushell PJ (1973) Hilbert's metric and positive contraction mappings in a Banach space. Arch Rational Mech Anal 52:330–338

Calabrese EJ, Blain R (2005) The occurrence of hormetic dose responses in the toxicological literature, the hormesis database: an overview. Toxicol Appl Pharmacol 202:289–301

Chen J-L, Ungar AA (2002) The Bloch gyrovector. Found Phys 32:531–565

Colnet B, Josse J, Varoquaux G, Scornet E (2023) Risk ratio, odds ratio, risk difference… Which causal measure is easier to generalize? arXiv:2303.16008

Crutchfield JP, Young K (1989) Inferring statistical complexity. Phys Rev Lett 63:105–108

Deeks JJ (2002) Issues in the selection of a summary statistic for meta-analysis of clinical trials with binary outcomes. Stat Med 21:1575–1600

Doi SA, Furuya-Kanamori L, Xu C, et al (2022) Controversy and debate: questionable utility of the relative risk in clinical research. J Clin Epidemiol 142:271–279

Dombi J (1982) Basic concepts for a theory of evaluation: the aggregative operator. Eur J Oper Res 10:282–293

Donnelly H (1981) The differential form spectrum of hyperbolic space. Manuscripta Math 33:365–385

Einstein A (1905) Zur Elektrodynamik bewegter Körper. Ann Phys 17:891–921

Engels EA, Schmid CH, Terrin N, Olkin I, Lau J (2000) Heterogeneity and statistical significance in meta-analysis: an empirical study of 125 meta-analyses. Stat Med 19:1707–1728

Faraut J, Korányi A (1994) Analysis on Symmetric Cones. Oxford University Press

Feller W (1952) The parabolic differential equations and the associated semi-groups of transformations. Ann Math 55:468–519

Fodor JC, Yager RR, Rybalov A (1997) Structure of uninorms. Int J Uncertain Fuzziness Knowl-Based Syst 5:411–427

Foertsch T, Karlsson A (2005) Hilbert metrics and Minkowski norms. J Geom 83:22–31

Friedman Y (2005) Physical Applications of Homogeneous Balls. Birkhäuser, Boston

Giust R, Vigoureux J-M, Lages J (2009) Generalized composition law from 2×2 matrices. Am J Phys 77:1068–1073

Good IJ (1950) Probability and the Weighing of Evidence. Griffin, London

Greco WR, Bravo G, Parsons JC (1995) The search for synergy: a critical review from a response surface perspective. Pharmacol Rev 47:331–385

Greenland S, Robins JM, Pearl J (1999) Confounding and collapsibility in causal inference. Stat Sci 14:29–46

Hájek P (1985) Combining functions for certainty degrees in consulting systems. Int J Man-Mach Stud 22:59–76

Haldane JBS (1924) A mathematical theory of natural and artificial selection, Part I. Trans Camb Phil Soc 23:19–41

Hamacher H (1978) Über logische Aggregationen nicht-binär explizierter Entscheidungskriterien. Rita G. Fischer Verlag, Frankfurt

Hardy GH, Littlewood JE, Pólya G (1934) Inequalities. Cambridge University Press

de la Harpe P (1993) On Hilbert's metric for simplices. In: Niblo GA, Roller MA (eds) Geometric Group Theory, Vol 1. London Math Soc Lecture Note Ser 181, Cambridge University Press, pp 97–119

Heckerman D (1986) Probabilistic interpretations for MYCIN's certainty factors. In: Kanal LN, Lemmer JF (eds) Uncertainty in Artificial Intelligence. North-Holland, Amsterdam, pp 167–196

Helgason S (1978) Differential Geometry, Lie Groups, and Symmetric Spaces. Academic Press, New York

Holbeck SL, Camalier R, Crowell JA, et al (2017) The National Cancer Institute ALMANAC: a comprehensive screening resource for the detection of anticancer drug pairs with enhanced therapeutic activity. Cancer Res 77:3564–3576

Hölder O (1901) Die Axiome der Quantität und die Lehre vom Mass. Ber Verh Sächs Ges Wiss Leipzig, Math-Phys Cl 53:1–64

Hübner M (1992) Explicit computation of the Bures distance for density matrices. Phys Lett A 163:239–242

Ianevski A, Giri AK, Gautam P, Kononov A, Potdar S, Saarela J, Wennerberg K, Aittokallio T (2019) Prediction of drug combination effects with a minimal set of experiments. Nat Mach Intell 1:568–577

Ignatowski W von (1910) Einige allgemeine Bemerkungen zum Relativitätsprinzip. Phys Z 11:972–976

Kay DC (1967) The ptolemaic inequality in Hilbert geometries. Pacific J Math 21:293–301

Kimura M (1962) On the probability of fixation of mutant genes in a population. Genetics 47:713–719

Kimura M, Ohta T (1969) The average number of generations until fixation of a mutant gene in a finite population. Genetics 61:763–771

Klement EP, Mesiar R, Pap E (2000) Triangular Norms. Kluwer, Dordrecht

Klimovskaia A, Lopez-Paz D, Bottou L, Nickel M (2020) Poincaré maps for analyzing complex hierarchies in single-cell data. Nat Commun 11:2966

Kolmogorov AN (1930) Sur la notion de la moyenne. Atti Accad Naz Lincei Rend 12:388–391

Krantz DH, Luce RD, Suppes P, Tversky A (1971) Foundations of Measurement, Vol I: Additive and Polynomial Representations. Academic Press, New York

Krioukov D, Papadopoulos F, Kitsak M, Vahdat A, Boguñá M (2010) Hyperbolic geometry of complex networks. Phys Rev E 82:036106

Øksendal B (2003) Stochastic Differential Equations, 6th edn. Springer, Berlin

Kuramoto Y (1984) Chemical Oscillations, Waves, and Turbulence. Springer, Berlin

Lévy-Leblond J-M (1976) One more derivation of the Lorentz transformation. Am J Phys 44:271–277

Lichnerowicz A (1958) Géométrie des groupes de transformations. Dunod, Paris

Lindley DV (1985) Making Decisions, 2nd edn. Wiley, London

Ling C-H (1965) Representation of associative functions. Publ Math Debrecen 12:189–212

Littman ML, Sutton RS, Singh S (2002) Predictive representations of state. Adv Neural Inf Process Syst 14:1555–1561

Luce RD, Marley AAJ (1969) Extensive measurement when concatenation is restricted and maximal elements may exist. In: Morgenbesser S, Suppes P, White M (eds) Philosophy, Science, and Method: Essays in Honor of Ernest Nagel. St Martin's Press, New York, pp 235–249

Luce RD, Narens L (1976) A qualitative equivalent to the relativistic addition law for velocities. Synthese 33:483–487

Masanes L, Oppenheim J (2017) A general derivation and quantification of the third law of thermodynamics. Nat Commun 8:14538

McKean HP (1970) An upper bound to the spectrum of Δ on a manifold of negative curvature. J Differential Geom 4:359–366

Meyer CT, Wooten DJ, Paudel BB, et al (2019) Quantifying drug combination synergy along potency and efficacy axes. Cell Syst 8:97–108

Mocanu CI (1986) Some difficulties within the framework of relativistic electrodynamics. Arch Elektrotech 69:97–110

Montgomery D, Zippin L (1955) Topological Transformation Groups. Interscience, New York

Monzón JJ, Yonte T, Sánchez-Soto LL, Cariñena JF (2002) Geometrical setting for the classification of multilayers. J Opt Soc Am A 19:985–991

Murray DJ (2026a) The Observer and the World: predictive closure, the projective shadow, and a first-principles grammar of empirical science. SSRN 7347861

Murray DJ (2026aa) A coefficient-locked test of atmospheric-loss geometry in the exoplanet radius valley. SSRN 6858878

Murray DJ (2026ab) c-Ring stoichiometry, energetic slack, and the limits of molecular optimality. SSRN 6858880

Murray DJ (2026b) The five Möbius composition laws on the bounded interval. SSRN 6754362

Murray DJ (2026c) Hormesis as a geometric necessity of bounded adaptive systems: quantitative predictions from first principles. Dose-Response. doi:10.1177/15593258261469171 (preprint SSRN 6858819)

Murray DJ (2026d) Bounded composition forces interior existence: a self-contained theorem. SSRN 6773218

Murray DJ (2026e) Bounded compositional geometry: interior-identity universality and the one-dimensional Möbius enrichment. SSRN 6800400

Murray DJ (2026f) A classification of bounded composition laws with isometric reassociation defects: flat rapidity addition, Einstein gyroaddition, and the holonomy that chooses between them. SSRN 6914800

Murray DJ (2026g) Lawful coordinates in bounded science: measurement, composition, and the Euclidean error. SSRN 6963978

Murray DJ (2026h) Predictive closure: a measurement-admission theorem for evolving systems. SSRN 7304339; revised as Predictive closure: state, action, and the experimental compression of history, SSRN 7427098

Murray DJ (2026i) A law of biological state sufficiency: history-conditioned prediction, viable continuation, and a test for when the past may be forgotten. SSRN 7425878

Murray DJ (2026j) A dynamical model of glutathione homeostasis in G6PD deficiency and NRF2-activated non-small cell lung cancer. Redox Biochem Chem 17:100084. doi:10.1016/j.rbc.2026.100084 (related preprint SSRN 6754498)

Murray DJ (2026k) IDA and the Boundedness Engine: a typed-residue research programme for bounded domains, return geometry, and awareness-gated control. SSRN 6987278

Murray DJ (2026l) Finite rescue windows and supply-limited redox commitment in NRF2-active cancer: fold geometry and a discriminating experimental test. SSRN 7427059 (supersedes SSRN 7181465)

Murray DJ (2026m) The Observer and the World: predictive state, lawful forgetting, and the geometry of empirical reality. SSRN 7426998 (reviewed revision in the same series as Murray 2026a)

Murray DJ (2026n) The acute dose-response curve as a transition potential: predictive-state closure, quadratic degeneracy, and temporal identifiability. SSRN 7426880

Murray DJ (2026o) The temporal architecture of living nature: predictive state, robust viability, and the recursive construction of biological futures. SSRN 7426938

Murray DJ (2026p) When equal BED is not equal biology: reversal, graph closure, and state recovery. SSRN 7427058 (earlier version SSRN 7302362)

Murray DJ (2026q) From predictive state to viable action: action sufficiency, safe diagnosis, and the operational recoverability bound. SSRN 7427100

Murray DJ (2026r) Bounded reflection and Möbius composition: a first-principles derivation. SSRN 6767896

Murray DJ (2026s) Bounded composition and deformed kinematics: an axiomatic route to hyperbolic momentum space. SSRN 6756063

Murray DJ (2026t) A universal composition law for bounded pharmacological observables: the Aczél-family structure of dose-response, combination effects, and aluminium toxicology. SSRN 6739201

Murray DJ (2026u) Rapidity coordinates for bounded belief: a resource-constrained predictive processing framework with a falsifiable inter-brain synchrony test. SSRN 6774878

Murray DJ (2026v) A plant–sensor–controller–surveillance architecture for bounded adaptive homeostasis: four threshold-typed failure modes, with the redox/NRF2 system as exemplar. SSRN 6754360

Murray DJ (2026w) Response-coefficient attenuation predicts hormetic peak amplitude: a metabolic-control extension of bounded adaptive systems. SSRN 6858760

Murray DJ (2026x) Dominance hides in the bend: boundary identifiability and sampling design in diploid selection. SSRN 6963958

Murray DJ (2026y) Projection geometry of the niche–neutral debate: hidden probability currents in community dynamics. SSRN 6963360

Murray DJ (2026z) Aczél-family composition in bounded pharmacology: mechanism-selected generators, combination effects, and an aluminium-toxicology test. SSRN 7426978

Nagumo M (1930) Über eine Klasse der Mittelwerte. Japan J Math 7:71–79

Nerode A (1958) Linear automaton transformations. Proc Amer Math Soc 9:541–544

O'Neill B (1983) Semi-Riemannian Geometry, with Applications to Relativity. Academic Press, New York

Osgood WF (1898) Beweis der Existenz einer Lösung der Differentialgleichung dy/dx = f(x,y) ohne Hinzunahme der Cauchy–Lipschitz'schen Bedingung. Monatsh Math Phys 9:331–345

Penrose R (1959) The apparent shape of a relativistically moving sphere. Proc Camb Phil Soc 55:137–139

Pikovsky A, Rosenblum M, Kurths J (2001) Synchronization: A Universal Concept in Nonlinear Sciences. Cambridge University Press

Piotrowski EW, Łuczka J (2007) The relativistic velocity addition law optimizes a forecast gambler's profit. arXiv:0709.4137

Pontryagin L (1939) Topological Groups. Princeton University Press

Poole C, Shrier I, VanderWeele TJ (2015) Is the risk difference really a more heterogeneous measure? Epidemiology 26:714–718

Prencipe N, Garcin V, Provenzi E (2020) Origins of hyperbolicity in color perception. J Imaging 6:42

Ratcliffe JG (2006) Foundations of Hyperbolic Manifolds, 2nd edn. Springer, New York

Resnikoff HL (1974) Differential geometry and color perception. J Math Biol 1:97–131

Sarkar R (2012) Low distortion Delaunay embedding of trees in hyperbolic plane. In: Graph Drawing 2011, Lecture Notes in Comput Sci 7034, Springer, pp 355–366

Shalizi CR, Crutchfield JP (2001) Computational mechanics: pattern and prediction, structure and simplicity. J Stat Phys 104:817–879

Terrell J (1959) Invisibility of the Lorentz contraction. Phys Rev 116:1041–1045

Thomas LH (1926) The motion of the spinning electron. Nature 117:514

Twarog NR, Stewart E, Hammill CV, Shelat AA (2016) BRAID: a unifying paradigm for the analysis of combined drug action. Sci Rep 6:25523

Ungar AA (1989) The relativistic velocity composition paradox and the Thomas rotation. Found Phys 19:1385–1396

Ungar AA (2008) Analytic Hyperbolic Geometry and Albert Einstein's Special Theory of Relativity. World Scientific, Singapore

Varićak V (1910) Anwendung der Lobatschefskijschen Geometrie in der Relativtheorie. Phys Z 11:93–96

Vigoureux J-M (1992) Use of the Einstein addition law in studies of reflection by stratified planar structures. J Opt Soc Am A 9:1313–1319

Wainwright MJ, Jordan MI (2008) Graphical models, exponential families, and variational inference. Found Trends Mach Learn 1:1–305

Wang L (2022) On the homogeneity of measures for binary associations. arXiv:2210.05179

Weinberg S (1996) The Quantum Theory of Fields, Vol II. Cambridge University Press

White T, Noble D, Senior A, Hamilton WK, Viechtbauer W (2026) metadat: Meta-analysis datasets. R package, https://CRAN.R-project.org/package=metadat (data accessed September 2026)

Wildberger NJ (2013) Universal hyperbolic geometry I: trigonometry. Geom Dedicata 163:215–274

Yaglom IM (1979) A Simple Non-Euclidean Geometry and Its Physical Basis. Springer, New York

Yilmaz H (1962) On color perception. Bull Math Biophys 24:5–29

Zagidullin B, Aldahdooh J, Zheng S, et al (2019) DrugComb: an integrative cancer drug combination data portal. Nucleic Acids Res 47:W43–W51

Zhang H, Maloney LT (2012) Ubiquitous log odds: a common representation of probability and frequency distortion in perception, action, and cognition. Front Neurosci 6:1

Zhang H, Rich PD, Lee AK, Sharpee TO (2023) Hippocampal spatial representations exhibit a hyperbolic geometry that expands with experience. Nat Neurosci 26:131–139

Zhao Y, Slate EH, Xu C, Chu H, Lin L (2022) Empirical comparisons of heterogeneity magnitudes of the risk difference, relative risk, and odds ratio. Syst Rev 11:26

Zhou Y, Smith BH, Sharpee TO (2018) Hyperbolic geometry of the olfactory space. Sci Adv 4:eaaq1458

Zwanzig R, Szabo A, Bagchi B (1992) Levinthal's paradox. Proc Natl Acad Sci USA 89:20–22
