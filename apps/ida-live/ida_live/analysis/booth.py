"""Your experience map, from the listening booth.

In the booth you listen to music and move three levers to say how you feel: FLOW, PRESENCE (depth
of focus) and HORIZON (how freely you can see ahead). The centre of each lever is "as usual", the
top is none, the bottom is full. Nothing on screen follows your brain: it is simply read.

For each lever this asks the question behind the whole IDA programme, in the plainest form:

    Does the EEG predict what you report feeling, on data it never learned from, and does it add
    anything beyond your body (muscle, head motion, blinks, breathing, heart rate, the music's
    loudness)?

    * window    the EEG predicts the lever and adds beyond the body: your brain reading carries
                something of the felt state
    * body      the body predicts it as well as the EEG: the "signal" is muscle, breath or music
    * nothing   neither predicts it (yet): more listening, or the lever doesn't show on this headband

Method (declared before any data):
  * each 0.25 s tick of features is paired with the lever's mean over [t - 1 s, t + 3 s] (a feeling is
    reported a little after it arises); ticks within 1 s of moving a lever, and ticks without usable
    signal, are left out (moving your hand is not a brain state)
  * each session's straight-line drift is removed from the levers and every feature first, so the
    test is whether the EEG follows your ups and downs, not whether both just rise over the session
  * ridge regression (lambda = 10) on standardised features, scored on held-out data: leave one
    booth session out when there are two or more, otherwise five contiguous blocks with 10 s
    guard bands
  * significance by circular shifts of the lever series (lag > 60 s, 200 shifts): this keeps
    both series' own slowness, which is what makes naive correlations look impressive
  * gate: held-out r >= 0.30, shift p < 0.05, and brain + body beats body alone by >= 0.05.
    Only a lever that passes can become a level's target (Control > Knobs > levels.target).
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

LEVERS = {"flow": ("Flow", "how much it flows"), "presence": ("Presence", "how present, how deep your focus"),
          "horizon": ("Horizon", "how freely you can see ahead")}
BRAIN = ["alpha_af", "alpha_tp", "theta_af", "beta", "beta_af", "delta_af", "gamma_tp", "ix_alpha_rel3", "ix_engagement",
         "ix_theta_af_rel", "ix_faa", "lzc", "phi_ctw", "aperiodic"]
BODY = ["emg_af", "emg_tp", "hum_tp", "hum_af", "motion_dps", "blink_ptp", "breath_bpm", "heart_bpm", "music_level", "elapsed"]
LOST = ("contact", "movement", "no signal")
WIN = (-1.0, 3.0)
LAM = 10.0
GATE_R, GATE_P, GATE_GAIN = 0.30, 0.05, 0.05
SHIFT_S = 60.0
RNG_SEED = 20260926


# ------------------------------------------------------------------ assembling one session
def _session_rows(folder: Path) -> Optional[dict]:
    s = Session(folder)
    B = Table(folder / "booth.csv")
    F = s.features
    if B.n < 50 or F.n < 120:
        return None
    t = F["t"]
    tb = B["t"]
    order = np.argsort(tb)
    tb = tb[order]
    reasons = np.array([""] * F.n, dtype=object)
    if s.state.n and s.state.has("reasons"):
        st = s.state["t"]
        j = np.clip(np.searchsorted(st, t), 0, s.state.n - 1)
        reasons = np.array([str(s.state["reasons"][k]) if abs(st[k] - tt) < 0.6 else "no signal" for k, tt in zip(j, t)], dtype=object)
    usable = np.array([not any(x in r for x in LOST) for r in reasons])
    moving = B["moving"][order] if B.has("moving") else np.zeros(len(tb))
    mv_t = tb[np.nan_to_num(moving) > 0]
    near_move = np.zeros(F.n, bool)
    if len(mv_t):
        k = np.searchsorted(mv_t, t)
        for kk in (k - 1, k):
            ok = (kk >= 0) & (kk < len(mv_t))
            near_move[ok] |= np.abs(mv_t[kk[ok]] - t[ok]) <= 1.0
    # the lever's mean over the window after each tick (cumulative sums over the sorted booth rows)
    y = {}
    lo = np.searchsorted(tb, t + WIN[0])
    hi = np.searchsorted(tb, t + WIN[1])
    cnt = hi - lo
    for lv in LEVERS:
        v = B[lv][order] if B.has(lv) else np.full(len(tb), np.nan)
        v = np.where(np.isfinite(v), v, 0.5)
        cs = np.concatenate([[0.0], np.cumsum(v)])
        y[lv] = np.where(cnt > 0, (cs[hi] - cs[lo]) / np.maximum(cnt, 1), np.nan)
    ml = B["music_level"][order] if B.has("music_level") else np.zeros(len(tb))
    hum = _hum_from_eeg(folder, t) if not F.has("hum_tp") else None   # older recordings: work it out from the raw EEG
    music_level = np.interp(t, tb, np.nan_to_num(ml))
    cols = {}
    for c in BRAIN + BODY:
        if c == "music_level":
            cols[c] = music_level
        elif c == "elapsed":
            cols[c] = (t - t[0]) / 60.0      # minutes into the session: anything that just drifts with time
        elif c in ("hum_tp", "hum_af") and hum is not None:
            cols[c] = hum[c]
        elif F.has(c):
            cols[c] = F[c].astype(float)
    keep = usable & ~near_move & (cnt > 0)
    peaks = int(np.nansum(B["peak"])) if B.has("peak") else 0
    return {"name": s.name, "t": t, "y": y, "cols": cols, "keep": keep, "n_ticks": int(F.n), "peaks": peaks,
            "peak_t": tb[np.nan_to_num(B["peak"][order]) > 0] if B.has("peak") else np.zeros(0),
            "minutes": float((tb[-1] - tb[0]) / 60.0), "music": sorted({str(m) for m in B["music"] if str(m) not in ("", "nan")}) if B.has("music") else []}


def _detrend(v: np.ndarray, t: np.ndarray) -> np.ndarray:
    if len(v) < 3:
        return v - np.mean(v) if len(v) else v
    A = np.column_stack([np.ones(len(t)), t - t.mean()])
    return v - A @ np.linalg.lstsq(A, v, rcond=None)[0]


def _hum_from_eeg(folder: Path, t: np.ndarray) -> Optional[dict]:
    """Mains hum (log power at 50 Hz) at the ear and forehead sensors over the 2 s before each
    tick, from eeg.csv: how firmly each sensor sat, for recordings made before it was logged."""
    p = Path(folder) / "eeg.csv"
    if not p.exists():
        return None
    try:
        e = np.loadtxt(p, delimiter=",", skiprows=1)
    except (ValueError, OSError):
        return None
    te, x = e[:, 0], np.nan_to_num(e[:, 1:5])
    n = 512
    f = np.fft.rfftfreq(n, 1 / 256.0)
    on = (f >= 49.4) & (f <= 50.6)
    win = np.hanning(n)[:, None]
    out = {"hum_tp": np.full(len(t), np.nan), "hum_af": np.full(len(t), np.nan)}
    idx = np.searchsorted(te, t)
    for k, j in enumerate(idx):
        if j < n:
            continue
        seg = x[j - n:j] - x[j - n:j].mean(axis=0)
        P = np.abs(np.fft.rfft(seg * win, axis=0)) ** 2
        h = np.log10(P[on].mean(axis=0) + 1e-12)
        out["hum_tp"][k], out["hum_af"][k] = float(h[[0, 3]].mean()), float(h[[1, 2]].mean())
    return out


def _matrix(sessions: List[dict], names: List[str], detrend: bool = True):
    """Rows usable for the analysis. With detrend (the default, declared): each session's own
    straight-line drift is removed from every feature and every lever, so what is tested is
    whether the EEG follows the lever's ups and downs, not whether both simply rise with time."""
    Xs, ys, sid, ts = [], {lv: [] for lv in LEVERS}, [], []
    for i, s in enumerate(sessions):
        X = np.column_stack([s["cols"].get(c, np.full(len(s["t"]), np.nan)) for c in names]) if names else np.zeros((len(s["t"]), 0))
        m = s["keep"] & np.isfinite(X).all(axis=1)
        X = X[m]
        tm = s["t"][m]
        if detrend and len(tm) > 3:
            X = np.column_stack([_detrend(X[:, k], tm) for k in range(X.shape[1])]) if X.shape[1] else X
        Xs.append(X)
        for lv in LEVERS:
            yv = s["y"][lv][m]
            ys[lv].append(_detrend(yv, tm) + np.mean(yv) if detrend and len(tm) > 3 else yv)
        sid.append(np.full(m.sum(), i))
        ts.append(s["t"][m])
    return np.concatenate(Xs), {lv: np.concatenate(v) for lv, v in ys.items()}, np.concatenate(sid), np.concatenate(ts)


