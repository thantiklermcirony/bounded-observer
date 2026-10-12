---
title: "Where Singularities Can Live"
subtitle: "Conditional field theorems for bounded records"
author: "Daniel John Murray"
orcid: "0009-0005-1794-5945"
affiliation: "Melbourne, Australia"
date: "12 October 2026"
version: "Working version 3.1"
abstract: |
  A bounded record space supports several inequivalent field geometries and evolution equations. We identify the hypotheses under which its hyperbolic interior and its mixed-qubit hemisphere admit global harmonic-map heat flow. For a fixed closed flat source, hyperbolic heat flow has non-increasing maximum target radius and energy density. A weighted maximum principle proves global regularity for smooth qubit heat-flow data with a strictly positive mixedness margin in the Bures hemisphere. A Bernstein estimate also controls pressure-free self-transport. On two-dimensional sources, sphere-valued heat flow can instead concentrate harmonic spheres; the bubble energy is determined by the normalization of the target metric. We give explicit mixing and attenuation constructions, distinguish their energy and topology statements from claims about arbitrary physical dynamics, and state the precise imported wave-map and equivariant Schrödinger-map results. An optional incompressible Klein-velocity model has a uniquely specified elliptic pressure closure while its global regularity remains conjectural. These results give the singularity hypothesis a conditional mathematical meaning without extending it to all field equations or to spacetime curvature singularities.
keywords: "bounded records; harmonic-map heat flow; Bures metric; bubbling; hyperbolic geometry; incompressible flow"
---

# 1. Geometry, dynamics and the question of singularity

A bounded readout need not have bounded derivatives. A field may stay in a compact set while its gradients concentrate. The relevant question is therefore not only where the values of a record lie, but which metric and evolution control their spatial variation.

For a binary complex record write

\[
\rho=\frac12(I+\mathbf b\cdot\boldsymbol\sigma),\qquad |\mathbf b|\leq1.
\]

The filter geometry of its interior is hyperbolic. The standard Bures geometry is a round open hemisphere. Their common underlying Bloch ball does not make their metrics interchangeable. Pure records lie at infinite distance in the first geometry and at finite distance in the second. A field theory must choose a source, a target metric, an equation and initial data before a regularity assertion has a definite meaning.

We use energy

\[
E[u]=\frac12\int_M|du|_g^2\,dV_M
\]

for a Riemannian target $(N,g)$. Its tension field is $\tau(u)$, and its heat flow is $u_t=\nu\tau(u)$ with $\nu>0$. Unless a theorem states otherwise, the source is a fixed closed flat manifold and the initial map is smooth. Results for a disk require boundary data; results on Minkowski space have their own energy and function-space hypotheses.

The name singularity hypothesis, or SIH, will refer here to the following model-dependent pattern: some constrained pure-target equations admit concentration, while specified interior-target or regularized equations avoid it. The paper proves that pattern in particular systems. It does not infer that every singularity in physics is a pure-record defect.

# 2. The invariant quadratic energy

## 2.1 Hyperbolic target invariance

**Theorem 1 (quadratic friction classification).** Let $M$ have dimension $n$, with its specified isotropic spatial metric. Let $N=\mathbb H^m$ with $m\geq2$. Suppose a nonnegative dissipation is local, quadratic in first spatial derivatives, invariant under all target isometries and under independent source tangent orthogonal transformations, with the same constitutive law at every source point. Then it has the form

\[
D[u]=\kappa\int_M |du|_{\mathbb H^m}^2\,dV_M,
\qquad \kappa\geq0.
\]

Strictly positive dissipation requires $\kappa>0$.

*Proof.* Target transitivity reduces the derivative tensor to its value at one target point $o$. Its stabilizer is $O(m)$. On the source and target tangent factors, the only invariant two-index tensor under the respective full orthogonal group is the metric. Invariance under their independent product group therefore leaves only the tensor product of these metrics. Transport by target isometries and the common source constitutive law give the same coefficient $\kappa$ everywhere. Nonnegativity determines its sign. $\square$

Allowing the constitutive law to vary with the source point instead permits a nonnegative coefficient $\kappa(x)$. The full orthogonal hypotheses also exclude orientation-dependent quadratic terms in two dimensions.

In polar coordinates about $o$,

\[
g_{\mathbb H^m}=dr^2+\sinh^2r\,d\Omega^2.
\]

Consequently radial and angular variations have different weights:

\[
|du|^2=|\nabla r|^2+\sinh^2r\,|\nabla\xi|^2.
\]

Two nearby directions at radius $r$ have infinitesimal separation $\sinh r\,d\theta$. A flat radial chart instead assigns $r\,d\theta$. Choosing between those energies is a constitutive choice unless the invariance hypotheses of Theorem 1 are imposed.

