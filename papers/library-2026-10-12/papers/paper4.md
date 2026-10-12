---
title: "Two Observers"
subtitle: "Complex composition purification and the dynamics of retained records"
author: "Daniel John Murray"
orcid: "0009-0005-1794-5945"
affiliation: "Independent researcher, Melbourne, Australia"
date: "12 October 2026"
version: "Working v3.1"
abstract: |
  We study two complex binary record systems under an explicitly specified tensor-product composition. Local tomography gives sixteen real readings, and the fifteen nonconstant generators contain entangling motions. A pure joint amplitude supplies exact determinant, concurrence, Schmidt and steering identities. Its right purification fiber and left determinant-preserving stabilizer recover the algebraic massive little group, while physical spin and proper time require separate identifications. We construct maximum-entropy forgetting for a complete retained observable algebra, distinguish it from canonical typicality, and prove a clock-invariant full-rank bound for finite-dimensional time-local GKSL evolution. A Busemann barycenter gives a nonlinear projection of angular probability onto harmonic measures, with a finite-entropy condition for its KL interpretation. Independently sampled non-elementary filters have conditional boundary and geodesic-tracking results; isotropic steps yield an exact escape-rate formula. These results close the declared composition and dynamics models without identifying every mixed environment with entanglement, every observer path with a geodesic, or equilibrium state selection with a unique physical generator.
keywords:
  - quantum composition
  - local tomography
  - purification
  - concurrence
  - quantum steering
  - conditional expectation
  - Lindblad evolution
  - hyperbolic random walk
---

# 1 Composition as an operational premise

A single binary complex record has state cone $\operatorname{Herm}_2(\mathbb C)_+$ and density $\rho=(I+\mathbf b\cdot\sigma)/2$. Its intrinsic order metric is hyperbolic. This metric differs from the Fubini–Study metric on pure amplitudes and the Bures metric used for quantum statistical distinguishability. Choosing a metric for an action or experiment remains part of that experiment.

For two such systems we specify the standard complex tensor product

$$\mathcal H_{AB}=\mathbb C^2\otimes\mathbb C^2,\qquad
\rho_{AB}\succeq0,\qquad \operatorname{Tr}\rho_{AB}=1,$$

with product effects, partial traces and completely positive local operations. Local tomography means that product effects separate joint states. It is true for this composition, but is not implied by the two local cones alone.

For instance a cone $\operatorname{Herm}_4(\mathbb C)_+\oplus\operatorname{Herm}_4(\mathbb C)_+$ can retain an extra global label. Product effects act on the sum of its components and local filters act identically on both. States $(\rho,0)$ and $(0,\rho)$ have equal product readings but a global effect distinguishes their labels. This is a countermodel to inference from local record rules alone; it fails an additional global simple-block classification.

**Proposition 1.** The standard complex two-binary composite is locally tomographic, with sixteen real readings and fifteen nonconstant Hermitian generators.

**Proof.** The matrices $I,\sigma_x,\sigma_y,\sigma_z$ span each local Hermitian space. Their sixteen tensor products span $\operatorname{Herm}_4(\mathbb C)$. Positive local effects span the same local spaces, so their products separate the joint density. Removing the identity leaves fifteen directions; commutators $i[X,\cdot]$ give $\mathfrak{su}(4)$. $\square$

If a globally classified complex system additionally has independent product preparations and local tomography for two binary parts, its dimension is sixteen and its abstract Jordan algebra is $\operatorname{Herm}_4(\mathbb C)$. The actual product embedding and accessible operations must still be specified. General Jordan composite constructions have their own assumptions [1].

The Lie identity $\mathfrak{su}(4)\cong\mathfrak{so}(6)$ is compatible with this result. The six-dimensional real representation is the Hodge-real form of $\Lambda^2\mathbb C^4$; the entire complex exterior power has twelve real dimensions. Under the local subgroup it splits as $3+3$. The algebra contains entangling motions:

