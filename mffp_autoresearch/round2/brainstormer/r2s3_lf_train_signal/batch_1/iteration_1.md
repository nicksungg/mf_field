# iteration_1 — brainstormer, `r2s3_lf_train_signal`, batch 1

## Design context considered

- `summary_so_far.md` §6 (unknowns) — especially the verified ladder asymmetry
  and the fact that no matched with/without-LF ablation exists anywhere.
- Prior-art verdict table, `websearches/r2s3_lf_train_signal/batch_1/report.md`
  ("## Prior-art verdict"), all three rows.
- program.md §12.3 (quoted verbatim in `summary_so_far.md` §2), §2.2 floor
  arms, §2.3 panel + guards, §4.2 seed/skip rules, §5 immutables + round-2
  additions 9–13, §5 pre-falsified levers.
- Anchor: `state/anchors/r2s3_lf_train_signal.json` = **23.0636** best-floor
  panel geomean; per-dataset floors `state/anchors/floors.json`.
- `state/noise_floor.json` (PROVISIONAL, `round1-batch0-rescaled`):
  `min_claimable_effect` helmholtz 10.6811, pfc 6.9839, allen_cahn 14.8152,
  fisher_kpp 1.2198, cahn_hilliard 1.1604, **ifc_poisson 0.2399** skill units.
- Declared baseline `mf_fno_transfer_film`, seed-0/200-epoch panel restated
  under corrected denominators from
  `round1/eval/results/mf_fno_transfer_film/*_e200_s0.json`: panel geomean
  skill **19.0433** (per-dataset in `summary_so_far.md` §4).
- Round-1 prior on ifc_poisson: `mf_fno_ladder_gain` arm `self_only__none`,
  nRMSE 0.021913326 / skill 0.6087035
  (`round1/experiment_cards/s1_poisson/batch_3/B3.json`, part 5 `per_arm`).
- Code read first-hand:
  `mf_field/factory_mffp/models/mf_fno_transfer_film/{model.py,smoke_eval.py}`
  (FiLM-FNO decoder, `forward(cond)` with the grid fixed at construction;
  `_to_grid` upsamples the LF field to the working grid; `norm="ortho"` FFTs;
  200 LF-pretrain + 200 HF-finetune; per-stage `max|y|` scaler);
  `round1/worktrees/s1_poisson/B3/models_r1/mf_fno_ladder_gain/` (cond =
  `[X, f_src, f_tgt]`, every rung upsampled to the working grid, per-level
  scalers); `round2/eval/score_panel.py` (stripped-view enforcement, cache key
  = family .py + `models/_common` + eval files + env; `out_json` and
  `ckpt_dir` derived from `ROUND2_EVAL_RESULTS`);
  `round2/eval/panel_data.py` (ADR r2-0001 conventions:
  `_node_aligned_periodic_up` is exact at shared nodes, `up[::r,::r] == lf`).
