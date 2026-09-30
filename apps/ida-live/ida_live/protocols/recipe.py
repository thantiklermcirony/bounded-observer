"""Recipes: stimulation rules you (or Claude) write as JSON, run live, and test honestly.

A recipe says WHEN to fire (a condition on your live state, or a schedule), WHAT to
fire (a pattern for an actuator), and HOW it is controlled. Example:

{
  "name": "alpha dip lift",
  "description": "When alpha behind the ears dips, fire a gentle 10 Hz burst.",
  "actuator": "external_led",
  "pattern": {"type": "burst", "pulse_hz": 10, "duty": 0.3, "duration_s": 2, "intensity": 0.2},
  "trigger": {"when": "clean and z_alpha_tp < -1.0", "hold_s": 3, "refractory_s": 30},
  "randomize": 0.5,
  "outcome": {"pre_s": 5, "post_s": 20, "exclude_s": 2, "measures": ["d", "z_alpha_tp"]},
  "limits": {"max_fires": 30, "max_minutes": 30}
}

Why every trigger is randomized to real or sham (randomize = chance of real):
a trigger fires when you are at an extreme ("alpha has dipped"). From an extreme,
signals drift back toward normal on their own, which is regression to the mean.
Without sham triggers, "fire when alpha dips, then alpha rises" would look like
success every time even if the light did nothing. Sham triggers happen in the
same states at the same moments, so real minus sham is the light's own effect.
randomize = 1.0 is allowed for exploration but the report marks it uncontrolled.

Variables a condition can use: clean, d, x, y, angle, drift_d, z_<feature> for
map features, any feature name (alpha_tp, theta_af, beta, aperiodic, emg_tp,
alpha_theta, heart_bpm, ...), minutes (since session start).
Operators: and, or, not, < <= > >= == !=, + - * /, abs(), min(), max().
"""

from __future__ import annotations

import ast
import hashlib
import json
import operator
import secrets
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import numpy as np

from ..actuators import make, normalize, summary
from ..core import now

_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}
_CMP = {ast.Lt: operator.lt, ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge,
        ast.Eq: operator.eq, ast.NotEq: operator.ne}
_FUNCS = {"abs": abs, "min": min, "max": max}


class Missing(Exception):
    pass


class Condition:
    """A small, safe expression language. No Python eval; only the nodes listed here."""

    def __init__(self, text: str):
        self.text = text
        self.tree = ast.parse(text, mode="eval")
        self.names = sorted({n.id for n in ast.walk(self.tree) if isinstance(n, ast.Name)} - set(_FUNCS))
        self._check(self.tree.body)

    def _check(self, node) -> None:
        ok = (ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.USub, ast.Compare, ast.Name,
              ast.Constant, ast.BinOp, ast.Call, ast.Load, *_BIN, *_CMP)
        for n in ast.walk(node):
            if not isinstance(n, ok):
                raise ValueError(f"'{self.text}': {type(n).__name__} is not allowed in a condition")
            if isinstance(n, ast.Call) and not (isinstance(n.func, ast.Name) and n.func.id in _FUNCS):
                raise ValueError(f"'{self.text}': only abs(), min() and max() may be called")

    def __call__(self, env: Dict[str, Any]) -> bool:
        try:
            return bool(self._eval(self.tree.body, env))
        except Missing:
            return False

    def _eval(self, n, env):
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.Name):
            if n.id not in env or env[n.id] is None:
                raise Missing(n.id)
            return env[n.id]
        if isinstance(n, ast.BoolOp):
            vals = (self._eval(v, env) for v in n.values)
            return all(vals) if isinstance(n.op, ast.And) else any(vals)
        if isinstance(n, ast.UnaryOp):
            v = self._eval(n.operand, env)
            return (not v) if isinstance(n.op, ast.Not) else -v
        if isinstance(n, ast.BinOp):
            return _BIN[type(n.op)](self._eval(n.left, env), self._eval(n.right, env))
        if isinstance(n, ast.Compare):
            left = self._eval(n.left, env)
            for op, right_n in zip(n.ops, n.comparators):
                right = self._eval(right_n, env)
                if not _CMP[type(op)](left, right):
                    return False
                left = right
            return True
        if isinstance(n, ast.Call):
            return _FUNCS[n.func.id](*[self._eval(a, env) for a in n.args])
        raise ValueError(type(n).__name__)


