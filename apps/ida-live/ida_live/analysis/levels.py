"""What the levels actually did to your brain.

For every level session this asks four questions, each with a test that can say "no":

1. Did your target signal move?  The level's index in each round, relative to your own
   settle baseline in that scene, in units of the settle spread. Muscle tension leaks into
   every band on a forehead headband, so the shift is also estimated with muscle and head
   motion regressed out ("after muscle"). 95% intervals come from a block bootstrap
   (10 s blocks), which respects the fact that neighbouring seconds are not independent.
2. Was it the feedback, or just trying?  Real rounds (the image follows your brain) against
   the sealed replay round (the image replays an earlier round; you are still trying).
   Real above replay means the loop itself helped.
3. What did effort do?  Effort is muscle tension (high-frequency power, 55-95 Hz) plus head
   motion. Coupling between effort and the target is measured in 2 s bins, and its p value
   comes from circularly shifting one series against the other (a null that keeps both
   series' own rhythm).
4. Could you tell?  Your ratings of real rounds against the replay.

analyse_session(folder) -> dict,  analyse_all(sessions_dir) -> dict,
write_session_report(folder) / write_levels_report(sessions_dir) -> HTML files.
Plain numpy; reads files only.
"""

from __future__ import annotations

import html
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from .common import Session, Table

# level -> (engine column, direction that counts as success, plain name)
TARGETS = {
    "still": ("ix_alpha_rel3", +1, "relative alpha (calm)"),
    "bloom": ("ix_faa", +1, "frontal asymmetry (warmth)"),
    "steady": ("ix_engagement", +1, "engagement (focus)"),
    "ride": ("ix_theta_af_rel", +1, "forehead theta share (flow)"),
    "sky": ("lzc", +1, "complexity (open awareness)"),
    "storm": ("return", +1, "closeness to your baseline (recovery)"),
}
FALLBACK = {"ix_alpha_rel3": "ix_alpha_rel", "ix_faa": "ix_alpha_rel", "ix_theta_af_rel": "theta_af"}
LOST = ("contact", "movement", "no signal")  # seconds that carry no usable EEG at all
BIN_S = 2.0
BLOCK_S = 10.0
RNG = np.random.default_rng(20260925)
ALL_FALLS: List[dict] = []


# ------------------------------------------------------------------ helpers
def _f(x, d=2):
    return None if x is None or not np.isfinite(x) else round(float(x), d)


def _bins(t: np.ndarray, x: np.ndarray, edges: np.ndarray) -> np.ndarray:
    idx = np.digitize(t, edges) - 1
    out = np.full(len(edges) - 1, np.nan)
    for i in range(len(out)):
        v = x[(idx == i) & np.isfinite(x)]
        if len(v):
            out[i] = v.mean()
    return out


def _shift_corr(a: np.ndarray, b: np.ndarray, n: int = 1000, min_shift: int = 5):
    """Pearson r and a two-sided p from circular shifts of b against a."""
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 12 or np.nanstd(a[m]) == 0 or np.nanstd(b[m]) == 0:
        return None, None, int(m.sum())
    r = float(np.corrcoef(a[m], b[m])[0, 1])
    N = len(a)
    if N <= 2 * min_shift + 2:
        return r, None, int(m.sum())
    null = []
    for _ in range(n):
        bb = np.roll(b, int(RNG.integers(min_shift, N - min_shift)))
        mm = np.isfinite(a) & np.isfinite(bb)
        if mm.sum() >= 10 and np.std(a[mm]) > 0 and np.std(bb[mm]) > 0:
            null.append(np.corrcoef(a[mm], bb[mm])[0, 1])
    if not null:
        return r, None, int(m.sum())
    null = np.abs(np.array(null))
    return r, float((np.sum(null >= abs(r)) + 1) / (len(null) + 1)), int(m.sum())


def _block_boot(X: np.ndarray, y: np.ndarray, t: np.ndarray, reps: int = 400) -> np.ndarray:
    blk = np.floor((t - t.min()) / BLOCK_S).astype(int)
    groups = [np.where(blk == b)[0] for b in np.unique(blk)]
    out = []
    for _ in range(reps):
        idx = np.concatenate([groups[i] for i in RNG.integers(0, len(groups), len(groups))])
        try:
            out.append(np.linalg.lstsq(X[idx], y[idx], rcond=None)[0])
        except np.linalg.LinAlgError:
            pass
    return np.array(out)


