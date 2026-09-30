"""Stimulus plugins for the audio-visual experience (TAO-style contracts).

The Thresholded Adaptive Orchestration paper separates three contracts:
world generation (what a stimulus can render), state estimation (the state
engine, which never sees the stimulus internals) and admissible world changes
(what the stimulus may do next). Here that separation is:

* Stimulus.render_params(t) - the stimulus's own business;
* Stimulus.propose(state) - a requested change, given only the public state;
* admissible(change) - checked by the guard before anything reaches the screen.

The guard enforces a photosensitivity limit by default: no luminance or
colour flashing above max_flash_hz (3 per second, the common guideline ceiling)
and no single-step luminance change above max_luminance_step.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Change:
    luminance: float            # 0..1 target mean luminance
    flicker_hz: float = 0.0     # rate of any periodic luminance/colour modulation
    ramp_s: float = 1.0         # time over which the change is applied


class FlickerGuard:
    def __init__(self, settings: dict):
        s = settings["stimuli"]
        self.max_hz = float(s["max_flash_hz"])
        self.max_step = float(s["max_luminance_step"])
        self.current = 0.2

    def admissible(self, change: Change) -> tuple:
        if change.flicker_hz > self.max_hz:
            return False, f"flicker {change.flicker_hz:g} Hz exceeds the {self.max_hz:g} Hz limit"
        step = abs(change.luminance - self.current)
        if step > self.max_step and change.ramp_s < 1.0:
            return False, f"luminance step {step:.2f} is too abrupt; ramp over at least 1 s"
        return True, "ok"

    def apply(self, change: Change) -> None:
        ok, why = self.admissible(change)
        if not ok:
            raise ValueError(why)
        self.current = change.luminance


class Stimulus:
    """Base class. Subclasses render in the browser; the server only brokers changes."""

    name = "base"

    def propose(self, public_state: dict) -> Optional[Change]:
        return None
