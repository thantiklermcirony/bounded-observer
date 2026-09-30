"""Replay a recorded session's eeg.csv (and accgyro.csv) through the live feature and state
code, to measure how often each reason would hold the signal back. Used to check changes to the
signal-quality rules against real recordings: python tests/replay_quality.py <session folder>"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ida_live.config import DEFAULTS, _merge  # noqa: E402
from ida_live.core import Buffers, Chunk  # noqa: E402
from ida_live.features import build_all  # noqa: E402
from ida_live.state import FrozenReference, StateEngine, StateMap  # noqa: E402


def replay(folder: Path, reference: Path | None = None, seconds: float | None = None, inject=None, windows=None) -> dict:
    folder = Path(folder)
    man = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    settings = _merge(json.loads(json.dumps(DEFAULTS)), man.get("settings", {}))
    settings["mre"]["source"] = "off"
    eeg = np.loadtxt(folder / "eeg.csv", delimiter=",", skiprows=1)
    acc = np.loadtxt(folder / "accgyro.csv", delimiter=",", skiprows=1) if (folder / "accgyro.csv").exists() else None
    if seconds:
        eeg = eeg[eeg[:, 0] <= eeg[0, 0] + seconds]
    if inject is not None:
        eeg = inject(eeg.copy())
    bufs = Buffers(seconds=60.0)
    feats = [f for f in build_all(settings) if f.name != "mre_phi"]
    from ida_live.state import Axis
    m = dict(man["map"])
    m["axes"] = [a if isinstance(a, Axis) else Axis(**a) for a in m.get("axes", [])]
    smap = StateMap(**m)
    ref = FrozenReference.load(reference) if reference else None
    st = StateEngine(smap, ref, settings)
    counts, qual, n = collections.Counter(), collections.Counter(), 0
    hits = collections.Counter()
    t0 = eeg[0, 0]
    ia = 0
    step = 16
    next_tick = t0 + 2.5
    for i in range(0, len(eeg), step):
        blk = eeg[i:i + step]
        bufs.push(Chunk("EEG", blk[:, 0], blk[:, 1:5], ["TP9", "AF7", "AF8", "TP10"], 256.0))
        if acc is not None:
            j = np.searchsorted(acc[:, 0], blk[-1, 0], side="right")
            if j > ia:
                bufs.push(Chunk("ACCGYRO", acc[ia:j, 0], acc[ia:j, 1:7], ["ACC_X", "ACC_Y", "ACC_Z", "GYRO_X", "GYRO_Y", "GYRO_Z"], 52.0))
                ia = j
        t = blk[-1, 0]
        if t < next_tick:
            continue
        next_tick += 0.25
        vals, flags = {}, {}
        for f in feats:
            v, fl = f.compute(bufs, t)
            vals.update(v)
            flags.update(fl)
        clean, reasons = st.is_clean(vals, flags)
        n += 1
        counts.update(reasons or ["clean"])
        if windows is not None:
            inside = any(a <= t - eeg[0, 0] <= b for a, b in windows)
            hits[("in" if inside else "out", "muscle" in reasons)] += 1
        for k in flags.get("quality") or []:
            qual[k] += 1
    out = {"ticks": n, "reasons": {k: round(v / max(1, n), 3) for k, v in counts.most_common()},
           "quality": dict(qual.most_common())}
    if windows is not None:
        tin = hits[("in", True)] + hits[("in", False)]
        tout = hits[("out", True)] + hits[("out", False)]
        out["detected_in_bursts"] = round(hits[("in", True)] / max(1, tin), 3)
        out["muscle_outside_bursts"] = round(hits[("out", True)] / max(1, tout), 3)
    return out


def emg_injector(windows, sensors, gain_log=1.0, seed=1):
    """Add realistic muscle bursts: 20-120 Hz noise carried by spiky motor-unit envelopes, sized so
    each sensor's 55-95 Hz power rises by about gain_log (1.0 = ten times) over its own level."""
    def inject(eeg):
        rng = np.random.default_rng(seed)
        t = eeg[:, 0] - eeg[0, 0]
        for a, b in windows:
            m = (t >= a) & (t <= b)
            n = int(m.sum())
            for c in sensors:
                w = rng.normal(0, 1, n)
                F = np.fft.rfft(w)
                f = np.fft.rfftfreq(n, 1 / 256)
                F[(f < 20) | (f > 120)] = 0
                y = np.fft.irfft(F, n)
                env = np.convolve(rng.gamma(0.3, 1, n), np.ones(12) / 12, mode="same")
                y = y * env / (np.std(y * env) + 1e-9)
                seg = eeg[m, 1 + c] - eeg[m, 1 + c].mean()
                Fs = np.abs(np.fft.rfft(seg)) ** 2
                ref = np.sqrt(Fs[(f >= 55) & (f <= 95)].mean() / Fs[(f >= 20) & (f <= 120)].mean()) * np.std(seg)
                eeg[m, 1 + c] += y * np.std(seg) * 0.3 * (10 ** (gain_log / 2))
        return eeg
    return inject


if __name__ == "__main__":
    print(json.dumps(replay(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else None), indent=1))
