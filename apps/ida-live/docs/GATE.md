# Calibration gate, version 1

Declared 25 September 2026, before any real data. The code is `ida_live/analysis/gate.py`.
Changing anything below after seeing results requires a new version number.

## Question

Does your position in the state map, taken from the 5 seconds before a thought probe,
predict your answer ("on what I meant to be doing" vs "wandered off") on sessions the
model never saw, better than simple alternatives?

## Data

- Probe answers "aware" and "drifting" only; "not sure" and unanswered probes are excluded.
- Self-caught drifts (key D) are recorded but not used: they are not randomly timed.
- A probe is dropped if fewer than half of its pre-probe ticks are clean.

## Models

Logistic regression, ridge penalty 1, standardised inside each training fold, evaluated
leave-one-session-out.

| Model | Inputs |
|---|---|
| M0 time | minutes since session start |
| M1 index | alpha/theta log ratio (a plain neurofeedback index) |
| M2 map | hyperbolic map x, y and displacement d |
| M3 flat | the same axes composed flat (Euclidean), x, y and displacement |

## Pass rule

With at least 3 sessions, 60 answered probes and 15 of each answer:
AUC(M2) >= 0.60, AUC(M2) >= AUC(M0) + 0.05 and AUC(M2) >= AUC(M1) + 0.05.

M2 minus M3 is reported separately. It asks whether the curvature itself earns its
place and is not part of pass/fail.

## If it fails

The map is decoration for this purpose. Options, each a new gate version: different
features or directions (a learned map), different time windows, or a different outcome
than probes. The failure is reported as it stands.

# Addendum, version 2: candidate awareness measures

Declared 25 September 2026, before any real data. Version 1 above is unchanged.

Each candidate is tested alone, exactly like the models above (the 5 s before each
probe, logistic regression with ridge 1, leave-one-session-out), on the same probes:

| Candidate | Source |
|---|---|
| Φ, observer information rate (bits/s) | Murray Reality Equation, section 3.2 (entropy-rate estimate) |
| LZ complexity of the binarized EEG | Schartner et al.; the standard complexity marker of conscious level |
| alternation bias δ at 20 Hz | Murray Reality Equation, section 3.1, applied to the binarized EEG |
| 1/f (aperiodic) exponent | arousal / excitation-inhibition marker (e.g. Gao et al. 2017; Lendner et al. 2020) |
| alpha/theta | the classic mind-wandering index |
| IDA residue, IDA displacement | IDA and the Boundedness Engine, section 6 |

A candidate earns its place when AUC >= 0.60 and AUC >= AUC(M0 time) + 0.05, with the
same minimum data as version 1. Results for every candidate are reported, including the
ones that fail.
