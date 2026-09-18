"""Read-only scientific artifact audit supplementing the manuscript build checks."""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from build_data import CLASS_OF
from paper_scope import EXTENSION_DATASETS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def read(path):
    return json.loads(path.read_text())


def close(actual, expected):
    np.testing.assert_allclose(actual, expected, rtol=2e-10, atol=1e-14)


def errors(g, w):
    return np.sqrt(np.maximum(np.einsum('m,nmk,k->n', w, g, w), 0))


def aggregate(ratios):
    logs = {d: math.log(v) for d, v in ratios.items()}
    classes = sorted({CLASS_OF[d] for d in logs})
    return dict(class_ratio=math.exp(np.mean([
        np.mean([v for d, v in logs.items() if CLASS_OF[d] == c]) for c in classes])),
        dataset_ratio=math.exp(np.mean(list(logs.values()))),
        wins=sum(v < .99 for v in ratios.values()),
        losses=sum(v > 1.01 for v in ratios.values()))


def main():
    primary = read(DATA / 'paper_primary_summary.json')
    datasets = set(primary['5']['mean_errors'])
    historical = datasets - set(EXTENSION_DATASETS)
    means = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    evaluation_ids = set()
    appearances = 0
    replay_count = 0
    query_count = 0
    min_diagonal = math.inf
    max_feasibility = 0.
    max_replay_difference = 0.
    for ds in historical:
        folder = DATA / 'review_grams' / ds
        with np.load(folder / 'labels.npz') as z:
            grams = z['gram']
        with np.load(folder / 'features.npz') as z:
            original_rows, groups = z['original_rows'], z['groups']
        query_count += len(original_rows)
        lookup = {int(row): i for i, row in enumerate(original_rows)}
        for run in sorted((DATA / 'historical_runs').glob(ds + '__s*')):
            split = read(run / 'split.json')
            evaluation = [lookup[r['row']] for r in split['evaluation']]
            appearances += len(evaluation)
            evaluation_ids.update((ds, r['row']) for r in split['evaluation'])
            previous = set()
            with np.load(run / 'locked_weights.npz') as weights, np.load(run / 'per_case_errors.npz') as saved:
                for budget in (5, 10, 20):
                    fitting = [lookup[r['row']] for r in split['calibration'][str(budget)]]
                    assert len(fitting) == budget and previous <= set(fitting)
                    assert not set(groups[fitting]) & set(groups[evaluation])
                    previous = set(fitting)
                    g = grams[fitting]
                    diagonal = np.diagonal(g, axis1=1, axis2=2)
                    min_diagonal = min(min_diagonal, float(diagonal.mean(0).min()))
                    selected = np.eye(9)[np.argmin(np.sqrt(np.maximum(diagonal, 0)).mean(0))]
                    inverse = 1 / np.maximum(diagonal.mean(0), 1e-30)
                    inverse /= inverse.sum()
                    close(weights[f'b{budget}__single_l2'], selected)
                    close(weights[f'b{budget}__inverse_mse'], inverse)
                    for method in ('single_l2', 'inverse_mse', 'full'):
                        key = f'b{budget}__{method}'
                        w = weights[key]
                        assert w.min() >= -1e-12
                        max_feasibility = max(max_feasibility, abs(float(w.sum()) - 1))
                        replay = errors(grams[evaluation], w)
                        close(replay, saved[key])
                        max_replay_difference = max(max_replay_difference, float(abs(replay - saved[key]).max()))
                        means[str(budget)][ds][method].append(float(replay.mean()))
                        replay_count += 1

    for ds in EXTENSION_DATASETS:
        result = read(DATA / 'four_dataset_completion/results' / (ds + '.json'))
        roles = read(DATA / 'four_dataset_completion/ROLES.json')
        plan = read(DATA / 'four_dataset_completion/PLAN.json')['datasets'][ds]
        query_count += plan['n_query']
        for partition in (71, 172, 273):
            role = roles[f'{ds}__s{partition}']
            appearances += len(role['evaluation'])
            evaluation_ids.update((ds, row) for row in role['evaluation'])
        for r in result['records']:
            if r['kind'] != 'ensemble' or r['model'] not in ('selected_single', 'inverse_mse', 'full'):
                continue
            method = 'single_l2' if r['model'] == 'selected_single' else r['model']
            close(np.mean(r['per_case_rel_l2']), r['mean_rel_l2'])
            means[str(r['budget'])][ds][method].append(float(np.mean(r['per_case_rel_l2'])))
    assert (query_count, appearances, len(evaluation_ids)) == (3058, 1842, 1505)
    for budget, by_dataset in means.items():
        assert set(by_dataset) == datasets
        for ds, by_method in by_dataset.items():
            for method, values in by_method.items():
                assert len(values) == 3
                close(np.mean(values), primary[budget]['mean_errors'][ds][method])

    # Reconstruct ERA5 errors from complete saved fields, not summary JSON.
    era = DATA / 'era5_completion/nine'
    with np.load(era / 'answers/calibration.npz') as z:
        fit_target, fit_theta = z['target'].astype(float), z['theta']
    with np.load(era / 'answers/evaluation.npz') as z:
        eval_target, eval_theta = z['target'].astype(float), z['theta']
    targets = np.concatenate([fit_target, eval_target])
    theta = np.concatenate([fit_theta, eval_theta])
    models = read(DATA / 'era5/s71/fit.json')['models']
    fields = []
    for model in models:
        with np.load(era / 'predictions' / (model + '__era5.npz')) as z:
            np.testing.assert_array_equal(z['theta'], theta)
            fields.append(z['pred'].astype(float))
    pred = np.stack(fields, axis=1)
    residual = (pred - targets[:, None]) / np.maximum(np.linalg.norm(targets, axis=1), 1e-8)[:, None, None]
    grams = np.einsum('nmp,nkp->nmk', residual, residual)
    era_per_case = defaultdict(list)
    for partition in (71, 172, 273):
        folder = DATA / 'era5' / f's{partition}'
        role = read(folder / 'fit.json')['roles']
        with np.load(folder / 'locked_weights.npz') as weights, np.load(folder / 'per_case_errors.npz') as saved:
            for budget in (5, 10):
                fitting = role['budgets'][str(budget)]
                assert len(fitting) == budget and not set(fitting) & set(role['evaluation'])
                g = grams[fitting]
                inv = 1 / np.maximum(np.diag(g.mean(0)), 1e-30)
                close(weights[f'b{budget}__inverse_mse'], inv / inv.sum())
                for method in ('selected_single', 'inverse_mse', 'full'):
                    key = f'b{budget}__{method}'
                    w = weights[key]
                    direct = np.linalg.norm(np.einsum('m,nmp->np', w, pred[10:]) - eval_target, axis=1) / np.linalg.norm(eval_target, axis=1)
                    close(direct, saved[key])
                    era_per_case[key].append(direct)
                    replay_count += 1
            for i, model in enumerate(models):
                close(np.linalg.norm(residual[10:, i], axis=1), saved['expert:' + model])
            mean_control = saved['training_mean_control'].copy()
    assert np.max(abs(pred[:, models.index('st_hf_pod_gp')] - pred[0, models.index('st_hf_pod_gp')])) == 0
    era_case_wins = {m: int(np.sum(np.mean(era_per_case['b5__' + m], axis=0) < mean_control)) for m in ('inverse_mse', 'full')}
    assert era_case_wins == {'inverse_mse': 6, 'full': 5}
    era_means = {k: float(np.mean(v)) for k, v in era_per_case.items()}

    full_ratios = {d: x['full']/x['single_l2'] for d, x in primary['5']['mean_errors'].items()}
    pde_aggregate = aggregate(full_ratios)
    all_ratios = dict(full_ratios, era5=era_means['b5__full']/era_means['b5__selected_single'])
    all_dataset_ratio = math.exp(np.mean(np.log(list(all_ratios.values()))))
    assert round(100 * (1 - pde_aggregate['class_ratio']), 1) == 11.6
    assert round(100 * (1 - all_dataset_ratio), 1) == 7.5
    assert sum(r < .99 for r in all_ratios.values()) == 16

    # Check the displayed supplement numbers and the scope of the conic fit.
    fresh = read(DATA / 'fresh_heat_summary.json')
    half = fresh['half_resolution']['5']['errors']['heat_generated']
    refresh = {m: 100 * half[m] for m in ('nominal_frozen:inverse_mse', 'inverse_mse', 'nominal_frozen:full', 'full')}
    for key, value in zip(refresh, (.182726, .005563, .148234, .005688)):
        assert round(refresh[key], 6) == value
    loss = read(DATA / 'loss_control/fit.json')
    fits = [r for r in loss['runs'].values() if r['dataset'] in historical]
    assert len(fits) == 51 and all(r['status'] == 'optimal' for r in fits)
    loss_diagnostics = dict(partitions=len(fits),
        max_simplex_residual=max(r['primal_simplex_residual'] for r in fits),
        min_relative_eigenvalue=min(a['relative_negative_eigenvalue'] for r in fits for a in r['psd']))

    # Derivations are checked analytically in the audit report, with these numeric constants.
    concentration = [2 * math.sqrt(2 * math.log(2 * 9**2 / .05) / k) for k in (5, 10, 20)]
    assert [round(v, 3) for v in concentration] == [3.596, 2.543, 1.798]
    t = 11 / 101
    close(1.1 - .1 * t, 110 / 101)
    report = dict(passed=True, scope='Artifact and mathematical audit, not new surrogate training or solver validation',
        historical_gram_prediction_replays=459, era5_direct_field_replays=18,
        total_replayed_rules=replay_count, extension_case_mean_records=108,
        query_rows=query_count, evaluation_appearances=appearances, distinct_dataset_rows=len(evaluation_ids),
        max_weight_sum_residual=max_feasibility, max_historical_error_replay_difference=max_replay_difference,
        minimum_historical_mean_diagonal=min_diagonal,
        pde_class_counts=dict(Counter(CLASS_OF[d] for d in datasets)),
        pde_fitted_vs_selected=pde_aggregate, all22_dataset_ratio=all_dataset_ratio,
        era5_case_wins=era_case_wins, era5_means=era_means,
        coarse_refresh_percent=refresh, direct_loss_diagnostics=loss_diagnostics,
        excess_risk_bound_multipliers=concentration)
    (ROOT / 'qa/appendix_audit_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
