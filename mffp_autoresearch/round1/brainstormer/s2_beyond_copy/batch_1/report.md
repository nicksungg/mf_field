# Brainstormer Report — Stream `s2_beyond_copy`, Batch 1

**Stream**: s2_beyond_copy
**Batch**: 1
**Total iterations**: 1
**Slot filled**: 1 / 1 (diagnostic, as pre-directed by program.md §12.2)
**Reopen candidates resolved**: 0 (none exist — first card of the round)

## Slot

- **Category**: `diagnostic / copy-LF excess-error forensics`
- **Card type**: `diagnostic` (no training; `epochs: 0`; single run, no seeds 1–2 — program.md §4.3)
- **Motivation**: program.md §12.2 pre-directs batch 1 to be the diagnostic that
  "localize[s] where and how models lose to copy-LF". The websearcher's verdict
  for that direction (D1) is **`preempted-but-MF-composition-open`**: every metric
  is published and must be adopted by citation, while the *reference* (error
  relative to the model's own LF input) and the *setting* (sharp-2D multi-fidelity
  phase-field) are open — arXiv:2604.20061 names the missing coarse-solution
  baseline as "a notable gap" in its own field. The design additionally answers
  the report's demand that the diagnostic **separate the three candidate
  mechanisms** (model ignores LF / spectral excess / interface-localized excess),
  and it gates D3 (band-split), which the verdict forbids proposing before D1
  reports because it is adjacent to the pre-falsified `mf_fno_spectral` lever (§5).
- **Concrete config**: new contract family `models_r1/s2_copylf_forensics/`
  (manifest.json + smoke_eval.py + INSPIRATION.md), run by `eval/score_panel.py`
  at `--epochs 0 --seed 0` over the five beyond-copy datasets. It trains nothing;
  it reloads the **batch-0 200-epoch checkpoints** at
  `round1/eval/results/<family>/ckpt_<ds>_e200_s{0,1,2}/last.pt` for
  `mf_fno_transfer_film` and `mf_fno_pinn_transfer` by calling each base family's
  own `run()` with its batch-0 `ckpt_dir` (resume path), capturing predictions via
  a monkeypatched module-level `finalize_and_write`, with three hard seam checks:
  (i) the module-level `_train`/`_train_pinn` are monkeypatched to raise — if
  resume did not take, the job aborts instead of silently training; (ii) the
  reproduced per-sample rel-L2 mean must equal the recorded batch-0 value to
  ≤1e-9; (iii) the recomputed copy-LF nRMSE must equal `eval/copylf_baselines.json`
  to ≤1e-9. Five measurements on the LF/model/HF triple:
  **M1 LF-blindness audit** (forward-hook records every tensor entering the model
  at eval ⇒ `lf_at_inference: bool` per family × dataset × seed);
  **M2 X-sufficiency ladder** (training-free predictors fit on the 400 HF train
  fields, scored on the 100 HF test fields through `eval/nrmse.py`: 1-NN-in-X as
  the scored `test_hf` split, k-NN k∈{3,5,10}, mean field, copy-LF, plus the two
  certified models' reloaded predictions — all as `ref_*` splits — and the
  train-split degeneracy statistic NN-in-X vs random-pair vs mean-field);
  **M3 spectral banding** (4 dyadic radial bands: band error share, ratio
  `R_b = ||e_b(model)||²/||e_b(copy-LF)||²`, transfer `H_b`, LF/HF coherence);
  **M4 interface stratification** (distance transform from `|u| < 0.1·max|u|`,
  4 strata, error-mass share model vs copy-LF);
  **M5 amplitude/pattern split** (per-sample optimal scalar rescale) **+ pairing
  control** (aligned vs index-shuffled LF↔HF residual — the §12.2 data-defect
  branch). Sidecar `diagnostics_<dataset>.json` per dataset carries M1–M5 and
  `nrmse_def_hash`. `ifc_poisson` is excluded (test split ships no LF; reference
  is the paper bar — ADR 0002).