# ------------------------------------------------------------------ models
def _ridge(X: np.ndarray, y: np.ndarray, lam: float = LAM):
    mu, sd = X.mean(axis=0), X.std(axis=0) + 1e-9
    Z = (X - mu) / sd
    w = np.linalg.solve(Z.T @ Z + lam * np.eye(Z.shape[1]), Z.T @ (y - y.mean()))
    return np.concatenate([[y.mean()], w]), mu, sd


def _predict(model, X):
    w, mu, sd = model
    return w[0] + ((X - mu) / sd) @ w[1:]


def _folds(sid: np.ndarray, t: np.ndarray) -> List[tuple]:
    """(train mask, test mask) pairs: leave one session out, or 5 blocks with 10 s guards."""
    us = np.unique(sid)
    if len(us) >= 2:
        return [(sid != u, sid == u) for u in us]
    edges = np.quantile(t, np.linspace(0, 1, 6))
    out = []
    for k in range(5):
        test = (t >= edges[k]) & (t <= edges[k + 1])
        guard = (t >= edges[k] - 10) & (t <= edges[k + 1] + 10)
        out.append((~guard, test))
    return out


def _cv_r(X: np.ndarray, y: np.ndarray, folds) -> tuple:
    if X.shape[1] == 0:
        return None, None
    # scored within each held-out stretch and averaged (weighted by length): pooling across folds
    # would reward or punish differences between the folds' means, which the training mean always
    # gets backwards (the classic negative bias of held-out correlation)
    pred = np.full(len(y), np.nan)
    rs, ns = [], []
    for tr, te in folds:
        if tr.sum() < 40 or te.sum() < 10:
            continue
        pred[te] = _predict(_ridge(X[tr], y[tr]), X[te])
        if np.std(pred[te]) > 1e-9 and np.std(y[te]) > 1e-9:
            rs.append(float(np.corrcoef(pred[te], y[te])[0, 1]))
            ns.append(int(te.sum()))
    if not rs:
        return None, pred
    return float(np.average(rs, weights=ns)), pred


