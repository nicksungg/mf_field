# Summary so far — Stream `r3s3_lf_value`, Batch 1

## 1. Websearch findings and prior-art verdict

Source: `mffp_autoresearch/round3/websearches/r3s3_lf_value/batch_1/report.md` (4 iterations, 12 WebSearch calls, 8 primary bodies read through `urllib.request`; `WebFetch`/`curl` were intercepted in that agent's environment and routed around).

Three verdict rows:

- **D1** — matched, budget-matched +/-LF-at-train contrast for a condition-only field surrogate on the completeness-certified panel: **preempted-but-MF-composition-open**.
  Open surface is the four-clause composition: "(a) LF **absent from the test path by construction** (stripped view) ...; (b) a panel carrying an explicit **completeness certificate** ...; (c) the **copy-LF denominator** ... plus the ifc `affine_on_hf_train` floor; (d) N_hf = 5 on the ifc ladder with a certified `min_claimable_effect`. **The finding must be the measured number, never the ablation genre.**"
- **D2** — identifiability vs trainability on `sharp__cahn_hilliard`: **preempted-but-MF-composition-open**; the discrimination "has a name" (statistical-to-computational gap, `https://arxiv.org/pdf/2502.04282`), so the card may not claim the concept, only the measurement.
- **D3** — distillation from an LF-consuming teacher: **preempted (cite)**; ship only as a cited baseline arm, and pre-register the documented PFD non-monotone failure.

"For the brainstormer" instructions I am bound by: quote D1 verbatim on any +/-LF card; write the rate-vs-information framing (Lopez-Paz et al. 2016) as a *pre-registered expectation*, not a discovery; carry the negative-transfer citation (`https://arxiv.org/abs/2410.12690`) so a certified null is publishable.
The websearcher's anchor arithmetic (best-floor 38.63, B3 at 16.7606) **predates the final panel rebuild** and is superseded by `state/anchors/launch_anchors.json` (section 3 below) per the orchestrator's note.

## 2. Section 12 conventions, verbatim

Round-3 `program.md` section 5 states: "Round-2 section 12 methodological rules apply verbatim". The stream's conventions are therefore `round2/program.md` 12.3, quoted verbatim:

> ### 12.3 `r2s3_lf_train_signal` (lever)
>
> - **Question**: LF as training-only signal. Candidate mechanisms (spec 6): distillation from an LF-consuming teacher (round-1 families in role 5.10b — teacher at train, absent at test), LF-pretrain -> HF-finetune, auxiliary multi-fidelity losses (predict LF and HF jointly from condition).
> - **The stream has a mandatory declared baseline**: `mf_fno_transfer_film` (factory zoo champion) IS LF-pretrain->HF-finetune from the condition vector (verified 2026-07-31: its test input is `cond_by_fid` only; it runs on the stripped view unmodified). Any r2s3 pretrain/finetune proposal must either score it as the baseline arm or cite how it differs — an undifferentiated re-proposal is a rebadge (reviewer FAIL, 5.10).
> - **revin_lf two-scaler finding** (r1 s5): exact at LF-pretrain, 3.1% proxy at HF — normalization transfer across fidelities is a solved sub-problem; reuse it, don't rediscover it.
> - **Nested-ladder degeneracy** (r1 report 6) directly constrains this stream: with aligned/nested ladders, "multi-fidelity" training pairs degenerate toward top-rung replication — LF-as-signal designs must state what information the LF rungs add that the HF rung does not already contain (spectral truncation structure, more samples at low rungs on ifc_poisson: 70 lower-fidelity vs 5 HF).
> - The **unified normalization eligibility rule** (r1 s2, checks 0-6) governs any per-sample normalization proposal; spread is not the decider.
> - Uses the existing 400 aligned samples only (5.11).

Also binding from the section-12 preamble (ADR r2-0004): **registration of model-side lifts** (vendor the interpolators from `eval/panel_data.py` or use `factory_mffp/models/_common/lf_registration.py`; a bare `F.interpolate`/`zoom` on a panel dataset is a reviewer FAIL) and **target-scaler pre-flight** (`tools/target_scale_spread_audit.py` on `sharp__phase_field_crystal_2d` before training).
Round-3 `program.md` section 2 adds the **affine-floor rule**: every card reporting an ifc number reports the fitted `affine_on_hf_train` floor next to it (ifc_poisson skill 1.5938, ifc_heat 0.9584).

## 3. Within-stream prior cards

Round 3 has no batch-0 card for this stream (no `round3/experiment_cards/` yet), so the within-stream lineage is round 2's `r2s3_lf_train_signal` B1-B4 (all `status: complete`, all `reopen_candidate: false`).

- **B1** (`round2/experiment_cards/r2s3_lf_train_signal/batch_1/B1.json`) — multi-rung native-resolution supervision; cratered; priced the ifc information value of disjoint LF rows at **+3.2317** skill units against **-7.3497** delivered through the network.
- **B2** (batch_2) — matched budget-equal +/-LF at N_hf ~ 5; established the step-matched / normalization-matched arm protocol this card inherits; measured the LF-replicated-at-HF-conditions penalty as net harmful (ifc -1.2860, ch -0.7080).
- **B3** (batch_3) — the panel +/-LF contrast (`A0_nolf` vs `A1_lf_cov`), 33 legs, one SLURM job (66196690), **55 min wall** (18:21 -> 19:16, ~1.7 min/leg, verified in `mffp_autoresearch_outputs/round2/r2s3_lf_train_signal/B3/slurm/*.out`). Its clauses F1 and F2 were **falsified**. Its recipe (`models_r2/r2s3_coverage_panel`, width 64, 4 blocks, `pinned_min_rung_nyquist`, per-rung `max|y|` scaler, `steps = epochs x 25`, AdamW 1e-3 / wd 1e-5 / cosine / clip 1.0, `_step_rng(seed, step)` resume contract) is the proven substrate; family code lives at `models_r2/r2s3_coverage_panel/` on branch `round2/exp-r2s3_lf_train_signal-B3` (commit dfcd46c6b51b5fe0bd533b9c670a7cdbf9d13830).
- **B4** (batch_4) — training-free substitution audit on B3's dumps. Key results: the ch +/-LF effect is **structural, not amplitude** (no-LF median per-sample cosine **0.0003-0.0385** vs LF **0.962-0.964**; E_struct 99-125x mce); train-fitted calibration heads are the **identity by construction** (sd(log optimal scale) <= 2.0e-06 on the 5 fit rows); the stream **closed formally on B4**.

B4's handoff, verbatim from `7_gap_and_future.open_question`: "whether 5 HF rows plus a 19-dimensional condition vector fail to DETERMINE that phase (an identifiability limit, in which case no training recipe can close the gap without LF or more HF rows) or merely fail to let this optimiser FIND it in 200 epochs (a trainability limit, closable without LF)", and `next_direction`: "it belongs to a FUTURE ROUND, not to a B5: it needs a rank/identifiability probe on cahn_hilliard's condition design plus at least one HF-budget rung above 5, which is a new stream premise".

## 4. Cross-stream cards

- **`r2s4_diag-B2`** — **the LF-as-auxiliary-target channel is CLOSED**: "|T1-T0| below its operative threshold in 15/15 dataset x N cells ... the mechanism is that the aux target is a duplicate of the main task, cos >= 0.997 and delta-identifiability <= 0.0015". Its open question names the one remaining channel as input-side privileged information (an LF-consuming teacher), i.e. the websearcher's preempted D3.
- **`r2s4_diag-B4`** — ifc few-HF anatomy: 65.4 % of the n=5 error is removable by a per-sample oracle gain vs 0.19 % by a global one; coverage/representativeness statistics select the **wrong** HF rows (Spearman -0.60 against measured Shapley value), which binds any subset-selection gate; the certified ifc mce 0.9377041 is an initialisation-replicate max-min whose own sampling distribution runs 0.202-2.778.
- **`r2s1_direct-B2`** — post-hoc blend/hedge stages are not neutral; a comparison decided at such a stage is a decorrelation verdict, not an accuracy verdict. (This card appends no blend stage.)

## 5. Reopen candidates

None. All 14 round-2 cards carry `reopen_candidate: false` (verified by reading every `round2/experiment_cards/*/batch_*/B*.json`), and round 3 has no prior cards for this stream.

## 6. What is UNKNOWN

**(a) The affine-coverage premise has silently inverted, and nobody has written it down.**
I computed the design ranks myself on the live stripped view (`round2/stripped_data`, the repaired arrays) using B3's own draw rule `np.sort(np.random.default_rng(s).permutation(400)[:5])`:

| dataset | cond_dim d | rank[X_hf,1] (draws 0/1/2) | deficit m = d+1-rank | B3's m (old panel) |
|---|---|---|---|---|
| pfc | 18 | 5/5/5 | **14** | 0 |
| allen_cahn | 19 | 5/5/5 | **15** | 0 |
| fisher_kpp | 50 | 5/5/5 | **46** | 0 |
| cahn_hilliard | 19 | 5/5/5 | 15 | 15 |
| ifc_poisson | 5 | 5 (native) | 1 | 1 |
| ifc_heat | 3 | 4 (native) | **0** | (not in panel) |

Option-A completeness certification pushed ac 3->19, fk 2->50, pfc 2->18 condition dims, so **five of six panel datasets now carry a large affine coverage deficit at N_hf = 5, and `ifc_heat` is the only m = 0 dataset**. B3's F2 — "claimable LF value is confined to the two datasets with an affine coverage deficit" — was falsified on a panel where 4/6 had **no** deficit; on the honest panel that test has never been run, and `ifc_heat` is now the panel's natural negative control for the coverage mechanism.

**(b) The ifc ladders are nested now, not disjoint.** I verified condition overlap against the HF rung on the live view: ifc_poisson and ifc_heat both give overlap **5 of 100 / 5 of 50 / 5 of 20** at rungs 8/16/32 (round-2 B1 measured pairwise **disjoint** rungs, exact overlap 0). Uncovered conditions per rung are 95/45/15. The "null-direction supply" that carried B3's ifc win still exists but is now mixed with replication of the HF conditions — the configuration B2 priced as net harmful.

**(c) B3's re-scored anchor contains an unexplained 130x asymmetry between the two ifc datasets.** From `state/anchors/launch_anchors.json`, `r2s3_lf_train_signal-B3` per-dataset mean skill: pfc 50.3973, ac 186.7596, fk 172.2459, ch 12.8723, ifc_poisson **9.5116**, ifc_heat **0.0725**; seed geomeans [15.2085, 15.8527, 15.7065], mean 15.5893, CI [15.2071, 15.9714]. On the repaired ladder its ifc_poisson arm is now **worse than the `nn_condition` floor (8.0409)** and 6x worse than `affine_on_hf_train` (1.5938) — the round-2 ifc coverage win did not survive the repair — while on ifc_heat the same arm is 13x better than that dataset's affine floor (0.9584). Nothing in the round-3 state files explains this, and **no matched no-LF control has ever been scored on either repaired ladder**.

**(d) Whether ch's near-orthogonal no-LF failure is identifiability or trainability** (B4's handoff, and the round-3 stream question's own words "ch identifiability-vs-trainability") is untouched; the discriminating arms have never been run.

**(e) What LF-at-train is worth in HF-row units.** No card has priced the +/-LF effect against simply spending more of the existing 400 HF rows.

**(f) `ifc_heat` has no `min_claimable_effect` in either noise-floor file.** `state/anchors_repaired/noise_floor.json` is round-1-rescaled and PROVISIONAL (keys: hz, ifc_poisson, ac, ch, fk, pfc; values 10.6811 / 0.2399 / 16.4223 / 1.1604 / 158.3322 / 8.8595); `round2/state/noise_floor.json` is the round-2 certified file (hz 2.9530, ifc 0.9377, ac 0.8797, ch 0.0912, fk 0.00071, pfc 0.2130) but was certified on pre-repair data. r3s4-B1 is pre-directed to certify the repaired-panel mce; until it lands, any ifc_heat effect is reportable but not claimable.

**(g) An infrastructure unknown I resolved by reading git, load-bearing for the recipe.** `round3-substrate` (8aae33a7fab11ef8234f4bb7158c2bc1a8b4bf51, 2026-08-04) predates ADR r3-0002/r3-0003 and carries a **stale `round2/eval/copylf_baselines.json`** (pre-ac-trim, pre-pfc-box, no `ifc_heat` entry) plus a stale `state/anchors_repaired/floors.json` (pfc `nn_condition` skill 95.8606 vs the current 65.0557; ac `n_test` 100 vs 78). A worktree forked at the substrate would score every skill against wrong denominators and would reject `--datasets ifc_heat` outright. Separately, `round2/eval/panel_data.py::load_config` reads **`round2/project.yaml`**, so `--datasets panel` resolves to the *round-2* panel (helmholtz in, ifc_heat out) — the recipe must always pass explicit dataset names.
