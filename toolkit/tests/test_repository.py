"""Repository checks: build portability, the atlas page's labels, and identifier hygiene.

These are not tests of any theorem. They keep the repository's own records consistent
(ERRATA E4-E5, review items 4, 10 and 11, and the portable build in papers/capstone/build.py).
"""
import csv
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_portable_build_markdown_matches_the_archived_concatenation(tmp_path):
    # The build resolves inputs from its own location and writes only to --out.
    out = tmp_path / "out"
    r = subprocess.run([sys.executable, str(ROOT / "papers/capstone/build.py"), "--out", str(out), "--formats", "md"],
                       cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    built = (out / "Bounded_Composition_and_Its_Horizons_v2.1.md").read_bytes()
    archived = (ROOT / "papers/capstone/Bounded_Composition_and_Its_Horizons_v2.1.md").read_bytes()
    assert built == archived
    assert (out / "build-manifest.json").exists()


def test_portable_build_refuses_to_write_into_the_source_directory(tmp_path):
    r = subprocess.run([sys.executable, str(ROOT / "papers/capstone/build.py"),
                        "--out", str(ROOT / "papers/capstone"), "--formats", "md"],
                       cwd=tmp_path, capture_output=True, text=True)
    assert r.returncode != 0 and "source directory" in r.stderr


def test_legacy_E_rows_are_labelled_and_never_shown_as_unclassified_or_proven():
    rows = list(csv.DictReader(open(ROOT / "registry/atlas.csv", encoding="utf-8")))
    legacy = [r for r in rows if any(re.match(r"^E(?:$|[\s;,(])", p) for p in r["verdict_status"].split(" / "))]
    assert {r["work"] for r in legacy} == {"L-08", "L-GSH"}
    page = (ROOT / "site/evidence.html").read_text(encoding="utf-8")
    for r in legacy:
        title = r["short_title"].replace("&", "&amp;")
        row = next(line for line in page.split("<tr ") if title in line)
        assert "legacy E — definition unverified" in row and 'data-tag="E"' in row
    index = (ROOT / "site/index.html").read_text(encoding="utf-8")
    glut = next(line for line in index.splitlines() if "glutathione model" in line)
    assert "legacy E — definition unverified" in glut and "tag-U" not in glut


def test_the_three_H5s_carry_distinct_identifiers_outside_the_capstone():
    docs = (ROOT / "docs/6-prediction.md").read_text(encoding="utf-8")
    site = (ROOT / "site/index.html").read_text(encoding="utf-8")
    atlas = (ROOT / "registry/atlas.csv").read_text(encoding="utf-8")
    assert "**IDA-RG**" in docs and "**H5**" not in docs
    assert "(IDA-RG)" in site and "(H5)" not in site
    assert "TAO-H5" in atlas and "assignment reliability H5" not in atlas
    # the capstone keeps its own manuscript identifier
    assert "**Hypothesis H5.**" in (ROOT / "papers/capstone/03_charts.md").read_text(encoding="utf-8")
