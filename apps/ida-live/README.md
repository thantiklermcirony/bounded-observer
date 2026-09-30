# IDA Live

The live instrument of the IDA programme. It reads a Muse S Athena over your laptop's
Bluetooth, places your state as a point in a hyperbolic (Poincaré disk) map against a
frozen personal reference, and runs blinded, sham-controlled light experiments, either
on a fixed schedule or triggered by your own brain signals. Every setting is a knob you
can change live, and every change is written into the recording.

It is a research tool for self-experiment. It is not a medical device, it does not
diagnose anything, and nothing it shows has been validated yet. The calibration gate
and the sham controls exist so that the data can tell us which parts work.

**Version 0.10.0.** This is the working research instrument, with tests configured to run in CI.
Raw session recordings are excluded from this repository. What it does not yet have is the Recoverability Instrument —
a fixed perturbation battery, an independent behavioural outcome and a leave-session-out read
gate — which `docs/IDA_EVOLUTION.md` argues is the only step that can show whether return
dynamics carry real information. That is the next build.

## Install (Windows)

1. Double-click **IDA-Live-Setup.exe**. If Windows shows "Windows protected your
   PC", click **More info**, then **Run anyway**. That warning appears because the
   installer isn't code-signed yet, not because anything is wrong with it.
2. Click through the installer. It needs no admin rights and nothing else installed; it
   brings its own Python.
3. Open **IDA Live** from the desktop icon or the Start menu. It opens in its own window
   (Edge's app mode: no tabs, no address bar). Closing the window closes IDA Live and
   saves any recording.
   **IDA Live (simulated headband)** in the Start menu lets you try everything without
   the headband.
4. For the headband: switch it on, close the Muse app on your phone (the headband
   talks to one device at a time), then **Find headband** and **Connect**.

Use **Quit** in the top bar to close it. Your recordings, references, recipes and
settings are in **Documents\IDA Live**; the Start-menu shortcut **My recordings** opens
that folder, and uninstalling (Settings › Apps) never deletes it. If something goes
wrong, `Documents\IDA Live\ida_live.log` has the details.

Developers can run from source: `install.bat`, then `Start IDA Live.bat`. The installer is
rebuilt with `packaging/build_windows.sh`. Tests: `python -m pytest tests`.

This folder is part of [The Bounded Observer](../../README.md). IDA Live is where the
programme's six gates run on a living mind: a frozen reference (access), return and residue
(state), sealed real-against-replay rounds (action), feature rapidities composed by Möbius
addition (chart), the Poincaré disk map with the flat map alongside as comparator (geometry),
and a pre-declared calibration gate (prediction).

## A session, start to finish

The big button at the bottom always shows the next step.

1. **Connect.** Pick your headband (or the simulated one).
2. **Fit.** Until the signal is clean enough the button reads "Fitting · signal %". The
   panel above it names any sensor that is reading muscle, noise or nothing, and what to do.
3. **Calibrate** (2 minutes, still, eyes open, soft gaze). This freezes your reference.
   A calibration that looks like noise is refused rather than saved.
4. **Start recording.** Thought probes ask where your attention was. Press **D** when you
   catch yourself drifting, **M** to drop a named marker.
5. Optional: **Control › Light trials** (fixed schedule) or **Control › Recipes** (brain-triggered).
6. **End recording.** A plain-text `summary.txt` is written into the session folder, and
   **Control › Sessions** shows every recording as charts.

## The view

Five lenses (keys 1-5), all showing the same live signal:

| Lens | What you see |
|---|---|
| Stream | You at the centre of a hyperbolic plane. Each band is a wave riding its own lane; new samples appear at the front horizon ("now") and are carried past you to the back horizon. |
| Tunnel | The same waves in first person, flying out of the distance and past you. |
| Map | Your IDA state: your point against the frozen reference, with trail, residue halo, drift, probes. |
| Aurora | The whole spectrum, 1-45 Hz around the circle, flowing outward in time. |
| Web | The four sensors and how strongly each pair moves together, per band; ripples show each sensor's rhythm. |

Filters (key F) apply to every lens: which bands, line thickness from amplitude,
rainbows where signals move together, left/right hemispheres, IDA coupling (your state
moves the whole field), grid, speed, wave height, tilt, glow. **H** hides everything but
the view. The panel on the left shows the measures live: Φ, LZ complexity and the
alternation bias δ from the Murray Reality Equation, the 1/f exponent, and the IDA
displacement, residue and return.

## Claude can drive it

While IDA Live runs, the folder `Documents\IDA Live\control` lets Claude read your live
state (`live.json`, every second) and send commands (`inbox`): change the view or any
knob, add markers, start and stop recordings, read any session, run the reports.
Everything Claude changes is written into the recording, tagged as Claude's. Details in
docs/CONTROL.md.

## What gets written

Plain text only; Notepad opens every file: `summary.txt`, `state.csv`, `features.csv`,
`eeg.csv`, `events.jsonl`, `manifest.json`, `raw_ble.txt` (the untouched headband bytes).

## First runs, in this order

Follow docs/IR_PROTOCOL.md, "Bench checks before any session on you". In short: phone
camera check, sponge with "Nothing", sponge with "Small", then the "Nothing" phase on
you, then "Small".

## Where things are

| Folder | What it holds |
|---|---|
| `ida_live/` | the app (sources, features, geometry, state, actuators, protocols, analysis) |
| `web/` | the display |
| `maps/` | state-map definitions (compass directions, weights, composition) |
| `recipes/` | stimulation recipes; drop new JSON files here or paste them in the app |
| `hardware/` | firmware for the optional external 850 nm LED driver |
| `docs/` | design, gate, protocols, recipes, hardware |
| `sessions/` | your recordings (created on first use) |
| `references/` | frozen references (created on first calibration) |

## Documents

- docs/DESIGN.md: how it is built and how to extend it (new sensors, actuators, maps)
- docs/RECIPES.md: the recipe and pattern language, and how to ask Claude for new ones
- docs/IR_PROTOCOL.md: light trials, bench checks, what each control rules out
- docs/GATE.md: the pre-declared test the map has to pass
- docs/HARDWARE.md: building the external LED driver

MIT licence. Third-party material is listed in NOTICE.md.
Daniel John Murray, 2026.
