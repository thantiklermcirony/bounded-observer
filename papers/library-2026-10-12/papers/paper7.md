---
title: "Gravity as Equilibrium"
subtitle: "Stationary record geometry, conditional horizon dynamics and cosmological identities"
author: "Daniel John Murray"
orcid: "0009-0005-1794-5945"
affiliation: "Melbourne, Australia"
date: "12 October 2026"
version: "Working version 3.1"
abstract: |
  Hyperbolic geometry enters gravity through two distinct constructions. On a timelike Killing patch, the stationary vacuum Einstein equations reduce to a hyperbolic Ernst map coupled to a three-dimensional quotient metric. We state that reduction, distinguish the stationary ergosurface from the event horizon, and give the precise conditions of an imported smooth-completion theorem. Photon exchange between normalized orbits of the same Killing field has an exact Busemann redshift expression. Separately, area entropy, Unruh temperature, local horizon equilibrium, the all-horizon Clausius relation and stress-tensor conservation imply Einstein's equation by Jacobson's argument. The entropy coefficient and cosmological constant remain physical inputs. Locality and bounded cells alone do not establish the required area entropy. A declared effective-theory non-collapse condition yields a density ceiling; in flat positive-Λ cosmology the future-event-horizon ratio lies below that scale and reaches equality in the de Sitter limit. These are identities and conditional bounds, not a prediction of the vacuum density. We distinguish a possible emergent-metric interpretation from a microscopic quantum-gravity theory and specify the variables, constitutive laws and initial-value requirements needed for a non-equilibrium extension.
keywords: "Ernst equation; hyperbolic geometry; local horizon thermodynamics; entanglement entropy; cosmological constant; non-equilibrium gravity"
---

# 1. Two routes and their premises

The positive cone of a binary complex record has a Lorentz symmetry and a hyperbolic projective interior. Gravity contains related geometries, but the occurrence of the same geometry is not by itself a derivation of physical gravitational dynamics.

We separate two routes. The stationary route begins with the vacuum Einstein equations and reduces them along a Killing symmetry. It identifies an exact classical hyperbolic target. The thermodynamic route begins with a Lorentzian spacetime, a specified horizon entropy and local equilibrium conditions. It derives Einstein's equation as a compatibility condition. The first assumes the field equation; the second assumes independent physical horizon premises.

This distinction allows both constructions to be complete at their supported strength. Record geometry organizes the variables and their transformations. The classical reduction and the physical thermodynamic hypotheses supply the bridges to gravity.

Throughout the local derivations the metric has signature $(-,+,+,+)$ and $c=k_B=1$, with $\hbar$ displayed. Entropy $s=S/k_B$ is dimensionless and uses natural logarithms. Constants are restored where the physical normalization matters.

# 2. The coupled stationary vacuum reduction

Assume a smooth four-dimensional vacuum spacetime, $R_{ab}(g)=0$, with a Killing vector $\xi$. On a connected patch where $\xi$ is timelike define $f=-g(\xi,\xi)>0$. The twist one-form is closed in vacuum, so a local potential $\psi$ can be chosen. In adapted coordinates,

\[
g=-f(dt+\omega)^2+f^{-1}h_{ij}dx^i dx^j,
\qquad \xi=\partial_t.
\]

Here $h$ is a Riemannian metric on the quotient, while $f$, $\omega$ and $\psi$ are independent of $t$.

**Imported reduction theorem (Ernst–Geroch).** With the conventional twist normalization, the vacuum equations on this patch are equivalent to the field equations of

\[
I[h,f,\psi]=\int\sqrt h\left[
R(h)-\frac{|Df|_h^2+|D\psi|_h^2}{2f^2}\right]d^3x,
\tag{2.1}
\]

up to the common action normalization and boundary terms [1,2]. Thus $\mathcal E=f+i\psi$ is a harmonic map into the hyperbolic half-plane with metric

\[
g_N=\frac{df^2+d\psi^2}{f^2},
\]