DEFAULT_OUTCOME = {"pre_s": 5.0, "post_s": 20.0, "exclude_s": 2.0, "measures": ["d"]}
DEFAULT_LIMITS = {"max_fires": 30, "max_minutes": 30}


def validate(recipe: dict) -> dict:
    """Check a recipe and fill defaults. Raises ValueError with a plain explanation."""
    r = json.loads(json.dumps(recipe))
    for key in ("name", "actuator", "pattern", "trigger"):
        if key not in r:
            raise ValueError(f"recipe is missing '{key}'")
    normalize(r["pattern"])
    trig = r["trigger"]
    if "when" in trig:
        Condition(trig["when"])
        trig.setdefault("hold_s", 0.0)
        trig.setdefault("refractory_s", 20.0)
    elif "every_s" not in trig:
        raise ValueError("trigger needs either 'when' (a condition) or 'every_s' ([min, max] seconds)")
    r.setdefault("randomize", 0.5)
    if not (0.0 < float(r["randomize"]) <= 1.0):
        raise ValueError("randomize is the chance a trigger is real: between 0 (exclusive) and 1")
    r["outcome"] = {**DEFAULT_OUTCOME, **r.get("outcome", {})}
    r["limits"] = {**DEFAULT_LIMITS, **r.get("limits", {})}
    return r


def load_folder(folder: Path) -> Dict[str, dict]:
    out = {}
    for p in sorted(folder.glob("*.json")):
        try:
            with open(p, encoding="utf-8") as f:
                r = validate(json.load(f))
            out[r["name"]] = {**r, "_file": p.name}
        except Exception as exc:
            out[p.stem] = {"name": p.stem, "_error": str(exc), "_file": p.name}
    return out


def allocation(n: int, p: float, rng: np.random.Generator) -> List[str]:
    if p >= 1.0:
        return ["active"] * n
    if abs(p - 0.5) < 1e-9:
        arms: List[str] = []
        while len(arms) < n:
            block = ["active", "active", "sham", "sham"]
            rng.shuffle(block)
            arms.extend(block)
        return arms[:n]
    return ["active" if rng.random() < p else "sham" for _ in range(n)]


