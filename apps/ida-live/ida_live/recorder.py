"""Session recording.

Each session folder holds:
  manifest.json          versions, settings, map, reference id, source
  raw_ble.txt            every BLE packet in OpenMuse's format (headband sessions)
  eeg.csv, accgyro.csv, optics.csv   decoded samples on the session clock
  features.csv           every feature at 4 Hz, with artifact flags
  state.csv              the disk point, comparators, drift, per-feature z
  events.jsonl           probes, answers, switches, protocol events, notes
  allocation.sealed.json light-trial allocation (only if trials were run)

Raw first, derived second: any later version of the app can recompute features
and state from the raw files, so nothing here locks the analysis in.
"""

from __future__ import annotations

import csv
import json
import platform
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, TextIO

from . import __version__
from .core import Chunk


class Recorder:
    def __init__(self, root: Path, label: str, manifest: dict):
        stamp = time.strftime("%Y-%m-%d_%H%M%S")
        safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in label.strip())[:40] or "session"
        self.folder = root / f"{stamp}_{safe}"
        self.folder.mkdir(parents=True, exist_ok=False)
        self.t0: Optional[float] = None
        self._files: Dict[str, TextIO] = {}
        self._writers: Dict[str, csv.writer] = {}
        self._channels: Dict[str, List[str]] = {}
        self._layouts: Dict[str, int] = {}
        self._raw = open(self.folder / "raw_ble.txt", "w", encoding="utf-8")
        self._events = open(self.folder / "events.jsonl", "w", encoding="utf-8")
        self.manifest = {
            "app": "IDA Live", "version": __version__, "python": sys.version.split()[0],
            "platform": platform.platform(), "started": time.strftime("%Y-%m-%d %H:%M:%S"),
            "clock": "seconds on the session clock (time.perf_counter); t0 recorded below",
            **manifest,
        }
        self._write_manifest()

    def _write_manifest(self) -> None:
        with open(self.folder / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=1, default=str)

    def set_t0(self, t0: float) -> None:
        self.t0 = t0
        self.manifest["t0"] = t0
        self._write_manifest()

    def raw(self, line: str) -> None:
        self._raw.write(line + "\n")

    def chunk(self, c: Chunk) -> None:
        key = c.stream.lower()
        if key == "battery":
            return
        if key not in self._writers or self._channels.get(key) != c.channels:
            n = self._layouts.get(key, 0)
            self._layouts[key] = n + 1
            if key in self._files:
                self._files[key].close()
            key_file = f"{key}.csv" if n == 0 else f"{key}_layout{n + 1}.csv"
            f = open(self.folder / key_file, "w", newline="", encoding="utf-8")
            w = csv.writer(f)
            w.writerow(["t"] + list(c.channels))
            self._files[key], self._writers[key], self._channels[key] = f, w, list(c.channels)
        w = self._writers[key]
        for ti, row in zip(c.t, c.x):
            w.writerow([f"{ti:.5f}"] + [f"{v:.4f}" for v in row])

    FEATURE_COLUMNS = ["t", "alpha_tp", "theta_af", "beta", "delta_af", "gamma_tp", "emg_tp", "emg_af", "hum_tp", "hum_af",
                       "alpha_theta", "aperiodic", "lp_delta", "lp_theta", "lp_alpha", "lp_beta", "lp_gamma",
                       "phi", "phi_ctw", "phi_ctw_raw", "lzc", "alt", "alt_rapidity", "readiness", "brain_slope", "ix_alpha_rel", "ix_engagement", "ix_alpha_rel3", "ix_faa", "ix_theta_af_rel",
                       "blink_ptp", "motion_dps", "breath_bpm", "breath_conf", "breath_sync", "heart_bpm", "blink", "motion", "muscle", "quality"]
    STATE_BASE = ["t", "clean", "reasons", "x", "y", "d", "angle", "euc_x", "euc_y",
                  "mid_x", "mid_y", "defect", "drift_x", "drift_y", "drift_d",
                  "excess", "residue", "S1", "S5", "S30", "S120", "phi", "lzc", "alt", "alt_rapidity", "readiness"]

    def features(self, t: float, vals: dict, flags: dict) -> None:
        row = {"t": round(t, 4), **{k: round(v, 5) for k, v in vals.items()},
               "blink": int(bool(flags.get("blink"))), "motion": int(bool(flags.get("motion"))),
               "muscle": int(bool(flags.get("muscle"))),
               "quality": "|".join(flags.get("quality") or [])}
        self._table("features", self.FEATURE_COLUMNS, row)

    def state(self, st: dict, z_names: List[str]) -> None:
        row = {k: (round(v, 5) if isinstance(v, float) else v) for k, v in st.items()
               if k not in ("z", "reasons", "last_return", "calibrated", "return_score")}
        for k, v in (st.get("return_score") or {}).items():
            row[k] = round(v, 5)
        row["clean"] = int(bool(st.get("clean")))
        row["reasons"] = "|".join(st.get("reasons", []))
        for k, v in (st.get("z") or {}).items():
            row[f"z_{k}"] = round(v, 4)
        self._table("state", self.STATE_BASE + [f"z_{k}" for k in z_names], row)

    def _table(self, name: str, columns: List[str], row: dict) -> None:
        if name not in self._writers:
            f = open(self.folder / f"{name}.csv", "w", newline="", encoding="utf-8")
            self._files[name] = f
            self._writers[name] = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore", restval="")
            self._writers[name].writeheader()
        self._writers[name].writerow(row)

    def event(self, kind: str, data: dict) -> None:
        self._events.write(json.dumps({"kind": kind, **data}, default=str) + "\n")
        self._events.flush()

    def close(self, summary: dict) -> None:
        self.manifest["ended"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.manifest["summary"] = summary
        self._write_manifest()
        for f in list(self._files.values()) + [self._raw, self._events]:
            try:
                f.close()
            except Exception:
                pass