coupled to

\[
R_{ij}(h)=\frac{D_i fD_j f+D_i\psi D_j\psi}{2f^2}.
\tag{2.2}
\]

The equivalence with four-dimensional vacuum gravity is the imported part of the statement. We give the variational consequences to make the coupling and normalization explicit.

**Proposition 1 (equations of the reduced action).** Varying (2.1) gives (2.2) and

\[
\Delta_h f=\frac{|Df|^2-|D\psi|^2}{f},
\qquad \Delta_h\psi=\frac{2Df\cdot D\psi}{f},
\]

or equivalently

\[
f\Delta_h\mathcal E=D\mathcal E\cdot D\mathcal E.
\tag{2.3}
\]

*Proof.* Varying $\psi$ gives $D_i(f^{-2}D^i\psi)=0$. Variation in $f$ gives $f\Delta_h f=|Df|^2-|D\psi|^2$. Combining the real and imaginary equations gives (2.3).

Let $H_{ij}=f^{-2}(D_i fD_j f+D_i\psi D_j\psi)$ and $H=h^{ij}H_{ij}$. Variation in the inverse quotient metric yields

\[
G_{ij}(h)=\tfrac12H_{ij}-\tfrac14h_{ij}H.
\]

Its three-dimensional trace implies $R(h)=H/2$, which gives (2.2). The target Christoffel symbols, $\Gamma^f_{ff}=-1/f$, $\Gamma^f_{\psi\psi}=1/f$ and $\Gamma^\psi_{f\psi}=-1/f$, reproduce the same tension equations. $\square$

The target geometry therefore does not fix gravitational coupling independently of the action. Nor is generic $h$ the fixed flat source used in an uncoupled heat-flow theorem. In the stationary axisymmetric Weyl formulation the scalar equations can be expressed using an axisymmetric flat-space operator, with the remaining metric functions reconstructed separately. That special representation does not remove their gravitational constraints.

The chart fails at $f=0$. The target distance to that ideal boundary diverges; for example it bounds from below the absolute change of $\log f$. On a fixed-sign patch with a spacelike Killing vector the quotient changes causal type. Neither statement makes $f=0$ a regular finite point of the same timelike reduction.

# 3. Ergosurfaces, horizons and completion

In Kerr geometric units let $M>0$, $|a|<M$ and $\Sigma=r^2+a^2\cos^2\theta$. For the stationary Killing field normalized at infinity,

\[
f=1-\frac{2Mr}{\Sigma}.
\]

Its outer zero surface and the outer event horizon are

\[
r_{\rm ergo}(\theta)=M+\sqrt{M^2-a^2\cos^2\theta},
\qquad r_+=M+\sqrt{M^2-a^2}.
\]

They are distinct except where they meet at the poles, or in the nonrotating limit. For $M=1$, $a=0.8$, the equatorial stationary-limit radius is two, whereas $r_+=1.6$ and $f(r_+,\pi/2)=-0.25$.

In a stationary exterior decomposition,

\[
g_{tt}=-\alpha^2+\omega_{\mathrm{drag}}^2\varpi^2,
\qquad f=\alpha^2(1-v_K^2),
\qquad v_K=\omega_{\mathrm{drag}}\varpi/\alpha.
\]

Here $v_K$ is the formal speed of the constant-spatial-coordinate Killing orbit relative to zero-angular-momentum observers. At the ordinary ergosurface it reaches one. Inside, that orbit is spacelike and cannot represent a material observer. This is a statement about a failing observer chart, not a superluminal material velocity.

**Imported completion theorem.** Consider the stationary axisymmetric vacuum Ernst equations in Weyl coordinates, away from the rotation axis, at a zero of $f$. If the Ernst potential is smooth there and $f$ has no zero of infinite order, the reconstructed spacetime metric is smooth and Lorentzian in a neighborhood. This is Theorem 1.1 of Chruściel–Greuel–Meinel–Szybka [3]. It identifies the exact regularity and finite-order assumptions under which a singular-looking reduction has a smooth geometric completion.

