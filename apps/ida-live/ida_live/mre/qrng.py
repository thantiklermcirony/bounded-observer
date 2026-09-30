"""Random-bit sources and the 10 Hz bit logger for the Murray Reality Equation test.

The MRE (history/R15) predicts that the alternation bias δ of a quantum measurement stream
shifts with the observer's information rate Φ:  δ(Φ) = tanh(atanh δ0 + 2 α0 κ Φ),
while the marginal rate p stays fixed. The paper's protocol bins a detector's events in 100 ms
bins and sets X_t = 1 if the bin's count is at or above the automation median.

Every source here is reduced the same way: each 100 ms bin gets a count of events per stream
(ones among a FIXED number of raw bits taken in that bin, or detector pulses), and the analysis
sets X_t = count >= median, the median fixed from the source's own unattended (C1) data. A fixed
number of bits per bin matters: counting everything that arrived would let USB throughput
jitter masquerade as structure. Nothing is whitened here: whitening or hashing would destroy
exactly the lag-1 structure the test looks for.

Sources:
  serial  a USB random-number device on a serial port (TrueRNG / TrueRNGpro / OneRNG / any
          CDC byte stream). A TrueRNGpro is switched to its unwhitened RAW ASCII mode, which
          gives two independent streams (generators A and B), like the paper's two GM tubes.
  anu     ANU's online vacuum-fluctuation QRNG (remote, generated before it reaches you:
          by the MRE's own locality theorem it is a control arm, not a test arm)
  sham    two seeded pseudo-random streams (the pipeline must find nothing in them)

Files, in Documents/IDA Live/mre/:
  bits_<tag>_YYYY-MM-DD.csv   one row per bin: wall,cond,clean,phi,phi_raw,count_A,n_A,count_B,n_B
                              cond 1 = C1 (nothing connected: automation), 2 = C2 (a recording
                              with a live headband), 0 = idle (anything else, e.g. headband on
                              but not recording, or the simulator)
  segments_<tag>.csv          when the source, session or task changed
  threshold_<tag>.json        the automation median per stream, fixed after 5 minutes of C1
"""

from __future__ import annotations

import csv
import json
import threading
import time
import urllib.request
from collections import deque
from pathlib import Path
from typing import Callable, List, Optional

import numpy as np

from ..core import now

BIN_S = 0.1
POPCOUNT = np.array([bin(i).count("1") for i in range(256)], dtype=np.int32)
BITS_COLUMNS = ["wall", "cond", "clean", "phi", "phi_raw", "count_A", "n_A", "count_B", "n_B"]
SEG_COLUMNS = ["wall", "source", "kind", "streams", "bits_per_bin", "session", "task"]
COND_CODE = {"idle": 0, "C1": 1, "C2": 2}


class Source:
    kind = "base"          # local-quantum | local-noise | remote | sham
    name = "none"
    streams = 1            # independent bit streams (the paper's two GM tubes; TrueRNGpro's A and B)
    bits_per_bin = 0       # raw bits counted per stream per bin

    def __init__(self):
        self.error: Optional[str] = None
        self.total_bits = 0

    def open(self) -> None: ...
    def close(self) -> None: ...

    def read(self, budget: List[int]):
        """Block briefly; return (ones, bits) per stream, counting at most budget[k] bits of
        stream k (the rest of what arrived is discarded), or None when nothing arrived."""
        raise NotImplementedError


