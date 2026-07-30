# Brainstormer Report — Stream `s4_hybrid_routing`, Batch 3

**Stream**: `s4_hybrid_routing` · **Batch**: 3 (ROUND SYNTHESIS / ROUTER)
**Total iterations**: 1 · **Slot filled**: 1 (`model`) · **Reopen candidates resolved**: 0 of 0 (none exist)

## Slot

- **Category**: `mf_composition_router_superlearner_lsi_cleaned_target`
- **Card type**: `model`

- **Motivation**:
  The round's synthesis slot takes the ONE form the prior-art verdict leaves open and
  claims nothing else. On the router itself the verdict is explicit —
  **D1: `preempted-but-MF-composition-open (cite)`** — *"The **selection rule is not open**
  (discrete super learner) and **availability-keyed gating is not open** (missing-modality
  MoE). Open: no fetched source routes on **fidelity availability inside a multi-fidelity
  PDE surrogate**, and none routes between a **defect-correction** path and a
  **transfer-learning** path. **Claim zero novelty for the router.** The card's
  contribution is the composition + its controls; the honest framing is "the discrete
  super learner applied per dataset over a 2-element library, where library membership is
  itself determined by a data property (does the test split ship LF?)"."*
  The card's single open claim is the TARGET —
  **D3: `preempted-but-MF-composition-open (cite)` — the card's strongest open surface** —
  *"In **every** fetched source the pre-stage is a *fixed classical solver*, a *learned*
  deconvolution layer, or a *scalar/affine* fidelity correlation. **Nobody fits a
  |k|-dependent LSI transfer function to the fidelity gap and then trains a corrector on
  ITS residual**, and nobody reports the zero-parameter filter as a scored floor beside the
  trained model."*
  The gate is cited, not claimed (**D2 `preempted (cite)` — outright**,
  https://arxiv.org/abs/1608.00060 *"K-fold sample splitting, which we call
  cross-fitting"*); the fitted taper is inherited, not claimed (**D4 `preempted (cite)` —
  textbook, twice; nothing open**); and the LSI-alone / corrector-alone controls ship in
  the same JSON because **D5** says the *practice of reporting them* is the transferable
  output. The claim shape follows the verdict's own instruction: *"the router's honest
  predicted gain is 'no dataset is worse than the better of its two branches', a
  **no-harm** claim, and the falsification clause should be written against that."*

