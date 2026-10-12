---
title: "Exact Onset and Peak Laws for Bounded Adaptive Responses"
subtitle: "A mathematical amendment to the geometric-necessity claim for hormesis"
author: "Daniel John Murray"
date: "12 October 2026"
abstract: |
  A published bounded-adaptation model represents repair and damage as opposing rapidity increments, while its analytical approximation multiplies a benefit and a survival factor. These are distinct response models. We derive exact onset, peak and return-to-control conditions for the published additive-rapidity model with equal linear-dose logistic slopes, with an exact zero-dose normalization. Activation before toxicity and greater high-dose damage are not sufficient for a beneficial interval: a further amplitude–slope condition is necessary. We then obtain closed-form laws for an explicitly different log-dose Hill version of the additive model and for the multiplicative Hill response. Their conditions and amplitudes differ, and none has a universal peak at twice the activation threshold. We also derive exact detectable-interval quadratics at a declared assay cutoff. Finally, we distinguish local metabolic-control coefficients from finite enzyme changes and prove an exact finite-gain attenuation law for a specified equal-resistance chain. These results correct the necessity, peak-location and finite-amplitude claims without discarding bounded projective composition. They are analytic model results, not a new fit to biological data. They provide independently testable response laws once their components and matched endpoints are measured.
keywords: "hormesis; bounded adaptation; rapidity; dose response; metabolic control; peak location; corrigendum"
---

Independent Researcher, Melbourne, Australia. ORCID: 0009-0005-1794-5945.

# 1. What requires amendment

The earlier paper [1] adopts a Möbius composition law for a bounded viability record. Its additive generator is $\operatorname{artanh}$, and independent repair and damage increments are added in that coordinate. The published version correctly distinguishes this adopted composition law from Aczél's general additive-representation theorem. That distinction is retained here.

The remaining issue is the inference from the geometry to hormesis. A permitted composition coordinate specifies how chosen increments combine; it does not select their amplitudes, slopes or functions of dose. The published threshold ordering and high-dose inequality therefore require an additional low-dose balance condition. Its approximate peak near $2D_a$ also lacks a universal parameter-independent derivation. The local flux-control argument needs a separate finite-change model.

We address the published primary model first. We then introduce two other models explicitly, rather than treating a new Hill law as an algebraic correction to a linear-dose logistic. Throughout, $D$ is a declared exposure variable and no treatment dose is inferred from the mathematics.

# 2. The published rapidity model with an exact control

Let $p_0\in(0,1)$ be baseline viability and $\rho_0=\tfrac12\log[p_0/(1-p_0)]$. Let repair and damage have positive rapidity amplitudes $\alpha,\beta$ and sigmoid occupancies $\sigma_a(D),\sigma_t(D)$. Define

$$\Delta(D)=\alpha\sigma_a(D)-\beta\sigma_t(D),$$

$$\rho(D)=\rho_0+\Delta(D)-\Delta(0),\qquad
R(D)=\frac{1+\tanh\rho(D)}{1+\tanh\rho_0}.$$

Then $R(0)=1$ exactly. The tail subtraction is needed for linear-dose logistics, whose occupancies are generally nonzero at zero dose. Equivalently, keep the original rapidity function and normalize by its actual zero-dose viability. Either normalization leaves extrema and return-to-control doses unchanged.

Because $\tanh$ is strictly increasing,

$$R(D)>1\iff\Delta(D)>\Delta(0),\qquad
\operatorname{sign}R'(D)=\operatorname{sign}\Delta'(D).$$

The baseline viability changes the peak amplitude but not its location. Its normalized upper bound is $R<1/p_0$.

## 2.1 Equal slopes in linear dose

Take the published logistic shape with common slope $s>0$,

$$\sigma_j(D)=\frac1{1+e^{-s(D-D_j)}},\qquad
0<D_a<D_t,\qquad\beta>\alpha>0.$$

Put

$$x=e^{sD},\qquad a=e^{sD_a},\qquad t=e^{sD_t},\qquad
C=\frac{\alpha}{1+a}-\frac{\beta}{1+t}.$$

