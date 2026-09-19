"""Isolated full-precision replay. Original scripts/checkpoints are never edited."""
import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
import numpy as np
import torch
from config import *

def export(task):
    out = ROOT/'predictions'/f"{task['id']}.npz"
    report = ROOT/'export_results'/f"{task['id']}.json"
    if out.exists() and report.exists(): return
    torch.set_num_threads(int(os.environ.get('OMP_NUM_THREADS','4')))
    start=time.time()
    sys.path.insert(0,str(MF/'factory_mffp'))
    import data_adapters
    from data_adapters.geometry import resolve_grid
    original_loader = data_adapters.load_mf_dataset
    seen = {}
    def loader(*args, **kwargs):
        d = original_loader(*args, **kwargs)
        split = args[1] if len(args)>1 else kwargs.get('split','train')
        if split == 'test':
            hf=d['hf_fid']; seen['theta']=d['cond_by_fid'][hf].copy()
        if split == 'train':
            hf=d['hf_fid']; fids=d['fids']; seen['n_hf']=len(d['cond_by_fid'][hf])
            seen['theta_train']=d['cond_by_fid'][hf].copy()
            seen['base_theta_all']=[v.copy() for v in d['cond_by_fid'].values()]
            seen['native_hf_grid']=resolve_grid(task['dataset'],d['n_cells_by_fid'][hf])
            seen['native_lf_grid']=resolve_grid(task['dataset'],d['n_cells_by_fid'][min(fids)])
            seen['levels']=len(fids)
        return d
    data_adapters.load_mf_dataset=loader
    os.environ.pop('SAVE_PRED_DIR',None)
    cksha = None; scriptsha = None
    if task['device']=='gpu':
        assert torch.cuda.is_available(), 'GPU required for faithful replay'
        # Small scientific errors are sensitive to TF32 convolution/matmul rounding.
        torch.backends.cuda.matmul.allow_tf32=False
        torch.backends.cudnn.allow_tf32=False
        torch.set_float32_matmul_precision('highest')
        src=Path(task['script']); ck=Path(task['checkpoint'])
        assert src.is_file() and sha(src)==task['script_sha256']
        assert ck.stat().st_size==task['checkpoint_bytes'] and ck.stat().st_mtime_ns==task['checkpoint_mtime_ns']
        cksha=sha(ck); scriptsha=sha(src)
        sd=torch.load(ck,map_location='cpu',weights_only=False)
        epochs=int(sd.get('epochs_target',2500)); del sd
        loaded=[]
        original_load_state=torch.nn.Module.load_state_dict
        def load_state(self,*a,**kw):
            result=original_load_state(self,*a,**kw);loaded.append(type(self).__name__);return result
        torch.nn.Module.load_state_dict=load_state
        def forbidden(*a,**kw): raise RuntimeError('Frozen export forbids training or checkpoint writes')
        torch.Tensor.backward=forbidden
        torch.autograd.backward=forbidden
        torch.optim.AdamW.step=forbidden
        torch.optim.Adam.step=forbidden
        torch.save=forbidden
        import data_adapters.metrics as metrics
        def capture(*args, **kwargs):
            assert loaded, 'No model state was loaded'
            seen['pred']=np.asarray(kwargs['pred'],np.float32)
            seen['target']=np.asarray(kwargs['target'],np.float32)
            seen['work_grid']=tuple(kwargs['work_grid'])
            seen['model_metadata']=dict(n_params=kwargs['n_params'],extra=kwargs.get('extra',{}))
            return {'captured':True}
        metrics.finalize_and_write=capture
        spec=importlib.util.spec_from_file_location('frozen_smoke',src)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        mod.run(argparse.Namespace(dataset_dir=str(ST/'data'/task['rel']),
            dataset_name=task['dataset'],epochs=epochs,seed=42,ckpt_dir=str(ck.parent)),
            ROOT/'export_results'/f"{task['id']}.unused.json")
        assert sha(ck)==cksha
        assert 'pred' in seen and 'theta' in seen
        replay=dict(checkpoint_sha256=cksha,script_sha256=scriptsha,epochs=epochs,loaded_modules=loaded,
                    device=torch.cuda.get_device_name(),base_retrained=False,
                    matmul_tf32=torch.backends.cuda.matmul.allow_tf32,cudnn_tf32=torch.backends.cudnn.allow_tf32,
                    matmul_precision=torch.get_float32_matmul_precision())
    else:
        sys.path.insert(0,str(ST))
        import st_common
        import st_classical
        # Canonical raw fields / input identities come from the common paper loader.
        train=loader(ST/'data'/task['rel'],'train')
        test=loader(ST/'data'/task['rel'],'test')
        raw_theta=seen['theta'].copy()
        data=st_common.load_any(task['rel'],str(ST/'data'),42,val_frac=0.,device='cpu',min_val=0)
        args=argparse.Namespace(seed=42,pod_energy=.999,pod_modes=64,gp_restarts=2)
        pred,extra=st_classical.arm_hf_pod_gp(data,args)
        # Classical dumps were normalized by a TRAINING-derived scale. Restore raw units.
        seen['pred']=pred.detach().cpu().numpy().reshape(len(pred),-1).astype(np.float64)*data['scale']
        seen['target']=data['Ytest'].detach().cpu().numpy().reshape(len(pred),-1).astype(np.float64)*data['scale']
        seen['theta']=raw_theta
        seen['work_grid']=tuple(data['grid'])
        seen['model_metadata']=extra
        replay=dict(device='cpu',base_retrained=True,reason='POD-GP estimator was not checkpointed',
                    raw_units_multiplier=float(data['scale']),registration=data['registration'])
    p=np.asarray(seen['pred'],np.float32);y=np.asarray(seen['target'],np.float32)
    assert p.shape==y.shape and len(p)==len(seen['theta']) and np.isfinite(p).all() and np.isfinite(y).all()
    # Base LF/HF training overlap audit; theta-only duplicates are unsafe meta-evaluation rows.
    theta=np.asarray(seen['theta'],np.float32)
    all_base={np.ascontiguousarray(row,np.float32).tobytes() for a in seen['base_theta_all'] for row in a}
    overlap=np.asarray([np.ascontiguousarray(row,np.float32).tobytes() in all_base for row in theta])
    atomic_npz(out,pred=p,target=y,theta=theta,base_train_overlap=overlap,
               work_grid=np.asarray(seen['work_grid']),native_hf_grid=np.asarray(seen['native_hf_grid']),
               native_lf_grid=np.asarray(seen['native_lf_grid']),
               n_hf=np.int64(seen['n_hf']),levels=np.int64(seen['levels']))
    # Replay diagnostics do not feed feature extraction, priors, or gate fitting.
    rel=np.linalg.norm(p.astype(float)-y,axis=1)/np.maximum(np.linalg.norm(y.astype(float),axis=1),1e-8)
    oldpath=MF/'release/predictions_full'/f"{task['model']}__{task['dataset']}__s42.npz"
    old=np.load(oldpath)['rel_l2_per_sample']
    write_json(report,dict(task=task,seconds=time.time()-start,replay=replay,
        n=len(p),work_grid=seen['work_grid'],base_train_overlap=int(overlap.sum()),
        rel_l2_mean=float(rel.mean()),archive_mean=float(old.mean()),
        prediction_sha256=sha(out),model_metadata=seen['model_metadata']))
    print(f"EXPORTED {task['id']} n={len(p)} seconds={time.time()-start:.1f}",flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--task',required=True);a=ap.parse_args()
    task=next(t for t in json.loads((ROOT/'plan.json').read_text())['tasks'] if t['id']==a.task)
    export(task)
