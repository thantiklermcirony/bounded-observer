---
title: "One Motion on the Line"
subtitle: "Filters, mixture curvature and competing responses in a bounded two-outcome record"
author: "Daniel John Murray"
date: "12 October 2026 — revised working version 3.1"
abstract: |
  A positive two-outcome record has a projective log-odds coordinate. Fixed diagonal filters translate this coordinate and compose the normalized bias by the Einstein addition formula. We show exactly how specified exponential growth, Boltzmann weighting and all-or-none binding models realize this same action. For fixed-rate mixtures, log-odds curvature is the difference of the within-group rate variances, rather than total hidden heterogeneity. We derive the transformation under a variable common clock, establish the finite-atomic criterion for constant-coefficient linear moment closure, and give counterexamples to broader identifiability claims. For an explicitly specified multiplicative Hill benefit–harm response, we prove a necessary and sufficient beneficial-interval condition, its unique peak, its exact amplitude and its threshold asymptotics. This response model is distinct from an additive-rapidity viability model. The results are conditional mathematical laws with experimentally stated model assumptions; boundedness alone does not force exponential growth, a Hill response, a common clock or hormesis. The line construction is self-contained and does not require a quantum or gravitational reconstruction. It supplies a practical common language for several biological models and their falsification.
keywords: "log odds; bounded records; selection; hidden heterogeneity; biological clocks; hormesis; Hill response"
---

Independent Researcher, Melbourne, Australia. ORCID: 0009-0005-1794-5945.

# 1. The operational record

Two positive amounts $x_A,x_B$ define a share $p=x_A/(x_A+x_B)$, odds $o=x_A/x_B$ and bias $b=2p-1$. Amounts add; their normalized ratios do not. A simultaneous rescaling of the amounts leaves the record unchanged. We study that projective record and its specified operations.

A fixed positive diagonal filter sends $(x_A,x_B)$ to $(a x_A,c x_B)$, with $a,c>0$. Normalization after the operation gives another share. This hypothesis is stronger than boundedness or a verbal statement that two interventions are independent. Type conversion, adaptive response, changing rate distributions and other operations may lie outside this filter class.

**Theorem 1.** The Hilbert projective distance on the positive orthant is

$$d_H(x,y)=\left|\log\frac{x_Ay_B}{x_By_A}\right|.
$$

In the coordinate $\theta=\log o$, a diagonal filter is translation by $\log(a/c)$. With $r=\theta/2=\operatorname{artanh}b$, its bias action is

$$b\longmapsto\frac{b+\tanh\left[\frac12\log(a/c)\right]}
{1+b\tanh\left[\frac12\log(a/c)\right]}.$$

Every continuous scalar coordinate which translates by a state-independent increment under all these filters is affine in $\theta$.

*Proof.* The orthant formula is $\log[\max_i(x_i/y_i)/\min_i(x_i/y_i)]$, which for two components is the displayed absolute log ratio. The filter multiplies $o$ by $a/c$. The bias formula follows from addition of hyperbolic tangents. If a continuous coordinate $f$ obeys $f(\theta+t)-f(\theta)=g(t)$, composition gives $g(s+t)=g(s)+g(t)$, so continuity gives $g(t)=kt$ and $f(\theta)=k\theta+f(0)$. A nondegenerate coordinate has $k\ne0$. $\square$

The result selects the logit within this declared operation class and reading normalization. It does not make every bounded associative law a hyperbolic law. Aczél's additive representation theorem supplies a generator for a law already specified; different laws admit different monotone charts [1]. In one dimension the resulting metric line is isometric to the real line. Its hyperbolic description concerns the bounded projective chart and its embedding along a diameter of a Lorentz-cone ball, not nonzero intrinsic one-dimensional curvature.

The same two weights can be embedded as a diagonal qubit record. That embedding is optional for this paper: all proofs below use positive weights directly. They do not require the full reading–motion correspondence that selects complex quantum records in the companion foundation paper.

# 2. Three realizations of the filter

**Proposition 2.** The following specified models act by log-odds translation.

