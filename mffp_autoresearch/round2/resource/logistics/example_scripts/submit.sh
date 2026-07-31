#!/bin/bash
# Template: submit seed 0 (the debug seed) only. Orchestrator-invoked.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
jid=$(sbatch --parsable "$SCRIPT_DIR/01_train_eval.sh" 0)
echo "submitted seed 0: job $jid"