Here $t>a>1$, $D\ge0$ means $x\ge1$, and

$$\Delta(x)=\frac{\alpha x}{x+a}-\frac{\beta x}{x+t}.$$

**Theorem 1.** Under these hypotheses, a positive-dose beneficial interval exists if and only if

$$\frac{\alpha a}{(1+a)^2}>\frac{\beta t}{(1+t)^2}.$$

When it exists, there is one positive-dose maximum, at

$$x_*=
\frac{\sqrt{\alpha a}\,t-\sqrt{\beta t}\,a}
{\sqrt{\beta t}-\sqrt{\alpha a}},\qquad D_*=\frac1s\log x_*.$$

The beneficial interval is $0<D<D_{\rm ret}$, where

$$x_{\rm ret}=\frac{Cat}{C-\alpha+\beta},\qquad
D_{\rm ret}=\frac1s\log x_{\rm ret}.$$

The amplitude is obtained without approximation by substituting
$\Delta(x_*)-C$ into the normalized hyperbolic response above.

*Proof.* Differentiation gives

$$\Delta_D=sx\left[\frac{\alpha a}{(x+a)^2}
-\frac{\beta t}{(x+t)^2}\right].$$

Its sign is that of

$$\sqrt{\alpha a}\frac{x+t}{x+a}-\sqrt{\beta t}.$$

The ratio $(x+t)/(x+a)$ strictly decreases, while $\sqrt{\beta t}>\sqrt{\alpha a}$. Hence the derivative can cross zero only once, from positive to negative. It does so in $x>1$ exactly when its value at $x=1$ is positive. Solving the equality gives $x_*$. If the initial derivative is zero, the maximum is the boundary point $D=0$ and all positive doses are harmful; if it is negative, the response decreases throughout $D\ge0$.

The high-dose relative rapidity is

$$\Delta(\infty)-C
=\alpha\frac a{1+a}-\beta\frac t{1+t}<0,$$

because both factors in the damage term are larger. When the initial derivative is positive, the response rises then returns once. The quadratic equation $\Delta(x)=C$ already has root $x=1$; the product of its roots gives the displayed other root $x_{\rm ret}>x_*$. $\square$

This proof exposes the missing condition in the necessity statement. The inequalities $D_a<D_t$ and $\beta>\alpha$ imply neither the displayed initial derivative inequality nor a beneficial interval.

**Counterexample.** Set $s=1$, $D_a=4$, $D_t=5$, $\alpha=0.3$, $\beta=1$. The repair threshold is lower, damage ultimately exceeds repair, both mechanisms are bounded and both increase with dose. Nevertheless $\alpha e^4/(1+e^4)^2<e^5/(1+e^5)^2$, so the exactly normalized response decreases at every positive dose. This satisfies the stated threshold and high-dose conditions while exhibiting no hormesis.

The formula for $D_*$ depends on $s$, both thresholds and both amplitudes. It cannot be reduced to a universal multiple of $D_a$. If slopes differ, the exact stationary equation is

$$\alpha s_a\sigma_a(1-\sigma_a)
=\beta s_t\sigma_t(1-\sigma_t),$$

and Theorem 1's unique-root proof no longer applies without additional analysis. The compatible reconstruction $s_a=4/D_a,s_t=4/D_t$ of Appendix A.2 has unequal slopes when $D_a\ne D_t$; Theorem 1 does not certify those reproduced peak numbers.

## 2.2 Coincident thresholds, ceilings and approximation bounds

If repair and damage have the same sigmoid shape and midpoint, then $\Delta(D)-\Delta(0)=(\alpha-\beta)[\sigma(D)-\sigma(0)]<0$ for every positive dose. Coincident thresholds therefore give no beneficial interval in that common-shape model. Different slopes require their own balance condition. For the additive Hill model below with $h=1$ and $\alpha<\beta\varepsilon$, the expansion has a negative linear term. Bounded composition permits locally linear harm; this is not an assertion of a globally proportional dose law.