# ------------------------------------------------------------------ one session
def analyse_session(folder: Path) -> Optional[dict]:
    s = Session(Path(folder))
    lvl_tab = Table(s.folder / "level.csv")
    start = s.of("level_start")
    if not start or s.features.n < 30:
        return None
    level = start[0]["level"]
    reveal = s.of("level_reveal")
    arms = reveal[0]["arms"] if reveal else []
    sound = (reveal[0].get("sound") if reveal else None) or ["none"] * len(arms)
    ratings = {e["round"]: e.get("rating") for e in s.of("level_rating")}
    ends = {e["round"]: e for e in s.of("level_round_end")}
    starts = {e["round"]: e["t"] for e in s.of("level_round_start")}
    t_end = (s.of("level_end") or s.of("session_end") or [{"t": s.features["t"][-1]}])[0]["t"]
    F = s.features
    t = F["t"]
    t0 = start[0]["t"]

    # settle window: from the level's own record if it has one
    if lvl_tab.n and lvl_tab.has("phase"):
        ph = lvl_tab["phase"]
        ts = lvl_tab["t"][ph == "settle"]
        settle = (float(ts.min()), float(ts.max())) if len(ts) else None
    else:
        settle = None
    if settle is None:
        b = s.of("level_baseline")
        if not b:
            return None
        settle = (b[0]["t"] - 40.0, b[0]["t"])

    # usable seconds: reasons from the state table matched by time
    reasons = np.array([""] * F.n, dtype=object)
    if s.state.n and s.state.has("reasons"):
        st_t = s.state["t"]
        j = np.clip(np.searchsorted(st_t, t), 0, s.state.n - 1)
        reasons = np.array([str(s.state["reasons"][k]) if abs(st_t[k] - tt) < 0.6 else "" for k, tt in zip(j, t)], dtype=object)
    usable = np.array([not any(x in r for x in LOST) for r in reasons])
    clean = np.array([r in ("", "nan", "blink") for r in reasons])

    in_settle = (t >= settle[0]) & (t <= settle[1])

    def settle_z(col):
        x = F[col].astype(float)
        ref = x[in_settle & usable & np.isfinite(x)]
        if len(ref) < 10:
            ref = x[usable & np.isfinite(x)]
        mu, sd = float(np.mean(ref)), float(np.std(ref))
        return (x - mu) / max(sd, 1e-6), mu, sd

    col, direction, label = TARGETS.get(level, ("ix_alpha_rel", +1, "relative alpha"))
    idx_ev = s.of("level_index")
    prof = idx_ev[0].get("profile") if idx_ev else None
    if prof:  # this run rewarded the personal signature from the attention map
        m_ = prof["model"]
        X = np.column_stack([F[c] if F.has(c) else np.full(F.n, np.nan) for c in m_["features"]])
        raw = prof.get("sign", 1) * (m_["w"][0] + ((X - np.array(m_["mean"])) / np.array(m_["sd"])) @ np.array(m_["w"][1:]))
        ref = raw[in_settle & usable & np.isfinite(raw)]
        y = (raw - ref.mean()) / max(ref.std(), 1e-6) if len(ref) > 10 else raw
        used, label = f"profile:{prof['contrast']}", f"your own {prof['contrast']} signature"
    elif col == "return":
        za, _, _ = settle_z("ix_alpha_rel3" if F.has("ix_alpha_rel3") else "ix_alpha_rel")
        ze, _, _ = settle_z("ix_engagement")
        y = -np.sqrt((za ** 2 + ze ** 2) / 2)
        # re-express in settle units of the distance itself
        ref = y[in_settle & usable & np.isfinite(y)]
        y = (y - ref.mean()) / max(ref.std(), 1e-6) if len(ref) > 10 else y
        used = "return"
    if prof:
        pass
    elif col == "return":
        pass
    else:
        used = col if F.has(col) and np.isfinite(F[col]).sum() > 30 else FALLBACK.get(col, col)
        if not F.has(used):
            return None
        if used != col:  # an older run, before this level had its own index
            label = {"ix_alpha_rel": "relative alpha", "theta_af": "forehead theta"}.get(used, used) + " (older version of the level)"
        y, _, _ = settle_z(used)
        y = direction * y

    # effort: muscle tension (high-frequency power; forehead too if recorded) and head motion
    emg_cols = [c for c in ("emg_af", "emg_tp") if F.has(c) and np.isfinite(F[c]).sum() > 30]
    effort = np.nanmean(np.vstack([settle_z(c)[0] for c in emg_cols]), axis=0) if emg_cols else np.zeros(F.n)
    motion = np.nan_to_num(F["motion_dps"]) if F.has("motion_dps") else np.zeros(F.n)
    muscle = np.nan_to_num(F["muscle"]) if F.has("muscle") else np.zeros(F.n)
    blink = np.nan_to_num(F["blink"]) if F.has("blink") else np.zeros(F.n)

    # segments
    segs = [{"name": "settle", "arm": "settle", "round": 0, "t0": settle[0], "t1": settle[1]}]
    for k in sorted(starts):
        t1 = ends[k]["t"] if k in ends else min([v for kk, v in starts.items() if kk > k] + [t_end])
        segs.append({"name": f"round {k}", "arm": arms[k - 1] if k - 1 < len(arms) else "?", "round": k,
                     "sound": sound[k - 1] if k - 1 < len(sound) else "none",
                     "t0": starts[k], "t1": t1, "complete": k in ends})
    cond = np.full(F.n, -1)
    for i, g in enumerate(segs):
        cond[(t >= g["t0"]) & (t < g["t1"] + (0.01 if i == 0 else 0))] = i

    # joint model: target ~ effort + motion + one term per round (settle is the baseline)
    m = usable & (cond >= 0) & np.isfinite(y) & np.isfinite(effort)
    rounds = [g for g in segs[1:] if ((cond == segs.index(g)) & m).sum() >= 20]
    cols = [np.ones(m.sum()), effort[m] - np.nanmean(effort[m]), motion[m] - motion[m].mean()]
    for g in rounds:
        cols.append((cond[m] == segs.index(g)).astype(float))
    X = np.column_stack(cols)
    fit = boot = None
    if m.sum() > len(cols) + 20:
        fit = np.linalg.lstsq(X, y[m], rcond=None)[0]
        boot = _block_boot(X, y[m], t[m])

    def ci(vec):
        return [_f(np.percentile(vec, 2.5)), _f(np.percentile(vec, 97.5))] if vec is not None and len(vec) > 20 else [None, None]

    # level-table extras: image clarity and the chamber's own record
    img_q = img_Fe = None
    if lvl_tab.n and lvl_tab.has("q"):
        img_q, img_Fe = lvl_tab["q"], (lvl_tab["Fe"] if lvl_tab.has("Fe") else None)

    out_rounds = []
    for i, g in enumerate(segs):
        sm = cond == i
        um = sm & usable
        row = {"name": g["name"], "arm": g["arm"], "round": g["round"], "seconds": _f(g["t1"] - g["t0"], 0),
               "usable": _f(um.sum() / max(1, sm.sum())), "clean": _f((sm & clean).sum() / max(1, sm.sum())),
               "muscle": _f(muscle[sm].mean() if sm.any() else np.nan), "motion": _f(motion[sm].mean() if sm.any() else np.nan, 1),
               "blink": _f(blink[sm].mean() if sm.any() else np.nan),
               "effort": _f(np.nanmean(effort[um]) if um.any() else np.nan),
               "shift": _f(np.nanmean(y[um]) if um.sum() >= 10 else np.nan)}
        if i > 0:
            row["rating"] = ratings.get(g["round"])
            row["sound"] = g.get("sound", "none")
            e = ends.get(g["round"], {})
            row.update({"max_tier": e.get("max_tier"), "tier_name": e.get("max_tier_name"),
                        "knocks": e.get("perturbations"), "recovery_s": e.get("mean_recovery_s"), "complete": g.get("complete", False)})
            if g in rounds and fit is not None:
                j = 3 + rounds.index(g)
                row["shift_after_muscle"] = _f(fit[j])
                row["ci"] = ci(boot[:, j] if boot is not None and len(boot) else None)
            # what the image followed (real rounds follow you; a replay should follow nothing)
            if img_q is not None and g["t1"] - g["t0"] > 30:
                edges = np.arange(g["t0"], g["t1"], BIN_S)
                q_b = _bins(lvl_tab["t"], img_q, edges)
                y_b = _bins(t[um], y[um], edges)
                e_b = _bins(t[sm], effort[sm], edges)
                r1, p1, _ = _shift_corr(y_b, q_b)
                r2, p2, _ = _shift_corr(e_b, q_b)
                row["image_follows_target"] = {"r": _f(r1), "p": _f(p1, 3)}
                row["image_follows_effort"] = {"r": _f(r2), "p": _f(p2, 3)}
        out_rounds.append(row)

    # effort <-> target coupling over all round time, 2 s bins
    rm = cond >= 1
    coupling = None
    if rm.sum() > 60:
        edges = np.arange(t[rm].min(), t[rm].max(), BIN_S)
        yb = _bins(t[rm & usable], y[rm & usable], edges)
        eb = _bins(t[rm], effort[rm], edges)
        mb = _bins(t[rm], motion[rm], edges)
        r, p, n = _shift_corr(eb, yb)
        rmo, pmo, _ = _shift_corr(mb, yb)
        coupling = {"effort_r": _f(r), "effort_p": _f(p, 3), "motion_r": _f(rmo), "motion_p": _f(pmo, 3), "bins": n}

    # pooled real vs replay (only complete-enough rounds with an estimate)
    def pooled(arm):
        idx = [3 + rounds.index(g) for g in rounds if g["arm"] == arm]
        if not idx or fit is None:
            return None
        est = float(np.mean(fit[idx]))
        bs = boot[:, idx].mean(axis=1) if boot is not None and len(boot) else None
        return {"shift": _f(est), "ci": ci(bs), "_bs": bs}

    real, sham = pooled("real"), pooled("sham")

    # the rhythmic tone: rounds with the rhythm against rounds with irregular pulses
    def pooled_sound(cond):
        idx = [3 + rounds.index(g) for g in rounds if g.get("sound") == cond]
        if not idx or fit is None:
            return None
        bs = boot[:, idx].mean(axis=1) if boot is not None and len(boot) else None
        return {"shift": _f(float(np.mean(fit[idx]))), "ci": ci(bs), "_bs": bs}

    ent, ctl = pooled_sound("entrain"), pooled_sound("control")
    rhythm = None
    if ent and ctl and ent["_bs"] is not None and ctl["_bs"] is not None:
        rhythm = {"shift": _f(ent["shift"] - ctl["shift"]), "ci": ci(ent["_bs"] - ctl["_bs"]),
                  "hz": next((e.get("entrain_hz") for e in start), None)}
    diff = None
    if real and sham and real["_bs"] is not None and sham["_bs"] is not None:
        d = real["_bs"] - sham["_bs"]
        diff = {"shift": _f(real["shift"] - sham["shift"]), "ci": ci(d)}
    for p_ in (real, sham):
        if p_:
            p_.pop("_bs", None)

    rr = [r["rating"] for r in out_rounds[1:] if r["arm"] == "real" and r.get("rating") is not None]
    rs = [r["rating"] for r in out_rounds[1:] if r["arm"] == "sham" and r.get("rating") is not None]
    sham_pos = [r["round"] for r in out_rounds[1:] if r["arm"] == "sham"]

    res = {
        "session": s.name, "level": level, "target": used, "target_label": label, "arms": arms,
        "made": time.strftime("%Y-%m-%d %H:%M"), "units": "settle SD (your spread while just watching this scene)",
        "effort_measure": "+".join(emg_cols) or "none", "rounds": out_rounds,
        "effort_weight": _f(fit[1]) if fit is not None else None,
        "effort_weight_ci": ci(boot[:, 1] if boot is not None and len(boot) else None),
        "coupling": coupling, "real": real, "sham": sham, "real_minus_sham": diff, "rhythm_minus_irregular": rhythm,
        "ratings": {"real": rr, "sham": rs}, "sham_rounds": sham_pos, "n_rounds_planned": len(arms),
    }
    res["feel"] = _feel(s, lvl_tab, segs)
    res["falls"] = carry_falls(lvl_tab)
    res["carry"] = carry_test(res["falls"])
    res["journey"] = bool(start[0].get("journey"))
    res["verdicts"] = _verdicts(res)
    res["_series"] = _series(t, y, effort, cond, segs, usable, t0)
    return res


