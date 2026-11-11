"""Run repeatable engineering checks. Does not certify cooking or medical accuracy."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--node',default='node');parser.add_argument('--output');args=parser.parse_args()
    commands=[[sys.executable,'-X','utf8','-m','unittest','discover','-s','tests','-v'],[args.node,'--test','tests/core.test.cjs','tests/household.test.cjs']]
    results=[]
    for cmd in commands:
        p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        results.append({'command':cmd,'passed':p.returncode==0,'output':p.stdout+p.stderr})
        print(p.stdout+p.stderr)
    report={'scope':'Engineering regression tests; not a culinary certification','suites':results,'passed':all(r['passed'] for r in results)}
    if args.output: Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    sys.exit(0 if report['passed'] else 1)
