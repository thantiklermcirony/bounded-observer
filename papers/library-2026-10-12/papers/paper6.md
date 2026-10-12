---
title: "The Partner Freedom"
subtitle: "Gauge connections, Higgs breaking and conditional charge classification"
author: "Daniel John Murray"
orcid: "0009-0005-1794-5945"
affiliation: "Independent researcher, Melbourne, Australia"
date: "12 October 2026"
version: "Working v3.1"
abstract: |
  Purification supplies a precise freedom of description, but a physical gauge connection requires an additional local frame identification. We formulate that identification explicitly and derive the centred covariance measured by a joint-fidelity experiment. The covariance becomes a trace form on traceless generators at maximal mixing; abelian response requires distinct charge sectors or a relational reference. Given a local Lorentz gauge action and a curvature-quadratic truncation, the leading dynamics is Yang–Mills with independent kinetic coefficients. We then classify Higgs stabilizers, admissible U(2) representations, the faithful local-field Standard Model quotient, and anomaly-free hypercharges within a specified chiral matter and Yukawa family. Right-handed neutrinos leave a B−L mixing freedom rather than forcing an additional gauge field. A conditional minimality theorem selects four completed U(2) doublets of charges (1,1,1,−3). Finally, an electrically neutral CPT pair with specified colour-reference sectors gives a covariance ratio of two. Its interpretation as a coupling relation remains conditional on an operational response-to-action identification. The framework separates mathematical classifications, physical premises and numerical hypotheses.
keywords:
  - purification
  - gauge covariance
  - Higgs mechanism
  - anomaly cancellation
  - Standard Model global group
  - conditional expectation
  - boundary representations
---

# 1. Operational scope and premises

A density matrix describes readings available to a part of a larger quantum record. A purification describes a pure joint record, and changing its partner description can preserve the part's marginal. This elementary freedom suggests an operational account of frame comparison. To use it in a field theory, one must specify which changes are passive descriptions, which joint readings remain accessible, and which connection carries physical information.

This paper develops that account within a finite-dimensional complex quantum record space and an ordinary four-dimensional field-theory setting. It does not assume that purification alone selects a gauge group, matter spectrum or interaction law. Its physical premises are:

1. **Local internal frames.** A chosen compact internal group acts on a declared partner or multiplicity bundle. Passive local frame changes leave the specified relational readings unchanged. A connection compares these frames.
2. **Spacetime and action.** Matter is defined on a Lorentzian spin background. The leading gauge action is local, Lorentz invariant and quadratic in curvature, with specified positive internal kinetic forms. Higher-derivative terms are omitted at the stated effective-action order.
3. **Matter and Higgs content.** The chiral representation family, scalar doublet, nonzero vector vacuum and allowed Yukawa interactions are declared before anomaly equations are solved.
4. **Quantum consistency.** The matter gauge theory is anomaly-free, including its coupling to background spin connections. The calculations assume cancellation by the stated matter spectrum, without additional anomaly inflow or compensating topological sectors.
5. **State response.** Whenever a carrier covariance is used as a gauge kinetic form, the carrier, state-selection dynamics, generator calibration and common response-to-action map are stated explicitly.

An operationally specified model consists of these structures together with its observables, preparation data and dynamical parameters. A framework is closed in this sense when its readings and response maps are defined and its conditional claims are mathematically determined. That usage does not assert that all phenomenological numbers have been derived.

The following results are classifications within these premises. Three colours, the observed generation count, numerical Yukawa couplings, vacuum scale and kinetic coefficients remain physical inputs or selection hypotheses. A rule excluding unexplained numbers can motivate a search for their origin, but does not replace that search.

# 2. Purification and local frame comparison

**Proposition 1 (marginal invariance).** Let \(|\Psi\rangle\in\mathcal H_A\otimes\mathcal H_B\) and \(\rho_A=\operatorname{Tr}_B|\Psi\rangle\langle\Psi|\). For every unitary \(V\) on \(\mathcal H_B\),

\[
 \operatorname{Tr}_B[(I\otimes V)|\Psi\rangle\langle\Psi|(I\otimes V^\dagger)]
 =\rho_A.
\]

**Proof.** The partial trace is invariant under conjugation on its traced factor. Equivalently, insert any orthonormal basis of \(\mathcal H_B\); its image under \(V^\dagger\) is another such basis. All expectation values of \(A\otimes I\) are therefore preserved. \(\square\)

