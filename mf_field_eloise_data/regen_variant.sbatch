#!/bin/bash
#SBATCH -p expansion
#SBATCH -N 1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --mail-user=ezeng@caltech.edu
#SBATCH --mail-type=END,FAIL

# Regenerate one sharp variant through the fixed (IC-encoded, gated) package path.
# Usage: sbatch -J regen_<variant> regen_variant.sbatch <variant>
# The completeness gate runs in-job and hard-fails on INCOMPLETE.
set -euo pipefail
VARIANT="$1"
REPO=/resnick/groups/Hippo/ezeng/mf_field
source "$REPO/.venv/bin/activate"
cd "$REPO/mf_field_eloise_data"
python generate_standardized.py "$VARIANT" --ntrain 400 --ntest 100 \
  --cfg "$REPO/mf_field_eloise_data/SURF_2026-main/mffp_sharp/configs/sample.yaml" \
  --ablation_dir "$REPO/mf_field_eloise_data" \
  --out_root "$REPO/regen_2026-08-03/sharp_generated"
