#!/bin/bash
# r3s3_lf_value-B3 — the PHASE-C confirming ladder for the sealed knee
# predictions. One SLURM job per TRAINING seed.
#
# Invoked as: 01_train_eval.sh <SEED>   (SEED is the TRAINING seed, --seed).
#
# ONE job runs this card's whole per-seed grid plus the blocking pre-flights.
# Train+eval is one `score_panel.py` invocation per leg (program.md §9); there is
# no train->eval chain. Every leg gets its own ROUND2_EVAL_RESULTS under
# $OUT_DIR/training (hence its own ckpt_dir and result path) and its own `done`
# marker keyed on (arm, dataset, cap, split_seed, n_hf, epochs_target, TRAINING
# seed), so a preempted/requeued job resumes leg-by-leg and, within a leg, from
# <ckpt_dir>/last.pt (card `recipe.env._slurm`; program.md §5.8). Every per-seed
# artifact carries `_s<SEED>`, so seeds 0/1/2 run concurrently into the same
# output tree without clobbering each other.
#
# THE ORDERING IS THE EXPERIMENT. This script REFUSES to start unless the
# phase-P seal exists and hashes to R3S3B3_PREREG_SHA256, and it reads every
# cap ladder OUT OF that seal — there is no ladder in this file to fall back to.
#
# `--job-name` is overridden per seed by submit.sh / submit_seeds_2_3.sh
# (r3-r3s3_lf_value-B3-s<SEED>, the round-3 naming state/timing_ledger.json
# records and the maintainer matches on).
#
#SBATCH --job-name=r3-r3s3_lf_value-B3-s0
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:nvidia_h200:1
#SBATCH --mem=32G
#SBATCH --time=06:00:00
#SBATCH --mail-user=ezeng@caltech.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round3/r3s3_lf_value/B3/slurm/%x_%j.out
#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round3/r3s3_lf_value/B3/slurm/%x_%j.err

set -euo pipefail
SEED="${1:?usage: 01_train_eval.sh <seed>}"

PROJECT_ROOT="/resnick/groups/Hippo/ezeng/mf_field"
ROUND_ROOT="$PROJECT_ROOT/mffp_autoresearch/round3"
EVAL_DIR="$PROJECT_ROOT/mffp_autoresearch/round2/eval"     # frozen round-2 eval layer
TOOLS_DIR="$ROUND_ROOT/tools"                              # registered round-3 probes
WORKTREE="$ROUND_ROOT/worktrees/r3s3_lf_value/B3"
FAMILY_DIR="$WORKTREE/models_r3/r3s3_knee_prereg"
OUT_DIR="$PROJECT_ROOT/mffp_autoresearch_outputs/round3/r3s3_lf_value/B3"

PREREG_JSON="$ROUND_ROOT/state/r3s3_lf_value/prereg_knees_B3.json"
# The digest of the SEALED payload, copied from the card's
# recipe.env.R3S3B3_PREREG_SHA256. If the seal is edited, every leg refuses.
PREREG_SHA256="e98f6dc78ab18d80d75f4ef1f819525682d0d01c61e11081939dee30fcea3e2c"

EPOCHS=200          # recipe.epochs
GUARD_EPOCHS=2      # recipe.env._note: "the guard leg also sets epochs=2"

source "$PROJECT_ROOT/.venv/bin/activate"
mkdir -p "$OUT_DIR/eval/done" "$OUT_DIR/slurm" "$OUT_DIR/training" \
         "$OUT_DIR/training_guard_contract_tier_excluded" \
         "$OUT_DIR/cache" "$OUT_DIR/preflight"

# ROUND-3 CONVENTION (batch-1 lesson): both eval-layer write targets are
# redirected into THIS card's output tree BEFORE anything runs, so nothing can
# fall back to the frozen round-2 eval layer's own results/ or cache/
# (program.md §5 immutable 3). Every leg narrows ROUND2_EVAL_RESULTS further to
# its own subdirectory.
export ROUND2_EVAL_RESULTS="$OUT_DIR/training"
export ROUND2_EVAL_CACHE="$OUT_DIR/cache"

