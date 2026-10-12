---
title: "The Ceiling and the Constants"
subtitle: "State selection, dynamical parameters and operational closure"
author: "Daniel John Murray"
orcid: "0009-0005-1794-5945"
affiliation: "Independent Researcher, Melbourne, Australia"
date: "12 October 2026"
version: "Revised working version 3.1"
abstract: |
  We ask what the bounded-observer framework determines about physical parameters. For fixed constraints and fixed readout operators, the unique finite-dimensional maximum-entropy state defines responses that factor through conserved expectations. We prove the exact rank bound and the Kubo–Mori derivative criterion for preparation-independent readings. A full conserved-algebra conditional expectation supplies an explicit completely positive forgetting semigroup, whereas mean-only Gibbs selection generally cannot be the universal limit of one fixed linear channel. Equilibrium does not determine every dynamical parameter: two locally covariant systems can share the same entropy-maximizing state and conserved algebra while having different clock-independent relative relaxation. Full unitary covariance of dynamics on one carrier is a stronger premise that genuinely selects an isotropic generator. We also classify the complete-positivity cone of the three locally covariant decay rates. We formulate a factorization criterion across admissible physical completions, distinguish preparation data from geometric horizons, and examine the separate cell, criticality and coupling hypotheses. The framework is operationally closed within its stated model class; physical readout, generator and scale identifications remain explicit content. The paper preserves the dated top-mass proposal while correcting its claim to be an already derived precision prediction.
keywords: "maximum entropy; conserved observables; quantum channels; physical constants; operational closure; Higgs criticality; bounded observer"
---

# 1. Parameters have different mathematical roles

A record geometry specifies possible states and operations. A dynamical model additionally specifies which operation occurs, how it is parameterized and how experimental quantities are read. An initial state, an integration constant, a representation label, a kinetic coefficient and an expectation value are distinct mathematical objects. They can be related by a proved mechanism, but naming each one a reading does not supply that mechanism.

The rule that unexplained numbers should not be inserted into a law is therefore a useful demand for origins. On its own it chooses no value: $\operatorname{diag}(1-a,a)$ realizes every reading $a\in[0,1]$. The same remains true if a number is assigned an arbitrary positive effect rather than an unexplained scalar coefficient. A canonical physical readout must be specified.

This does not prevent a complete operational framework. It distinguishes completeness of its objects, operations and deductions from uniqueness of its physical application. We formulate both meanings exactly.

# 2. A completed state-readout theorem

Fix a complex Hilbert space of finite dimension $d$, Hermitian constraint operators $Q_1,\ldots,Q_k$ and fixed Hermitian readout operators $R_1,\ldots,R_m$. Define the feasible moment set

$$\mathcal C=\{q:\operatorname{Tr}(\rho Q_i)=q_i,
\ \rho\succeq0,\ \operatorname{Tr}\rho=1\}.$$

**Theorem 1.** For every feasible $q$, entropy maximization gives a unique state $\rho_*(q)$. Its fixed readouts factor as

$$c_a(q)=\operatorname{Tr}(R_a\rho_*(q))=f_a(q).$$

Let $r=\dim\operatorname{span}_{\mathbb R}\{I,Q_1,\ldots,Q_k\}-1$. On the relative interior of $\mathcal C$, remove redundant constraints. The state is full rank, has Gibbs form

$$\rho_*(q)=\frac{\exp[-\sum_{i=1}^r\beta_i(q)Q_i]}{Z(q)},$$

and its readouts are smooth functions with Jacobian rank at most $r$. A readout is fixed throughout a connected admissible domain exactly when its derivative vanishes along every allowed retained-value direction.

*Proof.* The feasible density set is nonempty and compact. Entropy is continuous and strictly concave, so its maximizer exists and is unique. An interior feasible moment admits a full-rank feasible state. Mixing a rank-deficient candidate with that state has an infinite positive entropy derivative in its missing eigenvalue directions, excluding such a maximizer. Lagrange multipliers give the exponential form. Independent constraints modulo $I$ make the log-partition Hessian positive definite; the inverse-function theorem gives smooth dependence on moments. Composition with fixed readouts gives the rank bound and derivative characterization. $\square$

