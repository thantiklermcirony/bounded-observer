"""Check sealed files against MANIFEST.json by SHA-256, without reading their contents for display.

    python verify_sealed.py --sealed /path/to/sealed
    python verify_sealed.py --sealed /path/to/sealed --calibration /path/to/stage-root

Prints file names, sizes and PASS/FAIL only. A sealed file that is absent is reported as
MISSING; an extra file that the manifest does not list is reported as UNLISTED. Hashing reads
the bytes of a file; nothing else is done with them.
"""
import argparse
import hashlib
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def check(entries: dict, root: pathlib.Path, label: str, flat: bool) -> int:
    bad = 0
    for name, want in sorted(entries.items()):
        p = root / (pathlib.Path(name).name if flat else name)
        if not p.exists():
            print(f"MISSING  {label} {name}")
            bad += 1
            continue
        ok = p.stat().st_size == want["bytes"] and sha256(p) == want["sha256"]
        print(f"{'PASS' if ok else 'FAIL'}     {label} {name} ({want['bytes']} bytes)")
        bad += not ok
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sealed", required=True, help="directory holding the *.sealed.* files")
    ap.add_argument("--calibration", help="stage root holding work/ (singles and pairs extracts)")
    a = ap.parse_args()
    m = json.loads((HERE / "MANIFEST.json").read_text(encoding="utf-8"))
    sealed_dir = pathlib.Path(a.sealed)
    bad = check(m["sealed_files"], sealed_dir, "sealed", flat=True)
    listed = set(m["sealed_files"])
    for p in sorted(sealed_dir.glob("*.sealed.*")):
        if p.name not in listed:
            print(f"UNLISTED sealed {p.name}")
            bad += 1
    if a.calibration:
        bad += check(m["calibration_extracts"], pathlib.Path(a.calibration), "calibration", flat=False)
    print("all files match the manifest" if bad == 0 else f"{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