The theorem concerns an off-axis ergosurface. It is not a theorem removing Kerr's ring singularity or every spacetime curvature singularity. In Schwarzschild, the stationary Killing field becomes null at the event horizon; regular horizon-penetrating coordinates complete that observer chart. The curvature invariant $48M^2/r^6$ nevertheless diverges at $r=0$.

# 4. Stationary redshift as a Busemann difference

Normalize the chosen timelike Killing field consistently at both endpoints. A Killing observer has four-velocity $u=\xi/\sqrt f$ in $c=1$ units.

**Theorem 2 (stationary photon redshift).** Let a photon propagate along a null geodesic with momentum $p$ from emission to reception, both by normalized orbits of the same timelike Killing field. Then

\[
\frac{\omega_{\rm rec}}{\omega_{\rm em}}
=\sqrt{\frac{f_{\rm em}}{f_{\rm rec}}}.
\]

For the hyperbolic Ernst half-plane, the Busemann function toward its ideal point at infinity can be normalized as $B_\infty=-\log f$. Therefore

\[
\log\frac{\omega_{\rm rec}}{\omega_{\rm em}}
=\frac12\left[B_\infty(\mathcal E_{\rm rec})
-B_\infty(\mathcal E_{\rm em})\right].
\tag{4.1}
\]

*Proof.* Along the geodesic,

\[
p^a\nabla_a(\xi_bp^b)
=p^ap^b\nabla_a\xi_b+\xi_bp^a\nabla_ap^b=0,
\]

by the Killing equation and geodesic equation. The conserved Killing energy is $\mathcal E_\gamma=-\xi\cdot p$. The measured energy is $-u\cdot p=\mathcal E_\gamma/\sqrt f$, giving the ratio.

The half-plane distance between $(\psi,f)$ and $(0,e^s)$ obeys

\[
\cosh d=\frac{\psi^2+f^2+e^{2s}}{2fe^s}.
\]

Consequently $d((\psi,f),(0,e^s))-s\to-\log f$ as $s\to\infty$, establishing the Busemann normalization and (4.1). $\square$

A constant rescaling of the Killing field shifts this Busemann coordinate by a constant and leaves the redshift difference unchanged. The identity holds with nonzero twist on the timelike patch. It assumes the metric and null-geodesic energy law; it does not derive the equivalence principle. The analogous Busemann form of Doppler redshift organizes a related geometry in velocity space without identifying the two target spaces physically.

Negative curvature also supports uniqueness comparisons. If two smooth harmonic maps share a compact connected Riemannian source with nonempty boundary and the same Dirichlet data in a complete simply connected nonpositively curved target, the squared target distance between them is subharmonic. Convexity on the product target and the harmonic equations give this claim, and the maximum principle gives equality of the maps. This is a comparison mechanism. Black-hole uniqueness additionally uses its stationary reduction, symmetry, horizon, asymptotic and boundary-data assumptions; Mazur's electrovacuum theorem is an example [4]. The comparison lemma alone is not the complete uniqueness proof for a coupled spacetime.

# 5. Wedge thermality and area entropy

## 5.1 A specified equilibrium state

**Imported wedge theorem.** Under the usual relativistic quantum-field hypotheses of the Bisognano–Wichmann theorem, the Minkowski vacuum restricted to a wedge is a KMS state for the boost flow, with dimensionless inverse boost temperature $2\pi$ [5]. A uniformly accelerated observer with proper acceleration $a$ parametrizes that boost by $a\tau/c$. The physical Unruh temperature is

\[
T_U=\frac{\hbar a}{2\pi c k_B}.
\]

This is a quantum-field statement with locality, spectrum, covariance and vacuum hypotheses. It is not supplied by a bounded readout or a filter alone. In continuum quantum field theory the wedge state is naturally described algebraically; a normalized finite-dimensional Gibbs density matrix needs a regulator or a finite model.