The proof does not require the $Q_i$ to commute. At boundary moments, the maximizer may lose rank and require divergent multipliers. Only the full-rank relative-interior statement uses finite Gibbs multipliers. Maximum-entropy reasoning is established statistical mechanics [1]; the theorem states the exact finite model to which it is being applied.

## 2.1 The computable independence criterion

At a full-rank Gibbs state, put $\Delta Q_i=Q_i-q_iI$ and $\Delta R=R-f_RI$. Define

$$C_{ij}=\int_0^1\operatorname{Tr}(\rho^s\Delta Q_i\rho^{1-s}\Delta Q_j)ds,
\qquad
v_i=\int_0^1\operatorname{Tr}(\rho^s\Delta R\rho^{1-s}\Delta Q_i)ds.$$

Differentiating the matrix exponential gives

$$\frac{\partial q_i}{\partial\beta_j}=-C_{ij},\qquad
\frac{\partial f_R}{\partial\beta_i}=-v_i,
\qquad\nabla_q f_R=v^TC^{-1}.$$

The reduced covariance matrix is positive definite. Thus $R$ is state-independent on the whole connected interior precisely when $v(q)=0$ there. Commutation with a conserved operator is not that criterion: $R=Q_i$ commutes with it and its reading still changes with $q_i$.

For fixed nonlinear smooth responses, such as a specified inverse covariance, the chain rule supplies the same rank bound. The operator normalization and the response-to-physical-coefficient identification must remain fixed in that statement.

## 2.2 Relations do not mean individually fixed outputs

One conserved population $p$ can give two fixed-effect readings

$$\rho_p=\operatorname{diag}(p,1-p),\qquad c_1=p,
\qquad c_2=(1+p)/2.$$

Both readings vary. The relation $2c_2-c_1=1$ leaves one functional degree of freedom; it does not make one of the two numbers preparation-independent. More outputs than constraints imply a local rank restriction and, where rank is constant, functional relations. They do not require particular output coordinates to be fixed.

These are continuous parameter-count statements. They do not bound arbitrary discrete representation choices or the information in an exact real number. They apply within a completely specified model and preparation domain.

# 3. A realizable forgetting selector

Let $\mathcal A\subset M_d(\mathbb C)$ be a unital *-subalgebra of all retained observables. Its trace-preserving conditional expectation $E_{\mathcal A}$ is a completely positive, unital, idempotent map. It can be implemented by an appropriate unitary twirl.

**Theorem 2.** The output $\rho_*=E_{\mathcal A}\rho_0$ is the unique entropy-maximizing state with the same readings of every Hermitian element of $\mathcal A$. The semigroup

$$\Phi_u=e^{-u}\operatorname{id}+(1-e^{-u})E_{\mathcal A},\qquad u\ge0,$$

is completely positive and trace preserving and tends to that selector.

*Proof.* The expectation preserves all retained readings. On its support, $\log\rho_*$ belongs to $\mathcal A$. Every compatible state $\sigma$ has support within that of $\rho_*$ and satisfies $\operatorname{Tr}(\sigma\log\rho_*)=\operatorname{Tr}(\rho_*\log\rho_*)$. Hence

$$D(\sigma\|\rho_*)=S(\rho_*)-S(\sigma)\ge0,$$

with equality only for $\sigma=\rho_*$. Idempotence shows that the displayed family is the exponential of $E_{\mathcal A}-\operatorname{id}$. Its convex-combination form proves complete positivity and trace preservation. $\square$

This closes a concrete state-selection law. It chooses a state after the actual retained algebra and readings are specified. Fixed-point algebras and the asymptotic structure of quantum semigroups have established treatments [2,3].

**Obstruction to a stronger mean-only claim.** Consider $Q=\operatorname{diag}(0,1,2)$. Mean zero forces the first pure state; mean two forces the third. Any fixed linear limiting map realizing the maximum-entropy selector for every mean must fix both endpoints. It then maps their equal mixture to $\operatorname{diag}(1/2,0,1/2)$. But mean one has maximum-entropy state $I/3$. This is a contradiction.

