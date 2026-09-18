import json
import subprocess
import argparse
from config import *

def submit(args):
    return subprocess.check_output(['sbatch','--parsable',*args],text=True).strip().split(';')[0]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--smoke-job',type=int,required=True);args=ap.parse_args()
    out=ROOT/'GATE_LAUNCH.json'
    if out.exists():
        previous=json.loads(out.read_text())
        if previous.get('jobs'):print(out.read_text());return
        # No job was submitted: preserve the failed attempt and retry safely.
        saved=ROOT/'attempts/submission_without_jobs.json';saved.parent.mkdir(exist_ok=True)
        write_json(saved,previous);out.unlink()
    smoke=ROOT/'runs/cases__s71__smoke_darcy_generated/result.json'
    assert smoke.exists(),'Complete the real-data smoke first'
    sm=json.loads(smoke.read_text());assert sm['n_eval']==20 and sm['n_fit']==60 and sm['n_tune']==20
    exported=json.loads((ROOT/'EXPORT_LAUNCH.json').read_text())
    tasks=[dict(protocol='class',seed=71,held_class=c) for c in CLASSES]
    sources=[p for p in ROOT.iterdir() if p.suffix in ('.py','.sbatch')]
    record=dict(plan_sha256=sha(ROOT/'plan.json'),source_sha256={p.name:sha(p) for p in sources},
        tasks=tasks,smoke_job=args.smoke_job,smoke_result_sha256=sha(smoke),jobs=[],revision=2,
        revision_reason='Match global starting priors at fit/tune/evaluation for class holdout. Reuse the unchanged original case-split evaluations.',
        exclusions=EXCLUDE,no_evaluation_labels_for_fit_or_selection=True)
    # Write the contract before any task can start.
    write_json(out,record)
    try:
        datasets=json.loads((ROOT/'plan.json').read_text())['datasets']
        ready=all((ROOT/'cache'/d/'audit.json').exists() for d in datasets)
        gate_args=[]
        if ready:
            # Completed export jobs may have aged out of Slurm's dependency table.
            record['cache_ready_before_submission']=True
        else:
            complete=all((ROOT/'export_results'/f'{m}__{d}.json').exists() for m in MODELS for d in datasets)
            deps=[] if complete else ['--dependency=afterok:'+':'.join(j['id'] for j in exported['jobs'])]
            cache=submit([*deps,str(ROOT/'cache.sbatch')])
            record['jobs'].append(dict(kind='cache',id=cache));write_json(out,record)
            gate_args=['--dependency=afterok:'+cache]
        gates=submit([*gate_args,'--array=0-7%2',str(ROOT/'run.sbatch')])
        record['jobs'].append(dict(kind='gate_array',id=gates));write_json(out,record)
        report=submit(['--dependency=afterany:'+gates,str(ROOT/'collect.sbatch')])
        record['jobs'].append(dict(kind='report',id=report));write_json(out,record)
        print(json.dumps(record['jobs'],indent=2))
    finally:write_json(out,record)

if __name__=='__main__':main()
