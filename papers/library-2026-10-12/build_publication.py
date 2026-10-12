"""Build publication sources and PDFs using the installed XeLaTeX toolchain."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'toolchain'))
import pypandoc
import yaml
from pypdf import PdfReader

default_tex=os.getenv('XELATEX') or shutil.which('xelatex') or str(Path(os.getenv('LOCALAPPDATA',''))/'Programs/MiKTeX/miktex/bin/x64/xelatex.exe')
default_poppler=os.getenv('PDFTOPPM') or shutil.which('pdftoppm')
parser=argparse.ArgumentParser();parser.add_argument('--only');parser.add_argument('--render',action='store_true');parser.add_argument('--allow-package-install',action='store_true')
parser.add_argument('--xelatex',default=default_tex);parser.add_argument('--pdftoppm',default=default_poppler)
parser.add_argument('--mainfont',default='Cambria');parser.add_argument('--mathfont',default='Cambria Math')
args=parser.parse_args()
TEX=Path(args.xelatex)
POPPLER=Path(args.pdftoppm) if args.pdftoppm else None
if args.render and POPPLER is None:parser.error('PNG rendering requires pdftoppm on PATH or --pdftoppm PATH.')
for folder in ['latex','pdf','build','qa']:(BASE/folder).mkdir(exist_ok=True)
header=BASE/'build'/('header_'+(args.only or 'all')+'.tex')
header.write_text(r'''\pagestyle{plain}
\setlength{\emergencystretch}{3em}
\setlength{\parskip}{0.35em}
''',encoding='utf-8')
sources=sorted([* (BASE/'papers').glob('*.md'),* (BASE/'corrections').glob('*.md')])
if args.only:sources=[p for p in sources if p.stem==args.only]
assert sources,'No requested manuscript exists.'
report=[]
for source in sources:
    name=source.stem;tex=BASE/'latex'/f'{name}.tex';build=BASE/'build'/name;build.mkdir(exist_ok=True)
    pypandoc.convert_file(str(source),'latex',format='markdown+tex_math_dollars+tex_math_single_backslash',outputfile=str(tex),extra_args=[
        '--standalone','--wrap=none','--top-level-division=section',
        '-V','documentclass=article','-V','fontsize=11pt','-V','papersize=a4',
        '-V','geometry:margin=24mm','-V','mainfont='+args.mainfont,'-V','mathfont='+args.mathfont,
        '-V','colorlinks=true','-V','linkcolor=black','-V','urlcolor=blue',
        '--include-in-header='+str(header)])
    latex=tex.read_text(encoding='utf-8')
    text=source.read_text(encoding='utf-8')
    front=re.match(r'^---\n(.*?)\n---',text,re.S)
    meta=yaml.safe_load(front.group(1)) if front else {}
    if meta.get('affiliation') or meta.get('orcid'):
        info=[]
        if meta.get('affiliation'):info.append(r'{\small '+str(meta['affiliation'])+'}')
        if meta.get('orcid'):info.append(r'{\small ORCID: '+str(meta['orcid'])+'}')
        latex=latex.replace(r'\author{Daniel John Murray}',r'\author{Daniel John Murray\\'+r'\\'.join(info)+'}')
    if meta.get('version'):
        latex=re.sub(r'\\date\{([^{}]*)\}',lambda m:r'\date{'+m.group(1)+r'\\{\small '+str(meta['version'])+'}}',latex,count=1)
    # These manuscripts use no table footnotes. Avoid Pandoc's optional
    # longtable footnote helper when that package is absent locally.
    table_notes=any('\\footnote{' in m.group(0) for m in re.finditer(r'\\begin\{longtable\}.*?\\end\{longtable\}',latex,re.S))
    if not table_notes:
        latex=latex.replace(r'\IfFileExists{footnotehyper.sty}{\usepackage{footnotehyper}}{\usepackage{footnote}}'+'\n'+r'\makesavenoteenv{longtable}'+'\n','')
    latex=latex.replace(r'\usepackage{bookmark}',r'\IfFileExists{bookmark.sty}{\usepackage{bookmark}}{\usepackage{hyperref}}')
    latex=re.sub(r'\\href\{([^{}]+)\}\{((?:doi:|arXiv:)[^{}]+)\}',
                 lambda m:r'\href{'+m.group(1)+r'}{\nolinkurl{'+m.group(2)+'}}',latex)
    # Plain DOI bibliography labels also need discretionary URL breaks.
    latex=re.sub(r'(?<![\w{])doi:(10\.\d{4,9}/[A-Za-z0-9./()_:;\-]+)',
                 lambda m:r'\href{https://doi.org/'+m.group(1).rstrip('.')+r'}{\nolinkurl{doi:'+m.group(1).rstrip('.')+'}}'+('.' if m.group(1).endswith('.') else ''),latex)
    tex.write_text(latex,encoding='utf-8')
    command=[str(TEX),'--enable-installer' if args.allow_package_install else '--disable-installer','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-output-directory='+str(build),str(tex)]
    runs=[]
    for i in range(2):
        run=subprocess.run(command,cwd=BASE/'latex',capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=240)
        (build/f'compile_{i+1}.txt').write_text(run.stdout+'\n'+run.stderr,encoding='utf-8');runs.append(run.returncode)
        if run.returncode:break
    built=build/f'{name}.pdf'
    log=(build/f'{name}.log').read_text(encoding='utf-8',errors='replace') if (build/f'{name}.log').exists() else ''
    warnings=[line for line in log.splitlines() if any(x in line for x in ['Overfull','Missing character','undefined references','Undefined control sequence'])]
    row=dict(source=str(source.relative_to(BASE)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),name=name,compile_exit_codes=runs,warnings=warnings)
    if runs[-1]==0 and built.exists():
        final=BASE/'pdf'/f'{name}.pdf';final.write_bytes(built.read_bytes());reader=PdfReader(final)
        row.update(pdf=str(final.relative_to(BASE)),pages=len(reader.pages),pdf_sha256=hashlib.sha256(final.read_bytes()).hexdigest())
        if args.render:
            images=BASE/'qa'/name;images.mkdir(exist_ok=True)
            for stale in images.glob('page-*.png'):stale.unlink()
            render=subprocess.run([str(POPPLER),'-r','115','-png',str(final),str(images/'page')],capture_output=True,text=True,timeout=240)
            row.update(render_exit_code=render.returncode,rendered_pages=len(list(images.glob('page-*.png'))))
    report.append(row)
    (build/'result.json').write_text(json.dumps(row,indent=2),encoding='utf-8')
    print(json.dumps(row,ensure_ascii=True))
existing=BASE/'build_report.json'
prior=json.loads(existing.read_text(encoding='utf-8')) if existing.exists() else []
combined={x['name']:x for x in prior}
combined.update({x['name']:x for x in report})
if not args.only:existing.write_text(json.dumps(list(combined.values()),indent=2),encoding='utf-8')
if any(x['compile_exit_codes'][-1]!=0 for x in report):sys.exit(1)
