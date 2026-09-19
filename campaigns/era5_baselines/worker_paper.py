"""Run frozen B6--B10 recipes on the audited ERA5 training split.

Only staged training answers and input-only query files are accessible through
the adapter. Metrics are computed later by a separate collector. B10 is an
explicit recipe alias of B9, not an additional independent fit.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import types

import numpy as np

from baseline_common import (ROOT, completed, export_prediction, load_plan,
                             protected_numpy_load, sha, verify_inputs,
                             verify_source, write_json, task_claim)

MODELS = ('nomad_mf', 'mfrnp', 'fno_coregionalization',
          'mf_fno_transfer', 'mf_fno_transfer_bar')
ALIAS_SOURCE = 'mf_fno_transfer'
ALIAS_TARGET = 'mf_fno_transfer_bar'


def alias_evidence():
    """Fail closed unless the inspected frozen transfer recipes still agree."""
    a, b = (ROOT/'vendor'/m for m in (ALIAS_SOURCE, ALIAS_TARGET))
    assert (a/'model.py').read_bytes() == (b/'model.py').read_bytes(), \
        'B9/B10 architectures differ, so prediction reuse is invalid'
    def normalized(path):
        tree = ast.parse(path.read_text())
        tree.body = [node for node in tree.body if not (
            isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == 'REPO_ROOT'
                for target in node.targets))]
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value == ALIAS_TARGET:
                node.value = ALIAS_SOURCE
        return ast.dump(tree, include_attributes=False)
    assert normalized(a/'smoke_eval.py') == normalized(b/'smoke_eval.py'), \
        'B9/B10 recipes differ, so prediction reuse is invalid'
    return dict(alias_of=ALIAS_SOURCE, reused_from=ALIAS_SOURCE, independent_training=False,
        rationale='Frozen architectures are byte identical; executable recipe ASTs '
                  'are identical after removing the import-root assignment and '
                  'normalizing only the output model label.',
        architecture_sha256=sha(a/'model.py'),
        source_recipe_sha256=sha(a/'smoke_eval.py'),
        alias_recipe_sha256=sha(b/'smoke_eval.py'))


def export_alias(smoke=False):
    evidence = alias_evidence()
    assert completed(ALIAS_SOURCE, smoke=smoke), \
        'B10 has no distinct training run. Complete B9 first.'
    if completed(ALIAS_TARGET, smoke=smoke):
        return
    base = ROOT/'smoke' if smoke else ROOT
    source = base/'predictions'/f'{ALIAS_SOURCE}__era5.npz'
    source_metadata = base/'metadata'/f'{ALIAS_SOURCE}__era5.json'
    with np.load(source) as z:
        pred, theta, grid = z['pred'], z['theta'], z['work_grid'].tolist()
    metadata = json.loads(source_metadata.read_text())
    metadata.update(evidence)
    metadata.update(source_prediction_sha256=sha(source),
                    source_metadata_sha256=sha(source_metadata),
                    additional_training_seconds=0.)
    metadata.pop('prediction_sha256', None)
    export_prediction(ALIAS_TARGET, pred, theta, grid, metadata, smoke=smoke)
    print('ALIASED', ALIAS_TARGET, 'from', ALIAS_SOURCE, flush=True)


@contextmanager
def import_frozen(model_name, identity):
    """Isolate vendor packages so CPU fixtures can exercise multiple recipes."""
    import torch
    from paper_resume import (adapt_coregionalization, adapt_mfrnp, atomic_save,
                              capture_rng, restore_rng, resumable_mf_loader)
    assert model_name in MODELS and model_name != ALIAS_TARGET
    source = ROOT/'vendor'/model_name/'smoke_eval.py'
    old_path = sys.path.copy()
    packages = ('model', 'lib', 'torchvision', '_common')
    def isolated(name):
        return any(name == p or name.startswith(p+'.') for p in packages)
    saved = {name: mod for name, mod in list(sys.modules.items()) if isolated(name)}
    for name in saved:
        del sys.modules[name]
    sys.path.insert(0, str(ROOT/'vendor'))
    sys.path.insert(0, str(ROOT))
    name = '_era5_baseline_' + model_name
    spec = importlib.util.spec_from_file_location(name, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    module.__dict__.update(_RUN_IDENTITY=identity, atomic_save=atomic_save,
                           capture_rng=capture_rng, restore_rng=restore_rng)
    code = source.read_text()
    if model_name == 'mfrnp':
        # The upstream directories are namespace packages. Explicit paths keep
        # an unrelated model.py elsewhere on sys.path from shadowing them.
        for package in ('model', 'lib'):
            namespace = types.ModuleType(package)
            namespace.__path__ = [str(source.parent/'upstream'/package)]
            sys.modules[package] = namespace
        code = adapt_mfrnp(code)
    else:
        model_spec = importlib.util.spec_from_file_location('model', source.parent/'model.py')
        model_module = importlib.util.module_from_spec(model_spec)
        sys.modules['model'] = model_module
        model_spec.loader.exec_module(model_module)
        if model_name == 'fno_coregionalization':
            code = adapt_coregionalization(code)
    try:
        exec(compile(code, str(source), 'exec'), module.__dict__)
        if model_name == 'mfrnp':
            module.MFLoader = resumable_mf_loader(module.MFLoader)
        yield module
    finally:
        for key in list(sys.modules):
            if isolated(key):
                del sys.modules[key]
        sys.modules.update(saved)
        sys.modules.pop(name, None)
        sys.path[:] = old_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True, choices=MODELS)
    ap.add_argument('--smoke', action='store_true')
    args = ap.parse_args()
    claim_model = ALIAS_SOURCE if args.model == ALIAS_TARGET else args.model
    with task_claim(claim_model, smoke=args.smoke):
        run(args)


def run(args):
    verify_source()
    verify_inputs()
    if args.model == ALIAS_TARGET:
        export_alias(args.smoke)
        return
    if completed(args.model, smoke=args.smoke):
        print('Already complete', args.model, flush=True)
        if args.model == ALIAS_SOURCE:
            export_alias(args.smoke)
        return
    plan = load_plan()
    info = plan['datasets']['era5']
    assert info['n_base_hf_train'] == 55 and info['work_grid'] == [128, 256]
    assert plan['base_epochs'] == 2500
    base = ROOT/'smoke' if args.smoke else ROOT
    data_dir = ROOT/'data'/'core'/'era5'
    epochs = (4 if args.model == 'fno_coregionalization' else 1) if args.smoke else 2500
    identity = dict(model=args.model, dataset='era5', seed=42, epochs=epochs,
                    plan_sha256=sha(ROOT/'PLAN.json'),
                    inputs_sha256=sha(ROOT/'INPUT_MANIFEST.json'),
                    source_sha256=sha(ROOT/'SOURCE.json'), smoke=args.smoke)
    ckpt = base/'checkpoints'/f'{args.model}__era5'
    ckpt.mkdir(parents=True, exist_ok=True)
    identity_file = ckpt/'IDENTITY.json'
    if identity_file.exists():
        assert json.loads(identity_file.read_text()) == identity, 'Checkpoint identity mismatch'
    else:
        write_json(identity_file, identity)
    os.environ['DDE_BACKEND'] = 'pytorch'
    os.environ.pop('SAVE_PRED_DIR', None)
    import torch
    torch.set_num_threads(int(os.environ.get('OMP_NUM_THREADS', '4')))
    assert args.smoke or torch.cuda.is_available(), 'Production training requires a GPU'
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision('highest')
    import data_adapters
    assert Path(data_adapters.__file__).resolve().is_relative_to(ROOT.resolve())
    torch.manual_seed(42)
    np.random.seed(42)
    start = time.time()
    captured = {}
    with protected_numpy_load() as loads:
        with np.load(data_dir/f"test_l{info['hf_level']}.npz") as z:
            theta = z['x'].astype(np.float32)
        assert len(theta) == 17
        with import_frozen(args.model, identity) as mod:
            original_adapter = data_adapters.load_mf_dataset
            def guarded_adapter(path, split='train', *a, **kw):
                assert Path(path).resolve() == data_dir.resolve()
                if split == 'ood':
                    raise FileNotFoundError('No OOD split belongs to this frozen ERA5 comparison')
                assert split in ('train', 'test')
                data = original_adapter(path, split, *a, **kw)
                if split == 'test':
                    for f in data['fids']:
                        assert np.array_equal(data['cond_by_fid'][f], theta)
                        assert not np.any(data['field_by_fid'][f]), \
                            'A query file contains nonzero target answers'
                return data
            mod.load_mf_dataset = guarded_adapter
            def capture(**kwargs):
                assert not captured, 'More than one final prediction export'
                assert np.count_nonzero(kwargs['target']) == 0, 'Finalizer received real held-out answers'
                captured.update(pred=np.asarray(kwargs['pred'], np.float32),
                    grid=list(kwargs['work_grid']), train_seconds=float(kwargs['train_seconds']),
                    eval_seconds=float(kwargs['eval_seconds']), n_params=int(kwargs['n_params']),
                    extra=kwargs.get('extra', {}))
                return {'captured': True}
            mod.finalize_and_write = capture
            if args.model in ('nomad_mf', 'mf_fno_transfer'):
                from stage_train import StageTrainer
                trainer = StageTrainer(ckpt/'stages', identity)
                if args.model == 'nomad_mf':
                    mod.train_loop = trainer
                else:
                    mod._train = trainer
            run_args = argparse.Namespace(dataset_dir=str(data_dir), dataset_name='era5',
                seed=42, epochs=epochs, ckpt_dir=str(ckpt),
                out=str(base/'unused.json'), decoder='nonlinear')
            if args.model in ('nomad_mf', 'mf_fno_transfer'):
                mod.run(run_args, Path(run_args.out))
            else:
                mod.run(run_args)
    assert captured, 'Model did not export its predictions'
    assert captured['pred'].shape == (17, 128*256)
    assert captured['grid'] == [128, 256] and np.isfinite(captured['pred']).all()
    if args.model in ('nomad_mf', 'mf_fno_transfer'):
        stage_records = [json.loads(path.read_text()) for path in (ckpt/'stages').glob('*.json')]
        assert len(stage_records) == 2 and all(row['epoch'] == epochs for row in stage_records)
        captured['train_seconds'] = sum(row['seconds'] for row in stage_records)
    metadata = dict(identity, elapsed_seconds=time.time()-start,
                    train_seconds=captured['train_seconds'], eval_seconds=captured['eval_seconds'],
                    n_params=captured['n_params'], n_base_hf_train=55,
                    device=torch.cuda.get_device_name() if torch.cuda.is_available() else 'cpu',
                    raw_test_answers_loaded=False, calibration_answers_loaded=False,
                    loaded_data_paths=sorted(set(loads)),
                    matmul_tf32=False, cudnn_tf32=False,
                    independent_training=True, recipe_source=str(Path('vendor')/args.model/'smoke_eval.py'),
                    architecture_and_hyperparameters='Frozen release recipe, unchanged',
                    adaptations=['Audited 55 HF training rows and purged LF pool',
                        'Input-only 17-row query split and intercepted metrics finalizer',
                        'Atomic resumable checkpoints with optimizer and RNG state'],
                    extra=captured['extra'])
    if args.model == 'mfrnp':
        metadata['adaptations'].append('Native loader permutations additionally checkpointed for exact resume')
    export_prediction(args.model, captured['pred'], theta, captured['grid'], metadata,
                      smoke=args.smoke)
    print('EXPORTED', args.model, 'n=17', flush=True)
    if args.model == ALIAS_SOURCE:
        export_alias(args.smoke)


if __name__ == '__main__':
    main()
