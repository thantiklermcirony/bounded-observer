"""Start IDA Live.

  python -m ida_live                      open the display; choose a source there
  python -m ida_live --sim                start with the simulated headband
  python -m ida_live --address XX:XX:...  connect straight to your Muse S Athena
  python -m ida_live --replay FILE        replay a raw_ble.txt recording
  python -m ida_live reports              run all three reports below
  python -m ida_live gate                 run the calibration gate over saved sessions
  python -m ida_live light-report         analyse revealed light-trial sessions
  python -m ida_live recipe-report        analyse revealed recipe runs (real vs sham triggers)
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from .config import load_settings


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "reports":
        from .analysis import gate, light, recipes

        for title, mod in (("Calibration gate: does the map predict your probe answers?", gate),
                           ("Light trials", light), ("Recipes: real vs sham triggers", recipes)):
            print(f"\n==== {title} ====")
            try:
                mod.main([])
            except Exception as exc:
                print(f"Could not run: {exc}")
        print("\nThe reports are also saved as JSON files in your sessions folder.")
        try:
            input("\nPress Enter to close.")
        except EOFError:
            pass
        return 0
    if argv and argv[0] in ("gate", "light-report", "recipe-report"):
        from .analysis import gate, light, recipes

        mod = {"gate": gate, "light-report": light, "recipe-report": recipes}[argv[0]]
        return mod.main(argv[1:])

    ap = argparse.ArgumentParser(prog="ida_live", description="IDA Live")
    ap.add_argument("--sim", action="store_true", help="start with the simulated headband")
    ap.add_argument("--address", default="", help="Muse S Athena Bluetooth address")
    ap.add_argument("--replay", default="", help="path to a raw_ble.txt recording")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--port", type=int, default=None)
    args = ap.parse_args(argv)

    from .config import DATA_DIR, INSTALLED

    if INSTALLED or sys.stdout is None:
        # the installed app runs without a console window; keep a log you can send
        log = open(DATA_DIR / "ida_live.log", "a", encoding="utf-8", buffering=1)
        sys.stdout = sys.stderr = log
        print(f"\n==== IDA Live starting ====")
    settings = load_settings()
    if args.no_browser:
        settings["server"]["open_browser"] = False
    if args.port:
        settings["server"]["port"] = args.port
    auto = None
    if args.sim:
        auto = {"kind": "sim"}
    elif args.address:
        auto = {"kind": "athena", "address": args.address}
    elif args.replay:
        auto = {"kind": "replay", "path": args.replay}

    from .server import serve

    try:
        asyncio.run(serve(settings, auto))
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
