#!/usr/bin/env python3
"""Frozen K5 reported loss control. Run fit, then evaluate saved weights only."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import sys

import numpy as np
from build_data import ordered_datasets

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/loss_control'
METHODS = ['single_l2', 'inverse_mse', 'full', 'direct_l2']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def norm_errors(g, w):
    q = np.einsum('m,nmk,k->n', w, g, w)
    scale = np.maximum(np.max(np.abs(g), axis=(1, 2)), 1e-300)
    if np.any(q < -1e-12 * scale):
        raise ValueError('Indefinite mixture quadratic form')
    return np.sqrt(np.maximum(q, 0.0))


def factors(g):
    matrices, records = [], []
    for c in g:
        c = (c + c.T) / 2
        lam, vectors = np.linalg.eigh(c)
        spectral = max(float(np.max(np.abs(lam))), 1e-300)
        if float(lam.min()) < -1e-12 * spectral:
            raise ValueError('Gram has negative eigenvalues beyond recorded roundoff tolerance')
        a = np.sqrt(np.maximum(lam, 0.0))[:, None] * vectors.T
        records.append(dict(min_eigenvalue=float(lam.min()),
                            relative_negative_eigenvalue=float(min(lam.min(), 0.0) / spectral),
                            factor_relative_residual=float(np.max(np.abs(a.T @ a - c)) / spectral)))
        matrices.append(a)
    return matrices, records


def fit_direct(g):
    import cvxpy as cp
    k, m, _ = g.shape
    scale = max(float(np.trace(g.mean(0)) / m), 1e-300)
    aa, psd = factors(g / scale)
    w, t = cp.Variable(m), cp.Variable(k)
    constraints = [w >= 0, cp.sum(w) == 1]
    constraints += [cp.SOC(t[i], aa[i] @ w) for i in range(k)]
    problem = cp.Problem(cp.Minimize(cp.sum(t) / k), constraints)
    problem.solve(solver='CLARABEL', tol_gap_abs=1e-10, tol_gap_rel=1e-10,
                  tol_feas=1e-9, max_iter=500)
    if problem.status != 'optimal':
        raise RuntimeError(f'Conic optimization did not report optimal: {problem.status}')
    raw = np.array(w.value, float)
    residual = max(abs(float(raw.sum()) - 1.0), -float(raw.min()))
    if not np.isfinite(raw).all() or residual > 1e-8:
        raise RuntimeError(f'Nonfeasible weights: {residual}')
    weights = np.maximum(raw, 0.0)
    weights /= weights.sum()
    objective = float(norm_errors(g, weights).mean())
    norm_objective = objective / np.sqrt(scale)
    cone_residual = max(float(np.linalg.norm(a @ raw) - ti) for a, ti in zip(aa, t.value))
    return weights, dict(status=problem.status, iterations=problem.solver_stats.num_iters,
                         objective=objective, scale=scale, primal_simplex_residual=residual,
                         primal_cone_residual=cone_residual,
                         normalized_objective_residual=float(norm_objective-problem.value),
                         psd=psd)


def selfcheck():
    # The review's two-case analytic example has direct optimum at A (weight one).
    errors = np.array([[0., 1.1], [2., 1.1]])
    g = np.einsum('nm,nk->nmk', errors, errors)
    w, diag = fit_direct(g)
    assert abs(w[0] - 1.) < 1e-7
    assert abs(norm_errors(g, w).mean() - 1.) < 1e-8
    assert abs(norm_errors(g, np.array([11/101, 90/101])).mean() - 110/101) < 1e-12
    try:
        factors(np.array([[[1., 2.], [2., 1.]]]))
    except ValueError:
        rejected_indefinite = True
    else:
        raise AssertionError('Indefinite Gram accepted')
    rng = np.random.default_rng(938)
    e = rng.normal(size=(7, 4, 30))
    grams = np.einsum('nmp,nkp->nmk', e, e)
    ww = np.array([.1, .2, .3, .4])
    assert np.max(np.abs(norm_errors(grams, ww) - np.linalg.norm(np.einsum('m,nmp->np', ww, e), axis=1))) < 1e-12
    return dict(counterexample_optimal_weight=w.tolist(),
                counterexample_objective=diag['objective'],
                indefinite_gram_rejected=rejected_indefinite, field_identity_passed=True)


def load_case(run):
    split = json.loads((run/'split.json').read_text())
    ds = split['dataset']
    source = ROOT/'data/review_grams'/ds
    audit = json.loads((source/'audit.json').read_text())
    archive = json.loads((run/'fit.json').read_text())
    assert archive['models'] == audit['models']
    with np.load(source/'features.npz') as f:
        ids = np.array(f['original_rows'])
        groups = np.array(f['groups'])
    mapping = {int(row): n for n,row in enumerate(ids)}
    selected = {}
    for role, entries in [('calibration', split['calibration']['5']), ('evaluation', split['evaluation'])]:
        indices = [mapping[int(row['row'])] for row in entries]
        assert all(str(groups[i]) == row['group'] for i,row in zip(indices,entries))
        selected[role] = np.array(indices)
    assert len(selected['calibration']) == 5
    assert not set(selected['calibration']) & set(selected['evaluation'])
    with np.load(source/'labels.npz') as f:
        all_g = np.array(f['gram'])
    return ds, source, archive, selected, all_g


from paper_scope import retained, HISTORICAL_COUNT

def fit():
    import cvxpy, clarabel
    OUT.mkdir(exist_ok=True)
    checks = selfcheck()
    locked, records = {}, {}
    runs = sorted((ROOT/'data/historical_runs').glob('*'))
    runs = [r for r in runs if (r/'split.json').exists() and retained(json.loads((r/'split.json').read_text())['dataset'])]
    assert len(runs) == 3 * HISTORICAL_COUNT
    for run in runs:
        ds, source, archive, ids, all_g = load_case(run)
        g = all_g[ids['calibration']]
        ref_g = np.array(archive['fits']['5']['calibration_mean_gram'])
        mismatch = float(np.max(np.abs(g.mean(0) - ref_g)))
        assert np.allclose(g.mean(0), ref_g, rtol=1e-10, atol=1e-20), (run.name, mismatch)
        with np.load(run/'locked_weights.npz') as z:
            reference = {m: np.array(z['b5__'+m]) for m in METHODS[:-1]}
        weights, diagnostics = fit_direct(g)
        references = {m:float(norm_errors(g,w).mean()) for m,w in reference.items()}
        all_single = np.sqrt(np.maximum(np.diagonal(g,axis1=1,axis2=2),0)).mean(0)
        limit = min(references['full'], float(all_single.min()))
        assert diagnostics['objective'] <= limit * (1+1e-7), (run.name, diagnostics['objective'], limit)
        for m,w in {**reference,'direct_l2':weights}.items():
            locked[run.name+'___'+m] = w
        diagnostics.update(dataset=ds, n_calibration=5,
                           source_sha256={f:sha(source/f) for f in ['labels.npz','features.npz','audit.json']},
                           archive_sha256={f:sha(run/f) for f in ['split.json','fit.json','locked_weights.npz']},
                           calibration_mean_gram_max_absolute_difference=mismatch,
                           reference_calibration_objectives=references)
        records[run.name] = diagnostics
        print('fit',run.name,flush=True)
    # This file is completed before evaluation reads a single evaluation Gram.
    np.savez_compressed(OUT/'locked_weights.npz', **locked)
    metadata = dict(scope='Post hoc, previously inspected historical predictions',
                    protocol_sha256=sha(ROOT/'revision/LOSS_CONTROL_PROTOCOL.md'),
                    script_sha256=sha(__file__),locked_weights_sha256=sha(OUT/'locked_weights.npz'),
                    numpy_version=np.__version__,cvxpy_version=cvxpy.__version__,clarabel_version=clarabel.__version__,
                    selfcheck=checks,runs=records)
    dump(OUT/'fit.json',metadata)


def evaluate():
    fit_record=json.loads((OUT/'fit.json').read_text())
    assert sha(OUT/'locked_weights.npz') == fit_record['locked_weights_sha256']
    assert sha(ROOT/'revision/LOSS_CONTROL_PROTOCOL.md') == fit_record['protocol_sha256']
    # Verify the exact implementation that produced the archived weights.
    # Reporting scope can change without falsifying their original fit identity.
    fit_script = Path(__file__) if sha(__file__) == fit_record['script_sha256'] else OUT/'fit_script.py'
    assert sha(fit_script) == fit_record['script_sha256']
    percase, records = {}, []
    with np.load(OUT/'locked_weights.npz') as locked:
        for name, diagnostics in fit_record['runs'].items():
            if not retained(diagnostics['dataset']):continue
            run=ROOT/'data/historical_runs'/name
            ds, source, archive, ids, all_g=load_case(run)
            assert all(sha(source/f)==v for f,v in diagnostics['source_sha256'].items())
            assert all(sha(run/f)==v for f,v in diagnostics['archive_sha256'].items())
            test=all_g[ids['evaluation']]
            factors(test)  # Explicit PSD validation before any square root.
            scores={}
            with np.load(run/'per_case_errors.npz') as old:
                for method in METHODS:
                    w=locked[name+'___'+method]
                    errs=norm_errors(test,w)
                    if method!='direct_l2':
                        assert np.allclose(errs,old['b5__'+method],rtol=1e-8,atol=1e-12), (name,method,float(np.max(np.abs(errs-old['b5__'+method]))))
                    percase[name+'___'+method]=errs
                    scores[method]=float(errs.mean())
            row=dict(run=name,dataset=ds,class_name=json.loads((run/'result.json').read_text())['class_name'],n_evaluation=len(test),errors=scores)
            records.append(row)
    np.savez_compressed(OUT/'per_case_errors.npz',**percase)
    datasets=ordered_datasets({r['dataset'] for r in records})
    classes={d:next(r['class_name'] for r in records if r['dataset']==d) for d in datasets}
    means={d:{m:float(np.mean([r['errors'][m] for r in records if r['dataset']==d])) for m in METHODS} for d in datasets}
    comparisons={}
    for method,reference in [(m,'single_l2') for m in METHODS[1:]]+[('direct_l2','full'),('direct_l2','inverse_mse')]:
        ratios={d:means[d][method]/means[d][reference] for d in datasets}
        class_logs=[np.mean([np.log(ratios[d]) for d in datasets if classes[d]==c]) for c in sorted(set(classes.values()))]
        comparisons[method+'_vs_'+reference]=dict(class_ratio=float(np.exp(np.mean(class_logs))),
            dataset_ratio=float(np.exp(np.mean(np.log(list(ratios.values()))))),
            wins=sum(v<.99 for v in ratios.values()),losses=sum(v>1.01 for v in ratios.values()),
            neutral=sum(.99<=v<=1.01 for v in ratios.values()),ratios=ratios)
    out=dict(scope=fit_record['scope'],n_datasets=len(datasets),n_partitions=len(records),n_classes=len(set(classes.values())),
             budget=5,locked_weights_sha256=fit_record['locked_weights_sha256'],
             records=records,means=means,comparisons=comparisons)
    dump(OUT/'evaluation.json',out)
    names={'inverse_mse':'Inverse error mixture','full':'Fitted mixture','direct_l2':'Relative $L^2$ fit'}
    lines=[r'\begin{tabular}{lrrrr}',r'\toprule',r'Method & Class ratio & Dataset ratio & Wins & Losses \\',r'\midrule']
    for m in METHODS[1:]:
        c=comparisons[m+'_vs_single_l2']
        lines.append(f"{names[m]} & {c['class_ratio']:.3f} & {c['dataset_ratio']:.3f} & {c['wins']} & {c['losses']} \\\\")
    lines += [r'\bottomrule',r'\end{tabular}']
    (ROOT/'tables/loss_control.tex').write_text('\n'.join(lines)+'\n')
    (OUT/'per_dataset.csv').write_text('dataset,class,selected,inverse,squared_fit,relative_l2_fit\n'+'\n'.join(','.join([d,classes[d]]+[str(means[d][m]) for m in METHODS]) for d in datasets)+'\n')
    checks=dict(passed=True, n_partitions=len(records),n_datasets=len(datasets),budget=5,
                reference_evaluation_replay_passed=True,source_hashes_passed=True,
                all_weights_locked_before_evaluation=True,selfcheck=fit_record['selfcheck'],
                max_primal_simplex_residual=max(r['primal_simplex_residual'] for r in fit_record['runs'].values() if retained(r['dataset'])),
                min_relative_gram_eigenvalue=min(p['relative_negative_eigenvalue'] for r in fit_record['runs'].values() if retained(r['dataset']) for p in r['psd']),
                max_calibration_objective_ratio_to_original=max(r['objective']/r['reference_calibration_objectives']['full'] for r in fit_record['runs'].values() if retained(r['dataset'])),
                locked_weights_sha256=fit_record['locked_weights_sha256'])
    dump(ROOT/'qa/loss_control_checks.json',checks)
    print(json.dumps({k:{a:b for a,b in v.items() if a!='ratios'} for k,v in comparisons.items()},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['fit','evaluate'])
    args=parser.parse_args()
    {'fit':fit,'evaluate':evaluate}[args.stage]()