## 2.2 Other Lorentz orbits

Consider the connected Lorentz group acting on a single four-vector orbit, with ambient signature $(-,+,+,+)$. An invariant quadratic target energy corresponds to a stabilizer-invariant symmetric form on the orbit tangent space.

| Record orbit | Stabilizer | Nonzero invariant tangent form, up to scale |
|---|---|---|
| Unit future timelike vectors | $SO(3)$ | Positive hyperbolic form |
| Nonzero future null vectors | $ISO(2)$ | Degenerate form of rank two |
| Null directions without intensity | A parabolic stabilizer | No nonzero form |
| Unit spacelike vectors | $SO^+(1,2)$ | Indefinite Lorentzian form |

**Proposition 2 (orbit forms).** The forms in the table exhaust invariant symmetric tangent forms in this four-dimensional setting.

*Proof.* At a timelike vector the tangent representation is the standard orthogonal representation of $SO(3)$. At a spacelike vector it is the standard Lorentz representation of $SO^+(1,2)$. Each has a one-dimensional space of invariant symmetric forms, with the stated signature.

At a null vector $k$, the tangent space is $k^\perp$. A null rotation acts on a transverse vector by $e\mapsto e+ak$ while fixing $k$. Invariance of $B(e+ak,e+ak)$ for all $a$ forces $B(e,k)=B(k,k)=0$. The null direction is therefore in the radical. On the two-dimensional transverse quotient, rotational invariance leaves a scalar Euclidean form. In coordinates $k=I(1,\mathbf n)$, with $I>0$ and $|\mathbf n|=1$, the induced form is

\[
\langle dk,dk\rangle=I^2|d\mathbf n|^2.
\]

On the sky of null directions, the stabilizer also contains a boost that dilates the tangent plane at its fixed direction. Invariance under a dilation of arbitrary factor forces every quadratic form there to vanish. $\square$

This classifies the stated quadratic energies. It does not classify models with an additional medium velocity, other fields, higher derivatives or different functionals. Moreover, invariance under a Lorentz group acting on the target is different from Lorentz covariance of spacetime evolution. A spatial heat equation selects an evolution time and is parabolic even when its target has Lorentz isometries.

# 3. Hyperbolic heat flow

**Theorem 3 (global hyperbolic heat flow).** Let $M$ be a closed flat manifold of any dimension, $u_0:M\to\mathbb H^m$ smooth and $\nu>0$. The heat equation

\[
u_t=\nu\tau(u),\qquad u(0)=u_0,
\]

has a unique smooth solution for all $t\geq0$. For each fixed $o\in\mathbb H^m$,

\[
\sup_Md(u(t),o)\leq\sup_Md(u_0,o),\qquad
\sup_M|du(t)|^2\leq\sup_M|du_0|^2.
\]

*Proof.* Set $L=\partial_t-\nu\Delta$, $\varrho=d(\cdot,o)^2$ and $e=|du|^2/2$. Hyperbolic space has no cut locus. Writing $r=d(\cdot,o)$,

\[
\operatorname{Hess}\varrho
=2\,dr\otimes dr+2r\coth r\,(g-dr\otimes dr)\geq2g,
\]

with the smooth limiting value at $r=0$. The composition rule for heat flow gives

\[
L(\varrho\circ u)
=-\nu\sum_i\operatorname{Hess}\varrho(du(e_i),du(e_i))
\leq-2\nu|du|^2=-4\nu e.
\]

The scalar maximum principle proves the radius bound.

The Bochner identity is

\[
Le=-\nu|\nabla du|^2
-\nu\langle du(\operatorname{Ric}_M\cdot),du\rangle
+\nu\sum_{i,j}K_N(du(e_i),du(e_j))
|du(e_i)\wedge du(e_j)|^2.
\]

The source Ricci tensor vanishes and target sectional curvature is $-1$. Thus $Le\leq0$, and the second maximum principle gives the gradient bound.

The image stays in a compact target ball and its first derivative remains bounded. The standard local theory and continuation criterion for harmonic-map heat flow then give bounds for higher derivatives on every finite time interval and exclude a finite maximal existence time. Uniqueness is part of that parabolic local theory [1,2]. $\square$

For a general closed source with $\operatorname{Ric}_M\geq-Kg_M$, the radius argument is unchanged and the Bochner estimate gives $\sup e(t)\leq e^{2\nu Kt}\sup e(0)$. Gradient monotonicity requires the appropriate Ricci sign. A boundary-value problem needs boundary compatibility and gradient estimates and is not covered merely by replacing the closed source by a disk.

# 4. Pressure-free self-transport

In this section use dimensionless velocity units with limiting speed one, and let $u:\mathbb T^3\to\mathbb H^3$. Its Klein readout $v$ lies in $B^3$. The hyperbolic metric in these coordinates is

