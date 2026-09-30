"""Control folder: lets Claude (or any script) read and drive IDA Live while it runs.

Everything goes through files in  Documents/IDA Live/control/ :

  live.json        rewritten every second: connection, signal quality, your state,
                   the MRE and IDA measures, display settings, recording, recent log
  inbox/*.json     drop a command here; it runs within half a second
  outbox/<id>.json the result of that command
  done/            processed commands, kept as a record

A command file holds one command or a list of them, e.g.
  {"id": "lens-1", "cmd": "set", "values": {"display.lens": "tunnel", "display.speed": 0.5}}
  [{"cmd": "mark", "label": "eyes closed"}, {"cmd": "start_session", "label": "breathing"}]

Commands: every command the display itself uses (connect, calibrate, start_session,
end_session, set_knob, mark, note, light_start, recipe_start, save_recipe, ...), plus:
  get_state            the latest full tick (state, features, flags)
  set                  several knobs at once: {"values": {path: value, ...}}
  get_knobs            every knob with its value, range and description
  list_sessions        recorded sessions, newest first
  read_session         {"name": ..., "file": "events.jsonl"|"features.csv"|"state.csv"|"manifest.json", "tail": 200}
  report               {"which": "gate"|"light"|"recipe"} runs that analysis now and returns it
  summary              {"name": ..., "series": true} (re)writes and returns a session's summary.txt
  say                  {"text": ...} shows a message on the display
  help                 this text

Every command and its result is also written to the session's events when recording,
tagged by="claude" (or the "by" you give), so every change stays traceable.
Only processes on this computer can write here; it is the same trust as settings.json.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List

from .config import DATA_DIR


class _Collector:
    """Stands in for a WebSocket so the display's own command handler can be reused."""

    def __init__(self):
        self.messages: List[dict] = []

    async def send_str(self, text: str) -> None:
        try:
            self.messages.append(json.loads(text))
        except Exception:
            self.messages.append({"text": text})


def _atomic_write(path: Path, data: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, default=str)
    os.replace(tmp, path)