- Timing: `round1/state/timing_ledger.json`, `mf_fno_transfer_film`, 200
  epochs, p100 — helmholtz 7.73 min, pfc 12.35, allen_cahn 44.50, fisher_kpp
  44.35, cahn_hilliard 44.35, ifc_poisson 0.78 (panel ~154 min p100 for a
  200-LF + 200-HF budget, i.e. ~77 min per "400-rows x 200-epochs at the
  working grid" unit).

## Proposal reasoning

### The fulcrum

The stream's question ("how much does LF, available only during training,
help?") has a **different answer per dataset**, and the reason is on disk, not
in the literature:

| panel dataset | LF rung conditions | what LF can add |
|---|---|---|
| 4 sharp + helmholtz | **identical** to the HF rung's (bit-identical `x`) | only a spectrally truncated view of fields we already have at full resolution — a curriculum/regularizer at best |
| `ifc_poisson` | **disjoint** from the 5 HF conditions (170 extra) | genuine parameter-space coverage: a 35x sample multiplier |

Any design that does not put this asymmetry at its centre is either measuring
noise on 5 datasets or re-deriving round 1's `self_only` result on the sixth.

### Alternatives weighed and rejected

**A. D1 — distil an LF-consuming round-1 teacher into a condition-only
student (§5.10b).** Rejected on a *structural* ground I verified on disk. A
teacher of the form (LF field, cond) → HF field needs **aligned** LF↔HF pairs.
On ifc_poisson there are none — f8/f16/f32/f64 sit at pairwise disjoint
conditions (exact row-match counts 0/0/0), so the teacher is untrainable
exactly where LF carries information. On the sharp panel the teacher *is*
trainable (400 aligned pairs) but its pseudo-labels would land on the same 400
conditions that already carry real HF targets — zero coverage gain, and the
websearcher's own caveat (https://arxiv.org/html/2604.20061v1, "irreversible
information loss") bounds what the soft targets could add. So D1 is impossible
where it would help and useless where it is possible. Worth recording; not
worth a card. (This also disposes of the EAAI privileged-modality composition
for *this* benchmark: the privileged modality is not co-located with the
scarce labels.)

**B. Undifferentiated LF-pretrain → HF-finetune.** Forbidden by §12.3 and by
the websearcher's instruction 1; it is `mf_fno_transfer_film` verbatim and is
externally published (https://arxiv.org/pdf/2304.06972). It enters this card
only as the declared baseline.

**C. Re-run round 1's ladder recipe (`self_only`) on the panel.** This is the
nearest rebadge hazard. `mf_fno_ladder_gain` is a round-1 family; §5.10 allows
round-1 code only as a frozen test-time sub-component (r2s2) or a training-time
teacher (r2s3-D1, rejected above) — not as the model itself. Even
re-implemented, "fidelity-tagged joint training with upsampled rung targets"
would be the same pathway. Rejected as-is; kept as the *prior* that sets the
ifc_poisson expectation and as one of the two things arm A3 controls for.

**D (chosen). D2 x D3: multi-rung supervision at each rung's NATIVE
resolution, with a matched no-LF control and an upsample control.** One
condition→HF operator `S`, no fidelity tag, no LF anywhere at test. During
training the same weights are evaluated at each rung's native grid and
supervised by that rung's own coarse solve. Because the spectral weights are
indexed by absolute wavenumber and are clipped to the grid's Nyquist at
forward time, a rung at 64^2 constrains only the modes it resolves — the
"coarse-graining is irreversible information loss" caveat is honoured
*structurally* rather than asserted, and it is the exact formalization of the
websearcher's D2 open surface ("keeping the LF heads strictly out of that path,
as a pure representation regularizer"). There is no LF head at all: zero extra
parameters, so the test-time path is provably the HF path.

Why this is not the composite MFNN (https://arxiv.org/abs/1903.00104): the
composite MFNN's LF sub-network is *inside* the test-time prediction path (its
output feeds the HF net). Here the LF signal appears only as a loss term
evaluated on a resolution the test never uses.

Why this is not `mf_fno_transfer_film`: (i) joint, not sequential — every rung
is present in stage 1; (ii) rung targets are never upsampled; (iii) the forward
signature is `forward(cond, out_hw)`, not `forward(cond)` with the grid bound
at construction; (iv) the spectral normalization is `norm="forward"`, not
`"ortho"`, which is what makes the same mode weights act identically at every
rung resolution (under `ortho`, the normalized coefficients of one physical
field differ by sqrt(H1W1/H2W2) between rungs, so multi-rung weight sharing
would be silently inconsistent). (iv) is load-bearing, not cosmetic.

Why this is not `mf_fno_ladder*`: no fidelity tag in the conditioning (which
also removes round 1's `f_src` fragility — report §1: "the slate arm scores
0.1066 at `f_src=1` but 0.0219 at `f_src=0`"), one shared scaler instead of
per-level scalers, native-resolution supervision instead of upsampled rows,
and the panel instead of ifc_poisson alone.

### Arms

| arm | stage-1 rows | datasets | role |
|---|---|---|---|
| `hf_only` | HF rung only | panel (6) | **matched no-LF control** — identical architecture, identical 200+200 epoch budget, identical optimizer/LR schedule; the only difference is which rows enter stage 1 |
| `rung_native` | every rung, each at its **native** grid | panel (6) | **PRIMARY / scored** |
| `rung_upsampled` | every rung, bilinearly upsampled to the HF working grid (the `_to_grid` convention used by transfer_film and by every round-1 ladder family) | `ifc_poisson, sharp__cahn_hilliard, sharp__phase_field_crystal_2d` | **mechanism control** — isolates *how* the rung enters from *whether* LF helps; expected to lose partly because of round 1's (r-1)/2 registration defect (r1 report §5.1) and partly because it fabricates high-band content the coarse solve never resolved |

Declared baseline `mf_fno_transfer_film` is **cited**, not re-trained on the
whole panel (websearcher instruction 6: "reuse its numbers rather than
re-deriving"), because I read its round-1 seed-0/200-epoch result JSONs
directly and the round-2 metric (mean of `rel_l2_per_sample`) is byte-identical
to the one that produced them; only the denominators changed. A **validity
gate** re-runs it on `ifc_poisson` only (0.78 min on p100) under the round-2
eval layer and must reproduce nRMSE 0.055604 within 10% relative — cheap
insurance that the citation is sound across GPU types (round-1 process finding:
bitwise gates only on CPU; use a certified envelope when training is
independent). The gate is not a falsification clause.

`rung_upsampled` is restricted to 3 datasets purely for compute (it is 3x the
stage-1 cost of `hf_only`); it covers the one dataset where LF carries
information plus the cheapest and the most expensive nested datasets.

### Compute budget

Using the round-1 ledger unit (~77 min p100 for 400 rows x 200 epochs at the
working grid over the panel): `hf_only` ~2.0 units (154 min), `rung_native`
~2.31 units (178 min; the extra rungs cost 1/4 + 1/16 of an HF epoch),
`rung_upsampled` on 3 datasets ~115 min, validity gate ~1 min, guard set at
contract tier ~3 min. Total ~450 min on p100, ~2.5 h on h100. Every
(arm, dataset) pair is independently cached by `score_panel.py`
(`code_hash` includes the env), so the job is idempotent under preemption:
resubmitting skips finished pairs. `--time 04:00:00`, `gpu:h100:1`.

### Train/val discipline (§12.1, mandatory)

Fixed 200 + 200 epoch budget, cosine schedule, **no early stopping and no
validation-based model selection of any kind**, so no validation split is
consumed and there is no leakage surface (the round-1 D3 `val_idx`
double-consumption caveat cannot arise). This is stated because on ifc_poisson
a validation split of 5 HF samples would be meaningless anyway.

## Proposal

- **Category**: `lf_train_signal / multi-rung native-resolution supervision`
- **Card type**: `model`
- **Motivation**: the prior-art verdict scores the auxiliary-rung composition
  **`preempted-but-MF-composition-open`** and the ifc_poisson coverage variant
  **`novel`**; combined with the on-disk ladder asymmetry, the stream's
  question can be answered with one matched contrast whose predicted answer
  differs by dataset. (Verbatim verdict lines are quoted in `report.md`.)
- **Concrete config**: new family `models_r2/r2s3_rung_supervised`.
  - `CondFieldDecoder(cond_dim, hidden=64, n_blocks=4, modes_cap=12)`,
    `forward(cond, out_hw) -> (B, H, W)`. Coordinate channels are built at
    forward time for the requested `out_hw`; lift conv 2->64; 4 blocks of
    [SpectralConv2d(modes clipped to the grid Nyquist at forward time) + 1x1
    conv + FiLM(cond) affine after GroupNorm + GELU]; projection 1x1 64->128->1.
    FFTs use `norm="forward"` so mode weights are resolution-consistent.
  - Stage 1 (`--epochs` = 200, AdamW lr 1e-3, wd 1e-5, cosine, clip 1.0,
    batch 16): minibatches drawn from the arm's stage-1 row set, grouped by
    rung (one forward per rung per step), MSE in scaled units.
  - Stage 2 (200 epochs, lr 3e-4, otherwise identical): HF rows only, all
    arms — matched to the declared baseline's 200 + 200 structure.
  - Scaler: ONE shared `s = max|y|` over all stage-1 rung fields
    (round-1 `MFFP_LADDER_SCALER=shared`). Per-level scalers are unavailable
    without a fidelity tag; the r1 s5 revin_lf finding (cross-fidelity
    normalization transfer is exact at LF-pretrain, 3.1% proxy at HF) is
    reused as the justification for not re-litigating this axis, and the
    per-rung `max|y|`/`mean|y|` table is emitted as instrumentation so
    batch 2 can act on it.
  - Test: `S(cond, HF_work_grid)` only. No LF tensor is constructed at test.
  - Checkpoint: `<ckpt_dir>/last.pt` every 10 epochs with
    `{stage, epoch, model, opt, sched, rng, epochs_target, arm, grid}`;
    resume is exact. Arms never collide because each arm gets its own
    `ROUND2_EVAL_RESULTS` (and hence its own `ckpt_dir`).
  - Score-neutral instrumentation: per-rung row/grid/amplitude table + exact
    condition-overlap counts with the HF rung; a **resolution-consistency
    probe** (rel-L2 between `S(cond, coarse)` and the ADR r2-0001 restriction
    of `S(cond, HF)` — node subsample for periodic, interior-node for
    Dirichlet, area-mean for cell-centred — before and after training);
    train-vs-test nRMSE gap per arm (feeds r2s4's overfitting anatomy);
    per-rung stage-1 loss curves.
- **Recipe**: see `report.md` (complete JSON).
- **Expected outcome**:
  - `hf_only` ifc_poisson: skill ~11 (range 8-17), i.e. at or worse than the
    train-mean floor 11.2063 — 5 samples cannot cover a 5-D condition space.
  - `rung_native` ifc_poisson: skill ~1.0 (range 0.5-3.0), bracketed by
    transfer_film's 1.5446 (LF-pretrain on the f8 rung only) and round 1's
    `self_only` 0.6087 (all 175 rows, but with the fidelity tag and per-level
    scalers this design deliberately drops).
  - **Predicted value-of-LF effect on ifc_poisson: ~10 skill units**, versus
    the provisional floor `min_claimable_effect` **0.2399** — ~42x the floor.
  - 5 aligned datasets: `rung_native` ~ `hf_only` within each dataset's
    `min_claimable_effect` (predicted null from the nested-ladder degeneracy
    rule); absolute levels in the transfer_film ballpark (helmholtz ~20, pfc
    ~70, allen_cahn ~150, fisher_kpp ~12, cahn_hilliard ~12).
  - Panel geomean: `rung_native` ~17-19 (vs anchor **23.0636** and declared
    baseline **19.0433**); `hf_only` ~26-27. The card is not expected to move
    the geomean much — its deliverable is the certified contrast and the
    ifc_poisson skill, possibly < 1 (round-2 criterion 2).
  - Floor arms (mandatory, §2.2, read from `state/anchors/floors.json`, not
    recomputed): `rung_native` must beat the best floor on each dataset it
    claims; on ifc_poisson that is NN 10.0549 / mean 11.2063 / zero 27.7778,
    all of which a ~1.0 skill clears by an order of magnitude, and on
    helmholtz the zero floor 3.3441 which it is NOT expected to clear
    (report-only discipline continues).
- **Expected falsification**: **F1 (primary)** — falsified if `rung_native`
  fails to beat `hf_only` on `ifc_poisson` by more than the certified floor
  0.2399 skill units, which would mean 170 disjoint LF conditions add nothing
  a condition→HF operator can use and the stream's premise is empty on the one
  dataset where LF demonstrably carries information. **F2 (mechanism)** —
  falsified if `rung_native` fails to beat `rung_upsampled` on `ifc_poisson`
  by more than 0.2399 skill units, which would mean native-resolution
  supervision is not the differentiator and the round-1/zoo upsample
  convention was already optimal. **F3 (degeneracy prediction, pre-registered
  in both directions)** — the design predicts NO LF effect on the 5
  condition-aligned datasets; that prediction is falsified if `rung_native`
  beats `hf_only` on >= 2 of the 5 by more than each dataset's
  `min_claimable_effect` (helmholtz 10.6811, pfc 6.9839, allen_cahn 14.8152,
  fisher_kpp 1.2198, cahn_hilliard 1.1604), which would establish that LF acts
  as a curriculum/regularizer independent of parameter coverage and would
  extend the nested-ladder degeneracy rule rather than confirm it.
  Pre-registered 2x2 reading for (F1, F2): pass/pass -> LF-as-coverage works
  and the native pathway is the reason; pass/fail -> LF-as-coverage works but
  any entry route suffices (the contribution is the measurement, not the
  pathway); fail/pass -> the pathway matters but nothing clears the floor
  (direction real, below resolution); fail/fail -> LF-as-training-signal is
  empty in this regime, which is itself a publishable negative for round-2
  criterion 1.
- **Anchor reference**: `null` (program.md §4.5 — lever stream, own-stream
  anchor 23.0636 implicit; no champion re-targeting in round 2).

## Status

- Slot covered: yes (one proposal, `model` card).
- Skipped: no.
- Reopen candidates resolved: none exist for this stream (see
  `summary_so_far.md` §5).
- Immutables self-check: **pass (11/11)** — recorded below.

## Immutables self-check (positive evidence per item)

1. **Data read-only.** The family reads the stripped view only through
   `data_adapters.load_mf_dataset(ds_dir, split)` — the same call
   `mf_fno_transfer_film/smoke_eval.py:112-113` makes; no file is written under
   any dataset dir, no rung is regenerated, `N_hf` is whatever the loader
   returns (5 on ifc_poisson, 400 on sharp), and every LF field used is the
   dataset's own coarse solve as shipped. The `rung_upsampled` arm upsamples a
   coarse solve in memory for a *training target*; it never downsamples HF to
   manufacture LF.
2. **Panel + guard set fixed.** `datasets: panel` for the two scored arms,
   `guard` at contract tier for the primary arm; the dataset lists come from
   `project.yaml panel:`/`guard_set:` via `score_panel.py --datasets
   panel|guard`, which the card does not redefine. The 3-dataset restriction on
   `rung_upsampled` is a subset of the panel for a control arm, not a
   redefinition of the panel used for scoring.
3. **Eval layer / spec untouched.** Nothing in the proposal edits
   `round2/eval/`, `project.yaml`, `program.md`, or any subagent prompt: the
   family lives at `models_r2/r2s3_rung_supervised` inside the worktree, is
   invoked through the unmodified `score_panel.py` CLI, and the ADR r2-0001
   restriction rules it needs for the consistency probe are re-implemented in
   the family dir with a provenance comment pointing at
   `round2/eval/panel_data.py` (read, not imported or modified).
4. **One nRMSE definition.** The family emits `rel_l2_per_sample` on the HF
   test split through the factory `finalize_and_write` path, exactly as
   `mf_fno_transfer_film` does; `score_panel._extract_test_metric` then takes
   the mean of that array. The training loss (multi-rung MSE in scaled units)
   is free per §5 "training loss is free; the SCORED metric is not".
5. **Contract CLI fixed.** `smoke_eval.py` exposes exactly
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`; every
   behavioural knob (`R2S3_ARM`, `R2S3_RUNGS`, `R2S3_SCALER`,
   `R2S3_SPECTRAL_NORM`, `R2S3_LAMBDA`, `R2S3_RESCONSIST_PROBE`) is listed in
   `recipe.env` and passed via `--env`, so all of them enter
   `score_panel.code_hash`.
6. **Seeds and tier budgets fixed.** `seeds: [0]` per `project.yaml
   seed_protocol.seeds` and §4.2 strict 1-seed; `epochs: 200` = the smoke tier
   from `project.yaml tiers.smoke_epochs`; guards at `contract_epochs: 2`. The
   200 + 200 two-stage reading of `--epochs` is the declared baseline's own
   convention (`mf_fno_transfer_film/smoke_eval.py` docstring: "--epochs is the
   HF fine-tune budget; LF pretraining uses the same budget"), so budgets stay
   matched between the card's arms and the baseline.
7. **Guarded factory surfaces untouched.** All new code is written under
   `<worktree>/models_r2/`. `mf_field/factory_mffp/models/mf_fno_transfer_film`
   is only *read* (its numbers are cited) and, for the validity gate, executed
   read-only via `--family_dir`; nothing under `factory_root/{eval,baselines,
   references,scripts,data}`, `factory.md`, or `akash/` is touched.
8. **Checkpoint-resume.** Specified explicitly: `<ckpt_dir>/last.pt` written
   every 10 epochs carrying `{stage, epoch, model, opt, sched, rng,
   epochs_target, arm, grid}` and resumed exactly, with a `done` marker keyed
   on `(epochs_target, arm, grid)`; arms cannot collide on `last.pt` because
   each arm exports its own `ROUND2_EVAL_RESULTS`, and `score_panel._run_one`
   derives `ckpt_dir` from that directory.
9. **Falsification threshold vs the noise floor.** F1 and F2 are stated on
   `ifc_poisson`, whose `state/noise_floor.json` `min_claimable_effect` is
   **0.23990756** skill units (spread of the 3 rescaled round-1 seeds:
   1.5446694, 1.4561617, 1.6960692). The predicted F1 effect is ~10 skill
   units (~11 -> ~1.0), i.e. ~42x the floor; F1 requires strictly more than
   0.2399. F3's per-dataset thresholds are quoted from the same file
   (helmholtz 10.68110662, pfc 6.98392165, allen_cahn 14.81520561, fisher_kpp
   1.21978271, cahn_hilliard 1.16035691) and F3 additionally requires >= 2 of
   5 datasets, so no single-dataset fluctuation can fire it. The floor is
   provisional (§4.3), so these thresholds are treated as the direct judgement
   they are, and the card will be re-read against r2s4-B1's certified spread
   when it lands.
10. **Not a pre-falsified lever.** Nearest is **LF low-mode freezing**
    (`mf_fno_spectral`: "worst on sharp, catastrophic on lid-cavity", r1
    program §5). Differences: that lever *substituted* the LF field's low modes
    into the prediction at test time (an LF-consuming test path, impossible in
    round 2 anyway); here nothing is frozen, nothing is substituted, no LF
    tensor exists at test, and the low-mode information enters only as a
    training loss evaluated at conditions the HF rung does not contain. The
    other two levers (WNO backbone swap, diffusion prior) are unrelated —
    the backbone is FNO and there is no generative component.
11. **Floor arms in the falsification reasoning.** Part 5 will report, next to
    `rung_native`, the frozen NN-in-condition / train-mean / zero floors from
    `state/anchors/floors.json` for every panel dataset. They are already used
    above: `hf_only` on ifc_poisson is *predicted to land at the train-mean
    floor* (11.2063) — that prediction is the control's sanity check, and if
    `rung_native` failed to beat NN 10.0549 / mean 11.2063 / zero 27.7778 on
    ifc_poisson the card would have learned nothing there whatever F1 says.
    Helmholtz carries the standing zero-floor caveat (3.3441, report-only) and
    pfc carries the band-limited-denominator caveat (`eval/copylf_baselines.json
    _notes.pfc`).
