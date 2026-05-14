#!/bin/bash
# Launch a full benchmark across all datasets for the given families.
#   ./scripts/launch_full_benchmark.sh                    # v9_baseline only
#   ./scripts/launch_full_benchmark.sh "v9_baseline,foo"  # multiple families

set -euo pipefail
cd "$(dirname "$(realpath "$0")")/.."

FAMILIES="${1:-v9_baseline}"
N=$(/orcd/data/faez/001/nick/mf_field/akash/remote-factory-main/.venv/bin/python \
      eval/launch_full.py --plan --families "$FAMILIES" | head -1 | sed 's/N=//')

if [ -z "$N" ] || [ "$N" -le 0 ]; then
    echo "ERROR: empty plan"; exit 1
fi
LAST=$((N - 1))
echo "Submitting array 0-${LAST} for families: $FAMILIES"
sbatch --array="0-${LAST}%8" eval/run_full.sbatch "$FAMILIES"
