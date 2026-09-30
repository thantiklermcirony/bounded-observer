# Design

## The pipeline

```
source ──► buffers ──► features (4 Hz) ──► state engine ──► recorder, display
                                        └─► calibration, probes, light trials, recipes ──► actuators
```

The engine (`ida_live/engine.py`) owns the pipeline; the display is a client that sends
commands and draws what it receives. Everything is local (127.0.0.1).

## Built to grow: the plug-in points

| To add | Write | Register |
|---|---|---|
| a sensor (OpenBCI Cyton for the R1 headband, respiration belt, camera) | a `Source` subclass in `ida_live/sources/` | `@register("name")` |
| a feature | a `Feature` subclass in `ida_live/features/` | `@register` |
| a map | a JSON file in `maps/` | knob `state.map` |
| a stimulus device | an `Actuator` subclass in `ida_live/actuators.py` | `@register("name")` |
| a stimulation rule | a JSON recipe in `recipes/` | nothing, it is picked up live |
| an audio-visual stimulus | a `Stimulus` in `ida_live/stimuli/` (checked by the flicker guard) | |
| an analysis | a module in `ida_live/analysis/` | a command in `__main__.py` |

Raw data is always kept (`raw_ble.txt` in OpenMuse's format, plus decoded CSVs), so any
future feature, map or analysis can be re-run over old sessions.

## The IDA quantities

- **Frozen reference**: median and robust spread of each feature over a clean
  calibration, held fixed for the session (recalibration is refused while recording)
  and reusable across days. Improvement can't be manufactured by moving the reference.
- **Displacement** d: hyperbolic distance of the current point from the reference.
- **Return**: time to come back within `state.return_radius` after a probe, a trigger
  or a switch.
- **Baseline drift**: a slow running baseline (time constant `reference.drift_tau_s`)
  mapped into the same geometry.

## The geometry

Each feature's reference z-score times kappa is a rapidity. The feature becomes the disk
point tanh(rapidity/2) on its compass direction, and the points are composed by Möbius
addition in the declared order. Along a single direction this is Einstein velocity
addition (rapidities add). Across directions it doesn't commute; the order-dependence
is logged as the composition defect. Two comparators run alongside: the Einstein
midpoint (order-free) and a flat Euclidean sum mapped into the disk once. The
calibration gate tests the hyperbolic map against the flat one.

## Knobs

Every leaf of the settings and of the active map is a knob (`ida_live/knobs.py`).
Changes rebuild the processing chain on the next tick, keep the frozen reference, and
are logged as `knob` events with old and new values. Each session's manifest records
the settings and map at the start and at the end; every change in between is in
`events.jsonl` with its time.

## Later actuators, including TMS

The actuator interface accepts any device that can take a pattern and report when it
actually started and stopped. Transcranial magnetic stimulation is a different class
of intervention from a forehead LED. It can cause seizures, needs screening and is
normally run under medical supervision with purpose-built, certified equipment and
safety limits. If the data point that way, the right next step is a collaboration with
a lab that runs TMS, feeding it IDA Live's triggers, rather than a DIY headband.

## Version 0.2 (25 September 2026)

- Signal quality is judged per sensor on spread, muscle (30-45 Hz vs 4-13 Hz) and whether
  the spectrum falls with frequency; calibration needs 60% readiness and refuses a
  noise-dominated reference. The monitoring preset is p20 (all lights off).
- The first reference ever saved (0.1) was frozen on muscle/noise with the optics on; 0.2
  refuses to load references from 0.1 and asks for a new calibration.
- New measures: IDA residue with dead band and the multi-scale return score (IDA and the
  Boundedness Engine, section 6); the Murray Reality Equation's Φ and alternation bias δ,
  and LZ complexity (features.Complexity). The gate's version 2 addendum tests each as an
  awareness candidate against probe answers.
- The display is WebGL (web/js): dsp.js filters the raw 256 Hz stream into bands in the
  browser; lenses.js draws five lenses; gl.js renders soft additive light.
- control.py: the control folder for Claude. analysis/summary.py: summary.txt and the
  Sessions view.
