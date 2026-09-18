#!/usr/bin/env python3
"""Run all three rules on five fitting and five different Heat I query cases.

This is a small CLI demonstration, not the paper's fixed reporting partition.
"""
from pathlib import Path
import argparse,json,subprocess,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'outputs/ensemble_example');a=p.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
models=json.loads((ROOT/'configs/models.json').read_text());names=[models[f'M{i}']['archive_id'] for i in range(1,10)]
fields=[];target=None
for i,name in enumerate(names):
 with np.load(ROOT/'results/predictions/historical'/f'{name}__heat_generated.npz',allow_pickle=False) as z:
  fields.append(z['pred' if i<7 else 'pred_test'][:10].reshape(10,64,64))
  if target is None:target=z['target'][:10].reshape(10,64,64)
pred=np.stack(fields,axis=1)
np.savez_compressed(out/'fitting.npz',predictions=pred[:5],targets=target[:5],model_names=np.array(names))
np.savez_compressed(out/'queries.npz',predictions=pred[5:],model_names=np.array(names))
metrics={}
for rule in ['selected','inverse','fitted']:
 subprocess.run([sys.executable,str(ROOT/'ensemble/fit_fields.py'),'fit','--calibration',str(out/'fitting.npz'),
                 '--rule',rule,'--output',str(out/f'{rule}_weights.json')],check=True)
 subprocess.run([sys.executable,str(ROOT/'ensemble/fit_fields.py'),'predict','--predictions',str(out/'queries.npz'),
                 '--weights',str(out/f'{rule}_weights.json'),'--output',str(out/f'{rule}_prediction.npz')],check=True)
 with np.load(out/f'{rule}_prediction.npz') as z:
  y=z['predictions']
 err=np.linalg.norm((y-target[5:]).reshape(5,-1),axis=1)/np.maximum(np.linalg.norm(target[5:].reshape(5,-1),axis=1),1e-8)
 metrics[rule]={'mean_relative_l2':float(err.mean()),'per_case':err.tolist()}
(out/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics,indent=2))
