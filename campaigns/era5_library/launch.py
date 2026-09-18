"""Queue new ERA5 experts and a collector that requires all nine."""
import json
import subprocess
from era5_common import ROOT, sha, verify_source, write_json

def main():
    verify_source()
    proof=json.loads((ROOT/'PREFLIGHT.json').read_text())
    assert proof['passed'] and proof['source_sha256']==sha(ROOT/'SOURCE.json')
    path=ROOT/'LAUNCH.json'
    record=json.loads(path.read_text()) if path.exists() else dict(jobs=[],
        source_sha256=sha(ROOT/'SOURCE.json'),preflight_sha256=sha(ROOT/'PREFLIGHT.json'))
    if record.get('complete'):
        print(json.dumps(record,indent=2));return
    def submit(name,script,args,options):
        prior=[j for j in record['jobs'] if j['name']==name]
        if prior:return prior[0]['id']
        command=['sbatch','--parsable','--job-name='+name,'--chdir='+str(ROOT)]+options+[str(ROOT/script)]+args
        job=subprocess.check_output(command,text=True).strip().split(';')[0]
        record['jobs'].append(dict(id=job,name=name,command=command));write_json(path,record)
        print('SUBMITTED',job,name,flush=True);return job
    coarse=submit('era5nine-coarse','gpu.sbatch',['worker.py','coarse'],
        ['--array=0-19%4','--dependency=afterok:'+proof['job_id'],'--kill-on-invalid-dep=yes'])
    assembly=submit('era5nine-oof','cpu.sbatch',['run_coarse.py','--assemble'],
        ['--dependency=afterok:'+coarse,'--kill-on-invalid-dep=yes'])
    correctors=submit('era5nine-correct','gpu.sbatch',['worker.py','corrector'],
        ['--array=0-1%2','--dependency=afterok:'+assembly,'--kill-on-invalid-dep=yes'])
    submit('era5nine-ensemble','cpu.sbatch',['collect_nine.py'],
        ['--dependency=afterok:'+correctors,'--kill-on-invalid-dep=yes'])
    record.update(complete=True,new_coarse_models=20,new_correctors=2,ensemble_experts=9,
        reused_experts=7,calibration_budgets=[5,10],reserved_evaluation_cases=7)
    write_json(path,record)
    print(json.dumps(record,indent=2))

if __name__=='__main__':
    main()
