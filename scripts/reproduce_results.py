#!/usr/bin/env python3
"""Verify aggregate results and export readable CSVs. Optionally replay frozen analyses.

Default: needs only NumPy and the bundled JSON summaries.
--full: requires the companion analysis arrays and requirements-analysis.txt. All writes
go to a new output workspace, leaving the reference data unchanged.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RULES = {'single_l2': 'Selected model', 'inverse_mse': 'Inverse error mixture', 'full': 'Fitted mixture'}


def load_comparison(path=None):
    path = Path(path) if path else ROOT / 'analysis/data/table2_ranking.json'
    source = json.loads(path.read_text())
    datasets = json.loads((ROOT / 'configs/datasets.json').read_text())
    models = json.loads((ROOT / 'configs/models.json').read_text())
    identifiers = {v['archive_id']: (k, v['name'], 'Surrogates' if k.startswith('M') else 'Baselines')
                   for k, v in models.items()}
    identifiers.update({k: ('', v, 'Ensemble rules') for k, v in RULES.items()})
    errors = source['errors']
    assert set(errors) == set(datasets) and len(errors) == 22
    methods = list(source['statistics'])
    expected_methods = {models[f'M{i}']['archive_id'] for i in range(1, 10)}
    expected_methods |= {models[f'B{i}']['archive_id'] for i in range(1, 12)} | set(RULES)
    assert set(methods) == expected_methods
    classes = sorted({d['problem_class'] for d in datasets.values()} - {'climate'})
    assert len(classes) == 7
    records, details = [], []
    for method in methods:
        ratios = {}
        for dataset, info in datasets.items():
            value, denominator = errors[dataset][method], errors[dataset]['single_l2']
            assert np.isfinite(value) and value > 0 and np.isfinite(denominator) and denominator > 0
            ratios[dataset] = value / denominator
            details.append(dict(dataset=info['name'], dataset_id=dataset, problem_class=info['problem_class'],
                                method=method, mean_relative_l2=value, ratio_to_selected=ratios[dataset]))
        dataset_ratio = float(np.exp(np.mean(np.log(list(ratios.values())))))
        class_logs = [np.mean([np.log(ratios[d]) for d in datasets if datasets[d]['problem_class'] == c])
                      for c in classes]
        class_ratio = float(np.exp(np.mean(class_logs)))
        old = source['statistics'][method]
        assert np.isclose(dataset_ratio, old['dataset_ratio'], rtol=1e-12, atol=1e-14), method
        assert np.isclose(class_ratio, old['class_ratio'], rtol=1e-12, atol=1e-14), method
        wins, losses = sum(r < .99 for r in ratios.values()), sum(r > 1.01 for r in ratios.values())
        assert (wins, losses) == (old['wins'], old['losses'])
        ident, name, group = identifiers[method]
        records.append(dict(id=ident, name=name, group=group, method=method, datasets=len(ratios),
                            dataset_ratio=dataset_ratio, pde_class_ratio=class_ratio,
                            wins_over_1pct=wins, losses_over_1pct=losses, elo=old['elo'], elo_rank=old['rank']))
    return source, records, details


def write_csv(path, records):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def full_replay(out):
    workspace = out / 'replay'
    if workspace.exists():
        raise ValueError(f'Replay workspace exists: {workspace}. Use a new --output directory.')
    shutil.copytree(ROOT / 'analysis', workspace, ignore=shutil.ignore_patterns('__pycache__', 'figures', 'tables', 'qa'))
    for directory in ['figures', 'tables', 'qa', 'logs']:
        (workspace / directory).mkdir()
    for command in [['build_data.py'], ['build_comparisons.py'], ['build_visuals.py'],
                    ['build_field_comparison.py'], ['build_review_analysis.py'], ['review_loss_control.py', 'evaluate']]:
        log = workspace / 'logs' / (Path(command[0]).stem + '.log')
        print(f'Replaying {command[0]} ...', flush=True)
        with log.open('w') as stream:
            run = subprocess.run([sys.executable, str(workspace / 'scripts' / command[0]), *command[1:]],
                                 cwd=workspace, stdout=stream, stderr=subprocess.STDOUT)
        if run.returncode:
            raise RuntimeError(f'{command[0]} failed. See {log}')
    # This rebuild starts from per-case archives and refits the stored mechanisms.
    rebuilt, _, _ = load_comparison(workspace / 'data/table2_ranking.json')
    reference = json.loads((ROOT / 'analysis/data/table2_ranking.json').read_text())
    assert rebuilt == reference, 'Replayed comparison differs from the reference'
    return dict(passed=True, comparison_identical=True, workspace=str(workspace))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs/results')
    parser.add_argument('--full', action='store_true', help='Rebuild from frozen per-case archives and fitting records')
    parser.add_argument('--elo', action='store_true', help='Also recompute 500-order Elo from unrounded errors')
    args = parser.parse_args()
    source, records, details = load_comparison()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    checks = dict(passed=True, datasets=22, pde_datasets=21, pde_classes=7, compared_methods=len(records),
                  fitting_examples=5, reference='Lowest mean relative L2 on fitting examples among M1–M9',
                  ratios_recomputed=True, elo_recomputed=False,
                  source_sha256=hashlib.sha256((ROOT / 'analysis/data/table2_ranking.json').read_bytes()).hexdigest())
    if args.elo:
        sys.path.insert(0, str(ROOT / 'analysis/scripts'))
        from elo_ranking import rank_errors
        elo = rank_errors(source['errors'], list(source['statistics']))
        assert elo == source['elo'], 'Recomputed Elo differs'
        checks['elo_recomputed'] = True
    if args.full:
        checks['full_replay'] = full_replay(out)
    write_csv(out / 'comparison.csv', sorted(records, key=lambda r: r['elo_rank']))
    write_csv(out / 'per_dataset.csv', details)
    (out / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
    print('Verified: 22 datasets, 9 surrogates, 11 baselines and 3 ensemble rules.\n')
    for method in RULES:
        r = next(r for r in records if r['method'] == method)
        print(f'{r["name"]:23s}  dataset ratio {r["dataset_ratio"]:.4f}  PDE class ratio {r["pde_class_ratio"]:.4f}')
    print(f'\nCSV tables and verification: {out}')


if __name__ == '__main__':
    main()