\[
g_v=\frac{I}{1-|v|^2}+\frac{vv^T}{(1-|v|^2)^2}.
\]

It dominates the Euclidean metric, so $|dv|_{\rm Euclidean}\leq|du|_{\mathbb H^3}$.

**Theorem 4 (transport estimate).** Let $u_0$ be smooth and $\nu>0$. For

\[
u_t+(v\cdot\nabla)u=\nu\tau(u),
\]

set $R_0=\sup d(u_0,o)$, $K=7R_0^2+1$, $e=|du|^2/2$ and $\varrho=d(u,o)^2$. Then the solution is global and smooth, and

\[
\sup d(u(t),o)\leq R_0,
\]

\[
\sup e(t)\leq\frac1K\max\left\{
\sup(\varrho_0+K)e_0,
\frac{2(R_0^2+K)^3}{\nu^2}\right\}.
\]

*Proof.* Let $L=\partial_t+v\cdot\nabla-\nu\Delta$. Advection changes neither the sign of the radius maximum-principle argument nor its convexity term:

\[
L\varrho\leq-4\nu e.
\]

Differentiation of the advected equation adds a term controlled by $|\nabla v||du|^2$. Consequently

\[
Le\leq-\nu|\nabla du|^2+(2e)^{3/2}.
\]

For $\Phi=(\varrho+K)e$, use

\[
|\nabla e|\leq\sqrt{2e}|\nabla du|,
\qquad |\nabla\varrho|\leq2\sqrt\varrho\sqrt{2e}.
\]

Young's inequality yields

\[
-2\nu\nabla\varrho\cdot\nabla e
\leq\nu(\varrho+K)|\nabla du|^2
+\frac{16\nu\varrho}{\varrho+K}e^2.
\]

Since $\varrho\leq R_0^2$ and $K\geq7\varrho$, the coefficient $16\varrho/(\varrho+K)$ is at most two. The product rule therefore gives

\[
L\Phi\leq(\varrho+K)(2e)^{3/2}-2\nu e^2.
\]

Its right side is nonpositive when $e\geq2(R_0^2+K)^2/\nu^2$. In particular it is nonpositive whenever $\Phi\geq2(R_0^2+K)^3/\nu^2$. The maximum principle for $\Phi$ gives the asserted bound, since $\varrho+K\geq K$. Compact image, bounded first derivatives and parabolic continuation finish the proof. $\square$

The gradient need not be monotone in this transport problem. The theorem proves a uniform bound. It contains no pressure or arbitrary forcing term.

# 5. Mixed-qubit heat flow in Bures geometry

The standard Bures line element for a qubit is [3]

\[
ds_B^2=\frac14\left(d\mathbf b^2+
\frac{(\mathbf b\cdot d\mathbf b)^2}{1-|\mathbf b|^2}\right).
\]

Put $q=\sqrt{1-|\mathbf b|^2}$ and $U=(\mathbf b,q)\in S^3$. Then $q>0$ for a strictly mixed state and

\[
ds_B^2=\frac14(d\mathbf b^2+dq^2).
\]

The target is the open round hemisphere of radius $1/2$. Constant scaling of a target metric changes energy normalization but not its connection or heat equation.

**Theorem 5 (strict-mixedness regularity).** On a closed flat source, let smooth initial data satisfy $q_0\geq\delta>0$. Their Bures harmonic-map heat flow is smooth for all time. The minimum of $q$ is non-decreasing, and, using the unit-sphere embedding energy density $e=|dU|^2/2$,

\[
\sup_M\frac{e(t)}{q(t)^2}\leq
\sup_M\frac{e_0}{q_0^2}.
\]

In particular $\sup e(t)\leq\sup(e_0/q_0^2)$.

*Proof.* Rescale time to take $\nu=1$. The sphere heat equation is

\[
U_t=\Delta U+|dU|^2U.
\]

Writing $L=\partial_t-\Delta$, its height satisfies $Lq=2eq\geq0$. The minimum principle gives $q\geq\delta$ as long as the smooth solution exists.

The Bochner identity for a unit-sphere target implies

\[
Le\leq-|\nabla dU|^2+4e^2.
\]

Indeed the sphere curvature term is bounded by $|dU|^4=4e^2$. Set $w=e/q^2$. At a positive spatial maximum of $w$,

\[
\nabla e=\frac{2e}{q}\nabla q,
\qquad
|\nabla dU|^2\geq\frac{|\nabla e|^2}{2e}
=\frac{2e}{q^2}|\nabla q|^2.
\]

The product rule, $Lq^{-2}=-4eq^{-2}-6q^{-4}|\nabla q|^2$, and the maximum-point identity give

