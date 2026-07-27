#!/bin/bash
#SBATCH -J kdv_merge
#SBATCH -p pi_faez
#SBATCH -N 1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH -o /orcd/data/faez/001/nick/mf_field_eloise_data/logs/kdvmg_%j.out
#SBATCH -e /orcd/data/faez/001/nick/mf_field_eloise_data/logs/kdvmg_%j.err
set -euo pipefail
cd /orcd/data/faez/001/nick/mf_field_eloise_data
module load miniforge/25.11.0-0
source .venv/bin/activate
export PYTHONPATH="/orcd/data/faez/001/nick/mf_field_eloise_data/SURF_2026-main/mffp_sharp/src:${PYTHONPATH:-}"
srun python generate_kdv_fixed.py --merge
