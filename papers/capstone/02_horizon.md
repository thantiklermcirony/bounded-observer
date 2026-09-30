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