def _shift(y: np.ndarray, sid: np.ndarray, t: np.ndarray, rng) -> np.ndarray:
    out = y.copy()
    for u in np.unique(sid):
        m = np.where(sid == u)[0]
        n = len(m)
        dur = t[m[-1]] - t[m[0]] if n > 1 else 0
        if n < 10 or dur < 2 * SHIFT_S + 10:
            continue
        per = n / max(dur, 1e-6)
        k = int(rng.integers(int(SHIFT_S * per), n - int(SHIFT_S * per)))
        out[m] = np.roll(y[m], k)
    return out


def analyse(sessions_dir: Path) -> Optional[dict]:
    rows = []
    for p in sorted(Path(sessions_dir).glob("*booth*")):
        if (p / "booth.csv").exists() and (p / "manifest.json").exists():
            try:
                r = _session_rows(p)
            except Exception as exc:
                print(f"booth: skipping {p.name}: {exc}")
                continue
            if r is not None and r["keep"].sum() >= 120:
                rows.append(r)
    if not rows:
        return None
    rng = np.random.default_rng(RNG_SEED)
    brain = [c for c in BRAIN if all(c in s["cols"] and np.isfinite(s["cols"][c]).sum() > 30 for s in rows)]
    body = [c for c in BODY if all(c in s["cols"] and np.isfinite(s["cols"][c]).sum() > 0.8 * len(s["t"]) for s in rows)]
    # the ticks that have both brain and body values
    body = [c for c in body if c != "elapsed"]          # detrending removes the clock itself
    Xa, Ya, sida, ta = _matrix(rows, brain + body)
    # how much the levers simply drifted with time (reported, not used in the test)
    _, Yraw, _, traw = _matrix(rows, [], detrend=False)
    drift = {lv: round(float(np.corrcoef(Yraw[lv], traw)[0, 1]), 2) if np.std(Yraw[lv]) > 0.02 else None for lv in LEVERS}
    folds = _folds(sida, ta)
    out: Dict = {"made": time.strftime("%Y-%m-%d %H:%M"), "sessions": [s["name"] for s in rows],
                 "latest_session": rows[-1]["name"], "minutes": round(sum(s["minutes"] for s in rows), 1),
                 "brain_features": brain, "body_features": body, "ticks": int(len(ta)), "levers": {}, "gate": {},
                 "peaks": int(sum(s["peaks"] for s in rows)),
                 "cv": "leave one session out" if len(rows) >= 2 else "five blocks within the session"}
    nb = len(brain)
    # do the levers move together? then, so far, they are one feeling reported three times
    together = {}
    names = list(LEVERS)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a_, b_ = Ya[names[i]], Ya[names[j]]
            if np.std(a_) > 0.02 and np.std(b_) > 0.02:
                r = float(np.corrcoef(a_, b_)[0, 1])
                if r > 0.7:
                    together[f"{names[i]}+{names[j]}"] = round(r, 2)
    out["together"] = together
    out["drift_with_time"] = drift
    for lv, (title, sub) in LEVERS.items():
        y = Ya[lv]
        sd = float(np.std(y))
        entry = {"title": title, "sub": sub, "sd": round(sd, 3), "mean": round(float(np.mean(y)), 3),
                 "share_above": round(float(np.mean(y > 0.55)), 3), "share_below": round(float(np.mean(y < 0.45)), 3)}
        if sd < 0.04:
            entry.update(verdict="unmoved", passes_gate=False,
                         say=f"You kept {title} close to the same place, so there is nothing to learn from yet. Move it whenever the feeling changes.")
            out["levers"][lv], out["gate"][lv] = entry, False
            continue
        r_brain, pred_brain = _cv_r(Xa[:, :nb], y, folds)
        r_body, _ = _cv_r(Xa[:, nb:], y, folds) if body else (None, None)
        r_both, _ = _cv_r(Xa, y, folds)
        # circular-shift null for the brain model
        null = []
        for _ in range(200):
            rs, _ = _cv_r(Xa[:, :nb], _shift(y, sida, ta, rng), folds)
            if rs is not None:
                null.append(rs)
        p = (sum(1 for v in null if v >= (r_brain or 0) - 1e-12) + 1) / (len(null) + 1) if r_brain is not None and null else None
        gain = (r_both or 0) - (r_body or 0) if r_body is not None else (r_both or 0)
        passes = bool(r_brain is not None and r_brain >= GATE_R and p is not None and p < GATE_P and gain >= GATE_GAIN)
        if passes:
            verdict, say = "window", (f"Your EEG predicts {title} on data it never saw (r = {r_brain:.2f}), beyond your body. "
                                      "This signature can now drive the levels.")
        elif (r_body or 0) >= GATE_R and (r_body or 0) >= (r_brain or 0) - 0.02:
            verdict, say = "body", (f"Your body or the clock (muscle, motion, breath, the music, minutes into the session) predicts {title} "
                                    "about as well as the EEG. For this lever the brain reading isn't adding anything yet.")
        elif r_brain is not None and r_brain >= 0.15 and p is not None and p < 0.2:
            verdict, say = "emerging", f"A signature for {title} is forming (r = {r_brain:.2f}) but hasn't passed its test. More listening will tell."
        else:
            verdict, say = "nothing", f"Nothing predicts {title} yet."
        # per-feature tracking: correlation with a circular-shift null
        per = []
        for k, c in enumerate(brain + body):
            x = Xa[:, k]
            if np.std(x) < 1e-9:
                continue
            r = float(np.corrcoef(x, y)[0, 1])
            nl = [abs(np.corrcoef(x, _shift(y, sida, ta, rng))[0, 1]) for _ in range(100)]
            pp = (sum(1 for v in nl if v >= abs(r)) + 1) / (len(nl) + 1)
            label = {"elapsed": "minutes into the session", "hum_tp": "ear sensor contact (mains hum)", "hum_af": "forehead sensor contact (mains hum)",
                     "emg_tp": "ear high frequencies (jaw muscle or loose contact)", "emg_af": "forehead high frequencies (brow, eyes)"}.get(c, c)
            per.append({"feature": label, "kind": "brain" if k < nb else ("time" if c == "elapsed" else "contact" if c.startswith("hum") else "body"),
                        "r": round(r, 3), "p": round(pp, 3)})
        per.sort(key=lambda z: -abs(z["r"]))
        model = _ridge(Xa[:, :nb], y)
        entry.update({"heldout_r": None if r_brain is None else round(r_brain, 3), "body_r": None if r_body is None else round(r_body, 3),
                      "both_r": None if r_both is None else round(r_both, 3), "perm_p": None if p is None else round(p, 3),
                      "passes_gate": passes, "verdict": verdict, "say": say, "per_feature": per[:12],
                      "model": {"features": brain, "mean": model[1].tolist(), "sd": model[2].tolist(), "w": model[0].tolist(),
                                "note": "predicted lever = w0 + sum(w_k * (x_k - mean_k) / sd_k); 0 none, 0.5 usual, 1 full"}})
        # the latest session's lever and held-out prediction, for the picture
        last = sida == sida.max()
        tt = ta[last]
        entry["series"] = {"t": [round(float(v - tt[0]), 1) for v in tt[::8]], "y": [round(float(v), 3) for v in y[last][::8]],
                           "pred": [None if not np.isfinite(v) else round(float(v), 3) for v in (pred_brain[last][::8] if pred_brain is not None else [])]}
        out["levers"][lv], out["gate"][lv] = entry, passes
    return out


