from pathlib import Path
import hashlib
import json
import os
import numpy as np

ROOT = Path(__file__).resolve().parent
MF = Path('/archive/mf_field')
ST = MF/'experiments/st_bench'
PYTHON = MF/'factory_mffp/.venv/bin/python'
EXCLUDE = 'node2900,node4200,node2901,node4002,node1702,node2119,node2809,node2810,node4004,node4007,node4008,node5003,node5004,node5005,node5101,node5103,node5104,node5106,node5202,node5203,node5204'
MODELS = ['mf_fno_transfer_film','mf_fno_allpairs','convnext_unet_film',
          'fno_fire_distcond','wno_transfer_film','mf_deeponet','st_hf_pod_gp']
CORRECTORS = ['uqcorr_transolver_pred','uqcorr_convnext_pred']
DATASETS = ['era5','sharp__cahn_hilliard','sharp__fisher_kpp_2d',
            'sharp__allen_cahn_2d','sharp__phase_field_crystal_2d']
SEEDS = [71,172,273]

def rel(ds):
    return ds.replace('__','/') if '__' in ds else 'core/'+ds

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return h.hexdigest()

def write_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+f'.tmp.{os.getpid()}')
    temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');os.replace(temp,path)

def save_npz(path, **arrays):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+f'.tmp.{os.getpid()}')
    with temp.open('wb') as f: np.savez_compressed(f,**arrays)
    os.replace(temp,path)

def keys(x):
    a=np.asarray(x,np.float32).copy();a[a==0]=0
    return [np.ascontiguousarray(r).tobytes() for r in a]

def purge_mask(x, reserved):
    prohibited=set(keys(reserved))
    return np.asarray([k not in prohibited for k in keys(x)])

def paired_target_rows(source_x,target_x):
    """Keep each target's own input; an exact source match is required.

    Duplicate target inputs are preserved (e.g. multiple climate simulators).
    Duplicate source inputs do not multiply their weight arbitrarily.
    """
    available=set(keys(source_x))
    return np.asarray([i for i,k in enumerate(keys(target_x)) if k in available],dtype=int)

def fix_allpairs_finetune_source(source):
    old='X_lf = train["cond_by_fid"][lf].astype(np.float32)'
    new='X_lf = train["cond_by_fid"][hf].astype(np.float32)  # repair: HF targets use their own parameters'
    assert source.count(old)==1,'All-pairs source changed; inspect before patching'
    return source.replace(old,new)

def verify_source():
    manifest=json.loads((ROOT/'SOURCE.json').read_text())
    for name,digest in manifest.items():
        assert sha(ROOT/name)==digest, f'Source changed: {name}'
    return manifest
