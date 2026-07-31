# Summary so far — Stream `r2s2_stacked`, Batch 2

All paths relative to `mffp_autoresearch/round2/` unless absolute.

## 1. Websearch findings + prior-art verdict

Source: `websearches/r2s2_stacked/batch_2/report.md` (4 iterations, 12 searches,
10 fetches over 9 sources; `ENOUGH` at iteration 3; refutation pass at 4).

Verdict table, the four candidate directions:

- **D1** realisation-aware (stochastic/ensemble) stage-1 pseudo-LF -> corrector trained on
  real coarse solves, on cahn_hilliard (B1 part-7 option A):
  `preempted-but-MF-composition-open (cite)`. Open: *"the exact topology (parameter -> sampled
  LF realisation -> corrector trained on real coarse solves) and a coherence-threshold
  acceptance criterion appear in no fetched source. But the outcome is predicted negative by
  three lines: K-sample mean = conditional mean; an independent sample has coherence 0 with the
  test realisation in expectation; DPI"*. Citations: MFFM https://arxiv.org/html/2605.16118
  (VERIFIED, LF solve required at inference), https://arxiv.org/html/2602.00072 (VERIFIED,
  condition-only at test but no downstream model), https://arxiv.org/abs/2006.04731,
  https://arxiv.org/pdf/2507.02106, FreqNO-DPS https://arxiv.org/html/2606.03936 (VERIFIED).
- **D2a** amplitude x shape head for helmholtz: `novel (thin — must not be the claim)`.
  **D2b** POD+ridge head on ifc_poisson: `preempted (cite)` (Hesthaven & Ubbiali 2018) —
  *"enters as a declared baseline arm"*.
- **D3** training-free coherence eligibility precondition:
  `preempted-but-MF-composition-open (cite)` — FreqNO-DPS already calls a cross-spectral
  coherence diagnostic *"a prerequisite check for applying the method to any new surrogate"*;
  what is open is that *"r2s2's rule is a CALIBRATED THRESHOLD ON CORRECTOR VALUE
  (0.52 < gamma_b1 < 0.95 bracketed by the real->pseudo interpolation) plus an oracle-Wiener
  upper bound. No fetched source calibrates coherence against realised corrector value-add"*.
- **D4** closure of the stacked class: `preempted (cite)` as a *principle* (data-processing
  inequality), **open as a measurement** — *"No fetched source states the DPI for stacked PDE
  surrogates or measures the resulting ceiling on field-valued MF benchmarks. Claim the
  measurement, cite the theorem for the principle."*

Brainstormer-directed notes (section "For the brainstormer"): quote D1 verbatim if proposing
option A and *"say what your stage 1 conditions on that the conditional mean does not have. If
the answer is 'nothing', the arm is refuted before it runs"*; put the coherence go/no-go
**before** the SLURM submit; option A's ceiling on cahn_hilliard is ~1.6 skill units against a
panel geomean of 14.08, so *"a WIN here does not move the round's headline"*; carry the floor
arms, the helmholtz zero-floor column, the pfc band-limited caveat, and B1's ifc
`semantics_degraded` flag. Process rule from `Dead ends`: never fetch arXiv `/pdf/` (a `/pdf/`
fetch produced a confidently wrong reading this loop).

## 2. Program.md §12.2 conventions (verbatim)

