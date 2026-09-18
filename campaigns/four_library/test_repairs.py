"""Regression tests for the actual two ERA5 failure modes."""
import unittest
import numpy as np
from repair_common import purge_mask,paired_target_rows,keys,fix_allpairs_finetune_source

class Repairs(unittest.TestCase):
    def test_purge_all_repeated_occurrences_and_float32_collisions(self):
        train=np.array([[1.,2.],[3.,4.],[1.,2.],[5.,6.]],dtype=np.float64)
        reserved=np.array([[1.+1e-10,2.],[5.,6.]])
        np.testing.assert_array_equal(purge_mask(train,reserved),[False,True,False,False])

    def test_unpaired_join_retains_target_identity(self):
        source=np.array([[1.],[2.],[3.]])
        target=np.array([[3.],[9.],[1.],[1.]])
        values=np.array([30.,90.,10.,11.])
        rows=paired_target_rows(source,target)
        np.testing.assert_array_equal(rows,[0,2,3])
        np.testing.assert_array_equal(target[rows,0],[3.,1.,1.])
        np.testing.assert_array_equal(values[rows],[30.,10.,11.])

    def test_aligned_pair_behavior_is_unchanged(self):
        x=np.arange(18).reshape(6,3)
        np.testing.assert_array_equal(paired_target_rows(x,x),np.arange(6))

    def test_no_match_does_not_fabricate_pairs(self):
        self.assertEqual(len(paired_target_rows(np.array([[1.]]),np.array([[2.]]))),0)

    def test_finetune_uses_own_hf_inputs(self):
        source='X_lf = train["cond_by_fid"][lf].astype(np.float32)'
        env=dict(np=np,train={'cond_by_fid':{1:np.array([[1.]]),9:np.array([[9.]])}},lf=1,hf=9)
        exec(fix_allpairs_finetune_source(source),env)
        np.testing.assert_array_equal(env['X_lf'],[[9.]])

if __name__=='__main__':unittest.main()
