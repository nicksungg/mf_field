# Iteration 1 — `r2s2_stacked` B3 design

## Design context considered

- `summary_so_far.md` §6 (the six unknowns), especially (1) the unreplicated allen_cahn CNN
  increment and (2) the never-swapped base.
- The batch-3 prior-art verdict, all three rows, plus the websearcher's five "for the brainstormer"
  instructions — in particular #5: *"design it so that this negative is identifiable per dataset
  (LSI-only arm, LSI+CNN arm, same folds, same k*), because that contrast is the stream's only
  publishable content"*.
- **The immutables block (§4.5 of my prompt / program.md §5) verbatim**, both the round-1 eight and
  round-2's additions 9–13 (stripped test view; declared-reuse-only; no new HF data; floor arms
  mandatory; round-1 state immutable).
- Stream anchor `state/anchors/r2s2_stacked.json` = **23.063616857615774**
  (`best_floor_panel_geomean`, `provisional: false`), per-dataset floors: helmholtz 3.3441 (zero),
  pfc 59.8118 (train_mean), allen_cahn 269.1959 (nn_condition), fisher_kpp 11.9931 (train_mean),
  cahn_hilliard 23.1803 (nn_condition), ifc_poisson 10.0549 (nn_condition).
- `state/noise_floor.json` (`_provisional: false`, source r2s4_diag-B1 3-seed condition→HF spread),
  certified `min_claimable_effect`: helmholtz **2.9529916**, pfc **0.2130273**, allen_cahn
  **0.8797047**, fisher_kpp **0.0007137**, cahn_hilliard **0.0912454**, ifc_poisson **0.9377041**,
  panel geomean **1.1418668**.
- Pre-falsified levers (r1 program §5): WNO backbone swap, LF low-mode freezing, diffusion prior for
  point accuracy. Plus the round-2 in-stream retraction: B1's coherence **eligibility gate**
  (STOP-EXPORT, B2 part 7 cross-stream note 1) and B2's ladder rule (iv).
- ADR r2-0004: registration-of-lifts (reviewer FAIL if violated) and target-scaler pre-flight on
  helmholtz/pfc; the unified per-sample normalisation eligibility rule.
- Measured timing envelope this round: r2s3-B3 33 legs / 55 min, r2s4-B3 36 legs / 92 min (h200);
  r2s2-B2 itself 33.58 min panel + 2.4 min guard with 36 in-job corrector trainings.

## Proposal reasoning

### Step 1 — B3 or close?

The task poses B3-or-close and the websearcher's direction (iii) is `preempted` as a framing. I
choose **B3, scored**, on five grounds, each traceable:

1. **The stream's only surviving nonlinear evidence is one number, at one fold seed, one fit.** B2's
   own part 7 names this as *the* open question and it cannot be resolved by desk analysis: it needs
   the corrector refit under re-drawn folds. Closing now would export "the class is a closed-form
   filter" on evidence B2 itself flags as *"the number most exposed to fit noise"*.
2. **Direction (iii)'s export requires an artefact + measurement, not an idea.** The websearcher is
   explicit: *"If you close the stream, the deliverable is the numbers in skill units with the
   certified mce alongside, per dataset."* Those numbers do not exist: B2's 19.3868 is a *diagnostic*
   card's arm that includes a CNN and a blend stage. There is no scored zero-gradient model arm in
   this round.
3. **The publishable negative is only identifiable if B3 is scored** — the websearcher's instruction
   #5, verbatim. Two independent refutation terms found no MF/PDE paper reporting a switched-off
   learned corrector while a closed-form stage carries the gain.
4. **The nearest prior art can only be differentiated by running it.** Operator Boosting's recipe
   (cheap base + trained residual stages + validation-selected shrinkage) has never been run on this
   panel. Swapping the base from the LF-retrieval intermediate to a training-free floor, at matched
   folds/budget/shrinkage, turns the near-miss into an in-job control — and is simultaneously a
   matched ±LF contrast at equal corrector budget, i.e. §12.2's own falsification framing measured
   in-job rather than by comparing single-seed cards across streams.