$$e^{-i\theta X\otimes X}|00\rangle
=\cos\theta|00\rangle-i\sin\theta|11\rangle.$$

Availability of such a generator does not select an actual Hamiltonian or coupling.

# 2 The pure joint amplitude

Write a nonzero joint vector as $|\Psi\rangle=\sum_{ij}\Psi_{ij}|i\rangle|j\rangle$, using its $2\times2$ coefficient matrix. Set

$$P=\Psi\Psi^\dagger=\tfrac12(EI+\mathbf p\cdot\sigma),\qquad
E=\operatorname{Tr}P,\qquad \mathbf b=\mathbf p/E.$$

The raw amplitude can have arbitrary nonzero norm; the physical normalized pure density divides by $E$.

**Theorem 2.** If $\lambda_+\ge\lambda_-\ge0$ are the eigenvalues of $P$, then

$$m=2|\det\Psi|=\sqrt{E^2-|\mathbf p|^2},\qquad
C=\frac mE,\qquad C^2+|\mathbf b|^2=1.$$

For $\lambda_->0$,

$$R=\tfrac12\log(\lambda_+/\lambda_-)
=\operatorname{artanh}|\mathbf b|,\qquad C=\operatorname{sech}R.$$

The normalized pure-state concurrence is $C$; $m$ is the raw determinant invariant.

**Proof.** $\det P=|\det\Psi|^2=\lambda_+\lambda_-$ and $\operatorname{Tr}P=\lambda_++\lambda_-$. Pauli eigenvalues give $|\mathbf p|=\lambda_+-\lambda_-$. These identities give the formulas. The pure-state concurrence equals twice the product of normalized Schmidt amplitudes, namely $2\sqrt{\lambda_+\lambda_-}/E$ [2]. $\square$

Rank-one $P$ is a product joint amplitude and is null in the record cone. At equal Schmidt weights it is maximally entangled and has $\mathbf b=0$. These are exact representation identities.

With an additional calibration identifying $P$ as a timelike physical four-momentum, in units $c=1$ the cone invariant $m$ is its rest energy and $C=m/E=1/\gamma$. Restoring units gives $C=m_{\mathrm{phys}}c^2/E_{\mathrm{phys}}$. This does not show that all physical particle masses originate in entanglement: the polarization of a photon can be entangled while its physical momentum stays null.

Determinant-one left filtering gives $P\mapsto APA^\dagger$ and preserves the raw $m$. Normalized concurrence generally changes because $E$ changes. A physically selected Kraus filter may be $sA$ rather than its determinant-one representative; the success scale also rescales the raw determinant. Projective Lorentz comparison and an actual selected quantum operation must retain these different amounts.

# 3 Fibers little groups and steering

**Proposition 3.** For invertible $\Psi$, its amplitudes with the same raw $P$ are exactly $\Psi V$, $V\in U(2)$. Fixing the determinant phase restricts this fiber to $SU(2)$. Quotienting arbitrary global scalar phases instead gives $PU(2)\cong SO(3)$. The determinant-one left stabilizer is

$$G_P=\Psi SU(2)\Psi^{-1}.$$

**Proof.** $\Psi V(\Psi V)^\dagger=P$ iff $VV^\dagger=I$. Determinant-one $g$ stabilizes $P$ iff $V=\Psi^{-1}g\Psi$ is unitary with determinant one. The scalar-phase quotient of $U(2)$ is $PU(2)$; its spin cover is $SU(2)$. $\square$

This produces the spin-cover form of the massive momentum little group. A physical particle's spin is a choice of representation of that group, not the mere existence of its purification fiber. Spin-zero and higher-spin particles have the same massive orbit [3]. A partner unitary can preserve a marginal while changing joint correlations; marginal unreadability is not automatically a global gauge redundancy.

**Theorem 4.** A selected partner Kraus operation $M$ sends $\Psi$ to $\Psi M^T$. If its effect is $F=M^\dagger M$, its unnormalized conditional record is

