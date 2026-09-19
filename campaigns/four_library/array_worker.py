import argparse
import json
import os
import subprocess
from repair_common import *

ap=argparse.ArgumentParser();ap.add_argument('kind',choices=['base_gpu','base_cpu','coarse','corrector'])
ap.add_argument('--dataset');a=ap.parse_args()
verify_source();plan=json.loads((ROOT/'PLAN.json').read_text());index=int(os.environ['SLURM_ARRAY_TASK_ID'])
if a.kind.startswith('base_'):
    device=a.kind.split('_')[1];tasks=[t for t in plan['tasks'] if t['kind']=='base' and t['device']==device]
    t=tasks[index];command=['run_base.py','--dataset',t['dataset'],'--model',t['model']]
elif a.kind=='coarse':
    tasks=[t for t in plan['tasks'] if t['kind']=='coarse' and t['dataset']==a.dataset];t=tasks[index]
    command=['run_uq.py','--dataset',t['dataset'],'--kind','coarse','--fold',str(t['fold']),
             '--seed',str(t['seed']),'--variant',t['variant']]
else:
    command=['run_uq.py','--dataset',a.dataset,'--kind','corrector','--backbone',['transolver','convnext'][index]]
subprocess.run([str(PYTHON),'-u',*command],cwd=ROOT,check=True)