**Proposition 3 (entanglement first variation).** Let $\rho_0$ be a faithful finite-dimensional reference state and let $\rho_\varepsilon=\rho_0+\varepsilon\delta\rho$ be a differentiable normalized perturbation. With $K_0=-\log\rho_0$ fixed,

\[
s(\rho_\varepsilon)-s(\rho_0)
=\varepsilon\operatorname{Tr}(\delta\rho K_0)+O(\varepsilon^2).
\]

*Proof.* Differentiate $s(\rho)=-\operatorname{Tr}\rho\log\rho$. The derivative is $-\operatorname{Tr}\delta\rho(\log\rho_0+I)$. Normalization makes $\operatorname{Tr}\delta\rho=0$. $\square$

For a specified regulated Gibbs reference, $K_0$ is its inverse-temperature Hamiltonian plus a constant, giving the first-order energy–entropy relation. Interpreting that energy variation as heat across every curved-spacetime local horizon is an additional semiclassical and local-equilibrium premise.

## 5.2 Why the entropy premise is separate

Local interactions and finite-dimensional cells are consistent with area-law vacuum states, but they do not force every state to have area-law entropy. Let a region contain $N$ qubits, each paired in a Bell state with an outside qubit. Its entropy is $N\log2$. The cells are bounded, and this is a state of the local Hamiltonian $H=0$, but its entropy is extensive in the region's cell count.

This elementary counterexample does not deny an area law for a selected vacuum. It shows why selection of the state, its correlations and a spatial regulator must be stated. A bound on the readings of one cell does not specify a minimum cell size or a finite density of cells per unit area.

Srednicki's regulated free-field ground-state calculation supplies an important area-law example [6]. Jacobson's argument requires the stronger local relation $\delta s=\eta\delta A$ with one universal constant $\eta$. A microscopic entropy calculation, a cutoff prescription and gravitational renormalization must establish that relation if it is to be derived rather than assumed. They are not provided by locality alone.

# 6. Einstein's equation from all local horizons

**Theorem 4 (conditional local-horizon equation).** Assume:

1. A smooth four-dimensional Lorentzian spacetime, a conserved stress tensor $\nabla^aT_{ab}=0$, and the applicability of the null-congruence Raychaudhuri equation.
2. Through every event and every null direction, a local Rindler horizon pencil that is instantaneously in equilibrium: its expansion and shear vanish at the reference event.
3. A universal local entropy variation $\delta s=\eta\delta A$, with $\eta>0$ independent of the pencil.
4. The Unruh temperature $\Theta=\hbar\kappa/(2\pi)$ in energy units, and the reversible relation $\delta Q=\Theta\delta s$, with boost energy used consistently for both heat and temperature.
5. A thermodynamic regime in which stress-tensor fluctuations and higher-order horizon terms can be neglected at the order used below.

Then

\[
G_{ab}+\Lambda g_{ab}=8\pi G T_{ab},
\qquad G=\frac1{4\hbar\eta},
\tag{6.1}
\]

where $\Lambda$ is an undetermined constant. This is the local-horizon route of Jacobson [7].

*Proof.* Let $k^a$ be an affine null generator, with parameter $\lambda=0$ at the equilibrium event and $\lambda<0$ on the relevant past horizon segment. The approximate boost field is $\chi^a=-\kappa\lambda k^a$. Its energy flux is

\[
\delta Q=-\kappa\int\lambda T_{ab}k^ak^b\,d\lambda\,dA.
\]

Raychaudhuri gives

\[
\frac{d\theta}{d\lambda}
=-\frac12\theta^2-\sigma_{ab}\sigma^{ab}-R_{ab}k^ak^b.
\]

At the reference event $\theta=\sigma=0$. To leading order, $\theta=-\lambda R_{ab}k^ak^b$, so

\[
\delta A=-\int\lambda R_{ab}k^ak^b\,d\lambda\,dA.
\]

The entropy and temperature hypotheses yield, for every null direction,