> ### 12.2 `r2s2_stacked` (lever)
>
> - **B1 is pre-directed by the spec** (Eloise's stacking proposal): train a
>   FiLM-FNO **pseudo-LF emulator** (condition → LF field) on the TRAIN LF
>   data, feed the best round-1 corrector — the s6 DC lineage / s4-B3
>   `dc_cleaned` stage (r1 geomean 0.1233–0.19 under OLD denominators; restate
>   under corrected before claiming). Arms: **frozen corrector / fine-tuned
>   corrector / end-to-end**, to separate emulator error from distribution
>   shift (the corrector was trained on real LF; pseudo-LF is
>   off-distribution for it).
> - Declared-reuse rule (§5.10a): the corrector is a frozen test-time
>   sub-component — the reuse IS the experiment. Its code lives in the round-1
>   worktrees (`round1/worktrees/s6_local/B2`, `round1/worktrees/
>   s4_hybrid_routing/B3/models_r1/s4_router/`); vendor the needed pieces into
>   the round-2 family dir with provenance comments (round-1 branches are
>   immutable).
> - Round-1 mechanism rules apply to the cleaning stage: **BC-match rule**
>   (eligibility decidable training-free; audit tool
>   `tools/spectral_prestage_bc_audit.py`), the **wrap-seam caveat** (part of
>   dc_cleaned's pfc credit was a boundary-rim artifact of the DEFECTIVE
>   reference — under the corrected reference that credit may vanish; the
>   s4-B3 H4 finding says deep-bulk ratio was 0.908 on pfc), and the
>   **lineage-bound caveat** for any routing/eligibility rule.
> - Failure is informative: if pseudo-LF → corrector loses to r2s1's direct
>   models, the LF representation is not a useful bottleneck — that is the
>   stream's falsification framing.

Also binding: §2.2 floor arms + §2.3 panel/anchor table, §4.3 anchor
(`state/anchors/r2s2_stacked.json`: 23.063616857615774, `best_floor_panel_geomean`,
`provisional: false`), §5.9 stripped test view, §5.10 declared-reuse, §5.11 no new data.

## 3. Within-stream prior cards

`experiment_cards/r2s2_stacked/batch_1/B1.json` — status `complete`, `reopen_candidate: false`,
`anchor_reference: null`, 5 arms, single seed 0, `provisional-single-seed`.

Part 5: scored arm `frozen` panel geomean **14.0756** vs anchor 23.0636 (delta -8.99, beyond the
certified panel mce 1.1419). Per-dataset skill (frozen): helmholtz 2.8151, pfc 47.4553,
allen_cahn 147.7631, fisher_kpp 11.6713, cahn_hilliard 11.2789, ifc_poisson 2.9927
(`semantics_degraded: true`, `attribution.valid=false`, `pairing.paired_real_lf=false`).
Arm geomeans: emul_only 24.685 / frozen 14.076 / finetuned 13.873 / end_to_end 20.988 /
condmean_lf 29.363; **excluding ifc_poisson the five paired columns are 19.186 / 19.184 /
19.179** — the corrector is worth <= 0.08% there, and the whole all-6 gain is the ifc column
where the corrector was fitted on the emulator's own output (F17).

Part 6 findings that matter for B2: **F13** the frozen corrector's value is a steep function of
its input's *realisation* (relative value-add pfc 0.99997 at t=0 -> 0.1300 at t=0.1 ->
-0.000157 at t=1; cahn_hilliard 0.3209 -> 0.0450 -> +0.00082; guards *invert*: fluid 0.6094 ->
0.6289, heat_local 0.8996 -> 0.6786). **F14** cos(correction, residual) rotates +0.98 -> ~0.
**F15** band-1 coherence pseudo/real: pfc 0.128/1.000, allen_cahn 0.260/0.9998, fisher_kpp
0.214/0.9997, cahn_hilliard 0.516/0.997, helmholtz 0.129/0.391; in-sample **oracle Wiener** gain
on pseudo-LF: pfc -13.75%, helmholtz -2.99%, allen_cahn +2.45%, fisher_kpp +3.00%,
cahn_hilliard +14.07%, fluid +27.30%, heat_local +53.42%. **F16** the stack is at or past the
best training-free condition-only predictor on 5/6 panel datasets. Ceiling taxonomy: STRUCTURAL
(pfc, allen_cahn, fisher_kpp — ADR r2-0003), SAMPLING (cahn_hilliard, nn condition distance
3.91 sd at N=320), LEARNING gap (helmholtz, ifc_poisson).

Part 7: open question = *"Can ANY realisation-aware stage 1 ... restore the band>=1 coherence a
defect corrector needs, or is the stacked class dead on this benchmark?"*; two mutually
exclusive options (A) realisation-aware stage 1 on cahn_hilliard, (B) pivot to the two
learning-gap columns — with the explicit note that (B) *"should be run as a condition->HF card
and coordinated with r2s1/r2s4 rather than as another stacking arm"*; and *"Do NOT re-run the
frozen-vs-finetuned contrast as the card specified it"* (A3 had a 50% larger optimizer budget;
worth <= 0.08%). Promoted tools: `tools/reachable_set_rank_audit.py`,
`tools/surrogate_coherence_eligibility.py` (verified present; computes per-band coherence,
in-sample oracle Wiener ceiling, verdict rule `FUTILE <= 0.52 / ELIGIBLE >= 0.95`).

Timing (`state/timing_ledger.json`): B1 panel leg 20.13 min, guard leg 7.05 min on h200.