$$P_F=\Psi F^T\Psi^\dagger.$$

For $\Psi=P^{1/2}U$,

$$P_F=P^{1/2}(UF^TU^\dagger)P^{1/2},\qquad
\det P_F=|\det\Psi|^2\det F.$$

Unconditional trace-preserving partner operations leave $P$ unchanged.

**Proof.** Acting on the second tensor index transposes $M$. Multiplication by its adjoint gives $(M^\dagger M)^T$. The polar factorization gives the congruence formula and the determinant factors. For outcomes $M_j$ with $\sum_jM_j^\dagger M_j=I$, summing $P_{F_j}$ gives $P$. $\square$

The conditional probability is $\operatorname{Tr}P_F/E$. When both $P$ and $F$ are strictly positive, their determinant-normalized forms express canonical hyperbolic boost composition. Rank-deficient $F$ can produce a pure conditional output. The map $F\mapsto\Psi F^T\Psi^\dagger$ is an effect-to-state steering map; interpreting its transposed input as an ordinary arbitrary state channel would incorrectly assume complete positivity.

Every density matrix has a purification: diagonalize $\rho=\sum_j\lambda_j|v_j\rangle\langle v_j|$ and use $\sum_j\sqrt{\lambda_j}|v_j\rangle|j\rangle$. Existence of this representation does not imply that an actual environment is pure.

Similarly a finite CPTP map has Kraus form $\Phi(\rho)=\sum_jK_j\rho K_j^\dagger$, with $\sum_jK_j^\dagger K_j=I$. Its isometry $V|\psi\rangle=\sum_jK_j|\psi\rangle|j\rangle$ extends to a unitary on a sufficiently large environment, proving the finite dilation [4]. Positivity alone is insufficient: transpose applied to one factor of a Bell state has a negative eigenvalue.

# 4 Forgetting and actual records

The depolarizing semigroup in an additive activity parameter $u\ge0$ is

$$\rho_u=e^{-u}\rho_0+(1-e^{-u})I/2.$$

It gives $|\mathbf b_u|=e^{-u}|\mathbf b_0|$. The concurrence of a chosen pure purification is therefore $\sqrt{1-|\mathbf b_u|^2}$, increasing toward one.

This pure-whole interpretation is conditional. The same channel has a mixed-register implementation: use Pauli probabilities $(1+3e^{-u})/4$ for $I$ and $(1-e^{-u})/4$ for each of $X,Y,Z$, and a classical register controlling these unitaries. The actual joint output is a separable mixture $\sum_jp_j\sigma_j\rho_0\sigma_j\otimes|j\rangle\langle j|$. Forgetting need not create entanglement with that actual register.

Writing a correlation also differs from increasing marginal purity. CNOT on a system $I/2$ and memory $\operatorname{diag}(0.8,0.2)$ gives joint eigenvalues $(0.4,0.1,0.1,0.4)$ and two maximally mixed marginals. Its mutual information is $\log2-H(0.8,0.2)>0$. A full-rank correlation record is written by a unitary without reaching a state boundary.

For a CPTP map fixing reference $\sigma$, relative entropy obeys

$$D(\Phi\rho\Vert\sigma)\le D(\rho\Vert\sigma),$$

by data processing [5]. With $\sigma=I/d$ and a unital channel, entropy cannot decrease. This precise H-theorem neither selects a bath nor proves convergence under every spectrum-preserving or charge-conserving dynamics.

# 5 A complete retained-algebra selector

**Theorem 5.** Let $\mathcal A\subset M_d(\mathbb C)$ be a specified unital *-subalgebra and $E_{\mathcal A}$ its trace-preserving conditional expectation. Then

$$\mathcal T_u=e^{-u}\operatorname{id}+(1-e^{-u})E_{\mathcal A}$$

is a CPTP semigroup preserving all $\mathcal A$ readings and converging to
$\rho_*=E_{\mathcal A}\rho_0$. This output is the unique maximum-entropy state with the same complete retained readings.

