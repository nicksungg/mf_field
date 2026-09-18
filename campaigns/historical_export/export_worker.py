import argparse
import fcntl
import json
import subprocess
import time
from config import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--device',choices=['cpu','gpu'],required=True)
    ap.add_argument('--only',default='');a=ap.parse_args()
    plan=json.loads((ROOT/'plan.json').read_text())
    for t in plan['tasks']:
        if t['device']!=a.device or (a.only and t['dataset']!=a.only):continue
        tid=t['id']
        if (ROOT/'export_results'/f'{tid}.json').exists():continue
        with open(ROOT/'claims'/f'{tid}.lock','w') as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:continue
            if (ROOT/'export_results'/f'{tid}.json').exists():continue
            with open(ROOT/'logs'/f'{tid}.log','a') as log:
                r=subprocess.run([str(PYTHON),'-u',str(ROOT/'export_one.py'),'--task',tid],
                                 stdout=log,stderr=subprocess.STDOUT,timeout=1800)
            print(tid,'exit',r.returncode,flush=True)
            if r.returncode:
                write_json(ROOT/'export_results'/f'{tid}.failure.json',dict(task=t,code=r.returncode))
                raise RuntimeError(f'Export failed: {tid}; inspect log')

if __name__=='__main__':main()