Purifications of a fixed marginal are related by a partner isometry, or by a unitary after a common sufficiently large partner space is chosen. The minimum partner dimension is the marginal rank. Extra unused dimensions can enlarge the description group without altering the marginal; consequently its full unitary group is not automatically the physical gauge group.

An active \(I\otimes V\) generally changes partner readings and joint correlations. A passive frame change instead transforms the state coordinates and the corresponding observables together. Marginal invariance is a theorem; identifying a class of partner frames with a local gauge redundancy is premise 1.

With Hermitian connection \(\mathcal A\), use \(D=d-i\mathcal A\). A local frame change \(g\) gives

\[
 \mathcal A'=g\mathcal A g^{-1}-i(dg)g^{-1},\qquad
 F=d\mathcal A-i\mathcal A\wedge\mathcal A,\qquad F'=gFg^{-1}.
\]

These formulas follow from \(D'(g\psi)=gD\psi\). Holonomy compares frames around a loop; its conjugacy-invariant or relational readings can reveal curvature. The existence of such a connection does not yet supply its kinetic action.

# 3. Joint fidelity and the centred response metric

**Theorem 2 (covariance from fidelity).** Let \(\rho_B\) be the partner marginal of \(|\Psi\rangle\), and \(A=F^aT_a\) a fixed Hermitian operator. For \(W(\varepsilon)=e^{i\varepsilon A}\),

\[
 1-|\langle\Psi|(I\otimes W)|\Psi\rangle|^2
 =\varepsilon^2\operatorname{Var}_{\rho_B}(A)+O(\varepsilon^4).
\]

The corresponding real symmetric quadratic form is

\[
 K_\rho(X,Y)=\frac12\operatorname{Tr}\rho
 \{X-\langle X\rangle_\rho I,Y-\langle Y\rangle_\rho I\}.
\]

**Proof.** The joint overlap is \(\operatorname{Tr}(\rho_BW)\). Put \(a=\operatorname{Tr}\rho_BA\), \(b=\operatorname{Tr}\rho_BA^2\). Expansion gives \(1+i\varepsilon a-\varepsilon^2b/2+\cdots\); its squared modulus has quadratic coefficient \(a^2-b\). The squared modulus is even in \(\varepsilon\), because its value at \(-\varepsilon\) is the complex conjugate product at \(+\varepsilon\). Polarization yields \(K_\rho\). \(\square\)

This is the fidelity of the specified pure joint record with its transformed record, not a maximization over alternative purifications.

At \(\rho=I_n/n\),

\[
 K(X,Y)=\frac{\operatorname{Tr}(XY)}n
       -\frac{\operatorname{Tr}X\,\operatorname{Tr}Y}{n^2}. \tag{1}
\]

Equation (1) is the trace form on traceless generators and vanishes on scalar generators. For a defining doublet, \(Y=I_2/2\) has variance zero, while \(T_3=\operatorname{diag}(1,-1)/2\) has variance \(1/4\). The scalar phase cannot be read through this fidelity.

An abelian response therefore requires a carrier with distinct charges or a relational reference. Two populated sectors with charges \(q_0\ne q_1\) and weights \(1-p,p\) give

\[
 K(Q,Q)=p(1-p)(q_1-q_0)^2.
\]

A total-charge-neutral realization is

\[
 \sqrt p\,|q_1\rangle_M|-q_1\rangle_R+
 \sqrt{1-p}\,|q_0\rangle_M|-q_0\rangle_R.
\]

A holonomy acting on \(M\) changes a joint relative phase. The reference makes that phase an operational comparison while preserving total charge. Its sector weights remain preparation or state-selection data.

**Proposition 3 (independent factor metrics).** On \(\mathfrak{su}(3)\oplus\mathfrak u(1)\), an invariant positive symmetric form has the form

\[
 B(X+\alpha Q,Y+\beta Q)
 =\kappa_3\operatorname{tr}_{\mathbf3}(XY)+\kappa_Q\alpha\beta,
 \qquad \kappa_3,\kappa_Q>0.
\]

**Proof.** Simplicity fixes the colour form up to a scalar. The abelian centre supplies its own scalar. Invariance makes the cross term vanish on commutators, and \(\mathfrak{su}(3)\) is spanned by its commutators. \(\square\)

A finite global quotient does not remove this freedom in the Lie-algebra metric. The same conclusion applies to \(\mathfrak{su}(2)\oplus\mathfrak u(1)\).

# 4. The conditional gauge action

With premise 2, the leading parity-even gauge term is

\[
 S_{\mathrm{gauge}}=-\frac14\int d^4x\,\sqrt{-g}\,
 h_{ab}F^a_{\mu\nu}F^{b\,\mu\nu}, \tag{2}
\]

where \(h\) is an invariant positive internal form. This is the Yang–Mills structure [1], with independent coefficients for distinct simple and abelian factors. Lorentz invariance supplies the spacetime contraction; positivity of a spatial fidelity alone does not derive it. A finite propagation ceiling also does not substitute for the local effective-action premise.

Under an optional **common response hypothesis**, a declared carrier experiment fixes

\[
 h_{ab}=\chi K_{ab},\qquad\chi>0, \tag{3}
\]

at a specified matching scale and with fixed generator conventions. Equation (3) is an operational identification between a response experiment and the field action. It is not a consequence of equation (1). Separate calibrations would retain separate coupling parameters.

The parity-odd Pontryagin density is locally a total derivative,

\[
 \operatorname{tr}(F\wedge F)
 =d\,\operatorname{tr}\!\left(\mathcal A\wedge d\mathcal A
       -\frac{2i}{3}\mathcal A\wedge\mathcal A\wedge\mathcal A\right).
\]

A constant theta coefficient can nevertheless affect quantum topological sectors and transitions. Its global meaning also depends on the gauge group and allowed bundles [2]. Calling its local density a boundary term does not select theta or remove its CP effects.

# 5. Spin, internal multiplicity and masses

For a maximally entangled binary pair with coefficient matrix proportional to a unitary, a rotation on one factor can be represented by a unitary on the other. This is a useful matrix identity. Its interpretation as particle spin requires a separate physical dictionary. The phase-free binary frame group is \(PU(2)\cong SO(3)\); selecting its spinorial lift uses \(SU(2)\), rather than identifying the scalar-phase quotient itself with \(SU(2)\).

In a Lorentz particle representation, finite boosts preserve invariant mass and conjugate the massive little group to an isomorphic \(SU(2)\). In a spinor-matrix dictionary, \(B=e^{r\sigma_3/2}\) has determinant one, so \(\det(B\Psi)=\det\Psi\). Normalizing the boosted matrix can make its Schmidt weights approach \((1,0)\) as \(r\to\infty\); it does not make the invariant mass vanish at finite \(r\).

The stabilizer of a null momentum is the double cover of \(ISO(2)\). For ordinary finite-helicity representations the translation part acts trivially, leaving the \(U(1)\) helicity quotient [3,4]. A singular rank-one boundary and a finite boost must therefore be distinguished.

Here internal actions are defined on multiplicity factors commuting with the spacetime action. Coleman–Mandula supplies a related restriction when its scattering and spectral assumptions hold [5]; those assumptions are not supplied merely by a density-matrix dictionary. A spin decomposition \(\mathbf2\otimes\mathbf2=\mathbf1\oplus\mathbf3\) has commuting unitary group \(U(1)\times U(1)\), because its two irreducible summands each occur once. It does not furnish an internal colour \(U(3)\).

**Theorem 4 (Dirac mass criterion).** For unitary gauge representations \(R_L,R_R\), a gauge-invariant Dirac bilinear exists precisely when

\[
 \operatorname{Hom}_G(R_R,R_L)\ne0.
\]

**Proof.** A matrix \(M\) in \(\bar\psi_LM\psi_R\) is invariant exactly when \(U_L(g)^\dagger M U_R(g)=M\) for every \(g\), equivalently \(M\) is an intertwiner. For inequivalent irreducible representations Schur's lemma gives \(M=0\). \(\square\)

An allowed bilinear need not have a nonzero coefficient. For example, a vectorlike representation with a specified zero bare coefficient and a neutral-scalar Yukawa interaction \(y\phi\bar\psi_L\psi_R\) can acquire its mass from a scalar vacuum. This already disproves the implication from an absent bare mass to inequivalent gauge representations. Chiral matter is premise 3.

# 6. Higgs vectors and the electroweak stabilizer

Take a scalar doublet \(H\) with physical hypercharge \(Y_H=1/2\), covariant derivative

\[
 D_\mu H=(\partial_\mu-igW_\mu^a\sigma_a/2-ig'B_\mu Y)H,
\]

and nonzero vector vacuum \(H_0=(0,v/\sqrt2)^T\). A potential admitting this vacuum and the scalar kinetic term are included in premise 3 [6].

**Theorem 5 (Higgs stabilizer and masses).** The unbroken Lie-algebra generator is \(Q=T_3+Y\). Substitution into \(|D_\mu H_0|^2\) gives

\[
 m_W^2=g^2v^2/4,\qquad m_Z^2=(g^2+g'^2)v^2/4,\qquad m_\gamma=0,
\]

and \(m_W/m_Z=\cos\theta_W\), with \(\tan\theta_W=g'/g\).

**Proof.** \(QH_0=0\). The neutral quadratic term is \(v^2(-gW^3+g'B)^2/8\), of rank one. Its orthogonal photon direction is massless. The two charged directions have the same quadratic coefficient, yielding the stated masses. \(\square\)

For a defining \(U(2)\) vector, fixing \(H_0\) leaves \(\operatorname{diag}(e^{i\alpha},1)\), a \(U(1)\) stabilizer, with orbit \(S^3\). Fixing only its ray leaves \(U(1)\times U(1)\), with orbit \(\mathbb{CP}^1\). The theorem uses a vector vacuum, not a ray alone.

These results specify the weak Lie algebra and its breaking under the declared Higgs representation. Neither \(g'=g\) nor the values of \(g,g',v\) follow.

# 7. Global groups and the colour-centre identification

**Theorem 6 (U(2) weights).** An \(SU(2)\) isospin-j representation with integer central \(U(1)\) charge q descends to

\[
 U(2)=(SU(2)\times U(1))/\mathbb Z_2
\]

if and only if \(q\equiv2j\pmod2\).

**Proof.** The identified element \((-I_2,-1)\) acts as \((-1)^{2j+q}\), which must equal one. \(\square\)

With the defining Higgs assigned \(q=1\), its physical hypercharge is \(q/2\). Fractional quark hypercharges cannot then be added with unchanged charge convention and unchanged defining Higgs. One consistent alternative is \(q=6Y\): weak doublets still have odd q, but the Higgs has \(q=3\) and is \(\det\otimes\mathbf2\). Thus U(2) can accommodate the local weak matter with a changed Higgs representation and central normalization; the defining-Higgs toy does not uniquely choose the full physical global group.

For the usual three-colour local fields, let

\[
 \widetilde G=SU(3)\times SU(2)\times U(1)_{6Y}.
\]

**Theorem 7 (faithful local-field quotient).** The common kernel of the usual matter and Higgs representations is \(\mathbb Z_6\), generated by

\[
 (\omega_3I_3,-I_2,e^{i\pi/3}),\qquad\omega_3=e^{2\pi i/3}.
\]

Its maximal faithful local-field quotient is

\[
 G_{\max}=\widetilde G/\mathbb Z_6\cong S(U(3)\times U(2)).
\]

**Proof.** A representation of colour triality t, weak centre parity s and charge q admits the quotient exactly when

\[
 q+2t+3s=0\pmod6. \tag{4}
\]

The map \((A,B,z)\mapsto(z^{-2}A,z^3B)\) has image \(S(U(3)\times U(2))\) and the stated six-element kernel. The defining Higgs and down-type colour representation force any common kernel element to be central; the charged lepton then imposes \(z^6=1\). The kernel is therefore exactly this \(\mathbb Z_6\). \(\square\)

Write the defining representations of the two unitary factors as \(V_3,V_2\). The fields are

| Field | Representation of \(G_{\max}\) | Y |
|---|---|---:|
| H | \(V_2\) | \(1/2\) |
| \(Q_L\) | \(V_3\otimes V_2\) | \(1/6\) |
| \(u_R\) | \(V_3\otimes\det V_2\) | \(2/3\) |
| \(d_R\) | \(V_3\) | \(-1/3\) |
| \(L_L\) | \(V_2\otimes(\det V_2)^{-1}\) | \(-1/2\) |
| \(e_R\) | \((\det V_2)^{-1}\) | \(-1\) |
| \(\nu_R\), if present | trivial | 0 |

This description links colour and hypercharge centres. With the Higgs vector fixed, the stabilizer in \(G_{\max}\) is isomorphic to \(U(3)\): for \(C\in U(3)\), the corresponding weak factor is \(\operatorname{diag}((\det C)^{-1},1)\). Its Lie algebra is colour plus electromagnetism, and three gauge directions acquire Higgs masses.

The local fields also admit \(\widetilde G/\Gamma\) for \(\Gamma=1,\mathbb Z_2,\mathbb Z_3\). These choices differ in line operators and bundles [2]. Faithfulness on the declared local fields is a theorem; selection of the physical global gauge group is additional data.

# 8. Anomaly-free charges within a matter family

Choose colour \(SU(N)\), \(N\ge2\), one coloured weak doublet \(Q_L\), one uncoloured weak doublet \(L_L\), right-handed colour fundamentals \(u_R,d_R\), and an uncoloured \(e_R\). Let their doublet hypercharges be \(a,b\), and the Higgs charge be \(h\ne0\). Charged Yukawa invariance gives

\[
 Y(u_R)=a+h,\quad Y(d_R)=a-h,\quad Y(e_R)=b-h. \tag{5}
\]

We use left-minus-right anomaly coefficients. This spectrum and its Yukawas are selected matter premises. The standard charge-classification argument applies within such families [7,8].

**Theorem 8 (no right-handed neutrino).** Within (5), anomaly freedom fixes

\[
 a=h/N,\qquad b=-h.
\]

**Proof.** The colour cubic anomaly cancels through \(2-1-1\), and the colour-colour-hypercharge coefficient is proportional to \(2a-(a+h)-(a-h)=0\). The weak-weak-hypercharge coefficient is proportional to \(Na+b\). The mixed gravitational coefficient is \(b+h\). After \(b=-Na\), the cubic abelian coefficient is

\[
 N[2a^3-(a+h)^3-(a-h)^3]+2b^3-(b-h)^3
 =(h-Na)^3. \tag{6}
\]

The remaining coefficients vanish exactly at the stated solution. \(\square\)

The mixed gravitational condition is consistency of the quantum gauge theory on background spin connections; it does not require a derived gravitational action. It is distinct from a pure local gravitational anomaly in four dimensions [9].

At the charge convention \(h=1/2\), theorem 8 gives

\[
 Q_u=\frac{N+1}{2N},\quad Q_d=\frac{1-N}{2N},\quad Q_\nu=0,\quad Q_e=-1.
\]

Putting \(N=3\) yields the usual values. It does not prove N=3 or classify every possible chiral spectrum.

**Global weak consistency.** With \(n_g\) identical generations and no additional weak doublets, the familiar Witten parity condition is

\[
 n_g(N+1)=0\pmod2. \tag{7}
\]

For general weak matter, replace this by the parity of the total \(\sum_r \dim(R_{\mathrm{other},r})\,2T(j_r)\), with all multiplicities and \(T(1/2)=1/2\). Odd N follows from odd \(n_g\), or from requiring each generation separately consistent. An even-generation theory is not subject to that per-generation conclusion [10]. For colour SU(2) itself the chosen family has four colour doublets per generation, so its corresponding parity obstruction cancels. For actual quotient groups, global and perturbative conditions must be assessed together; in spin U(2) theories the familiar SU(2) parity is enforced through local anomaly cancellation [11].

**Theorem 9 (right-handed neutrino).** Add a neutrino Yukawa interaction and \(Y(\nu_R)=b+h\). The anomaly equations leave

\[
 b=-Na,\qquad
 Y=Y_{\mathrm{standard}}+t(B-L),\qquad t=Na-h, \tag{8}
\]

where \(B-L=1/N\) on quarks, \(-1\) on leptons and zero on H.

**Proof.** The mixed gravitational coefficient now cancels identically. The cubic coefficient becomes \(-6h^2(Na+b)\), so it imposes no condition beyond weak-weak-hypercharge cancellation. Substitution gives (8). \(\square\)

Equation (8) is a Lie-algebra charge family; a chosen compact global form additionally imposes integral weight and quotient constraints. Requiring neutral neutrinos sets \(b+h=0\), hence \(t=0\). Anomaly freedom alone does not impose it.

With this neutrino spectrum, B−L can be gauged: its cubic, mixed gravitational and mixed gauge anomalies cancel. It can also be an exact global symmetry of a Dirac-neutrino model, forbidding a Majorana bilinear without adding a gauge boson. A permitted singlet Majorana coefficient need not be nonzero. An additional B−L gauge extension is therefore optional.

For odd N, an N-quark baryon containing \(n_u\) up constituents has

\[
 Q_b=n_u-(N-1)/2.
\]

The composition \(n_u=(N+1)/2\) has charge +1, cancelled by one electron. Other baryons have other charges. This proves conditional charge counting; existence and stability of bound states require their dynamics.

# 9. A conditional U(2) minimality theorem

An alternative selection route can be stated without hiding its assumptions. Consider left-handed U(2) doublets of odd nonzero integer charges \(q_i\), one Higgs of odd charge h, and two right-handed singlets \(q_i+h,q_i-h\) per doublet. Exclude opposite-charge doublet pairs. Minimize first the number of doublets and then their maximum charge magnitude.

**Theorem 10.** Perturbative cancellation is equivalent to \(\sum_iq_i=0\). The minimal spectrum is, up to sign and permutation,

\[
 (q_1,q_2,q_3,q_4)=(1,1,1,-3).
\]

If the singleton doublet contains a neutral component and \(h>0\), then \(h=3\); setting \(Y=q/6\) gives the usual one-generation charges including \(\nu_R\).

**Proof.** Each completed doublet has zero gravitational coefficient. The weak mixed coefficient is proportional to \(q_i\), and the cubic coefficient is \(-6h^2q_i\). Their sums vanish exactly when \(\sum_iq_i=0\). Odd charges imply an even doublet count, satisfying the weak parity condition. Two doublets would be an excluded opposite pair, so four is minimal. Maximum magnitude one requires both +1 and −1, also excluded. At maximum three, no opposite pair and zero sum force three 1s against one −3, or its sign reversal. The singleton has component charges \(\pm1/2-3/(2h)\); neutrality with positive h fixes h=3. \(\square\)

The three repeated representations admit an internal SU(3) action if the interactions respect their common multiplicity. Gauging it, including its own kinetic term, is a further premise. The theorem is a conditional minimality result rather than a general prediction of the observed matter family.

# 10. Forgetting, conserved data and carrier covariance

**Theorem 11 (specified maximum-entropy forgetting).** Let \(\mathcal A\subset B(\mathcal H)\) be a finite unital *-algebra and \(E_{\mathcal A}\) its trace-preserving conditional expectation. The generator

\[
 \mathcal L=\gamma(E_{\mathcal A}-\mathrm{id}),\qquad\gamma>0,
\]

has unital completely positive semigroup \(e^{-\gamma t}\mathrm{id}+(1-e^{-\gamma t})E_{\mathcal A}\). It preserves all \(\mathcal A\) readings and converges to \(\rho_*=E_{\mathcal A}\rho_0\), the unique entropy maximizer among states with those same full-algebra readings.

**Proof.** The displayed convex combination proves the channel and convergence statements. For any admissible \(\sigma\), \(\log\rho_*\) lies in \(\mathcal A\) on its support, giving

\[
 D(\sigma\Vert\rho_*)=S(\rho_*)-S(\sigma)\ge0.
\]

Equality holds only at \(\sigma=\rho_*\). If \(\rho_*\) is singular, its kernel projection belongs to \(\mathcal A\); the constraints force \(\sigma\) onto the same support. \(\square\)

This is an explicit forgetting model within the completely positive Markov framework [12]. Its conclusion depends on the retained algebra and dynamics. A stationary state does not by itself select kinetic coefficients or relaxation rates.

For the residual carrier

\[
 \mathcal H_8=\mathbf3_u\oplus\mathbf3_d\oplus\mathbf1_e\oplus\mathbf1_\nu,
\]

Haar forgetting under SU(3) and electric U(1) retains four sector weights:

\[
 \rho_*=p_uI_3/3\oplus p_dI_3/3\oplus p_e\oplus p_\nu.
\]

With \(Q=(2/3,-1/3,-1,0)\), \(\operatorname{tr}_{\mathbf3}T_a^2=1/2\), and zero mean charge,

\[
 K_c=(p_u+p_d)/6,\qquad K_Q=(4p_u+p_d)/9+p_e. \tag{9}
\]

The additional condition \(K_Q/K_c=2\) is \(2p_d=p_u+9p_e\). Combining it with neutrality gives \(p_u:p_d:p_e=5:7:1\). That ratio is a valid constraint solution, not a consequence of Haar forgetting. Conserving \(O=Q^2-C_2/4\) retains its initial mean; it does not set the mean to zero.

# 11. An optional neutral-pair response mechanism

Choose the CPT carrier \(\mathcal K=\mathcal H_8\oplus\overline{\mathcal H}_8\), treating neutral particle and antiparticle modes as distinct, as in the Dirac case. Its charge eigenspaces have dimensions 3 at each of \(\pm2/3,\pm1/3\), dimension 1 at each of \(\pm1\), and dimension 2 at zero. Impose total matter-pair electric neutrality:

\[
 \mathcal V_0=\ker(Q_A+Q_B),\qquad \dim\mathcal V_0=42.
\]

Assume complete unbiased mixing on this allowed subspace. Then \(\Omega=\Pi_0/42\). Grouping particle and antiparticle sectors, its local marginal has

\[
 p_u=p_d=3/7,\qquad p_e=1/21,\qquad p_\nu=2/21.
\]

Direct substitution in (9) gives \(K_c=1/7\), \(K_Q=2/7\). Under the common response hypothesis (3), expressed in conventions \(h_c=1/g_3^2,h_Q=1/e^2\), this yields

\[
 g_3^2/e^2=K_Q/K_c=2. \tag{10}
\]

Equation (10) is conditional on the carrier, mixing constraint, kinetic bridge and matching scale. It is not an independently established numerical law.

Colour Gauss law supplies an essential boundary condition. The electrically neutral matter-pair space contains ten colour singlets and four octets. Restricting a closed pair to colour singlets gives weights \((1/5,1/5,1/5,2/5)\) and covariance ratio \(14/3\), rather than two.

If the octet sector has total weight b,

\[
 \Omega_b=(1-b)\Pi_1/10+b\Pi_8/32,\qquad
 K_Q/K_c=\frac{28-3b}{6+9b}. \tag{11}
\]

The value two requires \(b=16/21\). A gauge-invariant realization can provide compensating colour boundary or reference modes [13,14]. Let the relevant edge multiplicities be \(n_1,n_8\). Uniform mixing on the total colour-singlet physical space gives

\[
 b=\frac{4n_8}{10n_1+4n_8}.
\]

For the regular colour edge representation, Peter–Weyl multiplicities give \(n_R=\dim R\), so \(n_1=1,n_8=8\). The physical singlet space then has dimension 42 and its matter marginal is \(\Pi_0/42\). Only the relevant finite sectors enter this construction; no normalized identity on an infinite regular Hilbert space is assumed.

The model therefore specifies an electrically neutral matter pair with accessible colour-flux reference sectors. If an edge also compensates every electric charge and unbiased mixing includes all matter-pair charge sectors, the local state is maximally mixed on the whole CPT carrier and the ratio becomes \(8/3\). Nonuniform edge energies or bath weights change (11). The availability and dynamics of the required boundary modes remain a physical hypothesis.

# 12. Results and parameter scope

The operational construction gives an exact centred fidelity response, conditional Yang–Mills dynamics, Higgs stabilizers and masses, global representation constraints, and anomaly-free charge classifications within declared matter families. The four-doublet minimality theorem and the neutral-pair response model provide explicit conditional selection routes.

The framework retains independent physical questions: why the internal gauge bundle and chiral matter are realised; which global group and line operators occur; why there are three colours and the observed generations; which Higgs potential and vacuum are selected; and which kinetic, Yukawa and environment parameters govern response. A generic n-family Dirac mixing matrix has \((n-1)(n-2)/2\) physical CP phases [15]. Two Majorana lepton families can have an additional Majorana phase [16]; the existence of a right-handed neutrino alone does not establish it or a baryogenesis mechanism.

These questions are compatible with an operationally specified conditional framework. Their answers require further mechanisms or measurements. In particular, maximum entropy does not determine a scalar quartic coupling or its renormalization-group fixed-point condition, and a parameter encoded in a prepared reference state is not thereby localized on a causal horizon.

## Acknowledgements

The manuscript was developed with AI-assisted drafting and mathematical checks. Responsibility for its assumptions, proofs and scientific claims rests with the author.

## References

[1] C. N. Yang and R. L. Mills, “Conservation of Isotopic Spin and Isotopic Gauge Invariance,” *Physical Review* **96**, 191–195 (1954). [doi:10.1103/PhysRev.96.191](https://doi.org/10.1103/PhysRev.96.191).

[2] D. Tong, “Line Operators in the Standard Model,” *Journal of High Energy Physics* **07** (2017), 104. [doi:10.1007/JHEP07(2017)104](https://doi.org/10.1007/JHEP07(2017)104); [arXiv:1705.01853](https://arxiv.org/abs/1705.01853).

[3] E. P. Wigner, “On Unitary Representations of the Inhomogeneous Lorentz Group,” *Annals of Mathematics* **40**, 149–204 (1939). [doi:10.2307/1968551](https://doi.org/10.2307/1968551).

[4] S. Weinberg, “Feynman Rules for Any Spin. II. Massless Particles,” *Physical Review* **134**, B882–B896 (1964). [doi:10.1103/PhysRev.134.B882](https://doi.org/10.1103/PhysRev.134.B882).

[5] S. Coleman and J. Mandula, “All Possible Symmetries of the S Matrix,” *Physical Review* **159**, 1251–1256 (1967). [doi:10.1103/PhysRev.159.1251](https://doi.org/10.1103/PhysRev.159.1251).

[6] S. Weinberg, “A Model of Leptons,” *Physical Review Letters* **19**, 1264–1266 (1967). [doi:10.1103/PhysRevLett.19.1264](https://doi.org/10.1103/PhysRevLett.19.1264).

[7] C. Q. Geng and R. E. Marshak, “Uniqueness of Quark and Lepton Representations in the Standard Model from the Anomalies Viewpoint,” *Physical Review D* **39**, 693 (1989). [doi:10.1103/PhysRevD.39.693](https://doi.org/10.1103/PhysRevD.39.693).

[8] J. A. Minahan, P. Ramond and R. C. Warner, “Comment on Anomaly Cancellation in the Standard Model,” *Physical Review D* **41**, 715 (1990). [doi:10.1103/PhysRevD.41.715](https://doi.org/10.1103/PhysRevD.41.715).

[9] L. Álvarez-Gaumé and E. Witten, “Gravitational Anomalies,” *Nuclear Physics B* **234**, 269–330 (1984). [doi:10.1016/0550-3213(84)90066-X](https://doi.org/10.1016/0550-3213(84)90066-X).

[10] E. Witten, “An SU(2) Anomaly,” *Physics Letters B* **117**, 324–328 (1982). [doi:10.1016/0370-2693(82)90728-6](https://doi.org/10.1016/0370-2693(82)90728-6).

[11] J. Davighi and N. Lohitsiri, “Anomaly Interplay in U(2) Gauge Theories,” *Journal of High Energy Physics* **05** (2020), 098. [doi:10.1007/JHEP05(2020)098](https://doi.org/10.1007/JHEP05(2020)098); [arXiv:2001.07731](https://arxiv.org/abs/2001.07731).

[12] G. Lindblad, “On the Generators of Quantum Dynamical Semigroups,” *Communications in Mathematical Physics* **48**, 119–130 (1976). [doi:10.1007/BF01608499](https://doi.org/10.1007/BF01608499).

[13] W. Donnelly, “Decomposition of Entanglement Entropy in Lattice Gauge Theory,” *Physical Review D* **85**, 085004 (2012). [doi:10.1103/PhysRevD.85.085004](https://doi.org/10.1103/PhysRevD.85.085004); [arXiv:1109.0036](https://arxiv.org/abs/1109.0036).

[14] W. Donnelly, “Entanglement Entropy and Nonabelian Gauge Symmetry,” *Classical and Quantum Gravity* **31**, 214003 (2014). [doi:10.1088/0264-9381/31/21/214003](https://doi.org/10.1088/0264-9381/31/21/214003); [arXiv:1406.7304](https://arxiv.org/abs/1406.7304).

[15] M. Kobayashi and T. Maskawa, “CP-Violation in the Renormalizable Theory of Weak Interaction,” *Progress of Theoretical Physics* **49**, 652–657 (1973). [doi:10.1143/PTP.49.652](https://doi.org/10.1143/PTP.49.652).

[16] J. Schechter and J. W. F. Valle, “Neutrino Masses in SU(2) × U(1) Theories,” *Physical Review D* **22**, 2227–2235 (1980). [doi:10.1103/PhysRevD.22.2227](https://doi.org/10.1103/PhysRevD.22.2227).
