"""Read-only import of the completed four-dataset campaign and its identities."""
from pathlib import Path
import io, json, subprocess, zipfile, hashlib

ROOT = Path(__file__).resolve().parents[1]

def main():
    code = r'''
from pathlib import Path
import hashlib, io, json, sys, zipfile
import numpy as np
r=Path('/archive/mf_field/experiments/four_baselines_20260915')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
complete=json.loads((r/'results/COMPLETE.json').read_text())
assert complete['complete'] and complete['n_datasets']==4
assert sha(r/'PLAN.json')==complete['plan_sha256']
assert sha(r/'results/comparison.csv')==complete['comparison_sha256']
plan=json.loads((r/'PLAN.json').read_text())
payload={};samples={};gallery=[]
def add(p):payload[str(p.relative_to(r))]=p.read_bytes()
for name in ['PLAN.json','ROLES.json','SOURCE.json','REUSE.json','COVERAGE.json','EXPERT_REUSE.json','TASKS.json','collect.py','ensemble_rules.py']:
 p=r/name
 if p.exists():add(p)
for p in (r/'results').glob('*'):
 if p.is_file():add(p)
for ds,info in plan['datasets'].items():
 result=json.loads((r/'results'/f'{ds}.json').read_text())
 wp=r/'weights'/f'{ds}.json';assert sha(wp)==result['weight_sha256'];add(wp)
 locked=json.loads(wp.read_text());assert not locked['evaluation_answers_used']
 for model in plan['models']:
  mp=r/'metadata'/ds/f'{model}.json';m=json.loads(mp.read_text())
  assert m['scientific_result'] and not m.get('smoke',False)
  assert m['prediction_sha256']==locked['prediction_sha256'][model]
  add(mp)
 for model,artifact in result['baseline_artifacts'].items():
  if artifact['kind']=='per_case_errors':
   p=r/'baseline_errors'/ds/f'{model}.json';assert sha(p)==artifact['scalar_errors_sha256'];add(p)
  else:
   p=r/'metadata'/ds/f'{model}.json';assert sha(p)==artifact['metadata_sha256'];add(p)
 hf=info['levels'][str(info['hf_level'])];p=Path(hf['original_path'])
 assert sha(p)==hf['original_sha256']
 with np.load(p,allow_pickle=False) as z:
  x=z['x'];y=z['y'];a=y[0].copy();theta=x[0].copy()
  samples[ds+'__y']=a;samples[ds+'__x']=theta
  gallery.append(dict(dataset=ds,level=info['hf_level'],path=str(p),row=0,
   role='HF training',selection='first row, fixed for every dataset',
   x=dict(source_shape=list(x.shape),dtype=str(x.dtype),sample_sha256=hashlib.sha256(theta.tobytes()).hexdigest()),
   y=dict(source_shape=list(y.shape),dtype=str(y.dtype),sample_sha256=hashlib.sha256(a.tobytes()).hexdigest()),
   native_grid=hf['grid'],source_file_sha256=hf['original_sha256']))
b=io.BytesIO();np.savez_compressed(b,**samples);payload['gallery_samples.npz']=b.getvalue()
payload['gallery_manifest.json']=json.dumps({'datasets':gallery},indent=2).encode()
manifest={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()}
payload['IMPORT_MANIFEST.json']=json.dumps({'source_root':str(r),'sha256':manifest},indent=2).encode()
b=io.BytesIO()
with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
 for name,value in payload.items():z.writestr(name,value)
sys.stdout.buffer.write(b.getvalue())
'''
    run = subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','archive-host',
        '/archive/mf_field/experiments/era5_baselines_20260915/.venv/bin/python -'],
        input=code.encode(),capture_output=True,timeout=300)
    if run.returncode:raise RuntimeError(run.stderr.decode())
    output=ROOT/'data/four_dataset_completion'
    with zipfile.ZipFile(io.BytesIO(run.stdout)) as z:
        for name in z.namelist():
            p=output/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
    m=json.loads((output/'IMPORT_MANIFEST.json').read_text())
    for name,value in m['sha256'].items():assert hashlib.sha256((output/name).read_bytes()).hexdigest()==value
    print('Imported and verified',len(m['sha256']),'campaign artifacts.')

if __name__=='__main__':main()
