# Summary so far — Stream `r3s3_lf_value`, Batch 2

(Persisted verbatim by the orchestrator from the brainstormer's inline return, 2026-08-10; the harness blocked that subagent's report-file writes.)

## 1. Websearch findings and prior-art verdict

Source: `mffp_autoresearch/round3/websearches/r3s3_lf_value/batch_2/report.md` (5 iterations, cap hit 5/5; 15 WebSearch calls, 13 returned; 7 usable primary bodies via `urllib.request` + `pypdf`; `WebFetch` intercepted).
Three candidate directions, all **preempted-but-MF-composition-open**:

- **C1 row-efficiency law** (sweep distinct uncovered LF condition rows; derive knee + exchange rate).
  "The **LF-count sweep genre is published — do not claim it.**" Kirby et al. `https://arxiv.org/pdf/2301.01699` (fetched: HF fixed at 50, LF ∈ {250,500,1000}, MAE 1.46/0.828/0.866 %, saturation "because the number of high-fidelity training points is fixed"); functional-output grid `https://arxiv.org/pdf/2408.17075` (n1={2,5,10}×dim(U), n2={1,5,10}×n1, 9 combos × 10 DoEs).
  Open: (a) LF absent from the test path by construction — the survey's mapping family must "first run the low-fidelity simulator" at each new input (Eq. 13) and mapping/corrective families "are not able to take advantage" of n2 > n1; (b) sweep over *distinct conditions* with the covered/uncovered split held fixed (A2 control); (c) N_hf = 5 with a certified `tau_rel` and reference-free reporting; (d) regression on a **mediating learned quantity** (alignment, r = 0.985); (e) a numeric **exchange rate** — "iteration 2 term 1 returned **nothing**".
- **C2 LF-as-identifiability-supply**: the mechanism sentence is preempted **verbatim** (Kim et al. `https://arxiv.org/html/2409.07947v1`: spaces "not covered by the high-fidelity meta-GGA database can be effectively inferred from low-fidelity GGA data"). The claimable object is the **A2_lf_covered control** and the **E_cov/E_total decomposition**; externally the mechanism is named **semi-supervised regression with cheap biased pseudo-labels**.
- **C3 the 27-row ch hard subpopulation**: "the most defensible novelty in this batch — but it is a **diagnostic**, so it must be delivered as a certified measurement". **Terminology hazard (blocking for the card):** rename away from "non-identifiable" (PLOS pcbi.1013553, fetched: that term means parameters with *little to no impact on output* — the opposite of our mask).

Binding "For the brainstormer" instruction 6: fix `per_rung_max` on the full rung pool, drop `ifc_poisson`, ch **reference-free** (MDD 1.7077), ≥ 3 seeds/point, price every claim against certified `tau_rel` (ch **0.3612**, ifc_heat **0.1640**) — "a knee that moves by less than that is not a knee"; and any teacher/distillation arm stays `preempted`, baseline only (batch-1 D3).

## 2. Section 12 conventions, verbatim

Round-3 `program.md` §5: "Round-2 §12 methodological rules apply verbatim". The stream's conventions are therefore `round2/program.md` §12.3, quoted verbatim:

> ### 12.3 `r2s3_lf_train_signal` (lever)
>
> - **Question**: LF as training-only signal. Candidate mechanisms (spec 6): distillation from an LF-consuming teacher (round-1 families in role 5.10b — teacher at train, absent at test), LF-pretrain -> HF-finetune, auxiliary multi-fidelity losses (predict LF and HF jointly from condition).
> - **The stream has a mandatory declared baseline**: `mf_fno_transfer_film` (factory zoo champion) IS LF-pretrain->HF-finetune from the condition vector (verified 2026-07-31: its test input is `cond_by_fid` only; it runs on the stripped view unmodified). Any r2s3 pretrain/finetune proposal must either score it as the baseline arm or cite how it differs — an undifferentiated re-proposal is a rebadge (reviewer FAIL, 5.10).
> - **revin_lf two-scaler finding** (r1 s5): exact at LF-pretrain, 3.1% proxy at HF — normalization transfer across fidelities is a solved sub-problem; reuse it, don't rediscover it.
> - **Nested-ladder degeneracy** (r1 report 6) directly constrains this stream: with aligned/nested ladders, "multi-fidelity" training pairs degenerate toward top-rung replication — LF-as-signal designs must state what information the LF rungs add that the HF rung does not already contain (spectral truncation structure, more samples at low rungs on ifc_poisson: 70 lower-fidelity vs 5 HF).
> - The **unified normalization eligibility rule** (r1 s2, checks 0-6) governs any per-sample normalization proposal; spread is not the decider.
> - Uses the existing 400 aligned samples only (5.11).

Also binding: ADR r2-0004 **registration of model-side lifts** (vendor the `eval/panel_data.py` interpolators or `models/_common/lf_registration.py`; a bare `F.interpolate`/`zoom` is a reviewer FAIL) and the **target-scaler pre-flight**; round-3 `program.md` §2 **affine-floor rule** (every ifc number reports the fitted `affine_on_hf_train` floor beside it; ifc_heat skill 0.96); ADR r3-0003 D2 (**ch reference-free**, MDD 1.7077); ADR r3-0004 (pfc report-only — deliberately not enumerated in any clause of this card).

