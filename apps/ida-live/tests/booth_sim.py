"""A synthetic booth session in the recorder's file format: a felt state that drifts, a lever
that follows it (moved in steps, as a hand would), and features that may or may not track it."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

FEATS = ["alpha_tp", "theta_af", "beta", "delta_af", "gamma_tp", "emg_tp", "emg_af", "aperiodic", "lzc", "phi_ctw",
         "ix_alpha_rel3", "ix_engagement", "ix_theta_af_rel", "ix_faa", "blink_ptp", "motion_dps", "breath_bpm", "heart_bpm"]


def booth_session(root: Path, name: str, minutes: float = 20, brain: float = 0.0, body: float = 0.0, seed: int = 0):
    rng = np.random.default_rng(seed)
    f = Path(root) / name
    f.mkdir(parents=True, exist_ok=True)
    (f / "manifest.json").write_text(json.dumps({"t0": 1000.0, "settings": {}}))
    (f / "events.jsonl").write_text(json.dumps({"kind": "session_start", "t": 1000.0}) + "\n")
    n = int(minutes * 60 * 4)
    t = 1000.0 + np.arange(n) * 0.25
    z = np.cumsum(rng.normal(0, 1, n // 40 + 2))
    latent = np.repeat((z - z.mean()) / (z.std() + 1e-9), 40)[:n]
    latent = np.convolve(latent, np.ones(40) / 40, mode="same")
    lever = np.clip(0.5 + 0.2 * np.round(latent * 2) / 2, 0, 1)            # stepped, like a hand
    with open(f / "features.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["t"] + FEATS + ["blink", "motion", "muscle", "quality"])
        for i in range(n):
            vals = [rng.normal() for _ in FEATS]
            vals[FEATS.index("ix_alpha_rel3")] += brain * latent[i]
            vals[FEATS.index("lzc")] += 0.7 * brain * latent[i]
            vals[FEATS.index("emg_af")] += body * latent[i]
            w.writerow([round(t[i], 3)] + [round(v, 4) for v in vals] + [0, 0, 0, "good|good|good|good"])
    with open(f / "state.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["t", "clean", "reasons"])
        for i in range(n):
            w.writerow([round(t[i], 3), 1, ""])
    with open(f / "booth.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["t", "flow", "presence", "horizon", "moving", "peak", "music", "music_t", "music_level", "event"])
        prev = None
        for i in range(0, n, 1):  # booth rows at 4 Hz here (the app writes 10 Hz)
            lv = lever[i]
            w.writerow([round(t[i], 3), lv, 0.5, round(0.5 + 0.1 * rng.normal(), 3), int(prev is not None and lv != prev), 0,
                        "score:still", 0, 0.3, ""])
            prev = lv