class SerialSource(Source):
    kind = "local-noise"

    def __init__(self, port: str = "auto", mode: str = "raw", bits_per_bin: int = 0):
        super().__init__()
        self.port_req, self.mode, self.bpb_req = port, mode, int(bits_per_bin or 0)
        self.ser = None
        self.port = None
        self._buf = b""
        self.name = "serial"
        self.pro = False

    @staticmethod
    def ports() -> list:
        try:
            from serial.tools import list_ports
            return [{"device": p.device, "description": p.description or "", "vid": p.vid, "pid": p.pid,
                     "hwid": p.hwid or ""} for p in list_ports.comports()]
        except Exception:
            return []

    def _pick(self) -> Optional[str]:
        if self.port_req and self.port_req != "auto":
            return self.port_req
        for p in self.ports():
            d = (p["description"] + " " + p["hwid"]).lower()
            if any(k in d for k in ("truerng", "onerng", "rng", "quantis", "04d8:f5fe", "04d8:ebb5")):
                return p["device"]
        return None

    def _knock(self, baud: int) -> None:
        """TrueRNGpro mode change: open at 110, 300, 110 baud, then the mode's baud (ubld.it)."""
        import serial
        for b in (110, 300, 110, baud):
            s = serial.Serial(self.port, b, timeout=0.2)
            s.close()
            time.sleep(0.1)
        time.sleep(1.1)

    def open(self) -> None:
        import serial
        self.port = self._pick()
        if not self.port:
            raise RuntimeError("No USB random-number device found. Plug it in, or pick its port in the MRE tab.")
        d = next((p["description"] for p in self.ports() if p["device"] == self.port), "")
        self.name = (d or "serial") + f" [{self.port}]"
        self.pro = "pro" in d.lower()
        raw = self.pro and self.mode == "raw"
        self.streams = 2 if raw else 1
        # raw: one ADC sample per bit (rate depends on the device); bytes: 1 kB per bin is far
        # below any USB RNG's throughput, so every bin gets the same number of bits
        self.bits_per_bin = self.bpb_req or (200 if raw else 8192)
        if raw:
            self._knock(38400)  # RAW ASCII: "AAAA,BBBB" unwhitened ADC samples of both generators
            self.name += " RAW"
        self.ser = serial.Serial(self.port, 115200, timeout=0.05)
        self.ser.reset_input_buffer()

    def close(self) -> None:
        try:
            if self.ser:
                self.ser.close()
                if self.pro and self.mode == "raw":
                    self._knock(300)  # back to normal mode for other software
        except Exception:
            pass
        self.ser = None

    def read(self, budget):
        data = self.ser.read(self.ser.in_waiting or 1)
        if not data:
            return None
        if self.pro and self.mode == "raw":
            # the least significant bit of each generator's ADC sample is that stream's event bit
            self._buf += data
            *lines, self._buf = self._buf.split(b"\n")
            ones, n = [0, 0], [0, 0]
            for ln in lines:
                parts = ln.strip().split(b",")
                for k in (0, 1):
                    if n[k] < budget[k] and len(parts) > k and parts[k].strip().isdigit():
                        ones[k] += int(parts[k]) & 1
                        n[k] += 1
            self.total_bits += sum(n)
            return ones, n
        take = max(0, budget[0]) // 8
        arr = np.frombuffer(data[:take], dtype=np.uint8)
        self.total_bits += 8 * len(arr)
        return [int(POPCOUNT[arr].sum())], [8 * len(arr)]


class ANUSource(Source):
    """ANU QRNG over the internet. Numbers are measured in their lab and fetched in batches, so
    each bit was produced before the observer's moment: a remote control arm. One byte per bin:
    600 bytes a minute, within the free endpoint's one request (1024 bytes) a minute."""
    kind = "remote"
    name = "ANU QRNG (remote)"
    bits_per_bin = 8
    URL = "https://qrng.anu.edu.au/API/jsonI.php?length=1024&type=uint8"
    KEY_URL = "https://api.quantumnumbers.anu.edu.au?length=1024&type=uint8"

    def __init__(self, api_key: str = "", min_interval_s: float = 65.0):
        super().__init__()
        self.key = api_key
        self.min_interval = 2.0 if api_key else min_interval_s
        self.queue: deque = deque()
        self.last_fetch = 0.0

    def _fetch(self) -> None:
        if self.key:
            req = urllib.request.Request(self.KEY_URL, headers={"x-api-key": self.key})
        else:
            req = urllib.request.Request(self.URL, headers={"User-Agent": "IDA-Live"})
        with urllib.request.urlopen(req, timeout=20) as r:
            js = json.loads(r.read().decode())
        if "data" not in js:
            raise RuntimeError(str(js)[:200])
        self.queue.extend(int(v) for v in js["data"])

    def open(self) -> None:
        self._fetch()                       # fail early and visibly if the service is unreachable
        self.last_fetch = time.time()

    def read(self, budget):
        if len(self.queue) < 120 and time.time() - self.last_fetch > self.min_interval:
            self.last_fetch = time.time()
            try:
                self._fetch()
                self.error = None
            except Exception as exc:
                self.error = f"ANU fetch failed: {exc}"
        if not self.queue:
            time.sleep(0.05)
            return None
        v = self.queue.popleft()
        self.total_bits += 8
        return [int(POPCOUNT[v])], [8]


