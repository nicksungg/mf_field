# summary_so_far — brainstormer, stream `r2s3_lf_train_signal`, batch 1

All paths below are relative to `${ROUND_ROOT}` =
`/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round2` unless marked
`round1/`.

## 1. Websearch findings + prior-art verdict

Source: `websearches/r2s3_lf_train_signal/batch_1/report.md` (4 iterations, 12
WebSearch + 8 WebFetch calls, stopped by the ENOUGH rule). Three candidate
directions were scored:

- **D1** — distil an LF-consuming teacher (round-1 family, §5.10b, absent at
  test) into a condition-only student: **`preempted-but-MF-composition-open`**.
  Citations: EAAI 2025 representation-level multimodal distillation
  (https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293,
  403 on fetch — abstract only), LUPI canon, PI-distillation
  (https://arxiv.org/abs/2602.04942). Open: coarse *consistent solve* as the
  privileged modality with a condition-only, full-field student at N_hf = 5.
- **D2** — nested multi-resolution auxiliary target heads, heads discarded at
  test: **`preempted-but-MF-composition-open`**. Citations: composite MFNN
  (https://arxiv.org/abs/1903.00104 — LF net from the parameter input, LF data
  train-only, no LF solve at inference), MF-DeepONet
  (https://dl.acm.org/doi/10.1016/j.jcp.2023.112462), deep supervision
  (NeurIPS 2020 auxiliary-task reweighting). Open: keeping the LF signal
  strictly out of the test-time path on a fully nested ladder. Caveat to
  carry: https://arxiv.org/html/2604.20061v1 — coarse-graining is
  "irreversible information loss", so LF heads can only supply a
  spectral-truncation/curriculum prior.
- **D3** — LF-as-parameter-coverage on ifc_poisson (LF rungs at conditions
  *disjoint* from the 5 HF conditions) with a matched with/without-LF
  ablation: **`novel`**. Nearest neighbours: MLMC training of neural operators
  (https://arxiv.org/abs/2505.12940) and multiscale CNN training
  (https://arxiv.org/abs/2501.12739) — both are resolution hierarchies of the
  *same* parameters aimed at *cost*, not coverage. Iteration 3 also found **no**
  matched with/without-LF value-of-information ablation at N_hf ~ 5 anywhere.

Explicit instruction from the websearcher's "For the brainstormer" §1: *"Do not
propose LF-pretrain->HF-finetune in any undifferentiated form ... Score it as an
arm; never as the contribution."* And §2: *"The ladder asymmetry is the design
fulcrum."*

## 2. §12.3 conventions, verbatim from `program.md`

> ### 12.3 `r2s3_lf_train_signal` (lever)
>
> - **Question**: LF as training-only signal. Candidate mechanisms (spec §6):
>   distillation from an LF-consuming teacher (round-1 families in role §5.10b
>   — teacher at train, absent at test), LF-pretrain → HF-finetune, auxiliary
>   multi-fidelity losses (predict LF and HF jointly from condition).
> - **The stream has a mandatory declared baseline**: `mf_fno_transfer_film`
>   (factory zoo champion) IS LF-pretrain→HF-finetune from the condition
>   vector (verified 2026-07-31: its test input is `cond_by_fid` only; it runs
>   on the stripped view unmodified). Any r2s3 pretrain/finetune proposal must
>   either score it as the baseline arm or cite how it differs — an
>   undifferentiated re-proposal is a rebadge (reviewer FAIL, §5.10).
> - **revin_lf two-scaler finding** (r1 s5): exact at LF-pretrain, 3.1% proxy
>   at HF — normalization transfer across fidelities is a solved sub-problem;
>   reuse it, don't rediscover it.
> - **Nested-ladder degeneracy** (r1 report §6) directly constrains this
>   stream: with aligned/nested ladders, "multi-fidelity" training pairs
>   degenerate toward top-rung replication — LF-as-signal designs must state
>   what information the LF rungs add that the HF rung does not already
>   contain (spectral truncation structure, more samples at low rungs on
>   ifc_poisson: 70 lower-fidelity vs 5 HF).
> - The **unified normalization eligibility rule** (r1 s2, checks 0–6) governs
>   any per-sample normalization proposal; spread is not the decider.
> - Uses the existing 400 aligned samples only (§5.11).

Stream anchor (`state/anchors/r2s3_lf_train_signal.json`, `provisional:false`):
best-floor panel geomean **23.0636**; per-dataset best floors helmholtz 3.3441
(zero), pfc 59.8118 (mean), allen_cahn 269.1959 (NN), fisher_kpp 11.9931
(mean), cahn_hilliard 23.1803 (NN), ifc_poisson 10.0549 (NN).
`state/noise_floor.json` is PROVISIONAL; its `min_claimable_effect` values are
helmholtz 10.6811, pfc 6.9839, allen_cahn 14.8152, fisher_kpp 1.2198,
cahn_hilliard 1.1604, ifc_poisson 0.2399 skill units.

## 3. Within-stream prior cards

**None.** `experiment_cards/r2s3_lf_train_signal/` contains only `.gitkeep`;
this is the stream's first card. No batch 0 exists (§4.3: the launch anchor is
the training-free floor geomean, so no batch-0 training round was needed).

## 4. Cross-stream prior cards

**None in round 2** (all four stream card dirs are empty). Round-1 cards are
immutable read-only inputs (§5.13); the two that bear directly on this stream:

- `round1/experiment_cards/s1_poisson/batch_3/B3.json` — family
  `models_r1/mf_fno_ladder_gain`, `datasets: ifc_poisson`. Its arm
  `self_only__none` ("all 4 levels, self pairs only, 175 rows", a pure
  ladder-mode change, no gain head) scored **nRMSE 0.021913326, skill
  0.6087035** (part 5 `per_arm`). This is the round's best ifc_poisson number
  and — verified by reading `models_r1/mf_fno_ladder_gain/smoke_eval.py` — it
  is a **condition→field** model: `cond = [X, f_src, f_tgt] -> Y@work_grid`,
  no LF field input at test. So LF-as-training-signal already has an in-repo
  existence proof on ifc_poisson; it has never been run on the sharp panel
  (all four s1 cards are `datasets: ifc_poisson`) and never against a
  no-LF control.
- Declared baseline `mf_fno_transfer_film`: I recomputed its seed-0, 200-epoch
  panel under the CORRECTED denominators directly from
  `round1/eval/results/mf_fno_transfer_film/*_e200_s0.json` (mean of
  `rel_l2_per_sample` = the round-2 metric): helmholtz 6.202329 → skill
  20.7413; pfc 0.514776 → 69.7455; allen_cahn 0.263843 → 148.1626; fisher_kpp
  0.264904 → 12.3501; cahn_hilliard 0.487631 → 11.6650; ifc_poisson 0.055604 →
  1.5446. **Panel geomean skill 19.0433** — the number this stream must beat,
  and it already beats the 23.0636 floor anchor.

## 5. Reopen candidates

**None.** No prior r2s3 card exists, so no card carries `reopen_candidate:
true`.

## 6. What is UNKNOWN (the valuable section)

1. **The value of LF as a training signal has never been measured, here or
   anywhere.** Every in-repo LF-as-signal result (transfer_film,
   mf_fno_ladder*) is an LF-consuming arm with *no matched LF-free control at
   the same architecture and budget*. The websearcher found no such ablation in
   the literature either (iteration 3, term 3). Nobody knows whether
   transfer_film's 1.5446 ifc skill owes anything to the LF pretraining.
2. **The ladder asymmetry is verified on disk by me, not assumed** (I read the
   stripped view directly):
   - `sharp__{cahn_hilliard,allen_cahn_2d,fisher_kpp_2d,phase_field_crystal_2d}`
     — `train_l1/l2/l3` all carry **bit-identical** `x` arrays (400x19, 400x3,
     400x2, 400x2); `ext__helmholtz_2d` `train_l1/l2` likewise (400x3). LF adds
     **zero** parameter coverage on 5 of 6 panel datasets.
   - `ifc_poisson` `train/fidelity_{8,16,32,64}` hold 100/50/20/5 samples and
     the condition sets are **pairwise disjoint** (I checked exact row matches:
     f64 n f8 = 0, f64 n f32 = 0, f32 n f8 = 0). 170 extra conditions against
     5 HF.
   Two consequences nobody has tested: (a) on ifc_poisson there are **no
   aligned LF-HF pairs at all**, so a teacher of the form (LF field, cond) ->
   HF field is *untrainable there* — D1's mechanism is structurally impossible
   exactly where LF carries information, and useless where it is trainable
   (sharp, where the same 400 conditions already have HF targets); (b) the
   nested-ladder degeneracy rule predicts a **null** on the sharp panel, but it
   was established for all-pairs *fusion* training, never for condition→HF
   supervision.
3. **How the coarse rung should enter is unknown.** Every in-repo LF-as-signal
   family (`mf_fno_transfer_film/smoke_eval.py:_to_grid`,
   `mf_fno_ladder_gain/smoke_eval.py:field_cache`) **upsamples the coarse
   target to the HF working grid** and regresses full-field there. Round 1's
   own §5 finding says that interpolation carries a (r-1)/2 half-cell
   registration defect — i.e. the standard convention may be *teaching the
   network a shifted, high-band-fabricated target*. Nobody has compared it
   against supervising at the rung's native resolution.
4. **Whether a condition→HF operator is resolution-consistent at all.** FNO's
   discretization invariance is folklore for this codebase; the existing
   backbone uses `norm="ortho"` FFTs, under which the same physical field has
   resolution-dependent coefficients. Unmeasured.
5. **What the round-1 ladder result generalizes to.** `self_only` 0.6087 came
   with a fidelity tag `[X, f_src, f_tgt]` whose `f_src` setting is fragile
   (round-1 report §1: "the slate arm scores 0.1066 at `f_src=1` but 0.0219 at
   `f_src=0`"). Whether the gain survives removing the tag is unknown.
6. **Overfitting anatomy at N_hf = 5** (§12.4) — the train/test gap of a
   condition→HF model on ifc_poisson's 5 samples has never been recorded.