def carry_falls(lvl_tab: Table) -> List[dict]:
    """Every fall in a journey and how long it took to come back, from the recorded occupancy
    (your brain, never the display): smoothed like the level's own (1.5 s), the fall's peak is
    the highest value in the 8 s before it, and 'back' is the first moment at 90% of that peak
    (capped at 30 s). The arm (carry or follow) was sealed before the level started."""
    if not lvl_tab.n or not lvl_tab.has("event") or not lvl_tab.has("Fe"):
        return []
    t, fe, ev = lvl_tab["t"], np.nan_to_num(lvl_tab["Fe"]), lvl_tab["event"]
    o = np.argsort(t)
    t, fe, ev = t[o], fe[o], ev[o]
    fs = np.zeros(len(fe))
    for i in range(1, len(fe)):
        dt = max(0.0, min(1.0, t[i] - t[i - 1]))
        fs[i] = fs[i - 1] + (1 - math.exp(-dt / 1.5)) * (fe[i] - fs[i - 1])
    out = []
    for i in np.nonzero(np.array([str(e).startswith("dip:") for e in ev]))[0]:
        arm = str(ev[i]).split(":", 1)[1]
        pre_m = (t >= t[i] - 8) & (t <= t[i])
        pre = float(fs[pre_m].max()) if pre_m.any() else float(fs[i])
        after = np.nonzero((t > t[i]) & (fs >= 0.9 * pre))[0]
        back = float(min(30.0, t[after[0]] - t[i])) if len(after) else None
        if back is None and t[-1] - t[i] >= 30:
            back = 30.0
        out.append({"arm": arm, "t": float(t[i]), "pre": round(pre, 3), "back_s": None if back is None else round(back, 2)})
    return out


