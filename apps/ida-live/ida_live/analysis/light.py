"""Light-trial report. Only sessions whose allocation was revealed are analysed.

Per trial (windows declared in docs/IR_PROTOCOL.md):
  pre    [switch_on - pre_s + 1, switch_on - 0.5)
  post   [switch_on + excl, switch_off) and [switch_off + excl, switch_off + 20)
  outcomes: change (post - pre) in map displacement d, and in alpha_tp
  switch check: forehead low-frequency amplitude in the 3 s after each switch
                command, minus pre. This is where an electrical step shows up.

Statistics:
  active minus sham mean change, with a permutation p-value that reshuffles
  arms only within the original blocks (5,000 permutations), pooled per phase.
  Blinding: share of decided guesses that were right, exact binomial test vs 50%.
  "nothing" sessions have no active arm; they are reported as the null spread.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from ..config import load_settings, resolve
from .common import Session, binom_two_sided, find_sessions

N_PERM = 5000


def trial_table(s: Session) -> list:
    cfg = s.settings.get("ir_protocol", {})
    pre_s, excl = float(cfg.get("pre_s", 20)), float(cfg.get("exclude_after_switch_s", 3))
    reveal = s.of("reveal")
    if not reveal:
        return []
    arms = reveal[-1]["arms"]
    phase = reveal[-1]["phase"]
    block = int(cfg.get("block_size", 4))
    switches = defaultdict(dict)
    for e in s.of("switch"):
        if e.get("trial"):
            switches[e["trial"]][e["which"]] = float(e["t_cmd"])
    guesses = {e["trial"]: e.get("guess") for e in s.of("trial_end")}
    st, ft = s.state, s.features
    rows = []
    for i, arm in enumerate(arms, start=1):
        sw = switches.get(i, {})
        if "on" not in sw or "off" not in sw:
            continue
        on, off = sw["on"], sw["off"]
        pre = st.window(on - pre_s + 1, on - 0.5, st["clean"] == 1)
        post = (st.window(on + excl, off, st["clean"] == 1) | st.window(off + excl, off + 20, st["clean"] == 1))
        fclean = (ft["blink"] == 0) & (ft["motion"] == 0)
        fpre, fpost = ft.window(on - pre_s + 1, on - 0.5, fclean), (
            ft.window(on + excl, off, fclean) | ft.window(off + excl, off + 20, fclean))
        sw_amp = [np.nanmean(ft["blink_ptp"][ft.window(t, t + 3)]) for t in (on, off)]
        base_amp = np.nanmean(ft["blink_ptp"][ft.window(on - pre_s + 1, on - 0.5)])
        rows.append({
            "session": s.name, "phase": phase, "trial": i, "block": (i - 1) // block, "arm": arm,
            "d_change": float(st["d"][post].mean() - st["d"][pre].mean()) if pre.sum() > 4 and post.sum() > 4 else np.nan,
            "alpha_change": float(ft["alpha_tp"][fpost].mean() - ft["alpha_tp"][fpre].mean()) if fpre.sum() > 4 and fpost.sum() > 4 else np.nan,
            "switch_step_uv": float(np.nanmean(sw_amp) - base_amp),
            "guess": guesses.get(i),
            "bench": bool(any(e.get("bench") for e in s.of("light_sealed"))),
        })
    return rows


def perm_test(rows: list, key: str, rng: np.random.Generator) -> dict:
    ok = [r for r in rows if not np.isnan(r[key])]
    act = np.array([r["arm"] == "active" for r in ok])
    if act.sum() == 0 or (~act).sum() == 0:
        vals = np.array([r[key] for r in ok])
        return {"n": len(ok), "sham_mean": round(float(vals.mean()), 4) if len(vals) else None,
                "sham_sd": round(float(vals.std(ddof=1)), 4) if len(vals) > 1 else None}
    vals = np.array([r[key] for r in ok])
    groups = defaultdict(list)
    for j, r in enumerate(ok):
        groups[(r["session"], r["block"])].append(j)
    obs = vals[act].mean() - vals[~act].mean()
    count = 0
    for _ in range(N_PERM):
        a = act.copy()
        for idx in groups.values():
            a[idx] = rng.permutation(a[idx])
        if a.sum() and (~a).sum():
            count += abs(vals[a].mean() - vals[~a].mean()) >= abs(obs) - 1e-12
    return {"n_active": int(act.sum()), "n_sham": int((~act).sum()),
            "active_minus_sham": round(float(obs), 4), "p_perm": round((count + 1) / (N_PERM + 1), 4)}


def blinding(rows: list) -> dict:
    decided = [r for r in rows if r["guess"] in ("yes", "no")]
    right = sum((r["guess"] == "yes") == (r["arm"] == "active") for r in decided)
    return {"decided": len(decided), "correct": right,
            "p_vs_chance": round(binom_two_sided(right, len(decided)), 4) if decided else None,
            "cant_tell": sum(1 for r in rows if r["guess"] == "unsure")}


def run(root: Path) -> dict:
    rng = np.random.default_rng(7)
    rows = []
    for s in find_sessions(root):
        rows.extend(trial_table(s))
    report = {}
    for phase in ("nothing", "small", "larger"):
        pr = [r for r in rows if r["phase"] == phase]
        if not pr:
            continue
        human = [r for r in pr if not r["bench"]]
        bench = [r for r in pr if r["bench"]]
        entry = {}
        for label, sub in (("on_you", human), ("bench_sponge", bench)):
            if not sub:
                continue
            entry[label] = {
                "sessions": len({r["session"] for r in sub}),
                "displacement": perm_test(sub, "d_change", rng),
                "alpha": perm_test(sub, "alpha_change", rng),
                "switch_step": perm_test(sub, "switch_step_uv", rng),
            }
            if label == "on_you":
                entry[label]["blinding"] = blinding(sub)
        report[phase] = entry
    if not report:
        report["note"] = "No revealed light-trial sessions yet."
    return report


def main(argv=None) -> int:
    settings = load_settings()
    ap = argparse.ArgumentParser(prog="ida_live light-report")
    ap.add_argument("--sessions", default=str(resolve(settings, "sessions")))
    args = ap.parse_args(argv)
    root = Path(args.sessions)
    report = run(root)
    with open(root / "light_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    print(json.dumps(report, indent=1))
    return 0