class ShamSource(Source):
    """Two seeded pseudo-random streams. `effect` (for tests only) injects the MRE's predicted
    law: each bin switches with probability (1 + d)/2, d = effect x Φ(kbit/s), so the alternation
    bias rises with Φ while the marginal stays 0.5, and the analysis can be checked for finding
    what is there."""
    kind = "sham"
    name = "pseudo-random (sham)"
    streams = 2
    bits_per_bin = 160

    def __init__(self, seed: int = 12345, effect: float = 0.0, phi: Optional[Callable[[], float]] = None):
        super().__init__()
        self.rng = np.random.default_rng(seed)
        self.effect, self.phi = effect, phi
        self.prev = [0, 0]

    def read(self, budget):
        time.sleep(0.01)
        if self.effect and self.phi:
            if budget[0] <= 0:
                return None
            d = float(np.clip(self.effect * (self.phi() or 0.0) / 1000.0, -0.9, 0.9))
            out = []
            for k in (0, 1):
                x = self.prev[k] ^ int(self.rng.random() < (1 + d) / 2)
                self.prev[k] = x
                gap = 1 + int(self.rng.integers(0, 1000))
                out.append(1000 + gap if x else 1000 - gap)     # a count above or below the median
            return out, [budget[0], budget[1]]
        take = [max(0, min(80, b)) for b in budget]
        ones = [int(self.rng.binomial(t, 0.5)) if t else 0 for t in take]
        self.total_bits += sum(take)
        return ones, take


def make_source(cfg: dict, which: str = "source") -> Optional[Source]:
    kind = cfg.get(which, "off")
    if kind == "serial":
        return SerialSource(cfg.get("port", "auto"), cfg.get("mode", "raw"), int(cfg.get("bits_per_bin", 0)))
    if kind == "anu":
        return ANUSource(cfg.get("anu_key", ""))
    if kind == "sham":
        return ShamSource(int(cfg.get("sham_seed", 12345)) + (1 if which == "control" else 0))
    return None


def list_ports() -> list:
    return SerialSource.ports()


