"""Check fresh checkpoint scores against exported fields and common case provenance."""
from pathlib import Path
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    alignment = json.loads((ROOT / 'data/baseline_alignment.json').read_text())
    checks = []
    for dataset in ['heat_local', 'sharp__burgers_2d']:
        folder = ROOT / 'data/b8_recovery'
        info = json.loads((folder / (dataset + '__replay.json')).read_text())
        assert info['passed'] and info['no_training'] and info['dataset'] == dataset
        assert info['scores_recomputed'] and not info['tf32_enabled']
        assert digest(folder / 'model.py') == info['model_source_sha256']
        path = folder / info['archive']
        assert digest(path) == info['archive_sha256']
        rawpath = ROOT / 'data/baseline_raw' / ('fno_coregionalization__' + dataset + '__s42.json')
        assert digest(rawpath) == info['evaluated_raw_sha256']
        original_path = folder / (dataset + '__original_raw.json')
        assert digest(original_path) == info['original_raw_sha256']
        original = np.asarray(json.loads(original_path.read_text())['splits']['test_hf']['rel_l2_per_sample'])
        raw = json.loads(rawpath.read_text())
        expected = np.asarray(raw['splits']['test_hf']['rel_l2_per_sample'])
        reference = next(r for r in alignment['remote_checks'] if r['dataset'] == dataset)
        assert info['test_archive_sha256'] == reference['test_archive_sha256']
        assert reference['input_order_matches_reference']
        assert info['grid'] == reference['grid'] and info['n'] == reference['n']
        with np.load(path) as z:
            x, pred, target = z['x'], z['pred'], z['target']
            assert len(x) == len(expected) == len(target) == info['n']
            assert np.isfinite(pred).all() and np.isfinite(target).all()
            assert hashlib.sha256(target.tobytes()).hexdigest() == info['target_sha256']
            assert [hashlib.sha256(row.tobytes()).hexdigest() for row in x] == info['input_row_sha256']
            replay = np.linalg.norm(pred.astype(np.float64) - target, axis=1) / np.maximum(
                np.linalg.norm(target.astype(np.float64), axis=1), 1e-12)
            np.testing.assert_array_equal(z['archived_errors'], original)
            np.testing.assert_allclose(replay, z['errors'], rtol=1e-12, atol=1e-15)
            np.testing.assert_allclose(replay, expected, rtol=1e-12, atol=1e-15)
        arc = reference['archives']['fno_coregionalization']
        assert arc['target_rows_match'] and arc['checkpoint_replay_verified']
        assert arc['archive_sha256'] == info['archive_sha256']
        np.testing.assert_array_equal(arc['errors'], replay)
        checks.append(dict(dataset=dataset, n=len(x), checkpoint_sha256=info['checkpoint_sha256'],
                           test_archive_sha256=info['test_archive_sha256'],
                           original_archived_errors_reproduced=info['archived_errors_match'],
                           max_relative_error_difference=float((abs(replay-expected)/expected).max())))
    result = dict(passed=True, no_training=True, recovered_model_dataset_cells=len(checks), checks=checks)
    (ROOT / 'qa/b8_recovery_checks.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
