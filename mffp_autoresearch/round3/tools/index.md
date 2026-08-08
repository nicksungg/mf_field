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
