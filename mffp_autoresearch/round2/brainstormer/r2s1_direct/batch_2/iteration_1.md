# Iteration 1 — `r2s1_direct` batch 2

## Design context considered

- `summary_so_far.md` §6 (unknowns 1–7) and the batch-2 prior-art verdict
  (`websearches/r2s1_direct/batch_2/report.md`, "Prior-art verdict" table).
- program.md §12.1 verbatim (quoted in `summary_so_far.md` §2): bar = the
  per-dataset floor table; ADR r2-0003 (condition incomplete on
  pfc/fisher_kpp/allen_cahn → conditional-mean bound, skill→1 unreachable
  there); helmholtz zero-floor column mandatory; pfc variant-C denominator
  caveat; ifc_poisson N_hf = 5 is anecdote-grade; overfitting is THE threat and
  train/val discipline is mandatory.
- The IMMUTABLES block (§4.5 of my prompt, reproduced verbatim in the
  self-check below) and program.md §5 (incl. round-2 additions 9–13: stripped
  test view, declared-reuse-only novelty, no new HF data, floor arms mandatory,
  round-1 state immutable).
- Stream anchor 23.063616857615774 (`state/anchors/r2s1_direct.json`);
  certified per-dataset `min_claimable_effect` from `state/noise_floor.json`
  (`_provisional: false`, 3-seed family `r2s4_cert_min`): helmholtz 2.9530,
  pfc 0.2130, allen_cahn 0.8797, fisher_kpp 0.00071, cahn_hilliard 0.09125,
  ifc_poisson 0.9377, panel geomean 1.1419.
- `experiment_cards/r2s1_direct/batch_1/B1.json` part 6 (T1-F2, T2-F1/F2/F5,
  T3-F5/F6/F7/F8) and part 7 (`open_question`, `next_direction` items 1–5,
  `cross_stream_notes` 1–4). These are binding context per the orchestrator.
- Cross-stream: r2s4-B1's certified floors/mce and its excluded-by-aleatoric-
  barrier datasets; r2s4-B2 (drafted) owns value-of-LF accounting, so this card
  must not duplicate it; r2s3-B1's architecture-tax finding (trained nets are
  near-affine and can put energy in the unconstrained direction with the WRONG
  sign — hf_only null-direction cosine −0.9919 while a min-norm linear solution
  puts zero there).
- Pre-falsified levers (program.md §5 / r1 §5): WNO backbone swap, LF low-mode
  freezing, diffusion prior for point accuracy — none is proposed here.

## Proposal reasoning

### What the stream is actually short of

B1 answered the stream's own question in the negative for the obvious lever:
capacity. T2-F1/T2-F2 measured a 10^5 parameter ratio producing a 0.52×-mce
difference in panel geomean, and T3-F8 showed six out-of-fold band gains erase
the decoder's per-dataset advantage on 4 of 5 measured datasets. Exactly one
cell of the panel resisted: `sharp__cahn_hilliard`, where the register turn's
full-grid calibration left a 0.5511-skill gap = 6.0× that dataset's certified
mce 0.09125. B1's part 7 names three mutually exclusive mechanisms for it and a
training-free decider. That is the single highest-information open question in
this stream, and it is cheap (B1's whole panel+guard chain: 6.95 min on one
H200).

### Alternatives weighed and rejected

