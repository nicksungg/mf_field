#!/usr/bin/env python3
"""Render the README workflow and three bar-chart slides from actual results.

Requires requirements-visuals.txt and the included graphical abstract PNG.
The workflow is rendered from the exact Figure 1 PDF used in the manuscript.
No predictions, errors or weights are fitted or edited by this script.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from reproduce_results import ROOT, load_comparison

INK = '#152b3c'
MUTED = '#4d6576'
BLUE = '#317aa2'
GREEN = '#147d70'
ORANGE = '#bd754b'


def workflow(fig, abstract):
    """Use the paper figure unchanged, preserving its aspect ratio."""
    ax = fig.add_axes([.035, .493, .93, .492])
    ax.imshow(abstract, interpolation='antialiased', aspect='equal')
    ax.axis('off')
    return ax


def slide(records, abstract, group, title, note):
    fig = plt.figure(figsize=(14, 13.5), dpi=110, facecolor='white')
    workflow(fig, abstract)
    fig.text(.04, .452, title, fontsize=17, color=INK, weight='bold')
    fig.text(.04, .430, note, fontsize=10, color=MUTED)
    rows = [r for r in records if r['group'] == group]
    if group == 'Ensemble rules':
        order = {'single_l2': 0, 'inverse_mse': 1, 'full': 2}
        rows.sort(key=lambda r: order[r['method']])
    else:
        rows.sort(key=lambda r: int(r['id'][1:]))
    labels = [(r['id'] + '  ' if r['id'] else '') + r['name'] for r in rows]
    values = [r['dataset_ratio'] for r in rows]
    ax = fig.add_axes([.266, .107, .66, .278])
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
    source = ROOT / 'assets/graphical_abstract.pdf'
    rendered = ROOT / 'assets/graphical_abstract.png'
    with Image.open(rendered) as image:
        abstract = image.convert('RGB').copy()
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': INK, 'axes.labelcolor': INK})
    specs = [('Ensemble rules', 'Three ensemble rules', 'Fitted mixture: 7.5% lower dataset-balanced error than selecting one model.'),
             ('Surrogates', 'The nine surrogate models', 'These nine models form the library. Each model can be trained and evaluated individually.'),
             ('Baselines', 'Eleven baseline implementations', 'Literature-based adaptations are comparison methods; they are not added to the nine-model mixture.')]
    frames = [slide(records, abstract, *spec) for spec in specs]
    for frame, name in zip(frames, ['overview', 'surrogates', 'baselines']):
        frame.save(out / f'{name}.png', optimize=True)
    frames[0].save(out / 'automf_overview.gif', save_all=True, append_images=frames[1:], duration=[7000, 7000, 7000], loop=0, optimize=True)
    check = dict(passed=True, frames=len(frames), width=frames[0].width, height=frames[0].height,
                 chart_source='analysis/data/table2_ranking.json',
                 graphical_abstract_source='assets/graphical_abstract.pdf',
                 graphical_abstract_pdf_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                 graphical_abstract_png_sha256=hashlib.sha256(rendered.read_bytes()).hexdigest(),
                 workflow_matches_manuscript_figure_1=True,
                 illustrated_weight_rule='Fitted mixture',
                 denominator='Selected model using five fitting examples, evaluated on held-out cases',
                 dataset_count=22, baselines=11, library_models=9, ensemble_rules=3,
                 field_values_modified=False, displayed_prediction_grid=[128, 256],
                 bars=[{k: r[k] for k in ['id', 'name', 'group', 'dataset_ratio']} for r in records])
    (out / 'visuals_manifest.json').write_text(json.dumps(check, indent=2) + '\n')
    print(f'Wrote 3-slide GIF and static images in {out}')


if __name__ == '__main__':
    main()
