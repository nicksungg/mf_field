"""Dispatch exactly one frozen baseline, with cluster-specific validation."""
import argparse
import json
import os
import subprocess
import sys
from baseline_common import ROOT, sha, verify_source

parser = argparse.ArgumentParser()
parser.add_argument('device', choices=['cpu', 'gpu'])
args = parser.parse_args()
verify_source()
proof = json.loads((ROOT / f'{args.device.upper()}_PREFLIGHT.json').read_text())
assert proof['passed'] and proof['source_sha256'] == sha(ROOT / 'SOURCE.json')
assert proof['input_manifest_sha256'] == sha(ROOT / 'INPUT_MANIFEST.json')
models = [r for r in json.loads((ROOT / 'BASELINES.json').read_text())['models'] if r['device'] == args.device]
row = models[int(os.environ['SLURM_ARRAY_TASK_ID'])]
print('PRODUCTION', row, flush=True)
command = [sys.executable, '-u', f'worker_{row["worker"]}.py', '--model', row['model']]
if row['worker'] == 'st':
    command += ['--device', 'cuda' if args.device == 'gpu' else 'cpu', '--threads', '4']
subprocess.run(command, cwd=ROOT, check=True)
