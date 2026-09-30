"""A synthetic Muse S Athena for developing and testing without the headband.

What it models, and why:
* a hidden attention state that switches between "aware" and "drifting", so the
  probe answers and the calibration gate have a known truth to be tested against;
* blinks, jaw-muscle bursts and head movement, so artifact handling is exercised;
* preset switching with the same stream gap for every switch, plus an electrical
  step on the frontal channels only when the optics actually turn on or off.
  That step is the confound the light-trial analysis must survive: in the default
  simulator the light has NO effect on the brain, only on the electronics.
* an optional injected effect (settings.simulator.ir_effect) so we can check the
  analysis can find a real effect when there is one.

Nothing here is a model of real physiology; the numbers are chosen to look
roughly like a forehead headband and to make failure modes visible.
"""

from __future__ import annotations

import asyncio
import math
from typing import Optional

import numpy as np

from ..core import Chunk, STREAM_RATES, now
from .base import Source, register

MAIN_EEG = ["EEG_TP9", "EEG_AF7", "EEG_AF8", "EEG_TP10"]
OPTICS4 = ["OPTICS_LI_NIR", "OPTICS_RI_NIR", "OPTICS_LI_IR", "OPTICS_RI_IR"]
OPTICS16 = [
    "OPTICS_LO_NIR", "OPTICS_RO_NIR", "OPTICS_LO_IR", "OPTICS_RO_IR",
    "OPTICS_LI_NIR", "OPTICS_RI_NIR", "OPTICS_LI_IR", "OPTICS_RI_IR",
    "OPTICS_LO_RED", "OPTICS_RO_RED", "OPTICS_LO_AMB", "OPTICS_RO_AMB",
    "OPTICS_LI_RED", "OPTICS_RI_RED", "OPTICS_LI_AMB", "OPTICS_RI_AMB",
]
PRESET_OPTICS = {"p20": 0, "p21": 0, "p50": 0, "p51": 0, "p60": 0, "p61": 0,
                 "p1035": 4, "p1045": 4, "p1046": 4, "p4129": 4, "p1034": 8,
                 "p1043": 8, "p1044": 8, "p1041": 16, "p1042": 16}


