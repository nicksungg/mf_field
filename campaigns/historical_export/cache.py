"""Audit units, row identities and coverage; cache features separately from supervised errors."""
import argparse
import json
import hashlib
import time
import numpy as np
from config import *
from features import field_features,FEATURE_NAMES

def build_dataset(d):
    plan=json.loads((ROOT/'plan.json').read_text());paths=[ROOT/'predictions'/f'{m}__{d}.npz' for m in MODELS]
    if not all(p.exists() for p in paths):return False
    output=ROOT/'cache'/d
    if (output/'audit.json').exists():return True
    zs=[np.load(p) for p in paths]
    ref=zs[0];theta=ref['theta'];y=ref['target'].astype(np.float64);grid=tuple(ref['work_grid'])
    overlap=np.logical_or.reduce([z['base_train_overlap'] for z in zs])
    ia=json.loads((ROOT/'input_audits'/f'{d}.json').read_text())
    err=[]
    for m,z in zip(MODELS,zs):
        assert tuple(z['work_grid'])==grid and np.array_equal(z['theta'],theta),(d,m,'identity or grid mismatch')
        assert z['pred'].shape==y.shape,(d,m,'shape')
        td=np.linalg.norm(z['target'].astype(float)-y,axis=1)/np.maximum(np.linalg.norm(y,axis=1),1e-8)
        assert td.max()<5e-7,(d,m,'target mismatch',td.max())
        err.append(float(td.max()))
    # Never derive alignment/scaling by optimizing on target answers.
    features=[];grams=[]
    for lo in range(0,len(y),16):
        hi=min(lo+16,len(y))
        p=np.stack([z['pred'][lo:hi].astype(np.float64) for z in zs],axis=1)
        features.append(field_features(p.reshape(hi-lo,len(MODELS),*grid)))
        e=(p-y[lo:hi,None])/np.maximum(np.linalg.norm(y[lo:hi],axis=1),1e-8)[:,None,None]
        grams.append(np.einsum('nmp,nkp->nmk',e,e,optimize=True))
    x=np.concatenate(features);g=np.concatenate(grams)
    # Hash the INPUT, not the answer, to group duplicates/version-related instances.
    groups=np.asarray([specimen_group(d)+':'+hashlib.sha256(np.ascontiguousarray(row,np.float32).tobytes()).hexdigest()
                       for row in theta])
    # ERA5 has no HF-training overlap, but all seven inputs occur in LF training.
    # Preserve it only for a clearly flagged held-out-class diagnostic; never train
    # any gate/prior on it and never include it in the strict primary comparisons.
    flagged_lf_seen=bool(d=='era5' and not any(ia['hf_train_overlap']) and overlap.all())
    keep=np.ones(len(y),bool) if flagged_lf_seen else ~overlap
    assert keep.sum()>=5,(d,'too few independent rows after base-overlap exclusion')
    atomic_npz(output/'features.npz',x=x[keep],groups=groups[keep],original_rows=np.flatnonzero(keep),
               grid=np.asarray(grid),native_lf_grid=ref['native_lf_grid'],n_hf=ref['n_hf'],
               n_levels=ref['levels'],cond_dim=np.int64(theta.shape[1]))
    atomic_npz(output/'labels.npz',gram=g[keep])
    write_json(output/'audit.json',dict(dataset=d,n_raw=len(y),n_kept=int(keep.sum()),
        base_overlap_excluded=int((~keep).sum()),class_name=CLASS_OF[d],models=MODELS,
        strict_eligible=not flagged_lf_seen,diagnostic_lf_seen_only=flagged_lf_seen,
        hf_train_overlap=int(sum(ia['hf_train_overlap'])),lf_train_overlap=int(sum(ia['lf_train_overlap'])),
        primary_excluded_rows=int(overlap.sum()),actual_dropped_rows=int((~keep).sum()),
        target_max_relative_differences=dict(zip(MODELS,err)),source_sha256=dict(zip(MODELS,map(sha,paths))),
        feature_names=FEATURE_NAMES,features_sha256=sha(output/'features.npz'),labels_sha256=sha(output/'labels.npz'),
        precision='Float32 model outputs, float64 feature/error accumulation; canonical raw-unit target from FiLM transfer.',
        corpus='Historical benchmark test predictions. Newly reserved meta-evaluation rows are never used to fit/tune gates.'))
    for z in zs:z.close()
    print('CACHED',d,'n',keep.sum(),flush=True)
    return True

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--available',action='store_true');a=ap.parse_args()
    plan=json.loads((ROOT/'plan.json').read_text())
    done=[d for d in plan['datasets'] if build_dataset(d)]
    write_json(ROOT/'results/cache_status.json',dict(done=done,remaining=sorted(set(plan['datasets'])-set(done))))
    if not a.available:assert len(done)==len(plan['datasets'])

if __name__=='__main__':main()
