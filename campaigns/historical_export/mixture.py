"""Supervised convex mixtures and small field-conditioned adjustments."""
import numpy as np
from scipy.optimize import minimize
import torch

def risk(weights,gram):
    return np.maximum(np.einsum('...m,...mk,...k->...',weights,gram,weights,optimize=True),0.)

def simplex_fit(gram,importance=None):
    g=np.asarray(gram,np.float64)
    if g.ndim==3:
        g=np.average(g,axis=0,weights=importance)
    m=len(g);g=(g+g.T)/2
    scale=max(float(np.trace(g)/m),1e-30);g=g/scale
    uniform=np.full(m,1/m)
    # Include endpoints explicitly; useful for nearly perfect POD or duplicated experts.
    starts=[uniform,np.eye(m)[np.argmin(np.diag(g))]]
    candidates=starts.copy()
    for w0 in starts:
        opt=minimize(lambda w:float(w@g@w),w0,jac=lambda w:2*g@w,
            bounds=[(0.,1.)]*m,constraints=[dict(type='eq',fun=lambda w:w.sum()-1,
                jac=lambda w:np.ones_like(w))],method='SLSQP',options=dict(ftol=1e-12,maxiter=300))
        if np.isfinite(opt.x).all() and abs(opt.x.sum()-1)<1e-6:
            w=np.maximum(opt.x,0);w/=w.sum();candidates.append(w)
    return min(candidates,key=lambda w:float(w@g@w)).copy()

def sample_balance(datasets,classes):
    d=np.asarray(datasets);c=np.asarray(classes);ans=np.zeros(len(d))
    for cc in np.unique(c):
        names=np.unique(d[c==cc])
        for dd in names:
            mask=d==dd;ans[mask]=1/(len(np.unique(c))*len(names)*mask.sum())
    return ans/ans.sum()

def balanced_score(weights,gram,datasets,classes):
    """Mean log(dataset mean relative L2), giving each represented class equal weight."""
    rel=np.sqrt(risk(weights,gram));scores=[]
    for cc in np.unique(classes):
        scores.append(np.mean([np.log(max(float(rel[np.asarray(datasets)==dd].mean()),1e-12))
                               for dd in np.unique(np.asarray(datasets)[np.asarray(classes)==cc])]))
    return float(np.mean(scores))

def fit_priors(gram,datasets,classes):
    d=np.asarray(datasets);c=np.asarray(classes);g=np.asarray(gram)
    scales={dd:max(float(np.trace(g[d==dd],axis1=1,axis2=2).mean()/g.shape[1]),1e-24) for dd in np.unique(d)}
    imp=sample_balance(d,c)/np.asarray([scales[dd] for dd in d])
    result=dict(global_weights=simplex_fit(g,imp),dataset={},class_weights={},scales=scales)
    for cc in np.unique(c):
        mask=c==cc;result['class_weights'][cc]=simplex_fit(g[mask],imp[mask])
    for dd in np.unique(d):result['dataset'][dd]=simplex_fit(g[d==dd])
    return result

def prior_weights(priors,datasets,classes,level='dataset'):
    out=[]
    for d,c in zip(datasets,classes):
        w=priors['global_weights']
        if level in ('class','dataset') and c in priors['class_weights']:w=priors['class_weights'][c]
        if level=='dataset' and d in priors['dataset']:w=priors['dataset'][d]
        out.append(w)
    return np.asarray(out)

def standardizer(x):
    mu=np.mean(x,axis=(0,1),keepdims=True);sd=np.std(x,axis=(0,1),keepdims=True)
    return mu,np.maximum(sd,1e-6)

def gate_predict(x,prior,mu,sd,coef,kind='shared'):
    z=np.clip((x-mu)/sd,-8,8)
    raw=np.einsum('nmf,f->nm',z,coef) if kind=='shared' else np.einsum('nmf,mf->nm',z,coef)
    delta=4*np.tanh(raw/4)
    # Give experts with zero aggregate weight a chance on individual examples.
    logits=np.log(.95*prior+.05/prior.shape[1])+delta
    logits-=logits.max(axis=1,keepdims=True)
    w=np.exp(logits);return w/w.sum(axis=1,keepdims=True)

def train_gate(x,g,prior,d,c,xt,gt,pt,dt,ct,kind='shared',penalty=.01,steps=400):
    """Only fitting/tuning arrays enter this function. No evaluation labels are accepted."""
    torch.set_num_threads(2)
    mu,sd=standardizer(x);z=np.clip((x-mu)/sd,-8,8)
    xtn=np.clip((xt-mu)/sd,-8,8)
    dtype=torch.float64
    zt=torch.as_tensor(z,dtype=dtype);GG=torch.as_tensor(g,dtype=dtype)
    pp=torch.log(torch.as_tensor(.95*prior+.05/prior.shape[1],dtype=dtype))
    # Per-dataset normalization is computed from FIT labels only.
    scales={dd:max(float(np.trace(g[np.asarray(d)==dd],axis1=1,axis2=2).mean()/g.shape[1]),1e-24) for dd in np.unique(d)}
    importance=sample_balance(d,c)/np.asarray([scales[dd] for dd in d])
    iw=torch.as_tensor(importance,dtype=dtype);sw=torch.as_tensor(sample_balance(d,c),dtype=dtype)
    shape=(x.shape[-1],) if kind=='shared' else (x.shape[1],x.shape[2])
    coef=torch.nn.Parameter(torch.zeros(shape,dtype=dtype))
    opt=torch.optim.Adam([coef],lr=.025)
    best=coef.detach().numpy().copy();best_score=balanced_score(pt,gt,dt,ct);best_step=-1
    history=[]
    for step in range(1,steps+1):
        opt.zero_grad()
        raw=torch.einsum('nmf,f->nm',zt,coef) if kind=='shared' else torch.einsum('nmf,mf->nm',zt,coef)
        delta=4*torch.tanh(raw/4);w=torch.softmax(pp+delta,dim=1)
        loss=torch.sum(iw*torch.einsum('nm,nmk,nk->n',w,GG,w))
        loss=loss+penalty*torch.sum(sw*(delta**2).mean(dim=1))
        loss.backward();opt.step()
        if step%20==0 or step==steps:
            valcoef=coef.detach().numpy().copy()
            score=balanced_score(gate_predict(xt,pt,mu,sd,valcoef,kind),gt,dt,ct)
            history.append(dict(step=step,score=score))
            if score<best_score-1e-12:best_score=score;best=valcoef;best_step=step
    return dict(mu=mu,sd=sd,coef=best,kind=kind,penalty=penalty,tune_score=best_score,best_step=best_step,
                active=best_step>=0,history=history)
