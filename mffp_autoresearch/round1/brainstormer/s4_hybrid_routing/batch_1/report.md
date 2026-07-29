# Brainstormer Report — Stream `s4_hybrid_routing`, Batch 1

**Stream**: `s4_hybrid_routing`
**Batch**: 1
**Total iterations**: 1
**Slot filled**: 1 / 1
**Reopen candidates resolved**: 0 (none exist — this is the stream's first card)

## Slot

- **Category**: `mf_composition_measurement`
- **Card type**: `model` (it trains 200 epochs; program.md §4.3 reserves
  `diagnostic` for no-training measurements, and §4.4 forbids single-seed
  claims. The websearcher's "claims zero novelty" governs `prior_art`, not
  `card_type`.)
- **Motivation**: Panel-benchmark the built-but-unbenchmarked
  `mf_field/akash/models/fno_transolver_seq` (FNO-FiLM base + zero-init,
  alpha-gated Transolver corrector trained on out-of-fold LF→HF residuals),
  reading the **per-dataset gate `alpha`** as the measurement. The websearcher's
  prior-art verdict for this direction (D1) is
  `preempted-but-MF-composition-open`, and its instruction is verbatim:
  *"**D1 is a measurement card — it should claim no novelty at all**, only that
  it measures whether the +30.6% oracle survives against copy-LF on sharp 2-D"*;
  what it lists as still open is *"out-of-fold LF->HF residual targets under
  N_hf scarcity; the *real LF field* as corrector context; the least-squares +
  line-search `alpha` that makes the hybrid collapse **exactly** to the FNO when
  the correction is useless."* program.md §12.4:
  *"`mf_field/akash/models/fno_transolver_seq` (sequential FNO→Transolver
  residual hybrid) is BUILT but unbenchmarked — batch 1 should start by scoring
  it on the panel (cheap, mostly evaluation)."* The reason it earns GPU time
  rather than being a formality: the certified champion `mf_fno_transfer_film`
  is `FNO2d(cond_dim, ...)` and **never consumes the LF field at test time**
  (verified in its `smoke_eval.py` lines 106–170 — LF appears only as
  pretraining targets), while the copy-LF reference *is* the LF field and has
  skill 1.0 against the champion's 4.18–16.33 on the sharp sets. This artifact
  is the round's first model whose prediction path cross-attends to the **real
  test-time LF field** (all five npz_l panel datasets ship test LF), so the card
  measures how much of that discarded 4–16× information a gated point-based
  corrector recovers — informative whether it wins or loses (program.md §1).
- **Concrete config**:
  1. `models_r1/fno_transolver_seq/` = verbatim copy of the three files from
     `mf_field/akash/models/fno_transolver_seq/` at `967562e`
     (`git diff --stat round1-substrate -- <those paths>` is empty).
  2. Exactly **two** mechanical edits (a third should draw a code-reviewer FAIL —
     the artifact under measurement must stay the built family):
     (a) replace `AKASH = Path(__file__).resolve().parents[2]` with an upward
     search from `__file__` for the first ancestor containing
     `mf_field/akash/common/mffp.py`, raising `RuntimeError` if absent (the
     worktree is a full checkout, so it resolves; `parents[2]` would point at
     the worktree root once the family sits under `models_r1/`);
     (b) make the existing `--ctx_source` default
     `os.environ.get("MFFP_CTX_SOURCE", "auto")` so the knob is recipe-recorded
     (program.md §5.5) — a no-op at the declared value.
  3. Run only through `round1/eval/score_panel.py --datasets panel --epochs 200
     --seed {0,1,2} --env MFFP_CTX_SOURCE=auto`; do **not** set
     `ROUND1_EVAL_RESULTS` (batch 0's `eval/run_batch0.sbatch` did not).
  4. SLURM: one array task per (dataset, seed), `--time 08:00:00` for
     `sharp__allen_cahn_2d` / `sharp__fisher_kpp_2d` / `sharp__cahn_hilliard`
     (batch-0 champion 44.4 min × ≈5.25 epoch-equivalents: LF-pretrain +
     HF-finetune + 4 out-of-fold folds + corrector + epochs/4 joint stage),
     `--time 03:00:00` for the other three. Resume from `<ckpt_dir>/last.pt` is
     already implemented (lines 300–315 / 425–431).
  5. Guard set at contract tier in the seed-0 script
     (`--datasets guard --epochs 2 --seed 0`), per program.md §2.3.
  6. Measurement extraction requires **no new code** — `finalize_and_write`
     already emits, per run: `alpha`, `alpha_least_squares`, `base_only_rel_l2`
     (the *paired within-run control*: the champion recipe on the identical
     seed/split), `base_only_rel_l2_final_fno`, `val_rel_l2_base`,
     `val_rel_l2_hybrid`, `stage3_joint`, `correction_rms_raw_units`,
     `ctx_source`, `ctx_fidelity`, `latency_ms_per_sample`, `peak_mem_mb`
     (`smoke_eval.py` lines 474–500). The analyzer tabulates these per
     (dataset, seed) alongside the scored skills.
- **Recipe**:
  ```json
  {
    "base_family": "fno_transolver_seq",
    "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
    "family_dir": "models_r1/fno_transolver_seq",
    "datasets": "panel",
    "epochs": 200,
    "seeds": [0, 1, 2],
    "env": {"MFFP_CTX_SOURCE": "auto"}
  }
  ```
- **Expected outcome**:
  - *Free sanity gate*: `base_only_rel_l2` reproduces the batch-0 anchor
    per-dataset skills within each dataset's `min_claimable_effect` (the
    stage-1 recipe is the byte-identical `SMOKE` dict + `WORK_CAP = 256`);
    a larger gap means broken plumbing, not science.
  - *Primary*: `alpha > 0` on **≥ 3 of the 5** sharp-2-D panel datasets.
  - *Score*: panel geomean skill moves from the anchor **6.703 [6.219, 7.102]**
    to **4.5–6.0** (−10% to −33%), with ≥ 1 sharp dataset improving by more than
    its noise floor — `sharp__allen_cahn_2d` needs ≥ **1.633** skill units off
    16.334, `sharp__phase_field_crystal_2d` ≥ **1.151** off 11.511,
    `sharp__fisher_kpp_2d` ≥ **0.418** off 4.177, `sharp__cahn_hilliard`
    ≥ **0.553** off 5.533 (each floor = 10% relative). Directional evidence: a
    2-epoch contract-tier run I executed on `ifc_poisson` gave
    `rel_l2=0.438569` vs `base_only=0.490003` (−10.5%) with `alpha=1.5001`, on
    the *weaker* context path.
  - *Not claimed*: skill < 1 anywhere (needs 4–16×; criterion 2 stays open);
    nothing on `ext__helmholtz_2d` (floor **9.695** ≈ 70% relative — recorded,
    never claimed); `ifc_poisson` (floor **0.240** on mean skill 1.566) is a
    watch item.
  - Cratered threshold: 1.5 × 6.703 = **10.05** panel geomean skill at seed 0.
