"""Audit saved correctors and build identical-corpus seven/nine-expert caches."""
import argparse,json,time
from pathlib import Path
import numpy as np
from config import ROOT,MODELS,sha,atomic_npz,write_json
from local_features import local_features,LOCAL_NAMES
from features import field_features,FEATURE_NAMES

def rowkeys(x):return [np.ascontiguousarray(r,np.float32).tobytes() for r in x]

def build(dataset):
    plan=json.loads((ROOT/'PLAN.json').read_text());original=ROOT.parent/plan['remote_original_name']
    if all((ROOT/'cache'/p/dataset/'audit.json').exists() for p in plan['pools']):return
    start=time.time();old=original/'cache'/dataset
    audit=json.loads((old/'audit.json').read_text())
    assert audit['strict_eligible'] and not audit['hf_train_overlap'] and not audit['lf_train_overlap']
    with np.load(old/'features.npz') as z:
        rows=z['original_rows'].copy();grid=tuple(z['grid']);groups=z['groups'].copy();old_x=z['x'].copy()
    fields=[];theta=None;hashes={};target=None
    for model in MODELS:
        path=original/'predictions'/f'{model}__{dataset}.npz'
        hashes[model]=sha(path);assert hashes[model]==audit['source_sha256'][model]
        with np.load(path) as z:
            if theta is None:theta=z['theta'].copy();target=z['target'][rows].astype(np.float64)
            else:assert np.array_equal(theta,z['theta'])
            fields.append(z['pred'][rows].reshape(len(rows),*grid))
    task=plan['corrector_sources'][dataset]
    with np.load(task['test_file']) as z:uq_theta=z['x'].astype(np.float32);uq_target=z['y'].astype(np.float64)
    with np.load(task['coarse_test_file']) as z:assert np.array_equal(z['x'].astype(np.float32),uq_theta)
    uq_keys=rowkeys(uq_theta);assert len(set(uq_keys))==len(uq_keys), 'Ambiguous corrector input identities'
    lookup={k:i for i,k in enumerate(uq_keys)}
    mapping=np.asarray([lookup[k] for k in rowkeys(theta[rows])])
    td=np.linalg.norm(target-uq_target[mapping],axis=1)/np.maximum(np.linalg.norm(target,axis=1),1e-8)
    assert td.max()<5e-7,(dataset,'Target mismatch')
    train_keys=set();train_hashes={}
    for path in task['training_files']:
        with np.load(path) as z:train_keys.update(rowkeys(z['x']))
        train_hashes[path]=sha(path)
    assert not any(k in train_keys for k in rowkeys(theta[rows])), 'Corrector training input overlap'
    for expert,source in task['experts'].items():
        metadata=json.loads(Path(source['json']).read_text())
        assert metadata['backbone']==source['backbone'] and metadata['input']=='pred'
        assert metadata['seed']==42 and metadata['K']==6
        assert metadata['oof_members_train']==metadata['oof_members_test']==4
        with np.load(source['npz']) as z:prediction=z['pred_test'].copy()
        assert prediction.dtype==np.float32 and prediction.shape==(len(uq_theta),*grid)
        assert np.isfinite(prediction).all()
        # Check archived row order and raw units; these errors never enter features.
        rel=np.linalg.norm(prediction.reshape(len(uq_theta),-1).astype(float)-uq_target,axis=1)/np.maximum(np.linalg.norm(uq_target,axis=1),1e-8)
        np.testing.assert_allclose(rel,metadata['per_sample']['test'],rtol=1e-4,atol=1e-7)
        fields.append(prediction[mapping]);hashes[expert]=sha(source['npz'])
    for pool,models in plan['pools'].items():
        assert models==plan['pools']['nine'][:len(models)]
        dest=ROOT/'cache'/pool/dataset;xx=[];local=[];grams=[];m=len(models)
        for lo in range(0,len(rows),8):
            hi=min(lo+8,len(rows));p=np.stack([q[lo:hi] for q in fields[:m]],axis=1).astype(np.float64)
            xx.append(field_features(p));local.append(local_features(p))
            errors=(p.reshape(hi-lo,m,-1)-target[lo:hi,None])/np.maximum(np.linalg.norm(target[lo:hi],axis=1),1e-8)[:,None,None]
            grams.append(np.einsum('nmp,nkp->nmk',errors,errors,optimize=True))
        x=np.concatenate(xx);g=np.concatenate(grams)
        if pool=='seven':
            np.testing.assert_allclose(x,old_x,rtol=0,atol=1e-12)
            with np.load(old/'labels.npz') as z:np.testing.assert_allclose(g,z['gram'],rtol=1e-12,atol=1e-14)
        atomic_npz(dest/'features.npz',x=x,local=np.concatenate(local),theta=theta,original_rows=rows,groups=groups)
        atomic_npz(dest/'labels.npz',gram=g)
        record=dict(dataset=dataset,pool=pool,models=models,n=len(rows),strict_eligible=True,
                    source_prediction_sha256=hashes,training_file_sha256=train_hashes,
                    hf_target_file_sha256=sha(task['test_file']),corrector_row_mapping=mapping.tolist(),
                    corrector_training_input_overlap=0,target_max_relative_difference=float(td.max()),
                    feature_names=FEATURE_NAMES,local_feature_names=LOCAL_NAMES,raw_input_dimensions=theta.shape[1],
                    features_sha256=sha(dest/'features.npz'),labels_sha256=sha(dest/'labels.npz'),
                    feature_functions_use_truth=False,old_seven_features_and_gram_reproduced=(pool=='seven'),
                    corrector_precision='Saved float32 outputs; original TF32 flags were not recorded. No new corrector inference or training.',
                    seconds=time.time()-start)
        write_json(dest/'audit.json',record)
    print('CACHED BOTH POOLS',dataset,'n',len(rows),'exact inputs and targets matched',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--dataset');a=ap.parse_args()
    plan=json.loads((ROOT/'PLAN.json').read_text())
    for dataset in ([a.dataset] if a.dataset else plan['datasets']):build(dataset)
