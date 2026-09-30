"""Plain-English session summaries and chart series (no Office, no special software).

write_summary(folder) writes summary.txt into a finished session folder.
series(folder) returns downsampled measures for the Sessions view in the app.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

from .common import Session

MEASURES = [
    ("phi", "state", "Φ information rate (bits/s, LZ estimate; MRE uses CTW)"),
    ("lzc", "state", "LZ complexity"),
    ("alt", "state", "EEG alternation (proxy, not the MRE's δ)"),
    ("aperiodic", "features", "1/f exponent"),
    ("d", "state", "IDA displacement from reference"),
    ("residue", "state", "IDA residue"),
    ("readiness", "state", "signal readiness"),
]


def _col(s: Session, table: str, name: str):
    t = s.state if table == "state" else s.features
    if t.n == 0 or not t.has(name):
        return None, None
    return t["t"], t[name]


def _clock(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    return f"{seconds // 60}:{seconds % 60:02d}"


def write_summary(folder: Path) -> Path:
    s = Session(folder)
    m = s.manifest
    t0 = s.t_start
    end = next((e["t"] for e in s.events if e["kind"] == "session_end"), None)
    dur = (end - t0) if end else (s.state["t"][-1] - t0 if s.state.n else 0)
    lines: List[str] = []
    add = lines.append
    add(f"IDA Live session: {folder.name}")
    add(f"Started {m.get('started', '?')}  ·  length {_clock(dur)}  ·  app {m.get('version', '?')}")
    src = m.get("source") or {}
    add(f"Source: {src.get('name') or src.get('kind', '?')}  ·  preset {src.get('preset', '?')}")
    ref = m.get("reference") or {}
    add(f"Reference: {ref.get('ref_id', '?')} (made {ref.get('created', '?')})")
    add("")
    if s.state.n:
        clean = s.state["clean"]
        add(f"Clean signal: {100 * np.nanmean(clean):.0f}% of the time")
        reasons: Dict[str, int] = {}
        for r in s.state["reasons"]:
            for k in str(r).split("|"):
                if k and k != "nan":
                    reasons[k] = reasons.get(k, 0) + 1
        if reasons:
            add("Held back because of: " + ", ".join(f"{k} {100 * v / s.state.n:.0f}%" for k, v in sorted(reasons.items(), key=lambda kv: -kv[1])))
    add("")
    add("Measures over clean moments (mean ± spread, first third → last third):")
    for name, table, label in MEASURES:
        t, v = _col(s, table, name)
        if v is None:
            continue
        ok = np.isfinite(v)
        if table == "state" and s.state.has("clean"):
            ok &= s.state["clean"] == 1
        if ok.sum() < 4:
            continue
        vv = v[ok]
        third = max(1, len(vv) // 3)
        add(f"  {label:<38} {np.mean(vv):8.3f} ± {np.std(vv):.3f}   ({np.mean(vv[:third]):.3f} → {np.mean(vv[-third:]):.3f})")
    add("")
    probes = [e for e in s.events if e["kind"] == "answer" and e.get("question") == "probe"]
    if probes:
        counts: Dict[str, int] = {}
        for e in probes:
            counts[str(e.get("answer"))] = counts.get(str(e.get("answer")), 0) + 1
        add("Thought probes: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    caught = [e for e in s.events if e["kind"] == "self_caught"]
    if caught:
        add(f"You caught yourself drifting {len(caught)} time(s)")
    marks = [e for e in s.events if e["kind"] == "mark"]
    if marks:
        add("Markers:")
        for e in marks:
            add(f"  {_clock(e['t'] - t0)}  {e.get('label', '')}" + (f"  (by {e['by']})" if e.get("by") not in (None, "you") else ""))
    knobs = [e for e in s.events if e["kind"] == "knob" and not str(e.get("path", "")).startswith("display.")]
    if knobs:
        add("Settings changed during the recording:")
        for e in knobs:
            add(f"  {_clock(e['t'] - t0)}  {e.get('path')}: {e.get('old')} → {e.get('new')}" + (f"  (by {e['by']})" if e.get("by") not in (None, "you") else ""))
    light = [e for e in s.events if e["kind"] in ("light_protocol_start", "recipe_start")]
    if light:
        add(f"Light protocols run: {len(light)} (see the light and recipe reports; allocations stay sealed until revealed)")
    add("")
    add("Files in this folder (all plain text; Notepad opens every one):")
    add("  summary.txt      this page")
    add("  state.csv        your state 4 times a second: map position, IDA and MRE measures")
    add("  features.csv     every signal feature 4 times a second, with artifact flags")
    add("  eeg.csv          the raw EEG, 256 samples a second per sensor")
    add("  events.jsonl     every probe, answer, marker, setting change and light event, one per line")
    add("  manifest.json    the exact settings, map and reference used")
    add("  raw_ble.txt      the untouched headband bytes, so any later version can re-analyse this session")
    add("")
    add(f"Written {time.strftime('%Y-%m-%d %H:%M:%S')}")
    path = folder / "summary.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def series(folder: Path, max_points: int = 600) -> dict:
    s = Session(folder)
    t0 = s.t_start
    out: Dict[str, object] = {"name": folder.name, "measures": {}}
    for name, table, label in MEASURES:
        t, v = _col(s, table, name)
        if v is None:
            continue
        step = max(1, len(v) // max_points)
        tt = ((t - t0)[::step]).round(2)
        vv = v[::step]
        out["measures"][name] = {"label": label, "t": tt.tolist(),
                                 "v": [None if not np.isfinite(x) else round(float(x), 4) for x in vv]}
    ev = []
    for e in s.events:
        if e["kind"] == "answer" and e.get("question") == "probe" and e.get("answer"):
            ev.append({"t": round(e["t_prompt"] - t0, 2), "kind": "probe", "answer": e["answer"]})
        elif e["kind"] in ("mark", "self_caught", "trigger"):
            ev.append({"t": round(e["t"] - t0, 2), "kind": e["kind"], "label": e.get("label", "")})
    out["events"] = ev
    summ = folder / "summary.txt"
    out["summary"] = summ.read_text(encoding="utf-8") if summ.exists() else ""
    return out


def list_sessions(root: Path) -> list:
    rows = []
    for d in sorted((p for p in root.iterdir() if p.is_dir()), reverse=True)[:200]:
        mf = d / "manifest.json"
        if not mf.exists():
            continue
        try:
            m = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            continue
        summ = (m.get("summary") or {})
        rows.append({"name": d.name, "started": m.get("started"), "ended": m.get("ended"),
                     "probes": summ.get("n_probes"), "has_summary": (d / "summary.txt").exists()})
    return rows
