# Iteration 1 — Stream `r2s3_lf_train_signal`, Batch 3

## Design context considered

- **summary_so_far.md §6** (the six unknowns), in particular #1 (is the LF
  effect an affine-rank phenomenon or generic sampling?), #2 (the clean
  `A0 − A1` contrast exists on 2 legs only), #3 (no panel-level ±LF number
  exists anywhere in the round).
- **Prior-art verdict P1** (`preempted-but-MF-composition-open`, supersedes
  B2's `novel` E5) and the websearcher's five open items (a)–(e); P2/P4/P5
  `preempted`; instruction 6 (per-dataset clauses, "EACH of", priced against
  `state/noise_floor.json`) and instruction 7 (standing caveats).
- **program.md §12.3** verbatim (quoted in summary §2): mandatory declared
  baseline `mf_fno_transfer_film`; nested-ladder degeneracy (must state what
  the LF rungs add that the HF rung does not contain); existing 400 aligned
  samples only.
- **Immutables (§5, and the §4.5 block below) verbatim**, incl. round-2
  additions 9–13 (stripped test view; declared-reuse-only; no new HF data;
  floor arms mandatory; round-1 artefacts read-only).
- **Anchor** `state/anchors/r2s3_lf_train_signal.json` = 23.063616857615774
  (best-floor panel geomean, `provisional: false`).
- **Certified noise floor** `state/noise_floor.json` (`_provisional: false`,
  source r2s4_diag-B1 3-seed condition→HF spread): `min_claimable_effect`
  ifc_poisson **0.9377041289531141**, sharp__cahn_hilliard
  **0.09124535322300886**, sharp__fisher_kpp_2d **0.0007136812826775696**,
  sharp__allen_cahn_2d **0.8797047190126648**,
  sharp__phase_field_crystal_2d **0.21302734961699343**, ext__helmholtz_2d
  **2.95299157437233**; panel geomean 1.1418668211296108.
- **Frozen floors** `state/anchors/floors.json` (400-row): ifc NN 10.054891 /
  mean 11.206332 / zero 27.777778; ch NN 23.180342 / mean 23.969 / zero
  23.921749; fk NN 16.338 / mean 11.993 / zero 46.621; ac NN 269.196 / mean
  562.03 / zero 561.556; pfc NN 68.556 / mean 59.812 / zero 135.487; helmholtz
  NN 4.385 / mean 14.611 / zero 3.344.
- **B2 part 7** `next_direction` (the design skeleton) and `open_question`
  (the A1′ leg), plus anomaly M1 (the null penalty is net harmful where
  active).
- **Pre-flight I ran myself** (B2 part 7 required it before any extension):
  `tools/design_coverage_audit.py` on all six panel datasets at the exact
  N_hf = 5 draws the family would use (`np.sort(default_rng(s).permutation(400)[:5])`
  → draw 0 = 55,88,133,202,293; draw 1 = 39,45,51,198,379; draw 2 =
  11,157,162,211,355). Result table (JSONs in the session scratchpad,
  `cov_<dataset>_s<draw>.json`):

  | dataset | d | rank[X,1] | **m** | κ(HF design) | rung verdict | uncovered LF rows/rung |
  |---|---|---|---|---|---|---|
  | ifc_poisson (native) | 5 | 5 | **1** | 58.7 | FULL_POOL_COMPLETES + DISJOINT | 100 / 50 / 20 |
  | sharp__cahn_hilliard | 19 | 5 | **15** | 2.0–2.4 | FULL_POOL_COMPLETES | 395 |
  | sharp__fisher_kpp_2d | 2 | 3 | **0** | 50 382–78 566 | NO_DEFICIT_TO_FIX | 395 |
  | ext__helmholtz_2d | 3 | 4 | **0** | 221–251 | NO_DEFICIT_TO_FIX | 395 |
  | sharp__allen_cahn_2d | 3 | 4 | **0** | 234–1175 | NO_DEFICIT_TO_FIX | 395 |
  | sharp__phase_field_crystal_2d | 2 | 3 | **0** | 14–25 | NO_DEFICIT_TO_FIX | 395 |

  This is the single most consequential fact for the design: **the affine
  coverage story exists on only 2 of the 6 panel datasets**, and the three
  extension datasets B2 nominated all return `m_reduction_full = 0`.

## Proposal reasoning

### Should there be a B3 at all? (the close-on-B2 fallback, weighed)

B2's part 7 authorises closing on B2. I decided **against** closing, on four
grounds, each traceable to a file I read:

1. **The round's only positive value-of-LF evidence rests on a mechanism that
   failed.** `r2s4_diag-B2` (the sibling accounting card) came back
   **falsified**: LF as an auxiliary *target* moved nothing (|T1−T0| inside the
   operative threshold in 15/15 dataset×N cells). So the entire round-2
   affirmative answer to success criterion 1 is r2s3-B2's coverage effect —
   and in B2 that effect is reported through `A2_lf_cov_null`, whose penalty
   B2's own anomaly M1 prices as net harmful (−1.2860 ifc = 1.37× floor,
   −0.7080 ch = 7.8× floor). The clean `A0 − A1` contrast exists on **two
   legs** (ifc; ch draw 0). A deliverable in that shape is fragile.
