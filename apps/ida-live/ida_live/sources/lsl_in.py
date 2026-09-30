"""Read Muse streams from Lab Streaming Layer (e.g. `OpenMuse stream` running separately).

In this mode another program holds the Bluetooth connection, so presets cannot be
switched and light trials are unavailable. It is the fallback if the built-in
headband connection misbehaves.
"""

from __future__ import annotations

import asyncio
from typing import Dict, Optional

import numpy as np

from ..core import Chunk, STREAM_RATES, now
from .base import Source, register

try:
    from mne_lsl.lsl import StreamInlet, local_clock, resolve_streams

    HAVE_LSL = True
except Exception:  # pragma: no cover
    HAVE_LSL = False


def _stream_key(name: str) -> Optional[str]:
    up = name.upper()
    for key in ("EEG", "ACCGYRO", "OPTICS", "BATTERY"):
        if key in up:
            return key
    return None


@register("lsl")
class LSLSource(Source):
    def __init__(self, settings, on_chunk, on_log):
        super().__init__(settings, on_chunk, on_log)
        self._inlets: Dict[str, object] = {}
        self._task: Optional[asyncio.Task] = None
        self._offset = 0.0

    async def start(self) -> None:
        if not HAVE_LSL:
            raise RuntimeError("mne-lsl is not installed. Run install.bat again.")
        infos = await asyncio.to_thread(resolve_streams, 3.0)
        for info in infos:
            key = _stream_key(info.name)
            if key and "MUSE" in info.name.upper() and key not in self._inlets:
                inlet = StreamInlet(info)
                inlet.open_stream()
                self._inlets[key] = (inlet, info.get_channel_names() or [f"ch{i}" for i in range(info.n_channels)])
        if "EEG" not in self._inlets:
            raise RuntimeError("No Muse EEG stream found on LSL. Start `OpenMuse stream` first.")
        self._offset = now() - local_clock()
        self.connected = True
        self.info = {"streams": ", ".join(sorted(self._inlets))}
        self._task = asyncio.create_task(self._run())
        self.log(f"Reading LSL streams: {self.info['streams']}.")

    async def _run(self) -> None:
        while self.connected:
            await asyncio.sleep(0.05)
            for key, (inlet, names) in self._inlets.items():
                data, ts = inlet.pull_chunk(timeout=0.0)
                if len(ts) == 0:
                    continue
                x = np.asarray(data, dtype=np.float64)
                t = np.asarray(ts) + self._offset
                if key == "EEG":
                    self.on_chunk(Chunk("EEG", t, x[:, :4], list(names[:4]), STREAM_RATES["EEG"]))
                else:
                    self.on_chunk(Chunk(key, t, x, list(names), STREAM_RATES[key]))

    async def stop(self) -> None:
        self.connected = False
        if self._task:
            self._task.cancel()
        for inlet, _ in self._inlets.values():
            try:
                inlet.close_stream()
            except Exception:
                pass
