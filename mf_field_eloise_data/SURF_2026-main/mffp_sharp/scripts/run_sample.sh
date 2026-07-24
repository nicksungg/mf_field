#!/usr/bin/env bash
# Generate the SAMPLE-round datasets. Run THIS ON Nicholas's box.
#   cd SURF_2026/mffp_sharp && bash scripts/run_sample.sh [pde]
#   pde = all (default) | euler | cahn_hilliard | kuramoto_sivashinsky
#
# To update code first:  git -C .. pull
set -euo pipefail

cd "$(dirname "$0")/.."          # -> mffp_sharp/
PDE="${1:-all}"

# shellcheck disable=SC1091
source activate mffp 2>/dev/null || conda activate mffp

python -m mffp_sharp.generate --config configs/sample.yaml --pde "${PDE}"

echo
echo ">> done. Data + summary in: $(pwd)/data/sample/"
echo ">> review data/sample/sample_summary.json  (LF-vs-HF bottom-rung check)"
echo ">> datasets stay here on the box (git-ignored); copy small summaries/figures back for Nicholas."
