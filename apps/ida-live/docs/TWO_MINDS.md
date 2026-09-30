# Two minds, anywhere in the world: what the framework says, and the one game that tests it

## What the framework already commits to

Three of the programme's papers speak to minds reaching beyond themselves, and they agree:

1. **The MRE (history/R15).** An observer's information rate Φ tilts the *local* alternation of a
   quantum measurement, bounded by tanh, with the marginal rate untouched (Theorem 3: no
   signalling). **Theorem 4:** for spacelike-separated A and B, A's outcomes do not depend on B's Φ.
2. **Rapidity Coordinates for Bounded Belief (SSRN 6774878).** Two agents under joint attention
   align by a sinh force on the difference of their rapidities,
   `d(Δλ)/dt = (Φ_A − Φ_B) − 2β·sinh(Δλ)`. The paper says the coupling runs through **social
   signals (gaze, voice, posture)**: a channel.
3. **Boundedness itself (Aczél / UHL).** Every composition stays inside its interval. Influence
   composes additively in rapidity, and nothing reaches the boundary in finite steps.

Put together, there is only one consistent picture: **minds couple strongly, lawfully and
measurably through channels; each mind's reach into physics is local, bounded, and cannot carry a
message; and nothing runs backwards in time.** A game that proved thought crosses space with no
channel would not confirm this framework. It would falsify Theorem 4, the MRE as written, and the
channel mechanism of the dyad paper, all at once.

So the extraordinary claim the framework makes is not telepathy. It is that the way two minds come
into agreement follows an exact, parameter-free geometric law, and that the law switches off when
the channel is cut. That has never been measured, and it can be.

## The game: *Tether*

Two people, two headbands, two copies of IDA Live, any distance apart, joined over the internet.
Each sees a shared scene (the same footage) and a light that is their partner. Rounds are sealed
and random, and neither player knows which kind is running:

| Round | What each player sees of the other | The framework predicts |
|---|---|---|
| **Linked** | the partner's live state | alignment following `−2β·sinh(Δλ)`, with β fixed from calibration rounds; sinh beats linear and tanh coupling by Bayes factor |
| **Replay** | a recording of the partner from an earlier round, presented as live | coupling to the replay, none to the actual partner: separates belief and expectation from real coupling |
| **Severed** | nothing (each gets independently timed footage and events) | β = 0: no alignment beyond pseudo-pairs (A with B from a different round) |

Alongside, each site logs its own random-bit device:

* A's bits against A's Φ: the MRE's local prediction (κ > 0);
* A's bits against B's Φ: **nothing** (Theorem 4 covers events outside each other's light cone;
  a 100 ms bin between continents is close to that, and beyond it the MRE's local dynamics give B's
  brain no route to A's detector);
* bits generated before the round (ANU, pre-recorded): **nothing** (no influence backwards in time).

Every row of the table is a prediction that can fail. If Linked shows sinh coupling and Severed
shows nothing, the dyad paper gains its first real support and Theorem 4 survives. If Severed shows
coupling that survives the controls below, the framework as written is wrong, and so is a great
deal of physics, which is why that result would need independent replication before anyone
believed it.

### Controls that make "Severed" mean something

* **No shared input.** In Severed rounds the two players' footage, music and events are timed from
  independent seeds, so shared stimulation cannot synchronise their brains. This is the confound
  behind most published "inter-brain synchrony".
* **Commit–reveal allocation.** Each copy commits a hash of its own seed before the session and
  reveals it after. The schedule comes from both seeds together, so neither side can know or bias it.
* **Pseudo-pairs.** The null is A's round against B's recordings from *other* rounds: the same
  people and the same rhythms, with no possible link.
* **Clock sync.** A round-trip ping every few seconds keeps the two clocks within tens of
  milliseconds; the sinh dynamics play out over seconds.
* **Pre-registration.** β is fitted on calibration rounds and frozen, and the analysis code is
  hashed before the first real round, as the MRE analysis already is.

Earlier small studies reported EEG correlations between isolated partners in the early 2000s; as
far as I know they have not held up under replication. Their weak points were shared stimuli,
loose timing and flexible analysis, and the design above removes all three.

## What it takes to build

* A relay the two copies connect to (a few hundred lines; it can run on either laptop with a port
  opened, or on a small free host) carrying each person's rapidity, levers and time stamps at 4 Hz.
* A dyad engine: clock sync, the commit–reveal schedule, the partner light in the scene, and the
  Severed rounds' independent timing.
* The analysis: fit `dΔλ/dt` against sinh, linear and tanh forms with β frozen, Bayes factors,
  pseudo-pair nulls, and the cross-site bit tests.
* A second Muse and a willing partner. Roughly two to three weeks of building.

## In the right order

Tether rests on each person having a validated state variable λ: a lever of theirs that the
headband demonstrably reads. That is what the listening booth establishes. So: booth first (does
the EEG see Flow?), then the recovery battery (does it predict anything?), then Tether.
