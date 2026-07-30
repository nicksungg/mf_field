# Iteration 1 — s5_tuning batch 3

## Design context considered

- `summary_so_far.md` §6 (8 unknowns) and the E1–E4b prior-art verdicts.
- The §4.5 immutables block verbatim (reproduced in the self-check below).
- Anchor `state/anchors/s5_tuning.json` = panel geomean 6.703016 (batch 0,
  `mf_fno_transfer_film`); §4.5 policy for s5 batches >= 2 => `anchor_reference` is the
  current champion CARD, `s5_tuning-B2`.
- `state/noise_floor.json` `min_claimable_effect`: ext__helmholtz_2d **9.694961**,
  ifc_poisson **0.239908**, sharp__cahn_hilliard **0.553347**, sharp__fisher_kpp_2d
  **0.417735**, sharp__phase_field_crystal_2d 1.151100, sharp__allen_cahn_2d 1.633407;
  geomean floor 0.884. Batch-0 seed spreads: cahn_hilliard 0.191827, fisher_kpp 0.091789.
- §5 pre-falsified levers: WNO backbone swap, LF low-mode freezing (`mf_fno_spectral`),
  diffusion prior. None is touched (see self-check item 10).
- Orchestrator coordinated-twin decision (2026-07-30T12:15Z): s5-B3 owns RAW-target /
  LF-blind substrate, champion-family lineage; shared arm grammar with s2-B3; disjoint knob
  namespace (`MFFP_*`).

## Proposal reasoning

### Step 1 — what the pre-scope asks for, and the one fact that breaks part of it

The mechanism analyst's pre-scope is: (a) run arm A3 `revin_lf` at 200 epochs; (b) an LF-free
per-sample arm, ORACLE-labelled per E2; (c) a SCALER_INERT control dataset; (d) eligibility
`G >= 8 AND live pattern`; (e) per-batch grad-norm/clip-rate logging for H3; (f) headline
diagnostic = effective N of the REALIZED per-batch loss.

I HONOR (a)–(f) and EXPLICITLY IMPROVE (a)+(c), because of a substrate fact I verified in the
data and in B2's own pre-check rather than assuming:

`worktrees/s5_tuning/B2/notes/precheck_scale_ratio.json` -> `ifc_poisson.revin_lf_available =
false`, with `n_hf = 5`, `n_lf = 100`, `train_lf_hf_row_aligned = false`, `test_ships_lf =
false`. Confirmed against the raw data: `data/ifc_poisson/train/fidelity_{8,16,32,64}/Xs.npy`
have shapes (100,5)/(50,5)/(20,5)/(5,5) and `test/` ships `fidelity_64` only; `Xs` is a
5-dim CONDITION VECTOR, not a field. `smoke_eval.py::_lf_per_sample_scales` therefore returns
`None` on ifc_poisson and the arm falls back to a global scaler.

**Consequence**: `revin_lf` is a no-op on ifc_poisson by construction, and (from the same
pre-check) `hf_lf_ratio_cv <= 0.0173` on all four sharp sets makes it ~ a global `maxabs`
there. Its only per-sample content on the whole panel is `ext__helmholtz_2d`
(cv 0.689, p95/p5 1.744). So a `revin_lf` card CANNOT put a claimable numeric leg on
ifc_poisson, and helmholtz admits no numeric claim at all (see step 3). The orchestrator's
"PRIMARY leg on ifc_poisson" must therefore be carried by a different arm — the ORACLE — and
I say so explicitly rather than shipping a card whose primary leg is a silent fallback.

### Step 2 — the ifc_poisson bar, checked against the anchor file myself

- s5-B2 arm A2 (zscore) ifc_poisson skill **1.185106** (nRMSE 0.042664; reference_type
  `paper_bar` 0.036, ADR 0002).
- `min_claimable_effect` 0.239908.
- Orchestrator's proposed bar: `1.185106 - 0.239908 = 0.945198`. **Confirmed.** I harden it
  to **skill <= 0.945** so the implied improvement (0.240106) STRICTLY exceeds the floor
  (0.239908) — 1.0008x floor — because §4.5 requires the threshold to *exceed* the floor,
  and "equal to" is not "exceeds". In nRMSE: **<= 0.034020**.
