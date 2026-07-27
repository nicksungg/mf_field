#!/bin/bash
#SBATCH -J sharp_gen
#SBATCH -p pi_faez
#SBATCH -N 1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --array=0-23
#SBATCH --time=12:00:00
#SBATCH -o /orcd/data/faez/001/nick/mf_field_eloise_data/logs/sharp_gen_%A_%a.out
#SBATCH -e /orcd/data/faez/001/nick/mf_field_eloise_data/logs/sharp_gen_%A_%a.err

set -euo pipefail
cd /orcd/data/faez/001/nick/mf_field_eloise_data
mkdir -p logs
module load miniforge/25.11.0-0

VENV=/orcd/data/faez/001/nick/mf_field_eloise_data/.venv
source "$VENV/bin/activate"
# solvers live under the installed package; ensure src is importable
export PYTHONPATH="/orcd/data/faez/001/nick/mf_field_eloise_data/SURF_2026-main/mffp_sharp/src:${PYTHONPATH:-}"
# keep BLAS single-threaded per task so the 4 cores aren't oversubscribed
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4

VARIANT=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" variants.txt)
echo "=== task ${SLURM_ARRAY_TASK_ID}: generating ${VARIANT} on $(hostname) ==="
srun python generate_standardized.py "$VARIANT" --ntrain 400 --ntest 100
echo "=== done ${VARIANT} ==="