class RecipeRunner:
    def __init__(self, engine, recipe: dict, folder: Path, emit: Callable[[str, dict], None],
                 bench: bool = False, covered: bool = False):
        self.engine = engine
        self.r = validate(recipe)
        self.emit = emit
        self.bench, self.covered = bench, covered
        self.actuator = make(engine, self.r["actuator"])
        self.segs = self.actuator.check(self.r["pattern"])
        self.cond = Condition(self.r["trigger"]["when"]) if "when" in self.r["trigger"] else None
        seed = secrets.randbits(64)
        self.rng = np.random.default_rng(seed)
        n = int(self.r["limits"]["max_fires"])
        self.arms = allocation(n, float(self.r["randomize"]), self.rng)
        self.run_id = f"{now():.3f}"
        sealed = {"recipe": self.r, "arms": self.arms, "seed": f"{seed:016x}", "bench": bench, "covered": covered}
        blob = json.dumps(sealed, sort_keys=True).encode()
        self.digest = hashlib.sha256(blob).hexdigest()
        self.sealed_path = folder / f"allocation.recipe-{self.run_id}.sealed.json"
        with open(self.sealed_path, "wb") as f:
            f.write(blob)
        self.fired = 0
        self.state = "ready"
        self.cancelled = False
        self._true_since: Optional[float] = None
        self._busy = False
        self._last_end: float = -1e9
        self._next_scheduled: Optional[float] = None
        self._t_start: Optional[float] = None

    def public(self) -> dict:
        return {"name": self.r["name"], "run_id": self.run_id, "state": self.state, "fired": self.fired,
                "max_fires": len(self.arms), "sealed_sha256": self.digest, "bench": self.bench,
                "covered": self.covered, "pattern": summary(self.segs), "actuator": self.r["actuator"]}

    async def start(self) -> None:
        await self.actuator.open()
        self._t_start = now()
        self.state = "watching"
        if "every_s" in self.r["trigger"]:
            self._schedule_next(self._t_start)
        self.emit("recipe_start", {**self.public(), "recipe": self.r, "t": self._t_start})

    def _schedule_next(self, t: float) -> None:
        lo, hi = self.r["trigger"]["every_s"]
        self._next_scheduled = t + float(self.rng.uniform(lo, hi))

    def env(self, t: float, st: dict, vals: dict) -> Dict[str, Any]:
        e: Dict[str, Any] = dict(vals)
        for k in ("clean", "d", "x", "y", "angle", "drift_d"):
            if k in st:
                e[k] = st[k]
        for k, v in (st.get("z") or {}).items():
            e[f"z_{k}"] = v
        if self._t_start is not None:
            e["minutes"] = (t - self._t_start) / 60.0
        return e

    def on_tick(self, t: float, st: dict, vals: dict) -> None:
        if self.state not in ("watching",) or self.cancelled or self._busy:
            return
        lim = self.r["limits"]
        if self.fired >= len(self.arms) or (t - self._t_start) / 60.0 >= float(lim["max_minutes"]):
            self.state = "done"
            self.emit("recipe_end", {"run_id": self.run_id, "fired": self.fired, "state": self.state})
            return
        trig = self.r["trigger"]
        if self.cond is not None:
            if t - self._last_end < float(trig["refractory_s"]):
                self._true_since = None
                return
            env = self.env(t, st, vals)
            if self.cond(env):
                self._true_since = self._true_since or t
                if t - self._true_since >= float(trig["hold_s"]):
                    values = {k: env.get(k) for k in self.cond.names}
                    self._fire(t, values)
            else:
                self._true_since = None
        elif self._next_scheduled is not None and t >= self._next_scheduled:
            self._fire(t, {})

    def _fire(self, t: float, values: dict) -> None:
        import asyncio

        arm = self.arms[self.fired]
        self.fired += 1
        n = self.fired
        self._busy = True
        self._true_since = None
        self.emit("trigger", {"run_id": self.run_id, "n": n, "t": t, "values": values})
        self.engine.state_engine.returns.mark(t, "trigger")

        async def go():
            try:
                res = await self.actuator.fire(self.segs, sham=(arm == "sham"))
                self.emit("fire_done", {"run_id": self.run_id, "n": n, "t": now(),
                                        "t_start": res["t_start"], "t_end": res["t_end"],
                                        "switch_times": res.get("switch_times", [])})
            except Exception as exc:
                self.emit("fire_failed", {"run_id": self.run_id, "n": n, "error": str(exc)})
                self.state = "stopped"
                self.engine.log(f"Recipe stopped: {exc}")
            finally:
                self._busy = False
                self._last_end = now()
                if "every_s" in self.r["trigger"]:
                    self._schedule_next(self._last_end)
                self.engine.push_status()

        self.engine._tasks.append(asyncio.ensure_future(go()))

    def stop(self) -> None:
        self.cancelled = True
        if self.state == "watching":
            self.state = "stopped"
            self.emit("recipe_end", {"run_id": self.run_id, "fired": self.fired, "state": self.state})

    def reveal(self) -> dict:
        if self.state not in ("done", "stopped"):
            raise RuntimeError("Stop the recipe before revealing which triggers were real.")
        blob = self.sealed_path.read_bytes()
        if hashlib.sha256(blob).hexdigest() != self.digest:
            raise RuntimeError("The sealed allocation file was changed after the recipe started.")
        d = json.loads(blob)
        d["arms"] = d["arms"][: self.fired]
        return d
