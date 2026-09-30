"""Synthetic Searches in the recorder's format, with a known answer: clarity peaks at a point
along one shape (or depends on nothing)."""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path

import numpy as np

SHAPES = ["symmetry", "axis", "coherence", "calm", "flow", "focus", "openness"]


def search_session(root: Path, name: str, truth: str | None = "coherence", seed: int = 0, peak: float = 0.5):
    rng = np.random.default_rng(seed)
    f = Path(root) / name
    f.mkdir(parents=True, exist_ok=True)
    (f / "manifest.json").write_text(json.dumps({"t0": 0.0, "settings": {}}))
    sched = random.Random(seed).sample(SHAPES, 6) + ["free", "free"]
    random.Random(seed + 1).shuffle(sched)
    ev = [{"kind": "session_start", "t": 0.0}, {"kind": "level_start", "t": 0.0, "search": True, "level": "still"}]
    t = 30.0
    lv_rows, st_rows = [], []
    for k, c in enumerate(sched, start=1):
        base = {s: rng.normal(0, 0.6) for s in SHAPES}
        if c != "free":
            base[c] += 0.7                                          # steering moves its own shape
        for i in range(240):                                        # 60 s at 4 Hz
            row = {"t": round(t, 2), "round": k, "phase": "round"}
            for s in SHAPES:
                row[f"z_{s}"] = round(base[s] + rng.normal(0, 0.5), 3)
            lv_rows.append(row)
            st_rows.append({"t": round(t, 2), "clean": 1, "reasons": ""})
            t += 0.25
        x = base[truth] if truth else 0.0
        clar = 2.5 - 2.0 * (x - peak) ** 2 if truth else 2.0
        rating = int(np.clip(round(clar + rng.normal(0, 0.5)), 0, 4))
        ev.append({"kind": "level_rating", "t": t, "round": k, "rating": rating})
        for j in range(3):
            contrast = 0.08
            p = 1 / (1 + np.exp(-(-0.5 + 1.2 * (clar - 2))))
            ev.append({"kind": "level_probe", "t": t, "round": k, "cand": c, "contrast": contrast, "hit": bool(rng.random() < p), "rt": 0.5})
        t += 8
    ev.append({"kind": "level_reveal", "t": t, "search": sched})
    with open(f / "events.jsonl", "w") as fh:
        for e in ev:
            fh.write(json.dumps(e) + "\n")
    cols = ["t", "round", "phase"] + [f"z_{s}" for s in SHAPES]
    with open(f / "level.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(lv_rows)
    with open(f / "state.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["t", "clean", "reasons"])
        w.writeheader()
        w.writerows(st_rows)
    (f / "features.csv").write_text("t\n" + "\n".join(str(r["t"]) for r in st_rows[:200]))