1. Constant-rate independent growth, $x_j(s)=x_j(0)e^{r_js}$, gives $\theta(s)=\theta(0)+(r_A-r_B)s$.
2. Boltzmann weights $x_j=g_j e^{-\beta E_j}$ give $\theta=\log(g_A/g_B)-\beta(E_A-E_B)$.
3. A binding model with only unbound and completely bound states and odds $o=(D/K)^h$ gives $\theta=h\log(D/K)$ and $p=D^h/(D^h+K^h)$.

*Proof.* Each stated model multiplies the two positive weights by factors independent of their current ratio. Taking the log ratio proves every formula. $\square$

Relative fitness, energy bias and log concentration are therefore different parameterizations of the same declared record action. The biological identification and units remain part of each model. In particular, mass action with several partially bound states gives a binding polynomial. Its observed occupancy need not be an exact Hill curve. A Hill exponent can be independently measured or justified by an all-or-none model; it is not selected by projective geometry [2,3].

**Corollary 3.** Two fixed diagonal interventions have additive logit increments, unit logit slope and no order effect.

This is an experimentally restrictive statement once the intervention protocol and retained outcomes are specified. A different slope or order effect rejects that class. It does not identify its cause uniquely. Even two fixed type-converting Markov matrices can fail to commute without feedback. The algebra of general positive maps is larger than the algebra of invertible diagonal filters. Birkhoff nonexpansion or strict contraction applies under its own hypotheses; an invertible diagonal filter is an isometry [4].

# 3. Mixtures and their exact curvature

Let $\mu_A,\mu_B$ be positive measures of initial subtype amounts and fixed growth rates. Assume their moment-generating functions are finite on an open interval containing the clock values of interest:

$$A(s)=\int e^{rs}d\mu_A(r),\qquad B(s)=\int e^{rs}d\mu_B(r).
$$

Define current subtype distributions by exponential tilt,

$$d\nu_{A,s}(r)=\frac{e^{rs}d\mu_A(r)}{A(s)},
\qquad d\nu_{B,s}(r)=\frac{e^{rs}d\mu_B(r)}{B(s)}.$$

**Theorem 4.** For $\theta(s)=\log[A(s)/B(s)]$,

$$\theta_s=\bar r_A-\bar r_B,\qquad
\theta_{ss}=\operatorname{Var}_A(r)-\operatorname{Var}_B(r).$$

More generally, $\theta^{(m)}$ is the difference of the $m$th cumulants of the tilted distributions.

*Proof.* Differentiation under the integral gives $A'/A=\bar r_A$ and

