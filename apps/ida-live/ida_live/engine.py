"""The engine: one object that owns the live pipeline.

source -> buffers -> features (4 Hz) -> state engine -> recorder + display
                                   \\-> calibration / probes / light trials

The display is a client like any other: it receives messages and sends commands.
Nothing in the pipeline depends on how (or whether) it is drawn.
"""

from __future__ import annotations

import asyncio
import math
import json
import os
import hashlib
import random
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

import numpy as np

from . import __version__
from .config import DATA_DIR, resolve
from .core import Buffers, Chunk, now
from .features import build_all
from . import actuators as act
from . import knobs
from .protocols import recipe as recipes
from .protocols.ir import LightTrialProtocol
from .recorder import Recorder
from .sources import SOURCES
from .state import FrozenReference, ReferenceBuilder, StateEngine, StateMap

REFERENCE_FEATURES = ["alpha_tp", "theta_af", "beta", "delta_af", "gamma_tp", "emg_tp", "alpha_theta", "aperiodic",
                      "alpha_af", "beta_af", "alpha_theta_af",
                      "lp_delta", "lp_theta", "lp_alpha", "lp_beta", "lp_gamma", "phi", "lzc", "alt", "brain_slope",
                      "ix_alpha_rel", "ix_engagement", "ix_alpha_rel3", "ix_faa", "ix_theta_af_rel"]


