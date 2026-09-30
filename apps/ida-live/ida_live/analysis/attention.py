"""Your attention profile, from the attention map.

The attention map labels every second with what your attention was doing (focused on a region
or free; narrow or broad) and checks it with behaviour (lights caught with Space). From that:

1. Which EEG features separate the states for you (AUC per feature, 0.5 = no separation), with
   95% intervals from resampling whole blocks.
2. A personal signature per contrast: a ridge logistic model over the brain features, tested
   by leaving each block out in turn (it is always scored on a block it did not learn from).
3. A muscle and motion check: the same model on muscle, motion and blinks only. If that does as
   well, the "attention" signal is your face, not your brain.
4. The behavioural test: does the signature, in the 2 s before each light, predict whether you
   caught it quickly or missed it? That is the proof that it tracks attention, not the video.

Gate (pre-declared, as in docs/GATE.md): held-out AUC >= 0.60, a block-level permutation p < 0.05
(whole blocks relabelled, since slow drift makes seconds within a block far from independent), and
at least 0.05 above the muscle-and-motion model. Only a signature that passes may drive a level.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from .common import Session, Table
from .levels import page, _esc, _f

BRAIN = ["alpha_af", "alpha_tp", "theta_af", "beta", "beta_af", "delta_af", "ix_alpha_rel3", "ix_engagement",
         "ix_theta_af_rel", "ix_faa", "lzc", "phi", "aperiodic"]
CONFOUND = ["emg_af", "emg_tp", "motion_dps", "blink"]
LOST = ("contact", "movement", "no signal")
CONTRASTS = {"focus": ("focus", "watch", "Focused vs free attention"), "scope": ("narrow", "broad", "Narrow vs broad attention")}
SETTLE_S = 4.0
RNG = np.random.default_rng(7)


def _auc(y: np.ndarray, s: np.ndarray) -> Optional[float]:
    pos, neg = s[y == 1], s[y == 0]
    if len(pos) < 5 or len(neg) < 5:
        return None
    r = np.argsort(np.argsort(np.concatenate([pos, neg]))) + 1
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def _ridge_logit(X: np.ndarray, y: np.ndarray, lam: float = 1.0, iters: int = 60) -> np.ndarray:
    """L2-penalised logistic regression by Newton steps (intercept unpenalised)."""
    Xb = np.column_stack([np.ones(len(X)), X])
    w = np.zeros(Xb.shape[1])
    P = np.eye(Xb.shape[1]) * lam
    P[0, 0] = 0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(Xb @ w, -30, 30)))
        g = Xb.T @ (p - y) + P @ w
        H = (Xb * (p * (1 - p))[:, None]).T @ Xb + P + 1e-6 * np.eye(len(w))
        step = np.linalg.solve(H, g)
        w -= step
        if np.abs(step).max() < 1e-6:
            break
    return w


def _score(w: np.ndarray, X: np.ndarray) -> np.ndarray:
    return np.column_stack([np.ones(len(X)), X]) @ w


def _cv(X: np.ndarray, y: np.ndarray, blocks: np.ndarray, boot: bool = True) -> Optional[dict]:
    """Leave-one-block-out held-out scores, and the pooled held-out AUC with a block bootstrap."""
    ub = np.unique(blocks)
    if len(ub) < 3 or len(np.unique(y)) < 2:
        return None
    # leave out one block of EACH state per fold: leaving out a single block shifts the class
    # balance of the training set against it, which pushes null data below AUC 0.5
    pos = [b for b in ub if y[blocks == b].mean() > 0.5]
    neg = [b for b in ub if y[blocks == b].mean() <= 0.5]
    if not pos or not neg:
        return None
    k = max(len(pos), len(neg))
    folds = [(pos[i % len(pos)], neg[i % len(neg)]) for i in range(k)]
    out = np.full(len(y), np.nan)
    for bp, bn in folds:
        te = (blocks == bp) | (blocks == bn)
        tr = ~te
        if len(np.unique(y[tr])) < 2:
            continue
        mu, sd = X[tr].mean(axis=0), X[tr].std(axis=0) + 1e-9
        w = _ridge_logit((X[tr] - mu) / sd, y[tr])
        out[te] = _score(w, (X[te] - mu) / sd)
    ok = np.isfinite(out)
    auc = _auc(y[ok], out[ok])
    if auc is None:
        return None
    if not boot:
        return {"auc": auc, "ci": [None, None], "scores": out}
    boots = []
    for _ in range(500):
        pick = RNG.choice(ub, len(ub))
        idx = np.concatenate([np.where((blocks == b) & ok)[0] for b in pick])
        a = _auc(y[idx], out[idx])
        if a is not None:
            boots.append(a)
    ci = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))] if boots else [None, None]
    return {"auc": auc, "ci": ci, "scores": out}


def _perm_p(X: np.ndarray, y: np.ndarray, blocks: np.ndarray, observed: float, max_perm: int = 200) -> Optional[float]:
    """Block-level permutation test: relabel whole blocks (keeping the count of each state) and
    redo the held-out test. Blocks drift slowly, so resampling seconds would be far too lenient."""
    from itertools import combinations
    ub = list(np.unique(blocks))
    lab = {b: int(y[blocks == b].mean() > 0.5) for b in ub}
    npos = sum(lab.values())
    combos = list(combinations(ub, npos))
    if len(combos) > max_perm:
        combos = [tuple(RNG.choice(ub, npos, replace=False)) for _ in range(max_perm)]
    ge, n = 0, 0
    for c in combos:
        yy = np.isin(blocks, c).astype(float)
        r = _cv(X, yy, blocks, boot=False)
        if r is None:
            continue
        n += 1
        ge += r["auc"] >= observed - 1e-12
    return (ge / n) if n else None


def build_profile(folder: Path, data_dir: Path) -> dict:
    s = Session(Path(folder))
    A = Table(s.folder / "attention.csv")
    F = s.features
    if A.n == 0 or F.n < 60:
        raise ValueError("Not enough attention-map data in this session.")
    t = F["t"]
    # usable seconds
    reasons = np.array([""] * F.n, dtype=object)
    if s.state.n and s.state.has("reasons"):
        st = s.state["t"]
        j = np.clip(np.searchsorted(st, t), 0, s.state.n - 1)
        reasons = np.array([str(s.state["reasons"][k]) if abs(st[k] - tt) < 0.6 else "" for k, tt in zip(j, t)], dtype=object)
    usable = np.array([not any(x in r for x in LOST) for r in reasons])

    # block intervals from the attention table
    ph, task, blk, cond = A["phase"], A["task"], A["block"], A["cond"]
    intervals = []
    for key in sorted({(str(a), int(b)) for a, b, p in zip(task, blk, ph) if p == "block"}):
        m = (task == key[0]) & (blk == key[1]) & (ph == "block")
        if m.sum() < 8:
            continue
        intervals.append({"task": key[0], "block": key[1], "cond": str(cond[m][0]), "t0": float(A["t"][m].min()), "t1": float(A["t"][m].max())})
    label = np.array([""] * F.n, dtype=object)
    bid = np.full(F.n, -1)
    for i, iv in enumerate(intervals):
        m = (t >= iv["t0"] + SETTLE_S) & (t <= iv["t1"])
        label[m] = iv["cond"]
        bid[m] = i

    brain = [c for c in BRAIN if F.has(c) and np.isfinite(F[c]).sum() > 30]
    conf = [c for c in CONFOUND if F.has(c) and np.isfinite(F[c]).sum() > 30]
    prof: Dict = {"made": time.strftime("%Y-%m-%d %H:%M"), "session": s.name, "features": brain, "confounds": conf,
                  "contrasts": {}, "gate": {}}

    for name, (a, b, title) in CONTRASTS.items():
        m = usable & np.isin(label, [a, b])
        if m.sum() < 40:
            continue
        y = (label[m] == a).astype(float)
        Xb_ = np.column_stack([F[c][m] for c in brain])
        Xc_ = np.column_stack([np.nan_to_num(F[c][m]) for c in conf]) if conf else np.zeros((m.sum(), 1))
        good = np.isfinite(Xb_).all(axis=1)
        y, Xb_, Xc_, blocks, tm = y[good], Xb_[good], Xc_[good], bid[m][good], t[m][good]
        per = []
        for k, c in enumerate(brain + conf):
            x = Xb_[:, k] if k < len(brain) else Xc_[:, k - len(brain)]
            auc = _auc(y, x)
            if auc is None:
                continue
            bs = []
            ub = np.unique(blocks)
            for _ in range(300):
                idx = np.concatenate([np.where(blocks == bb)[0] for bb in RNG.choice(ub, len(ub))])
                aa = _auc(y[idx], x[idx])
                if aa is not None:
                    bs.append(aa)
            per.append({"feature": c, "auc": _f(auc, 3), "ci": [_f(np.percentile(bs, 2.5), 3), _f(np.percentile(bs, 97.5), 3)] if bs else [None, None],
                        "kind": "brain" if k < len(brain) else "muscle/motion",
                        "higher_in": a if auc > 0.5 else b})
        per.sort(key=lambda r: -abs((r["auc"] or 0.5) - 0.5))
        cvb = _cv(Xb_, y, blocks)
        cvc = _cv(Xc_, y, blocks) if conf else None
        mu, sd = Xb_.mean(axis=0), Xb_.std(axis=0) + 1e-9
        w = _ridge_logit((Xb_ - mu) / sd, y)
        perm = _perm_p(Xb_, y, blocks, cvb["auc"]) if cvb else None
        passes = bool(cvb and cvb["auc"] >= 0.60 and perm is not None and perm < 0.05
                      and (cvc is None or cvb["auc"] >= cvc["auc"] + 0.05))
        entry = {"title": title, "positive": a, "negative": b, "rows": int(len(y)), "blocks": int(len(np.unique(blocks))),
                 "per_feature": per, "heldout_auc": _f(cvb["auc"], 3) if cvb else None,
                 "heldout_ci": [_f(x, 3) for x in cvb["ci"]] if cvb else [None, None],
                 "muscle_motion_auc": _f(cvc["auc"], 3) if cvc else None, "permutation_p": _f(perm, 3), "passes_gate": passes,
                 "model": {"features": brain, "mean": mu.tolist(), "sd": sd.tolist(), "w": w.tolist(),
                           "note": "score = w0 + sum(w_k * (x_k - mean_k) / sd_k); higher = more " + a}}
        # the behavioural test: the held-out signature in the 2 s before each light
        if cvb and a in ("focus", "narrow"):
            ev = A["event"]
            tt = A["t"]
            trials = []
            for i in range(A.n):
                if ev[i] == "target" and cond[i] == a:
                    t_on = tt[i]
                    later = [(ev[j], A["rt"][j]) for j in range(i + 1, min(A.n, i + 40)) if ev[j] in ("hit", "miss")
                             and abs(A["x"][j] - A["x"][i]) < 1e-6 and abs(A["y"][j] - A["y"][i]) < 1e-6]
                    if not later:
                        continue
                    outcome, rt = later[0]
                    pre = (tm >= t_on - 2.0) & (tm < t_on)
                    sc = cvb["scores"][pre]
                    sc = sc[np.isfinite(sc)]
                    if len(sc):
                        trials.append((outcome, rt, float(sc.mean())))
            if len(trials) >= 10:
                rts = [r for o, r, _ in trials if o == "hit" and np.isfinite(r)]
                cut = np.median(rts) if rts else np.inf
                good_ = np.array([1.0 if (o == "hit" and r <= cut) else 0.0 for o, r, _ in trials])
                scs = np.array([x for _, _, x in trials])
                entry["behaviour_test"] = {"trials": len(trials), "auc_fast_hit_vs_slow_or_miss": _f(_auc(good_, scs), 3),
                                           "note": "above 0.5 means a stronger signature before the light went with catching it fast"}
        prof["contrasts"][name] = entry
        prof["gate"][name] = passes

    # behaviour summary
    beh = {}
    for c in ("focus", "narrow", "broad"):
        m = A["cond"] == c
        ev = A["event"][m]
        tg = int((ev == "target").sum())
        hits = int((ev == "hit").sum())
        rts = A["rt"][m][ev == "hit"]
        beh[c] = {"targets": tg, "hits": hits, "hit_rate": _f(hits / tg, 3) if tg else None,
                  "median_rt": _f(float(np.nanmedian(rts)), 3) if len(rts) else None,
                  "decoy_presses": int((ev == "decoy_press").sum()), "false_presses": int((ev == "false_press").sum())}
    prof["behaviour"] = beh

    out = Path(data_dir) / "profiles"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"attention_{s.name}.json").write_text(json.dumps(prof, indent=1), encoding="utf-8")
    (out / "attention_latest.json").write_text(json.dumps(prof, indent=1), encoding="utf-8")
    (s.folder / "attention_profile.json").write_text(json.dumps(prof, indent=1), encoding="utf-8")
    (s.folder / "report.html").write_text(profile_html(prof), encoding="utf-8")
    return prof


def profile_html(p: dict) -> str:
    cards = []
    for name, c in p["contrasts"].items():
        ok = c["passes_gate"]
        rows = "".join(
            f"<tr><td>{_esc(r['feature'])}</td><td>{_esc(r['kind'])}</td><td>{r['auc']:.2f}</td><td class='fine'>{r['ci'][0] or '–'} to {r['ci'][1] or '–'}</td><td>{_esc(r['higher_in'])}</td></tr>"
            for r in c["per_feature"][:10])
        bt = c.get("behaviour_test")
        cards.append(f"""<section class="card"><h3>{_esc(c['title'])}</h3>
          <div class="grid2">
            <div class="stat"><span class="fine">Your signature, tested on unseen blocks</span><b class="{'up' if ok else ''}">{c['heldout_auc'] if c['heldout_auc'] is not None else '–'}</b>
              <span class="fine">AUC, 95% {c['heldout_ci'][0]} to {c['heldout_ci'][1]} · {c['blocks']} blocks</span></div>
            <div class="stat"><span class="fine">Muscle and motion alone</span><b>{c['muscle_motion_auc'] if c['muscle_motion_auc'] is not None else '–'}</b><span class="fine">must be at least 0.05 lower</span></div>
            <div class="stat"><span class="fine">Gate</span><b class="{'up' if ok else 'down'}">{'Passes' if ok else 'Not yet'}</b><span class="fine">AUC ≥ 0.60, permutation p = {c.get('permutation_p', '–')} (&lt; 0.05), beats muscle</span></div>
            {f'<div class="stat"><span class="fine">Predicts catching the light</span><b>{bt["auc_fast_hit_vs_slow_or_miss"]}</b><span class="fine">{bt["trials"]} lights · 0.5 = no</span></div>' if bt else ''}
          </div>
          <div class="scroll"><table><tr><th>Feature</th><th>Kind</th><th>AUC</th><th>95%</th><th>Higher when</th></tr>{rows}</table></div>
          <p class="fine">AUC is the chance that a random second of <b>{_esc(c['positive'])}</b> scores above a random second of <b>{_esc(c['negative'])}</b>. 0.5 is chance; 1 is perfect.</p></section>""")
    b = p.get("behaviour", {})
    brow = "".join(f"<tr><td>{k}</td><td>{v['hits']} of {v['targets']}</td><td>{'–' if v['median_rt'] is None else str(int(1000 * v['median_rt'])) + ' ms'}</td><td>{v['decoy_presses']}</td><td>{v['false_presses']}</td></tr>" for k, v in b.items() if v["targets"])
    body = f"""<h1>Your attention profile</h1><p class="sub">From the attention map of {_esc(p['session'])}, made {_esc(p['made'])}. A signature that passes the gate can drive the levels; one that doesn't is shown so you can see why.</p>
      {''.join(cards) or '<p>Not enough usable data.</p>'}
      <section class="card"><h3>What you did</h3><div class="scroll"><table><tr><th>Attention</th><th>Lights caught</th><th>Median reaction</th><th>Decoys pressed</th><th>Other presses</th></tr>{brow}</table></div></section>"""
    return page("IDA Live · Attention profile", body)