A few-expectation Gibbs family is generally nonlinear as a map of arbitrary initial states. Realizing it requires additional bath, control, preparation or thermodynamic-limit assumptions. Its existence as an entropy maximizer is not a universal dynamical relaxation theorem. Canonical typicality supplies a conditional ensemble result, also distinct from arbitrary dynamics reaching equilibrium [4].

# 4. Observable dynamical freedom without an external clock

On $\mathbb C^2\otimes\mathbb C^3$ define commuting conditional expectations

$$E_A(\rho)=I_2/2\otimes\operatorname{Tr}_A\rho,
\qquad E_B(\rho)=\operatorname{Tr}_B\rho\otimes I_3/3.$$

For any $\gamma_A,\gamma_B>0$, take

$$\mathcal L=\gamma_A(E_A-\operatorname{id})
+\gamma_B(E_B-\operatorname{id}).$$

**Proposition 3.** These primitive unital Markov dynamics all have the same unique maximum-entropy equilibrium $I_6/6$ and Heisenberg conserved algebra $\mathbb CI$. They are covariant under every local $U_A\otimes U_B$. Nevertheless their physically readable relative relaxation $\gamma_A/\gamma_B$ is free even after a common clock calibration.

*Proof.* Decompose operators into identity, traceless A-only, traceless B-only and doubly traceless sectors. The eigenvalues are respectively

$$0,\quad-\gamma_A,\quad-\gamma_B,\quad-(\gamma_A+\gamma_B),$$

with multiplicities $1,3,8,24$. The kernel is the identity sector; every other sector decays. The generator is the sum of two commuting reset generators, each with a completely positive semigroup. Their tensor forms establish local-unitary covariance. $\square$

Fixing $\gamma_A+\gamma_B=1$ still permits $(1/2,1/2)$ and $(1/4,3/4)$, giving different ratios at the same equilibrium and with the same total rate ceiling. This construction has no preferred axis in either factor.

The difference is readable without introducing an external time unit. With nonzero initial local polarizations, define

$$u=-\log\left|\frac{\langle X_A\rangle}{\langle X_A\rangle_0}\right|,
\qquad v=-\log\left|\frac{\langle X_B\rangle}{\langle X_B\rangle_0}\right|.$$

The trajectory obeys $u=(\gamma_A/\gamma_B)v$. Every common increasing reparameterization leaves this relation unchanged. Observer-centrality cannot remove a distinction that these readings measure. The example disproves deriving a unique generator from equilibrium alone; it does not contradict a stronger assumption that every coefficient has already been identified with a canonical state response.

## 4.1 A condition that really selects dynamics

**Proposition 4.** On one fixed $d$-dimensional carrier, a unital trace-preserving Markov generator covariant under all $PU(d)$ conjugations has form

$$\mathcal L=\kappa(D-\operatorname{id}),\qquad
D(\rho)=I_d\operatorname{Tr}\rho/d,\qquad\kappa\ge0.$$

*Proof.* Under conjugation the operator space splits into the identity and irreducible traceless adjoint sectors. Covariance and Schur's lemma make the generator scalar on the latter. Unitality fixes the identity eigenvalue at zero; Hermiticity makes the traceless eigenvalue real. Positivity on pure inputs requires it to be nonpositive. Its negative is $\kappa$, and the displayed depolarizing semigroup is completely positive. $\square$

Full covariance of the actual dynamics is stronger than invariance of its equilibrium. It removes relative coefficients on that single irreducible carrier, leaving one common evolution scale. A product-group action has inequivalent sectors and can retain independent coefficients. This is a precise dynamical selector when its stronger premise is physically justified.

## 4.2 Environmental encoding is a mechanism, not a location theorem

A prepared register $\tau=\operatorname{diag}(r_x,r_y,r_z)$ controlling a Pauli collision gives $\Phi_r(\rho)=\sum_a r_a\sigma_a\rho\sigma_a$. A declared common collision rate $\kappa$ gives generator $\mathcal L=\kappa(\Phi_r-\operatorname{id})$ and Pauli jump coefficients $\gamma_a=\kappa r_a$. The actual decay rate of the $a$-th Pauli expectation is $2\kappa(1-r_a)$. In this specified mechanism both the jump-coefficient ratios and the relative expectation decays are bath-state readings.

