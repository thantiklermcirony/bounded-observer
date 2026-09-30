# Attention map

Calibrates the app to how you attend, with behaviour as the ground truth.

Three tasks, six 20 s blocks each (about 8 minutes):
* Hold the centre (city traffic): a still, sharp circle in the middle while the rest moves;
  focus blocks vs free-viewing blocks.
* The jellyfish: the jellyfish clears while the background blurs; focus vs free.
* The summit: the climber alone (narrow) vs the whole view at once (broad).

In focus and narrow blocks a small light blinks on the attended region every few seconds (press
Space); decoys blink elsewhere (ignore). In broad blocks lights blink anywhere. Free blocks have
no task. Every light, press, reaction time and miss is logged in attention.csv on the session
clock.

The profile (analysis/attention.py) reports, per contrast (focus vs free, narrow vs broad):
per-feature AUC with block-bootstrap intervals; a ridge-logistic signature tested on held-out
blocks (one block of each state left out per fold); the same model on muscle, motion and blinks
only; a block-level permutation p; and whether the signature in the 2 s before each light
predicts catching it fast. Gate: held-out AUC >= 0.60, permutation p < 0.05, and at least 0.05
above the muscle-and-motion model. Simulated null data: about 5% false passes. A signature that
passes replaces the textbook index in Tightrope (focus) and Night Sky (broad), logged at the
start of the level.
