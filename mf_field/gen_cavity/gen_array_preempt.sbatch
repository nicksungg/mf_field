#!/bin/bash
#SBATCH --job-name=cav_gen_p
#SBATCH --partition=mit_preemptable
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=12:00:00
#SBATCH --requeue
#SBATCH --output=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/cavgenp_%A_%a.out
set -uo pipefail
cd /orcd/data/faez/001/nick/mf_field/gen_cavity
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
/orcd/data/faez/001/nick/mf_field/factory_mffp/.venv/bin/python gen_one.py --task ${SLURM_ARRAY_TASK_ID}
