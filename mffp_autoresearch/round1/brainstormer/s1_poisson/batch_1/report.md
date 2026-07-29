# Brainstormer Report — Stream `s1_poisson`, Batch 1

**Stream**: s1_poisson · **Batch**: 1 · **Total iterations**: 1 ·
**Slot filled**: yes (1/1) · **Reopen candidates resolved**: 0 (none exist)

## Slot

- **Category**: `mf_composition / ladder-data-fusion` (gap stream)
- **Card type**: `model`
- **Motivation**: The batch-1 seed direction (§12.1: "all-pairs fidelity
  training … `mf_field/akash/models/mf_fno_allpairs`") is scored by the
  websearcher as **`preempted-but-MF-composition-open`**, open only as
  "**Not found published**: (i) **all ordered pairs** (not just adjacent) as a
  data-amplification augmentation, (ii) with a **single shared** network rather
  than one net per level, (iii) at **N_hf = 5** on the `li2022ifc` Poisson
  ladder." Reading that family against the data shows it *cannot be tested on
  this ladder as built*: `ifc_poisson`'s four fidelity levels are **not
  sample-aligned** (verified: `np.allclose(X8[:5], X64)` → `False`, max |diff|
  0.581; same for every other pair), while `build_pairs` pairs
  `cond_by_fid[s][:n]` with `field_by_fid[t][:n]` and the finetune stage pairs
  LF conditions with HF fields. Every cross-fidelity row and the whole finetune
  stage therefore associate parameters with fields from *different* samples —
  which is exactly what its 0.4657 nRMSE on `ifc_poisson` (vs the champion's
  0.0488) and 0.1457 on `ifc_heat` in `akash/results/bench_full_metrics.csv`
  predict, on precisely the two non-aligned datasets, while it wins the aligned
  npz datasets. This card fixes the correspondence and makes the pair set the
  measured variable, following the websearcher's directive "**Design the pair
  set as the actual variable.**"
- **Concrete config**: family `mf_fno_ladder` in the worktree, vendored from
  `akash/models/mf_fno_allpairs` + `akash/common/backbone.py` (SMOKE
  hyperparameters identical to the anchor family: hidden 64, blocks 4,
  modes_cap 12, batch 16, lr_pretrain 1e-3, lr_finetune 3e-4, wd 1e-5, clip
  1.0). Rows `(cond = [X, f_src, f_tgt]) → Y@(64,64)`, with
  `f = (log fid − log 8)/(log 64 − log 8)`. **Correction**: cross-pair rows take
  the condition vector from the **target** fidelity's own sample list (a no-op
  on aligned datasets, a fix on the ifc ladder), and **self pairs (f,f) are
  included** so the 100/50/20/5 ladder rows all enter training. Stage 1: joint
  training on the arm's row set, 200 epochs. Stage 2 (identical in every arm):
  HF finetune on the 5 rows `(X^{(64)}, f_src=0, f_tgt=1) → Y^{(64)}`, 200
  epochs. Eval query `(X_test, f_src=0, f_tgt=1)`.
  Four arms via `MFFP_LADDER_MODE`:

  | arm | levels | tags | rows | role |
  |---|---|---|---|---|
  | `two_level` | {8,64} | self ×2 + (8,64) | 110 | information-content control ≈ the champion |
  | `adjacent` | all 4 | self ×4 + (8,16),(16,32),(32,64) | 250 | published cascade structure |
  | `allpairs` | all 4 | self ×4 + all 6 ordered (s<t) | 280 | **primary** — the open composition |
  | `legacy_pairing` | all 4 | same rows, cross rows source-indexed | 280 | isolates the correspondence defect |

  Two build traps recorded for the builder/reviewer: (1) `score_panel._run_one`
  derives `out_json`/`ckpt_dir` from `(family_dir.name, dataset, epochs, seed)`
  only — the arm is invisible, and the base resume logic would silently reload
  another arm's `last.pt`; the checkpoint key **must** include the arm and the
  job script **must** export a per-arm `ROUND1_EVAL_RESULTS`. (2) The family
  must be *vendored*, not imported from `akash/**` via `parents[2]`, both
  because akash is a guarded read-only surface and because `code_hash` would not
  see the imported code. The result JSON `extra` also records (score-neutrally)
  the per-pair `max |X^{(s)}[:n] − X^{(t)}[:n]|` alignment measurement and the
  per-arm row counts.
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
- **Expected outcome**: metric = `ifc_poisson` test nRMSE → skill vs paper bar
  0.036 (ADR 0002), mean over seeds {0,1,2}. Anchor = **1.5656 [1.4562,
  1.6961]** (nRMSE ≈ 0.0564). Predictions: `allpairs` **skill 1.15–1.40 (nRMSE
  0.041–0.050)**, point estimate ≈1.28 → Δ ≈ **−0.29 skill vs anchor**, just
  above the **0.2399** floor; `adjacent` within the floor of `allpairs`;
  `two_level` ≈ anchor (1.4–1.7); `legacy_pairing` **≥ 3.0 skill (nRMSE
  ≥ 0.108)**, ≈6× the floor away from the anchor. Mechanism: the 32² level's 20
  samples are the only supervision besides the 5 HF samples covering spectral
  modes 4–12 (an 8² field lifted to 64² carries content only to mode ≈4; the FNO
  represents 12), and the 16² level adds 50 more rows. Stated plainly: the
  anchor comparison is *marginal* against the floor at this tier; the robust
  part of the card is the three internal contrasts (same code, same seeds, same
  hyperparameters). Wall-clock: batch 0 ran `ifc_poisson` @200 epochs in
  0.78–0.98 min, so 4 arms ≈ 15 min/seed → `--time=01:00:00` is ample.