1. **A new architecture (DeepONet branch–trunk / SIREN-modulated INR /
   attention decoder).** Rejected. It is buying capacity, which B1 part 7
   explicitly forbids for this stream ("Stop buying decoder capacity in this
   stream; spend B2 on IDENTIFICATION and CALIBRATION"); the batch-1 verdict
   already rated bare conditioned decoders `preempted` with "Nothing
   mechanism-level"; and T1-F2's identifiable rank of 1–3 says the ceiling is
   information, not representation — a 50-mode train basis already represents
   the TEST fields to 0.0033–0.0672. r2s3-B1's architecture tax adds that a
   trained net can actively anti-align the unconstrained directions.
2. **Ensembling / variance reduction targeted at ifc_poisson.** Rejected as a
   headline: ifc's certified mce is 0.9377 skill units against a floor of
   10.055, so almost nothing there is resolvable at N_hf = 5; §12.1 itself
   labels every ifc claim anecdote-grade. (It stays in the card only as a
   scored panel member.)
3. **Regime/class-conditional (MoE) prediction on pfc.** Rejected as the
   headline: the E4 verdict is explicitly `PROVISIONAL` — "search return only,
   not fetched" — and the websearcher says do not headline it without a
   batch-3 confirming fetch. Per-class pfc *scoring* is nevertheless adopted as
   an internal-validity reporting requirement (B1 cross-stream note 4).
4. **Identifiable-rank truncation as the contribution.** Rejected: the
   websearcher declared it "presumed prior art ... do not claim". It is used
   here as an instrument only (`tools/condition_identifiable_rank.py`).
5. **A pure diagnostic card (rank/centering sweep only, `epochs: 0`).**
   Rejected: the sweep is only decisive against a *trained, band-calibrated*
   competitor in the SAME job (B1 part 7 item 3, plus the drift-class rule that
   only in-job paired controls are controls). A model card that scores the
   selected closed form and carries the decoders as in-job reference arms gets
   both the contrast and a panel number; a diagnostic gets neither.
6. **Running the 3-seed protocol** (B1 part 7 item 4, first option). Rejected
   for the primary run: program.md §4.2 mandates "**strict 1-seed in-round**
   (seed 0 point estimates labeled `provisional-single-seed`; top-3 get seeds
   1–2 at round end)" and `project.yaml seed_protocol.seeds: [0]`; r2s4's
   3-seed cards are the §12.4 pre-directed certification exception, not a
   general licence. I take part 7 item 4's SECOND option instead — "state a
   per-dataset, per-mechanism prediction instead of a geomean one" — and add an
   in-job paired uncertainty (R = 5 fold resamples of the calibration/blend
   stage, decoder weights held fixed) so the register turn can see whether the
   cahn_hilliard contrast is resolvable. **No panel-geomean falsification leg
   appears on this card.**

### The proposal

The E3 shape, made falsifiable: a from-scratch condition→HF family whose
scored arm is chosen by a **pre-registered, training-free rule** over output
parameterizations, whose competitor set is a **four-point capacity ladder**
(10^2 → 10^3 → 10^5.6 → 10^7.2 fitted parameters) with **every arm under the
same out-of-fold Wiener band calibration and the same floor blend**, and whose
primary claim is the per-dataset localization of where capacity is worth
anything — with `sharp__cahn_hilliard`'s open cell decided by a rank ×
centering sweep. The Wiener stage is shipped as *named machinery* with the
citation, never as the claimed contribution (websearcher item 1); the rank
statistic is an instrument (item 4); the DC-only ridge joins the blend base set
(B1 part 7 item 2).

Why this is not a rebadge of B1: B1's scored arm was a 14–16 M-parameter
trained decoder with a fixed, architecture-imposed factorization; here the
scored arm is a ~10^2-parameter closed-form spectral head whose *form* is
selected from train-split statistics before any candidate is trained, and the
decoders appear only as declared in-round baseline arms. Forward signature,
fitting procedure and family are new; no round-1 code is vendored (§5.10 does
not apply — no round-1 family is present in any role).

### Concrete config

New family `models_r2/r2s1_selected_form` (worktree
`worktrees/r2s1_direct/B2`, branch `round2/exp-r2s1_direct-B2`), condition-only
forward signature, stripped view only, leakage tripwire.

Per dataset, per seed:

1. **Folds.** Train split → fit 80% / model-selection 10% / calibration 10%,
   disjoint, seeded, asserted disjoint. `N_train < 20` (ifc_poisson, N = 5) →
   leave-one-out, fixed-epoch, no early stop. No test quantity is consulted at
   any fitting or selection step (round-1 D3 `val_idx` double-consumption
   caveat).
2. **Stage S — training-free selection** (fit+selection folds only, written to
   the diagnostic JSON *before* any test scoring):
   - centering: `ratio = ||mean_i y_i|| / geomean_i ||y_i||`;
     `ratio >= CENTER_TAU (1.0)` → `fact` (unit-L2 direction ×
     `exp(mean log||y||)` centering), else `add` (plain mean-centred). The
     threshold is pre-registered from B1's three measured ratios (helmholtz
     4.210, cahn_hilliard 0.052, allen_cahn 0.024) and is itself under test
     (leg L4).
   - rank: `r_ident` = number of POD modes (basis from the fit fold, 50 modes
     retained) whose coefficient has 5-fold out-of-fold R² > `RANK_TAU (0.1)`
     from the condition under ridge; `r_sel = clip(r_ident, 1, 32)`.