**Proof.** A Haar twirl over the unitary group of the commutant realizes $E_{\mathcal A}$, so it is unital, trace preserving, completely positive and idempotent. Its idempotence proves the semigroup law. For every compatible $\sigma$, $\log\rho_*$ lies in $\mathcal A$ on its support and has the same expectation under $\sigma$ and $\rho_*$. Hence

$$D(\sigma\Vert\rho_*)=S(\rho_*)-S(\sigma)\ge0.$$

If $\rho_*$ is singular, its kernel projector lies in $\mathcal A$ and the retained readings force $\sigma$ onto the same support. Equality of relative entropy holds only at $\sigma=\rho_*$. $\square$

This is a physical quantum-channel construction after specifying which algebra is retained. It does not select that algebra or its kinetic rate. The fixed-point structure of quantum semigroups provides the wider setting [6].

Maximum entropy at only a few mean values is not generally realizable by one fixed linear selector on every preparation. For $Q=\operatorname{diag}(0,1,2)$, means zero and two force the endpoint pure states. Linearity sends their equal mixture to $\operatorname{diag}(1/2,0,1/2)$, whereas the maximum-entropy state at mean one is $I/3$. Thus a universal mean-only Gibbs selector needs additional control, preparation restrictions or a distinct limiting model.

Even the same unique equilibrium $I/2$ admits Pauli generators with different positive rates. Their Bloch decay rates are $2(\gamma_y+\gamma_z)$, $2(\gamma_x+\gamma_z)$ and $2(\gamma_x+\gamma_y)$. The rate ratios are not fixed by the equilibrium or a common clock calibration. A framework may specify these generators, but entropy selection alone does not derive them.

# 6 Canonical typicality

Canonical typicality supplies a different conditional result. Let $R\subset\mathcal H_S\otimes\mathcal H_B$ be a finite constrained subspace, $d_R=\dim R$, and draw a unit vector uniformly from $R$. Its reference marginal is

$$\Omega_S=\operatorname{Tr}_B(\Pi_R/d_R),\qquad
d_B^{\mathrm{eff}}=1/\operatorname{Tr}\Omega_B^2.$$

The trace-distance mean is bounded by

$$\mathbb E\|\rho_S-\Omega_S\|_1
\le\sqrt{d_S/d_B^{\mathrm{eff}}}.$$

Haar's second moment gives

$$\mathbb E\operatorname{Tr}\rho_S^2
=d_R(\operatorname{Tr}\Omega_S^2+\operatorname{Tr}\Omega_B^2)/(d_R+1).$$

Subtracting $\operatorname{Tr}\Omega_S^2$, then using
$\|A\|_1\le\sqrt{d_S}\|A\|_2$ and Jensen's inequality, proves the bound. Concentration on the sphere gives exponentially small tails in $d_R$ at fixed excess tolerance [7].

This is an ensemble statement with explicit dimension conditions. It does not establish that an arbitrary evolution samples Haar states. Gibbs form additionally uses weak coupling and a large bath whose density of states has approximately linear logarithm across the system's energy range. Exact finite-bath state-count ratios need not be exact Boltzmann factors.

# 7 A clock-invariant interior theorem

**Theorem 6.** For a well-defined finite-dimensional time-local GKSL evolution [8],

$$\dot\rho=-i[H,\rho]+\sum_kL_k\rho L_k^\dagger-\tfrac12\{G,\rho\},
\qquad G=\sum_kL_k^\dagger L_k,$$

let $\rho_0\succ0$, $p_0=\lambda_{\min}\rho_0$, and

$$\Xi(T)=\int_0^T\|G(t)\|_{\mathrm{op}}dt<\infty.$$

Then

$$\lambda_{\min}\rho(T)\ge p_0e^{-\Xi(T)}.$$

For a qubit the determinant-normalized radial rapidity therefore obeys

