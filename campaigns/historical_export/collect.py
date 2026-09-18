import csv
import json
import math
import numpy as np
from config import *

def main():
    plan=json.loads((ROOT/'plan.json').read_text())
    rows=[];runs=[]
    for path in sorted((ROOT/'runs').glob('*/result.json')):
        obj=json.loads(path.read_text())
        if obj['smoke']:continue
        runs.append(obj)
        for d in obj['datasets']:
            for method,value in d['errors'].items():
                rows.append(dict(run=obj['id'],protocol=('class_lf_seen_diagnostic' if obj.get('diagnostic_lf_seen_only') else obj['protocol']),seed=obj['seed'],
                    held_class=obj['held_class'] or '',dataset=d['dataset'],class_name=d['class_name'],
                    n=d['n'],method=method,error=value,prior_source=d['prior_source'],
                    ratio_to_fit_fixed=value/d['errors']['dataset_fixed'],
                    ratio_to_all_calibration_fixed=value/d['errors']['calibration_fixed']))
    (ROOT/'results').mkdir(exist_ok=True)
    if rows:
        with open(ROOT/'results/results.csv','w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    exports=list((ROOT/'export_results').glob('*.json'))
    failures=[p.name for p in exports if p.name.endswith('.failure.json')]
    status=dict(exported=len(exports)-len(failures),expected_exports=len(plan['tasks']),
        cached=len(list((ROOT/'cache').glob('*/audit.json'))),datasets=len(plan['datasets']),
        completed_runs=[r['id'] for r in runs],expected_runs=11,export_failures=failures,
        complete=len(runs)==11)
    write_json(ROOT/'results/status.json',status)
    lines=['# Field-conditioned ensemble pilot','',
        f"Status: {status['exported']}/{status['expected_exports']} full-precision exports; "
        f"{status['cached']}/{status['datasets']} audited datasets; {len(runs)}/11 evaluations.",'',
        'Seven experts. Primary evaluation: 21 datasets in seven classes. The eighth class, climate, is reported separately because all seven inputs appear in LF training (none in HF training). Paper predictors frozen; POD-GP reproduced from its original base training rows.',
        'Historical benchmark test rows form an exploratory meta-learning corpus. No fresh-test or matched total HF-label advantage is claimed.',
        'Field features contain only predictions. Fit/tune/evaluation groups are disjoint. Fitting functions receive only assigned fit/tune labels; evaluation weights are written and hashed before evaluation scoring.',
        'Static calibration_fixed uses every fit+tune label. Adaptive methods use fit labels for learning and tune labels for selection.',
        'In class holdout, no label from the held-out class enters fitting or tuning; the class/dataset prior falls back to a learned global mixture.','']
    lines += ['The class holdout applies to the weighting rule. The underlying experts were already trained on that dataset; this is not zero-shot PDE solution prediction.','']
    lines += ['Protocol correction: class-holdout rules and gates use global starting weights during fitting, tuning and evaluation. The earlier run used dataset-specific starting weights in fitting/tuning and a global prior at evaluation; it is preserved separately. This follow-up is exploratory, and the three unchanged case-split results are reused.','']
    for protocol in ['cases','class','class_lf_seen_diagnostic']:
        sub=[r for r in rows if r['protocol']==protocol]
        if not sub:continue
        lines += [f'## {protocol}: completed coverage only','',
            'Ratios below 1 improve on the fixed mixture using the full calibration budget. Means are first taken across split seeds for each dataset, then geometric means within each class and across classes.','',
            '| Method | Error ratio to calibration fixed | Dataset wins / covered |',
            '|---|---:|---:|']
        methods=sorted(set(r['method'] for r in sub))
        for method in methods:
            means={}
            for d in set(r['dataset'] for r in sub):
                vals=[r for r in sub if r['dataset']==d and r['method']==method]
                bases=[r for r in sub if r['dataset']==d and r['method']=='calibration_fixed']
                means[d]=np.mean([r['error'] for r in vals])/np.mean([r['error'] for r in bases])
            cs=[np.mean([np.log(max(v,1e-15)) for d,v in means.items() if CLASS_OF[d]==c]) for c in set(CLASS_OF[d] for d in means)]
            ratio=np.exp(np.mean(cs));wins=sum(v<1-1e-6 for v in means.values())
            lines.append(f'| {method} | {ratio:.4f} | {wins}/{len(means)} |')
        lines += ['', 'Oracle rows use evaluation answers and are diagnostic bounds, not deployable methods.','']
    if failures:lines+=['Export failures: '+', '.join(failures),'']
    lines += ['## Scope and interpretation','',
        'Three case splits (seeds 71, 172, 273), plus seven strict class holdouts and one separately flagged climate diagnostic. Matching input vectors across old/fixed Poisson and cavity versions stay in the same split.',
        'Climate has only seven historical cases, all seen as LF training inputs. It never supplies fitting/tuning labels and is excluded from primary aggregates. Dataset counts and overlap audits are retained.',
        'Missing current checkpoint coverage excludes sharp Allen–Cahn, Fisher–KPP and phase-field crystal. Climate is represented only in a separate LF-seen diagnostic.',
        'Known legacy data defects remain visible (including ext Helmholtz and the old Poisson/cavity versions). They are not dropped based on outcomes.',
        'Field gates have 20 shared or 140 model-specific linear coefficients and bounded logit changes. Validation can retain the original prior. Decision trees have at most depth three.',
        'Metadata-only trees and constant-feature gate ablations test whether per-case field information adds value beyond dataset descriptors and learned fixed preferences.',
        'A full-precision export avoids float16 quantization dominating the smallest errors. Classical fields are restored to raw units with training-derived scales, and targets/row identities are checked across experts.',
        'Neural exports use strict FP32 (matmul and convolution TF32 disabled). A two-mode replay isolated a large TF32 effect in a very-low-error FIRE case. Historical leaderboard errors are not used as mixture baselines.',
        'Runtime is measured for this pilot. Total base-model training costs are not matched; generating all candidate predictions requires running all experts.','']
    (ROOT/'results/RESULTS.md').write_text('\n'.join(lines))
    print(json.dumps(status,indent=2))

if __name__=='__main__':main()
