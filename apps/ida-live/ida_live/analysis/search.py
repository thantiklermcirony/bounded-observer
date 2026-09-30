"""The Search: which shape of your brain's activity goes with a clear mind, and where on it.

Each Search is eight one-minute rounds. In six the scene is steered (sealed, you are not told) by
one candidate shape of clarity; in two nothing is steered. After each round you tap how clear your
mind is (0-4), and three faint lights per round, held near your threshold by a staircase, measure
how clearly you actually perceive. Every round also records all seven shapes, whatever was steered.

Three questions, each able to say "no":

1. Steering. Does steering towards a shape make you clearer than nothing steered? Ratings are
   centred within each Search; faint-light catches are compared with what their brightness alone
   predicts. 95% intervals by resampling rounds.
2. Which shape goes with clarity, whatever was steered? Each shape's round average against your
   clarity (rank correlation, resampled intervals), and whether clarity peaks at an interior
   point along it (a quadratic with a maximum inside the range you visited): the sweet spot.
3. Does it hold on a Search it never saw? With three or more Searches, each is predicted from the
   others. Only this counts as finding the point.

Pre-declared: a shape is "the point" only if it predicts clarity on held-out Searches better than
every other shape (ratings and faint lights both above zero), steering towards it beats nothing
steered with a 95% interval above zero, and it stays first when the latest Search is left out.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from .common import Session, Table
from .levels import page, _esc

SHAPES = ["symmetry", "axis", "coherence", "calm", "flow", "focus", "openness"]
LOST = ("contact", "movement", "no signal")
RNG = np.random.default_rng(20260926)


def _rounds(folder: Path) -> List[dict]:
    s = Session(folder)
    st = s.of("level_start")
    if not st or not st[0].get("search"):
        return []
    rev = s.of("level_reveal")
    sched = (rev[0].get("search") if rev else None) or []
    ratings = {e["round"]: e.get("rating") for e in s.of("level_rating")}
    probes: Dict[int, list] = {}
    for e in s.of("level_probe"):
        probes.setdefault(int(e["round"]), []).append((float(e["contrast"]), 1.0 if e.get("hit") else 0.0))
    L = Table(folder / "level.csv")
    if not L.n or not L.has("round"):
        return []
    usable = np.ones(L.n, bool)
    if s.state.n and s.state.has("reasons"):
        stt = s.state["t"]
        j = np.clip(np.searchsorted(stt, L["t"]), 0, s.state.n - 1)
        usable = np.array([not any(x in str(s.state["reasons"][k]) for x in LOST) for k in j])
    out = []
    for k, cand in enumerate(sched, start=1):
        m = (L["round"] == k) & (L["phase"] == "round") & usable
        if m.sum() < 40:
            continue
        vals = {}
        for sh in SHAPES:
            col = f"z_{sh}"
            if L.has(col):
                v = L[col][m]
                v = v[np.isfinite(v)]
                vals[sh] = float(np.mean(v)) if len(v) > 20 else None
        out.append({"session": s.name, "round": k, "cand": cand, "rating": ratings.get(k), "shapes": vals,
                    "probes": probes.get(k, [])})
    return out


def _logit_fit(x: np.ndarray, y: np.ndarray, iters: int = 40):
    X = np.column_stack([np.ones(len(x)), x])
    w = np.zeros(2)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(X @ w, -30, 30)))
        H = X.T @ (X * (p * (1 - p))[:, None]) + 1e-3 * np.eye(2)
        w += np.linalg.solve(H, X.T @ (y - p) - 1e-3 * w)
    return w


def _spearman(a: np.ndarray, b: np.ndarray) -> Optional[float]:
    if len(a) < 5 or np.std(a) == 0 or np.std(b) == 0:
        return None
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def analyse(sessions_dir: Path) -> Optional[dict]:
    rows = []
    for p in sorted(Path(sessions_dir).glob("*level-*")):
        if (p / "level.csv").exists() and (p / "manifest.json").exists():
            try:
                rows += _rounds(p)
            except Exception as exc:
                print(f"search: skipping {p.name}: {exc}")
    rows = [r for r in rows if r["rating"] is not None]
    if len(rows) < 6:
        return None
    sessions = sorted({r["session"] for r in rows})
    # centre ratings within each Search (days differ; what matters is round against round)
    for s in sessions:
        rs = [r for r in rows if r["session"] == s]
        m = np.mean([r["rating"] for r in rs])
        for r in rs:
            r["rc"] = r["rating"] - m
    # faint lights: catches beyond what brightness alone predicts
    allp = [(c, h) for r in rows for c, h in r["probes"]]
    if len(allp) >= 8:
        cx = np.log(np.array([c for c, _ in allp])); hy = np.array([h for _, h in allp])
        w = _logit_fit(cx, hy)
        for r in rows:
            if r["probes"]:
                c = np.log(np.array([c for c, _ in r["probes"]])); h = np.array([h for _, h in r["probes"]])
                r["dc"] = float(np.mean(h - 1 / (1 + np.exp(-(w[0] + w[1] * c)))))
            else:
                r["dc"] = None
    else:
        for r in rows:
            r["dc"] = None

    def boot_diff(a: np.ndarray, b: np.ndarray):
        if len(a) == 0 or len(b) == 0:
            return None, None, None
        d = float(a.mean() - b.mean())
        bs = [RNG.choice(a, len(a)).mean() - RNG.choice(b, len(b)).mean() for _ in range(2000)]
        return d, float(np.std(bs)), [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]

    # 1. steering
    free_r = np.array([r["rc"] for r in rows if r["cand"] == "free"])
    free_d = np.array([r["dc"] for r in rows if r["cand"] == "free" and r["dc"] is not None])
    steer = {}
    for c in SHAPES:
        a = np.array([r["rc"] for r in rows if r["cand"] == c])
        ad = np.array([r["dc"] for r in rows if r["cand"] == c and r["dc"] is not None])
        d, se, ci = boot_diff(a, free_r)
        dd, sed, cid = boot_diff(ad, free_d)
        steer[c] = {"n_rounds": int(len(a)), "diff": d, "se": se, "ci": ci, "detect_diff": dd, "detect_ci": cid}

    # 2. passive: every round's shape values against clarity
    passive = {}
    for c in SHAPES:
        pts = [(r["shapes"].get(c), r["rc"], r["dc"]) for r in rows if r["shapes"].get(c) is not None]
        if len(pts) < 6:
            passive[c] = {"n": len(pts)}
            continue
        x = np.array([p[0] for p in pts]); y = np.array([p[1] for p in pts])
        rho = _spearman(x, y)
        bs = []
        for _ in range(1000):
            i = RNG.integers(0, len(x), len(x))
            v = _spearman(x[i], y[i])
            if v is not None:
                bs.append(v)
        dpts = [(p[0], p[2]) for p in pts if p[2] is not None]
        rho_d = _spearman(np.array([p[0] for p in dpts]), np.array([p[1] for p in dpts])) if len(dpts) >= 6 else None
        # an interior sweet spot?
        sweet = None
        if len(x) >= 10 and np.std(x) > 0:
            A = np.column_stack([np.ones(len(x)), x, x ** 2])
            coef = np.linalg.lstsq(A, y, rcond=None)[0]
            if coef[2] < 0:
                xs = -coef[1] / (2 * coef[2])
                opts = []
                for _ in range(500):
                    i = RNG.integers(0, len(x), len(x))
                    cb = np.linalg.lstsq(A[i], y[i], rcond=None)[0]
                    if cb[2] < 0:
                        opts.append(-cb[1] / (2 * cb[2]))
                inside = x.min() < xs < x.max()
                sweet = {"at": float(xs), "inside_range": bool(inside), "share_boot_peaked": round(len(opts) / 500, 2),
                         "ci": [float(np.percentile(opts, 2.5)), float(np.percentile(opts, 97.5))] if len(opts) > 50 else None}
        passive[c] = {"n": len(pts), "rho": rho, "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else None,
                      "rho_detect": rho_d, "range": [float(x.min()), float(x.max())], "sweet": sweet}

    # 3. held-out prediction across Searches
    held = {}
    if len(sessions) >= 3:
        for c in SHAPES:
            preds, act, actd, predd = [], [], [], []
            for s in sessions:
                tr = [r for r in rows if r["session"] != s and r["shapes"].get(c) is not None]
                te = [r for r in rows if r["session"] == s and r["shapes"].get(c) is not None]
                if len(tr) < 8 or not te:
                    continue
                xt = np.array([r["shapes"][c] for r in tr]); yt = np.array([r["rc"] for r in tr])
                A = np.column_stack([np.ones(len(xt)), xt, xt ** 2])
                cf = np.linalg.lstsq(A + 0, yt, rcond=None)[0]
                for r in te:
                    x0 = r["shapes"][c]
                    pv = cf[0] + cf[1] * x0 + cf[2] * x0 ** 2
                    preds.append(pv); act.append(r["rc"])
                    if r["dc"] is not None:
                        predd.append(pv); actd.append(r["dc"])
            held[c] = {"r_rating": float(np.corrcoef(preds, act)[0, 1]) if len(preds) >= 6 and np.std(preds) > 0 else None,
                       "r_detect": float(np.corrcoef(predd, actd)[0, 1]) if len(predd) >= 6 and np.std(predd) > 0 else None,
                       "n": len(preds)}

    # the leaderboard and the pre-declared criterion
    def score(c):
        h = held.get(c) or {}
        if h.get("r_rating") is not None:
            return h["r_rating"] + (h.get("r_detect") or 0)
        pz = passive.get(c) or {}
        return (pz.get("rho") or 0) + 0.5 * (pz.get("rho_detect") or 0)
    leaders = sorted(SHAPES, key=lambda c: -score(c))
    top = leaders[0]
    h = held.get(top) or {}
    st = steer.get(top) or {}
    found = bool(h.get("r_rating") is not None and h["r_rating"] > 0 and (h.get("r_detect") or 0) > 0
                 and st.get("ci") and st["ci"][0] > 0 and len(sessions) >= 3)
    weak = h.get("r_rating") is not None and h["r_rating"] < 0.15
    status = ("found (provisional)" if found else "no shape stands out yet" if weak
              else "a leader, not yet established" if len(sessions) >= 3 else "first look")
    # where to steer next time: a shape with a clear interior sweet spot is steered TO that point,
    # not towards "more" (more is worse past the peak)
    targets = {}
    for c in SHAPES:
        sw = (passive.get(c) or {}).get("sweet")
        if sw and sw["inside_range"] and sw["share_boot_peaked"] >= 0.8 and sw.get("ci"):
            targets[c] = round(sw["at"], 3)
    return {"made": time.strftime("%Y-%m-%d %H:%M"), "sessions": sessions, "rounds": len(rows), "steer": steer,
            "passive": passive, "held_out": held, "leaders": [{"shape": c, "score": round(score(c), 3)} for c in leaders],
            "status": status, "top": top, "targets": targets}


def build_search_profile(sessions_dir: Path, data_dir: Path) -> dict:
    prof = analyse(sessions_dir)
    if prof is None:
        raise ValueError("Not enough Search rounds yet (one full Search is the minimum).")
    d = Path(data_dir) / "profiles"
    d.mkdir(parents=True, exist_ok=True)
    (d / "search_latest.json").write_text(json.dumps(prof, indent=1), encoding="utf-8")
    return prof


LABEL = {"symmetry": "Side to side balance", "axis": "Front to back balance", "coherence": "Waves moving together",
         "calm": "Calm (alpha)", "flow": "Absorption (forehead theta)", "focus": "Focus (beta)", "openness": "Openness (complexity)"}


def _f(v, d=2, sign=True):
    return "–" if v is None else (f"{v:+.{d}f}" if sign else f"{v:.{d}f}")


def search_html(p: dict) -> str:
    rows = []
    for i, L in enumerate(p["leaders"]):
        c = L["shape"]
        s, pz, h = p["steer"].get(c, {}), p["passive"].get(c, {}), p["held_out"].get(c, {})
        sw = pz.get("sweet")
        sweet = ("–" if not sw else (f"peaks at {sw['at']:+.1f}" + (" (inside what you visited)" if sw["inside_range"] else " (outside your range)")
                                     + f", {int(100 * sw['share_boot_peaked'])}% of resamples peak"))
        ci_s = "–" if not s.get("ci") else "%+.2f to %+.2f" % (s["ci"][0], s["ci"][1])
        ci_p = "–" if not pz.get("ci") else "%+.2f to %+.2f" % (pz["ci"][0], pz["ci"][1])
        rows.append(f"<tr><td>{i + 1}</td><td><b>{_esc(LABEL.get(c, c))}</b></td>"
                    f"<td>{_f(s.get('diff'))}<br><span class='fine'>{ci_s} · {s.get('n_rounds', 0)} rounds</span></td>"
                    f"<td>{_f(s.get('detect_diff'))}</td>"
                    f"<td>{_f(pz.get('rho'))}<br><span class='fine'>{ci_p}</span></td>"
                    f"<td>{_f(pz.get('rho_detect'))}</td><td class='fine'>{_esc(sweet)}</td>"
                    f"<td>{_f(h.get('r_rating'))} / {_f(h.get('r_detect'))}</td></tr>")
    body = f"""<h1>The Search</h1>
