"""Build public project and paper pages from the branch and publication registries."""
from pathlib import Path
import html,json
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
branches=json.loads((ROOT/"registry/branches.json").read_text(encoding="utf-8"))
pubs=json.loads((ROOT/"registry/publications.json").read_text(encoding="utf-8"))
GITHUB="https://github.com/thantiklermcirony/bounded-observer/blob/main/"
def e(value):return html.escape(str(value),quote=True)
def shell(title,description,body,current):
    nav=[("project.html","Project"),("./","Walk"),("inside.html","Inside"),("evidence.html","Atlas"),("library.html","Library"),("labs.html","Labs"),("ida.html","IDA"),("radiation.html","Radiation"),("papers.html","Papers"),("contribute.html","Contribute")]
    links="".join(f'<a href="{url}"'+(' aria-current="page"' if url==current else '')+f'>{label}</a>' for url,label in nav)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · The Bounded Observer</title><meta name="description" content="{e(description)}">
<link rel="stylesheet" href="style.css"><link rel="icon" href="favicon.svg" type="image/svg+xml">
<style>
.programme{{max-width:70rem;margin:0 auto;padding:3rem 1rem 4rem}} .intro{{max-width:48rem;margin:0 0 2rem}}
.intro h1{{margin-bottom:1rem}} .intro p{{font-size:1.15rem}}
.loop{{display:flex;flex-wrap:wrap;gap:.65rem;align-items:center;padding:1rem;background:var(--bg-sunk);border:1px solid var(--rule);border-radius:.5rem;font-family:var(--sans);margin:1.5rem 0 2rem}}
.loop b{{padding:.4rem .6rem;background:var(--panel);border:1px solid var(--rule);border-radius:.3rem}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,26rem),1fr));gap:1rem;margin:1rem 0 2.5rem}}
.card{{padding:1.4rem;border:1px solid var(--rule);background:var(--panel);border-radius:.5rem}}
.card h3{{font-size:1.25rem;margin:0 0 .5rem}} .role{{font: .8rem var(--sans);color:var(--cool);margin-bottom:.8rem}}
.card details{{border-top:1px solid var(--rule);padding-top:.75rem;margin-top:.75rem}} summary{{cursor:pointer;font-family:var(--sans);font-size:.95rem}}
dt{{font:600 .85rem var(--sans);margin-top:.7rem;color:var(--ink-2)}} dd{{margin:0 0 .3rem;font-size:.95rem}}
.scroll{{overflow:auto}} .programme table{{width:100%;min-width:38rem}}
.note{{max-width:48rem}} .top-in{{height:auto;min-height:52px;flex-wrap:wrap;padding-top:.4rem;padding-bottom:.4rem}}
.top nav{{overflow:auto;max-width:100%}}
</style></head><body><a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap top-in"><a class="brand" href="./">The Bounded Observer <span>· science from within</span></a><nav aria-label="Primary">{links}</nav></div></header>
<main id="main" class="programme">{body}</main>
<footer class="foot"><div class="wrap">Daniel John Murray · original code MIT · original text CC BY 4.0 · linked sources retain their terms</div></footer></body></html>
"""
body=['<div class="intro"><h1>One project. A common operational foundation.</h1><p>The Bounded Observer studies what an observer can <b>record, read, retain, combine and change</b>. UHL gives the operational mathematics of bounded normalized readings. SIH studies regularity and concentration in specified field models. The branches turn these questions into models, instruments and experiments.</p><p><a href="papers.html">Read the current mathematical library</a> · <a href="'+GITHUB+'docs/project-structure.md">Follow the dependency map</a> · <a href="philosophy/">Read the philosophical journey</a></p></div>',
'<div class="loop" aria-label="The operational loop"><b>Record</b><span>→</span><b>Read or intervene</b><span>→</span><b>Next record</b><span>↔</span><b>Combine or retain parts</b></div>',
'<div class="note"><h2>What is closed?</h2><p><b>[P, conditional]</b> In the finite complex record model, the declared readings, instruments, composition, purification, environment dilation and discarding operations stay within the record class. The closure theorem has named premises. Applications identify their own records, dynamics and observation bridges.</p><p>The general predictive-state question and the independent two-positive-weight model also support classical branches. A shared interface does not impose a quantum interpretation on a cell assay or an AI record.</p></div>',
'<h2 style="margin-top:2rem">The branches</h2><p>Each entry states its relationship to the foundation, current evidence and operational contract.</p><div class="cards">']
for b in branches["branches"]:
    detail="".join(f'<dt>{e(k.replace("_"," ").capitalize())}</dt><dd>{e(v)}</dd>' for k,v in b["contract"].items())
    evidence="".join(f'<dt>{e(k.capitalize())}</dt><dd>{e(v)}</dd>' for k,v in b["evidence"].items())
    body.append(f'<article class="card" id="{e(b["id"])}"><div class="role">{e(b["role"])}</div><h3>{e(b["title"])}</h3><p>{e(b["question"])}</p><p>{e(b["relation"])}</p><p><a href="{GITHUB+e(b["landing"])}">Branch sources and explanation →</a></p><details><summary>Current evidence</summary><dl>{evidence}</dl><p>{e(b["next_task"])}</p></details><details><summary>Records, operations and time</summary><dl>{detail}</dl></details></article>')
body.extend(['</div><div class="note"><h2>Future branches</h2><p>A new extension specifies its record, readings, interventions, retained state, composition, clock/resources, observation bridge and evidence. It begins under the common project; independently maintained applications and large data workflows can remain in component repositories.</p><p><a href="'+GITHUB+'docs/branch-contract.md">Use the branch contract</a> · <a href="'+GITHUB+'registry/repositories.json">Repository roles</a></p>',
'<h2 style="margin-top:2rem">History and corrections</h2><p>The frozen v2.1 composition capstone, earlier catalogue, original manuscripts and failed comparisons remain available. The current library supplies dated hormesis and kinematics corrections. The older Virtual Cell laboratory and the Arc competition have distinct records.</p><p><a href="library.html">Historical library</a> · <a href="evidence.html">Earlier claim atlas</a> · <a href="papers.html">Current papers and correction links</a></p></div>'])
body.insert(1,'<div class="note"><h2>A working research lab</h2><p>Questions become specified models or candidates, frozen comparisons, independent checks, results and revisions. The lab keeps runnable models, instruments, active questions and completed outcomes together.</p><p><a href="labs.html">Enter the working lab</a> · <a href="'+GITHUB+'LAB.md">Run a model</a> · <a href="'+GITHUB+'docs/research-board.md">Join a research task</a> · <a href="'+GITHUB+'docs/incubation.md">Incubation and outreach</a></p></div>')
(SITE/"project.html").write_text(shell("Project and branches","One foundation, explicit branch relationships and evidence for The Bounded Observer.","".join(body),"project.html"),encoding="utf-8",newline="\n")
body=['<div class="intro"><h1>The current mathematical library</h1><p>A capstone, eight supporting papers, a hormesis amendment and two proposed author corrections. The twelve public manuscripts were received by SSRN on 13 October 2026 and await completeness review. Receipt is not peer review.</p><p><a href="project.html">How the whole project fits together</a> · <a href="'+GITHUB+'papers/PUBLICATION_STATUS_2026-10-13.md">Dated publication and licensing receipt</a></p></div>']
for heading,items in [("Capstone and supporting papers",pubs["publications"][:9]),("Amendment and proposed corrections",pubs["publications"][9:])]:
    body.append(f'<h2>{heading}</h2><div class="scroll"><table><thead><tr><th>Manuscript</th><th>PDF</th><th>Source</th><th>SSRN</th></tr></thead><tbody>')
    for p in items:
        body.append(f'<tr><td>{e(p["title"])}</td><td><a href="{GITHUB+e(p["pdf_path"])}">PDF</a></td><td><a href="{GITHUB+e(p["source_path"])}">Source</a></td><td><a href="{e(p["ssrn_url"])}">{e(p["abstract_id"])}</a></td></tr>')
    body.append('</tbody></table></div>')
body.append('<div class="note" style="margin-top:2rem"><p>The two notices are author proposals. The hormesis proposal is not an issued journal corrigendum. Original SSRN records retain their PDFs and now carry dated abstract correction links.</p><h2>Versions</h2><p>The October snapshot remains byte-for-byte intact. Its preparation metadata predates submission and the author-approved CC BY 4.0 option, which the dated receipt records. The <a href="https://github.com/thantiklermcirony/bounded-observer/tree/main/papers/capstone/">frozen v2.1 composition capstone</a> and <a href="library.html">earlier research inventory</a> remain separate historical sources.</p></div>')
(SITE/"papers.html").write_text(shell("Papers","Current manuscripts, SSRN receipt status and correction links.","".join(body),"papers.html"),encoding="utf-8",newline="\n")
lab=SITE/"labs.html"
lab_text=lab.read_text(encoding="utf-8")
start='<!-- CURRENT_PROGRAMME_LAB_START -->'
end='<!-- CURRENT_PROGRAMME_LAB_END -->'
tasks=''.join('<tr><td><a href="'+GITHUB+e(b['landing'])+'">'+e(b['title'])+'</a></td><td>'+e(b['next_task'])+'</td></tr>' for b in branches['branches'])
board=start+'<section><h2>Current work</h2><p>The lab works through question → specified candidate → frozen comparison → independent check → result → revision. These are next research tasks, distinct from completed experiments.</p><p><a href="'+GITHUB+'LAB.md">Runnable models and research tasks</a> · <a href="project.html">Branch contracts and evidence</a></p><div class="scroll"><table><thead><tr><th>Line</th><th>Next discriminating task</th></tr></thead><tbody>'+tasks+'</tbody></table></div><p><b>Arc competition:</b> the non-neural, rule-based 31-EchoFull predictor recorded validation-panel leaderboard entry rank 221 of 1,416 and overall score 0.2102, observed on 10 October 2026 (not a final standing). The competition and earlier GitHub Virtual Cell flights have separate records.</p><h2>Earlier laboratory records</h2></section>'+end
if start in lab_text:
    left,right=lab_text.split(start,1)
    _,tail=right.split(end,1)
    lab_text=left+board+tail
else:
    heading_end=lab_text.index('</h1>')+5
    lab_text=lab_text[:heading_end]+board+lab_text[heading_end:]
lab.write_text(lab_text,encoding='utf-8',newline='\n')
print("Generated project, paper and current laboratory pages from the registries.")