$$\frac{d^2}{ds^2}\log A=\frac{A''}{A}-\left(\frac{A'}A\right)^2
=\operatorname{Var}_A(r).$$

The same holds for $B$; subtraction proves the result. The higher derivative statement follows from the tilted log-partition function. The exponential-moment hypothesis justifies the required derivatives. $\square$

The formula relates to selection identities [5,6], but its content is a difference of variances. It does not measure total hidden variety or establish that a straight line contains only one subtype in each group.

**Counterexample.** Equal initial weights at rates $1,3$ in group $A$ and $0,2$ in group $B$ give

$$A(s)=e^s+e^{3s}=e^s(1+e^{2s}),\qquad B(s)=1+e^{2s}.$$

Thus $\theta(s)=s$ exactly, although both groups have nonzero variance. The two variances coincide and cancel. Detecting hidden variety from a zero bend requires an independent constraint on one group's distribution.

## 3.1 Removing a common clock assumption

Suppose the actual rate of every subtype is $r_j(t)=a(t)r_j^0+b(t)$, with $a(t)>0$. Set $s(t)=\int_0^t a(u)du$. The common term $b$ cancels from the log ratio, while the chain rule gives

$$\theta_t=a\Delta\bar r,\qquad
\theta_{tt}=a^2\Delta\operatorname{Var}+a'\Delta\bar r.$$

Hence the corrected curvature is

$$\frac{\theta_{tt}-(a'/a)\theta_t}{a^2}
=\operatorname{Var}_A(r^0)-\operatorname{Var}_B(r^0).$$

Laboratory curvature can therefore occur without fixed-rate heterogeneity. A time chart must be independently calibrated or declared before interpreting the bend. Fitting a clock from the same response later tested against it creates an additional statistical model-selection problem.

This issue does not require treating physical time as a universal primitive. For two positive filter processes with a common evolution parameter, their accumulated log changes can be compared relationally. Eliminating that parameter leaves a trajectory relation invariant under every common increasing reparameterization. The interpretation of that relation still depends on the actual common process.

## 3.2 What finite closure means

For a positive rate measure define the unnormalised tilted moments $M_j(s)=\int r^j e^{rs}d\mu(r)$. Then $M_j'=M_{j+1}$.

**Proposition 5.** A fixed constant-coefficient linear recurrence for the complete moment sequence has finite order $k$ exactly when the positive rate measure has at most $k$ distinct rate atoms. The minimal order equals the number of distinct atoms of positive weight.

*Proof.* If the support is $r_1,\ldots,r_k$, the polynomial $P(r)=\prod_i(r-r_i)$ vanishes on the support. Multiplication by $r^j e^{rs}$ and integration gives the linear recurrence for every $j$. Conversely a finite-rank positive moment Hankel matrix has a nonzero null polynomial: its squared integral is zero, so the support lies in that polynomial's finitely many real roots. The rank is the number of distinct atoms, by the Vandermonde factorization [7]. $\square$

This is a statement about linear moment closure. A continuous family may have a nonlinear finite description. A Gaussian rate distribution remains Gaussian after tilting, with a moving mean and fixed variance. It supplies a counterexample to the unqualified assertion that every finite-dimensional closure requires finitely many biological subtypes. Subtypes with identical rates also cannot be counted separately by these moments.

# 4. A specified competing response

Consider the multiplicative Hill response

$$R(D)=\left(1+A\frac{D^h}{D^h+D_a^h}\right)
\frac{D_t^h}{D^h+D_t^h},\qquad A>0,\quad h>0,
\quad0<D_a<D_t.$$

Here $R$ is normalized to its zero-dose value, the first factor is a maximal fractional functional benefit and the second a fractional survival or retention factor. This ansatz is additional biological content. It is not the same as adding two increments in the rapidity of one viability record.

Set $x=(D/D_a)^h$ and $\varepsilon=(D_a/D_t)^h\in(0,1)$. Then

$$R(x)=\frac{1+(1+A)x}{(1+x)(1+\varepsilon x)}.$$

**Theorem 6.** A beneficial dose interval exists exactly when $A>\varepsilon$. In that case

$$0<D<D_t(A-\varepsilon)^{1/h},$$

and the unique positive peak is

$$D_*=D_a\left[
\frac{A-\varepsilon}{\varepsilon+\sqrt{\varepsilon A(1+A-\varepsilon)}}
\right]^{1/h}.$$

Its exact amplitude is

$$R_*=
\frac{\left[\sqrt{1+A-\varepsilon}-\sqrt{A\varepsilon}\right]^2}
{(1-\varepsilon)^2}.$$

If $A\le\varepsilon$, the response decreases for every positive dose and never exceeds its control value.

*Proof.* Direct subtraction gives

$$R-1=\frac{x[A-\varepsilon-\varepsilon x]}
{(1+x)(1+\varepsilon x)}.$$

This proves the interval criterion. The derivative has positive denominator and numerator

$$A-\varepsilon-2\varepsilon x-\varepsilon(1+A)x^2.$$

For $A>\varepsilon$ that polynomial decreases from a positive value to a negative value and has one positive root. Rationalizing the quadratic formula gives the displayed $D_*$. Substitution into $R$ and simplification gives the amplitude. For $A\le\varepsilon$ the derivative numerator is negative for every $x>0$. $\square$

## 4.1 Two limiting laws

For fixed $A>0$ and well-separated thresholds, $\varepsilon\to0$,

$$\frac{D_*}{\sqrt{D_aD_t}}
\longrightarrow\left(\frac{A}{1+A}\right)^{1/(2h)}.$$

The limit retains an amplitude-dependent displacement from the geometric mean. It is not a universal peak at $2D_a$ or at the unweighted geometric mean.

Near onset, write $A=\varepsilon+\delta$ with fixed $0<\varepsilon<1$ and $\delta\downarrow0$. Then

$$D_*=D_a\left(\frac{\delta}{2\varepsilon}\right)^{1/h}[1+O(\delta)],
\qquad R_*-1=\frac{\delta^2}{4\varepsilon}+O(\delta^3).$$

These limits expose the distinction between an algebraic response law and its detectability: a real peak arbitrarily close to onset can have arbitrarily small amplitude. No finite noisy assay can have uniform power to detect all allowed peaks.

## 4.2 Unequal slopes

With exponents $h_a,h_t$ the derivative condition becomes

$$\frac{A h_a\sigma_a(1-\sigma_a)}{1+A\sigma_a}
=h_t\sigma_t,$$

where each occupancy uses its own exponent. At sufficiently small dose, benefit dominates when $h_a<h_t$, harm dominates when $h_a>h_t$, and when the exponents coincide the leading coefficients give Theorem 6's onset. This local condition does not classify all possible finite-dose extrema for unequal exponents. The simple common-exponent peak theorem must not be used outside its hypothesis.

# 5. Empirical use

The theorems prescribe model checks, not biological certainty. A useful test separates calibration from prediction: measure the declared interventions, subtype rates, clock or response components independently, then predict the retained outcome on a held-out system or protocol.

Earlier programme analyses used barcoded yeast data and a later fitness dataset [8,9]. The first registered laboratory-clock curvature test failed; a fitted-clock improvement was exploratory. The second missed its registered criteria. A later power analysis can explain limited sensitivity but does not change that outcome. These statements are the programme's reported empirical record, not an independent data reanalysis in this mathematical paper.

A new curvature test needs fixed-rate clonal controls, independently estimated subtype variance, a predeclared common clock, replicate-noise estimates and a meaningful predictive comparison. A peak test needs independently measured $A,D_a,D_t,h$ and a matched functional endpoint; threshold ordering alone cannot validate the quantitative peak law. The distinction is especially important when activation and toxicity are measured in different cell systems or when one quoted threshold is an onset and the other an EC50.

# 6. Position in the bounded-observer framework

The positive two-weight record, its filters, its allowed reading and its retained model parameters are fully specified here. Its operation algebra is closed: compositions of diagonal filters remain diagonal filters and projective normalization preserves the record class. Growth, equilibrium and a specified binding model fit that algebra. More general biological operations require larger models rather than an unproved claim that every subject has already been reduced to two types.

The value of the common structure is its exactness. It states how interventions combine, which clock-dependent term alters a curvature test, what heterogeneity can and cannot be identified, and precisely when one specified competing response produces a peak. It supplies a completed mathematical module within the wider framework while leaving biological parameter selection and empirical applicability to their own evidence.

# Acknowledgements and declarations

The manuscript was prepared with assistance from Claude and OpenAI Codex. AI agreement is not empirical validation or peer review. The author is responsible for the final manuscript and its submission. This paper contains mathematical analysis and no new human or animal experiments. Numerical checks supplement the analytic proofs; all model parameters and scope conditions are stated in the text.

# References

1. Aczél J. *Lectures on Functional Equations and Their Applications*. Academic Press; 1966.
2. Hill AV. The possible effects of the aggregation of the molecules of haemoglobin on its dissociation curves. *J Physiol*. 1910;40(suppl):iv-vii.
3. Berkson J. Application of the logistic function to bio-assay. *J Am Stat Assoc*. 1944;39:357-365. doi:10.1080/01621459.1944.10500699.
4. Birkhoff G. Extensions of Jentzsch's theorem. *Trans Am Math Soc*. 1957;85:219-227. doi:10.1090/S0002-9947-1957-0087058-6.
5. Fisher RA. *The Genetical Theory of Natural Selection*. Clarendon Press; 1930.
6. Price GR. Fisher's fundamental theorem made clear. *Ann Hum Genet*. 1972;36:129-140. doi:10.1111/j.1469-1809.1972.tb00764.x.
7. Shohat JA, Tamarkin JD. *The Problem of Moments*. American Mathematical Society; 1943.
8. Schlecht U, et al. A scalable double-barcode sequencing platform for characterization of dynamic protein–protein interactions. *Nat Commun*. 2017;8:15586. doi:10.1038/ncomms15586.
9. Kinsler G, Geiler-Samerotte K, Petrov DA. Fitness variation across subtle environmental perturbations reveals local modularity and global pleiotropy of adaptation. *eLife*. 2020;9:e61271. doi:10.7554/eLife.61271.
10. Murray DJ. Hormesis as a geometric necessity of bounded adaptive systems: quantitative predictions from first principles. *Dose Response*. 2026;24(3):15593258261469171. doi:10.1177/15593258261469171.