- **Concrete config**:

  A single family `models_r1/s4_router`, vendored from `models_r1/s6_local_repair`
  @ `d083d44` (s6_local-B2), implementing **two nested discrete super learners** plus one
  target change, run as a **6-arm sweep with a fixed promotion rank**.

  1. **L0 — availability gate (zero training, a data property).** `test["lf_fids"]` empty
     → champion transfer branch (`ifc_poisson` only, the substrate's existing
     `run_champion` path, `S6_FALLBACK_NO_TEST_LF=champion`); non-empty → the DC library
     (all 5 other panel datasets and all 3 guard datasets).
  2. **L1 — discrete super learner over a 2-element library** `{lsi_alone, corr_cleaned}`,
     selected by **cross-validated risk in the scored metric** (per-sample relative L2,
     4-fold inside the held-out slice `val_idx`, `S6_GATE_HOLDOUT_FRAC=0.2`).
  3. **The open claim (D3).** `corr_cleaned` retargets the stage-1 corrector onto the
     **fitted-LSI-cleaned residual**: fit `T(k) = Σ_n R̂_n conj(L̂F_n) / Σ_n |L̂F_n|²` on
     `fit_idx` only (the existing `lsi_filter.fit_transfer`), form
     `R' = R − irfft2(rfft2(LF)·T)`, train the corrector on `R'`, and predict
     `pred = LF + C_LSI + α·Δ_NN`. `α = 0` reproduces the zero-parameter LSI branch
     **bit-exactly**, so the LSI floor is a structural lower bound of the trained branch.
  4. **α level — trust head, reused per the s6-B2 register spec.** KEEP: out-of-fold
     fitting on a slice the corrector never saw, ridge on standardized features,
     `{persample_head, global_scalar, zero}` by k-fold CV, `α̂ = 0` bit-exact fallback, the
     own-correction band fractions (67–83 % of the head's weight mass), and
     `borrow_partner_stages` pairing. **CHANGE 1 (load-bearing)**: regress the α that
     minimises the **SCORED** metric — weight the per-sample regression by `1/‖Y_i‖²` —
     not the raw L2 optimum `⟨R,C⟩/‖C‖²`. **CHANGE 2**: a per-sample no-harm cap that
     shrinks α̂ toward 0 whenever the predicted relative gain is inside the dataset's
     certified floor.
  5. **OOF instrumentation (D2, cited not claimed).** Every stage prints
     `val_rel_l2_base_oof / val_rel_l2_base_insample`; no joint SGD may re-tune a
     selector-fitted α (enforced by freezing the corrector before any α stage, as the
     substrate already does); the **no-stage-3′ counterfactual is a free within-run leg**
     (it is the `corr_cleaned` arm itself).
  6. **Deliberately excluded**: the corrector-input wrap-continuity repair (it would break
     the `corr_plain` replica gate that makes the D3 contrast paired, and s6-B2 part 7
     files it as s6_local-B3 hygiene) — replaced by a mandatory **0-GPU**
     `tools/boundary_interior_split.py` interior-16 report on every per-dataset verdict.
     Also excluded: any attention path (s4-B2 register), so the
     permute-queries-before-chunking ride-along is **not applicable** here and stays a
     standing note on `tools/pooling_support_invariance.py`.

  **Arm table (ADR 0007: sweep with promotion rank fixed pre-submit; controls never
  promotable; screen numbers never reportable).**

  | tag | role | promotable | GPU |
  |---|---|---|---|
  | `router` | **PRIMARY** — L0 + L1 + `persample_head_rel` (CHANGE 1) + no-harm cap (CHANGE 2) | **rank 1** | borrows `corr_cleaned` stages 0–2 (~0) |
  | `corr_cleaned` | D3 branch alone (`heldout_scalar` α); **also the no-stage-3′ counterfactual** | **rank 2** | trains |
  | `corr_plain` | CONTROL — s6-B2 `circ_repair` replica (raw-residual target); paired denominator for the D3 claim + gate V1 | never | trains |
  | `lsi_ctrl` | CONTROL — zero-parameter fitted-LSI floor, scored beside the trained model (D5) | never | ~0 (except the ifc_poisson champion leg) |
  | `head_l2` | CONTROL for CHANGE 1 — raw-L2 α head on the same `corr_cleaned` substrate | never | borrows (~0) |
  | `champion_ctrl` | CONTROL — champion transfer path forced on the 5 LF-bearing panel sets; re-measures the stream anchor in-batch | never | trains |

  **Clause-design principle**: every clause is a **paired ratio between two arms on the
  same dataset**, hence denominator-free, hence exactly invariant to the `(r−1)/2`
  registration artifact — honouring s2-B2's standing rule without touching the frozen
  metric (immutable 4). `tools/registration_skill_split.py` is a MANDATORY analysis
  obligation on every sharp-set number reported, but decides no clause.

- **Recipe**:

```json
{
  "base_family": "s6_local_repair",
  "base_commit": "d083d44b09cd6ea2152212d7d7c0e2a0876d3255",
  "family_dir": "models_r1/s4_router",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "S6_ARM": "router",
    "S6_VARIANT": "local_pixel_gate",
    "S6_SELECTOR": "oof_persample_head",
    "S6_KERNEL": "7",
    "S6_DEPTH": "4",
    "S6_WIDTH": "32",
    "S6_PAD_MODE": "circular_if_periodic",
    "S6_PERIODIC_TEST": "wrap_continuity_ratio_hf_train",
    "S6_PERIODIC_TOL": "1.25",
    "S6_LF_FID": "max",
    "S6_LF_SOURCE": "dataset_lf_fidelity",
    "S6_GATE_HOLDOUT_FRAC": "0.2",
    "S6_GATE_INIT": "zero",
    "S6_GATE_LINESEARCH_INCLUDES_ZERO": "1",
    "S6_LSI_RIDGE": "0",
    "S6_LSI_SIDECAR": "1",
    "S6_LSI_F6_TOL": "0.02",
    "S6_BAND_EDGES_FRAC": "0,0.125,0.25,0.5,1.0",
    "S6_HEAD_MODEL": "ridge",
    "S6_HEAD_CANDIDATES": "persample_head,global_scalar,zero",
    "S6_HEAD_CV_FOLDS": "4",
    "S6_HEAD_RIDGE_GRID": "1e-3,1e-2,1e-1,1,10",
    "S6_HEAD_FEATURES": "X,log_lf_l2,log_lf_grad_ratio,log_lf_band_frac4,log_corr_l2_ratio,log_corr_band_frac4",
    "S6_HEAD_ALPHA_CLIP": "0,1.5",
    "S6_HEAD_MIN_GAIN": "1e-3",
    "S6_LEAKAGE_TRIPWIRE": "1",
    "S6_REPLICA_TOL": "0.10",
    "S6_ASSERT_PAIRED_CORRECTOR": "1",
    "S6_PIXEL_OOF_SIDECAR": "0",
    "S6_FALLBACK_NO_TEST_LF": "champion",
    "S6_DIAG_OUT": "mffp_autoresearch_outputs/round1/s4_hybrid_routing/B3/eval",
    "S4_TARGET": "lsi_cleaned",
    "S4_ROUTER": "1",
    "S4_ROUTER_LEVELS": "availability,cv_library",
    "S4_DC_LIBRARY": "lsi_alone,corr_cleaned",
    "S4_ROUTER_RISK": "per_sample_rel_l2",
    "S4_ROUTER_CV_FOLDS": "4",
    "S4_ALPHA_OBJECTIVE": "rel_l2",
    "S4_NOHARM_CAP": "1",
    "S4_NOHARM_CAP_SOURCE": "state/noise_floor.json:min_claimable_effect_relative",
    "S4_OOF_SCREEN": "1",
    "S4_FORCE_BRANCH": "none",
    "S4_BORROW_FROM": "corr_cleaned",
    "S4_EMIT_PREDS": "1",
    "S4_PREREG_ROUTE": "ifc_poisson=champion,ext__helmholtz_2d=alpha_zero,sharp__phase_field_crystal_2d=corr_cleaned_or_lsi,sharp__allen_cahn_2d=lsi_alone,sharp__fisher_kpp_2d=corr_cleaned,sharp__cahn_hilliard=lsi_alone,fluid=corr_cleaned,sharp__sod_1d=corr_cleaned,heat_local=corr_cleaned",

    "_arms": [
      {"tag": "router", "role": "PRIMARY, promotion rank 1", "promotable": true,
       "S6_ARM": "router", "S6_SELECTOR": "oof_persample_head",
       "S4_TARGET": "lsi_cleaned", "S4_ROUTER": "1", "S4_ALPHA_OBJECTIVE": "rel_l2",
       "S4_NOHARM_CAP": "1", "S4_BORROW_FROM": "corr_cleaned"},
      {"tag": "corr_cleaned", "role": "D3 branch alone + the free no-stage-3' counterfactual; promotion rank 2", "promotable": true,
       "S6_ARM": "corr_cleaned", "S6_SELECTOR": "heldout_scalar",
       "S4_TARGET": "lsi_cleaned", "S4_ROUTER": "0", "S4_NOHARM_CAP": "0",
       "S4_BORROW_FROM": "none"},
      {"tag": "corr_plain", "role": "CONTROL — s6-B2 circ_repair replica (raw-residual target); paired denominator for S1 + validity gate V1", "promotable": false,
       "S6_ARM": "corr_plain", "S6_SELECTOR": "heldout_scalar",
       "S4_TARGET": "raw", "S4_ROUTER": "0", "S4_NOHARM_CAP": "0",
       "S4_BORROW_FROM": "none"},
      {"tag": "lsi_ctrl", "role": "CONTROL — zero-parameter fitted-LSI scored floor (D5); validity gate V2", "promotable": false,
       "S6_ARM": "lsi_ctrl", "S6_VARIANT": "lsi_ctrl", "S6_SELECTOR": "heldout_scalar",
       "S4_TARGET": "raw", "S4_ROUTER": "0", "S4_NOHARM_CAP": "0",
       "S4_BORROW_FROM": "none"},
      {"tag": "head_l2", "role": "CONTROL for CHANGE 1 — raw-L2 alpha head on the corr_cleaned substrate (paired, ~0 GPU)", "promotable": false,
       "S6_ARM": "head_l2", "S6_SELECTOR": "oof_persample_head",
       "S4_TARGET": "lsi_cleaned", "S4_ROUTER": "0", "S4_ALPHA_OBJECTIVE": "l2",
       "S4_NOHARM_CAP": "0", "S4_BORROW_FROM": "corr_cleaned"},
      {"tag": "champion_ctrl", "role": "CONTROL — champion transfer path forced on the 5 LF-bearing panel datasets; in-batch re-measurement of the stream anchor", "promotable": false,
       "S6_ARM": "champion_ctrl", "S4_FORCE_BRANCH": "champion",
       "S4_ROUTER": "0", "S4_NOHARM_CAP": "0", "S4_BORROW_FROM": "none",
       "_datasets": "ext__helmholtz_2d,sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard"}
    ],

    "_promotion_rank": "FIXED BEFORE SUBMIT (ADR 0007): rank 1 = router, rank 2 = corr_cleaned. corr_plain / lsi_ctrl / head_l2 / champion_ctrl are CONTROLS and are NEVER promotable. If the contract screen craters router, corr_cleaned is promoted; if both crater the debugger classifies ALGO. No post-hoc arm switching.",

    "_source": "vendor models_r1/s6_local_repair from branch round1/exp-s6_local-B2 @ d083d44b09cd6ea2152212d7d7c0e2a0876d3255, rename to models_r1/s4_router. Verify each vendored file with `git show d083d44:mffp_autoresearch/round1/worktrees/s6_local/B2/models_r1/s6_local_repair/<f> | sha256sum` and record the sha256-16 in build_notes for bands.py, local_corrector.py, lsi_filter.py, model.py, periodicity.py, trust_head.py, smoke_eval.py, manifest.json. model.py stays the byte-identical copy of factory_root/models/mf_fno_transfer_film/model.py @ 967562e (champion branch, reproduced from source — the factory tree is never written). EDITS: (1) new router.py — the L0 availability gate (made explicit around the substrate's existing `if not test['lf_fids']: run_champion` dispatch) and the L1 discrete-super-learner selection over S4_DC_LIBRARY by 4-fold CV per-sample-relative-L2 risk inside val_idx, with the realised selection, the per-member CV risks and the S4_PREREG_ROUTE agreement/disagreement printed and written to the diag; (2) lsi_filter.py gains `cleaned_residual(LF_fit, R_fit, LF_all, grid, ridge)` returning (T, C_LSI, R') — T fitted on fit_idx ONLY; (3) stage 1's target becomes R' when S4_TARGET=lsi_cleaned and the prediction path becomes LF + C_LSI + alpha*Delta (alpha=0 must reproduce the lsi_alone branch bit-exactly — gate V4); (4) trust_head.py gains S4_ALPHA_OBJECTIVE=rel_l2 (weight the per-sample ridge target by 1/||Y_i||^2) and S4_NOHARM_CAP (shrink alpha_hat toward 0 whenever the predicted per-sample relative gain is inside the dataset's certified relative floor); (5) new oof_screen.py printing val_rel_l2_base_oof / val_rel_l2_base_insample per stage per dataset into the diag; (6) S4_FORCE_BRANCH=champion routes every dataset to run_champion; (7) S4_EMIT_PREDS writes preds_test.npz + rel_l2_per_sample so tools/registration_skill_split.py and tools/boundary_interior_split.py can run read-only afterwards. NEVER edited: round1/eval/, project.yaml, program.md, ADRs, subagent prompts, round1/tools/, factory_root/{eval,baselines,references,scripts,data}/, factory.md, mf_field/akash/**. LSI/registration logic is VENDORED into the family, never imported from round1/tools/, so score_panel.py::code_hash stays complete.",

    "_sweep": "ONE SLURM job, seed 0, six score_panel.py calls serially, each with its arm's --env deltas and its own --out result_panel_<tag>_s0.json; export ROUND1_EVAL_RESULTS=<outputs>/eval/results_<tag> per arm so per-arm result JSONs and ckpt dirs cannot collide (score_panel._run_one derives paths from (family_dir.name, dataset, epochs, seed) only — s1-B2 build trap 1). Checkpoint <ckpt_dir>/arm_<tag>/last.pt mirrored to <ckpt_dir>/last.pt; the meta guard is extended to (arm, variant, target, router_level, stage, epochs_target, grid, seed) so no cross-arm resume is possible. Arm order: corr_cleaned, corr_plain, lsi_ctrl, router, head_l2, champion_ctrl (the two borrowed arms run AFTER their donor).",

    "_guard_arms": ["router", "corr_cleaned", "corr_plain", "lsi_ctrl"],
    "_guard_spec": "same family, --datasets guard, --epochs 200, --seed 0, one score_panel.py call per arm, inside the same sweep job. program.md 2.3 requires a guard run for any panel-win claim; the guard cells also carry the routing-prediction leg's three most informative rows (fluid / sod_1d / heat_local, 1-rho_LSI 0.51943 / 0.25016 / 0.18007) as REPORT-ONLY (immutable 2: the guard set is not promoted to scored status). Expect the periodicity switch to choose ZEROS on all three (measured HF wrap ratios 16.55 / 2.56 / degenerate vs tol 1.25).",

    "_screen": "ONE contract-tier job BEFORE the sweep: --epochs 2 --seed 0, all six arms, --datasets panel and --datasets guard. Plumbing + tripwires only: the alpha=0 identity assertion, the LF-coarser leakage tripwire, gate V2 (epoch-independent, so fully checkable at 2 epochs), gate V4 (router degeneracy) and gate V5 (borrow pairing sha equality). Every arm must score skill <= 1.02 on the five beyond-copy datasets — a violation means the identity construction broke (ALGO). Screen numbers are NEVER reportable (ADR 0007) and live only in build_notes. s6-B2's equivalent screen was 8.6 min on H100; reserve 01:00:00.",

    "_validity_gates": "V1 (replica): corr_plain must reproduce s6-B2 circ_repair seed-0 test nRMSE within S6_REPLICA_TOL=0.10 on all six panel datasets — 0.32945012604380175 / 0.0007204126530396635 / 0.0009363332709684444 / 0.004697840233022452 / 0.04136137418852845 / 0.05562937038722282 (helmholtz / pfc / allen_cahn / fisher_kpp / cahn_hilliard / ifc_poisson). V2 (LSI): lsi_ctrl must reproduce s6-B2 lsi_ctrl within S6_LSI_F6_TOL=0.02 — pfc 0.0006124684737243416, allen_cahn 0.0008318192792299753, fisher_kpp 0.007695081137159533, cahn_hilliard 0.03856875162347986 — and must select alpha=0 on ext__helmholtz_2d. V3 (identity): every arm's alpha=0 path is bit-equal to eval/copylf_baselines.json (|delta| <= 1e-9; already an S6ContractError assert). V4 (router degeneracy): with S4_DC_LIBRARY forced to a single member the router's prediction must be bit-identical to that member's arm (max|delta| == 0) — proves the router adds no silent transformation. V5 (pairing): router and head_l2 must carry corrector_source='loaded_from_partner:corr_cleaned' with donor sha equality on every dataset. A miss on any gate is ALGO: fix before reading a single contrast.",

    "_analysis_obligations": "MANDATORY, read-only, 0 GPU, on the login node before any verdict is written: (1) tools/registration_skill_split.py --datasets PANEL on every reported sharp-set number (s2-B2 standing rule) — report model_skill_vs_best_fix and the corrected geomean beside the frozen-metric skill table; (2) tools/boundary_interior_split.py on every per-dataset verdict (s6-B2 part 7 item 4 — a crop_sign_flip verdict is decided by a one-cell rim); (3) tools/defect_correction_learnability.py rho_val_heldout beside every routing decision; (4) tools/stage_keep_test_audit.py on the shipped JSONs to confirm the S4_OOF_SCREEN ratios independently.",

    "_sbatch": "partition gpu, --gres=gpu:h100:1 (ADR 0005, project.yaml). SWEEP --time=03:00:00 (ledger: s6-B1 200-epoch 6-dataset panel run 17.95 min on H100; s6-B2's 5-arm sweep + 2 guard arms 59:53 => corr_cleaned ~18 + corr_plain ~18 + lsi_ctrl ~6 + router ~4 + head_l2 ~4 + champion_ctrl 5 datasets ~30 + guard legs ~14 = ~94 min, ~110 min with overhead, ~61% of the request). SCREEN --time=01:00:00 (~15 min expected). Job names r1-s4_hybrid_routing-B3-s0; logs under mffp_autoresearch_outputs/round1/s4_hybrid_routing/B3/slurm/. Seeds 1-2 are NOT launched in-round (ADR 0004); scripts/submit_seeds_2_3.sh is written but unused."
  }
}
```

  **FULL sbatch block** — `<worktree>/scripts/01_train_eval.sh` (the orchestrator submits;
  the builder never does):

```bash
#!/bin/bash
#SBATCH --job-name=r1-s4_hybrid_routing-B3-s0
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --output=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s4_hybrid_routing/B3/slurm/%x_%j.out
#SBATCH --error=/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round1/s4_hybrid_routing/B3/slurm/%x_%j.err

set -euo pipefail
SEED="${1:-0}"

PROJECT_ROOT=/resnick/groups/Hippo/ezeng/mf_field
ROUND_ROOT="$PROJECT_ROOT/mffp_autoresearch/round1"
WORKTREE="$ROUND_ROOT/worktrees/s4_hybrid_routing/B3"
OUT_DIR="$PROJECT_ROOT/mffp_autoresearch_outputs/round1/s4_hybrid_routing/B3"
FAMILY="$WORKTREE/models_r1/s4_router"

source "$PROJECT_ROOT/.venv/bin/activate"
mkdir -p "$OUT_DIR/eval" "$OUT_DIR/slurm" "$OUT_DIR/training"

echo "[$(date)] host=$(hostname) gpu=$(nvidia-smi -L | head -1) seed=$SEED"

COMMON=(
  --family_dir "$FAMILY" --epochs 200 --seed "$SEED"
  --env S6_KERNEL=7 --env S6_DEPTH=4 --env S6_WIDTH=32
  --env S6_PAD_MODE=circular_if_periodic
  --env S6_PERIODIC_TEST=wrap_continuity_ratio_hf_train --env S6_PERIODIC_TOL=1.25
  --env S6_LF_FID=max --env S6_LF_SOURCE=dataset_lf_fidelity
  --env S6_GATE_HOLDOUT_FRAC=0.2 --env S6_GATE_INIT=zero
  --env S6_GATE_LINESEARCH_INCLUDES_ZERO=1
  --env S6_LSI_RIDGE=0 --env S6_LSI_SIDECAR=1 --env S6_LSI_F6_TOL=0.02
  --env S6_BAND_EDGES_FRAC=0,0.125,0.25,0.5,1.0
  --env S6_HEAD_MODEL=ridge
  --env S6_HEAD_CANDIDATES=persample_head,global_scalar,zero
  --env S6_HEAD_CV_FOLDS=4 --env S6_HEAD_RIDGE_GRID=1e-3,1e-2,1e-1,1,10
  --env S6_HEAD_FEATURES=X,log_lf_l2,log_lf_grad_ratio,log_lf_band_frac4,log_corr_l2_ratio,log_corr_band_frac4
  --env S6_HEAD_ALPHA_CLIP=0,1.5 --env S6_HEAD_MIN_GAIN=1e-3
  --env S6_LEAKAGE_TRIPWIRE=1 --env S6_REPLICA_TOL=0.10
  --env S6_ASSERT_PAIRED_CORRECTOR=1 --env S6_PIXEL_OOF_SIDECAR=0
  --env S6_FALLBACK_NO_TEST_LF=champion
  --env S6_DIAG_OUT="$OUT_DIR/eval"
  --env S4_ROUTER_LEVELS=availability,cv_library
  --env S4_DC_LIBRARY=lsi_alone,corr_cleaned
  --env S4_ROUTER_RISK=per_sample_rel_l2 --env S4_ROUTER_CV_FOLDS=4
  --env S4_NOHARM_CAP_SOURCE=state/noise_floor.json:min_claimable_effect_relative
  --env S4_OOF_SCREEN=1 --env S4_EMIT_PREDS=1
  --env S4_PREREG_ROUTE=ifc_poisson=champion,ext__helmholtz_2d=alpha_zero,sharp__phase_field_crystal_2d=corr_cleaned_or_lsi,sharp__allen_cahn_2d=lsi_alone,sharp__fisher_kpp_2d=corr_cleaned,sharp__cahn_hilliard=lsi_alone,fluid=corr_cleaned,sharp__sod_1d=corr_cleaned,heat_local=corr_cleaned
)

run_arm () {   # run_arm <tag> <datasets> <extra --env ...>
  local TAG="$1"; local DS="$2"; shift 2
  export ROUND1_EVAL_RESULTS="$OUT_DIR/eval/results_${TAG}"
  mkdir -p "$ROUND1_EVAL_RESULTS"
  echo "[$(date)] ARM=$TAG DATASETS=$DS"
  python "$ROUND_ROOT/eval/score_panel.py" "${COMMON[@]}" \
      --datasets "$DS" --env "S6_ARM=$TAG" "$@" \
      --out "$OUT_DIR/eval/result_${DS}_${TAG}_s${SEED}.json"
}

# --- donor first; the two borrowed arms run after it ---
run_arm corr_cleaned  panel --env S6_VARIANT=local_pixel_gate --env S6_SELECTOR=heldout_scalar \
                            --env S4_TARGET=lsi_cleaned --env S4_ROUTER=0 --env S4_NOHARM_CAP=0 \
                            --env S4_BORROW_FROM=none --env S4_FORCE_BRANCH=none
run_arm corr_plain    panel --env S6_VARIANT=local_pixel_gate --env S6_SELECTOR=heldout_scalar \
                            --env S4_TARGET=raw --env S4_ROUTER=0 --env S4_NOHARM_CAP=0 \
                            --env S4_BORROW_FROM=none --env S4_FORCE_BRANCH=none
run_arm lsi_ctrl      panel --env S6_VARIANT=lsi_ctrl --env S6_SELECTOR=heldout_scalar \
                            --env S4_TARGET=raw --env S4_ROUTER=0 --env S4_NOHARM_CAP=0 \
                            --env S4_BORROW_FROM=none --env S4_FORCE_BRANCH=none
run_arm router        panel --env S6_VARIANT=local_pixel_gate --env S6_SELECTOR=oof_persample_head \
                            --env S4_TARGET=lsi_cleaned --env S4_ROUTER=1 \
                            --env S4_ALPHA_OBJECTIVE=rel_l2 --env S4_NOHARM_CAP=1 \
                            --env S4_BORROW_FROM=corr_cleaned --env S4_FORCE_BRANCH=none
run_arm head_l2       panel --env S6_VARIANT=local_pixel_gate --env S6_SELECTOR=oof_persample_head \
                            --env S4_TARGET=lsi_cleaned --env S4_ROUTER=0 \
                            --env S4_ALPHA_OBJECTIVE=l2 --env S4_NOHARM_CAP=0 \
                            --env S4_BORROW_FROM=corr_cleaned --env S4_FORCE_BRANCH=none
run_arm champion_ctrl ext__helmholtz_2d,sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard \
                            --env S4_FORCE_BRANCH=champion --env S4_ROUTER=0 \
                            --env S4_NOHARM_CAP=0 --env S4_BORROW_FROM=none

# --- guard legs (report-only; program.md 2.3) ---
for TAG in corr_cleaned corr_plain lsi_ctrl router; do
  case "$TAG" in
    corr_cleaned) X=(--env S6_VARIANT=local_pixel_gate --env S6_SELECTOR=heldout_scalar --env S4_TARGET=lsi_cleaned --env S4_ROUTER=0 --env S4_NOHARM_CAP=0 --env S4_BORROW_FROM=none --env S4_FORCE_BRANCH=none) ;;
    corr_plain)   X=(--env S6_VARIANT=local_pixel_gate --env S6_SELECTOR=heldout_scalar --env S4_TARGET=raw --env S4_ROUTER=0 --env S4_NOHARM_CAP=0 --env S4_BORROW_FROM=none --env S4_FORCE_BRANCH=none) ;;
    lsi_ctrl)     X=(--env S6_VARIANT=lsi_ctrl --env S6_SELECTOR=heldout_scalar --env S4_TARGET=raw --env S4_ROUTER=0 --env S4_NOHARM_CAP=0 --env S4_BORROW_FROM=none --env S4_FORCE_BRANCH=none) ;;
    router)       X=(--env S6_VARIANT=local_pixel_gate --env S6_SELECTOR=oof_persample_head --env S4_TARGET=lsi_cleaned --env S4_ROUTER=1 --env S4_ALPHA_OBJECTIVE=rel_l2 --env S4_NOHARM_CAP=1 --env S4_BORROW_FROM=corr_cleaned --env S4_FORCE_BRANCH=none) ;;
  esac
  run_arm "$TAG" guard "${X[@]}"
done

echo "[$(date)] sweep done"
```

  The contract-tier screen is the same script with `--epochs 2`,
  `--time=01:00:00`, `--job-name=r1-s4_hybrid_routing-B3-screen-s0`, results written under
  `$OUT_DIR/screen/` and **never** read into parts 5–7 (ADR 0007).

- **Expected outcome** (metric, Δ vs anchor, why, vs the noise floor):

  | quantity | predicted | comparator | floor | resolvable? |
  |---|---|---|---|---|
  | panel geomean skill, `router` | **0.150 – 0.190** | anchor 6.703016 (`state/anchors/s4_hybrid_routing.json`) | 13.183 % | trivially (≈ −97 %) — REPORTED, **no clause** |
  | panel geomean, `router` vs `lsi_ctrl` (≈ 0.1972) | **−5 % to −24 %** | in-batch zero-parameter floor | 13.183 % | **pre-registered NOT RESOLVABLE** (s6-B2 measured −2.355 % / −4.884 %) |
  | `corr_cleaned / corr_plain` on **pfc** | **0.60 – 0.85** (−15 % to −40 %) | 7.2041e-04 → 4.3e-04…6.1e-04 | 10.000 % | **YES — 1.5–4.0× the floor** |
  | `router` vs `min(branches)`, all 6 panel | **≤ 1.00**, exact equality on ≥ 3 | in-batch branches | 10.000 / 15.323 / 70.165 % | the no-harm clause |
  | pfc `router` vs `head_l2` global-scalar fallback | **0.75 – 1.00** | +21.51 % measured for the raw-L2 head (F11) | 10.000 % | **YES — the effect tested is 2.15× the floor** |
  | worse-than-base sample fraction (CHANGE 2) | 0.27 → **≤ 0.10** (pfc), 0.35 → **≤ 0.10** (helmholtz) | F13 | n/a | report-only |
  | `val_base_oof / val_base_insample`, all stages | **0.90 – 1.15** | s4-B2's 16.4× / 2.9× pathological, 0.82–1.09× benign | n/a | free instrumentation |
  | `ifc_poisson`, every arm | 0.055632 ± 0.1 % (skill ≈ 1.5453) | paper bar 0.036 | 15.323 % | **pre-registered no-op** |
  | guard geomean, `router` | **≤ 0.0624** | `corr_plain` 0.062438, `lsi_ctrl` 0.532461 | none certified | report-only |

  **Why**: the D3 target removes the corrector's obligation to re-derive the |k|-dependent
  transfer function it already fails at the rim (F3: 7.1× over-concentration on pfc,
  22.04 % of its squared error), leaving it only the F6-aligned surplus (cos 0.7630 on
  pfc). The router then cannot do worse than either branch except through selection error,
  and CHANGE 1 removes the one diagnosed cause of selection error at the α level (F11's
  norm mismatch, Pearson 0.9983 to an oracle worth −25.83 %).

- **Expected falsification**:

  **PRIMARY (no-harm)** — the card is falsified if `router`'s test nRMSE exceeds the lower
  of its own two in-batch branches (`min(lsi_ctrl, corr_cleaned)` on the five LF-bearing
  panel datasets; `champion_ctrl` on `ifc_poisson`) by more than that dataset's certified
  relative floor (10.000 % on pfc / allen_cahn / fisher_kpp / cahn_hilliard, 15.323 % on
  ifc_poisson, 70.165 % on helmholtz) on **any** panel dataset — a violation is possible
  only through selection error, for which two mechanisms are already documented
  (cahn_hilliard's val→test `rho` collapse 0.8998 → 0.0839, s6-B2 F9; the pfc head's
  +21.51 % val-selected loss, F11);
  **AND (routing-prediction leg)** the pre-registered routing table is falsified if the
  router's realised branch selection differs from the pre-registration on ≥ 2 of the four
  sharp panel datasets, or if on any dataset whose two branches differ by more than its
  floor the router selects the worse branch (`sharp__cahn_hilliard`, gap 7.24 % < 10.000 %,
  and `ext__helmholtz_2d` are declared **not resolvable in advance** and carry no clause;
  the guard rows are report-only because the guard set is not scored — immutable 2);
  **AND (secondary S1, the one open claim)** D3 is falsified if `corr_cleaned` fails to
  beat `corr_plain` on `sharp__phase_field_crystal_2d` by more than 10.000 % relative test
  nRMSE (predicted −15 % to −40 %; `sharp__fisher_kpp_2d`, `sharp__allen_cahn_2d` and
  `sharp__cahn_hilliard` are pre-registered **not resolvable**, |Δ| < 10 %, and a > 10 %
  move on cahn_hilliard in either direction is recorded in advance as a surprise requiring
  mechanism attention rather than as support);
  **AND (secondary S4, CHANGE 1)** the objective-mismatch diagnosis is falsified if the
  rel-L2-weighted α head is still more than 10.000 % worse than the global-scalar fallback
  on `sharp__phase_field_crystal_2d`;
  with `ext__helmholtz_2d` **report-only by arithmetic** (its 70.165 % floor exceeds even
  the per-sample oracle's −49.50 %), the panel geomean surplus over the zero-parameter
  floor pre-registered as **NOT RESOLVABLE** (predicted −5 % to −24 % vs a 13.183 % floor),
  and `ifc_poisson` pre-registered as a **no-op** (all arms reach the champion fallback;
  predicted spread ≤ 0.1 % around 0.055632 — s6-B1 part 7 item 4: the identical held-out α
  machinery chose α = 0 on **6/6** on a champion-generated base).

- **Prior-art verdict quoted**: see **Motivation** above — D1 and D3 rows quoted verbatim
  from `websearches/s4_hybrid_routing/batch_3/report.md`, with D2, D4 and D5 quoted for the
  gate, the taper and the controls. Fetched citations carried into the card's `prior_art`:
  https://tlverse.org/csp2020-workshop/sl3.html · https://arxiv.org/html/2511.11460v2 ·
  https://arxiv.org/pdf/2605.15179 · https://arxiv.org/abs/2509.24814 ·
  https://arxiv.org/abs/1608.00060 · https://ar5iv.labs.arxiv.org/html/2102.01010 ·
  https://arxiv.org/html/2310.03572 · https://arxiv.org/pdf/2005.05655 ·
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4915073/ ·
  https://vincmazet.github.io/bip/restoration/deconvolution.html ·
  https://mcpanalytics.ai/articles/stacking-ensemble-practical-guide-for-data-driven-decisions
  (non-peer-reviewed, usable only for the statement of the leakage artifact).
  **Novelty claimed: ZERO on the router, ZERO on the OOF gate, ZERO on the LSI filter,
  ZERO on the fitted taper; the single open claim is the D3 target composition.**

- **Immutables self-check**: **pass (10/10)** — full positive evidence in
  [iteration_1.md](iteration_1.md) §"Immutables self-check". Nothing flagged, no revision
  needed. Item 9 quotes the floors numerically (10.000 % = 1.151100 / 11.511001 on pfc,
  1.633407 / 16.334071 allen_cahn, 0.417735 / 4.177355 fisher_kpp, 0.553347 / 5.533466
  cahn_hilliard; 15.323 % = 0.239908 / 1.565633 ifc_poisson; 70.165 % = 9.694961 /
  13.817290 helmholtz; 13.183 % = 0.8836555 / 6.703016 geomean). Item 10 names **LF
  low-mode freezing (`mf_fno_spectral`)** as the nearest pre-falsified lever and states the
  difference: that lever *freezes* LF low modes with a **hard** spectral partition, whereas
  this card **fits** a full complex `T(k)` by least squares, applies it as a smooth
  data-fitted taper, freezes nothing, and uses it only to redefine the corrector's
  **training target**.

- **Anchor reference**: `null` — `s4_hybrid_routing` is a lever stream, so per program.md
  §4.5 the own-stream anchor is implicit (`state/anchors/s4_hybrid_routing.json`,
  `mf_fno_transfer_film` panel geomean **6.703016262587087**, 3-seed, `provisional: false`),
  re-measured in-batch by the `champion_ctrl` control. The real comparators for every
  clause are the in-batch paired arms, not the anchor.

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none — no card under `experiment_cards/s4_hybrid_routing/**` carries `reopen_candidate: true`; s4-B1 and s4-B2 are both `complete`)* | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| B3 | `mf_composition_router_superlearner_lsi_cleaned_target` | A discrete super learner over a 2-element library whose membership is set by a data property (does the test split ship LF?), whose trained branch is retargeted onto the **fitted-LSI-cleaned residual** with the zero-parameter filter scored beside it — 6 arms, 2 promotable, primary claim **no-harm**, every clause a floor-cleared paired ratio | **filled** |