Write $\ell(r)=(1+\tanh r)/2$. For the actual bounded control $p_0\in(0,1)$, normalized viability satisfies $R(D)<1/p_0$ at finite rapidity. Thus peaks of 145%, 200% and 300% of control require respectively $p_0<0.689655$, $p_0<0.5$ and $p_0<1/3$. These are necessary ceilings, not sufficient peak predictions. If the original logistic tails remain, the actual control is $\ell(\rho_b+\Delta(0))$, rather than the nominal $\ell(\rho_b)$.

The product shortcut also needs a complete calibration. For repair alone, match its saturation by $A=\ell(r+a)/\ell(r)-1$, $a>0$. Concavity gives

$$\frac{\ell(r+au)}{\ell(r)}\ge1+Au\quad(r\ge0,\ 0\le u\le1),$$

whereas convexity reverses the inequality when $r+a\le0$. Indeed $\ell''=4\ell(1-\ell)(1-2\ell)$. This chord result concerns one increment; it does not compare the full additive repair–damage model with $(1+Au)(1-v)$.

For example take $r=0$, repair rapidity $a=1$, damage rapidity $b=20$, common slope $s=1$, and $D_a=4$, $D_t=4+\log49$. With saturation-matched $A=\tanh1$, at $D=D_a$ the two occupancies are $u=1/2,v=1/50$. Dividing each curve by its own actual zero-dose value gives $R_{\rm exact}=1.08823$ and $R_{\rm product}=1.33539$. The actual exact-control rapidity is positive, about $0.01051$. Thus repair concavity does not make the full shortcut conservative.

A sufficient calibrated full bound does exist. For $a,b>0$ and $u,v\in[0,1]$, define $H=1-\ell(r-b)/\ell(r)$ and assume $r-b\ge0$. Then

$$\frac{\ell(r+au-bv)}{\ell(r)}\ge(1+Au)(1-Hv).$$

*Proof.* Since $(\log\ell)''=-4\ell(1-\ell)<0$, integrating its decreasing derivative gives $\ell(r+x-y)\ell(r)\ge\ell(r+x)\ell(r-y)$ for $x,y\ge0$. Concavity of $\ell$ on the two individual intervals bounds each factor below by its endpoint chord. Substitute $x=au,y=bv$. $\square$

The harm fraction $H<1$ and the baseline convention are explicit in this theorem. It does not supply a uniform error below 10% for the published fixed harm factor, which still needs its parameter map, range and error norm.

# 3. A distinct additive Hill model

A log-dose Hill model is a new specified choice,

$$\sigma_j(D)=\frac{D^h}{D^h+D_j^h},\qquad h>0.$$

Both occupancies vanish at $D=0$, so no control-tail correction is needed. Let
$\varepsilon=(D_a/D_t)^h\in(0,1)$, $u=(D/D_a)^h$ and retain $\beta>\alpha>0$. Then

$$\Delta(u)=\frac{\alpha u}{1+u}-\frac{\beta\varepsilon u}{1+\varepsilon u}.$$

**Theorem 2.** A beneficial interval exists exactly when $\alpha>\beta\varepsilon$. When it exists,

$$0<D<D_t\left(\frac{\alpha-\beta\varepsilon}{\beta-\alpha}\right)^{1/h},$$

$$u_*=
\frac{\sqrt\alpha-\sqrt{\beta\varepsilon}}
{\sqrt{\beta\varepsilon}-\varepsilon\sqrt\alpha},
\qquad D_*=D_a u_*^{1/h},$$

The peak rapidity increment and normalized amplitude are

$$\Delta_*=
\frac{(\sqrt\alpha-\sqrt{\beta\varepsilon})^2}{1-\varepsilon},
\qquad
R_*=
\frac{1+\tanh(\rho_0+\Delta_*)}{1+\tanh\rho_0}.$$

*Proof.* The sign of $\Delta$ for $u>0$ is that of
$\alpha-\beta\varepsilon+\varepsilon(\alpha-\beta)u$. The initial constant must be positive and the linear coefficient is negative, proving the interval. The derivative is

$$\Delta_u=\frac\alpha{(1+u)^2}
-\frac{\beta\varepsilon}{(1+\varepsilon u)^2}.$$

