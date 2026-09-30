"""Feature plugins.

A feature plugin reads the live buffers and returns named numbers plus flags. It
knows nothing about the map, the reference or the display, so adding a feature is
one class here and (optionally) one line in a map file.

Documented limits (from the IDA neuroscience atlas):
* F03: muscle activity leaks into high-frequency EEG, so gamma is reported as a
  muscle indicator, not a brain feature.
* F04: aperiodic (1/f) changes shift band power, so the aperiodic exponent is
  computed alongside the bands rather than naming oscillators from ratios.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Type

import numpy as np

from ..core import Buffers
from ..dsp import fft_filter, welch

FEATURES: Dict[str, Type["Feature"]] = {}


def register(cls):
    FEATURES[cls.name] = cls
    return cls


class Feature:
    name = "base"

    def __init__(self, settings: dict):
        self.s = settings["signal"]

    def compute(self, buffers: Buffers, t_now: float) -> Tuple[Dict[str, float], Dict[str, object]]:
        raise NotImplementedError


ELECTRODES = ["TP9", "AF7", "AF8", "TP10"]


def _used(signal_settings: dict) -> list:
    """Indices of the sensors in use (settings signal.sensors); all four by default."""
    names = signal_settings.get("sensors") or ELECTRODES
    idx = [ELECTRODES.index(n) for n in names if n in ELECTRODES]
    return idx or [0, 1, 2, 3]


def _band_mean(f: np.ndarray, p: np.ndarray, lo: float, hi: float) -> np.ndarray:
    m = (f >= lo) & (f < hi)
    return p[m].mean(axis=0)


QUALITY_SCORE = {"good": 1.0, "ok": 0.65, "interference": 0.8, "eyes": 0.5, "muscle": 0.2, "loose": 0.15, "noise": 0.15,
                 "poor": 0.1, "flat": 0.0}


@register
class Spectral(Feature):
    """Band powers, aperiodic exponent, muscle indicator and per-electrode signal quality.

    Quality is judged per electrode from three things, because a loose dry electrode
    can have a perfectly ordinary spread and still carry no brain signal:
      * spread of the 1-40 Hz signal (flat / good / ok / poor),
      * muscle: a burst of 55-95 Hz power above 3x that sensor's own floor over the last
        minute (muscle comes in bursts), or, after the floor is removed, 30-45 Hz still far
        above 4-13 Hz,
      * noise: a raw 2-20 Hz spectrum that does not fall with frequency (exponent below
        min_aperiodic): no brain signature at all.
    Mains hum is reported per electrode (a sign of a loose contact) but not disqualifying:
    it sits outside every band used here and the display notches it out.
    """

    name = "spectral"
    fs = 256.0

    def __init__(self, settings):
        super().__init__(settings)
        self.n = int(self.s["window_s"] * self.fs)

    def compute(self, buffers, t_now):
        buf = buffers.get("EEG")
        if buf is None or not buf.is_fresh(t_now):
            return {}, {"eeg": "missing"}
        _, x = buf.latest(self.n)
        if len(x) < self.n or np.isnan(x).any():
            return {}, {"eeg": "filling"}
        x = x - x.mean(axis=0)
        f, p_raw = welch(x, self.fs, nperseg=256, noverlap=128)
        p_raw = np.maximum(p_raw, 1e-12)
        mains = float(self.s.get("mains_hz", 50))
        # Each sensor's own high-frequency floor: the median of its 55-95 Hz density over the
        # last minute (mains excluded). Muscle is a burst above that floor; the floor itself
        # (electrode and amplifier noise, roughly flat) is subtracted from every band, so band
        # powers estimate the signal under the noise rather than signal plus noise.
        hm = (f >= 55) & (f <= 95) & (np.abs(f - mains) > 3) & (np.abs(f - 2 * mains) > 3)
        hfd = p_raw[hm].mean(axis=0)
        if getattr(self, "_hf_hist", None) is None or t_now - getattr(self, "_t_h", -1e9) > 3.0:
            self._hf_hist = []
        self._t_h = t_now
        self._hf_hist.append(hfd)
        if len(self._hf_hist) > 240:
            del self._hf_hist[0]
        floor = np.median(np.array(self._hf_hist), axis=0) if len(self._hf_hist) >= 8 else hfd
        burst = hfd > float(self.s.get("muscle_burst_ratio", 3.0)) * floor
        # Mains hum at each sensor, and its own recent level. A sensor whose contact loosens picks
        # up more hum, and its high-frequency floor rises WITH the hum; muscle raises the high
        # frequencies without touching the hum. (Checked on real recordings, docs/SIGNAL.md.)
        onl = (f >= mains - 0.6) & (f <= mains + 0.6)
        nbl = ((f >= mains - 7) & (f <= mains - 3)) | ((f >= mains + 3) & (f <= mains + 7))
        hum = np.log10(p_raw[onl].mean(axis=0)) if onl.any() else np.zeros(4)
        prom = hum - np.log10(p_raw[nbl].mean(axis=0)) if nbl.any() else np.zeros(4)   # how clearly the hum stands out
        # eye activity at the forehead: 1-4 Hz power (blinks and eye movements live there)
        e14 = (f >= 1.0) & (f <= 4.0)
        eye = np.log10(p_raw[e14].mean(axis=0))
        self._hum_hist = (getattr(self, "_hum_hist", None) or []) if len(self._hf_hist) > 1 else []
        self._hum_hist.append(np.concatenate([hum, eye, prom]))
        if len(self._hum_hist) > 240:
            del self._hum_hist[0]
        hh = np.array(self._hum_hist)
        hum_floor = np.median(hh[:, :4], axis=0) if len(hh) >= 8 else hum
        eye_floor = np.median(hh[:, 4:8], axis=0) if len(hh) >= 8 else eye
        prom_floor = np.median(hh[:, 8:12], axis=0) if len(hh) >= 8 else prom
        hum_up = hum - hum_floor
        eye_up = eye - eye_floor
        hf_rise = np.log10(hfd) - np.log10(floor)
        # The floor is subtracted with an EMG-like shape (little below 20 Hz, full above), since
        # muscle and loose-contact noise live mostly at high frequency; this never wipes out
        # a real low-frequency rhythm.
        shape = (f / 20.0) ** 2 / (1.0 + (f / 20.0) ** 2)
        p = (np.maximum(p_raw - shape[:, None] * floor[None, :], p_raw * 0.02)
             if self.s.get("floor_correct", True) else p_raw)
        bands = self.s["bands"]
        bp = {name: _band_mean(f, p, lo, hi) for name, (lo, hi) in bands.items()}
        use = _used(self.s)
        # rear (TP) and forehead (AF) groups, restricted to the sensors in use; if a group has
        # no usable sensor the other group stands in, so every feature always exists
        tp = [i for i in (0, 3) if i in use] or [i for i in (1, 2) if i in use] or [0, 3]
        af = [i for i in (1, 2) if i in use] or tp
        vals = {
            "alpha_tp": float(np.log10(bp["alpha"][tp].mean())),
            "theta_af": float(np.log10(bp["theta"][af].mean())),
            "beta": float(np.log10(bp["beta"][use].mean())),
            "alpha_af": float(np.log10(bp["alpha"][af].mean())),
            "beta_af": float(np.log10(bp["beta"][af].mean())),
            "delta_af": float(np.log10(bp["delta"][af].mean())),
            "gamma_tp": float(np.log10(bp["gamma"][tp].mean())),
            "emg_tp": float(np.log10(hfd[tp].mean())),
            # forehead muscle (brow, frontalis): the effort that shows first when you try hard
            "emg_af": float(np.log10(hfd[af].mean())),
            # mains hum at the ear and forehead sensors: a contact measure, not a brain or body one
            "hum_tp": float(np.mean(hum[tp])),
            "hum_af": float(np.mean(hum[af])),
        }
        for name, v in bp.items():  # whole-head band power, used for wave scaling and the reference
            vals[f"lp_{name}"] = float(np.log10(v[use].mean()))
        # level indices on the sensors in use (band power = density x bandwidth)
        pw = {k: float((v[use] * (hi - lo)).mean()) for k, v, (lo, hi) in
              ((k, bp[k], bands[k]) for k in ("delta", "theta", "alpha", "beta"))}
        vals["ix_alpha_rel"] = float(np.log(pw["alpha"] / (pw["delta"] + pw["theta"] + pw["alpha"] + pw["beta"])))
        vals["ix_engagement"] = float(np.log(pw["beta"] / (pw["alpha"] + pw["theta"])))
        # delta left out (blinks and eye movement live there); used by the levels
        vals["ix_alpha_rel3"] = float(np.log(pw["alpha"] / (pw["theta"] + pw["alpha"] + pw["beta"])))
        # frontal alpha asymmetry, ln(right) - ln(left): positive = relatively more left-frontal
        # activity (approach, positive feeling)
        vals["ix_faa"] = float(np.log(bp["alpha"][2] + 1e-12) - np.log(bp["alpha"][1] + 1e-12))
        pa = {k: float((bp[k][af] * (hi - lo)).mean()) for k, (lo, hi) in
              ((k, bands[k]) for k in ("theta", "alpha", "beta"))}
        vals["ix_theta_af_rel"] = float(np.log(pa["theta"] / (pa["theta"] + pa["alpha"] + pa["beta"])))
        vals["alpha_theta"] = vals["alpha_tp"] - vals["theta_af"]
        vals["alpha_theta_af"] = vals["alpha_af"] - vals["theta_af"]
        # aperiodic exponent: slope of log power vs log frequency, 2-40 Hz, alpha excluded
        m = (f >= 2) & (f <= 40) & ~((f >= 7) & (f <= 14))
        lf = np.log10(f[m])
        slope = np.polyfit(lf, np.log10(p[m][:, use].mean(axis=1)), 1)[0]
        vals["aperiodic"] = float(-slope)
        # brain signature per electrode: power falling with frequency over 2-20 Hz (alpha
        # excluded), measured on the raw spectrum, below where muscle and contact noise live
        m20 = (f >= 2) & (f <= 20) & ~((f >= 7) & (f <= 14))
        ch_aper = -np.polyfit(np.log10(f[m20]), np.log10(p_raw[m20]), 1)[0]
        hf = np.log10(_band_mean(f, p, 30.0, 45.0) / _band_mean(f, p, 4.0, 13.0))  # per electrode
        # one 2 s window gives a noisy per-electrode estimate: smooth over the last few ticks
        if getattr(self, "_hf", None) is None or t_now - getattr(self, "_t_q", -1e9) > 3.0:
            self._hf, self._ap = hf.copy(), ch_aper.copy()
        else:
            self._hf += 0.35 * (hf - self._hf)
            self._ap += 0.35 * (ch_aper - self._ap)
        self._t_q = t_now
        hf, ch_aper = self._hf.copy(), self._ap.copy()
        on = (f >= mains - 1) & (f <= mains + 1)
        near = ((f >= mains - 6) & (f < mains - 2)) | ((f > mains + 2) & (f <= mains + 6))
        line = np.log10(p_raw[on].mean(axis=0) / p_raw[near].mean(axis=0)) if on.any() and near.any() else np.zeros(4)
        xf = fft_filter(x, self.fs, lo=1.0, hi=40.0)
        sd = xf.std(axis=0)
        # Brain rhythms are smooth and shared by neighbouring sensors at low frequency; muscle is
        # spiky (sharp interruptions) and local to one sensor; electrical interference is smooth
        # but shared by every sensor. These three tests tell them apart.
        hf_sig = _band_signal(x, self.fs, 30.0, 95.0, mains, guard=4.0)
        spiky = _kurtosis(hf_sig)                       # Gaussian noise = 3; muscle spikes >> 3
        # each sensor's usual spikiness (blinks and hum leave some even at rest): spiky means
        # clearly above your own usual, not above a textbook number
        self._k_hist = (getattr(self, "_k_hist", None) or []) if len(self._hf_hist) > 1 else []
        self._k_hist.append(spiky)
        if len(self._k_hist) > 240:
            del self._k_hist[0]
        k_floor = np.median(np.array(self._k_hist), axis=0) if len(self._k_hist) >= 8 else spiky
        hc = np.corrcoef(hf_sig.T)
        lc = np.corrcoef(fft_filter(x, self.fs, lo=1.0, hi=20.0).T)
        hf_shared = np.array([np.nanmean(np.abs(np.delete(hc[i], i))) for i in range(4)])
        lf_shared = np.array([np.nanmean(np.delete(lc[i], i)) for i in range(4)])
        spike_lim = np.maximum(float(self.s.get("muscle_kurtosis", 5.0)), 1.6 * k_floor)
        hum_lim = float(self.s.get("hum_rise_log", 0.3))
        q = []
        for i, v in enumerate(sd):
            # contact: where a clear hum is present, a loosening sensor's hum rises about as much as its
            # high frequencies do; muscle raises the high frequencies and leaves the hum where it was
            loose = burst[i] and prom_floor[i] > 0.5 and hum_up[i] > hum_lim and hum_up[i] >= 0.6 * hf_rise[i]
            eyes = i in (1, 2) and burst[i] and eye_up[i] > 0.5  # a forehead burst that came with eye activity
            muscle = burst[i] and not loose and not eyes and (spiky[i] > spike_lim[i] or hf_shared[i] < 0.3)
            if v < self.s["quality_flat_uv"]:
                q.append("flat")
            elif v > self.s["quality_ok_uv"]:
                q.append("poor")
            elif loose:
                q.append("loose")
            elif eyes:
                q.append("eyes")
            elif muscle or (spiky[i] > 3 * spike_lim[i] and not loose):
                q.append("muscle")
            elif ch_aper[i] < float(self.s.get("min_aperiodic", 0.3)) and lf_shared[i] < 0.2:
                q.append("noise")
            elif burst[i] or hf[i] > float(self.s.get("muscle_ratio_log", 0.5)):
                q.append("interference")   # smooth, shared high-frequency power: electrical, not muscle
            elif v <= self.s["quality_good_uv"]:
                q.append("good")
            else:
                q.append("ok")
        vals["readiness"] = float(np.mean([QUALITY_SCORE[q[i]] for i in use]))
        # brain signature of the sensors in use: how steeply their raw 2-20 Hz power falls
        vals["brain_slope"] = float(np.mean([ch_aper[i] for i in use]))
        flags = {
            "quality": q,
            "muscle": sum(q[i] == "muscle" for i in use) >= (2 if len(use) > 2 else 1),
            "eyes": any(q[i] == "eyes" for i in use),
            "loose": [i for i in use if q[i] == "loose"],
            "sensors": use,
            "channel": {"sd_uv": [round(float(v), 1) for v in sd], "hf_log": [round(float(v), 2) for v in hf],
                        "aperiodic": [round(float(v), 2) for v in ch_aper], "line_log": [round(float(v), 2) for v in line],
                        "hf_floor": [round(float(np.log10(v)), 2) for v in floor],
                        "hf_now": [round(float(np.log10(v)), 2) for v in hfd], "burst": [bool(v) for v in burst],
                        "hf_kurtosis": [round(float(v), 2) for v in spiky],
                        "hf_shared": [round(float(v), 2) for v in hf_shared],
                        "hum_up": [round(float(v), 2) for v in hum_up], "eye_up": [round(float(v), 2) for v in eye_up],
                        "lf_shared": [round(float(v), 2) for v in lf_shared]},
            "band_log": {k: float(np.log10(v[use].mean())) for k, v in bp.items()},
        }
        return vals, flags


def _band_signal(x: np.ndarray, fs: float, lo: float, hi: float, mains: float, guard: float = 1.5) -> np.ndarray:
    """Band-limited signal by FFT masking, with the mains line and its harmonic removed. The hum
    is not a pure line (its strength wavers with contact), so its skirts are removed too."""
    n = x.shape[0]
    F = np.fft.rfft(x * np.hanning(n)[:, None], axis=0)
    f = np.fft.rfftfreq(n, 1.0 / fs)
    keep = (f >= lo) & (f <= hi) & (np.abs(f - mains) > guard) & (np.abs(f - 2 * mains) > guard)
    F[~keep] = 0
    return np.fft.irfft(F, n=n, axis=0)


def _kurtosis(v: np.ndarray) -> np.ndarray:
    v = v - v.mean(axis=0)
    return (v ** 4).mean(axis=0) / (v.var(axis=0) ** 2 + 1e-12)


def _lz76(s: np.ndarray) -> int:
    """Number of phrases in the Lempel-Ziv (1976) parsing of a symbol sequence (Kaspar-Schuster)."""
    n = len(s)
    if n < 2:
        return n
    s = s.tolist()
    c, l, i, k, kmax = 1, 1, 0, 1, 1
    while True:
        if s[i + k - 1] == s[l + k - 1]:
            k += 1
            if l + k > n:
                c += 1
                break
        else:
            kmax = max(k, kmax)
            i += 1
            if i == l:
                c += 1
                l += kmax
                if l + 1 > n:
                    break
                i, k, kmax = 0, 1, 1
            else:
                k = 1
    return c


@register
class Complexity(Feature):
    """Observer information measures from the Murray Reality Equation (MRE) and the
    complexity literature. All are computed per electrode on the last window of 1-40 Hz
    signal and averaged over electrodes.

    * phi: observer information rate Φ in bits/s (MRE section 3.2). The MRE specifies a
      context-tree-weighting entropy on 8-bit samples; here the entropy rate is
      estimated with the Lempel-Ziv parsing of the signal quantized into `mre.levels`
      equal-probability levels, h = c(n) log2(n) / n bits per sample, times the
      sample rate. It is an estimator of the same quantity, not the paper's exact one.
    * lzc: normalized Lempel-Ziv complexity of the median-binarized signal (the
      standard "LZc" of the consciousness literature; lower in sleep and anaesthesia).
    * alt: an alternation bias δ = P(switch) - P(stay) of the EEG's own median-binarized
      signal. NOTE: the MRE's δ is the alternation bias of an external random bitstream
      (a Geiger counter), predicted to shift with Φ; this is a proxy, not that test.
      (was: the MRE's alternation bias of the median-binarized
      signal sampled at `mre.delta_hz`, bounded in (-1, 1). At 20 Hz it approaches +1
      when a ~10 Hz rhythm dominates and falls toward -1 for slow activity.
    * alt_rapidity: atanh(δ), the MRE chart in which drives add.
    """

    name = "complexity"
    fs = 256.0

    def __init__(self, settings):
        super().__init__(settings)
        self.m = settings.get("mre", {})
        self.n = int(self.s["window_s"] * self.fs)

    def compute(self, buffers, t_now):
        buf = buffers.get("EEG")
        if buf is None or not buf.is_fresh(t_now):
            return {}, {}
        _, x = buf.latest(self.n)
        if len(x) < self.n or np.isnan(x).any():
            return {}, {}
        xf = fft_filter(x - x.mean(axis=0), self.fs, lo=1.0, hi=40.0)
        n = xf.shape[0]
        levels = int(self.m.get("levels", 8))
        step = max(1, int(round(self.fs / float(self.m.get("delta_hz", 20.0)))))
        phis, lzcs, alts = [], [], []
        for c in _used(self.s):
            v = xf[:, c]
            ranks = np.argsort(np.argsort(v))
            q = (ranks * levels // n).astype(np.int8)
            h = _lz76(q) * np.log2(n) / n
            phis.append(min(h, np.log2(levels)) * self.fs)
            b = (v > np.median(v)).astype(np.int8)
            lzcs.append(_lz76(b) * np.log2(n) / n)
            bd = b[::step]
            if len(bd) > 2:
                sw = np.mean(bd[1:] != bd[:-1])
                alts.append(2.0 * sw - 1.0)
        vals = {"phi": float(np.mean(phis)), "lzc": float(np.mean(lzcs))}
        if alts:
            a = float(np.clip(np.mean(alts), -0.999, 0.999))
            vals["alt"] = a
            vals["alt_rapidity"] = float(np.arctanh(a))
        return vals, {}


@register
class Blink(Feature):
    """Blink / eye-movement indicator from the forehead electrodes (AF7, AF8)."""

    name = "blink"
    fs = 256.0

    def compute(self, buffers, t_now):
        buf = buffers.get("EEG")
        if buf is None or not buf.is_fresh(t_now):
            return {}, {}
        _, x = buf.latest(512)
        if len(x) < 512 or np.isnan(x).any():
            return {}, {}
        af = x[:, 1:3].mean(axis=1)
        # whole 2 s window: a blink anywhere in it contaminates that window's spectrum
        lf = fft_filter(af, self.fs, hi=6.0)
        ptp = float(lf.max() - lf.min())
        return {"blink_ptp": ptp}, {"blink": ptp > self.s["blink_uv"]}


@register
class Motion(Feature):
    """Head movement from the gyroscope (degrees per second, RMS over one second)."""

    name = "motion"

    def compute(self, buffers, t_now):
        buf = buffers.get("ACCGYRO")
        if buf is None or not buf.is_fresh(t_now):
            return {}, {}
        _, x = buf.latest(52)
        if len(x) < 10:
            return {}, {}
        g = x[:, 3:6]
        rms = float(np.sqrt(((g - np.median(g, axis=0)) ** 2).sum(axis=1).mean()))
        return {"motion_dps": rms}, {"motion": rms > self.s["motion_dps"]}


@register
class Breath(Feature):
    """Breathing from the head's own motion (gyroscope and accelerometer), and how well it
    locks to the breath pacer. TAO drives rhythm strength h by breath synchrony and reads
    arousal partly from respiration; the Muse has no chest belt, so breathing is estimated
    from the tiny rocking of the head with each breath and reported with a confidence.

    breath_bpm    breaths per minute (spectral peak, 4-36 per minute, last 40 s)
    breath_conf   share of 0.07-0.6 Hz motion power in that peak (0..1): how sure the estimate is
    breath_sync   phase locking to the pacer over the last 30 s (0 none .. 1 locked), valid
                  only while the pacer is running; the pacer's phase is a pure function of the
                  shared clock (pacer_phase), so the display and the engine agree without messages
    """

    name = "breath"

    def __init__(self, settings: dict):
        super().__init__(settings)
        self.audio = settings.get("audio", {})

    def compute(self, buffers, t_now):
        buf = buffers.get("ACCGYRO")
        if buf is None or not buf.is_fresh(t_now):
            return {}, {}
        rate = float(getattr(buf, "rate", 52.0) or 52.0)
        n = int(40 * rate)
        t, x = buf.latest(n)
        ok = np.isfinite(x).all(axis=1)
        if ok.sum() < 20 * rate:
            return {}, {}
        t, x = t[ok], x[ok]
        y = fft_filter(x[:, :6] - x[:, :6].mean(axis=0), rate, lo=0.07, hi=0.6, transition_hz=0.05)
        y = y / (y.std(axis=0) + 1e-9)
        # the breathing axis: first principal component of the band-passed motion
        u, sv, vt = np.linalg.svd(y - y.mean(axis=0), full_matrices=False)
        b = u[:, 0] * sv[0]
        f = np.fft.rfftfreq(len(b), 1 / rate)
        P = np.abs(np.fft.rfft(b * np.hanning(len(b)))) ** 2
        band = (f >= 0.067) & (f <= 0.6)
        if not band.any() or P[band].sum() <= 0:
            return {}, {}
        k = np.argmax(np.where(band, P, 0))
        near = band & (np.abs(f - f[k]) <= 0.03)
        conf = float(P[near].sum() / P[band].sum())
        vals = {"breath_bpm": float(60 * f[k]), "breath_conf": conf}
        pace = float(self.audio.get("pacer_bpm", 6.0)) / 60.0
        if True:  # the pacer's phase is defined whether or not it is audible; the level log says when it was
            # analytic signal of the breath, phase-locking value against the pacer over 30 s
            B = np.fft.fft(b)
            h = np.zeros(len(b)); h[0] = 1
            h[1:(len(b) + 1) // 2] = 2
            if len(b) % 2 == 0:
                h[len(b) // 2] = 1
            ph = np.angle(np.fft.ifft(B * h))
            m = t >= t[-1] - 30
            d = ph[m] - pacer_phase(t[m], pace)
            vals["breath_sync"] = float(np.abs(np.mean(np.exp(1j * d))))
        return vals, {}


def pacer_phase(t, hz: float):
    """The breath pacer's phase at clock time t (radians). Inhale while it rises."""
    return 2 * np.pi * hz * np.asarray(t, dtype=float)


@register
class Heart(Feature):
    """Heart rate from the infrared optics. Only available while the optics are on."""

    name = "heart"
    fs = 64.0

    def compute(self, buffers, t_now):
        buf = buffers.get("OPTICS")
        if buf is None or not buf.is_fresh(t_now, 1.0):
            return {}, {"optics": "off"}
        _, x = buf.latest(640)
        if len(x) < 640 or np.isnan(x).any():
            return {}, {"optics": "filling"}
        idx = [i for i, c in enumerate(buf.channels) if c.endswith("_IR")]
        if not idx:
            return {}, {"optics": "on"}
        ir = fft_filter(x[:, idx].mean(axis=1), self.fs, lo=0.7, hi=3.5, transition_hz=0.3)
        ac = np.correlate(ir, ir, mode="full")[len(ir) - 1:]
        lo, hi = int(self.fs * 60 / 200), int(self.fs * 60 / 40)
        if ac[0] <= 0:
            return {}, {"optics": "on"}
        lag = lo + int(np.argmax(ac[lo:hi]))
        strength = float(ac[lag] / ac[0])
        vals = {"heart_bpm": 60.0 * self.fs / lag} if strength > 0.3 else {}
        return vals, {"optics": "on", "heart_confidence": strength}


@register
class MrePhi(Feature):
    """Φ as the Murray Reality Equation specifies it (history/R15 §3.2): a Butterworth 1-40 Hz
    (order 4) frontal average, 8-bit quantisation of each 2 s window, context-tree-weighting
    entropy, Φ = H_CTW / 2 s, smoothed over 10 s. Computed once a second on a worker thread (CTW
    in pure Python takes ~0.1 s a window) so the live loop never waits for it.

    Declared deviations: the Muse has no F3/Fz/F4, so the frontal average is (AF7 + AF8) / 2
    (the forehead sensors in use); there is no ICA with four channels, so windows with blinks,
    muscle or motion are marked unclean and the analysis leaves them out instead.

    phi_ctw      the 10 s moving average of the per-second Φ (bits/s): the MRE's Φ(t)
    phi_ctw_raw  the latest 2 s window's Φ
    """

    name = "mre_phi"
    fs = 256.0

    def __init__(self, settings):
        super().__init__(settings)
        import threading
        from ..dsp import butter_bandpass_sos
        self.sos = butter_bandpass_sos(1.0, 40.0, self.fs, 4)
        self.smooth_s = float(settings.get("mre", {}).get("phi_smooth_s", 10.0))
        self.hist: list = []            # (t, phi) per second
        self.next_t = 0.0
        self.busy = False
        self.lock = threading.Lock()

    def _work(self, x: np.ndarray, t: float) -> None:
        from ..dsp import sosfilt
        from ..mre.ctw import phi_ctw
        try:
            y = sosfilt(self.sos, x - x[0])[-int(2 * self.fs):]   # 8 s of history settles the filter
            phi = float(phi_ctw(y, 2.0))
            with self.lock:
                self.hist = [(tt, v) for tt, v in self.hist if tt > t - self.smooth_s] + [(t, phi)]
        except Exception:
            pass
        finally:
            self.busy = False

    def compute(self, buffers, t_now):
        buf = buffers.get("EEG")
        if buf is None or not buf.is_fresh(t_now):
            return {}, {}
        if t_now >= self.next_t and not self.busy:
            self.next_t = t_now + 1.0
            _, x = buf.latest(int(10 * self.fs))
            idx = [i for i in _used(self.s) if i in (1, 2)] or [1, 2]
            if len(x) >= int(10 * self.fs) and not np.isnan(x[:, idx]).any():
                import threading
                self.busy = True
                threading.Thread(target=self._work, args=(x[:, idx].mean(axis=1), t_now), daemon=True).start()
        with self.lock:
            h = [v for tt, v in self.hist if tt > t_now - self.smooth_s - 1.0]
            last = self.hist[-1][1] if self.hist else None
        if not h:
            return {}, {}
        return {"phi_ctw": float(np.mean(h)), "phi_ctw_raw": float(last)}, {}


def build_all(settings: dict) -> List[Feature]:
    return [cls(settings) for cls in FEATURES.values()]
