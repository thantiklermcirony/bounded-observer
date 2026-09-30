"""Loading saved sessions for analysis. Analyses read files only; they never touch a live session."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np


class Table:
    """Minimal column store for a CSV written by the recorder."""

    def __init__(self, path: Path):
        self.cols: Dict[str, np.ndarray] = {}
        if not path.exists():
            self.n = 0
            return
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.n = len(rows)
        if not rows:
            return
        for k in rows[0].keys():
            vals = [r.get(k, "") for r in rows]
            try:
                self.cols[k] = np.array([float(v) if v not in ("", None) else np.nan for v in vals])
            except ValueError:
                self.cols[k] = np.array(vals, dtype=object)

    def __getitem__(self, k: str) -> np.ndarray:
        return self.cols[k]

    def has(self, k: str) -> bool:
        return k in self.cols

    def window(self, t0: float, t1: float, mask: Optional[np.ndarray] = None) -> np.ndarray:
        if self.n == 0:
            return np.zeros(0, dtype=bool)
        m = (self.cols["t"] >= t0) & (self.cols["t"] < t1)
        return m & mask if mask is not None else m


class Session:
    def __init__(self, folder: Path):
        self.folder = folder
        self.name = folder.name
        with open(folder / "manifest.json", encoding="utf-8") as f:
            self.manifest = json.load(f)
        self.events: List[dict] = []
        ev = folder / "events.jsonl"
        if ev.exists():
            with open(ev, encoding="utf-8") as f:
                self.events = [json.loads(line) for line in f if line.strip()]
        self.state = Table(folder / "state.csv")
        self.features = Table(folder / "features.csv")
        self.t_start = next((e["t"] for e in self.events if e["kind"] == "session_start"), self.manifest.get("t0", 0.0))

    def of(self, kind: str) -> List[dict]:
        return [e for e in self.events if e["kind"] == kind]

    @property
    def settings(self) -> dict:
        return self.manifest.get("settings", {})


def find_sessions(root: Path) -> List[Session]:
    out = []
    for p in sorted(root.glob("*/manifest.json")):
        try:
            out.append(Session(p.parent))
        except Exception as exc:  # unreadable session: report and skip
            print(f"Skipping {p.parent.name}: {exc}")
    return out


def auc(y: np.ndarray, score: np.ndarray) -> float:
    """Area under the ROC curve via ranks (ties averaged)."""
    y = np.asarray(y).astype(bool)
    n1, n0 = int(y.sum()), int((~y).sum())
    if n1 == 0 or n0 == 0:
        return float("nan")
    order = np.argsort(score)
    ranks = np.empty(len(score))
    s = np.asarray(score)[order]
    i = 0
    r = np.arange(1, len(s) + 1, dtype=float)
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        r[i:j + 1] = (i + j + 2) / 2.0
        i = j + 1
    ranks[order] = r
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def fit_logistic(X: np.ndarray, y: np.ndarray, lam: float = 1.0, iters: int = 50) -> tuple:
    """Ridge-penalised logistic regression by Newton steps; intercept unpenalised."""
    mu, sd = X.mean(axis=0), X.std(axis=0)
    sd[sd < 1e-9] = 1.0
    Z = np.column_stack([np.ones(len(X)), (X - mu) / sd])
    w = np.zeros(Z.shape[1])
    P = lam * np.eye(Z.shape[1])
    P[0, 0] = 0.0
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-np.clip(Z @ w, -30, 30)))
        g = Z.T @ (p - y) + P @ w
        H = Z.T @ (Z * (p * (1 - p))[:, None]) + P + 1e-9 * np.eye(len(w))
        step = np.linalg.solve(H, g)
        w -= step
        if np.abs(step).max() < 1e-8:
            break
    return w, mu, sd


def predict_logistic(model: tuple, X: np.ndarray) -> np.ndarray:
    w, mu, sd = model
    Z = np.column_stack([np.ones(len(X)), (X - mu) / sd])
    return 1.0 / (1.0 + np.exp(-np.clip(Z @ w, -30, 30)))


def binom_two_sided(k: int, n: int) -> float:
    """Exact two-sided binomial test against p = 0.5."""
    if n == 0:
        return float("nan")
    probs = [math.comb(n, i) * 0.5 ** n for i in range(n + 1)]
    pk = probs[k]
    return float(min(1.0, sum(p for p in probs if p <= pk + 1e-15)))
