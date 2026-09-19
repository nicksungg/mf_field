"""Smoke test the entire unpaired coarse prediction and corrector path."""
import json
import os
import subprocess
import sys
import time
import numpy as np
import torch
from era5_common import ROOT, sha, verify_source, write_json

def run(*args):
    print('CHECK', *args, flush=True)
    subprocess.run([sys.executable, '-u', *args], cwd=ROOT, check=True)

def main():
    verify_source()
    assert torch.cuda.is_available() and torch.cuda.device_count()==1
    run('-m','unittest','test_unpaired.py','test_coarse.py','test_corrector.py','test_ensemble.py')
    for task in range(20):
        run('run_coarse.py','--task',str(task),'--smoke')
    run('run_coarse.py','--assemble','--smoke')
    with np.load(ROOT/'smoke/coarse/oof.npz') as z:
        assert z['mean_train'].shape==(55,128,256)
        assert z['mean_query'].shape==(17,128,256)
        assert np.all(z['n_members_train']==4) and int(z['members_query'])==4
    for backbone in ['transolver','convnext']:
        run('run_corrector.py','--backbone',backbone,'--smoke')
        name=f'uqcorr_{backbone}_pred__era5'
        meta=json.loads((ROOT/'smoke/metadata'/f'{name}.json').read_text())
        assert meta['smoke'] and meta['prediction_sha256']==sha(ROOT/'smoke/predictions'/f'{name}.npz')
        with np.load(ROOT/'smoke/predictions'/f'{name}.npz') as z:
            assert z['pred'].shape==(17,32768) and np.isfinite(z['pred']).all()
    write_json(ROOT/'PREFLIGHT.json',dict(passed=True,source_sha256=sha(ROOT/'SOURCE.json'),
        working_data_sha256=sha(ROOT/'data/training.npz'),coarse_tasks=20,
        corrected_models=['uqcorr_transolver_pred','uqcorr_convnext_pred'],
        oof_four_members=True,query_targets_used=False,smoke_outputs_separate=True,
        job_id=os.environ.get('SLURM_JOB_ID'),gpu=torch.cuda.get_device_name(),
        torch=torch.__version__,numpy=np.__version__,time=time.time()))
    print('PASSED: unpaired ERA5 prediction, OOF assembly and both correctors')

if __name__=='__main__':
    main()