echo "[$(date -u +%FT%TZ)] host=$(hostname) gpu=$(nvidia-smi -L 2>/dev/null | head -1 || echo none) seed=$SEED"
echo "[cfg] family=$FAMILY_DIR epochs=$EPOCHS out=$OUT_DIR"
echo "[cfg] ROUND2_EVAL_RESULTS=$ROUND2_EVAL_RESULTS ROUND2_EVAL_CACHE=$ROUND2_EVAL_CACHE"

# ── BLOCKING PRE-FLIGHT (a): THE SEAL ────────────────────────────────────────
# Card part 3 phase P item 4, verbatim: "No GPU job may be submitted before the
# seal exists." This is the script-side half of that rule (the family re-checks
# it per leg, and additionally asserts `_sealed_utc` precedes the leg's start).
echo "[preflight] pre-registration seal"
python - "$PREREG_JSON" "$PREREG_SHA256" <<'PY'
import hashlib, json, sys
from pathlib import Path
p, want = Path(sys.argv[1]), sys.argv[2]
if not p.exists():
    raise SystemExit(f"[FATAL] pre-registration missing: {p}. Phase P (CPU only, "
                     "scripts/phase_p_prereg.py) must seal the predicted knee caps "
                     "BEFORE any training leg. No sbatch may run without it.")
seal = json.loads(p.read_text())
got = hashlib.sha256(json.dumps(seal["payload"], sort_keys=True,
                                separators=(",", ":"), default=float).encode()).hexdigest()
if got != seal["_payload_sha256"]:
    raise SystemExit(f"[FATAL] seal corrupt: recorded {seal['_payload_sha256']} != "
                     f"recomputed {got}")
if want.startswith("__") or want != got:
    raise SystemExit(f"[FATAL] PREREG_SHA256 mismatch: script has {want!r}, seal "
                     f"hashes to {got!r}")
print(f"[ok] sealed_utc={seal['_sealed_utc']} payload_sha256={got}")
for ds, c in sorted(seal["payload"]["cells"].items()):
    print(f"[ok]   {ds:32s} ladder={[c['ladder'][k] for k in ('r1','r2','r3','r4')]} "
          f"c_pred={c['c_pred']} (c_hat={c['c_hat']})")
PY

# ── BLOCKING PRE-FLIGHT (b): the stale-checkpoint audit ──────────────────────
# `tools/stale_checkpoint_audit.py --fail-on-stale` over THIS card's own outputs
# BEFORE any scoring (card `_blocking_preflights` item 6). On a first run the
# tree is empty (0 legs, OK); on a requeue it re-audits every leg this card has
# already produced, so a result re-scored from a finished checkpoint without
# training cannot enter the card's evidence. `--mtime-slack-seconds 300` is B2's
# MEASURED value (max ckpt->result tail 39.6 s over B1's 234 checkpointed legs;
# 300 s is ~7.6x that and orders of magnitude below a genuine stale re-score).
# The GUARD leg is deliberately not in this tree: it is a 2-epoch contract-tier
# leg whose checkpoint/step profile sits outside the audit's 200-epoch
# heuristics, and B2 seed 1 hit exactly that spurious flag; the S3 adjudication
# RELOCATED the guard leg rather than relaxing the audit, and this script bakes
# that in from the start.
echo "[preflight] stale-checkpoint audit over this card's own scored outputs"
python "$TOOLS_DIR/stale_checkpoint_audit.py" \
    --root "$OUT_DIR/training" \
    --mtime-slack-seconds 300 \
    --out "$OUT_DIR/preflight/stale_checkpoint_audit_s${SEED}_$(date -u +%Y%m%dT%H%M%SZ).json" \
    --fail-on-stale

