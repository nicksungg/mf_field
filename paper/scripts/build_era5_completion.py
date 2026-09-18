"""Verify frozen ERA5 predictions and score all baselines on matching cases.

This reporting step never trains a model or changes a fitted weight. Scores are
replayed from predictions and checked against the completed production collector.
"""
from pathlib import Path
import csv
import hashlib
import importlib.util
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def relative(pred, target):
    return np.linalg.norm(np.asarray(pred, dtype=np.float64) - target, axis=1) / np.maximum(np.linalg.norm(target, axis=1), 1e-8)


def build():
    nine = DATA / 'era5_completion/nine'
    baseline = DATA / 'era5_completion/baselines'
    summary = read(DATA / 'era5_summary.json')
    audit = read(DATA / 'era5_nine_expert_audit.json')
    assert audit['passed'] and audit['original_roles_preserved']
    assert audit['both_correctors_available_to_all_rules'] and audit['mixtures_checked'] == 36
    assert audit['models'] == summary['models'] and len(summary['models']) == 9
    assert sha(nine / 'SOURCE.json') == audit['source_sha256']
    answers = {}
    for split in ('calibration', 'evaluation'):
        with np.load(nine / 'answers' / (split + '.npz')) as z:
            answers[split] = dict(theta=z['theta'].copy(), target=z['target'].astype(np.float64))
            assert z['work_grid'].tolist() == [128, 256]
    theta = np.concatenate([answers[k]['theta'] for k in ('calibration', 'evaluation')])
    target = answers['evaluation']['target']
    first_fit = read(DATA / 'era5/s71/fit.json')
    prediction_hashes = first_fit['prediction_sha256']
    predictions = {}
    for model, expected in prediction_hashes.items():
        path = nine / 'predictions' / (model + '__era5.npz')
        meta = read(nine / 'metadata' / (model + '__era5.json'))
        assert sha(path) == expected == meta['prediction_sha256']
        assert meta['smoke'] is False
        with np.load(path) as z:
            assert np.array_equal(z['theta'], theta)
            assert z['work_grid'].tolist() == [128, 256]
            predictions[model] = z['pred'].copy()
        assert predictions[model].shape == (17, 32768)
        assert np.isfinite(predictions[model]).all()
        if model.startswith('uqcorr_'):
            assert meta['scientific_result'] and meta['trained_no_reservedanswers']
            assert meta['reserved_answer_guard'] and not meta['synthetic_coarse_stub']
            assert meta['oof_members_train'] == meta['oof_members_query'] == 4
    fields = np.stack([predictions[m][10:] for m in summary['models']], axis=1)
    mixtures = 0
    for seed in (71, 172, 273):
        directory = DATA / 'era5' / f's{seed}'
        fit = read(directory / 'fit.json')
        evaluation = read(directory / 'evaluation.json')
        assert fit['prediction_sha256'] == prediction_hashes
        assert fit['source_manifest_sha256'] == sha(nine / 'SOURCE.json')
        for split in ('calibration', 'evaluation'):
            path = nine / 'answers' / f'partition_{split}.npz'
            assert fit['roles'][split + '_sha256'] == sha(path)
            with np.load(path) as z:
                assert np.array_equal(z['theta'], answers[split]['theta'])
                assert np.array_equal(z['target'], answers[split]['target'])
        assert not fit['final_answers_loaded'] and evaluation['weights_locked_before_evaluation']
        assert fit['weights_sha256'] == sha(directory / 'locked_weights.npz')
        assert evaluation['fit_sha256'] == sha(directory / 'fit.json')
        assert evaluation['per_case_errors_sha256'] == sha(directory / 'per_case_errors.npz')
        with np.load(directory / 'locked_weights.npz') as weights, np.load(directory / 'per_case_errors.npz') as errors:
            for method in weights.files:
                w = weights[method]
                assert w.shape == (9,) and np.all(w >= 0) and np.isclose(w.sum(), 1)
                replay = relative(np.einsum('m,nmp->np', w, fields.astype(np.float64)), target)
                assert np.allclose(replay, errors[method], rtol=2e-7, atol=2e-8), method
                mixtures += 1
            for model, pred in predictions.items():
                method = 'hf_only_control' if model == 'fno_hf_only_control' else 'expert:' + model
                assert np.allclose(relative(pred[10:], target), errors[method], rtol=2e-7, atol=2e-8), model
    pod = predictions['st_hf_pod_gp']
    assert np.max(np.abs(pod - pod[0])) == 0
    write(DATA / 'era5_archive_checks.json', dict(
        source_manifest_valid=True, source_manifest_sha256=sha(nine / 'SOURCE.json'),
        summary_sha256=sha(DATA / 'era5_summary.json'), prediction_hashes=prediction_hashes,
        pod_gp_query_rows=17, pod_gp_max_query_variation_relative_to_first=0,
        prediction_arrays_and_input_correspondence_verified=True,
        mixtures_replayed=mixtures, evaluation_targets_unchanged=True,
        replay_tolerance=dict(rtol=2e-7, atol=2e-8),
        source='Completed nine expert campaign with reused seven experts and two completed correctors'))

    # Retain the production collector's validation and scoring operations.
    module_path = DATA / 'era5_completion/validate_baselines.py'
    spec = importlib.util.spec_from_file_location('era5_baseline_validation', module_path)
    validation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validation)
    roster = validation.validate_roster(read(baseline / 'BASELINES.json'))
    available = [r for r in roster if (baseline / 'metadata' / (r['model'] + '__era5.json')).is_file()
                 and (baseline / 'predictions' / (r['model'] + '__era5.npz')).is_file()]
    missing = [r for r in roster if r not in available]
    assert not missing, 'The paper now requires the complete ERA5 baseline campaign'
    info = read(baseline / 'PLAN.json')['datasets']['era5']
    manifests = {key: sha(baseline / file) for key, file in
                 [('source_manifest_sha256', 'SOURCE.json'), ('plan_sha256', 'PLAN.json'),
                  ('input_manifest_sha256', 'INPUT_MANIFEST.json')]}
    bpred, bmeta, hashes, aliases = validation.validate_predictions(baseline, available, info, theta, manifests)
    inputs = read(baseline / 'INPUT_MANIFEST.json')['files']
    for split in ('calibration', 'evaluation'):
        path = baseline / 'answers' / (split + '.npz')
        assert sha(path) == inputs[f'answers/era5/{split}.npz']['sha256']
        assert path.read_bytes() == (nine / 'answers' / (split + '.npz')).read_bytes()
    rows, cases, means = [], [], {}
    for row in available:
        model = row['model']
        for split, inds in [('calibration', np.arange(10)), ('evaluation', np.arange(10, 17))]:
            err, rmse = validation.score(bpred[model][inds], answers[split]['target'])
            rows.append(dict(baseline_id=row['id'], model=model, split=split, n_cases=len(inds),
                             rel_l2=float(err.mean()), rmse_raw_units=rmse, reused_from=aliases.get(model, '')))
            for i, e in zip(inds, err):
                cases.append(dict(baseline_id=row['id'], model=model, split=split, query_row=int(i), relative_l2=float(e)))
            if split == 'evaluation':
                means[model] = float(err.mean())
    mean_control = summary['means']['training_mean_control']
    assert np.isclose(mean_control, read(baseline / 'prior_training_mean.json')['rel_l2'], rtol=1e-7)
    means['st_mean'] = mean_control
    production = baseline / 'production_results'
    production_audit = read(production / 'BASELINES_AUDIT.json')
    assert production_audit['passed'] and production_audit['complete']
    assert production_audit['models_verified'] == len(roster)
    assert production_audit['all_predictions_verified_before_answers']
    assert production_audit['calibration_count'] == 10 and production_audit['evaluation_count'] == 7
    assert production_audit['aliases'] == aliases
    for filename, expected in production_audit['results_sha256'].items():
        assert sha(production / filename) == expected, filename
    production_summary = read(production / 'era5_baselines__summary.json')
    assert production_summary['complete'] and production_summary['models'] == [r['model'] for r in roster]
    for model, value in means.items():
        key = 'training_mean_control' if model == 'st_mean' else model
        assert np.isclose(value, production_summary['means'][key], rtol=1e-10, atol=1e-12), model
    with np.load(production / 'era5_baselines_per_case.npz') as original_errors:
        for row in available:
            model = row['model']
            assert production_summary['metadata'][model]['prediction_sha256'] == hashes[model]['prediction_sha256']
            for split, inds in [('calibration', np.arange(10)), ('evaluation', np.arange(10, 17))]:
                replay, _ = validation.score(bpred[model][inds], answers[split]['target'])
                assert np.allclose(replay, original_errors[f'{split}__{model}'], rtol=1e-10, atol=1e-12), (model, split)
    for name, entries in [('era5_baselines_reported.csv', rows), ('era5_baselines_per_case.csv', cases)]:
        with (DATA / name).open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(entries[0]))
            writer.writeheader()
            writer.writerows(entries)
    bsummary = dict(snapshot_verified=True, campaign_complete=not missing,
                    available_entries=len(available), independent_fits=len(available)-len(aliases),
                    missing_models=[r['model'] for r in missing], missing_ids=[r['id'] for r in missing],
                    models=[r['model'] for r in available], means=means, aliases=aliases,
                    n_base_hf_train=55, n_calibration=10, n_evaluation=7, work_grid=[128, 256],
                    prediction_artifacts=hashes, manifests=manifests,
                    answers_identical_to_nine_model_study=True,
                    production_collection_verified=True,
                    production_audit_sha256=sha(production / 'BASELINES_AUDIT.json'),
                    scope='All twelve ERA5 baseline entries from eleven independent fits, plus the training mean control. Production collection and per-case scores verified.')
    write(DATA / 'era5_baselines_summary.json', bsummary)
    write(ROOT / 'qa/era5_baseline_checks.json', dict(passed=True, **bsummary))

    # Update the actual Figure 1 prediction and bars to the nine model fit.
    path = DATA / 'overview_era5.npz'
    with np.load(path) as z:
        bundle = {key: z[key].copy() for key in z.files}
    with np.load(DATA / 'era5/s71/locked_weights.npz') as z:
        w = z['b5__inverse_mse'].copy()
    candidates = np.stack([predictions[m][10].reshape(128, 256) for m in summary['models']])
    combined = np.tensordot(w, candidates, axes=(0, 0))
    new = dict(bundle, era5_candidate_fields=candidates, era5_inverse_weights=w, era5_mixture=combined)
    if any(not np.array_equal(bundle[key], new[key]) for key in new):
        np.savez_compressed(path, **new)
    manifest = read(DATA / 'overview_manifest.json')
    era = manifest['era5']
    era['models'], era['weights'] = summary['models'], w.tolist()
    era['source_predictions'] = [dict(model=m, source_path=f'data/era5_completion/nine/predictions/{m}__era5.npz',
                                     archive_sha256=prediction_hashes[m], prediction_row=10,
                                     prediction_sample_sha256=hashlib.sha256(predictions[m][10].tobytes()).hexdigest())
                               for m in summary['models']]
    era['mixture_sha256'] = hashlib.sha256(combined.tobytes()).hexdigest()
    era['weights_file_sha256'] = sha(DATA / 'era5/s71/locked_weights.npz')
    era['first_evaluation_relative_l2'] = float(relative(combined.reshape(1, -1), target[:1])[0])
    with np.load(DATA / 'era5/s71/per_case_errors.npz') as z:
        era['archived_first_evaluation_relative_l2'] = float(z['b5__inverse_mse'][0])
    assert abs(era['first_evaluation_relative_l2'] - era['archived_first_evaluation_relative_l2']) < 2e-8
    manifest['bundled_data_sha256'] = sha(path)
    write(DATA / 'overview_manifest.json', manifest)

    manifest_path = DATA / 'snapshot_manifest.json'
    snapshots = read(manifest_path)
    for entry in snapshots:
        if entry['snapshot'].startswith('era5') and 'sha256' in entry:
            entry['sha256'] = sha(DATA / entry['snapshot'])
            entry['source'] = 'Completed ERA5 nine model campaign, imported September 16, 2026. See data/era5_completion.'
    write(manifest_path, snapshots)
    print(f'ERA5: verified nine experts and {mixtures} mixtures. Scored {len(available)} baseline entries. Missing: {[r["id"] for r in missing]}')


if __name__ == '__main__':
    build()