5. **Cost is inside the envelope.** ~60 corrector trainings vs B2's 36, minus B2's permutation
   nulls, conditioners and 15-rung ladder: estimate 60–80 min, between r2s3-B3's 55 and r2s4-B3's 92.

Counter-argument weighed and rejected: "B2 already answered it; a second run risks another
instrument-defect card." B2's three fired clauses were all *statistic* defects, and the fix is
structural — this design has no coherence statistic, no permutation null, no scale-free estimator,
no endpoint-only comparison and no LOO-on-train/no-self-on-test rung. Every clause is a paired
difference of two scored nRMSEs on the same held-out fold, converted to skill and compared to a
certified mce. That is the narrowest instrument the round has.

### Step 2 — Which experiment?

Alternatives weighed:

- **(A) Realisation-aware stage 1 (B1 part 7 option A, generative).** Rejected again, same grounds
  B2's brainstormer recorded: the stripped view exposes only the condition, so no admissible stage 1
  conditions on anything E[LF|c] lacks; measured ceiling ~1.6 skill units against a ~19 geomean.
  Nothing in batch 3 changes this and the websearcher found no new mechanism.
- **(B) Re-run B2's full ladder with the centred/affine and σ(c)-null repairs.** Rejected: the
  repairs are already *measured and exported* (B2 turn 1/turn 2); re-running them buys a confirmed
  instrument, not a claim, and B2's part 7 explicitly says price stage eligibility in skill units
  instead of rebuilding the gate.
