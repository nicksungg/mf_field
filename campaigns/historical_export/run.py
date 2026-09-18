"""Fit rules/gates on fit/tune cases, lock evaluation weights, then score answers."""
import argparse
import json
import pickle
import time
import numpy as np
from config import *
from features import FEATURE_NAMES
from protocols import split_indices
from mixture import *
from rules import rule_inputs,fit_rules,predict_rules

def jsonable(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {str(k):jsonable(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [jsonable(v) for v in x]
    return x

def load_corpus(only=None,include_flagged=False):
    plan=json.loads((ROOT/'plan.json').read_text());parts=[];ds=[];cl=[];groups=[];rows=[];meta=[];local=[]
    audit={}
    for d in plan['datasets']:
        if only and d!=only:continue
        path=ROOT/'cache'/d
        q=json.loads((path/'audit.json').read_text());audit[d]=q
        if not q.get('strict_eligible',True) and not include_flagged:continue
        assert sha(path/'features.npz')==q['features_sha256']
        z=np.load(path/'features.npz');x=z['x'];n=len(x)
        parts.append(x);ds.extend([d]*n);cl.extend([CLASS_OF[d]]*n);groups.extend(z['groups'])
        rows.extend(z['original_rows']);local.extend(range(n))
        mm=[*np.log(z['grid']),*np.log(z['native_lf_grid']),np.log(int(z['n_hf'])),int(z['cond_dim'])]
        meta.extend([mm]*n)
    return dict(x=np.concatenate(parts),d=np.asarray(ds),c=np.asarray(cl),groups=np.asarray(groups),
                rows=np.asarray(rows),local=np.asarray(local),metadata=np.asarray(meta),audit=audit)

def load_labels(corpus,idx):
    """The caller explicitly requests fitting, tuning, or evaluation identities."""
    idx=np.asarray(idx);result=np.empty((len(idx),len(MODELS),len(MODELS)),np.float64)
    for d in np.unique(corpus['d'][idx]):
        mask=corpus['d'][idx]==d;p=ROOT/'cache'/d/'labels.npz'
        assert sha(p)==corpus['audit'][d]['labels_sha256']
        with np.load(p) as z:result[mask]=z['gram'][corpus['local'][idx[mask]]]
    assert np.isfinite(result).all()
    return result

def fit_models(x,g,d,c,meta,xt,gt,dt,ct,metat,steps=400,prior_level='dataset'):
    prior=fit_priors(g,d,c)
    pp=prior_weights(prior,d,c,prior_level);pt=prior_weights(prior,dt,ct,prior_level)
    if prior_level=='global':
        np.testing.assert_allclose(pp,np.broadcast_to(prior['global_weights'],pp.shape))
        np.testing.assert_allclose(pt,np.broadcast_to(prior['global_weights'],pt.shape))
    fitted=dict(priors=prior,gates={},rules=None,prior_level=prior_level)
    for kind in ['shared','specific']:
        candidates=[train_gate(x,g,pp,d,c,xt,gt,pt,dt,ct,kind,penalty,steps)
                    for penalty in [0.,.01,.1]]
        best=min(candidates,key=lambda t:t['tune_score'])
        fitted['gates'][kind]=best
        print('FIT gate',kind,'step',best['best_step'],'penalty',best['penalty'],flush=True)
    tx,names=rule_inputs(x,c,meta,list(CLASSES),FEATURE_NAMES,MODELS)
    txt,_=rule_inputs(xt,ct,metat,list(CLASSES),FEATURE_NAMES,MODELS)
    fitted['rules']=fit_rules(tx,g,pp,d,c,txt,gt,pt,dt,ct,names)
    nmeta=len(CLASSES)+6
    fitted['metadata_rules']=fit_rules(tx[:,:nmeta],g,pp,d,c,txt[:,:nmeta],gt,pt,dt,ct,names[:nmeta])
    fitted['field_centers']=dict(global_mean=x.mean(axis=0),
        dataset={dd:x[np.asarray(d)==dd].mean(axis=0) for dd in np.unique(d)},
        class_mean={cc:x[np.asarray(c)==cc].mean(axis=0) for cc in np.unique(c)})
    # Choose single experts only using FIT labels, with hierarchical fallback.
    single={}
    def best_single(mask):
        ids=np.flatnonzero(mask)
        return min(range(len(MODELS)),key=lambda j:balanced_score(np.broadcast_to(np.eye(len(MODELS))[j],(len(ids),len(MODELS))),
            g[ids],np.asarray(d)[ids],np.asarray(c)[ids]))
    single['global']=best_single(np.ones(len(g),bool))
    single['class']={cc:best_single(np.asarray(c)==cc) for cc in np.unique(c)}
    single['dataset']={dd:best_single(np.asarray(d)==dd) for dd in np.unique(d)}
    fitted['single']=single
    # Strong static control: spend the full fit+tune label budget fitting its weights.
    fitted['calibration_priors']=fit_priors(np.concatenate([g,gt]),np.r_[d,dt],np.r_[c,ct])
    return fitted

def predict_all(fitted,x,d,c,metadata):
    n=len(x);m=len(MODELS);pr=fitted['priors']
    prior=prior_weights(pr,d,c,fitted['prior_level'])
    out=dict(equal=np.full((n,m),1/m),global_fixed=prior_weights(pr,d,c,'global'),
             class_fixed=prior_weights(pr,d,c,'class'),dataset_fixed=prior_weights(pr,d,c,'dataset'))
    out['calibration_fixed']=prior_weights(fitted['calibration_priors'],d,c)
    choices=[fitted['single']['dataset'].get(dd,fitted['single']['class'].get(cc,fitted['single']['global'])) for dd,cc in zip(d,c)]
    out['best_single']=np.eye(m)[choices]
    for name,fit in fitted['gates'].items():
        out['field_gate_'+name]=(gate_predict(x,prior,fit['mu'],fit['sd'],fit['coef'],fit['kind'])
                                 if fit['active'] else prior.copy())
        centers=fitted['field_centers']
        constant=np.asarray([centers['dataset'].get(dd,centers['class_mean'].get(cc,centers['global_mean'])) for dd,cc in zip(d,c)])
        out['constant_features_'+name]=(gate_predict(constant,prior,fit['mu'],fit['sd'],fit['coef'],fit['kind'])
                                        if fit['active'] else prior.copy())
    rx,_=rule_inputs(x,c,metadata,list(CLASSES),FEATURE_NAMES,MODELS)
    out['field_rules']=predict_rules(fitted['rules'],rx,prior)
    out['metadata_rules']=predict_rules(fitted['metadata_rules'],rx[:,:len(CLASSES)+6],prior)
    for name,w in out.items():
        assert w.shape==(n,m) and np.isfinite(w).all() and w.min()>=-1e-10 and np.allclose(w.sum(1),1),name
    return out

def run(protocol,seed,held_class=None,only=None,steps=400):
    suffix=('__'+held_class) if held_class else ''
    if only:suffix+='__smoke_'+only
    rid=f'{protocol}__s{seed}'+suffix;out=ROOT/'runs'/rid
    if (out/'result.json').exists():print('SKIP',rid);return
    out.mkdir(parents=True,exist_ok=True);start=time.time()
    diagnostic=protocol=='class' and held_class=='climate'
    corpus=load_corpus(only,include_flagged=diagnostic);x=corpus['x'];d=corpus['d'];c=corpus['c'];md=corpus['metadata']
    fit,tune,test=split_indices(corpus['groups'],c,protocol,seed,held_class)
    assert all(corpus['audit'][dd].get('strict_eligible',True) for dd in np.unique(d[np.r_[fit,tune]]))
    split=dict(protocol=protocol,seed=seed,held_class=held_class,
        fit=[dict(dataset=d[i],row=int(corpus['rows'][i]),group=corpus['groups'][i]) for i in fit],
        tune=[dict(dataset=d[i],row=int(corpus['rows'][i]),group=corpus['groups'][i]) for i in tune],
        evaluation=[dict(dataset=d[i],row=int(corpus['rows'][i]),group=corpus['groups'][i]) for i in test])
    write_json(out/'split.json',split)
    # Fitting and tuning receive only their assigned rows from the shared label cache.
    # Evaluation rows are not requested for scoring until weights are written and hashed.
    gf=load_labels(corpus,fit);gt=load_labels(corpus,tune)
    prior_level='global' if protocol=='class' else 'dataset'
    fitted=fit_models(x[fit],gf,d[fit],c[fit],md[fit],x[tune],gt,d[tune],c[tune],md[tune],steps,prior_level)
    weights=predict_all(fitted,x[test],d[test],c[test],md[test])
    atomic_npz(out/'locked_weights.npz',**weights,dataset=d[test],row=corpus['rows'][test])
    weight_sha=sha(out/'locked_weights.npz')
    with open(out/'fitted.pkl','wb') as f:pickle.dump(fitted,f)
    record=dict(id=rid,protocol=protocol,seed=seed,held_class=held_class,smoke=bool(only),diagnostic_lf_seen_only=diagnostic,
        models=MODELS,n_fit=len(fit),n_tune=len(tune),n_eval=len(test),starting_prior_level=prior_level,
        prior_classes=sorted(fitted['priors']['class_weights']),prior_datasets=sorted(fitted['priors']['dataset']),
        locked_weights_sha256=weight_sha,split_sha256=sha(out/'split.json'),
        source_sha256={p.name:sha(p) for p in ROOT.glob('*.py')},
        locked_before_evaluation_scoring=True,fit_and_tune_receive_only_assigned_labels=True,features_use_truth=False,
        gates={k:{kk:jsonable(vv) for kk,vv in v.items() if kk not in ['history']} for k,v in fitted['gates'].items()},
        priors=jsonable(fitted['priors']),calibration_priors=jsonable(fitted['calibration_priors']),
        metadata_rules={k:jsonable(v) for k,v in fitted['metadata_rules'].items() if k!='tree'},
        rules={k:jsonable(v) for k,v in fitted['rules'].items() if k!='tree'},
        corpus_note='Exploratory meta-learning from historical benchmark test rows; not fresh benchmark confirmation.')
    write_json(out/'fit.json',record)
    (out/'RULES.txt').write_text(fitted['rules']['text']+'\n\nLeaf weights:\n'+json.dumps(jsonable(fitted['rules']['leaves']),indent=2)+'\n')
    (out/'METADATA_RULES.txt').write_text(fitted['metadata_rules']['text']+'\n\nLeaf weights:\n'+json.dumps(jsonable(fitted['metadata_rules']['leaves']),indent=2)+'\n')
    # Only now expose answers for evaluation.
    ge=load_labels(corpus,test)
    per={name:np.sqrt(risk(w,ge)) for name,w in weights.items()}
    per.update({'expert:'+m:np.sqrt(np.maximum(ge[:,j,j],0)) for j,m in enumerate(MODELS)})
    per['oracle_best_single']=np.sqrt(np.maximum(np.diagonal(ge,axis1=1,axis2=2).min(1),0))
    ow=np.stack([simplex_fit(g) for g in ge]);per['oracle_case_mixture']=np.sqrt(risk(ow,ge))
    assert sha(out/'locked_weights.npz')==weight_sha
    atomic_npz(out/'per_case_errors.npz',**per,dataset=d[test],row=corpus['rows'][test])
    summaries=[]
    for dd in np.unique(d[test]):
        mask=d[test]==dd
        summaries.append(dict(dataset=dd,class_name=CLASS_OF[dd],n=int(mask.sum()),
            errors={k:float(v[mask].mean()) for k,v in per.items()},
            mean_weights={k:w[mask].mean(0).tolist() for k,w in weights.items()},
            prior_source='dataset' if dd in fitted['priors']['dataset'] else
                        ('class' if CLASS_OF[dd] in fitted['priors']['class_weights'] else 'global')))
    result=dict(id=rid,protocol=protocol,seed=seed,held_class=held_class,smoke=bool(only),models=MODELS,
        diagnostic_lf_seen_only=diagnostic,
        seconds=time.time()-start,fit_sha256=sha(out/'fit.json'),locked_weights_sha256=weight_sha,
        n_fit=len(fit),n_tune=len(tune),n_eval=len(test),datasets=summaries,
        gates={k:dict(active=v['active'],step=v['best_step'],penalty=v['penalty']) for k,v in fitted['gates'].items()},
        rules=dict(alpha=fitted['rules']['alpha'],depth=fitted['rules'].get('depth',0)))
    write_json(out/'result.json',result)
    print('COMPLETE',rid,'seconds',round(time.time()-start,1),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--protocol',choices=['cases','class'],required=True)
    ap.add_argument('--seed',type=int,default=71);ap.add_argument('--held-class');ap.add_argument('--only-dataset');
    ap.add_argument('--steps',type=int,default=400);a=ap.parse_args()
    run(a.protocol,a.seed,a.held_class,a.only_dataset,a.steps)
