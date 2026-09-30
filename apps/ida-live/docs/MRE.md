# The MRE test in IDA Live (v0.7)

The Murray Reality Equation (history/R15) predicts that the alternation bias δ of a quantum
measurement stream rises with the observer's information rate Φ,

    δ(Φ) = tanh(atanh δ0 + 2 α0 κ Φ),   with the marginal p unchanged,

and it names its own falsifiers. IDA Live now runs the whole protocol: a random-bit device logged
at 10 Hz, Φ from your EEG by context-tree weighting, and the paper's analysis with F1–F3.

## What to plug in

| Option | What it is | Role here |
|---|---|---|
| **TrueRNGpro V2** (ubld.it, about $100) | USB, two avalanche-noise generators; a RAW mode gives their unwhitened samples | **Device under test.** Plug in, choose *USB random-number device*, mode *Raw*. Two independent streams, like the paper's two GM tubes. |
| Quantis USB (ID Quantique, about €1,000) | single photons at a beam splitter: the cleanest "quantum measurement" | The upgrade if the TrueRNGpro shows anything, or for publication. It needs ID Quantique's driver, so a small adaptor gets added when you have one. |
| GM tube + Am-241 + microcontroller | the paper's exact rig | Only with proper sealed sources and advice; never open a smoke detector. Background radiation alone is far too slow. |
| **ANU QRNG online** (free) | vacuum-fluctuation numbers generated in Canberra, fetched once a minute | **Control arm.** Every bit exists before you see it, so the MRE predicts nothing in it. An "effect" in both arms means an artefact. |
| Sham | seeded pseudo-random numbers | Checking the pipeline; must never show an effect. |

Why raw matters: whitening or hashing (what most RNGs do by default) scrambles exactly the
bin-to-bin structure the test measures.

## How it runs

1. Drawer → **MRE**. Device under test: *USB random-number device*. Control arm: *ANU online*.
2. **Automation (C1)** is any time nothing is connected. Leave the laptop on and plugged in with
   sleep turned off (Windows Settings → System → Power: never sleep when plugged in). Closing the
   window keeps logging; opening IDA Live brings it back; **Quit** stops everything. The first
   five minutes of automation fix each stream's median threshold (saved in `mre/threshold_main.json`).
   The paper plans 2 × 10⁷ pairs: about 12 days with two streams.
3. **Focused attention (C2)** is any recording with the live headband: levels, the attention map,
   plain recording. Only clean bins count. The paper plans 60 sessions of 30 minutes (2.2 × 10⁶ pairs).
4. **Analyse now** builds the report (`mre/report.html`, `mre/report.json`).

## What the report says

* **Verdict.** An effect is claimed only when the permutation p (circular shifts of Φ by more than
  60 s) is below 0.01 *and* the 99% block-bootstrap interval of the slope excludes zero. Otherwise it
  gives an upper bound on κ.
* **F1** automation shows no slope (a real Φ trace laid over automation data). **F2** a shuffled Φ
  shows nothing. **F3** sessions with higher mean Φ show higher δ, consistent with the fit. Each reads
  *waiting*, *on track*, *passes* or *fails*; final verdicts wait for the planned sample.
* **Equation (4) contrast.** δ in focused attention minus δ0 in automation, with κ from it. It is the
  comparison behind the paper's power figures and the most sensitive one here, but anything else
  that differs between automation and sessions can move it, so read it next to the control arm.
* **Detectable κ.** The smallest κ the data so far could detect. The paper expects 10⁻⁶–10⁻⁵.
* **Robustness.** Thresholds at the 40th and 60th percentiles.

## Files (Documents\IDA Live\mre)

`bits_main_DATE.csv` / `bits_control_DATE.csv`: one row per 100 ms bin:
`wall, cond (1 automation, 2 attention, 0 other), clean, phi, phi_raw, count_A, n_A, count_B, n_B`.
Counts are ones among a fixed number of raw bits per bin, so USB throughput cannot leak in.
`segments_*.csv` records when the source, session or task changed. About 30 MB a day.

## Declared differences from the paper

Muse forehead sensors (AF7 + AF8) instead of F3/Fz/F4; no ICA (unclean bins dropped instead); no
temperature covariate; an avalanche-noise device rather than GM tubes; the bootstrap linearised
around the full fit. The paper's expected Φ of 10³–5 × 10³ bit/s cannot be reached with 8-bit samples
at 256 Hz (the ceiling is 2,048 bit/s), and the same holds for its own 250 Hz spec. The oddball
validation of Φ is not built yet. Details in SPEC_AUDIT.md.
