# Light experiments: protocol, controls and bench checks

Declared 25 September 2026, before any data. Changing a window or rule below after
seeing results means writing a new version of this file, not editing this one.

## The question

Does light from the headband's optics (or an external 850 nm LED), delivered either on
a fixed schedule or in response to your brain signals, change your position in the
state map compared with sham, and does it survive the controls below?

## What the headband's own light can do

The Athena's optics are controlled only by choosing a sensor preset (documented by
OpenMuse from the data packets):

| Preset | EEG | Optics | Used as |
|---|---|---|---|
| p20 | 4 channels | off | baseline, light off |
| p1035 | same 4 channels | inner 850 nm IR + 730 nm near-IR | "small" dose |
| p1041 | 8 channels | all 16 optical channels incl. 660 nm red | "larger" dose |

Switching presets halts the headband and restarts it, giving a stream gap of about half
a second. Whether the preset really gates the emitters is **not yet verified on
hardware**; that is bench check 1. 730 nm can be faintly visible and 660 nm is visible,
so blinding is measured, not assumed.

## Fixed light trials (Light trials panel)

- Trials per run: 12, in randomized blocks of 4 (2 real, 2 sham).
- Timeline: 20 s baseline, switch on, burst (8 s small, 15 s larger), switch back, 25 s
  observation, blinding guess, 10-25 s rest.
- Sham: the same command sequence at the same times, re-sending the baseline preset, so
  both arms have identical stream gaps.
- "Nothing" phase: every trial is sham. This is the null run: it shows what switching
  alone does to the map.

## Declared outcome windows

Light trials (`python -m ida_live light-report`):
- pre: [on - pre_s + 1, on - 0.5) s
- post: [on + 3, off) and [off + 3, off + 20) s, excluding 3 s after every switch
- measures: change in map displacement d (primary), change in alpha_tp (secondary)
- switch check: forehead low-frequency amplitude in the 3 s after each switch minus pre.
  This is where an electrical step shows up. It is reported, never used as an outcome.
- test: real minus sham, permutation p-value reshuffling within the original blocks.
- blinding: correct guesses among decided guesses, exact binomial test against 50%.

Recipes (`python -m ida_live recipe-report`): windows are declared inside each recipe's
`outcome` field, before the run.

## Bench checks before any session on you

1. **Camera check (5 min).** Many phone front cameras see 850 nm. Film the headband's
   inner sensors in a dim room while a "Nothing" run and a "Small" run switch presets.
   Confirm the emitters really go dark in p20 and light in p1035. If they don't, the
   headband cannot be used as a dose and only the external LED remains.
2. **Sponge, Nothing.** Headband on a wet sponge (salt water), tick Bench test, run the
   Nothing phase. This gives the null spread of the map with no brain present.
3. **Sponge, Small.** Same, Small phase. Any real-minus-sham difference here is the
   hardware itself (electrical step, optical crosstalk into the electrodes). A
   difference on you smaller than this is not evidence of a brain effect.
4. **Covered LED** (external LED only). A recipe with the LED under opaque tape, "LED
   covered" ticked. Separates electrical from optical effects.

## On you

5. Nothing phase: learn what switching feels like and see the null spread on you.
6. Small phase over several sessions. Larger only after Small has been analysed.
7. Recipes: a closed-loop recipe and its open-loop twin, each with a covered-LED run.

## What would count

An effect counts only if all of these hold:
- real minus sham is consistent across sessions;
- it is larger than the sponge result;
- it survives covering the LED;
- your guesses were not reliably right, or the effect holds in trials where you guessed wrong.

Anything less is a lead for the next experiment, not a finding.

## Safety notes

The headband's optics run at the firmware's own levels in every preset; this app only
chooses between presets. For the external LED, see docs/HARDWARE.md: 850 nm is invisible,
so the eye has no blink reflex to it. Mount it against the forehead, never pointing at
the eyes, and keep within the LED's rated current.