def carry_test(falls: List[dict]) -> Optional[dict]:
    """Carried falls against followed falls: median time back, share back within 15 s, and a
    two-sided permutation test on the difference in mean time back (falls cut short left out)."""
    c = np.array([f["back_s"] for f in falls if f["arm"] == "carry" and f["back_s"] is not None])
    f_ = np.array([f["back_s"] for f in falls if f["arm"] == "follow" and f["back_s"] is not None])
    if len(c) == 0 and len(f_) == 0:
        return None
    res = {"carried": int(len(c)), "followed": int(len(f_)),
           "median_back_carry": _f(np.median(c)) if len(c) else None, "median_back_follow": _f(np.median(f_)) if len(f_) else None,
           "within15_carry": _f(np.mean(c <= 15)) if len(c) else None, "within15_follow": _f(np.mean(f_ <= 15)) if len(f_) else None, "p": None}
    if len(c) >= 3 and len(f_) >= 3:
        allv = np.concatenate([c, f_])
        obs = c.mean() - f_.mean()
        ge = 0
        for _ in range(4000):
            RNG.shuffle(allv)
            ge += abs(allv[:len(c)].mean() - allv[len(c):].mean()) >= abs(obs) - 1e-12
        res["p"] = _f((ge + 1) / 4001, 4)
        res["diff_mean_s"] = _f(obs)
    return res


def _sig(ci_):
    return ci_ and ci_[0] is not None and (ci_[0] > 0 or ci_[1] < 0)


def _feel(s: Session, lvl_tab: Table, segs: List[dict]) -> dict:
    """How it felt: the affect grid before, after and per round; chills and whether they fell
    on the music's designed peak moments (tier peaks, resolutions, returns) more than chance."""
    aff = {"pre": None, "post": None, "rounds": {}}
    for e in s.of("level_affect"):
        v = [e.get("valence"), e.get("arousal")]
        if e.get("when") == "pre":
            aff["pre"] = v
        elif e.get("when") == "post":
            aff["post"] = v
        elif e.get("when") == "round":
            aff["rounds"][int(e.get("round", 0))] = v
    if aff["pre"] and aff["post"]:
        aff["change"] = [_f(aff["post"][0] - aff["pre"][0]), _f(aff["post"][1] - aff["pre"][1])]
    out = {"affect": aff, "chills": 0}
    if lvl_tab.n == 0 or not lvl_tab.has("event"):
        return out
    ev, t = lvl_tab["event"], lvl_tab["t"]
    chills = np.array([tt for e, tt in zip(ev, t) if e == "chill"])
    peaks = np.array([tt for e, tt in zip(ev, t) if isinstance(e, str) and e in ("music:peak", "music:resolve", "music:return")])
    out["chills"] = int(len(chills))
    out["music_moments"] = int(len(peaks))
    rounds = [g for g in segs if g["round"] > 0]
    if len(chills) >= 3 and len(peaks) >= 2 and rounds:
        near = lambda cs, ps: int(sum(np.any((c - ps >= 0) & (c - ps <= 8.0)) for c in cs))
        obs = near(chills, peaks)
        # chance: the same chills shifted circularly within their round
        null = []
        for _ in range(2000):
            sh = []
            for c in chills:
                g = next((g for g in rounds if g["t0"] <= c <= g["t1"]), None)
                if g is None:
                    sh.append(c)
                    continue
                L = g["t1"] - g["t0"]
                sh.append(g["t0"] + ((c - g["t0"] + RNG.uniform(0, L)) % L))
            null.append(near(np.array(sh), peaks))
        null = np.array(null)
        out["chills_near_peaks"] = obs
        out["expected_by_chance"] = _f(null.mean(), 1)
        out["p"] = _f(float((np.sum(null >= obs) + 1) / (len(null) + 1)), 3)
    return out


