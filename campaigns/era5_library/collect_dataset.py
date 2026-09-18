"""Fit/lock every mixture before opening the separate evaluation answer file."""
import argparse
import csv
import json
import time
import numpy as np
from repair_common import *
from ensemble_rules import gram,fit_auto


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',required=True,choices=DATASETS);a=ap.parse_args()
    verify_source();plan=json.loads((ROOT/'PLAN.json').read_text());info=plan['datasets'][a.dataset]
    roles=json.loads((ROOT/'ROLES.json').read_text());models=info['pool'];pred=[];metas={};theta=None
    missing=[m for m in models+['fno_hf_only_control'] if not (ROOT/'predictions'/f'{m}__{a.dataset}.npz').exists()]
    if missing:
        write_json(ROOT/'results'/f'{a.dataset}__status.json',dict(complete=False,missing_models=missing))
        raise RuntimeError(f'Missing required predictions: {missing}')
    for model in models+['fno_hf_only_control']:
        path=ROOT/'predictions'/f'{model}__{a.dataset}.npz'
        meta=json.loads((ROOT/'metadata'/f'{model}__{a.dataset}.json').read_text())
        assert meta['prediction_sha256']==sha(path) and not meta.get('smoke',False)
        with np.load(path) as z:
            if theta is None:theta=z['theta'].copy()
            else:np.testing.assert_array_equal(theta,z['theta'])
            assert list(z['work_grid'])==info['work_grid']
            p=z['pred'].astype(np.float64)
        assert np.isfinite(p).all()
        if model=='fno_hf_only_control':hf_control=p
        else:pred.append(p)
        metas[model]=meta
    pred=np.stack(pred,axis=1);records=[];partitions=[]
    # A fixed training-mean baseline is useful especially for climate fields.
    import torch
    torch.set_num_threads(4)
    import torch.nn.functional as F
    d=ROOT/'data'/rel(a.dataset);hf=info['hf_level']
    with np.load(d/f'train_l{hf}.npz') as z:mean=z['y'].mean(0,dtype=np.float64).astype(np.float32)
    native=info['levels'][str(hf)]['grid'];t=torch.from_numpy(mean).reshape(1,1,*native)
    if native!=info['work_grid']:t=F.interpolate(t,size=info['work_grid'],mode='bilinear',align_corners=False)
    training_mean=t.numpy().reshape(-1).astype(np.float64)
    for seed in SEEDS:
        role=roles[f'{a.dataset}__s{seed}'];dest=ROOT/'results'/a.dataset/f's{seed}'
        answers=ROOT/'answers'/a.dataset/f's{seed}'
        assert sha(answers/'calibration.npz')==role['calibration_sha256']
        with np.load(answers/'calibration.npz') as z:
            cal=z['target'].astype(np.float64);pool=z['query_rows'].copy()
            np.testing.assert_array_equal(theta[pool],z['theta'])
        assert not set(pool)&set(role['evaluation'])
        lookup={int(row):i for i,row in enumerate(pool)}
        locked={};selection={}
        for b,rows in role['budgets'].items():
            idx=np.asarray([lookup[r] for r in rows])
            weights,chosen=fit_auto(gram(pred[rows],cal[idx]))
            weights['allpairs']=np.eye(len(models))[models.index('mf_fno_allpairs')]
            for name,w in weights.items():
                assert np.isfinite(w).all() and w.min()>=0 and abs(w.sum()-1)<1e-10
                locked[f'b{b}__{name}']=w
            selection[b]=chosen
        save_npz(dest/'locked_weights.npz',**locked)
        proof=dict(dataset=a.dataset,seed=seed,models=models,roles=role,selection=selection,
            weights_sha256=sha(dest/'locked_weights.npz'),source_manifest_sha256=sha(ROOT/'SOURCE.json'),
            final_answers_loaded=False,prediction_sha256={m:x['prediction_sha256'] for m,x in metas.items()})
        write_json(dest/'fit.json',proof)
        # The first access to this partition's final targets occurs below this point.
        assert sha(answers/'evaluation.npz')==role['evaluation_sha256']
        assert sha(dest/'locked_weights.npz')==proof['weights_sha256']
        with np.load(answers/'evaluation.npz') as z:
            target=z['target'].astype(np.float64);ev=z['query_rows'].copy()
            np.testing.assert_array_equal(theta[ev],z['theta'])
        assert ev.tolist()==role['evaluation'];per_case={}
        predictions={f'expert:{m}':pred[ev,j] for j,m in enumerate(models)}
        predictions.update(hf_only_control=hf_control[ev],training_mean_control=np.broadcast_to(training_mean,target.shape))
        predictions.update({k:np.einsum('m,nmp->np',w,pred[ev]) for k,w in locked.items()})
        denom=np.maximum(np.linalg.norm(target,axis=1),1e-8)
        for name,p in predictions.items():
            errors=p-target;relative=np.linalg.norm(errors,axis=1)/denom
            assert np.isfinite(relative).all();per_case[name]=relative
            records.append(dict(dataset=a.dataset,seed=seed,method=name,n_evaluation=len(ev),
                rel_l2=float(relative.mean()),rmse_raw_units=float(np.sqrt(np.mean(errors**2))),
                n_base_hf_train=info['n_base_hf_train']))
        save_npz(dest/'per_case_errors.npz',query_rows=ev,**per_case)
        write_json(dest/'evaluation.json',dict(passed=True,n_evaluation=len(ev),
            fit_sha256=sha(dest/'fit.json'),per_case_errors_sha256=sha(dest/'per_case_errors.npz'),
            weights_locked_before_evaluation=True))
        partitions.append(dict(seed=seed,selection=selection))
    with (ROOT/'results'/f'{a.dataset}.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    means={m:float(np.mean([r['rel_l2'] for r in records if r['method']==m])) for m in sorted({r['method'] for r in records})}
    write_json(ROOT/'results'/f'{a.dataset}__summary.json',dict(complete=True,means=means,partitions=partitions,
        models=models,metadata=metas,base_seed=42,n_base_hf_train=info['n_base_hf_train'],
        interpretation='Historical held-out input cases, one base seed; repeated calibration partitions are not independent base seeds.'))
    lines=[f'# Nine expert ensemble: {a.dataset}','',f"{len(models)} ensemble experts; {info['n_base_hf_train']} fine base-training cases. Separate fine-only FNO and training-mean controls.",'',
        '| Method | Mean relative L2 error |','|---|---:|']
    for name,value in means.items():lines.append(f'| {name} | {value*100:.6g}% |')
    lines+=['','`auto` chooses single-expert selection, inverse-MSE weighting, or a full convex mixture using leave-one-out calibration error only. Every method is reported, including losses. Calibration labels count beyond base training labels.',
        'The final targets were opened only after all budget weights were saved for that partition. Training workers received zero-valued placeholder test fields. Repeated partitions reuse the same base models.',
        'ERA5 uses 10 reserved calibration inputs and 7 existing evaluation inputs; these are not fresh years. All nine experts are included. The two correctors use predicted LF fields at HF inputs, without paired observed LF targets. Physical units of secondary RMSE are the units stored in the source archive.']
    (ROOT/'results'/f'{a.dataset}__FINDINGS.md').write_text('\n'.join(lines)+'\n')
    print('COMPLETE',a.dataset,means,flush=True)

if __name__=='__main__':main()
