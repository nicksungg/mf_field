import subprocess
import sys
from repair_common import ROOT,PYTHON,MODELS

i=int(sys.argv[1])
models=MODELS[:-1]+['fno_hf_only_control']
if i<len(models):
    command=['run_base.py','--dataset','era5','--model',models[i],'--smoke']
elif i==7:command=['run_uq.py','--dataset','sharp__phase_field_crystal_2d','--kind','coarse','--smoke']
elif i in [8,9]:command=['run_uq.py','--dataset','sharp__phase_field_crystal_2d','--kind','corrector',
                       '--backbone','transolver' if i==8 else 'convnext','--smoke']
else:raise ValueError(i)
subprocess.run([str(PYTHON),'-u',*command],cwd=ROOT,check=True)