## 3. Within-stream prior cards

`experiment_cards/r3s3_lf_value/batch_1/B1.json`, `status: complete`, `reopen_candidate: false`, worktree `worktrees/r3s3_lf_value/B1`, build commit `050806e0bdfce9144da4a7a9f523c3a2e97d6a69` (branch `round3/exp-r3s3_lf_value-B1`), family `models_r3/r3s3_lf_channels` (7 modules, 2154 LOC), 60 legs/seed × 3 seeds (jobs 66825323 / 66879960 / 66879961, 150.25 / 140.13 / 140.15 min ⇒ **~2.4 min/leg**, `state/timing_ledger.json`).

Parts 5–7 established, on the honest panel:
- **A2_lf_covered is the same learned function as A0_nolf** — D(A0,A2)/D(A0,A1) = 0.098–0.307 and D(A2,A1)/D(A0,A1) ≥ 1.007 on 5/5 cells ⇒ **E_cov/E_total ∈ [0.972, 1.024]** on 30/30 cells, E_opt ≈ 0. LF-at-train's value is **supply of distinct condition rows**, not coverage geometry (Spearman(improvement, distance-to-nearest-HF) = 0.041 / 0.174 / 0.147 on ac/fk/ch; only ifc_heat 0.520).
- Recovery is an almost deterministic function of the learned **condition-response alignment**: Pearson **r = +0.985**, Spearman +0.880 over 36 ch cells; alignment by arm A2 0.048–0.184, A3s 0.272–0.420, A1 0.684–0.719, A3 0.685–0.727.
- **A4_hf20_nolf**: 4× the HF budget buys only 8–59 % of the full LF pool ⇒ the LF-row ↔ HF-row exchange rate is unmeasured.
- ch reference-free effect nRMSE(A0)/nRMSE(A1) = **1.955–2.381** (mean 2.115) over 9 cells; ifc_heat seed-0 A0 0.060518 → A1 0.004849.
- The headlined −38.97 % ifc_poisson / −10.14 % panel deltas are **retracted stale-checkpoint artefacts** (STOP-THE-LINE #2; jobs 89201–11; `--fail-on-stale` CLEAN; part 7 `cross_stream_notes` RESOLUTION 2026-08-10). Post-repair the A1 arm reproduces the fresh anchor A1 legs to −0.75..+0.10 %/seed — the vendored-reproduction seam. Panel geomean 11.0789 vs anchor `r2s3_lf_train_signal-B3` 11.1689 [10.9988, 11.3390] = −0.81 %, **0.079× the noise floor, NOT resolvable**; the card's deliverable is the mechanism decomposition, not a score.
- **`per_rung_max` is computed over exactly the rows an arm keeps** (`models_r3/r3s3_lf_channels/smoke_eval.py:491-495`): mismatch 0.98–1.64 on ifc_poisson, and on **ch** s_rung/s_hf = 1.169–1.174 for A1/A3 vs 1.000 for A2/A3s. Batch 1's ch decomposition therefore carries a ~17 % un-matched-normalisation confound of its own.

Part 7 `next_direction` (explicit pre-directive for this batch): geometric cap ladder **5/10/20/40/80/160/395** uncovered conditions on `sharp__cahn_hilliard` + `ifc_heat`, 3 seeds, holding everything at B1's vendored recipe; (1) **fix the scaler across arms** ("compute one scaler per rung on the full rung pool"), (2) **drop ifc_poisson** (exactly affine, oracle residual 2.9e-08; `affine_on_hf_train` 0.057375 unbeaten; rung→HF transfer nRMSE 3.15–81.2), (3) **ch reference-free**, ≥ 3 seeds/point. Promoted tools: `tools/response_decomposition.py`, `tools/stale_checkpoint_audit.py`.

## 4. Cross-stream cards

`worktrees/r3s1_factorised/B1/scratchpad/turn3_results.json::t3c_hard_rows` + `reanalysis_turn_3_results.md` §T3c: a **seed-invariant 27-row ch subpopulation** (`n_hard_per_seed` [27,27,27]; hard at any seed = 27 = hard at all seeds), largest per-dimension standardised mean gap **0.4476 σ** (argmax dim 17; no dimension exceeds 0.5 σ), nearest-train-neighbour distance in standardised condition space hard 3.6671 vs easy 3.6037 (**ratio 1.0176** — not extrapolations), nearest-train-**field** rel-L2 hard 0.4202 vs easy 0.1278 (**ratio 3.29**), `ynorm_ratio` 1.0776 / `ymeanabs_ratio` 1.0072 (not an amplitude or level effect), and a clean empty band (no per-row rel-L2 in 0.62–0.99). Oracle nearest-train-field retrieval scores 0.4202 on them vs the head's 1.0632 ⇒ **not intrinsically unpredictable, unpredictable from this condition vector**. The mask ships as a verbatim 100-element 0/1 list.
Also live from the same file: r3s1-B1 T3a uses ch `tau_rel` 0.3612 as the operative constant, and round-2 §6's **arm-comparison mis-specification warning** ("compare at matched rows and matched procedure") is exactly what the scaler repair discharges.

## 5. Reopen candidates

**None.** `experiment_cards/r3s3_lf_value/batch_1/B1.json` carries `reopen_candidate: false`, `skipped_reason: null`, `status: complete`; batch 1's report resolved the inherited set as "all 14 round-2 cards carry `reopen_candidate: false`". Nothing to retry or drop.

## 6. Prior-round record — tested directions relevant to this stream

From `../round2/docs/round2_report.md` §4/§6:
- §4.4 "LF-at-train works through coverage and amplitude, not through auxiliary targets" — **confirmed and sharpened** on the repaired panel by B1 (coverage = *row supply*, not geometry); the auxiliary-LF-target head remains a **certified null** at every sample count (r2s4-B2), so no auxiliary-MF-loss arm is proposed here.
- §12.3's declared baseline `mf_fno_transfer_film` (LF-pretrain→HF-finetune) — **untested-on-repaired-panel**, and deliberately not re-run: it blends the optimisation and supply channels this lineage separates, and B1 cited-and-differentiated it in part 2. Re-proposing it now would be the §5.10 rebadge.
- Distillation from an LF-consuming teacher — **preempted (cite)** in round-2 batch 1 *and* round-3 batch 1 (D3); not proposed.
- §6 **three-channel value-of-LF taxonomy** (direction supply / row-space fit / level-amplitude) — **confirmed**: B1 answered "direction supply", so batch 2 must *price* that channel, not re-derive it.
- §6 **zero-information-null publication rule** and **arm-comparison mis-specification warning** — both bind directly (floor arms on every leg; the arm-invariant scaler).
- §5.7 "the certified mce on ifc is an init-replicate scale" — **superseded for this batch** by the now-**certified** `state/anchors_repaired/noise_floor.json` (`_provisional: false`, `_certified_utc` 2026-08-08T20:00:07Z, r3s4_audit-B1).
- §5.5 "ifc_poisson is degenerate for this regime" — **confirmed twice more** by B1 turn 2; this is the evidence behind dropping it.

## 7. What is UNKNOWN

**(a) The shape of the coverage channel between 10 and 790 LF rows.** B1 samples exactly two points on ch (10 distinct conditions → recovery 7–44 %; 395 → 97–102 %) and nothing between. Whether the curve saturates at a cap an HF-scarce user could afford, or runs log-linear to the pool edge, is unmeasured — and the ch cell resolves deltas of only **2.0–2.9 % of the total effect** (`tau_rel` 0.3612 skill × copy-LF reference 0.041802962686225575 = **0.015101 nRMSE**, against an inferred A0→A1 effect of 0.514–0.743 nRMSE), so a knee is genuinely *measurable here if it exists*.

**(b) Whether the ch decomposition survives a matched scaler.** ch's A1/A3 arms trained at s_rung/s_hf = 1.169–1.174 against A2/A3s at 1.000. Nobody has run the ch channel split at a scaler invariant to arm row selection, so E_cov/E_total ∈ [0.972, 1.024] is provisional **on the very dataset the stream intends to claim it on**.

**(c) The exchange rate.** A4 gives one HF point (N_hf 20 = 8–59 % of the full LF pool). Whether one HF row is worth ≈5 or ≈50 uncovered LF condition rows, and whether the rate is constant along the ladder, is the stream's stated debt (part 7: "the exchange rate ... is the quantity the stream still owes").

**(d) Whether one mediator explains both supplies.** r = 0.985 holds *within* the LF arms. If HF-budget legs land on the **same** R(alignment) curve, the exchange rate becomes a law with a stated mechanism; if not, it is a table. "Nothing retrieved reports a mediating learned quantity for MF sample-count curves" — this is the untouched seam.

**(e) Whether the coverage channel repairs the forward-sensitive rows at the same price as the bulk.** The 27 ch rows are condition-indistinguishable (0.448 σ, nnd ratio 1.018) but field-distant (3.29×). If R_hard(c) lags R_easy(c) by more than `tau_rel`, the headline knee is an average over two mechanisms.

**(f) Whether ifc_heat can resolve a knee at all.** `tau_rel` 0.1640195793751628 skill × paper bar 0.074 = **0.012137 nRMSE**, against a measured A0→A1 effect of 0.060518 − 0.004849 = 0.055669 ⇒ steps of **21.8 %** of the effect. ifc_heat can corroborate coarsely; it cannot locate a knee finely. That asymmetry between the two carded datasets has never been written down.

**(g) Where the model first beats its own training-free floors.** On ch, A0_nolf (≈1.052–1.281 nRMSE, inferred from the 1.955–2.381 ratio) is *worse* than `zero` (1.0) and `nn_condition` (0.96901); on ifc_heat A0 (0.060518) already beats `nn_condition` (0.10316) and `affine_on_hf_train` (0.070918). The cap at which training becomes worth doing **at all** is a different and unmeasured quantity from the recovery knee.
