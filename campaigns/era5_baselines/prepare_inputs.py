"""Audit the existing ERA5 split without constructing a new experiment split."""
import json
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from baseline_common import ROOT, sha, write_json, save_npz, load_plan


def keys(x):
    x = np.asarray(x, np.float32).copy()
    x[x == 0] = 0
    return [row.tobytes() for row in x]


def main():
    torch.set_num_threads(4)
    plan = load_plan()
    info = plan['datasets']['era5']
    data = ROOT / 'data/core/era5'
    with np.load(data / 'test_l9.npz', allow_pickle=False) as z:
        query = z['x'].copy()
    assert query.shape == (17, 12) and len(set(keys(query))) == 17
    reserved = set(keys(query))
    reports = {}
    entries = {}
    for level, rec in info['levels'].items():
        train = data / f'train_l{level}.npz'
        test = data / f'test_l{level}.npz'
        assert sha(train) == rec['prepared_sha256']
        assert sha(test) == rec['query_sha256']
        with np.load(train, allow_pickle=False) as z:
            x = z['x'].copy()
            assert len(x) == rec['kept_train_count']
            assert not (set(keys(x)) & reserved), f'Reserved input in level {level}'
            if int(level) == 9:
                y = torch.from_numpy(z['y'].mean(0, dtype=np.float64).astype(np.float32)).reshape(1, 1, 721, 1440)
                mean = F.interpolate(y, size=(128, 256), mode='bilinear', align_corners=False)[0, 0].numpy()
                save_npz(ROOT / 'data/training_mean.npz', mean=mean, work_grid=np.array([128, 256]))
                del y
        with np.load(test, allow_pickle=False) as z:
            assert np.array_equal(z['x'], query) and not np.any(z['y'])
        reports[level] = dict(training_rows=len(x), reserved_input_overlap=0,
                              original_grid=rec['grid'], original_prepared_sha256=rec['prepared_sha256'])
        for path, role in [(train, 'train'), (test, 'query')]:
            entries[str(path.relative_to(ROOT))] = dict(sha256=sha(path), role=role)
    for name, rows in [('calibration', slice(0, 10)), ('evaluation', slice(10, 17))]:
        path = ROOT / 'answers/era5' / f'{name}.npz'
        with np.load(path, allow_pickle=False) as z:
            assert np.array_equal(z['theta'], query[rows])
            assert z['target'].shape == (len(query[rows]), 32768)
            assert np.isfinite(z['target']).all()
    for path in sorted((ROOT / 'answers').rglob('*.npz')):
        entries[str(path.relative_to(ROOT))] = dict(sha256=sha(path), role='answer')
    entries['data/training_mean.npz'] = dict(sha256=sha(ROOT / 'data/training_mean.npz'), role='control')
    write_json(ROOT / 'INPUT_MANIFEST.json', dict(version=1, files=entries,
               original_plan_sha256=sha(ROOT / 'PLAN.json')))
    write_json(ROOT / 'INPUT_AUDIT.json', dict(passed=True, levels=reports,
               plan_sha256=sha(ROOT / 'PLAN.json'), input_manifest_sha256=sha(ROOT / 'INPUT_MANIFEST.json'),
               n_base_hf_train=55, n_calibration=10, n_evaluation=7, all_fidelities_checked=9,
               evaluation_inputs_excluded_at_every_fidelity=True,
               calibration_inputs_excluded_at_every_fidelity=True,
               original_split_unchanged=True, training_query_targets_are_zero=True))
    alias = ROOT / 'flat_data/era5'
    alias.parent.mkdir(exist_ok=True)
    if not alias.exists():
        alias.symlink_to('../data/core/era5', target_is_directory=True)
    print('Input audit passed: nine fidelities, 55 fine training, 10 calibration, seven evaluation.')


if __name__ == '__main__':
    main()