\[
R_{ab}k^ak^b=\frac{2\pi}{\hbar\eta}T_{ab}k^ak^b.
\]

Write $C=2\pi/(\hbar\eta)$. A symmetric tensor whose contraction with every null vector vanishes is proportional to the metric. To see this in an orthonormal frame, put $k=(1,\mathbf n)$ with $|\mathbf n|=1$. Replacing $\mathbf n$ by $-\mathbf n$ eliminates the mixed components; a quadratic form constant on the unit sphere is a scalar identity. Hence $R_{ab}-CT_{ab}=F g_{ab}$.

The contracted Bianchi identity and stress conservation give $\nabla_bF=\frac12\nabla_bR$. Thus $F=R/2-\Lambda$ on a connected region, and $G_{ab}+\Lambda g_{ab}=CT_{ab}$. Identifying $C=8\pi G$ proves (6.1). $\square$

Restoring constants, when $s=S/k_B$ is measured in nats,

\[
G=\frac{c^3}{4\hbar\eta},\qquad
G_{ab}+\Lambda g_{ab}=\frac{8\pi G}{c^4}T_{ab}.
\]

The theorem determines the form of the equation under these premises. It does not determine the entropy coefficient or the cosmological constant, prove the premise that all the horizon pencils are in the required quantum equilibrium, or construct a microscopic gravitational theory.

Jacobson's later fixed-volume small-ball entanglement-equilibrium argument is another conditional route [8]. Its precise first-order conformal-field result and its additional nonconformal-matter assumption should be kept distinct from the horizon-pencil hypotheses above.

# 7. A density scale and its cosmological limit

## 7.1 A declared effective-theory non-collapse condition

**Proposition 5 (spherical density scale).** For a specified effective-theory region of radius $L$, impose the non-collapse condition

\[
E\leq\frac{c^4L}{2G}
\]

and use its spherical volume $V=4\pi L^3/3$. Its mean positive energy density then satisfies

\[
\rho\leq\rho_{\rm cap}(L)=\frac{3c^4}{8\pi GL^2}.
\]

*Proof.* Divide the imposed energy inequality by $V$. $\square$

This is the scale restriction associated with the Cohen–Kaplan–Nelson effective-theory proposal [9]. A region can form a black hole; the inequality is not a universal consequence of finite record composition. Cosmological energy is also not automatically the Schwarzschild mass of an asymptotically flat sphere. Choosing a cosmological radius $L$ for this effective density condition is additional model content.

With $\ell_P^2=\hbar G/c^3$ and Planck energy density $\rho_P=c^7/(\hbar G^2)$,

\[
\frac{\rho_P}{\rho_{\rm cap}(L)}
=\frac{8\pi}{3}\left(\frac L{\ell_P}\right)^2.
\]

This explains the large scale ratio within the imposed comparison. It does not derive radiative cancellations or select the renormalized cosmological vacuum density.

## 7.2 An exact flat-cosmology theorem

Let the source now be a spatially flat FLRW cosmology with positive $\Lambda$, nonnegative matter and radiation terms, and

\[
H(a)^2=H_\Lambda^2+C_m a^{-3}+C_r a^{-4},
\qquad H_\Lambda^2=\frac{\Lambda c^2}{3},
\qquad C_m,C_r\geq0.
\]

Its proper future-event-horizon radius is