def _verdicts(r: dict) -> List[str]:
    v = []
    lab = r["target_label"]
    real, sham, diff = r["real"], r["sham"], r["real_minus_sham"]
    if real:
        word = ("rose" if real["shift"] > 0 else "fell") if _sig(real["ci"]) else "did not move clearly"
        v.append(f"While the scene followed you, your {lab} {word}: {real['shift']:+.2f} settle SD after removing muscle "
                 f"(95% interval {real['ci'][0]:+.2f} to {real['ci'][1]:+.2f}).")
    else:
        v.append("No complete real round with enough usable signal to estimate an effect.")
    if diff:
        if _sig(diff["ci"]):
            v.append(f"Real rounds differed from the replay by {diff['shift']:+.2f} SD "
                     f"({diff['ci'][0]:+.2f} to {diff['ci'][1]:+.2f}): the loop itself made a difference"
                     + (" in the intended direction." if diff["shift"] > 0 else ", but in the wrong direction."))
        else:
            v.append(f"Real rounds and the replay were not clearly different ({diff['shift']:+.2f} SD, "
                     f"{diff['ci'][0]:+.2f} to {diff['ci'][1]:+.2f}), so no evidence yet that the feedback loop itself helped.")
    elif sham is None and not r.get("journey"):
        v.append("No replay round was completed, so feedback and plain trying can't be told apart in this run.")
    cy = r.get("carry")
    if cy:
        v.append(f"You fell {cy['carried'] + cy['followed']} time{'s' if cy['carried'] + cy['followed'] != 1 else ''}: "
                 f"carried back in {cy['median_back_carry'] if cy['median_back_carry'] is not None else '–'} s (median, {cy['carried']} falls), "
                 f"followed back in {cy['median_back_follow'] if cy['median_back_follow'] is not None else '–'} s ({cy['followed']} falls)"
                 + (f"; permutation p = {cy['p']:.3f}." if cy.get("p") is not None else ". Too few falls in one journey to test; the pooled result is on the levels page."))
    c = r["coupling"]
    if c and c.get("effort_r") is not None and c.get("effort_p") is not None:
        if c["effort_p"] < 0.05:
            v.append(f"Effort and the target were coupled (r = {c['effort_r']:+.2f}, p = {c['effort_p']:.3f}): "
                     + ("more muscle tension went with a worse score." if c["effort_r"] < 0 else "more muscle tension went with a better score. Check this isn't muscle leaking into the signal."))
        else:
            v.append(f"No clear coupling between effort and the target (r = {c['effort_r']:+.2f}, p = {c['effort_p']:.2f}).")
    if r["ratings"]["real"] and r["ratings"]["sham"]:
        mr, ms = np.mean(r["ratings"]["real"]), np.mean(r["ratings"]["sham"])
        v.append(f"You rated real rounds {mr:.1f} and the replay {ms:.1f} (0-4)."
                 + (" The replay was the last round, so tiredness or giving up can explain the gap as well as real detection." if r["sham_rounds"] and r["sham_rounds"][0] == r["n_rounds_planned"] else ""))
    fe = r.get("feel") or {}
    a = fe.get("affect") or {}
    if a.get("change"):
        dv, da = a["change"]
        v.append(f"Mood moved {'towards pleasant' if dv > 0 else 'towards unpleasant' if dv < 0 else 'not at all on pleasantness'} ({dv:+.2f}) and "
                 f"{'more energised' if da > 0 else 'calmer' if da < 0 else 'no change in energy'} ({da:+.2f}) from before to after (grid units, -1 to 1).")
    if fe.get("chills"):
        if fe.get("p") is not None:
            v.append(f"You marked {fe['chills']} chills; {fe['chills_near_peaks']} came within 8 s after a designed peak, resolution or return, "
                     f"against {fe['expected_by_chance']} expected by chance (p = {fe['p']:.3f}).")
        else:
            v.append(f"You marked {fe['chills']} chill{'s' if fe['chills'] != 1 else ''} (too few to test against the music's peaks).")
    rh = r.get("rhythm_minus_irregular")
    if rh:
        v.append(f"The rhythmic tone ({rh.get('hz') or '?'} Hz) against irregular pulses: {rh['shift']:+.2f} SD "
                 f"({rh['ci'][0]:+.2f} to {rh['ci'][1]:+.2f})" + (": a real difference." if _sig(rh["ci"]) else ", not a clear difference yet."))
    for g in r["rounds"][1:]:
        f = g.get("image_follows_effort") or {}
        if g["arm"] == "real" and f.get("p") is not None and f["p"] < 0.05 and f["r"] > 0:
            v.append(f"In {g['name']} the image's clarity rose with your muscle tension (r = {f['r']:+.2f}): the scene was rewarding strain (fixed in 0.5).")
            break
    return v


def _series(t, y, effort, cond, segs, usable, t0) -> dict:
    lo, hi = segs[0]["t0"] - 5, max(g["t1"] for g in segs)
    edges = np.arange(lo, hi + BIN_S, BIN_S)
    mid = (edges[:-1] + edges[1:]) / 2
    m = cond >= 0
    yb = _bins(t[m & usable], np.clip(y[m & usable], -6, 6), edges)
    eb = _bins(t[m], np.clip(effort[m], -6, 8), edges)
    return {"x": [round(float(x - t0), 1) for x in mid], "y": [_f(v) for v in yb], "effort": [_f(v) for v in eb],
            "segs": [{"name": g["name"], "arm": g["arm"], "a": round(g["t0"] - t0, 1), "b": round(g["t1"] - t0, 1)} for g in segs]}


# ------------------------------------------------------------------ across sessions
def _each(sessions_dir: Path) -> List[dict]:
    per = []
    for p in sorted(Path(sessions_dir).glob("*level-*"), reverse=True):
        if not (p / "manifest.json").exists():
            continue
        try:
            r = analyse_session(p)
        except Exception as exc:  # one broken session must not hide the rest
            r = {"session": p.name, "error": str(exc)}
        if r:
            per.append(r)
    return per


def analyse_all(sessions_dir: Path, per: Optional[List[dict]] = None) -> dict:
    per = _each(sessions_dir) if per is None else per
    levels: Dict[str, dict] = {}
    global ALL_FALLS
    ALL_FALLS = []
    for r in per:
        if "error" in r:
            continue
        key = f"{r['level']}|{r['target']}"  # runs are only pooled when they measured the same thing
        L = levels.setdefault(key, {"level": r["level"], "label": r["target_label"], "runs": 0, "real": [], "diff": [],
                                          "rating_gaps": [], "coupling": [], "mood": []})
        L["runs"] += 1
        if r["real"] and r["real"]["ci"][0] is not None:
            L["real"].append((r["real"]["shift"], r["real"]["ci"]))
        if r["real_minus_sham"] and r["real_minus_sham"]["ci"][0] is not None:
            L["diff"].append((r["real_minus_sham"]["shift"], r["real_minus_sham"]["ci"]))
        if r["ratings"]["real"] and r["ratings"]["sham"]:
            L["rating_gaps"].append(float(np.mean(r["ratings"]["real"]) - np.mean(r["ratings"]["sham"])))
        if r["coupling"] and r["coupling"].get("effort_r") is not None:
            L["coupling"].append((r["coupling"]["effort_r"], r["coupling"]["bins"]))
        ch = ((r.get("feel") or {}).get("affect") or {}).get("change")
        if ch:
            L["mood"].append(ch[0])
        ALL_FALLS.extend(r.get("falls") or [])
    for L in levels.values():
        L["real_pooled"] = _pool(L.pop("real"))
        L["diff_pooled"] = _pool(L.pop("diff"))
        g = L.pop("rating_gaps")
        pos = sum(x > 0 for x in g)
        L["ratings"] = {"sessions": len(g), "real_above_replay": pos,
                        "sign_p": _f(_binom_p(pos, len(g)), 3) if g else None, "mean_gap": _f(np.mean(g)) if g else None}
        md = L.pop("mood")
        L["mood"] = {"sessions": len(md), "mean_valence_change": _f(np.mean(md)) if md else None,
                     "better_after": sum(x > 0 for x in md), "sign_p": _f(_binom_p(sum(x > 0 for x in md), len(md)), 3) if md else None}
        cp = L.pop("coupling")
        if cp:
            zs = [math.atanh(max(-0.999, min(0.999, r))) for r, n in cp]
            w = [max(1, n - 3) for r, n in cp]
            zbar = float(np.average(zs, weights=w))
            se = 1 / math.sqrt(sum(w))
            L["effort_coupling"] = {"r": _f(math.tanh(zbar)), "ci": [_f(math.tanh(zbar - 1.96 * se)), _f(math.tanh(zbar + 1.96 * se))], "runs": len(cp),
                                    "note": "bins treated as independent here, so this interval is optimistic"}
    return {"made": time.strftime("%Y-%m-%d %H:%M"), "levels": levels, "carry": carry_test(ALL_FALLS),
            "sessions": [{k: v for k, v in r.items() if k != "_series"} for r in per]}


