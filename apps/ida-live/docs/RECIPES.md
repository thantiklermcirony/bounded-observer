# Recipes: brain-triggered and scheduled stimulation

A recipe is a JSON file in `recipes/` (or pasted into **Control › Recipes**). It says
when to fire, what to fire and how the run is controlled. The app checks every recipe
before it will run it and explains what is wrong if it can't.

## Anatomy

```json
{
  "name": "alpha dip lift",
  "description": "When alpha behind the ears dips, fire a gentle 10 Hz burst.",
  "actuator": "external_led",
  "pattern": {"type": "burst", "pulse_hz": 10, "duty": 0.3, "duration_s": 2, "intensity": 0.2},
  "trigger": {"when": "clean and z_alpha_tp < -1.0", "hold_s": 3, "refractory_s": 30},
  "randomize": 0.5,
  "outcome": {"pre_s": 5, "post_s": 20, "exclude_s": 2, "measures": ["d", "z_alpha_tp"]},
  "limits": {"max_fires": 30, "max_minutes": 30}
}
```

| Field | Meaning |
|---|---|
| `actuator` | `external_led` (fast, needs hardware/ir_led_driver), `muse_optics` (the headband's own light, 1 s steps at best), `sim_led` (simulator) |
| `pattern` | what the light does on each fire (see below) |
| `trigger.when` | a condition on your live state; fires once it has been true for `hold_s` seconds |
| `trigger.refractory_s` | minimum pause after a fire before the next can happen |
| `trigger.every_s` | instead of `when`: fire at random intervals between [min, max] seconds (open loop) |
| `randomize` | chance each trigger is real rather than sham. 0.5 is the default and the fair test |
| `outcome` | the windows and measures the report uses. Declare them before running |
| `limits` | stop after this many fires or minutes |

## Patterns

| Type | Example | What it does |
|---|---|---|
| steady | `{"type": "steady", "duration_s": 8, "intensity": 0.3}` | on for 8 s |
| burst | `{"type": "burst", "pulse_hz": 40, "duty": 0.5, "duration_s": 1, "intensity": 0.2}` | 40 pulses in 1 s |
| ramp | `{"type": "ramp", "pulse_hz": 10, "duty": 0.3, "duration_s": 3, "intensity_from": 0.02, "intensity_to": 0.3}` | pulses that brighten as they go |
| train | `{"type": "train", "repeat": 5, "gap_s": 1.5, "burst": {...}}` | a burst repeated with gaps |
| sequence | `{"type": "sequence", "steps_ms": [[5, 45], [5, 45], [200, 800]], "intensity": 0.2}` | any on/off timing you like |

`intensity` runs from 0 to 1 of the LED driver's range (ignored by `muse_optics`, which is
either on or off). Hard ceilings: knobs `actuators.max_on_s_per_fire` and
`actuators.max_intensity`, plus the limits compiled into the LED firmware.

The headband's own light refuses anything faster than one switch per second, because
every switch halts and restarts the headband and blinds the EEG for about half a second.
Fast pulses need the external LED.

## Conditions

Variables:
- `clean`: true when there is no blink, movement, muscle or contact problem.
- The map: `d` (displacement), `x`, `y`, `angle`, `drift_d`.
- `z_alpha_tp`, `z_beta`, `z_theta_af`, `z_aperiodic`: each map feature in
  reference units (1 = one robust spread of your calibration).
- Raw features: `alpha_tp`, `theta_af`, `beta`, `delta_af`, `aperiodic`, `emg_tp`,
  `alpha_theta`, `heart_bpm`.
- `minutes`: time since the recipe started.

Operators: `and or not < <= > >= == != + - * /` and `abs() min() max()`.
Nothing else can run inside a condition. A variable that isn't available (for example
heart rate with the optics off) makes the condition false, never an error.

Examples:
- `clean and z_alpha_tp < -1.0`
- `clean and d > 1.2 and minutes > 5`
- `clean and abs(z_theta_af - z_alpha_tp) > 2`

## Why half the triggers are sham

A trigger fires when you are at an extreme, and from an extreme signals drift back
toward normal on their own (regression to the mean). If every trigger were real,
"fire when alpha dips, then alpha rises" would look like success even if the light did
nothing. Sham triggers happen in the same states at the same moments with the light
off, so **real minus sham** is the light's own effect. The report also prints the sham
change on its own, so you can see how large the self-return is.

Which triggers were real is sealed in a file hashed at the start and revealed only when
you press Reveal after the run.

## Two comparisons worth running

1. **Does reacting to the brain matter?** Run a closed-loop recipe (e.g. "alpha dip
   lift") and its open-loop twin ("schedule control": the same pattern at random times).
   If both show the same real-minus-sham effect, the brain-state trigger isn't adding
   anything.
2. **Is it light or electricity?** Repeat a recipe with the LED covered in opaque tape
   (tick "LED covered"). The electronics still switch but no light reaches you. An
   effect that survives covering is electrical, not optical.

A pulse rate inside an EEG band (10 Hz, 40 Hz) needs the covered run. Any electrical
leakage from the LED wiring appears in the EEG at exactly that frequency and would look
like entrainment.

## Asking Claude for changes

Describe what you want in plain words, for example:

> "Make a recipe that fires 40 Hz bursts of 5 ms pulses for 1 second whenever my
> forehead theta has been high for 5 seconds, brightening from 5% to 30% over three
> bursts, at most 20 times."

Claude replies with a recipe JSON. Paste it into **Control › Recipes**, press **Save
recipe**, select it and **Start selected**. Nothing about the app needs to change for a
new recipe. If you want something the pattern or condition language can't express yet,
Claude changes the Python in `ida_live/actuators.py` or `ida_live/protocols/recipe.py`
and you replace those files.

Knobs work the same way: "set the smoothing to 1 second" means the knob
`state.smooth_tau_s`. You can change it in **Control › Knobs**, and **Save all** writes
your settings to `settings.json` so they persist.
