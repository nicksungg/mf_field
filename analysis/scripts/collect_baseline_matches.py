"""Freeze seed-42 baseline errors and audit their alignment to the existing splits.

No weights, split assignments, or trained models change. Scalar errors are those
computed before the lossy float16 field export, not errors recomputed from that export.
"""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from build_data import ROOT,load,dump,digest

def main():
    work=ROOT.parent;release=work/'mf_field_surrogate_bench'
    summary=load(ROOT/'data/individual_model_summary.json')
    ds=sorted(summary['means']);library=summary['checks']['models']
    arms=load(release/'results/tables/results_page_data.json')['surr']
    extra=[m for m in arms if m not in library]
    audit={r['dataset']:r for r in load(work/'mf_field_ensemble_audit_20260913/raw_input_audit.json')['rows']}
    specs=[];snap=[];out=ROOT/'data/baseline_raw';out.mkdir(exist_ok=True)
    priority=['reevaluated','st_bench_reruns','st_bench','leaderboard_legacy']
    for d in ds:
        a=audit[d];specs.append(dict(dataset=d,test_path=a['hf_test_input']['path'],hf_level=a['hf_level'],models=extra))
        for m in extra:
            selected=None
            for folder in priority:
                files=sorted((release/'results/raw_json'/folder).glob(m+'__'+d+'__*s42.json'))
                files=[f for f in files if load(f).get('splits',{}).get('test_hf',{}).get('rel_l2_per_sample')]
                if len(files)>1:raise ValueError(('ambiguous source',d,m,files))
                if files:selected=files[0];break
            if selected:
                raw=load(selected);name=m+'__'+d+'__s42.json';(out/name).write_bytes(selected.read_bytes())
                snap.append(dict(dataset=d,model=m,seed=42,file='baseline_raw/'+name,
                    sha256=digest(selected),source=str(selected.relative_to(release)),work_grid=raw.get('work_grid')))
            else:snap.append(dict(dataset=d,model=m,seed=42,missing=True))
    code=r'''
import hashlib,json,zipfile
from pathlib import Path
import numpy as np
specs=__SPEC__
release=Path('/archive/mf_field/release/predictions_full')
refroot=Path('/archive/mf_field/experiments/fieldgate_matched_20260912/predictions')
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
records=[]
for spec in specs:
    ds=spec['dataset'];r=dict(spec)
    f=Path(spec['test_path']);r['test_archive_sha256']=digest(f)
    with np.load(f,allow_pickle=False) as z:x=z['x']
    # Match the historical cache's exact float32 input hashes.
    r['input_shape']=list(x.shape)
    r['input_row_sha256']=[hashlib.sha256(np.ascontiguousarray(v,np.float32).tobytes()).hexdigest() for v in x]
    with np.load(refroot/('mf_fno_transfer_film__'+ds+'.npz')) as z:
        target=z['target'];theta=z['theta'];grid=z['work_grid'].tolist()
        r['reference_sha256']=digest(refroot/('mf_fno_transfer_film__'+ds+'.npz'))
        assert x.shape==theta.shape and np.allclose(x.astype(np.float32),theta,rtol=0,atol=0)
        r['input_order_matches_reference']=True;r['grid']=grid;r['n']=len(x)
        r['reference_target_sha256']=hashlib.sha256(target.tobytes()).hexdigest()
    r['archives']={}
    for model in spec['models']:
        p=release/(model+'__'+ds+'__s42.npz')
        if not p.exists():continue
        with np.load(p,allow_pickle=False) as z:
            a=z['target'].astype(np.float64);b=target.astype(np.float64)
            v=dict(archive_sha256=digest(p),grid=z['work_grid'].tolist(),n=len(a),
                   errors=z['rel_l2_per_sample'].astype(float).tolist(),target_dtype=str(z['target'].dtype))
            if a.shape==b.shape and v['grid']==grid:
                # Classical exports can store normalized fields; relative L2 is scale invariant.
                scale=float(np.sum(a*b)/max(np.sum(b*b),1e-300))
                residual=np.linalg.norm(a-scale*b,axis=1)/np.maximum(abs(scale)*np.linalg.norm(b,axis=1),1e-30)
                v.update(target_scale=scale,target_alignment_max_rel=float(residual.max()),
                         target_rows_match=bool(residual.max()<0.002))
            else:v['target_rows_match']=False
            r['archives'][model]=v
    records.append(r)
print(json.dumps(records))
'''.replace('__SPEC__',repr(specs))
    p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','login006',
        '/archive/mf_field/factory_mffp/.venv/bin/python -'],input=code.encode(),capture_output=True,timeout=300)
    if p.returncode:raise RuntimeError(p.stderr.decode())
    remote=json.loads(p.stdout)
    dump(ROOT/'data/baseline_alignment.json',dict(raw_sources=snap,remote_checks=remote,
        rule='Seed 42; source priority reevaluated, st_bench_reruns, st_bench, leaderboard_legacy; never selected by error',
        source_raw_root='mf_field_surrogate_bench/results/raw_json'))
    print('Frozen',sum(not r.get('missing') for r in snap),'baseline records across',len(ds),'datasets.')
    print('Saved-target checks',sum(len(r['archives']) for r in remote),'; failed target matches',
        [(r['dataset'],m) for r in remote for m,v in r['archives'].items() if not v['target_rows_match']])

if __name__=='__main__':main()
