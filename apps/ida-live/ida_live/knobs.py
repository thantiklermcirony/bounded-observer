"""Knobs: every number, switch and choice in the app, adjustable live and logged.

Any leaf of the settings (see config.DEFAULTS) and of the active state map is a
knob, addressed by a dotted path such as "signal.blink_uv" or "map.axes.0.angle_deg".
Changing a knob:
  * takes effect on the next tick for signal/state/map knobs (the processing chain
    is rebuilt; the frozen reference is kept),
  * takes effect at the next run for protocol and recipe knobs,
  * needs a restart for server and path knobs,
and is always written to the session's events, so every result can be traced to
the exact settings that produced it.

META below documents the knobs that matter most. Knobs without an entry still
work; they just have no description or range yet.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Tuple

FEATURE_CHOICES = ["alpha_tp", "theta_af", "beta", "delta_af", "gamma_tp", "emg_tp", "alpha_theta", "aperiodic",
                   "alpha_af", "beta_af", "alpha_theta_af"]

# path: (description, min, max, step, choices, applies)
META: Dict[str, tuple] = {
    "signal.window_s": ("Length of the analysis window for every EEG feature (seconds)", 1.0, 8.0, 0.5, None, "now"),
    "signal.tick_hz": ("How often features and the map update (per second)", 1.0, 10.0, 1.0, None, "restart"),
    "signal.mains_hz": ("Local mains frequency (Thailand: 50)", 50, 60, 10, [50, 60], "now"),
    "signal.blink_uv": ("Forehead swing that counts as a blink (µV, low-passed)", 40.0, 600.0, 10.0, None, "now"),
    "signal.motion_dps": ("Head rotation that counts as movement (degrees per second)", 2.0, 60.0, 1.0, None, "now"),
    "signal.emg_z": ("Jaw-muscle level, in reference units, that counts as muscle", 1.0, 8.0, 0.5, None, "now"),
    "signal.quality_good_uv": ("Contact is 'good' below this 1-40 Hz spread (µV)", 5.0, 200.0, 5.0, None, "now"),
    "signal.quality_ok_uv": ("Contact is 'ok' below this 1-40 Hz spread (µV)", 10.0, 400.0, 5.0, None, "now"),
    "reference.calibration_s": ("Seconds of clean signal a calibration collects", 20, 600, 5, None, "next calibration"),
    "reference.max_calibration_s": ("A calibration gives up after this long (seconds)", 60, 1200, 10, None, "next calibration"),
    "reference.ear_min_share": ("Ear sensors join a calibration only if clean this share of the last 20 s", 0.3, 1.0, 0.05, None, "next calibration"),
    "reference.min_clean_fraction": ("Share of calibration that must be clean", 0.1, 0.95, 0.05, None, "next calibration"),
    "reference.drift_tau_s": ("Time constant of the slow drifting baseline (seconds)", 30, 3600, 30, None, "now"),
    "state.smooth_tau_s": ("Smoothing of the moving point (seconds; 0.3 is jumpy, 5 is calm)", 0.25, 20.0, 0.25, None, "now"),
    "state.return_radius": ("Radius counted as 'back' for return times (hyperbolic units)", 0.1, 2.0, 0.1, None, "now"),
    "state.return_hold_s": ("How long you must stay inside that radius to count as returned", 0.5, 10.0, 0.5, None, "now"),
    "probes.min_interval_s": ("Shortest gap between attention probes (seconds)", 10, 600, 5, None, "next probe"),
    "probes.max_interval_s": ("Longest gap between attention probes (seconds)", 10, 900, 5, None, "next probe"),
    "probes.pre_window_s": ("Seconds before a probe used to describe your state", 1.0, 20.0, 0.5, None, "analysis"),
    "ir_protocol.trials": ("Light trials per run", 2, 60, 2, None, "next run"),
    "ir_protocol.block_size": ("Randomization block size (even)", 2, 12, 2, None, "next run"),
    "ir_protocol.pre_s": ("Baseline before each switch-on (seconds)", 5, 120, 1, None, "next run"),
    "ir_protocol.post_s": ("Observation after each switch-off (seconds)", 5, 120, 1, None, "next run"),
    "ir_protocol.exclude_after_switch_s": ("Seconds ignored after every switch (electrical settling)", 0.5, 10, 0.5, None, "analysis"),
    "ir_protocol.max_burst_s": ("Hard ceiling on any single light-on period (seconds)", 1, 120, 1, None, "next run"),
    "map.kappa": ("Rapidity per reference unit: how far one unit of change moves the point", 0.05, 2.0, 0.05, None, "now"),
    "map.composition": ("How features combine into one point", None, None, None,
                        ["mobius_chain", "einstein_midpoint", "euclidean_tangent"], "now"),
    "actuators.max_on_s_per_fire": ("Most light-on time any single fire may contain (seconds)", 0.1, 120.0, 0.5, None, "next fire"),
    "actuators.max_intensity": ("Highest LED intensity any pattern may use (0-1 of the driver's range)", 0.0, 1.0, 0.05, None, "next fire"),
    "actuators.muse_dose_preset": ("Headband preset used for 'light on' with muse_optics", None, None, None,
                                   ["p1035", "p1045", "p1046", "p1041", "p1042", "p1034"], "next fire"),
    "actuators.external_led.port": ("Serial port of the LED driver, e.g. COM5", None, None, None, None, "next open"),
    "signal.sensors": ("Sensors used for every measure (forehead only: AF7, AF8)", None, None, None, None, "now"),
    "state.map": ("Which state map to use (a file in the maps folder)", None, None, None, None, "now"),
    "mre.source": ("Random-bit source for the MRE test: a USB device (serial), ANU online (remote control), sham, or off",
                   None, None, None, ["off", "serial", "anu", "sham"], "now"),
    "mre.control": ("A second arm logged at the same moments (the MRE predicts nothing in a remote or pseudo-random one)",
                    None, None, None, ["off", "anu", "sham", "serial"], "now"),
    "mre.port": ("Serial port of the USB random-number device (auto finds it)", None, None, None, None, "now"),
    "mre.mode": ("raw: a TrueRNGpro's unwhitened two-generator output (what the test needs); whitened: its normal output",
                 None, None, None, ["raw", "whitened"], "now"),
    "mre.bits_per_bin": ("Raw bits counted per 100 ms bin (0 = the device's default)", 0, 1000000, 8, None, "now"),
    "mre.anu_key": ("Key for ANU's newer QRNG API (optional; the free endpoint is used without one)", None, None, None, None, "now"),
    "mre.keep_running": ("Keep logging random bits (automation) when the window closes", None, None, None, [True, False], "now"),
    "levels.target": ("What the levels reward: auto, or your own felt state from the listening booth (once its signature passes)",
                      None, None, None, ["auto", "booth:flow", "booth:presence", "booth:horizon"], "next level"),
    "levels.replay": ("Levels: one continuous journey (off) or sealed rounds with a replay round (one)", None, None, None, ["off", "one"], "next level"),
    "levels.journey_s": ("Length of a journey (seconds)", 60, 900, 10, None, "next level"),
    "levels.ease": ("How much easier the lower tiers are, and how much of the scene always shows (0 = the paper's tiers)", 0.0, 1.0, 0.05, None, "next level"),
    "levels.carry": ("Share of falls where the scene, music and pulse lift you (the rest follow you, so the lift can be tested)", 0.0, 1.0, 0.05, None, "next level"),
    "levels.music_style": ("Music in the levels: each scene's own score, or a classical canon that evolves with you", None, None, None, ["scene", "canon"], "next level"),
    "levels.smooth_s": ("Seconds your target signal is averaged over before the scene reads it (steadier image, slower response)", 0.0, 20.0, 0.5, None, "next level"),
    "levels.use_profile": ("Let a passed attention signature replace a level's textbook index", None, None, None, [True, False], "next level"),
    "audio.enabled": ("Sound in the levels (headphones or bone conduction)", None, None, None, [True, False], "now"),
    "audio.music": ("The adaptive orchestral score in the levels", None, None, None, [True, False], "next level"),
    "audio.music_db": ("Music level against the scene sounds (dB)", -12.0, 14.0, 1.0, None, "next level"),
    "audio.volume": ("Master volume (0-1), under a hard ceiling", 0.0, 1.0, 0.05, None, "now"),
    "audio.max_db": ("Loudest the levels may ever get (dB below full scale)", -30.0, -6.0, 1.0, None, "now"),
    "audio.pacer_bpm": ("Breath pacer (breaths per minute; 6 is resonance breathing)", 3.0, 12.0, 0.5, None, "now"),
    "audio.entrain": ("Rhythmic tone at the level's target brain rhythm: sealed (random per round, revealed at the end), on, or off",
                      None, None, None, ["sealed", "on", "off"], "next level"),
    "audio.device": ("Output device id (empty = system default)", None, None, None, None, "now"),
    "display.lens": ("What the screen shows", None, None, None, ["stream", "tunnel", "map", "aurora", "web"], "now"),
    "display.speed": ("How fast the waves travel past you (hyperbolic units per second)", 0.1, 4.0, 0.05, None, "now"),
    "display.gain": ("Wave height multiplier", 0.1, 5.0, 0.05, None, "now"),
    "display.tilt": ("Tilt of the plane away from you (degrees; 0 = straight down)", 0, 70, 1, None, "now"),
    "display.glow": ("Glow strength", 0.0, 2.0, 0.05, None, "now"),
    "display.rainbow_threshold": ("Correlation needed before a rainbow shows", 0.0, 0.99, 0.01, None, "now"),
    "state.dead_band": ("IDA dead band: displacement ignored by the residue (hyperbolic units)", 0.0, 3.0, 0.05, None, "now"),
    "state.residue_beta": ("IDA residue decay rate (per second)", 0.005, 1.0, 0.005, None, "now"),
    "reference.min_readiness": ("Signal readiness needed before a calibration may start (0-1)", 0.0, 1.0, 0.05, None, "next calibration"),
    "signal.muscle_ratio_log": ("After floor removal, muscle when log10(30-45 Hz / 4-13 Hz) exceeds this", -2.0, 2.0, 0.05, None, "now"),
    "signal.muscle_burst_ratio": ("Muscle when 55-95 Hz bursts above this multiple of the sensor's own floor", 1.5, 20.0, 0.1, None, "now"),
    "signal.muscle_kurtosis": ("Muscle must be spiky: kurtosis of 30-95 Hz above this (Gaussian noise = 3)", 3.0, 30.0, 0.5, None, "now"),
    "signal.floor_correct": ("Subtract each sensor's steady high-frequency noise floor from every band", None, None, None, None, "now"),
    "signal.min_aperiodic": ("Electrode counts as noise when its 1/f exponent is below this", -1.0, 2.0, 0.05, None, "now"),
    "mre.levels": ("Quantization levels for the Φ entropy-rate estimate", 2, 64, 1, None, "now"),
    "mre.delta_hz": ("Rate at which the EEG alternation measure is sampled (Hz; not the MRE's δ, which is of an external random source)", 2.0, 128.0, 1.0, None, "now"),
    "mre.phi_smooth_s": ("Smoothing of Φ (seconds; the MRE uses 10)", 0.5, 60.0, 0.5, None, "now"),
    "simulator.ir_effect": ("Simulator only: injected alpha effect of light (0 = none)", 0.0, 2.0, 0.05, None, "now"),
    "simulator.switch_artifact_uv": ("Simulator only: electrical step when the optics toggle (µV)", 0, 300, 5, None, "now"),
    "simulator.auto_probe_accuracy": ("Simulator only: auto-answer probes with this accuracy (0 = off)", 0.0, 1.0, 0.05, None, "now"),
}


def flatten(d: Any, prefix: str = "") -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flatten(v, f"{prefix}{k}."))
    elif isinstance(d, list) and d and all(not isinstance(v, (dict, list)) for v in d):
        for i, v in enumerate(d):
            out[f"{prefix}{i}"] = v
    elif isinstance(d, list):
        for i, v in enumerate(d):
            out.update(flatten(v, f"{prefix}{i}."))
    else:
        out[prefix[:-1]] = d
    return out


def _walk(root: Any, path: str) -> Tuple[Any, Any]:
    parts = path.split(".")
    node = root
    for p in parts[:-1]:
        node = node[int(p)] if isinstance(node, list) else node[p]
    last = parts[-1]
    return node, (int(last) if isinstance(node, list) else last)


def get(root: Any, path: str) -> Any:
    node, key = _walk(root, path)
    return node[key]


def coerce(old: Any, value: Any) -> Any:
    if isinstance(old, list):
        if isinstance(value, str):
            value = [v.strip() for v in value.split(",") if v.strip()]
        return list(value)
    if isinstance(old, bool):
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        return bool(value)
    if isinstance(old, int) and not isinstance(old, bool):
        f = float(value)
        return int(f) if f.is_integer() else f
    if isinstance(old, float):
        return float(value)
    if old is None:
        if value in ("", None, "null", "none"):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return str(value)
    return str(value)


def set_value(root: Any, path: str, value: Any, full: Optional[str] = None) -> Tuple[Any, Any]:
    """Set one knob. `full` is the knob's full name when `root` is a sub-tree (the map)."""
    full = full or path
    node, key = _walk(root, path)
    old = node[key]
    new = coerce(old, value)
    meta = META.get(full)
    if meta:
        _, lo, hi, _, choices, _ = meta
        if choices and new not in choices:
            raise ValueError(f"{path} must be one of {choices}")
        if lo is not None and isinstance(new, (int, float)) and not (lo <= new <= hi):
            raise ValueError(f"{path} must be between {lo} and {hi}")
    if full.startswith("map.axes.") and full.endswith(".feature") and new not in FEATURE_CHOICES:
        raise ValueError(f"feature must be one of {FEATURE_CHOICES}")
    node[key] = new
    return old, new


