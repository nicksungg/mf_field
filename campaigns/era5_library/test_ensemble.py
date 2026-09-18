"""Regression: changing final targets must not change the calibrated weights."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import collect_dataset as collector
from repair_common import save_npz,write_json,sha


class AnswerSeparation(unittest.TestCase):
    def test_final_answers_open_only_after_lock_and_cannot_change_weights(self):
        rng=np.random.default_rng(7);theta=np.arange(17,dtype=np.float32)[:,None]
        target=rng.normal(size=(17,4))+3
        models=['mf_fno_allpairs','mf_fno_transfer_film']
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'results').mkdir();write_json(root/'SOURCE.json',{})
            info=dict(pool=models,work_grid=[2,2],hf_level=2,levels={'2':{'grid':[2,2]}},n_base_hf_train=55)
            write_json(root/'PLAN.json',{'datasets':{'era5':info}})
            save_npz(root/'data/core/era5/train_l2.npz',x=np.arange(55)[:,None],y=rng.normal(size=(55,4))+3)
            for i,m in enumerate(models+['fno_hf_only_control']):
                path=root/'predictions'/f'{m}__era5.npz'
                save_npz(path,pred=target+rng.normal(size=target.shape)*.1+(.2 if i==0 else -.2),theta=theta,work_grid=[2,2])
                write_json(root/'metadata'/f'{m}__era5.json',dict(prediction_sha256=sha(path),smoke=False))
            roles={}
            for seed in collector.SEEDS:
                d=root/'answers/era5'/f's{seed}'
                save_npz(d/'calibration.npz',theta=theta[:10],target=target[:10],query_rows=np.arange(10))
                save_npz(d/'evaluation.npz',theta=theta[10:],target=target[10:],query_rows=np.arange(10,17))
                roles[f'era5__s{seed}']=dict(calibration_pool=list(range(10)),evaluation=list(range(10,17)),
                    budgets={'5':list(range(5)),'10':list(range(10))},
                    calibration_sha256=sha(d/'calibration.npz'),evaluation_sha256=sha(d/'evaluation.npz'))
            write_json(root/'ROLES.json',roles)
            original=np.load;opened=[]
            def guard(path,*args,**kwargs):
                p=Path(path)
                if p.name=='evaluation.npz':
                    fit=root/'results/era5'/p.parent.name/'fit.json'
                    self.assertTrue(fit.exists());opened.append(str(p))
                return original(path,*args,**kwargs)
            with patch.object(collector,'ROOT',root),patch.object(collector,'verify_source',lambda:{}),patch('sys.argv',['collect_dataset.py','--dataset','era5']),patch.object(np,'load',guard),contextlib.redirect_stdout(io.StringIO()):
                collector.main()
                before={s:sha(root/'results/era5'/f's{s}'/'locked_weights.npz') for s in collector.SEEDS}
                for seed in collector.SEEDS:
                    p=root/'answers/era5'/f's{seed}'/'evaluation.npz'
                    save_npz(p,theta=theta[10:],target=100*target[10:],query_rows=np.arange(10,17))
                    roles[f'era5__s{seed}']['evaluation_sha256']=sha(p)
                write_json(root/'ROLES.json',roles)
                collector.main()
                for seed in collector.SEEDS:
                    self.assertEqual(before[seed],sha(root/'results/era5'/f's{seed}'/'locked_weights.npz'))
            self.assertEqual(len(opened),6)

if __name__=='__main__':unittest.main()
