# Iteration 1 — `s4_hybrid_routing`, Batch 1

## Design context considered

- `summary_so_far.md` §6 unknowns, especially **U1** (the certified champion
  `mf_fno_transfer_film` never consumes the LF field at test time — its model is
  `FNO2d(cond_dim, ...)` and LF enters only as pretraining targets, verified in
  `mf_field/factory_mffp/models/mf_fno_transfer_film/smoke_eval.py` lines
  106–170), **U2** (does the +30.6% oracle survive on sharp 2-D?), **U3** (nobody
  has the per-dataset gate values a router would need).
- Prior-art verdict (`websearches/s4_hybrid_routing/batch_1/report.md`), D1 row:
  `preempted-but-MF-composition-open`, with the instruction that D1 must claim
  zero novelty and stand as a measurement.
- program.md §12.4 verbatim (quoted in `summary_so_far.md` §2): *"batch 1 should
  start by scoring it on the panel (cheap, mostly evaluation)"*; *"The surviving
  novelty is the MF composition"*; *"whatever routing is learned should preserve
  [`transolver_residual`'s] behavior"*.
- Anchor `state/anchors/s4_hybrid_routing.json`: panel geomean skill **6.703**
  [6.219, 7.102], `provisional: false`, family `mf_fno_transfer_film`, smoke tier.
- `state/noise_floor.json` `min_claimable_effect`: helmholtz 9.695, pfc 1.151,
  allen_cahn 1.633, fisher_kpp 0.418, cahn_hilliard 0.553, ifc_poisson 0.240.
- program.md §5 immutables + the three pre-falsified levers.
- Read-throughs of the candidate artifact
  `mf_field/akash/models/fno_transolver_seq/{manifest.json,model.py,smoke_eval.py}`
  (850 lines) and its dependency `mf_field/akash/common/mffp.py` (a thin
  sys.path shim onto the factory `data_adapters` + the shared `SMOKE` dict).
- Batch-0 timings `state/timing_ledger.json` (44.4 min/seed on each 256² sharp
  dataset for the champion).

## Feasibility checks actually run (not assumed)

1. **Contract-tier run of the artifact, `ifc_poisson`, CPU, `--epochs 2`**
   (command: `python mf_field/akash/models/fno_transolver_seq/smoke_eval.py
   --dataset_dir mf_field/factory_mffp/data/ifc_poisson --dataset_name
   ifc_poisson --epochs 2 --out <scratch>/ifc.json --ckpt_dir <scratch>/c
   --seed 0`). It completed in < 10 min and printed:
   `[data] ... loader=ifc_raw LF=8 HF=64 ctx_fid=32 ctx_source=fno_base
   work_grid=(64,64) N_lf=100 N_hf=5 N_test=128 cond_dim=5`;
   `[stage 2b] alpha_ls=1.5000 alpha=1.5000 val_rel_base=0.915385
   val_rel_hybrid=0.900957`; `[done] ifc_poisson: rel_l2=0.438569
   base_only=0.490003 (final-fno 0.445722) alpha=1.5001 stage3=True
   ctx=fno_base`. So: the family runs, the gate turns on, and even a 2-epoch
   corrector beat its own base by 10.5% — on the *weaker* context path
   (ifc_poisson's test split ships HF only, so the context is the base
   prediction, not a real LF field).
2. **A CPU contract-tier run on `sharp__phase_field_crystal_2d` was launched
   and did NOT complete** — it was killed by my own 900 s wrapper timeout
   (exit 143, SIGTERM) with no output flushed, i.e. the 128² dataset's
   LF-pretrain + 4 out-of-fold folds + corrector exceed 15 min on CPU. This is a
   statement about CPU speed only; it is not evidence about GPU feasibility, and
   the builder's contract-tier gate on a p100 must answer that (especially the
   256² memory question).
3. **Recipe identity check**: `mf_field/akash/common/mffp.py` line 48 and
   `factory_mffp/models/mf_fno_transfer_film/smoke_eval.py` line 48 carry the
   identical `SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12,
   batch_size=16, lr_pretrain=1e-3, lr_finetune=3e-4, weight_decay=1e-5,
   grad_clip=1.0)` and `WORK_CAP = 256` — so the hybrid's stage-1 base *is* the
   certified champion's recipe, giving a within-run paired control.
