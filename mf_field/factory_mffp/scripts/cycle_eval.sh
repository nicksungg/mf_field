#!/bin/bash
# Per-cycle eval runner for the factory's research target.
#
# Strategy:
#   1) Try score.py locally with cache. If every (family, dataset) pair has a
#      cached result for the current code-hash, score.py prints the metric in
#      seconds — no SLURM round-trip.
#   2) If anything is missing (e.g. a new family was just added) AND we are
#      NOT inside the SLURM job ourselves, submit eval/run_smoke.sbatch with
#      sbatch --wait. This blocks until the job finishes.
#   3) Always finish by ensuring results/smoke_latest.json exists and contains
#      a finite metric_value, otherwise emit an explicit error stub.

set -uo pipefail
cd "${MFFP_PROJECT_ROOT:-/orcd/data/faez/001/nick/mf_field/factory_mffp}"
source scripts/env.sh
mkdir -p results logs

RESULT=results/smoke_latest.json
PARTITION="${MFFP_PARTITION:-mit_preemptable}"
FALLBACK="${MFFP_FALLBACK_PARTITION:-mit_normal_gpu}"

# 1) cache-only local pass
echo "[cycle_eval] trying cache-only local score…"
if "$MFFP_PY" eval/score.py --out "$RESULT" 2>&1 | tail -8; then
    # Did all families have cached results?
    MISSED=$("$MFFP_PY" -c "
import json, sys
d = json.load(open('$RESULT'))
n_err = sum(1 for r in d.get('runs', []) if 'error' in r)
print(n_err)
" 2>/dev/null || echo 1)
    if [ "$MISSED" = "0" ]; then
        echo "[cycle_eval] all cached. metric_value:"
        "$MFFP_PY" -c "import json; print('  ', json.load(open('$RESULT'))['metric_value'])"
        exit 0
    fi
    echo "[cycle_eval] $MISSED cached miss(es) — submitting full smoke to SLURM"
fi

# 2) submit smoke to SLURM
submit() {
    local part="$1"
    echo "[cycle_eval] sbatch --wait --partition=$part eval/run_smoke.sbatch"
    sbatch --wait --partition="$part" eval/run_smoke.sbatch
    return $?
}

submit "$PARTITION"
RC=$?
if [ $RC -ne 0 ] || ! "$MFFP_PY" -c "import json,sys; d=json.load(open('$RESULT')); sys.exit(0 if isinstance(d.get('metric_value'), (int,float)) else 1)" 2>/dev/null; then
    echo "[cycle_eval] $PARTITION submission did not produce a valid result — falling back to $FALLBACK"
    submit "$FALLBACK"
    RC=$?
fi

# 3) error stub if nothing produced a result
if ! "$MFFP_PY" -c "import json,sys; d=json.load(open('$RESULT')); sys.exit(0 if isinstance(d.get('metric_value'), (int,float)) else 1)" 2>/dev/null; then
    cat > "$RESULT" <<EOF
{"metric": "composite_nRMSE", "metric_value": 1e9,
 "metric_lower_is_better": true, "error": "no valid result from sbatch",
 "results": [{"name": "composite_nRMSE", "value": 1e9, "lower_is_better": true}]}
EOF
    echo "[cycle_eval] WARNING: emitted error stub"
    exit 1
fi

echo "[cycle_eval] done. metric_value:"
"$MFFP_PY" -c "import json; print('  ', json.load(open('$RESULT'))['metric_value'])"
