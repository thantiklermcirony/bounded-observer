"""The Murray Reality Equation test, analysed exactly as its paper plans it (history/R15 §3-4).

The claim under test: a quantum measurement stream's alternation bias δ = P(1|0) - P(1|1)
rises with the observer's information rate Φ, δ(Φ) = tanh(atanh δ0 + 2 α0 κ Φ), while the
marginal p stays put. Small-signal: dδ/dΦ = 2 α0 κ (1 - δ0²), so κ = β_δ / (2 α0 (1 - δ0²)).

C1  automation: bins logged with no headband connected. Gives δ0, p and the device transfer
    factor α0 = 1 / H_rate, H_rate = Laplace-smoothed H(X_t | X_t-1) / 0.1 s  (§3.3).
    F1: the same transition GLM fitted on C1 with a real Φ trace laid over it must show no
    slope, |β| < 2 SE.
C2  focused attention: bins logged while a recording runs with a clean headband signal.
    Transition GLM (7): logit P(X_t = 1 | X_t-1 = x) = β0(x) + β1(x) Φ_t + γ2 p̄_block
    + γ3 sin(2πh/24) + γ4 cos(2πh/24), per stream intercepts. β_δ, the slope of δ on Φ, is the
    average marginal effect of Φ on P(1|0) minus that on P(1|1).
    Inference: block bootstrap (block L = 10 τ_auto) and permutation by circular shifts of Φ
    (lag > 60 s). A claim needs perm-p < 0.01 AND a 99% bootstrap interval excluding zero.
C3  shuffled Φ: one pre-drawn circular shift (> 60 s). F2: its perm-p must exceed 0.10.
Sessions: δ̂ per session regressed on mean Φ with HAC (Newey-West) errors. F3: a positive
    slope consistent with the GLM's β_δ.
Any single failure falsifies the MRE (§4.6). Robustness: thresholds at the 40th/50th/60th
percentile of the automation counts.

Declared implementation choices (see docs/MRE.md):
  * No temperature sensor, so the paper's γ1 T_t term is left out.
  * The bootstrap resamples blocks of the GLM's estimating equations (a one-step linearisation
    around the full-data fit, the same asymptotics as refitting) so thousands of replicates run
    in seconds even at the paper's 2.2 million pairs.
  * The permutation distribution uses the score statistic for β_δ under the no-Φ model, over
    every allowed circular lag at once (by FFT); it is exact for the shift null.

Reads Documents/IDA Live/mre only; never touches a live logger.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

BIN_S = 0.1
MIN_SHIFT_BINS = 600                       # 60 s
TARGET_C1_PAIRS = 2e7                      # §4.4
TARGET_C2_PAIRS = 2.2e6
KAPPA_EXAMPLE = 5e-6
Z995, Z80 = 2.5758, 0.8416
SEED = 20260926


# ------------------------------------------------------------------ loading
def load(folder: Path, tag: str = "main") -> Optional[dict]:
    folder = Path(folder)
    files = sorted(folder.glob(f"bits_{tag}_*.csv"))
    parts = []
    for p in files:
        try:
            a = np.loadtxt(p, delimiter=",", skiprows=1, ndmin=2)
        except (ValueError, OSError):
            a = _slow_load(p)
        if a.size:
            parts.append(a[:, :9])
    if not parts:
        return None
    a = np.concatenate(parts)
    a = a[np.argsort(a[:, 0], kind="stable")]
    segs = []
    sp = folder / f"segments_{tag}.csv"
    if sp.exists():
        with open(sp, newline="", encoding="utf-8") as f:
            segs = [r for r in csv.DictReader(f)]
    seg_wall = np.array([float(s["wall"]) for s in segs]) if segs else np.array([-np.inf])
    if not segs:
        segs = [{"source": "unknown", "kind": "", "streams": "2", "bits_per_bin": "0", "session": "", "task": ""}]
    si = np.clip(np.searchsorted(seg_wall, a[:, 0] + 0.02, side="right") - 1, 0, len(segs) - 1)
    names = sorted({s["source"] for s in segs})
    src = np.array([names.index(segs[i]["source"]) for i in si]) if len(a) else np.zeros(0, int)
    sessions = sorted({s["session"] for s in segs if s["session"]})
    sess = np.array([sessions.index(segs[i]["session"]) if segs[i]["session"] else -1 for i in si])
    info = {}
    for s in segs:
        info.setdefault(s["source"], {"kind": s["kind"], "streams": int(float(s["streams"] or 1)),
                                      "bits_per_bin": int(float(s["bits_per_bin"] or 0))})
    theta = None
    tp = folder / f"threshold_{tag}.json"
    if tp.exists():
        try:
            theta = json.loads(tp.read_text(encoding="utf-8"))
        except ValueError:
            theta = None
    return {"wall": a[:, 0], "cond": a[:, 1].astype(int), "clean": a[:, 2].astype(int), "phi": a[:, 3],
            "phi_raw": a[:, 4], "count": a[:, [5, 7]], "n": a[:, [6, 8]], "src": src, "sources": names,
            "info": info, "sess": sess, "sessions": sessions, "theta": theta, "tag": tag,
            "files": [p.name for p in files]}


def _slow_load(p: Path) -> np.ndarray:
    rows = []
    with open(p, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        next(r, None)
        for row in r:
            try:
                rows.append([float(v) if v not in ("", None) else np.nan for v in row[:9]])
            except ValueError:
                continue
    return np.array(rows, dtype=float).reshape(-1, 9)


# ------------------------------------------------------------------ building pairs
def _pairs(d: dict, s: int, pct: float = 50.0) -> Optional[dict]:
    """Consecutive-bin pairs of every stream of source s, thresholded at the automation median
    (or the given percentile of the automation counts)."""
    m = d["src"] == s
    idx = np.nonzero(m)[0]
    if len(idx) < 3:
        return None
    name = d["sources"][s]
    inf = d["info"].get(name, {"streams": 2, "bits_per_bin": 0})
    K = inf["bits_per_bin"]
    out = {k: [] for k in ("prev", "y", "row", "stream")}
    thetas = {}
    for k in range(min(2, inf["streams"])):
        c = d["count"][idx, k]
        valid = np.isfinite(c) & ((d["n"][idx, k] >= K) if K else True)
        c1 = valid & (d["cond"][idx] == 1)
        pool = c[c1] if c1.sum() >= 3000 else c[valid]
        if len(pool) == 0:
            continue
        th = None
        if pct == 50.0 and d["theta"] and d["theta"].get("source") == name:
            th = d["theta"]["theta"].get(str(k))
        th = float(np.percentile(pool, pct)) if th is None or pct != 50.0 else float(th)
        thetas[k] = {"theta": th, "from": "automation" if c1.sum() >= 3000 else "all bins (provisional)"}
        x = (c >= th).astype(np.int8)
        w = d["wall"][idx]
        ok = valid[:-1] & valid[1:] & (np.diff(w) > 0.03) & (np.diff(w) < 0.3)
        j = np.nonzero(ok)[0]
        out["prev"].append(x[j])
        out["y"].append(x[j + 1])
        out["row"].append(idx[j + 1])
        out["stream"].append(np.full(len(j), k, np.int8))
    if not out["y"]:
        return None
    P = {k: np.concatenate(v) for k, v in out.items()}
    order = np.argsort(P["row"], kind="stable")
    P = {k: v[order] for k, v in P.items()}
    P["theta"] = thetas
    P["source"] = name
    P["kind"] = inf.get("kind", "")
    return P


def _counts(prev, y):
    n00 = int(((prev == 0) & (y == 0)).sum()); n01 = int(((prev == 0) & (y == 1)).sum())
    n10 = int(((prev == 1) & (y == 0)).sum()); n11 = int(((prev == 1) & (y == 1)).sum())
    return n00, n01, n10, n11


def _hb(q):
    return 0.0 if q <= 0 or q >= 1 else -(q * math.log2(q) + (1 - q) * math.log2(1 - q))


def transition_stats(prev: np.ndarray, y: np.ndarray) -> dict:
    """δ̂ (eq. 6), p, q0 = P(1|0), q1 = P(0|1), Laplace-smoothed H(X_t|X_t-1) and α0 (§3.3)."""
    n00, n01, n10, n11 = _counts(prev, y)
    N = n00 + n01 + n10 + n11
    if N == 0:
        return {"pairs": 0}
    delta = (n01 + n10 - n00 - n11) / N
    q0 = (n01 + 1) / (n00 + n01 + 2)
    q1 = (n10 + 1) / (n10 + n11 + 2)
    p0 = (n00 + n01 + 1) / (N + 2)
    H = p0 * _hb(q0) + (1 - p0) * _hb(q1)
    return {"pairs": N, "p": float(y.mean()), "delta": delta, "delta_se": math.sqrt(max(1e-12, 1 - delta ** 2) / N),
            "q0": q0, "q1": q1, "H_bits_per_bin": H, "H_rate": H / BIN_S, "alpha0": BIN_S / H if H > 0 else None}


# ------------------------------------------------------------------ the transition GLM
def _design(P: dict, d: dict, phi: Optional[np.ndarray], use_phi: bool = True):
    prev = P["prev"].astype(float)
    b = (P["stream"] == 1).astype(float)
    wall = d["wall"][P["row"]]
    # p̄_block: the stream's mean over its 10-minute block, leaving the bin itself out
    blk = np.floor((wall - wall.min()) / 600.0).astype(np.int64) * 2 + P["stream"]
    _, inv, cnt = np.unique(blk, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, weights=P["y"].astype(float))
    pbar = (sums[inv] - P["y"]) / np.maximum(cnt[inv] - 1, 1)
    off = time.localtime().tm_gmtoff
    h = ((wall + off) / 3600.0) % 24.0
    cols = [1 - prev, prev, (1 - prev) * b, prev * b]
    names = ["β0(x=0)", "β0(x=1)", "stream B (x=0)", "stream B (x=1)"]
    if use_phi:
        cols += [(1 - prev) * phi, prev * phi]
        names += ["β1(x=0) per kbit/s", "β1(x=1) per kbit/s"]
    cols += [pbar - 0.5, np.sin(2 * np.pi * h / 24), np.cos(2 * np.pi * h / 24)]
    names += ["γ2 p̄_block", "γ3 sin(2πh/24)", "γ4 cos(2πh/24)"]
    X = np.column_stack(cols)
    if b.sum() == 0:            # one stream: drop the stream-B columns
        X = np.delete(X, [2, 3], axis=1)
        names = [n for i, n in enumerate(names) if i not in (2, 3)]
    return X, names


def _fit(X: np.ndarray, y: np.ndarray, iters: int = 30):
    beta = np.zeros(X.shape[1])
    for _ in range(iters):
        mu = 1 / (1 + np.exp(-np.clip(X @ beta, -30, 30)))
        g = X.T @ (y - mu)
        H = X.T @ (X * (mu * (1 - mu))[:, None]) + 1e-9 * np.eye(len(beta))
        step = np.linalg.solve(H, g)
        beta += step
        if np.abs(step).max() < 1e-10:
            break
    mu = 1 / (1 + np.exp(-np.clip(X @ beta, -30, 30)))
    H = X.T @ (X * (mu * (1 - mu))[:, None]) + 1e-9 * np.eye(len(beta))
    return beta, mu, H


def _beta_delta_grad(X, mu, prev, names):
    """β_δ = AME of Φ on P(1|0) minus AME on P(1|1), per kbit/s, and its gradient in β."""
    i0, i1 = names.index("β1(x=0) per kbit/s"), names.index("β1(x=1) per kbit/s")
    v = mu * (1 - mu)
    w0 = float(v[prev == 0].mean()) if (prev == 0).any() else 0.0
    w1 = float(v[prev == 1].mean()) if (prev == 1).any() else 0.0
    g = np.zeros(X.shape[1])
    g[i0], g[i1] = w0, -w1
    return g


def glm(P: dict, d: dict, phi: np.ndarray, blocks_L: int, boots: int = 2000, rng=None) -> dict:
    """Fit (7) and return β_δ with Wald and block-bootstrap intervals."""
    rng = rng or np.random.default_rng(SEED)
    y = P["y"].astype(float)
    X, names = _design(P, d, phi)
    beta, mu, H = _fit(X, y)
    cov = np.linalg.inv(H)
    g = _beta_delta_grad(X, mu, P["prev"], names)
    bd = float(g @ beta)
    se = float(math.sqrt(max(0.0, g @ cov @ g)))
    # block bootstrap of the estimating equations: β_b = β + H^-1 Σ_blocks (m_b - 1) U_block
    wall = d["wall"][P["row"]]
    blk = np.floor((wall - wall.min()) / (blocks_L * BIN_S)).astype(np.int64)
    _, inv = np.unique(blk, return_inverse=True)
    nb = inv.max() + 1
    U = np.zeros((nb, X.shape[1]))
    np.add.at(U, inv, X * (y - mu)[:, None])
    Hinv_g = np.linalg.solve(H, g)          # β_δ,b - β_δ = g' H^-1 Σ (m_b - 1) U_b
    ub = U @ Hinv_g
    reps = np.empty(boots)
    for r in range(boots):
        m = np.bincount(rng.integers(0, nb, nb), minlength=nb)
        reps[r] = bd + float((m - 1) @ ub)
    lo99, hi99 = np.percentile(reps, [0.5, 99.5])
    lo95, hi95 = np.percentile(reps, [2.5, 97.5])
    return {"names": names, "beta": beta.tolist(), "se": np.sqrt(np.diag(cov)).tolist(),
            "beta_delta": bd, "beta_delta_se": se, "boot_se": float(reps.std()), "ci99": [float(lo99), float(hi99)],
            "ci95": [float(lo95), float(hi95)], "blocks": int(nb), "block_bins": int(blocks_L), "mu": mu, "X": X}


def _score_residual(P: dict, d: dict) -> np.ndarray:
    """r_i = c_i (y_i - μ0_i), c = +1 after a 0 and -1 after a 1, under the no-Φ model: the
    score for β_δ. T(Φ) = Σ r_i Φ_i."""
    y = P["y"].astype(float)
    X0, _ = _design(P, d, None, use_phi=False)
    _, mu0, _ = _fit(X0, y)
    return np.where(P["prev"] == 0, 1.0, -1.0) * (y - mu0)


def perm_distribution(R_pos: np.ndarray, phi_pos: np.ndarray) -> np.ndarray:
    """T(lag) = Σ_j R[j] Φ[(j + lag) mod M] for every lag, by FFT."""
    M = len(R_pos)
    f = np.fft.rfft(R_pos[::-1], 2 * M)
    g = np.fft.rfft(np.concatenate([phi_pos, phi_pos]), 2 * M)
    full = np.fft.irfft(f * g, 2 * M)
    return full[M - 1: 2 * M - 1]


def tau_auto(x: np.ndarray, max_lag: int = 3000) -> float:
    """Integrated autocorrelation time (bins), summed to the first negative autocorrelation."""
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 20 or x.std() == 0:
        return 1.0
    x = x - x.mean()
    n = len(x)
    f = np.fft.rfft(x, 2 * n)
    ac = np.fft.irfft(f * np.conj(f))[: min(max_lag, n - 1)]
    ac = ac / ac[0]
    neg = np.nonzero(ac < 0)[0]
    stop = neg[0] if len(neg) else len(ac)
    return float(max(1.0, 1 + 2 * ac[1:stop].sum()))


def level_contrast(P: dict, d: dict, a: np.ndarray, b: np.ndarray, L: int, rng) -> dict:
    """δ̂(C2) - δ̂(C1) with a block bootstrap (blocks of L bins, resampled within each condition)."""
    sw = np.where(P["prev"] != P["y"], 1.0, -1.0)
    wall = d["wall"][P["row"]]
    out = {}
    reps = []
    parts = []
    for m in (a, b):
        blk = np.floor((wall[m] - wall[m].min()) / (L * BIN_S)).astype(np.int64)
        _, inv = np.unique(blk, return_inverse=True)
        parts.append((np.bincount(inv, weights=sw[m]), np.bincount(inv)))
    dd = [p[0].sum() / p[1].sum() for p in parts]
    for _ in range(2000):
        v = []
        for sums, ns in parts:
            mlt = np.bincount(rng.integers(0, len(ns), len(ns)), minlength=len(ns))
            v.append((mlt @ sums) / max(1, mlt @ ns))
        reps.append(v[1] - v[0])
    reps = np.array(reps)
    out.update({"delta_c1": dd[0], "delta_c2": dd[1], "diff": dd[1] - dd[0], "se": float(reps.std()),
                "ci99": [float(np.percentile(reps, 0.5)), float(np.percentile(reps, 99.5))]})
    return out


def newey_west(x: np.ndarray, y: np.ndarray) -> Optional[dict]:
    n = len(x)
    if n < 4 or np.std(x) == 0:
        return None
    X = np.column_stack([np.ones(n), x])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    e = y - X @ b
    L = int(math.floor(4 * (n / 100.0) ** (2 / 9)))
    S = (X * e[:, None]).T @ (X * e[:, None])
    for l in range(1, L + 1):
        w = 1 - l / (L + 1)
        G = (X[l:] * e[l:, None]).T @ (X[:-l] * e[:-l, None])
        S += w * (G + G.T)
    XtXi = np.linalg.inv(X.T @ X)
    V = XtXi @ S @ XtXi
    se = float(math.sqrt(max(V[1, 1], 0)))
    return {"slope": float(b[1]), "se": se, "ci95": [float(b[1] - 1.96 * se), float(b[1] + 1.96 * se)], "n": n, "lags": L}


# ------------------------------------------------------------------ the whole plan for one source
def analyse_source(d: dict, s: int, boots: int = 2000) -> Optional[dict]:
    P = _pairs(d, s)
    if P is None:
        return None
    rng = np.random.default_rng(SEED)
    cond = d["cond"][P["row"]]
    clean = d["clean"][P["row"]]
    phi_all = d["phi"][P["row"]]
    r: Dict = {"source": P["source"], "kind": P["kind"], "thresholds": P["theta"],
               "pairs": {"C1": int((cond == 1).sum()), "C2": int((cond == 2).sum()), "idle": int((cond == 0).sum())}}
    # ---- C1 automation
    c1 = cond == 1
    r["C1"] = transition_stats(P["prev"][c1], P["y"][c1])
    r["C1"]["hours"] = r["pairs"]["C1"] / 36000.0 / max(1, len(P["theta"]))
    alpha0 = r["C1"].get("alpha0") or 0.1
    delta0 = r["C1"].get("delta", 0.0) if r["C1"].get("pairs", 0) > 1000 else 0.0
    r["alpha0_used"], r["delta0_used"] = alpha0, delta0
    # ---- C2 focused attention with clean signal and a Φ value
    c2 = (cond == 2) & (clean == 1) & np.isfinite(phi_all)
    r["C2"] = transition_stats(P["prev"][c2], P["y"][c2])
    r["C2"]["dropped_unclean"] = int(((cond == 2) & ~c2).sum())
    r["C2"]["hours"] = int(c2.sum()) / 36000.0 / max(1, len(P["theta"]))
    rows_c2 = np.unique(P["row"][c2])
    r["phi"] = ({"mean": float(np.mean(d["phi"][rows_c2])), "sd": float(np.std(d["phi"][rows_c2])),
                 "min": float(np.min(d["phi"][rows_c2])), "max": float(np.max(d["phi"][rows_c2]))} if len(rows_c2) else None)
    phi_rows = d["phi"] / 1000.0                                   # kbit/s
    if c2.sum() >= 2 * MIN_SHIFT_BINS + 200 and len(rows_c2) > 2 * MIN_SHIFT_BINS:
        Pc = {k: (v[c2] if isinstance(v, np.ndarray) else v) for k, v in P.items()}
        pos = np.searchsorted(rows_c2, Pc["row"])
        R = _score_residual(Pc, d)
        R_pos = np.bincount(pos, weights=R, minlength=len(rows_c2))
        # τ_auto of the quantity the inference rests on: the score series for β_δ in time order
        # (bits that drift, or a device with memory, lengthen it; Φ's own smoothness does not)
        ph = phi_rows[rows_c2]
        tau = max(tau_auto(R_pos * (ph - ph.mean())), tau_auto(Pc["y"]))
        L = int(max(10, round(10 * tau)))
        fit = glm(Pc, d, phi_rows[Pc["row"]], L, boots, rng)
        k_scale = 1.0 / (1000.0 * 2 * alpha0 * (1 - delta0 ** 2))   # per kbit/s -> κ
        # permutation: circular shifts of Φ over the C2 bins (lag > 60 s)
        Tl = perm_distribution(R_pos, phi_rows[rows_c2])
        M = len(rows_c2)
        allowed = np.arange(MIN_SHIFT_BINS, M - MIN_SHIFT_BINS)
        T0 = float(Tl[0])
        perm_p = float((np.sum(np.abs(Tl[allowed]) >= abs(T0) - 1e-12) + 1) / (len(allowed) + 1))
        # C3: one pre-drawn shift
        lag = int(np.random.default_rng(SEED + M).choice(allowed))
        shifted = phi_rows[rows_c2][(pos + lag) % M]
        c3 = glm(Pc, d, shifted, L, boots, np.random.default_rng(SEED + 3))
        c3_p = float((np.sum(np.abs(Tl[allowed]) >= abs(Tl[lag]) - 1e-12) + 1) / (len(allowed) + 1))
        claim = perm_p < 0.01 and (fit["ci99"][0] > 0 or fit["ci99"][1] < 0)
        se_b = fit["boot_se"]
        r["glm"] = {k: v for k, v in fit.items() if k not in ("mu", "X")}
        r["glm"].update({"tau_auto_bins": tau, "perm_p": perm_p, "perm_lags": int(len(allowed)), "claim": bool(claim),
                         "kappa": fit["beta_delta"] * k_scale,
                         "kappa_ci99": [fit["ci99"][0] * k_scale, fit["ci99"][1] * k_scale],
                         "kappa_upper99": max(abs(fit["ci99"][0]), abs(fit["ci99"][1])) * k_scale,
                         "kappa_detectable": (Z995 + Z80) * se_b * k_scale})
        r["C3"] = {"lag_bins": lag, "beta_delta": c3["beta_delta"], "ci99": c3["ci99"], "perm_p": c3_p}
        # robustness: thresholds at the 40th and 60th percentiles
        rob = {}
        for pct in (40.0, 60.0):
            Q = _pairs(d, s, pct)
            if Q is None:
                continue
            q2 = (d["cond"][Q["row"]] == 2) & (d["clean"][Q["row"]] == 1) & np.isfinite(d["phi"][Q["row"]])
            if q2.sum() < 1000:
                continue
            Qc = {k: (v[q2] if isinstance(v, np.ndarray) else v) for k, v in Q.items()}
            f2 = glm(Qc, d, phi_rows[Qc["row"]], L, 400, np.random.default_rng(SEED + int(pct)))
            rob[f"{int(pct)}th"] = {"beta_delta": f2["beta_delta"], "ci99": f2["ci99"], "p": float(Qc["y"].mean())}
        rob["50th"] = {"beta_delta": fit["beta_delta"], "ci99": fit["ci99"], "p": float(Pc["y"].mean())}
        r["robustness"] = rob
        # F1: the same GLM on automation with a real Φ trace laid over it
        if r["pairs"]["C1"] > 5000:
            Pa = {k: (v[c1] if isinstance(v, np.ndarray) else v) for k, v in P.items()}
            rows_c1 = np.unique(Pa["row"])
            off = int(np.random.default_rng(SEED + 1).integers(0, M))
            trace = phi_rows[rows_c2]
            sur = trace[(np.searchsorted(rows_c1, Pa["row"]) + off) % M]
            f1 = glm(Pa, d, sur, L, boots, np.random.default_rng(SEED + 1))
            r["F1_fit"] = {"beta_delta": f1["beta_delta"], "se": f1["boot_se"], "ci99": f1["ci99"]}
    # ---- eq. (4): Δδ = δ(Φ) - δ0, focused attention against automation (the paper's power basis)
    if r["C2"].get("pairs", 0) > 1000 and r["C1"].get("pairs", 0) > 1000:
        r["contrast"] = level_contrast(P, d, c1, c2, int(r.get("glm", {}).get("block_bins", 10)), rng)
        pm = r["phi"]["mean"] if r["phi"] else None
        if pm:
            k = (math.atanh(max(-0.999, min(0.999, r["C2"]["delta"]))) - math.atanh(max(-0.999, min(0.999, r["C1"]["delta"])))) / (2 * alpha0 * pm)
            r["contrast"]["kappa"] = k
            r["contrast"]["kappa_ci99"] = [x / (2 * alpha0 * pm * max(1e-9, 1 - r["C1"]["delta"] ** 2)) for x in r["contrast"]["ci99"]]
    # ---- sessions: δ̂ per session against mean Φ, HAC errors
    sess = []
    sidx = d["sess"][P["row"]]
    for si in np.unique(sidx[c2]):
        if si < 0:
            continue
        mm = c2 & (sidx == si)
        if mm.sum() < 600:
            continue
        st = transition_stats(P["prev"][mm], P["y"][mm])
        sess.append({"session": d["sessions"][si], "pairs": st["pairs"], "delta": st["delta"], "p": st["p"],
                     "phi": float(np.mean(phi_all[mm])), "start": float(d["wall"][P["row"][mm][0]])})
    sess.sort(key=lambda z: z["start"])
    r["sessions"] = sess
    r["session_fit"] = newey_west(np.array([z["phi"] / 1000 for z in sess]), np.array([z["delta"] for z in sess])) if len(sess) >= 4 else None
    r["verdicts"] = _verdicts(r)
    return r


def _verdicts(r: dict) -> dict:
    v = {}
    g = r.get("glm")
    c1h, c2p = r["pairs"]["C1"], r["C2"].get("pairs", 0)
    # F1
    f1 = r.get("F1_fit")
    if not f1:
        v["F1"] = ("waiting", "Needs automation data (headband off, logger on) and at least one recorded session's Φ trace.")
    else:
        ok = abs(f1["beta_delta"]) < 2 * f1["se"]
        final = c1h >= TARGET_C1_PAIRS
        v["F1"] = ("passes" if ok else "fails") if final else ("on track" if ok else "warning")
        v["F1"] = (v["F1"], f"Automation slope {f1['beta_delta']:+.2e} per kbit/s, 2 SE = {2 * f1['se']:.2e}. "
                   f"{c1h:,} of {int(TARGET_C1_PAIRS):,} planned automation pairs.")
    # F2
    c3 = r.get("C3")
    if not c3:
        v["F2"] = ("waiting", "Needs at least two minutes of clean recorded sessions.")
    else:
        ok = c3["perm_p"] > 0.10
        v["F2"] = ("passes" if ok else "fails", f"Shuffled-Φ perm-p = {c3['perm_p']:.3f} (must exceed 0.10).")
    # F3
    sf = r.get("session_fit")
    if not sf or not g:
        v["F3"] = ("waiting", "Needs at least 4 sessions of a minute or more (10+ for a decision).")
    else:
        pos = sf["ci95"][0] > 0
        consistent = sf["ci95"][0] <= g["beta_delta"] <= sf["ci95"][1]
        decidable = len(r["sessions"]) >= 10 and c2p >= TARGET_C2_PAIRS
        state = "passes" if (pos and consistent) else "fails"
        v["F3"] = (state if decidable else ("on track" if pos and consistent else "not yet"),
                   f"Session slope {sf['slope']:+.2e} per kbit/s (95% {sf['ci95'][0]:+.2e} to {sf['ci95'][1]:+.2e}) "
                   f"vs the GLM's {g['beta_delta']:+.2e}; {len(r['sessions'])} sessions.")
    if g:
        v["claim"] = ("effect found", "perm-p < 0.01 and the 99% interval excludes zero.") if g["claim"] else \
            ("no effect so far", f"perm-p = {g['perm_p']:.3f}; 99% interval {g['ci99'][0]:+.2e} to {g['ci99'][1]:+.2e}.")
    else:
        v["claim"] = ("waiting", "No focused-attention data yet.")
    return v


def analyse(folder: Path, boots: int = 2000) -> dict:
    out = {"made": time.strftime("%Y-%m-%d %H:%M"), "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16],
           "arms": {}}
    for tag in ("main", "control"):
        d = load(folder, tag)
        if d is None:
            continue
        per = []
        for s in range(len(d["sources"])):
            try:
                a = analyse_source(d, s, boots)
            except Exception as exc:          # one bad source must not hide the others
                a = {"source": d["sources"][s], "error": str(exc)}
            if a:
                per.append(a)
        per.sort(key=lambda a: -(a.get("pairs", {}).get("C1", 0) + a.get("pairs", {}).get("C2", 0)))
        out["arms"][tag] = per
    return out


# ------------------------------------------------------------------ report
def _e(x) -> str:
    return html.escape(str(x))


def _g(v, fmt="{:+.2e}"):
    return "–" if v is None else fmt.format(v)


def _bar(frac: float) -> str:
    f = max(0.0, min(1.0, frac))
    return f"<div class='bar'><i style='width:{100 * f:.1f}%'></i></div>"


def source_html(a: dict, arm: str) -> str:
    if a.get("error"):
        return f"<section class='card'><h3>{_e(a['source'])}</h3><p>Analysis failed: {_e(a['error'])}</p></section>"
    c1, c2, g, v = a["C1"], a["C2"], a.get("glm"), a["verdicts"]
    badge = {"passes": "up", "on track": "up", "effect found": "up", "fails": "down", "warning": "down"}
    ver = "".join(f"<li><b class='{badge.get(v[k][0], '')}'>{k if k != 'claim' else 'Verdict'}: {v[k][0]}</b> "
                  f"<span class='fine'>{_e(v[k][1])}</span></li>" for k in ("claim", "F1", "F2", "F3"))
    c1p, c2p = a["pairs"]["C1"], a["pairs"]["C2"]
    th = ", ".join(f"stream {'AB'[int(k)]}: {t['theta']:.1f} ({t['from']})" for k, t in a["thresholds"].items())
    rows = ""
    if g:
        rows = "".join(f"<tr><td>{_e(n)}</td><td>{b:+.4f}</td><td>{s:.4f}</td></tr>" for n, b, s in zip(g["names"], g["beta"], g["se"]))
    rob = "".join(f"<tr><td>{k}</td><td>{x['p']:.3f}</td><td>{_g(x['beta_delta'])}</td><td>{_g(x['ci99'][0])} to {_g(x['ci99'][1])}</td></tr>"
                  for k, x in sorted((a.get("robustness") or {}).items()))
    sess = "".join(f"<tr><td>{_e(z['session'])}</td><td>{z['pairs']:,}</td><td>{z['phi']:.0f}</td><td>{z['delta']:+.4f}</td><td>{z['p']:.3f}</td></tr>"
                   for z in a["sessions"][-40:])
    phi = a.get("phi")
    kd = g and g["kappa_detectable"]
    power = ""
    if g:
        pred = math.tanh(math.atanh(max(-0.99, min(0.99, a["delta0_used"]))) + 2 * a["alpha0_used"] * KAPPA_EXAMPLE * (phi["mean"] if phi else 1500)) - a["delta0_used"]
        power = (f"<p>With the data so far the test could detect κ ≥ <b>{kd:.1e}</b> (99% two-sided, 80% power). "
                 f"The paper expects κ between 10⁻⁶ and 10⁻⁵; at its example κ = 5×10⁻⁶ and your mean Φ the predicted shift is "
                 f"Δδ ≈ {pred:+.1e}.</p>")
    ct = a.get("contrast")
    contrast = (f"<p>Equation (4), focused attention against automation: Δδ = δ(C2) − δ0 = <b>{ct['diff']:+.2e}</b> "
                f"(99% {ct['ci99'][0]:+.2e} to {ct['ci99'][1]:+.2e}), κ from it = {_g(ct.get('kappa'))}. "
                f"This is the comparison the paper's power figures use; it is more sensitive than the slope within sessions but "
                f"can also pick up anything else that differs between automation and sessions (time of day, the room), "
                f"which is what the control arm is for. The claim rule stays with the GLM.</p>") if ct else ""
    return f"""<section class="card">
  <h3>{_e(a['source'])} <span class="fine">· {_e(a['kind'])} · {arm} arm</span></h3>
  <ul class="v">{ver}</ul>
  <div class="grid2">
    <div class="stat"><span class="fine">Automation (C1)</span><b>{c1.get('hours', 0):.1f} h</b>{_bar(c1p / TARGET_C1_PAIRS)}<span class="fine">{c1p:,} of 20,000,000 pairs</span></div>
    <div class="stat"><span class="fine">Focused attention (C2, clean)</span><b>{c2.get('hours', 0):.1f} h</b>{_bar(c2.get('pairs', 0) / TARGET_C2_PAIRS)}<span class="fine">{c2.get('pairs', 0):,} of 2,200,000 pairs · {c2.get('dropped_unclean', 0):,} unclean left out</span></div>
    <div class="stat"><span class="fine">Baseline δ0 (C1)</span><b>{_g(c1.get('delta'), '{:+.4f}')}</b><span class="fine">± {_g(c1.get('delta_se'), '{:.4f}')} · p = {_g(c1.get('p'), '{:.4f}')}</span></div>
    <div class="stat"><span class="fine">Device transfer α0</span><b>{_g(c1.get('alpha0'), '{:.4f}')} s/bit</b><span class="fine">H = {_g(c1.get('H_bits_per_bin'), '{:.5f}')} bit per bin</span></div>
    <div class="stat"><span class="fine">Your Φ in sessions (CTW)</span><b>{_g(phi and phi['mean'], '{:.0f}')} bit/s</b><span class="fine">sd {_g(phi and phi['sd'], '{:.0f}')}, range {_g(phi and phi['min'], '{:.0f}')}–{_g(phi and phi['max'], '{:.0f}')}</span></div>
    <div class="stat"><span class="fine">Slope of δ on Φ (β_δ)</span><b>{_g(g and g['beta_delta'])}</b><span class="fine">per kbit/s · 99% {_g(g and g['ci99'][0])} to {_g(g and g['ci99'][1])}</span></div>
    <div class="stat"><span class="fine">Coupling κ</span><b>{_g(g and g['kappa'])}</b><span class="fine">99% {_g(g and g['kappa_ci99'][0])} to {_g(g and g['kappa_ci99'][1])}</span></div>
    <div class="stat"><span class="fine">Permutation (circular shifts &gt; 60 s)</span><b>p = {_g(g and g['perm_p'], '{:.2g}')}</b><span class="fine">{_g(g and g['perm_lags'], '{:,}')} lags · blocks of {_g(g and g['block_bins'], '{:,}')} bins</span></div>
  </div>
  {contrast}
  {power}
  <p class="fine">Thresholds (events per bin): {_e(th)}.</p>
  {"<details><summary>Transition GLM coefficients</summary><table><tr><th>Term</th><th>Estimate</th><th>SE</th></tr>" + rows + "</table></details>" if rows else ""}
  {"<details><summary>Robustness: threshold at the 40th / 50th / 60th percentile</summary><table><tr><th>Threshold</th><th>p</th><th>β_δ</th><th>99% interval</th></tr>" + rob + "</table></details>" if rob else ""}
  {"<details><summary>Sessions</summary><table><tr><th>Session</th><th>Pairs</th><th>Mean Φ</th><th>δ̂</th><th>p</th></tr>" + sess + "</table></details>" if sess else ""}