4. **Contract plumbing**: `round1/eval/score_panel.py::_run_one` passes exactly
   the six contract args and merges `--env KEY=VAL` into the child environment
   (lines 90–103); `_extract_test_metric` prefers `splits.test_hf`'s per-sample
   array, which `finalize_and_write` emits for this family exactly as for the
   champion. `copylf_baselines.json` carries all 6 panel + all 3 guard datasets.
5. **Checkpoint-resume**: `smoke_eval.py` lines 298–315 load
   `<ckpt_dir>/last.pt` keyed on `(epochs_target, grid, recipe_hash)`; lines
   425–431 save it after the training stages. Already contract-compliant.
6. **Substrate**: `git ls-tree -r round1-substrate` contains
   `mf_field/akash/models/fno_transolver_seq/*` and `mf_field/akash/common/*`;
   `git diff --stat round1-substrate -- <those paths>` is empty, so the working
   tree artifact equals the substrate artifact. `git rev-parse round1-substrate`
   = `967562e2a4e3493515edab36b0fcb23655fce71f`.

## Proposal reasoning (alternatives weighed and rejected)

**Chosen: D1 as a 3-seed panel measurement of `fno_transolver_seq`, read for
the gate.**

Why this is a *genuine* experiment (program.md §1) and not a leaderboard row:
the artifact is the first thing in this round whose prediction path **consumes
the real test-time LF field** (its Transolver corrector cross-attends to a
1024-point context cloud drawn from the real LF field whenever the test split
carries it — all five npz_l panel datasets do; `smoke_eval.py` lines 355–362 and
439–444). The certified champion does not (U1). Since copy-LF has skill 1.0 by
definition and the champion has skill 4.18–16.33 on the sharp sets, the
information the champion discards is worth 4–16× — and this card measures how
much of it a gated point-based corrector can recover. Whether the answer is
"most", "some", or "none", it decides what stream s4 does next, and the answer
is a number nobody in this project has.

The gate makes the measurement self-testing: `alpha` is fitted by least-squares
plus a line search that contains 0 with `MIN_GAIN = 1e-3` on a held-out split
(`smoke_eval.py` lines 379–392), so `alpha = 0` on a dataset is a *measured
verdict* — "the Transolver correction failed its own out-of-sample test there" —
and needs no noise-floor argument at all. Per-dataset `alpha` is precisely the
routing prior D2 needs (U3).

**Alternatives rejected:**

- *(B) D1 + the D2 router in one card.* Rejected: confounds "does the corrector
  add value" with "does routing add value"; the router's own design (what the
  gate is conditioned on, per-region vs per-band) should be chosen from the
  measured per-dataset `alpha` and correction magnitudes, which do not exist
  yet; and it roughly doubles a batch that is already ~40 GPU-h. program.md §4.2
  is explicit: one batch = one experiment.
- *(C) Skip the measurement, go straight to D2 routing.* Rejected: §12.4
  directs the measurement first, and building a spatially-resolved router over
  an expert whose scalar-gated version has never been scored risks burning the
  5-ALGO-attempt budget on a mechanism with no measured foundation. It would
  also throw away the identity-safe construction the websearcher named as the
  differentiator — that construction is *this* artifact's `alpha` line search,
  and its behaviour on the panel is exactly what batch 1 would learn.
