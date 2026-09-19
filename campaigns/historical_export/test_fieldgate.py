import unittest
from unittest.mock import patch
import numpy as np
from features import field_features
from mixture import risk,simplex_fit,fit_priors,prior_weights,train_gate,gate_predict
from protocols import split_indices,case_roles

class FieldGateTests(unittest.TestCase):
    def test_global_prior_policy_matches_fit_tune_and_prediction(self):
        from run import fit_models,predict_all
        from mixture import balanced_score
        rng=np.random.default_rng(13);n=40;m=7
        x=rng.normal(size=(n,m,20));g=np.zeros((n,m,m))
        d=np.asarray(['first']*20+['second']*20);c=np.asarray(['elliptic']*20+['diffusion']*20)
        for i in range(n):
            errors=np.ones(m);errors[0 if i<20 else 1]=.1;g[i]=np.diag(errors**2)
        received=[]
        def fake_gate(*a):
            xx,gg,pp,dd,cc,xt,gt,pt,dt,ct,kind,penalty,steps=a
            received.append((pp.copy(),pt.copy()))
            return dict(mu=np.zeros((1,1,20)),sd=np.ones((1,1,20)),
                coef=np.zeros(20 if kind=='shared' else (m,20)),kind=kind,penalty=penalty,
                active=False,best_step=-1,tune_score=balanced_score(pt,gt,dt,ct),history=[])
        fit=np.r_[0:15,20:35];tune=np.r_[15:20,35:40];md=np.zeros((n,6))
        with patch('run.train_gate',side_effect=fake_gate):
            model=fit_models(x[fit],g[fit],d[fit],c[fit],md[fit],x[tune],g[tune],d[tune],c[tune],md[tune],
                             steps=20,prior_level='global')
        expected=model['priors']['global_weights']
        self.assertFalse(np.allclose(model['priors']['dataset']['first'],expected))
        for pp,pt in received:
            np.testing.assert_allclose(pp,np.broadcast_to(expected,pp.shape))
            np.testing.assert_allclose(pt,np.broadcast_to(expected,pt.shape))
        result=predict_all(model,x[:2],np.asarray(['first','unseen']),np.asarray(['elliptic','shocks']),md[:2])
        np.testing.assert_allclose(result['field_gate_shared'],np.broadcast_to(expected,(2,m)))

    def test_gram_matches_actual_field_mixture(self):
        rng=np.random.default_rng(4);p=rng.normal(size=(9,7,81));y=rng.normal(size=(9,81))
        e=(p-y[:,None])/np.linalg.norm(y,axis=1)[:,None,None]
        g=np.einsum('nmp,nkp->nmk',e,e);w=rng.dirichlet(np.ones(7),size=9)
        actual=np.sum((np.einsum('nm,nmp->np',w,p)-y)**2,axis=1)/np.sum(y*y,axis=1)
        np.testing.assert_allclose(risk(w,g),actual,rtol=1e-12)
        ww=simplex_fit(g)
        self.assertLessEqual(float(risk(ww,g).mean()),float(np.diagonal(g,axis1=1,axis2=2).mean(0).min())+1e-10)

    def test_features_are_per_example_and_model_order_equivariant(self):
        rng=np.random.default_rng(7);p=rng.normal(size=(5,7,16,16))
        x=field_features(p);order=[4,1,5,2,6,0,3]
        np.testing.assert_allclose(field_features(p[:,order]),x[:,order],atol=1e-12)
        np.testing.assert_allclose(field_features(p[:1]),x[:1],atol=1e-12)
        np.testing.assert_allclose(field_features(p[:1]),field_features(np.concatenate([p[:1],p[1:]*100]))[:1],atol=1e-12)

    def test_version_groups_and_entire_class_are_held_out(self):
        groups=np.asarray([f'poisson_versions:{i}' for i in range(30)]*2+[f'heat:{i}' for i in range(30)])
        classes=np.asarray(['elliptic']*60+['diffusion']*30)
        role=case_roles(groups,71);np.testing.assert_array_equal(role[:30],role[30:60])
        for mode,cc in [('cases',None),('class','diffusion')]:
            fit,tune,test=split_indices(groups,classes,mode,71,cc)
            self.assertFalse(set(groups[fit])&set(groups[test]))
            self.assertFalse(set(groups[tune])&set(groups[test]))
            if cc:self.assertFalse(np.any(classes[np.r_[fit,tune]]==cc))

    def test_gate_learns_feature_dependent_complementarity(self):
        # Alternating known field regimes: expert 0 helps one, expert 1 the other.
        n=120;r=np.arange(n)%2
        e=np.stack([np.where(r==0,.1,1.),np.where(r==0,1.,.1)],axis=1)
        g=e[:,:,None]*e[:,None,:]
        x=np.zeros((n,2,2));x[:,0,0]=r;x[:,1,0]=1-r
        d=np.asarray(['synthetic']*n);c=np.asarray(['one']*n)
        fit=np.arange(80);tune=np.arange(80,100);ev=np.arange(100,120)
        priors=fit_priors(g[fit],d[fit],c[fit]);p=prior_weights(priors,d,c)
        model=train_gate(x[fit],g[fit],p[fit],d[fit],c[fit],x[tune],g[tune],p[tune],d[tune],c[tune],steps=160)
        self.assertTrue(model['active'])
        w=gate_predict(x[ev],p[ev],model['mu'],model['sd'],model['coef'],model['kind'])
        self.assertLess(float(risk(w,g[ev]).mean()),float(risk(p[ev],g[ev]).mean())*.3)
        # Inference has no target argument: changing evaluation answers cannot change weights.
        changed=g[ev]*1000
        w2=gate_predict(x[ev],p[ev],model['mu'],model['sd'],model['coef'],model['kind'])
        np.testing.assert_array_equal(w,w2)
        self.assertGreater(float(risk(w2,changed).mean()),float(risk(w,g[ev]).mean()))

if __name__=='__main__':unittest.main()
