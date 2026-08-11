# Summary so far — `r3s2_field_reach`, batch 3 (emulator-ceiling slot)

## What the operator has fixed for this slot

`state/batch3_scope_2026-08-10.md` is binding and names exactly one card for this stream: the **emulator-ceiling card**, which is preference #1 of this stream's own batch-2 recommendation (`experiment_cards/r3s2_field_reach/batch_2/B2.json` part 7 `next_direction`).
Its three scoped components, verbatim from that card: *"(a) the real-LF oracle vs pseudo-LF ladder on all five cells, already emitted as S2 and needing only a proper scored arm; (b) selecting the corrector's regularisation on the EMULATOR's held-out output instead of on real LF — the covariate shift M7 names, fixed at the selection input rather than by deleting bands; (c) the ridge = 1e-9 correction, carried as a footnote and not as an idea."*
Explicitly out of scope: another corrector-repair card, another route contrast.
Clauses register against the certified `mf_fno_transfer_film` baseline (`state/anchors/film_denominator.json`, ADR r3-0006), **not** copy-LF.

## The measurement the card is built on

From B2 part 6:

- **F9**: the SAME frozen corrector reaches **nRMSE 0.0195–0.0211 on ifc_poisson fed a real coarse solve** and **0.119–2.147 fed the emulator's pseudo-LF**. The real-LF oracle is below the certified `affine_on_hf_train` floor (0.0574) and ~6x better than the deployed stack (0.1194–0.1271). The band-limit repair is *worse* on real LF at 15 of 15 legs.
- **M7 (HIGH, measured)**: *"the real defect is a COVARIATE SHIFT between the fit input and the deployment input, written into the recipe itself (`R3S2_CORRECTOR_FIT_ON=real_lf`, `R3S2_LF_INPUT=pseudo`) … LOOCV is honest out-of-sample in the ROW dimension and blind in the INPUT-DISTRIBUTION dimension, so no fit-fold selector at any n_fit can price it."*
- **M12**: the ifc_poisson route win is *"an EMULATOR-QUALITY result, not a route result."*
- **F10 / M8**: `ridge = 1e-9` clears the stability leg on all 10 leave-2-out folds at zero held-out cost — a footnote, not an idea.
- **M9 / M15**: ifc_poisson's LF→HF relation is a single scalar gain (coherence ~1, gain ~0.26 every band); ifc_heat is LEVEL_DOMINATED; both are floor-disqualified for every field arm this stream has built. Any ladder result must therefore be read across the sharp cells too, not only on ifc.

So the batch-3 object is a **decomposition**: total stack error = (estimator term, measurable with the oracle real-LF input) + (hallucination term, the degradation when the same frozen estimator is fed pseudo-LF). Plus a **selection-input repair**: choose the corrector's regularisation on the emulator's held-out output rather than on real LF.

## Prior-art state inherited (batch 2, `websearches/r3s2_field_reach/batch_2/report.md`)

Nothing this stream has proposed has ever come back `novel` (project record 0-for-7, program.md §13.3).
Relevant standing verdicts:

- **E2** `preempted-but-MF-composition-open`: *"every retrieved multi-fidelity comparison either calls the LF model at test or feeds the corrector a real coarse solve"* (fetched: arXiv 2411.07576 coarse-FE-in corrector; 2512.02868 correlation-based MF emulators incl. "exact or learnable low-fidelity information"; 2511.12764 INC; 2510.23111 neural-emulator superiority).
- **E1** `preempted`: regularised/shrunk spectral transfer estimation is classical (1511.07030, 1810.08360, 2606.03936) — hence (c) as a footnote.
- **E3** `preempted-but-MF-composition-open`: approximation-vs-statistical error decomposition is textbook (2512.03113); the n-width / weak-baseline reporting standard is published (2604.20061).

In-repo prior websearch reports (`/resnick/groups/Hippo/ezeng/mf_field/docs/reports/`): `MF_Leaderboard_Beaters_2026_Report.md` line 236 (arXiv:2512.02868, correlation-based MF emulators, *corrupted* LF sources) and line 35 (residual-decomposition convergence); `MF_Sharp_HighFreq_Report.md` lines 169/335/351 (displacement+amplitude error decomposition, band-limited reporting). Cited, not re-derived.

## Open questions this batch's search must settle

1. Is "oracle-vs-predicted intermediate" ablation of a **frozen** downstream stage a named, standard practice (pipeline error attribution / oracle ablation) — and is it standard *in the MF-surrogate literature*?
2. Is there published work on **choosing a downstream stage's regularisation on the upstream model's predicted outputs** (deployment-distribution model selection) rather than on ground-truth intermediates?
3. What is the closest ML analogue — teacher forcing vs free running, exposure bias, scheduled sampling, DAgger — and does any of it already cover a *non-autoregressive, single-shot* two-stage surrogate?
4. Does anyone report an **emulator ceiling** ratio (hallucination / estimator error) as a decision instrument for whether the intermediate is worth its place?