- **Expected falsification**: Falsified if the full-ladder all-ordered-pairs arm
  fails to beat the two-level arm on `ifc_poisson` by more than the certified
  noise floor — mean skill over seeds {0,1,2} improving by ≤ 0.240 skill units
  (≤ 0.00864 nRMSE) — which would mean the intermediate fidelities (16², 32²)
  carry no usable information for HF reconstruction at N_hf = 5 beyond what the
  8²→64² transfer already exploits.
- **Prior-art verdict quoted** (verbatim from
  `websearches/s1_poisson/batch_1/report.md`):
  > **D1.** All-ordered-pairs fidelity training — ONE FiLM-FNO over every
  > (f_src<f_tgt) pair of the nested 100/50/20/5 ladder, queried (LF→HF) at eval
  > (`akash/models/mf_fno_allpairs`) | **preempted-but-MF-composition-open** |
  > fidelity-as-input: https://www.emergentmind.com/topics/multi-fidelity-gaussian-process-surrogate-modeling
  > (snippet); continuous-fidelity conditioning: https://arxiv.org/abs/2207.00678
  > (fetched); adjacent-pair nested cascade: https://arxiv.org/html/2605.16118v1
  > (fetched); joint all-levels training: https://arxiv.org/html/2402.02031v1
  > (snippet); progressive ladder at tiny HF: https://arxiv.org/pdf/2510.13762
  > (fetched); all2all = **time** pairs only: https://nips.cc/virtual/2024/poster/95731
  > (snippet) | Conditioning on fidelity, joint multi-level training, and
  > adjacent-level cascades are all published. **Not found published**: (i)
  > **all ordered pairs** (not just adjacent) as a data-amplification
  > augmentation, (ii) with a **single shared** network rather than one net per
  > level, (iii) at **N_hf = 5** on the `li2022ifc` Poisson ladder. Two
  > independent searches (turn 3, turn 4) returned explicit negatives on (i)+(ii).

  Card `prior_art.verdict` should be recorded as **`preempted-pivoted`**
  (the schema's nearest enum value to the websearcher's
  `preempted-but-MF-composition-open`), with the citation list above.
- **Immutables self-check**: **pass (10/10)** — positive evidence per item in
  [iteration_1.md](iteration_1.md) §"Immutables self-check". Key numbers:
  floor `ifc_poisson.min_claimable_effect = 0.2399` skill units (= 0.00864
  nRMSE), falsification threshold set at exactly that floor; nearest
  pre-falsified lever = none of the three in §5 (nearest in-repo negative is
  `mf_fno_allpairs`' own 0.4657, which this card diagnoses and controls for).
- **Anchor reference**: `null` (gap stream — own-stream anchor
  `state/anchors/s1_poisson.json` = 1.5656 is implicit, per §4.5)
- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| (none — no prior cards exist in this stream; `experiment_cards/` holds only `SCHEMA.md`) | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| 1 | `mf_composition / ladder-data-fusion` | Fix the cross-fidelity sample correspondence in the all-pairs FiLM-FNO and measure the pair set as the variable (two_level / adjacent / allpairs / legacy_pairing) on `ifc_poisson` at N_hf = 5 | filled (`model`) |

### Notes for later batches (not part of this card)

- The same correspondence fix should be worth checking on `ifc_heat` (the other
  non-aligned `ifc_raw` dataset, akash 0.1457 vs champion 0.0089); it is in
  neither the panel nor the guard set, so it is a batch-2 generality question,
  not a batch-1 scope item.
- On `ifc_poisson` no model can consume an LF *field* at test time (the test
  split ships only `fidelity_64`), so "multi-fidelity" here can only mean
  training-data fusion. Any batch-2 design that assumes an LF input channel is
  dead on arrival for this stream.
- A physics-residual card (§12.1 "add information") is blocked until the Poisson
  source term can be decoded from the 5-dim condition vector; the dataset does
  not ship it.