def build_booth_profile(sessions_dir: Path, data_dir: Path) -> dict:
    prof = analyse(sessions_dir)
    if prof is None:
        raise ValueError("Not enough booth listening yet (a few minutes with a clean signal is the minimum).")
    d = Path(data_dir) / "profiles"
    d.mkdir(parents=True, exist_ok=True)
    (d / "booth_latest.json").write_text(json.dumps(prof, indent=1), encoding="utf-8")
    (d / "booth_report.html").write_text(booth_html(prof), encoding="utf-8")
    return prof


# ------------------------------------------------------------------ report
def _chart(series: dict) -> str:
    x, y, pr = series["t"], series["y"], series.get("pred") or []
    if len(x) < 3:
        return ""
    W, H, L, R, T, B = 1000, 200, 46, 12, 12, 26
    x0, x1 = x[0], x[-1]
    sx = lambda v: L + (v - x0) / max(1e-6, x1 - x0) * (W - L - R)
    sy = lambda v: T + (1 - max(0.0, min(1.0, v))) * (H - T - B)   # 0 (none) at the top, like the lever
    o = [f'<svg viewBox="0 0 {W} {H}" class="bchart" role="img" aria-label="Lever and prediction over time">']
    for g, lab in ((0.0, "none"), (0.5, "usual"), (1.0, "full")):
        o.append(f'<line x1="{L}" x2="{W - R}" y1="{sy(g):.1f}" y2="{sy(g):.1f}" stroke="var(--line)" stroke-width="{1.4 if g == 0.5 else 0.8}"/>')
        o.append(f'<text x="{L - 6}" y="{sy(g) + 4:.1f}" font-size="11" text-anchor="end" fill="var(--ink3)">{lab}</text>')
    o.append(f'<text x="{W - R}" y="{H - 6}" font-size="11" text-anchor="end" fill="var(--ink3)">{(x1 - x0) / 60:.0f} min</text>')

    def path(vals, color, width, dash=""):
        pts, pen = [], False
        for xv, v in zip(x, vals):
            if v is None:
                pen = False
                continue
            pts.append(("L" if pen else "M") + f"{sx(xv):.1f},{sy(v):.1f}")
            pen = True
        return f'<path d="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="{width}" {dash} stroke-linejoin="round"/>'
    o.append(path(y, "var(--ink)", 2.2))
    if pr:
        o.append(path(pr, "#2a9d8f", 1.8, 'stroke-dasharray="5 4"'))
    o.append("</svg>")
    return "".join(o)


