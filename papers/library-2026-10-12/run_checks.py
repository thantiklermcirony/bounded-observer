"""Run the independent mathematical modules from any working directory."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parent
reports=[]
for script in sorted((ROOT/'checks').glob('*.py')):
    result=subprocess.run([sys.executable,str(script)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
    row={'script':script.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'exit_code':result.returncode}
    reports.append(row)
    if result.returncode:
        print(result.stdout);print(result.stderr);break
    # Three modules print, rather than independently save, a complete JSON receipt.
    if script.name in ['constants_dynamics_checks.py','paper6_checks.py','hormesis_revision_checks.py','deformed_kinematics_checks.py']:
        parsed=json.loads(result.stdout)
        script.with_suffix('.json').write_text(json.dumps(parsed,indent=2)+'\n',encoding='utf-8')
    print('PASS '+script.name)
receipt={'scope':'Analytic identities, explicit countermodels and finite numerical constructions; no empirical dataset replication is claimed.','passed':sum(r['exit_code']==0 for r in reports),'modules':reports}
receipt_path=ROOT/'verification/check_run.json' if (ROOT/'verification').exists() else ROOT/'check_run.json'
receipt_path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
if len(reports)!=len(list((ROOT/'checks').glob('*.py'))) or any(r['exit_code'] for r in reports):sys.exit(1)