def _pool(items):
    """Inverse-variance mean of per-session shifts (SE from each 95% interval)."""
    if not items:
        return None
    est = np.array([x for x, _ in items])
    se = np.array([max(1e-3, (c[1] - c[0]) / 3.92) for _, c in items])
    w = 1 / se ** 2
    m = float(np.sum(w * est) / np.sum(w))
    s = float(1 / math.sqrt(np.sum(w)))
    return {"shift": _f(m), "ci": [_f(m - 1.96 * s), _f(m + 1.96 * s)], "runs": len(items)}


def _binom_p(k: int, n: int) -> float:
    """One-sided P(X >= k), X ~ Binomial(n, 1/2)."""
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0


# ------------------------------------------------------------------ HTML
CSS = """
:root { color-scheme: light; --bg:#fcfcfb; --card:#ffffff; --ink:#0b0b0b; --ink2:#52514e; --ink3:#8a8984; --line:#e4e3de;
  --real:#2a78d6; --sham:#eb6834; --settle:#8a8984; --realbg:rgba(42,120,214,.09); --shambg:rgba(235,104,52,.10); --settlebg:rgba(138,137,132,.10);
  --good:#008300; --bad:#c23b3a; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { color-scheme: dark; --bg:#121211; --card:#1a1a19; --ink:#ffffff; --ink2:#c3c2b7; --ink3:#8f8e87;
  --line:#2e2e2b; --real:#3987e5; --sham:#d95926; --settle:#8f8e87; --realbg:rgba(57,135,229,.16); --shambg:rgba(217,89,38,.18); --settlebg:rgba(143,142,135,.14);
  --good:#3fb950; --bad:#e66767; } }
:root[data-theme="dark"] { color-scheme: dark; --bg:#121211; --card:#1a1a19; --ink:#ffffff; --ink2:#c3c2b7; --ink3:#8f8e87; --line:#2e2e2b;
  --real:#3987e5; --sham:#d95926; --settle:#8f8e87; --realbg:rgba(57,135,229,.16); --shambg:rgba(217,89,38,.18); --settlebg:rgba(143,142,135,.14); --good:#3fb950; --bad:#e66767; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1040px; margin: 0 auto; padding: 28px 16px 60px; }
h1 { font-size: 28px; font-weight: 600; margin: 0 0 4px; } h2 { font-size: 19px; font-weight: 600; margin: 34px 0 10px; }
h3 { font-size: 16px; font-weight: 600; margin: 0 0 6px; }
.sub { color: var(--ink2); margin: 0 0 18px; } .fine { color: var(--ink3); font-size: 13px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 16px 18px; margin: 12px 0; }
ul.v { margin: 0; padding-left: 20px; } ul.v li { margin: 6px 0; }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; font-variant-numeric: tabular-nums; }
th, td { text-align: left; padding: 7px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { color: var(--ink3); font-weight: 500; }
.tag { display:inline-block; padding: 1px 8px; border-radius: 99px; font-size: 12px; border:1px solid var(--line); }
.tag.real { color: var(--real); border-color: var(--real); } .tag.sham { color: var(--sham); border-color: var(--sham); } .tag.settle { color: var(--ink2); }
.chart { position: relative; } .chart svg { width: 100%; height: auto; display: block; overflow: visible; }
.tip { position: absolute; pointer-events: none; background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 6px 9px;
  font-size: 12.5px; box-shadow: 0 6px 20px rgba(0,0,0,.18); display: none; white-space: nowrap; }
.legend { display:flex; gap:16px; flex-wrap: wrap; font-size: 13px; color: var(--ink2); margin: 6px 0 2px; }
.legend i { display:inline-block; width: 14px; height: 10px; border-radius: 3px; margin-right: 6px; vertical-align: -1px; }
.grid2 { display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; }
.stat b { font-size: 26px; font-weight: 600; display:block; } .up { color: var(--good); } .down { color: var(--bad); }
a { color: var(--real); } .scroll { overflow-x: auto; }
details summary { cursor: pointer; color: var(--ink2); }
"""

JS = """
document.querySelectorAll('.chart[data-series]').forEach(el => {
  const d = JSON.parse(el.dataset.series), svg = el.querySelector('svg'), tip = el.querySelector('.tip'), cross = svg.querySelector('.cross');
  const W = +svg.dataset.w, L = +svg.dataset.l, R = +svg.dataset.r, x0 = +svg.dataset.x0, x1 = +svg.dataset.x1;
  svg.addEventListener('mousemove', ev => {
    const b = svg.getBoundingClientRect(), px = (ev.clientX - b.left) * W / b.width;
    const xv = x0 + (px - L) / (W - L - R) * (x1 - x0);
    let k = 0, best = 1e9; d.x.forEach((x, i) => { const dd = Math.abs(x - xv); if (dd < best) { best = dd; k = i; } });
    const seg = d.segs.find(s => d.x[k] >= s.a && d.x[k] <= s.b);
    const cx = L + (d.x[k] - x0) / (x1 - x0) * (W - L - R);
    cross.setAttribute('x1', cx); cross.setAttribute('x2', cx); cross.style.display = '';
    const f = v => v === null ? '–' : (v > 0 ? '+' : '') + v.toFixed(2);
    tip.innerHTML = `<b>${Math.floor(d.x[k] / 60)}:${String(Math.round(d.x[k] % 60)).padStart(2, '0')}</b> · ${seg ? seg.name + (seg.arm === 'sham' ? ' (replay)' : '') : 'between'}<br>target ${f(d.y[k])} SD<br>effort ${f(d.effort[k])} SD`;
    tip.style.display = 'block';
    const left = (cx / W) * b.width; tip.style.left = Math.min(b.width - 170, left + 12) + 'px'; tip.style.top = '8px';
  });
  svg.addEventListener('mouseleave', () => { tip.style.display = 'none'; cross.style.display = 'none'; });
});
"""


