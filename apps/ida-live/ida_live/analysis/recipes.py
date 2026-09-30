"""Recipe report: did firing change your state, compared with sham triggers in the same moments?

For every trigger of a revealed recipe run:
  pre   [decision - pre_s, decision)                  clean map ticks only
  post  [fire_end + exclude_s, fire_end + exclude_s + post_s)
  change = mean(post) - mean(pre) for each declared measure

Reported per recipe (pooled over its revealed runs):
  real minus sham change, with a permutation p-value (labels reshuffled 5,000 times);
  the sham change on its own, which shows how much the state moves back by itself
  after a trigger (regression to the mean) and is what an uncontrolled test would
  have mistaken for an effect.
Runs with randomize = 1.0 have no sham arm and are listed as uncontrolled.
Bench (sponge) and covered-LED runs are reported separately from runs on you.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from ..config import load_settings, resolve
from .common import Session, find_sessions

N_PERM = 5000


def trigger_rows(s: Session) -> list:
    rows = []
    starts = {e["run_id"]: e for e in s.of("recipe_start")}
    reveals = {e["run_id"]: e["arms"] for e in s.of("recipe_reveal")}
    done = {(e["run_id"], e["n"]): e for e in s.of("fire_done")}
    st = s.state
    for run_id, start in starts.items():
        if run_id not in reveals:
            continue
        r = start["recipe"]
        oc = r["outcome"]
        arms = reveals[run_id]
        for trig in (e for e in s.of("trigger") if e["run_id"] == run_id):
            n = trig["n"]
            fd = done.get((run_id, n))
            if fd is None or n > len(arms):
                continue
            t_dec, t_end = float(trig["t"]), float(fd["t_end"])
            pre = st.window(t_dec - oc["pre_s"], t_dec, st["clean"] == 1)
            a = t_end + oc["exclude_s"]
            post = st.window(a, a + oc["post_s"], st["clean"] == 1)
            row = {"session": s.name, "recipe": r["name"], "run_id": run_id, "n": n, "arm": arms[n - 1],
                   "controlled": float(r.get("randomize", 0.5)) < 1.0,
                   "condition": "bench" if start.get("bench") else "covered" if start.get("covered") else "on_you"}
            for m in oc["measures"]:
                col = m if st.has(m) else None
                if col is None or pre.sum() < 3 or post.sum() < 3:
                    row[m] = np.nan
                else:
                    row[m] = float(st[col][post].mean() - st[col][pre].mean())
            rows.append(row)
    return rows


def compare(rows: list, m: str, rng) -> dict:
    ok = [r for r in rows if not np.isnan(r.get(m, np.nan))]
    vals = np.array([r[m] for r in ok])
    act = np.array([r["arm"] == "active" for r in ok])
    out = {"n_real": int(act.sum()), "n_sham": int((~act).sum())}
    if act.sum():
        out["real_change"] = round(float(vals[act].mean()), 4)
    if (~act).sum():
        out["sham_change"] = round(float(vals[~act].mean()), 4)
    if act.sum() and (~act).sum():
        obs = vals[act].mean() - vals[~act].mean()
        cnt = sum(abs(vals[p].mean() - vals[~p].mean()) >= abs(obs) - 1e-12
                  for p in (rng.permutation(act) for _ in range(N_PERM)))
        out["real_minus_sham"] = round(float(obs), 4)
        out["p_perm"] = round((cnt + 1) / (N_PERM + 1), 4)
    return out


def run(root: Path) -> dict:
    rng = np.random.default_rng(11)
    rows = [r for s in find_sessions(root) for r in trigger_rows(s)]
    if not rows:
        return {"note": "No revealed recipe runs yet."}
    report = defaultdict(dict)
    groups = defaultdict(list)
    for r in rows:
        groups[(r["recipe"], r["condition"], r["controlled"])].append(r)
    for (name, cond, controlled), sub in groups.items():
        measures = [k for k in sub[0] if k not in ("session", "recipe", "run_id", "n", "arm", "controlled", "condition")]
        entry = {"triggers": len(sub), "sessions": len({r["session"] for r in sub}),
                 "controlled": controlled, **{m: compare(sub, m, rng) for m in measures}}
        if not controlled:
            entry["warning"] = ("No sham triggers: any change includes regression to the mean "
                                "and cannot be credited to the light.")
        report[name][cond] = entry
    return dict(report)


def main(argv=None) -> int:
    settings = load_settings()
    ap = argparse.ArgumentParser(prog="ida_live recipe-report")
    ap.add_argument("--sessions", default=str(resolve(settings, "sessions")))
    args = ap.parse_args(argv)
    root = Path(args.sessions)
    report = run(root)
    with open(root / "recipe_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    print(json.dumps(report, indent=1))
    return 0
