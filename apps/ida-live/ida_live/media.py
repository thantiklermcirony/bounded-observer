"""Footage for the levels: downloaded on this computer on first use, or supplied by you.

Each level's clip lives in  Documents/IDA Live/media/<level id>/ . The app downloads the
free-licence clip listed in levels/levels.json the first time; any other video you drop
into that folder (mp4, webm, mov) is used instead, newest first. Preview frames the display
grabs are saved in media/previews so the footage can be checked without opening it.
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.request
from pathlib import Path
from typing import Callable, Dict, Optional

from .config import APP_DIR, DATA_DIR

MEDIA_DIR = DATA_DIR / "media"
MANIFEST = APP_DIR / "levels" / "levels.json"
VIDEO_EXT = (".mp4", ".webm", ".mov", ".m4v")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")


def manifest() -> dict:
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def entries() -> list:
    """Every clip the app knows: the levels and the attention-map tasks."""
    m = manifest()
    return m.get("levels", []) + m.get("attention", [])


def level_dir(level_id: str) -> Path:
    safe = "".join(c for c in level_id if c.isalnum() or c in "-_")
    d = MEDIA_DIR / safe
    d.mkdir(parents=True, exist_ok=True)
    return d


def clip_for(level: dict) -> Optional[Path]:
    """Your own clip if you added one, otherwise the downloaded default."""
    d = level_dir(level["id"])
    default = d / level["clip"]["file"]
    own = [p for p in d.iterdir() if p.suffix.lower() in VIDEO_EXT and p.name != default.name]
    if own:
        return max(own, key=lambda p: p.stat().st_mtime)
    return default if default.exists() and default.stat().st_size > 100_000 else None


def listing(kind: str = "levels") -> list:
    out = []
    prev = MEDIA_DIR / "previews"
    for lv in manifest().get(kind, []):
        clip = clip_for(lv)
        previews = sorted(p.name for p in prev.glob(f"{lv['id']}_*.jpg")) if prev.exists() else []
        out.append({**lv, "media": {
            "ready": clip is not None,
            "url": f"/media/{lv['id']}/{clip.name}" if clip else None,
            "own": bool(clip and clip.name != lv["clip"]["file"]),
            "mb": round(clip.stat().st_size / 1e6, 1) if clip else None,
            "folder": str(level_dir(lv["id"])),
            "previews": [f"/media/previews/{n}" for n in previews],
        }})
    return out


_active: Dict[str, threading.Thread] = {}


def fetch(level_id: str, progress: Callable[[dict], None]) -> None:
    """Download a level's clip in a background thread, trying each listed source in turn."""
    if level_id in _active and _active[level_id].is_alive():
        return
    lv = next((l for l in entries() if l["id"] == level_id), None)
    if lv is None:
        raise ValueError(f"No level called {level_id!r}")
    dest = level_dir(level_id) / lv["clip"]["file"]

    def run():
        errors = []
        for url in lv["clip"]["urls"]:
            part = dest.with_suffix(".part")
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "video/*,*/*"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    ctype = r.headers.get("Content-Type", "")
                    total = int(r.headers.get("Content-Length") or 0)
                    if "video" not in ctype and "octet-stream" not in ctype:
                        raise ValueError(f"not a video ({ctype or 'unknown type'})")
                    got, last = 0, 0.0
                    with open(part, "wb") as f:
                        while True:
                            chunk = r.read(1 << 16)
                            if not chunk:
                                break
                            f.write(chunk)
                            got += len(chunk)
                            if time.time() - last > 0.3:
                                last = time.time()
                                progress({"level": level_id, "state": "downloading", "got": got, "total": total})
                if got < 100_000:
                    raise ValueError("file too small")
                os.replace(part, dest)
                progress({"level": level_id, "state": "done", "got": got, "total": got, "source": url})
                return
            except Exception as exc:  # try the next source
                errors.append(f"{url.split('/')[2]}: {exc}")
                try:
                    part.unlink()
                except OSError:
                    pass
        progress({"level": level_id, "state": "failed", "errors": errors,
                  "folder": str(dest.parent)})

    t = threading.Thread(target=run, daemon=True)
    _active[level_id] = t
    t.start()


def save_preview(level_id: str, n: int, data: bytes) -> Path:
    d = MEDIA_DIR / "previews"
    d.mkdir(parents=True, exist_ok=True)
    safe = "".join(c for c in level_id if c.isalnum() or c in "-_")
    p = d / f"{safe}_{int(n)}.jpg"
    p.write_bytes(data[:5_000_000])
    return p
