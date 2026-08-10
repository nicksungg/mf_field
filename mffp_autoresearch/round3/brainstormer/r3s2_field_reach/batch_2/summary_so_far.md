# Summary so far — Stream `r3s2_field_reach`, Batch 2

## 1. Websearch findings + prior-art verdict

Source: `mffp_autoresearch/round3/websearches/r3s2_field_reach/batch_2/report.md` (5 iterations, 19 WebSearch calls, 10 successful fetches, cap hit).
Three directions adjudicated; **nothing is `novel`** — "the project's record is now 0-for-7".

**E1** — regularised / band-limited / shrunk estimation of the LSI Wiener `T(k)` at `n_fit ~ 3`, `ridge = 0`: verdict **`preempted (cite)`** — *"usable ONLY as an instrument repair, never as a contribution"*.
Open piece, verbatim: *"Only the **measurement**: that this published stack's whole panel-level 3-seed spread was 100 % attributable to an unregularised band above the LF Nyquist, and that a one-line ridge/band-limit removes it against the pre-registered prediction (ifc_poisson seed-2 2.041 -> ~0.171; panel range [10.32, 17.83] -> ~[10.3, 10.9]), acceptance-checked by `tools/lsi_transfer_stability_audit.py`. Presenting ridge/band-limiting as the *idea* is a rebadge"*.
Citations: arXiv 1511.07030 (spectral-matrix shrinkage when DOF barely exceed dimension), 1810.08360 (LOOCV choice of the shrinkage coefficient, "near-oracle"), 2606.03936 (FreqNO-DPS, closed-form per-band weighting of a **frozen** operator).

**E2** — route contrast, direct condition->HF vs condition->pseudo-LF->corrector at matched total budget, no LF at test: verdict **`preempted-but-MF-composition-open (cite)`**.
Open piece, verbatim: *"No fetched source runs a **direct parameter->HF arm against a coarse-intermediate arm at matched total optimizer budget where the coarse field cannot be produced at inference**. Every MF comparison retrieved either calls the LF model online (2512.02868's "exact LF"; the MF-ROM line) or feeds a real coarse solve to the corrector (2411.07576, INC). The open question is exactly: *is the LF intermediate worth its place in the graph when it must itself be hallucinated from the condition?* Prior is two-sided — 2512.02868 predicts the stack wins, 2606.17460 + in-repo `MF_Sharp_HighFreq_Report.md` line 101 predict it loses, B1's F2 already measured no resolvable value"*.

**E3** — approximability-vs-information attribution of the residual `cahn_hilliard` gap: **`preempted-but-MF-composition-open (cite)`**; Duraisamy (2604.20061) supplies vocabulary, diagnostic and reporting standard, and *"This verdict also preempts any claim that the `affine_on_hf_train` / `task_linearity_audit` accounting on the ifc cells is methodologically new"*.
Open is only *"The **paired** application ... used prospectively to rule a cell off-limits for capacity spending"*.

Instructions to me: build the card on **E2**, claim the *regime and the contrast* never the topology, pre-register **both** directions; put E1 on the card as a **repair with a pre-registered numeric prediction**; report fractional error-reduction units *and* band-limited error columns alongside skill; do not spend the batch on ch capacity/conditioning; on ifc cite Duraisamy before claiming anything and prefer the held-out selector between the affine closed form and the LF route.
Thresholds handed over: certified `min_claimable_effect` ac 18.6198 / ch 0.3612 / fk 10.3128 / ifc_poisson 0.6910 / ifc_heat 0.1640, panel `seed_mce` 0.5083; stream anchor 12.9556; training-free best floor 34.4198.

## 2. §12 conventions, verbatim

Round-3 `program.md` §5: *"Round-2 §12 methodological rules apply verbatim"*. The stacking/route conventions are round-2 §12.2 (`mffp_autoresearch/round2/program.md` lines 371-396):

