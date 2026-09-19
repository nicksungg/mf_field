"""Plot an actual evaluation field using previously locked ensemble weights."""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, SymLogNorm
import numpy as np
from rule_labels import RULE_NAMES

ROOT = Path(__file__).resolve().parents[1]
DATASET = 'heat_generated'
PARTITION = 71
BUDGET = 5


def build():
    bundle = ROOT / 'data/field_example_heat.npz'
    manifest = json.loads((ROOT / 'data/field_example_heat_manifest.json').read_text())
    assert hashlib.sha256(bundle.read_bytes()).hexdigest() == manifest['bundle_sha256']
    with np.load(bundle) as z:
        target = z['target'].astype(np.float64)
        predictions = z['predictions'].astype(np.float64)
        models = z['models'].tolist()
        row = int(z['query_row'])
    assert target.shape == (64, 64) and predictions.shape == (9, 64, 64)
    audit = json.loads((ROOT / f'data/review_grams/{DATASET}/audit.json').read_text())
    assert models == audit['models']
    for model in models:
        assert manifest['sources'][model]['sha256'] == audit['source_prediction_sha256'][model]
    folder = ROOT / f'data/historical_runs/{DATASET}__s{PARTITION}'
    split = json.loads((folder / 'split.json').read_text())
    evaluation_rows = [entry['row'] for entry in split['evaluation']]
    fitting_rows = [entry['row'] for entry in split['calibration'][str(BUDGET)]]
    assert row == evaluation_rows[0] and row not in fitting_rows
    with np.load(ROOT / f'data/review_grams/{DATASET}/labels.npz') as z:
        grams = z['gram'].copy()
    scale = max(float(np.linalg.norm(target)), 1e-8)
    errors = (predictions - target).reshape(9, -1) / scale
    np.testing.assert_allclose(errors @ errors.T, grams[row], rtol=1e-10, atol=1e-16)
    weights_path = ROOT / 'data/review_analysis_locked_weights.npz'
    methods = ['selected_single', 'inverse_mse', 'full']
    with np.load(weights_path) as z:
        weights = np.stack([z[f'{DATASET}__s{PARTITION}__b{BUDGET}__{m}'] for m in methods])
        selected = z[f'{DATASET}__s{PARTITION}__b{BUDGET}__selected_single'].copy()
    assert np.all(weights >= -1e-12)
    np.testing.assert_allclose(weights.sum(axis=1), 1, atol=1e-12)
    combined = np.einsum('km,mhw->khw', weights, predictions)
    fields = np.concatenate([target[None], predictions, combined])
    absolute_errors = np.abs(fields - target)
    relative_errors = np.linalg.norm((fields - target).reshape(13, -1), axis=1) / scale
    gram_errors = np.sqrt(np.maximum(np.einsum('ki,ij,kj->k', weights, grams[row], weights), 0))
    np.testing.assert_allclose(relative_errors[-3:], gram_errors, rtol=1e-10, atol=1e-14)
    best = int(relative_errors[1:10].argmin())
    assert best == int(selected.argmax()) == 3
    # Model selection uses the saved fitting decision, not the evaluation errors.
    # It chose M4 here, so the selected model must reproduce M4 exactly.
    np.testing.assert_array_equal(weights[0], selected)
    np.testing.assert_array_equal(combined[0], predictions[int(selected.argmax())])
    assert np.all(relative_errors[-2:] < relative_errors[best + 1])
    all_model_errors = np.sqrt(np.maximum(np.diagonal(grams[evaluation_rows], axis1=1, axis2=2), 0))
    all_fitted_errors = np.sqrt(np.maximum(np.einsum('i,nij,j->n', weights[2], grams[evaluation_rows], weights[2]), 0))
    all_case_wins = int(np.sum(all_fitted_errors < all_model_errors.min(axis=1)))
    with np.load(folder / 'per_case_errors.npz') as z:
        np.testing.assert_allclose(all_fitted_errors, z['b5__full'], rtol=1e-10, atol=1e-14)

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'pdf.fonttype': 42})
    fig = plt.figure(figsize=(14.8, 3.78), facecolor='white')
    names = ['Ground truth'] + [f'M{i}' for i in range(1, 10)] + [RULE_NAMES[m] for m in methods]
    left, width, gap = .040, .0675, .005
    xs = [left + j * (width + gap) for j in range(13)]
    heights = .285
    field_norm = Normalize(float(fields.min()), float(fields.max()))
    error_norm = SymLogNorm(linthresh=1e-5, linscale=1, vmin=0,
                            vmax=float(absolute_errors.max()), base=10)
    for col, name in enumerate(names):
        color = '#146B61' if col >= 10 else '#243544'
        display_name = name.replace(' ', '\n') if col == 0 or col >= 10 else name
        fig.text(xs[col] + width / 2, .904, display_name, ha='center', va='center',
                 fontsize=11 if col < 10 else 10, color=color,
                 fontweight='bold' if col >= 10 else 'normal')
        for bottom, array, cmap, norm in [
            (.550, fields[col], 'viridis', field_norm),
            (.225, absolute_errors[col], 'magma', error_norm),
        ]:
            ax = fig.add_axes([xs[col], bottom, width, heights])
            im = ax.imshow(array, origin='lower', interpolation='nearest',
                           aspect='equal', cmap=cmap, norm=norm)
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_linewidth(.7 if col >= 10 else .35)
                spine.set_color(color if col >= 10 else '#B9C1C5')
        value = '0' if col == 0 else f'{100 * relative_errors[col]:.4f}'
        fig.text(xs[col] + width / 2, .187, value + '%', ha='center', va='center',
                 fontsize=10, color=color, fontweight='bold' if col >= 10 else 'normal')
    fig.text(.016, .6925, 'Field', ha='center', va='center', rotation=90, fontsize=11)
    fig.text(.016, .3675, 'Absolute error', ha='center', va='center', rotation=90, fontsize=11)
    fig.text(.047, .047, r'Relative $L^2$ errors shown below panels', fontsize=9, va='center')
    # Both rows use shared scales. The logarithmic error color scale makes
    # the small errors visible without rescaling each model independently.
    cax = fig.add_axes([.32, .073, .245, .028])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=field_norm, cmap='viridis'), cax=cax,
                      orientation='horizontal', ticks=[0, .5, 1.0])
    cb.ax.tick_params(labelsize=8, length=2, pad=1)
    cb.ax.set_title('Field value', fontsize=9, pad=3)
    cax = fig.add_axes([.666, .073, .270, .028])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=error_norm, cmap='magma'), cax=cax,
                      orientation='horizontal', ticks=[0, 1e-5, 1e-4, 1e-3, 1e-2])
    cb.ax.set_xticklabels(['0', r'$10^{-5}$', r'$10^{-4}$', r'$10^{-3}$', r'$10^{-2}$'])
    cb.ax.tick_params(labelsize=8, length=2, pad=1)
    cb.ax.set_title('Absolute error: shared logarithmic color scale', fontsize=9, pad=3)
    for ext in ['pdf', 'png']:
        fig.savefig(ROOT / f'figures/field_comparison_heat.{ext}', dpi=320,
                    bbox_inches='tight', pad_inches=.02)
    plt.close(fig)
    report = {
        'passed': True, 'dataset': DATASET, 'display_name': 'Heat I',
        'partition': PARTITION, 'budget': BUDGET, 'query_row': row,
        'selection': 'Dataset chosen as an illustrative success. First evaluation row of the first partition, not the largest case gain.',
        'fitting_rows': fitting_rows, 'evaluation_rows': evaluation_rows,
        'models': models, 'methods': methods, 'weights': weights.tolist(),
        'weights_source_sha256': hashlib.sha256(weights_path.read_bytes()).hexdigest(),
        'bundle_sha256': manifest['bundle_sha256'],
        'field_gram_replay_passed': True, 'saved_errors_replayed': True,
        'evaluation_case_excluded_from_fitting': True,
        'relative_errors_percent': dict(zip(names, (100 * relative_errors).tolist())),
        'best_individual': f'M{best + 1}',
        'fitted_reduction_vs_best_individual_percent': float(100 * (1 - relative_errors[-1] / relative_errors[best + 1])),
        'inverse_reduction_vs_best_individual_percent': float(100 * (1 - relative_errors[-2] / relative_errors[best + 1])),
        'fitted_case_wins_over_each_individual': all_case_wins,
        'evaluation_cases_in_partition': len(evaluation_rows),
        'selected_model': f'M{int(selected.argmax()) + 1}',
        'selected_model_identical_to_saved_member': True,
        'automatic_selection_displayed': False,
        'field_color_limits': [float(fields.min()), float(fields.max())],
        'error_color_limits': [0, float(absolute_errors.max())],
        'error_color_linthresh': 1e-5,
        'shared_color_scales': True, 'field_values_transformed': False,
        'grid': [64, 64], 'orientation': 'Stored arrays with origin lower. Heat panels span space and time.',
    }
    (ROOT / 'qa/field_comparison_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ['passed', 'best_individual',
          'relative_errors_percent', 'fitted_reduction_vs_best_individual_percent',
          'fitted_case_wins_over_each_individual']}, indent=2))
    return report


if __name__ == '__main__':
    build()