def _esc(x) -> str:
    return html.escape(str(x))


def _timeline(series: dict) -> str:
    """Two stacked panels sharing time: target (top) and effort (bottom), rounds shaded."""
    W, H, L, R = 1000, 330, 46, 12
    x = series["x"]
    if not x:
        return ""
    x0, x1 = min(x), max(x)
    sx = lambda v: L + (v - x0) / max(1e-6, x1 - x0) * (W - L - R)
    panels = [("y", 14, 160, -4, 4, "target (settle SD)"), ("effort", 196, 300, -2, 6, "effort (settle SD)")]
    out = [f'<svg viewBox="0 0 {W} {H}" data-w="{W}" data-l="{L}" data-r="{R}" data-x0="{x0}" data-x1="{x1}" role="img" aria-label="Target and effort over time">']
    for g in series["segs"]:
        a, b = sx(max(x0, g["a"])), sx(min(x1, g["b"]))
        fill = {"real": "var(--realbg)", "sham": "var(--shambg)"}.get(g["arm"], "var(--settlebg)")
        out.append(f'<rect x="{a:.1f}" y="8" width="{max(0, b - a):.1f}" height="{H - 36}" fill="{fill}"/>')
        name = "settle" if g["arm"] == "settle" else g["name"] + (" · replay" if g["arm"] == "sham" else "")
        out.append(f'<text x="{a + 5:.1f}" y="{H - 12}" font-size="12" fill="var(--ink2)">{_esc(name)}</text>')
    for key, top, bot, lo, hi, lab in panels:
        sy = lambda v, top=top, bot=bot, lo=lo, hi=hi: bot - (min(hi, max(lo, v)) - lo) / (hi - lo) * (bot - top)
        for gv in range(lo, hi + 1, 2):
            out.append(f'<line x1="{L}" x2="{W - R}" y1="{sy(gv):.1f}" y2="{sy(gv):.1f}" stroke="var(--line)" stroke-width="{1.4 if gv == 0 else 0.8}"/>')
            out.append(f'<text x="{L - 6}" y="{sy(gv) + 4:.1f}" font-size="11" text-anchor="end" fill="var(--ink3)">{gv:+d}</text>')
        out.append(f'<text x="{L}" y="{top - 2}" font-size="12" fill="var(--ink2)">{_esc(lab)}</text>')
        path, pen = [], False
        for xv, v in zip(x, series[key]):
            if v is None:
                pen = False
                continue
            path.append(("L" if pen else "M") + f"{sx(xv):.1f},{sy(v):.1f}")
            pen = True
        out.append(f'<path d="{" ".join(path)}" fill="none" stroke="var(--ink)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
    out.append(f'<line class="cross" x1="0" x2="0" y1="8" y2="{H - 28}" stroke="var(--ink3)" stroke-width="1" style="display:none"/>')
    out.append("</svg>")
    return f'<div class="chart" data-series="{_esc(json.dumps(series))}">{"".join(out)}<div class="tip"></div></div>'


def _ci(c):
    return "–" if not c or c[0] is None else f"{c[0]:+.2f} to {c[1]:+.2f}"


def _num(v, d=2, sign=True):
    return "–" if v is None else (f"{v:+.{d}f}" if sign else f"{v:.{d}f}")


def session_html(r: dict) -> str:
    rows = []
    for g in r["rounds"]:
        snd = {"entrain": " · rhythm", "control": " · irregular"}.get(g.get("sound") or "", "")
        tag = f'<span class="tag {g["arm"]}">{"replay" if g["arm"] == "sham" else g["arm"]}</span><span class="fine">{snd}</span>'
        img = g.get("image_follows_target") or {}
        eff = g.get("image_follows_effort") or {}
        rows.append(f"<tr><td>{_esc(g['name'])}{'' if g.get('complete', True) else ' (cut short)'}</td><td>{tag}</td><td>{_num(g['seconds'], 0, False)} s</td>"
                    f"<td>{_num(g['usable'] and 100 * g['usable'], 0, False)}%</td><td>{_num(g['muscle'] and 100 * g['muscle'], 0, False)}%</td>"
                    f"<td>{_num(g['motion'], 1, False)}</td><td>{_num(g['effort'])}</td><td>{_num(g['shift'])}</td>"
                    f"<td>{_num(g.get('shift_after_muscle'))}<br><span class='fine'>{_ci(g.get('ci'))}</span></td>"
                    f"<td>{_num(img.get('r'))} / {_num(eff.get('r'))}</td>"
                    f"<td>{'' if g['arm'] == 'settle' else (g.get('max_tier') or '–')}</td>"
                    f"<td>{'' if g['arm'] == 'settle' else ('–' if g.get('rating') is None else g['rating'])}</td></tr>")
    c = r.get("coupling") or {}
    return f"""
<section class="card">
  <h3>{_esc(r['level'].title())} · {_esc(r['session'])}</h3>
  <p class="fine">Target: {_esc(r['target_label'])} ({_esc(r['target'])}). Effort: muscle tension ({_esc(r['effort_measure'])}) and head motion. Units: {_esc(r['units'])}.</p>
  <ul class="v">{"".join(f"<li>{_esc(v)}</li>" for v in r['verdicts'])}</ul>
  <div class="legend"><span><i style="background:var(--settlebg);border:1px solid var(--settle)"></i>settle (baseline)</span>
    <span><i style="background:var(--realbg);border:1px solid var(--real)"></i>real round</span>
    <span><i style="background:var(--shambg);border:1px solid var(--sham)"></i>replay round</span></div>
  {_timeline(r['_series'])}
  <div class="scroll"><table>
    <tr><th>Part</th><th>Arm</th><th>Length</th><th>Usable</th><th>Muscle</th><th>Motion °/s</th><th>Effort</th><th>Target shift</th><th>After muscle (95%)</th><th>Image follows target / effort (r)</th><th>Top tier</th><th>Rating</th></tr>
    {"".join(rows)}
  </table></div>
  <p class="fine">Effort ↔ target over all rounds: r = {_num(c.get('effort_r'))} (p = {_num(c.get('effort_p'), 3, False)}), head motion ↔ target r = {_num(c.get('motion_r'))} (p = {_num(c.get('motion_p'), 3, False)}), {c.get('bins', 0)} bins of 2 s.
  Target shift is the raw mean against settle; "after muscle" removes the part explained by muscle and motion.</p>
</section>"""


def page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title><style>{CSS}</style></head><body><main>{body}</main><script>{JS}</script></body></html>"""


def levels_html(a: dict, sessions: List[dict]) -> str:
    cards = []
    for L in a["levels"].values():
        rp, dp, rt, ec = L.get("real_pooled"), L.get("diff_pooled"), L.get("ratings", {}), L.get("effort_coupling")
        cls = lambda p: "" if not p or p["ci"][0] is None else ("up" if p["ci"][0] > 0 else "down" if p["ci"][1] < 0 else "")
        cards.append(f"""<div class="card"><h3>{_esc(L['level'].title())}</h3><p class="fine">{_esc(L['label'])} · {L['runs']} run{'s' if L['runs'] != 1 else ''}</p>
          <div class="grid2">
          <div class="stat"><span class="fine">Real rounds vs your baseline</span><b class="{cls(rp)}">{_num(rp and rp['shift'])}</b><span class="fine">{_ci(rp and rp['ci'])} SD</span></div>
          <div class="stat"><span class="fine">Real minus replay</span><b class="{cls(dp)}">{_num(dp and dp['shift'])}</b><span class="fine">{_ci(dp and dp['ci'])} SD · {dp['runs'] if dp else 0} run(s)</span></div>
          <div class="stat"><span class="fine">Rated real above replay</span><b>{rt.get('real_above_replay', 0)} of {rt.get('sessions', 0)}</b><span class="fine">sign test p = {_num(rt.get('sign_p'), 3, False)}</span></div>
          <div class="stat"><span class="fine">Effort ↔ target</span><b>{_num(ec and ec['r'])}</b><span class="fine">{_ci(ec and ec['ci'])}</span></div>
          <div class="stat"><span class="fine">Felt better after</span><b>{(L.get('mood') or {}).get('better_after', 0)} of {(L.get('mood') or {}).get('sessions', 0)}</b><span class="fine">mean pleasantness change {_num((L.get('mood') or {}).get('mean_valence_change'))}</span></div>
          </div></div>""")
    body = f"""<h1>What the levels did</h1><p class="sub">Every level session so far, made {_esc(a['made'])}. Units are settle SD: how far from your own baseline in that scene.
      A result counts only when its 95% interval excludes zero. One run proves little; the replay rounds make the evidence build up across runs.</p>
      {_carry_card(a.get('carry'))}
      {''.join(cards) or '<p>No level sessions yet.</p>'}
      <h2>Each session</h2>{''.join(session_html(s) for s in sessions if 'error' not in s)}
      <details class="card"><summary>How this is worked out</summary>
      <p class="fine">The target is the engine's version of the level's index (1 s windows), zeroed at your settle mean and divided by your settle spread.
      Seconds with lost contact or head movement are dropped; muscle is kept and regressed out, since on a headband muscle tension raises the power of every band.
      Intervals: block bootstrap with 10 s blocks. Coupling p values: circular shifts of one 2 s series against the other.
      Pooling across runs: inverse-variance weights. Ratings: one-sided sign test of real above replay across sessions.</p></details>"""
    return page("IDA Live · What the levels did", body)


def _carry_card(c) -> str:
    if not c:
        return ""
    verdict = ("The carry brings you back faster." if c.get("p") is not None and c["p"] < 0.05 and (c.get("diff_mean_s") or 0) < 0
               else "Carried falls came back slower: the lift may be getting in the way." if c.get("p") is not None and c["p"] < 0.05
               else "No clear difference yet." if c.get("p") is not None else "Not enough falls of each kind yet (three of each is the minimum).")
    return f"""<div class="card"><h3>The carry: does being lifted bring you back?</h3>
      <p class="fine">At each fall a sealed coin decided whether the scene, music and pulse lifted you (carry) or simply followed you.
      Time back is measured from your brain, never the display.</p>
      <div class="grid2">
      <div class="stat"><span class="fine">Carried</span><b>{_num(c.get('median_back_carry'), 1, False)} s</b><span class="fine">median time back · {c['carried']} falls · {_num(c.get('within15_carry') and 100 * c['within15_carry'], 0, False)}% within 15 s</span></div>
      <div class="stat"><span class="fine">Followed</span><b>{_num(c.get('median_back_follow'), 1, False)} s</b><span class="fine">median time back · {c['followed']} falls · {_num(c.get('within15_follow') and 100 * c['within15_follow'], 0, False)}% within 15 s</span></div>
      <div class="stat"><span class="fine">Difference (carry − follow)</span><b>{_num(c.get('diff_mean_s'), 1)} s</b><span class="fine">permutation p = {_num(c.get('p'), 3, False)}</span></div>
      </div><p>{_esc(verdict)}</p></div>"""


def write_session_report(folder: Path) -> Optional[Path]:
    r = analyse_session(Path(folder))
    if not r:
        return None
    p = Path(folder) / "report.html"
    p.write_text(page(f"IDA Live · {r['level']} · {r['session']}", f"<h1>{_esc(r['level'].title())}</h1><p class='sub'>What this run did to your brain.</p>" + session_html(r)), encoding="utf-8")
    (Path(folder) / "report.json").write_text(json.dumps({k: v for k, v in r.items() if k != "_series"}, indent=1), encoding="utf-8")
    return p


def build_levels_report(sessions_dir: Path) -> str:
    per = _each(sessions_dir)
    return levels_html(analyse_all(sessions_dir, per), per)


def write_levels_report(sessions_dir: Path, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_levels_report(sessions_dir), encoding="utf-8")
    return out
