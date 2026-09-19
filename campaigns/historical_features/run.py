"""Ablation of extra information with an unchanged whole-field gating rule."""
import argparse,json,time
import numpy as np
from config import *
from mixture import *
from local_features import parameter_blocks,LOCAL_NAMES
from features import FEATURE_NAMES
from protocols import split_indices

def plain(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {str(k):plain(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [plain(v) for v in x]
    return x

def load_features(plan,pool):
    old=ROOT.parent/plan['remote_original_name']
    part=[];local=[];datasets=[];classes=[];groups=[];rows=[];indices=[];thetas={};audits={}
    for dataset in plan['datasets']:
        base=ROOT/'cache'/pool/dataset
        audit=json.loads((base/'audit.json').read_text())
        assert audit['strict_eligible']
        assert sha(base/'features.npz')==audit['features_sha256']
        with np.load(base/'features.npz') as z:
            n=len(z['x']);part.append(z['x']);local.append(z['local']);thetas[dataset]=z['theta']
            datasets.extend([dataset]*n);classes.extend([CLASS_OF[dataset]]*n)
            groups.extend(z['groups']);rows.extend(z['original_rows']);indices.extend(range(n))
        audits[dataset]=dict(labels_sha256=audit['labels_sha256'],features_sha256=audit['features_sha256'])
    return dict(global_x=np.concatenate(part),local_x=np.concatenate(local),d=np.asarray(datasets),
                c=np.asarray(classes),groups=np.asarray(groups),rows=np.asarray(rows),local_indices=np.asarray(indices),
                theta=thetas,audits=audits)

def labels(corpus,idx,plan,pool):
    # Only explicitly requested rows are returned to fitting or scoring.
    m=len(plan['pools'][pool]);out=np.empty((len(idx),m,m),np.float64)
    for d in np.unique(corpus['d'][idx]):
        p=ROOT/'cache'/pool/d/'labels.npz'
        assert sha(p)==corpus['audits'][d]['labels_sha256']
        mask=corpus['d'][idx]==d
        with np.load(p) as z:out[mask]=z['gram'][corpus['local_indices'][idx[mask]]]
    return out

def selected_single(g,d,c,all_d):
    m=g.shape[1];by_dataset={}
    for dd in np.unique(d):
        ids=np.flatnonzero(d==dd)
        by_dataset[dd]=min(range(m),key=lambda j:balanced_score(np.broadcast_to(np.eye(m)[j],(len(ids),m)),g[ids],d[ids],c[ids]))
    return np.eye(m)[[by_dataset[dd] for dd in all_d]]

def run(seed,pool):
    start=time.time();plan=json.loads((ROOT/'PLAN.json').read_text())
    models_in_pool=plan['pools'][pool];m=len(models_in_pool)
    dest=ROOT/'runs'/f'{pool}__s{seed}'
    assert not (dest/'result.json').exists(), 'Completed evaluation is immutable'
    dest.mkdir(parents=True,exist_ok=True)
    corpus=load_features(plan,pool);d=corpus['d'];c=corpus['c']
    fit,tune,ev=split_indices(corpus['groups'],c,'cases',seed)
    split=dict(seed=seed,protocol='cases',fit=[],tune=[],evaluation=[])
    for name,ids in [('fit',fit),('tune',tune),('evaluation',ev)]:
        split[name]=[dict(dataset=d[i],row=int(corpus['rows'][i]),group=corpus['groups'][i]) for i in ids]
    reference=ROOT.parent/plan['remote_matched_name']/'runs'/f'cases__s{seed}'
    previous=json.loads((reference/'split.json').read_text())
    for name in ['fit','tune','evaluation']:
        assert split[name]==[r for r in previous[name] if r['dataset'] in plan['datasets']],name
    write_json(dest/'split.json',split)
    # Dataset-specific parameter scaling is fitted before any evaluation scoring.
    inputs,input_names,input_scaling=parameter_blocks(corpus['theta'],plan['datasets'],corpus['rows'],d,fit)
    input_x=np.broadcast_to(inputs[:,None,:],(len(d),m,inputs.shape[1]))
    gf=labels(corpus,fit,plan,pool);gt=labels(corpus,tune,plan,pool)
    priors=fit_priors(gf,d[fit],c[fit]);p=prior_weights(priors,d,c)
    full_priors=fit_priors(np.concatenate([gf,gt]),d[np.r_[fit,tune]],c[np.r_[fit,tune]])
    weights=dict(dataset_fixed=p[ev],calibration_fixed=prior_weights(full_priors,d[ev],c[ev]),
                 best_single=selected_single(gf,d[fit],c[fit],d[ev]),
                 best_single_full=selected_single(np.concatenate([gf,gt]),d[np.r_[fit,tune]],c[np.r_[fit,tune]],d[ev]))
    models={};feature_names={};centers={}
    variants=[('current',False,False),('input',True,False),('local',False,True),('input_local',True,True)]
    for name,use_input,use_local in variants:
        parts=[corpus['global_x']];names=list(FEATURE_NAMES)
        if use_local:parts.append(corpus['local_x']);names+=LOCAL_NAMES
        if use_input:parts.append(input_x);names+=input_names
        x=np.concatenate(parts,axis=-1)
        tail=inputs.shape[1] if use_input else 0
        candidates=[train_gate(x[fit],gf,p[fit],d[fit],c[fit],x[tune],gt,p[tune],d[tune],c[tune],
                               kind='specific',penalty=penalty,steps=plan['steps'],passthrough_tail=tail)
                    for penalty in plan['penalties']]
        chosen=min(candidates,key=lambda q:q['tune_score'])
        model={k:v for k,v in chosen.items() if k!='history'}
        model['candidate_histories']=[dict(penalty=q['penalty'],active=q['active'],best_step=q['best_step'],history=q['history']) for q in candidates]
        model['features_per_model']=x.shape[-1];model['coefficient_count']=int(chosen['coef'].size)
        models[name]=model;feature_names[name]=names
        method='gate_'+name
        def predict(a):
            return gate_predict(a,p[ev],chosen['mu'],chosen['sd'],chosen['coef'],chosen['kind']) if chosen['active'] else p[ev].copy()
        weights[method]=predict(x[ev])
        mean={dd:x[fit][d[fit]==dd].mean(axis=0) for dd in np.unique(d)}
        centers[name]=mean
        constant=np.asarray([mean[dd] for dd in d[ev]])
        weights['constant_'+name]=predict(constant)
        print('FIT',seed,name,'active',chosen['active'],'step',chosen['best_step'],'penalty',chosen['penalty'],flush=True)
    for key,w in weights.items():
        assert w.shape==(len(ev),m) and np.isfinite(w).all() and w.min()>=-1e-12 and np.allclose(w.sum(1),1)
    # All predictions are fixed before comparing to old locked weights or any evaluation answers.
    atomic_npz(dest/'locked_weights.npz',**weights,dataset=d[ev],row=corpus['rows'][ev])
    locked_sha=sha(dest/'locked_weights.npz')
    if pool=='seven':
        with np.load(reference/'locked_weights.npz') as old:
            mask=np.isin(old['dataset'],plan['datasets'])
            for name in ['dataset_fixed','calibration_fixed','best_single']:
                np.testing.assert_allclose(weights[name],old[name][mask],rtol=0,atol=1e-7,
                                           err_msg='Reference static control mismatch: '+name)
    fit_record=dict(seed=seed,pool=pool,models=models_in_pool,n_fit=len(fit),n_tune=len(tune),n_eval=len(ev),
                    gates=plain(models),feature_names=feature_names,input_scaling=input_scaling,
                    priors=plain(priors),full_calibration_priors=plain(full_priors),constant_centers=plain(centers),
                    fit_and_tune_receive_only_assigned_labels=True,features_use_truth=False,
                    weights_locked_before_evaluation_scoring=True,original_static_controls_match=(pool=='seven'),
                    locked_weights_sha256=locked_sha,split_sha256=sha(dest/'split.json'),
                    source_sha256={p.name:sha(p) for p in ROOT.glob('*.py')},plan_sha256=sha(ROOT/'PLAN.json'),
                    input_artifact_audits=corpus['audits'])
    write_json(dest/'fit.json',fit_record)
    ge=labels(corpus,ev,plan,pool)
    per={name:np.sqrt(risk(w,ge)) for name,w in weights.items()}
    for j,expert in enumerate(models_in_pool):per['expert:'+expert]=np.sqrt(np.maximum(ge[:,j,j],0.))
    atomic_npz(dest/'per_case_errors.npz',**per,dataset=d[ev],row=corpus['rows'][ev])
    summaries=[]
    for dd in np.unique(d[ev]):
        mask=d[ev]==dd
        summaries.append(dict(dataset=dd,class_name=CLASS_OF[dd],n=int(mask.sum()),
            errors={k:float(v[mask].mean()) for k,v in per.items()},
            mean_weights={k:w[mask].mean(0).tolist() for k,w in weights.items()}))
    assert sha(dest/'locked_weights.npz')==locked_sha
    write_json(dest/'result.json',dict(seed=seed,pool=pool,seconds=time.time()-start,datasets=summaries,
        n_fit=len(fit),n_tune=len(tune),n_eval=len(ev),fit_sha256=sha(dest/'fit.json'),
        locked_weights_sha256=locked_sha,
        gates={k:{kk:plain(vv) for kk,vv in v.items() if kk in ['active','best_step','penalty','tune_score','features_per_model','coefficient_count']} for k,v in models.items()}))
    print('COMPLETE',seed,round(time.time()-start,1),'seconds',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--seed',required=True,type=int);ap.add_argument('--pool',choices=['seven','nine'],required=True)
    a=ap.parse_args();run(a.seed,a.pool)
