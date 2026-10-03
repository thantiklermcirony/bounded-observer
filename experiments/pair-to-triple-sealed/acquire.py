"""Re-acquire the source repositories behind the sealed pair-to-triple data, at the exact commits.

Clones each source repository listed in MANIFEST.json, checks out the recorded commit, and
verifies the SHA-256 of every source file the sealing used. It prints names, hashes and
PASS/FAIL only. It never prints file contents.

    python acquire.py --dest /some/scratch/raw            # sources of sealed files only
    python acquire.py --dest /some/scratch/raw --all      # every repository that was searched
    python acquire.py --dest /some/scratch/raw --only bg_ncats_tact

Re-sealing: the scripts in extraction/ are archived exactly as they ran (with their original
/tmp paths). Five sealed files are verbatim copies of a source file and are reproduced
exactly by acquisition. Re-running the scripts for the others may not reproduce byte-identical
CSVs under other pandas versions; compare with verify_sealed.py and record any difference.
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def run(*cmd: str) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"command failed: {' '.join(cmd)}\n{r.stderr.strip()}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dest", required=True, help="directory to clone into (outside the repository)")
    ap.add_argument("--all", action="store_true", help="also clone repositories that supplied no sealed file")
    ap.add_argument("--only", nargs="*", help="local names of repositories to acquire")
    a = ap.parse_args()
    manifest = json.loads((HERE / "MANIFEST.json").read_text(encoding="utf-8"))
    dest = pathlib.Path(a.dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    bad = 0
    for name, repo in sorted(manifest["repositories"].items()):
        if a.only and name not in a.only:
            continue
        if not a.all and not a.only and repo["role"] != "source of sealed files":
            continue
        target = dest / name
        if not (target / ".git").exists():
            run("git", "clone", "--quiet", repo["url"], str(target))
        run("git", "-C", str(target), "fetch", "--quiet", "origin", repo["commit"])
        run("git", "-C", str(target), "checkout", "--quiet", repo["commit"])
        head = subprocess.run(["git", "-C", str(target), "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        ok = head == repo["commit"]
        print(f"{'PASS' if ok else 'FAIL'} {name} @ {head[:12]} (want {repo['commit'][:12]})")
        bad += not ok
        for rel, want in (repo.get("source_files") or {}).items():
            p = target / rel
            if want == "MISSING" or not p.exists():
                print(f"  FAIL missing {rel}")
                bad += 1
                continue
            got = sha256(p)
            same = got == want["sha256"]
            print(f"  {'PASS' if same else 'FAIL'} {rel}")
            bad += not same
    print("all sources verified" if bad == 0 else f"{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