- *(D) D3 per-band fidelity routing.* Rejected for batch 1: the verdict carries
  a **pre-falsified-lever flag** (program.md §5 "LF low-mode freezing
  (`mf_fno_spectral`): worst on sharp, catastrophic on lid-cavity"), and a
  defensible soft variant needs the per-band error decomposition that
  `s2_beyond_copy`'s batch-1 diagnostic is about to produce. Better in batch 2+
  with that evidence.
- *(E) Add a second arm (`ctx_source = fno_base`) as an in-card ablation.*
  Rejected on cost (it doubles ~40 GPU-h and the three 256² datasets are the
  expensive ones), but **kept reachable**: the proposal declares
  `MFFP_CTX_SOURCE=auto` as a recipe env knob so the mechanism-analyzer's probe
  turns (or batch 2) can run the LF-context ablation by flipping one env var,
  with the knob already inside the cache key. `ifc_poisson` also supplies a free
  weak contrast: it *automatically* runs the `fno_base` context path.
- *(F) Make it a `diagnostic` card.* Rejected: program.md §4.3 defines
  `diagnostic` as a measurement with **no training**; this trains for 200 epochs
  and a single-seed claim would not be reportable under §4.4. The websearcher's
  "claims zero novelty" is a statement about `prior_art`, not about `card_type`.
  The card is `model`, with `prior_art.verdict = "preempted"` for the
  architecture and the novelty claim made only for the MF composition question.

## Proposal

- **Category**: `mf_composition_measurement` (score the built hybrid; read the
  gate).
- **Card type**: `model` (trains; full 1+2 seed protocol).
- **Motivation** (quotes the prior-art verdict verbatim): the websearcher's D1
  row reads *"`preempted-but-MF-composition-open`* … *Neither source is
  multi-fidelity. Open: out-of-fold LF->HF residual targets under N_hf scarcity;
  the *real LF field* as corrector context; the least-squares + line-search
  `alpha` that makes the hybrid collapse **exactly** to the FNO when the
  correction is useless. **D1 is a measurement card — it should claim no novelty
  at all**, only that it measures whether the +30.6% oracle survives against
  copy-LF on sharp 2-D."* program.md §12.4 directs the same: *"batch 1 should
  start by scoring it on the panel (cheap, mostly evaluation)."* The reason it
  is worth GPU time rather than being a formality: the certified champion's
  model is `FNO2d(cond_dim, ...)` — it never sees the LF field at test time,
  while copy-LF (skill 1.0) is the LF field; this artifact is the round's first
  model whose prediction path reads the real test-time LF field, so its
  per-dataset `alpha` and base→hybrid delta measure how much of the discarded
  4–16× LF information a gated corrector recovers.
- **Concrete config**:
  1. `models_r1/fno_transolver_seq/` = **verbatim copy** of
     `mf_field/akash/models/fno_transolver_seq/{manifest.json,model.py,smoke_eval.py}`
     at base_commit `967562e`.
  2. **Exactly two permitted edits**, both mechanical (a third edit should draw
     a code-reviewer FAIL — the artifact under measurement must stay the built
     family):
     (a) `smoke_eval.py` line 57: `AKASH = Path(__file__).resolve().parents[2]`
     is wrong once the family lives at `models_r1/<family>/`. Replace with an
     upward search from `__file__` for the first ancestor containing
     `mf_field/akash/common/mffp.py`, and `raise RuntimeError` if none is found
     (assert, never default). The worktree is a full checkout, so the search
     terminates at the worktree root.
     (b) `smoke_eval.py` line 557: make the existing `--ctx_source` default read
     `os.environ.get("MFFP_CTX_SOURCE", "auto")`, because `score_panel.py`
     passes only the six contract args and program.md §5.5 requires every knob
     to be a recipe-recorded env var. Behaviourally a no-op at the declared
     value.
  3. Run through the round eval layer only:
     `score_panel.py --family_dir <worktree>/models_r1/fno_transolver_seq
     --datasets panel --epochs 200 --seed {0,1,2} --env MFFP_CTX_SOURCE=auto`.
     Do **not** set `ROUND1_EVAL_RESULTS` — batch 0 (`eval/run_batch0.sbatch`)
     did not, and per-run JSONs must land where the anchor's did.
  4. SLURM shape: one array task per (dataset, seed), job name
     `r1-s4_hybrid_routing-B1-s{seed}`. `--time 08:00:00` for
     `sharp__allen_cahn_2d`, `sharp__fisher_kpp_2d`, `sharp__cahn_hilliard`
     (batch-0 champion 44.4 min × ≈5.25 epoch-equivalents: LF-pretrain +
     HF-finetune + 4 OOF folds + corrector + epochs/4 joint stage);
     `--time 03:00:00` for `sharp__phase_field_crystal_2d`, `ext__helmholtz_2d`,
     `ifc_poisson`. Resume from `<ckpt_dir>/last.pt` is already implemented.
  5. Guard set at contract tier with seed 0 (`--datasets guard --epochs 2`) in
     the seed-0 script, per program.md §2.3, so part 5 can carry guard flags.
  6. **Measurement extraction (no new code — all keys already emitted by
     `finalize_and_write(extra=...)`, `smoke_eval.py` lines 474–500):** the
     analyzer must tabulate, per (dataset, seed): `alpha`,
     `alpha_least_squares`, `base_only_rel_l2` (the *paired within-run control*
     — the champion recipe trained on the identical seed/split),
     `base_only_rel_l2_final_fno`, `val_rel_l2_base`, `val_rel_l2_hybrid`,
     `stage3_joint`, `correction_rms_raw_units`, `ctx_source`, `ctx_fidelity`,
     `latency_ms_per_sample`, `peak_mem_mb`.
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
  - *Sanity gate (free):* `base_only_rel_l2` should reproduce the batch-0 anchor
    per-dataset skills within each dataset's `min_claimable_effect` (the recipe
    is byte-identical). A larger disagreement means broken plumbing, not
    science, and should be debugged before the hybrid numbers are read.
  - *Primary prediction:* `alpha > 0` on **≥ 3 of the 5** sharp-2-D panel
    datasets (the gate is fitted on held-out data with `MIN_GAIN = 1e-3`, and
    the correction's context is a field 4–16× more accurate than the base).
  - *Score:* panel geomean skill improves from the anchor **6.703**
    [6.219, 7.102] to **4.5–6.0** (−10% to −33%), with at least one of
    `sharp__allen_cahn_2d` (anchor skill 16.334, floor 1.633),
    `sharp__phase_field_crystal_2d` (11.511, floor 1.151),
    `sharp__fisher_kpp_2d` (4.177, floor 0.418), `sharp__cahn_hilliard`
    (5.533, floor 0.553) improving by **more than its floor** — i.e. ≥ 10%
    relative on a dataset whose floor is 10% relative, so the claim is
    falsifiable. Evidence for the direction: the 2-epoch `ifc_poisson` contract
    run already produced a 10.5% base→hybrid gain on the weaker context path.
  - *Explicitly NOT claimed:* skill < 1 anywhere (that needs a 4–16×
    improvement; success criterion 2 stays open), and **nothing on
    `ext__helmholtz_2d`**, whose floor is 9.695 skill units (≈70% relative) —
    recorded, never claimed. `ifc_poisson`'s floor is 0.240 skill (15.3%), above
    the 10.5% seen at contract tier, so it is a watch item, not a claim.
- **Expected falsification**: If the fitted gate `alpha` is 0 on ≥ 4 of the 5
  sharp-2-D panel datasets at seed 0 (the least-squares + line-search gate
  rejecting the correction on its own held-out split) **and** no sharp-2-D
  dataset's 3-seed mean skill beats the batch-0 anchor by at least its
  `min_claimable_effect` (allen_cahn 1.633, pfc 1.151, fisher_kpp 0.418,
  cahn_hilliard 0.553 skill units), then the +30.6% FNO↔Transolver pairwise
  oracle does not transfer to sharp-2-D multi-fidelity fusion, and routing
  between these two experts is not this stream's lever.
- **Anchor reference**: `null` (s4 is a lever stream; program.md §4.5 gives a
  card_id only for `s5_tuning` batches ≥ 2 — the own-stream anchor 6.703 is
  implicit).
- **Prior art to transcribe into the card**: `verdict:
  "preempted-but-MF-composition-open"`; citations
  `https://arxiv.org/html/2602.11197`, `https://arxiv.org/abs/2311.12902`
  (architecture preempted, neither multi-fidelity), with the boundary sentence
  from the websearch report item 2 recorded verbatim.

## Status

- Slot **covered** (one proposal, category `mf_composition_measurement`).
- Skipped: no.
- Reopen candidates resolved: none exist (no prior cards in this stream).
- Immutables self-check: **pass** (10/10, evidence in the section below;
  no revision was needed, so there is no `iteration_2.md`).

## Immutables self-check (10 items, positive evidence)

1. **Data read-only.** The card touches nothing under `factory_root/data/**`;
   `score_panel.py::_run_one` builds `data_dir` itself from `project.yaml` and
   passes it read-only to `smoke_eval.py`; the family only calls
   `load_mf_dataset(ds_dir, "train"|"test")`. N_hf stays 5 on ifc_poisson (the
   contract run printed `N_hf=5`), and LF is the dataset's own coarse solve —
   the family's docstring explicitly refuses to synthesise test LF by
   downsampling HF ("would leak the answer, and this family refuses to do that",
   `smoke_eval.py` lines 26–31).
2. **Panel + guard fixed.** `--datasets panel` and `--datasets guard` expand
   from `project.yaml`; the card names no dataset outside those lists.
3. **Eval layer / spec untouched.** All two edits are inside
   `models_r1/fno_transolver_seq/` in the worktree; the run command is the
   stock `score_panel.py` CLI already used by `eval/run_batch0.sbatch`, with no
   change requested to `round1/eval/`, `project.yaml`, `program.md`, or any
   agent prompt.
4. **One nRMSE definition.** The score comes from
   `_extract_test_metric` → `splits.test_hf.rel_l2_per_sample` via
   `nrmse.py`; the family's own `_rel_l2` numbers (`base_only_rel_l2` etc.) are
   recorded as *diagnostics inside `extra`*, never substituted for the scored
   metric, and the card says so.
5. **Contract CLI fixed.** The copied `smoke_eval.py` keeps
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed` (verified at
   lines 551–556); the only knob is `MFFP_CTX_SOURCE`, declared in
   `recipe.env`, which `score_panel.py` merges into the child env (line 95) and
   folds into `code_hash` (lines 68–70).
6. **Seeds and tier fixed.** `seeds: [0, 1, 2]`, `epochs: 200` = the smoke tier
   from `project.yaml tiers.smoke_epochs`; the seed-0-then-1–2 protocol is
   named in the config; cratered threshold = 1.5 × 6.703 = **10.05** panel
   geomean skill.
7. **Guarded factory surfaces untouched.** `mf_field/akash/**` and
   `factory_root/{eval,baselines,references,scripts,data}/` are *copied from and
   imported*, never written: the card's only writes are new files under
   `<worktree>/models_r1/`. The `git diff --stat round1-substrate -- <akash
   paths>` I ran is empty and must stay empty.
8. **Checkpoint-resume.** Implemented already: `<ckpt_dir>/last.pt` is loaded
   at `smoke_eval.py` lines 300–315 keyed on `(epochs_target, grid,
   recipe_hash)` and written at lines 425–431 after the training stages; the
   contract run created `<ckpt_dir>/last.pt` in my scratch dir.
9. **Falsification exceeds the noise floor.** The score half of the clause is
   stated per dataset in `min_claimable_effect` units taken verbatim from
   `state/noise_floor.json`: allen_cahn **1.633**, pfc **1.151**, fisher_kpp
   **0.418**, cahn_hilliard **0.553** (each = 10% of that dataset's anchor mean
   skill 16.334 / 11.511 / 4.177 / 5.533). `ext__helmholtz_2d` (floor **9.695**,
   ≈70% relative) is excluded from every claim by construction, and
   `ifc_poisson` (floor **0.240** on mean skill 1.566) is a watch item only. The
   `alpha` half of the clause is a directly measured, out-of-sample-tested
   scalar and does not depend on a floor at all.
10. **Not a pre-falsified lever.** Nearest of the three: *"LF low-mode freezing
    (`mf_fno_spectral`)"*. Difference: this card freezes **no spectral band and
    imposes no LF constraint** — the LF field enters only as cross-attention
    *context* for a corrector whose contribution is scaled by a gate that is
    zero unless it earns held-out improvement. The other two (WNO backbone swap;
    diffusion prior) share no component with this card: the backbone is the
    certified FNO champion and there is no generative prior.

**Self-check verdict: pass (10/10).** No revision required; no
`iteration_2.md`.
