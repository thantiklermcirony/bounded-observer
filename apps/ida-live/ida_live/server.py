"""Local server: serves the display and carries messages both ways over one WebSocket.

It listens on 127.0.0.1 only, so nothing leaves the laptop.
"""

from __future__ import annotations

import asyncio
import json
import os
import socket
import shutil
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

import mimetypes

from aiohttp import WSMsgType, web

# Windows can map .js to text/plain in the registry, which makes browsers refuse ES modules.
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("font/woff2", ".woff2")

from .config import APP_DIR
from .engine import Engine
from .sources.athena import scan

WEB_DIR = APP_DIR / "web"


async def _send(ws, text: str) -> None:
    try:
        await ws.send_str(text)
    except Exception:
        pass


async def handle_command(engine: Engine, ws, msg: dict) -> None:
    cmd = msg.get("cmd")
    if cmd == "hello":
        await ws.send_str(json.dumps(engine.status(), default=str))
        for line in engine.log_lines[-30:]:
            await ws.send_str(json.dumps({"type": "log", "text": line}))
    elif cmd == "scan":
        engine.log("Searching for Muse headbands (about 8 s) …")
        devices = await scan()
        await ws.send_str(json.dumps({"type": "scan_result", "devices": devices}))
        engine.log(f"Found {len(devices)} headband(s)." if devices else
                   "No headband found. Is it switched on and not connected to your phone?")
    elif cmd == "connect":
        kind = msg.get("kind", "sim")
        kw = {}
        if kind == "athena":
            kw["address"] = msg.get("address", "")
        if kind == "replay":
            kw["path"] = msg.get("path", "")
        await engine.connect(kind, **kw)
    elif cmd == "disconnect":
        await engine.disconnect()
    elif cmd == "calibrate":
        engine.start_calibration(msg.get("seconds"), bool(msg.get("force", False)))
    elif cmd == "start_session":
        engine.start_session(msg.get("label", ""), bool(msg.get("probes", True)))
    elif cmd == "end_session":
        await engine.end_session()
    elif cmd == "answer":
        engine.answer(msg.get("id", ""), msg.get("value"))
    elif cmd == "self_caught":
        engine.self_caught()
    elif cmd == "light_start":
        engine.start_light(msg.get("phase", "nothing"), bool(msg.get("bench", False)))
    elif cmd == "light_stop":
        engine.stop_light()
    elif cmd == "reveal":
        engine.reveal()
    elif cmd == "knobs":
        await ws.send_str(json.dumps({"type": "knobs", "knobs": engine.knob_list()}, default=str))
    elif cmd == "set_knob":
        engine.set_knob(msg["path"], msg.get("value"), by=msg.get("by", "you"))
        if not str(msg["path"]).startswith(("display.", "control.")):
            await ws.send_str(json.dumps({"type": "knobs", "knobs": engine.knob_list()}, default=str))
    elif cmd == "levels":
        from . import media
        await ws.send_str(json.dumps({"type": "levels", "levels": media.listing(), "bests": engine.bests()}, default=str))
    elif cmd == "media_fetch":
        from . import media
        loop = asyncio.get_running_loop()
        media.fetch(str(msg.get("level", "")),
                    lambda m: loop.call_soon_threadsafe(engine.broadcast, {"type": "media_progress", **m}))
    elif cmd == "level_start":
        await engine.level_start(str(msg.get("level", "")), int(msg.get("rounds", 3)),
                           float(msg.get("round_s", 120)), float(msg.get("settle_s", 30)), by=msg.get("by", "you"))
    elif cmd == "level_event":
        engine.level_event(str(msg.get("kind", "")), msg.get("data") or {})
    elif cmd == "level_samples":
        engine.level_samples(msg.get("rows") or [])
    elif cmd == "attention_list":
        from . import media
        await ws.send_str(json.dumps({"type": "attention_tasks", "tasks": media.listing("attention")}, default=str))
    elif cmd == "attention_start":
        await engine.attention_start(str(msg.get("by", "you")))
    elif cmd == "attention_event":
        engine.attention_event(str(msg.get("kind", "")), msg.get("data") or {})
    elif cmd == "attention_samples":
        engine.attention_samples(msg.get("rows") or [])
    elif cmd == "attention_end":
        await engine.attention_end(msg.get("summary") or {})
    elif cmd == "search_start":
        await engine.search_start(str(msg.get("by", "you")))
    elif cmd == "booth_start":
        await engine.booth_start(str(msg.get("by", "you")))
    elif cmd == "booth_event":
        engine.booth_event(str(msg.get("kind", "")), msg.get("data") or {})
    elif cmd == "booth_samples":
        engine.booth_samples(msg.get("rows") or [])
    elif cmd == "booth_end":
        await engine.booth_end(msg.get("summary") or {})
    elif cmd == "home":
        await ws.send_str(json.dumps({"type": "home", **engine.home_info()}, default=str))
    elif cmd == "music_list":
        await ws.send_str(json.dumps({"type": "music_list", "music": engine.music_list(), "folder": str(engine.music_dir())}))
    elif cmd == "open_music":
        if sys.platform == "win32":
            os.startfile(str(engine.music_dir()))  # noqa: S606 - your own music folder
    elif cmd == "level_end":
        await engine.level_end(msg.get("summary") or {})
    elif cmd == "sessions":
        from .analysis.summary import list_sessions
        await ws.send_str(json.dumps({"type": "sessions", "sessions": list_sessions(engine.sessions_dir)}, default=str))
    elif cmd == "session_detail":
        from .analysis.summary import series, write_summary
        folder = (engine.sessions_dir / str(msg.get("name", ""))).resolve()
        if engine.sessions_dir.resolve() not in folder.parents or not folder.is_dir():
            raise ValueError("No such session.")
        if not (folder / "summary.txt").exists() and (folder / "state.csv").exists():
            try:
                write_summary(folder)
            except Exception:
                pass
        await ws.send_str(json.dumps({"type": "session_detail", **series(folder)}, default=str))
    elif cmd == "open_folder":
        path = engine.sessions_dir if not msg.get("name") else (engine.sessions_dir / str(msg["name"]))
        if sys.platform == "win32" and path.exists():
            os.startfile(str(path))  # noqa: S606 - opens Explorer on your own recordings folder
    elif cmd == "mark":
        engine.mark(msg.get("label", "mark"), by=msg.get("by", "you"))
    elif cmd == "save_knobs":
        engine.save_knobs()
    elif cmd == "recipes":
        await ws.send_str(json.dumps({"type": "recipes", "recipes": engine.recipe_list()}, default=str))
    elif cmd == "save_recipe":
        text = msg.get("text", "")
        engine.save_recipe(json.loads(text) if isinstance(text, str) else text)
        await ws.send_str(json.dumps({"type": "recipes", "recipes": engine.recipe_list()}, default=str))
    elif cmd == "recipe_start":
        await engine.start_recipe(msg.get("name", ""), bool(msg.get("bench")), bool(msg.get("covered")))
    elif cmd == "recipe_stop":
        engine.stop_recipe()
    elif cmd == "recipe_reveal":
        engine.reveal_recipe()
    elif cmd == "test_fire":
        res = await engine.test_fire(msg.get("actuator", "sim_led"), msg.get("pattern", {}), bool(msg.get("sham")))
        engine.log(f"Test fire done: {res}")
    elif cmd == "serial_ports":
        from .actuators import list_serial_ports
        await ws.send_str(json.dumps({"type": "serial_ports", "ports": list_serial_ports()}))
    elif cmd == "mre_status":
        await ws.send_str(json.dumps({"type": "mre", **engine.mre_status()}, default=str))
    elif cmd == "mre_ports":
        from .mre.qrng import list_ports
        await ws.send_str(json.dumps({"type": "mre_ports", "ports": list_ports()}))
    elif cmd == "quit":
        engine.log("Closing IDA Live …")
        await asyncio.get_running_loop().run_in_executor(None, engine.mre_stop)
        await engine.disconnect()
        await ws.send_str(json.dumps({"type": "quit"}))
        asyncio.get_running_loop().call_later(0.5, os._exit, 0)
    elif cmd == "note":
        engine.event("note", {"text": str(msg.get("text", ""))[:2000]})
    else:
        raise ValueError(f"Unknown command {cmd!r}")


