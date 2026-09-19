import json
import subprocess
import numpy as np
from repair_common import *

def main():
    subprocess.run([str(PYTHON),'-m','unittest','discover','-s',str(ROOT),'-p','test_*.py'],check=True)
    plan=json.loads((ROOT/'PLAN.json').read_text())
    counts={}
    for ds,info in plan['datasets'].items():
        d=ROOT/'data'/rel(ds)
        with np.load(d/f"test_l{info['hf_level']}.npz") as z:query=z['x'].copy()
        n_removed=0
        for level,record in info['levels'].items():
            with np.load(d/f'train_l{level}.npz') as z:x=z['x'].copy()
            assert purge_mask(x,query).all(),(ds,level)
            assert sha(d/f'train_l{level}.npz')==record['prepared_sha256']
            n_removed+=len(record['removed_rows'])
        counts[ds]=dict(base_hf=info['n_base_hf_train'],reserved_query=len(query),removed_rows_all_levels=n_removed)
    subprocess.run([str(PYTHON),str(ROOT/'seal_roles.py')],check=True)
    subprocess.run([str(PYTHON),str(ROOT/'run_base.py'),'--dataset','era5','--model','st_hf_pod_gp','--smoke'],check=True)
    write_json(ROOT/'smoke/CPU_QA.json',dict(passed=True,counts=counts,
        unit_tests='purge, exact join, HF finetune association, interrupted optimizer replay',
        source_sha256={p.name:sha(p) for p in ROOT.glob('*.py')}))
    print('CPU PREFLIGHT PASSED',flush=True)

if __name__=='__main__':main()
