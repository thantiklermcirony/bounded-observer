"""Settings. Defaults live here; `settings.json` in the app folder overrides any of them.

Every number that affects what the app concludes is in this file (or the map file),
so a session's manifest can record exactly what produced its results.
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any, Dict

APP_DIR = Path(__file__).resolve().parent.parent
INSTALLED = (APP_DIR / "installed.flag").exists()


def _data_dir() -> Path:
    """Where your recordings, references, recipes and settings live.

    Installed app: Documents/IDA Live (kept when the app is updated or uninstalled).
    Unzipped developer copy: the app folder itself. IDA_LIVE_DATA overrides both.
    """
    if os.environ.get("IDA_LIVE_DATA"):
        d = Path(os.environ["IDA_LIVE_DATA"])
    elif INSTALLED:
        docs = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Documents"
        d = (docs if docs.exists() else Path.home()) / "IDA Live"
    else:
        d = APP_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


DATA_DIR = _data_dir()

DEFAULTS: Dict[str, Any] = {
    "server": {"host": "127.0.0.1", "port": 8765, "open_browser": True, "app_window": True,
               "close_with_window": True},
    "paths": {"sessions": "sessions", "references": "references", "maps": "maps", "recipes": "recipes"},
    "device": {
        "address": "",
        # Presets documented by OpenMuse. p20: 4 EEG channels, optics off.
        # p1035: same 4 EEG channels plus the inner IR (850 nm) and near-IR (730 nm) optics.
        # p1041: 8 EEG channels plus all 16 optics channels, including red (660 nm).
        # Default is p20: EEG only, every light off. Monitoring with the optics on would
        # light your forehead the whole time and confound any light experiment.
        # Choose p1035 (dim, IR + near-IR, gives heart rate) if you want the optics.
        "monitor_preset": "p20",
        "raw_log": True,
    },
    "signal": {
        "mains_hz": 50,
        # Sensors used for every measure. ["AF7", "AF8"] is forehead-only mode, for when the
        # ear sensors won't make clean contact (use it with the "forehead" map).
        "sensors": ["TP9", "AF7", "AF8", "TP10"],
        "window_s": 2.0,
        "tick_hz": 4.0,
        "bands": {
            "delta": [1, 4],
            "theta": [4, 8],
            "alpha": [8, 13],
            "beta": [13, 30],
            "gamma": [30, 45],
        },
        "blink_uv": 150.0,
        "motion_dps": 12.0,
        "emg_z": 3.0,
        # Provisional contact-quality limits on 1-40 Hz standard deviation (µV).
        "quality_good_uv": 60.0,
        "quality_ok_uv": 150.0,
        "quality_flat_uv": 0.5,
        # Muscle = 55-95 Hz power bursting above this multiple of the sensor's own floor.
        "muscle_burst_ratio": 3.0,
        # ...and only if it is spiky (kurtosis of 30-95 Hz above this; Gaussian noise is 3)
        # or local to that sensor. Smooth power shared by all sensors is interference.
        "muscle_kurtosis": 5.0,
        # Subtract each sensor's steady high-frequency floor from every band.
        "floor_correct": True,
        # After floor removal, 30-45 Hz this far above 4-13 Hz (log10) is still muscle.
        "muscle_ratio_log": 0.5,
        # Scalp EEG falls with frequency; an electrode whose 1/f exponent is below this
        # is reading noise, not brain.
        "min_aperiodic": 0.3,
    },
    "mre": {
        # Murray Reality Equation measures (features.Complexity)
        "levels": 8,          # quantization levels for the entropy-rate estimate of Φ
        "delta_hz": 20.0,     # sample rate at which the alternation bias δ is taken
        "phi_smooth_s": 10.0, # the MRE smooths Φ over 10 s
        # the random-bit test of the MRE (mre/qrng.py, analysis/mre.py, docs/MRE.md)
        "source": "off",      # off | serial (a USB random-number device) | anu (online) | sham
        "control": "off",     # a second arm logged at the same moments: off | anu | sham | serial
        "port": "auto",       # serial port of the USB device (auto finds TrueRNG/OneRNG/Quantis)
        "mode": "raw",        # raw: TrueRNGpro's unwhitened two-generator mode; whitened: its normal output
        "bits_per_bin": 0,    # raw bits counted per 100 ms bin (0: the device's default)
        "anu_key": "",        # optional key for ANU's newer API (quantumnumbers.anu.edu.au)
        "sham_seed": 12345,
        "keep_running": True, # keep logging (automation, C1) after the window closes
    },
    "reference": {"calibration_s": 60,          # seconds of CLEAN signal a calibration collects
                  "max_calibration_s": 300,     # give up if that takes longer than this
                  "ear_min_share": 0.8,         # ear sensors join only if clean this share of the time
                  "min_clean_fraction": 0.5, "drift_tau_s": 300, "min_readiness": 0.6},
    "state": {"map": "default", "smooth_tau_s": 2.0, "return_radius": 0.5, "return_hold_s": 2.0,
              # IDA residue (IDA and the Boundedness Engine, section 6): leaky memory of the
              # displacement left outside a dead band, dR/dt = e - beta R, e = max(0, d - dead_band)
              "dead_band": 0.6, "residue_beta": 0.05},
    "probes": {"min_interval_s": 45, "max_interval_s": 90, "pre_window_s": 5.0},
    "ir_protocol": {
        "baseline_preset": "p20",
        "dose_presets": {"nothing": None, "small": "p1035", "larger": "p1041"},
        "trials": 12,
        "block_size": 4,
        "pre_s": 20.0,
        "burst_s": {"nothing": 8.0, "small": 8.0, "larger": 15.0},
        "post_s": 25.0,
        "iti_jitter_s": [10.0, 25.0],
        "exclude_after_switch_s": 3.0,
        "max_burst_s": 30.0,
        "ask_guess": True,
    },
    "stimuli": {"max_flash_hz": 3.0, "max_luminance_step": 0.1},
    # sound for the levels (headphones or bone conduction). Output goes to the system's
    # default device unless you pick one in Sound. Loudness is capped and every change ramps.
    "audio": {"enabled": True, "music": True, "music_db": 8.0, "volume": 0.7, "max_db": -12.0, "pacer_bpm": 6.0, "entrain": "sealed",
              "device": ""},
    "actuators": {
        # Hard ceilings checked before any pattern is sent. The LED firmware has its own too.
        "max_on_s_per_fire": 30.0,
        "max_intensity": 1.0,
        "muse_dose_preset": "p1035",
        "external_led": {"port": "", "baud": 115200},
    },
    "display": {
        # What the screen shows. Claude can change these live through the control folder.
        "lens": "stream",           # stream | tunnel | map | aurora | web
        "bands": ["delta", "theta", "alpha", "beta", "gamma"],
        "amplitude": True,          # line thickness follows amplitude
        "rainbows": True,           # rainbow sheets where signals move together
        "rainbow_threshold": 0.55,  # correlation above which a rainbow appears
        "hemispheres": False,       # split each band into left and right brain
        "ida": True,                # your IDA state moves the whole field
        "grid": True,
        "speed": 1.4,               # hyperbolic units per second the stream travels
        "gain": 1.0,                # wave height multiplier
        "tilt": 38,                 # degrees the plane is tilted away from you (0 = top-down)
        "glow": 1.0,
    },
    "control": {"enabled": True, "poll_s": 0.5, "live_every_s": 1.0},
    # what the levels reward: auto (the level's own index, or your attention signature when it has
    # passed its test), or one of your listening-booth signatures once it has passed its test
    # journey: one continuous run (replay "off") or the old sealed rounds with a replay ("one");
    # ease: how much easier the lower tiers are and how much of the scene always shows (0-1);
    # carry: share of falls where the scene, music and pulse lift you (the rest simply follow you,
    # so the lift can be tested); music_style: each scene's own score, or "canon" (a classical
    # ground that evolves with you)
    "levels": {"use_profile": True, "target": "auto", "replay": "off", "journey_s": 180, "ease": 0.6,
               "carry": 0.75, "music_style": "scene", "smooth_s": 5.0, "search_scene": "still"},
    "simulator": {"auto_probe_accuracy": 0.0, "ir_effect": 0.0, "switch_artifact_uv": 80.0, "seed": None},
}


def _merge(base: Dict[str, Any], over: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load_settings(path: Path | None = None) -> Dict[str, Any]:
    path = path or DATA_DIR / "settings.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return _merge(DEFAULTS, json.load(f))
    return copy.deepcopy(DEFAULTS)


def resolve(settings: Dict[str, Any], key: str) -> Path:
    p = Path(settings.get("paths", {}).get(key, DEFAULTS["paths"][key]))
    p = p if p.is_absolute() else DATA_DIR / p
    fresh = not p.exists()
    p.mkdir(parents=True, exist_ok=True)
    # first run of an installed copy: seed your folders with the bundled maps and recipes
    builtin = APP_DIR / key
    if key in ("maps", "recipes") and builtin.is_dir() and builtin.resolve() != p.resolve():
        for f in builtin.glob("*.json"):
            # maps: always make sure the built-ins exist; recipes: only on first run,
            # so a recipe you delete stays deleted
            if (key == "maps" and not (p / f.name).exists()) or fresh:
                (p / f.name).write_bytes(f.read_bytes())
    return p