The ratio $(1+\varepsilon u)/(1+u)$ decreases from 1 to $\varepsilon$. Under $\beta>\alpha>\beta\varepsilon$, its crossing with $\sqrt{\beta\varepsilon/\alpha}$ is unique. Taking positive square roots and solving gives $u_*$. Substitution yields $\Delta_*$. $\square$

For fixed amplitude ratio and $\varepsilon\to0$,

$$\frac{D_*}{\sqrt{D_aD_t}}
\longrightarrow\left(\frac\alpha\beta\right)^{1/(2h)}.$$

Near onset, $\alpha=\beta\varepsilon+\delta$ with fixed $\beta,\varepsilon$ and $\delta\downarrow0$,

$$u_*\sim\frac{\delta}{2\beta\varepsilon(1-\varepsilon)},
\qquad\Delta_*\sim\frac{\delta^2}{4\beta\varepsilon(1-\varepsilon)}.$$

These onset laws are for the additive rapidity model. They differ from the multiplicative law below. The viability amplitude additionally depends on baseline: to first order in a small $\Delta_*$,
$R_*-1=2(1-p_0)\Delta_*+O(\Delta_*^2)$.

# 4. A distinct multiplicative Hill response

Now let $A$ be a fractional functional benefit, rather than a rapidity amplitude, and define

$$R_M(D)=\left(1+A\frac{D^h}{D^h+D_a^h}\right)
\frac{D_t^h}{D^h+D_t^h}.$$

The exact theorem from the companion binary-record paper is:

$$R_M>1\text{ for some }D>0\iff A>\varepsilon,$$

$$D_{M,*}=D_a\left[
\frac{A-\varepsilon}{\varepsilon+\sqrt{\varepsilon A(1+A-\varepsilon)}}
\right]^{1/h},$$

$$R_{M,*}=
\frac{(\sqrt{1+A-\varepsilon}-\sqrt{A\varepsilon})^2}{(1-\varepsilon)^2},$$

with beneficial interval $0<D<D_t(A-\varepsilon)^{1/h}$.

*Proof.* Write $x=(D/D_a)^h$ and
$R_M=[1+(1+A)x]/[(1+x)(1+\varepsilon x)]$. Then

$$R_M-1=\frac{x(A-\varepsilon-\varepsilon x)}{(1+x)(1+\varepsilon x)},$$

and the derivative numerator is
$A-\varepsilon-2\varepsilon x-\varepsilon(1+A)x^2$. This polynomial has exactly one positive root when $A>\varepsilon$ and none when $A\le\varepsilon$. Solving and substituting proves the result. $\square$

The amplitudes $A$ and $\alpha$ have different meanings. The two peak formulas are not interchangeable. When the thresholds separate, the multiplicative peak ratio tends to $[A/(1+A)]^{1/(2h)}$ relative to $\sqrt{D_aD_t}$. The existence and location depend on independently specified model content.

## 4.1 Why product composition is not automatically an approximation

For $\ell(\rho)=(1+\tanh\rho)/2$ and a small net rapidity increment $z$,

$$\frac{\ell(\rho_0+z)}{\ell(\rho_0)}
=1+2(1-p_0)z+2(1-p_0)(1-2p_0)z^2+O(z^3).$$

This expansion does not automatically equal $(1+A\sigma_a)(1-\sigma_t)$. Matching the linear term requires both amplitudes to be calibrated to the same baseline, including a harm coefficient; matching quadratic terms requires further relations and introduces cross terms. An approximation error or conservative amplitude bias therefore needs an explicitly calibrated parameter map and a domain-specific bound. A numerical illustration at chosen parameters does not establish a universal approximation theorem.

The amendment does not replace the earlier exact model by its product approximation. It retains the exact model and states the product ansatz independently.

## 4.2 Exact assay-threshold intervals

A mathematical beneficial interval begins arbitrarily close to zero dose in these hormetic branches. A finite detectable fold-width requires a stated response threshold. Let the assay criterion be $R>1+\delta$, $\delta>0$, and let $R_*$ be the actual normalized peak.

