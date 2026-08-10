# round3/tools — index

Shared, parameterized instruments for round 3.
Everything here takes CLI arguments only: **no hardcoded stream, batch or output paths**.
Run under the repo venv (`source ${PROJECT_ROOT}/.venv/bin/activate`) and, for anything heavier than a few seconds, under `timeout --kill-after=30s 1200 python ...`.

Every tool that scores imports `mffp_autoresearch/round2/eval/{nrmse.py,panel_data.py}` read-only, so all numbers are on the round's own metric definitions.

| tool | what it measures | invocation | provenance |
|---|---|---|---|
| `make_round3_anchors.py` | builds `state/anchors/launch_anchors.json` (per-card panel geomeans, training-free floors, repaired-ifc floors) from the anchor cards' output trees | `python tools/make_round3_anchors.py` | round-3 launch (ADR r3-0001 D6) |
| `recompute_ac_reference_floors.py` | recomputes the allen_cahn copy-LF reference and floors after the test-split trim | `python tools/recompute_ac_reference_floors.py` | ADR r3-0003 D1 |
| `trim_ac_task_void.py` | removes the task-void allen_cahn test rows (per-row copy-LF gap below threshold) | `python tools/trim_ac_task_void.py` | ADR r3-0003 D1 |
| `response_decomposition.py` | **whether a model learned a condition->field MAP at all**: per-arm response amplitude (`sigma_pred/sigma_hf`), response alignment (`cos(pred anomaly, HF anomaly)`), own spread, plus pairwise "how far apart are two arms AS FUNCTIONS" distances. Two arms can share an nRMSE for opposite reasons; alignment ~0 means condition-independent noise. | `python tools/response_decomposition.py --dataset <name> --pred LABEL=/path/preds.npz [--pred ...] [--pred-key pred_test] [--split test] [--out out.json]` | `r3s3_lf_value-B1` turn 1 |
| `stale_checkpoint_audit.py` | **result JSONs produced WITHOUT training** — the "re-score that resumed from a completed checkpoint" defect class, which every hash/floor seam passes because references are recomputed live while only the weights are stale. Flags `ckpt mtime < result mtime`, `resumed_from_step >= steps`, collapsed `train_seconds`, and (optionally) checkpoints predating a dataset swap. **Run after any re-score campaign, trim, or ladder repair.** | `python tools/stale_checkpoint_audit.py --root <outputs dir> [--pattern '*_e*_s*.json'] [--data-changed-after 2026-08-05T18:33] [--out audit.json] [--fail-on-stale]` | `r3s3_lf_value-B1` turn 2 |
| `lsi_transfer_stability_audit.py` | **closed-form correctors that AMPLIFY instead of correcting.** Reads `T_band_mean_abs` / `band_contribution_profile` / `split_protocol` from any diag sidecar in the `s4_router → r2s2_stack → r3s2_stack_ic` lineage and flags `AMPLIFYING` (\|T\|>1 in a band), `SEED_UNSTABLE` (band \|T\| swings >2× across seeds), `SAMPLE_STARVED` (`n_fit` below the tolerance) and `UNREGULARISED` (ridge 0 on an amplifying cell). The failure it was written from turned a 3-sample unregularised Wiener fit above the LF Nyquist into a 15× scored-nRMSE swing. **Run after any card whose stage 2 contains an LSI/Wiener/deconvolution pre-stage, and after any change to the fit-fold protocol.** | `python tools/lsi_transfer_stability_audit.py --diag-root <eval dir> [--pattern 'diag_*_e200_s*.json'] [--amplify-tol 1.0] [--seed-ratio-tol 2.0] [--min-fit 32] [--out audit.json] [--fail-on-flag]` | `r3s2_field_reach-B1` turn 1 |
| `task_linearity_audit.py` | **whether a cell is a closed-form task in disguise, and whether its condition→field map is learnable at all.** Model-free, seed-free, training-free, dataset-side only: oracle affine residual (same estimator as the certified `affine_on_hf_train` floor), PCA rank of the field ensemble, map-smoothness ratio (nearest-in-condition vs random-pair field difference), and mean-removed variance fraction. Verdicts `CLOSED_FORM_TASK` / `NON_SMOOTH_MAP` / `LEVEL_DOMINATED`. **Run before committing GPU time to a cell**: it separates cells where nonlinear MF fusion can pay from cells a 6-parameter closed form already solves, and it flags the project's `rel-l2-is-level-dominated` trap. | `python tools/task_linearity_audit.py --datasets a,b,c [--split test] [--max-samples 128] [--affine-tol 1e-4] [--smoothness-tol 0.95] [--out report.json]` | `r3s2_field_reach-B1` turns 2–3 |