\[
Lw\leq-\frac{|\nabla dU|^2}{q^2}
+\frac{2e}{q^4}|\nabla q|^2\leq0.
\]

The maximum principle proves the weighted estimate. If its initial maximum is zero, the solution is spatially constant and the result is immediate. Since $q\leq1$, the estimate also bounds $e$. The image remains in a compact subhemisphere. Parabolic continuation proves global smoothness. $\square$

This proof is valid in every spatial dimension. It does not depend on extending a two-dimensional bubbling criterion to higher dimensions. Since $q=1/\cosh r$ when $r=\operatorname{artanh}|\mathbf b|$, the height and rapidity bounds both say that maximum purity does not increase, although they arise from different chosen metrics.

For completeness, neither target admits a nonconstant harmonic sphere. For hyperbolic space, integrate the convex squared-distance identity on $S^2$. In the open hemisphere, a harmonic map has $\Delta q=-|dU|^2q$. Its integral is zero; positivity of $q$ forces $dU=0$. These facts explain the target contrast, while the actual regularity theorem above uses its explicit estimate.

# 6. Surface bubbles and metric normalization

**Proposition 6 (surface degree bound).** For a smooth map $n:\Sigma\to S^2$ from a closed oriented Riemannian surface to the unit round sphere,

\[
E[n]\geq4\pi|\deg n|.
\]

Equality holds exactly for holomorphic or antiholomorphic maps, including a constant map in degree zero, with the compatible conformal structures.

*Proof.* For an oriented orthonormal pair on the source, the arithmetic–geometric mean inequality gives

\[
\tfrac12(|dn(e_1)|^2+|dn(e_2)|^2)
\geq|\omega_{S^2}(dn(e_1),dn(e_2))|.
\]

Integrating and using $\int_\Sigma n^*\omega_{S^2}=4\pi\deg n$ proves the bound. Equality requires equal-length orthogonal derivative vectors and a consistent orientation: this is the weakly conformal holomorphic or antiholomorphic condition. $\square$

**Imported surface-flow theorem.** Smooth sphere-valued harmonic-map heat flow in two spatial dimensions can develop finite-time singularities. Chang–Ding–Ye supply such data for the corotational disk problem [4]. In the standard surface-flow setting of Struwe and the sphere-target energy identity, a singularity has rescaled nonconstant harmonic-sphere bubbles, and its lost energy is the sum of their energies [5,6]. This is an imported analytic theorem, not a consequence of boundedness alone.

A harmonic map $Q:S^2\to S^2$ has holomorphic Hopf differential, which vanishes because the sphere has no nonzero holomorphic quadratic differential. Hence $Q$ is holomorphic or antiholomorphic and

\[
E[Q]=4\pi|\deg Q|.
\]

Such bubble profiles are rational maps. If several bubbles occur, energy loss sums absolute degrees, whereas signed degree loss sums signed degrees. A nontrivial bubble does not by itself establish that the total signed degree changes by a nonzero amount at the entire event.

The number $4\pi$ refers to unit radius. Scaling the target metric to a sphere of radius $R$ multiplies the energy by $R^2$. The conventional pure-qubit Fubini–Study metric inherited from the Bures hemisphere has $R=1/2$ and bubble energy $\pi|\deg Q|$. A pure-state convention with $4\pi$ energy instead uses four times that metric. The convention must accompany the quantum.

If observer sky metrics are pullbacks of the round metric under Möbius aberration maps, each has area $4\pi$ and the same conformal class. Proposition 6 then holds with the same holomorphic equality maps for every such sky metric. Generic non-holomorphic energies need not agree between observers. This common minimum-energy statement does not make the associated round-metric heat dynamics Lorentz invariant.

In the one-corotational degree-one profile,

\[
Q_\lambda(r)=2\arctan(r/\lambda),
\]

the stereographic dilation is a Möbius map and admits a sky-boost interpretation. Define its profile rapidity as $\eta=\log(\ell_0/\lambda)$ for a declared reference length $\ell_0$. A general higher-degree rational bubble is not a Möbius transformation. A shifted core branch in a selected corotational continuation is a specific inversion mechanism, rather than a universal statement about bubbling.

The familiar stable rate $\lambda\sim C(T-t)/|\log(T-t)|^2$ belongs to a constructed one-corotational regime [7]. Other constructed unstable rates differ [8]. Time and length scales inside logarithms are understood to be normalized by declared reference units. No one rate is assigned to every surface singularity.

In three spatial dimensions the Dirichlet energy has a different scaling. For a localized map $n_\lambda(x)=n(x/\lambda)$,

\[
E[n_\lambda]=\lambda E[n].
\]

A Hopf charge can remain unchanged as this energy tends to zero. The two-dimensional energy quantum therefore does not extend to a three-dimensional Hopf event.

