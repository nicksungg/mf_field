# Iteration 1 — `s1_poisson` batch 1 slot design

## Design context considered

- `summary_so_far.md` §6 (unknowns), in particular the verified finding that
  `ifc_poisson`'s fidelity levels are **not sample-aligned** and that the
  batch-1 seed-direction family (`akash/models/mf_fno_allpairs`) pairs
  source-fidelity conditions with target-fidelity fields.
- Prior-art verdict D1: `preempted-but-MF-composition-open`; open only as
  "all *ordered* pairs (not just adjacent) through a *single shared* network,
  at N_hf = 5 on this nested 100/50/20/5 ladder"
  (`websearches/s1_poisson/batch_1/report.md`).
- program.md §12.1 verbatim (quoted in `summary_so_far.md` §2): N_hf = 5;
  "Prefer designs that reduce variance … or add information … over designs that
  add capacity"; batch-1 seed direction = all-pairs on the ifc ladder; L = 4 so
  the family's known O(L²) failure cannot fire.
- Anchor `state/anchors/s1_poisson.json`: 1.5656 [1.4562, 1.6961], family
  `mf_fno_transfer_film`, per-seed nRMSE [0.05561, 0.05242, 0.06106].
- Noise floor `state/noise_floor.json::ifc_poisson.min_claimable_effect`
  = **0.2399 skill units** = 0.2399 × 0.036 = **0.00864 nRMSE**.
- §5 immutables block (reproduced in the self-check below) and the three
  pre-falsified levers (WNO backbone swap; LF low-mode freezing; diffusion
  prior).
- Timing: `state/timing_ledger.json` — `ifc_poisson` @200 epochs = 0.78–0.98 min
  per (family, seed) on p100.

## Proposal reasoning

**Step 1 — the seed direction cannot be run as-is.** §12.1 says to apply
`mf_fno_allpairs` to this gap. I read the family
(`mf_field/akash/models/mf_fno_allpairs/smoke_eval.py`) and the dataset. Its
`build_pairs` takes `Xsrc = cond_by_fid[s][:n]` and `Ytgt = field_by_fid[t][:n]`
with `n = min(N_s, N_t)`, and its finetune stage takes `X_lf = cond_by_fid[lf]`
against HF fields. Both are correct only if the fidelity sample lists are index
aligned. On `ifc_poisson` they are not (verified: `np.allclose(X8[:5], X64)` →
False, max |diff| 0.581; same for every other pair). So all 6 cross-pair row
blocks *and* the finetune stage would train on mismatched (parameters, field)
correspondences. The akash bench number 0.4657 on `ifc_poisson` (vs 0.0488 for
`mf_fno_transfer_film`) and 0.1457 on `ifc_heat` — the two non-aligned datasets,
while the family wins the aligned npz datasets — is exactly what that defect
predicts. Re-running it unchanged would burn a batch to reproduce a known
catastrophe.

**Step 2 — what the corrected construction is.** The backbone
(`akash/common/backbone.py::FNO2d`) maps a condition vector to a field; there is
no LF-field input channel. So a "pair" (s,t) is a *conditioning label*, and the
only correct supervised row for target fidelity t is `(X^{(t)}_i, f_s, f_t) →
Y^{(t)}_i`, i.e. the condition vector must come from the **target** fidelity's
own sample list. On an aligned dataset `X^{(s)}[:n] == X^{(t)}[:n]`, so this
change is a **no-op on every dataset the family previously won** and a fix on
the ifc ladder. Taking target-own conditions alone would, however, drop the 100
level-8 samples entirely (no pair has t = 8), so the corrected family must also
carry the **self pairs** (f,f) — which is what actually pools the ladder's
100+50+20+5 = 175 rows.

**Step 3 — choose the variable.** The websearcher's directive is explicit:
"Design the pair set as the actual variable." I make the arm knob
`MFFP_LADDER_MODE` and define four arms that share code, seeds, hyperparameters,
grid, and the identical HF-finetune stage:

| arm | levels used | fidelity tags instantiated | rows | role |
|---|---|---|---|---|
| `two_level` | {8, 64} | self(8,8),(64,64) + cross (8,64) | 110 | information-content control ≈ what the champion sees |
| `adjacent` | all 4 | self ×4 + (8,16),(16,32),(32,64) | 250 | the published cascade structure |
| `allpairs` | all 4 | self ×4 + all 6 ordered (s<t) | 280 | **primary**: the open composition |
| `legacy_pairing` | all 4 | same rows as `allpairs`, but cross rows use source-indexed conditions `X^{(s)}[:n]` | 280 | isolates the correspondence defect |

