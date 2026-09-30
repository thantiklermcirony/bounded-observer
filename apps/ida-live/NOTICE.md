# Third-party material in IDA Live

- **OpenMuse** (MIT licence, Dominique Makowski and contributors) decodes the Muse S Athena's
  Bluetooth protocol, vendored in `ida_live/vendor/openmuse/` and pinned to commit a9be252.
  https://github.com/DominiqueMakowski/OpenMuse
- **Tone.js** (MIT licence) in `web/vendor/tone.js`, for the levels' generative score.
  Licence text: `web/vendor/tone.LICENSE.txt`.
- **Atkinson Hyperlegible** font (SIL Open Font Licence 1.1, Braille Institute), bundled in
  `web/fonts` so the display works offline. Licence text: `web/fonts/OFL-LICENSE.txt`.

`tests/data/athena_p1035_openmuse.txt`, a one-minute Muse S Athena recording from OpenMuse's
test data (MIT licence) used to test decoding against real bytes, is not included in this
repository for size reasons; `tests/test_replay_real_bytes.py` skips without it. Fetch it from
the OpenMuse repository to run that test.

`web/samples.zip`, the bundled audio samples for the listening booth, is not included here for
size reasons. The booth falls back to synthesis without it.
