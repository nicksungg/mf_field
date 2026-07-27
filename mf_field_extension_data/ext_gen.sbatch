#!/bin/bash
#SBATCH -J ext_gen
#SBATCH -p pi_faez
#SBATCH -N 1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --array=0-6
#SBATCH --time=04:00:00
#SBATCH -o /orcd/data/faez/001/nick/mf_field_extension_data/logs/ext_%A_%a.out
#SBATCH -e /orcd/data/faez/001/nick/mf_field_extension_data/logs/ext_%A_%a.err
set -euo pipefail
cd /orcd/data/faez/001/nick/mf_field_extension_data
mkdir -p logs
module load miniforge/25.11.0-0
source /orcd/data/faez/001/nick/mf_field_eloise_data/.venv/bin/activate
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
NAME=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" ext_variants.txt)
echo "=== ext regen: ${NAME} on $(hostname) ==="
srun python generate_ext_standardized.py "$NAME" --ntrain 400 --ntest 100