class BitLogger:
    """Reads one source continuously, counts each stream's events in 100 ms bins over a fixed
    number of bits, and writes one row per bin with the condition and the observer's Φ.

    `tag` separates simultaneous loggers: "main" (the device under test) and "control" (a remote
    or pseudo-random arm logged at the same moments against the same Φ)."""

    THETA_BINS = 3000            # 5 minutes of unattended (C1) bins fix the automation median

    def __init__(self, folder: Path, source: Optional[Source], context: Callable[[], dict],
                 log: Callable[[str], None], tag: str = "main"):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.src, self.context, self.log, self.tag = source, context, log, tag
        self.thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()
        self.stats = {"tag": tag, "state": "off", "bins": 0, "c1": 0, "c2": 0, "idle": 0, "short": 0,
                      "rate_bps": 0, "theta": None, "error": None, "source": source.name if source else None,
                      "kind": source.kind if source else None, "streams": 0, "p1": None}
        self.theta: Optional[dict] = None
        self.c1_counts: dict = {}
        self._ones = [0, 0]
        self._n = 0

    # the automation median: fixed once enough unattended data exists (a stable threshold)
    def theta_path(self) -> Path:
        return self.folder / f"threshold_{self.tag}.json"

    def _load_theta(self, source_name: str) -> Optional[dict]:
        try:
            th = json.loads(self.theta_path().read_text(encoding="utf-8"))
            return th if th.get("source") == source_name else None      # a new device needs its own
        except (OSError, ValueError):
            return None

    def start(self) -> None:
        if (self.thread and self.thread.is_alive()) or self.src is None:
            return
        self.stop_flag.clear()
        self.stats["state"] = "starting"
        self.thread = threading.Thread(target=self._run, daemon=True, name=f"mre-bits-{self.tag}")
        self.thread.start()

    def stop(self) -> None:
        self.stop_flag.set()
        if self.thread:
            self.thread.join(timeout=5)
        self.stats["state"] = "off"

    def _maybe_fix_theta(self, k: int, count: int) -> None:
        if self.theta and str(k) in self.theta["theta"]:
            return
        c1 = self.c1_counts.setdefault(k, [])
        c1.append(count)
        if len(c1) >= self.THETA_BINS:
            th = self.theta or {"source": self.src.name, "bits_per_bin": self.src.bits_per_bin, "theta": {},
                                "from_bins": {}, "made": time.strftime("%Y-%m-%d %H:%M")}
            th["theta"][str(k)] = float(np.median(c1))
            th["from_bins"][str(k)] = len(c1)
            self.theta = th
            self.theta_path().write_text(json.dumps(th), encoding="utf-8")
            self.log(f"MRE bits ({self.tag}): automation median for stream {'AB'[k]} fixed at "
                     f"{th['theta'][str(k)]:.1f} events per bin.")

    def _run(self) -> None:
        src = self.src
        try:
            src.open()
        except Exception as exc:
            self.stats.update(state="error", error=str(exc))
            self.log(f"MRE bits ({self.tag}): {exc}")
            return
        self.theta = self._load_theta(src.name)
        ns, K = int(src.streams), int(src.bits_per_bin)
        self.stats.update(state="running", error=None, source=src.name, kind=src.kind, streams=ns,
                          theta=(self.theta or {}).get("theta"))
        self.log(f"MRE bits ({self.tag}): logging from {src.name} ({src.kind}, {ns} stream"
                 f"{'s' if ns > 1 else ''}, {K} bits per bin).")
        f = day = writer = None
        seg_key = None
        bin_start = now()
        counts, nbits = [0] * ns, [0] * ns
        t_rate, bits_rate = time.time(), 0
        segp = self.folder / f"segments_{self.tag}.csv"
        try:
            while not self.stop_flag.is_set():
                got = src.read([K - n for n in nbits] + [0] * (2 - ns))
                if got is not None:
                    for k in range(ns):
                        counts[k] += got[0][k]
                        nbits[k] += got[1][k]
                self.stats["error"] = src.error
                if src.kind == "remote":
                    # a remote batch has no local timing: one byte is one bin, played out at 10 Hz
                    if got is None:
                        continue
                    time.sleep(max(0.0, BIN_S - (now() - bin_start)))
                elif now() - bin_start < BIN_S:
                    continue
                ctx = self.context()
                eeg, session = bool(ctx.get("eeg")), ctx.get("session") or ""
                # C2: recording with a live headband; C1: no headband (or any source) connected
                cond = "C2" if (session and eeg) else ("C1" if not ctx.get("connected") else "idle")
                key = (session, ctx.get("task") or "")
                if key != seg_key:
                    new = not segp.exists()
                    with open(segp, "a", newline="", encoding="utf-8") as sf:
                        w = csv.writer(sf)
                        if new:
                            w.writerow(SEG_COLUMNS)
                        w.writerow([round(time.time(), 2), src.name, src.kind, ns, K, session, key[1]])
                    seg_key = key
                d = time.strftime("%Y-%m-%d")
                if d != day:
                    if f:
                        f.close()
                    p = self.folder / f"bits_{self.tag}_{d}.csv"
                    new = not p.exists()
                    f = open(p, "a", newline="", encoding="utf-8")
                    writer = csv.writer(f)
                    if new:
                        writer.writerow(BITS_COLUMNS)
                    day = d
                full = all(n >= K for n in nbits) if K else True
                row = [round(time.time(), 2), COND_CODE[cond], int(bool(ctx.get("clean"))),
                       _r(ctx.get("phi")), _r(ctx.get("phi_raw"))]
                for k in range(2):
                    row += [counts[k], nbits[k]] if k < ns else ["nan", 0]
                writer.writerow(row)
                if not full:
                    self.stats["short"] += 1
                elif cond == "C1":
                    for k in range(ns):
                        self._maybe_fix_theta(k, counts[k])
                if full and self.theta and "0" in self.theta["theta"]:
                    self._ones[0] += int(counts[0] >= self.theta["theta"]["0"])
                    self._n += 1
                    self.stats["p1"] = round(self._ones[0] / self._n, 4)
                self.stats["bins"] += 1
                self.stats[{"C1": "c1", "C2": "c2", "idle": "idle"}[cond]] += 1
                self.stats["theta"] = (self.theta or {}).get("theta")
                bits_rate += sum(nbits)
                if time.time() - t_rate > 5:
                    self.stats["rate_bps"] = round(bits_rate / (time.time() - t_rate))
                    t_rate, bits_rate = time.time(), 0
                    f.flush()
                bin_start = now() if src.kind == "remote" else bin_start + BIN_S
                if now() - bin_start > 1.0:          # fell behind (sleep, suspend): resynchronise
                    bin_start = now()
                counts, nbits = [0] * ns, [0] * ns
        except Exception as exc:
            self.stats.update(state="error", error=str(exc))
            self.log(f"MRE bits ({self.tag}) stopped: {exc}")
        finally:
            try:
                src.close()
            except Exception:
                pass
            if f:
                f.close()
            if self.stats["state"] == "running":
                self.stats["state"] = "off"


def _r(v):
    try:
        return "nan" if v is None else round(float(v), 1)
    except (TypeError, ValueError):
        return "nan"
