"""Source plugins: anything that produces sample chunks.

A new device (OpenBCI Cyton for the R1 headband, a camera, a respiration belt) is
added by writing one subclass and registering it. Nothing downstream changes.
"""

from __future__ import annotations

import abc
from typing import Callable, Dict, Optional, Type

from ..core import Chunk

SOURCES: Dict[str, Type["Source"]] = {}


def register(name: str):
    def deco(cls):
        cls.kind = name
        SOURCES[name] = cls
        return cls

    return deco


class Source(abc.ABC):
    kind = "base"
    #: True if the source can switch the headband's sensor preset (needed for light trials)
    can_set_preset = False

    def __init__(self, settings: dict, on_chunk: Callable[[Chunk], None], on_log: Callable[[str], None]):
        self.settings = settings
        self.on_chunk = on_chunk
        self.log = on_log
        self.preset: Optional[str] = None
        self.raw_sink: Optional[Callable[[str], None]] = None
        self.connected = False
        self.info: Dict[str, str] = {}

    @abc.abstractmethod
    async def start(self) -> None:
        """Connect and begin producing chunks (returns once streaming has begun)."""

    @abc.abstractmethod
    async def stop(self) -> None:
        """Stop streaming and release the device."""

    async def set_preset(self, preset: str) -> float:
        """Switch sensor preset. Returns the time the command sequence started."""
        raise NotImplementedError(f"{self.kind} cannot switch presets")

    def status(self) -> dict:
        return {"kind": self.kind, "connected": self.connected, "preset": self.preset,
                "reconnecting": bool(getattr(self, "reconnecting", False)), **self.info}