2. **3 of 6 panel datasets cannot support a panel statement**, and criterion 1
   asks for a claimable effect "on at least 3 panel datasets" — B2 has exactly
   3, one of which (fisher_kpp) is a pure level effect and loses its floor.
   Widening to 6 converts a marginal pass into a panel-level result and makes
   a panel geomean computable for both arms for the first time in the round.
3. **The pre-flight turned the extension from "more of the same" into a real
   test.** Before I ran `design_coverage_audit.py`, "extend to 3 more datasets"
   was measurement bulk. After it, the extension is a discriminating
   experiment: all three extension datasets have **m = 0**, so they separate
   "LF pays by supplying affine directions the HF design cannot see"
   (B2's ifc/ch reading) from "LF pays by sampling the map at 395 conditions
   the HF rows do not cover, affine or not". Both outcomes are publishable
   statements about the regime; neither is currently known.
4. **Cost is small and measured**: B2 ran 17 legs / 3 datasets in 41.63 min on
   h200 (`state/timing_ledger.json`, job 66185845). 33 legs over 6 datasets,
   with the expensive penalty machinery removed, extrapolates to ≈ 85 min —
   inside B2's part-7 estimate of ~1.5 h.

### Alternatives weighed and rejected

- **A1′, the amplitude-corrected null-direction penalty on cahn_hilliard**
  (B2's `open_question`; websearch P4 `preempted`). **Rejected.** B2 turn 3
  measured the cahn_hilliard defect as *alignment*, not amplitude: A1's
  15-d unseeable block sits at amplitude ratio **0.8861** but Frobenius
  cos **+0.2172**, and the shipped penalty pushed amplitude to 0.9925 while
  dropping alignment to **+0.0463** and costing 0.7080 skill units. An
  amplitude correction therefore attacks the 11%-wrong quantity and leaves the
  78%-wrong one untouched. On ifc the same turn bounds the best possible
  retune at 2.6349 vs penalty-free A1's 2.1690 — i.e. **the ceiling of the
  retune is still worse than doing nothing**. Dropping it also removes the
  entire penalty/ridge-law/lift-target code surface from the family, which is
  the main build risk on three new datasets. This is not a silent drop: it is
  the explicit resolution of B2's open question, decided on B2's own numbers.
- **Re-proposing the null penalty as-is.** Rejected: pre-falsified-lever
  discipline (program.md §5) — B2 measured it net-negative and turn 1–2 priced
  the retune ceiling.
- **A gated / adaptively-weighted LF loss** (P5). Rejected: `preempted`, and
  the websearcher calls a card claiming it "a rebadge risk under §5.10".
- **Running the extension at full N = 400 HF.** Rejected: at N = 400 every
  design is full rank and m = 0 trivially, the coverage question evaporates,
  and full-N ±LF accounting is `r2s4_diag-B2`'s declared turf (§12.4,
  "r2s4 measures, r2s3 optimizes"; that card already ran N_fit ∈ {20,80,320}).
- **Citing B2's existing legs instead of re-running them.** Rejected: the
  drift-class rule (§12.4) says only in-job paired controls are controls, and
  cross-worktree code identity has never been verified. Re-running the 8
  overlapping legs in-job costs ~20 min and makes every contrast on the card
  self-contained; the comparison against B2's recorded numbers then becomes a
  free reproduction check (F3) instead of a load-bearing assumption.
- **Adding seeds 1–2.** Not available: program.md §4.2 strict 1-seed in-round
  (orchestrator note 4). Variance is addressed with 3 HF-subset draws per
  dataset (draws are *not* seeds and are reported as draws, per B2's
  `seed_semantics`).

### The proposal

A **measurement-completion model card**: the matched, step-matched,
normalization-matched ±LF contrast `A0_nolf` vs `A1_lf_cov` at N_hf = 5 on
**all six panel datasets × three HF-subset draws**, with the failed penalty
mechanism removed, the mandatory floor arms in-regime and frozen, and a
pre-registered structural clause on the four m = 0 datasets.

What the LF rungs add that the HF rung does not contain (§12.3 nested-ladder
requirement): **395 condition rows per rung that carry no HF row at all**
(100/50/20 on ifc_poisson, where the ladder is disjoint by construction) —
verified training-free by the pre-flight above. Nothing here relies on
`hf − lf` pairing, so the nested-ladder degeneracy does not apply.

## Proposal

- **Category**: `lf_train_signal / panel completion of the matched budget-equal
  ±LF contrast at N_hf = 5 (coverage arm), with the m = 0 extension as the
  discriminating test of the affine-coverage reading`
- **Card type**: `model` (trained arms scored on the panel in skill units;
  floor arms mandatory per §2.2). PRIMARY scored arm = `A1_lf_cov`.
- **Motivation**: quotes prior-art row **P1** verbatim (see report.md), which
  supersedes B2's `novel` verdict for E5. The deliverable is framed as the
  regime-specific composition (a)+(d)+(e) — condition-vector-only test input
  with genuine coarse consistent solves used only at train, the copy-LF-solve
  denominator, and a panel that varies in condition completeness — not as a
  new mechanism and not as a novel measurement genre.
- **Concrete config**:
  - New family `models_r2/r2s3_coverage_panel/` in worktree
    `worktrees/r2s3_lf_train_signal/B3`, forked from `round2-substrate`
    (9e10d414e35a96398f7b091bc84ddf936d88acc7). Code **vendored with
    provenance comments** from this stream's own round-2 family
    `worktrees/r2s3_lf_train_signal/B2/models_r2/r2s3_null_supply/`
    (`model.py`, `refs.py`, `lf_reference.py`, `affine_probe.py`,
    `smoke_eval.py`). This is a within-round, within-stream continuation, not
    a round-1 reuse; §5.10's rebadge question ("is this a rebadge of a round-1
    family?") answers **no** on both the forward signature and the pathway.
  - **Deletions from the vendored code** (the point of the card): the
    null-direction penalty, its ridge-affine LF law, its rung tie-break, and
    the `A2/A3/A5` arms. Remaining arms: `A0_nolf`, `A1_lf_cov`. Env keys
    `*_LAMBDA_NULL`, `*_NULL_BATCH`, `*_NULL_T`, `*_NULL_RUNG_SELECT` are
    removed, and their presence must raise.
  - **Everything else byte-preserved** so the reproduction check is meaningful:
    `NullSupplyDecoder`→`CoverageDecoder` (rename only), width 64, blocks 4,
    coord channels at forward time, FFT `norm="forward"`, mode policy
    `pinned_min_rung_nyquist` (α = min(12, min over ALL train rungs of
    floor(N_rung/2)) → 4 on ifc_poisson, 12 on all five others), per-rung
    scaler `max|y|`, step-matched budget `steps = epochs × 25` identical in
    both arms, AdamW(1e-3, wd 1e-5) + cosine + clip 1.0, HF batch 5, LF batch
    16 (LF rungs cycled deterministically), loss `MSE_HF + 1.0·MSE_LF` in
    per-rung-scaled units, `_step_rng(seed, step)` so resume is exact.
  - **N_hf = 5 protocol**: native on ifc_poisson; on the five 400-row datasets
    5 HF rows are drawn by `R2S3B3_SPLIT_SEED ∈ {0,1,2}` while the LF rungs
    keep all 400 conditions.
  - **Reference / floor splits** (never named `test*`): `ref_zero`,
    `ref_train_mean_n5`, `ref_nn_condition_n5` (in-regime), plus
    `ref_train_mean_full` / `ref_nn_condition_full` seam-checked against
    `state/anchors/floors.json` at 1e-9 **raising on mismatch**, plus
    `ref_linear_hfonly` (min-norm affine on the 5 HF rows = the HF-only
    information limit) and `ref_linear_mf` (the P2/E1 preempted linear channel,
    reported as a cited baseline, requiring the copy-LF lift convention with
    an in-job verification that raises on mismatch).
  - **Reported instruments** (never switches): per-rung affine-LOO residual at
    the rung's own resolution, `m`, rank and singular values of `[X_hf, 1]`,
    covered/uncovered condition counts, per-arm train-vs-test gap, and
    `*_preds.npz` dumps (`pred_hf_train`, `target_hf_train`, `cond_test_raw`,
    `pred_test`, `selected_train_rows`) for
    `tools/null_family_ceiling_audit.py` at analysis time.
  - **Declared baseline** (§12.3): `mf_fno_transfer_film`, **cited not re-run**
    from B1's on-disk gate run — ifc_poisson, 200 epochs, seed 0, nRMSE
    0.055637439592454, skill 1.5454844331237223, `nrmse_def_hash d3d0ade9…` /
    `copylf_def_hash 9753ff24…`
    (`…/round2/r2s3_lf_train_signal/B1/eval/result_ifc_poisson_baseline_mf_fno_transfer_film_s0.json`).
    Differences: joint step-matched HF+LF rung supervision with per-rung
    scalers and pinned modes at N_hf = 5 with LF at uncovered conditions,
    versus sequential LF-pretrain→HF-finetune with no coverage framing; and
    the card's deliverable is a matched ±LF *contrast*, not a champion.
  - **33 legs**, one SLURM job, seed 0, 200 epochs (smoke tier), except the
    guard leg at contract tier (2 epochs).
- **Recipe**: see report.md (complete JSON, transcribed verbatim by the
  starter).
- **Expected outcome** (skill units, corrected denominators, seed 0,
  `provisional-single-seed`, draw-mean over 3 draws):

  | quantity | prediction | vs threshold |
  |---|---|---|
  | ifc `A0 − A1` | +5 to +7 (best est. +5.97, B2 measured) | mce 0.9377041 → 6.4× |
  | ch `A0 − A1` (3 draws) | +12 to +18 (best est. +15) | mce 0.0912454 → ≥130× |
  | fk `A0 − A1` (3 draws) | +0.8 to +1.6 (best est. +1.2) | mce 0.0007137 → ≥1100× |
  | ac `A0 − A1` (3 draws) | +30 to +150 (best est. +70) | mce 0.8797047 → ≥34× |
  | pfc `A0 − A1` (3 draws) | +4 to +30 (best est. +12) | mce 0.2130273 → ≥19× |
  | helmholtz `A0 − A1` (3 draws) | +1 to +6 (best est. +3) | mce 2.9530 → **1.0×, the coin flip** |
  | relative effect ordering | ch ≈ ifc (0.55–0.75) > ac ≈ pfc (0.15–0.5) > helm > fk (0.07) | — |
  | panel geomean, `A1` (draw-mean) | 12–25 | anchor 23.0636; 1.5× anchor = 34.60 (cratered bound) |
  | panel geomean, `A0` (draw-mean) | 25–60 | control arm; may exceed the cratered bound — not the primary arm |

  Grounding for the extension predictions: `A0` at N_hf = 5 should sit
  1.4–2.1× above the full-400 condition→HF reference (r2s4-B1 `r2s4_cert_min`:
  ac 147.32, pfc 47.85, helm 6.94, ch 13.18, fk 11.56), which is the observed
  N_hf=5-vs-400 ratio on ch (27.36/13.18 = 2.08) and fk (16.56/11.56 = 1.43);
  `A1`, having 395 uncovered LF conditions, should recover much of that gap.
  Helmholtz is the exception in both directions: its best floor is the **zero
  field** (3.3441), so the level channel is worthless there, and its certified
  `min_claimable_effect` (2.9530) is the largest on the panel.
- **Expected falsification**:
  **F1 (primary, panel completion)** — falsified if the draw-mean effect
  `A0_nolf − A1_lf_cov` fails to be positive and to exceed the operative
  threshold `max(certified min_claimable_effect, in-job paired 3-draw spread
  of the effect)` on at least **5 of the 6** panel datasets (thresholds: ifc
  0.9377041, ch 0.0912454, fk 0.0007137, ac 0.8797047, pfc 0.2130273,
  helmholtz 2.9530).
  **F2 (structural, the discriminating clause)** — falsified if fewer than
  **2 of the 4 m = 0 datasets** (`sharp__fisher_kpp_2d`,
  `ext__helmholtz_2d`, `sharp__allen_cahn_2d`,
  `sharp__phase_field_crystal_2d`) show a relative effect
  `1 − skill(A1)/skill(A0) > 0.15` that is also above that dataset's operative
  threshold in absolute units; i.e. falsified if claimable LF value is
  confined to the two datasets with an affine coverage deficit (m > 0).
  **F3 (instrument / reproduction seam)** — falsified if any of the 8 legs
  that repeat a B2 configuration (`ifc A0`, `ifc A1`, `ch A0` draws 0/1/2,
  `ch A1` draw 0, `fk A0` draws 0/1) deviates from its B2-recorded skill by
  more than 1% relative **and** more than that dataset's certified
  `min_claimable_effect`; the card then reports B3-internal contrasts only and
  flags a code-identity break.
  **F4 (channel pre-registration)** — falsified if, on every m = 0 dataset
  with a claimable effect, the level channel accounts for ≥ 70% of the effect
  (measured post hoc from the prediction dumps with
  `tools/null_family_ceiling_audit.py`), i.e. if LF at m = 0 is only ever a
  better estimate of the mean field, as it was on fisher_kpp (76.8%).
  **F5 (floor arms — has it learned anything)** — falsified if `A1_lf_cov`
  fails to beat the best **in-regime N = 5** floor
  (`max`-skill over `nn_condition_n5`, `train_mean_n5`, `zero`) on **EACH of**
  `ifc_poisson` and `sharp__cahn_hilliard`. The frozen 400-row floors are
  seam-checked in-job at 1e-9 and reported beside every arm on all six
  datasets. Pre-registered expectation (not a claim): both arms lose the
  in-regime floor on `sharp__fisher_kpp_2d` (B2 measured 15.25/15.43 vs
  13.16/12.87) and plausibly on `sharp__phase_field_crystal_2d` and
  `sharp__allen_cahn_2d` — ADR r2-0003 makes those maps stochastic and bounds
  every deterministic arm by the conditional-mean floor.
- **Standing caveats carried on the card** (websearch instruction 7):
  helmholtz is report-only (best floor = the zero field, 3.3441); every pfc
  claim carries the band-limited-denominator caveat
  (`eval/copylf_baselines.json _notes.pfc`); ac/pfc/fk have incomplete
  condition vectors (ADR r2-0003); ifc_poisson is affine to 3.2e-08, so
  bar-level numbers there are rank recovery, not operator learning (B2 M11);
  P2 is `preempted` — the coverage result travels as a quantified neural
  instance with https://arxiv.org/html/2408.17075v1 attached, never as a
  mechanism claim.
- **Anchor reference**: `null` (program.md §4.5 — lever stream, own-stream
  anchor implicit).

## Immutables self-check (§4.5) — positive evidence, 11/11

1. **Data read-only.** The card reads `stripped_data/` through
   `score_panel.py` only; N_hf = 5 is a *subset* of the existing 400 train
   rows chosen by `np.sort(default_rng(split_seed).permutation(400)[:5])`, no
   file is written under any dataset dir, no LF is generated, and the LF used
   is the on-disk coarse consistent solve at its own rung resolution (never a
   downsampled HF).
2. **Panel + guard fixed.** Datasets are exactly the 6 panel names from
   `project.yaml` plus one contract-tier leg on `--datasets guard`
   (`heat_local`, `fluid`, `sharp__sod_1d`); no dataset is added or dropped.
3. **Eval layer / spec untouched.** The card needs no edit to `round2/eval/`,
   `project.yaml`, `program.md` or `subagents/`: all new code lives in
   `models_r2/r2s3_coverage_panel/`, and the floor/lift seam checks *read*
   `state/anchors/floors.json` and the eval-layer lift function rather than
   changing them.
4. **One nRMSE definition.** Scoring is whatever `score_panel.py` writes
   (`splits.test_hf`), and every leg must carry
   `nrmse_def_hash d3d0ade9191c13bacc40702f3eb26ad290e01641cacee22a1d2233b74c035850`
   and `copylf_def_hash 9753ff24e856f595748492dec6cb6c215d748f97e8ec4a679b651f8846da907a`
   (B2's 17 result JSONs carried exactly one hash pair; a mismatch is a
   card-level failure). The training loss (`MSE_HF + MSE_LF` in per-rung-scaled
   units) is free and is not the scored metric.
5. **Contract CLI fixed.** `smoke_eval.py` keeps the six-arg signature
   (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`); every
   knob is an `R2S3B3_*` env key listed in the recipe block and passed via
   `--env`, exactly as B2's 25-key set was.
6. **Seeds / tier epochs fixed.** Training seed is 0 only (33 legs, one job);
   epochs are 200 (smoke) except the guard leg at 2 (contract). The
   `d0/d1/d2` suffixes are HF-subset **draws**, and the card's part 5 must
   repeat B2's `seed_semantics` sentence so they are never presented as a seed
   CI.
7. **Guarded factory surfaces untouched.** Nothing under
   `mf_field/factory_mffp/{eval,baselines,references,scripts,data}`,
   `factory.md` or `akash/` is read-for-write or edited; the declared baseline
   `mf_fno_transfer_film` is **cited** from an existing round-2 result JSON
   and is not re-run or modified.
8. **Checkpoint resume.** The vendored `smoke_eval.py` already writes
   `<ckpt_dir>/last.pt` every `R2S3B3_CKPT_EVERY_STEPS=250` steps keyed by
   `(steps_target, arm, split_seed, dataset, resolved-recipe digest)` with a
   `done` flag, and sampling is `_step_rng(seed, step)` so resume is exact;
   each leg gets its own `ROUND2_EVAL_RESULTS` dir so `ckpt_dir`s cannot
   collide (B2's mechanism, preserved).
9. **Falsification thresholds exceed the noise floor** (`state/noise_floor.json`,
   `_provisional: false`): F1 uses `max(mce, in-job spread)` per dataset with
   mce ifc **0.9377041289531141**, ch **0.09124535322300886**, fk
   **0.0007136812826775696**, ac **0.8797047190126648**, pfc
   **0.21302734961699343**, helmholtz **2.95299157437233**; predicted effects
   are 6.4× / ≥130× / ≥1100× / ≥34× / ≥19× / ~1.0× those numbers respectively,
   so every clause is priced above the floor and helmholtz is explicitly
   flagged as the marginal one. F2 additionally requires the absolute effect to
   clear the same per-dataset threshold. F3 requires 1% relative **and** the
   dataset's mce.
10. **Not a pre-falsified lever.** Program.md §5's pre-falsified levers (WNO
    backbone swap, LF low-mode freezing, diffusion prior for point accuracy)
    are all absent from this design. The nearest net-negative mechanism in
    scope is B2's own null-direction penalty (anomaly M1): it is **removed
    outright**, not retuned — the card's arms are `A0_nolf` and `A1_lf_cov`
    only, the penalty code is deleted, and the deliberately-rejected A1′
    retune is documented above with B2's own numbers (alignment defect
    +0.2172, not amplitude 0.8861; ifc retune ceiling 2.6349 > A1's 2.1690).
11. **Floor arms mandatory (spec §3 / §2.2).** Every leg emits
    `ref_nn_condition_n5`, `ref_train_mean_n5`, `ref_zero` (in-regime) and
    `ref_nn_condition_full`, `ref_train_mean_full` seam-checked at 1e-9 against
    `state/anchors/floors.json` (raising on mismatch); F5 is written directly
    against the best in-regime floor on EACH of ifc_poisson and
    sharp__cahn_hilliard, and the expected-outcome table pre-registers the
    floor losses on fk/pfc/ac as a task property (ADR r2-0003), not an arm
    defect.

## Status

- Slot covered (1 of 1). Not skipped: the close-on-B2 fallback was weighed
  explicitly (see "Should there be a B3 at all?") and rejected on the four
  recorded grounds.
- Reopen candidates: none exist for this stream (all 9 cards carry
  `reopen_candidate: false`).
- B2's `open_question` (the A1′ leg) is resolved as **drop**, with reasons
  from B2's own turn-3 numbers.
- Immutables self-check: **pass (11/11)** on the first pass; no revision
  needed, so no `iteration_2.md`.