def booth_html(p: dict) -> str:
    badge = {"window": ("up", "a window"), "body": ("down", "body, not brain"), "emerging": ("", "forming"),
             "nothing": ("", "nothing yet"), "unmoved": ("", "lever not moved")}
    cards = []
    for lv, e in p["levers"].items():
        cls, word = badge.get(e.get("verdict"), ("", ""))
        bars = ""
        if "heldout_r" in e:
            def bar(lab, v):
                w = 0 if v is None else max(0.0, min(1.0, v))
                return (f"<div class='rb'><span>{lab}</span><div class='bar'><i style='width:{100 * w:.0f}%'></i></div>"
                        f"<b>{'–' if v is None else f'{v:+.2f}'}</b></div>")
            bars = bar("EEG", e["heldout_r"]) + bar("Body", e["body_r"]) + bar("Both", e["both_r"])
        feats = "".join(f"<tr><td>{_esc(r['feature'])}</td><td>{r['kind']}</td><td>{r['r']:+.2f}</td><td>{r['p']:.3f}</td></tr>"
                        for r in e.get("per_feature", [])[:8])
        cards.append(f"""<section class="card"><h3>{_esc(e['title'])} <span class="fine">· {_esc(e['sub'])}</span></h3>
  <p><b class="{cls}">{_esc(word)}</b> · {_esc(e['say'])}</p>
  <p class="fine">You spent {100 * e['share_below']:.0f}% of the time below usual and {100 * e['share_above']:.0f}% above.
  {'' if e.get('perm_p') is None else f"Held-out r, shift test p = {e['perm_p']:.3f}."}</p>
  {bars}
  {(_chart(e['series']) + '<p class="fine">Solid: your lever in the latest session. Dashed: what your EEG predicted, from a model that never saw that stretch.</p>') if e.get('series') else ''}
  {"<details><summary>What tracks it</summary><table><tr><th>Measure</th><th>Kind</th><th>r</th><th>shift p</th></tr>" + feats + "</table></details>" if feats else ""}
</section>""")
    body = f"""<style>.bar{{height:8px;flex:1;background:rgba(127,127,127,.22);border-radius:4px;overflow:hidden}}
.bar i{{display:block;height:100%;background:#2a9d8f}} .rb{{display:flex;gap:10px;align-items:center;margin:4px 0;max-width:520px}}
.rb span{{width:44px;color:var(--ink2)}} .rb b{{width:48px;text-align:right}} .bchart{{width:100%;height:auto;margin-top:10px}}
details{{margin-top:8px}} summary{{cursor:pointer}}</style>
<h1>Your experience map</h1>
<p class="sub">{len(p['sessions'])} booth session{'s' if len(p['sessions']) != 1 else ''}, {p['minutes']:.0f} minutes, {p['ticks']:,} usable moments,
{p['peaks']} "this!" moments · tested by {_esc(p['cv'])} · made {_esc(p['made'])}</p>
{('<div class="card"><p><b>Your levers mostly rose with time</b> (' + ', '.join(f"{k} r = {v:+.2f}" for k, v in (p.get('drift_with_time') or {}).items() if v is not None) + ' with minutes into the session). That drift is taken out before testing, because anything that changes slowly would match it.</p></div>') if any(v is not None and abs(v) > 0.5 for v in (p.get('drift_with_time') or {}).values()) else ''}
{('<div class="card"><p><b>Your levers moved together</b> (' + ', '.join(f"{_esc(k.replace('+', ' and '))} r = {v:.2f}" for k, v in p.get('together', {}).items()) + '). So far they are one feeling reported three times. Try moving just one when only that one changes.</p></div>') if p.get('together') else ''}
<div class="card"><p>Can a headband read what you feel? For each lever the EEG tries to predict where you put it, on listening it
never learned from. <b>A window</b> means it can, beyond your body. <b>Body, not brain</b> means muscle, motion, breathing or the music
predict it just as well. Bars show held-out correlation (0 = no idea, 1 = perfect).</p></div>
{''.join(cards)}"""
    return page("Experience map", body)


def build_booth_report(sessions_dir: Path, data_dir: Path) -> str:
    try:
        return booth_html(build_booth_profile(sessions_dir, data_dir))
    except ValueError as exc:
        return page("Experience map", f"<h1>Your experience map</h1><p class='sub'>{_esc(exc)}</p>"
                    "<p>Open the Listening booth from Home, put on music you love, and move the levers as you go.</p>")