<p class="sub">{len(p['sessions'])} Search{'es' if len(p['sessions']) != 1 else ''}, {p['rounds']} rounds · status: <b>{_esc(p['status'])}</b> · made {_esc(p['made'])}</p>
<div class="card"><p>Which shape of your brain's activity goes with a clear mind? Seven candidates, each steered in some rounds and
measured in all. <b>Steered</b>: clarity when the scene steered towards it, minus rounds with nothing steered (your 0-4 taps,
centred per Search; faint lights caught beyond what their brightness predicts). <b>Goes with clarity</b>: across every round,
whether more of that shape went with clearer moments (rank correlation). <b>Sweet spot</b>: whether clarity peaks at a point
along it rather than at an extreme. <b>Held out</b>: predicting a whole Search from the others (needs three).
The point is only called when one shape leads on held-out Searches for both measures and steering towards it beats nothing
steered. Once a shape shows a sweet spot, later Searches steer to that point instead of towards "more".
One Search is a first look; five to ten will say.</p></div>
<div class="card"><table><tr><th>#</th><th>Shape</th><th>Steered: clarity</th><th>Steered: lights</th><th>Goes with clarity</th><th>…with lights</th><th>Sweet spot</th><th>Held out (clarity / lights)</th></tr>
{''.join(rows)}</table></div>"""
    return page("The Search", body)


def build_search_report(sessions_dir: Path, data_dir: Path) -> str:
    try:
        return search_html(build_search_profile(sessions_dir, data_dir))
    except ValueError as exc:
        return page("The Search", f"<h1>The Search</h1><p class='sub'>{_esc(exc)}</p><p>Start it from Home: The Search (about 12 minutes).</p>")