- Against the certified batch-0 anchor 1.565633 the equivalent bar is **<= 1.325527**.
- Note what the bar means physically: skill < 1 on ifc_poisson IS success criterion 1
  (beating the published paper bar 0.036). A NEW s5 claim there is therefore, arithmetically,
  a paper-bar claim.

Is that reachable? One-sided evidence says probably not: s1_poisson-B3 part 7 note (2)
measured that a per-sample gain oracle applied to THIS zscore arm is worth
0.042664 -> 0.039985 = 0.0027 nRMSE = **0.31x the floor**. That bounds the *amplitude*
channel, not a *trained* per-sample normalization — which is exactly why the oracle arm is
worth running: it is the only thing that can settle whether training in per-sample space
changes the learned function rather than just its gain.

### Step 3 — helmholtz is arithmetically unclaimable, and I state the arithmetic

A0's helmholtz skill is 5.766462; the floor is 9.694961; `5.766462 - 9.694961 = -3.928500`.
Since skill >= 0, **no attainable helmholtz value can clear its own floor**. Helmholtz is
REPORT-ONLY, not by convention but by arithmetic. Everything helmholtz contributes to this
card is therefore a DIAGNOSTIC (effective N, clip rate, displacement), not a score.

### Step 4 — alternatives weighed and rejected

1. **Per-sample-normalized MSE loss (relative loss), no test-time scale needed.** Rejected:
   `s7_loss-B2` is running `MFFP_S7_LOSS=rel` on the SAME champion family right now
   (`experiment_cards/s7_loss/batch_2/B2.json`, `reviewed_pass`, job 66064289). Duplication.
   It is also loss-as-mechanism, which §12.5 forbids in s5. It becomes the card's comparator
   instead: s7 isolates the WEIGHTING half, s5's A1 is WEIGHTING + PLACEMENT.
2. **A closed-form condition-vector scale law for ifc_poisson** (`s_i = exp(c0 + c^T X_i)`,
   least squares on the 5 HF rows). Rejected twice: it is `s1_poisson-B3`'s gain-law
   mechanism (direct double-count, and s1-B3 part 7 note (2) already prices porting it to
   this family at 0.31x floor), and a fitted law is a mechanism, not a knob (§12.5).
3. **Nearest-neighbour LF retrieval to synthesize a per-sample scale on ifc_poisson**
   (level-8 pool covers the test conditions at scaled NN distance 1.007, s1-B3 T3-F3).
   Rejected: a retrieval-keyed scale is a new mechanism (§12.5), and the websearcher never
   searched it, so it would ship without a prior-art verdict.