- **Expected falsification**: If the fitted gate `alpha` is 0 on ≥ 4 of the 5
  sharp-2-D panel datasets at seed 0 (the least-squares + line-search-containing-0
  gate rejecting the correction on its own held-out split) **and** no sharp-2-D
  dataset's 3-seed mean skill beats the batch-0 anchor by at least its
  `min_claimable_effect` (allen_cahn 1.633, pfc 1.151, fisher_kpp 0.418,
  cahn_hilliard 0.553 skill units), then the +30.6% FNO↔Transolver pairwise
  oracle does not transfer to sharp-2-D multi-fidelity fusion and routing
  between these two experts is not this stream's lever.
- **Prior-art verdict quoted** (verbatim from
  `websearches/s4_hybrid_routing/batch_1/report.md`, D1 row):
  > **D1** — panel-benchmark the built `fno_transolver_seq` (FNO-FiLM base +
  > zero-init alpha-gated Transolver corrector on out-of-fold LF->HF residuals)
  > | `preempted-but-MF-composition-open` | https://arxiv.org/html/2602.11197
  > (FNO smooth background + ViT high-contrast corrector);
  > https://arxiv.org/abs/2311.12902 (hierarchical FNO + conv-residual +
  > attention, frequency-complementary, sequential, no MF) | Neither source is
  > multi-fidelity. Open: out-of-fold LF->HF residual targets under N_hf
  > scarcity; the *real LF field* as corrector context; the least-squares +
  > line-search `alpha` that makes the hybrid collapse **exactly** to the FNO
  > when the correction is useless. **D1 is a measurement card — it should claim
  > no novelty at all**, only that it measures whether the +30.6% oracle
  > survives against copy-LF on sharp 2-D.

  Card `prior_art` block to transcribe: `verdict:
  "preempted-but-MF-composition-open"`, citations
  `["https://arxiv.org/html/2602.11197", "https://arxiv.org/abs/2311.12902"]`.
- **Immutables self-check**: **pass (10/10)** — every item answered with
  positive evidence in
  [iteration_1.md](iteration_1.md) ("Immutables self-check"), including
  (9) thresholds quoted from `state/noise_floor.json` with helmholtz excluded by
  construction, and (10) nearest pre-falsified lever = "LF low-mode freezing
  (`mf_fno_spectral`)", differing in that no band is frozen and no LF constraint
  is imposed — the LF field enters only as cross-attention context behind a gate
  that is 0 unless it earns held-out improvement.
- **Anchor reference**: `null` (lever stream; program.md §4.5 — own-stream
  anchor 6.703 implicit).
- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _none_ (no prior cards exist in this stream) | — | — | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| 1 | `mf_composition_measurement` | Score the built `fno_transolver_seq` on the panel at smoke tier, 3 seeds, and read the per-dataset gate `alpha` + the paired within-run `base_only` control to decide whether the +30.6% FNO↔Transolver oracle survives on sharp 2-D. | filled |

## Notes for downstream agents

- **Deferred, deliberately** (see iteration_1 "alternatives rejected"): the D2
  router (LF-conditioned, spatially resolved, identity-safe) is batch 2's
  candidate and should be designed from *this* card's measured per-dataset
  `alpha` and `correction_rms_raw_units`; the `ctx_source = fno_base` ablation
  is one env flip (`MFFP_CTX_SOURCE=fno_base`) and belongs in the
  mechanism-analyzer's probe turns, not in this card.
- **Honesty note**: a CPU contract-tier run on
  `sharp__phase_field_crystal_2d` was launched while writing this report and was
  **killed by a 900 s wrapper timeout (exit 143) with no output** — only the
  `ifc_poisson` contract-tier result above is a completed, observed run, and the
  pfc attempt says nothing except that CPU is too slow for it. The
  256²-dataset GPU memory question
  (`n_query=2048 / n_ctx=1024 / corr_batch=4` on a p100) is therefore still open
  and is the builder's contract-tier gate to answer first.
