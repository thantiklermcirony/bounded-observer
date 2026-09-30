"""Actuators: things that deliver a stimulus. Each one takes the same pattern language.

Pattern language (JSON), all times in seconds unless named _ms:
  {"type": "steady", "duration_s": 8, "intensity": 0.3}
  {"type": "burst", "pulse_hz": 10, "duty": 0.5, "duration_s": 2, "intensity": 0.3}
  {"type": "train", "burst": {<a burst>}, "repeat": 5, "gap_s": 1.5}
  {"type": "sequence", "steps_ms": [[on_ms, off_ms], ...], "intensity": 0.3}
  {"type": "ramp", "pulse_hz": 10, "duty": 0.5, "duration_s": 6,
   "intensity_from": 0.05, "intensity_to": 0.4}          (a "rising cloud")

Every pattern normalises to a list of (on_ms, off_ms, intensity) segments, which
each actuator checks against what its hardware can physically do.

Actuators:
  muse_optics   The Athena's own optics, switched by preset. Each switch halts the
                headband for about half a second, so segments shorter than 1 s are
                refused and EEG is blind during every switch.
  external_led  An 850 nm LED on a microcontroller (hardware/ir_led_driver). Timing
                is done on the microcontroller to the millisecond; the app only sends
                the pattern. The firmware enforces its own limits as well.
  sim_led       For the simulator: produces the same log entries and, optionally,
                a known injected effect and electrical artifact.

Sham: every actuator runs an identical command sequence with the light off
(Muse: re-sends the baseline preset; LED: intensity 0 with identical timing).
"""

from __future__ import annotations

import asyncio
from typing import Dict, List, Optional, Tuple, Type

from .core import now

Segment = Tuple[float, float, float]  # on_ms, off_ms, intensity 0..1


def normalize(p: dict) -> List[Segment]:
    kind = p.get("type", "steady")
    if kind == "steady":
        return [(1000.0 * float(p["duration_s"]), 0.0, float(p.get("intensity", 1.0)))]
    if kind in ("burst", "ramp"):
        hz, duty, dur = float(p["pulse_hz"]), float(p.get("duty", 0.5)), float(p["duration_s"])
        if not (0 < hz <= 200):
            raise ValueError("pulse_hz must be between 0 and 200")
        if not (0 < duty <= 1):
            raise ValueError("duty must be between 0 and 1")
        n = max(1, int(round(dur * hz)))
        period = 1000.0 / hz
        segs = []
        for i in range(n):
            if kind == "ramp":
                a, b = float(p["intensity_from"]), float(p["intensity_to"])
                inten = a + (b - a) * (i / max(1, n - 1))
            else:
                inten = float(p.get("intensity", 1.0))
            segs.append((period * duty, period * (1 - duty), inten))
        return segs
    if kind == "train":
        one = normalize(p["burst"])
        out: List[Segment] = []
        for r in range(int(p["repeat"])):
            seg = list(one)
            if r < int(p["repeat"]) - 1:
                on, off, inten = seg[-1]
                seg[-1] = (on, off + 1000.0 * float(p["gap_s"]), inten)
            out.extend(seg)
        return out
    if kind == "sequence":
        inten = float(p.get("intensity", 1.0))
        return [(float(a), float(b), inten) for a, b in p["steps_ms"]]
    raise ValueError(f"unknown pattern type {kind!r}")


def summary(segs: List[Segment]) -> dict:
    on = sum(s[0] for s in segs) / 1000.0
    total = sum(s[0] + s[1] for s in segs) / 1000.0
    return {"segments": len(segs), "light_on_s": round(on, 3), "total_s": round(total, 3),
            "max_intensity": round(max((s[2] for s in segs), default=0.0), 3)}


ACTUATORS: Dict[str, Type["Actuator"]] = {}


def register(name: str):
    def deco(cls):
        cls.kind = name
        ACTUATORS[name] = cls
        return cls
    return deco


class Actuator:
    kind = "base"
    min_segment_ms = 1.0
    supports_intensity = True

    def __init__(self, engine):
        self.engine = engine
        self.cfg = engine.settings["actuators"]

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    def check(self, pattern: dict) -> List[Segment]:
        segs = normalize(pattern)
        info = summary(segs)
        if info["light_on_s"] > float(self.cfg["max_on_s_per_fire"]):
            raise ValueError(f"pattern keeps the light on for {info['light_on_s']} s; "
                             f"the limit is {self.cfg['max_on_s_per_fire']} s (knob actuators.max_on_s_per_fire)")
        short = [s for s in segs if (s[0] and s[0] < self.min_segment_ms) or (s[1] and s[1] < self.min_segment_ms)]
        if short:
            raise ValueError(f"{self.kind} cannot switch faster than every {self.min_segment_ms:g} ms; "
                             f"this pattern needs {min(x for s in short for x in s[:2] if x):g} ms")
        if any(s[2] > float(self.cfg["max_intensity"]) for s in segs):
            raise ValueError(f"intensity above the limit {self.cfg['max_intensity']} (knob actuators.max_intensity)")
        return segs

    async def fire(self, segs: List[Segment], sham: bool) -> dict:
        raise NotImplementedError