4. **Train per-sample, denormalize with the global constant at test** (the "train-space
   benefit without test-time statistics" reading of 2603.11869). Rejected as a PROMOTABLE
   arm: the network learns `y_i/s_i` and multiplying by one constant mis-scales every sample
   by `c/s_i`, i.e. it is miscalibrated by construction. Retained only as the oracle arm's
   legal `splits.test` readout, pre-registered to be WORSE than A0 — which is itself the
   measurement E2 asks for ("the arm is unusable without a per-sample test scale").
5. **Running the full 6-dataset panel.** Rejected on cost + information: B2 closed sharp-2D
   for normalization at high confidence, and pfc/allen_cahn occupy the redundant
   (low-G, dead-pattern) cell of the eligibility 2x2 while costing 680 s/arm. Cost saved
   ~34 min. Consequence accepted and stated: **no panel geomean for this card**, no
   panel-level claim; all comparisons are per-dataset against the paired in-job A0.
6. **A `maxabs` re-run as the control.** Rejected: B2's promoted `zscore` IS the current
   champion recipe and §4.5 makes B2 the anchor card; s5-B1's H100 same-hardware maxabs
   numbers already exist and serve as the SECONDARY basis for free.
7. **A screen-only no-floor variant** (the s2-B3 shape). Not needed in that direction: B2's
   `scalers.py:186` already floors per-sample denominators at `FLOOR = 1e-8`. The open
   question here is the OPPOSITE — whether a *stronger* (q25) floor is needed per s7-B1 M6.
   So the screen variant is `revin_lf_floorq25`, and it doubles as ADR-0007's second
   promotable candidate (otherwise the promotable set would be a singleton).

### Step 5 — dataset selection (the eligibility 2x2)

| cell | dataset | G | pattern verdict | role |
|---|---|---|---|---|
| high G, live pattern | `ext__helmholtz_2d` | 39.47 | WEAK_PATTERN 0.402 | diagnostics host (report-only) |
| high G, live pattern | `ifc_poisson` | 9.858 | REAL_PATTERN 0.994 | PRIMARY numeric leg (oracle) |
| low G, live pattern | `sharp__cahn_hilliard` | 1.322 | REAL_PATTERN 0.735 | control: pattern WITHOUT G |
| mid G, dead pattern | `sharp__fisher_kpp_2d` | 5.997 (1.55 x 3.88) | LEVEL_ONLY 0.0024 | control: G WITHOUT pattern |

These are exactly B2's F7 cells. pfc and allen_cahn are the redundant (neither) cell.

### Step 6 — cost

B2 measured `train_seconds` per dataset at 200 ep on H100: helmholtz 180.85, ifc_poisson
35.61, cahn_hilliard 491.63, fisher_kpp 496.32 => **1204.4 s per 4-dataset arm**.
Three 4-dataset arms (A0, A1, A4) + two 2-dataset clip arms (A2, A3, helmholtz+ifc_poisson =
216.5 s each) = **4046 s = 67.4 min** train; B2's wall/train overhead was +2% => ~69 min.
Matches the orchestrator's ~70 min budget. `--time=03:00:00`.

## Proposal

**Category**: `tuning_persample_target_scaler` — per-sample output-target scaling on the
LF-blind champion lineage, with clip-attribution and effective-N instrumentation.

**Card type**: `model`.

**Motivation** (quotes the prior-art verdict, E1 row, verbatim): **preempted-but-MF-
composition-open** — *"a parameter-free wrapper that normalizes the input, applies any
backbone, and denormalizes the output. We prove every NE function admits this
factorization"* (https://arxiv.org/abs/2605.08193), already inside PDE surrogates
(*"use these statistics to exactly denormalize model outputs"*,
https://arxiv.org/html/2509.21670v3); what is unoccupied is *"(i) the statistic comes from a
**different fidelity's field**, not the sample's own target — unretrieved anywhere;
(ii) applied to a **raw** (non-residual) target, which is the complement of s2-B3's D1;
(iii) as a **scaler-only knob**, zero new parameters, inside a few-HF-sample MF recipe ...
(iv) **WNE's guarantee does not transfer**: in denoising input and target share a space,
across a fidelity boundary they do not, so `max|LF_i|`-as-HF-scale-proxy is an empirical
question (B2 measured helmholtz 3929x -> 1.74x; sharp CV <= 0.0099 = no-op)"*.

**Concrete config**: see the arm table, deltas D1–D7 and the falsification bands in
`report.md` (written from this iteration, no content added there that is not here).

**Expected outcome / falsification / anchor**: `report.md`. Anchor reference
`"s5_tuning-B2"` per §4.5 (s5 batches >= 2 re-target the current champion card).

## Status

- Slot **covered** (1 proposal, `model`).
- Reopen candidates: **none exist** for this stream (both prior cards `complete`,
  `reopen_candidate: false`) — nothing to retry or drop.
- Immutables self-check: **pass (10/10)** — recorded below; no revision pass needed, so
  there is no `iteration_2.md`.

## Immutables self-check (10 items, positive evidence)

1. **Data read-only.** The card reads the same four dataset dirs through
   `round1/eval/panel_data.py` that B2 read; the only data-touching addition,
   `_lf_per_sample_scales`, already exists at `smoke_eval.py:207-244` and only *reads*
   `train["field_by_fid"][lf]` / `test["field_by_fid"][lf]`. N_hf on ifc_poisson stays 5
   (loader prints `N_hf=5`; verified in the raw file shape (5,5)/(5,64,64)). The per-sample
   scale is taken from the dataset's own coarse SOLVE, never from downsampled HF.
2. **Panel + guard fixed.** The card scores a 4-dataset SUBSET of the frozen 6-dataset
   `project.yaml panel:` and runs the unchanged `guard_set: [heat_local, fluid,
   sharp__sod_1d]` at contract tier; it adds no dataset and edits no list.
3. **Eval layer untouched.** Every number flows through `round1/eval/score_panel.py` +
   `eval/nrmse.py` at the same `nrmse_def_hash d3d0ade9191c13bacc40702f3eb26ad290e01641cacee22a1d2233b74c035850`
   B2 recorded; all seven deltas live inside the worktree family dir
   `models_r1/mf_fno_transfer_film_scaler_ps`; no file under `round1/eval/`, `project.yaml`,
   `program.md`, `docs/adr/` or `subagents/` is written.
4. **One nRMSE definition.** The training loss stays `F.mse_loss` on the normalized target
   (`smoke_eval.py:191`, unchanged); only the normalization CONSTANTS change, which §5
   "What CAN be changed" lists explicitly ("normalization"). The scored metric stays
   `eval/nrmse.py`'s per-sample rel-L2 on the raw HF field, and the oracle arm's leaked
   readout is written to a `ref_oracle_persample` split key so it can never enter
   `splits.test`.
5. **Contract CLI fixed.** `smoke_eval.py --dataset_dir --dataset_name --epochs --out
   --ckpt_dir --seed` is byte-identical to B2's family signature; all seven new knobs are
   environment-only and every one appears in the recipe `env` block, so they enter
   `score_panel.py`'s cache key (B2 precedent: `MFFP_TARGET_SCALER`, `MFFP_MODES_CAP`).
6. **Seeds / tier epochs fixed.** `seeds: [0]` (ADR 0004 strict single seed), `epochs: 200`
   (smoke tier per `project.yaml tiers.smoke_epochs`), screen at `epochs: 2`
   (`contract_epochs`). No other epoch count appears in the card; `submit_seeds_2_3.sh` is
   written but never invoked in-round.
7. **Guarded factory surfaces untouched.** Nothing under
   `mf_field/factory_mffp/{eval,baselines,references,scripts,data}`, `factory.md` or
   `mf_field/akash/**` is written. The base is COPIED from B2's already-vendored worktree
   family (`worktrees/s5_tuning/B2/models_r1/mf_fno_transfer_film_scaler` @
   `a55c788eec97683061b8a049610de59377cfd332`, itself vendoring `mf_fno_transfer_film` @
   `967562e2a4e3493515edab36b0fcb23655fce71f`) — the same read-only path B2 used.
8. **Checkpoint resume.** B2's family already implements arm-isolated mid-stage resume from
   `<ckpt_dir>/<arm_tag>/last.pt` with a config-match gate that includes `scaler_mode`
   (`smoke_eval.py:296-315`) and a fallback read of the contract path `<ckpt_dir>/last.pt`;
   delta D6 extends the gate key with `MFFP_ARM_TAG` so the clip/oracle arms cannot
   cross-load, and the card requires the builder to demonstrate resume at contract tier
   before submit.
9. **Thresholds strictly exceed the noise floor** (numbers quoted): ifc_poisson bar
   `skill <= 0.945` implies improvement `1.185106 - 0.945 = 0.240106` > floor **0.239908**
   (1.0008x); cahn_hilliard band `+/-0.554` > floor **0.553347** (1.0012x; 2.888x the
   batch-0 seed spread 0.191827); fisher_kpp band `+/-0.418` > floor **0.417735** (1.0006x;
   4.554x the spread 0.091789). `ext__helmholtz_2d` carries NO numeric threshold because
   `5.766462 - 9.694961 = -3.928500 < 0` makes one unattainable; it is report-only and its
   thresholds are diagnostic (n_eff, clip rate), not skill.
10. **Not a pre-falsified lever.** The §5 list is the WNO backbone swap, LF low-mode freezing
    (`mf_fno_spectral`) and the diffusion prior; this card swaps no backbone, freezes no
    modes and adds no generative prior — backbone, `modes_cap=12`, optimizer, schedule and
    batch size are held bit-identical to the certified champion. The nearest in-round
    neighbour is s5-B2's own arm A3 `revin_lf`, which was implemented, rank-ordered (rank 3)
    and screened but **never run at 200 epochs** (B2 `promotion.survivors = [A2,A1,A3,A4]`);
    the difference is that this card runs it at smoke tier with a paired in-job control, a
    control-matched fallback, clip-off arms, an oracle bound and effective-N/clip-rate
    instrumentation, and its purpose is the H3 attribution B2 part 6 left explicitly open,
    not the score B2 already measured.