def describe(settings: dict, smap: dict) -> List[dict]:
    """Everything the knob panel needs, grouped by first path segment."""
    rows = []
    both = {"map": {k: v for k, v in smap.items() if k not in ("name", "note")}, **settings}
    for path, value in flatten(both).items():
        meta = META.get(path)
        if path.startswith("map.axes.") and path.endswith(".feature"):
            meta = ("Which feature this compass direction shows", None, None, None, FEATURE_CHOICES, "now")
        elif path.startswith("map.axes.") and path.endswith(".angle_deg"):
            meta = ("Compass direction of this feature on the disk (degrees; 90 = up)", -180, 360, 5, None, "now")
        elif path.startswith("map.axes.") and path.endswith(".weight"):
            meta = ("How strongly this feature moves the point (0 removes it)", 0.0, 5.0, 0.1, None, "now")
        applies = meta[5] if meta else ("restart" if path.startswith(("server.", "paths.")) else "now")
        rows.append({
            "path": path, "group": path.split(".")[0], "value": value,
            "type": "bool" if isinstance(value, bool) else "number" if isinstance(value, (int, float)) else "text",
            "description": meta[0] if meta else "", "min": meta[1] if meta else None,
            "max": meta[2] if meta else None, "step": meta[3] if meta else None,
            "choices": meta[4] if meta else None, "applies": applies,
        })
    return rows


def snapshot(settings: dict, smap: dict) -> dict:
    return {"settings": copy.deepcopy(settings), "map": copy.deepcopy(smap)}


def diff(a: dict, b: dict) -> Dict[str, Tuple[Optional[Any], Optional[Any]]]:
    fa, fb = flatten(a), flatten(b)
    return {k: (fa.get(k), fb.get(k)) for k in set(fa) | set(fb) if fa.get(k) != fb.get(k)}
