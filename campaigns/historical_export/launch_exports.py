import json
import subprocess
from config import *

def main():
    out=ROOT/'EXPORT_LAUNCH.json'
    if out.exists():print(out.read_text());return
    smoke=json.loads((ROOT/'cache/darcy_generated/audit.json').read_text())
    assert smoke['n_kept']==100 and len(smoke['models'])==7
    files=['config.py','prepare.py','export_one.py','export_worker.py','export_gpu.sbatch','export_cpu.sbatch']
    record=dict(plan_sha256=sha(ROOT/'plan.json'),source_sha256={f:sha(ROOT/f) for f in files},
                smoke_jobs={'gpu':22658738,'cpu':22658660,'cancelled_pending_qos':22658659},jobs=[])
    try:
        for device,script,partition in [('gpu','export_gpu.sbatch','mit_preemptable'),
                                        ('gpu','export_gpu.sbatch','mit_preemptable'),
                                        ('cpu','export_cpu.sbatch','mit_normal')]:
            jid=subprocess.check_output(['sbatch','--parsable','--partition='+partition,
                '--export=ALL,ONLY_DATASET=',str(ROOT/script)],text=True).strip().split(';')[0]
            record['jobs'].append(dict(id=jid,device=device,partition=partition))
            write_json(out,record)
            print('SUBMITTED',jid,device,flush=True)
    finally:write_json(out,record)

if __name__=='__main__':main()
