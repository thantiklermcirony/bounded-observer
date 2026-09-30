"""Signal processing with numpy only.

IDA Live used scipy for three things: Welch spectra, band filtering and low-pass
filtering. Doing them with numpy's FFT keeps the installed app about 100 MB smaller
and removes a large binary dependency. Filters here are zero-phase FFT filters
applied to short analysis windows (a couple of seconds), with reflective padding so
the window edges don't wrap around; they are not meant for long continuous streams.
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np


def _detrend_linear(x: np.ndarray) -> np.ndarray:
    n = x.shape[0]
    t = np.arange(n, dtype=float)
    t -= t.mean()
    denom = (t ** 2).sum()
    xm = x - x.mean(axis=0)
    slope = (t[:, None] * xm).sum(axis=0) / denom if denom > 0 else 0.0
    return xm - np.outer(t, slope) if x.ndim == 2 else xm - t * slope


def welch(x: np.ndarray, fs: float, nperseg: int = 256, noverlap: int = 128) -> Tuple[np.ndarray, np.ndarray]:
    """One-sided power spectral density (units²/Hz), Hann window, linear detrend per segment.

    Matches scipy.signal.welch(..., window='hann', detrend='linear', scaling='density').
    x has shape (n,) or (n, channels); returns (freqs, psd) with psd shaped (freqs, channels).
    """
    x = np.asarray(x, dtype=float)
    one_d = x.ndim == 1
    if one_d:
        x = x[:, None]
    n = x.shape[0]
    nperseg = min(nperseg, n)
    step = max(1, nperseg - noverlap)
    win = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(nperseg) / nperseg)  # periodic Hann
    scale = 1.0 / (fs * (win ** 2).sum())
    acc = None
    count = 0
    for start in range(0, n - nperseg + 1, step):
        seg = _detrend_linear(x[start:start + nperseg]) * win[:, None]
        p = np.abs(np.fft.rfft(seg, axis=0)) ** 2 * scale
        acc = p if acc is None else acc + p
        count += 1
    psd = acc / count
    if nperseg % 2 == 0:
        psd[1:-1] *= 2
    else:
        psd[1:] *= 2
    freqs = np.fft.rfftfreq(nperseg, 1.0 / fs)
    return freqs, (psd[:, 0] if one_d else psd)


def fft_filter(x: np.ndarray, fs: float, lo: Optional[float] = None, hi: Optional[float] = None,
               transition_hz: float = 0.5) -> np.ndarray:
    """Zero-phase band-pass (lo and hi), high-pass (lo only) or low-pass (hi only).

    Raised-cosine transitions of `transition_hz` avoid ringing. Reflective padding of a
    quarter window on each side keeps the edges from wrapping around.
    """
    x = np.asarray(x, dtype=float)
    one_d = x.ndim == 1
    if one_d:
        x = x[:, None]
    x = _detrend_linear(x)
    n = x.shape[0]
    pad = max(1, n // 4)
    xp = np.concatenate([x[pad:0:-1], x, x[-2:-pad - 2:-1]], axis=0)
    m = xp.shape[0]
    f = np.fft.rfftfreq(m, 1.0 / fs)
    gain = np.ones_like(f)
    w = max(transition_hz, 1e-6)
    if lo is not None:
        gain *= np.clip((f - (lo - w / 2)) / w, 0, 1)
    if hi is not None:
        gain *= np.clip(((hi + w / 2) - f) / w, 0, 1)
    gain = 0.5 - 0.5 * np.cos(np.pi * gain)  # smooth the linear ramps into raised cosines
    y = np.fft.irfft(np.fft.rfft(xp, axis=0) * gain[:, None], n=m, axis=0)[pad:pad + n]
    return y[:, 0] if one_d else y


def butter_bandpass_sos(lo: float, hi: float, fs: float, order: int = 4) -> np.ndarray:
    """Digital Butterworth band-pass as second-order sections, the same design as
    scipy.signal.butter(order, [lo, hi], 'bandpass', fs=fs, output='sos') (bilinear transform
    with pre-warping). Written out in numpy because the app ships without scipy."""
    k = np.arange(1, order + 1)
    p = np.exp(1j * np.pi * (2 * k + order - 1) / (2 * order))          # analog prototype poles
    fs2 = 2.0 * fs
    wl, wh = fs2 * np.tan(np.pi * lo / fs), fs2 * np.tan(np.pi * hi / fs)  # pre-warped edges
    bw, wo = wh - wl, np.sqrt(wl * wh)
    plp = p * bw / 2.0
    root = np.sqrt(plp ** 2 - wo ** 2)
    pbp = np.concatenate([plp + root, plp - root])                        # 2N band-pass poles
    kbp = bw ** order
    pd = (fs2 + pbp) / (fs2 - pbp)                                        # bilinear transform
    # N zeros at s = 0 map to z = 1, N zeros at infinity map to z = -1
    kd = kbp * np.real(fs2 ** order / np.prod(fs2 - pbp))
    upper = pd[np.imag(pd) > 1e-12]
    upper = upper[np.argsort(np.abs(upper - 1))]
    sos = []
    for q in upper:
        sos.append([1.0, 0.0, -1.0, 1.0, -2.0 * np.real(q), np.abs(q) ** 2])   # zeros at +1 and -1
    sos = np.array(sos)
    sos[0, :3] *= kd
    return sos


def sosfilt(sos: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Causal filtering by cascaded second-order sections (direct form II transposed)."""
    y = np.asarray(x, dtype=float).copy()
    for b0, b1, b2, _, a1, a2 in sos:
        out = np.empty_like(y)
        z1 = z2 = 0.0
        for i, v in enumerate(y):
            o = b0 * v + z1
            z1 = b1 * v - a1 * o + z2
            z2 = b2 * v - a2 * o
            out[i] = o
        y = out
    return y