</section>"""


def report_html(res: dict) -> str:
    from .levels import page
    arms = res.get("arms", {})
    if not arms:
        body = ("<h1>Murray Reality Equation test</h1><p class='sub'>No random-bit data yet. Open the drawer, MRE tab, "
                "choose a source and leave it logging. Automation (headband off) comes first: the paper wants two weeks.</p>")
        return page("MRE test", body)
    cards = "".join(source_html(a, tag) for tag in ("main", "control") for a in arms.get(tag, []))
    body = f"""<style>.bar{{height:6px;background:rgba(127,127,127,.25);border-radius:3px;overflow:hidden;margin:6px 0}}
.bar i{{display:block;height:100%;background:#5fb3ff}} details{{margin-top:10px}} summary{{cursor:pointer}}</style>
<h1>Murray Reality Equation test</h1>
<p class="sub">Does the alternation bias of a random-bit stream rise with your information rate Φ, as
δ(Φ) = tanh(atanh δ0 + 2α0κΦ) predicts? Analysed exactly as the paper's plan (history/R15 §4) · made {_e(res['made'])} ·
analysis code {_e(res['code_sha256'])}.</p>
<div class="card"><p>How to read this. <b>Effect</b> is claimed only when the permutation p is below 0.01 <i>and</i> the 99%
bootstrap interval excludes zero. <b>F1</b>: automation must show no slope. <b>F2</b>: a shuffled Φ must show nothing.
<b>F3</b>: sessions with higher Φ must show higher δ, consistent with the fit. The paper counts any single failure as
falsifying the MRE; a null result gives an upper bound on κ. The <b>control</b> arm (the online ANU generator,
produced before you see it) should show nothing whatever the main arm does: an effect in both points to an artefact.</p></div>
{cards}"""
    return page("MRE test", body)


def build_report(folder: Path, boots: int = 2000) -> str:
    res = analyse(Path(folder), boots)
    out = Path(folder)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(_jsonable(res), indent=1), encoding="utf-8")
    text = report_html(res)
    (out / "report.html").write_text(text, encoding="utf-8")
    return text


def _jsonable(o):
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    return o
