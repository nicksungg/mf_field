"""Post hoc frozen prediction reanalysis. Never changes historical artifacts.

The entire calibration phase writes immutable weight arrays and choices before
the scoring phase reads evaluation Gram rows. See protocols/ANALYSIS_PROTOCOL.md.
"""
from pathlib import Path
import collections
import hashlib
import importlib.util
import json
import math
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('review_ensemble_rules', DATA / 'ensemble_rules.py')
rules_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules_module)
from build_data import CLASS_OF, NAMES, ordered_datasets
from paper_scope import retained, HISTORICAL_COUNT

BUDGETS = (5, 10, 20)
RULES = ('selected_single', 'inverse_mse', 'full')
OLD_NAMES = {'selected_single': 'single_l2', 'inverse_mse': 'inverse_mse', 'full': 'full'}
from rule_labels import RULE_NAMES, canonical_label, header_label
LABELS = RULE_NAMES
REMOTE = 'archive-host:/archive/mf_field/experiments/fieldgate_features_20260913/cache/nine'


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(value):
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plain(value), indent=2) + '\n')


def aggregate(a, b, datasets):
    logs = {d: math.log(a[d] / b[d]) for d in datasets}
    classes = sorted({CLASS_OF[d] for d in datasets})
    return dict(n_datasets=len(datasets), n_classes=len(classes),
                class_ratio=math.exp(np.mean([np.mean([logs[d] for d in datasets if CLASS_OF[d] == c]) for c in classes])),
                dataset_ratio=math.exp(np.mean(list(logs.values()))),
                wins=sum(v < math.log(.99) for v in logs.values()),
                losses=sum(v > math.log(1.01) for v in logs.values()),
                neutral=sum(math.log(.99) <= v <= math.log(1.01) for v in logs.values()))


def tex_table(name, header, rows, columns):
    text = ['\\begin{tabular}{' + columns + '}', '\\toprule', ' & '.join(header_label(v) for v in header) + r' \\', '\\midrule']
    text.extend(' & '.join(canonical_label(v) for v in row) + r' \\' for row in rows)
    text.extend(['\\bottomrule', '\\end{tabular}', ''])
    (ROOT / 'tables' / name).write_text('\n'.join(text))


def source_contexts():
    contexts = []
    manifests = {}
    for source in sorted((DATA / 'historical_runs').iterdir()):
        split = load(source / 'split.json')
        fit = load(source / 'fit.json')
        dataset = split['dataset']
        if not retained(dataset):
            continue
        cache = DATA / 'review_grams' / dataset
        audit = load(cache / 'audit.json')
        assert audit['strict_eligible'] and audit['models'] == fit['models']
        for name in ('labels', 'features'):
            assert sha(cache / (name + '.npz')) == audit[name + '_sha256']
        with np.load(cache / 'features.npz') as z:
            rows, groups = z['original_rows'].copy(), z['groups'].copy()
        lookup = {int(row): i for i, row in enumerate(rows)}
        assert len(lookup) == len(rows)

        def indices(entries):
            idx = []
            for item in entries:
                assert item['dataset'] == dataset
                i = lookup[item['row']]
                assert item['group'] == groups[i]
                idx.append(i)
            return np.asarray(idx, dtype=int)

        evaluation = indices(split['evaluation'])
        calibration = {str(b): indices(split['calibration'][str(b)]) for b in BUDGETS}
        prior = set()
        for b in BUDGETS:
            ids = calibration[str(b)]
            assert prior <= set(ids) and len(ids) >= 2
            assert not set(ids) & set(evaluation)
            assert not set(groups[ids]) & set(groups[evaluation])
            prior = set(ids)
        contexts.append(dict(name=source.name, source=source, dataset=dataset, cache=cache,
                             fit=fit, split=split, rows=rows, groups=groups,
                             calibration=calibration, evaluation=evaluation))
        manifests[dataset] = dict(remote=REMOTE + '/' + dataset,
                                  local='data/review_grams/' + dataset,
                                  files={name: sha(cache / name) for name in ('audit.json', 'features.npz', 'labels.npz')},
                                  models=audit['models'], n_rows=len(rows),
                                  source_prediction_sha256=audit['source_prediction_sha256'])
    assert len(contexts) == 3 * HISTORICAL_COUNT and len(manifests) == HISTORICAL_COUNT
    dump(DATA / 'review_analysis_source_manifest.json', dict(protocol_sha256=sha(ROOT / 'protocols/ANALYSIS_PROTOCOL.md'),
                                                            sources=manifests, read_only_remote_copy=True))
    return contexts


