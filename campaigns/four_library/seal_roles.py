"""Create separate calibration/evaluation answer files before fitting anything."""
import hashlib
import json
import numpy as np
from repair_common import *

def main():
    if (ROOT/'SOURCE.json').exists():raise RuntimeError('Already frozen')
    plan=json.loads((ROOT/'PLAN.json').read_text())
    roles={}
    for ds,info in plan['datasets'].items():
        d=ROOT/'answers'/ds
        if ds=='era5':
            with np.load(d/'calibration.npz') as a, np.load(d/'evaluation.npz') as b:
                theta=np.concatenate([a['theta'],b['theta']]);y=np.concatenate([a['target'],b['target']])
        else:
            with np.load(d/'historical.npz') as z:theta=z['theta'].copy();y=z['target'].copy()
        hashes=[hashlib.sha256(k).hexdigest() for k in keys(theta)]
        for seed in SEEDS:
            ranked=sorted(range(len(theta)),key=lambda i:hashlib.sha256(f'final:{seed}:{hashes[i]}'.encode()).hexdigest())
            if ds=='era5':pool=list(range(10));ev=list(range(10,17))
            else:
                n_eval=max(1,round(.2*len(theta)));ev=sorted(ranked[:n_eval]);pool=sorted(ranked[n_eval:])
            order=sorted(pool,key=lambda i:hashlib.sha256(f'calibration:{seed}:{hashes[i]}'.encode()).hexdigest())
            budgets=plan['era5_budgets'] if ds=='era5' else plan['budgets']
            selected={str(b):sorted(order[:min(b,len(order))]) for b in budgets}
            assert not set(pool)&set(ev)
            folder=d/f's{seed}'
            save_npz(folder/'calibration.npz',theta=theta[pool],target=y[pool],query_rows=np.asarray(pool))
            save_npz(folder/'evaluation.npz',theta=theta[ev],target=y[ev],query_rows=np.asarray(ev))
            spec=dict(dataset=ds,seed=seed,calibration_pool=pool,evaluation=ev,budgets=selected,
                input_hashes=hashes,calibration_sha256=sha(folder/'calibration.npz'),evaluation_sha256=sha(folder/'evaluation.npz'))
            roles[f'{ds}__s{seed}']=spec
    write_json(ROOT/'ROLES.json',roles)
    print('Sealed 15 dataset/partition roles; evaluation targets are stored separately.')

if __name__=='__main__':main()