3. **Head.** Ridge from `[1, standardized condition]` to the `r_sel` POD
   coefficients (params `(d+1) * r_sel`: 60 on cahn_hilliard's 19-dim
   condition, 12 on pfc), ridge alpha by exact LOO over a 13-point log grid on
   the fit fold.
4. **Wiener band gains.** Six radial Fourier bands, one scalar gain each,
   fitted by coordinate descent (41-point grid on [0, 2], 2 passes) on the
   *calibration* fold and applied to the test prediction. Declared in code and
   `INSPIRATION.md` as the empirical non-causal Wiener gain `H_nc = S_hy/S_yy`
   restricted to radial bands, citing the verdict's sources. Grid widened from
   B1's [0, 1.5] because B1's cahn_hilliard optimum sat ON the 1.5 edge.
   Applied identically to EVERY arm (B1 cross-stream note 2).
5. **Blend.** `lambda * arm + (1 - lambda) * base`, 21-point grid, bases
   {zero, train_mean, nn_condition, **dc_only**}, both chosen on the
   calibration fold.
6. **Arms.** Scored `test_hf` = selected form. Reference splits (none may start
   with `test` — B1's `_extract_test_metric` lesson): `ref_selrule_alt` (the
   non-selected centering at `r_sel`), `ref_rank_{1,2,3,5,8,12,20,32}`,
   `ref_head_rff16` (~10^3 params), `ref_decoder_small` (w32/b2/modes16,
   ~10^5.6), `ref_decoder_big` (w64/b4/modes16/latent16, B1 scale, ~10^7.2),
   `ref_raw_head` and `ref_raw_decoder_big` (uncalibrated twins),
   `ref_dc_only`, `ref_zero`, `ref_train_mean`, `ref_nn_condition` (the three
   frozen floors seam-checked to `state/anchors/floors.json` at 1e-9, raising
   on mismatch). Decoders early-stop on the model-selection fold (B1's
   best_epoch 2–24/200 anomaly) — a fair, not a starved, competitor.
7. **Diagnostics** (JSON, non-scored): the selection statistics and the chosen
   form; the full rank × centering test curve with the oracle-rank number
   explicitly labelled ORACLE; the calibrated↔uncalibrated delta per arm; the
   R = 5 fold-resample paired spread of (scored arm − `ref_decoder_big`) per
   dataset; per-class pfc scoring (patterned/unpatterned) using a
   condition-only classifier fitted on the train split.
8. Guards `heat_local, fluid, sharp__sod_1d` at contract tier (2 epochs).

## Proposal

- **Category**: `gap / identification-vs-capacity localization — pre-registered
  training-free selection of a closed-form condition→HF head, Wiener-calibrated
  capacity ladder`
- **Card type**: `model`
- **Motivation**: quotes the E3 verdict row (see report.md).
- **Concrete config**: as above.
- **Recipe**: see `report.md` (complete JSON).
- **Expected outcome**: scored-arm skill helmholtz 3.10 (report-only, zero-floor
  column 3.3441), pfc 46–53 (variant-C caveat), allen_cahn 175–200, fisher_kpp
  11.50–11.60, cahn_hilliard 12.8–13.4, ifc_poisson 9.5–10.0; panel geomean
  ~18.5 vs anchor 23.0636 (−20%), reported but carrying no falsification
  weight, and NOT claimable as an improvement over B1's 19.6444 (the ~1.1-unit
  difference is at the panel mce 1.1419).
- **Expected falsification**: four per-dataset legs, L1–L4 (see report.md);
  every threshold exceeds its dataset's certified mce.
- **Anchor reference**: `null` (program.md §4.5 — all four round-2 streams;
  own-stream anchor implicit).

## Status

- Slot covered: yes (one model card).
- Skipped: no.
- Reopen candidates resolved: none exist (B1 `reopen_candidate: false`; batch-1
  brainstormer report line 211 records none).
- Immutables self-check: **pass (11/11)** — see below.

## Immutables self-check (positive evidence for each)

1. **Data read-only.** The family reads the stripped view through
   `score_panel.py` only; it fits on the existing 400 aligned train samples
   (5 on ifc_poisson) and generates nothing — the recipe has no generation knob
   and `datasets: "panel"` is the frozen panel string B1 used.