@register("muse_optics")
class MuseOptics(Actuator):
    min_segment_ms = 1000.0
    supports_intensity = False

    async def open(self) -> None:
        src = self.engine.source
        if not (src and getattr(src, "can_set_preset", False)):
            raise RuntimeError("The headband optics need the direct headband connection (or the simulator).")

    async def fire(self, segs, sham):
        src = self.engine.source
        base = self.engine.settings["ir_protocol"]["baseline_preset"]
        dose = self.cfg["muse_dose_preset"]
        t0 = now()
        cmd_times = []
        for on_ms, off_ms, _ in segs:
            cmd_times.append(await src.set_preset(base if sham else dose))
            await asyncio.sleep(on_ms / 1000.0)
            cmd_times.append(await src.set_preset(base))
            if off_ms:
                await asyncio.sleep(off_ms / 1000.0)
        return {"t_start": t0, "t_end": now(), "switch_times": cmd_times}


@register("external_led")
class ExternalLED(Actuator):
    """Talks to hardware/ir_led_driver over USB serial.

    Protocol (one line each, newline-terminated):
      host -> "P <on_us> <off_us> <count> <pwm0-255>"   queue a uniform run
      host -> "G"                                          execute the queue
      board -> "S <micros>" at start, "D <micros>" when done, "E <reason>" on refusal
    """

    min_segment_ms = 0.5

    def __init__(self, engine):
        super().__init__(engine)
        self.ser = None

    async def open(self) -> None:
        import serial  # pyserial

        port = self.cfg["external_led"]["port"]
        if not port:
            raise RuntimeError("Set the LED's serial port first (knob actuators.external_led.port).")
        self.ser = await asyncio.to_thread(serial.Serial, port, int(self.cfg["external_led"]["baud"]), timeout=0.2)
        await asyncio.sleep(2.0)  # most boards reset when the port opens
        await asyncio.to_thread(self.ser.reset_input_buffer)

    async def close(self) -> None:
        if self.ser:
            await asyncio.to_thread(self.ser.close)
            self.ser = None

    def _runs(self, segs, sham) -> List[Tuple[int, int, int, int]]:
        runs: List[List[int]] = []
        for on_ms, off_ms, inten in segs:
            key = (int(on_ms * 1000), int(off_ms * 1000), 0 if sham else int(round(255 * inten)))
            if runs and tuple(runs[-1][:2]) == key[:2] and runs[-1][3] == key[2]:
                runs[-1][2] += 1
            else:
                runs.append([key[0], key[1], 1, key[2]])
        return [tuple(r) for r in runs]

    async def fire(self, segs, sham):
        if not self.ser:
            await self.open()
        for on_us, off_us, count, pwm in self._runs(segs, sham):
            await asyncio.to_thread(self.ser.write, f"P {on_us} {off_us} {count} {pwm}\n".encode())
        t0 = now()
        await asyncio.to_thread(self.ser.write, b"G\n")
        total = sum(s[0] + s[1] for s in segs) / 1000.0
        deadline = now() + total + 3.0
        started, done = None, None
        while now() < deadline:
            line = (await asyncio.to_thread(self.ser.readline)).decode(errors="ignore").strip()
            if line.startswith("S"):
                started = now()
            elif line.startswith("D"):
                done = now()
                break
            elif line.startswith("E"):
                raise RuntimeError(f"LED driver refused the pattern: {line[1:].strip()}")
        if done is None:
            raise RuntimeError("LED driver did not confirm the pattern finished.")
        return {"t_start": started or t0, "t_end": done}


@register("sim_led")
class SimLED(Actuator):
    min_segment_ms = 0.5

    async def open(self) -> None:
        if not hasattr(self.engine.source, "inject_light"):
            raise RuntimeError("sim_led works with the simulated headband only.")

    async def fire(self, segs, sham):
        t0 = now()
        total = sum(s[0] + s[1] for s in segs) / 1000.0
        self.engine.source.inject_light(t0, segs, sham)
        await asyncio.sleep(total)
        return {"t_start": t0, "t_end": now()}


def make(engine, kind: str) -> Actuator:
    cls = ACTUATORS.get(kind)
    if cls is None:
        raise ValueError(f"Unknown actuator {kind!r}. Available: {sorted(ACTUATORS)}")
    return cls(engine)


def list_serial_ports() -> List[dict]:
    try:
        from serial.tools import list_ports
    except Exception:
        return []
    return [{"port": p.device, "description": p.description} for p in list_ports.comports()]

