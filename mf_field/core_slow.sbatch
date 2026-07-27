#!/bin/bash
#SBATCH -J core_gen
#SBATCH -p pi_faez
#SBATCH -N 1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --array=0-1
#SBATCH --time=12:00:00
#SBATCH -o /orcd/data/faez/001/nick/mf_field/logs/core_%A_%a.out
#SBATCH -e /orcd/data/faez/001/nick/mf_field/logs/core_%A_%a.err
set -euo pipefail
cd /orcd/data/faez/001/nick/mf_field
module load miniforge/25.11.0-0
source /orcd/data/faez/001/nick/mf_field_eloise_data/.venv/bin/activate
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
NAME=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" core_slow_variants.txt)
echo "=== core regen: ${NAME} on $(hostname) ==="
srun python generate_all_datasets.py /orcd/data/faez/001/nick/mf_field/core_regenerated 500 "$NAME"
echo "=== done ${NAME} ==="