2. **Panel + guard fixed.** `datasets: "panel"` and the guard leg names exactly
   `heat_local, fluid, sharp__sod_1d` from `project.yaml guard_set` — no
   dataset is added, dropped, or re-weighted.
3. **Eval layer / spec untouched.** Every artefact lives under
   `models_r2/r2s1_selected_form` in the B2 worktree; the scored number is
   produced by the unmodified `round2/eval/score_panel.py` invocation of §9,
   and the design needs no change to `round2/eval/`, `project.yaml`,
   `program.md` or `subagents/`.
4. **One nRMSE definition.** The scored quantity is the per-sample relative L2
   emitted for `test_hf` and consumed by `score_panel.py`; the family imports
   `round2/eval/nrmse.py` rather than re-implementing it (B1's reviewer Q3
   SUGGEST, adopted here as a build requirement). Wiener gains and blends are
   *training/calibration-side* objects fitted on train-side folds — the scored
   metric is untouched.
5. **Contract CLI fixed.** `smoke_eval.py` keeps the six-argument signature
   (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`); every
   knob introduced above appears in `recipe.env` and is passed only through
   `score_panel.py --env`.
6. **Seeds and tier epochs.** `seeds: [0]` matches `project.yaml
   seed_protocol.seeds` and program.md §4.2's strict-1-seed in-round rule;
   `epochs: 200` is the smoke tier; the guard leg is `epochs: 2` = contract
   tier; no full-tier (2500) run is requested. Alternative 3 in the rejected
   list records why 3 seeds were declined.
7. **Guarded factory surfaces untouched.** The only factory contact is a
   read-only import of `mf_field/factory_mffp/data_adapters/loaders.py` (the
   same contact B1's build notes record); nothing under
   `factory_mffp/{eval,baselines,references,scripts,data}`, `factory.md` or
   `akash/` is written.
8. **Checkpoint resume.** Both decoder arms train through a loop that writes
   `<ckpt_dir>/last.pt` atomically with a meta block (model/dataset/seed/epochs)
   and resumes from it; the closed-form arms are re-derived deterministically
   from the same checkpoint file's stored fold indices and fitted coefficients,
   so a preempted job resumes rather than restarts — the same structure B1
   verified empirically in `scratchpad/test_resume.log`.
9. **Falsification thresholds exceed the noise floor**, per dataset, quoting
   `state/noise_floor.json`: L1 uses each dataset's own certified
   `min_claimable_effect` as the loss margin (pfc 0.21302735, allen_cahn
   0.87970472, fisher_kpp 0.00071368, cahn_hilliard 0.09124535, ifc_poisson
   0.93770413); L2 uses 3× cahn_hilliard's mce = **0.27374** skill units
   against a measured B1 gap of 0.5511 (6.0× mce); L3's margins are 15.3 (pfc),
   99.7 (allen_cahn), 1.03 (fisher_kpp), 11.2 (cahn_hilliard) and 1.76
   (ifc_poisson, threshold set at 1.15× rather than 1.05× precisely so the
   margin 1.76 exceeds its mce 0.9377); L4 uses each dataset's own mce.
   `ext__helmholtz_2d` carries NO falsification weight because its certified
   mce is 2.9530 against a floor of 3.3441 — report-only with the zero-floor
   column, per §12.1's helmholtz lesson.
10. **Not a pre-falsified lever.** Nearest is round 1's "LF low-mode freezing";
    this card freezes nothing, uses no LF at any stage (train or test), and its
    band stage is a *fitted out-of-fold gain per radial band on the HF-side
    prediction*, not a fidelity-selective mode transfer. The WNO backbone swap
    is not proposed (no wavelet backbone anywhere) and no diffusion prior
    appears. Within round 2, the nearest prior art is B1's own band-gain probe,
    which is why the stage is declared as machinery with the Wiener citation
    rather than as a contribution.
11. **Floor arms in the falsification reasoning.** `ref_zero`,
    `ref_train_mean`, `ref_nn_condition` are recomputed in-job and asserted
    equal to `state/anchors/floors.json` within 1e-9; leg L3 is stated
    *entirely* in units of the best frozen floor per dataset (1.05× / 1.15×),
    and `ref_dc_only` — B1's 35-parameter constant-field ridge — is added both
    as a reported floor and as a blend base, so an arm that only regresses the
    mean level is visible as such.
