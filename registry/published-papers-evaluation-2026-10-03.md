# The two published papers: a reading of the available extracts — 3 October 2026

An evaluation of the programme's two journal papers, written because the author rightly objected
that the review had described them only through the registry. Five independent analyses were run
for each paper: the maths re-derived and run, the empirical record, prior art, the strongest case
for, and the strongest case against. A judge then weighed them. The judge for the glutathione
paper was stopped by an automated filter, so that verdict was weighed by the lead reviewer from
the same five analyses.

**The limit on this whole document.** It reviews claims *as worded in partial preprint
extracts*. That can check specific statements, such as whether a stated condition is sufficient
or whether a printed equation has an equilibrium. **It cannot settle the value of the full
published papers.** The journal versions may differ, add analyses, or fix what is flagged here.
The "readings" below are readings of the extracts, not verdicts on the papers.

**Read this first: what was and was not read.** The published journal texts could not be
fetched; every publisher, DOI, PubMed and Europe PMC route is blocked from this environment.
The full SSRN preprints are not stored anywhere in the repositories or in the author's Drive.
The analyses rest on:
- the partial preprint extracts in `boundedness-atlas/content/atlas.json`;
- the author's own audits in `empirical-architecture/research/theory-atlas-v0.1/`;
- publication records.

The missing pages hold the hormesis paper's Eqs 1–2 and §§3.1–3.2, and the glutathione paper's
ODE system and G6PD tables. **Every conclusion below is provisional until checked against the
journal versions.** If the journal text differs, the journal text wins.

---

## 1. Murray DJ, "Hormesis as a Geometric Necessity of Bounded Adaptive Systems: Quantitative Predictions from First Principles", *Dose-Response* 24(3), 2026, doi:10.1177/15593258261469171 (SSRN 6858819)

**It is a real, peer-reviewed contribution.** [P] as a statement of record. It establishes:
- **A correct sufficient condition inside an opposing-channel model.** If repair and damage add
  independent increments, repair's low-dose contribution exceeds damage's, and damage
  eventually dominates, then the response rises above control at low dose and has an interior
  maximum. Re-derived. [P] within the model.
- **A measurable parameterisation** (Da, Dt, η, amplitudes) that ties the shape of the dose
  response to quantities that can be measured independently of the curve. This makes a
  prospective, non-curve-fitting test possible.
- **An application of the metabolic-control summation theorem to hormetic amplitude.** It
  explains why a large molecular induction yields only a modest functional gain. Within the
  sources read, this looks like a genuinely new link. [D]
- **Sharp, falsifiable predictions, honestly labelled untested:**
  - the peak near 2 × Da;
  - zone width scaling with Dt/Da;
  - amplitude classes set by pathway architecture;
  - a narrower zone in NRF2-knockout cells.

**What it does not establish.**
- **"Geometric necessity" is not accurate as stated.** [P], checked here.
  - *The stated conditions are not sufficient.* With repair before damage (Da < Dt) and damage
    eventually dominating, an amplitude condition is still needed. For n = 1 it is
    A/B > Da/Dt. A = 1, B = 3, Da = 1, Dt = 2 gives no hormetic zone at any dose; the maximum
    net rapidity is below zero.
  - *The bounded geometry does not decide whether hormesis occurs.* Any monotone readout of the
    summed increments, including the bounded tanh chart, gives the same existence, peak dose and
    zone boundaries. The geometry shapes amplitude only.
  - *The author's own record agrees.* The 7 September 2026 SSRN notice states "Boundedness alone
    does not imply hormesis", the capstone (§2.4) withdraws the claim that Aczél selects
    artanh, and audit F7 gives a bounded adaptive system with no benefit.
- **"From first principles" overstates.** The premises include independent composition, a
  logistic form and linear dose–rapidity. These are modelling choices.
- **No quantitative prediction has been confirmed prospectively.**
  - *Calabrese database:* the "match without parameter fitting" overlaps author-chosen model
    ranges with the database's published summary figures. It is not a record-level test.
  - *The 2 × Da peak law:* it depends on a sigmoid steepness the text does not report, and is
    not reproducible from the stated inputs. Under a Hill reading of the paper's own grid,
    d*/Da spans roughly 0.2–4.
  - *The three-agent check:* it tests an ordering that is close to a precondition of observing
    hormesis at all.