# 7. Equilibria and two regularization mechanisms

## 7.1 Corotational equilibrium laws

For a corotational disk map with polar target coordinate $u(r)$, the energy uses angular weight $F(u)=\sinh^2u$ for $\mathbb H^2$ or $F(u)=\sin^2u$ for $S^2$. With $s=\log r$, the equilibrium equation is $u_{ss}=F'(u)/2$. Regularity and finite energy at the centre fix its first integral to $u_s^2=F(u)$.

**Proposition 7 (equilibrium branches).** For nonnegative hyperbolic boundary demand $u(1)=b$ and centre $u(0)=0$, the regular increasing equilibrium is

\[
u(r)=2\operatorname{artanh}(\mu r),\qquad \mu=\tanh(b/2)<1.
\]

For the spherical increasing branch starting at $u(0)=0$, it is

\[
u(r)=2\arctan(\mu r),\qquad \mu=\tan(b/2)>0,
\]

and has $0<b<\pi$. No smooth branch with that centre condition reaches $\pi<b<2\pi$. A branch with centre $u(0)=\pi$ instead admits $u(r)=\pi+2\arctan(\mu r)$ for those demands.

*Proof.* Integrate $u_s=\sinh u$ or $u_s=\sin u$ on the respective increasing interval. A spherical solution starting at zero cannot cross $u=\pi$ at finite $s$, since the first-order equation has a stationary solution there and uniqueness prevents crossing. The centre-$\pi$ branch follows by shifting the angular coordinate. $\square$

Absence of an equilibrium in a chosen class excludes smooth precompact convergence to an equilibrium in that class. It does not alone force a finite-time class exit; concentration can occur at infinite time. An inversion assertion requires the data and continuation of the particular blow-up theorem.

## 7.2 Mixing by an explicit penalized flow

Choose the flat-ball regularization

\[
E_\varepsilon[m]=\int_M\left[
\tfrac12|\nabla m|^2+\frac{(1-|m|^2)^2}{4\varepsilon^2}\right]dV,
\qquad \varepsilon>0.
\]

Its equation is $m_t=\Delta m+\varepsilon^{-2}(1-|m|^2)m$. This choice is related to standard harmonic-map penalization [9]; its flat metric and potential are declared model content.

**Theorem 8 (fixed-penalty smoothness).** On a closed smooth source, smooth initial data with $|m_0|\leq1$ produce a global smooth solution with $|m(t)|\leq1$.

*Proof.* For $a=|m|^2$,

\[
(\partial_t-\Delta)a=-2|\nabla m|^2
+2\varepsilon^{-2}(1-a)a.
\]

The reaction is negative when $a>1$, so the maximum principle preserves $a\leq1$. On that bounded range the reaction and all its derivatives needed for local semilinear continuation are bounded. Parabolic regularity excludes a finite maximal existence time. $\square$

If $m/|m|$ is defined everywhere during a continuous evolution, its degree is unchanged. A change of that degree requires $m=0$ somewhere. This is the precise topological role of a mixed core. Theorem 8 does not force a degree change or a specific centre crossing. Nor does it prove convergence of passage times to a singular time as $\varepsilon\to0$.

The Bures hemisphere flow provides another smooth mixed-state model. Neither is a smooth continuation through a finite point of the infinite-distance hyperbolic boundary. They are different completions of the constrained pure description.

## 7.3 Attenuation in the null cone

For a null field $k=I(1,n)$, $I>0$, use

\[
D[k]=\frac12\int_\Sigma I^2|dn|^2.
\]

**Proposition 9 (arbitrarily small direction cost).** On a closed oriented surface, at any fixed positive total intensity $\int I=I_0$, the infimum of $D$ is zero in every degree class of $n$.

*Proof.* Choose a smooth degree-$d$ map $n$ constant outside a disk. Its derivative has compact support within that disk. Let a smooth cutoff $\chi$ equal one on the derivative support and have integral $J$ strictly smaller than the area $A_\Sigma$. Set

\[
I_\varepsilon=\varepsilon\chi+a_\varepsilon(1-\chi),
\qquad a_\varepsilon=\frac{I_0-\varepsilon J}{A_\Sigma-J}.
\]

For sufficiently small $\varepsilon>0$ this is positive and has total intensity $I_0$. All direction variation lies where $I_\varepsilon=\varepsilon$, so $D[k_\varepsilon]=\varepsilon^2E[n]\to0$. $\square$

For unconstrained variation of $I$, a critical point with $I>0$ satisfies $I|dn|^2=0$ and has constant direction. At fixed total intensity, the condition instead is $I|dn|^2=\text{constant}$. Constant $I$ and the identity map on a round source $S^2$ give a nonconstant constrained critical point. The infimum statement must not be replaced by a blanket absence of such critical points.

