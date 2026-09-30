"""Frozen reference, the state map, and the hyperbolic state engine.

The IDA quantities this implements (from "IDA and the Boundedness Engine"):
* frozen reference: a baseline recorded once, then held fixed so "improvement"
  can never be produced by quietly moving the reference;
* displacement: how far the current state sits from that reference;
* return: how long it takes to come back within a declared radius after an event;
* baseline drift: where a slow running baseline has wandered to, measured against
  the frozen reference in the same geometry.

How features become a point (the "map"):
Each feature is expressed as a robust z-score against the frozen reference,
scaled by kappa into a rapidity, placed on its declared compass direction, and the
per-feature points are composed by Möbius addition in the declared order. The
directions are a readable starting hypothesis, not a finding. The calibration gate
(ida_live.analysis.gate) decides whether this geometry predicts anything.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from . import geometry as geo


# ---------------------------------------------------------------- map
@dataclass
class Axis:
    feature: str
    angle_deg: float
    weight: float = 1.0
    label: str = ""


@dataclass
class StateMap:
    name: str
    axes: List[Axis]
    kappa: float = 0.5
    composition: str = "mobius_chain"
    note: str = ""

    @classmethod
    def load(cls, path: Path) -> "StateMap":
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        axes = [Axis(**a) for a in d.pop("axes")]
        return cls(axes=axes, **d)

    def to_dict(self) -> dict:
        return {**asdict(self), "axes": [asdict(a) for a in self.axes]}

    @property
    def features(self) -> List[str]:
        return [a.feature for a in self.axes]


# ---------------------------------------------------------------- reference
@dataclass
class FrozenReference:
    median: Dict[str, float]
    scale: Dict[str, float]
    n_ticks: int
    created: str
    note: str = ""
    ref_id: str = ""

    def __post_init__(self):
        if not self.ref_id:
            blob = json.dumps({"m": self.median, "s": self.scale, "c": self.created}, sort_keys=True)
            self.ref_id = hashlib.sha256(blob.encode()).hexdigest()[:12]

    def z(self, vals: Dict[str, float]) -> Dict[str, float]:
        return {k: (vals[k] - self.median[k]) / self.scale[k] for k in self.median if k in vals}

    def save(self, folder: Path, name: str) -> Path:
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=1)
        return path

    @classmethod
    def load(cls, path: Path) -> "FrozenReference":
        with open(path, "r", encoding="utf-8") as f:
            return cls(**json.load(f))


class ReferenceBuilder:
    """Collects clean ticks during calibration, then freezes median and robust scale."""

    def __init__(self, features: List[str], min_clean_fraction: float):
        self.features = features
        self.min_clean = min_clean_fraction
        self.rows: List[Dict[str, float]] = []
        self.total = 0

    def add(self, vals: Dict[str, float], clean: bool) -> None:
        self.total += 1
        if clean and all(k in vals for k in self.features):
            self.rows.append({k: vals[k] for k in self.features})

    def freeze(self, note: str = "") -> FrozenReference:
        if self.total == 0 or len(self.rows) < max(20, self.min_clean * self.total):
            frac = len(self.rows) / max(1, self.total)
            raise ValueError(
                f"Ran out of time: only {len(self.rows) / 4:.0f} clean seconds were collected ({frac:.0%} of the time). "
                "Check the electrode contact, sit still, and calibrate again."
            )
        if "brain_slope" in self.features:
            ap = float(np.median([r["brain_slope"] for r in self.rows]))
            if ap < 0.3:
                raise ValueError(
                    "The calibration looks like electrical noise, not brain signal "
                    f"(the 2-20 Hz spectrum does not fall with frequency: slope {ap:.2f}). "
                    "Wet the sensors, move hair from under them, relax your jaw, and calibrate again."
                )
        med, scale = {}, {}
        for k in self.features:
            v = np.array([r[k] for r in self.rows])
            m = float(np.median(v))
            mad = float(np.median(np.abs(v - m))) * 1.4826
            med[k] = m
            scale[k] = max(mad, 0.05 * abs(m), 1e-3)
        return FrozenReference(med, scale, len(self.rows), time.strftime("%Y-%m-%d %H:%M:%S"), note)


# ---------------------------------------------------------------- engine
@dataclass
class ReturnTracker:
    radius: float
    hold_s: float
    pending: Optional[tuple] = None  # (t_event, kind)
    inside_since: Optional[float] = None
    last: Optional[dict] = None

    def mark(self, t: float, kind: str) -> None:
        self.pending = (t, kind)
        self.inside_since = None

    def update(self, t: float, d: float) -> None:
        if self.pending is None:
            return
        if d <= self.radius:
            if self.inside_since is None:
                self.inside_since = t
            elif t - self.inside_since >= self.hold_s:
                self.last = {"kind": self.pending[1], "seconds": round(self.inside_since - self.pending[0], 2)}
                self.pending = None
        else:
            self.inside_since = None


@dataclass
class StateEngine:
    smap: StateMap
    reference: Optional[FrozenReference]
    settings: dict
    _zs: Dict[str, float] = field(default_factory=dict)
    _slow: Dict[str, float] = field(default_factory=dict)
    _t_prev: Optional[float] = None
    _held: Optional[dict] = None
    _emg_anchor: Optional[tuple] = None
    _emg_anchor_hist: list = field(default_factory=list)

    def __post_init__(self):
        st = self.settings["state"]
        self.tau = float(st["smooth_tau_s"])
        self.drift_tau = float(self.settings["reference"]["drift_tau_s"])
        self.returns = ReturnTracker(float(st["return_radius"]), float(st["return_hold_s"]))
        self.thetas = [math.radians(a.angle_deg) for a in self.smap.axes]
        self.emg_z = float(self.settings["signal"]["emg_z"])
        self.dead_band = float(st.get("dead_band", 0.6))
        self.beta = float(st.get("residue_beta", 0.05))
        self.phi_tau = float(self.settings.get("mre", {}).get("phi_smooth_s", 10.0))
        self.residue = 0.0
        self._dhist: List[tuple] = []
        self._mre: Dict[str, float] = {}

    def is_clean(self, vals: Dict[str, float], flags: Dict[str, object]) -> tuple:
        reasons = []
        q = flags.get("quality") or []
        use = flags.get("sensors") or [0, 1, 2, 3]
        n_ok = sum(q[i] in ("good", "ok", "interference", "eyes") for i in use) if q else 0
        if not q or n_ok < (len(use) - 1 if len(use) > 2 else len(use)):
            reasons.append("contact")
        # one sensor having a bad moment is tolerated when three or more are in use
        if flags.get("blink"):
            reasons.append("blink")
        if flags.get("motion"):
            reasons.append("movement")
        if flags.get("eyes"):
            reasons.append("eyes")
        if flags.get("muscle"):
            reasons.append("muscle")
        # Sustained tension that the burst test (relative to the last minute) would absorb: compare
        # with THIS session's own first minute, not a calibration from another day (the headband
        # never sits the same way twice), and only when the ear sensors' hum hasn't risen with it
        # (then it is contact, not jaw).
        if "emg_tp" in vals and "hum_tp" in vals:
            hist = self._emg_anchor_hist
            if len(hist) < 240:
                if not flags.get("loose") and not flags.get("muscle"):
                    hist.append((vals["emg_tp"], vals["hum_tp"]))
            elif self._emg_anchor is None:
                a = np.array(hist)
                self._emg_anchor = (float(np.median(a[:, 0])), float(np.median(a[:, 1])))
            if self._emg_anchor is not None:
                scale = (self.reference.scale.get("emg_tp") if self.reference else None) or 0.2
                rise = vals["emg_tp"] - self._emg_anchor[0]
                hum_rise = vals["hum_tp"] - self._emg_anchor[1]
                if rise / scale > self.emg_z and hum_rise < 0.3 and "muscle" not in reasons:
                    reasons.append("muscle")
        if not all(f in vals for f in self.smap.features):
            reasons.append("no signal")
        return (len(reasons) == 0, reasons)

    def _point(self, z: Dict[str, float], method: Optional[str] = None) -> complex:
        rs = [a.weight * self.smap.kappa * z.get(a.feature, 0.0) for a in self.smap.axes]
        return geo.compose(rs, self.thetas, method or self.smap.composition)

    def update(self, t: float, vals: Dict[str, float], flags: Dict[str, object]) -> dict:
        clean, reasons = self.is_clean(vals, flags)
        out = {"t": t, "clean": clean, "reasons": reasons, "calibrated": self.reference is not None}
        if "readiness" in vals:
            out["readiness"] = vals["readiness"]
        dt = 0.25 if self._t_prev is None else min(2.0, max(1e-3, t - self._t_prev))
        self._t_prev = t
        # MRE observer measures (shown before calibration too; smoothed only on clean ticks)
        if clean:
            for k, tau in (("phi", self.phi_tau), ("lzc", self.tau), ("alt", self.tau)):
                if k in vals:
                    a = 1.0 - math.exp(-dt / tau)
                    self._mre[k] = vals[k] if k not in self._mre else self._mre[k] + a * (vals[k] - self._mre[k])
        out.update({k: v for k, v in self._mre.items()})
        if "alt" in self._mre:
            out["alt_rapidity"] = math.atanh(max(-0.999, min(0.999, self._mre["alt"])))
        if self.reference is None or any(f not in self.reference.median for f in self.smap.features):
            out["calibrated"] = False
            return out
        if not clean:
            if self._held:
                out.update({k: v for k, v in self._held.items() if k not in ("t", "clean", "reasons")})
            return out
        z_now = self.reference.z({k: vals[k] for k in self.smap.features})
        a = 1.0 - math.exp(-dt / self.tau)
        for k, v in z_now.items():
            self._zs[k] = v if k not in self._zs else self._zs[k] + a * (v - self._zs[k])
        b = 1.0 - math.exp(-dt / self.drift_tau)
        for k in self.smap.features:
            self._slow[k] = vals[k] if k not in self._slow else self._slow[k] + b * (vals[k] - self._slow[k])
        p = self._point(self._zs)
        pts = [geo.from_rapidity(ax.weight * self.smap.kappa * self._zs[ax.feature], th)
               for ax, th in zip(self.smap.axes, self.thetas)]
        euc = self._point(self._zs, "euclidean_tangent")
        mid = self._point(self._zs, "einstein_midpoint")
        drift_p = self._point(self.reference.z(self._slow))
        d = geo.rapidity(p)
        self.returns.update(t, d)
        # IDA residue and multi-scale return score (IDA and the Boundedness Engine, 6 and 6.3)
        e = max(0.0, d - self.dead_band)
        decay = math.exp(-self.beta * dt)
        self.residue = self.residue * decay + e * (1.0 - decay)
        self._dhist.append((t, d))
        while self._dhist and t - self._dhist[0][0] > 125.0:
            self._dhist.pop(0)
        ret = {}
        for lag in (1, 5, 30, 120):
            past = [dd for tt, dd in self._dhist if tt <= t - lag]
            if past:
                ret[f"S{lag}"] = (past[-1] - d) / lag
        out.update({
            "x": p.real, "y": p.imag, "d": d, "angle": math.degrees(math.atan2(p.imag, p.real)),
            "z": dict(self._zs),
            "euc_x": euc.real, "euc_y": euc.imag,
            "mid_x": mid.real, "mid_y": mid.imag,
            "defect": geo.composition_defect(pts),
            "drift_x": drift_p.real, "drift_y": drift_p.imag, "drift_d": geo.rapidity(drift_p),
            "last_return": self.returns.last,
            "excess": e, "residue": self.residue, "return_score": ret,
        })
        self._held = out
        return out
