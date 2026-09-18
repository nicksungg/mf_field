"""Inventory only: choose experts by mechanism and checkpoint coverage, not scores."""
from pathlib import Path
from collections import Counter
from config import *

def main():
    if (ROOT/'EXPORT_LAUNCH.json').exists():
        raise RuntimeError('Already launched; do not overwrite the inventory.')
    archive = MF/'release/predictions_full'
    roster = sorted(set.intersection(*[
        {p.name[len(m)+2:-len('__s42.npz')] for p in archive.glob(m+'__*__s42.npz')}
        for m in MODELS]))
    tasks = {}
    for line in (ST/'pred_tasks_gpu_all.txt').read_text().splitlines():
        m, rel, seed, ck = line.split()
        d = rel[5:] if rel.startswith('core/') else rel.replace('/', '__')
        if m in PAPER_MODELS and d in roster and seed == '42':
            src = next((b/m/'smoke_eval.py' for b in [MF/'akash/models',
                MF/'factory_mffp/models', MF/'factory_mffp/references/external_sota']
                if (b/m/'smoke_eval.py').exists()), None)
            assert src and Path(ck).is_file(), (m,d,ck)
            tasks[(m,d)] = dict(id=m+'__'+d, model=m, dataset=d, rel=rel,
                seed=42, checkpoint=ck, script=str(src), device='gpu',
                checkpoint_bytes=Path(ck).stat().st_size,
                checkpoint_mtime_ns=Path(ck).stat().st_mtime_ns,
                script_sha256=sha(src))
    for d in roster:
        assert d in CLASS_OF
        rel = d.replace('__','/') if '__' in d else 'core/'+d
        assert all((m,d) in tasks for m in PAPER_MODELS), d
        tasks[('st_hf_pod_gp',d)] = dict(id='st_hf_pod_gp__'+d,
            model='st_hf_pod_gp', dataset=d, rel=rel, seed=42, device='cpu',
            note='Classical estimator state was not saved; reproduce its original training-only fit.')
    # Interleave datasets so a complete dataset is ready as early as possible.
    order = ['darcy_generated','sharp__euler','heat_generated','poisson_generated','era5']
    ds_order = sorted(roster, key=lambda d:(order.index(d) if d in order else len(order),d))
    plan = dict(version=1, models=MODELS, datasets=ds_order, classes=CLASSES,
        class_mapping_source='/archive/workspace/mf_field_report/build_2d_figs.py:CLASS_ORDER',
        class_mapping_note='Existing eight classes; add corrected Poisson/cavity to their original classes.',
        tasks=[tasks[(m,d)] for d in ds_order for m in MODELS],
        excluded_datasets={d:'Incomplete common expert checkpoint coverage on current data'
                           for d in CLASS_OF if d not in roster},
        provenance='Historical benchmark test rows become a separate meta-learning corpus. No claim of fresh benchmark confirmation.',
        protocols={'case_holdout':'Three deterministic 60/20/20 fit/tune/evaluation splits, grouping shared generator inputs across versions.',
                   'class_holdout':'Eight folds: exclude all labels of one class from fitting, priors, normalization and tuning.'},
        split_seeds=[71,172,273], exclude_nodes=EXCLUDE,
        reuse_policy='Paper predictors frozen and inference-only. POD-GP refit using original base training rows only.',
        source_archive=str(archive))
    for f in ['logs','predictions','export_results','cache','results','runs','claims']:
        (ROOT/f).mkdir(exist_ok=True)
    write_json(ROOT/'plan.json', plan)
    print(json.dumps(dict(datasets=len(roster), classes=Counter(CLASS_OF[d] for d in roster),
                         tasks=len(tasks), omitted=plan['excluded_datasets']),indent=2))

if __name__ == '__main__': main()

