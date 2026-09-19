#!/usr/bin/env python3
"""Create a writable retraining workspace from the archived campaign sources.

No training runs until the printed worker command is invoked. Data arrays are
linked without changing bytes. A new source manifest records portable copies.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def link(dst,src):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists() or dst.is_symlink():return
    dst.symlink_to(os.path.relpath(src,dst.parent),target_is_directory=src.is_dir())

def prepare(name,out):
    src=ROOT/'campaigns'/name
    if out.exists():raise ValueError('Use a new, empty output directory.')
    out.mkdir(parents=True)
    omit={'data','flat_data','answers','predictions','metadata','weights','results','baseline_errors',
          'checkpoints','coarse','claims','smoke','logs','monitor','__pycache__','source'}
    for p in src.iterdir():
        if p.name in omit or p.suffix in ('.sbatch','.sh'):continue
        if p.is_dir():shutil.copytree(p,out/p.name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        else:shutil.copy2(p,out/p.name)
    if name=='era5_baselines':
        link(out/'data/core/era5',ROOT/'datasets/core/era5')
        # Additional train-only mean control is tracked by the original input manifest.
        extra=src/'data/training_mean.npz'
        if extra.exists():link(out/'data/training_mean.npz',extra)
        link(out/'answers',ROOT/'datasets/answers')
        link(out/'flat_data/era5',out/'data/core/era5')
    elif name=='four_final_library':
        for d in json.loads((src/'PLAN.json').read_text())['datasets']:
            link(out/'data'/d,ROOT/'campaigns/four_library/data'/d.replace('__','/'))
    elif name=='era5_library':
        link(out/'data',src/'data')
        # Saved OOF inputs allow independent corrector retraining; --fresh-coarse can
        # be implemented by removing this copy and rerunning all 20 coarse tasks.
        if (src/'coarse').exists():shutil.copytree(src/'coarse',out/'coarse')
        link(out/'answers',ROOT/'datasets/answers')
    else:
        lib=ROOT/'campaigns/four_library'
        link(out/'data/sharp',lib/'data/sharp')
        link(out/'data/core/era5',ROOT/'datasets/core/era5')
        link(out/'answers',lib/'answers')
        for d in ['sharp__allen_cahn_2d','sharp__cahn_hilliard','sharp__fisher_kpp_2d','sharp__phase_field_crystal_2d','era5']:
            rel=d.replace('__','/') if '__' in d else 'core/'+d
            link(out/'flat_data'/d,out/'data'/rel)
    # Worker paths embedded in the four-baseline plan must point to staged inputs.
    planfile=out/'PLAN.json'
    if planfile.exists():
        plan=json.loads(planfile.read_text())
        for d,entry in plan.get('datasets',{}).items():
            rel=d.replace('__','/') if '__' in d else 'core/'+d
            if 'data_dir' in entry:entry['data_dir']=str(out/'data'/rel)
        write(planfile,plan)
    old_source=sha(src/'SOURCE.json') if (src/'SOURCE.json').exists() else None
    sources={str(p.relative_to(out)):sha(p) for p in out.rglob('*')
             if p.is_file() and p.suffix=='.py' and '__pycache__' not in p.parts}
    write(out/'SOURCE.json',sources)
    if name=='era5_baselines':
        mf=out/'INPUT_MANIFEST.json';m=json.loads(mf.read_text())
        for name_,entry in m['files'].items():
            if entry['role']!='answer':
                assert sha(out/name_)==entry['sha256'],name_
        audit=json.loads((out/'INPUT_AUDIT.json').read_text())
        audit['input_manifest_sha256']=sha(mf);audit['plan_sha256']=sha(planfile)
        audit['release_preparation']='Input byte identities checked; paths and source manifest relocated.'
        write(out/'INPUT_AUDIT.json',audit)
    write(out/'RELEASE_PREPARATION.json',{'campaign':name,'archived_source_manifest_sha256':old_source,
        'portable_source_manifest_sha256':sha(out/'SOURCE.json'),
        'note':'This is a retraining workspace, not the recorded historical run.'})
    print(out)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('campaign',choices=['four_library','four_baselines','era5_library','era5_baselines','four_final_library'])
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();prepare(a.campaign,a.output.resolve())
