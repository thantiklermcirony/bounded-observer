"""Shared data types: sample chunks, ring buffers and the session clock."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


def now() -> float:
    """The one clock every part of the app uses (seconds, monotonic)."""
    return time.perf_counter()


@dataclass
class Chunk:
    """A block of samples from one stream.

    stream: "EEG", "ACCGYRO", "OPTICS" or "BATTERY" (new sources may add more)
    t:      (n,) timestamps on the session clock
    x:      (n, n_channels) values
    """

    stream: str
    t: np.ndarray
    x: np.ndarray
    channels: List[str]
    rate: float


STREAM_RATES = {"EEG": 256.0, "ACCGYRO": 52.0, "OPTICS": 64.0, "BATTERY": 0.2}


class RingBuffer:
    """Fixed-length buffer of timestamped multichannel samples.

    If a stream's channel set changes (for example the optics going from 4 to 16
    channels after a preset switch) the buffer resets rather than mixing layouts.
    """

    def __init__(self, seconds: float, rate: float, channels: List[str]):
        self.rate = rate
        self.capacity = max(8, int(seconds * rate))
        self.channels = list(channels)
        self._t = np.full(self.capacity, np.nan)
        self._x = np.full((self.capacity, len(channels)), np.nan, dtype=np.float64)
        self._n = 0
        self._head = 0
        self.total = 0
        self.last_time: Optional[float] = None
        self._lock = threading.Lock()

    def push(self, t: np.ndarray, x: np.ndarray) -> None:
        if len(t) == 0:
            return
        with self._lock:
            n = len(t)
            if n >= self.capacity:
                t, x, n = t[-self.capacity:], x[-self.capacity:], self.capacity
            idx = (self._head + np.arange(n)) % self.capacity
            self._t[idx] = t
            self._x[idx] = x
            self._head = (self._head + n) % self.capacity
            self._n = min(self.capacity, self._n + n)
            self.total += n
            self.last_time = float(t[-1])

    def latest(self, n: int) -> Tuple[np.ndarray, np.ndarray]:
        with self._lock:
            n = min(n, self._n)
            if n == 0:
                return np.empty(0), np.empty((0, len(self.channels)))
            idx = (self._head - n + np.arange(n)) % self.capacity
            return self._t[idx].copy(), self._x[idx].copy()

    def since(self, total_seen: int) -> Tuple[np.ndarray, np.ndarray, int]:
        """Samples pushed after a previous `total` counter (for streaming to the UI)."""
        with self._lock:
            new = self.total - total_seen
        if new <= 0:
            return np.empty(0), np.empty((0, len(self.channels))), self.total
        t, x = self.latest(new)
        return t, x, self.total

    def is_fresh(self, at: float, max_age: float = 1.5) -> bool:
        return self.last_time is not None and (at - self.last_time) <= max_age


@dataclass
class Buffers:
    """All live stream buffers, keyed by stream name."""

    seconds: float = 60.0
    streams: Dict[str, RingBuffer] = field(default_factory=dict)

    def push(self, chunk: Chunk) -> None:
        buf = self.streams.get(chunk.stream)
        if buf is None or buf.channels != list(chunk.channels):
            buf = RingBuffer(self.seconds, chunk.rate, chunk.channels)
            self.streams[chunk.stream] = buf
        buf.push(chunk.t, chunk.x)

    def get(self, stream: str) -> Optional[RingBuffer]:
        return self.streams.get(stream)
