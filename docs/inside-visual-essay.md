# Inside · story and production notes

The public piece is an original, narrated, captioned visual story. Its fictional
river valley lets one observer discover that an inherited account shaped what
they expected to see. The camera then pulls above two observers and shows their
different projected futures. A shared fact makes a joint action visible, while
cost and uncertainty remain. `site/inside-film.mjs` carries the timed captions,
claim statuses and boundaries; the page exposes them as selectable text.

The story does not simulate subjective consciousness or establish that real
people will agree when they exchange records. Gate 1 supplies the programme's
finite-access premise. Gate 2's `[P]` criterion says that a reading is
insufficient if it merges histories that respond differently to an admissible
action. The social turn is a constructed illustration of a possible practice,
not a mathematical consequence of that criterion.

The page now ends with a four-view epilogue covering ten documented events.
Each case moves from a scene, through two recorded interpretations, to a
retrospective evidence view. `site/inside-cases-data.mjs` contains the compact
public summaries; [`docs/inside-real-cases.md`](inside-real-cases.md) records
sources, limits, and responsibilities. Its graphics are abstract drawings,
not historical footage or a simulation of any person's private experience.

## Story beats and narration

The page plays `site/inside-audio.mp3` after the viewer chooses Play or Enter
the story. The audio clock drives the film, including pause, replay, scrub,
scene jumps and the sound toggle. The full spoken text is also in the page's
expandable transcript. The 123-second track combines an AI-generated reading
of this original script with an original, procedurally generated soundscape.
`docs/media/build_inside_audio.py` documents the eight source cuts, scene
durations and deterministic mix. `docs/media/inside-voice-master.mp3` is the
unmixed voice master. The public page credits
[AIDOCMAKER.COM](https://www.aidocmaker.com/) for the generated voiceover.

| Time | Picture | Spoken narration |
| --- | --- | --- |
| 0:00–0:14 | A closed gate and a thin channel, seen from Estuary. | The gate is shut. From my bank, the river is thinning. I already know the story. I heard it before I knew the people across the water: when they close the gate, we pay. |
| 0:14–0:27 | The observer's reflection fills with childhood, rationing and passed-down records. | I thought I was looking directly at the world. But my view carried old summers, rationed cups, names of people who waited, sentences repeated until they felt like sight. History had arrived with me. |
| 0:27–0:46 | Downriver families measure what remains. | We measure the falling channel. The loss is real. Children carry buckets farther. A record of harm is not a mistake. The mistake begins when that record pretends to tell us why the other bank acted. |
| 0:46–1:05 | The camera crosses the river to Ridge, past an old flood scar. | Across the river, Ridge remembers a different danger. Their wall broke under an old crest. They rebuilt it. From there, a closed gate looks less like punishment, more like protection. Their record, too, is true and incomplete. |
| 1:05–1:22 | The current gauge and two incomplete records enter one frame. | Today the gauge is rising again. Neither inherited sentence can tell us whether opening the gate will help or flood another home. We need the reading both banks can check. |
| 1:22–1:34 | The inherited sentence lifts from the observer's view; both losses stay. | What I saw was true. It was not enough. I knew our loss. I was guessing at their reason. The guess had become a person in my mind, and I had begun to blame it. |
| 1:34–1:48 | The camera rises above both people. Their future-possibility cones diverge, then a shared measured fact changes the overlap. | Pull back. Each of us projects a future from a different past. One fact enters both views. It does not make the past fair or the risks equal. It changes which next actions we can see. |
| 1:48–2:03 | A joint response costs time; a new record reaches the next generation. | They do not have to agree about everything. They can warn each other, share what the gauge shows, and choose a costly response together. That day is gone. What reaches the next generation is still being made. |

## Original artwork

Four website assets were generated with the built-in `imagegen` tool and
compressed to WebP for the page. The prompts specified the same fictional
river valley, stone gate, dark teal and copper documentary-CGI style, no text
or logos, and these distinct scenes:

1. `site/inside-observer.webp` — a person at a rain-darkened window, their
   translucent reflection carrying places, people and records from the valley.
2. `site/inside-ridge.webp` — the opposite bank with an old flood scar, a
   gate gauge and a second observer carrying a different inherited record.
3. `site/inside-gate.webp` — both observers at the physical gate, incomplete
   records in hand, inspecting shared evidence while unresolved strands remain
   dark.
4. `site/inside-inheritance.webp` — the next generation at dawn with two
   preserved records, people maintaining the gate, and visible remaining cost.

The images are fictional concept art, not depictions of a real society or
historical event. The procedural animation and future cones are rendered in
Canvas on top of the artwork.