If a continuous null-record field changes the degree of its normalized direction, intensity must vanish somewhere, because a positive intensity would define a continuous direction homotopy throughout. The vertex $k=0$ therefore supplies a possible path for topology change. The proposition is an energy construction; it does not supply a physical attenuation equation that selects this path.

# 8. Wave maps, Schrödinger maps and clocks

**Imported wave-map theorem.** Smooth finite-energy wave maps from fixed $\mathbb R^{1+2}$ Minkowski spacetime to hyperbolic space are globally smooth. Sterbenz–Tataru's compact-target threshold theorem and its covering-space consequence include this result [10]. A finite-time concentration in their theorem produces a sequence of scales $\lambda_j$ at times $t_j\to T$ with $\lambda_j/(T-t_j)\to0$ and rescaled convergence to a Lorentz-transformed nontrivial harmonic map. It is a statement about this energy-critical equation and source.

The extracted scales satisfy the dimensionless identity

\[
\log\frac{\ell_0}{\lambda_j}
-\log\frac{\ell_0}{c(T-t_j)}
=\log\frac{c(T-t_j)}{\lambda_j}\longrightarrow+\infty.
\]

The concentration theorem does not by itself define a continuous bubble scale or prove the corresponding limit at every time. The Lorentz transformation here acts on the wave-map source; it should not be conflated with a Möbius target dilation.

**Imported Schrödinger-map theorem.** For target $\mathbb H^2$, nonzero integer equivariance $m\ne0$, and initial data in the homogeneous $\dot H^1\cap\dot H^3$ class on $\mathbb R^2$, Bejenaru–Ionescu–Kenig–Tataru prove a unique global solution and scattering in a specified moving frame. Their theorem extends to finite-energy data by its prescribed smooth approximation [11]. It does not assert unrestricted large-data regularity in arbitrary dimension. Sphere-valued equivariant Schrödinger-map blow-up constructions are separate results [12], not a universal concentration criterion for every dispersive field.

**Proposition 10 (finite accumulated rapidity rate).** In Minkowski spacetime, let $U(\tau)$ be a future four-velocity compared with a fixed inertial observer, and let $a(\tau)$ be its proper acceleration magnitude. Its hyperbolic mass-shell path has speed $a/c$. Consequently

\[
d(U(\tau)/c,U(0)/c)\leq\int_0^\tau\frac{a(s)}c\,ds.
\]

*Proof.* Differentiating $g(U,U)=-c^2$ makes $A=dU/d\tau$ tangent to the mass shell. Its induced positive norm after normalization is $|A|/c=a/c$. Distance is no greater than path length. $\square$

Finite accumulated rate prevents this velocity curve from reaching its ideal boundary in finite proper time. A uniform cap $a\leq a_{\max}$ is sufficient. Without it, $d\eta/d\tau=\cosh\eta/T_0$ reaches infinite rapidity after $\pi T_0/2$, since $\int_0^\infty\operatorname{sech}\eta\,d\eta=\pi/2$. Its acceleration is unbounded.

A rate bound on a trajectory is not an estimate of field gradients. In curved spacetime it also requires a reference congruence or a transport convention. A freely falling Schwarzschild geodesic has zero proper acceleration but reaches $r=0$ in finite proper time, where $R_{abcd}R^{abcd}=48M^2/r^6$ in geometric units. The field and trajectory theorems therefore do not establish universal absence of gravitational singularities.

# 9. An optional pressure-coupled fluid

Theorem 1 selects a friction metric within a stated class. It does not select a pressure force, momentum law or Eulerian constraint. We now give one complete candidate model rather than treating those choices as consequences of the record cone.

On the flat periodic source $\mathbb T^3$, in speed-one units, choose the Klein field $v:\mathbb T^3\to B^3$, its metric $g_v$ from §4, and

\[
A(v)=g_v^{-1}=(1-|v|^2)(I-vv^T).
\]

Take the evolution and constraint

\[
v_t+(v\cdot\nabla)v=\nu\tau_g(v)-A(v)\nabla p,
\qquad \operatorname{div}v=0,
\tag{9.1}
\]

with $\nu>0$, smooth divergence-free initial data satisfying $|v_0|\leq\kappa_0<1$, and pressure of zero spatial mean. In Klein coordinates the tension is

\[
\tau_g(v)^i=\Delta v^i+
\frac{2}{1-|v|^2}\sum_a(v\cdot\partial_a v)\partial_a v^i.
\]

**Proposition 11 (elliptic pressure closure).** At a smooth field with $|v|\leq\kappa<1$, the equation

\[
\operatorname{div}(A(v)\nabla p)
=\nu\operatorname{div}\tau_g(v)
-\operatorname{div}\big((v\cdot\nabla)v\big)
\tag{9.2}
\]