\[
L(a)=ca\int_a^\infty\frac{da'}{a'^2H(a')}.
\]

**Theorem 6 (event-horizon density ratio).** At every $a>0$,

\[
\frac c{H(a)}\leq L(a)\leq\frac c{H_\Lambda},
\]

and

\[
q(a):=\frac{\rho_\Lambda}{\rho_{\rm cap}(L(a))}
=\frac{H_\Lambda^2L(a)^2}{c^2}\leq1.
\]

The ratio is non-decreasing and tends to one as $a\to\infty$.

*Proof.* $H(a')\geq H_\Lambda$ bounds the integral above by $1/(aH_\Lambda)$. Since $H$ is non-increasing, $H(a')\leq H(a)$ for $a'\geq a$, which gives the lower bound. Differentiating $L=a c\int_t^\infty dt'/a(t')$ gives $\dot L=HL-c\geq0$, proving monotonicity. Finally $H(a)\to H_\Lambda$, so the two bounds squeeze $L$ to $c/H_\Lambda$. The ratio uses $\rho_\Lambda=\Lambda c^4/(8\pi G)=3c^2H_\Lambda^2/(8\pi G)$. $\square$

If matter or radiation is nonzero, the upper inequality is strict at finite scale factor. Pure de Sitter saturates it throughout. This theorem is an identity within the assumed cosmology, independent of a new saturation law or a forgetting dynamics.

**Corollary 7 (asymptotic entropy capacity).** Define

\[
N=\frac{\pi L_\infty^2}{\ell_P^2},\qquad
L_\infty=\frac c{H_\Lambda}.
\]

Then

\[
\frac{\rho_\Lambda}{\rho_P}=\frac3{8N}.
\]

*Proof.* Substitute $L_\infty=c/H_\Lambda$ and $\ell_P^2=\hbar G/c^3$ into $N$, and use the displayed density formulas. $\square$

With the Einstein area-entropy normalization, $N$ is the horizon entropy in nats. It is not the number of microscopic states, which would be exponential in entropy in a finite state-count interpretation. The relation rewrites the supplied $\Lambda$; it does not predict $N$.

## 7.3 A separately reported saturation test

An additional hypothesis sets the dark-energy density equal to $\rho_{\rm cap}(L)$ at every epoch, with $L$ the future event horizon. This is Li's holographic dark-energy model with its saturation parameter $c_h=1$ [10]. The parameter $c_h$ is distinct from the speed of light.

A separate registered analysis in the research record [T20] reports the following comparison with flat $\Lambda$CDM:

| Reported likelihood | $\Delta\chi^2=\chi^2_{c_h=1}-\chi^2_{\Lambda\mathrm{CDM}}$ | Analysis status and interpretation |
|---|---:|---|
| DESI DR2 BAO plus Pantheon+ supernovae | $-3.37$ | Preregistered primary test: neutral under its $\pm4$ threshold |
| Addition of Planck distance priors | $+117.46$ | Exploratory extension: saturation disfavoured in the stated combined likelihood |

The exploratory late-time profile reported $c_h=0.98$ with a 68% interval of 0.92–1.07. CMB information was expressly excluded from the preregistered decisive test. Its later extension disfavors the stronger saturation hypothesis under the stated combined likelihood and leaves the primary registered verdict neutral. These figures are reported outcomes of the specified pipeline, not consequences of Theorem 6. Their reproduction requires the released covariance data, likelihood definition, matching conventions and the applicability of the compressed CMB likelihood to the compared model [11–13].

For its reported flat-$\Lambda$CDM fit, $q$ is about 0.91 today. This is a normalized density ratio. It is not an established fraction of elapsed cosmological history or of thermodynamic equilibration. The theorem retains asymptotic equality without selecting the failed all-epoch saturation law.

# 8. Quantum and non-equilibrium extensions

An emergent interpretation may regard the metric as a collective equilibrium reading of quantum records. The local-horizon theorem neither requires nor excludes that interpretation. It does not decide whether a microscopic metric operator is fundamental, and it does not calculate effective quantum metric correlations.

Jacobson's sound analogy motivates caution about treating an equation of state as a fundamental canonical equation [7]. It is a proposal, not a no-quantization theorem. Collective excitations can have a quantum effective description even if their variables are not microscopic. Low-energy gravitational effective-field calculations explicitly contain calculable quantum fluctuations without claiming an ultraviolet completion [14].

## 8.1 Equilibrium does not select response

**Proposition 8 (same equilibrium, different dynamics).** In frequency units for $H$, each equation

\[
\dot\rho=-i[H,\rho]+\Gamma(\tfrac12I-\rho),\qquad\Gamma>0,
\]

has the same unique equilibrium $\rho_*=I/2$, while its decay time depends on $\Gamma$.

*Proof.* The solution is

\[
\rho(t)=\tfrac12I+e^{-\Gamma t}e^{-iHt}
(\rho_0-\tfrac12I)e^{iHt}.
\]

It is a convex mixture of a unitary image of $\rho_0$ and $I/2$, hence a valid quantum channel, and converges uniquely to $I/2$. Different $\Gamma$ give different response times at a fixed clock. $\square$

Likewise a horizon entropy at equilibrium does not select a relaxation coefficient, causal response kernel or noise correlation. A statement that the record space is quantum leaves its Hamiltonian, environment and geometry readout to be specified.

**Proposition 9 (identical vacuum family, different effective curvature response).** Choose the additional action

\[
I_\alpha=\frac1{16\pi G}\int\sqrt{-g}(R+\alpha R^2)d^4x+I_m,
\]

with $\alpha$ of dimension length squared. Its equation is

\[
(1+2\alpha R)R_{ab}-\tfrac12(R+\alpha R^2)g_{ab}
+2\alpha(g_{ab}\Box-\nabla_a\nabla_b)R=8\pi GT_{ab}.
\]

Every Ricci-flat vacuum Einstein metric solves it for every $\alpha$. Its trace is

\[
6\alpha\Box R-R=8\pi GT.
\]

For $\alpha>0$, linearized vacuum curvature obeys a scalar equation with mass squared $1/(6\alpha)$.

*Proof.* Varying the action and integrating the derivative terms in $\delta R$ by parts gives the displayed tensor equation. Its trace cancels the $R^2$ algebraic terms and leaves $6\alpha\Box R-R$. At $R_{ab}=0$ every added term vanishes. Linearizing the trace about such a vacuum gives $(\Box-1/(6\alpha))\delta R=0$. $\square$

This is a constructive underdetermination example, not an adoption of the added action. It need not obey the exact area-only hypotheses of Theorem 4 outside its equilibrium regime; curvature-dependent entropy is new content. An identical Ricci-flat vacuum family therefore cannot select all extensions or their fluctuation spectra.

## 8.2 A definite research specification

Non-equilibrium horizon thermodynamics can be defined by an entropy balance

\[
ds=\delta Q/\Theta+d_is,
\]

but the balance is not closed until $d_is$ and the retained variables are defined. Eling–Guedens–Jacobson give a specific curvature-dependent entropy and entropy-production construction, including shear production in Einstein gravity [15]. Its constitutive additions are essential. Classical entropy production is not synonymous with every quantum correction.

For a gravitational record extension, the following constitute a definite model specification:

1. The microscopic or effective state variables, their evolution, the conserved stress operator and the reading/coarse-graining map that yields geometry and entropy.
2. The entropy functional, production law and causal constitutive response, with fluctuation correlations if retained. A positivity inequality restricts coefficients but does not determine every kernel.
3. The full coupled evolution, gauge, constraints, compatible initial and boundary data and function spaces. A well-posed regime requires existence, uniqueness, continuous dependence and constraint preservation.
4. The equilibrium limit of Theorem 4 with its calibrated $\eta$, together with a calculable response or fluctuation observable and an established low-energy match or testable departure.

These requirements locate the next problem without asserting that it has already been solved. The equilibrium theorem is a complete conditional result. Its microscopic and non-equilibrium extensions remain model-construction and analysis tasks.

# 9. Position within an operational framework

The gravitational branch contains an imported stationary reduction, an imported patch-completion theorem, a stationary redshift identity, a conditional local-horizon equation, an independently imposed effective density bound and exact flat-cosmology identities. Their premises are named where each result is stated.

The operational framework is complete within these premises. Its physical metric, entropy law, state selection and response dynamics require the specified bridges. Further work must derive or test those bridges and extensions. This manuscript was prepared with AI-assisted drafting and mathematical checks.

# References

[1] F. J. Ernst, “New formulation of the axially symmetric gravitational field problem,” *Physical Review* **167**, 1175–1178 (1968). [doi:10.1103/PhysRev.167.1175](https://doi.org/10.1103/PhysRev.167.1175).

[2] R. Geroch, “A method for generating solutions of Einstein's equations,” *Journal of Mathematical Physics* **12**, 918–924 (1971). [doi:10.1063/1.1665681](https://doi.org/10.1063/1.1665681).

[3] P. T. Chruściel, G.-M. Greuel, R. Meinel and S. J. Szybka, “The Ernst equation and ergosurfaces,” *Classical and Quantum Gravity* **23**, 4399–4414 (2006). [arXiv:gr-qc/0603041](https://arxiv.org/abs/gr-qc/0603041).

[4] P. O. Mazur, “Proof of uniqueness of the Kerr–Newman black hole solution,” *Journal of Physics A: Mathematical and General* **15**, 3173–3180 (1982). [doi:10.1088/0305-4470/15/10/021](https://doi.org/10.1088/0305-4470/15/10/021).

[5] J. J. Bisognano and E. H. Wichmann, “On the duality condition for quantum fields,” *Journal of Mathematical Physics* **17**, 303–321 (1976). [doi:10.1063/1.522898](https://doi.org/10.1063/1.522898).

[6] M. Srednicki, “Entropy and area,” *Physical Review Letters* **71**, 666–669 (1993). [arXiv:hep-th/9303048](https://arxiv.org/abs/hep-th/9303048).

[7] T. Jacobson, “Thermodynamics of spacetime: the Einstein equation of state,” *Physical Review Letters* **75**, 1260–1263 (1995). [arXiv:gr-qc/9504004](https://arxiv.org/abs/gr-qc/9504004).

[8] T. Jacobson, “Entanglement equilibrium and the Einstein equation,” *Physical Review Letters* **116**, 201101 (2016). [arXiv:1505.04753](https://arxiv.org/abs/1505.04753).

[9] A. G. Cohen, D. B. Kaplan and A. E. Nelson, “Effective field theory, black holes, and the cosmological constant,” *Physical Review Letters* **82**, 4971–4974 (1999). [arXiv:hep-th/9803132](https://arxiv.org/abs/hep-th/9803132).

[10] M. Li, “A model of holographic dark energy,” *Physics Letters B* **603**, 1–5 (2004). [arXiv:hep-th/0403127](https://arxiv.org/abs/hep-th/0403127).

[11] DESI Collaboration, “DESI DR2 results II: measurements of baryon acoustic oscillations and cosmological constraints” (2025). [arXiv:2503.14738](https://arxiv.org/abs/2503.14738).

[12] D. Brout et al., “The Pantheon+ analysis: cosmological constraints,” *The Astrophysical Journal* **938**, 110 (2022). [arXiv:2202.04077](https://arxiv.org/abs/2202.04077).

[13] L. Chen, Q.-G. Huang and K. Wang, “Distance priors from Planck final release,” *Journal of Cosmology and Astroparticle Physics* **2019**(02), 028 (2019). [arXiv:1808.05724](https://arxiv.org/abs/1808.05724).

[14] J. F. Donoghue, “General relativity as an effective field theory: the leading quantum corrections,” *Physical Review D* **50**, 3874–3888 (1994). [arXiv:gr-qc/9405057](https://arxiv.org/abs/gr-qc/9405057).

[15] C. Eling, R. Guedens and T. Jacobson, “Non-equilibrium thermodynamics of spacetime,” *Physical Review Letters* **96**, 121301 (2006). [arXiv:gr-qc/0602001](https://arxiv.org/abs/gr-qc/0602001).

[T20] D. J. Murray, “Dark energy and the horizon ceiling,” registered analysis and research dossier, 12 October 2026, including the T20 protocol, validation and likelihood outputs. Unpublished research record accompanying the series.
