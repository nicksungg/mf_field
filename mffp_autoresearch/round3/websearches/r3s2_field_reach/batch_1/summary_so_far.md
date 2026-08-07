# Summary so far — `r3s2_field_reach`, batch 1

## What the stream is being asked

Round-3 program (`round3/program.md` §1, §4) poses r3s2 as a **gap** stream:
"Can any architecture (including internal IC reconstruction from the complete condition vector) recover field-level structure the scalar-deep law cannot — and if not, is the negative certifiable?"

The regime is unchanged from round 2 — LF fields at train time only, condition vector alone at test — but the data changed.
Per `round3/docs/adr/0001-launch-panel-composition.md` D1, the pattern-former datasets were regenerated under **option A: band-limited parametric ICs stored in the condition vector**, and every scored dataset now carries a COMPLETE certificate (HF field exactly reconstructible from the stored condition vector; reconstruction rel-L2 = 0.0).
Measured on `round2/stripped_data/*/train_l3.npz` (2026-08-07): condition dims are now pfc 18, allen_cahn 19, cahn_hilliard 19, fisher_kpp 50, against fields of 128² = 16384 (pfc) and 256² = 65536 (ac/fk/ch) cells.
ADR D1 also records that **option C (IC field as a model input) was NOT formalized** — no round-3 dataset ships an IC field, so any IC-field intermediate must be *reconstructed inside the model* from the condition vector, which the program explicitly puts in scope ("any deterministic feature map of it is fair game"); a numerical PDE solve at test remains banned.

## What round 2 established that constrains this stream

From `round2/docs/round2_report.md` §1, §3, §4 and the round-2 `r2s2_stacked` card lineage:

- **Scalar-deep verdict.** After granting the closed-form condition→level law, the residual carried 40–211× each dataset's certified mce of *oracle* value with **zero usable condition reachability**, while the paired LF field carried it almost perfectly (median fluctuation cosine ≥ 0.997) — "the class headroom is exactly one scalar per sample, and that scalar is free from LF" (r2s2-B3 parts 6–7).
- **Constraint I8** (r2s2-B1 parts 6–7): a learned deterministic intermediate field is a *re-parameterisation* of the condition→HF class, never a new information channel. B1's stack took the round's best geomean (14.0755) while the downstream corrector added 0.0061 units; 99.98% of the stack's cahn_hilliard error was stage-1 (emulator) error.
- r2s2-B3 part 7 **forbade proposing another condition-only field corrector inside round 2** and recorded "is the class's correct next output a certified impossibility statement?" for a future round — this stream is that future round.
- **The excuse that is now gone**: r2s1/r2s2's negatives were partly explained by ADR r2-0003 (per-sample random ICs absent from the condition vector ⇒ condition→HF stochastic ⇒ deterministic models bounded by the conditional-mean floor). ADR r3-0001 D6 states the round-2 aleatoric exclusion of criterion 2 "no longer applies to the sharp panel". **The round-2 negatives are therefore not automatically transferable; the point of r3s2-B1 is that they must be re-measured on complete conditions.**

## Bars this batch must design against

`round3/state/anchors/launch_anchors.json` — best-floor panel geomean **38.63**; per-dataset best training-free floors: pfc train_mean 64.454, allen_cahn nn_condition 507.853, fisher_kpp train_mean 390.701, cahn_hilliard nn_condition 23.180, ifc_poisson nn_condition 8.041, ifc_heat nn_condition 1.394.
Program §2 adds the **affine-floor rule**: ifc_poisson is EXACTLY affine in the condition (oracle-affine residual 5.4e-16) and ifc_heat's 6-dof affine fit on 5 HF rows already beats the paper bar (skill 0.958) — every ifc claim reports `affine_on_hf_train` alongside.
`round3/state/anchors_repaired/noise_floor.json` is **PROVISIONAL** (r3s4 re-certifies mce); its round-2-rescaled `min_claimable_effect` values (ac 16.42, ch 1.16, fk 158.33, pfc 8.86, ifc_poisson 0.240) are the interim "is this signal?" yardstick.
`round3/state/HOLD.json` is currently SET (allen_cahn task-void rows, cahn_hilliard outlier domination) — allen_cahn's test split is already trimmed to n=78, and any ac/ch threshold in this batch inherits that caveat.

## Prior websearch this loop must not re-derive

- `round2/websearches/r2s2_stacked/batch_{1,2,3}/report.md` — batch 1 already returned `preempted` for "condition→pseudo-LF emulator → frozen corrector" (Xu et al. 2023 arXiv:2310.00057; Yang et al. 2025 arXiv:2503.17941; Meng & Karniadakis arXiv:1903.00104) and `preempted-but-MF-composition-open` for the frozen/finetuned/end-to-end attribution arms (CALM-PDE arXiv:2505.12944 §4.3). **Round-3 rule (program §13.3): those may not be re-cited from the prior report — anything cited in THIS batch's verdict must be fetched in THIS loop.**
- `docs/reports/MF_Sharp_HighFreq_Report.md` line 101 (the zoo's discrepancy/stack families already run on "model-generated LF only" and are weak), lines 226/295 (band-split at the coherence<0.7 cutoff), line 260 (fit the LF↔HF transfer kernel in one FFT pass, then unroll proximal steps).
- `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` rows 46/123/131 (transfer-FiLM champion; MFFM cascaded refinement; function-space flow matching from LF), [LF-11] MF-DeepONet arXiv:2503.17941.

## Open questions this batch's search should serve

1. Is **"decode a finite IC parameterisation into an IC field inside the model, then apply an operator / rollout to the readout time"** published prior art? (The round-3-specific "internal option C".)
2. Does anything published **re-test a stacked pseudo-LF pipeline once the condition vector is complete** — does completeness change the emulator/corrector attribution, or is the distribution-shift story the same?
3. Is there methodology for **certifying a negative** — a reachability / impossibility statement for a parametric surrogate class — that this stream could adopt rather than invent?