has a unique zero-mean smooth pressure. Equations (9.1)–(9.2) preserve the divergence constraint.

*Proof.* The eigenvalues of $A$ are $1-|v|^2$ on transverse directions and $(1-|v|^2)^2$ in the radial direction. Thus $A\geq(1-\kappa^2)^2I$. The right side has zero integral on the torus. The weak elliptic problem is coercive on zero-mean $H^1$ functions by the Poincaré inequality. Existence and uniqueness follow, with smoothness by elliptic regularity for the specified smooth coefficients and source. Taking the divergence of (9.1) and substituting (9.2) gives $\partial_t\operatorname{div}v=0$.

The pressure correction is also normal to divergence-free variations for the chosen $L^2(g_v)$ pairing. If $\operatorname{div}Y=0$, then

\[
\int g_v(A\nabla p,Y)=\int\nabla p\cdot Y=0.
\]

This establishes the specified projection interpretation. $\square$

**Conjecture 12 (global regularity of the chosen candidate).** For every initial field specified above, (9.1)–(9.2) have a unique global smooth solution, whose image stays a finite hyperbolic distance from the boundary on every finite time interval.

The pressure proposition defines pressure while a mixedness margin exists; it does not prove that the margin or the derivative estimates persist. Controlling those quantities is the conjecture. The candidate's frame, inverse-metric pressure projection and inertia are additional physical modeling choices. Excluding a different flat-friction model by the chosen invariance criterion does not settle that model's regularity problem.

One exact comparison is useful. With $v=\tanh r\,\xi$ and $m=M_\gamma(r)\xi$, where

\[
M_\gamma(r)=\int_0^r\cosh^{2\gamma-2}s\,ds,
\]

orthogonality $\xi\cdot\partial_a\xi=0$ gives

\[
\nabla v:\nabla m=
\cosh^{2\gamma-4}r\,|\nabla r|^2
+M_\gamma(r)\tanh r\,|\nabla\xi|^2.
\]

The angular weight is linear at $\gamma=1$ and grows exponentially for $\gamma>1$. This identifies a constitutive difference. It is not a proof of a pressure-coupled regularity theorem for the whole momentum-law family, nor an identification of that family with (9.1).

# 10. The resulting field form of SIH

The results establish four separate statements. Hyperbolic heat flow and strictly mixed Bures heat flow are globally regular under their declared hypotheses. Surface sphere heat flow can have quantized harmonic bubbles. Explicit flat-ball penalization is smooth for fixed penalty, while a null-cone intensity construction removes a topological energy lower bound. Fixed-background wave and equivariant Schrödinger results supply further conditional target comparisons.

For a chosen pure bipartite purification, mixedness has an entanglement interpretation. That interpretation does not replace the equation hypotheses in any of these theorems. Similarly, a finite composition remains in the interior only as an algebraic statement; a continuous-time conclusion additionally needs a rate estimate in a declared clock.

The framework is closed as a collection of specified models and conditional theorems. Its remaining fluid task is Conjecture 12 for an explicit equation. A claim about all physical singularities would require new dynamics and estimates beyond this collection.

# Appendix A. A separate scalar fold law

Consider, in one declared clock,

\[
\dot u=Au^p(1-u^2/C^2)^\gamma,
\qquad A>0,\quad p>1,\quad\gamma>0,
\]

with fixed $u_0>0$ and $C$ sufficiently large that $u_0<u_f$. The rate maximum is

\[
u_f=C\sqrt{\frac{p}{p+2\gamma}}.
\]

It follows by differentiating the rate. Let $T=u_0^{1-p}/[A(p-1)]$ be the uncapped ODE blow-up time and let $t_f$ be the capped time to $u_f$.

**Proposition A1 (large-ceiling fold delay).** As $C\to\infty$, for $p=3$,

\[
t_f-T=\frac1{AC^2}
\left[\gamma\log\frac C{u_0}+K_\gamma\right]+o(C^{-2}),
\]

where, with $x_f=\sqrt{3/(3+2\gamma)}$,

\[
K_\gamma=\gamma\log x_f-\frac1{2x_f^2}
+\int_0^{x_f}\frac{(1-x^2)^{-\gamma}-1-\gamma x^2}{x^3}\,dx.
\]

For $p>3$,

\[
t_f-T\sim\frac{\gamma u_0^{3-p}}{A(p-3)C^2}.
\]

*Proof.* Subtract the uncapped time integral:

\[
A(t_f-T)=\int_{u_0}^{Cx_f}u^{-p}
\big[(1-u^2/C^2)^{-\gamma}-1\big]du
-\frac{(Cx_f)^{1-p}}{p-1}.
\]

