#!/usr/bin/env python3
"""Fit three ensembles on five Heat I cases and evaluate five different cases.

CPU only. This demonstration uses saved predictions, not the reporting partition,
and does not retrain any of the nine surrogates.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RULES = {'selected': 'Selected model', 'inverse': 'Inverse error mixture', 'fitted': 'Fitted mixture'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New output directory, defaults to a timestamped run')
    args = parser.parse_args()
    out = args.output or ROOT / 'outputs' / ('ensemble_' + datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f'))
    out = out.resolve()
    if out.exists():
        parser.error(f'Output already exists: {out}. Choose a new directory.')
    source = ROOT / 'examples/heat_demo.npz'
    manifest = json.loads(source.with_suffix('.json').read_text())
    if hashlib.sha256(source.read_bytes()).hexdigest() != manifest['sha256']:
        parser.error('Example data checksum differs from examples/heat_demo.json')
    with np.load(source, allow_pickle=False) as z:
        pred, target, names = z['predictions'], z['targets'], z['model_names']
    out.mkdir(parents=True)
    np.savez_compressed(out / 'fitting.npz', predictions=pred[:5], targets=target[:5], model_names=names)
    # Prediction never receives query targets. They are used only below for scoring.
    np.savez_compressed(out / 'queries.npz', predictions=pred[5:], model_names=names)
    metrics = {}
    for rule in RULES:
        subprocess.run([sys.executable, str(ROOT / 'ensemble/fit_fields.py'), 'fit', '--fitting',
                        str(out / 'fitting.npz'), '--rule', rule, '--output', str(out / f'{rule}_weights.json')],
                       check=True, capture_output=True, text=True)
        subprocess.run([sys.executable, str(ROOT / 'ensemble/fit_fields.py'), 'predict', '--predictions',
                        str(out / 'queries.npz'), '--weights', str(out / f'{rule}_weights.json'),
                        '--output', str(out / f'{rule}_prediction.npz')], check=True, capture_output=True, text=True)
        with np.load(out / f'{rule}_prediction.npz') as z:
            y = z['predictions']
        error = np.linalg.norm((y - target[5:]).reshape(5, -1), axis=1)
        error /= np.maximum(np.linalg.norm(target[5:].reshape(5, -1), axis=1), 1e-8)
        metrics[rule] = dict(mean_relative_l2=float(error.mean()), per_case=error.tolist())
    (out / 'metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')
    print('Heat I demo: 9 saved surrogates, 5 fitting cases, 5 different query cases.\n')
    for rule, label in RULES.items():
        print(f'{label:23s}  relative L2 = {100 * metrics[rule]["mean_relative_l2"]:.6f}%')
    print(f'\nWeights, predictions and metrics: {out}')
    print('This usage example is separate from the benchmark comparison.')


if __name__ == '__main__':
    main()