@register("sim")
class SimulatorSource(Source):
    can_set_preset = True

    def __init__(self, settings, on_chunk, on_log, preset: Optional[str] = None):
        super().__init__(settings, on_chunk, on_log)
        sim = settings["simulator"]
        self.rng = np.random.default_rng(sim.get("seed"))
        self.preset = preset or settings["device"]["monitor_preset"]
        self.artifact_uv = float(sim.get("switch_artifact_uv", 80.0))
        self.ir_effect = float(sim.get("ir_effect", 0.0))
        self._task: Optional[asyncio.Task] = None
        self._t_last = 0.0
        self._frac = {k: 0.0 for k in STREAM_RATES}
        self._phase = {"alpha": 0.0, "theta": 0.0, "beta": 0.0, "heart": 0.0, "resp": 0.0}
        self._ar = np.zeros(4)
        self.aware = True
        self._next_state_flip = 0.0
        self._gap_until = 0.0
        self._switch_steps: list = []   # (time, amplitude) electrical steps
        self._blinks: list = []
        self._emg_until = 0.0
        self._move_until = 0.0
        self._effect_until = 0.0
        self._next = {"blink": 0.0, "emg": 0.0, "move": 0.0}
        self._light: list = []  # (t_start, on/off edges array, intensity) from sim_led

    def inject_light(self, t0: float, segs: list, sham: bool) -> None:
        """Called by the sim_led actuator. Light pulses put a small electrical square wave
        on the forehead channels (at the pulse rate!) and, only if ir_effect > 0, raise alpha."""
        edges, t = [], t0
        for on_ms, off_ms, inten in segs:
            edges.append((t, t + on_ms / 1000.0, 0.0 if sham else inten))
            t += (on_ms + off_ms) / 1000.0
        self._light.append(edges)
        if not sham and self.ir_effect:
            self._effect_until = t + 20.0

    # hidden truth, exposed only for automated tests of the probe and gate pipeline
    def hidden_state(self) -> str:
        return "aware" if self.aware else "drifting"

    async def start(self) -> None:
        t = now()
        self._t_last = t
        self._next_state_flip = t + self.rng.exponential(50.0)
        for k, m in (("blink", 5.0), ("emg", 40.0), ("move", 60.0)):
            self._next[k] = t + self.rng.exponential(m)
        self.connected = True
        self.info = {"name": "Simulated Athena"}
        self._task = asyncio.create_task(self._run())
        self.log(f"Simulator running with preset {self.preset}.")

    async def stop(self) -> None:
        self.connected = False
        if self._task:
            self._task.cancel()

    async def set_preset(self, preset: str) -> float:
        t0 = now()
        before = PRESET_OPTICS.get(self.preset, 0) > 0
        after = PRESET_OPTICS.get(preset, 0) > 0
        self._gap_until = t0 + 0.55  # same stream gap for every switch
        if before != after:
            sign = 1.0 if after else -1.0
            self._switch_steps.append((t0 + 0.55, sign * self.artifact_uv))
        if after and not before and self.ir_effect:
            # injected brain effect for power checks: alpha rises while the light is on
            self._effect_until = float("inf")
        if before and not after and self.ir_effect:
            self._effect_until = t0 + 20.0
        await asyncio.sleep(0.4)
        self.preset = preset
        return t0

    async def _run(self) -> None:
        while self.connected:
            await asyncio.sleep(0.05)
            t = now()
            self._advance_events(t)
            if t < self._gap_until:
                self._t_last = t
                continue
            for stream, rate in STREAM_RATES.items():
                self._frac[stream] += (t - self._t_last) * rate
                n = int(self._frac[stream])
                if n <= 0:
                    continue
                self._frac[stream] -= n
                ts = t - (np.arange(n)[::-1]) / rate
                self._emit(stream, ts)
            self._t_last = t

    def _advance_events(self, t: float) -> None:
        if t >= self._next_state_flip:
            self.aware = not self.aware
            self._next_state_flip = t + self.rng.exponential(50.0 if self.aware else 30.0)
        if t >= self._next["blink"]:
            self._blinks.append(t)
            self._blinks = [b for b in self._blinks if t - b < 1.0]
            self._next["blink"] = t + self.rng.exponential(5.0)
        if t >= self._next["emg"]:
            self._emg_until = t + self.rng.uniform(0.8, 2.0)
            self._next["emg"] = t + self.rng.exponential(40.0)
        if t >= self._next["move"]:
            self._move_until = t + 1.0
            self._next["move"] = t + self.rng.exponential(60.0)

    def _emit(self, stream: str, ts: np.ndarray) -> None:
        if stream == "EEG":
            self.on_chunk(Chunk("EEG", ts, self._eeg(ts), MAIN_EEG, STREAM_RATES["EEG"]))
        elif stream == "ACCGYRO":
            n = len(ts)
            x = self.rng.normal(0, 0.01, (n, 6))
            x[:, 2] += 1.0
            moving = ts < self._move_until
            x[moving, 3:] += self.rng.normal(0, 30.0, (moving.sum(), 3))
            x[:, 3:] += self.rng.normal(0, 1.0, (n, 3))
            self.on_chunk(Chunk("ACCGYRO", ts, x, ["ACC_X", "ACC_Y", "ACC_Z", "GYRO_X", "GYRO_Y", "GYRO_Z"], 52.0))
        elif stream == "OPTICS":
            n_opt = PRESET_OPTICS.get(self.preset, 0)
            if n_opt:
                names = OPTICS4 if n_opt == 4 else OPTICS16[:n_opt]
                self.on_chunk(Chunk("OPTICS", ts, self._optics(ts, len(names)), names, 64.0))
        elif stream == "BATTERY":
            self.on_chunk(Chunk("BATTERY", ts, np.full((len(ts), 1), 87.0), ["BATTERY_PERCENT"], 0.2))

    def _eeg(self, ts: np.ndarray) -> np.ndarray:
        n = len(ts)
        dt = 1.0 / 256.0
        out = np.empty((n, 4))
        noise = self.rng.normal(0, 4.0, (n, 4))
        for i in range(n):
            self._ar = 0.97 * self._ar + noise[i]
            out[i] = self._ar
        drifting = not self.aware
        alpha_amp = np.array([7.0, 3.0, 3.0, 7.0]) * (1.6 if drifting else 1.0)
        if self.ir_effect and ts[0] < self._effect_until:
            alpha_amp = alpha_amp * (1.0 + self.ir_effect)
        theta_amp = np.array([2.0, 5.0, 5.0, 2.0]) * (1.7 if drifting else 1.0)
        beta_amp = np.array([2.5, 3.0, 3.0, 2.5]) * (0.8 if drifting else 1.0)
        k = np.arange(n)
        a = self._phase["alpha"] + 2 * math.pi * 10.0 * dt * k
        th = self._phase["theta"] + 2 * math.pi * 6.0 * dt * k
        b = self._phase["beta"] + 2 * math.pi * 20.0 * dt * k
        self._phase["alpha"] = float(a[-1] + 2 * math.pi * 10.0 * dt) % (2 * math.pi)
        self._phase["theta"] = float(th[-1] + 2 * math.pi * 6.0 * dt) % (2 * math.pi)
        self._phase["beta"] = float(b[-1] + 2 * math.pi * 20.0 * dt) % (2 * math.pi)
        out += np.outer(np.sin(a), alpha_amp) + np.outer(np.sin(th), theta_amp) + np.outer(np.sin(b), beta_amp)
        for bt in self._blinks:
            rel = ts - bt
            m = (rel >= 0) & (rel < 0.3)
            out[m, 1] += 200.0 * np.sin(math.pi * rel[m] / 0.3)
            out[m, 2] += 200.0 * np.sin(math.pi * rel[m] / 0.3)
        emg = ts < self._emg_until
        if emg.any():
            burst = self.rng.normal(0, 25.0, (emg.sum(), 2))
            out[np.ix_(emg, [0, 3])] += burst
        moving = ts < self._move_until
        out[moving] += self.rng.normal(0, 40.0, (moving.sum(), 4))
        for t_s, amp in self._switch_steps:
            rel = ts - t_s
            m = rel >= 0
            decay = amp * np.exp(-rel[m] / 0.5)
            out[m, 1] += decay
            out[m, 2] += decay
        self._switch_steps = [(t_s, a_) for t_s, a_ in self._switch_steps if ts[-1] - t_s < 4.0]
        for edges in self._light:
            for a_, b_, inten in edges:
                if inten <= 0 or b_ < ts[0] or a_ > ts[-1]:
                    continue
                m = (ts >= a_) & (ts < b_)
                out[m, 1] += 0.25 * self.artifact_uv * inten
                out[m, 2] += 0.25 * self.artifact_uv * inten
        self._light = [e for e in self._light if e and e[-1][1] > ts[-1] - 1.0]
        return out + 800.0

    def _optics(self, ts: np.ndarray, n_ch: int) -> np.ndarray:
        hr = 62.0 / 60.0
        k = np.arange(len(ts))
        ph = self._phase["heart"] + 2 * math.pi * hr * k / 64.0
        self._phase["heart"] = float(ph[-1] + 2 * math.pi * hr / 64.0) % (2 * math.pi)
        pulse = np.sin(ph) + 0.35 * np.sin(2 * ph + 0.8)
        base = np.linspace(0.30, 0.45, n_ch)
        return base + 0.004 * pulse[:, None] + self.rng.normal(0, 0.0006, (len(ts), n_ch))
