#!/usr/bin/env python3
"""Render the README workflow and three bar-chart slides from actual results.

Requires requirements-visuals.txt and analysis/data/overview_era5.npz (included in the review ZIP).
No predictions, errors or weights are fitted or edited by this script.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
from PIL import Image

from reproduce_results import ROOT, load_comparison

INK = '#152b3c'
MUTED = '#4d6576'
BLUE = '#317aa2'
GREEN = '#147d70'
ORANGE = '#bd754b'
COLORS = ['#226f9b', '#3a8fbb', '#76a2c0', '#5d8095', '#737baf', '#ac92ba', '#d5a763', '#488f82', '#84b6a2']


def workflow(fig, arrays):
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis('off')
    fig.text(.04, .946, 'AutoMF', fontsize=27, weight='bold', color=INK)
    fig.text(.194, .949, 'Automated ensembles for multifidelity field prediction', fontsize=17, color=INK)
    fig.text(.04, .906, 'Train a diverse library. Fit its weights. Predict a fine field from new parameters.', fontsize=13, color=MUTED)

    panels = [(.035, .255, '1  LEARN FROM COARSE + FINE DATA'),
              (.322, .342, '2  COMBINE NINE SURROGATES'), (.696, .267, '3  PREDICT AT A NEW INPUT')]
    for x, width, title in panels:
        ax.add_patch(FancyBboxPatch((x, .576), width, .288, boxstyle='round,pad=.006,rounding_size=.014',
                                   facecolor='#f2f6f8', edgecolor='#d4e0e6', linewidth=1))
        fig.text(x + width / 2, .839, title, ha='center', fontsize=10, weight='bold', color=INK)
    for x1, x2 in [(.294, .317), (.668, .690)]:
        ax.add_patch(FancyArrowPatch((x1, .72), (x2, .72), arrowstyle='-|>', mutation_scale=17, color=GREEN, lw=1.6))
    fig.text(.163, .811, r'ERA5 example: $x$ = 12 emissions inputs', ha='center', fontsize=10, color=MUTED)
    coarse = arrays['era5_training_coarse']
    fine = arrays['era5_training_fine']
    candidates = arrays['era5_candidate_fields']
    weights = arrays['era5_inverse_weights']
    prediction = arrays['era5_mixture']
    limits = min(coarse.min(), fine.min(), prediction.min()), max(coarse.max(), fine.max(), prediction.max())

    def field(rect, values):
        p = fig.add_axes(rect)
        p.imshow(values, origin='lower', cmap='RdYlBu_r', vmin=limits[0], vmax=limits[1], interpolation='nearest', aspect='equal')
        p.set_xticks([])
        p.set_yticks([])
        for s in p.spines.values():
            s.set_color('#acbfc7')
            s.set_linewidth(.5)

    field([.05, .619, .105, .138], coarse)
    field([.17, .619, .105, .138], fine)
    fig.text(.102, .777, 'Low fidelity', ha='center', fontsize=10, color=INK)
    fig.text(.222, .777, r'High fidelity $y$', ha='center', fontsize=10, color=INK)
    fig.text(.102, .597, '192 × 384', ha='center', fontsize=10, color=MUTED)
    fig.text(.222, .597, '721 × 1440', ha='center', fontsize=10, color=MUTED)

    for index in range(9):
        x = .343 + index * .034
        ax.add_patch(FancyBboxPatch((x, .765), .027, .035, boxstyle='round,pad=.002,rounding_size=.004',
                                   facecolor=COLORS[index], edgecolor='none'))
        fig.text(x + .0135, .777, f'M{index + 1}', color='white', fontsize=9, ha='center')
    fig.text(.493, .738, 'Separate fine examples determine weights', ha='center', fontsize=10, color=MUTED)
    bars = fig.add_axes([.347, .633, .292, .091])
    bars.bar(np.arange(9), weights, color=COLORS)
    bars.set_ylim(0, .27)
    bars.set_xticks(np.arange(9), [f'M{i + 1}' for i in range(9)], fontsize=8)
    bars.tick_params(axis='both', length=0)
    bars.set_yticks([])
    bars.set_facecolor('none')
    bars.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
    fig.text(.493, .595, 'Saved inverse error weights for ERA5', ha='center', fontsize=9, color=MUTED)
    field([.746, .651, .166, .119], prediction)
    fig.text(.8295, .800, r'New $x$ → nine predictions → mixture', ha='center', fontsize=10, color=MUTED)
    fig.text(.8295, .620, r'$\widehat{y}(x)=\sum_{m=1}^{9}w_m f_m(x)$', ha='center', fontsize=13, color=INK)
    fig.text(.8295, .591, 'Prediction working grid: 128 × 256', ha='center', fontsize=9, color=MUTED)
    fig.text(.04, .548, 'ERA5 training pair at left; a different reserved input at right. No new simulation is needed at prediction time.',
             fontsize=9, color=MUTED)
    return ax


def slide(records, arrays, group, title, note):
    fig = plt.figure(figsize=(14, 10), dpi=110, facecolor='white')
    workflow(fig, arrays)
    fig.text(.04, .495, title, fontsize=17, color=INK, weight='bold')
    fig.text(.04, .466, note, fontsize=10, color=MUTED)
    rows = [r for r in records if r['group'] == group]
    if group == 'Ensemble rules':
        order = {'single_l2': 0, 'inverse_mse': 1, 'full': 2}
        rows.sort(key=lambda r: order[r['method']])
    else:
        rows.sort(key=lambda r: int(r['id'][1:]))
    labels = [(r['id'] + '  ' if r['id'] else '') + r['name'] for r in rows]
    values = [r['dataset_ratio'] for r in rows]
    ax = fig.add_axes([.266, .115, .66, .308])
    color = {'Surrogates': BLUE, 'Baselines': ORANGE, 'Ensemble rules': GREEN}[group]
    ax.barh(np.arange(len(rows)), values, color=color, height=.64)
    ax.set_yticks(np.arange(len(rows)), labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values) * 1.14)
    ax.axvline(1, color=INK, ls='--', lw=1, zorder=3)
    ax.tick_params(axis='y', length=0, pad=10)
    ax.tick_params(axis='x', labelsize=9, colors=MUTED)
    ax.set_xlabel('Error / Selected model error  ·  geometric mean across 22 datasets  ·  lower is better', fontsize=10, labelpad=10)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color('#ccd9df')
    for index, value in enumerate(values):
        ax.text(value + max(values) * .012, index, f'{value:.3f}', va='center', color=INK, fontsize=10)
    fig.text(.04, .033, 'Reference: the M1–M9 model with the lowest error on five fitting examples for each dataset, then scored on held-out cases.', fontsize=9, color=MUTED)
    fig.text(.04, .016, 'Common evaluation cases; training resources differ. Each slide uses its own labeled linear axis. B12/B13 are additional controls.', fontsize=9, color=MUTED)
    fig.canvas.draw()
    frame = Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert('RGB')
    plt.close(fig)
    return frame


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'assets')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    _, records, _ = load_comparison()
    source = ROOT / 'analysis/data/overview_era5.npz'
    manifest = json.loads((ROOT / 'analysis/data/overview_manifest.json').read_text())
    with np.load(source, allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files}
    weights = arrays['era5_inverse_weights']
    prediction = arrays['era5_mixture']
    assert np.all(weights >= 0) and np.isclose(weights.sum(), 1)
    assert np.array_equal(prediction, np.tensordot(weights, arrays['era5_candidate_fields'], axes=(0, 0)))
    assert hashlib.sha256(prediction.tobytes()).hexdigest() == manifest['era5']['mixture_sha256']
    assert np.array_equal(arrays['era5_training_lf_parameters'], arrays['era5_training_hf_parameters'])
    for key, label in [('era5_training_coarse', 'coarse'), ('era5_training_fine', 'fine')]:
        assert hashlib.sha256(arrays[key].tobytes()).hexdigest() == manifest['era5']['training_pair'][label + '_array_sha256']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': INK, 'axes.labelcolor': INK})
    specs = [('Ensemble rules', 'Three ensemble rules', 'Fitted mixture: 7.5% lower dataset-balanced error than selecting one model.'),
             ('Surrogates', 'The nine surrogate models', 'These nine models form the library. Each model can be trained and evaluated individually.'),
             ('Baselines', 'Eleven baseline implementations', 'Literature-based adaptations are comparison methods; they are not added to the nine-model mixture.')]
    frames = [slide(records, arrays, *spec) for spec in specs]
    for frame, name in zip(frames, ['overview', 'surrogates', 'baselines']):
        frame.save(out / f'{name}.png', optimize=True)
    frames[0].save(out / 'automf_overview.gif', save_all=True, append_images=frames[1:], duration=[7000, 7000, 7000], loop=0, optimize=True)
    check = dict(passed=True, frames=len(frames), width=frames[0].width, height=frames[0].height,
                 chart_source='analysis/data/table2_ranking.json',
                 era5_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                 denominator='Selected model using five fitting examples, evaluated on held-out cases',
                 dataset_count=22, baselines=11, library_models=9, ensemble_rules=3,
                 field_values_modified=False, displayed_prediction_grid=list(prediction.shape),
                 bars=[{k: r[k] for k in ['id', 'name', 'group', 'dataset_ratio']} for r in records])
    (out / 'visuals_manifest.json').write_text(json.dumps(check, indent=2) + '\n')
    print(f'Wrote 3-slide GIF and static images in {out}')


if __name__ == '__main__':
    main()
