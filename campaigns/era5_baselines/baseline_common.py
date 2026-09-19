"""Frozen inputs, exclusive task claims, and prediction-only training exports."""
from contextlib import contextmanager
from pathlib import Path
import fcntl
import hashlib
import json
import os
import numpy as np

ROOT = Path(__file__).resolve().parent


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.tmp.{os.getpid()}')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    os.replace(temp, path)


def save_npz(path, **arrays):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.tmp.{os.getpid()}')
    with temp.open('wb') as stream:
        np.savez_compressed(stream, **arrays)
    os.replace(temp, path)


def load_plan():
    return json.loads((ROOT / 'PLAN.json').read_text())


def verify_source():
    manifest = json.loads((ROOT / 'SOURCE.json').read_text())
    for name, digest in manifest.items():
        assert sha(ROOT / name) == digest, f'Source changed: {name}'
    return manifest


def verify_inputs():
    manifest = json.loads((ROOT / 'INPUT_MANIFEST.json').read_text())
    for name, entry in manifest['files'].items():
        # Sealed answers are verified only by the independent collector.
        if entry['role'] == 'answer':
            continue
        assert sha(ROOT / name) == entry['sha256'], f'Input changed: {name}'
    audit = json.loads((ROOT / 'INPUT_AUDIT.json').read_text())
    assert audit['passed'] and audit['input_manifest_sha256'] == sha(ROOT / 'INPUT_MANIFEST.json')
    assert audit['plan_sha256'] == sha(ROOT / 'PLAN.json')
    return audit


@contextmanager
def protected_numpy_load():
    manifest = json.loads((ROOT / 'INPUT_MANIFEST.json').read_text())
    allowed = {(ROOT / name).resolve() for name, entry in manifest['files'].items()
               if entry['role'] in ('train', 'query')}
    original = np.load
    loads = []

    def guarded(file, *args, **kwargs):
        if not isinstance(file, (str, os.PathLike)):
            raise RuntimeError('Training cannot load an untracked NumPy stream')
        path = Path(file).resolve()
        if path not in allowed:
            raise RuntimeError(f'Training attempted to read an unapproved array: {path}')
        loads.append(str(path))
        kwargs['allow_pickle'] = False
        return original(file, *args, **kwargs)

    np.load = guarded
    try:
        yield loads
    finally:
        np.load = original


def identity():
    return dict(source_manifest_sha256=sha(ROOT / 'SOURCE.json'),
                plan_sha256=sha(ROOT / 'PLAN.json'),
                input_manifest_sha256=sha(ROOT / 'INPUT_MANIFEST.json'))


def output_root(smoke=False):
    return ROOT / 'smoke' if smoke else ROOT


def completed(model, smoke=False):
    folder = output_root(smoke)
    pred = folder / 'predictions' / f'{model}__era5.npz'
    meta = folder / 'metadata' / f'{model}__era5.json'
    if not (pred.exists() and meta.exists()):
        return False
    doc = json.loads(meta.read_text())
    assert doc['prediction_sha256'] == sha(pred), f'Prediction changed: {model}'
    assert all(doc[k] == v for k, v in identity().items()), f'Output identity changed: {model}'
    assert doc['smoke'] is bool(smoke) and doc['scientific_result'] is (not smoke)
    return True


def export_prediction(model, pred, theta, grid, metadata, smoke=False):
    info = load_plan()['datasets']['era5']
    pred = np.asarray(pred, np.float32).reshape(len(theta), -1)
    theta = np.asarray(theta, np.float32)
    grid = np.asarray(grid, np.int64)
    assert list(grid) == info['work_grid'] == [128, 256]
    assert pred.shape == (17, 32768) and theta.shape == (17, 12)
    assert np.isfinite(pred).all() and np.isfinite(theta).all()
    with np.load(ROOT / 'data/core/era5/test_l9.npz', allow_pickle=False) as data:
        assert np.array_equal(theta, data['x'])
    folder = output_root(smoke)
    path = folder / 'predictions' / f'{model}__era5.npz'
    save_npz(path, pred=pred, theta=theta, work_grid=grid)
    doc = dict(metadata, **identity())
    doc.update(model=model, dataset='era5', prediction_sha256=sha(path),
               smoke=bool(smoke), scientific_result=not smoke,
               n_base_hf_train=55, n_calibration=10, n_evaluation=7,
               n_query=17, work_grid=grid.tolist(), seed=42,
               evaluation_answers_used_for_training=False)
    write_json(folder / 'metadata' / f'{model}__era5.json', doc)
    return doc


@contextmanager
def task_claim(model, smoke=False):
    folder = output_root(smoke) / 'claims'
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / f'{model}.lock').open('a+') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(f'Task already running: {model}') from error
        stream.seek(0)
        stream.truncate()
        stream.write(json.dumps(dict(pid=os.getpid(), job=os.environ.get('SLURM_JOB_ID'))))
        stream.flush()
        yield