The mechanism also needs a fixed controlled interaction and a preparation law. The register can be a local apparatus or bath; no horizon follows from the density matrix. If boundary data means initial or preparation data, that usage is mathematically legitimate. Identifying it with a projective ideal boundary, null surface or cosmological horizon requires a further encoding and reconstruction map.

## 4.3 Exact finite programming has a boundary of its own

One can ask whether every Hamiltonian coefficient can instead be encoded as a state of one fixed finite program register. Exact deterministic unitary programming supplies a precise restriction [8]. Let a fixed isometric processor $W$ implement a unitary channel $U$ for every data input using pure program $p_U$. Purity and linearity give

$$W(\psi\otimes p_U)=U\psi\otimes q_U,$$

with $q_U$ independent of $\psi$. Preservation of cross inner products for two programs implies

$$\langle p_U,p_V\rangle I=\langle q_U,q_V\rangle U^\dagger V.$$

Unless $U^\dagger V$ is scalar, both overlaps vanish. Mixed-program supports are also orthogonal: unitary channels are extreme completely positive trace-preserving maps, so every pure program in such a support implements that same unitary. Consequently at most the program dimension many projectively inequivalent unitaries can be implemented exactly.

A nontrivial continuum $e^{-igT}$ cannot therefore be programmed exactly and deterministically in one fixed finite register. This is a conditional limit on a proposed state-to-unitary mechanism, not a quantization law for constants. Approximation, postselection, varying runtimes or processors and nonunitary mixture channels escape these hypotheses. The bath-programmed Pauli model above remains compatible. Stating how a coefficient is read must include the mechanism that uses the reading.

## 4.4 Complete positivity fixes the admissible rate cone

Local covariance leaves several rates, but it constrains them. Put $\mathcal H=\mathbb C^m\otimes\mathbb C^n$, $m,n\ge2$. The operator space has identity, traceless A-only, traceless B-only and doubly traceless correlation sectors. Denote the decay eigenvalues on those three traceless sectors by $-\lambda_A,-\lambda_B,-\lambda_C$.

**Theorem 5.** A time-homogeneous trace-preserving quantum Markov generator covariant under all local unitary conjugations is specified by three nonnegative canonical coefficients $x,y,z$. Its sector rates are exactly

$$\lambda_A=x+(1-n^{-2})z,\qquad
\lambda_B=y+(1-m^{-2})z,$$

$$\lambda_C=x+y+(1-m^{-2}-n^{-2})z.$$

Equivalently, its rates obey

$$\lambda_C\le\lambda_A+\lambda_B,\qquad
\lambda_C\ge\lambda_B-\frac{\lambda_A}{n^2-1},\qquad
\lambda_C\ge\lambda_A-\frac{\lambda_B}{m^2-1}.$$

Every triple satisfying these inequalities is realized by such a generator. The cone has two relative degrees of freedom in its interior after a common rate calibration.

*Proof.* The canonical traceless Kossakowski space splits into three inequivalent irreducible representations under $SU(m)\times SU(n)$: traceless A-only, B-only and correlations. Covariance makes its matrix scalar on each block; the GKSL theorem [2] makes those three scalars nonnegative. The invariant Hamiltonian is scalar and has no commutator action. Covariance and trace preservation also force the identity sector to be fixed.