async def _background_only(engine: Engine) -> None:
    """No window, but the MRE logger is collecting automation data: free the headband (saving
    any recording) and keep logging. Opening IDA Live again brings the window back."""
    if engine.source or engine.session:
        await engine.disconnect()
    if not getattr(engine, "_bg_noted", False):
        engine._bg_noted = True
        engine.log("Window closed: still logging random bits for the MRE test. Open IDA Live to see it; "
                   "Quit stops everything.")
    print("Window closed; IDA Live keeps logging random bits (MRE automation).")


async def _quit_if_abandoned(engine: Engine, grace_s: float = 12.0) -> None:
    """The last window closed. Wait (a reload reconnects within a second), then stop,
    saving any recording, so IDA Live never lingers invisibly holding the headband."""
    await asyncio.sleep(grace_s)
    if engine.clients:
        return
    if engine.mre_keep_alive():
        await _background_only(engine)
        return
    print("No window open; stopping IDA Live.")
    try:
        await engine.disconnect()
    finally:
        engine.mre_stop()
        os._exit(0)


def make_app(engine: Engine, request_port: int = 8765) -> web.Application:
    app = web.Application(middlewares=[])

    allowed = {f"http://{h}:{request_port}" for h in ("127.0.0.1", "localhost")}

    async def ws_handler(request):
        # only the app's own page may control it; blocks other websites open in your browser
        origin = request.headers.get("Origin")
        if origin and origin not in allowed:
            return web.Response(status=403, text="forbidden")
        ws = web.WebSocketResponse(heartbeat=20)
        await ws.prepare(request)
        engine.clients.add(ws)
        try:
            async for m in ws:
                if m.type != WSMsgType.TEXT:
                    continue
                try:
                    await handle_command(engine, ws, json.loads(m.data))
                except Exception as exc:
                    await ws.send_str(json.dumps({"type": "error", "text": str(exc)}))
                    engine.log(str(exc))
        finally:
            engine.clients.discard(ws)
            if not engine.clients and engine.settings["server"].get("close_with_window", True):
                asyncio.ensure_future(_quit_if_abandoned(engine))
        return ws

    async def index(_):
        return web.FileResponse(WEB_DIR / "index.html", headers={"Cache-Control": "no-store"})

    @web.middleware
    async def no_cache(request, handler):
        resp = await handler(request)
        if request.path.endswith((".js", ".css", ".html")):
            resp.headers["Cache-Control"] = "no-store"
        return resp

    app.middlewares.append(no_cache)

    async def api_quit(request):
        # used by the installer to close a running copy before updating or uninstalling;
        # the custom header means a web page cannot trigger it
        if request.headers.get("X-IDA-Live") != "quit":
            return web.Response(status=403, text="forbidden")
        await asyncio.get_running_loop().run_in_executor(None, engine.mre_stop)
        await engine.disconnect()
        asyncio.get_running_loop().call_later(0.3, os._exit, 0)
        return web.Response(text="closing")

    async def media_file(request):
        from . import media
        level, name = request.match_info["level"], request.match_info["name"]
        base = media.MEDIA_DIR.resolve()
        path = (media.MEDIA_DIR / level / name).resolve()
        if base not in path.parents or not path.is_file():
            return web.Response(status=404, text="not found")
        return web.FileResponse(path, headers={"Cache-Control": "no-store"})

    async def api_preview(request):
        # the display saves a few frames of each clip so the footage can be checked
        if request.headers.get("X-IDA-Live") != "preview":
            return web.Response(status=403, text="forbidden")
        from . import media
        data = await request.read()
        media.save_preview(request.match_info["level"], int(request.match_info["n"]), data)
        return web.Response(text="saved")

    async def report(request):
        # what the levels did: every level session, one session, or the latest one
        from .analysis import levels as lv
        which = request.match_info.get("which", "levels")
        sessions = engine.sessions_dir
        try:
            if which == "mre":
                from .analysis import mre
                text = await asyncio.get_running_loop().run_in_executor(None, mre.build_report, engine.mre_folder())
                return web.Response(text=text, content_type="text/html", headers={"Cache-Control": "no-store"})
            if which == "search":
                from .analysis import search
                text = await asyncio.get_running_loop().run_in_executor(None, search.build_search_report, engine.sessions_dir, engine.data_dir())
                return web.Response(text=text, content_type="text/html", headers={"Cache-Control": "no-store"})
            if which == "booth":
                from .analysis import booth
                text = await asyncio.get_running_loop().run_in_executor(None, booth.build_booth_report, engine.sessions_dir, engine.data_dir())
                return web.Response(text=text, content_type="text/html", headers={"Cache-Control": "no-store"})
            if which == "attention":
                done = sorted(p for p in sessions.glob("*attention-map*") if (p / "attention_profile.json").exists())
                if not done:
                    return web.Response(text=lv.page("Attention profile", "<h1>No attention profile yet</h1><p class='sub'>Run the attention map (Levels, first card). It takes about seven minutes.</p>"),
                                        content_type="text/html")
                text = (done[-1] / "report.html").read_text(encoding="utf-8")
            elif which == "levels":
                text = await asyncio.get_running_loop().run_in_executor(None, lv.build_levels_report, sessions)
                (sessions.parent / "reports").mkdir(parents=True, exist_ok=True)
                (sessions.parent / "reports" / "levels.html").write_text(text, encoding="utf-8")
            else:
                names = sorted(p.name for p in sessions.glob("*level-*") if (p / "level.csv").exists())
                name = names[-1] if which == "latest" and names else which
                folder = (sessions / name).resolve()
                if sessions.resolve() not in folder.parents or not (folder / "level.csv").exists():
                    return web.Response(status=404, text="No such level session yet.")
                path = await asyncio.get_running_loop().run_in_executor(None, lv.write_session_report, folder)
                text = path.read_text(encoding="utf-8") if path else "<p>Not enough data in this session.</p>"
        except Exception as exc:
            engine.log(f"Report failed: {exc}")
            return web.Response(status=500, text=f"Report failed: {exc}")
        return web.Response(text=text, content_type="text/html", headers={"Cache-Control": "no-store"})

    # instrument samples ship as one archive (web/samples.zip); a loose web/samples folder wins
    import zipfile
    _zip = {"z": None}

    async def samples(request):
        tail = request.match_info["tail"].replace("\\", "/")
        if ".." in tail.split("/"):
            return web.Response(status=404, text="not found")
        loose = WEB_DIR / "samples" / tail
        if loose.is_file():
            return web.FileResponse(loose, headers={"Cache-Control": "max-age=86400"})
        zp = WEB_DIR / "samples.zip"
        if not zp.exists():
            return web.Response(status=404, text="not found")
        if _zip["z"] is None:
            _zip["z"] = zipfile.ZipFile(zp)
        try:
            data = _zip["z"].read(tail)
        except KeyError:
            return web.Response(status=404, text="not found")
        ctype = "audio/ogg" if tail.endswith(".ogg") else "application/json" if tail.endswith(".json") else "text/plain"
        return web.Response(body=data, content_type=ctype, headers={"Cache-Control": "max-age=86400"})

    async def music(request):
        # your own music, from Documents/IDA Live/music
        base = engine.music_dir().resolve()
        path = (base / request.match_info["name"]).resolve()
        if base not in path.parents or not path.is_file():
            return web.Response(status=404, text="not found")
        return web.FileResponse(path, headers={"Cache-Control": "no-store"})

    app.router.add_get("/music/{name}", music)
    app.router.add_get("/samples/{tail:.*}", samples)
    app.router.add_get("/report/{which}", report)
    app.router.add_get("/media/{level}/{name}", media_file)
    app.router.add_post("/api/preview/{level}/{n}", api_preview)
    app.router.add_get("/ws", ws_handler)
    app.router.add_post("/api/quit", api_quit)
    app.router.add_get("/", index)
    app.router.add_static("/", WEB_DIR)
    return app


