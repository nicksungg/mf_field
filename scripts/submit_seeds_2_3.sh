#!/bin/bash
# r3s3_lf_value-B3 — submit seeds 1 and 2 in parallel, AFTER the seed-0 gate.
# (Round-3 seeds are {0,1,2}; this file keeps the round-5 name so the
#  orchestrator flow reads the same. Card recipe.seeds = [0, 1, 2].)
#
# Same seal gate as submit.sh: no sbatch before the pre-registration exists.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="/resnick/groups/Hippo/ezeng/mf_field"
PREREG_JSON="$PROJECT_ROOT/mffp_autoresearch/round3/state/r3s3_lf_value/prereg_knees_B3.json"

if [[ ! -f "$PREREG_JSON" ]]; then
  echo "[FATAL] pre-registration missing: $PREREG_JSON — no sbatch before the seal." >&2
  exit 2
fi
"$PROJECT_ROOT/.venv/bin/python" -c "import json,sys;s=json.load(open(sys.argv[1]));print('[seal] sealed_utc',s['_sealed_utc'],'sha256',s['_payload_sha256'])" "$PREREG_JSON"

for s in 1 2; do
  mkdir -p "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round3/r3s3_lf_value/B3/slurm"  # SLURM opens --output before the job script runs (review finding 3.5)
jid=$(sbatch --parsable --job-name="r3-r3s3_lf_value-B3-s${s}" "$SCRIPT_DIR/01_train_eval.sh" "$s")
  echo "submitted seed $s: job $jid"
done
