# Summary so far — Stream `r2s2_stacked`, Batch 1

Stream class: **lever**. Question (`project.yaml streams[1]`): *"does a
condition->pseudo-LF emulator feeding the frozen round-1 DC corrector beat
direct condition->HF prediction, and how much is lost to pseudo-LF
distribution shift?"*

---

## 1. Websearch findings + prior-art verdict

Source: `websearches/r2s2_stacked/batch_1/report.md` (4 iterations, 12
WebSearch / 16 WebFetch calls, `ENOUGH` declared — cap not hit).

Three candidate directions were adjudicated:

- **D1** (condition→pseudo-LF → *frozen* DC corrector, vs direct condition→HF):
  **`preempted (cite)`**. Xu, Cao, Yuan, Meschke 2023
  (https://arxiv.org/abs/2310.00057) already run a frozen LF DeepONet subnet
  whose *predicted* LF output feeds a residual subnet; Yang et al. 2025
  (https://arxiv.org/html/2503.17941v1) names the class outright.
  What remains open: reuse of a corrector **trained on real coarse solves**
  behind an emulator (deliberate train/test input mismatch), evaluation
  against **copy-LF skill** in a no-solver-at-test regime, and the
  N_hf in {5, 400} sharp-field regime.
- **D2** (frozen / fine-tuned / end-to-end arms decomposing emulator error vs
  pseudo-LF distribution shift): **`preempted-but-MF-composition-open (cite)`**.
  Yang et al. 2025 ablate fine-tune/full-tune/linear-probe; CALM-PDE §4.3
  (https://arxiv.org/abs/2505.12944) reports end-to-end more stable than
  two-stage; Conti et al. 2025 (https://arxiv.org/html/2510.13762v1) freeze
  lower fidelity levels but **still require LF inputs at test**. Open: the
  **attribution** — no fetched source decomposes stacked error into emulator
  error + downstream distribution shift, nor uses the **frozen - fine-tuned
  delta as the shift estimator**, on field-valued PDEs.
- **D3** (LF as a supervised intermediate bottleneck inside one net):
  **`preempted (cite)`** — Meng & Karniadakis, Howard et al., PANIS. Arm, not
  mechanism.

Report §"Dead ends" records that **no source quantifies a real-LF-trained
corrector's degradation on emulated LF inputs** (iteration_4). The
websearcher's directive to me is explicit: *"You may not claim a new mechanism
for the stack ... Frame B1 as measuring a known composition in an unmeasured
regime"* and *"Put the stream's claim on D2, not D1."*

## 2. §12 conventions, verbatim (program.md §12.2)

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

Anchor (`state/anchors/r2s2_stacked.json`): **best-floor panel geomean 23.0636**
(`anchor_type: best_floor_panel_geomean`, `provisional: false`). Per-dataset
best floors: helmholtz 3.344 (zero) / pfc 59.812 (mean) / allen_cahn 269.196
(NN) / fisher_kpp 11.993 (mean) / cahn_hilliard 23.180 (NN) / ifc_poisson
10.055 (NN).

## 3. Within-stream prior cards

**None.** `experiment_cards/r2s2_stacked/` is empty (verified by glob: zero
`round2/experiment_cards/*/batch_*/B*.json` exist round-wide). B1 is the
stream's first card, and `state/r2s2_stacked/current_batch.txt` confirms
batch 1.

The stream's substantive prior is round-1's `s4_hybrid_routing-B3`
(`round1/experiment_cards/s4_hybrid_routing/batch_3/B3.json`), whose
`dc_cleaned` arm is the sub-component §12.2 directs me to reuse. I parsed its
part-5 `per_arm_nrmse` and restated skill under the round-2 corrected
denominators from `state/anchors/floors.json` (model nRMSEs are unchanged;
only the denominator moves):

| dataset | `dc_cleaned` nRMSE | r1 skill | corrected ref | **r2 skill** | best floor |
|---|---|---|---|---|---|
| ext__helmholtz_2d | 0.329450 | 1.0000 | 0.299033 | **1.1017** | 3.344 |
| sharp__phase_field_crystal_2d | 0.000333 | 0.0074 | 0.007381 | **0.0451** | 59.812 |
| sharp__allen_cahn_2d | 0.000197 | 0.0122 | 0.001781 | **0.1105** | 269.196 |
| sharp__fisher_kpp_2d | 0.003579 | 0.0571 | 0.021450 | **0.1669** | 11.993 |
| sharp__cahn_hilliard | 0.038569 | 0.4400 | 0.041803 | **0.9226** | 23.180 |
| ifc_poisson | 0.055631 | 1.5453 | 0.036 | **1.5453** | 10.055 |

**Panel geomean: 0.1232 (r1 denominators) -> 0.3306 (corrected).** This is
§12.2's mandated restatement, and it is the single most useful number for
designing B1: with **real LF at test**, the DC corrector sits at 0.3306, i.e.
**69.8x better than the best-floor anchor 23.0636**. That factor of ~70 is
the headroom band inside which the pseudo-LF stack must land, and where it
lands *is* the value-of-the-LF-bottleneck measurement.

Architecture facts read from
`round1/worktrees/s4_hybrid_routing/B3/models_r1/s4_router/`:
`model.py::FNO2d` is *already* `cond (B,cond_dim) -> field (B,H,W)` (FiLM at
every block, coords-only input) — the pseudo-LF emulator backbone exists
ready-made; `lsi_filter.py::fit_transfer/apply_transfer` is the closed-form
Wiener `T(k)` (zero trained parameters); `local_corrector.py::LocalCorrector`
is `(LF_up, coords, cond) -> Delta` with a zero-init head. Vendoring precedent
and `manifest.json` pin format are established by that family
(`base_family_pins_sha256_16`, `vendored_unchanged`, ...).

## 4. Cross-stream prior cards

**None** — no round-2 cards exist in any stream. Forward couplings I must
respect rather than read: `r2s1_direct`-B1 produces the direct condition→HF
comparator that §12.2's falsification framing names, and `r2s4_diag`-B1 is
pre-directed to replace the provisional noise floor. Both run *in parallel*
with this card, so neither result is available at design time — the design
must carry its own in-job comparator (drift-class rule, r1 report §5.6: when
n_eff/N < 1%, only in-job paired controls are controls).

## 5. Reopen candidates

**None.** Verified by scanning every round-1 and round-2 card for
`reopen_candidate: true` — zero hits round-wide.

## 6. What is UNKNOWN (the design surface)

1. **Is condition→LF any easier than condition→HF here?** This is the stream's
   load-bearing premise and it is *unmeasured*. I checked the grids: on the
   sharp panel the corrector's `S6_LF_FID=max` rung is only **r = 2** coarser
   than HF (cahn_hilliard 128^2 LF vs 256^2 HF; pfc 64^2 vs 128^2); helmholtz is
   r = 4 (24^2 vs 96^2). At r = 2 the "bottleneck" buys almost nothing
   dimensionally — its only possible value is **spectral truncation** (the LF
   target is band-limited, hence smoother). This is exactly the
   **nested-ladder degeneracy** (r1 report §6): the emulator and a direct
   condition→HF model may be learning nearly the same function. Unknown
   whether the smoother target is enough of an advantage to survive the
   corrector's error amplification.
2. **ADR r2-0003 propagates into this stream and nobody has said how.** On
   pfc / fisher_kpp / allen_cahn the condition vector carries **no IC
   parameters**, and the ADR measured the missing driver *in the LF field*
   (pfc: nearest-condition train pair differs by 1.149 in HF and **1.148 in
   `train_l1.npz`**; fisher_kpp 0.343 HF / **0.412 LF**). Therefore
   **condition→LF is stochastic on exactly the same three datasets** — the
   emulator inherits the identical conditional-mean bound, and a
   condition-only emulator can at best output E[LF|c], a featureless field.
   What is unknown is whether the downstream corrector then degrades
   gracefully or catastrophically, and whether the stack collapses all the way
   to the `train_mean` floor there. Nobody has measured this; it is cheap to
   measure and it is the sharpest thing this card can add.
   Contrast: **cahn_hilliard** carries 16 `ic_c*` dims of its 19 (verified in
   `stripped_data/sharp__cahn_hilliard/meta.json param_names`), so
   condition→LF is near-deterministic there — cahn_hilliard is the one panel
   dataset where the stacking hypothesis is *identifiable*.
3. **How much of dc_cleaned's credit survives the corrected reference?** The
   restatement above already shows pfc moving 0.0074 -> 0.0451 (6x) and
   allen_cahn 0.0122 -> 0.1105 (9x). The wrap-seam caveat (deep-bulk ratio
   0.908 on pfc) says more of that credit may be boundary-rim artifact.
   Unknown how much survives once the corrector's *input* upsampling also uses
   the corrected convention (round 1's "corrector-input wrap-seam fix" was on
   the between-rounds fix list and was **never applied**).
4. **Is the distribution shift separable from emulator error at all?** The
   websearcher found no source that decomposes it. Whether
   `frozen - fine-tuned` is a *usable* shift estimator here (vs being swamped
   by fine-tuning capacity effects) is unknown and is the stream's claim.
5. **Does ifc_poisson unlock?** In round 1 every DC arm collapsed to a
   pre-registered no-op there because the *test* split ships no LF
   (`S6_FALLBACK_NO_TEST_LF=champion`). A pseudo-LF emulator supplies test-time
   LF for the first time, so the DC lineage becomes runnable on ifc_poisson —
   but N_hf = 5, so anything measured is anecdote-grade.
6. **Direction of the frozen-vs-end-to-end result.** CALM-PDE §4.3 predicts
   end-to-end >= two-stage; Yang et al. found *partial* fine-tuning beat both
   full-tuning and linear probing. Unknown here; the websearcher asks that the
   expectation be pre-registered so a frozen-arm win is reportable as an
   inversion rather than rationalized after the fact.