> - **B1 is pre-directed by the spec** (Eloise's stacking proposal): train a FiLM-FNO **pseudo-LF emulator** (condition -> LF field) on the TRAIN LF data, feed the best round-1 corrector — the s6 DC lineage / s4-B3 `dc_cleaned` stage ... Arms: **frozen corrector / fine-tuned corrector / end-to-end**, to separate emulator error from distribution shift (the corrector was trained on real LF; pseudo-LF is off-distribution for it).
> - Declared-reuse rule (§5.10a): the corrector is a frozen test-time sub-component — the reuse IS the experiment. Its code lives in the round-1 worktrees (...); vendor the needed pieces into the round-2 family dir with provenance comments (round-1 branches are immutable).
> - Round-1 mechanism rules apply to the cleaning stage: **BC-match rule** ..., the **wrap-seam caveat** ..., and the **lineage-bound caveat** for any routing/eligibility rule.
> - **Failure is informative: if pseudo-LF -> corrector loses to r2s1's direct models, the LF representation is not a useful bottleneck — that is the stream's falsification framing.**

Also binding, round-2 §5 immutables 9-13 (lines 214-228):

> 9. **Stripped test view.** Models are evaluated ONLY against `stripped_data_root` ... Family code or scripts reading the original `data_root` at test time = reviewer **FAIL**. Train-side LF use is free (that is the round's question).
> 10. **Novelty guarantee / declared-reuse-only.** ... A round-1 model may appear ONLY as (a) a **declared frozen test-time sub-component** behind a new condition->pseudo-LF front end (the r2s2 design, where the reuse IS the experiment), or (b) a **training-time-only teacher** ..., never present at test. The reviewer answers "is this a rebadge of a round-1 family?" on every card.
> 11. **No new HF data, no LF-only pools** ...: the round runs on the existing aligned train samples only (400 per sharp dataset; 5/20/50 ladder on ifc_poisson).
> 12. **Floor arms mandatory** on every model card (§2.2).

And round-2 §12.1: *"N_hf on ifc_poisson is 5 — every claim there is anecdote-grade; prefer variance-reducing designs"*.

Round-3 amendments (`round3/program.md` §1-§2): *"Reconstructing the IC from the condition vector inside a model (an internal 'option C') is explicitly in scope ... Calling a numerical PDE solver at test time remains banned"*; scored panel = the 5 ADR r3-0004 datasets (pfc **report-only**, *"Any falsification clause or threshold citing pfc is void for claim purposes"*, B1 `adr_r3_0004_addendum`); the **affine-floor rule** — *"an ifc claim that does not beat this floor has learned nothing beyond linearity"* (ifc_poisson 1.5938, ifc_heat 0.9584).

## 3. Within-stream prior cards

`experiment_cards/r3s2_field_reach/batch_1/B1.json` — model, `status: complete`, `reopen_candidate: false`, `anchor_reference: null`, family `models_r3/r3s2_stack_ic`, 10 arms, 200 epochs, seeds 0/1/2, worktree HEAD `d5069a74`.
Verdict: H falsified through **F2** (the corrector leg) while **F1** (the reach leg) held.

Numbers that govern batch 2 (parts 5-7 + `state/anchors/r3s2_field_reach.json`):

- Stream anchor = E1_frozen 3-seed panel geomean **12.9556**, per-seed [10.7213, 10.3180, 17.8277]; per-dataset mean skill ac 83.5967 / fk 29.4519 / ch 8.6029 / ifc_poisson 21.4239 / ifc_heat 1.5730.
- M1: the ifc_poisson seed-2 blow-up is *"a CLOSED-FORM, DETERMINISTIC, SAMPLE-STARVED WIENER DECONVOLUTION DEFECT ... not a training instability and not new"* — `T_band_mean_abs` band 4 = 6.23981 (s0/s1) vs **66.21924** (s2), identical in r2s2-B1; 100 % of the seed-2 error in that band (`band_contribution_profile` [0.0012, 0.0272, 0.0763, **2311.94**]); `n_fit = 3`, `S6_LSI_RIDGE = 0`.
- M3 (testable): band-limit / Tikhonov above the LF Nyquist -> *"ifc_poisson seed-2 nRMSE falls from 2.041 toward ~0.171 ... panel 3-seed range from [10.32, 17.83] to roughly [10.3, 10.9]"*.
- M5: F1's 59x ac-vs-ch skill gap = 20.3x denominator x 2.14x real effect; report both units.
- M6/M11: *"everything that worked on this card happened at stage 1"*; the same frozen corrector fed **real** LF beats `affine_on_hf_train` by 2.7x (ifc_poisson) / 16x (ifc_heat), while the stack loses those floors by 2.58x-35.6x / 1.63x.
- M7: ch is approximability-limited (nn/random field-difference ratio 0.980) — *"Do not propose a B2 that assumes capacity or conditioning will fix ch"* (handoff).
- M12 (testable): *"a direct condition->HF head on the ifc cells, at any capacity, beats every arm on this card; a stack that CHOOSES between the affine closed form and the LF route on a held-out split dominates both"*.
- Part 7 `next_direction`: *"r3s2-B2 should be a ROUTE contrast, not another front-end contrast"*, carrying (1) the direct arm at *"the same total optimizer budget as the stack's arm_equal_total 300 epochs"* and (2) the T(k) repair.
- Budget accounting read from the B1 diag JSONs (`mffp_autoresearch_outputs/round3/r3s2_field_reach/B1/eval/diag_*_e200_s0.json`): tier 200, split 0.5 -> `E_emu = 100`, `E_dc = 100`, stage-2 arms spend **300** optimizer epochs. Emulator fit rows: **18** (both ifc cells, of 20 LF train rows) vs HF train rows **5**; 320 vs 400 on the sharp cells.

## 4. Cross-stream cards

- **r3s4_audit-B1** (diagnostic, complete): installed the **certified** `noise_floor.json` (`_provisional: false`, 2026-08-08). For this stream its part 7 says *"mdd_scored == 0 on the two paper-bar cells means 'the reference's uncertainty is unobservable from this round's data', not 'zero' ... Same-reference comparisons (arm vs arm, or vs the affine floor) are unaffected - the bar cancels"* -> an arm-vs-arm route contrast is licensed to use `tau_rel`; an absolute-bar ifc claim is not. Also: *"do not read stale_checkpoint_audit.py's train_seconds_collapsed verdicts as evidence of staleness"*; run `tools/zero_work_resume_scan.py` beside it with `--exclude stale_ckpt`. Open question: *"the round has no witness for 'did the TRAINING data change between this checkpoint and this score' ... Only a content hash bound into the checkpoint can, and coverage of that binding is measured at 0/18"*.
- **r3s3_lf_value-B1**: raised the STOP-THE-LINE #2 stale-checkpoint finding (zero-work resumes re-evaluating pre-repair weights). Direct consequence for B2: fresh checkpoint dirs, and a data-hash bound into the checkpoint.
- **r3s1_factorised-B1**: complete, no r3s2-facing part-7 item.

## 5. Reopen candidates

**None.** All four round-3 batch-1 cards carry `reopen_candidate: false` (verified by reading every JSON in `experiment_cards/*/batch_1/`); no round-3 card is flagged for reopening, and B1's own status is `complete`.

## 6. Prior-round record — tested directions relevant to this stream

| Direction | Round-1/2 record | Status on the repaired panel |
|---|---|---|
| condition->pseudo-LF->frozen DC corrector (the stack) | r2s2_stacked-B1, round-2's best geomean; corrector worth **0.0061** skill units on ch | **confirmed-null, re-tested**: r3s2-B1 re-ran it under completeness; F2 fired again (corrector effect 0.0107 on ch, 9x-163x below one mce) |
| exact IC channel into the emulator | untested in rounds 1-2 (the vector was incomplete) | **confirmed positive at stage 1** (F1 held; 3.1x/1.3x/8.0x emulator gain) — this is why B2 keeps the `ic_synth` front end fixed and varies the ROUTE |
| direct condition->HF head, FiLM-only | r2s1_direct-B2/B3, certified 23.7753 / 25.5119 on the repaired 5-ds panel | **untested at matched budget/front end**: those cards have no IC channel and no budget-matched pairing with the stack — this is precisely the gap B2 fills |
| ifc `affine_on_hf_train` accounting | round-3 launch degeneracy audit | **confirmed**: every B1 arm lost it; websearcher E3 preempts claiming the instrument as new |
| LSI Wiener corrector with `ridge = 0` | round-1 s6/s4 `dc_cleaned` lineage, carried through r2s2-B1 | **refuted as an instrument** on sample-starved cells (M1, bit-identical across two rounds) -> repaired, not re-proposed, in B2 |
| more capacity / conditioning on `cahn_hilliard` | not tested; B1's mechanism analysis forbids it | **untested and pre-emptively ruled out** (M7, handoff caution) |

## 7. What is UNKNOWN

1. **Whether the LF intermediate has any value at all once it must be hallucinated.** This is the round-2 §12.2 falsification framing (*"if pseudo-LF -> corrector loses to r2s1's direct models, the LF representation is not a useful bottleneck"*) and it has **never been measured at matched budget with a matched front end**. The existing comparison (stack 12.9556 vs r2s1_direct 23.7753) is confounded three ways: different family, different front end (no IC channel), different optimizer budget. The sign of the honest contrast is genuinely unknown, and the literature prior is explicitly two-sided.
2. **Where the LF route's data advantage actually pays.** On both ifc cells the LF route trains its stage 1 on **18 of 20 LF rows** while any direct head sees **5 HF rows** — a 3.6x data advantage that 2512.02868 predicts should make the stack win "particularly in data-scarce scenarios". Yet B1 measured the stack *losing* a 5-row closed form by 1.6x-36x. Nobody has run the arm that isolates this.
3. **How much of the stream anchor is the deconvolution defect.** 12.9556 is a 3-seed mean whose upper leg (17.8277) is one unregularised band on one cell on one seed. Whether the repaired anchor is ~10.6 (M3's prediction) or something else is unmeasured, and every later r3s2 comparand depends on it.
4. **Whether the repair is enough, or whether the corrector is structurally blind.** M8 says the IC channel's information is per-sample and non-ensemble-linear while the corrector's load-bearing stage is a linear shift-invariant filter — so a *stable* corrector may still be worthless. Regularisation fixes the variance, not the function class; the two are confounded in every number on B1.
5. **Whether the prospective approximability declaration survives contact.** E3 is only defensible if the declaration is made *before* the measurement and then holds: ch's route delta should be below one `tau_rel` while at least one other cell's is not. Never tested prospectively anywhere in this project.
6. **Whether a held-out selector can rescue the ifc cells.** With 5 HF rows a LOO selector between the affine closed form, the stack and the direct head is the only ifc design that is not anecdote-grade by construction — and it has never been run.
7. **What the certified floors imply for headroom.** Certified `tau_rel`: ac 18.6198, fk 10.3128, ch 0.3612, ifc_poisson 0.6910, ifc_heat 0.1640; panel `seed_mce` 0.5083 (`state/anchors_repaired/noise_floor.json`, `_provisional: false`). The stack's *whole* corrector effect on ch (0.0107) is 34x below `tau_rel(ch)` — so any B2 clause stated on the corrector alone is unresolvable by construction; only route-level and repair-level deltas are large enough to be measurable.