- **(C) A trained pseudo-LF emulator front end again (B1's design) with the k-NN intermediate as
  control.** Rejected: B1 measured the emulator's conditional-mean collapse and I8 settled the
  representation question; re-proposing it is the rebadge the reviewer checks for.
- **(D) CHOSEN — a scored zero-gradient panel arm with a pre-registered, per-dataset,
  fold/train-seed-paired stage-attribution and a base-swap control.** This is the intersection of
  the only open verdict row (i), the only unpublished content (the negative), the export direction
  (iii) needs, and B2's own next_direction items (i)+(ii)+(iii)+(iv).

### Step 3 — Concrete design decisions and why

- **Four arms, all on identical folds and the identical `k*`** (the websearcher's "same folds, same
  k*"):
  - `ref_retrieval_raw` (A0) — the intermediate itself, 0 parameters.
  - **`test_hf` (A1, SCORED)** — A0 → one closed-form LSI Wiener filter `T(k)` fitted on the fit
    fold, mixing coefficient `alpha_lsi` selected out-of-fold on calib **including 0**. Zero
    gradient steps. This is the arm the panel geomean is computed from.
  - `ref_lsi_cnn` (A2) — A1 → gated `LocalCorrector` (kernel 7, depth 4, width 32, zero-init head),
    2000 steps, shrinkage `alpha_nn` selected out-of-fold on calib **including 0**.
  - `ref_base_lsi_cnn` (A3) — the **Operator-Boosting analog / matched no-LF control**: the same
    LSI+CNN pipeline at the same folds, budget and shrinkage grids, but starting from the best
    training-free base selected on calib from `state/anchors/floors.json`
    (`zero` / `train_mean` / `nn_condition`) instead of the LF-retrieval intermediate. Because
    `alpha_lsi = 0` is in the grid, the *literal* Operator Boosting recipe (cheap base + trained
    stage + validation-selected shrinkage, no closed-form stage) is a reachable special case and is
    recorded per cell as `alpha_lsi_star == 0`.
  A0..A3 is the 2x2 {LF-retrieval intermediate, no-LF base} x {closed-form only, closed-form +
  trained} minus the one cell (base, closed-form-only) that is degenerate for the constant bases.
- **No blend stage on the scored arm.** B2 measured `lambda* = 1.0` on 3/4 sharp datasets (blend
  contributes exactly 0.000000) and r2s1-B2/B3 independently traced the blend stage to an
  error-decorrelation evaluation artefact. Keeping it would re-import the round's known
  post-hoc-stage instrument-error class into the scored column. The floors are still *reported* as
  mandatory arms (F4) — they are simply not blended into the score.
- **Five in-job fold/train seeds `0,1,2,3,4`, one SLURM seed.** Program §4.2 fixes strict 1-seed
  in-round (seeds 1–2 only at the end-of-round top-3 confirmation), and 2510.26714 says extra
  downstream seeds cannot substitute for training-seed variation. Each fold seed **re-draws the
  fit/calib/eval partition AND re-initialises the corrector AND re-shuffles its batches**, so the
  paired A1−A2 delta is measured across five genuinely independent train draws — strictly stronger
  than two extra SLURM seeds over a fixed fold split. This follows the r2s4-B3 and r2s3-B3 precedent
  (strict-1-seed argued via in-job paired fold deltas).
- **k grid `1,2,4,8,16,32,64,128` — `all` deliberately absent** (B2 part 7 rule (iv): never build a
  rung that is LOO on train and no-self on test). Selection: minimum held-out **calib** nRMSE of the
  raw intermediate, per fold seed, LOO on train rows. Two tripwires: (a) `k*` and its calib curve
  recorded for all 5 fold seeds (answers B2 reviewer carry-forward 2 with a measurement rather than
  a proxy); (b) assert the per-row fluctuation-energy ratio train-vs-test at `k*` exceeds 0.1 —
  the direct detector for B2's `B:all` defect class.
- **No coherence statistic anywhere.** STOP-EXPORT is honoured: centred gamma is computed and
  reported as a *directional* descriptor only, never as a gate, and every threshold in this card is
  already stated in skill units against the certified mce, so
  `tools/relative_gain_units_audit.py` is run on the arms table as a reporting instrument, not a
  decision rule.
- **`tools/zero_gradient_stage_ladder.py`** (B2-promoted) is the in-job attribution instrument,
  adapted to consume the four-arm table; it already emits attribution in percent AND in skill units
  against the certified mce, which is exactly the claim unit direction (iii) requires.
- **Pre-flights (ADR r2-0004 + the unified rule)**: `tools/target_scale_spread_audit.py` on
  `ext__helmholtz_2d` and `sharp__phase_field_crystal_2d`; `tools/persample_norm_eligibility.py` on
  the corrector's residual target for all six. An `OUTLIER_DOMINATED` or `NEAR_ZERO_TARGETS` verdict
  switches that dataset's corrector target to per-sample normalisation; verdicts recorded on the
  card either way.
- **Registration**: `upsample.py` vendored from `worktrees/r2s2_stacked/B2/models_r2/
  r2s2_correctability` @ `bd54bcb` (per-dataset `node_aligned_periodic` / `dirichlet_node` /
  `legacy_cell_centred`), with the existing 1e-9 read-only seam assert against
  `round2/eval/panel_data.py` on the TRAIN split. No bare `F.interpolate`/`zoom` anywhere.
- **Report-only / low-n discipline**: `ext__helmholtz_2d` report-only with the zero-floor column
  (§2.3 + ADR r2-0004 exact-solve caveat), carries no falsification weight; `ifc_poisson` LOO,
  `low_n` flagged, excluded from clause counting (N_hf = 5, and B1/B2's unpaired-rung caveat
  stands); pfc claims carry the band-limited denominator caveat. Decidable set for every clause =
  the four sharp datasets pfc / allen_cahn / fisher_kpp / cahn_hilliard.
- **Guard leg** at contract tier (2 epochs) on `heat_local`, `fluid`, `sharp__sod_1d`, as B2 ran it.

### Step 4 — Predicted numbers (derivation)

From B2's measured attribution (T3/F3.3, skill units CNN + blend: allen_cahn 9.443 + 3.540,
cahn_hilliard 0.081 + 0, fisher_kpp 0.019 + 0, pfc 0.000 + 0), removing the CNN and blend stages
from B2's scored per-dataset skills [4.2465, 48.4515, 170.0842, 11.5725, 15.5067, 8.4546] gives
A1 ~ [4.25, 48.45, 183.07, 11.59, 15.59, 8.45] and a panel geomean of **19.65** (recomputed:
19.6485), i.e. **Δ = −3.42 vs the 23.0636 anchor = 2.99x the certified panel mce 1.1418668**. Band
19.2–20.7 over the helmholtz/ifc uncertainty (those two arms change shape when the blend is dropped).

## Proposal

- **Category**: `zero_gradient_stage_attribution` / scored retrieval→closed-form panel arm with a
  fold-seed-paired learned-stage decision and a matched no-LF base-swap control.
- **Card type**: `model` (a scored `test_hf` panel arm; floor arms mandatory).
- **Motivation** (quotes the prior-art verdict): direction (i) is
  `preempted-but-MF-composition-open (cite)` — *"No fetched source composes retrieval intermediate →
  one fitted LSI Fourier-diagonal transfer as a multi-fidelity corrector, scores it under a
  copy-LF-skill denominator with no LF at test, or reports the attribution (closed-form stage carries
  33-100 % of a trained stack's out-of-fold gain; learned stage switched off on 5/8 cells). Claim the
  composition + attribution, never the filter"*; direction (ii) is `preempted (cite)` as a method —
  *"Nothing methodological is open — only the answer on this panel"* — with the two inherited
  constraints (vary the fold/train seed per https://arxiv.org/abs/2510.26714; decide against the
  certified `min_claimable_effect`, not a paired p-value, per https://arxiv.org/abs/2511.19794).
  Closest prior art **Operator Boosting** (https://arxiv.org/abs/2606.17460): its base is the
  empirical mean predictor and every stage is trained; here the base is an LF-retrieval intermediate
  and the winning stage is closed-form — and A3 runs their recipe as the in-job control.
- **Concrete config**: new family `models_r2/r2s2_zerograd`, vendored with provenance comments from
  `worktrees/r2s2_stacked/B2/models_r2/r2s2_correctability` @ `bd54bcb`
  (`lsi_filter.py`, `local_corrector.py`, `bands.py`, `periodicity.py`, `upsample.py`, `floors.py`,
  `folds.py`), condition-only at test, stripped view only, tripwire
  `R2S2B3_REQUIRE_NO_TEST_LF=1`. Folds 0.70 fit / 0.15 calib / 0.15 eval, disjointness asserted, LOO
  below `R2S2B3_LOO_MIN_N=20`. Arms A0–A3 as above at 5 fold/train seeds x 6 panel datasets = 120
  legs (60 of them corrector trainings at 2000 steps). Scored column = A1 at fold seed 0; A1 at fold
  seeds 1–4 reported as `ref_a1_fs{1..4}`. Reference-split names never begin with `test`.
- **Recipe**: see report.md (complete JSON).
- **Expected outcome**: scored A1 panel geomean **19.65** (band 19.2–20.7), Δ = −3.42 vs anchor
  23.0636 = **2.99x** the certified panel mce 1.1418668. Per dataset A1 beats its best training-free
  floor by 11.36 (pfc, 53x mce) / 86.13 (allen_cahn, 98x) / 0.40 (fisher_kpp, 563x) / 7.59
  (cahn_hilliard, 83x) / 1.60 (ifc_poisson, 1.7x, low-n) skill units, and loses to the zero floor on
  helmholtz by 0.90 (0.31x its 2.9530 mce — unresolvable, report-only). The learned stage's paired
  increment A1−A2 is predicted to fall **below 2x allen_cahn's mce (1.7594)** with inconsistent sign
  across the 5 fold seeds, and to stay at 0.00–0.10 skill units on pfc/cahn_hilliard/fisher_kpp. The
  no-LF control A3 is predicted to lose to A2 by tens of skill units on allen_cahn/pfc/cahn_hilliard
  (its starting floors are 269.2 / 59.8 / 23.2) — the LF-retrieval intermediate, not the stagewise
  recipe, is what carries the class.
- **Expected falsification**: see report.md (one sentence, four clauses F1–F4, every threshold in
  certified mce units).
- **Anchor reference**: `null` (program.md §4.5 — all four round-2 streams; own-stream anchor
  23.0636 implicit).

## Status

- Slot covered: yes — one `model` card proposal, complete recipe, four mce-denominated clauses.
- Skipped: no. Close-on-B2 considered and rejected on five recorded grounds (Step 1).
- Reopen candidates resolved: none exist round-wide (verified by reading both stream cards'
  `reopen_candidate` fields, both `false`).
- Immutables self-check: **pass (11/11)** — see report.md; performed after this design, no revision
  required, so no `iteration_2.md`.
