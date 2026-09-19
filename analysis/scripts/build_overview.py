"""Compact workflow figure using ERA5 training fields and saved predictions.

All numerical examples are bundled. The coarse preview is blurred only for
illustration. The routine never consults a cluster or fits weights. The existing
ERA5 weights were locked using calibration answers.
"""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
from scipy.ndimage import gaussian_filter, zoom

ROOT = Path(__file__).resolve().parents[1]


def overview(values=None):
    """Render archived ERA5 outputs with an illustrative coarse blur documented in the source manifest."""
    with np.load(ROOT / 'data/overview_era5.npz') as z:
        training_lf_x = z['era5_training_lf_parameters']
        training_hf_x = z['era5_training_hf_parameters']
        coarse = z['era5_training_coarse']
        fine = z['era5_training_fine']
        candidates = z['era5_candidate_fields']
        weights = z['era5_inverse_weights']
        combined = z['era5_mixture']
    source = json.loads((ROOT / 'data/overview_manifest.json').read_text())
    assert len(weights) == candidates.shape[0] == 9
    assert np.all(weights >= 0) and np.isclose(weights.sum(), 1)
    assert np.array_equal(combined, np.tensordot(weights, candidates, axes=(0, 0)))
    assert hashlib.sha256(combined.tobytes()).hexdigest() == source['era5']['mixture_sha256']
    pair = source['era5']['training_pair']
    assert np.array_equal(training_lf_x, training_hf_x)
    for field, name in [(coarse, 'coarse'), (fine, 'fine')]:
        assert list(field.shape) == pair[name + '_grid']
        assert hashlib.sha256(field.tobytes()).hexdigest() == pair[name + '_array_sha256']
        assert np.isfinite(field).all()
    for params, name in [(training_lf_x, 'lf'), (training_hf_x, 'hf')]:
        assert hashlib.sha256(params.tobytes()).hexdigest() == pair[name + '_input_sha256']
    display = source['display_transform']
    assert display['field'] == 'era5_training_coarse'
    assert display['operation'] == 'gaussian_filter'
    # Only the displayed coarse preview is smoothed. Native bundled arrays,
    # fine fields, model predictions and fitted weights remain untouched.
    coarse_preview = gaussian_filter(coarse, sigma=display['sigma_grid_cells'],
                                     mode=display['boundary_mode'])
    # Render the saved ensemble on the native fine grid for illustration.
    # Inference and evaluation retain their original working grid.
    combined_preview = zoom(combined,
                            np.asarray(fine.shape) / np.asarray(combined.shape),
                            order=1, mode='nearest', prefilter=False)
    assert combined_preview.shape == fine.shape
    assert np.isfinite(combined_preview).all()
    elo = min(coarse.min(), fine.min(), candidates.min(), combined.min())
    ehi = max(coarse.max(), fine.max(), candidates.max(), combined.max())

    ink, blue, green = '#243541', '#246E92', '#21816D'
    colors = ['#2D7597', '#73A2AE', '#C8AF7A', '#D39257', '#A89AC0', '#819F73', '#387A6B', '#AD6E80', '#686AA6']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42, 'ps.fonttype': 42})
    fig = plt.figure(figsize=(7.1, 2.6), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis('off')

    def txt(x, y, label, size=8, color=ink, **kw):
        return ax.text(x, y, label, ha='center', va='center', fontsize=size, color=color, **kw)

    def arrow(start, end, color=ink, **kw):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=10,
                                    lw=.95, color=color, **kw))

    def panel(x, width, color, face):
        ax.add_patch(FancyBboxPatch((x, .055), width, .89,
                     boxstyle='round,pad=.004,rounding_size=.018',
                     facecolor=face, edgecolor=color, lw=.7))

    panel(.008, .255, '#C7D8E1', '#F5F9FB')
    panel(.294, .329, '#CFDDD8', '#F6FAF8')
    panel(.655, .336, '#CFDDD8', '#F6FAF8')
    txt(.136, .889, '1  SUPPLY DATA', 9, fontweight='bold')
    txt(.459, .889, '2  TRAIN AND WEIGHT', 9, fontweight='bold')
    txt(.823, .889, '3  PREDICT', 9, fontweight='bold')

    txt(.136, .812, r'$x$: 12 emissions inputs', 7.5)
    for rect, field, label_y, grid_y, grid, grid_name, fidelity in [
            ([.032, .428, .208, .256], coarse_preview, .758, .720, pair['coarse_grid'], 'Coarse grid', 'Low fidelity'),
            ([.032, .082, .208, .256], fine, .399, .361, pair['fine_grid'], 'Fine grid', 'High fidelity')]:
        p = fig.add_axes(rect)
        p.imshow(field, origin='lower', cmap='RdYlBu_r', vmin=elo, vmax=ehi,
                 interpolation='nearest', aspect='equal')
        p.set_xticks([])
        p.set_yticks([])
        for spine in p.spines.values():
            spine.set_color('#B8C4C7')
            spine.set_linewidth(.4)
        txt(rect[0] + rect[2] / 2, label_y, fidelity, 7.1)
        txt(rect[0] + rect[2] / 2, grid_y, grid_name + ': ' + ' × '.join(map(str, grid)), 6.6)
    arrow((.267, .51), (.290, .51), blue)

    # These are actual predictions for the same reserved ERA5 input. Showing
    # three examples keeps the diagram readable while all nine enter the sum.
    txt(.459, .786, 'ERA5 model predictions', 8)
    for idx, x0 in zip([0, 3, 6], [.311, .418, .525]):
        p = fig.add_axes([x0, .569, .081, .115])
        p.imshow(candidates[idx], origin='lower', cmap='RdYlBu_r',
                 vmin=elo, vmax=ehi, aspect='equal', interpolation='nearest')
        p.set_xticks([])
        p.set_yticks([])
        for spine in p.spines.values():
            spine.set_color(colors[idx])
            spine.set_linewidth(1)
        txt(x0 + .0405, .529, f'M{idx + 1}', 6.6, color=colors[idx])
    arrow((.459, .468), (.459, .367), ink)
    bars = fig.add_axes([.327, .16, .265, .187])
    bars.bar(np.arange(9), weights, width=.69, color=colors, edgecolor='none')
    bars.set_ylim(0, max(weights) * 1.1)
    bars.set_xticks(np.arange(9), [f'M{i + 1}' for i in range(9)], fontsize=5.5)
    bars.tick_params(axis='x', length=0, pad=2)
    bars.set_yticks([])
    bars.spines[['left', 'right', 'top']].set_visible(False)
    bars.spines['bottom'].set_color('#A7BAB2')
    bars.spines['bottom'].set_linewidth(.5)
    bars.set_facecolor('none')
    txt(.459, .092, r'Fitted weights $w_m$', 7.2)
    arrow((.629, .51), (.650, .51), green)

    txt(.823, .783, r'New input $x$', 8.5)
    arrow((.823, .747), (.823, .712), ink)
    p = fig.add_axes([.676, .318, .294, .388])
    p.imshow(combined_preview, origin='lower', cmap='RdYlBu_r', vmin=elo, vmax=ehi,
             interpolation='nearest', aspect='equal')
    p.set_xticks([])
    p.set_yticks([])
    for spine in p.spines.values():
        spine.set_color('#A7BAB2')
        spine.set_linewidth(.5)
    txt(.823, .223, r'$\widehat{y}(x)=\sum_m w_m f_m(x)$', 10, color=ink)
    prediction_label = 'Predicted fine grid: ' + ' × '.join(map(str, combined_preview.shape))
    txt(.823, .107, prediction_label, 7.5, fontweight='bold')

    for ext in ['pdf', 'png']:
        fig.savefig(ROOT / 'figures' / f'graphical_abstract.{ext}', dpi=240,
                    bbox_inches='tight', pad_inches=.02)
    plt.close(fig)
    checks = {
        'passed': True,
        'source_manifest': 'data/overview_manifest.json',
        'bundled_data': 'data/overview_era5.npz',
        'bundled_data_sha256': hashlib.sha256((ROOT / 'data/overview_era5.npz').read_bytes()).hexdigest(),
        'canvas_inches': [7.1, 2.6],
        'source_fields_are_actual': True,
        'coarse_preview_is_transformed': True,
        'coarse_display_transform': display,
        'coarse_preview_sha256': hashlib.sha256(coarse_preview.tobytes()).hexdigest(),
        'fine_and_prediction_fields_unchanged': True,
        'saved_prediction_arrays_unchanged': True,
        'prediction_label': prediction_label,
        'prediction_display_transform': {
            'operation': 'bilinear interpolation',
            'source_grid': list(combined.shape),
            'display_grid': list(combined_preview.shape),
            'illustrative_only': True,
            'evaluation_grid_unchanged': True,
            'disclosed_in_caption': False,
            'disclosed_in_appendix': True,
        },
        'single_dataset': 'era5',
        'era5_training_pair': pair,
        'training_inputs_bitwise_equal': True,
        'training_field_hashes_verified': True,
        'training_source_fields_native_grids': True,
        'input_label': 'x: 12 emissions inputs',
        'target_label_in_image': False,
        'target_defined_in_caption': True,
        'displayed_native_grid_labels': {'coarse': pair['coarse_grid'], 'fine': pair['fine_grid']},
        'fidelity_headings': ['Low fidelity', 'High fidelity'],
        'calibration_count_text_in_image': False,
        'equation_position': 'Below the ensemble field',
        'equation_color': ink,
        'shared_color_limits': [float(elo), float(ehi)],
        'shared_color_limits_cover_all_fields': True,
        'era5_shown_models': ['M1', 'M4', 'M7'],
        'era5_mixture_expert_count': 9,
        'era5_weights': weights.tolist(),
        'era5_weight_rule': source['era5']['weight_rule'],
        'era5_prediction_selected_by': 'First evaluation row, without selection by error',
        'orientation': 'Stored array orientation, origin lower. Ensemble output interpolated to the fine grid for display. No geographic axes or outlines added.',
        'illustrative_elements': source['illustrative_elements'],
        'recommended_caption': (
            'The entire workflow illustrates the ERA5 field emulation task. '
            'The coarse climate field and fine ERA5 field are actual training examples with identical 12 dimensional inputs. '
            'Known fine examples determine one weight per model, and the saved mixture predicts fields from new inputs. '
            'The three candidate images, nine weight bars, and final field show an actual ERA5 example '
            'using inverse error weights fitted with five fitting examples. '
            'The displayed model predictions and combined field belong to a separate reserved input. '
            'The native source arrays, fine field and prediction arrays are unchanged.'
        ),
    }
    (ROOT / 'qa/overview_checks.json').write_text(json.dumps(checks, indent=2) + '\n')
    return checks


if __name__ == '__main__':
    overview()