- **Recipe**:
```json
{
  "base_family": "mf_fno_transfer_film",
  "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
  "family_dir": "models_r1/s2_copylf_forensics",
  "datasets": "ext__helmholtz_2d,sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard",
  "epochs": 0,
  "seeds": [0],
  "env": {
    "S2B1_BASE_FAMILIES": "mf_fno_transfer_film,mf_fno_pinn_transfer",
    "S2B1_CKPT_ROOT": "mffp_autoresearch/round1/eval/results",
    "S2B1_CKPT_EPOCHS": "200",
    "S2B1_CKPT_SEEDS": "0,1,2",
    "S2B1_KNN_K": "1,3,5,10",
    "S2B1_BANDS": "4",
    "S2B1_INTERFACE_TAU": "0.1",
    "S2B1_DIAG_OUT": "mffp_autoresearch_outputs/round1/s2_beyond_copy/B1/eval"
  }
}
```
  (`base_commit` = `round1-substrate` HEAD. Env paths are repo-root-relative and
  resolved against the root derived from `--dataset_dir` — `dataset_dir.parents[3]`
  — so the worktree, which has no `data/` symlinks, never needs them. Contract-tier
  plumbing check: the same command on `ext__helmholtz_2d` only. Walltime: no
  inference-only analog in `state/timing_ledger.json`; estimated 30–60 min for all
  five datasets, so the rules' default `04:00:00` with headroom.)
- **Expected outcome**: nothing moves — a diagnostic measures. Predicted, and
  calibrated against hand-probes recorded in `iteration_1.md` (train-split,
  leave-one-out, no models; explicitly **not reportable** under §2.1):
  **M1** `lf_at_inference = false` for both certified families on all 5 datasets ×
  3 seeds — the champions are structurally LF-blind at inference, so "the model
  destroys the LF information it was handed" is a category error: it was never
  handed the LF field at test time.
  **M2 (headline, scored)** 1-NN-in-X skill ≈ 5.4 fisher_kpp (certified 4.18),
  ≈ 18 allen_cahn (16.33), **≈ 0.42 pfc** (certified 11.51 — a training-free
  lookup beating copy-LF, i.e. skill < 1 on one beyond-copy dataset), ≈ 14
  cahn_hilliard (5.53), ≈ 1.7 helmholtz (13.82). Reading: on fisher_kpp and
  allen_cahn the certified models sit within ~1 skill unit of a trivial X-only
  lookup, so the X-only regime is information-bounded far from copy-LF; on pfc the
  information *is* in X and the model is 27× worse than lookup, so that dataset is
  a representation/optimization failure, not an information failure.
  **M3** `R_low > 1` on ≥4 of 5 datasets (excess over copy-LF present even in the
  lowest band ⇒ not a high-k blur).
  **M4** error-mass share ≈ stratum-area share on the information-limited
  datasets (§12.2's "concentrated in X" framing falsified on the spatial axis
  there), interface-concentrated on pfc.
  **M5** helmholtz optimal-rescale nRMSE ≪ raw ⇒ amplitude/normalization
  divergence; aligned≪cross-pair residual ⇒ pairing sound, no dataset bug of that
  kind. Versus the noise floor: the claims carried are ≥1.0 (fisher_kpp, floor
  0.4177), ≥2.0 (allen_cahn, floor 1.6334) and ≥5.0 (pfc, floor 1.1511) skill
  units; helmholtz (floor 9.6950) carries no numeric claim.
- **Expected falsification**: H1 ("the copy-LF gap is a conditioning-sufficiency
  dichotomy, not one localized model defect") is falsified if
  `|skill(best training-free X-only predictor) − skill(certified best family)| > 2.0`
  skill units on `sharp__allen_cahn_2d` (floor 1.6334) or `> 1.0` on
  `sharp__fisher_kpp_2d` (floor 0.4177), or if the pfc excess
  `skill(certified 11.511) − skill(1-NN-in-X) < 5.0` skill units (floor 1.1511),
  or if the low-band ratio `R_low ≤ 1.0` on ≥3 of the four low-floor datasets
  across all three batch-0 seeds — the last outcome relocating the failure to
  high-k spectral localization and licensing the band-split (D3) direction for
  batch 2.
- **Prior-art verdict quoted** (verbatim, `websearches/s2_beyond_copy/batch_1/report.md`,
  D1 row): verdict **`preempted-but-MF-composition-open`**; citations
  `https://arxiv.org/html/2604.20061v1` (band-energy error, frequency-response
  lens, no-new-model diagnostic); `https://arxiv.org/html/2606.03936` (`rFFT`
  bands, `H(k)`, coherence check); `https://arxiv.org/pdf/2605.26412` (per-scale
  coherence, represented vs reference field); `https://arxiv.org/pdf/2510.17887`
  (shock-window / gradient-weighted / shock-location errors);
  `https://christophm.github.io/interpretable-ml-book/feature-importance.html`
  (permutation attribution); plus `https://arxiv.org/html/2605.07375` (QuadNorm,
  motivating M5a). What remains open (verbatim, D1 "what remains open" cell):

  > (1) **The reference**: no fetched source decomposes error *relative to the
  > model's own LF input*; 2604.20061 names the missing coarse-solution baseline
  > as "a notable gap" in its own field. (2) **The setting**: 2604.20061's example
  > is KS (the smooth control); 2510.17887 is single-fidelity shock flow — neither
  > is sharp-2D **multi-fidelity** phase-field. (3) **The joint decomposition**: no
  > source combines spectral banding + interface stratification + LF-input
  > attribution on one LF/model/HF triple.

  The strongest
  quotable gap, verbatim: *"does not systematically compare neural surrogates
  against coarse/low-fidelity solutions as a direct baseline. This is a notable
  gap; comparisons focus on training error, rollout divergence, and idealized
  reduced-order models rather than demonstrating whether surrogates outperform the
  coarse approximation they learn from."*
- **Immutables self-check**: **pass (10/10)** — all ten items answered with
  positive evidence in [iteration_1.md](iteration_1.md) §"Immutables self-check";
  nearest pre-falsified lever named (LF low-mode freezing, `mf_fno_spectral`) with
  the difference stated (this card builds and freezes nothing; it measures whether
  the LF low band is accurate, which the websearch verdict makes the precondition
  for ever proposing D3).
- **Anchor reference**: `null` (gap stream — own-stream anchor `copylf_bar` skill
  1.0 is implicit, program.md §4.5).
- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _none — `experiment_cards/` holds only `SCHEMA.md`; this is the round's first card_ | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| 1 | `diagnostic / copy-LF excess-error forensics` | Training-free forensics on the LF/model/HF triple for the five beyond-copy datasets: forward-hook LF-blindness audit of the two certified batch-0 champions, an X-only sufficiency ladder (1-NN-in-X scored through `score_panel`), spectral band ratios vs copy-LF, interface stratification, and amplitude/pairing controls — designed to split "the condition vector does not determine the realization" from "the model loses high-k structure", and to gate the band-split direction for batch 2. | filled |

## Notes for the starter / builder / analyzer

1. The scored `test_hf` split of this family is the **training-free 1-NN-in-X
   predictor**, not a learned model. If it returns skill < 1 on
   `sharp__phase_field_crystal_2d` (predicted ≈ 0.42), that is a real
   beats-copy-LF datapoint but a **lookup table, not a model** — part 5 must say
   so, and it does not by itself satisfy success criterion 2 in spirit.
2. The batch-0 checkpoints under `round1/eval/results/*/ckpt_*_e200_s*/last.pt`
   are load-bearing inputs. The builder should record each `last.pt` sha256 and
   mtime in `build_notes`; the family must hard-stop (never retrain) if any is
   missing or its `epochs_target`/`grid` mismatches.
3. Batch-2 successors, in the order the diagnostic's outcome selects them:
   **D2 (identity-to-LF fusion)** — bind an identity path to the LF field so the
   model is structurally never worse than copy-LF (Fixup zero-init residual,
   arXiv:1901.09321, is the *mechanism* and is preempted; only the MF binding and
   a gate conditioned on what this diagnostic measures may be claimed as novel);
   and/or **an LF-consuming family at test time** (`transolver_residual`, which
   §12.4 records as best-in-zoo on 4 of the 5 beyond-copy datasets and which does
   ingest LF tokens at inference — the natural control for M1). **D3 (band-split)
   only if `R_low ≤ 1`.**
4. If M2's degeneracy statistic confirms that the condition vector omits the
   initial condition on `sharp__{fisher_kpp_2d,allen_cahn_2d,phase_field_crystal_2d}`
   — the repo already contains the precedent fix in
   `data/sharp__cahn_hilliard/meta.json` ("IC-encoded cond (low Fourier modes) so
   field=f(x) is learnable; fixes rel-L2>1 bug") — part 7 should carry a written
   recommendation to the mentor (program.md §13.4). It is a recommendation, never
   an action: data is immutable (§5.1).