class Engine:
    def __init__(self, settings: dict):
        self.settings = settings
        self.buffers = Buffers(seconds=60.0)
        self.features = build_all(settings)
        self.maps_dir = resolve(settings, "maps")
        self.refs_dir = resolve(settings, "references")
        self.sessions_dir = resolve(settings, "sessions")
        self.recipes_dir = resolve(settings, "recipes")
        self.runner: Optional[recipes.RecipeRunner] = None
        self.last_runner: Optional[recipes.RecipeRunner] = None
        self.smap = StateMap.load(self.maps_dir / f"{settings['state']['map']}.json")
        self.reference: Optional[FrozenReference] = None
        latest = self.refs_dir / "latest.json"
        self._startup_note = ""
        if latest.exists():
            try:
                ref = FrozenReference.load(latest)
                if "lp_alpha" not in ref.median:
                    self._startup_note = ("Your saved reference was made by an older version of IDA Live, before the "
                                          "signal checks were fixed. Calibrate again to make a new one.")
                elif ref.median.get("brain_slope", 1.0) < 0.3:
                    self._startup_note = "Your saved reference looks like noise rather than brain signal. Calibrate again."
                else:
                    self.reference = ref
            except Exception:
                self.reference = None
        self.state_engine = StateEngine(self.smap, self.reference, settings)
        self.source = None
        self.recorder: Optional[Recorder] = None
        self.session: Optional[dict] = None
        self.calibration: Optional[dict] = None
        self.protocol: Optional[LightTrialProtocol] = None
        self.clients: Set[Any] = set()
        self.send_fn: Optional[Callable[[Any, str], Any]] = None
        self.t_origin = now()
        self._questions: Dict[str, asyncio.Future] = {}
        self._probe_next: Optional[float] = None
        self._probe_open: Optional[str] = None
        self._raw_seen: Dict[str, int] = {}
        self._last_state: dict = {}
        self._last_flags: dict = {}
        self._last_vals: dict = {}
        self._tasks: List[asyncio.Task] = []
        self.log_lines: List[str] = []
        self.level: Optional[dict] = None

    # ------------------------------------------------------------ messaging
    def rel(self, t: float) -> float:
        return round(t - self.t_origin, 3)

    def broadcast(self, msg: dict) -> None:
        if not self.send_fn:
            return
        text = json.dumps(msg, default=_json_default)
        for ws in list(self.clients):
            asyncio.ensure_future(self.send_fn(ws, text))

    def log(self, text: str) -> None:
        line = f"{time.strftime('%H:%M:%S')}  {text}"
        self.log_lines = (self.log_lines + [line])[-200:]
        self.broadcast({"type": "log", "text": line})

    def event(self, kind: str, data: Optional[dict] = None, public: bool = True) -> None:
        data = dict(data or {})
        data.setdefault("t", now())
        if self.recorder:
            self.recorder.event(kind, data)
        if public:
            self.broadcast({"type": "event", "kind": kind, **{k: v for k, v in data.items() if k != "t"},
                            "t": self.rel(data["t"])})

    def status(self) -> dict:
        return {
            "type": "status",
            "version": __version__,
            "source": self.source.status() if self.source else None,
            "session": self.session,
            "calibration": self.calibration,
            "reference": ({"id": self.reference.ref_id, "created": self.reference.created,
                           "n": self.reference.n_ticks, "median": self.reference.median,
                           "scale": self.reference.scale} if self.reference else None),
            "display": self.settings.get("display", {}),
            "audio": self.settings.get("audio", {}),
            "signal": {"bands": self.settings["signal"]["bands"], "mains_hz": self.settings["signal"]["mains_hz"],
                       "sensors": self.settings["signal"].get("sensors")},
            "reference_fits_map": bool(self.reference and all(f in self.reference.median for f in self.smap.features)),
            "ida": {"dead_band": self.settings["state"].get("dead_band", 0.6)},
            "min_readiness": self.settings["reference"].get("min_readiness", 0.6),
            "note": self._startup_note if self.reference is None else "",
            "data_dir": str(DATA_DIR),
            "map": self.smap.to_dict(),
            "light": self.protocol.public() if self.protocol else None,
            "can_light": bool(self.source and getattr(self.source, "can_set_preset", False)),
            "recipe": (self.runner or self.last_runner).public() if (self.runner or self.last_runner) else None,
            "mre": self.mre_status(),
        }

    def push_status(self) -> None:
        self.broadcast(self.status())

    # ------------------------------------------------------------ source
    def on_chunk(self, chunk: Chunk) -> None:
        self.buffers.push(chunk)
        if self.recorder:
            self.recorder.chunk(chunk)

    def _raw_sink(self, line: str) -> None:
        if self.recorder and self.settings["device"].get("raw_log", True):
            self.recorder.raw(line)

    async def connect(self, kind: str, **kw) -> None:
        if self.source:
            await self.disconnect()
        cls = SOURCES.get(kind)
        if cls is None:
            raise ValueError(f"Unknown source {kind!r}")
        self.buffers = Buffers(seconds=60.0)
        self._raw_seen = {}
        self.source = cls(self.settings, self.on_chunk, self.log, **kw)
        self.source.raw_sink = self._raw_sink
        if hasattr(self.source, "on_reconnect"):
            self.source.on_reconnect = lambda gap: (self.event("reconnected", {"gap_s": round(gap, 1)}), self.push_status())
        await self.source.start()
        self.push_status()

    async def disconnect(self) -> None:
        if self.session:
            await self.end_session()
        if self.calibration and "failed" not in self.calibration:
            self.calibration = {"failed": "The headband disconnected during calibration."}
            self._close_cal_recording({"ok": False, "error": "disconnected"})
        if self.source:
            await self.source.stop()
        self.source = None
        self.push_status()

    # ------------------------------------------------------------ calibration
    def start_calibration(self, seconds: Optional[float] = None, force: bool = False) -> None:
        if not self.source:
            raise RuntimeError("Connect a source first.")
        names = ["TP9", "AF7", "AF8", "TP10"]
        plain = ("left ear", "left forehead", "right forehead", "right ear")
        chosen = self._usable_sensors()
        if not force:
            if len(chosen) < 2 or not any(i in chosen for i in (1, 2)):
                bad = [plain[i] for i in range(4) if i not in chosen]
                raise RuntimeError(
                    "Signal isn't ready yet: fewer than two sensors (including a forehead one) have been "
                    "clean for most of the last 20 seconds. "
                    + (f"Check the {', '.join(bad)} sensor{'s' if len(bad) > 1 else ''}. " if bad else "")
                    + "Wet the sensors, tuck hair away, relax your jaw and sit still.")
            want = [names[i] for i in chosen]
            if want != list(self.settings["signal"].get("sensors") or names):
                # calibrate on the sensors that are actually delivering; the reference records them
                self.set_knob("signal.sensors", want, by="auto")
                left_out = [plain[i] for i in range(4) if i not in chosen]
                self.log(f"Calibrating on {', '.join(want)}; left out the {', '.join(left_out)} "
                         "sensor(s), which weren't clean. Change this under Control › Signal.")
        if self.session:
            raise RuntimeError("The reference stays frozen during a session. End the session to recalibrate.")
        # Calibration collects a fixed amount of CLEAN signal. Progress only ever goes up: bad
        # moments just make it slower. It gives up only if the time limit passes first.
        target = float(seconds or self.settings["reference"]["calibration_s"])
        limit = max(target * 1.5, float(self.settings["reference"].get("max_calibration_s", 300)))
        feats = list(dict.fromkeys(REFERENCE_FEATURES + self.smap.features))
        self._builder = ReferenceBuilder(feats, 0.0)
        self.calibration = {"started": self.rel(now()), "seconds": target, "limit": limit, "elapsed": 0.0,
                            "progress": 0.0, "clean": 0, "clean_s": 0.0, "holding": []}
        self._cal_elapsed = 0.0
        # every calibration is recorded too, so a failed one can be looked at afterwards
        try:
            self.recorder = Recorder(self.sessions_dir, "calibration", {
                "settings": self.settings, "map": self.smap.to_dict(), "reference": None,
                "source": self.source.status(), "kind": "calibration"})
            self.recorder.set_t0(now())
            self._cal_rec = True
            self.event("session_start", {"label": "calibration", "probes": False, "preset": self.source.preset})
        except Exception as exc:
            self._cal_rec = False
            self.log(f"Calibration will not be recorded: {exc}")
        self.log(f"Calibrating: collecting {target:.0f} s of clean signal (gives up after {limit:.0f} s). Sit still, eyes open, soft gaze.")
        self.push_status()

    def _update_sensor_rates(self, flags: dict) -> None:
        """Share of the last ~20 s each sensor has been usable (good, ok or interference)."""
        q = flags.get("quality")
        if not q:
            return
        self._n_rate = getattr(self, "_n_rate", 0) + 1
        a = max(1.0 - math.exp(-0.25 / 20.0), 1.0 / self._n_rate)  # a true share from the first tick
        rates = getattr(self, "_ok_rate", None) or [0.0, 0.0, 0.0, 0.0]
        for i, k in enumerate(q[:4]):
            rates[i] += a * ((1.0 if k in ("good", "ok", "interference") else 0.0) - rates[i])
        self._ok_rate = rates

    def _usable_sensors(self) -> list:
        """Forehead sensors count when clean half the time; ear sensors only when reliably clean,
        because an intermittent ear sensor drags the whole reference toward noise."""
        rates = getattr(self, "_ok_rate", None) or [0.0] * 4
        ear = float(self.settings["reference"].get("ear_min_share", 0.8))
        return [i for i in range(4) if rates[i] >= (ear if i in (0, 3) else 0.5)]

    def _close_cal_recording(self, result: dict) -> None:
        if not getattr(self, "_cal_rec", False) or not self.recorder:
            return
        self._cal_rec = False
        self.event("calibration_result", result)
        self.event("session_end", {})
        folder = self.recorder.folder
        self.recorder.close({"calibration": result})
        self.recorder = None
        try:
            from .analysis.summary import write_summary
            write_summary(folder)
        except Exception:
            pass

    def _finish_calibration(self) -> None:
        try:
            ref = self._builder.freeze(note=f"{self.source.kind} {self.source.info}")
            name = time.strftime("ref_%Y-%m-%d_%H%M%S")
            ref.save(self.refs_dir, name)
            ref.save(self.refs_dir, "latest")
        except Exception as exc:
            self.log(f"Calibration not saved: {exc}")
            self.calibration = {"failed": str(exc)}
            self._close_cal_recording({"ok": False, "error": str(exc), "clean_ticks": len(self._builder.rows),
                                       "total_ticks": self._builder.total})
            self.push_status()
            return
        self._close_cal_recording({"ok": True, "ref_id": ref.ref_id, "clean_ticks": ref.n_ticks,
                                   "total_ticks": self._builder.total})
        self.reference = ref
        self.state_engine = StateEngine(self.smap, ref, self.settings)
        self.calibration = None
        self.log(f"Reference frozen ({ref.n_ticks} clean ticks, id {ref.ref_id}). Saved as {name}.")
        self.push_status()

    # ------------------------------------------------------------ sessions
    def start_session(self, label: str = "", probes: bool = True) -> None:
        if not self.source:
            raise RuntimeError("Connect a source first.")
        if self.reference is None:
            raise RuntimeError("Calibrate first, so the session has a frozen reference.")
        if self.session:
            raise RuntimeError("A session is already running.")
        if self.calibration and "failed" not in self.calibration:
            raise RuntimeError("Calibration is still running; start recording when it finishes.")
        self.recorder = Recorder(self.sessions_dir, label or "session", {
            "settings": self.settings, "map": self.smap.to_dict(),
            "reference": self.reference.__dict__, "source": self.source.status(),
        })
        self.recorder.set_t0(now())
        self.state_engine = StateEngine(self.smap, self.reference, self.settings)
        self.session = {"label": label, "folder": str(self.recorder.folder), "started": self.rel(now()),
                        "probes": probes, "n_probes": 0}
        self._probe_next = self._schedule_probe() if probes else None
        self.event("session_start", {"label": label, "probes": probes, "preset": self.source.preset})
        self.log(f"Recording to {self.recorder.folder.name}.")
        self.push_status()

    async def end_session(self) -> None:
        if not self.session:
            return
        if self.protocol and self.protocol.state not in ("done", "stopped"):
            self.protocol.cancelled = True
            await asyncio.sleep(0.3)
        if self.runner:
            self.stop_recipe()
        if getattr(self, "booth", None):
            self.event("booth_end", {"summary": {"ended_early": True, "reason": "session ended"}})
            self.booth = None
            self.broadcast({"type": "level_aborted"})
        if getattr(self, "attention", None):
            self.event("attention_end", {"summary": {"ended_early": True, "reason": "session ended"}})
            self.attention = None
            self.broadcast({"type": "level_aborted"})
        if self.level:  # a level cut short still reveals its allocation into the record
            lv, self.level = self.level, None
            self.event("level_reveal", {"level": lv["id"], "arms": lv["arms"], "sound": lv.get("sound"), "carry": lv.get("carry"), "search": lv.get("search"), "salt": lv["salt"],
                                        "sealed_sha256": lv["digest"], "ended_early": True})
            self.broadcast({"type": "level_aborted"})
        for fut in self._questions.values():
            if not fut.done():
                fut.set_result(None)
        self.event("session_end", {})
        self.recorder.close({"n_probes": self.session.get("n_probes", 0),
                             "light": self.protocol.public() if self.protocol else None,
                             "settings_at_end": self.settings, "map_at_end": self.smap.to_dict()})
        try:
            from .analysis.summary import write_summary
            write_summary(self.recorder.folder)
            if (self.recorder.folder / "level.csv").exists():  # what the level did, as a page
                from .analysis.levels import write_session_report
                write_session_report(self.recorder.folder)
        except Exception as exc:  # a summary must never cost you the recording
            self.log(f"Summary not written: {exc}")
        self.log(f"Session saved: {self.recorder.folder.name}.")
        self.broadcast({"type": "session_saved", "name": self.recorder.folder.name})
        self.recorder = None
        self.session["ended"] = True
        self.session = None
        self._probe_next = None
        self.push_status()

    # ------------------------------------------------------------ questions
    def _schedule_probe(self) -> float:
        p = self.settings["probes"]
        return now() + random.uniform(float(p["min_interval_s"]), float(p["max_interval_s"]))

    async def ask(self, kind: str, extra: dict, timeout: float = 30.0) -> Optional[str]:
        qid = f"{kind}-{int(now() * 1000)}"
        fut = asyncio.get_running_loop().create_future()
        self._questions[qid] = fut
        t_prompt = now()
        self.event("question", {"id": qid, "question": kind, **extra, "t": t_prompt})
        self.broadcast({"type": "question", "id": qid, "kind": kind, **extra})
        self._maybe_auto_answer(qid, kind)
        try:
            answer = await asyncio.wait_for(fut, timeout)
        except asyncio.TimeoutError:
            answer = None
        self._questions.pop(qid, None)
        self.event("answer", {"id": qid, "question": kind, "answer": answer, "t_prompt": t_prompt})
        self.broadcast({"type": "question_closed", "id": qid})
        return answer

    def _maybe_auto_answer(self, qid: str, kind: str) -> None:
        acc = float(self.settings["simulator"].get("auto_probe_accuracy", 0.0))
        if kind != "probe" or acc <= 0 or not hasattr(self.source, "hidden_state"):
            return
        truth = self.source.hidden_state()
        other = "drifting" if truth == "aware" else "aware"
        ans = truth if random.random() < acc else other

        def _answer():
            fut = self._questions.get(qid)
            if fut and not fut.done():
                fut.set_result(ans)

        asyncio.get_running_loop().call_later(1.0, _answer)

    def answer(self, qid: str, value: Optional[str]) -> None:
        fut = self._questions.get(qid)
        if fut and not fut.done():
            fut.set_result(value)

    async def _run_probe(self) -> None:
        self._probe_open = "open"
        ans = await self.ask("probe", {})
        if self.session is not None:
            self.session["n_probes"] = self.session.get("n_probes", 0) + 1
            self.state_engine.returns.mark(now(), "probe")
        self._probe_open = None
        self._probe_next = self._schedule_probe() if self._probes_allowed() else None
        self.push_status()
        return ans

    def _probes_allowed(self) -> bool:
        """Random probes run only in plain recording, not during light trials or recipes."""
        light_on = self.protocol is not None and self.protocol.state not in ("done", "stopped")
        return bool(self.session and self.session.get("probes") and not light_on and self.runner is None
                    and not self.level and not getattr(self, "booth", None))

    def mark(self, label: str, by: str = "you") -> None:
        """A named marker in the recording (e.g. 'eyes closed', 'music on')."""
        self.event("mark", {"label": str(label)[:200], "by": by})
        self.log(f"Marker: {label}" + (f"  ({by})" if by != "you" else ""))
        if self.session:
            self.state_engine.returns.mark(now(), f"mark:{label}")

    def self_caught(self) -> None:
        if self.session:
            self.event("self_caught", {})
            self.state_engine.returns.mark(now(), "self_caught")

    # ------------------------------------------------------------ levels (games that are tests)
    # The Search: which shape of your brain's activity is clarity? Each candidate is a hypothesis
    # about the target state; the scene steers towards one of them per round, sealed, and you say
    # how clear your mind is, while faint lights measure how clearly you actually perceive.
    SEARCH_CANDIDATES = {
        "symmetry": "side to side balance (left and right alike)",
        "axis": "front to back balance",
        "coherence": "waves moving together across the head",
        "calm": "alpha: relaxed alertness",
        "flow": "forehead theta: absorbed",
        "focus": "beta over alpha and theta: engaged",
        "openness": "complexity: rich, open activity",
    }

    def _search_targets(self) -> dict:
        try:
            return json.loads((self.data_dir() / "profiles" / "search_latest.json").read_text(encoding="utf-8")).get("targets") or {}
        except (OSError, ValueError):
            return {}

    def _search_schedule(self) -> list:
        """Eight 60 s rounds: two free (nothing steered) and six candidates, favouring those whose
        evidence is still uncertain (Thompson sampling on earlier sessions), in a sealed order."""
        cands = list(self.SEARCH_CANDIDATES)
        weights = {c: 1.0 for c in cands}
        try:
            prof = json.loads((self.data_dir() / "profiles" / "search_latest.json").read_text(encoding="utf-8"))
            for c, e in (prof.get("steer") or {}).items():
                if c in weights and e.get("n_rounds"):
                    m, se = e.get("diff") or 0.0, e.get("se") or 1.0
                    weights[c] = max(0.05, random.gauss(m, se) + 2.0)  # a draw from each candidate's evidence
        except (OSError, ValueError, KeyError, TypeError):
            pass
        pick = sorted(cands, key=lambda c: -weights[c] * random.random())[:6]
        sched = pick + ["free", "free"]
        random.shuffle(sched)
        return sched

    async def search_start(self, by: str = "you") -> dict:
        return await self.level_start(str(self.settings.get("levels", {}).get("search_scene", "still")), by=by, search=True)

    async def level_start(self, level_id: str, rounds: int = 3, round_s: float = 60.0, settle_s: float = 20.0,
                    by: str = "you", search: bool = False) -> dict:
        """Start a level: sealed allocation of real and sham rounds, recorded as its own session
        unless you are already recording. The display runs the level and reports back."""
        from . import media
        lv = next((l for l in media.manifest()["levels"] if l["id"] == level_id), None)
        if lv is None:
            raise RuntimeError(f"No level called {level_id!r}.")
        if self.reference is None:
            raise RuntimeError("Calibrate first: every level is scaled to your own reference.")
        if not any(l["id"] == level_id and l["media"]["ready"] for l in media.listing()):
            raise RuntimeError(f"Level {lv['number']} has no footage yet. Open Levels and press Get footage.")
        if getattr(self, "attention", None):
            raise RuntimeError("The attention map is running.")
        if getattr(self, "level", None):
            # the display that ran it is gone (window closed or reloaded mid-level): close it out
            old = self.level
            self.event("level_end", {"level": old["id"], "summary": {"ended_early": True, "reason": "replaced"}})
            self.event("level_reveal", {"level": old["id"], "arms": old["arms"], "sound": old.get("sound"), "carry": old.get("carry"), "search": old.get("search"), "salt": old["salt"],
                                        "sealed_sha256": old["digest"]})
            self.level = None
            if old["auto_session"] and self.session:  # its own session ends with it
                await self.end_session()
        L = self.settings.get("levels", {})
        journey = str(L.get("replay", "off")) != "one" and not search
        schedule = None
        if search:
            schedule = self._search_schedule()
            rounds, n_sham, arms = len(schedule), 0, ["real"] * len(schedule)
            round_s, settle_s = float(L.get("search_round_s", 60.0)), 25.0
        elif journey:
            # the journey: one continuous run, no replay round (you can tell a replay at once, so it
            # no longer blinds anything). What is tested instead is the carry: at each fall a sealed
            # coin decides whether the scene, music and pulse lift you or simply follow you.
            rounds, n_sham, arms = 1, 0, ["real"]
            round_s = float(L.get("journey_s", 180))
            settle_s = min(settle_s, 20.0)
        else:
            rounds = max(2, min(8, int(rounds)))
            n_sham = max(1, rounds // 3)
            # the replay ("sham") rounds replay an earlier real round, so the first round is always real
            rest = ["real"] * (rounds - n_sham - 1) + ["sham"] * n_sham
            random.shuffle(rest)
            arms = ["real"] + rest
        share = 0.0 if search else float(L.get("carry", 0.75))   # no carry in the Search: it would confound
        carry = [random.random() < share for _ in range(60)]
        # sound condition per round: the level's rhythmic tone at its target rhythm ("entrain")
        # or the same pulses at irregular intervals ("control"), balanced over the real rounds
        au = self.settings.get("audio", {})
        hz = float(lv.get("entrain_hz") or 0) if au.get("enabled", True) else 0.0
        mode = str(au.get("entrain", "sealed"))
        sound = ["none"] * rounds
        if hz and mode == "on":
            sound = ["entrain"] * rounds
        elif hz and mode == "sealed":
            real_idx = [i for i, a in enumerate(arms) if a == "real"]
            pool = (["entrain", "control"] * len(real_idx))[:len(real_idx)]
            random.shuffle(pool)
            for i, c in zip(real_idx, pool):
                sound[i] = c
            for i, a in enumerate(arms):
                if a != "real":
                    sound[i] = random.choice(["entrain", "control"])
        salt = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
        digest = hashlib.sha256(json.dumps({"arms": arms, "sound": sound, "carry": carry, "search": schedule, "salt": salt}).encode()).hexdigest()
        contract = lv.get("contract_sha256")
        auto = False
        if not self.session:
            self.start_session(label=f"level-{level_id}", probes=False)
            auto = True
        self.level = {"id": level_id, "arms": arms, "sound": sound, "carry": carry, "search": schedule, "entrain_hz": hz, "salt": salt, "digest": digest, "auto_session": auto,
                      "rounds": rounds, "round_s": round_s, "settle_s": settle_s, "started": self.rel(now())}
        self.event("level_start", {"level": level_id, "rounds": rounds, "round_s": round_s, "settle_s": settle_s,
                                   "journey": journey, "carry_share": share, "ease": float(L.get("ease", 0.6)),
                                   "smooth_s": float(L.get("smooth_s", 5.0)), "search": bool(search),
                                   "entrain_hz": hz, "entrain_mode": mode, "audio": au, "contract_sha256": contract,
                                   "sealed_sha256": digest, "by": by})
        lv = next((l for l in media.listing() if l["id"] == level_id), lv)  # with its footage
        if not lv.get("media", {}).get("ready"):
            self.level = None
            raise RuntimeError(f"Level {lv['number']} has no footage yet. Open Levels and press Get footage.")
        # your attention signature replaces the textbook index when it has passed its gate
        profile = None
        pc = lv.get("profile")
        tgt = "auto" if search else str(self.settings.get("levels", {}).get("target", "auto"))
        if tgt.startswith("booth:"):
            # your own felt state from the listening booth, if its signature passed its gate
            try:
                bp = json.loads((self.data_dir() / "profiles" / "booth_latest.json").read_text(encoding="utf-8"))
                lvr = bp["levers"].get(tgt.split(":", 1)[1])
                if lvr and lvr.get("passes_gate"):
                    profile = {"contrast": tgt, "sign": 1, "model": lvr["model"], "auc": lvr.get("heldout_r"),
                               "session": bp.get("latest_session")}
                else:
                    self.log(f"Your booth signature for {tgt[6:]} hasn't passed its test yet; using the level's own target.")
            except (OSError, ValueError, KeyError):
                self.log("No booth signature yet; using the level's own target.")
        if pc and profile is None and not tgt.startswith("booth:") and not search:
            try:
                prof = json.loads((self.data_dir() / "profiles" / "attention_latest.json").read_text(encoding="utf-8"))
                c = prof["contrasts"].get(pc["contrast"])
                if c and c.get("passes_gate") and self.settings.get("levels", {}).get("use_profile", True):
                    profile = {"contrast": pc["contrast"], "sign": pc.get("sign", 1), "model": c["model"],
                               "auc": c.get("heldout_auc"), "session": prof.get("session")}
            except (OSError, ValueError, KeyError):
                profile = None
        self.event("level_index", {"level": level_id, "index": "profile:" + profile["contrast"] if profile else lv.get("index"),
                                   "profile_session": profile and profile["session"], "profile": profile})
        self.broadcast({"type": "level_plan", "level": lv, "arms": arms, "sound": sound, "entrain_hz": hz, "profile": profile,
                        "journey": journey, "carry": carry, "ease": float(L.get("ease", 0.6)), "smooth_s": float(L.get("smooth_s", 5.0)),
                        "search": {"schedule": schedule, "labels": self.SEARCH_CANDIDATES, "targets": self._search_targets()} if search else None,
                        "music_style": str(L.get("music_style", "scene")),
                        "best": self.bests().get(level_id),
                        "audio": au, "rounds": rounds, "round_s": round_s,
                        "settle_s": settle_s, "digest": digest})
        self.log("The Search started (8 rounds, sealed)." if search else f"Level {lv['number']} · {lv['title']} started " + (f"(journey, {round_s:.0f} s, carry sealed)." if journey else f"({rounds} rounds, {n_sham} sham, sealed)."))
        return self.level

    def level_event(self, kind: str, data: dict) -> None:
        self.event(f"level_{kind}"[:40], dict(data), public=False)

    LEVEL_COLUMNS = ["t", "level", "round", "arm", "phase", "tier", "x_fast", "z", "z_live", "z_ref", "z_eng", "gate",
                     "F", "Fe", "conf", "a", "c", "l", "q", "h", "n", "p", "warning", "blink", "speed",
                     "emg", "effort", "breath_sync", "breath_bpm", "sound", "admissible", "pressure", "tau",
                     "video_t", "carry", "cand", "z_symmetry", "z_axis", "z_coherence", "z_calm", "z_flow", "z_focus",
                     "z_openness", "event"]

    def level_samples(self, rows: list) -> None:
        if not self.recorder:
            return
        base = self.t_origin
        for r in rows[:400]:
            row = {k: r.get(k) for k in self.LEVEL_COLUMNS}
            row["t"] = round(base + float(r.get("t", 0.0)), 4)
            self.recorder._table("level", self.LEVEL_COLUMNS, row)

    def bests(self) -> dict:
        try:
            return json.loads((self.data_dir() / "profiles" / "bests.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def _update_bests(self, level_id: str, summary: dict) -> None:
        """Personal bests per level: highest tier held and fastest return (real rounds only)."""
        b = self.bests()
        cur = b.get(level_id, {"runs": 0})
        real = [r for r in summary.get("rounds", []) if r.get("arm") == "real"]
        tiers = [r.get("max_tier") or 1 for r in real]
        recs = [x for r in real for x in (r.get("recoveries_s") or []) if x is not None and x < 15]
        cur["runs"] = cur.get("runs", 0) + 1
        if tiers and max(tiers) > cur.get("best_tier", 0):
            cur["best_tier"] = max(tiers)
            cur["best_tier_name"] = next((r.get("max_tier_name") for r in real if (r.get("max_tier") or 1) == max(tiers)), None)
            cur["best_tier_date"] = time.strftime("%Y-%m-%d")
        if recs and min(recs) < cur.get("fastest_return_s", 1e9):
            cur["fastest_return_s"] = round(min(recs), 2)
        b[level_id] = cur
        d = self.data_dir() / "profiles"
        d.mkdir(parents=True, exist_ok=True)
        (d / "bests.json").write_text(json.dumps(b, indent=1), encoding="utf-8")

    async def level_end(self, summary: dict) -> None:
        lv = getattr(self, "level", None)
        if not lv:
            return
        if not summary.get("ended_early"):
            try:
                self._update_bests(lv["id"], summary)
            except Exception as exc:
                self.log(f"Personal bests not updated: {exc}")
        self.event("level_end", {"level": lv["id"], "summary": summary})
        self.event("level_reveal", {"level": lv["id"], "arms": lv["arms"], "sound": lv.get("sound"), "carry": lv.get("carry"), "search": lv.get("search"), "salt": lv["salt"],
                                    "sealed_sha256": lv["digest"]})
        self.level = None
        self.log(f"Level {lv['id']} finished. Allocation revealed and saved.")
        if lv["auto_session"] and self.session:
            await self.end_session()
        if lv.get("search"):
            try:
                from .analysis.search import build_search_profile
                prof = await asyncio.get_running_loop().run_in_executor(None, build_search_profile, self.sessions_dir, self.data_dir())
                self.broadcast({"type": "search_done", "leaders": prof.get("leaders"), "sessions": prof.get("sessions")})
            except Exception as exc:
                self.log(f"Search not analysed yet: {exc}")

    # ------------------------------------------------------------ attention map (calibrating how you focus)
    ATTN_COLUMNS = ["t", "task", "block", "cond", "phase", "event", "x", "y", "rt", "roi_blur", "video_t"]

    async def attention_start(self, by: str = "you") -> dict:
        """Start the attention map: labelled focus/free/narrow/broad blocks with a behavioural
        check. Recorded as its own session; the profile is worked out when it ends."""
        from . import media
        tasks = media.listing("attention")
        if not tasks:
            raise RuntimeError("No attention tasks are declared in levels.json.")
        missing = [t["title"] for t in tasks if not t["media"]["ready"]]
        if missing:
            raise RuntimeError("Footage missing for: " + ", ".join(missing) + ". Press Get footage first.")
        if getattr(self, "level", None):
            raise RuntimeError("A level is running.")
        if getattr(self, "attention", None):  # left over from a window that closed mid-run
            old = self.attention
            self.event("attention_end", {"summary": {"ended_early": True, "reason": "replaced"}})
            self.attention = None
            if old["auto_session"] and self.session:
                await self.end_session()
        auto = False
        if not self.session:
            self.start_session(label="attention-map", probes=False)
            auto = True
        seed = int.from_bytes(os.urandom(4), "little")
        self.attention = {"auto_session": auto, "seed": seed, "started": self.rel(now())}
        self.event("attention_start", {"tasks": [{k: t[k] for k in ("id", "roi", "blocks")} for t in tasks], "seed": seed, "by": by})
        self.broadcast({"type": "attention_plan", "tasks": tasks, "seed": seed})
        self.log("Attention map started.")
        return self.attention

    def attention_event(self, kind: str, data: dict) -> None:
        self.event(f"attn_{kind}"[:40], dict(data), public=False)

    def attention_samples(self, rows: list) -> None:
        if not self.recorder:
            return
        base = self.t_origin  # the display speaks session-relative time; tables use the session clock
        for r in rows[:600]:
            row = {k: r.get(k) for k in self.ATTN_COLUMNS}
            row["t"] = round(base + float(r.get("t", 0.0)), 4)
            self.recorder._table("attention", self.ATTN_COLUMNS, row)

    async def attention_end(self, summary: dict) -> None:
        a = getattr(self, "attention", None)
        if not a:
            return
        self.event("attention_end", {"summary": summary})
        self.attention = None
        folder = self.recorder.folder if self.recorder else None
        if a["auto_session"] and self.session:
            await self.end_session()
        if folder is not None and not summary.get("ended_early"):
            try:
                from .analysis.attention import build_profile
                prof = await asyncio.get_running_loop().run_in_executor(None, build_profile, folder, self.data_dir())
                self.broadcast({"type": "attention_done", "session": folder.name,
                                "summary": {k: prof.get(k) for k in ("made", "gate", "behaviour")}})
                self.log("Attention profile saved.")
            except Exception as exc:
                self.log(f"Attention profile not made: {exc}")

    # ------------------------------------------------------------ the listening booth (your experience, read)
    BOOTH_COLUMNS = ["t", "flow", "presence", "horizon", "moving", "peak", "music", "music_t", "music_level", "event"]

    def music_dir(self) -> Path:
        d = self.data_dir() / "music"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def music_list(self) -> list:
        exts = {".mp3", ".ogg", ".wav", ".m4a", ".flac", ".aac", ".opus", ".webm"}
        return sorted(p.name for p in self.music_dir().iterdir() if p.is_file() and p.suffix.lower() in exts)

    async def booth_start(self, by: str = "you") -> dict:
        """The listening booth: music, three levers for how you feel, and the headband simply
        read (nothing on screen follows your brain). Recorded as its own session."""
        if getattr(self, "level", None) or getattr(self, "attention", None):
            raise RuntimeError("A level or the attention map is running.")
        if getattr(self, "booth", None):  # left over from a window that closed mid-listen
            old = self.booth
            self.event("booth_end", {"summary": {"ended_early": True, "reason": "replaced"}})
            self.booth = None
            if old["auto_session"] and self.session:
                await self.end_session()
        auto = False
        if not self.session:
            self.start_session(label="booth", probes=False)
            auto = True
        self.booth = {"auto_session": auto, "started": self.rel(now())}
        self.event("booth_start", {"by": by, "levers": ["flow", "presence", "horizon"],
                                   "scale": "0 = none (top), 0.5 = as usual (centre), 1 = full (bottom)"})
        self.broadcast({"type": "booth_plan", "music": self.music_list(), "best": None})
        self.log("Listening booth started.")
        return self.booth

    def booth_event(self, kind: str, data: dict) -> None:
        self.event(f"booth_{kind}"[:40], dict(data), public=False)

    def booth_samples(self, rows: list) -> None:
        if not self.recorder:
            return
        base = self.t_origin
        for r in rows[:600]:
            row = {k: r.get(k) for k in self.BOOTH_COLUMNS}
            row["t"] = round(base + float(r.get("t", 0.0)), 4)
            self.recorder._table("booth", self.BOOTH_COLUMNS, row)

    async def booth_end(self, summary: dict) -> None:
        b = getattr(self, "booth", None)
        if not b:
            return
        self.event("booth_end", {"summary": summary})
        self.booth = None
        folder = self.recorder.folder if self.recorder else None
        if b["auto_session"] and self.session:
            await self.end_session()
        if folder is not None and summary.get("reason") != "not started":
            try:
                from .analysis.booth import build_booth_profile
                prof = await asyncio.get_running_loop().run_in_executor(None, build_booth_profile, self.sessions_dir, self.data_dir())
                self.broadcast({"type": "booth_done", "session": folder.name,
                                "summary": {k: prof.get(k) for k in ("made", "sessions", "gate", "levers")}})
                self.log("Booth analysed: your experience map is updated.")
            except Exception as exc:
                self.broadcast({"type": "booth_done", "session": folder.name, "error": str(exc)})
                self.log(f"Booth not analysed yet: {exc}")

    def home_info(self) -> dict:
        """What the Home screen shows on each door."""
        prof = self.data_dir() / "profiles"
        out: Dict[str, Any] = {"target": self.settings.get("levels", {}).get("target", "auto")}
        try:
            b = json.loads((prof / "booth_latest.json").read_text(encoding="utf-8"))
            out["booth"] = {"sessions": len(b.get("sessions", [])), "minutes": b.get("minutes"),
                            "levers": {k: {"title": v.get("title"), "verdict": v.get("verdict"), "r": v.get("heldout_r"),
                                           "passes": v.get("passes_gate")} for k, v in b.get("levers", {}).items()}}
        except (OSError, ValueError):
            out["booth"] = None
        try:
            sp = json.loads((prof / "search_latest.json").read_text(encoding="utf-8"))
            out["search"] = {"searches": len(sp.get("sessions", [])), "top": sp.get("top"), "status": sp.get("status")}
        except (OSError, ValueError):
            out["search"] = None
        try:
            a = json.loads((prof / "attention_latest.json").read_text(encoding="utf-8"))
            out["attention"] = {"made": a.get("made"), "gate": a.get("gate")}
        except (OSError, ValueError):
            out["attention"] = None
        try:
            out["level_sessions"] = sum(1 for p in self.sessions_dir.glob("*level-*") if (p / "level.csv").exists())
            out["booth_sessions"] = sum(1 for p in self.sessions_dir.glob("*booth*") if (p / "booth.csv").exists())
        except OSError:
            out["level_sessions"] = out["booth_sessions"] = 0
        return out

    def data_dir(self):
        return self.sessions_dir.parent

    # ------------------------------------------------------------ MRE random-bit logging
    def mre_folder(self) -> Path:
        return self.data_dir() / "mre"

    def mre_context(self) -> dict:
        """What the bit logger tags each 100 ms bin with. Read from the logger's thread."""
        src = self.source
        connected = bool(src is not None and getattr(src, "connected", False))
        live = connected and getattr(src, "kind", "") in ("athena", "lsl")
        fresh = bool(self._last_vals) and now() - getattr(self, "_t_tick_now", 0.0) < 2.0
        task = ""
        if self.session:
            task = ("level:" + self.level["id"]) if self.level else "attention" if getattr(self, "attention", None) \
                else "booth" if getattr(self, "booth", None) \
                else "light" if (self.protocol and self.protocol.state not in ("done", "stopped")) \
                else "recipe" if self.runner else "recording"
        vals = self._last_vals or {}
        return {"connected": connected, "eeg": live and fresh,
                "session": Path(self.session["folder"]).name if self.session else "",
                "task": task, "phi": vals.get("phi_ctw"), "phi_raw": vals.get("phi_ctw_raw"),
                "clean": bool((self._last_state or {}).get("clean")) and fresh}

    def mre_restart(self) -> None:
        """(Re)start the bit loggers from settings.mre: the device under test and a control arm."""
        import threading
        from .mre.qrng import BitLogger, make_source

        def work():
            for lg in list(getattr(self, "mre_loggers", {}).values()):
                lg.stop()
            cfg = self.settings.get("mre", {})
            loggers = {}
            for tag, which in (("main", "source"), ("control", "control")):
                src = make_source(cfg, which)
                if src is not None:
                    loggers[tag] = BitLogger(self.mre_folder(), src, self.mre_context, self.log, tag)
                    loggers[tag].start()
            self.mre_loggers = loggers
            self.push_status()
        threading.Thread(target=work, daemon=True, name="mre-restart").start()

    def mre_stop(self) -> None:
        for lg in list(getattr(self, "mre_loggers", {}).values()):
            lg.stop()

    def mre_status(self) -> dict:
        cfg = self.settings.get("mre", {})
        return {"source": cfg.get("source", "off"), "control": cfg.get("control", "off"),
                "keep_running": bool(cfg.get("keep_running", True)),
                "loggers": {t: dict(lg.stats) for t, lg in getattr(self, "mre_loggers", {}).items()}}

    def mre_keep_alive(self) -> bool:
        return bool(self.settings.get("mre", {}).get("keep_running", True)) and any(
            lg.stats.get("state") in ("running", "starting") for lg in getattr(self, "mre_loggers", {}).values())

    # ------------------------------------------------------------ light trials
    def start_light(self, phase: str, bench: bool = False) -> None:
        if not self.session:
            raise RuntimeError("Start a session first so the trials are recorded.")
        if self.protocol and self.protocol.state not in ("done", "stopped"):
            raise RuntimeError("Light trials are already running.")
        self.protocol = LightTrialProtocol(
            self.settings, phase, self.source, self.recorder.folder,
            emit=lambda k, d: self.event(k, d), ask_guess=lambda i: self.ask("guess", {"trial": i}),
            mark_event=lambda kind: self.state_engine.returns.mark(now(), kind), bench=bench,
        )
        self.event("light_sealed", {"sha256": self.protocol.digest, "phase": phase, "bench": bench})
        self._probe_next = None
        self._tasks.append(asyncio.create_task(self._light_task()))
        self.push_status()

    async def _light_task(self) -> None:
        try:
            await self.protocol.run()
        except Exception as exc:
            self.protocol.state = "stopped"
            self.log(f"Light trials stopped: {exc}")
        self.log(f"Light trials {self.protocol.state}. Reveal the allocation when you are ready.")
        if self._probes_allowed():
            self._probe_next = self._schedule_probe()
        self.push_status()

    def stop_light(self) -> None:
        if self.protocol:
            self.protocol.cancelled = True

    def reveal(self) -> dict:
        if not self.protocol:
            raise RuntimeError("No light trials to reveal.")
        sealed = self.protocol.reveal()
        self.event("reveal", {"arms": sealed["arms"], "phase": sealed["phase"]})
        self.broadcast({"type": "reveal", **sealed})
        return sealed

    # ------------------------------------------------------------ knobs
    def knob_list(self) -> list:
        return knobs.describe(self.settings, self.smap.to_dict())

    def set_knob(self, path: str, value, by: str = "you") -> dict:
        if path.startswith("map."):
            d = self.smap.to_dict()
            old, new = knobs.set_value(d, path[4:], value, full=path)
            self.smap = StateMap(**{**d, "axes": [recipes_axis(a) for a in d["axes"]]})
        else:
            old, new = knobs.set_value(self.settings, path, value)
        if path == "state.map":
            try:
                self.smap = StateMap.load(self.maps_dir / f"{new}.json")
            except Exception as exc:
                knobs.set_value(self.settings, path, old)
                raise ValueError(f"No map called {new!r} in the maps folder ({exc})")
        if path.startswith("mre.") and path.split(".")[1] in ("source", "control", "port", "mode", "anu_key",
                                                                 "bits_per_bin", "sham_seed"):
            self.mre_restart()
        quiet = path.startswith(("display.", "control."))
        if not quiet:
            self.rebuild()
        self.event("knob", {"path": path, "old": old, "new": new, "by": by}, public=not quiet)
        if quiet:
            self.broadcast({"type": "display", "display": self.settings.get("display", {}), "by": by})
        else:
            self.log(f"{path}: {old} → {new}" + (f"  ({by})" if by != "you" else ""))
            self.push_status()
        return {"path": path, "old": old, "new": new}

    def rebuild(self) -> None:
        """Rebuild the processing chain after a knob change; the frozen reference is kept."""
        self.features = build_all(self.settings)
        old = self.state_engine
        self.state_engine = StateEngine(self.smap, self.reference, self.settings)
        for k in ("residue", "_dhist", "_mre", "_zs", "_slow", "_t_prev", "returns"):
            setattr(self.state_engine, k, getattr(old, k))
        if hasattr(self.source, "ir_effect"):
            sim = self.settings["simulator"]
            self.source.ir_effect = float(sim.get("ir_effect", 0.0))
            self.source.artifact_uv = float(sim.get("switch_artifact_uv", 80.0))

    def save_knobs(self) -> str:
        with open(self.maps_dir / "custom.json", "w", encoding="utf-8") as f:
            json.dump({**self.smap.to_dict(), "name": "custom"}, f, indent=1)
        self.settings["state"]["map"] = "custom"
        from .config import DATA_DIR
        with open(DATA_DIR / "settings.json", "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=1)
        self.log("Saved all knobs to settings.json and the map to maps/custom.json.")
        return "settings.json"

    # ------------------------------------------------------------ recipes
    def recipe_list(self) -> dict:
        return recipes.load_folder(self.recipes_dir)

    def save_recipe(self, recipe: dict) -> str:
        r = recipes.validate(recipe)
        safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in r["name"].strip())[:60]
        path = self.recipes_dir / f"{safe}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(recipe, f, indent=1)
        self.log(f"Recipe saved: {path.name}")
        return path.name

    async def start_recipe(self, name: str, bench: bool = False, covered: bool = False) -> None:
        if not self.session:
            raise RuntimeError("Start a recording first so the recipe's triggers are saved.")
        if self.runner and self.runner.state == "watching":
            raise RuntimeError("A recipe is already running. Stop it first.")
        if self.protocol and self.protocol.state not in ("done", "stopped"):
            raise RuntimeError("Light trials are running. Stop them first.")
        rec = self.recipe_list().get(name)
        if rec is None or "_error" in rec:
            raise RuntimeError(rec.get("_error") if rec else f"No recipe called {name!r}.")
        runner = recipes.RecipeRunner(self, {k: v for k, v in rec.items() if not k.startswith("_")},
                                      self.recorder.folder, emit=lambda k, d: self.event(k, d),
                                      bench=bench, covered=covered)
        self.event("recipe_sealed", {"sha256": runner.digest, "name": name, "run_id": runner.run_id,
                                     "bench": bench, "covered": covered})
        await runner.start()
        self.runner = runner
        self._probe_next = None
        self.log(f"Recipe '{name}' watching. {runner.public()['pattern']}")
        self.push_status()

    def stop_recipe(self) -> None:
        if self.runner:
            self.runner.stop()
            self.last_runner = self.runner
            self.runner = None
            if self._probes_allowed():
                self._probe_next = self._schedule_probe()
            self.push_status()

    def reveal_recipe(self) -> dict:
        r = self.runner or self.last_runner
        if r is None:
            raise RuntimeError("No recipe run to reveal.")
        sealed = r.reveal()
        self.event("recipe_reveal", {"run_id": r.run_id, "arms": sealed["arms"]})
        self.broadcast({"type": "recipe_reveal", "name": r.r["name"], "arms": sealed["arms"]})
        return sealed

    async def test_fire(self, actuator: str, pattern: dict, sham: bool = False) -> dict:
        """Fire one pattern by hand (for bench checks). Logged, never counted as a trial."""
        a = act.make(self, actuator)
        segs = a.check(pattern)
        await a.open()
        self.event("test_fire", {"actuator": actuator, "pattern": pattern, "sham": sham, **act.summary(segs)})
        res = await a.fire(segs, sham)
        if actuator == "external_led":
            await a.close()
        return {**act.summary(segs), "seconds": round(res["t_end"] - res["t_start"], 3)}

    # ------------------------------------------------------------ main loop
    async def run(self) -> None:
        from .control import ControlBridge
        if self._startup_note:
            self.log(self._startup_note)
        if self.settings.get("control", {}).get("enabled", True):
            self.bridge = ControlBridge(self)
            self._tasks.append(asyncio.create_task(self.bridge.run()))
        self.mre_restart()
        tick = 1.0 / float(self.settings["signal"]["tick_hz"])
        next_tick = now()
        while True:
            await asyncio.sleep(0.1)
            self._send_raw()
            t = now()
            if t < next_tick:
                continue
            next_tick += tick
            if next_tick < t:
                next_tick = t + tick
            if self.source is None:
                continue
            link = (bool(self.source.connected), bool(getattr(self.source, "reconnecting", False)))
            if link != getattr(self, "_link", link):
                self.event("link", {"connected": link[0], "reconnecting": link[1]})
                self.push_status()
            self._link = link
            try:
                self._tick(t)
            except Exception as exc:  # keep the loop alive; report once per failure
                self.log(f"Processing error: {exc}")

    def _tick(self, t: float) -> None:
        vals: Dict[str, float] = {}
        flags: Dict[str, Any] = {}
        for feat in self.features:
            v, f = feat.compute(self.buffers, t)
            vals.update(v)
            flags.update(f)
        st = self.state_engine.update(t, vals, flags)
        self._last_state, self._last_flags, self._last_vals = st, flags, vals
        self._update_sensor_rates(flags)
        chosen = self._usable_sensors()
        st["sensor_ok"] = [round(r, 2) for r in (getattr(self, "_ok_rate", None) or [0.0] * 4)]
        st["can_calibrate"] = len(chosen) >= 2 and any(i in chosen for i in (1, 2))
        prev_tick = getattr(self, "_t_tick_now", t)
        self._t_last_tick, self._t_tick_now = prev_tick, t
        if self.runner:
            self.runner.on_tick(t, st, vals)
            if self.runner.state in ("done", "stopped"):
                self.stop_recipe()
        cal = self.calibration
        if cal and "failed" not in cal and not vals:
            # no signal (Bluetooth gap, reconnecting): the calibration waits
            cal["paused"] = True
        elif cal and "failed" not in cal:
            cal.pop("paused", None)
            dt_tick = min(1.0, t - getattr(self, "_t_last_tick", t)) or 0.25
            self._cal_elapsed += dt_tick
            self._builder.add(vals, st["clean"])
            clean_s = len(self._builder.rows) / float(self.settings["signal"]["tick_hz"])
            cal.update({"clean": len(self._builder.rows), "total": self._builder.total, "clean_s": round(clean_s, 1),
                        "elapsed": round(self._cal_elapsed, 1), "progress": round(min(1.0, clean_s / cal["seconds"]), 3),
                        "holding": [] if st["clean"] else list(st.get("reasons", []))})
            if clean_s >= cal["seconds"]:
                self._finish_calibration()
            elif self._cal_elapsed >= cal["limit"]:
                self._builder.min_clean = 1.0  # force the explanatory failure
                self._finish_calibration()
        if self.recorder:
            if vals:
                self.recorder.features(t, vals, flags)
            if st.get("calibrated"):
                self.recorder.state(st, self.smap.features)
        if self.session and self._probe_next and not self._probe_open and t >= self._probe_next:
            self._probe_open = "pending"
            self._tasks.append(asyncio.create_task(self._run_probe()))
        battery = self.buffers.get("BATTERY")
        msg = {
            "type": "tick", "t": self.rel(t),
            "state": {k: v for k, v in st.items() if k != "t"},
            "features": {k: round(v, 4) for k, v in vals.items()},
            "flags": {k: v for k, v in flags.items()},
            "calibration": self.calibration,
            "battery": float(battery.latest(1)[1][0, 0]) if battery and battery.total else None,
            "preset": self.source.preset if self.source else None,
        }
        self.broadcast(msg)

    def _send_raw(self) -> None:
        if not self.clients:
            return
        out = {"type": "raw"}
        for name, step in (("EEG", 1), ("OPTICS", 1)):
            buf = self.buffers.get(name)
            if buf is None:
                continue
            seen = self._raw_seen.get(name, max(0, buf.total - int(buf.rate)))
            t, x, total = buf.since(seen)
            self._raw_seen[name] = total
            if len(t) == 0:
                continue
            x = x[::step]
            out[name.lower()] = {"channels": buf.channels, "rate": buf.rate / step, "total": total,
                                 "t_end": self.rel(float(t[-1])), "data": np.round(x, 2).tolist()}
        if len(out) > 1:
            self.broadcast(out)


def _json_default(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, Path):
        return str(o)
    return str(o)


def recipes_axis(a):
    from .state import Axis
    return a if isinstance(a, Axis) else Axis(**a)
