"""Read-only verification of completed artifacts; writes only the QA report."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT.parent / 'mf_field_fieldgate_20260912'

def digest(p):
    return sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def main():
    launch = read(ROOT / 'GATE_LAUNCH.json')
    assert digest(ROOT / 'plan.json') == launch['plan_sha256']
    for name, expected in launch['source_sha256'].items():
        assert digest(ROOT / name) == expected, name
    assert {'node2900', 'node4200'} <= set(launch['exclusions'].split(','))
    plan = read(ROOT / 'plan.json')
    class_of = {d: c for c, ds in plan['classes'].items() for d in ds}
    status = read(ROOT / 'results/status.json')
    assert status['complete'] and len(status['completed_runs']) == 11
    run_checks = []
    for name in status['completed_runs']:
        folder = ROOT / 'runs' / name
        fit = read(folder / 'fit.json')
        result = read(folder / 'result.json')
        split = read(folder / 'split.json')
        assert digest(folder / 'fit.json') == result['fit_sha256']
        assert digest(folder / 'split.json') == fit['split_sha256']
        assert digest(folder / 'locked_weights.npz') == fit['locked_weights_sha256'] == result['locked_weights_sha256']
        assert fit['locked_before_evaluation_scoring']
        assert fit['fit_and_tune_receive_only_assigned_labels'] and not fit['features_use_truth']
        groups = [set(row['group'] for row in split[k]) for k in ['fit', 'tune', 'evaluation']]
        assert not (groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2])
        assert all(row['dataset'] != 'era5' for k in ['fit', 'tune'] for row in split[k])
        if split['protocol'] == 'class':
            held = split['held_class']
            assert all(class_of[row['dataset']] != held for k in ['fit', 'tune'] for row in split[k])
            assert all(class_of[row['dataset']] == held for row in split['evaluation'])
            assert fit['starting_prior_level'] == 'global'
            for source, expected in fit['source_sha256'].items():
                assert digest(ROOT / source) == expected
        else:
            original = ORIGINAL / 'runs' / name
            for artifact in ['fit.json', 'result.json', 'split.json', 'locked_weights.npz', 'per_case_errors.npz']:
                assert digest(folder / artifact) == digest(original / artifact), artifact
        weights = np.load(folder / 'locked_weights.npz', allow_pickle=False)
        assert list(zip(weights['dataset'].tolist(), weights['row'].tolist())) == [(r['dataset'], r['row']) for r in split['evaluation']]
        for method in weights.files:
            if method in ['dataset', 'row']:
                continue
            w = weights[method]
            assert w.shape == (fit['n_eval'], 7), method
            assert np.isfinite(w).all() and w.min() >= -1e-12, method
            assert np.allclose(w.sum(axis=1), 1, rtol=0, atol=1e-10), method
        run_checks.append(dict(id=name, fit=fit['n_fit'], tune=fit['n_tune'], evaluation=fit['n_eval'], passed=True))
    gpu = cpu = strict_rows = 0
    for task in plan['tasks']:
        export = read(ROOT / 'export_results' / (task['id'] + '.json'))
        replay = export['replay']
        if task['device'] == 'gpu':
            assert replay['matmul_tf32'] is False and replay['cudnn_tf32'] is False
            assert replay['matmul_precision'] == 'highest' and not replay['base_retrained']
            gpu += 1
        else:
            assert replay['base_retrained'] and task['model'] == 'st_hf_pod_gp'
            cpu += 1
    max_target_difference = 0.
    for dataset in plan['datasets']:
        audit = read(ROOT / 'cache' / dataset / 'audit.json')
        max_target_difference = max(max_target_difference, max(audit['target_max_relative_differences'].values()))
        assert max_target_difference < 5e-7
        assert audit['hf_train_overlap'] == 0
        for model, expected in audit['source_sha256'].items():
            assert read(ROOT / 'export_results' / f'{model}__{dataset}.json')['prediction_sha256'] == expected
        if dataset == 'era5':
            assert audit['lf_train_overlap'] == 7 and not audit['strict_eligible']
        else:
            assert audit['lf_train_overlap'] == 0 and audit['strict_eligible']
            strict_rows += audit['n_kept']
    assert (gpu, cpu, strict_rows) == (132, 22, 2990)
    report = dict(passed=True, checked_at_utc=datetime.now(timezone.utc).isoformat(),
                  frozen_source_hashes_checked=len(launch['source_sha256']),
                  strict_fp32_neural_exports=gpu, training_only_classical_refits=cpu,
                  strict_datasets=21, strict_classes=7, strict_historical_rows=strict_rows,
                  max_cross_expert_target_relative_difference=max_target_difference,
                  checks=['Source and plan hashes', 'Fit/weight/split hashes',
                          'Disjoint fit/tune/evaluation input groups', 'Entire class excluded from gate fit/tune',
                          'Climate excluded from every fit/tune split', 'Convex finite locked evaluation weights',
                          'Original case results reused byte-for-byte', 'Global prior contract for corrected class runs',
                          'All neural export precision metadata', 'Cache/export provenance links',
                          'Target alignment and base input overlap audits', 'Required node exclusions'],
                  scope='Checks completed artifact consistency. Does not make historical data fresh or independently rerun model inference.',
                  runs=run_checks)
    (ROOT / 'results/QA.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'runs'}, indent=2))

if __name__ == '__main__':
    main()
