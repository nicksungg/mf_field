"""Verified four-dataset completion, merged without changing diagnostic archives."""
from pathlib import Path
import hashlib,json,math
import numpy as np
from paper_scope import EXTENSION_DATASETS,PDE_COUNT
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/four_dataset_completion'
CORE_METHODS=('single_l2','uniform','inverse_mse','full','allpairs')
SEEDS=(71,172,273)
def load(path):return json.loads(path.read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def records():return {d:load(DATA/'results'/f'{d}.json') for d in EXTENSION_DATASETS}
def verify():
    manifest=load(DATA/'IMPORT_MANIFEST.json')
    for name,sha in manifest['sha256'].items():assert digest(DATA/name)==sha,name
    complete=load(DATA/'results/COMPLETE.json');plan=load(DATA/'PLAN.json');roles=load(DATA/'ROLES.json')
    assert complete['complete'] and set(complete['datasets'])==set(EXTENSION_DATASETS)
    assert digest(DATA/'PLAN.json')==complete['plan_sha256']
    assert digest(DATA/'results/comparison.csv')==complete['comparison_sha256']
    distinct=set();appearances=0;record_count=0
    for ds,result in records().items():
        assert result['complete'] and result['n_individual_models']==9 and result['n_baseline_entries']==13
        assert plan['datasets'][ds]['training_reserved_overlap']==0
        lock=load(DATA/'weights'/f'{ds}.json')
        assert digest(DATA/'weights'/f'{ds}.json')==result['weight_sha256']
        assert lock['plan_sha256']==digest(DATA/'PLAN.json') and lock['roles_sha256']==digest(DATA/'ROLES.json')
        assert lock['evaluation_answers_used'] is False
        assert result['model_order']==plan['models']==lock['model_order']
        for seed in SEEDS:
            role=roles[f'{ds}__s{seed}'];evaluation=role['evaluation']
            assert len(set(evaluation))==len(evaluation)
            assert not set(evaluation)&set(role['calibration_pool'])
            distinct.update((ds,row) for row in evaluation);appearances+=len(evaluation)
            part=[r for r in result['records'] if r['partition']==seed]
            assert len(part)==37 and sum(r['kind']=='individual' for r in part)==9 and sum(r['kind']=='baseline' for r in part)==13
            for b in (5,10,20):
                fitting=role['budgets'][str(b)];fit=lock['fits'][f's{seed}_K{b}']
                assert len(fitting)==b and set(fitting)<=set(role['calibration_pool'])
                assert fitting==fit['query_rows'] and fit['actual_calibration_count']==b
                if b<20:assert set(fitting)<=set(role['budgets'][str(b*2)])
                for rule,w in fit['weights'].items():
                    assert len(w)==9 and min(w)>=-1e-12 and abs(sum(w)-1)<1e-10
                w=fit['weights']['selected_single'];assert np.count_nonzero(w)==1 and max(w)==1
                selected=next(r for r in part if r['kind']=='ensemble' and r['budget']==b and r['model']=='selected_single')
                expert=next(r for r in part if r['kind']=='individual' and r['model']==result['model_order'][int(np.argmax(w))])
                assert np.allclose(selected['per_case_rel_l2'],expert['per_case_rel_l2'],rtol=1e-12,atol=1e-15)
            for row in part:
                a=np.asarray(row['per_case_rel_l2']);assert np.isfinite(a).all() and (a>=0).all()
                assert row['query_rows']==evaluation and row['n_eval']==len(evaluation)==len(a)
                assert np.isclose(a.mean(),row['mean_rel_l2'],rtol=1e-12,atol=1e-15)
                record_count+=1
        for model,artifact in result['baseline_artifacts'].items():
            if artifact['kind']=='per_case_errors':
                path=DATA/'baseline_errors'/ds/f'{model}.json'
                assert digest(path)==artifact['scalar_errors_sha256']
                baseline=load(path)
                assert baseline['query_sha256']==plan['datasets'][ds]['query_sha256']==artifact['query_sha256']
                for row in result['records']:
                    if row['kind']=='baseline' and row['model']==model:
                        assert np.allclose(np.asarray(baseline['per_query_rel_l2'])[row['query_rows']],row['per_case_rel_l2'],rtol=1e-12,atol=1e-15)
            else:
                path=DATA/'metadata'/ds/f'{model}.json'
                assert digest(path)==artifact['metadata_sha256']
        for model in result['model_order']:
            meta=load(DATA/'metadata'/ds/f'{model}.json')
            assert meta['scientific_result'] and not meta.get('smoke',False)
            assert meta['prediction_sha256']==lock['prediction_sha256'][model]
    check=dict(passed=True,datasets=list(EXTENSION_DATASETS),imported_artifacts=len(manifest['sha256']),
               individual_predictions=36,baseline_entries=52,partitions=12,verified_error_records=record_count,
               evaluation_appearances=appearances,distinct_evaluation_dataset_rows=len(distinct),
               primary_methods=list(CORE_METHODS),historical_diagnostics_not_extended=True)
    (ROOT/'qa/extension_checks.json').write_text(json.dumps(check,indent=2)+'\n')
    return check

def partitions(ds):
    result=records()[ds];out=[]
    for seed in SEEDS:
        p=[r for r in result['records'] if r['partition']==seed]
        errors={r['model']:float(np.mean(r['per_case_rel_l2'])) for r in p if r['kind']=='individual'}
        errors.update({('single_l2' if r['model']=='selected_single' else r['model']):float(np.mean(r['per_case_rel_l2'])) for r in p if r['kind']=='ensemble' and r['budget']==5 and r['model'] in ['selected_single','inverse_mse','full']})
        out.append(dict(dataset=ds,seed=seed,n_evaluation=p[0]['n_eval'],errors=errors))
    return out

def extend_primary(original,class_of):
    verify();results=records();out={}
    for b,old in original.items():
        means={d:{m:e[m] for m in CORE_METHODS} for d,e in old['mean_errors'].items()}
        for ds,result in results.items():
            means[ds]={}
            for m in CORE_METHODS:
                source='selected_single' if m=='single_l2' else m
                rows=[r for r in result['records'] if r['kind']=='individual' and r['model']=='mf_fno_allpairs'] if m=='allpairs' else [r for r in result['records'] if r['kind']=='ensemble' and r['model']==source and r['budget']==int(b)]
                assert len(rows)==3
                means[ds][m]=float(np.mean([np.mean(r['per_case_rel_l2']) for r in rows]))
        assert len(means)==PDE_COUNT
        comparisons={}
        for m in CORE_METHODS:
            ratios={d:e[m]/e['single_l2'] for d,e in means.items()}
            cs=sorted({class_of[d] for d in ratios})
            classes={c:math.exp(np.mean([math.log(v) for d,v in ratios.items() if class_of[d]==c])) for c in cs}
            comparisons[m]=dict(dataset_ratios=ratios,class_ratios=classes,
                class_balanced_ratio=math.exp(np.mean(np.log(list(classes.values())))),
                dataset_balanced_ratio=math.exp(np.mean(np.log(list(ratios.values())))),
                improved_over_1pct=sum(v<.99 for v in ratios.values()),worsened_over_1pct=sum(v>1.01 for v in ratios.values()))
        out[b]=dict(mean_errors=means,comparisons={'single_l2':comparisons})
    return out

def update_inventory(inventory):
    plan=load(DATA/'PLAN.json');gallery=load(DATA/'gallery_manifest.json')
    dimensions={r['dataset']:r['x']['source_shape'][1] for r in gallery['datasets']}
    for a in inventory:
        ds=a['dataset']
        if ds not in EXTENSION_DATASETS:continue
        spec=plan['datasets'][ds];lf=[v['kept_train_count'] for k,v in spec['levels'].items() if int(k)!=spec['hf_level']]
        a.update(input_dimension=dimensions[ds],work_grid=spec['work_grid'],levels=len(spec['levels']),
                 hf_train_available=spec['n_base_hf_train'],lf_train_min=min(lf),lf_train_max=max(lf),
                 n_historical_query=spec['n_query'],lf_overlap=0,hf_overlap=0,historical_nine_experts=True,
                 evaluation_cases_per_partition=partitions(ds)[0]['n_evaluation'])
    return inventory

def add_baselines(means,records_out,proofs):
    for ds,result in records().items():
        grouped={}
        for r in result['records']:
            if r['kind']!='baseline':continue
            grouped.setdefault(r['model'],[]).append(float(np.mean(r['per_case_rel_l2'])))
            for row,value in zip(r['query_rows'],r['per_case_rel_l2']):
                records_out.append(dict(dataset=ds,model=r['model'],base_seed=42,partition_seed=r['partition'],row=row,relative_l2=value))
        for m,values in grouped.items():
            assert len(values)==3;means[ds][m]=float(np.mean(values))
            proofs.append(dict(dataset=ds,model=m,proof='verified completion on sealed query identities',source=f'four_dataset_completion/results/{ds}.json',seed=42))
