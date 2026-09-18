"""Shared paths, atomic artifacts, and source validation for ERA5 correctors."""
from pathlib import Path
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
    temporary = path.with_name(path.name + f'.tmp.{os.getpid()}')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    os.replace(temporary, path)

def save_npz(path, **arrays):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f'.tmp.{os.getpid()}')
    with temporary.open('wb') as stream:
        np.savez_compressed(stream, **arrays)
    os.replace(temporary, path)

def input_keys(x):
    a = np.asarray(x, np.float32).copy()
    a[a == 0] = 0
    return [np.ascontiguousarray(row).tobytes() for row in a]

def verify_source():
    manifest = json.loads((ROOT / 'SOURCE.json').read_text())
    for name, digest in manifest.items():
        assert sha(ROOT / name) == digest, f'Source changed: {name}'
    return manifest

def load_training(keys=None):
    with np.load(ROOT / 'data/training.npz', allow_pickle=False) as data:
        names = data.files if keys is None else keys
        return {name: data[name].copy() for name in names}
