"""Collect both model pools on identical cases without test-based method selection."""
import json,csv
import numpy as np
from config import ROOT,sha,write_json

def main():
    plan=json.loads((ROOT/'PLAN.json').read_text());records=[];rows=[];checks=[]
    for pool in plan['pools']:
        for seed in plan['seeds']:
            folder=ROOT/'runs'/f'{pool}__s{seed}'
            if not (folder/'result.json').exists():continue
            r=json.loads((folder/'result.json').read_text());fit=json.loads((folder/'fit.json').read_text())
            split=json.loads((folder/'split.json').read_text())
            assert sha(folder/'fit.json')==r['fit_sha256']
            assert sha(folder/'split.json')==fit['split_sha256']
            assert sha(folder/'locked_weights.npz')==fit['locked_weights_sha256']==r['locked_weights_sha256']
            assert fit['weights_locked_before_evaluation_scoring']
            if pool=='seven':assert fit['original_static_controls_match']
            assert fit['fit_and_tune_receive_only_assigned_labels'] and not fit['features_use_truth']
            groups=[{x['group'] for x in split[k]} for k in ['fit','tune','evaluation']]
            assert not (groups[0]&groups[1] or groups[0]&groups[2] or groups[1]&groups[2])
            for name,h in fit['source_sha256'].items():assert sha(ROOT/name)==h,name
            with np.load(folder/'locked_weights.npz') as z:
                for k in z.files:
                    if k in ['dataset','row']:continue
                    w=z[k];assert np.isfinite(w).all() and w.min()>=-1e-12 and np.allclose(w.sum(1),1)
            records.append(r);checks.append(dict(pool=pool,seed=seed,passed=True))
            for item in r['datasets']:
                for method,error in item['errors'].items():
                    rows.append(dict(pool=pool,seed=seed,dataset=item['dataset'],class_name=item['class_name'],n=item['n'],method=method,error=error))
    complete=len(records)==len(plan['seeds'])*len(plan['pools'])
    write_json(ROOT/'results/status.json',dict(complete=complete,completed=checks,expected_runs=6))
    assert complete, 'All planned fits must finish before aggregate reporting'
    for seed in plan['seeds']:
        a=json.loads((ROOT/'runs'/f'seven__s{seed}'/'split.json').read_text())
        b=json.loads((ROOT/'runs'/f'nine__s{seed}'/'split.json').read_text())
        assert a==b
    with open(ROOT/'results/results.csv','w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    datasets=plan['datasets'];class_of={r['dataset']:r['class_name'] for r in rows};classes=sorted(set(class_of.values()))
    means={};methods={}
    for pool in plan['pools']:
        part=[r for r in records if r['pool']==pool];methods[pool]=list(part[0]['datasets'][0]['errors'])
        means[pool]={d:{m:float(np.mean([r['error'] for r in rows if r['pool']==pool and r['dataset']==d and r['method']==m])) for m in methods[pool]} for d in datasets}
    def aggregate(ratios):
        by_class={cc:float(np.exp(np.mean([np.log(ratios[d]) for d in datasets if class_of[d]==cc]))) for cc in classes}
        return dict(class_balanced_ratio=float(np.exp(np.mean(np.log(list(by_class.values()))))),wins=sum(v<1-1e-6 for v in ratios.values()),
                    ties=sum(abs(v-1)<=1e-6 for v in ratios.values()),dataset_ratios=ratios,class_ratios=by_class)
    summaries={}
    for pool in plan['pools']:
        mean=means[pool]
        comparisons={base:{m:aggregate({d:mean[d][m]/mean[d][base] for d in datasets}) for m in methods[pool]}
                     for base in ['dataset_fixed','calibration_fixed','gate_current','best_single_full']}
        splits={}
        for r in records:
            if r['pool']!=pool:continue
            splits[str(r['seed'])]={m:aggregate({q['dataset']:q['errors'][m]/q['errors']['calibration_fixed'] for q in r['datasets']})['class_balanced_ratio'] for m in methods[pool]}
        summaries[pool]=dict(comparisons=comparisons,split_ratios_to_full_calibration=splits,
                            gates={str(r['seed']):r['gates'] for r in records if r['pool']==pool},mean_errors=mean)
    between={m:aggregate({d:means['nine'][d][m]/means['seven'][d][m] for d in datasets}) for m in methods['seven'] if not m.startswith('expert:')}
    write_json(ROOT/'results/summary.json',dict(pools=summaries,nine_vs_seven=between,
        semantics='Dataset mean errors averaged over three partitions, then geometric error ratios balanced within/across seven classes.'))
    write_json(ROOT/'results/QA.json',dict(passed=True,runs=checks,source_hashes_verified=True,disjoint_groups=True,
        matched_pool_splits=True,convex_weights=True,original_seven_static_controls_reproduced=True,weights_locked_before_scoring=True,
        scope='Artifact consistency; historical evaluations remain exploratory.'))
    text=['# Additional inputs, local field features and two more experts','',
          'Seven versus nine experts, evaluated on the SAME 20 datasets, seven classes and three case partitions.',
          'The nine-expert pool adds uqcorr_transolver_pred and uqcorr_convnext_pred (seed 42, K=6, predicted coarse ensemble input).',
          'No base model was retrained. The original seven strict-FP32 outputs and saved float32 corrector predictions are reused.',
          'Corrector TF32 flags were not recorded historically. Both pools use identical canonical raw-unit targets.',
          'Input identities, target fields, grids and no overlap with corrector training inputs were audited.',
          'One weight per model for the whole field; no pixel-specific weights. Only known-dataset case holdout is tested.',
          'Sharp Cahn-Hilliard lacks both additional predictions; it is excluded from BOTH pools. Climate remains excluded.',
          'Historical benchmark cases are reused: exploratory, not fresh confirmation. No lower-total-HF-label claim.','']
    for pool in plan['pools']:
        cmp=summaries[pool]['comparisons'];mean=means[pool]
        text += [f'## {pool} experts','', '| Method | Ratio to fit-only fixed | Ratio to full-calibration fixed | Wins / ties / 20 versus full calibration |','|---|---:|---:|---|']
        for m in methods[pool]:
            a=cmp['dataset_fixed'][m];b=cmp['calibration_fixed'][m]
            text.append(f"| {m} | {a['class_balanced_ratio']:.5f} | {b['class_balanced_ratio']:.5f} | {b['wins']} / {b['ties']} / 20 |")
        text += ['', '| Split | Variant | Active | Selected update | Penalty | Coefficients |','|---|---|---|---:|---:|---:|']
        for r in records:
            if r['pool']!=pool:continue
            for name,g in r['gates'].items():text.append(f"| {r['seed']} | {name} | {g['active']} | {g['best_step']} | {g['penalty']} | {g['coefficient_count']} |")
        text += ['', '| Dataset | Full-calibration fixed | Current | + inputs | + local | + both |','|---|---:|---:|---:|---:|---:|']
        for d in datasets:
            vals=[mean[d][m]*100 for m in ['calibration_fixed','gate_current','gate_input','gate_local','gate_input_local']]
            text.append('| '+d+' | '+' | '.join(f'{v:.6g}%' for v in vals)+' |')
    text += ['', '## Effect of adding the two correctors','', '| Method | Nine / seven error | Dataset wins / 20 |','|---|---:|---:|']
    for m,q in between.items():text.append(f"| {m} | {q['class_balanced_ratio']:.5f} | {q['wins']}/20 |")
    text += ['', 'Ratios below 1 are better. Aggregate ratios balance classes geometrically; they are not arithmetic average improvements.',
             'dataset_fixed and best_single use fitting labels. calibration_fixed and best_single_full use fitting+tuning labels.',
             'Gates fit on fitting labels, with penalty/update/fallback selected on tuning labels. constant_* supplies per-dataset fitting mean features to that same fitted gate.',
             'The seven-expert static controls reproduce earlier saved weights within 1e-7; all gates are refitted on the common 20-dataset corpus.',
             'Related-version inputs keep the same fit/tune/evaluation roles. Original base-training seed is 42; split seeds are not independent base-model replications.',
             'Known legacy defects and tiny legacy cavity (two evaluation cases per split) remain visible. All models cost inference; base training costs are not matched.',
             'See PLAN.json, SOURCE.json, cache audits, and runs/*/{fit.json,split.json,locked_weights.npz}.']
    (ROOT/'results/RESULTS.md').write_text('\n'.join(text)+'\n')
    print('Complete: six pool/split fits, four variants each; audits passed.')
    for pool in plan['pools']:
        for m in ['gate_current','gate_input','gate_local','gate_input_local']:
            q=summaries[pool]['comparisons']['calibration_fixed'][m];print(pool,m,'ratio',q['class_balanced_ratio'],'wins',q['wins'])
    print('Added experts fixed mixture ratio',between['calibration_fixed']['class_balanced_ratio'])

if __name__=='__main__':main()
