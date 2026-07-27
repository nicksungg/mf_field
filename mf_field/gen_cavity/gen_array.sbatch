#!/bin/bash
#SBATCH --job-name=cav_gen
#SBATCH --partition=mit_normal
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=04:00:00
#SBATCH --output=/orcd/data/faez/001/nick/mf_field/factory_mffp/logs/cavgen_%A_%a.out
set -uo pipefail
cd /orcd/data/faez/001/nick/mf_field/gen_cavity
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
/orcd/data/faez/001/nick/mf_field/factory_mffp/.venv/bin/python gen_one.py --task ${SLURM_ARRAY_TASK_ID}
