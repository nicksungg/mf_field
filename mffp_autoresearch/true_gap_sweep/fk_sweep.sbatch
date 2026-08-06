#!/bin/bash
# true_gap_sweep Task 1: fisher_kpp_2d solve-time sweep (measurement-only).
# One array task per output_time T; writes JSON cells to results/.
#SBATCH --job-name=fk_gap_sweep
#SBATCH --partition=expansion
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --array=0-7
#SBATCH --mail-user=ezeng@caltech.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/true_gap_sweep/logs/fk_%A_%a.out
#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/true_gap_sweep/logs/fk_%A_%a.err

set -euo pipefail
ROOT=/resnick/groups/Hippo/ezeng/mf_field
SWEEP=$ROOT/mffp_autoresearch/true_gap_sweep
PY=$ROOT/.venv/bin/python

TS=(0.3 0.6 1.0 1.5 2.0 3.0 4.5 6.0)
T=${TS[$SLURM_ARRAY_TASK_ID]}

$PY $SWEEP/fk_sweep.py --T "$T" --n 8 --n_div 3 \
    --out_dir $SWEEP/results --tag prod
