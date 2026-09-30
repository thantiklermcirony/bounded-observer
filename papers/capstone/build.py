import subprocess
parts=['00_front.md','01_law.md','02_horizon.md','03_charts.md','04_test.md','05_appendix.md']
open('UHL_v2.md','w').write('\n'.join(open(p).read() for p in parts))
subprocess.run(['pandoc','UHL_v2.md','-s','--mathml','--css','style.css','--embed-resources','-o','UHL_v2.html'],check=True)
subprocess.run(['pandoc','UHL_v2.md','-o','UHL_v2.docx'],check=True)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto('file:///home/claude/ms2/UHL_v2.html'); pg.wait_for_timeout(1500)
    pg.pdf(path='UHL_v2.pdf',format='A4',display_header_footer=True,header_template='<div></div>',
      footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#666">Murray — Bounded Composition and Its Horizons, v2.1 — <span class="pageNumber"></span>/<span class="totalPages"></span></div>',
      margin={'top':'18mm','bottom':'18mm','left':'18mm','right':'18mm'})
    b.close()
