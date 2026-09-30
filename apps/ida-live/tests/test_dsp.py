import numpy as np
import pytest

from ida_live import dsp


def test_welch_matches_scipy():
    signal = pytest.importorskip("scipy.signal")
    x = np.random.default_rng(0).normal(size=(512, 4)) + np.linspace(0, 5, 512)[:, None]
    f1, p1 = signal.welch(x, fs=256, nperseg=256, noverlap=128, axis=0, detrend="linear")
    f2, p2 = dsp.welch(x, 256, 256, 128)
    assert np.allclose(f1, f2) and np.allclose(p1, p2, rtol=1e-9)


def test_band_filter_keeps_band_and_removes_rest():
    t = np.arange(512) / 256
    s = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 50 * t)
    y = dsp.fft_filter(s, 256, lo=8, hi=13)
    assert np.std(y[64:-64]) == pytest.approx(1 / np.sqrt(2), rel=0.05)
    y50 = dsp.fft_filter(np.sin(2 * np.pi * 50 * t), 256, lo=8, hi=13)
    assert np.std(y50) < 0.01
