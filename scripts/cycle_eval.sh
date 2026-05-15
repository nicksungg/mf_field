#!/bin/bash
# Per-cycle eval runner. Called by the factory's research target.
#
# Submits the smoke eval as a SLURM job and waits for it. The result lands at
# results/smoke_latest.json which the factory reads back.
#
# Behavior:
#   - First tries the partition in MFFP_PARTITION (default: mit_preemptable).
#   - On failure, retries once on MFFP_FALLBACK_PARTITION (default: mit_normal_gpu).
#   - Always emits a results JSON so the factory has *something* to read; on
#     hard failure the JSON contains {"error": "..."} and an inf metric.

set -uo pipefail
cd "$(dirname "$(realpath "$0")")/.."
mkdir -p results logs
source scripts/env.sh

PARTITION="${MFFP_PARTITION:-mit_preemptable}"
FALLBACK="${MFFP_FALLBACK_PARTITION:-mit_normal_gpu}"
RESULT=results/smoke_latest.json

submit() {
    local part="$1"
    echo "[cycle_eval] submitting smoke eval to $part"
    sbatch --wait --partition="$part" eval/run_smoke.sbatch
    return $?
}

submit "$PARTITION"
RC=$?
if [ $RC -ne 0 ] || [ ! -s "$RESULT" ]; then
    echo "[cycle_eval] $PARTITION submission failed (rc=$RC), retrying on $FALLBACK"
    submit "$FALLBACK"
    RC=$?
fi

if [ ! -s "$RESULT" ]; then
    cat > "$RESULT" <<EOF
{"metric": "composite_nRMSE", "metric_value": 1e9,
 "metric_lower_is_better": true, "error": "no result file produced",
 "results": [{"name": "composite_nRMSE", "value": 1e9, "lower_is_better": true}]}
EOF
    echo "[cycle_eval] WARNING: no result file produced; emitted error stub"
    exit 1
fi

echo "[cycle_eval] done. metric:"
"$MFFP_PY" -c \
    "import json; d=json.loads(open('$RESULT').read()); print('  metric_value=', d.get('metric_value'))"