def _find_app_browser() -> str | None:
    """Edge (always on Windows) or Chrome, which can open a page as a chromeless app window."""
    cands = []
    for env in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA"):
        base = os.environ.get(env)
        if base:
            cands += [Path(base) / "Microsoft/Edge/Application/msedge.exe",
                      Path(base) / "Google/Chrome/Application/chrome.exe"]
    for c in cands:
        if c.exists():
            return str(c)
    for name in ("msedge", "google-chrome", "chromium", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    return None


def open_window(url: str, settings: dict, on_closed=None) -> None:
    """Open IDA Live in its own full-window app frame (no tabs, no address bar).

    It uses its own browser profile inside your IDA Live folder, so it never touches
    your normal browser and the window's process ends when you close it, which also
    closes IDA Live (on_closed). Falls back to your default browser."""
    exe = _find_app_browser() if settings["server"].get("app_window", True) else None
    if not exe:
        webbrowser.open(url)
        return
    from .config import DATA_DIR
    base = Path(os.environ["LOCALAPPDATA"]) / "IDA Live" if os.environ.get("LOCALAPPDATA") else DATA_DIR
    prof = base / "window-profile"
    args = [exe, f"--app={url}", f"--user-data-dir={prof}", "--start-maximized",
            "--no-first-run", "--no-default-browser-check", "--disable-features=Translate",
            "--autoplay-policy=no-user-gesture-required"]
    try:
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        webbrowser.open(url)
        return
    if on_closed:
        def watch():
            proc.wait()
            on_closed()
        threading.Thread(target=watch, daemon=True).start()


def already_running(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


async def serve(settings: dict, autoconnect: dict | None = None) -> None:
    host, port = settings["server"]["host"], int(settings["server"]["port"])
    if already_running(host, port):
        # a second launch (e.g. the desktop icon clicked twice) just reopens the window
        print("IDA Live is already running; opening its window.")
        open_window(f"http://{host}:{port}/", settings)
        return
    engine = Engine(settings)
    engine.send_fn = _send
    app = make_app(engine, port)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, host, port).start()
    url = f"http://{host}:{port}/"
    from .config import INSTALLED
    print(f"IDA Live is running at {url}" + ("" if INSTALLED else "  (close this window to stop)"))
    if autoconnect:
        try:
            await engine.connect(**autoconnect)
        except Exception as exc:
            engine.log(f"Could not connect automatically: {exc}")
    loop = asyncio.get_running_loop()

    def window_closed():
        # the app window was closed: give a moment in case it is being reopened, then quit
        async def maybe_quit():
            await asyncio.sleep(4.0)
            if not engine.clients and engine.mre_keep_alive():
                await _background_only(engine)
            elif not engine.clients:
                print("Window closed; stopping IDA Live.")
                try:
                    await engine.disconnect()
                finally:
                    engine.mre_stop()
                    os._exit(0)
        asyncio.run_coroutine_threadsafe(maybe_quit(), loop)

    if settings["server"].get("open_browser", True):
        open_window(url, settings, on_closed=window_closed if settings["server"].get("close_with_window", True) else None)
    await engine.run()
