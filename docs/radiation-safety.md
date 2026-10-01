# Radiation safety: what a dose total leaves out

This is the source and claim ledger for the [Radiation chapter](../site/radiation.html). The chapter is an explanation of state, time, and decisions under incomplete information. Its interactive traces use **unitless, illustrative doses**. They are not estimates of an individual's cancer risk, a radiation emergency calculator, or instructions to evacuate or shelter.

The claim tags follow [`AGENTS.md`](../AGENTS.md): **[P]** is a checked source or a result proved under stated assumptions, **[D]** is a derivation or synthesis awaiting independent checking, and **[H]** is an empirical hypothesis with a test and loss condition. A mathematical result about a model does not establish that the model describes human health.

## The question the chapter tests

- **[P, conditional]** A total dose $D=a+b$ gives the same number for the histories $a\to b$ and $b\to a$. Any model whose only input is that total must assign them the same prediction. This is an input-identifiability statement, not a claim that nature must respond differently.
- **[P]** Equal nominal biologically effective dose (BED) for a reversed fraction pair is similarly built into the order-blind BED calculation. [Vetrugno et al.](https://pubmed.ncbi.nlm.nih.gov/41862030/) reported that 6+12 Gy and 12+6 Gy in immunocompetent mouse tumours separated on tumour-growth delay and immune endpoints; in vitro clonogenic survival showed no resolved order separation, and the in vivo separation was not reproduced in the immune-deficient model. Murray's reviewed [*When Equal BED Is Not Equal Biology*](https://papers.ssrn.com/abstract=7427058) analyses the test boundary. These are **therapeutic-dose, endpoint-specific** observations. They do not estimate environmental exposure risk or establish continuous SNT.
- **[P, conditional]** A reproducible reversal difference on a declared endpoint rejects a *specified* order-blind summary for that endpoint and protocol. A null result does not prove history has no effect; it may reflect a model's symmetry, noise, an insensitive endpoint, or insufficient power. The proposed state must also predict futures after a common intervention; see [Gate 2](2-state.md).

**[P, conditional]** The minimum truth is narrow and useful: **if two histories merged by a proposed summary have distinguishable future response laws, that summary was insufficient for that task**. It does not identify the missing mechanism or prescribe a safety decision.

## Continuous SNT as a candidate state model

[Jack Devanney's *Rate SNT: the continuous version of SNT*](https://jackdevanney.substack.com/p/rate-snt-the-continuous-version-of) presents a continuous dose-rate and repair model, with a [reference PDF and code](https://gordianknotbook.com/wp-content/uploads/2026/08/hazard_snt_welsh_m3.pdf). Devanney explicitly credits **Daniel Murray** for working through the mathematics and explains the add-subtract increment. Murray's [*The Acute Dose-Response Curve as a Transition Potential*](https://papers.ssrn.com/abstract=7426880), equations 20–22, develops the broader predictive-state formulation. Both contributions should be named; neither turns the candidate into a validated replacement for radiation protection models.

**[P, model definition]** In the scalar candidate, $q(t)\geq0$ is input rate, $x(t)\geq0$ is a recoverable state, $R(x)$ its recovery law, $h(x)$ a differentiable acute response potential with $h(0)=0$, and $H(t)$ an accumulated endpoint ledger:

\[
\dot x=q(t)-R(x),\qquad \dot H=h'(x)q(t).
\]

**[P, conditional]** For an ideal short pulse $d$, while recovery during the pulse is negligible,

\[
x_{+}=x_{-}+d,\qquad \Delta H=h(x_{-}+d)-h(x_{-}).
\]

- **[P, conditional]** These equations imply the add-subtract pulse rule by the fundamental theorem of calculus. They separate the state that can recover during a gap from the endpoint ledger already accumulated. The pulse identity depends on the specified scalar coordinate, additive input and observation law; it is not a measurement of DNA damage from a sievert. Effective dose in sieverts is a radiation-protection quantity, not a direct reading of one person's DNA lesions.
- **[D]** The site uses this model family to make a *state sufficiency* question visible: how much of a prior exposure must be carried forward to predict response to a later, identical challenge? Fitting $h$ alone does not answer this; $R$, initial state, population, endpoint, observation law and exposure setting also matter.
- **[H]** A calibrated continuous SNT specification will predict a held-out, endpoint-specific dose-order and gap response better than prespecified comparators. **Test:** preregister a dose pair, gap ladder, endpoint, equivalence margin and out-of-sample scoring rule; measure or perturb candidate state and then give a common challenge. **Loss condition:** held-out response distributions or gap dependence fall outside the model's declared bounds, or a simpler comparator predicts as well or better under the frozen rule. No such general human safety validation is claimed here.

### Why the identical third challenge matters

For the exhibit's simple exponential recovery, $R(x)=x/\tau$. If fraction $\rho=e^{-g/\tau}$ of state remains across gap $g$, starting from $x=H=0$, then

\[
H_{ab}=h(a)+h(\rho a+b)-h(\rho a),\qquad
H_{ba}=h(b)+h(\rho b+a)-h(\rho b).
\]

- **[P, conditional]** The formula follows directly by applying the pulse rule twice. It is exact for the stated pulse model, not for every repair mechanism. When $g=0$, both paths give $h(a+b)$; after complete recovery, both give $h(a)+h(b)$.
- **[P, conditional]** If $h(x)=\alpha x+\beta x^2$, both orders have the *same immediate ledger*, $H=\alpha(a+b)+\beta(a^2+b^2+2\rho ab)$. But the state after the pair is $x_{ab}=\rho a+b$ versus $x_{ba}=\rho b+a$. If $a\ne b$ and $0<\rho<1$, a common later pulse can separate their next increments even though the first ledger tied. This is the chapter's clearest Gate 2 example: agreement on today's endpoint does not prove equivalence under tomorrow's intervention.
- **[D]** Within the zero-initial-state, additive-input, exponential-recovery, no-gap-hazard scalar class, equality for *all* unequal pulse pairs and retained fractions characterizes a quadratic $h$ under the stated regularity assumptions. The all-pairs classification is not an inference from one finite test. More general nonlinear recovery can create reversal with quadratic $h$, and special nonlinear repair can hide reversal with nonquadratic $h$. An order effect alone cannot identify continuous SNT.

The public simulator should show **model state** and **model response ledger**, with dimensionless inputs. A plotted difference is a result of the chosen $h$ and $R$; it is not an observed health effect or a safety threshold. Do not turn the output into “mortality percentage” unless the full hazard-to-outcome model is independently calibrated for a specified endpoint and population.

**[P, code specification]** The website's live rate simulation uses two 0.55-time-unit delivery windows containing 0.80 and 0.20 **normalized** input units. The user changes their gap and the exponential-recovery time constant $\tau$. Its illustrative acute response is $C(x)=0.88[1-(1+(x/0.55)^{2.18})^{-0.55}]$ and $h(x)=-\log(1-C(x))$. The quadratic comparison uses $h(x)=x^2$. A common later exposure adds 0.24 normalized units over 0.4 time units after a fixed 0.45-time-unit wait. These numbers are chosen to make model differences visible; they are **not** Devanney's fitted parameters, a human dose scale, a calibrated biological endpoint, or a safety threshold. [Source code](../site/radiation-model.mjs) and [invariant tests](../site/radiation-model.test.mjs) fix the implementation.

### What Jack's worked example shows

- **[P, reported model output]** In Devanney's worked **model**, 100 then 700 mSv/day over one day each and the reverse order produce different calculated cancer mortality: about 0.0676 versus 0.0710. This is a prediction of its chosen curve and recovery constant, **not a measured human dose-order result**.
- **[D]** The broader research question goes beyond drawing two curves: freeze what counts as the same initial state, endpoint and common future challenge; ask whether an order-blind summary fails; then test whether the augmented state removes the difference on held-out histories. That is how a time-dependent model becomes a tool for checking what may lawfully be forgotten.
- **[P, model distinction]** The linear-no-threshold (LNT) approach used in radiation protection is a population risk extrapolation under uncertainty. Its use does not assert that cells have no repair. [ICRP Publication 147](https://www.icrp.org/publication.asp?id=ICRP+Publication+147) and the [EPA radiogenic cancer risk models](https://www.epa.gov/radiation/blue-book-epa-radiogenic-cancer-risk-models-and-projections-us-population) are appropriate context. Do not describe continuous SNT as having displaced protection guidance.

## The context horizon

Let $\mathcal U(P)$ be the exposure histories compatible with record $P$, and $\mathcal I(P)=\{F[u]:u\in\mathcal U(P)\}$ the predictions of **one fixed model** on those histories. If a refined record $Q$ only removes compatible histories, then $\mathcal U(Q)\subseteq\mathcal U(P)$ and $\mathcal I(Q)\subseteq\mathcal I(P)$. This is the conditional set-inclusion result in Murray's transition-potential paper, equations 30–33. **Status: [P, conditional].**

**[P, conditional]** That is the meaning of “more context narrows the horizon” under a fixed model. **[D]** A finer dose-time record, measured recovery, organ, age and clinical history can narrow a *conditional* prediction set. The practical set can widen again when model uncertainty, measurement error, biology and competing outcomes are honestly included. No finite record makes safety “infinitely certain,” and knowing a person's history cannot remove future chance. A risk model's uncertainty should be displayed, not hidden behind extra sliders.

## Fukushima: two real risks in one decision

**[P]** The 2011 Fukushima Daiichi accident followed an earthquake and tsunami. **[D]** The chapter uses it as a historical example of information and action under uncertainty, **not** as a retrospective simulation of what a particular household should have done. A radiation desk could see possible releases and exposure pathways; a hospital ward could see frail patients, interrupted supplies and transport strain. Neither view alone contained all outcomes. A later source can clarify the trade-off without pretending to know the one correct action for every place, hour or patient.

| Claim | Status and source | What it does **not** establish |
| --- | --- | --- |
| No adverse health effects among Fukushima residents have been documented as directly attributable to radiation from the accident; UNSCEAR does not expect a detectable population-wide increase. | **[P]** [UNSCEAR 2020/21 FAQ](https://www.unscear.org/unscear/en/areas-of-work/fukushima-report-faq.html), questions 3–4. | Zero radiation risk, zero individual radiation-caused cancers, or a universal result for other accidents. Detection against background incidence is difficult. |
| Evacuation and other protective measures also reduced radiation exposure; UNSCEAR modelled substantial avoided exposure for some locations and groups. | **[P]** [UNSCEAR 2020/21 Scientific Annex B](https://www.unscear.org/unscear/uploads/documents/unscear-reports/UNSCEAR_2020_21_Report_Vol.II-CORR.pdf), public-dose reconstruction and Appendix A. | An observed outcome for the same people had they stayed; all evacuations having the same benefit. Modelled counterfactuals are conditional on release, location, age and behaviour. |
| A review of Futaba Hospital records reports 39 of 338 inpatients died before its emergency evacuation was complete, amid staff loss, infrastructure failure, interrupted care and difficult transport. | **[P]** [Futaba Hospital retrospective](https://doi.org/10.1017/dmp.2021.265). Its authors note judicial records could not be fully medically verified. | That every death was caused solely by the act of evacuation, or that leaving these patients in a damaged, unsupported hospital would have saved them. |
| A five-home cohort of 715 Minamisoma residents found higher mortality after the disaster than before (relative risk 2.68; 95% CI 2.04–3.49); first evacuation carried more risk than later evacuations (hazard ratio 1.94; 95% CI 1.07–3.49). | **[P]** [Nomura et al., PLOS ONE 2013](https://doi.org/10.1371/journal.pone.0060192). | A clean causal comparison of evacuate versus remain: the study lacked an otherwise comparable un-evacuated control and the earthquake, tsunami, infrastructure and care disruption were intertwined. |
| Staying without adequate care was dangerous too. | **[P]** [Takano Hospital shelter-versus-evacuation cohort](https://pubmed.ncbi.nlm.nih.gov/30056383/) and [WHO Fukushima health review](https://www.who.int/news-room/questions-and-answers/item/health-consequences-of-fukushima-nuclear-accident). | That staying is generally safer. Shelter depends on building, radiation field, staff, water, power, supplies and ability to deliver care. |
| Japan's Reconstruction Agency reports 2,350 certified disaster-related deaths in Fukushima Prefecture through 31 December 2025. Its category includes illness after worsening injury or the physical burden of evacuation life after the **whole Great East Japan Earthquake disaster**. | **[P]** [13 February 2026 official report](https://www.reconstruction.go.jp/files/user/topics/main-cat2/sub-cat2-6/20260213_kanrenshi.pdf), pp. 1–2. | A count of deaths caused solely by nuclear evacuation, directly comparable to radiation-attributable deaths. Do not use it as “evacuation killed 2,350.” |

**[D]** The supported lesson is to account for **both** radiation exposure and the health cost of protective action, especially continuity of care for vulnerable people. WHO explicitly says evacuation aims to reduce radiation risk while evacuation itself can pose serious risks. “The evacuation killed more than the radiation” compresses unlike quantities into an unsupported causal ranking. “Everyone should have stayed” would be worse: it ignores radiation avoided and the danger of unsupported sheltering. The scientific and ethical task is to compare feasible, locally specified actions with uncertainty and care resources visible.

## Transfer boundaries and the next test

1. **[P, transfer boundary] Radiotherapy is not an accident exposure.** Gy fraction order in tumours, tumour-growth delay and immunity cannot be transplanted to low-dose public cancer incidence. Exposure type, organ, dose rate, endpoint, time horizon and population must be declared.
2. **[P, transfer boundary] A mathematical curve is not a safety rule.** A valid candidate may still have wrong parameters, hidden state, a wrong endpoint map, or no domain transfer. Published radiation protection guidance remains the reference for real decisions.
3. **[H] The proposed empirical test must be prospective.** Start with a qualified reversal pair, an endpoint and a gap ladder. Predeclare order contrasts and equivalence margins; replicate independently. Measure a candidate state before a common third challenge. If matching on that state fails to erase the history-dependent future separation beyond measured noise, the proposed state is insufficient. **Loss condition:** this stated failure, or inability of the frozen model to predict held-out dose orders and gaps.
4. **[P, transfer boundary] Fukushima is an observational history, not validation of continuous SNT.** No fact about the accident in this ledger is evidence that a particular acute potential $h$ or recovery law $R$ correctly predicts human cancer risk.

The research register's dated [RAD-1 and RAD-2 records](../registry/legacy/atlas-2026-09.json) retain their own status and next tests. The current programme's [L-03 and L-08 entries](../registry/atlas.csv) connect this chapter to the manuscript record. Historical sources here are read with the same rule as the [Inside real-case ledger](inside-real-cases.md): distinguish what was known then, what a later source supports, and what remains a counterfactual.