## Verified invocations (2026-08-10)

```bash
# lsi_transfer_stability_audit — positive control (the defect it was written from)
python mffp_autoresearch/round3/tools/lsi_transfer_stability_audit.py \
  --diag-root mffp_autoresearch_outputs/round3/r3s2_field_reach/B1/eval \
  --pattern 'diag_*_e200_s*.json'
# -> FLAGGED 3/8. ifc_poisson: AMPLIFYING(b4:66.2), SEED_UNSTABLE(b4:10.6x),
#    SAMPLE_STARVED(n_fit=3), UNREGULARISED(ridge=0); band-4 error contribution
#    s0=4.625 s1=3.833 s2=2312. Also flags the guard cell `fluid` (b4 |T|=15.2,
#    n_fit=206 so seed-stable) and ifc_heat (SAMPLE_STARVED only).

# lsi_transfer_stability_audit — cross-card control on the round-2 anchor
python mffp_autoresearch/round3/tools/lsi_transfer_stability_audit.py \
  --diag-root mffp_autoresearch_outputs/round3_anchors/r2s2_stacked-B1/eval \
  --pattern 'diag_*_e200_s*.json'
# -> FLAGGED 4/7; ifc_poisson reproduces BIT-FOR-BIT (b4 = 6.2398/6.2398/66.219),
#    and sharp__phase_field_crystal_2d is independently flagged
#    AMPLIFYING(b4:10.4) with band-3 error contribution 5.8/10.6/29.2.

# task_linearity_audit — reproduces r3s2-B1 turns 2-3 exactly
python mffp_autoresearch/round3/tools/task_linearity_audit.py \
  --datasets sharp__allen_cahn_2d,sharp__cahn_hilliard,sharp__fisher_kpp_2d,ifc_poisson,ifc_heat,sharp__phase_field_crystal_2d \
  --split test --max-samples 128
# -> ifc_poisson oracle affine 2.92e-08, rank99=5, var@cond 1.000000 => CLOSED_FORM_TASK
#    ifc_heat 0.0376882 (== the certified launch_anchors oracle value) => LEVEL_DOMINATED
#    cahn_hilliard smoothness 0.9796 => NON_SMOOTH_MAP ; fisher_kpp meanrm var 0.00504 => LEVEL_DOMINATED
#    allen_cahn 0.459838 / 0.7912 => mf-fusion-relevant ; pfc 0.776563 / 0.9900 => NON_SMOOTH_MAP
```

## Verified invocations (2026-08-08)

```bash
# response_decomposition — reproduces r3s3-B1 turn 1 exactly
python mffp_autoresearch/round3/tools/response_decomposition.py \
  --dataset sharp__cahn_hilliard \
  --pred A0=.../A0_nolf__sharp__cahn_hilliard__d0__e200__s0/r3s3_lf_channels/sharp__cahn_hilliard_e200_s0_preds.npz \
  --pred A2=.../A2_lf_covered__.../sharp__cahn_hilliard_e200_s0_preds.npz \
  --pred A1=.../A1_lf_all__.../sharp__cahn_hilliard_e200_s0_preds.npz
# -> A0 nRMSE 1.257361 amp 0.5941 align 0.0957 | A2 1.291956 / 0.6147 / 0.1032 | A1 0.528166 / 0.7671 / 0.7128
#    pairwise A0->A2 0.31961, A0->A1 1.04031, A2->A1 1.09378

# stale_checkpoint_audit — positive control (the defect it was written from)
python mffp_autoresearch/round3/tools/stale_checkpoint_audit.py \
  --root mffp_autoresearch_outputs/round3_anchors/r2s3_lf_train_signal-B3/eval \
  --pattern 'ifc*_e200_s*.json' --data-changed-after 2026-08-05T18:33
# -> STALE 6/12 (all six ifc_poisson legs), OK on all six ifc_heat legs

# stale_checkpoint_audit — negative control
python mffp_autoresearch/round3/tools/stale_checkpoint_audit.py \
  --root mffp_autoresearch_outputs/round3/r3s3_lf_value/B1/work --pattern '*_e200_s*.json'
# -> STALE 0/225
```
