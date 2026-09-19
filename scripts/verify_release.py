#!/usr/bin/env python3
"""Verify the review ZIP, or the complete release after importing companion data."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--full', action='store_true', help='Also require every companion data file')
    p.add_argument('--quick', action='store_true', help='Check sizes instead of full SHA256 hashes')
    args = p.parse_args()
    bundle = json.loads((ROOT / 'release_manifest.json').read_text())
    companion = json.loads((ROOT / 'data_manifest.json').read_text())
    records = bundle['files'] + (companion['files'] if args.full else [])
    errors = []
    for record in records:
        path = ROOT / record['path']
        if not path.is_file():
            errors.append('Missing: ' + record['path'])
        elif path.stat().st_size != record['bytes']:
            errors.append('Size: ' + record['path'])
        elif not args.quick and digest(path) != record['sha256']:
            errors.append('SHA256: ' + record['path'])
    datasets = json.loads((ROOT / 'configs/datasets.json').read_text())
    models = json.loads((ROOT / 'configs/models.json').read_text())
    if len(datasets) != 22 or not all(f'M{i}' in models for i in range(1, 10)):
        errors.append('Dataset or surrogate roster mismatch')
    if not all(f'B{i}' in models for i in range(1, 14)):
        errors.append('Baseline roster mismatch')
    if args.full:
        for key, info in datasets.items():
            folder = ROOT / info['path']
            train = sorted(folder.glob('train_l*.npz'))
            test = sorted(folder.glob('test_l*.npz'))
            if not train or len(train) != len(test):
                errors.append('Missing dataset levels: ' + key)
    print(json.dumps({'passed': not errors, 'files_checked': len(records),
                      'scope': 'complete release' if args.full else 'review ZIP',
                      'mode': 'size' if args.quick else 'SHA256',
                      'datasets': len(datasets), 'surrogates': 9,
                      'baseline_entries_including_controls': 13,
                      'companion_files': len(companion['files']), 'errors': errors}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
