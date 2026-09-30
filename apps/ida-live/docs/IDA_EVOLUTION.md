# Why IDA matters, and the step it has to take next

Sources: *IDA and the Boundedness Engine* (SSRN 6987278), the programme synthesis
(*The State Atlas*, Programme_Grand_Project.md, 7 Sept 2026) and the IDA brief
(AI_Benchmark_and_IDA_Brief.md, part B). Quotations are short; the argument is mine and says so
where it goes beyond the sources.

## 1. Why the programme is important

Every paper in the programme runs into the same failure: **a measurement merges histories that
have different futures.** A biomarker merges the histories that produced it; a calm-looking reading
merges a system that has recovered, one held steady by support, and one whose reserve is spent.
Once that distinction is erased, fitting the same measurement harder cannot bring it back: if two
histories give the same reading but different futures, any predictor fed only that reading gets
the same input for both. The only ways forward are more information, a narrower claim, or
predicting the mixture.

The programme's contribution is a disciplined route out of this: name what a representation
erases, build a future that exposes the erasure, and ask whether restoring the distinction earns
better prediction or better action. Its own summary of the loop:

> Declare the future → test the present → expose a missing distinction → freeze and validate a
> richer representation → test whether it changes action → test recovery after support → update the
> scope of the claim.

IDA is that loop pointed at a human mind. Its bet is that **how you come back** after being
displaced (latency, overshoot, the residue left behind) carries information about your future
capacity that **where you are** does not. That is why it matters beyond neurofeedback: recovery
is what mental health, training and performance interventions are actually trying to change, and
almost every existing tool measures a present reading instead. The synthesis puts it plainly:
"recovery is a property of subsequent capacity, not just a restored reading."

## 2. What IDA should help us learn

1. **Read (wager 1).** Do return-trajectory features predict an independent later outcome better
   than static features, strong dynamic baselines and simple recovery curves?
2. **Write (wager 2).** Does feedback gated on unresolved residue beat matched open-loop, replay
   and sham feedback on that independent outcome?
3. **Instrument.** Which channels earn their place (EEG, breathing, heart, behaviour)? That decides
   what device is worth building; the brief warns against commissioning a headband first.
4. **Real vs apparent recovery.** Drift of the baseline can look like recovery (ANDY); support can
   hold a reading steady without restoring capacity. Both need controls.
5. **Geometry.** Averaging in bounded native coordinates instead of the rapidity chart (the
   "Euclidean error") should make measurable mistakes near the boundary.

How: a frozen personal reference, sealed allocations, replay and sham arms, held-out prediction,
permutation nulls, and an outcome the controller does not produce itself. IDA Live already has
most of this machinery.

## 3. Where IDA Live stands (v0.7)

It has the read-side apparatus (frozen reference, rapidity map, residue, returns), write-side
trials (levels with sealed real and replay rounds, the TAO chamber), a learned attention
signature checked on held-out blocks, and now the MRE test. What it does **not** yet have is any
of the three things wager 1 needs:

* **A common future.** Returns are measured after whatever happened to happen (a knock in a scene,
  a probe). Different perturbations of different sizes at different moments can't be compared.
* **A matched present.** Nothing makes sure two returns started from the same measured state, so
  history and starting point are confounded.
* **An independent outcome.** Levels score how well your signal moved during feedback: the brief
  says outright that "a controller predicting its own smoothed score is not independent validation."

## 4. The next step, and why it is the only one that follows

The argument works by elimination.

* **Better visuals, more levels, a smarter controller:** they all refine the present reading and the
  write side. The merged-histories result says no refinement of the same input can answer wager 1,
  and wager 2 is uninterpretable until wager 1 holds (you cannot gate on residue before knowing the
  residue means anything).
* **New hardware:** the brief says the device should follow the measurement result, not precede it.
* **The MRE and the two-person (sinh) coupling:** separate branches. The synthesis says IDA does not
  need them to establish recovery prediction, and they don't help it.

What remains is the programme's own loop, applied to one person. The identifiability result on
"holding" makes the shape of it precise. In the balance *dG/dt = production − consumption + support*,
holding G constant reveals only the net imbalance the support offsets: it cannot separate demand,
regenerative capacity and controller response. Sitting calm in a level is holding. Only a
**calibrated perturbation panel** separates those three, and only an **independent later outcome**
shows whether the separation matters. So the next IDA has to become:

### The Recoverability Instrument: a State Atlas entry for one mind

1. **Declare the future.** Before any data: the outcome and horizon. Primary: lapses and median
   reaction time in a two-minute vigilance block (a light you catch with Space, as in the attention
   map) at the end of each session. Behaviour, not EEG, and not something the controller produces.
   Secondary: the next session's mood grid, and the rechallenge next day.
2. **A common future: the Perturbation–Return Battery.** A fixed panel, same doses every time:
   * *surprise* (a sudden sound and flash, within the app's safety limits),
   * *load* (15 s of serial subtraction on screen),
   * *support withdrawal* (music and feedback cut for 30 s: the "recovery after support" test the
     synthesis asks for),
   * *null* perturbations: scheduled, logged, nothing delivered. They measure drift and apparent
     recovery (ANDY), and every return is reported against them.
   Order is sealed and randomised; each is delivered only when your frozen state has sat inside the
   dead band for 20 s, so **every return starts from a matched present**.
3. **Test the present.** Return geometry in rapidity coordinates: peak excursion, time to return,
   overshoot, residue integral, and what is left at 30 s, minus the null-perturbation drift.
   Baselines it has to beat: the static reading at the moment of perturbation, a dynamic model of
   the last two minutes (variance, autocorrelation, critical slowing), and a simple exponential
   recovery time.
4. **Expose a missing distinction.** When two returns start from the same present and diverge, test
   candidates for what the reading erased: time on task, earlier residue, breathing rate and pacer
   lock, heart rate from the optics, mood, sleep, time of day, and Φ. Chosen on discovery sessions,
   then frozen.
5. **Freeze and validate.** Leave-session-out prediction of the declared outcome. The read gate
   passes if return features add held-out predictive value beyond all three baselines, with a
   session-level bootstrap interval excluding zero, over at least 20 sessions after the freeze.
6. **Test whether it changes action.** At matched states after a perturbation, randomise the support
   (breath pacer, holding the scene, nothing). If different states need different supports, a
   state-guided policy has something to do. Only then run wager 2: residue-gated support against
   yoked replay.
7. **Test recovery after support, and update the claim.** The same battery the next day, with no
   support, then a report that says what was shown and for what scope, including failures.

### What each result would teach

* **Read gate passes:** return dynamics are a real, measurable property of this mind, and IDA has a
  locked protocol to show an engineering partner (channels, timing, held-out performance).
* **It fails with EEG but passes with breathing or heart:** the instrument should be built around
  those channels. That is exactly the result the brief says should decide the hardware.
* **It fails everywhere:** return dynamics do not add information at this timescale. That is a clean
  negative that stops the wrong device being built.
* Mixed outcomes are informative too, as the synthesis says: good measurement with no feedback
  advantage supports the read claim but not the controller.

### How it will feel

A six-minute "recovery check" at the start and end of each session: you get knocked, you come back,
and you see how fast. The quantity trained and tracked is **recovery half-life**, not a calmer
number: "back in 6.1 s after surprise (best 5.2); 94% returned after support was taken away." That
is the honest version of "maximising your mind": resilience you can measure and that has to show up
in a task the app does not control.

A caution on depression: slow recovery from negative states is associated with depression in the
research literature, so a validated recovery measure could matter clinically. IDA Live would still
be a personal research instrument, not a treatment, until a controlled study says otherwise.

## 5. Where the MRE sits

The random-bit test runs underneath all of this, all the time, as its own falsifiable branch with
its own falsifiers. It never enters an IDA claim. Φ is one of the candidate variables in step 4:
if it helps predict recovery it earns its place like breathing or heart rate would; if it doesn't,
it doesn't.

## 6. Build order (v0.8)

1. The battery: perturbation scheduler with sealed order, matched-present trigger, null
   perturbations, safety limits (engine + levels.js).
2. The vigilance block as the declared outcome, and the next-day rechallenge prompt.
3. Return geometry with drift correction; the three baselines; leave-session-out prediction and
   the read gate as a report.
4. A discovery/validation split with a frozen-feature file, like the attention gate.
5. Only after the read gate: the support randomisation, then residue-gated vs yoked replay.