def selected_grams(ctx, role, budget=None):
    ids = ctx['calibration'][str(budget)] if role == 'calibration' else ctx['evaluation']
    with np.load(ctx['cache'] / 'labels.npz') as z:
        g = z['gram'][ids].copy()
    assert np.isfinite(g).all()
    np.testing.assert_allclose(g, g.swapaxes(1, 2), atol=1e-18, rtol=1e-12)
    return g


def main():
    contexts = source_contexts()
    protocol_hash = sha(ROOT / 'protocols/ANALYSIS_PROTOCOL.md')
    rules_hash = sha(DATA / 'ensemble_rules.py')
    fits = []
    locked = {}
    mean_replay_max = 0.
    inverse_replay_max = 0.
    feasibility_max = 0.
    for ctx in contexts:
        for budget in BUDGETS:
            g = selected_grams(ctx, 'calibration', budget)
            archived = np.asarray(ctx['fit']['fits'][str(budget)]['calibration_mean_gram'])
            mean_replay_max = max(mean_replay_max, float(np.max(np.abs(g.mean(0) - archived))))
            np.testing.assert_allclose(g.mean(0), archived, rtol=1e-12, atol=1e-18)
            fitted, meta = rules_module.fit_auto(g)
            with np.load(ctx['source'] / 'locked_weights.npz') as old:
                inverse_replay_max = max(inverse_replay_max, float(np.max(np.abs(fitted['inverse_mse'] - old[f'b{budget}__inverse_mse']))))
                np.testing.assert_allclose(fitted['inverse_mse'], old[f'b{budget}__inverse_mse'], atol=1e-12, rtol=1e-12)
                np.testing.assert_allclose(fitted['selected_single'], old[f'b{budget}__single_l2'], atol=0, rtol=0)
            for name in (*RULES, 'auto'):
                w = fitted[name]
                assert w.min() >= -1e-12 and abs(w.sum() - 1) <= 1e-12
                feasibility_max = max(feasibility_max, abs(float(w.sum()) - 1))
                locked[f"{ctx['name']}__b{budget}__{name}"] = w
            fits.append(dict(run=ctx['name'], dataset=ctx['dataset'], budget=budget,
                             n_calibration=len(g), calibration_rows=ctx['rows'][ctx['calibration'][str(budget)]],
                             split_sha256=sha(ctx['source'] / 'split.json'), **meta))
        print('Fitted ' + ctx['name'], flush=True)
    # This file is complete before any evaluation rows are scored.
    lock_file = DATA / 'review_analysis_locked_weights.npz'
    np.savez_compressed(lock_file, **locked)
    lock_hash = sha(lock_file)
    dump(DATA / 'review_analysis_fits.json', dict(protocol_sha256=protocol_hash,
                                                rules_sha256=rules_hash,
                                                locked_weights_sha256=lock_hash, fits=fits,
                                                evaluation_scored_before_lock=False))
    print(f'All {len(fits)} fits locked. Evaluation scoring starts now.', flush=True)
    scores = []
    per_case = {}
    replay_error_max = 0.
    full_replay_relative_max = 0.
    min_scaled_eigenvalue = 0.
    for ctx in contexts:
        assert sha(lock_file) == lock_hash
        g = selected_grams(ctx, 'evaluation')
        scale = max(float(np.max(np.abs(g))), 1e-30)
        min_scaled_eigenvalue = min(min_scaled_eigenvalue, float(np.linalg.eigvalsh(g / scale).min()))
        assert min_scaled_eigenvalue >= -1e-10
        with np.load(ctx['source'] / 'per_case_errors.npz') as old_errors, np.load(ctx['source'] / 'locked_weights.npz') as old_weights:
            np.testing.assert_array_equal(ctx['rows'][ctx['evaluation']], old_errors['row'])
            for budget in BUDGETS:
                means, means_squared = {}, {}
                for name in (*RULES, 'auto'):
                    key = f"{ctx['name']}__b{budget}__{name}"
                    w = locked[key]
                    squared = np.maximum(np.einsum('m,nmk,k->n', w, g, w), 0.)
                    error = np.sqrt(squared)
                    means[name], means_squared[name] = float(error.mean()), float(squared.mean())
                    per_case[key] = error
                    if name in OLD_NAMES:
                        old_key = f'b{budget}__' + OLD_NAMES[name]
                        ow = old_weights[old_key]
                        replay = np.sqrt(np.maximum(np.einsum('m,nmk,k->n', ow, g, ow), 0.))
                        diff = float(np.max(np.abs(replay - old_errors[old_key])))
                        replay_error_max = max(replay_error_max, diff)
                        np.testing.assert_allclose(replay, old_errors[old_key], rtol=1e-10, atol=1e-12)
                        if name == 'full':
                            full_replay_relative_max = max(full_replay_relative_max, abs(means[name] / replay.mean() - 1))
                scores.append(dict(run=ctx['name'], dataset=ctx['dataset'], budget=budget,
                                   n_evaluation=len(g), mean_relative_l2=means,
                                   mean_squared_relative_l2=means_squared))
        per_case[ctx['name'] + '__evaluation_rows'] = ctx['rows'][ctx['evaluation']]
    assert sha(lock_file) == lock_hash
    np.savez_compressed(DATA / 'review_analysis_per_case_errors.npz', **per_case)
    existing = load(DATA / 'matched_baseline_summary.json')['means']
    models = load(DATA / 'individual_model_summary.json')['checks']['models']
    baselines = load(DATA / 'headline_comparisons.json')['additional_baselines']
    datasets = ordered_datasets(load(DATA / 'paper_mechanism_summary.json')['5']['mean_errors'])
    existing = {d: existing[d] for d in datasets}
    excluded = load(DATA / 'audit_sensitivity.json')['exclusions']
    # Preserve the fixed sensitivity subset after recovering the two B8 entries.
    assert all(all(m in existing[d] for m in baselines) for d in datasets)
    common = [d for d in datasets if d not in {'heat_local', 'sharp__burgers_2d'}]
    scopes = {'historical': datasets, 'audit': [d for d in datasets if d not in excluded],
              'common': common, 'audit_common': [d for d in common if d not in excluded]}
    assert len(scopes['audit']) == HISTORICAL_COUNT - len(excluded) and len(common) == HISTORICAL_COUNT - 2
    summaries = {}
    for budget in BUDGETS:
        chosen = [f for f in fits if f['budget'] == budget]
        current = [r for r in scores if r['budget'] == budget]
        means = {metric: {d: {m: float(np.mean([r[metric][m] for r in current if r['dataset'] == d]))
                               for m in (*RULES, 'auto')} for d in datasets}
                 for metric in ('mean_relative_l2', 'mean_squared_relative_l2')}
        budget_stats = {}
        for scope, ds in scopes.items():
            e = means['mean_relative_l2']
            auto = {d: e[d]['auto'] for d in ds}
            hindsight = {d: min(e[d][m] for m in RULES) for d in ds}
            # Also report hindsight choice separately per partition, a stronger oracle.
            partition_oracle = {d: float(np.mean([min(r['mean_relative_l2'][m] for m in RULES)
                                                 for r in current if r['dataset'] == d])) for d in ds}
            comparisons = {'auto / ' + m: aggregate(auto, {d: e[d][m] for d in ds}, ds) for m in RULES}
            comparisons['auto / best fixed rule per dataset'] = aggregate(auto, hindsight, ds)
            comparisons['auto / best fixed rule per partition'] = aggregate(auto, partition_oracle, ds)
            comparisons['inverse / selected'] = aggregate({d:e[d]['inverse_mse'] for d in ds}, {d:e[d]['selected_single'] for d in ds}, ds)
            comparisons['fitted / selected'] = aggregate({d:e[d]['full'] for d in ds}, {d:e[d]['selected_single'] for d in ds}, ds)
            counts = collections.Counter(f['chosen'] for f in chosen if f['dataset'] in ds)
            best_library = {d: min(existing[d][m] for m in models) for d in ds}
            best_baseline = {d: min(existing[d][m] for m in baselines if m in existing[d]) for d in ds}
            old = load(DATA / 'paper_mechanism_summary.json')[str(budget)]['mean_errors']
            headlines = {
                'Best library / best additional baseline': aggregate(best_library, best_baseline, ds),
                'Fitted / best library': aggregate({d:old[d]['full'] for d in ds}, best_library, ds),
                'Inverse / best library': aggregate({d:old[d]['inverse_mse'] for d in ds}, best_library, ds),
                'Fitted / best additional baseline': aggregate({d:old[d]['full'] for d in ds}, best_baseline, ds),
                'Fitted / selected': aggregate({d:old[d]['full'] for d in ds}, {d:old[d]['single_l2'] for d in ds}, ds),
                'Inverse / selected': aggregate({d:old[d]['inverse_mse'] for d in ds}, {d:old[d]['single_l2'] for d in ds}, ds),
                'Automatic / best library': aggregate(auto, best_library, ds),
                'Automatic / best additional baseline': aggregate(auto, best_baseline, ds),
                'Automatic / selected': aggregate(auto, {d:old[d]['single_l2'] for d in ds}, ds),
            }
            squared = means['mean_squared_relative_l2']
            squared_comparisons = {'auto / ' + m: aggregate({d:squared[d]['auto'] for d in ds}, {d:squared[d][m] for d in ds}, ds) for m in RULES}
            budget_stats[scope] = dict(datasets=ds, selection_counts={m:counts[m] for m in RULES},
                                      comparisons=comparisons, historical_headlines=headlines,
                                      squared_loss_comparisons=squared_comparisons)
        summaries[str(budget)] = dict(scopes=budget_stats, means=means)
    dump(DATA / 'review_analysis.json', dict(status='completed', interpretation='post hoc exploratory frozen prediction reanalysis',
                                            protocol_sha256=protocol_hash, rules_sha256=rules_hash,
                                            locked_weights_sha256=lock_hash, scopes=scopes, exclusions=excluded,
                                            summaries=summaries, partitions=scores))
    qa = dict(passed=True, n_datasets=len(datasets), n_partitions=len(contexts), n_fits=len(fits),
              source_hashes_verified=True, evaluation_rows_excluded_from_every_fit=True,
              all_fits_locked_before_scoring=True, locked_weights_hash_unchanged=True,
              maximum_mean_gram_replay_difference=mean_replay_max,
              maximum_inverse_weight_replay_difference=inverse_replay_max,
              maximum_simplex_residual=feasibility_max,
              minimum_scaled_evaluation_eigenvalue=min_scaled_eigenvalue,
              maximum_original_per_case_error_replay_difference=replay_error_max,
              maximum_new_full_vs_historical_full_relative_mean_error_difference=full_replay_relative_max,
              original_fixed_results_preserved=True, protocol_sha256=protocol_hash)
    dump(ROOT / 'qa/review_analysis_checks.json', qa)
    rows = []
    for budget in BUDGETS:
        for scope in ('historical', 'audit', 'common'):
            s = summaries[str(budget)]['scopes'][scope]
            for method in ('inverse_mse', 'full', 'auto'):
                key = {'inverse_mse': 'inverse / selected', 'full': 'fitted / selected', 'auto': 'auto / selected_single'}[method]
                v = s['comparisons'][key]
                rows.append([budget, len(s['datasets']), LABELS[method], f"{v['class_ratio']:.3f}", f"{v['dataset_ratio']:.3f}", f"{v['wins']}/{v['neutral']}/{v['losses']}"])
    tex_table('review_automatic.tex', ['$K$', '$N$', 'Rule', 'Class ratio', 'Dataset ratio', 'W / T / L'], rows, 'rrlrrr')
    tex_table('review_automatic_main.tex', ['$K$', 'Rule', 'Class ratio', 'Dataset ratio', 'W / T / L'],
              [[r[0], *r[2:]] for r in rows if r[1] == HISTORICAL_COUNT], 'rlrrr')
    # The manuscript reports the two fixed mixtures against the Selected model.
    # Preserve earlier selector analyses in the archive without displaying them.
    tex_table('review_fixed_budgets.tex', ['$K$', '$N$', 'Rule', 'Class ratio', 'Dataset ratio', 'W / T / L'],
              [r for r in rows if r[2] != LABELS['auto']], 'rrlrrr')
    rows = []
    for scope in ('historical', 'audit', 'common', 'audit_common'):
        s = summaries['5']['scopes'][scope]
        for name, v in s['historical_headlines'].items():
            if name.startswith('Automatic /'):
                continue
            rows.append([len(s['datasets']), name, f"{v['class_ratio']:.3f}", f"{v['dataset_ratio']:.3f}", f"{v['wins']}/{v['neutral']}/{v['losses']}"])
    tex_table('review_subsets.tex', ['$N$', 'Comparison', 'Class ratio', 'Dataset ratio', 'W / T / L'], rows, 'rlrrr')
    subset_names = {'historical':'Diagnostic set', 'audit':'Data quality subset',
                    'common':'Without Heat II and Burgers', 'audit_common':'Intersection'}
    rows = []
    for scope, scope_name in subset_names.items():
        s = summaries['5']['scopes'][scope]
        v = s['historical_headlines']
        rows.append([scope_name, len(s['datasets']),
                     *[f"{v[key]['class_ratio']:.3f} / {v[key]['dataset_ratio']:.3f}"
                       for key in ('Best library / best additional baseline',
                                   'Fitted / selected', 'Inverse / selected')]])
    tex_table('review_sensitivity_main.tex', ['Scope', '$N$', 'Library / baseline', 'Fitted / selected', 'Inverse / selected'], rows, 'lrrrr')
    rows = []
    for budget in BUDGETS:
        s = summaries[str(budget)]['scopes']['historical']
        c = s['selection_counts']
        v = s['comparisons']['auto / best fixed rule per partition']
        rows.append([budget, c['selected_single'], c['inverse_mse'], c['full'], f"{v['class_ratio']:.3f}", f"{v['dataset_ratio']:.3f}"])
    tex_table('review_selection.tex', ['$K$', 'Selected', 'Inverse', 'Fitted', 'Class regret ratio', 'Dataset regret ratio'], rows, 'rrrrrr')
    rows = []
    for d in datasets:
        e = summaries['5']['means']['mean_relative_l2'][d]
        rows.append([NAMES[d], *[f"{100*e[m]:.4g}" for m in (*RULES, 'auto')]])
    tex_table('review_automatic_per_dataset.tex', ['Dataset', 'Selected', 'Inverse', 'Fitted', 'Automatic'], rows, 'lrrrr')
    print(json.dumps(qa, indent=2))


if __name__ == '__main__':
    main()
