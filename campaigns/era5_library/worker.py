import argparse
import os
import subprocess
import sys
from era5_common import ROOT, verify_source

parser=argparse.ArgumentParser()
parser.add_argument('kind',choices=['coarse','corrector'])
args=parser.parse_args()
verify_source()
index=int(os.environ['SLURM_ARRAY_TASK_ID'])
if args.kind=='coarse':
    command=['run_coarse.py','--task',str(index)]
else:
    command=['run_corrector.py','--backbone',['transolver','convnext'][index]]
subprocess.run([sys.executable,'-u',*command],cwd=ROOT,check=True)
