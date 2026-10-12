"""Check branch/publication references and exact bytes of the immutable public release."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding="utf-8"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def local(path):
    if path.startswith(("https://","http://")):return
    resolved=(ROOT/path).resolve()
    assert resolved.is_relative_to(ROOT.resolve()),path
    assert resolved.exists(),f"Missing source: {path}"
branches=read("registry/branches.json")
ids=[b["id"] for b in branches["branches"]]
assert len(ids)==len(set(ids))
assert "virtual-cell-lab" in ids and "vcc-arc" in ids
for b in branches["branches"]:
    for field in ["id","title","role","relation","landing","question","contract","dependencies","evidence","next_task"]:assert b.get(field), (b["id"],field)
    for field in ["record","normalization","readings","operations","retained_state","composition","clock_resources","bridge","test_revision"]:assert b["contract"].get(field),(b["id"],field)
    for field in ["proof","numerical","implementation","empirical"]:assert b["evidence"].get(field),(b["id"],field)
    local(b["landing"])
    for d in b["dependencies"]:local(d)
pubs=read("registry/publications.json")["publications"]
assert len(pubs)==12
assert len({p["abstract_id"] for p in pubs})==12
for p in pubs:
    local(p["pdf_path"]);local(p["source_path"])
    assert p["pdf_sha256"]==sha(ROOT/p["pdf_path"]),p["name"]
    assert p["reuse"]=="CC BY 4.0"
lib=ROOT/"papers/library-2026-10-12"
for name,digest in read("registry/release_manifest_digests.json").items():
    assert sha(lib/name)==digest,name
manifest=read("papers/library-2026-10-12/manifest.json")
for row in manifest:
    path=lib/row["path"]
    assert path.stat().st_size==row["bytes"] and sha(path)==row["sha256"],row["path"]
actual={p.relative_to(lib).as_posix() for p in lib.rglob("*") if p.is_file()}
assert actual=={r["path"] for r in manifest}|{"manifest.json","provenance/manifest.json"},"Unexpected/missing snapshot files"
assert len(list((lib/"pdf").glob("*.pdf")))==12
for row in read("papers/library-2026-10-12/provenance/manifest.json"):
    assert sha(lib/row["record"])==row["sha256"],row["record"]
assert "virtual-cell-lab" in (ROOT/"site/project.html").read_text(encoding="utf-8")
assert "vcc-arc" in (ROOT/"site/project.html").read_text(encoding="utf-8")
for path in [ROOT/"README.md",ROOT/"LAB.md",ROOT/"PUBLISH.md",*ROOT.glob("docs/*.md"),ROOT/"papers/README.md",*ROOT.glob("branches/*/README.md"),*ROOT.glob("toolkit/*.md")]:
    text=path.read_text(encoding="utf-8")
    for link in re.findall(r"(?<!!)\[[^\]]*\]\(([^\s)]+)\)",text):
        if link.startswith(("http:","https:","#","mailto:")):continue
        target=(path.parent/link.split("#",1)[0]).resolve()
        assert target.is_relative_to(ROOT.resolve()) and target.exists(),(str(path.relative_to(ROOT)),link)
print(f"PASS: {len(ids)} branches, {len(pubs)} distinct SSRN manuscripts, {len(manifest)} snapshot files and local documentation links.")
