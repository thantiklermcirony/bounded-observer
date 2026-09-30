# How closely IDA Live follows the papers (v0.7)

Checked against the text of *Thresholded Adaptive Orchestration* (SSRN 6779487) and
*The Murray Reality Equation* (history/R15). "As written" = implemented the way the paper states
it. "Adapted" = the paper's structure, with a choice the paper leaves open, declared in the
contract. "Not yet" = missing or different; said plainly.

## TAO Chamber (web/js/chamber.js, contract logged at the start of every level)

| Paper | App | Status |
|---|---|---|
| Player x = (a, c, l, f), world w = (q, h, n, p) | same variables | as written |
| q clarity: saturating growth chart, driven by c and l (suppressive) | e/(1-e) chart, drive from F, c, minus l | as written (v0.4 used log-odds: fixed) |
| h rhythm: multiplicative-gate chart, driven by breath/movement synchrony, actuator audio/haptic rhythm | -log e chart; target rapidity = sum of -log(gate) over breath lock to the pacer, steadiness, confidence; drives the breath pacer, a felt low pulse and the visual swell | as written (v0.4 used stability only and had no audio: fixed) |
| n novelty, p perturbation: independent-threat charts | -log(1-e); knocks add in rapidity | as written |
| a arousal: log-odds target corridor from HR/HRV, respiration, motion; actuator = pressure gain | breath rate and motion vs settle (the Muse's optics are off in the EEG-only preset, so no heart rate); scales knock strength | adapted: no heart rate |
| c coherence: saturating, from gaze/breath/input smoothness | steadiness of the level signal and breath regularity | adapted: no eye tracking |
| l load: inhibitory suppression, from task error/reaction delay/optional EEG; actuator density/noise reduction | muscle effort (forehead + temporal EMG) and lost signal; thins sound and novelty, suppresses clarity | adapted: effort stands in for task error |
| f flow: F = sech^2(z/tau), distance from target | two-sided corridor around each tier's target (v0.4 was one-sided: fixed) | as written |
| Update r += dt[G tanh(g/G) c^p - gamma (r - r*) + b(r)] | same, p = 2 | as written |
| Confidence gate, staleness decay, c_min, fallback to safe default | c^2 gate, exponential staleness, inadmissible below 0.6 for 3 s. v0.9.2: while the signal is unclean the world HOLDS for up to 10 s (the safe default is "no change", not "decay to grey"), and unclean moments are left out of corridor occupancy instead of counting as zero; after 10 s it relaxes to its rest point as before | as written (fallback made a hold; declared) |
| f read from the order parameter z | z averaged over the last 5 s of clean signal (levels.smooth_s) before the flow law reads it: in Danny's recordings the 2 s index decorrelates within 2 s (lag-2 s autocorrelation 0.1), so the unsmoothed law was reading noise | measurement choice, declared |
| Sampled update law | integrated in 8 sub-steps per 0.25 s tick so the barrier can act before a step crosses the margin (v0.9.1 logged 197 emergency stops in one run, 0 after) | as written (numerics) |
| h target rapidity | clamped inside the declared margins (a product of three small gates asked for a rest point the barrier forbids) | fixed |
| Barrier B(e) = -log(e-eps) - log(1-eps-e); clipping only as emergency stop | same (one-sided for n and p, where 0 is safe); emergency stops are counted and logged | as written |
| Hysteretic modes in rapidity with h+ - h- >= 0.5 and dwell time; blended actuator changes | tiers switch at logit(0.7) / logit(0.2) of corridor occupancy (width 2.2), 12 s dwell; tier changes blend over 2 s | as written |
| Critical slowing: variance and lag-1 autocorrelation both above baseline margins; W score; anticipatory action | same on the level's coordinate (paper default is the first principal component of several); action = widen the band, lower intensity, hold the next knock | adapted: 1-D order parameter |
| Gains within anchors (gamma 0.1-1.0 etc.), declared before testing | gamma 0.1-0.9; contract sent to the record at the start of each level | as written |
| BAST metrics (boundary pinning, clip events, recovery) | recovery per knock, pinning time, barrier time, emergency stops in each round summary | as written |
| Coupling with tanh and a small-gain check | variables are coupled only through declared drives; no spectral-radius check yet | not yet |
| Order-effect (Lie bracket) test | not run | not yet |

## Murray Reality Equation (v0.7: the test itself now runs)

| Paper (history/R15) | App | Status |
|---|---|---|
| Φ = CTW entropy of 2 s windows, 8-bit quantisation, Φ = H/2 s, smoothed 10 s (§3.2) | `phi_ctw`: decomposed binary CTW on 8-bit (256-level) windows of 2 s, bits/s, 10 s moving average, once a second (features.MrePhi, mre/ctw.py) | as written |
| 1–40 Hz Butterworth, order 4 | the same design, written in numpy (checked against scipy to 1e-13), causal, 8 s of history before each window | as written |
| Frontal montage, average of F3, Fz, F4 | (AF7 + AF8) / 2: the Muse has no F3/Fz/F4 | deviation (hardware) |
| ICA artefact removal | four channels cannot support ICA; bins with blinks, muscle or motion are flagged unclean and left out | deviation (declared) |
| Validate Φ with an oddball task, ρ(Φ, I(S;R)/T) > 0.7 | not built yet | not yet |
| Expected Φ 10³–5×10³ bit/s | at 256 Hz and 8 bits Φ cannot exceed 2048 bit/s (the paper's own 250 Hz, 8-bit spec caps it at 2000) | paper inconsistency, noted |
| Dual SBM-20 GM tubes + Am-241, Teensy 1 MHz timestamps | any USB random-number device; a TrueRNGpro in raw mode gives two unwhitened streams like the two tubes; ANU online as a remote control arm | deviation (hardware; see MRE.md) |
| 100 ms bins, X_t = count ≥ automation median, robustness at 40/50/60th percentiles | the same; counts are taken over a fixed number of raw bits per bin so USB throughput cannot leak in | as written |
| C1 automation 2 weeks; δ0, α0 = 1/H_rate (Laplace-smoothed) | C1 = bins with nothing connected; logging continues with the window closed | as written |
| C2 focused attention 60 × 30 min with EEG | any recording with the live headband (levels, attention map, plain recording), clean bins only | as written (tasks recorded per bin) |
| C3 shuffled Φ, circular shift > 60 s | one pre-drawn shift; F2 from its permutation p | as written |
| Transition GLM (7) with β0(x), β1(x), γ1 T, γ2 p̄_block, γ3/γ4 circadian | the same, per-stream intercepts added; no temperature sensor, so no γ1 T | deviation (no thermometer) |
| MLE; block bootstrap L = 10 τ_auto; permutation by circular shifts; claim needs perm-p < 0.01 and a 99% CI excluding 0 | MLE; block bootstrap of the estimating equations (one-step linearisation), τ_auto of the score series; exact circular-shift permutation over every allowed lag; the same claim rule | as written (bootstrap linearised for speed, declared) |
| κ̂ = β1 / (2 α0 (1 − δ0²)) | β1 read as the slope of δ on Φ: the average marginal effect on P(1\|0) minus that on P(1\|1) | as written (the paper's β1 made explicit) |
| Session level: δ̂ on Φ̄ with HAC SEs | Newey–West | as written |
| F1, F2, F3; any single failure falsifies | all three, with "waiting / on track / passes / fails" until the planned sample is reached | as written |

Checked by simulation (tests/test_mre.py, tests/mre_sim.py): on null data the claim rate was 0 of 60
and permutation p values were uniform; an injected κ was recovered inside its 99% interval.
The EEG's own alternation measure ("alt") is still shown, relabelled, and is not the MRE's δ.

## Levels' target signals

The levels' indices come from the EEG literature, not from the papers (the papers do not name
EEG indices for calm, warmth, focus or flow). From v0.5 a level can instead reward your own
signature from the attention map, once that signature passes its pre-declared gate.
