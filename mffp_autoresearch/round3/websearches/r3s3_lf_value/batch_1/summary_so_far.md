# Summary so far — stream `r3s3_lf_value`, batch 1

## Regime and the round-3 change that matters

Round 3 keeps round 2's regime: LF coarse-solve fields are available **at train time only**; at test the model sees the condition vector alone, on the stripped view (`mffp_autoresearch/round2/stripped_data`, project.yaml `stripped_data_root`).
What changed is the panel (`mffp_autoresearch/round3/docs/adr/0001-launch-panel-composition.md` D1/D3/D4+A1): every scored dataset is now **completeness-certified** — the HF field is exactly reconstructible from the stored condition vector (band-limited parametric ICs, reconstruction rel-L2 = 0.0).
Condition dimensions on the repaired panel (`state/anchors_repaired/floors.json`): pfc 18, allen_cahn 19, cahn_hilliard 19, fisher_kpp **50**, ifc_poisson 5, ifc_heat 3.
`n_train_hf` = 400 on the four sharp datasets, **5** on both ifc datasets.

This directly reframes the stream's question (program.md §4, project.yaml `streams`): *what is LF-at-train worth on the honest panel?*
In round 2 an unknown share of LF's measured value was LF **supplying the unexported random IC** (round-2 program §13.1, ADR r2-0003 caveat).
That channel is now closed by construction on the sharp panel, so LF-at-train can only pay through (a) parameter-space **coverage** (LF rows at conditions with no HF row), (b) **amplitude/calibration**, (c) **optimisation/trainability** help, or (d) spectral-truncation curriculum on nested ladders.
Whether any of those survives condition completeness is exactly the measurable, falsifiable thing this batch should set up.

## Where the stream stands (round-2 predecessor `r2s3_lf_train_signal`, read as inputs)

- **B1** (`round2/experiment_cards/r2s3_lf_train_signal/batch_1/B1.json`): multi-rung native-resolution auxiliary supervision. LF arms were *worse* than the no-LF control on ifc_poisson even with a perfect per-sample gain oracle; the failure traced to a shared `max|y|` scaler (1772x HF-loss deflation) and unpinned mode clipping. Architecture tax at matched information: a 4.8 M-param decoder recovered a 6-coefficient affine law to 60-130 % relative error where OLS on 20 LF rows got 4.5 %.
- **B2** (`.../batch_2/B2.json`): budget-matched +/-LF at N_hf ~ 5 with LF at **uncovered** conditions plus a null-direction penalty. Coverage arm won; the penalty family was net-negative (collateral in the row space).
- **B3** (`.../batch_3/B3.json`): the panel-completion matched +/-LF contrast, `A0_nolf` vs `A1_lf_cov`, step/budget matched. Certified effect on exactly **3** datasets under the operative threshold reading — ifc_poisson +5.98, cahn_hilliard +14.78, fisher_kpp +1.31 skill units — with allen_cahn/pfc/helmholtz failing. B3 is the **round-3 model anchor**: `state/anchors/launch_anchors.json` cards `r2s3_lf_train_signal-B3`, panel geomean **16.7606**, CI [16.3658, 17.1555], per-dataset skills pfc 76.37 / ac 190.36 / fk 172.25 / ch 12.87 / ifc_poisson 9.51 / ifc_heat 0.0725 — i.e. the LF-at-train coverage arm is currently the **best card on the round-3 panel**, well under the launch best-floor geomean **38.63**.
- **B4** (`.../batch_4/B4.json`, diagnostic): substitution audit. LF-free achievable calibration heads absorb ~78 % of the ifc effect but ~0 % elsewhere because the 5-row fit set is informationally empty; on cahn_hilliard the no-LF arm's predictions are essentially **uncorrelated with truth** (median per-sample cosine 0.0003-0.0385) while the LF arm is aligned (0.962-0.964) — LF supplies the field's **phase** there. B4's closing open question is verbatim the r3s3 seed: *is ch's no-LF failure an **identifiability** limit (5 HF rows + 19-D condition cannot determine the phase) or a **trainability** limit (the optimiser cannot find it in the budget)?*

## Floors, anchors, and the noise-floor rule

Launch best-floor geomean 38.63 with per-dataset training-free floors pfc 64.45 (train_mean), ac 507.85 (nn_condition), fk 390.70 (train_mean), ch 23.18 (nn_condition), ifc_poisson 8.04 (nn_condition), ifc_heat 1.394 (nn_condition) (`state/anchors/launch_anchors.json`).
Mandatory extra ifc arm (program.md §2 affine-floor rule): `affine_on_hf_train` ifc_poisson skill 1.5938 (oracle-affine residual 5.4e-16 — the map is exactly affine), ifc_heat 0.96 — an ifc claim that does not beat this has learned nothing beyond linearity.
`state/anchors_repaired/noise_floor.json` is **PROVISIONAL** (r3s4 re-certifies mce); its `min_claimable_effect` values are pfc 8.86, ac 16.42, fk 158.33, ch 1.16, ifc_poisson 0.24. Any claim inside the anchor CI or below the floor is noise, not signal.

## Prior websearch coverage to reuse, not re-derive

Round-2 `r2s3_lf_train_signal` websearch reports `round2/websearches/r2s3_lf_train_signal/batch_{1,2,3,4}/report.md` already returned: LUPI / privileged-information distillation `preempted-but-MF-composition-open`; multi-resolution auxiliary heads `preempted-but-MF-composition-open`; LF-as-null-space-coverage `preempted-but-MF-composition-open`; the matched +/-LF ablation genre itself `preempted-but-MF-composition-open`; LF-free amplitude/gain heads `preempted-but-MF-composition-open`; per-rung scalers / HF-Nyquist-pinned modes `preempted` (standard convention, bug fix only).
The two in-repo literature reports (`docs/reports/MF_Leaderboard_Beaters_2026_Report.md`, `docs/reports/MF_Sharp_HighFreq_Report.md`) are prior websearches by another agent but target the **LF-at-test** fusion regime (IRNO refinement, generative residual transport, misaligned LF/HF fusion); they carry little to this stream beyond the standing spectral-bias and metric caveats — cite, do not re-derive.

## Open questions this batch must serve

1. Does condition completeness **destroy, shrink, or leave intact** the certified LF-at-train effect (the re-measurement is now on repaired denominators, so round-2 numbers do not transfer)?
2. ch identifiability vs trainability at 19-D complete condition — is there literature separating "auxiliary/privileged data adds information" from "auxiliary data eases optimisation"?
3. Is any of that composition already published, given the project's **0-for-4 novelty record** (round-2 program §13.3: recall is not citation; every verdict must be retrieval-grounded).
