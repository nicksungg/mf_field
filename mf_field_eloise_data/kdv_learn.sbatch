#!/bin/bash
#SBATCH -J kdv_learn
#SBATCH -p pi_faez
#SBATCH -N 1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --array=0-9
#SBATCH --time=03:00:00
#SBATCH -o /orcd/data/faez/001/nick/mf_field_eloise_data/logs/kdvl_%A_%a.out
#SBATCH -e /orcd/data/faez/001/nick/mf_field_eloise_data/logs/kdvl_%A_%a.err
set -euo pipefail
cd /orcd/data/faez/001/nick/mf_field_eloise_data
module load miniforge/25.11.0-0
source .venv/bin/activate
export PYTHONPATH="/orcd/data/faez/001/nick/mf_field_eloise_data/SURF_2026-main/mffp_sharp/src:${PYTHONPATH:-}"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
LO=$((SLURM_ARRAY_TASK_ID*50)); HI=$((LO+50))
srun python generate_kdv_learnable.py --shard $LO $HI
