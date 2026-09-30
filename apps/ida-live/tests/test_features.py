import numpy as np

from ida_live.config import load_settings
from ida_live.core import Buffers, Chunk
from ida_live.features import Spectral


def pink(n, ch, rng, exponent=1.0):
    """Noise with a 1/f^exponent spectrum. Real EEG has an aperiodic slope; white noise
    does not, and from v0.10.0 the quality classifier correctly calls a flat spectrum
    "noise" (features.Spectral, min_aperiodic). A test signal has to look like a brain."""
    f = np.fft.rfftfreq(n, d=1 / 256.0)
    scale = np.ones_like(f)
    scale[1:] = f[1:] ** (-exponent / 2.0)
    spec = (rng.normal(size=(len(f), ch)) + 1j * rng.normal(size=(len(f), ch))) * scale[:, None]
    x = np.fft.irfft(spec, n=n, axis=0)
    return x / x.std(0, keepdims=True) * 2.0


def make_buffers(alpha_amp):
    t = np.arange(1024) / 256.0
    rng = np.random.default_rng(1)
    x = pink(1024, 4, rng)
    x[:, [0, 3]] += alpha_amp * np.sin(2 * np.pi * 10 * t)[:, None]
    b = Buffers()
    b.push(Chunk("EEG", t, x + 800, ["EEG_TP9", "EEG_AF7", "EEG_AF8", "EEG_TP10"], 256.0))
    return b, t[-1]


def test_alpha_detected_and_quality_reported():
    s = load_settings()
    f = Spectral(s)
    lo, t = make_buffers(0.0)
    hi, _ = make_buffers(10.0)
    v_lo, fl = f.compute(lo, t)
    v_hi, _ = f.compute(hi, t)
    assert v_hi["alpha_tp"] > v_lo["alpha_tp"] + 1.0
    assert abs(v_hi["theta_af"] - v_lo["theta_af"]) < 0.3
    assert fl["quality"] == ["good"] * 4


def test_stale_buffer_reports_missing():
    s = load_settings()
    b, t = make_buffers(5.0)
    vals, flags = Spectral(s).compute(b, t + 10.0)
    assert vals == {} and flags["eeg"] == "missing"
