"""Create isolated input-disjoint data, sealed answers, and a frozen task plan."""
import json
import shutil
import sys
from pathlib import Path
import numpy as np
from repair_common import *


def main():
    if (ROOT/'PREPARED.json').exists():
        print('Preparation already complete');return
    for name in ['data','flat_data','answers','predictions','metadata','checkpoints','logs','results','uqcorr','claims']:
        (ROOT/name).mkdir(parents=True,exist_ok=True)
    old=json.loads((MF/'experiments/fieldgate_matched_20260912/plan.json').read_text())
    sources={t['model']:Path(t['script']) for t in old['tasks'] if t['dataset']=='era5' and 'script' in t}
    provenance={}
    for model,source in sources.items():
        dest=ROOT/'vendor'/model
        shutil.copytree(source.parent,dest,dirs_exist_ok=True,
            ignore=shutil.ignore_patterns('__pycache__','*.pt','*.npz','*.json','runs','logs','results'))
        provenance[model]=dict(original=str(source),original_sha256=sha(source),copied=str(dest/'smoke_eval.py'))
    # Akash model code imports common.backbone/common.mffp.
    shutil.copytree(MF/'akash/common',ROOT/'common',dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__'))
    for name in ['diag_coarse.py','corr_ens.py','corr_backbones.py']:
        shutil.copy2(MF/'experiments/uqcorr'/name,ROOT/'uqcorr'/name)
    # Keep snapshots of the external helpers used by training and preprocessing.
    shutil.copytree(MF/'factory_mffp/data_adapters',ROOT/'data_adapters',dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__'))
    for name in ['st_common.py','st_classical.py','ct_common.py']:
        shutil.copy2(ST/name,ROOT/'vendor'/name)
    sys.path.insert(0,str(ROOT));sys.path.insert(0,str(MF/'factory_mffp'))
    from data_adapters.geometry import resolve_grid
    import torch
    torch.set_num_threads(4)
    import torch.nn.functional as F
    reports={}
    for ds in DATASETS:
        folder=ST/'data'/rel(ds)
        if not list(folder.glob('train_l*.npz')):
            folder=next(folder.glob('*/train_l1.npz')).parent
        trains=sorted(folder.glob('train_l*.npz'),key=lambda p:int(p.stem.split('_l')[1]))
        hf=int(trains[-1].stem.split('_l')[1])
        with np.load(trains[-1]) as z: xhf=z['x'].astype(np.float32)
        with np.load(folder/f'test_l{hf}.npz') as z: xt=z['x'].astype(np.float32)
        cal_rows=np.arange(55,65) if ds=='era5' else np.array([],dtype=int)
        if ds=='era5': assert xhf.shape==(65,12) and len(xt)==7
        query=np.concatenate([xhf[cal_rows],xt])
        reserved=query
        assert len(set(keys(query)))==len(query)
        dest=ROOT/'data'/rel(ds);dest.mkdir(parents=True,exist_ok=True)
        alias=ROOT/'flat_data'/ds
        if not alias.exists():alias.symlink_to(dest,target_is_directory=True)
        report=dict(dataset=ds,hf_level=hf,n_query=len(query),n_original_test=len(xt),
                    calibration_from_original_hf_train=cal_rows.tolist(),levels={})
        fine_answers=None
        for p in trains:
            level=int(p.stem.split('_l')[1])
            with np.load(p) as z: x=z['x'].copy();y=z['y'].copy()
            assert len(x)==len(y)
            mask=purge_mask(x,reserved)
            if ds!='era5':assert mask.all(),(ds,level,'Unexpected preexisting overlap')
            if ds=='era5' and level==hf:
                assert mask.sum()==55
                with np.load(folder/f'test_l{hf}.npz') as z: yf=z['y'].astype(np.float32)
                fine_answers=np.concatenate([y[cal_rows].astype(np.float32),yf])
            elif level==hf:
                with np.load(folder/f'test_l{hf}.npz') as z:fine_answers=z['y'].astype(np.float32)
            if ds=='era5':save_npz(dest/p.name,x=x[mask],y=y[mask])
            else:
                # Immutable source hashes are checked before each worker.
                link=dest/p.name
                if not link.exists():link.symlink_to(p.resolve())
            cells=int(np.prod(y.shape[1:]));grid=tuple(resolve_grid(ds,cells))
            save_npz(dest/f'test_l{level}.npz',x=query,y=np.zeros((len(query),cells),dtype=np.float32))
            report['levels'][str(level)]=dict(original_train_count=len(x),kept_train_count=int(mask.sum()),
                removed_rows=np.flatnonzero(~mask).tolist(),grid=list(grid),
                original_path=str(p),original_sha256=sha(p),prepared_sha256=sha(dest/p.name),
                query_sha256=sha(dest/f'test_l{level}.npz'))
            assert purge_mask(x[mask],reserved).all()
            del x,y
        native=report['levels'][str(hf)]['grid'];factor=min(1.,256/max(native))
        grid=tuple(max(1,round(n*factor)) for n in native)
        target=torch.as_tensor(fine_answers).reshape(len(query),1,*native)
        if list(grid)!=native:target=F.interpolate(target,size=grid,mode='bilinear',align_corners=False)
        answers=target[:,0].numpy().reshape(len(query),-1).copy()
        # Separate files make final truth access auditable in the collector.
        if ds=='era5':
            save_npz(ROOT/'answers'/ds/'calibration.npz',theta=query[:10],target=answers[:10],work_grid=grid)
            save_npz(ROOT/'answers'/ds/'evaluation.npz',theta=query[10:],target=answers[10:],work_grid=grid)
        else:save_npz(ROOT/'answers'/ds/'historical.npz',theta=query,target=answers,work_grid=grid)
        report.update(work_grid=list(grid),query_sha256=__import__('hashlib').sha256(query.tobytes()).hexdigest(),
                      n_base_hf_train=report['levels'][str(hf)]['kept_train_count'],
                      test_fields_in_training_tree='zeros; real targets stored separately under answers/',
                      pool=MODELS+(CORRECTORS if ds!='era5' else []))
        reports[ds]=report
        if ds=='sharp__cahn_hilliard':
            for model in MODELS:
                src=MF/'experiments/fieldgate_matched_20260912/predictions'/f'{model}__{ds}.npz'
                with np.load(src) as z:
                    assert np.array_equal(z['theta'],query) and not z['base_train_overlap'].any()
                    pred=z['pred'].copy();g=z['work_grid'].copy()
                save_npz(ROOT/'predictions'/f'{model}__{ds}.npz',pred=pred,theta=query,work_grid=g)
                write_json(ROOT/'metadata'/f'{model}__{ds}.json',dict(reused=True,source=str(src),
                    source_sha256=sha(src),prediction_sha256=sha(ROOT/'predictions'/f'{model}__{ds}.npz'),
                    dataset=ds,model=model,source_experiment='fieldgate_matched_20260912'))
        print('PREPARED',ds,'base HF',report['n_base_hf_train'],'query',len(query),flush=True)
    (ROOT/'roster.txt').write_text('\n'.join(rel(d) for d in DATASETS if d!='era5')+'\n')
    tasks=[]
    for ds in DATASETS:
        if ds!='sharp__cahn_hilliard':
            for model in MODELS:
                tasks.append(dict(kind='base',dataset=ds,model=model,device='cpu' if model=='st_hf_pod_gp' else 'gpu'))
        tasks.append(dict(kind='base',dataset=ds,model='fno_hf_only_control',device='gpu'))
    for ds in DATASETS[1:]:
        for fold in range(5):
            for variant in ['plain','hetero']:
                for seed in [42,123]:
                    tasks.append(dict(kind='coarse',dataset=ds,fold=fold,variant=variant,seed=seed,device='gpu'))
    plan=dict(version=1,datasets=reports,paper_sources=provenance,base_seed=42,base_epochs=2500,
        coarse_steps=30000,corrector_steps=6000,corrector_K=6,coarse_members_per_fold=4,nfolds=5,
        split_seeds=SEEDS,budgets=[5,10,20],era5_budgets=[5,10],tasks=tasks,
        primary_methods=['full','inverse_mse','selected_single','uniform','allpairs'],
        era5_protocol='55 original HF training rows, last 10 original training rows reserved for calibration, 7 original test rows for evaluation. Purge all 17 input vectors at every fidelity. Row order is retained; calendar dates are not inferred. This is input-held-out climate emulation, not a strict forecast-origin experiment.',
        sharp_protocol='Existing base train rows preserved; historical test inputs partitioned 80/20 into calibration pool/evaluation using fixed input hashes. Nested calibration budgets 5/10/20.',
        allpairs_fix='Exact parameter join, using target rows and their own parameters; never zip unmatched fidelity rows by position.',
        era5_unavailable=CORRECTORS,era5_unavailable_reason='Current OOF correctors require aligned LF/HF rows. ERA5 is unpaired and they are not silently substituted.',
        diagnostics_only=['legacy cavity and Poisson versions with documented defects; use corrected versions for primary physical interpretation'],
        fresh_test_claim=False,excluded_nodes=EXCLUDE)
    write_json(ROOT/'PLAN.json',plan)
    write_json(ROOT/'PREPARED.json',dict(passed=True,datasets=reports,plan_sha256=sha(ROOT/'PLAN.json')))
    print('Preparation complete; launcher will freeze source before training.',flush=True)


if __name__=='__main__':main()
