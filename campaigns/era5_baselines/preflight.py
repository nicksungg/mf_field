"""Run contract tests and isolated smoke fits before production becomes eligible."""
import argparse
import json
import os
import subprocess
import sys
import time
from baseline_common import ROOT, sha, verify_source, verify_inputs, write_json, completed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', choices=['cpu', 'gpu'], required=True)
    args = parser.parse_args()
    verify_source()
    verify_inputs()
    # A GPU check must execute its kernels, even if a prior CPU smoke exists.
    smoke = ROOT / 'smoke'
    if smoke.exists():
        history = ROOT / 'smoke_history'
        history.mkdir(exist_ok=True)
        smoke.rename(history / f'{args.device}_{os.environ.get("SLURM_JOB_ID", "local")}_{time.time_ns()}')
    import torch
    import numpy as np
    rows = json.loads((ROOT / 'BASELINES.json').read_text())['models']
    if args.device == 'cpu':
        subprocess.run([sys.executable, '-m', 'pytest', '-q', 'tests'], cwd=ROOT, check=True)
    else:
        assert torch.cuda.is_available() and torch.cuda.device_count() == 1
        assert 'H100' in torch.cuda.get_device_name(), 'This queued campaign was validated for an H100 request'
        cpu = json.loads((ROOT / 'CPU_PREFLIGHT.json').read_text())
        assert cpu['passed'] and cpu['source_sha256'] == sha(ROOT / 'SOURCE.json')
    tested = []
    for row in rows:
        if row['device'] != args.device:
            continue
        cmd = [sys.executable, '-u', f'worker_{row["worker"]}.py', '--model', row['model'], '--smoke']
        if row['worker'] == 'st':
            cmd += ['--device', 'cuda' if args.device == 'gpu' else 'cpu', '--threads', '4']
        print('PREFLIGHT', cmd, flush=True)
        subprocess.run(cmd, cwd=ROOT, check=True)
        assert completed(row['model'], smoke=True)
        if args.device == 'gpu':
            meta = json.loads((ROOT / 'smoke/metadata' / f'{row["model"]}__era5.json').read_text())
            assert meta['device'] == 'cuda' or 'H100' in meta['device'], 'A GPU smoke was satisfied by a CPU output'
        tested.append(row['model'])
    if args.device == 'gpu':
        assert completed('mf_fno_transfer_bar', smoke=True)
    verify_source()
    proof = dict(passed=True, source_sha256=sha(ROOT / 'SOURCE.json'),
                 input_manifest_sha256=sha(ROOT / 'INPUT_MANIFEST.json'),
                 models=tested, device=args.device, job_id=os.environ.get('SLURM_JOB_ID'),
                 torch=torch.__version__, numpy=np.__version__, python=sys.version,
                 gpu=torch.cuda.get_device_name() if args.device == 'gpu' else None,
                 time=time.time(), smoke_outputs_are_scientific_results=False)
    write_json(ROOT / f'{args.device.upper()}_PREFLIGHT.json', proof)
    print('PREFLIGHT PASSED', args.device, flush=True)


if __name__ == '__main__':
    main()
