#!/usr/bin/env python3
"""Regenerate selected in-house fields at the exact bundled parameter inputs.

This smoke/inspection entry point deliberately writes a new file. Full sampling,
sharding and solver drivers are preserved in generators/.
"""
import argparse,importlib.util,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
 sys.modules[name]=m;spec.loader.exec_module(m);return m

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--dataset',required=True,choices=['poisson_generated_v2','heat_generated','lid_driven_cavity_v2','ext__wave_2d','ext__eikonal_2d','ext__rayleigh_benard_2d','ext__cahn_hilliard_2d'])
 p.add_argument('--level',type=int,default=1);p.add_argument('--rows',type=int,default=1)
 p.add_argument('--split',choices=['train','test'],default='test');p.add_argument('--output',required=True,type=Path)
 a=p.parse_args();rel=a.dataset.replace('__','/') if '__' in a.dataset else 'core/'+a.dataset
 if a.output.exists():p.error('Use a new output path; reference arrays are never overwritten.')
 with np.load(ROOT/'datasets'/rel/f'{a.split}_l{a.level}.npz',allow_pickle=False) as z:
  x=z['x'][:a.rows].copy();ref=z['y'][:a.rows].copy()
 cells=ref.shape[1];n=int(np.sqrt(cells));assert n*n==cells
 if a.dataset in ('poisson_generated_v2','heat_generated'):
  original_argv=sys.argv;sys.argv=[str(ROOT/'generators/datafix/gen_core_v2.py')]
  m=load(ROOT/'generators/datafix/gen_core_v2.py','released_core');sys.argv=original_argv
  solve=m.poisson_solve if a.dataset=='poisson_generated_v2' else m.heat_solve
  y=np.stack([solve(n,row).reshape(-1) for row in x])
 elif a.dataset=='lid_driven_cavity_v2':
  m=load(ROOT/'generators/cavity/lid_driven_cavity.py','released_cavity')
  fields=[]
  for row in x:
   omega,steps,resid=m.solve_cavity(float(row[0]),n);fields.append(omega.reshape(-1))
  y=np.stack(fields)
 else:
  sys.path.insert(0,str(ROOT/'generators/ext'));m=load(ROOT/'generators/ext/solvers.py','released_ext')
  name=a.dataset.split('__',1)[1];entry=m.REGISTRY[name]
  y=np.asarray(entry['solve'](x,n)).reshape(len(x),-1)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 np.savez_compressed(a.output,x=x,y=y,reference=ref)
 error=np.linalg.norm(y-ref,axis=1)/np.maximum(np.linalg.norm(ref,axis=1),1e-12)
 print(json.dumps({'dataset':a.dataset,'level':a.level,'rows':len(x),'relative_difference_from_archive':error.tolist()},indent=2))
if __name__=='__main__':main()
