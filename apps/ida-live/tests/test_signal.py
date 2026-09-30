"""Contact versus muscle: a loosening sensor raises its high frequencies together with the mains
hum; a muscle burst raises the high frequencies and leaves the hum alone. Built from what Danny's
recordings showed (docs/SIGNAL.md)."""
import os, sys, tempfile
from pathlib import Path

import numpy as np

os.environ.setdefault("IDA_LIVE_DATA", tempfile.mkdtemp())
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ida_live.config import load_settings  # noqa: E402
from ida_live.core import Buffers, Chunk  # noqa: E402
from ida_live.features import build_all  # noqa: E402

FS = 256


def run(x, t):
    feats = [f for f in build_all(load_settings()) if f.name == "spectral"]
    out = {}
    b = Buffers(60)
    for k in range(0, len(t), 64):
        b.push(Chunk("EEG", t[k:k + 64], x[k:k + 64], ["TP9", "AF7", "AF8", "TP10"], FS))
        if k < 512:
            continue
        _, fl = feats[0].compute(b, t[min(len(t), k + 64) - 1])
        out[round(float(t[min(len(t), k + 64) - 1]), 2)] = fl["quality"]
    return out


def base(seconds=60, seed=1):
    rng = np.random.default_rng(seed)
    n = seconds * FS
    t = np.arange(n) / FS
    x = np.cumsum(rng.normal(0, 1, (n, 4)), axis=0)
    x -= np.linspace(x[0], x[-1], n)
    x = x / x.std() * 12 + 8 * np.sin(2 * np.pi * 10 * t)[:, None]
    x += rng.normal(0, 2.0, (n, 4))                                  # amplifier floor
    hum = np.sin(2 * np.pi * 50 * t)[:, None] * np.array([20, 6, 6, 20])  # mains, strongest at the ears
    return t, x, hum, rng


def test_a_loosening_ear_is_contact_not_muscle():
    t, x, hum, rng = base()
    step = t > 40
    x = x + hum
    x[step, 0] += 3 * hum[step, 0] + rng.normal(0, 8, step.sum())     # left ear loosens: more hum AND more noise
    q = run(x + 800, t)
    after = [v[0] for tt, v in q.items() if 41.5 < tt < 50]
    assert after and sum(a == "loose" for a in after) >= len(after) // 2, after
    assert not any(a == "muscle" for a in after), after


def test_a_jaw_burst_with_hum_present_is_muscle():
    t, x, hum, rng = base(seed=2)
    x = x + hum
    burst = (t > 45) & (t < 49)
    for c in (0, 3):
        w = rng.normal(0, 1, burst.sum())
        F = np.fft.rfft(w); f = np.fft.rfftfreq(burst.sum(), 1 / FS); F[(f < 20) | (f > 120)] = 0
        y = np.fft.irfft(F, burst.sum()) * np.convolve(rng.gamma(0.3, 1, burst.sum()), np.ones(12) / 12, "same")
        x[burst, c] += y / y.std() * 25
    q = run(x + 800, t)
    during = [v for tt, v in q.items() if 46.5 < tt < 49]
    assert sum(v[0] == "muscle" or v[3] == "muscle" for v in during) >= len(during) // 2, during
    quiet = [v for tt, v in q.items() if 20 < tt < 44]
    assert not any("muscle" in v or "loose" in v for v in quiet), quiet[:3]