- **Prior art.** The opposing-process explanation of hormesis predates the paper (for example
  Stebbing 1982, and Conolly and Lutz 2004). These references were identified by the analyses
  and not re-read here. Whether the journal version cites them could not be checked.

**Reading of the extract (not a verdict on the paper).** A peer-reviewed, conditional, retrospectively consistent model. Its distinctive
predictions are open, and the necessity claim in its title overstates it.

**What would make it a discovery.** Measure Da, Dt, both steepnesses, the baseline and η
independently in one system. Freeze and publish the predicted peak dose, zone width and
amplitude. Then measure the functional dose response, and beat a generic biphasic comparator
(Brain–Cousens or Cedergreen) fitted to the same data. The NRF2-competent versus knockout
zone-width prediction would also count. **Of everything in the programme, this is the closest
existing design to an independently calibrated prediction tested against conventional
alternatives.**

## 2. Murray DJ, "A Dynamical Model of Glutathione Homeostasis in G6PD Deficiency and NRF2-Activated Non-Small Cell Lung Cancer", *Redox Biochemistry and Chemistry* 17:100084, 2026, doi:10.1016/j.rbc.2026.100084 (SSRN 6754498)

**It is a real, peer-reviewed contribution.** [P] as a statement of record. It establishes:
- **A reduced three-variable model** (GSH pool, saturable NADPH regeneration, slow NRF2-
  controlled capacity) that puts G6PD and KEAP1/NRF2 phenotypes in one parameter space, with
  two failure modes: threshold collapse, and a graded "reductive fade".
- **A retrospective calibration** that recovers known G6PD severe-deficiency contraindications.
  The paper itself calls this recovery, not new clinical knowledge.
- **A prospective, pre-specified, numerical prediction with a falsification rule.**
  - *The prediction:* adjunctive N-acetylcysteine (NAC) harms NRF2-active NSCLC patients on
    platinum chemotherapy, with stratum-A HR 1.20–2.00.
  - *The falsification rule:* falsified if HR ≤ 1.10 with the upper 95% CI below 1.30, with a
    selectivity ratio ≥ 1.30.
  - *Context:* no earlier model found by the analyses commits to such a band. It is untested,
    and the paper rates the magnitude as not robust.
- **Unusual epistemic care.** It has a claims hierarchy, retrospective trials are labelled
  "organizing context, not validation", it includes a robustness table, and it deposits
  time-stamped code (Zenodo 10.5281/zenodo.20600332, not fetched here).

**What it does not establish.**
- **It does not support hormesis.** The paper says so itself: "This three-variable GSH model
  does not produce hormesis."
- **The depleted boundary attractor fails as printed in the preprint.** At G = 0 the printed
  equation gives Ġ = V·Gmax/(KM+Gmax) − β·Vtotal, which is −1/2 at unit parameters. So G = 0 is
  not an equilibrium, and G ≥ 0 is not preserved, without an explicit boundary rule (audit F1;
  re-derived). The finite-capacity concept survives a corrected boundary model, but the onset
  of bistability moves. Whether the journal version fixed this is unknown.
- **Direction and novelty.** The direction of the NAC prediction was the prevailing preclinical
  expectation (Sayin 2014, which the paper cites). Its novelty is the numerical commitment.
  Kinetic GSH models with saturable regeneration predate it (Reed 2008, which the paper cites,
  and others named by the analyses).

**Reading of the extract (not a verdict on the paper).** A careful, peer-reviewed modelling paper with one creditable pre-registered clinical
prediction. Not yet a discovery: nothing it predicted has been measured.

**What would make it a discovery.** A trial or cohort that tests the pre-specified HR band and
selectivity ratio. Short of that, the decisive in-vitro experiment the paper itself names:
matched KEAP1-mutant and wild-type NSCLC lines, ± cisplatin × NAC.

---

## Open items

- **The journal versions of both papers must be read.** Every "provisional" above depends on it.
- **"E" in atlas row L-GSH remains undefined** (see the review, item 11).
- **Disclosure.** While looking for the published texts, one analysis read publication emails in
  the author's Gmail (SAGE and Elsevier notices), read-only, to confirm publication. Nothing was
  sent or changed.
