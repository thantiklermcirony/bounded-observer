"""The calibration gate for the state map.

Question: does position in the hyperbolic map, taken from the seconds BEFORE a
thought probe, predict your answer ("on what I intended" vs "wandered off") on
sessions the model never saw, better than simple alternatives?

Everything below is declared before any real data exists (see docs/GATE.md) and
must not be tuned after looking at results. Changing it means a new gate version.

Models (logistic regression, ridge lambda = 1, leave-one-session-out):
  M0 time      minutes since session start
  M1 index     alpha/theta log ratio (a plain neurofeedback index)
  M2 map       hyperbolic map position: x, y, displacement d
  M3 flat      Euclidean comparator with the same axes: x, y, displacement

Gate v1 passes when, on pooled held-out predictions:
  AUC(M2) >= 0.60, AUC(M2) >= AUC(M0) + 0.05, AUC(M2) >= AUC(M1) + 0.05,
with at least 3 sessions, 60 answered probes, and 15 of each answer.
M2 vs M3 is reported as a separate question (does curvature earn its place?);
it is not part of pass/fail.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import numpy as np

from ..config import load_settings, resolve
from .common import Session, auc, find_sessions, fit_logistic, predict_logistic

GATE_VERSION = 1
# Gate v2 addendum, declared 25 September 2026 before any data: candidate awareness
# measures, each tested alone the same way (single-feature logistic, leave-one-session-out).
# A candidate "earns its place" when AUC >= 0.60 and AUC >= AUC(M0 time) + 0.05.
CANDIDATES = {"Φ information rate (LZ estimate; the MRE specifies CTW)": "phi", "LZ complexity": "lzc", "EEG alternation (a proxy, not the MRE's δ)": "alt",
              "1/f exponent": "aperiodic", "alpha/theta": "alpha_theta", "IDA residue": "residue",
              "IDA displacement": "d"}
MIN_SESSIONS, MIN_PROBES, MIN_PER_CLASS = 3, 60, 15
MIN_AUC, MARGIN = 0.60, 0.05
MODELS = {"M0 time": ["minutes"], "M1 index": ["alpha_theta"], "M2 map": ["x", "y", "d"],
          "M3 flat": ["euc_x", "euc_y", "euc_d"]}


def probe_rows(s: Session, pre: float) -> tuple:
    rows, dropped = [], 0
    for a in s.of("answer"):
        if a.get("question") != "probe" or a.get("answer") not in ("aware", "drifting"):
            continue
        tp = float(a["t_prompt"])
        st = s.state
        if st.n == 0:
            dropped += 1
            continue
        w = st.window(tp - pre, tp)
        clean = w & (st["clean"] == 1)
        if w.sum() == 0 or clean.sum() < 0.5 * w.sum():
            dropped += 1
            continue
        ft = s.features
        fw = ft.window(tp - pre, tp, (ft["blink"] == 0) & (ft["motion"] == 0)) if ft.n else None
        ex, ey = st["euc_x"][clean].mean(), st["euc_y"][clean].mean()
        r = min(np.hypot(ex, ey), 1 - 1e-9)
        def st_mean(col):
            return float(st[col][clean].mean()) if st.has(col) and clean.any() else np.nan

        def ft_mean(col):
            return float(ft[col][fw].mean()) if fw is not None and ft.has(col) and fw.any() else np.nan

        rows.append({
            "phi": st_mean("phi"), "lzc": st_mean("lzc"), "alt": st_mean("alt"), "residue": st_mean("residue"),
            "aperiodic": ft_mean("aperiodic"),
            "session": s.name, "y": 1.0 if a["answer"] == "drifting" else 0.0,
            "minutes": (tp - s.t_start) / 60.0,
            "alpha_theta": float(ft["alpha_theta"][fw].mean()) if fw is not None and fw.any() else np.nan,
            "x": st["x"][clean].mean(), "y_": st["y"][clean].mean(), "d": st["d"][clean].mean(),
            "euc_x": ex, "euc_y": ey, "euc_d": 2 * np.arctanh(r),
        })
    return rows, dropped


def evaluate(rows: List[Dict], models: Dict[str, List[str]] = MODELS) -> Dict[str, float]:
    sessions = sorted({r["session"] for r in rows})
    y = np.array([r["y"] for r in rows])
    out = {}
    for name, cols in models.items():
        cols = ["y_" if c == "y" else c for c in cols]
        X = np.array([[r[c] for c in cols] for r in rows], dtype=float)
        ok = ~np.isnan(X).any(axis=1)
        pred = np.full(len(rows), np.nan)
        for s in sessions:
            test = np.array([r["session"] == s for r in rows]) & ok
            train = ~test & ok & np.array([r["session"] != s for r in rows])
            if test.sum() == 0 or len(set(y[train])) < 2:
                continue
            pred[test] = predict_logistic(fit_logistic(X[train], y[train]), X[test])
        m = ~np.isnan(pred)
        out[name] = auc(y[m], pred[m]) if m.sum() else float("nan")
    return out


def run(root: Path, pre: float) -> dict:
    sessions = [s for s in find_sessions(root) if s.of("answer")]
    rows, dropped = [], 0
    for s in sessions:
        r, d = probe_rows(s, pre)
        rows.extend(r)
        dropped += d
    n_sess = len({r["session"] for r in rows})
    n_drift = int(sum(r["y"] for r in rows))
    n_aware = len(rows) - n_drift
    report = {"gate_version": GATE_VERSION, "sessions": n_sess, "probes": len(rows),
              "aware": n_aware, "drifting": n_drift, "dropped_for_artifacts": dropped}
    enough = n_sess >= MIN_SESSIONS and len(rows) >= MIN_PROBES and min(n_aware, n_drift) >= MIN_PER_CLASS
    if not enough:
        report["verdict"] = "not enough data yet"
        report["needed"] = {"sessions": MIN_SESSIONS, "probes": MIN_PROBES, "each_answer": MIN_PER_CLASS}
        return report
    res = evaluate(rows)
    report["auc"] = {k: round(v, 3) for k, v in res.items()}
    m2 = res["M2 map"]
    passed = m2 >= MIN_AUC and m2 >= res["M0 time"] + MARGIN and m2 >= res["M1 index"] + MARGIN
    report["verdict"] = "PASS" if passed else "FAIL"
    report["curvature_question"] = {"M2 minus M3": round(m2 - res["M3 flat"], 3)}
    cand = evaluate(rows, {k: [v] for k, v in CANDIDATES.items()})
    base = res["M0 time"]
    report["awareness_candidates"] = {
        k: {"auc": round(v, 3), "earns_place": bool(v >= MIN_AUC and v >= base + MARGIN)} for k, v in cand.items()}
    return report


def main(argv=None) -> int:
    settings = load_settings()
    ap = argparse.ArgumentParser(prog="ida_live gate")
    ap.add_argument("--sessions", default=str(resolve(settings, "sessions")))
    args = ap.parse_args(argv)
    root = Path(args.sessions)
    report = run(root, float(settings["probes"]["pre_window_s"]))
    with open(root / "gate_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    print(json.dumps(report, indent=1))
    return 0
