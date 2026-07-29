# `tools/` — promoted round-1 probes

Reusable, parameterized diagnostics promoted out of experiment scratchpads.
Every tool: CLI args only (no hardcoded stream/batch paths), read-only w.r.t.
`models/`, `eval/`, `data/`, scored through `round1/eval/nrmse.py` when it
produces a metric.

**Append to this file — never rewrite entries you did not add.** One row per
tool: name, what it measures, invocation, provenance card.

| tool | what it measures | provenance card |
|---|---|---|
| `ladder_level_diagnostic.py` | a multi-fidelity dataset's ladder structure before a model is designed for it (level-to-level field shape, amplitude law, index alignment) | s1_poisson-B1 turn 1 |
| `field_error_decomposition.py` | splits a predictor's test error into per-sample AMPLITUDE vs STRUCTURE, plus the per-sample-gain oracle | s1_poisson-B1 turn 2 |
| `lf_conditioned_headroom.py` | how much of a dataset's copy-LF error is removable, training-free, by conditioning on the per-sample LF FIELD; classifies datasets A (residual-learnable) / B (residual-unlearnable) | s2_beyond_copy-B1 turn 2 |
| `lf_at_inference_audit.py` | whether a model family actually consumes the LF field at inference, or only during training | s2_beyond_copy-B1 turn 3 |
| `render_readme.py` | regenerates `round1/README.md` from the experiment cards (housekeeping, not a probe) | round infrastructure |

---

## `lf_conditioned_headroom.py`

**Measures.** A ladder of training-free predictors on one or more panel datasets,
scored with `round1/eval/nrmse.py` against `round1/eval/panel_data.py`'s copy-LF:

`L0 copylf` · `L1 alpha*copylf` (one train-fitted scalar) · `L2 copylf + mean train
residual` · `L3 copylf + kNN-in-X residual` · `L4 field lookup keyed on LF` ·
**`L5 copylf + kNN-in-LF residual`** · `L6 low-passed L5` · `Lx knnX{k} field
lookup` · `O2` per-sample rescale oracle (labelled, uses HF).

**Read it as.** `L5 << 1` → **Class A**, the residual `hf−lf` is a function of the
LF field and an LF-input residual architecture has real headroom. `L5 ≈ 1` and
`L1 ≈ 1` → **Class B**, copy-LF is already near-optimal for what (X, LF) determine
at this `N_train`; target *matching* copy-LF, not beating it. `L3 >> L5` → the
lever is the query KEY (LF-conditioning), not the additive-residual form.
`leak_control_test_over_train_nn_dist ≈ 1` confirms the test set is not a
near-duplicate of train in signature space.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/lf_conditioned_headroom.py \
    --datasets sharp__phase_field_crystal_2d,ext__helmholtz_2d \
    --out /path/to/headroom.json [--sig 16] [--ks 1,5,10]
# whole panel from project.yaml:
python tools/lf_conditioned_headroom.py --datasets PANEL --out headroom.json
```
Pure numpy on the login node; ~1–3 min per 256×256 dataset. Datasets whose test
split ships no LF (e.g. `ifc_poisson`) are skipped with an `error` field.

**Verified.** Run 2026-07-29 on `sharp__phase_field_crystal_2d,ext__helmholtz_2d`
→ `L5_lf_plus_knnLF5_resid` 0.5620 / 0.7851, leak control 1.31 / 1.00 —
identical to the source probe (`s2_beyond_copy-B1` card part 6, F6/F9).

**Provenance.** `worktrees/s2_beyond_copy/B1/scratchpad/reanalysis_turn_2.py`;
card `experiment_cards/s2_beyond_copy/batch_1/B1.json` part 6, findings F6–F9.

---

## `lf_at_inference_audit.py`

**Measures.** For every family directory with a `smoke_eval.py`: each source line
that reads a TEST-split field, the fidelity key used, the declared `mf_mechanism`,
whether an LF surrogate is built from `X_te`, and whether training uses
`min(lf_fids)` or `max(lf_fids)` (copy-LF always uses `max`).

**Why it matters.** `skill = nRMSE(model) / nRMSE(copy-LF)` compares a model
against a baseline that receives the per-sample coarse solve. If the model does
not receive it at inference, the comparison is LF-blind-model vs LF-using-baseline
and any "fusion failure" it reports is an input gap, not a mechanism gap.
`reads_test_lf` is the load-bearing field; `surrogate_lf_at_test` and
`lf_fidelity_used_in_training` are import-graph heuristics — treat as leads.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/lf_at_inference_audit.py \
    --models_dir "$FACTORY_ROOT/models" --out /path/to/lf_audit.json \
    [--families a,b,c] [--verbose]
```
< 2 s, pure file reads.

**Verified.** Run 2026-07-29 over `mf_field/factory_mffp/models` →
**0 of 27 families read the test split's LF field at inference**, matching the
runtime forward-hook audit (M1) recorded in card part 5.

**Provenance.** `worktrees/s2_beyond_copy/B1/scratchpad/reanalysis_turn_3.py`;
card `experiment_cards/s2_beyond_copy/batch_1/B1.json` part 6, finding F14.
