"""Splits depend exclusively on input identities and the existing PDE taxonomy."""
import hashlib
import numpy as np

def case_roles(groups,seed):
    groups=np.asarray(groups);mapping={}
    families=np.asarray([g.split(':')[0] for g in groups])
    for family in np.unique(families):
        unique=sorted(set(groups[families==family]),
                      key=lambda g:hashlib.sha256(f'{seed}:{g}'.encode()).hexdigest())
        n=len(unique);assert n>=5
        nf=max(2,int(.6*n));nv=max(1,int(.2*n))
        for i,g in enumerate(unique):mapping[g]=0 if i<nf else (1 if i<nf+nv else 2)
    return np.asarray([mapping[g] for g in groups])

def split_indices(groups,classes,protocol,seed,held_class=None):
    role=case_roles(groups,seed);classes=np.asarray(classes)
    if protocol=='cases':
        fit=np.flatnonzero(role==0);tune=np.flatnonzero(role==1);test=np.flatnonzero(role==2)
    elif protocol=='class':
        assert held_class in set(classes)
        test=np.flatnonzero(classes==held_class)
        fit=np.flatnonzero((classes!=held_class)&(role!=1))
        tune=np.flatnonzero((classes!=held_class)&(role==1))
        assert held_class not in set(classes[fit])|set(classes[tune])
    else:raise ValueError(protocol)
    assert len(fit) and len(tune) and len(test)
    sets=[set(np.asarray(groups)[i]) for i in (fit,tune,test)]
    assert not (sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2])
    return fit,tune,test

