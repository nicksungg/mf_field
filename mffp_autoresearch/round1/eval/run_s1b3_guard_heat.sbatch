#!/bin/bash
# s1-B3: close the heat_local guard-contract leg (reviewer S1 — the one
# _contract_check dataset infeasible on the login node). Non-blocking,
# 2-epoch plumbing; contract numbers are never results.
#SBATCH --job-name=r1-s1_poisson-B3-guard-heat
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --exclude=hpc-93-36
#SBATCH --requeue
#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s1_poisson/B3/slurm/%x_%j.out
#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s1_poisson/B3/slurm/%x_%j.err
set -euo pipefail
mkdir -p /resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s1_poisson/B3/slurm
GUARD_DATASETS=heat_local GUARD_TAG=_heat \
  bash /resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round1/worktrees/s1_poisson/B3/scratchpad/run_guard_contract.sh