class ControlBridge:
    def __init__(self, engine):
        self.engine = engine
        c = engine.settings.get("control", {})
        self.poll_s = float(c.get("poll_s", 0.5))
        self.live_every = float(c.get("live_every_s", 1.0))
        self.root = DATA_DIR / "control"
        self.inbox, self.outbox, self.done = self.root / "inbox", self.root / "outbox", self.root / "done"
        for d in (self.inbox, self.outbox, self.done):
            d.mkdir(parents=True, exist_ok=True)
        readme = self.root / "README.txt"
        readme.write_text(__doc__, encoding="utf-8")
        self._last_live = 0.0
        self.last_command: Dict[str, Any] = {}

    # ------------------------------------------------------------------ loop
    async def run(self) -> None:
        while True:
            try:
                for path in sorted(self.inbox.glob("*.json")):
                    await self._process(path)
                if time.time() - self._last_live >= self.live_every:
                    self._last_live = time.time()
                    _atomic_write(self.root / "live.json", self.live())
            except Exception as exc:  # the bridge must never take the app down
                self.engine.log(f"Control folder error: {exc}")
            await asyncio.sleep(self.poll_s)

    async def _process(self, path: Path) -> None:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except OSError:
            return  # still being written; next poll
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            if time.time() - path.stat().st_mtime < 3:
                return  # possibly half-written
            payload, err = None, f"not valid JSON: {exc}"
        cmds = payload if isinstance(payload, list) else [payload] if payload is not None else []
        results = []
        for i, cmd in enumerate(cmds):
            if not isinstance(cmd, dict):
                results.append({"ok": False, "error": "each command must be a JSON object"})
                continue
            results.append(await self.execute(cmd))
        if payload is None:
            results = [{"ok": False, "error": err}]
        rid = (payload.get("id") if isinstance(payload, dict) else None) or path.stem
        _atomic_write(self.outbox / f"{rid}.json", {"id": rid, "file": path.name, "at": time.strftime("%H:%M:%S"),
                                                     "results": results})
        try:
            os.replace(path, self.done / f"{time.strftime('%Y%m%d-%H%M%S')}_{path.name}")
        except OSError:
            pass
        _atomic_write(self.root / "live.json", self.live())

    async def execute(self, cmd: dict) -> dict:
        from .server import handle_command

        e = self.engine
        name = cmd.get("cmd")
        by = str(cmd.get("by", "claude"))
        self.last_command = {"cmd": name, "at": time.strftime("%H:%M:%S"), "by": by}
        try:
            if name == "help":
                return {"ok": True, "help": __doc__}
            if name == "get_state":
                return {"ok": True, "state": e._last_state, "features": e._last_vals, "flags": e._last_flags}
            if name == "get_knobs":
                return {"ok": True, "knobs": e.knob_list()}
            if name == "set":
                changed = [e.set_knob(p, v, by=by) for p, v in (cmd.get("values") or {}).items()]
                return {"ok": True, "changed": changed}
            if name == "list_sessions":
                return {"ok": True, "sessions": self._sessions()}
            if name == "read_session":
                return {"ok": True, **self._read_session(cmd)}
            if name == "summary":
                from .analysis.summary import write_summary, series
                folder = self.engine.sessions_dir / str(cmd.get("name", ""))
                if not folder.is_dir():
                    raise ValueError("No such session")
                write_summary(folder)
                return {"ok": True, "summary": (folder / "summary.txt").read_text(encoding="utf-8"),
                        "series": series(folder, int(cmd.get("points", 300)))["measures"] if cmd.get("series") else None}
            if name == "level_report":
                # what the levels did: one session (name) or every level session
                from .analysis.levels import analyse_session, analyse_all
                if cmd.get("name"):
                    r = analyse_session(self.engine.sessions_dir / str(cmd["name"]))
                    return {"ok": True, "report": {k: v for k, v in (r or {}).items() if k != "_series"}}
                return {"ok": True, "report": analyse_all(self.engine.sessions_dir)}
            if name == "report":
                return {"ok": True, "report": self._report(str(cmd.get("which", "gate")))}
            if name == "say":
                e.broadcast({"type": "say", "text": str(cmd.get("text", ""))[:400], "by": by})
                e.event("say", {"text": str(cmd.get("text", ""))[:400], "by": by})
                return {"ok": True}
            if name in ("set_knob", "mark"):
                cmd = {**cmd, "by": by}
            col = _Collector()
            await handle_command(e, col, cmd)
            e.event("control", {"cmd": name, "by": by}, public=False)
            e.broadcast({"type": "control", "cmd": name, "by": by})
            return {"ok": True, "messages": col.messages[-5:]}
        except Exception as exc:
            return {"ok": False, "error": str(exc), "trace": traceback.format_exc(limit=3)}

    # ------------------------------------------------------------------ views
    def live(self) -> dict:
        e = self.engine
        st = dict(e._last_state or {})
        st.pop("t", None)
        return {
            "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": e.source.status() if e.source else None,
            "quality": (e._last_flags or {}).get("quality"),
            "channel": (e._last_flags or {}).get("channel"),
            "state": st,
            "features": e._last_vals,
            "calibration": e.calibration,
            "reference": ({"id": e.reference.ref_id, "created": e.reference.created} if e.reference else None),
            "session": e.session,
            "light": e.protocol.public() if e.protocol else None,
            "recipe": (e.runner or e.last_runner).public() if (e.runner or e.last_runner) else None,
            "display": e.settings.get("display"),
            "windows_open": len(e.clients),
            "last_command": self.last_command,
            "log": e.log_lines[-15:],
        }

    def _sessions(self) -> list:
        root = self.engine.sessions_dir
        out = []
        for d in sorted((p for p in root.iterdir() if p.is_dir()), reverse=True)[:100]:
            files = {f.name: f.stat().st_size for f in d.iterdir() if f.is_file()}
            out.append({"name": d.name, "files": files})
        return out

    def _read_session(self, cmd: dict) -> dict:
        root = self.engine.sessions_dir
        name = str(cmd.get("name", ""))
        folder = (root / name).resolve()
        if root.resolve() not in folder.parents or not folder.is_dir():
            raise ValueError(f"No session called {name!r}")
        fname = str(cmd.get("file", "events.jsonl"))
        path = (folder / fname).resolve()
        if path.parent != folder or not path.is_file():
            raise ValueError(f"No file {fname!r} in {name}")
        tail = int(cmd.get("tail", 200))
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        head = lines[:1] if fname.endswith(".csv") else []
        return {"file": fname, "lines": len(lines), "text": "\n".join(head + lines[-tail:])}

    def _report(self, which: str) -> dict:
        from .analysis import gate, light, recipes

        root = self.engine.sessions_dir
        if which == "gate":
            return gate.run(root, float(self.engine.settings["probes"]["pre_window_s"]))
        mod = {"light": light, "recipe": recipes}.get(which)
        if mod is None:
            raise ValueError("which must be gate, light or recipe")
        if hasattr(mod, "run"):
            return mod.run(root)
        raise ValueError(f"The {which} report has no run() entry point")
