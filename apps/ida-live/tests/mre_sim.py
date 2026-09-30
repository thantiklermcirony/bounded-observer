"""Synthetic MRE data in the logger's exact file format, with a known κ (0 = null)."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

HEADER = ["wall", "cond", "clean", "phi", "phi_raw", "count_A", "n_A", "count_B", "n_B"]


def simulate(folder: Path, c1_bins: int = 200_000, sessions: int = 12, session_bins: int = 18_000,
             kappa: float = 0.0, alpha0: float = 0.1, delta0: float = 0.0, seed: int = 1, tag: str = "main",
             source: str = "sim RNG") -> None:
    rng = np.random.default_rng(seed)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    wall0 = 1.79e9
    rows, segs = [], [[wall0 - 1, source, "sham", 2, 160, "", ""]]
    prev = [0, 0]
    t = wall0

    def emit(n, cond, phi_series, session):
        nonlocal t
        for i in range(n):
            phi = phi_series[i] if phi_series is not None else float("nan")
            d = math.tanh(math.atanh(delta0) + 2 * alpha0 * kappa * (phi if phi == phi else 0.0))
            row = [round(t, 2), cond, 1 if cond == 2 else 0, round(phi, 1) if phi == phi else "nan", "nan"]
            for k in (0, 1):
                x = prev[k] ^ int(rng.random() < (1 + d) / 2)
                prev[k] = x
                gap = 1 + int(rng.integers(0, 1000))
                row += [1000 + gap if x else 1000 - gap, 160]
            rows.append(row)
            t += 0.1
    emit(c1_bins, 1, None, "")
    for s in range(sessions):
        m = rng.uniform(900, 1900)
        z = np.cumsum(rng.normal(0, 1, session_bins // 10 + 2))
        z = (z - z.mean()) / (z.std() + 1e-9) * 150
        phi = np.repeat(m + z, 10)[:session_bins]
        name = f"2026-09-{10 + s:02d}_120000_level-still"
        segs.append([round(t, 2) - 0.01, source, "sham", 2, 160, name, "level:still"])
        emit(session_bins, 2, phi, name)
        segs.append([round(t, 2) - 0.01, source, "sham", 2, 160, "", ""])
        emit(3000, 1, None, "")
    with open(folder / f"bits_{tag}_2026-09-10.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)
    with open(folder / f"segments_{tag}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["wall", "source", "kind", "streams", "bits_per_bin", "session", "task"])
        w.writerows(segs)