$$R(T)\le\tfrac12\log\frac{1-p_0e^{-\Xi(T)}}{p_0e^{-\Xi(T)}}.$$

**Proof.** The no-jump propagator satisfies
$\dot K=(-iH-G/2)K$. Variation of constants writes $\rho(T)$ as $K\rho_0K^\dagger$ plus an integral of positive jump sources, so $\rho(T)\succeq K\rho_0K^\dagger$. For every vector $v$,

$$\frac d{dt}\|Kv\|^2=-\langle Kv,GKv\rangle
\ge-\|G\|_{\mathrm{op}}\|Kv\|^2.$$

Integration bounds the smallest singular value squared of $K$ by $e^{-\Xi}$. Since $\rho_0\succeq p_0I$, the eigenvalue bound follows. For a qubit $R=\tfrac12\log[(1-p_{\min})/p_{\min}]$, which decreases with $p_{\min}$. $\square$

The bound is sharp: amplitude damping with a diagonal initial state whose smaller population is excited gives $p_{\min}(T)=p_0e^{-\Xi(T)}$. Under a differentiable clock change $t=t(s)$ with $t'>0$, set $H_s=t'H_t$ and $L_{k,s}=\sqrt{t'}L_{k,t}$. Then $G_s=t'G_t$ and $\Xi$ is unchanged. This requires a specified jump representation, or a fixed canonical traceless representation; scalar shifts of jumps can change $\Xi$ for the same channel.

Finite integrated activity forbids a full-rank boundary arrival in this model. Finite parameter time alone does not. A pure bath coupled by bounded excitation exchange gives excited population $p_0\cos^2(gt)$ and reaches a pure output at $t=\pi/(2g)$. Its local amplitude-damping rate $2g\tan(gt)$ has divergent integrated activity there. This is compatible with the theorem and illustrates why all finite-time physics cannot be inferred from a regular local GKSL bound.

# 8 Angular records and nonlinear projection

The sky of hyperbolic record space carries harmonic measures
$dh_x/d\sigma=e^{-2B_\xi(x)}$, with $\sigma$ the uniform center probability. An arbitrary angular probability $\mu$ retains more information than an additive Bloch mean.

**Theorem 7.** If $\mu$ has no atom of mass at least one-half, its potential

$$F_\mu(x)=\int B_\xi(x)\,d\mu(\xi)$$

has a unique minimizer $\beta(\mu)\in\mathbb H^3$, equivariant under Lorentz sky transformations. If additionally $D(\mu\Vert\sigma)<\infty$, it is the unique finite KL projection onto the harmonic family:

$$D(\mu\Vert h_x)=D(\mu\Vert\sigma)+2F_\mu(x).$$

**Proof.** The Hessian is $\int(g_H-dB_\xi\otimes dB_\xi)d\mu$. It is strictly positive: degeneracy on a tangent would require support on the two ends of one geodesic, forcing an atom of at least one-half.

The no-heavy-atom condition also gives a uniformly positive escape coefficient. Compactness of the sky supplies sufficiently small caps with mass uniformly below one-half. Outside a cap about a ray endpoint, $B_\xi(x)\ge d(o,x)-C$; inside it, $B_\xi(x)\ge-d(o,x)$. Thus $F_\mu(x)\to\infty$ as $d(o,x)\to\infty$. Properness and strict convexity prove existence and uniqueness. The Busemann transformation changes the potential only by an $x$-independent term, proving equivariance. The density formula proves the KL identity under the finite-entropy assumption. $\square$

This is a conformal-barycenter construction related to conformally natural extensions [9]. Absolute continuity alone is insufficient for a finite KL projection. For example with $u=(1-\cos\theta)/2$ uniform on $[0,1]$, density $1/[u\log^2(1/u)]$ on $0<u<e^{-1}$ has unit integral but infinite relative entropy. Every finite-frame harmonic density has bounded log density, so every candidate KL value is infinite.

The barycenter differs from the additive raw-record summary. For $\mu=(1+a\cos\theta)\sigma$, the additive Bloch mean is $a/3$ while barycenter rapidity is $a/2+O(a^3)$. It also differs from a bolometric Landau frame. The nonlinear projection is a specified summary operation, not an identity of all these records.

# 9 Random filters and geodesic tracking

Choose independently and identically distributed $g_j\in SL(2,\mathbb C)$ with
$\mathbb E\,d(o,g_jo)<\infty$. Let their generated action be non-elementary: unbounded and preserving no finite boundary set. Put

$$G_n=g_n\cdots g_1,\qquad
P_n=G_nG_n^\dagger,\qquad R_n=G_n^\dagger G_n.$$

The physical filtered output from equilibrium is $P_n/\operatorname{Tr}P_n$. The accumulated dual record is $R_n/\operatorname{Tr}R_n$. They have identical eigenvalues but different directional evolution. The dual hyperbolic point is the right random walk $G_n^\dagger o$.

Under these hypotheses, the classical random-product and hyperbolic ergodic theorems give positive escape, boundary convergence and a geodesic ray tracked to $o(n)$ distance [10,11]. Finite first moment means integrable, not bounded, steps. This is a specified stochastic model, not a theorem that all physical evidence is independently sampled or all observers follow geodesics.

**Proposition 8.** For isotropic steps with radial rapidity $\rho$ and uniform direction conditional on $\rho$, the escape rate is

$$\ell=\mathbb E[\rho\coth\rho-1],$$

with continuous value zero at $\rho=0$.

**Proof.** Fix a deterministic sky direction $\xi$. The Busemann cocycle increments along the right walk have the same conditional law at each step, because the next isotropic direction is independent and its law is unchanged by the past-transformed $\xi$. Their common mean is

$$\frac12\int_{-1}^1\log(\cosh\rho+u\sinh\rho)\,du
=\rho\coth\rho-1.$$

The increments are identically distributed and independent in this conditional-law sense, and are bounded in magnitude by $\rho$. The law of large numbers applies. Isotropy makes the random limit direction uniform, so almost surely it differs from fixed $\xi$. If $x_n=(\cosh r_n,\sinh r_n\,\eta_n)$ converges directionally to that other endpoint, then
$r_n-B_\xi(x_n)\to-\log[(1-\eta_\infty\cdot\xi)/2]$.
Hence its radial escape equals the cocycle mean. $\square$

Toward the walk's own endpoint, the same sign convention gives
$B_{\xi_\infty}(x_n)/n\to-\ell$ by sublinear tracking. Its negative is an asymptotic event-count parameter, not necessarily a monotone exact clock or physical proper time.

Commuting filters do not characterize exact geodesics. The commuting parabolics
$N(s)=\left(\begin{smallmatrix}1&s\\0&1\end{smallmatrix}\right)$ trace a horocycle; at $s=0,1,2$ adjacent distances are $\operatorname{arcosh}(3/2)$ but endpoint distance is $\operatorname{arcosh}(3)$, strictly smaller than their sum. Conversely, the axis normalizer generated by
$B(r)=\operatorname{diag}(e^{r/2},e^{-r/2})$ and
$\epsilon=\left(\begin{smallmatrix}0&1\\-1&0\end{smallmatrix}\right)$ is noncommutative and preserves one geodesic. Right products $B(a)$, then $B(b)\epsilon$, then $B(-c)\epsilon$, with $a,b,c>0$, move its center to increasing coordinates $a,a+b,a+b+c$. Positive boosts along one fixed axis are a sufficient commuting geodesic construction.

# 10 Learning contraction and scope

For a positive linear map whose image has finite Hilbert projective diameter $\Delta$, the Birkhoff coefficient is at most $\tanh(\Delta/4)$ [12]. An invertible diagonal likelihood filter has infinite diameter and is a log-odds isometry. Strictly mixing matrices can have finite diameter and genuine contraction. This puts learning and forgetting in a common order calculus while distinguishing their mechanisms and resource requirements.

The framework closes the stated tensor-product, pure-amplitude and retained-algebra constructions. It also provides a sharp finite-activity boundary theorem and conditional stochastic tracking. Physical inertia, particle spin, bath dynamics, actual evidence laws and clock calibration are separately specified. Their identification with the common cone structure is meaningful when an operational bridge is supplied; it is not inferred merely from equal formulas.

## Acknowledgements

Claude and Codex were used for drafting, independent calculations and mathematical checking. Responsibility for the assumptions, proofs, citations and final scientific claims rests with the author.

## References

[1] H. Barnum, M. A. Graydon and A. Wilce, “Composites and Categories of Euclidean Jordan Algebras,” *Quantum* **4**, 359 (2020). [doi:10.22331/q-2020-11-08-359](https://doi.org/10.22331/q-2020-11-08-359).

[2] W. K. Wootters, “Entanglement of Formation of an Arbitrary State of Two Qubits,” *Physical Review Letters* **80**, 2245–2248 (1998). [doi:10.1103/PhysRevLett.80.2245](https://doi.org/10.1103/PhysRevLett.80.2245).

[3] E. P. Wigner, “On Unitary Representations of the Inhomogeneous Lorentz Group,” *Annals of Mathematics* **40**, 149–204 (1939). [doi:10.2307/1968551](https://doi.org/10.2307/1968551).

[4] W. F. Stinespring, “Positive Functions on C$^*$-algebras,” *Proceedings of the American Mathematical Society* **6**, 211–216 (1955). [doi:10.1090/S0002-9939-1955-0069403-4](https://doi.org/10.1090/S0002-9939-1955-0069403-4).

[5] G. Lindblad, “Completely Positive Maps and Entropy Inequalities,” *Communications in Mathematical Physics* **40**, 147–151 (1975). [doi:10.1007/BF01609396](https://doi.org/10.1007/BF01609396).

[6] B. Baumgartner and H. Narnhofer, “Analysis of quantum semigroups with GKS–Lindblad generators II. General,” *Journal of Physics A* **41**, 395303 (2008). [arXiv:0806.3164](https://arxiv.org/abs/0806.3164).

[7] S. Popescu, A. J. Short and A. Winter, “Entanglement and the foundations of statistical mechanics,” *Nature Physics* **2**, 754–758 (2006). [doi:10.1038/nphys444](https://doi.org/10.1038/nphys444); [arXiv:quant-ph/0511225](https://arxiv.org/abs/quant-ph/0511225).

[8] G. Lindblad, “On the Generators of Quantum Dynamical Semigroups,” *Communications in Mathematical Physics* **48**, 119–130 (1976). [doi:10.1007/BF01608499](https://doi.org/10.1007/BF01608499).

[9] A. Douady and C. J. Earle, “Conformally natural extension of homeomorphisms of the circle,” *Acta Mathematica* **157**, 23–48 (1986). [doi:10.1007/BF02392590](https://doi.org/10.1007/BF02392590).

[10] H. Furstenberg, “Noncommuting random products,” *Transactions of the American Mathematical Society* **108**, 377–428 (1963); V. A. Kaimanovich, “The Poisson formula for groups with hyperbolic properties,” *Annals of Mathematics* **152**, 659–692 (2000). [arXiv:math/9802132](https://arxiv.org/abs/math/9802132).

[11] A. Karlsson and G. A. Margulis, “A Multiplicative Ergodic Theorem and Nonpositively Curved Spaces,” *Communications in Mathematical Physics* **208**, 107–123 (1999). [doi:10.1007/s002200050750](https://doi.org/10.1007/s002200050750).

[12] G. Birkhoff, “Extensions of Jentzsch's Theorem,” *Transactions of the American Mathematical Society* **85**, 219–227 (1957). [doi:10.2307/1992971](https://doi.org/10.2307/1992971).
