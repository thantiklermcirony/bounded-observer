"""Muse S Athena over the laptop's own Bluetooth.

The BLE protocol decoding is OpenMuse's (MIT licence, D. Makowski and contributors),
used as a library. This module owns the connection itself so it can switch the
sensor preset mid-session, which is what the light trials need. OpenMuse's own
`OpenMuse stream` command cannot do that while it holds the device.

Status: the command sequence and decoding match OpenMuse's; switching presets
mid-stream is NOT yet verified on hardware. The raw BLE log written for every
session is in OpenMuse's format, so any recording can be re-decoded later with
`OpenMuse.decode_rawdata` if this module's live decoding turns out to be wrong.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional

import numpy as np

from ..core import Chunk, STREAM_RATES, now
from .base import Source, register

try:  # OpenMuse is a required dependency for the headband but not for tests/simulator
    import bleak
    from ..vendor.openmuse.clocks import WindowedRegressionClock
    from ..vendor.openmuse.decode import (
        ACCGYRO_CHANNELS,
        make_timestamps,
        parse_message,
        select_eeg_channels,
        select_optics_channels,
    )
    from ..vendor.openmuse.muse import MuseS

    HAVE_OPENMUSE = True
except Exception:  # pragma: no cover - reported to the user at connect time
    HAVE_OPENMUSE = False

MAIN_EEG = ["EEG_TP9", "EEG_AF7", "EEG_AF8", "EEG_TP10"]


class _StreamState:
    def __init__(self, n_channels: int):
        self.n_channels = n_channels
        self.base_time: Optional[float] = None
        self.wrap_offset = 0
        self.last_abs_tick = 0
        self.sample_counter = 0
        self.last_update_device_time = -1.0
        self.clock = WindowedRegressionClock() if HAVE_OPENMUSE else None


def utc_stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


async def scan(timeout: float = 8.0) -> List[dict]:
    """List nearby Muse headbands."""
    if not HAVE_OPENMUSE:
        raise RuntimeError("The Bluetooth library (bleak) is missing. Reinstall IDA Live.")
    devices = await bleak.BleakScanner.discover(timeout=timeout)
    return [{"name": d.name, "address": d.address} for d in devices if d.name and "muse" in d.name.lower()]


@register("athena")
class AthenaSource(Source):
    can_set_preset = True

    def __init__(self, settings, on_chunk, on_log, address: str = "", preset: Optional[str] = None):
        super().__init__(settings, on_chunk, on_log)
        self.address = address or settings["device"]["address"]
        self.start_preset = preset or settings["device"]["monitor_preset"]
        self.client = None
        self._states: Dict[str, _StreamState] = {}
        self._control_text = ""
        self._switch_lock = asyncio.Lock()
        self._watch: Optional[asyncio.Task] = None
        self._wanted = False
        self.reconnecting = False
        self.on_reconnect = None

    # ---- decoding -------------------------------------------------------
    def _state_for(self, stype: str, n_channels: int) -> _StreamState:
        st = self._states.get(stype)
        if st is None or st.n_channels != n_channels:
            st = _StreamState(n_channels)
            self._states[stype] = st
        return st

    def _on_data(self, sender, data: bytearray) -> None:
        uuid_str = str(getattr(sender, "uuid", sender))
        message = f"{utc_stamp()}\t{uuid_str}\t{data.hex()}"
        if self.raw_sink:
            self.raw_sink(message)
        self._handle_message(message)

    def _handle_message(self, message: str) -> None:
        arrived = now()
        try:
            subpackets = parse_message(message)
        except Exception as exc:  # malformed packet: log and continue
            self.log(f"Skipped a packet that could not be decoded ({exc}).")
            return
        for stype, pkts in subpackets.items():
            if not pkts:
                continue
            n_ch = pkts[0].get("n_channels") or 1
            st = self._state_for(stype, n_ch)
            arr, st.base_time, st.wrap_offset, st.last_abs_tick, st.sample_counter = make_timestamps(
                pkts, st.base_time, st.wrap_offset, st.last_abs_tick, st.sample_counter
            )
            if arr.size == 0 or arr.ndim != 2:
                continue
            dev_t, x = arr[:, 0], arr[:, 1:].astype(np.float64)
            if dev_t[-1] > st.last_update_device_time:
                st.clock.update(float(dev_t[-1]), arrived)
                st.last_update_device_time = float(dev_t[-1])
            t = st.clock.map_time(dev_t)
            order = np.argsort(t)
            t, x = t[order], x[order]
            self._emit(stype, t, x)

    def _emit(self, stype: str, t: np.ndarray, x: np.ndarray) -> None:
        if stype == "EEG":
            names = select_eeg_channels(x.shape[1])
            self.on_chunk(Chunk("EEG", t, x[:, :4], MAIN_EEG, STREAM_RATES["EEG"]))
            if x.shape[1] > 4:
                self.on_chunk(Chunk("AUX", t, x[:, 4:], names[4:], STREAM_RATES["EEG"]))
        elif stype == "OPTICS":
            self.on_chunk(Chunk("OPTICS", t, x, select_optics_channels(x.shape[1]), STREAM_RATES["OPTICS"]))
        elif stype == "ACCGYRO":
            self.on_chunk(Chunk("ACCGYRO", t, x, list(ACCGYRO_CHANNELS), STREAM_RATES["ACCGYRO"]))
        elif stype == "BATTERY":
            self.on_chunk(Chunk("BATTERY", t, x[:, :1], ["BATTERY_PERCENT"], STREAM_RATES["BATTERY"]))

    def _on_control(self, _sender, data: bytearray) -> None:
        text = data.decode("utf-8", errors="ignore")
        self._control_text = (self._control_text + text)[-4096:]
        if self.raw_sink:
            self.raw_sink(f"{utc_stamp()}\t{MuseS.CONTROL_UUID}\t{data.hex()}")

    # ---- connection -----------------------------------------------------
    async def _open(self, preset: str) -> None:
        self.client = bleak.BleakClient(self.address, timeout=15.0)
        await self.client.connect()
        await self.client.start_notify(MuseS.CONTROL_UUID, self._on_control)
        for uuid in MuseS.DATA_CHARACTERISTICS:
            await self.client.start_notify(uuid, self._on_data)
        await MuseS.initialize_device(self.client, preset)
        self.preset = preset

    async def start(self) -> None:
        if not HAVE_OPENMUSE:
            raise RuntimeError("The Bluetooth library (bleak) is missing. Reinstall IDA Live.")
        if not self.address:
            raise RuntimeError("No headband address yet. Use Find headband first.")
        self.log(f"Connecting to {self.address} …")
        await self._open(self.start_preset)
        self.connected = True
        self._wanted = True
        self.reconnecting = False
        self.info = {"address": self.address, "name": str(self.client.name or "Muse")}
        self.log(f"Streaming from {self.info['name']} with preset {self.preset}.")
        self._watch = asyncio.create_task(self._watchdog())

    async def _watchdog(self) -> None:
        """Bluetooth links drop now and then. When it happens, reconnect by ourselves with the
        same preset, as fast as the headband allows, and keep trying for a few minutes."""
        while self._wanted:
            await asyncio.sleep(1.0)
            if self.client is not None and self.client.is_connected:
                continue
            self.connected = False
            self.reconnecting = True
            self.log("The headband's Bluetooth link dropped. Reconnecting …")
            t0 = asyncio.get_running_loop().time()
            attempt = 0
            while self._wanted:
                attempt += 1
                try:
                    try:
                        if self.client is not None:
                            await self.client.disconnect()
                    except Exception:
                        pass
                    self._states = {}  # restart the timestamp clocks on the new link
                    await self._open(self.preset or self.start_preset)
                    self.connected = True
                    self.reconnecting = False
                    gap = asyncio.get_running_loop().time() - t0
                    self.log(f"Reconnected after {gap:.0f} s (attempt {attempt}).")
                    if self.on_reconnect:
                        self.on_reconnect(gap)
                    break
                except Exception as exc:
                    if asyncio.get_running_loop().time() - t0 > 300:
                        self.reconnecting = False
                        self.log(f"Could not reconnect for 5 minutes ({exc}). Check the battery, then Connect again.")
                        self._wanted = False
                        return
                    await asyncio.sleep(min(10.0, 1.0 + attempt))

    async def set_preset(self, preset: str) -> float:
        """Halt, apply preset, restart streaming. Same command sequence every time,
        whether or not the preset actually changes (this is what makes sham trials match)."""
        async with self._switch_lock:
            t0 = now()
            await MuseS.send_command(self.client, "h")
            await asyncio.sleep(0.15)
            await MuseS.send_command(self.client, preset)
            await asyncio.sleep(0.15)
            await MuseS.send_command(self.client, "dc001")
            await asyncio.sleep(0.05)
            await MuseS.send_command(self.client, "dc001")
            await asyncio.sleep(0.05)
            await MuseS.send_command(self.client, "L1")
            self.preset = preset
            return t0

    async def stop(self) -> None:
        self.connected = False
        self._wanted = False
        if self._watch:
            self._watch.cancel()
        if self.client is not None:
            try:
                await MuseS.stop_streaming(self.client)
                await self.client.disconnect()
            except Exception:
                pass
        self.client = None
