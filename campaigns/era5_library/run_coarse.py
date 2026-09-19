"""ERA5 LF-only coarse fits and four-member, input-disjoint OOF assembly.

No HF target is read here. The observed HF inputs identify the exclusion folds;
the only supervised fields are y_lf. Query fields are never scored by this code.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import sys
import time

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

from era5_common import ROOT, sha, write_json, save_npz, verify_source


def array_sha(value):
    a = np.ascontiguousarray(value)
    h = hashlib.sha256(str((a.shape, a.dtype.str)).encode())
    h.update(a.tobytes())
    return h.hexdigest()


def input_keys(x):
    x = np.asarray(x, np.float32).copy()
    x[x == 0] = 0
    return [np.ascontiguousarray(row).tobytes() for row in x]


@contextmanager
def restricted_load(allowed):
    """Allow only explicitly named NPZs, including during imported code calls."""
    original = np.load
    allowed = {Path(p).resolve() for p in allowed}

    def guarded(path, *args, **kwargs):
        if not isinstance(path, (str, os.PathLike)):
            raise RuntimeError('Untracked NumPy input stream')
        resolved = Path(path).resolve()
        if resolved not in allowed:
            raise RuntimeError(f'Unauthorized coarse-worker data access: {resolved}')
        return original(path, *args, **kwargs)

    np.load = guarded
    try:
        yield
    finally:
        np.load = original


def training_inputs(include_targets=True):
    # NPZ access is lazy: deliberately never index y_hf or any query target.
    with np.load(ROOT / 'data/training.npz', allow_pickle=False) as z:
        names = ['x_lf', 'x_hf', 'x_query'] + (['y_lf'] if include_targets else [])
        data = {name: z[name].astype(np.float32) for name in names}
    for name, value in data.items():
        assert np.isfinite(value).all(), f'Nonfinite {name}'
    assert data['x_lf'].ndim == data['x_hf'].ndim == data['x_query'].ndim == 2
    assert data['x_lf'].shape[1] == data['x_hf'].shape[1] == data['x_query'].shape[1]
    if include_targets:
        assert len(data['y_lf']) == len(data['x_lf'])
    return data


def checked_plan(plan, data):
    """Reconstruct identity masks rather than trusting row lists alone."""
    folds = {int(f['fold']): f for f in plan['folds']}
    assert len(plan['folds']) == len(folds) == 5 and set(folds) == set(range(5))
    lf_keys, hf_keys, query_keys = [input_keys(data[n]) for n in ['x_lf', 'x_hf', 'x_query']]
    assert len(set(query_keys)) == len(query_keys), 'Query input identities must be unique'
    assert not set(query_keys) & (set(lf_keys) | set(hf_keys)), 'Reserved query input in training'
    coverage = np.zeros(len(hf_keys), np.int64)
    identity_folds = {}
    for number, fold in folds.items():
        hold = np.asarray(fold['hold_hf_rows'], dtype=np.int64)
        train = np.asarray(fold['train_lf_rows'], dtype=np.int64)
        assert len(hold) and len(train)
        assert len(set(hold.tolist())) == len(hold)
        assert np.all((hold >= 0) & (hold < len(hf_keys)))
        for row in hold:
            key = hf_keys[row]
            assert identity_folds.setdefault(key, number) == number, 'Duplicate HF identity split across folds'
        assert len(set(train.tolist())) == len(train)
        assert np.all((train >= 0) & (train < len(lf_keys)))
        excluded = {hf_keys[i] for i in hold}
        expected = [i for i, key in enumerate(lf_keys) if key not in excluded]
        assert sorted(train.tolist()) == expected, f'Incorrect identity exclusion in fold {number}'
        coverage[hold] += 1
    assert np.all(coverage == 1), 'Each HF input must belong to exactly one fold'
    tasks = plan['tasks']
    expected = {(f, v, s) for f in range(5) for v in ['plain', 'hetero'] for s in [42, 123]}
    actual = [(int(t['fold']), t['variant'], int(t['seed'])) for t in tasks]
    assert len(tasks) == 20 and set(actual) == expected
    tags = [t['tag'] for t in tasks]
    assert len(set(tags)) == 20 and all(t and Path(t).name == t and t not in ['.', '..'] for t in tags)
    return folds


def recipe():
    folder = ROOT / 'vendor/mf_fno_transfer_film'
    spec = importlib.util.spec_from_file_location('era5_coarse_fno', folder / 'model.py')
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    # smoke_eval imports its backbone by this generic name. Use the frozen copy.
    previous = sys.modules.get('model')
    sys.modules['model'] = model
    try:
        spec = importlib.util.spec_from_file_location('era5_coarse_recipe', folder / 'smoke_eval.py')
        se = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(se)
    finally:
        if previous is None:
            sys.modules.pop('model', None)
        else:
            sys.modules['model'] = previous
    return model.FNO2d, dict(se.SMOKE), se._modes


class HeteroFNO(nn.Module):
    """Same two-channel head and variance clamp as frozen diag_coarse.py."""
    def __init__(self, base):
        super().__init__()
        self.base = base
        head = nn.Conv2d(base.proj[0].out_channels, 2, 1)
        with torch.no_grad():
            head.weight[0].copy_(base.proj[-1].weight[0])
            head.bias[0].copy_(base.proj[-1].bias[0])
            head.weight[1].zero_()
            head.bias[1].fill_(-4.)
        base.proj[-1] = head

    def forward(self, x):
        b = self.base
        z = b.lift(b.coord_grid.expand(len(x), 2, *b.grid))
        for block in b.blocks:
            z = block(z, x)
        out = b.proj(z)
        return out[:, 0], out[:, 1].clamp(-14., 6.)


def beta_nll(mu, logvar, y, beta=.5):
    var = logvar.exp()
    nll = .5 * ((y - mu).square() / var + logvar)
    weight = var.detach().pow(beta) if beta > 0 else 1.
    return (weight * nll).mean()


def atomic_checkpoint(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.tmp.{os.getpid()}')
    with temp.open('wb') as stream:
        torch.save(state, stream)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def train_loop(model, x, y, path, key, settings, epochs, updates, device,
               hetero=False, checkpoint_every=250):
    """Atomic resumption includes a partially consumed epoch permutation."""
    opt = torch.optim.AdamW(model.parameters(), lr=settings['lr_pretrain'],
                            weight_decay=settings['weight_decay'])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs, eta_min=1e-6)
    generator = torch.Generator().manual_seed(key['seed'])
    epoch = step = offset = 0
    permutation = None
    spent = 0.
    last_loss = None
    if path.exists():
        state = torch.load(path, map_location=device, weights_only=False)
        assert state['key'] == key, 'Checkpoint/data/recipe identity mismatch'
        model.load_state_dict(state['model'])
        opt.load_state_dict(state['optimizer'])
        scheduler.load_state_dict(state['scheduler'])
        generator.set_state(state['generator'].cpu())
        torch.set_rng_state(state['torch_rng'].cpu())
        if torch.cuda.is_available():
            assert len(state['cuda_rng']) == torch.cuda.device_count()
            torch.cuda.set_rng_state_all([s.cpu() for s in state['cuda_rng']])
        np.random.set_state(state['numpy_rng'])
        random.setstate(state['python_rng'])
        epoch, step, offset = state['epoch'], state['step'], state['offset']
        permutation = state['permutation']
        if permutation is not None:
            permutation = permutation.cpu()
        spent, last_loss = state['seconds'], state['last_loss']
        print(f'RESUME {key["tag"]} step {step}/{updates}, epoch {epoch}, offset {offset}', flush=True)
        del state
    assert 0 <= step <= updates and 0 <= epoch <= epochs
    batch = min(int(settings['batch_size']), len(x))
    start = last_save = time.time()
    model.train()
    while step < updates:
        assert epoch < epochs
        if permutation is None:
            permutation = torch.randperm(len(x), generator=generator)
            offset = 0
        idx = permutation[offset:offset + batch]
        assert len(idx)
        xb, yb = x[idx].to(device), y[idx].to(device)
        opt.zero_grad(set_to_none=True)
        output = model(xb)
        loss = beta_nll(*output, yb) if hetero else F.mse_loss(output, yb)
        if not torch.isfinite(loss):
            raise RuntimeError(f'Nonfinite coarse loss at step {step}')
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), settings['grad_clip'])
        opt.step()
        step += 1
        offset += len(idx)
        last_loss = float(loss.detach())
        if offset == len(x):
            scheduler.step()
            epoch += 1
            offset = 0
            permutation = None
        if step % checkpoint_every == 0 or time.time() - last_save >= 300 or step == updates:
            atomic_checkpoint(path, dict(key=key, model=model.state_dict(), optimizer=opt.state_dict(),
                scheduler=scheduler.state_dict(), generator=generator.get_state(),
                torch_rng=torch.get_rng_state(), cuda_rng=torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [],
                numpy_rng=np.random.get_state(), python_rng=random.getstate(), epoch=epoch, step=step,
                offset=offset, permutation=permutation, seconds=spent + time.time() - start, last_loss=last_loss))
            write_json(path.with_suffix('.json'), dict(tag=key['tag'], step=step, total_updates=updates,
                epoch=epoch, epochs=epochs, offset=offset, loss=last_loss, seconds=spent + time.time() - start))
            print(f'{key["tag"]} step {step}/{updates}, epoch {epoch}/{epochs}, loss {last_loss:.7g}', flush=True)
            last_save = time.time()
    return dict(optimizer_steps=step, completed_epochs=epoch, last_scaled_loss=last_loss,
                train_seconds=spent + time.time() - start)


@torch.no_grad()
def predict(model, x, scale, device, hetero, batch=64):
    model.eval()
    out = []
    for start in range(0, len(x), batch):
        pred = model(x[start:start + batch].to(device))
        if hetero:
            pred = pred[0]
        out.append(pred.cpu() * scale)
    result = torch.cat(out).numpy().astype(np.float32)
    assert np.isfinite(result).all()
    return result


def base_identity(config, plan, smoke):
    return dict(experiment_sha256=sha(ROOT / 'EXPERIMENT.json'),
                coarse_plan_sha256=sha(ROOT / 'COARSE_PLAN.json'),
                training_sha256=sha(ROOT / 'data/training.npz'),
                source_manifest_sha256=sha(ROOT / 'SOURCE.json'), smoke=bool(smoke))


def run_task(index, smoke, config, plan, data, folds, identity, out):
    assert 0 <= index < len(plan['tasks'])
    task = plan['tasks'][index]
    fold = folds[int(task['fold'])]
    train = np.asarray(fold['train_lf_rows'], np.int64)
    hold = np.asarray(fold['hold_hf_rows'], np.int64)
    grid = tuple(config['coarse_grid'])
    assert data['y_lf'].shape[1:] == grid
    prediction_path = out / 'preds' / (task['tag'] + '.npz')
    metadata_path = out / 'raw' / (task['tag'] + '.json')
    if prediction_path.exists() and metadata_path.exists():
        previous = json.loads(metadata_path.read_text())
        assert previous['identity'] == identity and previous['task'] == task
        assert previous['prediction_sha256'] == sha(prediction_path) and previous['complete']
        print('ALREADY COMPLETE', task['tag'], flush=True)
        return
    assert torch.cuda.is_available(), 'A CUDA GPU is required for coarse training'
    device = torch.device('cuda')
    random.seed(task['seed'])
    np.random.seed(task['seed'])
    torch.manual_seed(task['seed'])
    torch.cuda.manual_seed_all(task['seed'])
    backbone, p, modes = recipe()
    mean = data['x_lf'][train].mean(0)
    std = np.maximum(data['x_lf'][train].std(0), 1e-6)
    normalize = lambda x: torch.from_numpy((x - mean) / std).float()
    xt, xh, xq = normalize(data['x_lf'][train]), normalize(data['x_hf'][hold]), normalize(data['x_query'])
    y = torch.from_numpy(data['y_lf'][train])
    scale = max(float(y.abs().max()), 1e-8)
    y = y / scale
    mh, mw = modes(grid, p['modes_cap'])
    model = backbone(data['x_lf'].shape[1], hidden_channels=p['hidden_channels'],
                     n_blocks=p['n_blocks'], modes_h=mh, modes_w=mw, grid=grid)
    hetero = task['variant'] == 'hetero'
    if hetero:
        model = HeteroFNO(model)
    model = model.to(device)
    batches = math.ceil(len(train) / min(p['batch_size'], len(train)))
    requested = 8 if smoke else int(config['coarse_steps'])
    epochs = math.ceil(requested / batches)
    updates = requested if smoke else epochs * batches
    masks = dict(train_lf_rows_sha256=array_sha(train), hold_hf_rows_sha256=array_sha(hold),
                 theta_hold_sha256=array_sha(data['x_hf'][hold]), theta_query_sha256=array_sha(data['x_query']))
    key = dict(identity=identity, tag=task['tag'], seed=task['seed'], variant=task['variant'],
               fold=task['fold'], grid=list(grid), settings=p, scale=scale, xmean=mean.tolist(), xstd=std.tolist(),
               epochs=epochs, optimizer_steps=updates, requested_steps=requested, masks=masks, hetero_beta=.5)
    result = train_loop(model, xt, y, out / 'ck' / task['tag'] / 'last.pt', key, p,
                        epochs, updates, device, hetero)
    mu_hold = predict(model, xh, scale, device, hetero)
    mu_query = predict(model, xq, scale, device, hetero)
    save_npz(prediction_path, hold_rows=hold, mu_hold=mu_hold, mu_query=mu_query,
             theta_hold=data['x_hf'][hold], theta_query=data['x_query'])
    write_json(metadata_path, dict(complete=True, identity=identity, task=task, masks=masks,
        prediction_sha256=sha(prediction_path), n_lf_training=len(train), n_hf_hold=len(hold),
        n_query=len(xq), grid=list(grid), settings=p, scaler=scale, xmean=mean.tolist(), xstd=std.tolist(),
        requested_steps=requested, planned_epochs=epochs, beta=.5 if hetero else None,
        target_keys_read=['y_lf'], query_targets_read=False, hf_targets_read=False,
        torch_version=torch.__version__, numpy_version=np.__version__, gpu=torch.cuda.get_device_name(),
        matmul_tf32=False, cudnn_tf32=False, **result))
    print('COMPLETE', task['tag'], flush=True)


def assemble(config, plan, data, folds, identity, out):
    grid = tuple(config['coarse_grid'])
    mean = np.zeros((len(data['x_hf']), *grid), np.float64)
    count = np.zeros(len(mean), np.int64)
    queries, sources = [], {}
    for task in plan['tasks']:
        path = out / 'preds' / (task['tag'] + '.npz')
        metadata_path = out / 'raw' / (task['tag'] + '.json')
        record = json.loads(metadata_path.read_text())
        assert record['complete'] and record['identity'] == identity and record['task'] == task
        assert not record['query_targets_read'] and not record['hf_targets_read']
        assert record['prediction_sha256'] == sha(path)
        expected = np.asarray(folds[int(task['fold'])]['hold_hf_rows'], np.int64)
        with np.load(path, allow_pickle=False) as z:
            rows, mu, query = z['hold_rows'], z['mu_hold'], z['mu_query']
            np.testing.assert_array_equal(rows, expected)
            np.testing.assert_array_equal(z['theta_hold'], data['x_hf'][rows])
            np.testing.assert_array_equal(z['theta_query'], data['x_query'])
            assert mu.shape == (len(rows), *grid) and query.shape == (len(data['x_query']), *grid)
            assert np.isfinite(mu).all() and np.isfinite(query).all()
            assert record['masks']['hold_hf_rows_sha256'] == array_sha(rows)
            assert record['masks']['theta_hold_sha256'] == array_sha(z['theta_hold'])
            assert record['masks']['theta_query_sha256'] == array_sha(z['theta_query'])
            train = np.asarray(folds[int(task['fold'])]['train_lf_rows'], np.int64)
            assert record['masks']['train_lf_rows_sha256'] == array_sha(train)
            mean[rows] += mu.astype(np.float64)
            count[rows] += 1
            if int(task['fold']) == 0:
                queries.append(query.astype(np.float64))
        sources[task['tag']] = dict(prediction_sha256=sha(path), metadata_sha256=sha(metadata_path))
    assert np.all(count == 4) and len(queries) == 4
    dest = out / 'oof.npz'
    save_npz(dest, mean_train=(mean / count[:, None, None]).astype(np.float32),
             mean_query=np.mean(np.stack(queries), axis=0).astype(np.float32),
             n_members_train=count, members_query=np.int64(4), x_hf=data['x_hf'], x_query=data['x_query'])
    write_json(out / 'oof_audit.json', dict(passed=True, identity=identity, members_train=4,
        members_query=4, query_fold=0, n_hf=len(mean), n_query=len(data['x_query']),
        source_predictions=sources, oof_sha256=sha(dest), query_targets_read=False, hf_targets_read=False))
    print('ASSEMBLED: four members per HF training input and four fold-zero query members', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--task', type=int)
    action.add_argument('--assemble', action='store_true')
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    verify_source()
    config = json.loads((ROOT / 'EXPERIMENT.json').read_text())
    assert sha(ROOT / 'data/training.npz') == config['training_sha256'], 'Training data changed after preparation'
    plan = json.loads((ROOT / 'COARSE_PLAN.json').read_text())
    out = (ROOT / 'smoke' if args.smoke else ROOT) / 'coarse'
    allowed = [ROOT / 'data/training.npz']
    if args.assemble:
        allowed += [out / 'preds' / (t['tag'] + '.npz') for t in plan['tasks']]
    torch.set_num_threads(int(os.environ.get('OMP_NUM_THREADS', '4')))
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision('highest')
    with restricted_load(allowed):
        data = training_inputs(include_targets=not args.assemble)
        folds = checked_plan(plan, data)
        identity = base_identity(config, plan, args.smoke)
        if args.assemble:
            assemble(config, plan, data, folds, identity, out)
        else:
            run_task(args.task, args.smoke, config, plan, data, folds, identity, out)


if __name__ == '__main__':
    main()