For $p=3$, substitute $x=u/C$, subtract the leading $\gamma x^2$ in the numerator and integrate its $\gamma/x$ term explicitly. The remainder is integrable at zero since it is $O(x)$, giving the displayed constant and error. For $p>3$, the leading correction is $\gamma C^{-2}u^{2-p}$. Splitting the integral at a fixed small fraction of $C$ bounds the remaining high-$u$ part by $O(C^{1-p})=o(C^{-2})$; the low-$u$ part converges to $\gamma\int_{u_0}^\infty u^{2-p}du$. $\square$

At $p=3$, $\gamma=1$, direct integration gives

\[
t_f-T=\frac1{AC^2}\left[
\log\frac C{u_0}+\frac12\log\frac32-\frac56
+\frac12\log(1-u_0^2/C^2)\right].
\]

The delay is positive for sufficiently large $C$, not necessarily for every admissible finite ceiling. A corresponding local additive chart has

\[
\phi_C(u)=\int_0^u(1-s^2/C^2)^{-\gamma}ds
=u+\frac{\gamma u^3}{3C^2}+O(u^5/C^4),
\]

so its local composition obeys

\[
u\oplus w=u+w-\frac{\gamma}{C^2}uw(u+w)
+O((|u|+|w|)^5/C^4).
\]

The composition correction and the leading delay therefore contain the same chosen coefficient $\gamma/C^2$. This is an identity within the scalar model. The exponent $p=3$ supplies no fluid regularity theorem. Under a changed clock the rate maximum and comparison times must be recalculated in that clock.

# References

[1] J. Eells Jr. and J. H. Sampson, “Harmonic mappings of Riemannian manifolds,” *American Journal of Mathematics* **86**, 109–160 (1964). [doi:10.2307/2373037](https://doi.org/10.2307/2373037).

[2] R. S. Hamilton, *Harmonic Maps of Manifolds with Boundary*, Lecture Notes in Mathematics 471 (Springer, 1975). [doi:10.1007/BFb0087227](https://doi.org/10.1007/BFb0087227).

[3] M. Hübner, “Explicit computation of the Bures distance for density matrices,” *Physics Letters A* **163**, 239–242 (1992). [doi:10.1016/0375-9601(92)91004-B](https://doi.org/10.1016/0375-9601(92)91004-B).

[4] K.-C. Chang, W. Ding and R. Ye, “Finite-time blow-up of the heat flow of harmonic maps from surfaces,” *Journal of Differential Geometry* **36**, 507–515 (1992). [doi:10.4310/jdg/1214448751](https://doi.org/10.4310/jdg/1214448751).

[5] M. Struwe, “On the evolution of harmonic mappings of Riemannian surfaces,” *Commentarii Mathematici Helvetici* **60**, 558–581 (1985). [doi:10.1007/BF02567432](https://doi.org/10.1007/BF02567432).

[6] J. Qing, “On singularities of the heat flow for harmonic maps from surfaces into spheres,” *Communications in Analysis and Geometry* **3**, 297–315 (1995). [doi:10.4310/CAG.1995.v3.n2.a4](https://doi.org/10.4310/CAG.1995.v3.n2.a4).

[7] P. Raphaël and R. Schweyer, “Stable blowup dynamics for the 1-corotational energy critical harmonic heat flow,” *Communications on Pure and Applied Mathematics* **66**, 414–480 (2013). [arXiv:1106.0914](https://arxiv.org/abs/1106.0914).

[8] P. Raphaël and R. Schweyer, “Quantized slow blow up dynamics for the corotational energy critical harmonic heat flow.” [arXiv:1301.1859](https://arxiv.org/abs/1301.1859).

[9] Y. Chen and M. Struwe, “Existence and partial regularity results for the heat flow for harmonic maps,” *Mathematische Zeitschrift* **201**, 83–103 (1989). [doi:10.1007/BF01161997](https://doi.org/10.1007/BF01161997).

[10] J. Sterbenz and D. Tataru, “Regularity of wave-maps in dimension 2+1,” *Communications in Mathematical Physics* **298**, 231–264 (2010). [arXiv:0907.3148](https://arxiv.org/abs/0907.3148).

[11] I. Bejenaru, A. D. Ionescu, C. E. Kenig and D. Tataru, “Equivariant Schrödinger maps in two spatial dimensions: the $\mathbb H^2$ target.” [arXiv:1212.2566](https://arxiv.org/abs/1212.2566).

[12] F. Merle, P. Raphaël and I. Rodnianski, “Blowup dynamics for smooth data equivariant solutions to the critical Schrödinger map problem,” *Inventiones Mathematicae* **193**, 249–365 (2013). [doi:10.1007/s00222-012-0427-y](https://doi.org/10.1007/s00222-012-0427-y).

**Preparation note.** This manuscript was prepared with AI-assisted drafting and mathematical checks.
