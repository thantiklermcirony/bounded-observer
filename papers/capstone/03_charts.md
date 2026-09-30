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