Choose traceless Hermitian bases $A_a,B_b$ with $\operatorname{Tr}(A_aA_{a'})=\delta_{aa'}$ and similarly for B. Give the jump families $A_a\otimes I$, $I\otimes B_b$ and $A_a\otimes B_b$ coefficients $x/m$, $y/n$ and $z/(mn)$. The identities

$$\sum_aA_aXA_a=\operatorname{Tr}(X)I-X/m,\qquad
\sum_a A_a^2=(m^2-1)I/m$$

give the displayed eigenvalues by direct substitution. Conversely $z=\lambda_A+\lambda_B-\lambda_C$, $x=\lambda_A-(1-n^{-2})z$ and $y=\lambda_B-(1-m^{-2})z$. Their nonnegativity is precisely the three rate inequalities, completing sufficiency and necessity. $\square$

For $m=2,n=3$, the lower bounds are $\lambda_B-\lambda_A/8$ and $\lambda_A-\lambda_B/3$. The two independent resets in Proposition 3 occupy the face $z=0$. Positive rates alone are insufficient: $(\lambda_A,\lambda_B,\lambda_C)=(1,1,3)$ have a negative infinitesimal Choi sector, since $1-2e^{-t}+e^{-3t}=-t+O(t^2)$. Thus the framework restricts the permitted kinetic content without selecting one point of its cone. A generator generates completely positive maps; the generator itself need not be a positive map.

# 5. The operational closure criterion

Let $\mathfrak M$ be the nonempty class of physical completions satisfying the declared premises, modulo operational gauge equivalence. Let $B:\mathfrak M\to\mathcal B$ be the supplied preparation/boundary-data map and $X$ an observable response.

**Theorem 6.** The premises fix $X$ without additional data exactly when it is constant across $\mathfrak M$. They determine $X$ from the declared data exactly when $X=F\circ B$ for a well-defined $F$ on $B(\mathfrak M)$, equivalently when $X$ is constant on each fibre of $B$.

*Proof.* Factorization makes equal data give equal responses. Conversely define $F(b)$ by any model in the fibre with data $b$; constancy on that fibre makes the definition independent of the choice. $\square$

Within one completely specified state/readout model, Theorem 1 gives the relevant factorization and the state-independent/preparation-dependent split. Across candidate physical completions, canonical readouts, retained algebra, interaction, response-to-action map and calibration must also be selected. Two admissible completions with equal proposed data and different predictions identify missing content rather than a third ontological category of constants.

This criterion respects closure as a completed operational framework. The admissible model family and deductions can be defined and internally closed, while its physical application still chooses a model and preparation. A stronger claim that actual physics is uniquely selected is a different theorem and must satisfy the same-fibre test.

# 6. Geometric scales and separate high-scale hypotheses

The horizon-entropy route uses an independently supplied area coefficient $\eta$ and gives $G=c^3/(4\hbar\eta)$ in its local-equilibrium regime. A de Sitter horizon then repackages a supplied $\Lambda$ as its entropy capacity. These relations do not predict that cosmological parameter.

If one further chooses one maximally entangled qubit pair per square regulator cell, its entropy $\log2$ and the area law give $A_{\rm cell}=4\log2\,\ell_P^2$. Identifying the square side with a cutoff length gives

$$E_{\rm cell}=\frac{E_P}{2\sqrt{\log2}},\qquad E_P=\sqrt{\frac{\hbar c^5}{G}}.$$

The arithmetic is exact within that cell and energy-matching model. Neither the spatial cell shape nor its connection to the renormalization scale follows from record geometry alone.

## 6.1 Entropy stationarity is not RG criticality

Maximum entropy without nonconstant constraints gives $I/d$. It does not force every response coefficient to zero: the purity, read as a Swap expectation on two copies, is $1/d$. A scalar quartic is not identified with zero by this state selection.

Nor does stationarity near a bounded scale boundary imply a vanishing beta function. For $\mu(r)=\Lambda\tanh r$,

$$\frac{d\lambda}{dr}=\beta_\lambda(\mu)
\frac{\operatorname{sech}^2r}{\tanh r}\longrightarrow0$$

for every finite limiting beta function, including a nonzero one. The conditions $\lambda(\Lambda)=\beta_\lambda(\Lambda)=0$ remain an additional high-scale criticality hypothesis. A zero of an individual running coupling also depends on its finite renormalization scheme. Physical degeneracy of effective-potential minima is a distinct stability criterion [5,6].

## 6.2 The dated top proposal and a reproducible fit calculation

The research programme recorded $171.2\pm0.4$ GeV as a proposed top-pole-mass target on 12 October 2026. That historical target is preserved. It combined different criteria and a shifted numerical summary; it was not an independently reproduced simultaneous solution of both high-scale conditions at the fixed cell scale. This revised manuscript does not certify it as a precision consequence of the operational axioms.

A specified calculation can be reproduced. The published approximate stability-bound fit in Buttazzo et al., equation (64), is

$$M_h^{\rm crit}=129.6+2(M_t-173.34)
-0.5\frac{\alpha_s-0.1184}{0.0007}\quad\text{GeV},$$

with its separately stated theoretical uncertainty. Algebraic inversion at the programme inputs $M_h=125.20$ GeV and $\alpha_s=0.1180$ gives a central boundary of about $170.997$ GeV. This is the conditional value of that existing approximate fit, not a new parameter-free UHL prediction and not a computation of the fixed-cell joint condition. Adding a shift to the published scalar top-summary equation (66) is not an interchangeable inverse formula with an established new reference point.

A precision prediction needs one declared criterion, spectrum, matching scheme, loop order, mass definition and input covariance. Direct reconstructed top masses and short-distance threshold masses require controlled interpretation or conversion before a pole-mass comparison [7]. A simple sigma estimate around the historical target cannot settle those issues or turn the hypothesis into a derivation.

## 6.3 Gauge coupling hypotheses

On $\mathfrak{su}(3)\oplus\mathfrak u(1)$, covariance permits two independent positive kinetic coefficients. The original common-coupling proposal and its reported weak-angle discrepancy belong to that additional hypothesis. They do not falsify the cone classification.

The exploratory relation $g_3=\sqrt2\,e$ uses a chosen normalization and matching scale. The companion matter paper gives a concrete zero-electric-charge pair whose centred covariance ratio is two, and alternative boundary conditions giving $14/3$ or $8/3$. Interpreting the covariance as an inverse kinetic coefficient requires the physical response-to-action bridge. Selecting the electric and colour reference conditions is a further physical mechanism.

The near-alignment found using the earlier two-loop implementation remains a reported post-hoc observation. Its exact crossing and significance are not certified here as precision results. A valid recalculation must remove every two-loop contribution in a one-loop comparison, consistently rematch threshold inputs when changing $\alpha_s$, state the model particle content and propagate uncertainties. A chance estimate based on three conveniently chosen scale windows is illustrative only without a defined null and search model.

# 7. What has closed

The paper completes a finite entropy-readout theorem, an implementable full-algebra forgetting law, a clock-independent test of residual dynamical freedom, a conditional isotropic-generator selector and a precise factorization criterion for physical completion. These results make the remaining questions mathematically specific.

The classification of model responses can be complete without computing every number. The programme can use that completed structure by declaring a subject's record space, operations, conserved algebra, physical readouts and preparation data, then deriving its permitted consequences. An unresolved generator or a missing physical readout cannot be removed merely by renaming it horizon information. Such content remains an explicit hypothesis or measurement until a mechanism establishes the factorization.

# Acknowledgements

Prepared with assistance from Claude and OpenAI Codex. Numerical checks supplement the stated proofs. Historical comparisons are distinguished from newly proved statements, and no new biological or collider dataset is claimed. The author is responsible for final review and submission.

# References

1. Jaynes ET. Information theory and statistical mechanics. *Phys Rev*. 1957;106:620-630. doi:10.1103/PhysRev.106.620.
2. Lindblad G. On the generators of quantum dynamical semigroups. *Commun Math Phys*. 1976;48:119-130. doi:10.1007/BF01608499.
3. Baumgartner B, Narnhofer H. Analysis of quantum semigroups with GKS–Lindblad generators: II. General. *J Phys A*. 2008;41:395303. doi:10.1088/1751-8113/41/39/395303. arXiv:0806.3164.
4. Popescu S, Short AJ, Winter A. Entanglement and the foundations of statistical mechanics. *Nat Phys*. 2006;2:754-758. doi:10.1038/nphys444.
5. Buttazzo D, et al. Investigating the near-criticality of the Higgs boson. *JHEP*. 2013;12:089. doi:10.1007/JHEP12(2013)089. arXiv:1307.3536.
6. Shaposhnikov M, Wetterich C. Asymptotic safety of gravity and the Higgs boson mass. *Phys Lett B*. 2010;683:196-200. doi:10.1016/j.physletb.2009.12.022. arXiv:0912.0208.
7. Particle Data Group. Top-quark mass listings, 2026. [Top-quark listing](https://pdg.lbl.gov/2026/listings/rpp2026-list-t-quark.pdf).
8. Nielsen MA, Chuang IL. Programmable quantum gate arrays. *Phys Rev Lett*. 1997;79:321-324. doi:10.1103/PhysRevLett.79.321. arXiv:quant-ph/9703032.