**Theorem 3.** In the hormetic branches of Theorems 1–2 and the multiplicative Hill model, a strict detectable interval exists exactly when $\delta<R_*-1$. Its two endpoints are the positive roots given below. At equality the endpoints merge to the peak and no strict interval remains.

For normalized viability, a cutoff at or above $1/p_0$ gives no interval. Otherwise $p_0(1+\delta)<1$ and define

$$z_\delta=\frac12\log\frac{(1+\delta)(1-p_0)}{1-p_0(1+\delta)}.$$

For the published equal-slope logistic model set $c=C+z_\delta$. The interval is where

$$B_xx^2-K_xx+cat<0,\qquad
B_x=\beta-\alpha+c,\quad K_x=\alpha t-\beta a-c(a+t).$$

Its roots $1<x_-<x_*<x_+$ give $D_\pm=\log x_\pm/s$ and dose-width ratio $\log x_+/\log x_-$.

For additive Hill viability, the interval is where

$$B_uu^2-K_uu+z_\delta<0,$$

$$B_u=\varepsilon(\beta-\alpha+z_\delta),\qquad
K_u=\alpha-\beta\varepsilon-z_\delta(1+\varepsilon).$$

For the product Hill response replace these coefficients by

$$B_u=\varepsilon(1+\delta),\qquad
K_u=A-\varepsilon-\delta(1+\varepsilon),$$

and replace the constant term by $\delta$. In each Hill case the two positive roots give $D_\pm=D_au_\pm^{1/h}$ and width $(u_+/u_-)^{1/h}$.

*Proof.* Inverting $\ell(\rho_0+z)>p_0(1+\delta)$ gives $z>z_\delta$. Multiplication by the positive response denominators gives each displayed quadratic. The previously proved single-peak property, together with zero-dose control and the harmful high-dose limit, gives two crossings precisely below the peak. Their order and the dose conversions follow. $\square$

These laws use both threshold edges. Substituting the zero-gain return dose for the upper edge at a positive cutoff overstates the detectable width. For an additive Hill rapidity cutoff $0<q<\Delta_*$, the roots are

$$u_\pm=\frac{K\pm\sqrt{K^2-4\varepsilon(\beta-\alpha+q)q}}
{2\varepsilon(\beta-\alpha+q)},\qquad
K=\alpha-\beta\varepsilon-q(1+\varepsilon).$$

As $q\downarrow0$, the width diverges as

$$\frac{D_+}{D_-}\sim
\left[\frac{(\alpha-\beta\varepsilon)^2}{\varepsilon(\beta-\alpha)q}\right]^{1/h}.$$

The assay cutoff is operational data, and a statistical significance criterion additionally needs its noise and replication model. No universal 8–80-fold detectable zone follows from bounded composition. The Appendix A.2 peak range can be reproduced by one relative-slope protocol $s_a=4/D_a,s_t=4/D_t$ in the product-logistic shortcut; this compatible reconstruction does not establish the original unstated protocol or its uniqueness.

# 5. Local control and finite molecular changes

Metabolic control analysis defines the local coefficient

$$C_i^J=\frac{\partial\log J}{\partial\log E_i}$$

at a specified steady state. The summation theorem $\sum_i C_i^J=1$ follows under the relevant uniform enzyme-scaling hypotheses [2,3]. It does not make the individual coefficients equal, and it does not keep them constant during a finite change. Equal control $C_i^J=1/n$ is an additional symmetry or kinetic approximation.

**Theorem 4.** In an explicitly chosen equal-resistance series model with positive rates and a fixed nonzero driving drop $\Delta$,

$$J=\frac{\Delta}{\sum_{i=1}^n 1/k_i},\qquad k_i=k,$$

increase one rate to $k(1+A_{\rm mol})$, with $A_{\rm mol}>0$, leaving the rest fixed. Then

