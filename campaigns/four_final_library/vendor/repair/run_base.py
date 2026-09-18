"""Train isolated surrogates; workers receive input-only evaluation files."""
import argparse
import importlib.util
import json
import os
import sys
import time
from itertools import combinations
import numpy as np
from repair_common import *


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',required=True,choices=DATASETS)
    ap.add_argument('--model',required=True,choices=MODELS+['fno_hf_only_control'])
    ap.add_argument('--smoke',action='store_true');a=ap.parse_args()
    manifest=verify_source() if not a.smoke else None
    plan=json.loads((ROOT/'PLAN.json').read_text());info=plan['datasets'][a.dataset]
    base=ROOT/'smoke' if a.smoke else ROOT
    tag=f'{a.model}__{a.dataset}';out=base/'predictions'/f'{tag}.npz'
    if out.exists() and (base/'metadata'/f'{tag}.json').exists():
        print('Already complete',tag);return
    d=ROOT/'data'/rel(a.dataset)
    for level,r in info['levels'].items():
        assert sha(d/f'train_l{level}.npz')==r['prepared_sha256']
        assert sha(d/f'test_l{level}.npz')==r['query_sha256']
    with np.load(d/f"test_l{info['hf_level']}.npz") as z:theta=z['x'].astype(np.float32)
    loads=[];original_load=np.load
    def protected_load(file,*args,**kwargs):
        if isinstance(file,(str,os.PathLike)):
            p=Path(file).absolute()
            assert ROOT/'answers' not in p.parents,'Training worker attempted to load held-out answers'
            if p.suffix=='.npz' and ('test_l' in p.name or 'train_l' in p.name):
                assert p.parent.resolve()==d.resolve(), f'Unexpected data path: {p}'
                loads.append(str(p))
        return original_load(file,*args,**kwargs)
    np.load=protected_load
    os.environ['DDE_BACKEND']='pytorch';os.environ.pop('SAVE_PRED_DIR',None)
    sys.path.insert(0,str(ROOT/'vendor'));sys.path.insert(0,str(ROOT))
    import torch
    torch.set_num_threads(int(os.environ.get('OMP_NUM_THREADS','4')))
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.set_float32_matmul_precision('highest')
    import data_adapters
    from data_adapters.geometry import resolve_grid
    torch.manual_seed(42);np.random.seed(42)
    start=time.time();extra={};training_time=None
    if a.model=='st_hf_pod_gp':
        import st_common,st_classical
        st_common.FACTORY_DATA=ROOT/'flat_data'
        data=st_common.load_any(rel(a.dataset),str(ROOT/'data'),42,val_frac=0.,device='cpu',min_val=0)
        pred,extra=st_classical.arm_hf_pod_gp(data,argparse.Namespace(seed=42,pod_energy=.999,pod_modes=64,gp_restarts=2))
        pred=pred.detach().cpu().numpy().reshape(len(theta),-1).astype(np.float64)*data['scale']
        grid=data['grid'];training_time=time.time()-start
    else:
        assert torch.cuda.is_available(),'GPU required'
        source_model='mf_fno_transfer_film' if a.model=='fno_hf_only_control' else a.model
        source=ROOT/'vendor'/source_model/'smoke_eval.py'
        spec=importlib.util.spec_from_file_location('repair_model',source)
        mod=importlib.util.module_from_spec(spec)
        if a.model=='mf_fno_allpairs':
            exec(compile(fix_allpairs_finetune_source(source.read_text()),str(source),'exec'),mod.__dict__)
        else:spec.loader.exec_module(mod)
        # Every dataset read must pass through the staged, audited adapter.
        original_adapter=data_adapters.load_mf_dataset
        def guarded_adapter(path,split='train',*args,**kwargs):
            assert Path(path).resolve()==d.resolve()
            data=original_adapter(path,split,*args,**kwargs)
            if a.model=='fno_hf_only_control':
                hf=data['hf_fid'];data=dict(data,fids=[hf],lf_fids=[])
                for name in ['cond_by_fid','field_by_fid','n_cells_by_fid','grid_shape_by_fid']:
                    data[name]={hf:data[name][hf]}
            return data
        mod.load_mf_dataset=guarded_adapter
        captured={}
        def capture(**kwargs):
            captured.update(pred=np.asarray(kwargs['pred'],np.float32),grid=list(kwargs['work_grid']),
                            train_seconds=float(kwargs['train_seconds']),extra=kwargs.get('extra',{}))
            return {'captured':True}
        mod.finalize_and_write=capture
        ck=base/'checkpoints'/tag
        from stage_train import StageTrainer
        trainer=StageTrainer(ck/'stages',dict(tag=tag,plan_sha256=sha(ROOT/'PLAN.json'),smoke=a.smoke))
        if hasattr(mod,'_train'):
            if a.model=='fno_hf_only_control':
                def only_hf(*args,**kwargs):
                    if args[-1]=='LF-pretrain':return
                    return trainer(*args,**kwargs)
                mod._train=only_hf
            else:mod._train=trainer
        if hasattr(mod,'_train_aug'):mod._train_aug=trainer.augmented
        if a.model=='mf_fno_allpairs':
            pair_records=[]
            def build_pairs(train,grid,args,fnorm):
                fields={f:mod._to_grid(train['field_by_fid'][f],resolve_grid(args.dataset_name,train['n_cells_by_fid'][f]),grid)
                        for f in train['fids']}
                xs=[];ys=[];pairs=[]
                for s,t in combinations(train['fids'],2):
                    source_x=train['cond_by_fid'][s];target_x=train['cond_by_fid'][t]
                    idx=paired_target_rows(source_x,target_x)
                    pair_records.append(dict(source=s,target=t,target_rows=idx.tolist(),n=len(idx)))
                    if not len(idx):continue
                    x=target_x[idx].astype(np.float32)
                    xs.append(np.column_stack([x,np.full(len(x),fnorm(s)),np.full(len(x),fnorm(t))]))
                    ys.append(fields[t][idx]);pairs.append((s,t))
                assert xs,'No aligned input pairs remain'
                return np.concatenate(xs).astype(np.float32),np.concatenate(ys).astype(np.float32),pairs
            mod.build_pairs=build_pairs
        mod.run(argparse.Namespace(dataset_dir=str(d),dataset_name=a.dataset,
            seed=42,epochs=1 if a.smoke else plan['base_epochs'],ckpt_dir=str(ck)),base/'unused.json')
        assert captured,'No predictions captured'
        pred=captured['pred'];grid=captured['grid'];extra=captured['extra'];training_time=captured['train_seconds']
        if a.model=='mf_fno_allpairs':extra=dict(extra,exact_join_pairs=pair_records,
            hf_finetune_uses_hf_parameters=True)
    assert pred.shape==(len(theta),int(np.prod(info['work_grid']))) and np.isfinite(pred).all()
    assert list(grid)==info['work_grid']
    save_npz(out,pred=np.asarray(pred,np.float32),theta=theta,work_grid=np.asarray(grid))
    write_json(base/'metadata'/f'{tag}.json',dict(dataset=a.dataset,model=a.model,smoke=a.smoke,
        seed=42,epochs=1 if a.smoke else plan['base_epochs'],prediction_sha256=sha(out),
        source_manifest_sha256=sha(ROOT/'SOURCE.json') if manifest else None,
        plan_sha256=sha(ROOT/'PLAN.json'),n_base_hf_train=info['n_base_hf_train'],
        elapsed_seconds=time.time()-start,train_seconds=training_time,device=torch.cuda.get_device_name() if torch.cuda.is_available() else 'cpu',
        matmul_tf32=False,cudnn_tf32=False,raw_test_answers_loaded=False,
        loaded_data_paths=sorted(set(loads)),extra=extra))
    print('EXPORTED',tag,'n',len(theta),flush=True)


if __name__=='__main__':main()