# ── the 45 recipe.env keys that are identical on every leg ───────────────────
# The card's recipe.env enumerates exactly 49 R3S3B3_* keys; per
# `recipe.env._note` each leg overrides only ARM, LF_COND_SET, LF_COND_CAP and
# SPLIT_SEED, so 45 are common. Values are the card's, verbatim.
COMMON_ENV=(
  R3S3B3_PHASE=C
  "R3S3B3_PREREG_JSON=$PREREG_JSON"
  "R3S3B3_PREREG_SHA256=$PREREG_SHA256"
  R3S3B3_PREREG_ASSERT=1
  R3S3B3_LADDER_FROM_PREREG=1
  R3S3B3_CELLS=sharp__cahn_hilliard,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__phase_field_crystal_2d,ifc_heat
  R3S3B3_N_HF=5
  R3S3B3_SCALER=per_rung_max_fullpool
  R3S3B3_SCALER_INVARIANCE_ASSERT=1
  R3S3B3_WIDTH=64
  R3S3B3_BLOCKS=4
  R3S3B3_MODES_CAP=12
  R3S3B3_MODE_POLICY=pinned_min_rung_nyquist
  R3S3B3_STEPS_PER_EPOCH=25
  R3S3B3_HF_BATCH=5
  R3S3B3_LF_BATCH=16
  R3S3B3_LR=1e-3
  R3S3B3_WD=1e-5
  R3S3B3_SCHED=cosine
  R3S3B3_CLIP=1.0
  R3S3B3_LAMBDA_LF=1.0
  R3S3B3_LF_LIFT=match_copylf_convention
  R3S3B3_REF_ARMS=nn_condition_n5,train_mean_n5,zero,affine_on_hf_train,nn_condition_full,train_mean_full
  R3S3B3_FLOORS_JSON=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/anchors_repaired/floors.json
  R3S3B3_FLOOR_TOL=1e-9
  R3S3B3_FLOOR_TOLERANCES_JSON=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/floor_tolerances.json
  R3S3B3_NOISE_FLOOR_JSON=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/anchors_repaired/noise_floor.json
  R3S3B3_FILM_DENOM_JSON=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/anchors/film_denominator.json
  R3S3B3_FILM_UNITS=1
  R3S3B3_MCE_MODE=certified_r3
  R3S3B3_ANCHORS_JSON=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/anchors/launch_anchors.json
  R3S3B3_G5_FITSET_BAND=1
  R3S3B3_DATA_BINDING_ASSERT=1
  R3S3B3_CKPT_BINDING=1
  R3S3B3_TARGET_SCALE_AUDIT=1
  R3S3B3_STALE_CKPT_ASSERT=1
  R3S3B3_LF_ROW_MANIFEST=1
  R3S3B3_STRATIFY_ROWS=1
  R3S3B3_HARD_MASK_MODE=rederive_model_free
  R3S3B3_HARD_MASK_TOPFRAC=0.27
  R3S3B3_MEAN_REMOVED_REPORT=1
  R3S3B3_DUMP_TEST_PREDS=1
  R3S3B3_ALIGNMENT_REPORT=0
  R3S3B3_CKPT_EVERY_STEPS=250
  R3S3B3_GUARD_NSUB=off
)

# ── leg runner ───────────────────────────────────────────────────────────────
N_DONE=0
N_RUN=0

# run_leg <arm> <dataset> <split_seed> <cond_set> <cap> <epochs> [work_root]
run_leg() {
  local arm="$1" ds="$2" split="$3" cond_set="$4" cap="$5" epochs="$6"
  local work_root="${7:-$OUT_DIR/training}"
  # the done marker key is (arm, dataset, cap, split_seed, n_hf, epochs_target)
  # plus the TRAINING seed — card `recipe.env._slurm`.
  local leg="${arm}__${ds}__d${split}__n5__c${cap}__e${epochs}"
  local tag="${leg}__s${SEED}"
  local marker="$OUT_DIR/eval/done/${tag}.done"
  if [[ -f "$marker" ]]; then
    echo "[skip] $tag (done marker present)"
    N_DONE=$((N_DONE + 1))
    return 0
  fi
  local work="$work_root/$tag"
  mkdir -p "$work" "$OUT_DIR/eval"
  echo "[leg] $tag arm=$arm ds=$ds split_seed=$split COND_SET=$cond_set CAP=$cap epochs=$epochs"
  ROUND2_EVAL_RESULTS="$work" python "$EVAL_DIR/score_panel.py" \
      --family_dir "$FAMILY_DIR" \
      --datasets "$ds" \
      --epochs "$epochs" \
      --seed "$SEED" \
      --out "$OUT_DIR/eval/result_${tag}.json" \
      --env "${COMMON_ENV[@]}" \
            "R3S3B3_ARM=$arm" \
            "R3S3B3_LF_COND_SET=$cond_set" \
            "R3S3B3_LF_COND_CAP=$cap" \
            "R3S3B3_SPLIT_SEED=$split"
  touch "$marker"
  N_RUN=$((N_RUN + 1))
}

