# Iteration 1 — s2_beyond_copy, Batch 3

## Design context considered

- `summary_so_far.md` §6 (7 unknowns) and the batch-3 prior-art verdict (D1
  `preempted-but-MF-composition-open`; D2 `preempted (cite)`; D3 `novel` but reporting-only;
  D4 preempted-with-a-negative; D5 unsearched).
- §12.2 verbatim (summary §2): anchor **skill 1.0 = copy-LF**; "normalization destroying
  amplitude structure" is a listed candidate mechanism for later batches; the data-defect
  warning (already discharged by the operator note, which is the mentor-facing bug report).
- The immutables block (§4.5 of the brainstormer prompt = program.md §5) held in view
  through the self-check below.
- Anchor `state/anchors/s2_beyond_copy.json` value 1.0; `state/noise_floor.json`
  `min_claimable_effect`: pfc 1.151100, allen_cahn 1.633407, cahn_hilliard 0.553347,
  fisher_kpp 0.417735, helmholtz 9.694961.
- **Operating-point floors** (the convention B2 established and the mechanism analyser
  endorsed): the rescaled batch-0 seed spread `spread / mean_skill` = pfc 0.082643/11.511001
  = **0.007180**, allen_cahn 0.014150/16.334071 = **0.000866**, cahn_hilliard
  0.191827/5.533466 = **0.034667**, fisher_kpp 0.091789/4.177355 = **0.021973**, helmholtz
  9.694961/13.817290 = **0.701654** (-> helmholtz admits no fine-grained claim: REPORT-ONLY).
- B2 part 5 operating point (the paired control target): pfc 0.018360, allen_cahn 0.287282,
  cahn_hilliard 0.453228, fisher_kpp 0.804192, helmholtz 4.135972, geomean 0.380264;
  leave-helmholtz-out geomean = exp(mean ln) over the four sharp sets = **0.20940**.
- B2 part 6 F10/F12/F5/F6 and the mechanism-analyser handoff
  (`worktrees/s2_beyond_copy/B2/notes/handoff_experiment_mechanism_analyzer.md`):
  "Per-sample target normalisation (F10) and a per-sample trust gate (F12, geomean 0.259)
  are the two cheap non-architectural levers".
- Pre-falsified levers (program.md §5): WNO backbone swap; LF low-mode freezing
  (`mf_fno_spectral`); diffusion prior. None is this proposal (see self-check item 10).
- The substrate as it actually exists on disk:
  `worktrees/s2_beyond_copy/B2/models_r1/s2_lf_residual_control/` (manifest.json, model.py,
  retrieval.py, smoke_eval.py, INSPIRATION.md) at build_commit
  `5bf0e86c292042b3050979f5c35af538305f1152`. Read directly: `_scale(a) = max(|a|.max(),
  1e-8)` (smoke_eval.py:223-224); `scaler_out = _scale(r_tr)` (:504); `_train` divides the
  target by that ONE scalar (:243) and `_predict` multiplies the output back (:289); the
  promoted arm `lf_resid_fno` is **single-stage** (`stages.append(("HFresid-train", ...))`,
  :628, no LF-pretrain stage). The per-sample change is a vector `scaler` in exactly those
  three places.

## Proposal reasoning (alternatives weighed and rejected)

**Chosen: D1 — per-sample amplitude normalisation of the fidelity-residual TARGET, with the
test-time scale PREDICTED from `(X, LF)`, on the unchanged `lf_resid_fno` substrate.**
It is the only direction that (a) the search scores as an open MF composition, (b) B2 part 7
ranks as the top *intervention* (item 2), (c) attacks a defect measured on this exact
substrate (F10), and (d) makes a falsifiable 2x5 asymmetric prediction rather than a
"geomean went down" claim.

Rejected alternatives:

1. **D4 tail/hard-sample reweighting** — the websearcher fetched a NEGATIVE result
   (density-inverse cost-sensitive weighting raised test max error 76.63 K -> 96.72 K,
   https://arxiv.org/html/2605.16078) and instructs "Prefer D1 (normalize) over D4
   (reweight)". Not proposed in any arm.
2. **D5 `modes_cap` raise** — unsearched by both websearcher runs; §12.5's audited knob F22;
   B2 part 7: "it should be tested only after (1)-(3), since raising it cannot help the four
   datasets whose residual is already >= 83 % in-band". It is also the reason fisher_kpp is
   predicted NEUTRAL here (F5: 16.8 % in-band), which makes the two streams separable.
3. **D2 trust gate as the card's mechanism** — `preempted (cite)` at protocol *and*
   mechanism level, and ADR 0009 forbids the published PDE-residual certificate. Demoted to
   a non-promotable `ref_*` measurement column + contract screen, exactly as instructed.
4. **D3 node-aligned reference as the scored metric** — forbidden (immutables 2-4, metric
   frozen; operator note: "cards may carry a registration-corrected reference ALONGSIDE the
   frozen skill ... never replacing it"). Carried as a mandatory reported sidecar instead.
5. **A zero-GPU re-scoring card** (B2 part 7 item 1 alone) — rejected as a whole card: it is
   a measurement we get for free as instrumentation inside this card, and it leaves the one
   untested causal claim (F10) untested for another batch.
6. **A relative / robust (Huber, log-cosh) loss instead of renormalising the target** —
   that is s7_loss's stream, and s7-B1 already found a gradient pathology there; it would
   also collide with s7's live lambda=1 question.
7. **Per-sample normalising the INPUT channels as well, or feeding `log s_hat` as an extra
   FiLM scalar** — both are second levers in one card. Noted as the natural B4 composition.
8. **A true-per-sample-scale arm as the SCORED arm** — illegal: `max|HF-LF|` at test time is
   not observable (the websearcher settles this: "A card that normalizes by the *true*
   per-sample `max|HF-LF|` at test time would be an oracle, not a method"). Kept as an
   explicitly labelled ORACLE `ref_*` column that bounds the headroom.

**The in-repo near-refutation I must design around (s7_loss-B1 M6).** A per-sample
denominator silently re-weights samples by `1/s_i^2`; s7-B1's rule reads "(1) spread >= ~10
-> do not use it **without a denominator floor**". Our residual-scale spreads are 8.2e4
(pfc) and 1.4e4 (helmholtz) — far past that line, and on pfc the bottom decile's "residual"
is numerical roundoff (F6: 1.77e-08 relative), so an unfloored per-sample scale would spend
capacity fitting roundoff. **Mitigation, pre-registered:** `s_i = max(max_x|r_i(x)|,
q25(train per-sample scales))` — a train-split quantile floor, no test data, one fixed
a-priori quantile. The unfloored variant runs as a screen-only arm so the floor's necessity
is auditable, and `tools/target_scale_spread_audit.py` reports the effective-N and weight
spread under the floored scale BEFORE submit. s7-M6's other two rules are satisfied by
construction: there is no explicit gain weight (lambda = 1 equivalent: plain MSE in the
normalised space), and the promoted arm has **no LF-pretrain stage** (verified at
smoke_eval.py:628).

**Why the scale should be predictable.** Where the residual is the registration ramp (F1/F4:
cos 0.987-0.999 on allen_cahn/cahn_hilliard, ~100 % on pfc), `r ~ (h/2) grad(LF)`, so
`||r_i|| ~ ||grad LF_i||` — a quantity computable from the LF field the model already
receives. DiSOL's "optional amplitude regressor" is the citable precedent; s1_poisson-B3
(per-sample gain law predicted from the condition vector, ifc_poisson 0.951 -> 0.694) is the
in-repo feasibility datum. Both a learned MLP regressor (rank 1) and a closed-form
calibrated gradient proxy (rank 2) are therefore credible, and the ORACLE arm measures
exactly what the predictor costs.

**Why pfc is the primary leg and what its ceiling is.** helmholtz is REPORT-ONLY (rescaled
floor 0.701654). Of the four claimable datasets, `target_scale_spread_audit.py` flags only
pfc. Honest ceiling arithmetic: the F12 no-harm oracle removes only **9.8 %** of the arm's
pfc error, so damage-removal alone cannot clear a defensible threshold — the remaining gain
must come from the better-conditioned objective (all 400 samples contributing instead of an
effective handful). That is precisely the mechanism claim, so a 20 % threshold makes the leg
decide the mechanism rather than the plumbing. F6's reproducibility caveat ("Treat pfc deltas
below ~10 % as non-differences regardless of seed count") sets the floor for that threshold
at 10 %; 20 % is 2x it and 27.9x the rescaled seed spread.

**Cross-stream separation from s5_tuning-B2 (per-DATASET zscore).** s5-B2's lever is a
per-dataset affine on the LF-blind champion over the 6-dataset panel; it moved helmholtz and
ifc_poisson and left all four sharp sets inside their floors. This card's lever is a
per-SAMPLE amplitude on the LF-residual target of `lf_resid_fno` over the 5 beyond-copy sets.
The discriminating result is **pfc**: a per-dataset scaler cannot move it (s5-B2: 11.511 ->
11.216, inside the 1.151 floor) because the defect is *within-dataset* spread; if the
per-sample arm moves pfc >= 20 % the lever is sample-specific, and if it also fails on pfc
while helmholtz alone moves, the two streams have found the same dataset-level amplitude
channel and s2's per-sample framing adds nothing. The cards **compose** rather than collide:
different substrate (LF-consuming vs LF-blind), different axis (per-sample vs per-dataset),
disjoint knob namespaces (`S2B3_*` vs `MFFP_TARGET_SCALER`), so a future merged card is
literally `MFFP_TARGET_SCALER=zscore` x `S2B3_TARGET_NORM=per_sample_maxabs`.

## Proposal

- **Category**: `mf_composition / target-normalisation repair — per-sample amplitude
  normalisation of the fidelity residual with a test-time-predicted scale`.
- **Card type**: `model`.
- **Motivation**: quotes the D1 verdict verbatim (see report.md "Prior-art verdict quoted");
  the defect is B2 F10 (global `max|HF-LF|` scaler; spread 82379 pfc / 13702 helmholtz;
  helmholtz effective N = 1.2 of 400), the intervention is B2 part 7 item (2).
- **Concrete config**: family `models_r1/s2_resid_amplitude_norm`, vendored verbatim from
  `worktrees/s2_beyond_copy/B2/models_r1/s2_lf_residual_control` @ `5bf0e86c2920...`
  (which itself vendors `mf_fno_transfer_film` @ `967562e2a4e3...`). Network, optimiser,
  schedule, batch size, `modes_cap=12`, zero-init head, `max(lf_fids)` LF channel, seam and
  leakage tripwires **unchanged**. One behavioural change: the scalar `scaler_out` becomes a
  per-sample vector, with the test-time value predicted. Arms:

  | arm | `S2B3_ARM` | what it does | role | promotable |
  |---|---|---|---|---|
  | A0 | `global_ctrl` | B2's exact path (`scaler = max|r| over train`) | paired control + B2-continuity gate, same job/node/seed | never |
  | A1 | `persample_pred` | `s_i = max(max_x|r_i|, q25_train)`; MLP predicts `log s` from `(X, log max|LF_i|, log ||grad LF_i||_2, log ||LF_i||_2, log std(LF_i))`; test-time `s_hat_i` | **THE CANDIDATE** | rank 1 |
  | A2 | `persample_gradproxy` | same normalisation; closed-form `s_hat_i = c * ||grad LF_i||_inf`, `c` by least squares in log space on train | fallback candidate (no extra net) | rank 2 |
  | A3 | `ref_oracle_truescale` | A1's checkpoint evaluated with the TRUE `s_i` | **ORACLE**, bounds predictor headroom | never (ref split) |
  | A4 | `ref_gate_lfkeyed` | physics-free no-harm gate on A1's output (16x16 block-mean LF signature, k=5, margin threshold calibrated on a 20 % HF-train holdout) | D2 measurement only | never (ref split) |
  | A5 | `persample_nofloor` | A1 without the q25 denominator floor | screen-only audit of the s7-M6 floor rule | never (screen) |

  200-epoch scored job trains **A0 and A1** (paired); A3/A4 are extra eval paths off A1's
  checkpoint (no GPU); A5 and A2 appear at contract tier only unless A1 is broken.
  **Fixed promotion rank, pinned before submit (ADR 0007)**: A1 -> A2; *broken* := crash /
  non-finite metric / contract-tier 5-dataset geomean > 3x A0's on the same screen run;
  close calls never reorder; A0/A3/A4/A5 are never promotable.
  **Mandatory instrumentation**: `tools/registration_skill_split.py` on both arms' shipped
  result JSONs (registration-vs-genuine split of any gain, `damage_share`, corrected
  geomean); `tools/target_scale_spread_audit.py` before (global) and after (under `s_hat`)
  per dataset; per-dataset Spearman `rho(s_hat, s_true)` and median `|log10(s_hat/s)|`;
  per-sample rel-L2 columns dumped for both arms.
- **Recipe**: see report.md (complete JSON).
- **Expected outcome**: pfc 0.018360 -> **0.010** (range 0.006-0.014); helmholtz 4.136 ->
  ~1.0 (0.7-1.4, REPORT-ONLY); allen_cahn / cahn_hilliard / fisher_kpp NEUTRAL inside
  +/-15 %; 5-dataset geomean 0.380 -> ~0.25; leave-helmholtz-out geomean 0.2094 -> ~0.18
  (the honest headline). Oracle A3 <= A1 on pfc and helmholtz; the gap is the predictor's cost.
- **Expected falsification**: four legs (primary pfc 20 %, asymmetry +/-15 % on the neutral
  three in EITHER direction, absolute-floor sanity vs the batch-0 champion, and the
  instrumented mechanism leg on `damage_share`) — verbatim in report.md.
- **Anchor reference**: `null` (gap stream; own-stream anchor skill 1.0 implicit — §4.5).

## Status

- Slot covered (1 proposal, `model`).
- Skipped: no.
- Reopen candidates resolved: none exist in this stream (or any stream) — nothing to retry
  or drop.
- Immutables self-check: **pass (10/10)** — recorded in report.md; no revision pass needed,
  so there is no `iteration_2.md`.
