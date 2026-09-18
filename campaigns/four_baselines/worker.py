"""One missing baseline only: verify, short GPU check, then full resumable fit."""
import argparse,fcntl,subprocess,sys
from campaign_common import *

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--index',required=True,type=int);a=ap.parse_args();verify_source();tasks=json.loads((ROOT/'TASKS.json').read_text());t=tasks[a.index]
 assert t['dataset'] in json.loads((ROOT/'PLAN.json').read_text())['datasets']
 (ROOT/'claims').mkdir(exist_ok=True)
 with (ROOT/'claims'/f"{t['dataset']}__{t['model']}.lock").open('a') as f:
  fcntl.flock(f,fcntl.LOCK_EX)
  command=[sys.executable,'-u','baseline_worker.py','--dataset',t['dataset'],'--model',t['model'],'--threads','4','--device','cuda']
  subprocess.run(command+['--smoke'],cwd=ROOT,check=True)
  subprocess.run(command,cwd=ROOT,check=True)
if __name__=='__main__':main()