Row counts for a cross pair (s,t) are `n = min(N_s, N_t) = N_t`:
(8,16)=50, (8,32)=20, (8,64)=5, (16,32)=20, (16,64)=5, (32,64)=5 → 105 cross
rows; self rows 100+50+20+5 = 175.

The three contrasts this buys, all internally controlled and all on the same
seeds:
- `allpairs` vs `two_level` → **does the ladder's intermediate information
  (16², 32²) close any of the gap?** This is the stream's own question.
- `allpairs` vs `adjacent` → do non-adjacent pairs carry information beyond the
  published adjacent cascade? (the websearcher's only-open claim)
- `allpairs` vs `legacy_pairing` → how much of the akash catastrophe is the
  cross-fidelity correspondence defect, measured in-round through this round's
  eval layer rather than inferred from a 2500-epoch external CSV.

**Alternatives weighed and rejected.**
1. *Run `mf_fno_allpairs` verbatim on the panel* (the literal §12.1 seed
   direction). Rejected: guaranteed ≈0.47 nRMSE on `ifc_poisson` for a reason I
   can already name; it would produce a skipped/cratered card and no
   understanding. The `legacy_pairing` arm preserves that measurement for ~3
   GPU-minutes instead of a whole batch.
2. *D2, telescoping / MLMC-NO or MFRNP-style residual aggregation.* Rejected on
   the websearcher's explicit instruction — "preempted (cite)", demonstrated on
   **FNO + Poisson** (arXiv 2505.12940) and MFRNP's Poisson 0.0076 is one of this
   repo's own bars; also its hierarchy construction is unresolved and repo law
   forbids downsampled LF.
3. *D3, ensembling as the mechanism.* Rejected: preempted, and it consumes the
   seed axis that §4.4 reserves for the CI.
4. *Physics residual (PINN-style Poisson residual) on the ifc ladder.* Attractive
   under §12.1 "add information", and `mf_fno_pinn_transfer` already exists — but
   `ifc_poisson` does **not** ship the source term decode (noted in §12.3 for
   the sibling stream), so the residual Δu − f is not computable; a Laplacian-only
   smoothness prior would be a capacity/regularization knob, not information.
   Deferred; batch 2 candidate only if the source decode can be recovered from
   the 5-dim condition vector.
5. *Raising `modes_cap` 12→32.* Spectrally the most obvious lever here, and
   explicitly assigned to `s5_tuning`-B1 by §12.5. Out of scope by construction.
6. *Adding capacity (wider/deeper FNO).* §12.1 explicitly deprioritizes it.

**Step 4 — traps the builder must not fall into** (recorded here so they enter
the card description):
- `score_panel.py::_run_one` derives `out_json` and `ckpt_dir` from
  `(family_dir.name, dataset, epochs, seed)` **only** — the arm is invisible to
  those paths. The base family's resume logic reloads `last.pt` whenever
  `(epochs_target, grid)` match, so a second arm would silently load the first
  arm's weights and skip training. The port MUST include the arm mode in the
  checkpoint key, and the job script MUST export a per-arm
  `ROUND1_EVAL_RESULTS` so per-arm artifacts do not overwrite each other. The
  round's cache key is safe by itself (`code_hash` folds in the env dict), but
  the checkpoint is not.
- The family must be **vendored** into the worktree (backbone + SMOKE
  hyperparameters copied from `akash/common/`), not imported from `akash/**` via
  `parents[2]`: (a) `mf_field/akash/**` is a guarded read-only surface, (b)
  `code_hash` hashes the family dir, `factory_root/models/_common`, and the eval
  files — code imported from akash would be invisible to the cache key.
  `load_mf_dataset` / `resolve_grid` / `finalize_and_write` stay imported from
  the guarded `factory_root/data_adapters` exactly as every certified family does.
- The cratered rule (§4.4) must be evaluated on the **primary** arm
  (`allpairs`); `legacy_pairing` is expected to be cratered by design and must
  not gate seeds 1–2.

## Proposal

- **Category**: `mf_composition / ladder-data-fusion` (gap stream).
- **Card type**: `model`.
- **Motivation**: The batch-1 seed direction (§12.1: "all-pairs fidelity
  training … `mf_field/akash/models/mf_fno_allpairs`") is scored by the
  websearcher as **"preempted-but-MF-composition-open"**, with only this open:
  "**Not found published**: (i) **all ordered pairs** (not just adjacent) as a
  data-amplification augmentation, (ii) with a **single shared** network rather
  than one net per level, (iii) at **N_hf = 5** on the `li2022ifc` Poisson
  ladder." Reading the family against the data shows it cannot be tested on this
  ladder as built: `ifc_poisson`'s four fidelity levels are not sample-aligned
  (`np.allclose(X8[:5], X64)` → False, max |diff| 0.581), so its cross-pair and
  finetune rows pair conditions with fields from different parameters — which
  explains its 0.4657 vs the champion's 0.0488 on this dataset
  (`akash/results/bench_full_metrics.csv`). The card fixes the correspondence
  and turns the pair set into the measured variable, per the websearcher's
  directive "Design the pair set as the actual variable."
- **Concrete config**: family `mf_fno_ladder` in the worktree, vendored from
  `akash/models/mf_fno_allpairs` (+ `akash/common/backbone.py` SMOKE
  hyperparameters: hidden 64, blocks 4, modes_cap 12, batch 16, lr_pretrain
  1e-3, lr_finetune 3e-4, wd 1e-5, clip 1.0 — identical to the anchor family).
  Rows `(cond=[X, f_src, f_tgt]) → Y@work_grid(64,64)`, `f = (log fid − log 8)/
  (log 64 − log 8)`. Stage 1: joint training on the arm's row set, 200 epochs,
  lr_pretrain. Stage 2 (identical in all arms): HF finetune on the 5 rows
  `(X^{(64)}, f_src=0, f_tgt=1) → Y^{(64)}`, 200 epochs, lr_finetune. Eval:
  query `(X_test, f_src=0, f_tgt=1)`. Four arms via `MFFP_LADDER_MODE ∈
  {two_level, adjacent, allpairs, legacy_pairing}` (table above); `allpairs` is
  primary. Checkpoint key extended with the arm mode; per-arm
  `ROUND1_EVAL_RESULTS`. The family also records, in the result JSON `extra`
  (score-neutral), the per-pair `max |X^{(s)}[:n] − X^{(t)}[:n]|` alignment
  measurement and the per-arm row counts.
- **Recipe**:
```json
{
  "base_family": "mf_fno_allpairs",
  "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
  "family_dir": "models_r1/mf_fno_ladder",
  "datasets": "ifc_poisson",
  "epochs": 200,
  "seeds": [0, 1, 2],
  "env": {
    "MFFP_LADDER_MODE": "allpairs",
    "_arms": ["two_level", "adjacent", "allpairs", "legacy_pairing"],
    "_primary_arm": "allpairs",
    "_sweep": "one SLURM job per seed runs 4 score_panel.py calls, each with --env MFFP_LADDER_MODE=<arm> and its own --out result_ifc_poisson_<arm>_s<seed>.json; export ROUND1_EVAL_RESULTS=<outputs>/eval/results_<arm> per arm so per-arm result JSONs and ckpt dirs cannot collide",
    "_source": "vendored from mf_field/akash/models/mf_fno_allpairs (model.py sha256 984d4e5e…, smoke_eval.py sha256 611729bc…) + mf_field/akash/common/backbone.py (sha256 f56fa802…) at commit 967562e2; akash itself is never edited"
  }
}
```
- **Expected outcome**: Primary metric = `ifc_poisson` test nRMSE → skill vs the
  paper bar 0.036 (ADR 0002), mean over seeds {0,1,2}. Anchor 1.5656
  [1.4562, 1.6961] (nRMSE ≈ 0.0564). Prediction: `allpairs` ≈ **skill 1.15–1.40
  (nRMSE 0.041–0.050)**, point estimate ≈ 1.28 (0.046) — an improvement of
  ≈0.29 skill units, i.e. just above the 0.2399 floor; mechanism: the 32²
  level's 20 samples are the only supervision besides the 5 HF samples that
  covers spectral modes 4–12 (an 8² field lifted to 64² carries content only to
  mode ≈4, and the FNO represents 12 modes), and the 16² level adds 50 more.
  `adjacent` predicted within the floor of `allpairs` (the ladder's value is
  mostly in adjacent steps); `two_level` predicted ≈ the anchor (1.4–1.7);
  `legacy_pairing` predicted **≥ 3.0 skill (nRMSE ≥ 0.108)**, far outside the
  floor, corroborating the akash 0.4657. I state plainly that the anchor
  comparison is marginal against the floor by design at this tier; the robust
  part of the card is the set of internal contrasts, which share code, seeds and
  hyperparameters.
- **Expected falsification**: Falsified if the full-ladder all-ordered-pairs arm
  fails to beat the two-level arm on `ifc_poisson` by more than the certified
  noise floor — mean skill over seeds {0,1,2} improving by ≤ 0.240 skill units
  (≤ 0.00864 nRMSE) — which would mean the intermediate fidelities (16², 32²)
  carry no usable information for HF reconstruction at N_hf = 5 beyond what the
  8²→64² transfer already exploits.
- **Anchor reference**: `null` — `s1_poisson` is a gap stream, so per §4.5 the
  own-stream anchor (`state/anchors/s1_poisson.json`, 1.5656) is implicit.

## Immutables self-check (10 items, positive evidence)

1. **Data read-only** — the family reads only
   `factory_root/data/ifc_poisson/{train,test}` through the guarded
   `data_adapters.load_mf_dataset`, opens nothing for writing under `data/`, and
   uses HF supervision solely from `train/fidelity_64` (5 samples, unchanged
   N_hf); the 8²/16²/32² levels are the dataset's own coarse solves loaded as
   shipped and only ever **up**-sampled to the 64² working grid by
   `_to_grid` (bilinear) — no HF field is ever downsampled to synthesize an LF
   one, and no file is regenerated.
2. **Panel + guard fixed** — the card scores exactly one existing panel member,
   `ifc_poisson`, via `--datasets ifc_poisson`; it adds no dataset, removes
   none, and makes no panel-geomean claim, so the §2.3 guard-set run
   (required only "for any experiment claiming a panel win") is not triggered.
3. **Eval layer untouched** — every number comes from unmodified
   `round1/eval/score_panel.py`; the arm knob is an environment variable read
   inside the worktree family's own code, so the card requires zero edits to
   `round1/eval/`, `project.yaml`, `program.md`, ADRs or subagent prompts.
4. **One nRMSE definition** — the family calls the guarded
   `data_adapters.metrics.finalize_and_write` (as the certified batch-0 families
   do) and `score_panel._extract_test_metric` selects the per-sample test
   metric; the training objective stays `F.mse_loss` in scaled space, which §5
   explicitly permits ("training loss is free") and which is never reported.
5. **Contract CLI fixed** — `smoke_eval.py` keeps the six-argument signature
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed` inherited
   verbatim from the base family (its `main()` at lines 221–234); the single
   knob `MFFP_LADDER_MODE` is declared in `recipe.env` and therefore enters
   `score_panel.code_hash` (which folds `for k, v in sorted(env.items())` into
   the sha).
6. **Seeds / tier epochs fixed** — `seeds: [0,1,2]` and `epochs: 200` (smoke
   tier) for all four arms, with the builder's plumbing check at contract tier
   2; no full-tier (2500) run is requested anywhere in the card.
7. **Guarded factory surfaces untouched** — all new code lives at
   `<worktree>/models_r1/mf_fno_ladder/`; `mf_field/akash/**` and
   `factory_root/{eval,baselines,references,scripts,data}` are only *read*
   (copied from), and the recipe records the source blob sha256s so a reviewer
   can verify the originals are byte-identical afterwards.
8. **Checkpoint resume** — the base family already writes
   `torch.save({"epochs_target", "grid", "model"}, ckpt_dir/"last.pt")` and
   reloads it when the key matches (lines 161–183); the port keeps that path and
   extends the key with `MFFP_LADDER_MODE`, which both preserves preemption
   resume and closes the cross-arm contamination trap noted in Step 4.
9. **Threshold vs noise floor** — `state/noise_floor.json::ifc_poisson`
   `min_claimable_effect = 0.2399` skill units (per-seed skills 1.5447 /
   1.4562 / 1.6961, spread 0.2399; per-seed nRMSE 0.05561 / 0.05242 / 0.06106).
   The falsification threshold is a **0.240 skill-unit** improvement
   (= 0.240 × 0.036 = 0.00864 nRMSE), i.e. strictly at/above the floor, and the
   secondary `legacy_pairing` prediction (≥ 3.0 skill, ≥ 1.43 above the anchor)
   clears it by ~6×. `ifc_poisson` is the only dataset the card cites, and its
   floor is quoted.
10. **Not a pre-falsified lever** — the three §5 levers are the WNO backbone
    swap (`wno_transfer_film`), LF low-mode freezing (`mf_fno_spectral`) and the
    diffusion prior (`mf_fno_diffprior`); this card uses none of them: the
    backbone is the anchor family's own FiLM-FNO, no spectral band is frozen,
    and no generative prior is involved. Nearest in-repo negative is
    `mf_fno_allpairs`' own 0.4657 on `ifc_poisson`, which is **not** a §5
    pre-falsified lever; the card cites it, diagnoses it as a cross-fidelity
    correspondence defect, and differs by taking target-fidelity conditions,
    adding self pairs, and re-running the legacy construction as a measured
    control arm.

## Status

- Slot covered (one proposal, `card_type: model`, complete recipe).
- Not skipped.
- Reopen candidates resolved: none exist for this stream (no prior cards).
- Immutables self-check: **pass** (10/10, no revision needed → no iteration_2).