$$\frac{J'}J=\frac{n(1+A_{\rm mol})}{n+(n-1)A_{\rm mol}},$$

$$A_{\rm func}=\frac{A_{\rm mol}}{n+(n-1)A_{\rm mol}},
\qquad \eta=\frac{A_{\rm mol}}{A_{\rm func}}
=n+(n-1)A_{\rm mol}.$$

*Proof.* The initial total resistance is $n/k$; the changed resistance is $[n-1+1/(1+A_{\rm mol})]/k$. Their ratio gives the flux fold. Subtracting one proves the remaining formulas. $\square$

Thus doubling one rate gives a flux increase of $1/3$ for $n=2$ and $1/5$ for $n=3$, rather than $1/2$ and $1/3$. The published values describe an infinitesimal linearization extended to a finite doubling. The finite correction here depends on the stated series kinetics.

For the printed parameter window $A_{\rm mol}\in[0.8,1.5]$, $n\in\{2,3\}$, the finite flux folds range exactly from $27/23$ to $10/7$, or 117.4–142.9% of control. These are conditional flux saturation factors under the series kinetics, not a predicted distribution of hormesis peaks. Partial activation, damage and the flux-to-endpoint bridge can make the actual peak smaller.

**Why the summation theorem alone cannot select the correction.** The homogeneous model
$J=(\prod_i E_i)^{1/n}$ has the same baseline coefficients $C_i^J=1/n$ and satisfies the summation theorem, but its finite fold is $(1+A_{\rm mol})^{1/n}$. Different admissible flux functions therefore agree locally and disagree for finite changes. A physical attenuation factor requires measured kinetics or a justified response function, not only a pathway-step count.

The effect of a multifunctional effector on several survival processes also requires an explicit endpoint-combination model. Neither the summation theorem nor the series model proves a universal multi-target attenuation or explains a population distribution of peak amplitudes without further biological inputs.

# 6. What remains testable

The earlier paper reports agreement with broad database features and qualitative threshold ordering in several systems. This amendment does not reclassify those comparisons as blind quantitative validation. A threshold-ordering observation does not test the missing amplitude–slope condition or an exact peak formula. Nor can an activation EC50, toxicity onset and toxicity IC50 be substituted for one another.

A decisive matched-endpoint experiment measures the repair and damage dose curves, their amplitudes and slopes, baseline viability, and the functional response in the same system. The component measurements determine the model before its response curve is inspected. Held-out dose points then test the onset, peak and return-to-control predictions, with replicate-based power sufficient for the predicted amplitude. A second experiment measures molecular induction and flux or protection together to distinguish a local control approximation from a finite-change law.

The framework remains useful because it makes these requirements explicit. The bounded record and its adopted composition law can be mathematically complete while a particular biological response is conditional on its independently established increments. No peak, pathway or therapeutic optimum follows merely from naming the record bounded.

# 7. Relation to the correction notice

The accompanying proposed corrigendum identifies the affected sections of the published article. This follow-up supplies the full proofs and new, explicitly scoped response laws. It should be linked to the original journal DOI and its SSRN versions, while preserving their historical text and date. Acceptance of a journal correction is for the editor; posting this mathematical amendment does not by itself alter the published article.

# Acknowledgements and declarations

Prepared with assistance from Claude and OpenAI Codex. All equations and model boundaries were independently checked; the general results are established by the proofs. This contribution contains no new clinical, human or animal experiment and makes no treatment recommendation. The author remains responsible for review and submission. The accompanying reproducibility files supply numerical checks and no newly collected biological dataset.

# References

1. Murray DJ. Hormesis as a geometric necessity of bounded adaptive systems: quantitative predictions from first principles. *Dose Response*. 2026;24(3):15593258261469171. doi:10.1177/15593258261469171.
2. Kacser H, Burns JA. The control of flux. *Symp Soc Exp Biol*. 1973;27:65-104.
3. Heinrich R, Rapoport TA. A linear steady-state treatment of enzymatic chains. General properties, control and effector strength. *Eur J Biochem*. 1974;42:89-95. doi:10.1111/j.1432-1033.1974.tb03318.x.
4. Aczél J. *Lectures on Functional Equations and Their Applications*. Academic Press; 1966.
5. Murray DJ. Hormesis as a geometric necessity of bounded adaptive systems: quantitative predictions from first principles. SSRN preprint, 1 June 2026. doi:10.2139/ssrn.6858819. Earlier version: doi:10.2139/ssrn.6754378.