# read r1/r2/r3 for one cell OUT OF THE SEAL (there is no ladder in this file)
ladder_for() {
  python - "$PREREG_JSON" "$1" <<'PY'
import json, sys
c = json.load(open(sys.argv[1]))["payload"]["cells"][sys.argv[2]]
print(" ".join(str(int(c["ladder"][k])) for k in ("r1", "r2", "r3")))
PY
}

# ── the grid, card `recipe.env._grid` under ADR r3-0007 option C ─────────────
# Per sharp cell: 5 legs (A0_nolf, A3c@r1, A3c@r2, A3c@r3, A1_lf_all) x
# SPLIT_SEED in {0,1,2} = 15 legs; 4 sharp cells = 60. ifc_heat is native
# (N_hf = 5, one draw): 5 legs. Plus 1 guard leg. TOTAL 66 legs/seed — the
# card's `_grid` budgets <= 71 because it was written before ADR r3-0007 made
# ifc_poisson report-only (60 + 10 + 1); option C removes its 5 legs.
#
# NEVER `--datasets panel`: round2/eval/panel_data.py::load_config reads the
# ROUND-2 panel (helmholtz in, ifc_heat out). Datasets are always named
# explicitly. `--dataset_dir` is bound by score_panel.py to the main-tree
# stripped view; R3S3B3_DATA_BINDING_ASSERT=1 is the check.
SHARP_CELLS=(sharp__cahn_hilliard sharp__allen_cahn_2d sharp__fisher_kpp_2d sharp__phase_field_crystal_2d)
SPLIT_DRAWS=(0 1 2)                      # HF-SUBSET DRAWS, never a seed CI

for ds in "${SHARP_CELLS[@]}"; do
  read -r R1 R2 R3 <<<"$(ladder_for "$ds")"
  echo "[ladder] $ds sealed r1,r2,r3 = $R1,$R2,$R3 (r4 = FULL = the A1_lf_all arm)"
  for d in "${SPLIT_DRAWS[@]}"; do
    run_leg A0_nolf          "$ds" "$d" none      0    "$EPOCHS"
    run_leg A3c_lf_uncov_cap "$ds" "$d" uncovered "$R1" "$EPOCHS"
    run_leg A3c_lf_uncov_cap "$ds" "$d" uncovered "$R2" "$EPOCHS"
    run_leg A3c_lf_uncov_cap "$ds" "$d" uncovered "$R3" "$EPOCHS"
    run_leg A1_lf_all        "$ds" "$d" all       0    "$EPOCHS"
  done
done

# ifc_heat: native HF split (N_hf = 5), one draw
IFC=ifc_heat
read -r R1 R2 R3 <<<"$(ladder_for "$IFC")"
echo "[ladder] $IFC sealed r1,r2,r3 = $R1,$R2,$R3 (r4 = FULL = the A1_lf_all arm)"
run_leg A0_nolf          "$IFC" native none      0    "$EPOCHS"
run_leg A3c_lf_uncov_cap "$IFC" native uncovered "$R1" "$EPOCHS"
run_leg A3c_lf_uncov_cap "$IFC" native uncovered "$R2" "$EPOCHS"
run_leg A3c_lf_uncov_cap "$IFC" native uncovered "$R3" "$EPOCHS"
run_leg A1_lf_all        "$IFC" native all       0    "$EPOCHS"

# 1 leg: the guard set at the contract tier (native N_hf via GUARD_NSUB=off),
# into its OWN work root so it is never scanned by the stale-checkpoint audit
# above (see the pre-flight (b) comment).
run_leg A1_lf_all heat_local 0 all 0 "$GUARD_EPOCHS" \
        "$OUT_DIR/training_guard_contract_tier_excluded"

# ── post-run stale-checkpoint audit (reported, not blocking on the last leg) ─
echo "[post] stale-checkpoint audit over the legs this job produced"
python "$TOOLS_DIR/stale_checkpoint_audit.py" \
    --root "$OUT_DIR/training" \
    --mtime-slack-seconds 300 \
    --out "$OUT_DIR/preflight/stale_checkpoint_audit_post_s${SEED}.json" || true

echo "[$(date -u +%FT%TZ)] done; legs run=$N_RUN skipped_as_done=$N_DONE (expect 66 total)"
ls -1 "$OUT_DIR/eval"/result_*__s${SEED}.json | wc -l | xargs echo "[count] result JSONs for seed $SEED:"
