#!/usr/bin/env python3
"""Portable entry point for the archived surrogate implementations.

This launches a new training job locally, not through a cluster scheduler.
Campaign-specific retraining (ERA5 and the four added PDEs) is documented separately.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def configure():
    """Recreate the relative layout expected by legacy source imports."""
    runtime = ROOT / '.runtime'
    def link(dst, src):
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.is_symlink():
            if dst.resolve() == src.resolve(): return
            dst.unlink()
        elif dst.exists():
            raise RuntimeError(f'Refusing to replace existing path {dst}')
        dst.symlink_to(os.path.relpath(src, dst.parent), target_is_directory=src.is_dir())
    link(runtime/'factory_mffp/models', ROOT/'models/paper')
    link(runtime/'factory_mffp/data_adapters', ROOT/'models/data_adapters')
    link(runtime/'factory_mffp/common', ROOT/'models/common')
    link(runtime/'experiments/bench_ct', ROOT/'models/st_bench')
    link(runtime/'experiments/st_bench/data', ROOT/'datasets')
    link(runtime/'experiments/st_bench/roster.txt', ROOT/'configs/roster.txt')
    flat = runtime/'factory_mffp/data'
    for d, entry in json.loads((ROOT/'configs/datasets.json').read_text()).items():
        link(flat/d, ROOT/entry['path'])
    env = os.environ.copy()
    env.update(MF_ROOT=str(runtime), MFFP_DATA=str(flat),
        FILM_FAMILY=str(ROOT/'models/paper/mf_fno_transfer_film'),
        UQ_ST=str(runtime/'experiments/st_bench'), DDE_BACKEND='pytorch',
        PYTHONPATH=os.pathsep.join([str(ROOT/'models'), str(ROOT/'models/paper'),
                                   str(ROOT/'models/st_bench'), env.get('PYTHONPATH','')]))
    env.setdefault('OMP_NUM_THREADS','4')
    env.setdefault('OPENBLAS_NUM_THREADS','4')
    return env

def main():
    models = json.loads((ROOT/'configs/models.json').read_text())
    datasets = json.loads((ROOT/'configs/datasets.json').read_text())
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', choices=sorted(models), required=True)
    p.add_argument('--dataset', choices=sorted(datasets), required=True)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--epochs', type=int, default=2500)
    p.add_argument('--steps', type=int, default=100000)
    p.add_argument('--device', default='auto')
    p.add_argument('--output', type=Path, default=ROOT/'outputs/training')
    p.add_argument('--dry-run', action='store_true')
    args, extra = p.parse_known_args()
    if args.dataset=='era5':
        p.error('ERA5 uses the unpaired, reserved-input campaign. See docs/TRAINING.md.')
    if args.model in ('M8','M9'):
        p.error('Correctors require out-of-fold coarse fits first. Use scripts/train_corrector.py.')
    entry=models[args.model]; arm=entry['archive_id']
    rel=datasets[args.dataset]['path'].removeprefix('datasets/')
    out=args.output.resolve()/f'{args.model}__{args.dataset}__s{args.seed}'
    if arm.startswith('st_'):
        cmd=[sys.executable,str(ROOT/'models/st_bench/run_st.py'),'--data-root',str(ROOT/'datasets'),
             '--dataset',rel,'--arm',arm,'--seed',str(args.seed),'--out-dir',str(out),
             '--steps',str(args.steps),'--device',args.device]+extra
    else:
        cmd=[sys.executable,str(ROOT/'models/paper'/arm/'smoke_eval.py'),
             '--dataset_dir',str(ROOT/'datasets'/rel),'--dataset_name',args.dataset,
             '--epochs',str(args.epochs),'--seed',str(args.seed),
             '--out',str(out/'result.json'),'--ckpt_dir',str(out/'checkpoints')]+extra
    if args.dry_run:
        import shlex
        print(shlex.join(cmd)); return
    out.mkdir(parents=True,exist_ok=True)
    env=configure();env['SAVE_PRED_DIR']=str(out/'predictions')
    (out/'command.json').write_text(json.dumps({'command':cmd,'model':entry,
        'note':'New run; use archived per-run settings for historical replication.'},indent=2)+'\n')
    subprocess.run(cmd,env=env,cwd=ROOT,check=True)

if __name__=='__main__':main()
