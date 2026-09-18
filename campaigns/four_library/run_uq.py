"""Complete four paired-dataset ensembles with matched four-member OOF inputs."""
import argparse
import importlib.util
import json
import os
import sys
import time
import numpy as np
from repair_common import *

def preload(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod;spec.loader.exec_module(mod);return mod

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',required=True,choices=DATASETS[1:])
    ap.add_argument('--kind',required=True,choices=['coarse','assemble','corrector'])
    ap.add_argument('--fold',type=int,default=0);ap.add_argument('--variant',choices=['plain','hetero'],default='plain')
    ap.add_argument('--seed',type=int,default=42);ap.add_argument('--backbone',choices=['transolver','convnext'],default='transolver')
    ap.add_argument('--smoke',action='store_true');a=ap.parse_args()
    if not a.smoke:verify_source()
    plan=json.loads((ROOT/'PLAN.json').read_text());info=plan['datasets'][a.dataset]
    U=(ROOT/'smoke' if a.smoke else ROOT)/'uqcorr';U.mkdir(parents=True,exist_ok=True)
    d=ROOT/'data'/rel(a.dataset);lf=info['hf_level']-1
    for level,r in info['levels'].items():
        assert sha(d/f'train_l{level}.npz')==r['prepared_sha256']
        assert sha(d/f'test_l{level}.npz')==r['query_sha256']
    os.environ['UQ_ST']=str(ROOT)
    sys.path.insert(0,str(ROOT/'vendor'));sys.path.insert(0,str(ROOT/'uqcorr'));sys.path.insert(0,str(ROOT))
    import torch
    torch.set_num_threads(int(os.environ.get('OMP_NUM_THREADS','4')))
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.set_float32_matmul_precision('highest')
    import data_adapters
    preload('model',ROOT/'vendor/mf_fno_transfer_film/model.py')
    preload('smoke_eval',ROOT/'vendor/mf_fno_transfer_film/smoke_eval.py')
    preload('ct_common',ROOT/'vendor/ct_common.py')
    diag=preload('diag_coarse',ROOT/'uqcorr/diag_coarse.py')
    original_load=np.load;loaded=[]
    def guarded(file,*args,**kwargs):
        if isinstance(file,(str,os.PathLike)):
            path=Path(file).absolute()
            assert ROOT/'answers' not in path.parents,'Held-out answers requested by training'
            if 'train_l' in path.name or 'test_l' in path.name:
                assert d in path.parents,f'Unexpected dataset path: {path}'
            loaded.append(str(path))
        return original_load(file,*args,**kwargs)
    np.load=guarded
    if a.kind=='coarse':
        assert torch.cuda.is_available()
        tag=f'{a.variant}__{a.dataset}__L{lf}__F{a.fold}of5__s{a.seed}'
        result=U/'raw'/f'{tag}.json'
        if result.exists() and (U/'preds'/f'{tag}.npz').exists():return
        sys.argv=['diag_coarse.py','--name',a.dataset,'--lf-level',str(lf),'--variant',a.variant,
            '--seed',str(a.seed),'--nfolds','5','--fold',str(a.fold),'--steps',str(8 if a.smoke else plan['coarse_steps']),
            '--out-dir',str(U),'--ckpt-dir',str(U/'ck'/tag),'--tag',tag,'--device','cuda']
        diag.main()
        record=json.loads(result.read_text());assert not record.get('excluded'),record.get('excluded')
        write_json(U/'audit'/f'{tag}.json',dict(smoke=a.smoke,raw_test_answers_loaded=False,
            plan_sha256=sha(ROOT/'PLAN.json'),prediction_sha256=sha(U/'preds'/f'{tag}.npz'),loaded_paths=sorted(set(loaded))))
    elif a.kind=='assemble':
        assert not a.smoke
        with np.load(d/f'train_l{lf}.npz') as z:n=len(z['x'])
        grid=info['levels'][str(lf)]['grid'];mean=np.zeros((n,*grid),np.float64)
        squares=np.zeros_like(mean);count=np.zeros(n,int);test=[];fold_rows={};digests={}
        for fold in range(5):
            for variant in ['plain','hetero']:
                for seed in [42,123]:
                    tag=f'{variant}__{a.dataset}__L{lf}__F{fold}of5__s{seed}'
                    path=U/'preds'/f'{tag}.npz'
                    with np.load(path) as z:
                        rows=z['hold_rows'].copy();mu=z['mu_hold'].astype(np.float64)
                        assert mu.shape==(len(rows),*grid)
                        if fold in fold_rows:np.testing.assert_array_equal(rows,fold_rows[fold])
                        else:fold_rows[fold]=rows
                        mean[rows]+=mu;squares[rows]+=mu**2;count[rows]+=1
                        if fold==0:test.append(z['mu_test'].astype(np.float64))
                    digests[tag]=sha(path)
        assert np.all(count==4) and len(test)==4
        mean/=4;spread=np.sqrt(np.maximum(squares/4-mean**2,0));test=np.stack(test)
        dest=U/'oof'/f'{a.dataset}__L{lf}.npz'
        save_npz(dest,mean_train=mean.astype(np.float32),spread_train=spread.astype(np.float32),
            n_members_train=count,mean_test=test.mean(0).astype(np.float32),spread_test=test.std(0).astype(np.float32),
            members_test=np.int64(4),test_fold=np.int64(0),grid=np.asarray(grid))
        write_json(U/'audit'/f'{a.dataset}__oof.json',dict(passed=True,n_train=n,members_train=4,members_test=4,
            source_predictions=digests,oof_sha256=sha(dest),test_fold=0,raw_test_answers_loaded=False))
        print('ASSEMBLED',a.dataset,'4 members for every training and test input',flush=True)
    else:
        assert torch.cuda.is_available()
        corr=preload('corr_ens',ROOT/'uqcorr/corr_ens.py');corr.HERE=U
        if a.smoke:
            with np.load(d/f'train_l{lf}.npz') as z:n=len(z['x'])
            g=info['levels'][str(lf)]['grid']
            save_npz(U/'oof'/f'{a.dataset}__L{lf}.npz',
                mean_train=np.zeros((n,*g),np.float32),mean_test=np.zeros((info['n_query'],*g),np.float32),
                n_members_train=np.full(n,4),members_test=np.int64(4))
            print('Architecture smoke only: zero-field OOF stub; never a scientific result',flush=True)
        else:
            proof=json.loads((U/'audit'/f'{a.dataset}__oof.json').read_text())
            assert proof['passed'] and proof['members_train']==proof['members_test']==4
            assert sha(U/'oof'/f'{a.dataset}__L{lf}.npz')==proof['oof_sha256']
        tag=f'{a.backbone}-pred__{a.dataset}__L{lf}__s42'
        result=U/'raw_corr'/f'{tag}.json'
        if not(result.exists() and (U/'preds_corr'/f'{tag}.npz').exists()):
            sys.argv=['corr_ens.py','--name',a.dataset,'--backbone',a.backbone,'--input','pred','--seed','42',
                '--steps',str(1 if a.smoke else plan['corrector_steps']),'--K','6',
                '--out-dir',str(U),'--ckpt-dir',str(U/'ck_corr'/tag),'--tag',tag,'--device','cuda']
            corr.main()
        with np.load(U/'preds_corr'/f'{tag}.npz') as z:pred=z['pred_test'].reshape(info['n_query'],-1).copy()
        with np.load(d/f"test_l{info['hf_level']}.npz") as z:theta=z['x'].astype(np.float32)
        assert np.isfinite(pred).all()
        model=f'uqcorr_{a.backbone}_pred';base=ROOT/'smoke' if a.smoke else ROOT
        dest=base/'predictions'/f'{model}__{a.dataset}.npz'
        save_npz(dest,pred=pred,theta=theta,work_grid=np.asarray(info['work_grid']))
        result_data=json.loads(result.read_text())
        write_json(base/'metadata'/f'{model}__{a.dataset}.json',dict(dataset=a.dataset,model=model,smoke=a.smoke,
            plan_sha256=sha(ROOT/'PLAN.json'),prediction_sha256=sha(dest),raw_test_answers_loaded=False,
            train_seconds=result_data['train_seconds'],selected_step=result_data['selected_step'],
            members_train=result_data['oof_members_train'],members_test=result_data['oof_members_test'],
            matmul_tf32=False,cudnn_tf32=False,loaded_paths=sorted(set(loaded))))
        print('EXPORTED',model,a.dataset,flush=True)

if __name__=='__main__':main()
