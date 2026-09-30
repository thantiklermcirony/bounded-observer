"""Replay a raw BLE log (OpenMuse format, which is also what every IDA Live session saves).

Useful for re-running a session through a newer feature set or map without the
headband, and for testing the headband decoding path on real bytes.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from .athena import HAVE_OPENMUSE, AthenaSource
from .base import register


@register("replay")
class ReplaySource(AthenaSource):
    can_set_preset = False

    def __init__(self, settings, on_chunk, on_log, path: str = "", speed: float = 1.0, loop: bool = False):
        super().__init__(settings, on_chunk, on_log, address="replay")
        self.path = Path(path)
        self.speed = max(0.1, float(speed))
        self.loop = loop
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        if not HAVE_OPENMUSE:
            raise RuntimeError("The Bluetooth library (bleak) is missing. Reinstall IDA Live.")
        if not self.path.exists():
            raise RuntimeError(f"No recording at {self.path}.")
        self.connected = True
        self.info = {"file": self.path.name}
        self._task = asyncio.create_task(self._run())
        self.log(f"Replaying {self.path.name} at {self.speed:g}× speed.")

    async def _run(self) -> None:
        while self.connected:
            lines = [ln.rstrip("\n") for ln in open(self.path, "r", encoding="utf-8") if ln.count("\t") >= 2]
            if not lines:
                break
            t_first = datetime.fromisoformat(lines[0].split("\t", 1)[0])
            loop = asyncio.get_running_loop()
            start = loop.time()
            for line in lines:
                if not self.connected:
                    return
                uuid = line.split("\t")[1]
                if uuid.startswith("273e0001"):
                    continue  # control notifications carry no samples
                dt = (datetime.fromisoformat(line.split("\t", 1)[0]) - t_first).total_seconds() / self.speed
                wait = start + dt - loop.time()
                if wait > 0:
                    await asyncio.sleep(wait)
                if self.raw_sink:
                    self.raw_sink(line)
                self._handle_message(line)
            if not self.loop:
                break
        self.connected = False
        self.log("Replay finished.")

    async def stop(self) -> None:
        self.connected = False
        if self._task:
            self._task.cancel()