## 4. Cross-stream cards touching this stream

- `r2s1_direct/batch_2/B2.json` (status `drafted`) — pre-registered training-free selection of a
  **closed-form condition->HF head** (POD+ridge), Wiener band gains, blend over bases
  {zero, train_mean, nn_condition, dc_only}, capacity ladder up to a 10^7-parameter decoder,
  full panel. **This is B1 part-7 option (B) already in flight** — helmholtz *and* ifc_poisson,
  including the closed-form ifc head. Any r2s2-B2 proposing option (B) would duplicate it.
- `r2s4_diag/batch_2/B2.json` (status `built`) — value-of-LF accounting, LF-teacher /
  LF-ablated inner-fold arms, N_hf scaling. Measures LF as a *training* signal; adjacent to but
  disjoint from correctability of a *test-time intermediate*.
- `r2s3_lf_train_signal/batch_2/B2.json` (status `drafted`) — +/-LF at N_hf ~ 5 with
  null-direction supply; independently corroborates ifc_poisson's affine condition->field law.
- `state/noise_floor.json` is now **certified** (`_provisional: false`, r2s4-B1, 3 seeds):
  panel mce 1.1419; per dataset helmholtz 2.95299, pfc 0.21303, allen_cahn 0.87970, fisher_kpp
  0.00071, cahn_hilliard 0.09125, ifc_poisson 0.93770; and its per-dataset `mean_skill` is the
  certified condition->HF comparator (helmholtz 6.9438, pfc 47.8472, allen_cahn 147.3154,
  fisher_kpp 11.5582, cahn_hilliard 13.1781, ifc 8.2612; geomean 19.8178).

## 5. Reopen candidates

None. `grep -rl '"reopen_candidate": true' experiment_cards/` returns nothing round-wide, and
B1 carries `reopen_candidate: false`.

## 6. What is UNKNOWN

1. **The threshold is bracketed, not calibrated.** B1 measured value-add >= 63% at
   gamma_band1 >= 0.95 and <= 0.08% at <= 0.52, from *three* interpolation points
   (t = 0, 0.1, 1) with a **frozen** corrector. Nobody knows the shape of value-add(gamma) in
   between, nor whether the drop is the *input's* correctability or the frozen corrector's
   distribution shift — those two are confounded in every number B1 produced. Refitting the
   corrector at every rung at a matched budget separates them; that is one job and it has never
   been run.
2. **Is the promoted eligibility rule SAFE for nonlinear correctors?** The tool's ceiling is
   an LSI (spatially invariant) oracle. Round 1's corrector is a gated CNN — spatially adaptive,
   able in principle to fix registration/edge errors an LSI filter cannot, i.e. able to exceed
   the "ceiling" we are about to hand the round as a precondition. We shipped the rule
   (`tools/surrogate_coherence_eligibility.py`, B1 cross-stream note 3) without ever testing it
   against a nonlinear corrector. If it is unsafe, a round-level rule is wrong right now.
3. **What quantity actually predicts value-add?** Raw coherence with the target is inflated by
   the component both fields share with the condition. The quantity DPI implies should govern
   value *over a direct condition->HF model* is coherence after the condition-predictable part
   is removed — which is identically 0 for any deterministic function of c. That statement has
   never been measured on a field-valued benchmark (websearch D4: open as a measurement), and
   the size of the *real* LF's partial coherence (what a genuine coarse solve carries beyond c)
   is unknown on all six panel datasets.
4. **Does a realisation-carrying-but-mismatched intermediate beat the conditional mean?**
   Option (A)'s premise. It is answerable at **zero emulator-training cost**: the
   nearest-condition train LF field IS a draw from the empirical p(LF | c), and k-NN averaging
   sweeps continuously from that sample (k=1) to the conditional mean (k=N). Nobody has scored
   that ladder, on train or test.
5. **Is B1's ifc_poisson result a corrector result at all?** `paired_real_lf=false`,
   `attribution.valid=false`, and the 87.02 -> 2.99 move came from fitting the corrector on the
   emulator's own output — an ordinary pseudo-LF->HF regression, not a defect correction. Any
   ladder must carry the flag and keep ifc report-only for the law.
6. **What closes the stream honestly?** If (2)-(4) come out as predicted, the stream has a
   mechanism-carrying negative with a number and a reusable, *calibrated* precondition. If any
   comes out the other way, a round-level rule is falsified. Either outcome is a result; nobody
   knows which.
