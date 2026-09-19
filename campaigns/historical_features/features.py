"""Prediction-only descriptors. This module has no access to targets or errors."""
import numpy as np
from scipy.fft import dctn

FEATURE_NAMES = ['mean_over_consensus_rms','log_rms_ratio','log_std_ratio','skew',
    'log_peak_ratio','log_gradient_ratio','broad_energy','middle_energy','fine_energy',
    'log_disagreement','signed_disagreement','broad_disagreement','middle_disagreement',
    'fine_disagreement','agreement_cosine','nearest_peer_disagreement','mean_peer_disagreement',
    'context_log_rms','context_log_gradient','context_mean_over_rms']

def field_features(predictions):
    """(N,M,H,W) -> (N,M,F), dimensionless except explicitly named log RMS.

    DCT-II is an analysis convention, not a claim about physical boundary conditions.
    Bands use fraction of the OUTPUT grid's mode range; no hard Nyquist filtering.
    """
    p=np.asarray(predictions,np.float64)
    assert p.ndim==4 and p.shape[1]>=2 and np.isfinite(p).all()
    n,m,h,w=p.shape
    center=np.median(p,axis=1)
    eps=np.maximum(np.sqrt(np.mean(center**2,axis=(-2,-1))),1e-20)
    rms=np.maximum(np.sqrt(np.mean(p*p,axis=(-2,-1))),eps[:,None]*1e-12)
    mu=p.mean(axis=(-2,-1)); std=np.sqrt(np.mean((p-mu[:,:,None,None])**2,axis=(-2,-1)))
    skew=np.mean((p-mu[:,:,None,None])**3,axis=(-2,-1))/np.maximum(std,eps[:,None]*1e-8)**3
    grad=np.sqrt(np.mean(np.diff(p,axis=-2)**2,axis=(-2,-1))*h*h+
                 np.mean(np.diff(p,axis=-1)**2,axis=(-2,-1))*w*w)
    cg=np.sqrt(np.mean(np.diff(center,axis=-2)**2,axis=(-2,-1))*h*h+
               np.mean(np.diff(center,axis=-1)**2,axis=(-2,-1))*w*w)/eps
    diff=p-center[:,None]
    dis=np.sqrt(np.mean(diff**2,axis=(-2,-1)))/eps[:,None]
    spec=dctn(p,axes=(-2,-1),norm='ortho',workers=1)
    ds=dctn(diff,axes=(-2,-1),norm='ortho',workers=1)
    q=np.maximum(np.arange(h)[:,None]/h,np.arange(w)[None,:]/w)
    masks=[q<=.125,(q>.125)&(q<=.5),q>.5]
    energy=[np.sum(spec[:,:,mask]**2,axis=-1)/(h*w*rms*rms) for mask in masks]
    de=[np.sqrt(np.sum(ds[:,:,mask]**2,axis=-1)/(h*w))/eps[:,None] for mask in masks]
    cosine=np.mean(p*center[:,None],axis=(-2,-1))/(rms*eps[:,None])
    distances=np.empty((n,m,m))
    for a in range(m):
        distances[:,a]=np.sqrt(np.mean((p[:,a,None]-p)**2,axis=(-2,-1)))/eps[:,None]
    distances[:,np.arange(m),np.arange(m)]=np.nan
    broad=lambda z:np.broadcast_to(z[:,None],(n,m))
    vals=[mu/eps[:,None],np.log(rms/eps[:,None]),np.log(np.maximum(std/rms,1e-12)),
          np.clip(skew,-20,20),np.log1p(np.max(np.abs(p),axis=(-2,-1))/rms),
          np.log1p(grad/rms),*energy,np.log1p(dis),diff.mean(axis=(-2,-1))/eps[:,None],
          *[np.log1p(a) for a in de],cosine,np.log1p(np.nanmin(distances,axis=-1)),
          np.log1p(np.nanmean(distances,axis=-1)),broad(np.log(eps)),broad(np.log1p(cg)),
          broad(center.mean(axis=(-2,-1))/eps)]
    x=np.stack(vals,axis=-1)
    assert x.shape==(n,m,len(FEATURE_NAMES)) and np.isfinite(x).all()
    return x

