"""Light trials: does switching the headband's own infrared optics on change the state map?

Design (follows the IDA discovery protocol's rules):
* Randomized: each trial is "active" or "sham", balanced in permuted blocks.
* Blinded: the allocation is written to a sealed file whose SHA-256 is logged at
  the start; the screen never shows which arm a trial is in until you reveal it.
* Matched sham: both arms send the identical command sequence at identical times
  (halt, preset, start, start, low-latency). Active trials switch to the dose
  preset and back; sham trials re-send the baseline preset twice. So both arms get
  the same stream gaps; the only intended difference is whether the optics emit.
* Phases: "nothing" is all sham (the null run, including the sponge bench test),
  "small" uses p1035 (inner 850 nm IR + 730 nm near-IR only), "larger" uses p1041
  (all optics including 660 nm red).
* Outcome windows exclude a few seconds after each switch command, because
  switching LED drivers can put an electrical step into the frontal electrodes.

Unknowns this protocol cannot settle by itself (see docs/IR_PROTOCOL.md):
whether the firmware's preset actually gates the emitters, whether the dose is
visible to you (730 nm and 660 nm can be faintly visible), and whether any effect
is optical rather than electrical. The bench tests address those.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import secrets
from pathlib import Path
from typing import Awaitable, Callable, List, Optional

import numpy as np

from ..core import now

PHASES = ("nothing", "small", "larger")


def make_allocation(n_trials: int, block_size: int, rng: np.random.Generator, phase: str) -> List[str]:
    if phase == "nothing":
        return ["sham"] * n_trials
    if block_size % 2:
        raise ValueError("block size must be even so each block is balanced")
    arms: List[str] = []
    while len(arms) < n_trials:
        block = ["active"] * (block_size // 2) + ["sham"] * (block_size // 2)
        rng.shuffle(block)
        arms.extend(block)
    return arms[:n_trials]


class LightTrialProtocol:
    def __init__(
        self,
        settings: dict,
        phase: str,
        source,
        folder: Path,
        emit: Callable[[str, dict], None],
        ask_guess: Callable[[int], Awaitable[Optional[str]]],
        mark_event: Callable[[str], None],
        bench: bool = False,
    ):
        if phase not in PHASES:
            raise ValueError(f"phase must be one of {PHASES}")
        if not getattr(source, "can_set_preset", False):
            raise RuntimeError("This source cannot switch the headband optics. Connect the headband directly.")
        self.cfg = settings["ir_protocol"]
        self.phase = phase
        self.source = source
        self.folder = folder
        self.emit = emit
        self.ask_guess = ask_guess
        self.mark_event = mark_event
        self.bench = bench
        self.baseline = self.cfg["baseline_preset"]
        self.dose = self.cfg["dose_presets"][phase] or self.baseline
        self.burst = float(self.cfg["burst_s"][phase])
        if self.burst > float(self.cfg["max_burst_s"]):
            raise ValueError("burst longer than the configured maximum")
        seed = secrets.randbits(64)
        self.rng = np.random.default_rng(seed)
        self.arms = make_allocation(int(self.cfg["trials"]), int(self.cfg["block_size"]), self.rng, phase)
        self.sealed = {
            "phase": phase, "dose_preset": self.dose, "baseline_preset": self.baseline,
            "burst_s": self.burst, "arms": self.arms, "seed": f"{seed:016x}", "bench": bench,
        }
        blob = json.dumps(self.sealed, sort_keys=True).encode()
        self.digest = hashlib.sha256(blob).hexdigest()
        with open(folder / "allocation.sealed.json", "wb") as f:
            f.write(blob)
        self.current = 0
        self.cancelled = False
        self.state = "ready"

    def public(self) -> dict:
        return {"phase": self.phase, "trials": len(self.arms), "current": self.current,
                "state": self.state, "sealed_sha256": self.digest, "bench": self.bench}

    async def _wait(self, seconds: float) -> None:
        end = now() + seconds
        while now() < end and not self.cancelled:
            await asyncio.sleep(min(0.2, end - now()))

    async def run(self) -> None:
        cfg = self.cfg
        self.emit("light_protocol_start", {**self.public(), "n_trials": len(self.arms)})
        self.state = "settling"
        t = await self.source.set_preset(self.baseline)
        self.emit("switch", {"trial": 0, "which": "settle", "t_cmd": t})
        await self._wait(10.0)
        for i, arm in enumerate(self.arms, start=1):
            if self.cancelled:
                break
            self.current = i
            self.state = "baseline"
            self.emit("trial_start", {"trial": i, "t": now()})
            await self._wait(float(cfg["pre_s"]))
            self.state = "switch"
            on_preset = self.dose if arm == "active" else self.baseline
            t_on = await self.source.set_preset(on_preset)
            self.emit("switch", {"trial": i, "which": "on", "t_cmd": t_on})
            self.mark_event("switch")
            await self._wait(self.burst)
            t_off = await self.source.set_preset(self.baseline)
            self.emit("switch", {"trial": i, "which": "off", "t_cmd": t_off})
            self.mark_event("switch")
            self.state = "after"
            await self._wait(float(cfg["post_s"]))
            guess = await self.ask_guess(i) if cfg.get("ask_guess", True) and not self.bench else None
            self.emit("trial_end", {"trial": i, "t": now(), "guess": guess})
            lo, hi = cfg["iti_jitter_s"]
            self.state = "rest"
            await self._wait(float(self.rng.uniform(lo, hi)))
        self.state = "done" if not self.cancelled else "stopped"
        self.emit("light_protocol_end", {"completed": self.current, "state": self.state})

    def reveal(self) -> dict:
        if self.state not in ("done", "stopped"):
            raise RuntimeError("Finish or stop the trials before revealing the allocation.")
        with open(self.folder / "allocation.sealed.json", "rb") as f:
            blob = f.read()
        if hashlib.sha256(blob).hexdigest() != self.digest:
            raise RuntimeError("The sealed allocation file was changed after the trials started.")
        return json.loads(blob)
