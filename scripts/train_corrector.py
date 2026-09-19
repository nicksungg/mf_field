#!/usr/bin/env python3
"""Train one coarse ensemble member, assemble OOF inputs, or train M8/M9."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
from train import ROOT, configure

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('action',choices=['coarse','assemble','corrector'])
p.add_argument('--dataset',required=True)
p.add_argument('--model',choices=['M8','M9'],default='M8')
p.add_argument('--fold',type=int,choices=range(5),default=0)
p.add_argument('--variant',choices=['plain','hetero'],default='plain')
p.add_argument('--seed',type=int,default=42)
p.add_argument('--steps',type=int)
p.add_argument('--device',default='cuda')
p.add_argument('--work',type=Path,required=True)
a=p.parse_args()
if a.dataset=='era5':p.error('Use the ERA5 unpaired campaign in docs/TRAINING.md.')
# Restrict paths to the published roster.
import json
roster=json.loads((ROOT/'configs/datasets.json').read_text())
if a.dataset not in roster:p.error('Dataset is outside the release roster.')
work=a.work.resolve();work.mkdir(parents=True,exist_ok=True)
for name in ['diag_coarse.py','assemble_oof.py','corr_ens.py','corr_backbones.py','ct_common.py']:
    dst=work/name
    if not dst.exists():shutil.copy2(ROOT/'models/uqcorr'/name,dst)
env=configure()
if a.action=='coarse':
    cmd=[sys.executable,str(work/'diag_coarse.py'),'--name',a.dataset,'--nfolds','5',
         '--fold',str(a.fold),'--variant',a.variant,'--seed',str(a.seed),
         '--steps',str(a.steps or 30000),'--out-dir',str(work),'--ckpt-dir',str(work/'ck'),
         '--device',a.device]
elif a.action=='assemble':
    cmd=[sys.executable,str(work/'assemble_oof.py'),str(work),'--require-complete']
else:
    cmd=[sys.executable,str(work/'corr_ens.py'),'--name',a.dataset,'--backbone',
         'transolver' if a.model=='M8' else 'convnext','--input','pred',
         '--seed',str(a.seed),'--steps',str(a.steps or 6000),
         '--out-dir',str(work),'--ckpt-dir',str(work/'ck_corr'),'--device',a.device]
subprocess.run(cmd,cwd=work,env=env,check=True)
