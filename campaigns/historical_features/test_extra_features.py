import unittest
import numpy as np
from local_features import local_features,parameter_blocks
from features import field_features
from mixture import train_gate,gate_predict,risk

class AdditionalFeatureTests(unittest.TestCase):
    def test_local_features_locate_errors_hidden_by_global_summaries(self):
        p=np.ones((2,3,20,20));p[0,0,2:7,2:7]+=1.;p[1,0,-7:-2,-7:-2]+=1.
        # A reflection preserves whole-field magnitude, gradient and spectral-energy summaries.
        global_x=field_features(p)
        np.testing.assert_allclose(global_x[0],global_x[1],atol=1e-12)
        extra=local_features(p)
        self.assertGreater(extra[0,0,2],extra[1,0,2])
        self.assertLess(extra[0,0,14],extra[1,0,14])

    def test_local_features_are_case_independent_and_permutation_equivariant(self):
        rng=np.random.default_rng(5);p=rng.normal(size=(3,7,12,18));perm=[4,1,0,5,3,2,6]
        x=local_features(p)
        np.testing.assert_allclose(local_features(p[:,perm]),x[:,perm],atol=1e-12)
        changed=p.copy();changed[1:]*=1000
        np.testing.assert_array_equal(local_features(changed)[:1],x[:1])

    def test_parameter_scaling_fits_only_assigned_rows_and_keeps_meanings_separate(self):
        theta={'a':np.array([[0.,7.],[2.,7.],[4.,8.]]),'b':np.array([[10.],[30.],[50.]])}
        d=np.array(['a']*3+['b']*3);rows=np.array([0,1,2]*2);fit=np.array([0,1,3,4])
        x,names,stats=parameter_blocks(theta,['a','b'],rows,d,fit)
        np.testing.assert_array_equal(x[:,1],0.)
        np.testing.assert_array_equal(x[:3,2],0.)
        np.testing.assert_array_equal(x[3:,:2],0.)
        np.testing.assert_allclose(x[[0,1],0],[-1,1]);np.testing.assert_allclose(x[[3,4],2],[-1,1])
        theta['a'][2]=[1e9,1e9]
        xx,_,newstats=parameter_blocks(theta,['a','b'],rows,d,fit)
        self.assertEqual(stats,newstats);np.testing.assert_array_equal(xx[fit],x[fit])

    def test_parameters_can_change_preferences_with_identical_field_descriptors(self):
        n=120;regime=np.arange(n)%2
        errors=np.stack([np.where(regime==0,.1,1.),np.where(regime==0,1.,.1)],axis=1)
        g=errors[:,:,None]*errors[:,None,:]
        x=np.zeros((n,2,2));x[:,:,-1]=(2*regime-1)[:,None]
        prior=np.full((n,2),.5);d=np.array(['synthetic']*n);c=np.array(['class']*n)
        fit=train_gate(x[:80],g[:80],prior[:80],d[:80],c[:80],x[80:100],g[80:100],prior[80:100],d[80:100],c[80:100],
                       kind='specific',penalty=0.,steps=160,passthrough_tail=1)
        self.assertTrue(fit['active'])
        w=gate_predict(x[100:],prior[100:],fit['mu'],fit['sd'],fit['coef'],fit['kind'])
        self.assertLess(risk(w,g[100:]).mean(),risk(prior[100:],g[100:]).mean()*.3)

if __name__=='__main__':unittest.main()
