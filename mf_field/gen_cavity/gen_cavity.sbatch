#!/bin/bash
# Regenerate lid-driven-cavity at [32,64,128,256] (256 = converged HF) on a CPU node.
#SBATCH --job-name=gen_cavity
#SBATCH --partition=mit_normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --output=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/gen_cavity_%j.out
#SBATCH --error=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/gen_cavity_%j.err

set -uo pipefail
ROOT=/orcd/data/faez/001/nick/mf_field
PY=$ROOT/factory_mffp/.venv/bin/python
cd "$ROOT/gen_cavity"
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8
echo "[$(date)] regenerating lid_driven_cavity [32,64,128,256] n=50 seed=42"
"$PY" lid_driven_cavity.py --levels 32,64,128,256 --n_samples 50 --seed 42 \
    --out_dir "$ROOT/lid_driven_cavity_generated_v2"
echo "[$(date)] done"
