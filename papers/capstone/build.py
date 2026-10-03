"""Build the capstone from its part files: concatenated Markdown, HTML, DOCX and PDF.

    python papers/capstone/build.py --out /some/output/dir [--formats md,html,docx,pdf]
                                    [--css path/to/style.css] [--chromium /path/to/chrome]

Portable by design:
- Inputs are resolved from this script's own location, never from the working directory.
- Outputs go to --out, which must not be the source directory, so the archived v2.1 files
  (Bounded_Composition_and_Its_Horizons_v2.1.md and .pdf) are never overwritten.
- The PDF footer's version is read from the 'date' line of 00_front.md, not hard-coded.
- Required tools are checked before anything is written. A missing tool stops the build with
  a plain message; it is never reported as a successful render.
- A build manifest (build-manifest.json) records the source commit, source hashes, tool
  versions and output hashes.

Note: the stylesheet used for the original v2.1 HTML/PDF (style.css) is not in the repository.
Without --css the HTML and PDF are rendered with pandoc's default styling, so they will not match
the archived PDF's appearance.

Tools: pandoc (on PATH, or via the pypandoc_binary package) for html/docx; Python playwright
with a Chromium build for pdf (pass --chromium if the bundled revision is not installed).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
PARTS = ["00_front.md", "01_law.md", "02_horizon.md", "03_charts.md", "04_test.md", "05_appendix.md"]
STEM = "Bounded_Composition_and_Its_Horizons"


class BuildError(SystemExit):
    pass


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_pandoc() -> str | None:
    exe = shutil.which("pandoc")
    if exe:
        return exe
    try:
        import pypandoc  # provided by pypandoc_binary
        return pypandoc.get_pandoc_path()
    except Exception:
        return None


def version_from_front(front: str) -> str:
    m = re.search(r'^date:\s*"[^"]*version\s+([0-9][0-9.]*)"', front, re.MULTILINE)
    if not m:
        raise BuildError("build: could not read the version from the 'date' line of 00_front.md")
    return m.group(1)


def git_commit() -> str | None:
    r = subprocess.run(["git", "-C", str(HERE), "rev-parse", "HEAD"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    dirty = subprocess.run(["git", "-C", str(HERE), "status", "--porcelain", "--", "."],
                           capture_output=True, text=True).stdout.strip()
    return r.stdout.strip() + ("+uncommitted-changes" if dirty else "")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build the capstone from its part files.")
    ap.add_argument("--out", required=True, help="output directory (not the source directory)")
    ap.add_argument("--formats", default="md,html,docx,pdf", help="comma list of md, html, docx, pdf")
    ap.add_argument("--css", help="optional stylesheet for the HTML/PDF")
    ap.add_argument("--chromium", help="optional path to a Chromium executable for the PDF")
    a = ap.parse_args(argv)

    formats = [f.strip() for f in a.formats.split(",") if f.strip()]
    unknown = set(formats) - {"md", "html", "docx", "pdf"}
    if unknown:
        raise BuildError(f"build: unknown format(s): {', '.join(sorted(unknown))}")
    if "pdf" in formats and "html" not in formats:
        formats.insert(formats.index("pdf"), "html")      # the PDF is rendered from the HTML

    out = pathlib.Path(a.out).resolve()
    if out == HERE:
        raise BuildError("build: --out must not be the source directory (it holds the archived v2.1 files)")
    for p in PARTS:
        if not (HERE / p).is_file():
            raise BuildError(f"build: missing source part {HERE / p}")
    css = pathlib.Path(a.css).resolve() if a.css else None
    if css and not css.is_file():
        raise BuildError(f"build: stylesheet not found: {css}")

    pandoc = find_pandoc() if {"html", "docx"} & set(formats) else None
    if {"html", "docx"} & set(formats) and not pandoc:
        raise BuildError("build: pandoc not found (install pandoc, or `pip install pypandoc_binary`)")
    if "pdf" in formats:
        try:
            import playwright.sync_api  # noqa: F401
        except ImportError:
            raise BuildError("build: python playwright not installed (`pip install playwright`); PDF not built")

    texts = [(HERE / p).read_text(encoding="utf-8") for p in PARTS]
    version = version_from_front(texts[0])
    out.mkdir(parents=True, exist_ok=True)
    md = out / f"{STEM}_v{version}.md"
    md.write_text("\n".join(texts), encoding="utf-8")
    outputs = {"md": md}
    tools = {"python": sys.version.split()[0]}

    if pandoc:
        tools["pandoc"] = subprocess.run([pandoc, "--version"], capture_output=True, text=True,
                                         check=True).stdout.splitlines()[0]
    if "html" in formats:
        html = out / f"{STEM}_v{version}.html"
        cmd = [pandoc, str(md), "-s", "--mathml", "--embed-resources", f"--resource-path={HERE}", "-o", str(html)]
        if css:
            cmd[4:4] = ["--css", str(css)]
        subprocess.run(cmd, check=True)
        outputs["html"] = html
    if "docx" in formats:
        docx = out / f"{STEM}_v{version}.docx"
        subprocess.run([pandoc, str(md), f"--resource-path={HERE}", "-o", str(docx)], check=True)
        outputs["docx"] = docx
    if "pdf" in formats:
        from playwright.sync_api import sync_playwright
        import playwright as _pw
        tools["playwright"] = getattr(_pw, "__version__", "unknown")
        pdf = out / f"{STEM}_v{version}.pdf"
        footer = ('<div style="font-size:8px;width:100%;text-align:center;color:#666">Murray — Bounded '
                  f'Composition and Its Horizons, v{version} — <span class="pageNumber"></span>/'
                  '<span class="totalPages"></span></div>')
        with sync_playwright() as p:
            browser = p.chromium.launch(**({"executable_path": a.chromium} if a.chromium else {}))
            tools["chromium"] = browser.version
            page = browser.new_page()
            page.goto(outputs["html"].as_uri())
            page.wait_for_timeout(1500)
            page.pdf(path=str(pdf), format="A4", display_header_footer=True, header_template="<div></div>",
                     footer_template=footer, margin={"top": "18mm", "bottom": "18mm", "left": "18mm", "right": "18mm"})
            browser.close()
        outputs["pdf"] = pdf

    manifest = {
        "version_from_sources": version,
        "source_commit": git_commit(),
        "sources": {p: sha256(HERE / p) for p in PARTS},
        "css": {str(css): sha256(css)} if css else "none (pandoc default styling; original style.css not in repository)",
        "tools": tools,
        "outputs": {k: {"file": v.name, "sha256": sha256(v), "bytes": v.stat().st_size} for k, v in outputs.items()},
    }
    (out / "build-manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
