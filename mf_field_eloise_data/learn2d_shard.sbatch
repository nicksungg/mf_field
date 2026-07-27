#!/bin/bash
#SBATCH -J learn2d
#SBATCH -p pi_faez
#SBATCH -N 1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --array=0-39
#SBATCH --time=05:00:00
#SBATCH -o /orcd/data/faez/001/nick/mf_field_eloise_data/logs/l2d_%A_%a.out
#SBATCH -e /orcd/data/faez/001/nick/mf_field_eloise_data/logs/l2d_%A_%a.err
set -euo pipefail
cd /orcd/data/faez/001/nick/mf_field_eloise_data
module load miniforge/25.11.0-0
source .venv/bin/activate
export PYTHONPATH="/orcd/data/faez/001/nick/mf_field_eloise_data/SURF_2026-main/mffp_sharp/src:${PYTHONPATH:-}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
VIDX=$((SLURM_ARRAY_TASK_ID / 10)); SIDX=$((SLURM_ARRAY_TASK_ID % 10))
VAR=$(sed -n "$((VIDX + 1))p" learn2d_variants.txt)
LO=$((SIDX * 50)); HI=$((LO + 50))
echo "=== ${VAR} shard [$LO:$HI] ==="
srun python generate_learnable.py "$VAR" --shard $LO $HI
