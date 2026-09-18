"""Submit bounded GPU arrays and dependency-driven assembly/scoring jobs."""
import json
import subprocess
from repair_common import *

def main():
    if (ROOT/'LAUNCH.json').exists():
        existing=json.loads((ROOT/'LAUNCH.json').read_text())
        if existing.get('submission_complete'):
            print((ROOT/'LAUNCH.json').read_text());return
    else:existing=None
    assert json.loads((ROOT/'smoke/CPU_QA.json').read_text())['passed']
    assert json.loads((ROOT/'smoke/ENSEMBLE_QA.json').read_text())['passed']
    for m in MODELS+['fno_hf_only_control']:
        meta=json.loads((ROOT/'smoke/metadata'/f'{m}__era5.json').read_text())
        assert meta['smoke'] and meta['prediction_sha256']==sha(ROOT/'smoke/predictions'/f'{m}__era5.npz')
    for m in CORRECTORS:
        ds='sharp__phase_field_crystal_2d';meta=json.loads((ROOT/'smoke/metadata'/f'{m}__{ds}.json').read_text())
        assert meta['smoke'] and meta['prediction_sha256']==sha(ROOT/'smoke/predictions'/f'{m}__{ds}.npz')
    assert (ROOT/'smoke/uqcorr/raw/plain__sharp__phase_field_crystal_2d__L2__F0of5__s42.json').exists()
    plan=json.loads((ROOT/'PLAN.json').read_text())
    sources={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*.py') if '__pycache__' not in p.parts}
    sources.update({p.name:sha(p) for p in ROOT.glob('*.sbatch')})
    for name in ['PLAN.json','ROLES.json','PAIRING_AUDIT.json']:sources[name]=sha(ROOT/name)
    if existing:
        assert json.loads((ROOT/'SOURCE.json').read_text())==sources,'Source changed after partial submission'
    else:write_json(ROOT/'SOURCE.json',sources)
    verify_source()
    record=existing or dict(source_manifest_sha256=sha(ROOT/'SOURCE.json'),excluded_nodes=EXCLUDE,jobs=[])
    def submit(name,script,arguments,options=None):
        previous=[j for j in record['jobs'] if j['name']==name]
        if previous:return previous[0]['id']
        command=['sbatch','--parsable','--job-name='+name,'--exclude='+EXCLUDE]
        command+=options or [];command+=[str(ROOT/script),*arguments]
        job=subprocess.check_output(command,text=True).strip().split(';')[0]
        record['jobs'].append(dict(id=job,name=name,command=command));write_json(ROOT/'LAUNCH.json',record)
        print('SUBMITTED',job,name,flush=True);return job
    gpu=[t for t in plan['tasks'] if t['kind']=='base' and t['device']=='gpu']
    cpu=[t for t in plan['tasks'] if t['kind']=='base' and t['device']=='cpu']
    gjob=submit('automl-base','gpu.sbatch',['array_worker.py','base_gpu'],[f'--array=0-{len(gpu)-1}%4'])
    cjob=submit('automl-pod','cpu.sbatch',['array_worker.py','base_cpu'],[f'--array=0-{len(cpu)-1}%2'])
    dependency={ds:[f'{gjob}_{i}' for i,t in enumerate(gpu) if t['dataset']==ds]+
                  [f'{cjob}_{i}' for i,t in enumerate(cpu) if t['dataset']==ds] for ds in DATASETS}
    for ds in DATASETS[1:]:
        short=ds.replace('sharp__','')[:12]
        coarse=submit('automl-lf-'+short,'gpu.sbatch',['array_worker.py','coarse','--dataset',ds],['--array=0-19%1'])
        assembly=submit('automl-oof-'+short,'cpu.sbatch',['run_uq.py','--dataset',ds,'--kind','assemble'],['--dependency=afterok:'+coarse,'--kill-on-invalid-dep=yes'])
        corr=submit('automl-corr-'+short,'gpu.sbatch',['array_worker.py','corrector','--dataset',ds],
            ['--array=0-1%1','--dependency=afterok:'+assembly,'--kill-on-invalid-dep=yes'])
        dependency[ds].append(corr)
    for ds in DATASETS:
        submit('automl-score-'+ds[:12],'cpu.sbatch',['collect_dataset.py','--dataset',ds],
               ['--dependency=afterany:'+':'.join(dependency[ds])])
    record['base_gpu_tasks']=len(gpu);record['base_cpu_tasks']=len(cpu)
    record['coarse_tasks']=80;record['corrector_tasks']=8
    record['era5_neural_models']=7;record['era5_ensemble_experts']=7
    record['submission_complete']=True
    write_json(ROOT/'LAUNCH.json',record)
    print('All jobs submitted. Up to eight training GPUs: four direct models plus one coarse/corrector task per paired dataset.',flush=True)

if __name__=='__main__':main()
