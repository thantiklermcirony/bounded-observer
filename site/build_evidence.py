"""Build site/evidence.html from registry/atlas.csv, so the page cannot drift from the register."""
import csv, html, pathlib, re

root = pathlib.Path(__file__).resolve().parents[1]
with (root / "registry" / "atlas.csv").open(encoding="utf-8", newline="") as source:
    rows = list(csv.DictReader(source))

missing_tests = [r["work"] for r in rows if not r["next_test"].strip()]
if missing_tests:
    raise ValueError("atlas rows without a next test: " + ", ".join(missing_tests))

def tag(v):
    v = (v or "").strip()
    if v.lower().startswith(("outside", "refuted")):
        return "X"
    parts = v.split(" / ")
    statuses = [re.match(r"^([PDH])(?:$|[\s;,(])", part) for part in parts]
    if len(parts) > 1 and all(statuses):
        return "M"  # one row contains claims with different statuses
    if len(parts) == 1 and statuses[0]:
        return statuses[0].group(1)
    return "U"  # unrecognized or absent: never silently treat as proven

layers = sorted({r["layer"] for r in rows}, key=lambda s: (s.lower().startswith("outside"), s))
body = []
for L in layers:
    rs = [r for r in rows if r["layer"] == L]
    body.append(f'<h3>{html.escape(L)} <span style="color:var(--ink-3);font-weight:400">· {len(rs)}</span></h3>')
    body.append('<div class="scroll"><table><thead><tr><th>Tag</th><th>Work</th><th>Status detail</th><th>Bounded quantity</th>'
                '<th>Chart</th><th>Next test</th><th>Last result</th></tr></thead><tbody>')
    for r in rs:
        t = tag(r["verdict_status"])
        ssrn = r["ssrn"].strip()
        title = html.escape(r["short_title"])
        if ssrn.isdigit():
            title = f'<a href="https://papers.ssrn.com/abstract={ssrn}">{title}</a>'
        body.append(
            f'<tr data-tag="{t}"><td><span class="tag tag-{t}">{t}</span></td>'
            f'<td>{title}</td><td>{html.escape(r["verdict_status"])}</td>'
            f'<td>{html.escape(r["bounded_quantity"])}</td>'
            f'<td>{html.escape(r["chart"])}</td><td>{html.escape(r["next_test"])}</td>'
            f'<td>{html.escape(r["last_result"])}</td></tr>')
    body.append("</tbody></table></div>")

counts = {t: sum(1 for r in rows if tag(r["verdict_status"]) == t) for t in "PDHMXU"}

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The atlas · The Bounded Observer</title>
<meta name="description" content="Every work in the programme placed as a chart of the law, with its status and its next test. Failures included.">
<link rel="stylesheet" href="style.css">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
</head>
<body>
<a class="skip" href="#main">Skip to the atlas</a>
<header class="top"><div class="wrap top-in">
  <a class="brand" href="./">The Bounded Observer <span>· science from within</span></a>
  <nav aria-label="Primary"><a href="./">Walk</a><a href="inside.html">Inside</a><a href="evidence.html" aria-current="page">Atlas</a>
  <a href="library.html">Library</a><a href="labs.html">Labs</a><a href="ida.html">IDA Live</a>
  <a href="radiation.html">Radiation</a><a href="papers.html">Papers</a><a href="contribute.html">Contribute</a></nav>
</div></header>

<main id="main" class="wrap" style="padding-top:2.5rem;padding-bottom:4rem">
  <div class="prose">
    <h1>The atlas</h1>
    <p>Every work in the programme, placed as a chart of the law: what is bounded, which chart
    applies, what state the claim is in, and — the column that matters — <b>what would move it</b>.
    A row with no next test is a row that cannot be wrong, and it does not belong here.</p>
    <p><span class="tag tag-P">P</span> proven, or classical with a citation ·
       <span class="tag tag-D">D</span> derived, awaiting checking ·
       <span class="tag tag-H">H</span> hypothesis with a stated loss condition ·
       <span class="tag tag-M">M</span> mixed statuses within one work ·
       <span class="tag tag-X">X</span> outside the law's conditions or explicitly refuted ·
       <span class="tag tag-U">U</span> status needs classification</p>
    <p>{counts['P']} proven · {counts['D']} derived · {counts['H']} open · {counts['M']} mixed ·
    {counts['X']} outside or refuted · {counts['U']} unclassified. The full status text stays
    visible in each row. The law applies <b>only where its four conditions hold</b>.</p>
  </div>
  <div style="max-width:76rem;margin-top:2rem">
  {''.join(body)}
  </div>
  <div class="prose" style="margin-top:2.5rem">
    <p>Source of record: <code>registry/atlas.csv</code>. This page is generated from it by
    <code>site/build_evidence.py</code>, so the two cannot drift apart.</p>
  </div>
</main>
<footer class="foot"><div class="wrap">Code MIT · text and figures CC BY 4.0 ·
<a href="https://orcid.org/0009-0005-1794-5945">Daniel John Murray</a></div></footer>
</body>
</html>
"""
with (root / "site" / "evidence.html").open("w", encoding="utf-8", newline="\n") as output:
    output.write(page)
print(f"evidence.html written: {len(rows)} rows, {counts}")
