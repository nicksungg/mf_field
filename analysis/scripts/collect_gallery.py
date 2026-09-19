"""Collect row zero of each HF training table; read only on CLUSTER.

The bundled gallery snapshot suffices for all later offline figure builds.
Samples are selected by row index before inspecting fields or prediction errors.
"""
from pathlib import Path
import hashlib, io, json, subprocess, zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

def main():
    audit = json.loads((ROOT.parent/'mf_field_ensemble_audit_20260913/raw_input_audit.json').read_text())
    spec = [dict(dataset=r['dataset'], level=r['hf_level'], path=next(
        f['path'] for f in r['training_inputs'] if Path(f['path']).stem == 'train_l'+str(r['hf_level'])))
        for r in audit['rows']]
    code = r'''
import hashlib,io,json,sys,zipfile
from pathlib import Path
import numpy as np
spec=__SPEC__
arrays={};records=[]
for rec in spec:
    r=dict(rec,row=0,role='HF training',selection='first row, fixed for every dataset')
    with zipfile.ZipFile(r['path']) as z:
        for key in ['x','y']:
            name=key+'.npy'
            with z.open(name) as f:
                version=np.lib.format.read_magic(f)
                shape,order,dtype=(np.lib.format.read_array_header_1_0(f) if version==(1,0) else np.lib.format.read_array_header_2_0(f))
                assert not order and not dtype.hasobject
                count=int(np.prod(shape[1:]));raw=f.read(count*dtype.itemsize)
                a=np.frombuffer(raw,dtype=dtype).copy().reshape(shape[1:])
                assert np.isfinite(a).all()
            arrays[r['dataset']+'__'+key]=a
            r[key]=dict(source_shape=list(shape),dtype=str(dtype),member_crc32=z.getinfo(name).CRC,
                sample_sha256=hashlib.sha256(a.tobytes()).hexdigest())
    n=arrays[r['dataset']+'__y'].size
    grid=[721,1440] if r['dataset']=='era5' else [int(round(n**.5))]*2
    assert int(np.prod(grid))==n
    r['native_grid']=grid;records.append(r)
b=io.BytesIO()
with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
    a=io.BytesIO();np.savez_compressed(a,**arrays);z.writestr('gallery_samples.npz',a.getvalue())
    z.writestr('gallery_manifest.json',json.dumps(dict(selection='Row zero of every HF training table; no test answers or predictions used',datasets=records),indent=2))
sys.stdout.buffer.write(b.getvalue())
'''.replace('__SPEC__', repr(spec))
    p = subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','login006',
        '/archive/mf_field/factory_mffp/.venv/bin/python -'],
        input=code.encode(),capture_output=True,timeout=60)
    if p.returncode: raise RuntimeError(p.stderr.decode())
    with zipfile.ZipFile(io.BytesIO(p.stdout)) as z:
        for name in ['gallery_samples.npz','gallery_manifest.json']:
            (ROOT/'data'/name).write_bytes(z.read(name))
    manifest=json.loads((ROOT/'data/gallery_manifest.json').read_text())
    assert len(manifest['datasets'])==25
    with np.load(ROOT/'data/gallery_samples.npz') as z:
        for r in manifest['datasets']:
            for key in ['x','y']:
                assert hashlib.sha256(z[r['dataset']+'__'+key].tobytes()).hexdigest()==r[key]['sample_sha256']
    print('Collected and verified 25 fixed-index HF training samples.')

if __name__=='__main__':main()
