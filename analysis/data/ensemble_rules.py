"""Fixed mixtures and calibration-only automatic selection among simple rules."""
import numpy as np
from scipy.optimize import minimize

def gram(pred,target):
    e=(pred-target[:,None])/np.maximum(np.linalg.norm(target,axis=1),1e-8)[:,None,None]
    return np.einsum('nmp,nkp->nmk',e,e,optimize=True)

def fit_full(g):
    g=np.asarray(g,np.float64).mean(0);m=len(g);g=(g+g.T)/2
    g/=max(float(np.trace(g)/m),1e-30)
    starts=[np.full(m,1/m),np.eye(m)[np.argmin(np.diag(g))]];candidates=starts.copy()
    for w0 in starts:
        fit=minimize(lambda w:float(w@g@w),w0,jac=lambda w:2*g@w,bounds=[(0.,1.)]*m,
            constraints=[dict(type='eq',fun=lambda w:w.sum()-1,jac=lambda w:np.ones_like(w))],
            method='SLSQP',options=dict(ftol=1e-12,maxiter=300))
        if np.isfinite(fit.x).all() and abs(fit.x.sum()-1)<1e-6:
            w=np.maximum(fit.x,0);w/=w.sum();candidates.append(w)
    return min(candidates,key=lambda w:float(w@g@w)).copy()

def rules(g):
    diag=np.maximum(np.diagonal(g,axis1=1,axis2=2),0);m=g.shape[1]
    inverse=1/np.maximum(diag.mean(0),1e-30);inverse/=inverse.sum()
    return dict(selected_single=np.eye(m)[np.argmin(np.sqrt(diag).mean(0))],
                inverse_mse=inverse,full=fit_full(g),uniform=np.full(m,1/m))

def fit_auto(g):
    assert len(g)>=2
    names=['selected_single','inverse_mse','full'];scores={k:[] for k in names}
    for held in range(len(g)):
        fitted=rules(g[np.arange(len(g))!=held])
        for name in names:
            w=fitted[name];scores[name].append(float(np.sqrt(max(w@g[held]@w,0))))
    means={k:float(np.mean(v)) for k,v in scores.items()}
    chosen=min(names,key=lambda k:means[k]);fitted=rules(g);fitted['auto']=fitted[chosen].copy()
    return fitted,dict(chosen=chosen,leave_one_out_scores=means)
