# The listening booth (v0.8)

Home › **Listening booth**. Pick music (the six IDA scores, your own files, or silence) and listen
for as long as you like. Three levers say how you feel:

| Lever | Top (less) | Middle | Bottom (more) | Keys |
|---|---|---|---|---|
| Flow | stuck | as usual | full flow | Q / A |
| Presence | scattered | as usual | fully here | W / S |
| Horizon | closed in | as usual | wide open | E / D |

**Space** ("This!") marks a moment that feels most alive and connected. Double-click a lever to
send it back to usual. Your own music goes in `Documents\IDA Live\music` (+ Add opens it), or drop
files onto the window.

Nothing on screen follows your brain. The IDA scores play open-loop on a slow tide of their own, so
the recording is you, not you reacting to feedback. The music's loudness is recorded every 100 ms so
the analysis can separate the music from you.

## What it tells you

After each session the experience map (Home › Results) says, per lever, whether:

* **your EEG sees it**: it predicts where you put the lever on listening it never learned from, and
  adds beyond your body;
* **body, not brain**: muscle, head motion, blinks, breathing, heart rate or the music predict it as
  well;
* **forming** or **nothing yet**.

Method and gate are in `ida_live/analysis/booth.py` (held-out correlation ≥ 0.30, circular-shift
p < 0.05, brain + body beating body alone by ≥ 0.05). Checked on simulated data: 0 of 40 null runs
passed; a planted signal passed; a muscle-only signal was called "body".

## Using it

A lever that passes can become what the levels reward: the button appears at the end of the
session, or set Control › Knobs › `levels.target` to `booth:flow`, `booth:presence` or
`booth:horizon`. Then Bloom opens at *your* felt flow instead of a textbook index.

Files: `booth.csv` in the session folder (t, the three levers 0–1, moving, peak, music, music_t,
music_level, event); `profiles/booth_latest.json` and `booth_report.html`.
