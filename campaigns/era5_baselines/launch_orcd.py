"""Idempotent scheduler chain. Maintenance determines eligibility automatically."""
import fcntl
import json
import re
import subprocess
import time
from baseline_common import ROOT, sha, verify_source, verify_inputs, write_json


def main():
    assert str(ROOT).startswith('/orcd/'), 'This launcher belongs exclusively to ORCD'
    verify_source()
    verify_inputs()
    with (ROOT / '.submission.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        path = ROOT / 'ORCD_LAUNCH.json'
        record = json.loads(path.read_text()) if path.exists() else dict(
            jobs=[], source_sha256=sha(ROOT / 'SOURCE.json'),
            input_manifest_sha256=sha(ROOT / 'INPUT_MANIFEST.json'),
            created=time.time(), cluster='ORCD',
            independent_fits=11, table_entries=12, alias='B10 reuses identical B9 recipe',
            max_concurrent_production_gpus=4,
            supercloud_jobs_unchanged=True)
        assert record['source_sha256'] == sha(ROOT / 'SOURCE.json')
        assert record['input_manifest_sha256'] == sha(ROOT / 'INPUT_MANIFEST.json')
        if record.get('submission_complete'):
            print(json.dumps(record, indent=2))
            return

        def submit(name, script, arguments, options):
            old = [j for j in record['jobs'] if j['name'] == name]
            comment = 'era5base:' + record['source_sha256'][:20] + ':' + name
            # Recover an accepted submission even if the process died before
            # writing its local journal. Check active and recent finished jobs.
            found = set()
            queue = subprocess.check_output(['squeue', '-h', '-u', 'review-author', '-o', '%i|%k'], text=True)
            account = subprocess.check_output(['sacct', '-X', '-u', 'review-author',
                      '--starttime=2026-09-15', '--format=JobID,Comment', '-n', '-P'], text=True)
            for line in (queue + '\n' + account).splitlines():
                fields = line.split('|')
                if len(fields) >= 2 and fields[1].strip() == comment:
                    found.add(re.split(r'[_\.]', fields[0].strip())[0])
            assert len(found) <= 1, f'Multiple scheduler copies of {name}: {found}'
            if old:
                assert found == {old[0]['id']}, f'Journal does not match scheduler: {name}'
                return old[0]['id']
            if found:
                job = next(iter(found))
                record['jobs'].append(dict(id=job, name=name, comment=comment, recovered_from_scheduler=True))
                write_json(path, record)
                return job
            command = ['sbatch', '--parsable', '--job-name=' + name,
                       '--comment=' + comment, '--chdir=' + str(ROOT),
                       '--output=' + str(ROOT / 'logs/%x_%A_%a.out')]
            command += options + [str(ROOT / script)] + arguments
            job = subprocess.check_output(command, text=True).strip().split(';')[0]
            record['jobs'].append(dict(id=job, name=name, comment=comment, command=command))
            write_json(path, record)
            print('SUBMITTED', job, name, flush=True)
            return job

        def after(*jobs):
            return ['--dependency=afterok:' + ':'.join(jobs), '--kill-on-invalid-dep=yes']

        cpu_check = submit('era5base-cpu-check', 'cpu_orcd.sbatch', ['preflight.py', '--device', 'cpu'], [])
        gpu_check = submit('era5base-gpu-check', 'gpu_orcd.sbatch', ['preflight.py', '--device', 'gpu'],
                           ['--time=03:00:00'] + after(cpu_check))
        cpu = submit('era5base-cpu', 'cpu_orcd.sbatch', ['array_worker.py', 'cpu'],
                     ['--array=0-3%4'] + after(cpu_check))
        gpu = submit('era5base-gpu', 'gpu_orcd.sbatch', ['array_worker.py', 'gpu'],
                     ['--array=0-6%4'] + after(gpu_check))
        submit('era5base-collect', 'cpu_orcd.sbatch', ['collect_baselines.py'], after(cpu, gpu))
        record['submission_complete'] = True
        write_json(path, record)
        print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
