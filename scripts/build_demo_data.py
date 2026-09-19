#!/usr/bin/env python3
"""Extract ten unchanged Heat I cases for the small, Git-native CPU example."""
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    models = json.loads((ROOT / 'configs/models.json').read_text())
    names = [models[f'M{i}']['archive_id'] for i in range(1, 10)]
    fields, sources = [], []
    target = theta = None
    for index, name in enumerate(names):
        path = ROOT / 'results/predictions/historical' / f'{name}__heat_generated.npz'
        with np.load(path, allow_pickle=False) as z:
            key = 'pred' if index < 7 else 'pred_test'
            fields.append(z[key][:10].reshape(10, 64, 64))
            if index < 7:
                if target is None:
                    target = z['target'][:10].reshape(10, 64, 64)
                    theta = z['theta'][:10]
                # GP export reconstructs targets through normalization, with float32 roundoff.
                assert np.allclose(target, z['target'][:10].reshape(10, 64, 64), rtol=1e-6, atol=1e-7)
                assert np.array_equal(theta, z['theta'][:10])
                assert not z['base_train_overlap'][:10].any()
        sources.append(dict(model=name, path=path.relative_to(ROOT).as_posix(),
                            array_key=key, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    destination = ROOT / 'examples/heat_demo.npz'
    np.savez_compressed(destination, predictions=np.stack(fields, axis=1), targets=target,
                        parameters=theta, model_names=np.array(names), source_rows=np.arange(10))
    record = dict(dataset='heat_generated', grid=[64, 64], fitting_rows=list(range(5)),
                  query_rows=list(range(5, 10)), sources=sources,
                  bytes=destination.stat().st_size,
                  sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                  scope='Usage example, not the fixed benchmark reporting partition.',
                  target_source='M1 export, retained unchanged. Other direct-export targets match '
                  'within float32 normalization roundoff (rtol=1e-6, atol=1e-7).',
                  corrector_alignment='Original test-row ordering, retained from the archived export. '
                  'Corrector files do not store theta. See analysis/data/field_example_heat_manifest.json '
                  'and the original export provenance for the alignment audit.')
    (ROOT / 'examples/heat_demo.json').write_text(json.dumps(record, indent=2) + '\n')
    print(f'Wrote {destination.name}: {destination.stat().st_size / 1e6:.2f} MB')


if __name__ == '__main__':
    main()
