"""Prepare unpaired training inputs without changing the ERA5 case roles."""
import json
import shutil
import sys
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from era5_common import ROOT, sha, write_json, save_npz, input_keys

def grouped_split(x, fraction=.1, seed=42):
    keys = input_keys(x)
    unique = list(dict.fromkeys(keys))
    order = np.random.default_rng(seed).permutation(len(unique))
    count = min(len(unique)-1, max(4, int(round(fraction * len(unique)))))
    held = {unique[i] for i in order[:count]}
    val = [i for i, k in enumerate(keys) if k in held]
    train = [i for i, k in enumerate(keys) if k not in held]
    assert train and val
    return dict(train_rows=train, val_rows=val)

def coarse_folds(x_lf, x_hf, nfolds=5):
    hf_keys, lf_keys = input_keys(x_hf), input_keys(x_lf)
    groups = list(dict.fromkeys(hf_keys))
    order = np.random.default_rng(1234).permutation(len(groups))
    folds = []
    for fold, indices in enumerate(np.array_split(order, nfolds)):
        prohibited = {groups[i] for i in indices}
        held = [i for i, k in enumerate(hf_keys) if k in prohibited]
        train = [i for i, k in enumerate(lf_keys) if k not in prohibited]
        assert train and held
        assert not set(lf_keys[i] for i in train) & prohibited
        folds.append(dict(fold=fold, hold_hf_rows=held, train_lf_rows=train))
    assert sorted(i for f in folds for i in f['hold_hf_rows']) == list(range(len(x_hf)))
    return folds

def resized(y, native, grid):
    t = torch.from_numpy(np.asarray(y, np.float32)).reshape(-1, 1, *native)
    if list(native) != list(grid):
        t = F.interpolate(t, size=grid, mode='bilinear', align_corners=False)
    return t[:, 0].numpy().copy()

def main():
    torch.set_num_threads(4)
    marker = ROOT / 'EXPERIMENT.json'
    if marker.exists():
        print('Already prepared'); return
    manifest = json.loads((ROOT / 'transfer/CLUSTER_INPUT_MANIFEST.json').read_text())
    for entry in manifest['files']:
        assert sha(ROOT / 'source' / entry['path']) == entry['sha256'], entry['path']
    original = json.loads((ROOT / 'source/PLAN.json').read_text())
    info = original['datasets']['era5']
    folder = ROOT / 'source/data/core/era5'
    with np.load(folder / 'train_l8.npz') as z:
        x_lf = z['x'].astype(np.float32)
        y_lf = resized(z['y'], info['levels']['8']['grid'], info['work_grid'])
    with np.load(folder / 'train_l9.npz') as z:
        x_hf = z['x'].astype(np.float32)
        y_hf = resized(z['y'], info['levels']['9']['grid'], info['work_grid'])
    with np.load(folder / 'test_l9.npz') as z:
        x_query = z['x'].astype(np.float32)
        assert not np.any(z['y']), 'Reserved target file is not a placeholder'
    reserved = set(input_keys(x_query))
    assert x_hf.shape == (55, 12) and x_query.shape == (17, 12)
    assert len(reserved) == 17
    assert not reserved & set(input_keys(x_lf))
    assert not reserved & set(input_keys(x_hf))
    assert np.isfinite(y_lf).all() and np.isfinite(y_hf).all()
    save_npz(ROOT / 'data/training.npz', x_lf=x_lf, y_lf=y_lf,
             x_hf=x_hf, y_hf=y_hf, x_query=x_query)
    for name in ['answers', 'predictions', 'metadata']:
        shutil.copytree(ROOT/'source'/name, ROOT/name, dirs_exist_ok=True)
    shutil.copy2(ROOT/'source/ROLES.json', ROOT/'ROLES.json')
    # The collector reads the same native HF training field to compute its mean control.
    (ROOT/'data/core/era5').mkdir(parents=True, exist_ok=True)
    shutil.copy2(folder/'train_l9.npz', ROOT/'data/core/era5/train_l9.npz')
    models = list(info['pool']) + ['uqcorr_transolver_pred', 'uqcorr_convnext_pred']
    original['datasets']['era5']['pool'] = models
    original['era5_unavailable'] = []
    original['era5_unavailable_reason'] = 'Both correctors use LF predictions at HF inputs'
    write_json(ROOT/'PLAN.json', original)
    folds = coarse_folds(x_lf, x_hf)
    tasks = [dict(fold=f['fold'], variant=variant, seed=seed,
                  tag=f'{variant}__era5__L8__F{f["fold"]}of5__s{seed}')
             for f in folds for variant in ['plain', 'hetero'] for seed in [42, 123]]
    write_json(ROOT/'COARSE_PLAN.json', dict(folds=folds, tasks=tasks))
    write_json(marker, dict(version=1, dataset='era5', models=models,
        coarse_steps=30000, corrector_steps=6000, corrector_K=6, alpha=.2,
        coarse_grid=info['work_grid'], grid=info['work_grid'], work_grid=info['work_grid'],
        lf_level=8, lf_native_grid=info['levels']['8']['grid'],
        hf_native_grid=info['levels']['9']['grid'], base_seed=42,
        n_hf_train=len(x_hf), n_lf_train=len(x_lf), n_query=len(x_query),
        calibration_count=10, evaluation_count=7, budgets=[5,10],
        corrector_split=grouped_split(x_hf), training_sha256=sha(ROOT/'data/training.npz'),
        original_plan_sha256=sha(ROOT/'source/PLAN.json'), roles_sha256=sha(ROOT/'ROLES.json'),
        matched_observed_fields_required=False,
        preprocessing='LF level8 and HF level9 bilinear resize to128x256, align_corners=False; fixed array grid',
        python=sys.version, torch=torch.__version__, numpy=np.__version__))
    write_json(ROOT/'PREPARATION_AUDIT.json', dict(passed=True,
        verified_source_files=len(manifest['files']), reserved_input_overlap_lf=0,
        reserved_input_overlap_hf=0, unique_hf_inputs=len(set(input_keys(x_hf))),
        hf_lf_input_overlap=len(set(input_keys(x_hf)) & set(input_keys(x_lf))),
        fold_rows=[dict(fold=f['fold'], held_hf=len(f['hold_hf_rows']),
                       retained_lf=len(f['train_lf_rows'])) for f in folds],
        fine_targets_used_for_coarse_training=False, original_case_roles_unchanged=True,
        reused_models=list(info['pool'][:7]), working_data_sha256=sha(ROOT/'data/training.npz')))
    print('PREPARED', len(x_lf), 'LF rows,55 HF rows,17 reserved queries,9 ensemble experts')

if __name__ == '__main__':
    main()
