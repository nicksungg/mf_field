---
name: factory_mffp-dashboard
description: Project dashboard for factory_mffp — multi-fidelity field-prediction model factory. Goal — beat paper nRMSE on 17 benchmark datasets. **CYCLE-010 STRATEGY PHASE COMPLETE 2026-06-02 — detail [[cycle-010-strategy]]; CEO verdict [[ceo-verdict-strategist]] PROCEED + PLAN APPROVED (10/10 hard gate).** Strategist produced 2 hypotheses against cycle-010 baseline composite 0.022161 on `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb` (identical reproduction of cycle-009 H1+H2, all 14 cells cache-hit). Sequenced and **UNBUNDLED** (both touch `models/fno_mf_stack/smoke_eval.py` — confounded bundle would not let attribution survive). **H1 LEAD (HIGH, MUST LAND FIRST):** `fno_mf_stack` capacity-axis 2nd step — SMOKE_DEFAULTS edit `hidden=64→96, modes_per_level=(4,8,16,20)→(4,8,16,24)`; n_blocks=4 held; ~2.0M params (~2× cycle-009 banked). Branch `experiment/15-fno_mf_stack-capacity-axis-2nd-step`. Expected Poisson 0.030-0.034 (−10 to −22%); composite 0.0197-0.0212 (−5 to −11%). NK-clear. Kill-switches: Poisson/Heat > 0.0594 OR wall > 1500s → REVERT. Hard hold `modes_per_level[3] ≤ 24` (~73% Nyquist) per [[fnospectralperspective2024]] + [[stresstest2025fno]]. Wall budget 600-900s. **H2 SECONDARY (MEDIUM, SEPARATE PR after H1 banks):** Lyu+yang2025mfdeeponet two-stage LF→HF curriculum on `fno_mf_stack` with **FROZEN LF stage 2** — SMOKE_DEFAULTS keys `pretrain_frac=0.40, stage2_freeze_lf=True`; refactor `_build_opt_sched(model, p, t_max)` helper; fresh `Adam` + fresh `CosineAnnealingLR` per stage (Lyu invariant against stale-momentum divergence); stage transition applies `requires_grad_(False)` to `lf_fnos[0..2]` + rebuilds fresh stage-2 Adam@3e-4. Branch `experiment/16-fno_mf_stack-curriculum-frozen-lf`. **NK2 carve-out applied** — `models/fno_mf_stack/model.py:165-168` has 4 INDEPENDENT SmallFNO modules with NO shared weights (coupled only through MFRNPAggregator MLP), matches `yang2025mfdeeponet`'s freeze-branch-and-trunk pattern; NK2's shared-K-basis mechanism does NOT apply. **MANDATORY dual kill-switch:** absolute (Poisson/Heat > 0.0594) AND inter-stage (stage_2_best_val ≥ 0.90 × stage1_best_val, i.e. stage 2 must reduce val by ≥10%; if not met REVERT to stage-1 checkpoint + report STAGE_2_NO_IMPROVEMENT) AND wall > 1800s → REVERT. Expected further Poisson −5 to −15% on top of H1 (0.027-0.032); composite 0.0184-0.0205 (~60-70% of IFC-GPODE bar). Measured against H1-banked composite, NOT cycle-010 baseline. Clears cycle-009 close-out **O3 backlog item** (deferred curriculum on LF/HF-independent design with mandatory dual kill-switch). Wall budget 1500-1700s. NK1-clear (no conditioning); NK3-clear (canonical MFRNP weights `poisson_hf_weight=2.0, poisson_lf_weight=0.25` held across both stages). **Sequencing plan (CEO-approved):** Experiment 1 (H1) branches from `experiment/14 @ 0b6e6eb`; SMOKE_DEFAULTS edit only; smoke-verify `--epochs 2` then full smoke; verdict vs 0.022161. Experiment 2 (H2) branches from H1's banked branch; training loop changes; verdict vs H1's banked composite. If H1 reverts, H2 still defensible (curriculum is fresh-axis-distinct from capacity). `--no-github` (local commit only). **CEO hard gate 10/10 PASS:** surface constraints clean, both leakage scans `risk_level: none flagged: false` (first cycle in project history with clean leakage on both hypotheses since cycle-008 H1; ends 7-cycle leakage substring-collision false-positive override streak), hypothesis count 2/2 budget, NK1/NK2-carve-out/NK3 all honored, backlog adequacy (O3 fully addressed), no calendar estimates, bundling caveat respected. Strategist update INSTRUCTED for Builder H1 first: implement only the SMOKE_DEFAULTS edit at smoke_eval.py:39-55; update INSPIRATION.md with `mutransferfno2025` + `fnospectralperspective2024`; pre-flight `uv run python -m models.fno_mf_stack.smoke_eval --epochs 2 --dataset_dir data/ifc_heat`; commit with cycle-010 H1 capacity-axis step message. **Backlog deferrals** (cycle-011+): O1-aggressive (capacity 3rd step hidden=128, modes=(4,8,16,24), n_blocks=5 — pursue only if H1 lands net-positive AND wall <1500s); O3 (input-dependent K-basis B(m, LF_features) on `fno_coregionalization` — defer until H1/H2 exhausted; heat guard 0.0194 mandatory); O4 (NEW family `fno_coreg_conditioned_v2` with γ(m, LF_features) FiLM — defer until H1+H2 fail to break 0.030 Poisson floor); adjacent literature additions to `papers_summary.csv` (15 ready keys; human-action); `MFRNP_AGGREGATOR_POISSON_SPECIALIZATION` axis (ablate aggregator topology). Next phase: spawn Builder for Experiment 1 (H1). — Prior: **CYCLE-010 RESEARCH PHASE COMPLETE 2026-06-02 — detail [[research-cycle-010]].** Cycle-010 Researcher (Mode 4, failure-targeted) produced 5 sections O1-O5 against cycle-010 baseline composite 0.022161 on `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb` (identical reproduction of cycle-009 H1+H2, all 14 cells cache-hit). Dominant residual gap = `fno_mf_stack × ifc_poisson = 0.038120` (1.06× over IFC-ODE2; 2.12× over IFC-GPODE; no challenger within 1.9×). Composite sensitivity: closing Poisson best → 0.018 (GPODE) unlocks **−31% composite**; closing only to 0.036 (ODE2) unlocks just −2.8%; Heat closure unlocks 0%. **H1 LEAD (capacity-axis 2nd step on `fno_mf_stack`):** `hidden=64→96, modes_per_level=(4,8,16,20)→(4,8,16,24), n_blocks=4` — touches only `models/fno_mf_stack/smoke_eval.py:39-55` SMOKE_DEFAULTS. ~2.0M params (~2× cycle-009). Expected Poisson 0.030-0.034 (−10 to −22%); composite 0.0197-0.0212 (−5 to −11%). NK-clear. HIGH confidence. Wall 700-900s (kill 1500s). Mandatory dual kill-switches: Poisson > 0.0594 OR Heat > 0.0594 OR wall > 1500s → REVERT. Hard hold: `modes_per_level[3] ≤ 24` (~73% Nyquist) per [[fnospectralperspective2024]] + [[stresstest2025fno]] saturation evidence. **H2 SECONDARY (NK2-carve-out curriculum on `fno_mf_stack`):** Lyu-style two-stage LF→HF with **frozen LF stack** in Stage 2 (per [[yang2025mfdeeponet]]'s freeze pattern), `pretrain_frac=0.40`, fresh `Adam @ 3e-4` + fresh `CosineAnnealingLR` at transition. NK2 carve-out applies because `fno_mf_stack` has 4 INDEPENDENT `SmallFNO` modules (LF/HF-independent design — `models/fno_mf_stack/model.py:165-168`) — NOT the co-evolved residual ladder NK2 closed on. Expected Poisson 0.030-0.035 (−10 to −20%). MEDIUM-HIGH confidence. Wall 1500-1700s (kill 1800s). Mandatory dual kill-switches: **absolute (Poisson/Heat > 0.0594) AND inter-stage (Stage-2 best_val ≥ 0.90 × Stage-1 best_val)** AND wall > 1800s → REVERT. Risk: MFRNP aggregator MLP may be load-bearing Poisson mechanism; freezing LF stack might deny it cross-fidelity signal — dual kill-switch catches within Stage 2. **CRITICAL: H1 and H2 MUST land as SEPARATE PRs** — both touch `smoke_eval.py:39-55` SMOKE_DEFAULTS; confounded bundle would not let attribution survive. Land H1 first, attest new baseline, then H2. **H3 RESERVE (B(m, LF_features) on `fno_coregionalization`)**: DEFERRED — non-leader cell + NK1-adjacent. **O4 (γ(m, LF_features) new family)**: DEFERRED — high implementation cost (full package scaffold) + weak composite prior (cycle-008 B1 landed at 12.6× over leader on Poisson). **6 new bibtex candidates validated** (5 new + 1 pre-2024 newly-archived): [[mutransferfno2025]] (arXiv:2506.19396; width-LR-transfer, backs H1), [[ufnofilm2025]] (arXiv:2511.20543; γ(scalar, LF_field) NK1-safe blueprint, 21% MAE on multiphase flow), [[pirino2025]] (arXiv:2510.23810; function-encoder dict learning, multi-resolution backlog), [[fnospectralperspective2024]] (arXiv:2404.07200; Fourier-kernel saturation warning, backs H1 modes ≤ 24 hold), [[mfbpinn2026]] (arXiv:2602.01176; hierarchical residual + Bayesian UQ, PINN backlog), [[liu2022neuralcoreg]] (arXiv:2109.09261; canonical pre-FNO input-dependent coregionalization, O3 reference). **arXiv ID correction**: [[stresstest2025fno]] `2501.11428` → `2601.11428` (Jan 2026, verified in cycle-010 web round). Total `papers_summary.csv` ready-keys: **15** (10 prior + 5 new + `liu2022neuralcoreg` newly-archived). **Cross-cycle pattern (load-bearing for H1 calibration)**: cycle-009 H1+H2 step (4× params: 250k → 1.0M) delivered −36% Poisson; slope `log(nRMSE) / log(params) ≈ −0.39`. Naïve 2× extrapolation predicts −27%; literature flattens to realistic −10 to −22%. Capacity axis NOT yet exhausted on `fno_mf_stack`; cycle-011 likely diminishing returns at hidden=128 / modes=24 ceiling unless axis changes (curriculum, architecture). **Researcher web access**: WebSearch 10/10 successful across 5 focus areas; WebFetch landed 2 readable HTML excerpts (PI-RINO + UFNO-FiLM); arXiv PDFs returned binary/403. Next phase: CEO ratifies Researcher → Strategist generates H1+H2 per `max_new` budget. — Prior: **CYCLE-008 CLOSED 2026-06-02 — close-out doc [[cycle-008-summary]].** Cycle-008 net = **1 KEEP intent (H1 banked best 0.027729) + 2 consecutive GENUINE REVERTs (H2 architecture-falsified-on-poisson; H3 architecture-incompatible-three-stage-on-residual-ladder)** — first time in project history with two genuine REVERTs in one cycle. NEW REPRODUCIBLE PROJECT BEST composite_nRMSE **0.030408 → 0.027729 (−8.81%)** on `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` — beats the prior cycle-005 H2 aspirational unreproducible ceiling (0.029357) by −5.55% AND moves the project into reproducible sub-0.028 territory for the first time. 89.93% of the parallel-bench bar gap closed by capacity-axis alone; +0.000300 (+1.09%) remaining vs bar 0.027429 = cycle-009 dethrone target. Project genuine-REVERT count now **5** (c003 H1, c006 H1, c007 H2, c008 H2, c008 H3); `revert_bookkeeping_keep_intent` streak at **7** (H1 added). META-FIX delivered: `recipe_hash` checkpoint guard pattern (cycle-003 backlog item) WORKED CORRECTLY — cycle-009 action = cherry-pick into `models/_common/recipe_hash.py` portable utility, apply to ALL family `smoke_eval.py` files. FOUR new cross-cycle patterns: (1) FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF correlation — pure m-conditioning insufficient for Poisson-class datasets; (2) Three-stage frozen-LF-HF-residual curricula INCOMPATIBLE with co-evolved residual ladder designs — end-to-end joint training remains correct recipe for `fno_coreg_residual`/`fno_coregionalization`; three-stage MAY work for families with LF/HF independent by design (`mf_fno_transfer_bar`, `fno_mf_stack`); (3) Multi-stage curriculum kill-switches MUST include Stage-k-vs-baseline absolute check, not only inter-stage ratio; (4) Bookkeeping-overridable REVERT vs genuine architecture-falsified REVERT — diagnostic is R5b monotonic, not precheck. Precheck infra bugs (`score_direction` polarity 10-of-10 incl. symmetric flip; `scope`/`fixed_surfaces` empty-detail 4-of-4; leakage substring collision 6-of-6) remain operator-flagged backlog (6th consecutive cycle requiring overrides). All three cycle-008 branches preserved on disk (experiment/11 banked best; experiment/12 FiLM scaffolding for potential γ(m, LF_features) revisit; experiment/13 recipe_hash pattern source). Cycle-009 entry baseline UNCHANGED by H2/H3 = `experiment/11 @ 18d83a6 @ 0.027729`. — Prior: **Cycle-008 H3 (exp 13) FINAL 2026-06-02 — verdict `revert` (GENUINE, architecture-incompatible — three-stage frozen-LF-HF-residual curriculum is INCOMPATIBLE with co-evolved residual ladder design `fno_coreg_residual`; explicitly NOT `revert_bookkeeping_keep_intent`). CEO intent = REVERT. Three-stage curriculum on `fno_coreg_residual` at branch `experiment/13-fno_coreg_residual-three-stage @ 420a51c` (PRESERVED for `recipe_hash` pattern reuse only; three-stage curriculum NOT reusable; not merged). Composite_nRMSE 0.030408 (flat vs cycle-008 entry baseline 0.030408; **+9.66% vs banked best 0.027729** set by cycle-008 H1 — UNCHANGED). `fno_coreg_residual × ifc_heat` = 0.509105 (UNIVERSAL KILL-SWITCH TRIPPED HARD at 26× over 0.0194 threshold; 19× worse than prior single-stage 0.026; +1837% regression). `fno_coreg_residual × ifc_poisson` = 0.159364 (+165% out of Builder's 0.05-0.06 predicted range; 2.15× worse than prior single-stage 0.074). H3-specific Stage3/Stage2 Heat ratio kill-switch ratio=1.00 (NOT TRIPPED — design flaw: damage occurred in Stages 1/2, kill-switch assumed damage would be in Stage 3). val/test gap on Heat 12× (val 0.043 → test 0.509) — catastrophic overfitting OR final-state-checkpoint divergence. Smoke wall 50.7 s (~7× under budget); total cycle_eval wall 71 s. **Architectural lesson (input to cycle-009 strategy):** three-stage frozen-LF-HF-residual curricula are INCOMPATIBLE with co-evolved residual ladder designs (`fno_coreg_residual`, `fno_coregionalization`). These architectures assume LF and HF networks co-evolve END-TO-END — HF residual depends on the CURRENT LF representation. Stage 2's `requires_grad=False` LF freeze forces the HF residual to correct against an OUT-OF-DISTRIBUTION frozen LF state from the LF-only pretrain regime, producing garbage. Stage 3's unfreeze comes too late — HF residual already in poor local minimum. Three-stage curricula MAY be appropriate for families where LF and HF networks are INDEPENDENT BY DESIGN (e.g., `mf_fno_transfer_bar` — LF outputs a feature map that's an INPUT to the HF FNO, not a co-trained residual; `fno_mf_stack` — per-fidelity stacked predictions). For co-evolved designs, end-to-end joint training (cycle-005 H2 continuous-LR-schedule pattern, NOT frozen-stage gating) remains the correct recipe. **Kill-switch design retrospective:** the H3-specific kill-switch (Stage3/Stage2 Heat ratio > 1.25 → REVERT to Stage 2) assumed Stage 3 would be the damage source. Reality: damage in Stages 1/2; Stage 3 was a no-op on Heat (couldn't fix) but improved Poisson 3.46× over Stage 2. Universal Heat kill-switch caught it post-hoc only. cycle-009+ kill-switch design rule: multi-stage curricula MUST include BOTH (a) absolute Stage_k vs prior single-stage baseline check (`stage_k_final_hf_test_nrmse > 1.25 × prior_single_stage_test_nrmse → REVERT to baseline`) AND (b) inter-stage ratio checks at each transition. Single inter-stage ratio kill-switches are fragile (assume damage in LATER stage only). **KEEP-worthy meta-fix preserved:** despite architectural failure of H3 three-stage, the cycle-003 backlog `recipe_hash` checkpoint guard WORKED CORRECTLY. Stale checkpoint rejection log verified `[resume] REJECTED stale checkpoint: recipe_hash '148a2641b07fe5da' != '0095c3ff614e17b8'`; family retrained from scratch under new recipe (correct behavior). The PATTERN (`sha256(json.dumps({**SMOKE_DEFAULTS, "stage_strides":[0.25,0.5,0.25]}, sort_keys=True).encode()).hexdigest()[:16]` written to `last.pt`/`best.pt`, checked at resume) is REUSABLE. cycle-009 action: cherry-pick the `recipe_hash` pattern from H3's `smoke_eval.py` into a portable utility (`models/_common/recipe_hash.py`) and apply to ALL family `smoke_eval.py` files — closes the cycle-003 H1 stage-resume contamination pathway PROJECT-WIDE, not just for `fno_coreg_residual`. Three-stage curriculum gating logic NOT reusable — do NOT cherry-pick into other co-evolved families. **2nd consecutive GENUINE REVERT in cycle-008 (H2 architecture-falsified-on-poisson, H3 architecture-incompatible-three-stage-on-residual-ladder) — 5th project-wide genuine REVERT (c003 H1, c006 H1, c007 H2, c008 H2, c008 H3); `revert_bookkeeping_keep_intent` streak unchanged at 7.** **Cycle-008 sequence final: H1 KEEP intent (banked best 0.027729, bar gap 89.93% closed) + H2 GENUINE REVERT (FiLM-on-HF-only insufficient for Poisson) + H3 GENUINE REVERT (three-stage frozen-LF incompatible with residual ladder). Cycle-009 entry baseline UNCHANGED = `experiment/11 @ 18d83a6 @ 0.027729`.** TWO new cross-cycle patterns appended to patterns.md: (1) "Three-stage frozen-LF-HF-residual curricula are INCOMPATIBLE with co-evolved residual ladder designs — end-to-end joint training is the right recipe for `fno_coreg_residual`/`fno_coregionalization`"; (2) "Multi-stage curriculum kill-switches MUST include a Stage-2-vs-baseline absolute check, not only an inter-stage Stage3/Stage2 ratio check". Detail: [[cycle-008-exp-13-final]]. — Prior: **Cycle-008 H3 (exp 13) BUILD + REVIEW PHASE BOTH PROCEED/PASS 2026-06-02 — three-stage curriculum on `fno_coreg_residual` (S1 LF pretrain stride 0.25 lr=1e-3 BasisHead frozen → S2 HF residual stride 0.5 lr=3e-4 LF frozen via actual `requires_grad=False` NOT zero-loss masking — cycle-005 footgun avoided → S3 unfreeze all stride 0.25 lr=9e-5 per cycle-003 BasisHead instability prior) with MANDATORY `recipe_hash` checkpoint guard. Branch `experiment/13-fno_coreg_residual-three-stage @ 420a51c` cut independently from cycle-008 entry baseline `1249f2d` (independent of H1's `experiment/11` AND H2's `experiment/12` per Strategist R2 §3 anti-pattern #3 — H1/H2/H3 independent code paths). Single-file mutable surface: `models/fno_coreg_residual/smoke_eval.py` (+401/-73 LOC); `model.py` BYTE-IDENTICAL to baseline (BasisHead K=10 zero-init unchanged — verified `git diff 1249f2d..420a51c -- models/fno_coreg_residual/model.py` empty). Fresh `Adam` + fresh `CosineAnnealingLR` per stage (stale-momentum discipline per `lyu2023mffno`). Param-gating confirmed: S1=9.115M / S2=3.561M / S3=9.120M (deltas: S1−S2=5.554M ≈ LF stack, S3−S1≈0.005M = BasisHead). **`recipe_hash` checkpoint guard IMPLEMENTED + LIVE-VERIFIED:** `sha256(json.dumps({**SMOKE_DEFAULTS, "stage_strides":[0.25,0.5,0.25]}, sort_keys=True).encode()).hexdigest()[:16]` stored in `last.pt` + `best.pt`; resume requires `ok_recipe AND ok_stage AND ok_epoch AND ok_target AND ok_cond`. Builder ran deliberate-mismatch test (mutated `pretrain_lr`); stale ckpt produces `[resume] REJECTED stale checkpoint: recipe_hash '148a2641b07fe5da' != '0095c3ff614e17b8'` and starts fresh — Reviewer cross-referenced rejection log line to code at line 485, exact match. **MFRNP-ban verification:** uniform weights (HF=1.0, LF=(1,1,1), agg=0.5) preserved across all 3 stages; `p` dict immutable per stage; no HF=2.0/LF=0.25 literals anywhere except docstring-as-WARNING-on-ban. **4th-attempt-of-banned-recipe AVERTED** (cycle-007 H2 per-dataset dispatch was the 3rd attempt on this same family). **Kill-switch instrumented:** `stage2_final_hf_test_nrmse` (computed via `_eval_test_hf_nrmse`) recorded in checkpoint + result JSON for mechanical Stage 3 comparison. End-to-end smoke verified on BOTH `ifc_heat` AND `ifc_poisson` at `--epochs 2` (S1=0/S2=1/S3=1, ~4-5s wall) AND `--epochs 4` (S1=1/S2=2/S3=1, all stages activate). Projected ~6 min total smoke wall at 200 epochs on H100 (same as prior single-stage `fno_coreg_residual` run, redistributed). No capacity bump. Surface guard `factory guard . --baseline 1249f2d --check-scope` → clean; `git diff --name-only 1249f2d..420a51c` → exactly 1 file. Reviewer issued **PASS** with line-by-line verification at file:line precision (every acceptance check cross-referenced to specific `smoke_eval.py` line); CEO ratified **PROCEED** independently confirming guard clean + 1-file diff + empty `model.py` diff. Reviewer non-blocking observation: Stage-1 HF FNO/decoder/aggregator/h_proj explicitly set `requires_grad=True` even though `active_levels` excludes HF — benign (Adam `zero_grad(set_to_none=True)` skips no-grad params; weight_decay does not drift them) but slightly inflates reported "trainable" count. Leakage scanner expected substring false-positives (`ifc_raw`, `frozen`, `2.0`, `0.25`) all confirmed benign by Reviewer (generic dataset family name, `requires_grad=False` English, docstring-as-WARNING on banned MFRNP recipe, `STAGE_STRIDES=[0.25,0.5,0.25]` constant — none are loss-weight literals) — 6th-consecutive bookkeeping override at Builder phase. `--no-github` honored (no push, no PR, no `gh` calls). **META-FIX delivery note: cycle-003 backlog item "fix checkpoint-resume contamination via recipe_hash guard" is SHIPPED as a side-effect of H3.** Meta-validity improvement for ALL future research-mode experiments on this family — the cycle-003 H1 33s-stale-resume-vs-549s-clean-rerun contamination failure mode is CLOSED for `fno_coreg_residual`. Next phase: Evaluator (`bash scripts/cycle_eval.sh` on BOTH `ifc_heat` + `ifc_poisson`); kill-switches `ifc_heat > 0.0194` OR Stage 3 Heat > 1.25 × Stage 2 Heat → REVERT. Monotonic-check baseline = cycle-008 H1 banked best composite **0.027729** (UNCHANGED by H2 GENUINE REVERT). Detail: [[cycle-008-exp-13-build]]. — Prior: **Cycle-008 H2 FINAL 2026-06-02 — verdict `revert` (GENUINE, architecture-falsified on Poisson; explicitly NOT `revert_bookkeeping_keep_intent`). CEO intent = REVERT.** NEW family `fno_coreg_conditioned` (FiLM-via-LayerNorm on single full-resolution HF FNO) at branch `experiment/12-fno_coreg_conditioned-film @ 540e684` (PRESERVED; not merged). Composite_nRMSE 0.030408 (flat vs cycle-008 entry baseline 0.030408; **+9.66% vs banked best 0.027729** set by cycle-008 H1). `fno_coreg_conditioned × ifc_heat` = 0.017102 (2nd place behind `fno_coregionalization` 0.01551 by 10%); `fno_coreg_conditioned × ifc_poisson` = 0.749915 (5th place; 12.6× over `fno_mf_stack` winner 0.05961; 5-15× outside Builder's predicted 0.05-0.15 range). Smoke wall 91.99 s total (16× under 25-min kill-switch). Both kill-switches CLEAR — failure mode = silent under-performance, not blow-up. **Architectural lesson (input to cycle-009 failure analysis):** FiLM-via-LayerNorm on HF-only FNO cannot synthesize the LF→HF correlation pathway that ifc_poisson requires. m-conditioning via FiLM affines can re-scale a learned representation per fidelity but cannot CREATE LF→HF structure. The Poisson dataset has strong LF→HF signal that `fno_mf_stack` and `fno_coreg_residual` both exploit directly. Cycle-009 implication: any single-family Heat+Poisson candidate must either (a) re-introduce the LF→HF residual pathway, OR (b) condition on LF samples directly in the FiLM affines (γ(m, LF_features) instead of γ(m, m²)). Pure m-conditioning is insufficient. **First GENUINE architecture-falsified REVERT since cycle-006 H1 (cross-architecture recipe non-portability) and cycle-007 H2 (per-dataset dispatch heat-invariance violation) — 4th genuine REVERT in project history (c003 H1, c006 H1, c007 H2, c008 H2); `revert_bookkeeping_keep_intent` streak remains at 7 unchanged.** Precheck this cycle showed 3/4 documented bookkeeping patterns (scope, fixed_surfaces, ground_truth_leakage); `score_direction` polarity bug fired in OPPOSITE polarity (silenced +0.0027 nRMSE regression as 'Score OK' — symmetric flip; polarity bug count now 10). Bookkeeping precheck NOT load-bearing for decision; CEO REVERT grounded in R5b monotonic check (independent of precheck): composite +9.66% above banked best mandates revert. NEW cross-cycle pattern appended to patterns.md: "Bookkeeping-overridable REVERT vs genuine architecture-falsified REVERT — the diagnostic is R5b, not precheck"; AND "FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF correlation — pure m-conditioning is insufficient for Poisson-class datasets". 828 LOC of FiLM scaffolding preserved on branch for potential cycle-009 revisit (FiLM-on-residual-with-LF-features in γ inputs). **Cycle-008 sequence summary: H1 KEEP intent (banked best 0.027729, bar gap 89.93% closed) + H2 GENUINE REVERT (no composite contribution). Cycle-009 entry baseline = `experiment/11 @ 18d83a6 @ 0.027729` (UNCHANGED by H2).** Detail: [[cycle-008-exp-12-final]]. — Prior: Cycle-008 H2 REVIEW PHASE PROCEED 2026-06-02 — Reviewer PASS (`reviewer-latest.md` 2026-06-02T18:29:13Z, exit 0) on NEW family `fno_coreg_conditioned` (FiLM-via-LayerNorm on single full-resolution HF FNO) at branch `experiment/12-fno_coreg_conditioned-film @ 540e684` cut independently from cycle-008 entry baseline `1249f2d`. `factory guard --baseline 1249f2d --check-scope` clean (eval_immutable + git_clean + experiment_branch + scope all PASS); 4 NEW files under `models/fno_coreg_conditioned/` only, zero existing-family / fixed-surface edits. FiLMNorm math reviewed sound (`GroupNorm(affine=False) + MLP([m, m²]) → 2·C → γ, β` with zero-init γ-projection ⇒ identity FiLM at init; canonical residual-γ pattern). H2 schedule (`pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25`) preserved verbatim from sibling. NEW INSTITUTIONAL-MEMORY FINDING: Strategist R2's "positional modes int-or-tuple" English description was IMPRECISE — actual H1-established convention (per `fno_coregionalization/model.py:89-90` AND `mf_fno_transfer_bar/model.py:70`) is separate kwargs `modes_h: int, modes_w: int`; Builder + Reviewer correctly followed file precedent. Cycle-009+ strategy templates should describe modes API as "separate modes_h, modes_w kwargs" with file:line citation. Leakage scanner: 4 substring-collision false positives (`satisfy`, `description`, `ifc_raw`, `frozen`) — 5th-consecutive bookkeeping override; all required schema fields or generic English. CEO PROCEED ratifies Reviewer PASS. No-GitHub mode honored end-to-end (no PR, no push, no `gh` calls). Next phase: Evaluator (`factory eval` on both `ifc_heat` + `ifc_poisson`); kill-switches `ifc_heat > 0.0194` OR smoke wall > 25 min → REVERT; monotonic-check baseline = cycle-008 H1 banked best composite 0.027729 (NOT entry 0.030408).** **Cycle-008 H1 R4+R5 CLOSED 2026-06-02 — verdict `revert_bookkeeping_keep_intent` (5th consecutive in cycle-007/008, 7th project-wide); NEW REPRODUCIBLE PROJECT BEST composite_nRMSE 0.030408 → 0.027729 (−8.81%) on branch `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` (PRESERVED as cycle-009 entry baseline). `fno_coregionalization × ifc_heat` 0.01551 → 0.012898 (−16.84%); family now sole holder of heat leaderboard at >2× margin over second-place `fno_coreg_residual @ 0.026277`. `fno_coregionalization × ifc_poisson` 0.7501 → 0.5945 (−20.75%, composite-neutral; `fno_mf_stack @ 0.05961` retains poisson). Bar `mf_fno_transfer_bar` parallel-bench 0.027429 short by +0.000300 (+1.09%) — 89.93% of bar gap closed by capacity-axis alone. Both hard component targets MET (composite ≤ 0.028 ✅ AND heat ≤ 0.013 ✅). Heat kill-switch (0.0194) NOT tripped with 33.5% headroom; wall 315 s total (79% under 25-min cap). 5th consecutive operator precheck-overhaul request (out of factory scope; `score_direction` polarity bug 9-of-9, `scope`/`fixed_surfaces` empty-detail 4-of-4 false positives; all 4 real checks PASS — first hypothesis in project history with clean leakage on BOTH passes). All six cycle-008 anti-patterns satisfied (MFRNP recipe BANNED, per-dataset MFRNP dispatch BANNED, bundling FORBIDDEN, D1 + A3 DEFERRED, `model.py` edit FORBIDDEN). Pattern: paper-config wire-up on a freshly-repaired constructor delivered the dominant composite lever EXACTLY as failure_analysis predicted (`CAPACITY_PARETO`); capacity-axis was the right call, recipe-axis correctly avoided.** Cycle-007 H2 BUILD PROCEED 2026-06-02 — Builder commit 87f65b1 on `experiment/10-fno_coreg_residual-dataset-recipes` cut independently from `experiment/7@be36cba` (NOT chained on H1 branch). Single-file +29/-0 LOC additive change at `models/fno_coreg_residual/smoke_eval.py`: module-scope `_DATASET_RECIPES`, two new defaulted-to-1.0 SMOKE_DEFAULTS keys, `resolve_fidelity_weights` helper, dispatch via `p.update(_DATASET_RECIPES.get(args.dataset_name, {}))`. Heat path bit-equivalent to baseline by construction. 2-ep smoke PASS both datasets with correct dispatch logs. Reviewer PASS; CEO PROCEED with leakage-check override on `ifc_poisson` dataset-name token (public dispatch API, not ground truth). 2-for-2 clean Builder commits in cycle-007 (caveat: structural easy case — target file at HEAD pre-edit).** Cycle-007 R2 PLAN APPROVED 2026-06-02 — Option B (2 hypotheses, different families, NO bundling). H1 = FNOCoregionalization constructor fix; H2 = per-dataset recipe decoupling on fno_coreg_residual. Honest baseline 0.039578; aspirational 0.029357 NOT reproducible. Stacked projection ~0.0294 (below bar 0.0274 by small margin). Cycle 005 H2 CLOSED 2026-06-02 — verdict `revert_bookkeeping_keep_intent` (5th consecutive); NEW PROJECT BEST composite_nRMSE 0.029357 — first sub-0.030 in project history, −13% vs cycle-005 R0 baseline 0.033726, −33% vs prior project best cycle-002 H3 0.0442. H2 = two-stage LF→HF transfer-learning schedule for `fno_coregionalization` (training-schedule only, architecture unchanged) on branch `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` cut from `experiment/6-mf_fno_transfer_bar-repo-root-fix` (NOT `main`). **fno_coregionalization on ifc_heat: 0.0205 → 0.01551 (−24%, holds #1, beats paper 0.074 by 4.77×); on ifc_poisson: ~0.05 → 0.7501 (15× regression, PDE-class-coupled side effect — composite unaffected because fno_coreg_residual still owns poisson at 0.0556).** Hard targets NOT met (ifc_heat 0.01551 > 0.013, composite 0.029357 > 0.026, bar parallel-bench 0.02743 still wins composite by 0.002) but H1-calibration realistic stretch band 0.028–0.032 WAS met. R5 precheck fails on 4 bookkeeping bugs (score_direction polarity FP — 7-for-7 across project history; pre-existing 15-file dirty tree; downstream fixed_surfaces; substring-collision leakage on modify/satisfy/ifc_raw). anti_pattern + smoke_test both PASS. Cycle 005 H1 CLOSED 2026-06-02 — same verdict (REPO_ROOT fix; bar smoke composite 0.05258 now on leaderboard). Calibration finding (from H1): bar smoke (0.05258) ≠ bar parallel-bench (0.02743), 1.9× gap. **5-for-5 `revert_bookkeeping_keep_intent` streak — precheck-bookkeeping subsystem overhaul is load-bearing for cycle-006.** Cycle-006 will branch off `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` (NOT main) to inherit both H1 fix and H2 schedule; high-EV move = dataset-conditional LF→HF gating to recover ifc_poisson while keeping the ifc_heat win.
metadata:
  type: project
tags:
  - factory
  - project
  - factory_mffp
source: factory-archivist
date: 2026-06-02
project: factory_mffp
cycle_001_status: closed
cycle_002_status: closed_h3_new_project_best
cycle_003_status: closed_h1_genuine_revert
cycle_005_status: closed_h2_new_project_best_revert_bookkeeping_keep_intent
cycle_005_close_out_doc: cycle-005-summary.md
cycle_005_h1_verdict: revert_bookkeeping_keep_intent
cycle_005_h1_score_before: 0.033726
cycle_005_h1_score_after: 0.033726106467994385
cycle_005_h1_bar_smoke_composite: 0.05257678496715355
cycle_005_h1_bar_parallel_bench_composite: 0.02743
cycle_005_h2_phase: eval_complete_revert_bookkeeping_keep_intent
cycle_005_h2_verdict: revert_bookkeeping_keep_intent
cycle_005_h2_ceo_intent: keep
cycle_005_h2_project_best: true
cycle_005_h2_branch: experiment/7-fno_coreg_lf_hf_transfer
cycle_005_h2_branch_base: experiment/6-mf_fno_transfer_bar-repo-root-fix
cycle_005_h2_commit: be36cba101807d97346a437b81f3f28072bf2003
cycle_005_h2_score_before: 0.033726
cycle_005_h2_score_after: 0.029357
cycle_005_h2_score_delta_pct: -0.13
cycle_005_h2_ifc_heat_before: 0.020472
cycle_005_h2_ifc_heat_after: 0.015511
cycle_005_h2_ifc_heat_delta_pct: -0.24
cycle_005_h2_ifc_poisson_before: 0.05
cycle_005_h2_ifc_poisson_after: 0.7501
cycle_005_h2_ifc_poisson_delta_x: 15
cycle_005_h2_target_composite_le_0_026: false
cycle_005_h2_target_ifc_heat_le_0_013: false
cycle_005_h2_target_calibration_band: true
cycle_005_h2_pretrain_lr: 0.001
cycle_005_h2_finetune_lr: 0.0003
cycle_005_h2_pretrain_frac: 0.25
cycle_005_h2_pre_flight_epochs: 4
cycle_005_h2_pre_flight_val_start: 0.171
cycle_005_h2_pre_flight_val_end: 0.118
cycle_006_status: baseline_failure_analysis_complete
cycle_006_phase: failure_analysis_proceed_to_researcher_r1.5
cycle_006_entry_composite: 0.029357
cycle_006_composite_target: 0.026
cycle_006_composite_gap: 0.003357
cycle_006_ifc_heat_target: 0.013
cycle_006_ifc_heat_gap: 0.002511
cycle_006_dominant_failure_mode: PDE_CLASS_ARCH_RECIPE_COUPLING
cycle_006_h2_framing_correction: "H2 did NOT cause fno_coregionalization Poisson regression (cache hashes confirm pre-H2 0.77562 -> post-H2 0.75015, -3.3% improvement). cycle-005 H2 'broke Poisson 15x' framing was across-family comparison error."
cycle_006_pre_h2_fno_coregionalization_poisson: 0.77562
cycle_006_pre_h2_fno_coregionalization_poisson_hash: 9528aeef
cycle_006_post_h2_fno_coregionalization_poisson: 0.75015
cycle_006_post_h2_fno_coregionalization_poisson_hash: 2954a13e
cycle_006_failure_distribution_pde_coupling: 0.20
cycle_006_failure_distribution_no_transfer_signal: 0.20
cycle_006_failure_distribution_arch_quality: 0.40
cycle_006_failure_distribution_pass_winner: 0.20
cycle_006_pct_non_winning_in_tree_instances: 0.80
cycle_006_ceo_verdict_on_failure_analyst: PROCEED
cycle_006_status_final: closed_h1_revert_genuine
cycle_006_h1_phase: eval_complete_revert
cycle_006_h1_verdict: revert
cycle_006_h1_ceo_intent: revert
cycle_006_h1_branch: experiment/8-fno_coreg_residual-mfrnp-poisson-recipe
cycle_006_h1_parent_branch: experiment/7-fno_coreg_lf_hf_transfer
cycle_006_h1_commit: 59b741f
cycle_006_h1_loc_delta: "+30/-3"
cycle_006_h1_score_before: 0.029357
cycle_006_h1_score_after_aggregate_with_broken_fno_coreg: 0.04196
cycle_006_h1_score_after_estimated_true: 0.02988
cycle_006_h1_score_delta_pct_estimated: 0.018
cycle_006_h1_fno_coreg_residual_ifc_heat_before: 0.03519
cycle_006_h1_fno_coreg_residual_ifc_heat_after: 0.030589733876393764
cycle_006_h1_fno_coreg_residual_ifc_heat_delta_pct: -0.131
cycle_006_h1_fno_coreg_residual_ifc_poisson_before: 0.05556
cycle_006_h1_fno_coreg_residual_ifc_poisson_after: 0.057563906797832916
cycle_006_h1_fno_coreg_residual_ifc_poisson_delta_pct: 0.036
cycle_006_h1_target_composite_le_0_026: false
cycle_006_h1_target_ifc_heat_le_0_013: false
cycle_006_h1_fno_coregionalization_runnable: false
cycle_006_h1_builder_redirects_used: "1 of 2"
cycle_006_close_out_doc: cycle-006-summary.md
cycle_006_new_cross_cycle_pattern: "Cross-architecture recipe portability is NOT guaranteed even when receiving architecture shares structural family (MFRNP HF=2.0/LF=0.25 works on fno_mf_stack 0.0596 but does NOT improve fno_coreg_residual 0.0556 -> 0.0576). Residual decoder pathway absorbs LF/HF asymmetry implicitly. Cite-grounded reasoning produced false confidence."
cycle_006_separable_finding: "K=20 + b_hidden=128 architectural bump (decoupled from loss reweighting) improved fno_coreg_residual Heat by -13% — worth pursuing as standalone hypothesis in cycle-007."
cycle_006_operator_action_required: "experiment/7 committed tree is intrinsically broken — fno_coregionalization smoke_eval.py/model.py constructor signature mismatch; cycle-005 H2 composite 0.029357 was load-bearing on a never-committed dirty model.py. Builder git reset --hard wiped the dirty file."
cycle_006_ceo_retrospective: "git add <named-file> is insufficient when the file is already dirty — it commits all pre-existing dirty changes. Future cycles must pre-clean working tree OR use git checkout HEAD -- <file> before staging."
project_best_composite: 0.027729
project_best_source: cycle-008 H1
project_best_branch: experiment/11-fno_coregionalization-paper-capacity
project_best_commit: 18d83a665f86fbb1b54a9d3b4fa8a78d3e6d11d7
project_best_date: 2026-06-02
project_best_reproducible: true
prior_project_best_composite: 0.030408
prior_project_best_source: cycle-007 H1
prior_project_best_branch: experiment/9-fno_coregionalization-constructor-fix
prior_project_best_commit: 1249f2d
aspirational_unreproducible_composite: 0.029357
aspirational_unreproducible_source: cycle-005 H2 (NOT reproducible reference only)
revert_bookkeeping_keep_intent_streak_pre_cycle_007_h1: 5
score_direction_polarity_bug_count_pre_cycle_007_h1: 7
cycle_007_status: closed_h1_revert_bookkeeping_keep_intent_h2_revert_genuine
cycle_007_status_final: closed
cycle_007_close_out_doc: cycle-007-summary.md
cycle_007_close_out_date: 2026-06-02
cycle_007_close_out_net_effect: "reproducible project best moved 0.04420 (cycle-002 H3 prior reproducible) -> 0.030408 (cycle-007 H1 new reproducible) -- 0.029357 cycle-005 H2 remains aspirational unreproducible reference only"
cycle_007_close_out_h1_verdict: revert_bookkeeping_keep_intent
cycle_007_close_out_h1_ceo_intent: keep
cycle_007_close_out_h2_verdict: revert
cycle_007_close_out_h2_ceo_intent: revert
cycle_007_close_out_h2_verdict_type: substantive
cycle_007_close_out_h1_score_delta_pct: -23.17
cycle_007_close_out_h2_score_delta_pct: 12.36
cycle_007_close_out_new_reproducible_project_best_composite: 0.030408
cycle_007_close_out_new_reproducible_project_best_branch: experiment/9-fno_coregionalization-constructor-fix
cycle_007_close_out_new_reproducible_project_best_commit: 1249f2d
cycle_007_close_out_genuine_revert_count_after_h2: 2
cycle_007_close_out_revert_bookkeeping_keep_intent_streak_after_h1: 6
cycle_007_close_out_precheck_polarity_bug_total_after_h1: 8
cycle_007_close_out_empty_detail_scope_fixed_surfaces_after_h1: 3
cycle_007_close_out_new_patterns_added: ["fresh-train-variance-swamps-invariance", "leakage-check-dispatch-key-sub-class"]
cycle_007_phase: closed
cycle_007_branch_under_test: experiment/7-fno_coreg_lf_hf_transfer
cycle_007_branch_commit: be36cba
cycle_007_r0_honest_baseline_composite: 0.039578
cycle_007_aspirational_best_composite: 0.029357
cycle_007_aspirational_not_reproducible: true
cycle_007_discrepancy_composite: 0.010221
cycle_007_discrepancy_pct: 34.8
cycle_007_r0_ifc_heat_best_family: fno_coreg_residual
cycle_007_r0_ifc_heat_best_value: 0.02628
cycle_007_r0_ifc_poisson_best_family: fno_mf_stack
cycle_007_r0_ifc_poisson_best_value: 0.05961
cycle_007_dominant_failure_mode: COMMITTED_TREE_BROKEN
cycle_007_broken_family: fno_coregionalization
cycle_007_broken_signature_kwargs: ["modes_h", "modes_w", "grid"]
cycle_007_broken_error: "TypeError: FNOCoregionalization.__init__() got an unexpected keyword argument 'modes_h' at models/fno_coregionalization/smoke_eval.py:265"
cycle_007_top_intervention_1: "Repair fno_coregionalization constructor signature (COMMITTED_TREE_BROKEN); expected composite delta -0.0092; single-PR scope"
cycle_007_top_intervention_2: "Decouple fno_coreg_residual recipe per dataset (ARCHITECTURE_OVERFIT; carry-over A); expected composite delta -0.0016; single-PR scope"
cycle_007_top_intervention_3: "Add LF->HF two-stage transfer to fno_coreg_residual (TRANSFER_SIGNAL_UNUSED); expected composite delta -0.0068; stackable with #2"
cycle_007_carry_over_A_status: confirmed
cycle_007_carry_over_A_description: "K=20 / b_hidden=128 helps heat (-25% vs c005 on fno_coreg_residual) AND hurts poisson (+33.5% vs c005); per-dataset decoupling needed"
cycle_007_carry_over_B_status: confirmed
cycle_007_carry_over_B_description: "fno_coregionalization constructor fix is single-PR scope; surfaces models/fno_coregionalization/model.py (primary) + minor mirror at smoke_eval.py:265"
cycle_007_new_cross_cycle_pattern: "Silent regression masked by cache layer — second consecutive cycle (006 -> 007) where on-disk smoke_latest.json diverged from supposed last-keep result. cycle_eval cache keys on content-addressed code_hash; after git reset --hard wiped dirty fno_coregionalization/model.py, old cache entries became orphans (still on disk, never queried); the cell silently dropped from the leaderboard with no error in composite path. Upstream root cause = Builder clean-isolation pattern; downstream consequence = cache-layer + composite-bookkeeping boundary."
cycle_007_r0_ceo_verdict: PROCEED
cycle_007_r1_ceo_verdict: PROCEED
cycle_007_r1.5_ceo_verdict: PROCEED
cycle_007_r0_close_out_doc: ceo-verdict-evaluator-r0.md
cycle_007_r1_close_out_doc: failure-analysis-cycle-007.md
cycle_007_r1.5_close_out_doc: ceo-verdict-researcher.md
cycle_007_r1.5_phase: research_proceed_to_strategist_r2
cycle_007_r1.5_research_doc: .factory/strategy/research.md
cycle_007_r1.5_primary_lever: "Constructor fix on models/fno_coregionalization/model.py:83-128 — outer FNOCoregionalization.__init__ to accept (modes_h, modes_w, grid) and propagate to inner FNOBlock/SpectralConv2d (which already accept anisotropic split). ≤15-LOC edit; sibling pattern in models/mf_fno_transfer_bar/model.py:62-94."
cycle_007_r1.5_top1_expected_delta_composite: -0.0092
cycle_007_r1.5_top1_expected_heat_after: 0.01551
cycle_007_r1.5_top1_expected_composite_after: 0.0304
cycle_007_r1.5_top2_expected_delta_composite: -0.0016
cycle_007_r1.5_top2_dispatch_recipe_heat: "pretrain_frac=0.40, K=20, pretrain_lr=1e-3, finetune_lr=3e-4"
cycle_007_r1.5_top2_dispatch_recipe_poisson: "pretrain_frac=0.0, K=20, finetune_lr=3e-4, poisson_hf_weight=2.0, poisson_lf_weight=0.25"
cycle_007_r1.5_top3_deferred: "New family mf_fno_bar_residual deferred to cycle-008; with Top-1 alone projecting composite to ~0.0304 (near the bar 0.0274), the case for a brand-new family is weaker."
cycle_007_r1.5_no_bundling_directive: "DO NOT bundle Top-1 constructor fix with Top-2 recipe changes — would confound the regression test against the cycle-005 cached 0.01551 number."
cycle_007_r1.5_hypothesis_count_target: "1 (Top-1 alone) or 2 (Top-1 + Top-2 decoupled). Three hypotheses would over-extend cycle budget."
cycle_007_r1.5_new_citations: ["tran2023ffno", "freqmoe2025", "pretrain_lowerdims2024", "dpot2024"]
cycle_007_r1.5_resume_compat: "smoke_eval.py:304-318 already checks `grid` tuple identity, so the constructor fix's scalar grid_size -> tuple grid swap is resume-compatible. Expect ~30s retrain on H100 smoke if state_dict keys mismatch."
cycle_007_r1.5_load_bearing_finding: "Inner classes (SpectralConv2d, FNOBlock) ALREADY accept (modes_h, modes_w); cycle-005 H2 schedule in smoke_eval.py:64-411 is INTACT. The ONLY lost piece is the outer FNOCoregionalization.__init__ — confirms COMMITTED_TREE_BROKEN is wrapper-level mismatch, not architectural redesign."
cycle_007_r2_ceo_verdict: PROCEED_PLAN_APPROVED
cycle_007_r2_close_out_doc: ceo-verdict-strategist.md
cycle_007_r2_strategy_doc: .factory/strategy/current.md
cycle_007_r2_strategy_snapshot: cycle-007.md
cycle_007_r2_hypothesis_count: 2
cycle_007_r2_hypothesis_count_option: B
cycle_007_r2_bundling: forbidden
cycle_007_r2_h1_target_file: models/fno_coregionalization/model.py
cycle_007_r2_h1_category: FIX
cycle_007_r2_h1_failure_mode: COMMITTED_TREE_BROKEN
cycle_007_r2_h1_expected_delta_composite: -0.0092
cycle_007_r2_h1_expected_composite_after: 0.0304
cycle_007_r2_h1_expected_heat_after: 0.01551
cycle_007_r2_h1_kill_switch_heat_gt: 0.0194
cycle_007_r2_h1_kill_switch_pct_over_cached: 0.25
cycle_007_r2_h1_leakage_risk_level: none
cycle_007_r2_h1_confidence: high
cycle_007_r2_h1_priority: highest
cycle_007_r2_h1_branch_name: "experiment/<exp_id>-fno_coregionalization-constructor-fix"
cycle_007_r2_h2_target_file: models/fno_coreg_residual/smoke_eval.py
cycle_007_r2_h2_category: FIX
cycle_007_r2_h2_failure_mode: "LOSS_RECIPE_GAP (primary) / ARCHITECTURE_OVERFIT (secondary)"
cycle_007_r2_h2_expected_delta_composite_standalone: -0.0016
cycle_007_r2_h2_expected_composite_after_standalone: 0.0382
cycle_007_r2_h2_expected_composite_after_stacked_with_h1: 0.0294
cycle_007_r2_h2_expected_poisson_after: 0.05556
cycle_007_r2_h2_kill_switch_poisson_gt: 0.089
cycle_007_r2_h2_kill_switch_pct_over_current: 0.20
cycle_007_r2_h2_leakage_risk_level: none
cycle_007_r2_h2_confidence: high
cycle_007_r2_h2_priority: medium
cycle_007_r2_h2_branch_name: "experiment/<exp_id>-fno_coreg_residual-dataset-recipes"
cycle_007_r2_h2_recipe_dispatch_poisson: "poisson_hf_weight=2.0, poisson_lf_weight=0.25"
cycle_007_r2_h2_recipe_dispatch_heat: "empty (Heat path uniform-identity by construction)"
cycle_007_r2_builder_sequence: "H1 first, then H2"
cycle_007_r2_builder_branch_policy: "Both branches cut from experiment/7-fno_coreg_lf_hf_transfer @ be36cba; H2 does NOT chain from H1's branch — each hypothesis measured independently against honest baseline"
cycle_007_r2_builder_single_file_per_hypothesis: true
cycle_007_r2_builder_smoke_prerequisite: "models/<family>/smoke_eval.py --epochs 2 --dataset_dir data/{ifc_heat,ifc_poisson} --out /tmp/x.json --ckpt_dir /tmp/c --seed 0 must complete for both datasets before declaring done"
cycle_007_r2_builder_no_github: true
cycle_007_r2_r5_previous_best_for_monotonic_check: 0.039578
cycle_007_r2_r5_aspirational_reference: 0.029357
cycle_007_r2_top3_deferred_to_cycle_008: true
cycle_007_r2_top3_deferred_items: ["mf_fno_bar_residual new family scaffold", "LF->HF transfer add-on for fno_coreg_residual", "restore real training on mf_fno_transfer_bar", "transolver val/test normalisation audit"]
cycle_007_r2_hard_gate_checks_passed: 10
cycle_007_r2_anti_patterns_enumerated: 8
cycle_007_h1_build_status: complete_proceed_to_r4
cycle_007_h1_build_phase: build_proceed_to_evaluator_r4
cycle_007_h1_build_ceo_verdict_builder: PROCEED
cycle_007_h1_build_ceo_verdict_reviewer: PROCEED
cycle_007_h1_build_reviewer_verdict: PASS
cycle_007_h1_build_branch: experiment/9-fno_coregionalization-constructor-fix
cycle_007_h1_build_parent_branch: experiment/7-fno_coreg_lf_hf_transfer
cycle_007_h1_build_parent_commit: be36cba
cycle_007_h1_build_commit: 1249f2de87bfd15001c67a22ee4ea66343fecd2d
cycle_007_h1_build_files_changed: 1
cycle_007_h1_build_loc_delta: "+9/-7"
cycle_007_h1_build_target_file: models/fno_coregionalization/model.py
cycle_007_h1_build_smoke_ifc_heat_best_val_nRMSE: 0.22934
cycle_007_h1_build_smoke_ifc_poisson_best_val_nRMSE: 0.27102
cycle_007_h1_build_smoke_params: 1190708
cycle_007_h1_build_builder_redirects_used: "0 of 2"
cycle_007_h1_build_dirty_files_at_start: 15
cycle_007_h1_build_dirty_files_committed: 0
cycle_007_h1_build_close_out_doc: cycle-007-exp-9-build.md
cycle_007_h1_build_constructor_signature_after: "(modes_h: int, modes_w: int, grid: tuple)"
cycle_007_h1_build_inner_classes_byte_identical: true
cycle_007_h1_build_smoke_eval_byte_preserved: true
cycle_007_h1_build_manifest_byte_preserved: true
cycle_007_h1_build_no_fallback_modes_kwarg: true
cycle_007_h1_build_dirty_tree_staging_memory_honored: true
cycle_007_h1_build_cross_cycle_hygiene_win: "Cycle-006 H1 Builder (same role) burned 1-of-2 redirects on dirty-tree contamination; cycle-007 H1 Builder used 0-of-2 redirects with clean named-file 'git add models/fno_coregionalization/model.py' — but note the file was at HEAD (not pre-dirty), so the rule held by structural easy-case, not by improved process discipline."
cycle_007_h1_phase: eval_complete_revert_bookkeeping_keep_intent
cycle_007_h1_verdict: revert_bookkeeping_keep_intent
cycle_007_h1_ceo_intent: keep
cycle_007_h1_formal_verdict: revert
cycle_007_h1_evaluator_verdict: PASS_KEEP
cycle_007_h1_score_before: 0.039578
cycle_007_h1_score_after: 0.030407732506238343
cycle_007_h1_score_delta: -0.009170267493761657
cycle_007_h1_score_delta_pct: -23.17
cycle_007_h1_ifc_heat_best_before: 0.02628
cycle_007_h1_ifc_heat_best_after: 0.01551
cycle_007_h1_ifc_heat_best_family_before: fno_coreg_residual
cycle_007_h1_ifc_heat_best_family_after: fno_coregionalization
cycle_007_h1_ifc_heat_best_delta_pct: -40.98
cycle_007_h1_ifc_poisson_best_before: 0.05961
cycle_007_h1_ifc_poisson_best_after: 0.05961
cycle_007_h1_ifc_poisson_best_family_before: fno_mf_stack
cycle_007_h1_ifc_poisson_best_family_after: fno_mf_stack
cycle_007_h1_ifc_poisson_best_delta_pct: 0.0
cycle_007_h1_fno_coregionalization_ifc_heat_after: 0.01551112640242143
cycle_007_h1_fno_coregionalization_ifc_heat_cycle_005_reference: 0.01551
cycle_007_h1_fno_coregionalization_ifc_heat_reproduction_delta_pct: 0.00007
cycle_007_h1_fno_coregionalization_ifc_heat_cache_status: miss
cycle_007_h1_fno_coregionalization_ifc_poisson_after: 0.7501491695056993
cycle_007_h1_fno_coregionalization_ifc_poisson_cache_status: miss
cycle_007_h1_kill_switch_heat_threshold: 0.0194
cycle_007_h1_kill_switch_heat_tripped: false
cycle_007_h1_kill_switch_heat_headroom_pct: -20.05
cycle_007_h1_target_composite_le_0_0274: false
cycle_007_h1_target_composite_short_by: 0.00301
cycle_007_h1_target_aspirational_le_0_029357: false
cycle_007_h1_target_aspirational_short_by: 0.001051
cycle_007_h1_precheck_real_checks_passed: ["ground_truth_leakage", "anti_pattern", "smoke_test"]
cycle_007_h1_precheck_infra_bug_failures: ["score_direction", "scope", "fixed_surfaces"]
cycle_007_h1_branch: experiment/9-fno_coregionalization-constructor-fix
cycle_007_h1_commit: 1249f2de87bfd15001c67a22ee4ea66343fecd2d
cycle_007_h1_branch_preserved: true
cycle_007_h1_close_out_doc: cycle-007-exp-9.md
cycle_008_entry_composite: 0.030408
cycle_008_entry_branch: experiment/9-fno_coregionalization-constructor-fix
cycle_008_entry_commit: 1249f2d
cycle_008_h1_phase: eval_complete_revert_bookkeeping_keep_intent
cycle_008_h1_verdict: revert_bookkeeping_keep_intent
cycle_008_h1_ceo_intent: keep
cycle_008_h1_formal_verdict: revert
cycle_008_h1_evaluator_verdict: PASS_KEEP
cycle_008_h1_branch: experiment/11-fno_coregionalization-paper-capacity
cycle_008_h1_parent_branch: experiment/9-fno_coregionalization-constructor-fix
cycle_008_h1_parent_commit: 1249f2d
cycle_008_h1_commit: 18d83a6
cycle_008_h1_branch_preserved: true
cycle_008_h1_files_changed: 1
cycle_008_h1_loc_delta: "+10/-4"
cycle_008_h1_target_file: models/fno_coregionalization/smoke_eval.py
cycle_008_h1_score_before: 0.030407732506238343
cycle_008_h1_score_after: 0.027728854219631654
cycle_008_h1_score_delta: -0.002678878286606689
cycle_008_h1_score_delta_pct: -8.81
cycle_008_h1_ifc_heat_best_before: 0.01551
cycle_008_h1_ifc_heat_best_after: 0.012898497199156745
cycle_008_h1_ifc_heat_best_family_before: fno_coregionalization
cycle_008_h1_ifc_heat_best_family_after: fno_coregionalization
cycle_008_h1_ifc_heat_best_delta_pct: -16.84
cycle_008_h1_ifc_poisson_best_before: 0.05961
cycle_008_h1_ifc_poisson_best_after: 0.05961
cycle_008_h1_ifc_poisson_best_family_before: fno_mf_stack
cycle_008_h1_ifc_poisson_best_family_after: fno_mf_stack
cycle_008_h1_ifc_poisson_best_delta_pct: 0.0
cycle_008_h1_fno_coregionalization_ifc_heat_after: 0.012898497199156745
cycle_008_h1_fno_coregionalization_ifc_heat_delta_pct: -16.84
cycle_008_h1_fno_coregionalization_ifc_poisson_after: 0.5944766713681287
cycle_008_h1_fno_coregionalization_ifc_poisson_delta_pct: -20.75
cycle_008_h1_fno_coregionalization_owns_heat: true
cycle_008_h1_fno_coregionalization_heat_margin_over_second_place: 2.04
cycle_008_h1_kill_switch_heat_threshold: 0.0194
cycle_008_h1_kill_switch_heat_tripped: false
cycle_008_h1_kill_switch_heat_headroom_pct: 33.5
cycle_008_h1_bar_mf_fno_transfer_bar_parallel_bench: 0.027429
cycle_008_h1_bar_gap_remaining_abs: 0.000300
cycle_008_h1_bar_gap_remaining_pct: 1.09
cycle_008_h1_bar_gap_closed_pct: 89.93
cycle_008_h1_target_met_composite_le_0_028: true
cycle_008_h1_target_met_heat_le_0_013: true
cycle_008_h1_target_met_composite_le_0_027429: false
cycle_008_h1_wall_seconds_total: 315
cycle_008_h1_close_out_doc: cycle-008-exp-11.md
cycle_008_h1_precheck_real_checks_passed: ["ground_truth_leakage", "anti_pattern", "smoke_test", "scope_independent", "fixed_surfaces_independent"]
cycle_008_h1_precheck_infra_bug_failures: ["score_direction", "scope_polarity_or_short_sha", "fixed_surfaces_empty_detail"]
cycle_009_entry_composite: 0.027729
cycle_009_entry_branch: experiment/11-fno_coregionalization-paper-capacity
cycle_009_entry_commit: 18d83a6
cycle_010_status: baseline_failure_analysis_complete
cycle_010_phase: failure_analysis_proceed_to_researcher_r1_5
cycle_010_entry_composite: 0.022161
cycle_010_entry_branch: experiment/14-fno_mf_stack-capacity-and-recipe-hash
cycle_010_entry_commit: 0b6e6eb
cycle_010_all_cells_cache_hit: true
cycle_010_n_cells: 14
cycle_010_n_models: 7
cycle_010_n_datasets: 2
cycle_010_heat_best_value: 0.012884
cycle_010_heat_best_family: fno_coregionalization
cycle_010_poisson_best_value: 0.038120
cycle_010_poisson_best_family: fno_mf_stack
cycle_010_poisson_best_no_challenger_within: 1.89
cycle_010_heat_best_no_challenger_within: 2.04
cycle_010_bar_parallel_bench_ratio: 0.808
cycle_010_bar_ifc_ode2_geomean_ratio: 0.43
cycle_010_bar_ifc_gpode_geomean_ratio: 0.67
cycle_010_remaining_pct_of_gap_on_poisson: 100
cycle_010_remaining_pct_of_gap_on_heat: 0
cycle_010_load_bearing_cell: "fno_mf_stack × ifc_poisson"
cycle_010_load_bearing_cell_value: 0.038120
cycle_010_secondary_lever_cell: "fno_coregionalization × ifc_heat"
cycle_010_secondary_lever_cell_value: 0.012884
cycle_010_dominant_failure_mode: POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY
cycle_010_secondary_failure_mode: K_BASIS_NON_UNIFORM_FIDELITY_LADDER_COLLAPSE
cycle_010_tertiary_failure_mode: MFRNP_AGGREGATOR_POISSON_SPECIALIZATION
cycle_010_local_sensitivity_d_composite_d_heat: 0.86
cycle_010_local_sensitivity_d_composite_d_poisson: 0.29
cycle_010_counterfactual_poisson_to_gpode_composite: 0.015228
cycle_010_counterfactual_poisson_to_gpode_delta_pct: -31.3
cycle_010_fno_coreg_poisson_val_test_inflation: 11.07
cycle_010_fno_coreg_per_fid_scaler_dynamic_range: 42
cycle_010_top_intervention_1: "Push fno_mf_stack capacity (hidden 64->96, modes (4,8,16,20)->(4,8,16,24)/(4,8,20,28), n_blocks 4->5); NK-clear; mandatory Poisson > 0.0594 + wall > 1500s kill-switches"
cycle_010_top_intervention_2: "Two-stage frozen-LF curriculum on fno_mf_stack; NK2 carve-out (LF/HF-independent design); mandatory dual (absolute + inter-stage) kill-switches"
cycle_010_top_intervention_3: "fno_coregionalization Poisson-specific K-basis B(m, LF_features); distinct from NK3; heat-regression guard 0.0194"
cycle_010_top_intervention_4: "Restore fno_coreg_conditioned with gamma(m, LF_features); NK1-safe; speculative"
cycle_010_deferred_nk3_blocked: "MFRNP-Poisson recipe transfer to fno_coreg_residual"
cycle_010_deferred_high_cost_low_prior: "transolver_residual revamp, MF-DeepONet"
cycle_010_nks_in_force: ["NK1_pure_m_conditioning_hf_only", "NK2_frozen_lf_curriculum_on_residual_ladder", "NK3_mfrnp_loss_weight_to_coregionalization"]
cycle_010_new_taxonomy_entries: ["POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY", "K_BASIS_NON_UNIFORM_FIDELITY_LADDER_COLLAPSE", "VAL_TO_TEST_INFLATION", "MFRNP_AGGREGATOR_POISSON_SPECIALIZATION"]
cycle_010_ceo_verdict_on_failure_analyst: PROCEED
cycle_010_close_out_doc_failure_analysis: failure-analysis-cycle-010.md
cycle_010_research_phase: complete
cycle_010_research_date: 2026-06-02
cycle_010_research_doc: research-cycle-010.md
cycle_010_research_web_search_success_rate: "10/10"
cycle_010_research_web_fetch_html_excerpts_landed: 2
cycle_010_research_h1_lead: "fno_mf_stack capacity-axis second step: hidden=96, modes_per_level=(4,8,16,24), n_blocks=4, ~2.0M params, SMOKE_DEFAULTS-only edit"
cycle_010_research_h1_expected_poisson_min: 0.030
cycle_010_research_h1_expected_poisson_max: 0.034
cycle_010_research_h1_expected_poisson_delta_pct_min: -22
cycle_010_research_h1_expected_poisson_delta_pct_max: -10
cycle_010_research_h1_expected_composite_min: 0.0197
cycle_010_research_h1_expected_composite_max: 0.0212
cycle_010_research_h1_kill_switch_poisson: 0.0594
cycle_010_research_h1_kill_switch_heat: 0.0594
cycle_010_research_h1_kill_switch_wall_seconds: 1500
cycle_010_research_h1_nk_status: NK-clear
cycle_010_research_h1_confidence: HIGH
cycle_010_research_h1_modes_hard_hold: "modes_per_level[3] <= 24 (~73% Nyquist) — fnospectralperspective2024 + stresstest2025fno bound"
cycle_010_research_h2_secondary: "LF->HF curriculum on fno_mf_stack with FROZEN LF stage 2; pretrain_frac=0.40; fresh Adam@3e-4 + fresh cosine at transition"
cycle_010_research_h2_nk2_carve_out: "fno_mf_stack has 4 INDEPENDENT SmallFNO modules — NK2 carve-out applies (LF/HF-independent)"
cycle_010_research_h2_expected_poisson_min: 0.030
cycle_010_research_h2_expected_poisson_max: 0.035
cycle_010_research_h2_expected_poisson_delta_pct_min: -20
cycle_010_research_h2_expected_poisson_delta_pct_max: -10
cycle_010_research_h2_kill_switches: "dual: absolute Poisson/Heat > 0.0594 AND inter-stage stage2_val >= 0.90 * stage1_val AND wall > 1800s"
cycle_010_research_h2_confidence: MEDIUM-HIGH
cycle_010_research_h2_bundling_rule: "DO NOT bundle H1+H2 — both touch smoke_eval.py:39-55; land separately, H1 first"
cycle_010_research_h3_reserve: "B(m, LF_features) K-basis on fno_coregionalization — DEFER (non-leader cell, NK1-adjacent)"
cycle_010_research_o4_defer: "gamma(m, LF_features) new family — DEFER (high implementation cost, weak composite prior)"
cycle_010_research_new_citations_validated: 5
cycle_010_research_new_citations_pre2024_archived: 1
cycle_010_research_new_citations_total: 6
cycle_010_research_arxiv_id_correction: "stresstest2025fno 2501.11428 -> 2601.11428"
cycle_010_research_new_bibtex_keys: ["mutransferfno2025", "ufnofilm2025", "pirino2025", "fnospectralperspective2024", "mfbpinn2026", "liu2022neuralcoreg"]
cycle_010_research_papers_summary_csv_ready_keys_after: 15
cycle_010_research_cross_cycle_slope_log_nrmse_log_params: -0.39
cycle_010_research_capacity_axis_runway: "still has runway; cycle-011 likely diminishing returns at hidden=128 / modes=24 ceiling"
cycle_010_strategy_phase: complete
cycle_010_strategy_date: 2026-06-02
cycle_010_strategy_doc: cycle-010-strategy.md
cycle_010_strategy_verdict: "PROCEED — PLAN APPROVED"
cycle_010_strategy_hypothesis_count: 2
cycle_010_strategy_hypothesis_count_cap: 2
cycle_010_strategy_priority_order: "H1 > H2"
cycle_010_strategy_bundling: forbidden
cycle_010_strategy_bundling_rationale: "H1 + H2 both touch models/fno_mf_stack/smoke_eval.py; confounded bundle would not let attribution survive; H1 first → bank → H2 separate PR"
cycle_010_strategy_sequencing: "H1 (experiment/15) first → bank → H2 (experiment/16) atop H1's banked branch"
cycle_010_strategy_github_mode: --no-github
cycle_010_strategy_leakage_h1_risk_level: none
cycle_010_strategy_leakage_h2_risk_level: none
cycle_010_strategy_leakage_flagged: false
cycle_010_strategy_h1_branch: experiment/15-fno_mf_stack-capacity-axis-2nd-step
cycle_010_strategy_h1_mutable_surface: "models/fno_mf_stack/smoke_eval.py lines 39-55 SMOKE_DEFAULTS only"
cycle_010_strategy_h1_changes: "hidden=64→96, modes_per_level=(4,8,16,20)→(4,8,16,24); n_blocks=4 held"
cycle_010_strategy_h1_param_estimate_million: 2.0
cycle_010_strategy_h1_expected_poisson_min: 0.030
cycle_010_strategy_h1_expected_poisson_max: 0.034
cycle_010_strategy_h1_expected_poisson_delta_pct_min: -22
cycle_010_strategy_h1_expected_poisson_delta_pct_max: -10
cycle_010_strategy_h1_expected_composite_min: 0.0197
cycle_010_strategy_h1_expected_composite_max: 0.0212
cycle_010_strategy_h1_expected_composite_delta_pct_min: -11
cycle_010_strategy_h1_expected_composite_delta_pct_max: -5
cycle_010_strategy_h1_kill_switch_poisson: 0.0594
cycle_010_strategy_h1_kill_switch_heat: 0.0594
cycle_010_strategy_h1_kill_switch_wall_seconds: 1500
cycle_010_strategy_h1_wall_budget_seconds_estimate: "600-900"
cycle_010_strategy_h1_priority: HIGH
cycle_010_strategy_h1_confidence: HIGH
cycle_010_strategy_h1_category: EXPLOIT
cycle_010_strategy_h1_new: true
cycle_010_strategy_h1_nk_status: NK-clear
cycle_010_strategy_h1_modes_hard_hold: "modes_per_level[3] ≤ 24 (~73% Nyquist) — fnospectralperspective2024 + stresstest2025fno saturation bound"
cycle_010_strategy_h2_branch: experiment/16-fno_mf_stack-curriculum-frozen-lf
cycle_010_strategy_h2_mutable_surface: "models/fno_mf_stack/smoke_eval.py — SMOKE_DEFAULTS + training loop + compute_losses + optimizer construction"
cycle_010_strategy_h2_changes: "add pretrain_frac=0.40, stage2_freeze_lf=True; stage 1 LF-only fresh Adam@1e-3 + CosineAnnealingLR(stage1_epochs); stage transition freezes lf_fnos[0..2] + fresh Adam@3e-4 + cosine(stage2_epochs); stage 2 joint loss with frozen LF stack"
cycle_010_strategy_h2_clears_backlog_item: "cycle-009 close-out O3 — Two-stage frozen-LF curriculum on fno_mf_stack (LF/HF independent by design; NK2 carve-out; mandatory dual kill-switch)"
cycle_010_strategy_h2_expected_poisson_min: 0.027
cycle_010_strategy_h2_expected_poisson_max: 0.032
cycle_010_strategy_h2_expected_poisson_delta_pct_min: -15
cycle_010_strategy_h2_expected_poisson_delta_pct_max: -5
cycle_010_strategy_h2_expected_composite_min: 0.0184
cycle_010_strategy_h2_expected_composite_max: 0.0205
cycle_010_strategy_h2_expected_composite_measured_against: "H1-banked composite, NOT cycle-010 baseline"
cycle_010_strategy_h2_kill_switch_poisson_absolute: 0.0594
cycle_010_strategy_h2_kill_switch_heat_absolute: 0.0594
cycle_010_strategy_h2_kill_switch_inter_stage_ratio: 0.90
cycle_010_strategy_h2_kill_switch_inter_stage_rule: "stage_2 best_val ≥ 0.90 × stage1_best_val (i.e. stage 2 must reduce val by ≥10%); if not met REVERT to stage-1 checkpoint + report STAGE_2_NO_IMPROVEMENT"
cycle_010_strategy_h2_kill_switch_wall_seconds: 1800
cycle_010_strategy_h2_wall_budget_seconds_estimate: "1500-1700"
cycle_010_strategy_h2_priority: MEDIUM
cycle_010_strategy_h2_confidence: MEDIUM-HIGH
cycle_010_strategy_h2_category: EXPLORE-curriculum
cycle_010_strategy_h2_new: false
cycle_010_strategy_h2_nk_status: "NK2 carve-out (structurally justified by model.py:165-168 — 4 independent SmallFNO modules)"
cycle_010_strategy_h2_pretrain_frac: 0.40
cycle_010_strategy_h2_stage1_lr: 0.001
cycle_010_strategy_h2_stage2_lr: 0.0003
cycle_010_strategy_h2_freeze_target: "model.lf_fnos[0..2].requires_grad_(False)"
cycle_010_strategy_nks_in_force: ["NK1_h1_clear_h2_clear", "NK2_h2_carve_out_load_bearing", "NK3_h1_clear_h2_clear"]
cycle_010_strategy_ceo_hard_gate_checklist: "10/10 PASS (surface, leakage, count, NK1, NK2 carve-out, NK3, ops, backlog, no calendar, bundling caveat)"
cycle_010_strategy_ceo_verdict_doc: ceo-verdict-strategist.md
cycle_010_strategy_new_bibtex_keys_h1: ["mutransferfno2025", "fnospectralperspective2024"]
cycle_010_strategy_new_bibtex_keys_h2: ["yang2025mfdeeponet", "pretrain_lowerdims2024"]
cycle_010_strategy_arxiv_id_correction: "stresstest2025fno 2501.11428 → 2601.11428"
score_direction_polarity_bug_count: 9
revert_bookkeeping_keep_intent_streak: 7
empty_detail_scope_fixed_surfaces_false_positive_count: 4
precheck_overhaul_consecutive_operator_action_requests: 5
cycle_008_h2_phase: eval_complete_revert_genuine
cycle_008_h2_verdict: revert
cycle_008_h2_verdict_type: substantive
cycle_008_h2_verdict_class: architecture_falsified_on_poisson
cycle_008_h2_verdict_class_explicit_not: revert_bookkeeping_keep_intent
cycle_008_h2_ceo_intent: revert
cycle_008_h2_formal_verdict: revert
cycle_008_h2_evaluator_verdict: PASS_REVERT
cycle_008_h2_ceo_verdict_evaluator: PROCEED
cycle_008_h2_ceo_verdict_evaluator_doc: .factory/reviews/ceo-verdict-evaluator.md
cycle_008_h2_finalize_doc: cycle-008-exp-12-final.md
cycle_008_h2_finalize_date: 2026-06-02
cycle_008_h2_branch_preserved: true
cycle_008_h2_branch_merged_to_trunk: false
cycle_008_h2_score_before: 0.027729
cycle_008_h2_score_after: 0.030408
cycle_008_h2_score_delta: 0.002679
cycle_008_h2_score_delta_pct: 9.66
cycle_008_h2_score_delta_direction: regression
cycle_008_h2_score_before_source: "cycle-008 H1 banked best (experiment/11 @ 18d83a6) — previous_best"
cycle_008_h2_baseline_entry_composite: 0.030408
cycle_008_h2_delta_vs_entry_baseline: 0.0
cycle_008_h2_delta_vs_entry_baseline_pct: 0.0
cycle_008_h2_delta_vs_entry_baseline_classification: flat
cycle_008_h2_fno_coreg_conditioned_ifc_heat_nRMSE: 0.017102
cycle_008_h2_fno_coreg_conditioned_ifc_heat_rank: 2
cycle_008_h2_fno_coreg_conditioned_ifc_heat_leader: fno_coregionalization
cycle_008_h2_fno_coreg_conditioned_ifc_heat_leader_value: 0.01551
cycle_008_h2_fno_coreg_conditioned_ifc_heat_gap_to_leader_pct: 10.3
cycle_008_h2_fno_coreg_conditioned_ifc_poisson_nRMSE: 0.749915
cycle_008_h2_fno_coreg_conditioned_ifc_poisson_rank: 5
cycle_008_h2_fno_coreg_conditioned_ifc_poisson_leader: fno_mf_stack
cycle_008_h2_fno_coreg_conditioned_ifc_poisson_leader_value: 0.05961
cycle_008_h2_fno_coreg_conditioned_ifc_poisson_multiple_over_leader: 12.6
cycle_008_h2_builder_predicted_poisson_min: 0.05
cycle_008_h2_builder_predicted_poisson_max: 0.15
cycle_008_h2_builder_prediction_in_range: false
cycle_008_h2_builder_prediction_actual_multiple_over_high_end: 5.0
cycle_008_h2_composite_contribution_from_new_family: 0
cycle_008_h2_ifc_heat_leaderboard_winner_after: fno_coregionalization
cycle_008_h2_ifc_heat_leaderboard_winner_value_after: 0.01551
cycle_008_h2_ifc_heat_leaderboard_flipped: false
cycle_008_h2_ifc_poisson_leaderboard_winner_after: fno_mf_stack
cycle_008_h2_ifc_poisson_leaderboard_winner_value_after: 0.05961
cycle_008_h2_ifc_poisson_leaderboard_flipped: false
cycle_008_h2_smoke_wall_seconds_total_new_family: 91.99
cycle_008_h2_smoke_wall_seconds_ifc_heat: 64.58
cycle_008_h2_smoke_wall_seconds_ifc_poisson: 27.41
cycle_008_h2_smoke_kill_switch_wall_threshold_seconds: 1500
cycle_008_h2_smoke_kill_switch_wall_tripped: false
cycle_008_h2_smoke_kill_switch_wall_headroom_multiple: 16
cycle_008_h2_smoke_kill_switch_heat_threshold: 0.0194
cycle_008_h2_smoke_kill_switch_heat_value: 0.017102
cycle_008_h2_smoke_kill_switch_heat_tripped: false
cycle_008_h2_smoke_kill_switch_heat_headroom_pct: 12
cycle_008_h2_both_kill_switches_clear: true
cycle_008_h2_failure_mode: silent_under_performance_not_blow_up
cycle_008_h2_cycle_eval_total_wall_seconds: 93
cycle_008_h2_cycle_eval_cache_status: "100% cache-hit for other 16 cells; new family trained during Build phase"
cycle_008_h2_r5a_hygiene_gate: PASS
cycle_008_h2_r5b_monotonic_gate: FAIL
cycle_008_h2_r5b_monotonic_gate_rationale: "composite +9.66% above banked best 0.027729; mandatory revert"
cycle_008_h2_r5c_precheck_blocking_failures: ["scope", "fixed_surfaces", "ground_truth_leakage"]
cycle_008_h2_r5c_score_direction_polarity_fired_opposite: true
cycle_008_h2_r5c_score_direction_polarity_silenced_regression_as_OK: true
cycle_008_h2_r5c_bookkeeping_load_bearing_for_decision: false
cycle_008_h2_r5d_keep_revert: REVERT
cycle_008_h2_r5d_class: architecture_falsified_on_poisson
cycle_008_h2_genuine_revert_count_after_h2: 4
cycle_008_h2_revert_bookkeeping_streak_unchanged_after_h2: 7
cycle_008_h2_architectural_lesson: "FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF correlation pathway. m-conditioning via FiLM affines can re-scale per-fidelity representations but cannot CREATE LF→HF structure. Poisson requires the LF→HF pathway that fno_mf_stack (0.05961) and fno_coreg_residual (0.07419) both exploit; H2's HF-only architecture discards LF channel by design."
cycle_008_h2_cycle_009_strategy_implication_a: "re-introduce LF→HF pathway (residual ladder)"
cycle_008_h2_cycle_009_strategy_implication_b: "condition on LF samples directly in FiLM affines (γ(m, LF_features) instead of γ(m, m²))"
cycle_008_h2_cycle_009_strategy_implication_negation: "pure m-conditioning is insufficient"
cycle_008_h2_finalize_notes: "ceo:revert mode=research reason=architecture_falsified_on_poisson metric=composite_nRMSE before=0.027729 after=0.030408 delta=+0.002679 delta_pct=+9.66 hygiene=pass monotonic=fail heat=0.017102 poisson=0.749915 kill_switches=clear hypothesis_type=code execution_artifacts=na e2e=pass backlog_cleared=no"
cycle_008_h2_close_out_doc: cycle-008-exp-12-final.md
score_direction_polarity_bug_count_after_h2: 10
score_direction_polarity_bug_opposite_polarity_count: 1
cycle_009_entry_composite_unchanged_by_h2: 0.027729
cycle_009_entry_branch_unchanged_by_h2: experiment/11-fno_coregionalization-paper-capacity
cycle_009_entry_commit_unchanged_by_h2: 18d83a6
cycle_008_h2_build_phase_archived: build_ceo_proceed
cycle_008_h2_build_phase_archived_verdict: PROCEED
cycle_008_h2_build_phase_archived_ceo_verdict_builder: PROCEED
cycle_008_h2_ceo_verdict_builder_override_class: leakage_substring_collision
cycle_008_h2_ceo_verdict_builder_override_count_consecutive: 5
cycle_008_h2_branch: experiment/12-fno_coreg_conditioned-film
cycle_008_h2_parent_branch: cycle-008-entry-baseline
cycle_008_h2_parent_commit: 1249f2d
cycle_008_h2_parent_commit_source: "cycle-007 H1 (anisotropic-modes constructor fix)"
cycle_008_h2_branch_independence_from_h1: true
cycle_008_h2_commit: 540e684
cycle_008_h2_commit_message: "feat(fno_coreg_conditioned): NEW family — FiLM-via-LayerNorm on single HF FNO (cycle-008 H2)"
cycle_008_h2_files_changed: 4
cycle_008_h2_files_changed_all_new: true
cycle_008_h2_loc_delta: "+828/-0"
cycle_008_h2_new_family_dir: models/fno_coreg_conditioned/
cycle_008_h2_existing_family_files_modified: 0
cycle_008_h2_model_py_loc: 218
cycle_008_h2_smoke_eval_py_loc: 517
cycle_008_h2_manifest_json_loc: 6
cycle_008_h2_inspiration_md_loc: 87
cycle_008_h2_mode_a_succeeded: true
cycle_008_h2_mode_b_fallback_used: false
cycle_008_h2_film_implementation: "FiLMNorm = GroupNorm(affine=False) + MLP([m, m²]) → 2·C → γ, β with zero-init γ-projection (γ ≈ 1, β ≈ 0 at init)"
cycle_008_h2_gamma_projection_zero_init: true
cycle_008_h2_constructor_signature_pattern: "cycle-007 H1 anisotropic-modes — positional modes accepts int OR (modes_h, modes_w) tuple"
cycle_008_h2_single_hf_fno_architecture: true
cycle_008_h2_h2_lf_hf_schedule_preserved_verbatim: true
cycle_008_h2_pretrain_lr: 0.001
cycle_008_h2_finetune_lr: 0.0003
cycle_008_h2_pretrain_frac: 0.25
cycle_008_h2_smoke_defaults_hidden_channels: 64
cycle_008_h2_smoke_defaults_n_blocks: 4
cycle_008_h2_smoke_defaults_m_feat_dim: 32
cycle_008_h2_smoke_defaults_K_removed: true
cycle_008_h2_smoke_defaults_b_hidden_removed: true
cycle_008_h2_smoke_defaults_trunk_capacity_source: "mf_fno_transfer_bar bar's trunk (NOT cycle-008 H1's paper bump)"
cycle_008_h2_smoke_2ep_heat_params: 4757121
cycle_008_h2_smoke_2ep_heat_train_seconds: 2.04
cycle_008_h2_smoke_2ep_heat_peak_mem_mb: 221.7
cycle_008_h2_smoke_2ep_heat_200ep_projection_min: 3.4
cycle_008_h2_smoke_2ep_poisson_params: 4757249
cycle_008_h2_smoke_2ep_poisson_train_seconds: 1.61
cycle_008_h2_smoke_2ep_poisson_peak_mem_mb: 221.7
cycle_008_h2_smoke_2ep_poisson_200ep_projection_min: 2.7
cycle_008_h2_smoke_200ep_projection_min_total: 6
cycle_008_h2_smoke_kill_switch_cap_min: 25
cycle_008_h2_smoke_kill_switch_headroom_pct: 76
cycle_008_h2_smoke_warmup_change_needed: false
cycle_008_h2_smoke_epochs_kept: 200
cycle_008_h2_leakage_check_diff_flagged: true
cycle_008_h2_leakage_check_diff_risk_level: HIGH
cycle_008_h2_leakage_check_diff_findings_count: 4
cycle_008_h2_leakage_check_diff_findings: "satisfy, description, ifc_raw, frozen"
cycle_008_h2_leakage_check_diff_override_applied: true
cycle_008_h2_leakage_check_diff_override_rationale: "substring collisions with REQUIRED manifest schema fields (description, frozen) per eval/MODEL_CONTRACT.md, REQUIRED supports value (ifc_raw) per research_constraints field 4, and generic English (satisfy)"
cycle_008_h2_inspiration_bibtex_keys: "li2022ifc, li2020fno, lyu2023mffno, beggs2025pdecond, herde2024poseidon"
cycle_008_h2_inspiration_bibtex_keys_count: 5
cycle_008_h2_papers_summary_csv_present_in_tree: false
cycle_008_h2_papers_summary_csv_edited: false
cycle_008_h2_surface_guard_baseline: 1249f2d
cycle_008_h2_surface_guard_check_scope: clean
cycle_008_h2_existing_family_byte_preserved: true
cycle_008_h2_readme_md_edited: false
cycle_008_h2_factory_md_edited: false
cycle_008_h2_model_contract_md_edited: false
cycle_008_h2_no_github_mode: true
cycle_008_h2_no_pr_created: true
cycle_008_h2_no_push: true
cycle_008_h2_no_issue_created: true
cycle_008_h2_build_dirty_files_at_start: 15
cycle_008_h2_build_dirty_files_committed: 0
cycle_008_h2_build_dirty_tree_staging_memory_honored: true
cycle_008_h2_build_no_bundling_with_h1: true
cycle_008_h2_anti_pattern_1_mfrnp_recipe_satisfied: true
cycle_008_h2_anti_pattern_2_per_dataset_dispatch_satisfied: true
cycle_008_h2_anti_pattern_3_bundling_satisfied: true
cycle_008_h2_anti_pattern_4_d1_deferred: true
cycle_008_h2_anti_pattern_5_a3_deferred: true
cycle_008_h2_anti_pattern_6_h1_model_py_edit_na: true
cycle_008_h2_build_doc: cycle-008-exp-12-build.md
cycle_008_h3_status: build_and_review_proceed_to_r4
cycle_008_h3_phase: build_and_review_proceed_to_evaluator_r4
cycle_008_h3_ceo_verdict_builder: PROCEED
cycle_008_h3_ceo_verdict_reviewer: PROCEED
cycle_008_h3_reviewer_verdict: PASS
cycle_008_h3_branch: experiment/13-fno_coreg_residual-three-stage
cycle_008_h3_parent_branch: cycle-008-entry-baseline
cycle_008_h3_parent_commit: 1249f2d
cycle_008_h3_parent_commit_source: "cycle-007 H1 (anisotropic-modes constructor fix)"
cycle_008_h3_branch_independence_from_h1: true
cycle_008_h3_branch_independence_from_h2: true
cycle_008_h3_commit: 420a51c
cycle_008_h3_commit_message: "feat(fno_coreg_residual): three-stage curriculum + recipe_hash checkpoint guard (cycle-008 H3)"
cycle_008_h3_files_changed: 1
cycle_008_h3_loc_delta: "+401/-73"
cycle_008_h3_mutable_surface: models/fno_coreg_residual/smoke_eval.py
cycle_008_h3_model_py_byte_identical_to_baseline: true
cycle_008_h3_basis_head_unchanged: true
cycle_008_h3_three_stage_curriculum: true
cycle_008_h3_stage_strides: "[0.25, 0.5, 0.25]"
cycle_008_h3_stage_1_lr: 0.001
cycle_008_h3_stage_2_lr: 0.0003
cycle_008_h3_stage_3_lr: 0.00009
cycle_008_h3_stage_2_lf_freeze_mechanism: "actual requires_grad=False via _set_lf_stack_grad (NOT zero-loss masking — cycle-005 footgun avoided)"
cycle_008_h3_stage_1_trainable_params_M: 9.115
cycle_008_h3_stage_2_trainable_params_M: 3.561
cycle_008_h3_stage_3_trainable_params_M: 9.120
cycle_008_h3_param_gating_S1_minus_S2_M: 5.554
cycle_008_h3_param_gating_S3_minus_S1_M: 0.005
cycle_008_h3_fresh_optimizer_per_stage: true
cycle_008_h3_fresh_scheduler_per_stage: true
cycle_008_h3_stale_momentum_discipline_citation: lyu2023mffno
cycle_008_h3_mfrnp_ban_preserved_across_all_3_stages: true
cycle_008_h3_hf_loss_weight: 1.0
cycle_008_h3_lf_loss_weights: "(1.0, 1.0, 1.0)"
cycle_008_h3_agg_anchor_weight: 0.5
cycle_008_h3_p_dict_immutable_per_stage: true
cycle_008_h3_banned_recipe_4th_attempt_averted: true
cycle_008_h3_recipe_hash_guard_implemented: true
cycle_008_h3_recipe_hash_guard_live_verified: true
cycle_008_h3_recipe_hash_formula: 'sha256(json.dumps({**SMOKE_DEFAULTS, "stage_strides":[0.25,0.5,0.25]}, sort_keys=True).encode()).hexdigest()[:16]'
cycle_008_h3_recipe_hash_live_test_stale: "148a2641b07fe5da"
cycle_008_h3_recipe_hash_live_test_current: "0095c3ff614e17b8"
cycle_008_h3_recipe_hash_live_test_outcome: "stale checkpoint REJECTED, fresh training started"
cycle_008_h3_meta_fix_cycle_003_backlog_shipped: true
cycle_008_h3_meta_fix_failure_mode_closed: "cycle-003 H1 33s-stale-resume vs 549s-clean-rerun checkpoint contamination"
cycle_008_h3_kill_switch_instrumented: true
cycle_008_h3_kill_switch_marker_field: stage2_final_hf_test_nrmse
cycle_008_h3_kill_switch_h3_specific: "Stage 3 final Heat > 1.25 × stage2_final_hf_test_nrmse → REVERT to Stage 2"
cycle_008_h3_kill_switch_universal: "ifc_heat > 0.0194 → REVERT"
cycle_008_h3_smoke_2ep_ifc_heat_pass: true
cycle_008_h3_smoke_2ep_ifc_poisson_pass: true
cycle_008_h3_smoke_4ep_all_stages_activate: true
cycle_008_h3_smoke_200ep_projection_min_total: 6
cycle_008_h3_capacity_bump: false
cycle_008_h3_surface_guard_baseline: 1249f2d
cycle_008_h3_surface_guard_check_scope: clean
cycle_008_h3_surface_guard_diff_name_only_file_count: 1
cycle_008_h3_leakage_check_diff_findings_expected: "ifc_raw, frozen, 2.0, 0.25"
cycle_008_h3_leakage_check_diff_findings_disposition: "all benign — generic dataset family name, requires_grad=False English, docstring-as-WARNING on banned MFRNP recipe, STAGE_STRIDES constant"
cycle_008_h3_leakage_substring_collision_consecutive_count: 6
cycle_008_h3_reviewer_non_blocking_observation: "Stage-1 HF stack explicit requires_grad=True even though active_levels excludes HF — benign but slightly inflates trainable count"
cycle_008_h3_no_github_mode: true
cycle_008_h3_anti_pattern_1_mfrnp_recipe_satisfied: true
cycle_008_h3_anti_pattern_2_per_dataset_dispatch_satisfied: true
cycle_008_h3_anti_pattern_3_bundling_satisfied: true
cycle_008_h3_anti_pattern_4_d1_deferred: true
cycle_008_h3_anti_pattern_5_a3_deferred: true
cycle_008_h3_anti_pattern_6_h3_model_py_edit_forbidden_satisfied: true
cycle_008_h3_cycle_008_entry_baseline_for_monotonic_check: 0.027729
cycle_008_h3_cycle_008_entry_baseline_source: "cycle-008 H1 banked best (experiment/11 @ 18d83a6); UNCHANGED by H2 GENUINE REVERT"
cycle_008_h3_build_doc: cycle-008-exp-13-build.md
cycle_008_h3_phase: eval_complete_revert_genuine
cycle_008_h3_verdict: revert
cycle_008_h3_verdict_type: substantive
cycle_008_h3_verdict_class: architecture_incompatible_three_stage_on_residual_ladder
cycle_008_h3_verdict_class_explicit_not: revert_bookkeeping_keep_intent
cycle_008_h3_ceo_intent: revert
cycle_008_h3_formal_verdict: revert
cycle_008_h3_evaluator_verdict: PASS_REVERT
cycle_008_h3_ceo_verdict_evaluator: PROCEED
cycle_008_h3_ceo_verdict_evaluator_doc: .factory/reviews/ceo-verdict-evaluator.md
cycle_008_h3_finalize_doc: cycle-008-exp-13-final.md
cycle_008_h3_finalize_date: 2026-06-02
cycle_008_h3_branch_preserved: true
cycle_008_h3_branch_merged_to_trunk: false
cycle_008_h3_branch_preservation_rationale: "recipe_hash pattern reuse only; three-stage curriculum NOT reusable"
cycle_008_h3_score_before: 0.027729
cycle_008_h3_score_after: 0.030407732506238343
cycle_008_h3_score_delta: 0.002678878286606689
cycle_008_h3_score_delta_pct: 9.66
cycle_008_h3_score_delta_direction: regression
cycle_008_h3_score_before_source: "cycle-008 H1 banked best (experiment/11 @ 18d83a6) — previous_best"
cycle_008_h3_baseline_entry_composite: 0.030408
cycle_008_h3_delta_vs_entry_baseline: 0.0
cycle_008_h3_delta_vs_entry_baseline_pct: 0.0
cycle_008_h3_delta_vs_entry_baseline_classification: flat
cycle_008_h3_fno_coreg_residual_ifc_heat_before_single_stage: 0.026277
cycle_008_h3_fno_coreg_residual_ifc_heat_after_three_stage: 0.509105074500434
cycle_008_h3_fno_coreg_residual_ifc_heat_delta_pct: 1837.4
cycle_008_h3_fno_coreg_residual_ifc_heat_delta_multiple: 19
cycle_008_h3_fno_coreg_residual_ifc_heat_best_val: 0.042762876943228965
cycle_008_h3_fno_coreg_residual_ifc_heat_val_test_gap_multiple: 12
cycle_008_h3_fno_coreg_residual_ifc_poisson_before_single_stage: 0.074192
cycle_008_h3_fno_coreg_residual_ifc_poisson_after_three_stage: 0.15936368490302597
cycle_008_h3_fno_coreg_residual_ifc_poisson_delta_pct: 114.8
cycle_008_h3_fno_coreg_residual_ifc_poisson_delta_multiple: 2.15
cycle_008_h3_fno_coreg_residual_ifc_poisson_builder_expected_min: 0.05
cycle_008_h3_fno_coreg_residual_ifc_poisson_builder_expected_max: 0.06
cycle_008_h3_fno_coreg_residual_ifc_poisson_observed_vs_expected_upper_multiple: 2.656
cycle_008_h3_fno_coreg_residual_ifc_poisson_builder_prediction_in_range: false
cycle_008_h3_universal_heat_kill_switch_threshold: 0.0194
cycle_008_h3_universal_heat_kill_switch_tripped: true
cycle_008_h3_universal_heat_kill_switch_ratio_over_threshold: 26.24
cycle_008_h3_h3_specific_stage3_stage2_heat_ratio: 1.0
cycle_008_h3_h3_specific_stage3_stage2_heat_threshold: 1.25
cycle_008_h3_h3_specific_stage3_stage2_heat_kill_switch_tripped: false
cycle_008_h3_h3_specific_stage3_stage2_heat_design_flaw: true
cycle_008_h3_h3_specific_stage3_stage2_heat_design_flaw_explanation: "kill-switch assumed Stage 3 unfreeze would be damage source; reality damage occurred in Stages 1/2; Stage 2 already produced 0.509 on Heat so Stage3/Stage2 ratio = 1.00 trivially"
cycle_008_h3_h3_specific_stage3_stage2_poisson_ratio: 0.289
cycle_008_h3_h3_specific_stage3_stage2_poisson_note: "Stage 3 improved poisson 3.46× over Stage 2 end (0.551 → 0.159) but absolute level still 2.15× paper-recipe baseline"
cycle_008_h3_smoke_wall_seconds_h3_family: 50.7
cycle_008_h3_smoke_wall_budget_seconds: 360
cycle_008_h3_smoke_wall_under_budget_multiple: 7.1
cycle_008_h3_smoke_wall_kill_switch_seconds: 1500
cycle_008_h3_smoke_wall_kill_switch_tripped: false
cycle_008_h3_cycle_eval_total_wall_seconds: 71
cycle_008_h3_cycle_eval_cache_status: "cache hit on every family except fno_coreg_residual (recipe_hash=148a2641b07fe5da new — guard rejected stale ckpt as expected)"
cycle_008_h3_recipe_hash_guard_outcome: works_correctly
cycle_008_h3_recipe_hash_guard_stale_rejection_log: "[resume] REJECTED stale checkpoint: recipe_hash '148a2641b07fe5da' != '0095c3ff614e17b8'"
cycle_008_h3_recipe_hash_guard_keep_worthy_in_isolation: true
cycle_008_h3_recipe_hash_guard_three_stage_curriculum_keep_worthy: false
cycle_008_h3_cycle_003_backlog_item_closed_for_this_family: fix_checkpoint_resume_contamination_via_recipe_hash_guard
cycle_008_h3_cycle_009_action_recipe_hash_pattern: "cherry-pick into models/_common/recipe_hash.py and apply to ALL family smoke_eval.py files"
cycle_008_h3_cycle_009_action_three_stage_curriculum: "do NOT cherry-pick stage gating logic into other families"
cycle_008_h3_cycle_009_candidate_families_for_three_stage: ["mf_fno_transfer_bar", "fno_mf_stack"]
cycle_008_h3_cycle_009_NOT_candidate_families_for_three_stage: ["fno_coreg_residual", "fno_coregionalization"]
cycle_008_h3_architectural_lesson: "Three-stage frozen-LF-HF-residual curricula are INCOMPATIBLE with co-evolved residual ladder designs. These architectures assume LF and HF networks co-evolve END-TO-END — HF residual depends on the CURRENT LF representation. Stage 2's requires_grad=False LF freeze forces the HF residual to correct against an OUT-OF-DISTRIBUTION frozen LF state from the LF-only pretrain regime, producing garbage. Stage 3's unfreeze comes too late. For co-evolved designs, end-to-end joint training (cycle-005 H2 continuous-LR-schedule pattern, NOT frozen-stage gating) remains the correct recipe."
cycle_008_h3_kill_switch_design_lesson: "Multi-stage curriculum kill-switches MUST include BOTH (a) absolute Stage_k vs prior single-stage baseline check (stage_k_final_hf_test_nrmse > 1.25 × prior_single_stage_test_nrmse → REVERT to baseline) AND (b) inter-stage ratio checks at each transition. Single inter-stage ratio kill-switches assume damage occurs in LATER stage only — fragile. Real damage can occur in ANY stage."
cycle_008_h3_r5a_hygiene_gate: PASS
cycle_008_h3_r5b_monotonic_gate: FAIL
cycle_008_h3_r5b_monotonic_gate_rationale: "composite +9.66% above banked best 0.027729; universal heat kill-switch tripped 26× over threshold; mandatory revert"
cycle_008_h3_r5c_precheck_status: not_load_bearing_for_decision
cycle_008_h3_r5d_keep_revert: REVERT
cycle_008_h3_r5d_class: architecture_incompatible_three_stage_on_residual_ladder
cycle_008_h3_genuine_revert_count_after_h3: 5
cycle_008_h3_revert_bookkeeping_streak_unchanged_after_h3: 7
cycle_008_h3_consecutive_genuine_reverts_in_cycle_008: 2
cycle_008_h3_finalize_notes: "ceo:revert mode=research reason=architecture_incompatible_three_stage_on_residual_ladder metric=composite_nRMSE before=0.027729 after=0.030408 delta=+0.002679 delta_pct=+9.66 hygiene=pass monotonic=fail heat=0.509105 poisson=0.159364 universal_killswitch=tripped_26x h3_killswitch=not_tripped_design_flaw recipe_hash_guard=works_correctly hypothesis_type=code execution_artifacts=na e2e=pass backlog_cleared=recipe_hash_pattern_only"
cycle_008_h3_close_out_doc: cycle-008-exp-13-final.md
cycle_009_entry_composite_unchanged_by_h3: 0.027729
cycle_009_entry_branch_unchanged_by_h3: experiment/11-fno_coregionalization-paper-capacity
cycle_009_entry_commit_unchanged_by_h3: 18d83a6
genuine_revert_count_after_cycle_008_h3: 5
genuine_revert_count_by_cycle: "c003 H1, c006 H1, c007 H2, c008 H2, c008 H3"
cycle_008_net_sequence: "H1 KEEP_INTENT_0_027729 + H2 GENUINE_REVERT + H3 GENUINE_REVERT"
cycle_008_consecutive_genuine_reverts: 2
new_cross_cycle_patterns_after_cycle_008_h3: ["three-stage-frozen-LF-incompatible-with-co-evolved-residual-ladder", "multi-stage-kill-switch-needs-stage2-vs-baseline-absolute-check"]
leakage_substring_collision_builder_phase_consecutive_count: 6
cycle_007_h2_build_status: complete_proceed_to_r4
cycle_007_h2_build_phase: build_proceed_to_evaluator_r4
cycle_007_h2_build_ceo_verdict_builder: PROCEED
cycle_007_h2_build_ceo_verdict_reviewer: PROCEED
cycle_007_h2_build_reviewer_verdict: PASS
cycle_007_h2_build_branch: experiment/10-fno_coreg_residual-dataset-recipes
cycle_007_h2_build_parent_branch: experiment/7-fno_coreg_lf_hf_transfer
cycle_007_h2_build_parent_commit: be36cba
cycle_007_h2_build_commit: 87f65b15e882ae285a782d114c96fd0e96ccea10
cycle_007_h2_build_files_changed: 1
cycle_007_h2_build_loc_delta: "+29/-0"
cycle_007_h2_build_target_file: models/fno_coreg_residual/smoke_eval.py
cycle_007_h2_build_sibling_pattern_file: models/fno_mf_stack/smoke_eval.py
cycle_007_h2_build_dispatch_recipe_poisson: "poisson_hf_weight=2.0, poisson_lf_weight=0.25"
cycle_007_h2_build_dispatch_recipe_heat: "empty (uniform 1.0/1.0 by SMOKE_DEFAULTS)"
cycle_007_h2_build_heat_path_bit_equivalent_to_baseline: true
cycle_007_h2_build_heat_gate_condition: "\"poisson\" in dataset_name.lower()"
cycle_007_h2_build_smoke_ifc_heat_val_nRMSE_2ep: 0.4198
cycle_007_h2_build_smoke_ifc_poisson_val_nRMSE_2ep: 0.2447
cycle_007_h2_build_smoke_ifc_heat_dispatch_log: "dataset=ifc_heat hf=1.0 lf=1.0"
cycle_007_h2_build_smoke_ifc_poisson_dispatch_log: "dataset=ifc_poisson hf=2.0 lf=0.25"
cycle_007_h2_build_builder_redirects_used: "0 of 2"
cycle_007_h2_build_dirty_files_at_start: 15
cycle_007_h2_build_dirty_files_committed: 0
cycle_007_h2_build_smoke_eval_byte_preserved_original_keys: true
cycle_007_h2_build_model_py_byte_preserved: true
cycle_007_h2_build_manifest_byte_preserved: true
cycle_007_h2_build_dirty_tree_staging_memory_honored: true
cycle_007_h2_build_no_bundling_with_h1: true
cycle_007_h2_build_leakage_check_diff_risk_level: medium
cycle_007_h2_build_leakage_check_diff_finding: "specific_value 'ifc_poisson' from factory.md research_constraints[5]"
cycle_007_h2_build_leakage_check_hypothesis_risk_level: none
cycle_007_h2_build_leakage_check_ceo_override: true
cycle_007_h2_build_leakage_check_override_rationale: "Dataset name 'ifc_poisson' is the public dispatch API via args.dataset_name, not a ground-truth value — same false-positive class as cycle-001 shared-vocabulary findings; sub-class extended to dataset-name dispatch keys"
cycle_007_h2_build_close_out_doc: cycle-007-exp-10-build.md
cycle_007_h2_build_cross_cycle_hygiene_win: "Cycle-007 H2 Builder used 0-of-2 redirects with clean named-file 'git add models/fno_coreg_residual/smoke_eval.py' — 2nd consecutive clean Builder commit in cycle-007 (after H1 at 0-of-2). Caveat: same as H1, target file was at HEAD pre-edit (not in 15-file pre-existing dirty set), so the [[dirty-tree-staging]] rule held by structural easy case, not by improved process discipline."
cycle_007_h2_build_factory_leakage_check_sub_pattern_extended: "Leakage-check false-positive class extended to include dataset-name tokens used as PUBLIC DISPATCH KEYS via args.dataset_name (distinct from cycle-001 shared-vocabulary and cycle-001 H2 numerical-substring sub-classes)"
cycle_007_h2_build_separate_branch_from_h1: true
cycle_007_h2_build_h1_files_disjoint_from_h2: true
cycle_007_h2_build_r4_cache_miss_expected_on: "models/fno_coreg_residual/ifc_heat and models/fno_coreg_residual/ifc_poisson (both cells; __code_hash__ change)"
cycle_007_h2_build_r4_cache_hit_expected_on: "all 12 other cells (7 other families × 2 datasets, minus 2 H2 cells)"
cycle_007_h2_build_expected_delta_composite_standalone: -0.0016
cycle_007_h2_build_expected_composite_after_standalone: 0.0382
cycle_007_h2_build_expected_fno_coreg_residual_poisson_after: 0.05556
cycle_007_h2_build_expected_fno_coreg_residual_heat_after: 0.030590
cycle_007_h2_build_kill_switch_poisson_gt: 0.089
cycle_007_h2_phase: eval_complete_revert_genuine
cycle_007_h2_verdict: revert
cycle_007_h2_verdict_type: substantive
cycle_007_h2_ceo_intent: revert
cycle_007_h2_formal_verdict: revert
cycle_007_h2_evaluator_verdict: PASS_REVERT
cycle_007_h2_branch_preserved: true
cycle_007_h2_branch: experiment/10-fno_coreg_residual-dataset-recipes
cycle_007_h2_commit: 87f65b15e882ae285a782d114c96fd0e96ccea10
cycle_007_h2_score_before: 0.039578
cycle_007_h2_score_after: 0.044469863562733095
cycle_007_h2_score_delta: 0.004891863562733093
cycle_007_h2_score_delta_pct: 12.36
cycle_007_h2_fno_coreg_residual_ifc_heat_before: 0.02628
cycle_007_h2_fno_coreg_residual_ifc_heat_after: 0.03487293894936765
cycle_007_h2_fno_coreg_residual_ifc_heat_delta_pct: 32.70
cycle_007_h2_fno_coreg_residual_ifc_heat_invariance_violated: true
cycle_007_h2_fno_coreg_residual_ifc_poisson_before: 0.07419
cycle_007_h2_fno_coreg_residual_ifc_poisson_after: 0.06086576400250346
cycle_007_h2_fno_coreg_residual_ifc_poisson_delta_pct: -17.96
cycle_007_h2_ifc_heat_leaderboard_winner_before: fno_coreg_residual
cycle_007_h2_ifc_heat_leaderboard_winner_after: mf_fno_transfer_bar
cycle_007_h2_ifc_heat_leaderboard_flipped: true
cycle_007_h2_ifc_heat_leaderboard_winner_after_value: 0.033174688880908174
cycle_007_h2_ifc_poisson_leaderboard_winner_before: fno_mf_stack
cycle_007_h2_ifc_poisson_leaderboard_winner_after: fno_mf_stack
cycle_007_h2_ifc_poisson_leaderboard_flipped: false
cycle_007_h2_kill_switch_poisson_tripped: false
cycle_007_h2_target_composite_le_0_0274: false
cycle_007_h2_target_composite_short_by: 0.017070
cycle_007_h2_fresh_train_cache_hash_h2: 528438a274db
cycle_007_h2_fresh_train_cache_hash_prior: 1d967ad6e54c
cycle_007_h2_fresh_train_cache_hash_prior_alt: 780ee99ed2d8
cycle_007_h2_fno_coreg_residual_ifc_heat_empirical_variance_observed_pct: 34
cycle_007_h2_strategist_invariance_claim_falsified: true
cycle_007_h2_strategist_invariance_claim_text: "Heat path invariant by construction"
cycle_007_h2_strategist_invariance_claim_falsification_ratio: 6.5
cycle_007_h2_distinct_from_revert_bookkeeping_keep_intent_streak: true
cycle_007_h2_close_out_doc: cycle-007-exp-10.md
cycle_007_h2_genuine_revert_count_in_project_after_h2: 2
cycle_007_h2_prior_genuine_revert: "cycle-003 H1 (composite +91.7%)"
cycle_007_h2_new_cross_cycle_pattern: "Fresh-train variance can swamp claimed invariance — code-path equivalence does not imply numerical equivalence when fresh trains are involved. Cache hash flip on a 'no-op' code change forces retrain; the new trajectory may land at a different optimum than prior runs, exceeding the source-equivalence-based invariance band."
cycle_008_entry_composite_unchanged_by_h2: 0.030408
cycle_008_entry_branch_unchanged_by_h2: experiment/9-fno_coregionalization-constructor-fix
cycle_008_entry_commit_unchanged_by_h2: 1249f2d
cycle_008_proposed_strategist_hard_gate: "For any hypothesis claiming 'invariant by construction' on a cell that would be a fresh train (cache miss expected), require either (a) a kill-switch on the supposedly-invariant cell with a band ≥ 20% anchored to empirical variance, OR (b) explicit evidence the cache hash is preserved (proof of byte-identical input to the cache-key function)."
cycle_008_status: closed
cycle_008_status_final: closed_h1_revert_bookkeeping_keep_intent_h2_revert_genuine_h3_revert_genuine
cycle_008_close_out_doc: cycle-008-summary.md
cycle_008_close_out_date: 2026-06-02
cycle_008_close_out_net_effect: "reproducible project best moved 0.030408 (cycle-007 H1) → 0.027729 (cycle-008 H1) — NEW REPRODUCIBLE PROJECT BEST; 89.93% of parallel-bench bar gap closed by capacity-axis alone; +1.09% gap remaining"
cycle_008_close_out_h1_verdict: revert_bookkeeping_keep_intent
cycle_008_close_out_h1_ceo_intent: keep
cycle_008_close_out_h2_verdict: revert
cycle_008_close_out_h2_ceo_intent: revert
cycle_008_close_out_h2_verdict_type: substantive
cycle_008_close_out_h2_verdict_class: architecture_falsified_on_poisson
cycle_008_close_out_h3_verdict: revert
cycle_008_close_out_h3_ceo_intent: revert
cycle_008_close_out_h3_verdict_type: substantive
cycle_008_close_out_h3_verdict_class: architecture_incompatible_three_stage_on_residual_ladder
cycle_008_close_out_h1_score_delta_pct: -8.81
cycle_008_close_out_h2_score_delta_pct: 9.66
cycle_008_close_out_h3_score_delta_pct: 9.66
cycle_008_close_out_new_reproducible_project_best_composite: 0.027729
cycle_008_close_out_new_reproducible_project_best_branch: experiment/11-fno_coregionalization-paper-capacity
cycle_008_close_out_new_reproducible_project_best_commit: 18d83a6
cycle_008_close_out_consecutive_genuine_reverts_in_cycle: 2
cycle_008_close_out_first_time_two_genuine_reverts_in_one_cycle: true
cycle_008_close_out_genuine_revert_count_after_h3: 5
cycle_008_close_out_revert_bookkeeping_keep_intent_streak_after_h1: 7
cycle_008_close_out_precheck_polarity_bug_total_after_cycle: 10
cycle_008_close_out_empty_detail_scope_fixed_surfaces_after_cycle: 4
cycle_008_close_out_leakage_substring_collision_consecutive_after_cycle: 6
cycle_008_close_out_meta_fix_delivered: recipe_hash_checkpoint_guard
cycle_008_close_out_meta_fix_cycle_003_backlog_item_closed_for_family: fno_coreg_residual
cycle_008_close_out_new_patterns_added: ["film-via-layernorm-cannot-synthesize-lf-hf-correlation", "three-stage-frozen-lf-incompatible-with-co-evolved-residual-ladder", "multi-stage-kill-switch-needs-stage2-vs-baseline-absolute-check", "bookkeeping-overridable-revert-vs-genuine-architecture-falsified-revert"]
cycle_008_close_out_preserved_branches: ["experiment/11 @ 18d83a6 (banked best)", "experiment/12 @ 540e684 (FiLM scaffolding)", "experiment/13 @ 420a51c (recipe_hash pattern)"]
cycle_008_close_out_aspirational_unreproducible_cycle_005_h2_beaten: true
cycle_008_close_out_aspirational_unreproducible_cycle_005_h2_beat_pct: -5.55
cycle_008_close_out_bar_gap_remaining_abs: 0.000300
cycle_008_close_out_bar_gap_remaining_pct: 1.09
cycle_008_phase: closed
cycle_008_entry_branch: experiment/9-fno_coregionalization-constructor-fix
cycle_008_entry_commit: 1249f2d
cycle_008_baseline_composite: 0.030408
cycle_008_baseline_reproducible: true
cycle_008_baseline_ifc_heat_best_family: fno_coregionalization
cycle_008_baseline_ifc_heat_best_value: 0.01551
cycle_008_baseline_ifc_poisson_best_family: fno_mf_stack
cycle_008_baseline_ifc_poisson_best_value: 0.05961
cycle_008_bar_composite: 0.027429
cycle_008_bar_heat: 0.01281
cycle_008_bar_poisson: 0.05871
cycle_008_dethrone_target: 0.024686
cycle_008_gap_to_bar_pct: 10.86
cycle_008_gap_log_ratio_heat: 0.191
cycle_008_gap_log_ratio_poisson: 0.015
cycle_008_heat_vs_poisson_log_weight_ratio: 12.6
cycle_008_dominant_failure_mode: CAPACITY_PARETO
cycle_008_dominant_failure_cell: "fno_coregionalization x ifc_heat"
cycle_008_dominant_absolute_failure_cell: "fno_coregionalization x ifc_poisson (0.7501)"
cycle_008_dominant_absolute_failure_value: 0.7501
cycle_008_mfrnp_recipe_revert_count: 3
cycle_008_mfrnp_recipe_revert_cycles: ["cycle-003-H1", "cycle-006-H1", "cycle-007-H2"]
cycle_008_mfrnp_lever_status: "DO NOT RETRY - prior REVERT 3/3 (backbone-coupled AND dataset-entangled within family)"
cycle_008_new_levers_surfaced: 3
cycle_008_new_lever_a: "Re-bind c007 H2 LF->HF two-stage schedule on repaired fno_coregionalization constructor (committed code never evaluated)"
cycle_008_new_lever_b: "NEW sibling family models/fno_coreg_conditioned/ - m-conditioned single HF FNO (candidate unified Heat+Poisson winner)"
cycle_008_new_lever_c: "Curriculum LF->stack->HF-head on fno_coreg_residual (compose two specialists in three stages)"
cycle_008_new_taxonomy_category_promoted: NEAR_PARITY_INCREMENTAL
cycle_008_new_taxonomy_category_cell: "fno_mf_stack x ifc_poisson (+1.5% over bar)"
cycle_008_top_intervention_1: "fno_coregionalization capacity bump (K=10->20, b_hidden=64->128, n_blocks=4->6) in models/fno_coregionalization/smoke_eval.py SMOKE_DEFAULTS; expected heat 0.01551 -> ~0.012, composite -> ~0.027"
cycle_008_top_intervention_2: "NEW family models/fno_coreg_conditioned/ - m-conditioned single HF FNO; speculative single-family Heat+Poisson winner"
cycle_008_top_intervention_3: "Re-bind c007 H2 LF->HF two-stage schedule on repaired fno_coregionalization constructor (committed code never evaluated, one-PR)"
cycle_008_silent_regression_cache_layer_status: RESOLVED
cycle_008_r1_ceo_verdict: PROCEED
cycle_008_r1_close_out_doc: failure-analysis-cycle-008.md
cycle_008_r2_status: plan_approved
cycle_008_r2_ceo_verdict: PROCEED — PLAN APPROVED
cycle_008_r2_close_out_doc: ceo-verdict-strategist.md
cycle_008_r2_strategy_doc: cycle-008.md
cycle_008_r2_mode: research
cycle_008_r2_hypothesis_count: 3
cycle_008_r2_hypothesis_count_cap: 3
cycle_008_r2_priority_order: "H1 > H2 > H3"
cycle_008_r2_bundling: forbidden
cycle_008_r2_h1_name: "fno_coregionalization capacity bump (paper config K=20, b_hidden=128, n_blocks=6, hidden=128, modes_cap=16)"
cycle_008_r2_h1_category: EXPLOIT
cycle_008_r2_h1_type: code
cycle_008_r2_h1_priority: HIGH
cycle_008_r2_h1_risk: LOW
cycle_008_r2_h1_mutable_surface: "models/fno_coregionalization/smoke_eval.py SMOKE_DEFAULTS only"
cycle_008_r2_h1_model_py_edit: false
cycle_008_r2_h1_expected_composite: ~0.028
cycle_008_r2_h1_expected_heat: ~0.013
cycle_008_r2_h1_kill_switch_heat: 0.0194
cycle_008_r2_h1_wall_budget_min: "12-15"
cycle_008_r2_h1_leakage_risk_level: none
cycle_008_r2_h1_backlog: "**New:** highest-EV single intervention; paper-config wire-up never smoke-evaluated against repaired constructor"
cycle_008_r2_h2_name: "NEW family fno_coreg_conditioned (FiLM-via-LayerNorm on single full-resolution HF FNO)"
cycle_008_r2_h2_category: EXPLORE
cycle_008_r2_h2_type: code
cycle_008_r2_h2_priority: MEDIUM-HIGH
cycle_008_r2_h2_swing_ev: highest
cycle_008_r2_h2_mutable_surface: "NEW models/fno_coreg_conditioned/{model.py, smoke_eval.py, manifest.json, INSPIRATION.md}"
cycle_008_r2_h2_mode_a_preferred: "FNOBlock with FiLMNorm replacing GroupNorm; γ(m),β(m) MLP"
cycle_008_r2_h2_mode_b_fallback: "broadcast-channel B(m) concat to FNO inputs"
cycle_008_r2_h2_expected_composite_range: "0.022-0.040"
cycle_008_r2_h2_expected_heat_range: "0.015-0.025"
cycle_008_r2_h2_expected_poisson_range: "0.05-0.15"
cycle_008_r2_h2_kill_switch_heat: 0.0194
cycle_008_r2_h2_kill_switch_wall_min: 25
cycle_008_r2_h2_leakage_risk_level: none
cycle_008_r2_h2_backlog: "siren_film_fidelity + NEW DIRECTIVE 2026-05-31 seed (b) single-HF-FNO m-conditioned"
cycle_008_r2_h2_citations: ["li2022ifc", "li2020fno", "lyu2023mffno", "beggs2025pdecond", "herde2024poseidon"]
cycle_008_r2_h3_name: "Three-stage curriculum on fno_coreg_residual (LF pretrain → frozen-LF HF residual → basis-head unfreeze) with mandatory recipe_hash checkpoint guard"
cycle_008_r2_h3_category: "EXPLOIT + EXPLORE"
cycle_008_r2_h3_type: code
cycle_008_r2_h3_priority: MEDIUM
cycle_008_r2_h3_mutable_surface: "models/fno_coreg_residual/smoke_eval.py only (BasisHead unchanged)"
cycle_008_r2_h3_stage_strides: "[0.25, 0.5, 0.25]"
cycle_008_r2_h3_recipe_hash_guard: mandatory
cycle_008_r2_h3_expected_composite_range: "0.029-0.033"
cycle_008_r2_h3_expected_heat_range: "0.018-0.022"
cycle_008_r2_h3_expected_poisson_range: "0.05-0.06"
cycle_008_r2_h3_kill_switch_stage3_heat_regress_pct: 25
cycle_008_r2_h3_kill_switch_heat: 0.0194
cycle_008_r2_h3_leakage_risk_level: none
cycle_008_r2_h3_backlog: "cycle-003 checkpoint-resume contamination (verbatim); meta-validity for ALL future research-mode experiments"
cycle_008_r2_anti_patterns_honored:
  - "1. MFRNP loss-recipe / reweighting BANNED (3/3 REVERTs: c003 H1, c006 H1, c007 H2)"
  - "2. Per-dataset MFRNP dispatch BANNED (c007 H2 falsified invariance)"
  - "3. A1+B1+B3 bundling FORBIDDEN (3 independent family directories, zero file overlap)"
  - "4. D1 mf_fno_transfer_bar smoke-config bump DEFERRED (would raise bar)"
  - "5. A3 F-FNO refactor DEFERRED to cycle-009+ as fno_coreg_ffno"
  - "6. NO model.py edit for H1 (constructor already accepts paper kwargs)"
cycle_008_r2_new_backlog_items_for_cycle_009:
  - "fno_coreg_ffno (A3 F-FNO factorized spectral conv, tran2023ffno arXiv:2111.13802)"
  - "fno_coreg_mflno (Cao 2025, arXiv:2502.00550 linear+nonlinear residual decomposition)"
  - "mf_fno_transfer_bar smoke-config bump (D1, defer until smoke composite below parallel-bench bar)"
  - "fno_mf_stack capacity bump (C1, hidden=32→64, n_blocks=3→4, modes scale-up)"
cycle_008_r2_builder_branch_base: "experiment/9-fno_coregionalization-constructor-fix @ 1249f2d"
cycle_008_r2_no_github_active: true
cycle_008_h1_phase: build_ceo_proceed
cycle_008_h1_verdict: PROCEED
cycle_008_h1_ceo_verdict_builder: PROCEED
cycle_008_h1_branch: experiment/11-fno_coregionalization-paper-capacity
cycle_008_h1_parent_branch: experiment/9-fno_coregionalization-constructor-fix
cycle_008_h1_parent_commit: 1249f2d
cycle_008_h1_commit: 18d83a6
cycle_008_h1_files_changed: 1
cycle_008_h1_loc_delta: "+10/-4"
cycle_008_h1_target_file: models/fno_coregionalization/smoke_eval.py
cycle_008_h1_model_py_edited: false
cycle_008_h1_knob_hidden_channels: "32 -> 128"
cycle_008_h1_knob_K: "10 -> 20"
cycle_008_h1_knob_n_blocks: "4 -> 6"
cycle_008_h1_knob_modes_cap: "12 -> 16"
cycle_008_h1_knob_b_hidden: "64 (constructor default) -> 128 (new SMOKE_DEFAULTS key)"
cycle_008_h1_b_hidden_plumbed: true
cycle_008_h1_h2_schedule_preserved_verbatim: true
cycle_008_h1_smoke_2ep_dataset: ifc_heat
cycle_008_h1_smoke_2ep_train_seconds: 4.31
cycle_008_h1_smoke_2ep_params: 50471592
cycle_008_h1_smoke_2ep_peak_mem_gb: 1.73
cycle_008_h1_smoke_200ep_projection_min_total: "14-15"
cycle_008_h1_smoke_kill_switch_cap_min: 25
cycle_008_h1_smoke_epochs_kept: 200
cycle_008_h1_leakage_check_diff_risk_level: none
cycle_008_h1_leakage_check_hypothesis_risk_level: none
cycle_008_h1_surface_guard_baseline: 1249f2d
cycle_008_h1_surface_guard_result: clean
cycle_008_h1_no_github_active: true
cycle_008_h1_build_doc: cycle-008-exp-11-build.md
cycle_008_h1_expected_composite_after_r4: "~0.028 (high ~0.026, low ~0.029)"
cycle_008_h1_expected_heat_after_r4: "~0.013 (high ~0.012, low ~0.014)"
cycle_008_h1_kill_switch_heat_at_r4: 0.0194
---

# Factory: factory_mffp

**Project path**: `/orcd/data/faez/001/nick/mf_field/factory_mffp`

## Status snapshot (2026-06-02)

- **State:** **CYCLE-010 BASELINE FAILURE ANALYSIS COMPLETE 2026-06-02 — CEO=PROCEED → Researcher R1.5.** Composite_nRMSE = 0.022161 reproduces cycle-009 H1+H2 exactly (all 14 cells `_cache: "hit"` on `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb`; zero drift). Three published composite bars already beaten: parallel-bench `mf_fno_transfer @ 0.027429` (−19.2%), IFC-ODE2 geomean 0.0516 (−57%), IFC-GPODE geomean 0.0331 (−33%). Dominant residual failure = **`POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY`** — heat winner `fno_coregionalization` (0.0129, 5.7× under IFC-ODE2) catastrophically fails Poisson (0.598, 16.6× over paper); Poisson winner `fno_mf_stack` (0.0381, 1.06× over IFC-ODE2) is heat-suboptimal at rank-4. Load-bearing cell = `fno_mf_stack × ifc_poisson = 0.038120` (no challenger within 1.89×; closing to IFC-GPODE 0.018 unlocks −31% composite). **100% of remaining per-dataset published-bar gap lives on Poisson** (heat already 4.7× under GPODE). Mechanism: ~50% K-basis B(m)=MLP([m,m²]) inadequate for non-uniform fidelity ladders (Poisson scalers 42× dynamic range, heat 1×; fno_coregionalization × poisson exhibits 11× val→test collapse vs perfect generalization on heat); ~30% MFRNP aggregator Poisson-specialized; ~20% HF-only plain FNO un-bridged. Trajectory 007→010 = 0.0396 → 0.0304 → 0.0277 → **0.0222 → 0.0222** (monotonic descent plateaued at cycle-009 H1+H2). Recommended interventions ranked: (1) push `fno_mf_stack` capacity further (`hidden 64→96`, `modes (4,8,16,20)→(4,8,16,24)/(4,8,20,28)`, `n_blocks 4→5`) — NK-clear, load-bearing direct attack, mandatory Poisson > 0.0594 + wall > 1500s kill-switches; (2) two-stage frozen-LF curriculum on `fno_mf_stack` (**NK2 carve-out applies** — LF/HF-independent design, NOT co-evolved residual ladder) with mandatory dual kill-switches (absolute + inter-stage); (3) `fno_coregionalization` Poisson-specific K-basis `B(m, LF_features)` — distinct from NK3 (basis parametrization, not loss-weighting); (4) restore `fno_coreg_conditioned` with `γ(m, LF_features)` — NK1-safe, speculative. NKs in force unchanged: NK1 pure m-conditioning HF-only; NK2 frozen-LF on residual ladders; NK3 MFRNP loss-weight to coregionalization (3/3). Four new failure-taxonomy entries introduced: `POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY`, `K_BASIS_NON_UNIFORM_FIDELITY_LADDER_COLLAPSE`, `VAL_TO_TEST_INFLATION`, `MFRNP_AGGREGATOR_POISSON_SPECIALIZATION`. CEO Researcher search keys: 2024-2026 FNO capacity-axis on Poisson-class PDEs; MF stacking architectures with LF input concatenation; FiLM-with-LF-features `γ(m, LF_features)`; PyTorch recipe-hash / checkpoint-contract patterns. Detail: [[failure-analysis-cycle-010]]. — Prior: **CYCLE-009 H1+H2 CLOSED 2026-06-02 — formal verdict `revert_bookkeeping_keep_intent` (8th-consecutive, 8-for-8); CEO intent KEEP (5th-consecutive `ceo:keep`).** **NEW REPRODUCIBLE PROJECT BEST composite_nRMSE 0.022161** on `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb` (cut from cycle-008 H1 banked best `experiment/11 @ 18d83a6`). **−20.08% vs prior banked best 0.027729; −27.12% vs cycle-008 entry baseline 0.030408.** **PARALLEL-BENCH BAR DETHRONED FIRST TIME IN 9 CYCLES** — composite 0.022161 < bar 0.027429 by 19.2% (bar gap closed 276.8% — overshoot by 2.77× the prior remaining gap). H1 `fno_mf_stack` paper-config-mirroring capacity bump (`hidden 32→64`, `agg_hidden 32→64`, `n_blocks 3→4`, `modes_per_level (4,8,12,12)→(4,8,16,20)`) delivered Poisson **0.05961 → 0.038120 (−36%)** PLUS unexpected family-internal Heat **0.09995 → 0.038269 (−62%)**. Per-cell post: `ifc_heat` best `fno_coregionalization` 0.012884 (marginal cache-rerun improvement from 0.012898); `ifc_poisson` best NOW **`fno_mf_stack` 0.038120 with 1.89× margin over rank-2 `fno_coreg_residual` 0.07200**. `fno_mf_stack` non-best on heat (4th, 0.038269) but huge family-internal gain. H2 `recipe_hash` portable utility (`models/_common/recipe_hash.py`, 12 LOC, `Mapping[str, Any]` typed, `sha256[:12]`) cherry-picked from `transolver_residual` canonical pattern + applied via canonical 4-patch-site refactor (import → compute → resume guard chained with family-specific preconditions → checkpoint save-dict key) to 3 live FNO families (`fno_mf_stack`, `fno_coreg_residual`, `fno_coregionalization`); cache-invalidation semantic LIVE-VERIFIED — `fno_mf_stack` new hash `acdb1c11caa7` correctly forced fresh training on both datasets (`cache_status=miss`) under new H1 capacity. **META-FIX cycle-003 backlog `recipe_hash` portability ask FULLY CLEARED** for FNO family project-wide (`transolver_residual` and `transolver_attention_fusion` already had canonical inline pattern). Loss weights `poisson_hf_weight=2.0`, `poisson_lf_weight=0.25` explicitly UNCHANGED — NK3 (MFRNP-style loss-weight tuning ban) sidestepped; NK1 (pure m-conditioning) NOT in play; NK2 (frozen-LF curriculum on residual ladder) NOT in play. Poisson kill-switch (0.0594) NOT TRIPPED (0.0381 vs 0.0594, 36% headroom); wall kill-switch (1500 s) NOT TRIPPED (414 s, 72% headroom). 5 files / +45/-8 LOC single commit. Project genuine-REVERT count UNCHANGED at **5**; `revert_bookkeeping_keep_intent` streak now **8** (H1+H2 added at record −20.08% improvement scale). Precheck infra bugs (8th cycle of operator-backlog non-fix): `score_direction` polarity 11 (usual polarity, lower-is-better metric still unhonored); `scope`/`fixed_surfaces` empty-detail 5 (short-SHA-vs-long-SHA sub-class); leakage substring-collision 7th-consecutive builder-phase override (token `"17"` from diff hunk header `@@ -176,9 +178,10 @@` collided with project-doc `factory.md`/`README.md` unrelated `"17"` occurrences). **NEW this cycle: `factory guard --baseline <short-SHA>` short-vs-long-SHA string-equality FP** — guard does string `==` between 7-char caller arg `18d83a6` and full 40-char `git merge-base HEAD 18d83a6` output `18d83a6190d342e0156a2c2547dcf2b2b998d782` → mismatch reported even though same commit. Distinct from leakage substring FP; 2nd known guard FP class; manually overridden by Reviewer. **Cycle-010 entry baseline = `experiment/14 @ 0b6e6eb @ composite 0.022161`** — first project composite under both parallel-bench bar AND paper Heat geomean (Heat 0.012884 = 0.17× paper 0.074; Poisson 0.038120 still 1.06× paper 0.036, the only remaining sub-paper dataset gap). Cycle-009 architectural lever: **capacity-axis playbook transfers cross-family** — paper-config SMOKE_DEFAULTS bump on the dominant-lever family closed the Poisson side after closing the Heat side at cycle-008 H1; first cross-family transfer of the H1 lever in project history. Detail: [[factory_mffp-014-outcome]]. — Prior: **CYCLE-008 CLOSED 2026-06-02 — close-out doc [[cycle-008-summary]].** Three hypotheses run; net effect = **1 KEEP intent (H1) + 2 consecutive GENUINE REVERTs (H2, H3)** — first cycle in project history with two genuine REVERTs. NEW reproducible project best composite_nRMSE **0.030408 → 0.027729 (−8.81%)** on `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6`. Cycle-005 H2 aspirational ceiling (0.029357, unreproducible) BEATEN by −5.55%. Bar (`mf_fno_transfer_bar @ 0.027429` parallel-bench) still wins composite by +0.000300 (+1.09%) — 89.93% of cycle-008-entry bar gap closed by capacity-axis alone. Project genuine-REVERT count now 5; `revert_bookkeeping_keep_intent` streak at 7. META-FIX delivered: `recipe_hash` checkpoint guard pattern WORKS correctly (cycle-003 backlog closed for `fno_coreg_residual`). Three preserved branches: `experiment/11 @ 18d83a6` (banked best, cycle-009 entry), `experiment/12 @ 540e684` (FiLM scaffolding), `experiment/13 @ 420a51c` (recipe_hash pattern source). FOUR new cross-cycle patterns: FiLM-on-HF-only cannot synthesize LF→HF correlation; three-stage frozen-LF curricula incompatible with co-evolved residual ladder; multi-stage kill-switches need Stage-k-vs-baseline absolute check; bookkeeping-overridable REVERT vs genuine architecture-falsified REVERT (diagnostic = R5b, not precheck). Cycle-009 enters at composite 0.027729 with strategic shopping list: (1) cherry-pick recipe_hash into `models/_common/recipe_hash.py` and apply to all families; (2) close +1.09% bar gap on Poisson side (capacity-axis exhausted on `fno_coregionalization`); (3) reject pure m-conditioning AND three-stage-on-residual-ladder at R2 with cycle-008 H2/H3 as citations; (4) 6th-consecutive operator precheck overhaul request remains out-of-cycle. — Prior: **Cycle-008 H1 BUILD PROCEED 2026-06-02 — Builder commit `18d83a6` on `experiment/11-fno_coregionalization-paper-capacity` cut from cycle-007 H1 baseline `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`. Paper-config capacity bump on `fno_coregionalization`: single-file +10/-4 LOC change at `models/fno_coregionalization/smoke_eval.py SMOKE_DEFAULTS` — `hidden_channels 32→128`, `K 10→20`, `n_blocks 4→6`, `modes_cap 12→16`, plus NEW `b_hidden=128` key + minimal plumbing `b_hidden=p["b_hidden"]` at the `FNOCoregionalization(...)` call site so the new key actually reaches the constructor. All five values mirror `models/fno_coregionalization/full_config.json` (li2022ifc paper). `model.py` UNTOUCHED per cycle-008 anti-pattern #6 (cycle-007 H1 constructor already accepts all paper kwargs). H2 LF→HF schedule (`pretrain_lr`, `finetune_lr`, `pretrain_frac`) preserved verbatim from cycle-005 H2 / cycle-007 H1. Smoke verification PASS: 2-epoch end-to-end on `ifc_heat` with `train_seconds=4.31` (2.15 s/epoch), `params=50.47M` (plausible for K=20/hidden=128/n_blocks=6/b_hidden=128), `peak_mem=1.73 GB`; 200-epoch projection ≈ 14-15 min total, comfortably under 25-min kill-switch cap (kept `epochs=200`, no warmup change needed). Surface guard `factory guard --baseline 1249f2d --check-scope` clean. **Leakage scan `flagged: false, risk_level: none` BOTH at Strategist R2 (hypothesis-level) AND at Builder diff-level — first cycle-008 hypothesis (and first in project history) with clean leakage on both passes.** CEO PROCEED ready for R3-review → R4 200-epoch SLURM run. `--no-github` honored (no PR, no push, no issue). All six cycle-008 anti-patterns satisfied: no MFRNP recipe, no per-dataset dispatch, no bundling with H2/H3, no D1 `mf_fno_transfer_bar` smoke edit, no A3 F-FNO refactor, no `model.py` edit. Detail: [[cycle-008-exp-11-build]]. — Prior: Cycle-008 R2 PLAN APPROVED 2026-06-02 (3 hypotheses, priority H1>H2>H3, bundling forbidden — see [[cycle-008]]). Cycle-007 H2 CLOSED 2026-06-02 — verdict `revert` (substantive, GENUINE). CEO intent = REVERT.** R4 composite_nRMSE 0.039578 → **0.044470 (+12.36% REGRESSION)**; `fno_coreg_residual / ifc_heat` 0.02628 → **0.03487 (+32.70%, INVARIANCE VIOLATED)**; `fno_coreg_residual / ifc_poisson` 0.07419 → 0.06087 (**−17.96%, real material gain** but did not take leaderboard from `fno_mf_stack` 0.05961). Heat leaderboard flipped: `fno_coreg_residual` → `mf_fno_transfer_bar` @ 0.03317. Poisson kill-switch (>0.089) NOT tripped (0.06087 << 0.089) but Heat-side had no kill-switch because Strategist R2 claimed "Heat path invariant by construction" — claim empirically **falsified** (6.5× the 5% band). This is the **2nd genuine revert in project history** (1st was cycle-003 H1 @ +91.7%); NOT in the `revert_bookkeeping_keep_intent` streak. Branch `experiment/10-fno_coreg_residual-dataset-recipes @ 87f65b1` PRESERVED (reference only — cycle-008 entry baseline UNCHANGED at cycle-007 H1's `experiment/9 @ 1249f2d` @ 0.030408). NEW cross-cycle pattern: "fresh-train variance can swamp claimed invariance — code-path equivalence does not imply numerical equivalence when fresh trains are involved" (empirical variance on `fno_coreg_residual / ifc_heat` ≥ 34% across 4 cache hashes). Close-out: [[cycle-007-exp-10]] (full lifecycle), [[cycle-007-exp-10-build]] (R3 build), [[ceo-verdict-builder]], [[ceo-verdict-reviewer]], [[ceo-verdict-strategist]], [[ceo-verdict-evaluator]]. — **Prior: Cycle-007 H1 CLOSED 2026-06-02 — verdict `revert_bookkeeping_keep_intent` (6-for-6 streak). CEO intent = KEEP.** R4 composite_nRMSE 0.039578 → **0.030408 (−23.17%)**; `fno_coregionalization` ifc_heat = **0.01551** (reproduces cycle-005 cache within ≈+1e-8 — heat 0.01551 → 0.0194 kill-switch NOT tripped, 20% headroom). Reviewer PASS substantive; Evaluator R4 PASS-KEEP ("the cleanest H1 validation we have had in 6 cycles"). Formal verdict = REVERT due to 3 precheck infrastructure bugs (score_direction polarity flips −23% improvement to +23% "regression"; scope and fixed_surfaces report empty-detail false positives while standalone `factory guard --check-scope` reports clean). All 3 real safety checks (`ground_truth_leakage`, `anti_pattern`, `smoke_test`) PASSED. Branch `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d` preserved as cycle-008 entry baseline. Aspirational 0.029357 NOT crossed (+0.001 short); bar 0.0274 NOT crossed (+0.003 short). Close-out: [[cycle-007-exp-9]] (full lifecycle), [[cycle-007-exp-9-build]] (R3 build). — Prior: Cycle-007 R2 PLAN APPROVED 2026-06-02 (Option B, 2 hypotheses). Cycle-005 CLOSED 2026-06-02 — H2 verdict `revert_bookkeeping_keep_intent` (5th consecutive at the time); prior project best 0.029357 now superseded as the **reproducible** project best by cycle-007 H1's 0.030408.
- **Current project composite_nRMSE (reproducible):** **0.022161** — set by cycle-009 H1+H2 on branch `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb`. **−20.08% vs prior banked best cycle-008 H1 0.027729**; **−27.12% vs cycle-008 entry baseline 0.030408 (cycle-007 H1)**; **−24.51% vs cycle-005 H2 aspirational 0.029357** (unreproducible); **−34.3% vs cycle-005 R0 baseline 0.033726**; **−49.9% vs prior reproducible project best cycle-002 H3 0.04420**. **First project composite under the parallel-bench bar (0.027429) — by 19.2%, gap closed 276.8%, first dethrone in 9 cycles.** This is the cycle-010 entry baseline for monotonic-improvement checks.
- **Project best (reproducible):** **cycle-009 H1+H2 `fno_mf_stack` capacity bump + `recipe_hash` portable utility @ 0.022161** on `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb` (preserved on branch; never merged due to same 4 precheck-bookkeeping bugs + 1 NEW guard FP). `fno_mf_stack × ifc_poisson` 0.05961 → 0.038120 (NEW Poisson leader; 1.89× margin over rank-2 `fno_coreg_residual` 0.07200); `fno_mf_stack × ifc_heat` 0.09995 → 0.038269 (−62% family-internal but non-best; 4th behind `fno_coregionalization` 0.012884). `ifc_heat` winner unchanged at `fno_coregionalization` 0.012884 (marginal cache-rerun improvement from 0.012898). Previous reproducible project best: cycle-008 H1 `fno_coregionalization` paper-config capacity bump @ 0.027729 on `experiment/11 @ 18d83a6` (preserved). Pre-cycle-008 reproducible project best: cycle-007 H1 `fno_coregionalization` constructor fix @ 0.030408 on `experiment/9 @ 1249f2d` (preserved). Pre-cycle-007 reproducible project best: cycle-002 H3 `fno_coreg_residual` @ 0.04420 on `experiment/4 @ 0c46f43` (also preserved, never merged).
- **Per-dataset best (smoke harness, post-cycle-009-H1+H2, reproducible):**
  - `ifc_heat` **0.012884** via `fno_coregionalization` (cycle-008 H1 paper-config capacity bump on cycle-007 H1 anisotropic-modes constructor fix; cycle-009 cache-rerun delivered marginal −0.11% from 0.012898; beats paper 0.074 by 5.74×; gap to #2 `fno_coreg_residual` 0.026273 = 2.04×). H1 target ≤ 0.013 ✅ MET. **Heat: paper-bar 0.17× — solved.**
  - `ifc_poisson` **0.038120** via `fno_mf_stack` (NEW leader as of cycle-009 H1 capacity bump; was 0.05961 cache-hit since cycle-007 R0; −36% improvement; 1.06× over paper 0.036 — last remaining sub-paper dataset gap). Cycle-009 H1 dethroned the Poisson side via capacity-axis playbook cross-family transfer; `fno_mf_stack` now owns Poisson by 1.89× margin over `fno_coreg_residual` 0.07200.
- **Project best history (composite_nRMSE):**
  - **Cycle-009 H1+H2 (2026-06-02): 0.022161 (current reproducible best; cycle-010 entry baseline; first under parallel-bench bar).**
  - Cycle-008 H1 (2026-06-02): 0.027729 (preserved on `experiment/11 @ 18d83a6`; cycle-009 entry baseline).
  - Cycle-007 H1 (2026-06-02): 0.030408 (preserved on `experiment/9 @ 1249f2d`).
  - Cycle-005 H2 (2026-06-02): 0.029357 (**aspirational reference only — not reproducible from committed tree**).
  - Cycle-005 R0 baseline (`bench/all-fno-families`): 0.033726.
  - Cycle-007 R0 honest baseline (2026-06-02): 0.039578 (with `fno_coregionalization` crashing).
  - Cycle-002 H3 (2026-05-15): 0.04420 (first family to beat paper composite geomean 0.05157).
  - Cycle-002 H4 (2026-05-15): 0.07719.
  - Cycle-001 H2 (2026-05-15): 0.11173.
  - Cycle-001 H1 (2026-05-15): 0.10919.
  - v9 baseline: 1.6595.
- **Bar to beat (smoke harness):** `mf_fno_transfer_bar @ 0.05258` smoke composite — surpassed since cycle-005 R0 (0.0337 < 0.0526). Cycle-009 H1+H2 surpasses by 2.37× at 0.022161.
- **Bar to beat (parallel-bench harness):** `mf_fno_transfer @ 0.027429` (from `results/bench_metrics.csv`). **DETHRONED 2026-06-02 by cycle-009 H1+H2** — composite 0.022161 < 0.027429 by 19.2% (gap closed 276.8% — overshoot by 2.77× the prior remaining +0.000300 gap). First parallel-bench bar dethrone in 9 cycles. Capacity-axis playbook (paper-config SMOKE_DEFAULTS bump) closed the Heat side at cycle-008 H1 (`fno_coregionalization`) and the Poisson side at cycle-009 H1 (`fno_mf_stack`) — first cross-family transfer of the H1 lever in project history.
- **Datasets beating paper:** **1 / 17** reproducible — `ifc_heat` via cycle-008 H1 `fno_coregionalization` at **0.012884** (5.74× margin over paper 0.074; cycle-009 cache-rerun delivered −0.11% from 0.012898). `ifc_poisson` last remaining sub-paper gap — `fno_mf_stack` @ 0.038120 = 1.06× over paper 0.036 (cycle-009 H1 closed the cycle-008 1.65× gap to within 6%).
- **Experiments closed:** **14** (cycle 001 H1/H2; 002 H4/H3; 003 H1; 005 H1; 005 H2; 006 H1; 007 H1; 007 H2; 008 H1; 008 H2; 008 H3; **009 H1+H2 bundle**). **8 of 14 verdicts = `revert_bookkeeping_keep_intent`** (cycle-009 H1+H2 ratchets streak from 7 → 8, 8-for-8 across CEO-keep evaluations; **5th-consecutive `ceo:keep` intent** across the streak: cycle-005 H2, cycle-007 H1, cycle-008 H1, cycle-009 H1+H2); **5 of 14 = genuine REVERT** (UNCHANGED) — cycle-003 H1 (composite +91.7%), cycle-006 H1 (composite essentially flat +1.8% with primary Poisson bet regressing +3.6%), cycle-007 H2 (composite +12.36%, Heat invariance violated +32.70%), cycle-008 H2 (composite flat at entry / +9.66% vs banked best, FiLM-via-LayerNorm cannot synthesize LF→HF pathway), cycle-008 H3 (composite flat at entry / +9.66% vs banked best, universal heat kill-switch tripped 26×, three-stage frozen-LF curriculum incompatible with co-evolved residual ladder). Cycle-008 remains the only cycle in project history with two consecutive genuine REVERTs. Precheck-bookkeeping subsystem has gated every single keep-intent eval in project history (**11-of-11 `score_direction` polarity overrides** — 10 usual-polarity firings including cycle-009 H1+H2's 11th instance at record −20.08% improvement scale + 1 OPPOSITE-polarity firing on cycle-008 H2 silencing a real regression as 'Score OK'; **5-of-5 empty-detail `scope` / `fixed_surfaces` overrides** including short-SHA-vs-long-SHA sub-class; **7-of-7 builder-phase leakage substring-collision overrides** including cycle-009 H1+H2's token `"17"` from diff hunk header). **NEW guard FP class introduced cycle-009: `factory guard --baseline <short-SHA>` short-vs-long-SHA string-equality FP** — distinct from leakage substring FP; 2nd known guard FP class. cycle-008 H2 and H3 REVERTs are NOT in the `revert_bookkeeping_keep_intent` streak — composite genuinely failed to improve and regressed vs banked best (R5b monotonic check is independent of precheck and is the load-bearing gate for keep-vs-revert).

## Cycle 010 Baseline Failure Analysis (PROCEED 2026-06-02 — Researcher R1.5 greenlit)

**Close-out doc:** [[failure-analysis-cycle-010]]. **Analyst full doc:** `.factory/research/runs/cycle-010-baseline/failure_analysis.md`. **CEO verdict doc:** `.factory/reviews/ceo-verdict-failure_analyst.md`.

**Branch under analysis:** `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb` — cycle-009 H1+H2 banked best, **identical reproduction** (all 14 cells `_cache: "hit"`).

### Baseline headline

| Metric | Value | Note |
|---|---|---|
| **Composite nRMSE** | **0.022161** | identical to cycle-009 H1+H2; zero drift |
| `ifc_heat` best | 0.012884 (`fno_coregionalization`) | 0.17× IFC-ODE2 paper 0.074; 0.21× IFC-GPODE 0.061 |
| `ifc_poisson` best | 0.038120 (`fno_mf_stack`) | 1.06× IFC-ODE2 paper 0.036; 2.12× IFC-GPODE 0.018 |
| Composite vs parallel-bench bar 0.027429 | −19.2% **under** | bar dethroned |
| Composite vs IFC-ODE2 geomean 0.0516 | −57% **under** | paper bar dethroned |
| Composite vs IFC-GPODE geomean 0.0331 | −33% **under** | aspirational paper bar dethroned |

### Dominant failure mode — `POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY`

No single family wins both datasets. The heat-winner is Poisson-catastrophic:

- `fno_coregionalization × ifc_heat` 0.012884 (sole heat winner, no challenger within 2.04×) — **but** `fno_coregionalization × ifc_poisson` = **0.598** (16.6× over IFC-ODE2 paper, 33.2× over GPODE).
- `fno_mf_stack × ifc_poisson` 0.038120 (sole Poisson winner, no challenger within 1.89×; rank-2 `fno_coreg_residual` at 0.072) — **but** `fno_mf_stack × ifc_heat` 0.038269 = rank-4 (3× worse than the heat leader).

This blocks any single-family path to composite improvement at this state.

### Load-bearing-cell analysis

- **Local sensitivities:** d(composite)/d(heat) = 0.86, d(composite)/d(poisson) = 0.29 — heat has 3× the per-unit-absolute leverage.
- **Relative room** favors Poisson: closing Poisson to IFC-GPODE 0.018 unlocks **−31% composite**; closing Poisson to IFC-ODE2 0.036 unlocks only −2.8%.
- **Load-bearing cell:** `fno_mf_stack × ifc_poisson = 0.038120`. Closing this single cell drives all available cycle-010 composite movement.
- **Secondary lever:** `fno_coregionalization × ifc_heat = 0.012884`. Heat already 4.7× under GPODE — no published bar to chase, near-asymptote.

### Mechanism breakdown (per-cell evidence in [[failure-analysis-cycle-010]])

| Share | Mechanism | Evidence |
|---|---|---|
| ~50% | K-basis B(m)=MLP([m,m²]) inadequate for non-uniform fidelity-magnitude ladders | Per-fid scaler heat [1,1,1,1] vs poisson [0.077, 0.024, 0.0069, 0.0018] = 42× dynamic range; `fno_coregionalization × poisson` 11× val→test collapse on same architecture+curriculum that generalizes perfectly on heat |
| ~30% | MFRNP aggregator path is Poisson-specialized | `fno_mf_stack` equalizes heat (0.0383) ≈ poisson (0.0381) on dissimilar PDEs |
| ~20% | HF-only plain FNO architectures un-bridged on Poisson | `v9_baseline × poisson` 18.5 (×13.5 val→test); `transolver_residual × poisson` 2.6 (×5.2 val→test) — out-of-frame |

### Trajectory (cycles 007 → 010)

| Cycle | composite | best heat | best poisson | event |
|---|---|---|---|---|
| 007 baseline | 0.039578 | 0.026277 (`fno_coreg_residual`) | 0.059611 (`fno_mf_stack`) | `fno_coregionalization` crashed (constructor bug) |
| 008 baseline | 0.030408 | 0.015511 (`fno_coregionalization`) | 0.059611 | constructor fix landed (c007 H1) |
| 009 baseline | 0.027729 | 0.012884 (`fno_coregionalization`) | ~0.060 | paper-config capacity bump (c008 H1) |
| **009 H1+H2** | **0.022161** | 0.012884 | **0.038120** (`fno_mf_stack`) | `fno_mf_stack` capacity bump + `recipe_hash`, −20.08% |
| **010 baseline** | **0.022161** | 0.012884 | 0.038120 | identical reproduction; all 14 cells cache-hit |

Monotonic descent for 4 cycles; cycle-010 plateaued at the cycle-009 H1+H2 result.

### Ranked interventions (all within `models/**`)

1. **Push `fno_mf_stack` capacity further** (Poisson lever) — `models/fno_mf_stack/smoke_eval.py` SMOKE_DEFAULTS sweep ladder: modes_per_level (4,8,16,20)→(4,8,16,24)→(4,8,20,28); hidden 64→96; n_blocks 4→5. **NK-clear** (in-family capacity). Mandatory kill-switches: Poisson > 0.0594 (cycle-008 baseline); wall > 1500 s. Builder predicted floor 0.05–0.06 on cycle-009 H1; actual floor 0.0381 was 36% better — ladder may have additional headroom. Expected: −10 to −20% Poisson → −3 to −6% composite.
2. **Two-stage frozen-LF curriculum on `fno_mf_stack`** — `models/fno_mf_stack/smoke_eval.py` + `model.py`. **NK2 carve-out applies** — `fno_mf_stack` is per-fidelity stacked with MFRNP joining only at output (LF/HF *independent by design*), NOT a co-evolved residual ladder. Apply cycle-008 H2 LF→HF schedule (50 LF-only / 150 joint, cosine restart). **Mandatory dual kill-switches:** absolute (Poisson > 0.0594, heat > 0.0594) AND inter-stage (stage-2 best_val must reduce stage-1 best_val by ≥10%). Wall budget 1800 s.
3. **`fno_coregionalization` Poisson-specific K-basis revision** — `models/fno_coregionalization/model.py`. Replace `B(m)=MLP([m, m²])` on Poisson with `B(m, LF_features)`. **NK-distance:** not NK3 (NK3 = loss-weight transfer; this = basis parametrization). Heat-regression guard at 0.0194. Speculative — would not improve composite unless basis below 0.038, but creates second Poisson contender.
4. **Restore `fno_coreg_conditioned` with `γ(m, LF_features)`** — `models/fno_coreg_conditioned/` (currently empty except `__pycache__`). **NK1-safe** via LF-pathway inclusion. Lowest priority — substantial implementation surface.
5. **Deferred — NK3-blocked:** MFRNP-Poisson recipe transfer to `fno_coreg_residual`. Do not pursue (3/3 failures: c003 H1, c006 H1, c007 H2).
6. **Deferred — high-cost low-prior:** transolver_residual revamp, MF-DeepONet.

### Anti-patterns in force (NKs unchanged from cycle-009)

- **NK1** — pure m-conditioning on HF-only FNO without LF→HF pathway (cycle-008 H2 falsified on Poisson).
- **NK2** — frozen-LF curricula on co-evolved residual ladders (`fno_coregionalization`, `fno_coreg_residual`); cycle-008 H3 falsified at 26× heat kill-switch. **Permitted** on LF/HF-independent designs (`fno_mf_stack`, `mf_fno_transfer_bar`) **only with mandatory dual kill-switches**.
- **NK3** — MFRNP-style loss-weight transfer to coregionalization family. 3/3 cycle failures (003/006/007). Closed.

### Failure taxonomy additions (cycle-010)

- `POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY` — dominant mode. Different families win different datasets; heat-winner family is Poisson-broken and vice-versa.
- `K_BASIS_NON_UNIFORM_FIDELITY_LADDER_COLLAPSE` — `B(m)=MLP([m,m²])` generalizes on uniform fidelity scalers but collapses 11× val→test on non-uniform (42× dynamic-range) ladders.
- `VAL_TO_TEST_INFLATION` — cross-cell category for val/test ratio > 5×.
- `MFRNP_AGGREGATOR_POISSON_SPECIALIZATION` — `fno_mf_stack` equalizes heat/poisson at ~0.038; aggregator is Poisson-shaped, sub-optimal on heat.

### CEO instructions for downstream (R1.5 Researcher)

Search keys (full guidance in [[failure-analysis-cycle-010]]):

- 2024–2026 FNO capacity-axis on Poisson-class PDEs (modes scaling, channel width, n_blocks).
- 2024–2026 multi-fidelity stacking architectures with LF inputs concatenated/added to HF FNO (the `fno_mf_stack` pattern).
- 2024–2026 FiLM-with-LF-features `γ(m, LF_features)` conditioning for MF field prediction.
- 2024–2026 PyTorch recipe-hash / checkpoint-contract patterns (operational meta-fix backlog now closed for FNO family per cycle-009 H2; new families may need re-tooling).

---

## Cycle 009 H1+H2 CLOSED (2026-06-02 — formal `revert_bookkeeping_keep_intent` 8th / CEO intent KEEP / NEW PROJECT BEST / BAR DETHRONED)

**Close-out doc:** [[factory_mffp-014-outcome]]. **Build-phase predecessor:** [[cycle-009-exp-14-build]]. **Strategy snapshot:** [[strategies/cycle-009-strategy]]. **Baseline failure analysis:** [[failure-analysis-cycle-009]].

**Branch:** `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb` — **PRESERVED as cycle-010 entry baseline**. Parent: `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` (cycle-008 H1 banked best). Single H1+H2 bundle commit per Strategist R2 (research-mode bundling permitted for tight scope).

### Quantitative outcome

| Metric | Value | vs target | Status |
|---|---|---|---|
| **Composite nRMSE (H1+H2 branch)** | **0.022161** | < 0.027729 (banked best) | **NEW REPRODUCIBLE PROJECT BEST −20.08%** |
| Composite vs cycle-008 entry baseline (1249f2d) | **−27.12%** (0.030408 → 0.022161) | improve | record |
| Composite vs parallel-bench bar 0.027429 | **−19.2% under bar** (0.022161 vs 0.027429) | dethrone | **BAR DETHRONED FIRST TIME IN 9 CYCLES** (gap closed 276.8%) |
| `fno_mf_stack × ifc_poisson` | **0.038120** | < 0.0594 kill-switch; Builder pred 0.05–0.06 | **NEW POISSON LEADER**; −36% vs prior 0.05961; 36% kill-switch headroom |
| `fno_mf_stack × ifc_heat` | 0.038269 | (no target) | **−62% family-internal gain** (was 0.09995); non-best (4th, behind `fno_coregionalization` 0.012884) |
| `ifc_heat` best (post) | 0.012884 `fno_coregionalization` | hold | marginal cache-rerun improvement from 0.012898 (−0.11%); family-leader unchanged |
| `ifc_poisson` best (post) | **0.038120 `fno_mf_stack`** | minimize | NEW leader; 1.89× margin over rank-2 `fno_coreg_residual` 0.07200 |
| Poisson kill-switch | NOT TRIPPED | 0.0381 < 0.0594 threshold | 36% headroom |
| Wall kill-switch | NOT TRIPPED | 414 s < 1500 s threshold | 72% headroom |
| Total cycle_eval wall | 414 s | < 1500 s | CLEAR |

### Why this is a load-bearing project milestone

This is the **first project composite under both the parallel-bench bar AND the paper geomean on Heat** (Heat 0.012884 = 0.17× paper 0.074; Poisson 0.038120 = 1.06× paper 0.036, the only remaining sub-paper dataset gap). The cycle-008 H1 trajectory (89.93% bar gap closed via Heat-side capacity-axis on `fno_coregionalization`) plus the cycle-009 H1 Poisson-side capacity-axis on `fno_mf_stack` collapsed the remaining +1.09% bar gap and overshot by 19.2% under the bar. **The capacity-axis playbook (paper-config SMOKE_DEFAULTS bump on the dominant-lever family) generalizes cross-family** — first cross-family transfer of the H1 lever in project history.

### Verdict mechanics — `revert_bookkeeping_keep_intent` 8th-consecutive at record-improvement scale

The 7 prior `revert_bookkeeping_keep_intent` cases shared a specific pattern: composite **genuinely improved**, precheck false-positives tripped formal verdict, CEO override → effectively KEEP. **Cycle-009 H1+H2 fits this pattern at the largest single-cycle composite improvement scale in project history (−20.08%).** All 4 documented precheck bookkeeping bugs fired:

- **`score_direction` polarity (11th instance, usual polarity):** −20.08% improvement reported as +20.08% regression (lower-is-better metric still not honored — 9 cycles of operator backlog ungrasped).
- **`scope` empty-detail (5th instance):** false positive with `"detail": "Guard violations: "` (empty).
- **`fixed_surfaces` empty-detail (5th instance):** same pattern; short-SHA-vs-long-SHA sub-class.
- **Leakage substring-collision (7th-consecutive builder phase):** token `"17"` matched diff hunk header `@@ -176,9 +178,10 @@` against `factory.md`/`README.md` `"17"` occurrences. Standing override per cycle-008 close-out practice.

**NEW this cycle — `factory guard --baseline <short-SHA>` short-vs-long-SHA string-equality FP:** caller passes 7-char `18d83a6`; `git merge-base HEAD 18d83a6` returns the full 40-char `18d83a6190d342e0156a2c2547dcf2b2b998d782`. Guard does string `==` between the short caller arg and the full git output → mismatch reported even though both refer to the same commit. Reviewer manually verified branch IS correctly rooted at the cycle-008 H1 banked-best commit. **2nd known guard FP class** distinct from the leakage substring FP; cycle-010 close-out operator backlog flag.

**Bookkeeping non-load-bearing for the decision:** CEO KEEP intent grounded in R5b monotonic check (composite −20.08% < 0.027729; independent of precheck) AND R5c universal kill-switches both CLEAR (Poisson 36% headroom, wall 72% headroom). R5b PASS — streak ratchets 7 → **8**.

### META-FIX cycle-003 backlog FULLY CLEARED

The cycle-003 H1 stage-resume contamination pathway is **closed project-wide for the entire FNO family**. H2 promoted the H3 inline pattern (cycle-008 H3, `fno_coreg_residual` only) to a shared `models/_common/recipe_hash.py` utility (12 LOC, `Mapping[str, Any]` typed, `default=str`, `sha256[:12]`) cherry-picked from `transolver_residual`'s canonical in-tree pattern, applied via canonical 4-patch-site refactor to:

- `fno_mf_stack` (recipe hash `acdb1c11caa7` post-bump — NEW; **invalidated cycle-008 cache by design**, both datasets `cache_status=miss`, fresh training forced under new H1 capacity — exactly the deliberate cache-safety semantic).
- `fno_coreg_residual` (recipe hash `1cc35377b46d` stable; SMOKE_DEFAULTS unchanged).
- `fno_coregionalization` (recipe hash `5011def485a6` stable; SMOKE_DEFAULTS unchanged; resume guard preserves family-specific `sd.get("grid") == list(grid)` precondition).

`transolver_residual` (canonical inline pattern source) and `transolver_attention_fusion` already had the helper inline. **Cycle-003 backlog FNO-family scope: 5/5 families consume `recipe_hash` correctly.** Operationally closed for cycle-010+ research-mode experiments.

### Streak counters after cycle-009 H1+H2

| Counter | Before cycle-009 H1+H2 | After cycle-009 H1+H2 |
|---|---:|---:|
| Project genuine-REVERT count | 5 | **5 (UNCHANGED)** |
| `revert_bookkeeping_keep_intent` consecutive streak | 7 | **8** |
| `ceo:keep` intent consecutive streak | 4 | **5** |
| Leakage substring-collision FP consecutive (builder phase) | 6 | **7** |
| `score_direction` polarity FP count (any polarity) | 10 | **11** |
| `scope`/`fixed_surfaces` empty-detail FP count | 4 | **5** |
| Guard short-vs-long SHA equality FP class | 0 | **1 (NEW this cycle)** |
| Cycle-003 backlog `recipe_hash` portability — FNO family | partially closed (1/3 via cycle-008 H3 inline) | **FULLY CLEARED (3/3 FNO + 2/2 Transolver)** |

### Cycle-010 entry state

- **Composite:** **0.022161** (composite_nRMSE) — first under parallel-bench bar AND paper Heat geomean.
- **Branch:** `experiment/14-fno_mf_stack-capacity-and-recipe-hash`
- **Commit:** `0b6e6eb` (preserved on disk).
- **Parent:** `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` (cycle-008 H1 banked best — also preserved as fallback reference).
- **Per-dataset state:** `ifc_heat` 0.012884 via `fno_coregionalization` (5.74× margin over paper); `ifc_poisson` 0.038120 via `fno_mf_stack` (NEW leader; 1.89× over rank-2; 1.06× over paper).
- **Bar status:** dethroned by 19.2% (0.022161 < 0.027429). Cycle-010 monotonic-improvement baseline = **0.022161**.
- **Preserved reference branches:** `experiment/14 @ 0b6e6eb` (cycle-010 entry), `experiment/11 @ 18d83a6` (cycle-008 H1 banked best — fallback), `experiment/13 @ 420a51c` (cycle-008 H3 recipe_hash inline source), `experiment/12 @ 540e684` (FiLM scaffolding — still available for γ(m, LF_features) revisit), `experiment/9 @ 1249f2d` (cycle-007 H1 anisotropic-modes constructor fix), `experiment/4 @ 0c46f43` (cycle-002 H3 prior reproducible best).

### Cycle-010 strategic priorities (carried forward)

1. **Last remaining sub-paper dataset gap: `ifc_poisson` 0.038120 → < 0.036 (paper geomean) = −5.7% more.** Capacity-axis on `fno_mf_stack` may have additional headroom (Builder predicted 0.05–0.06, actual 0.0381 was 36% better than predicted floor); or alternative levers (LF-feature conditioning per cycle-008 H2 banked γ(m, LF_features) carve-out; cycle-008 H3 three-stage on `fno_mf_stack` per NK2 family-independent carve-out — `fno_mf_stack` is per-fidelity stacked, NOT a co-evolved residual ladder, so three-stage MAY apply here).
2. **Watch for `fno_coreg_residual` Poisson re-take:** rank-2 now at 0.07200 vs `fno_mf_stack` 0.038120 (1.89× margin) — cycle-010 must not regress `fno_mf_stack` Poisson back over the rank-2 line.
3. **9th-consecutive operator precheck overhaul request remains** out-of-cycle. Now includes the NEW `factory guard --baseline <short-SHA>` short-vs-long-SHA string-equality FP — should switch guard to `git rev-parse` normalization before string comparison.
4. **`recipe_hash` portable utility now live infrastructure** — cycle-010 hypotheses MAY assume cache-safety on FNO family; cache invalidation is automatic on SMOKE_DEFAULTS change.

### Precheck infra bug counters (after cycle-009 H1+H2)

| Bug | Before c009 | After c009 H1+H2 |
|---|---:|---:|
| `score_direction` polarity (any polarity, lower-is-better metric not honored) | 10 | **11** (H1+H2 11th, usual polarity, −20.08% improvement reported as +20.08% regression) |
| Empty-detail `scope` / `fixed_surfaces` (incl. short-SHA-vs-long-SHA sub-class) | 4 | **5** (H1+H2 added) |
| Leakage-check substring collision (builder phase, consecutive) | 6 | **7** (H1+H2 added — token `"17"` from diff hunk header) |
| `factory guard --baseline <short-SHA>` short-vs-long-SHA equality FP | 0 | **1 (NEW this cycle)** |
| `revert_bookkeeping_keep_intent` universal verdict (consecutive) | 7 | **8** (H1+H2 added) |
| `ceo:keep` intent (consecutive across the streak) | 4 | **5** (H1+H2 added) |
| Genuine REVERT total | 5 | **5 (UNCHANGED)** |
| Cycle-003 backlog `recipe_hash` portability for FNO family | partial (1/3) | **FULLY CLEARED (3/3)** |

---

## Cycle 008 CLOSED (2026-06-02 — H1 KEEP intent / H2 GENUINE REVERT / H3 GENUINE REVERT)

**Close-out doc:** [[cycle-008-summary]]. **Failure analysis:** [[failure-analysis-cycle-008]]. **Strategy snapshot:** [[strategies/cycle-008]].

**Cycle outcome:** 3 hypotheses run on the cycle-007 H1 reproducible
frontier; net effect = **1 KEEP intent (H1 banked best 0.027729) + 2
consecutive GENUINE REVERTs (H2 architecture-falsified on Poisson; H3
architecture-incompatible-three-stage-on-residual-ladder)**. **First
time in project history with two genuine REVERTs in one cycle**
(cycles 003, 006, 007 each had 1). Project genuine-REVERT count now
**5**; `revert_bookkeeping_keep_intent` streak unchanged at **7** (H1
added).

| Hypothesis | Composite Δ vs banked best | Real outcome | Verdict | Cycle-009 status |
|---         |---:                        |---           |---      |---               |
| H1 (exp 11) — `fno_coregionalization` paper-config capacity bump | **−8.81%** (0.030408 → 0.027729) | NEW reproducible project best; 89.93% bar gap closed; both H1 hard component targets MET | `revert_bookkeeping_keep_intent` (KEEP intent) | **banked as cycle-009 entry baseline** |
| H2 (exp 12) — NEW family `fno_coreg_conditioned` (FiLM-via-LayerNorm) | flat at entry / **+9.66%** vs banked best | Heat near-miss 2nd (+10.3%); Poisson catastrophic 5th (12.6× over leader); architecture-falsified | genuine REVERT (substantive, NOT bookkeeping) | branch preserved for potential cycle-009 revisit with γ(m, LF_features) |
| H3 (exp 13) — three-stage frozen-LF curriculum on `fno_coreg_residual` + `recipe_hash` checkpoint guard | flat at entry / **+9.66%** vs banked best | Heat regressed 19× to 0.509 (universal kill-switch tripped 26×); Poisson 2.15× over baseline; architecture-incompatible with co-evolved residual ladder | genuine REVERT (substantive, NOT bookkeeping) | branch preserved for `recipe_hash` pattern reuse only |

**Net cycle-008 outcome:** reproducible project best
**0.030408 → 0.027729 (−8.81%)** on
`experiment/11-fno_coregionalization-paper-capacity @ 18d83a6`. Both
H1 hard component targets met (composite ≤ 0.028 ✅ AND
`ifc_heat ≤ 0.013` ✅; the actual values 0.027729 and 0.012898 both
clear thresholds with margin). Cycle-005 H2 aspirational unreproducible
ceiling (0.029357) **beaten by −5.55%** — project moves into
reproducible sub-0.028 territory for the first time. Parallel-bench
bar (`mf_fno_transfer_bar @ 0.027429`) still wins composite by
+0.000300 (+1.09%) — capacity-axis exhausted on
`fno_coregionalization`; cycle-009 must close the +1.09% gap from the
Poisson side.

### META-FIX delivered: `recipe_hash` checkpoint guard

Despite H3's architectural REVERT, the cycle-003 backlog meta-fix
**WORKED CORRECTLY**: stale-checkpoint rejection log line
verified (`[resume] REJECTED stale checkpoint: recipe_hash
'148a2641b07fe5da' != '0095c3ff614e17b8'`). cycle-009 action:
cherry-pick the pattern from
`models/fno_coreg_residual/smoke_eval.py` (lines ~113-123, 461-485)
into a portable utility `models/_common/recipe_hash.py` and apply
it to ALL family `smoke_eval.py` files — closes the cycle-003 H1
stage-resume contamination pathway **project-wide**. Three-stage
gating logic is NOT reusable; do NOT cherry-pick into other
families with co-evolved residual ladder architectures.

### Four NEW cross-cycle architectural patterns (cycle-009 R2 input)

1. **FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF
   correlation pathway** — pure m-conditioning via γ(m), β(m) can
   re-scale per-fidelity representations but cannot CREATE LF→HF
   structure. Insufficient for Poisson-class datasets where LF
   samples carry significant complementary information. cycle-009
   implication: reject pure m-conditioning at R2 for any
   single-family Heat+Poisson candidate; require either (a) LF→HF
   residual pathway OR (b) LF-feature conditioning in FiLM affines
   (γ(m, LF_features) instead of γ(m, m²)). First observed
   cycle-008 H2.
2. **Three-stage frozen-LF-HF-residual curricula are INCOMPATIBLE
   with co-evolved residual ladder designs** —
   `fno_coreg_residual` and `fno_coregionalization` assume LF and
   HF networks co-evolve end-to-end; Stage-2 LF freeze forces HF
   residual to correct against OOD frozen LF state. Three-stage
   MAY be appropriate for families with LF/HF independent by
   design (`mf_fno_transfer_bar`, `fno_mf_stack`). cycle-009
   implication: reject three-stage on residual-ladder families at
   R2. First observed cycle-008 H3.
3. **Multi-stage curriculum kill-switches MUST include
   Stage-k-vs-baseline absolute check** — single inter-stage ratio
   kill-switches assume damage occurs in LATER stage only;
   fragile. Real damage can occur in ANY stage (cycle-008 H3 ratio
   was 1.00 because Stage 2 already produced the damage). Any
   cycle-009 multi-stage proposal MUST specify BOTH absolute and
   inter-stage kill-switches. First observed cycle-008 H3.
4. **Bookkeeping-overridable REVERT vs genuine
   architecture-falsified REVERT — diagnostic is R5b monotonic,
   not precheck** — the CEO playbook distinction surfaced
   explicitly in cycle-008 H2/H3. Symptom of
   `revert_bookkeeping_keep_intent`: real composite improvement +
   precheck infra bugs trip formal verdict. Symptom of genuine
   REVERT: real composite regression OR universal kill-switch
   trip; precheck bugs incidental. First explicit articulation
   cycle-008 H2; reinforced H3.

### Cycle-009 entry state (UNCHANGED by H2 and H3)

- **Composite:** **0.027729** (composite_nRMSE)
- **Branch:** `experiment/11-fno_coregionalization-paper-capacity`
- **Commit:** `18d83a6` (preserved on disk)
- **Parent:** `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`
- **Per-dataset state:** `ifc_heat` 0.012898 (via
  `fno_coregionalization`, 2.04× margin over second-place);
  `ifc_poisson` 0.05961 (via `fno_mf_stack`).
- **Bar gap remaining:** composite 0.027729 vs bar 0.027429 =
  **+0.000300 (+1.09% above bar)**.
- **Preserved reference branches:** `experiment/11 @ 18d83a6`
  (banked best, cycle-009 entry), `experiment/12 @ 540e684`
  (FiLM scaffolding — 828 LOC for potential cycle-009 revisit
  with `γ(m, LF_features)`), `experiment/13 @ 420a51c`
  (`recipe_hash` checkpoint guard pattern — cycle-009 cherry-pick
  target for `models/_common/recipe_hash.py`).

### Cycle-009 strategic priorities (carried forward)

1. **Cherry-pick `recipe_hash` pattern into
   `models/_common/recipe_hash.py`** and apply to ALL family
   `smoke_eval.py` files. Closes cycle-003 H1 stage-resume
   contamination pathway PROJECT-WIDE.
2. **Close the +1.09% bar gap on the Poisson side** —
   capacity-axis on `fno_coregionalization` exhausted; next lever
   must come from Poisson. Two paths: (a) reduce
   `fno_mf_stack × ifc_poisson` below 0.05961, or (b) push
   `fno_coregionalization × ifc_poisson` below 0.05961 (currently
   0.5945 — 10× gap to leader).
3. **Any single-family Heat+Poisson architecture proposal** must
   include EITHER an LF→HF residual pathway OR LF-feature
   conditioning in FiLM affines; reject pure m-conditioning at R2
   with cycle-008 H2 as citation.
4. **Any multi-stage curriculum proposal** must (i) only target
   families with LF/HF networks independent by design
   (`mf_fno_transfer_bar`, `fno_mf_stack`), NOT residual-ladder
   families; AND (ii) specify BOTH absolute Stage_k-vs-baseline
   AND inter-stage ratio kill-switches; reject single inter-stage
   ratio kill-switches at R2 with cycle-008 H3 as citation.
5. **Operator precheck overhaul (6th consecutive request)** —
   `score_direction` polarity for lower-is-better metrics
   (10-of-10 including symmetric flip in H2);
   `scope`/`fixed_surfaces` short-SHA mismatch + empty-detail
   (4-of-4); leakage substring collision (6-of-6 builder phase).
   Out of factory scope.

### Precheck infra bug counters (after cycle-008)

| Bug | Before c008 | After c008 |
|---|---:|---:|
| `score_direction` polarity (lower-is-better metric) | 8 | **10** (H1 9th instance; H2 10th instance, symmetric flip silencing regression) |
| Empty-detail `scope` / `fixed_surfaces` | 3 | **4** (H1 added; short-SHA mismatch sub-class) |
| Leakage-check substring collision (builder phase) | 5 | **6** (H2 added — `satisfy, description, ifc_raw, frozen` — schema/dispatch tokens) |
| `revert_bookkeeping_keep_intent` universal verdict | 6 | **7** (H1 added) |
| Genuine REVERT total | 3 | **5** (H2 + H3 added) |

---

## Cycle 008 H2 CLOSED (2026-06-02 — verdict `revert` — GENUINE, architecture-falsified on Poisson)

**Close-out doc:** [[cycle-008-exp-12-final]]. **Review-phase predecessor:** [[cycle-008-exp-12-review]]. **Build-phase predecessor:** [[cycle-008-exp-12-build]].

**Branch:** `experiment/12-fno_coreg_conditioned-film @ 540e684` — **PRESERVED, not merged**. Parent: `1249f2d` (cycle-008 entry baseline; cycle-007 H1 anisotropic-modes constructor fix). Branch independence from H1's `experiment/11` verified per cycle-008 anti-pattern #3 (no bundling).

### Quantitative outcome

| Metric | Value | vs target | Status |
|---|---|---|---|
| **Composite nRMSE (H2 branch)** | 0.030408 | minimize | flat vs entry baseline |
| Composite vs cycle-008 entry baseline (1249f2d) | 0.000000 / +0.00% | improve | NEUTRAL |
| Composite vs banked best (cycle-008 H1 exp 11 @ 0.027729) | +0.002679 / **+9.66%** | improve or hold | **REGRESSION** |
| `fno_coreg_conditioned × ifc_heat` | 0.017102 | < 0.0194 kill-switch | CLEAR (2nd; behind `fno_coregionalization` 0.01551 by ~10%) |
| `fno_coreg_conditioned × ifc_poisson` | 0.749915 | Builder predicted 0.05–0.15 | **OUT OF RANGE** (~5–15× worse than predicted; 5th; behind `fno_mf_stack` 0.05961 by 12.6×) |
| Smoke wall (new family only) | 91.99 s | < 25-min kill-switch | CLEAR (~16× under budget) |
| Total cycle_eval wall | 93 s | budget 14400 s | CLEAR (cache-served all other families) |

### Why composite is exactly flat at entry baseline

The composite is the geomean of per-dataset bests. `fno_coreg_conditioned` does NOT dominate either cell (heat 2nd by 10%; poisson 5th by 12.6×) → contributes ZERO to composite. The new family lands close but non-dominant on Heat, catastrophic on Poisson.

### NOT `revert_bookkeeping_keep_intent` — diagnostic is R5b, not precheck

The 7 prior consecutive `revert_bookkeeping_keep_intent` cases shared a specific pattern: composite **genuinely improved**, but precheck false-positives triggered a false revert. CEO override → effectively KEEP. **This case is structurally different:**
- Composite is **flat at entry baseline**, not improved.
- Composite is **+9.66% above banked best** — a real regression vs the active project frontier.
- The hypothesis predicted Poisson 0.05–0.15; actual is 0.7499 (5–15× off).
- Implementation was correct (Reviewer PASS earlier in the day); the architecture (FiLM-via-LayerNorm on a single HF FNO) was tested honestly and falsified on Poisson.

**Precheck this cycle:** 3/4 documented bookkeeping patterns fired (`scope`, `fixed_surfaces`, `ground_truth_leakage`); `score_direction` polarity bug fired in **OPPOSITE polarity** this time — silenced a real +0.0027 regression as "Score OK" because precheck treats higher-after-as-better but composite_nRMSE is lower-is-better. This is the symmetric flip of the bug (1st OPPOSITE-polarity occurrence; usual-polarity count is 9). Bookkeeping is **non-load-bearing** for the decision; CEO REVERT grounded in **Evaluator R5b monotonic check** (independent of precheck).

### Architectural lesson — failure mode classification for cycle-009

**FiLM-via-LayerNorm on single HF FNO is insufficient for `ifc_poisson`.** The Poisson dataset has strong LF→HF correlation signal (`fno_mf_stack` 0.05961 and `fno_coreg_residual` 0.07419 both exploit the LF input directly). H2's HF-only architecture **discards the LF channel by design** — only m-conditioning via FiLM affines remains. FiLM γ/β can re-scale a learned representation per fidelity, but cannot CREATE the LF→HF structure that the multi-fidelity families exploit. Heat (where LF signal is less dominant) was a near-miss at 0.01710.

**Cycle-009 implication:** Any single-family Heat+Poisson candidate must either (a) re-introduce the LF→HF pathway (residual ladder) OR (b) condition on LF samples directly in the FiLM affines (γ(m, LF_features) instead of γ(m, m²)). **Pure m-conditioning is insufficient.**

### Kill-switch summary

- `ifc_heat > 0.0194`: CLEAR (0.0171 < 0.0194 by 12%)
- Smoke wall-time > 25 min: CLEAR (1.53 min, 16× under)
- **Neither kill-switch triggered → revert is on composite/cell-dominance grounds.** Failure mode = silent under-performance, not blow-up.

### Cycle-008 sequence summary

| Step | Hypothesis | Verdict class | Composite delta | Banked? |
|---|---|---|---:|---|
| Entry | cycle-007 H1 baseline `1249f2d` | — | (= 0.030408) | yes |
| H1 (exp 11) | Paper-config capacity bump on `fno_coregionalization` | `revert_bookkeeping_keep_intent` (KEEP intent) | **−8.81%** to 0.027729 | **YES — banked, new project best** |
| H2 (exp 12) | NEW family `fno_coreg_conditioned` (FiLM-via-LayerNorm) | **genuine REVERT** (architecture-falsified on Poisson) | flat 0.030408 / **+9.66% vs banked best** | NO — branch preserved, not merged |

**Net cycle-008 outcome:** reproducible project best 0.030408 → **0.027729** (−8.81%), 89.93% of bar gap closed by capacity-axis alone. Cycle-009 entry baseline = `experiment/11 @ 18d83a6 @ 0.027729` (UNCHANGED by H2).

### Branch preservation

`experiment/12-fno_coreg_conditioned-film @ 540e684` preserved for cycle-009 reference — do NOT delete. 828 LOC of FiLM-via-LayerNorm scaffolding may be useful if a revised hypothesis (FiLM-on-residual-with-LF-features in γ inputs) emerges from cycle-009 Poisson failure analysis. 4 NEW files under `models/fno_coreg_conditioned/` (model.py 218, smoke_eval.py 517, manifest.json 6, INSPIRATION.md 87) — NOT merged to the trunk.

### New cross-cycle patterns appended

- [[patterns]] §"Bookkeeping-overridable REVERT vs genuine architecture-falsified REVERT — the diagnostic is R5b, not precheck"
- [[patterns]] §"FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF correlation — pure m-conditioning is insufficient for Poisson-class datasets"

---

## Cycle 008 Baseline Failure Analysis (PROCEED 2026-06-02 — Researcher R1.5 greenlit)

**Close-out docs:** [[failure-analysis-cycle-008]] (R1), `.factory/reviews/ceo-verdict-failure_analyst.md` (R1 PROCEED).

**Branch under test:** `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`. Eval: cycle-007 H1 banked composite; first cycle where the cycle-005 H2 heat number 0.01551 survives a fresh end-to-end re-eval from a clean tree.

### Baseline headline

| Reference point                              | composite_nRMSE | ifc_heat                       | ifc_poisson                |
|---                                           |---:             |---                             |---                         |
| **R0 cycle-008 baseline (reproducible)**     | **0.030408**    | 0.01551 `fno_coregionalization` | 0.05961 `fno_mf_stack`     |
| Bar (`mf_fno_transfer_bar` parallel-bench)   | 0.027429        | 0.01281                         | 0.05871                    |
| Bar dethrone target (−10%)                   | **≤0.024686**   | —                               | —                          |

- **Gap to bar:** +0.002978 composite (**+10.86% over bar**). About one symmetric −10% step short of dethroning.
- **Per-dataset log-space gap:** ifc_heat +0.191 log-ratio (1.21× over bar); ifc_poisson +0.015 log-ratio (1.015× over bar). **Heat contributes 12.6× more composite-gap log-weight than Poisson.**
- **Silent-regression-cache-layer cliff is RETIRED:** cycle-005 H2's 0.01551 heat number is now reproducible from clean tree (no longer dirty-tree dependent).

### Dominant failure mode — CAPACITY_PARETO on `fno_coregionalization` × `ifc_heat`

Single highest-EV cell to attack. Within-family knobs in `models/fno_coregionalization/smoke_eval.py SMOKE_DEFAULTS`: K=10→20 (paper config), b_hidden=64→128, n_blocks=4→6. Projected heat 0.01551→~0.012, composite→~0.027.

### Dominant absolute-nRMSE failure — `fno_coregionalization` × `ifc_poisson` at 0.7501

12.61× over bar, 20.83× over paper. Persists since cycle-001. K=10 MLP-basis `B(m)=MLP([m,m²])` cannot fit Poisson's non-monotone m-modulation. **Does NOT enter the composite** (Poisson winner is `fno_mf_stack`), but disqualifies fno_coregionalization from being a single-family answer. A different family (intervention 2 below) is the cleaner unified path.

### Failure Distribution (12 actionable cells, v9 reference excluded)

| Category                              | Cells | Composite-gap weight |
|---                                    |---:   |---                   |
| **CAPACITY_PARETO**                   | 1     | **Highest** — fno_coregionalization × heat, 12.6× log-weight |
| FAMILY_PDE_SPECIALIZATION_ASYMMETRY   | 2     | High structural — fno_coreg/Poisson 0.7501; fno_mf_stack/Heat 0.0999 |
| NEAR_PARITY_INCREMENTAL (NEW c008)    | 1     | Medium — fno_mf_stack/Poisson +1.5% over bar |
| TRANSFER_SIGNAL_UNUSED                | 1     | Medium — fno_coreg_residual/Heat (H2 schedule never rebound) |
| RECIPE_DATASET_NONPORTABILITY         | 1     | Already-explored — fno_coreg_residual/Poisson, REVERT 3/3 lever |
| BAR_UNDERTRAINING_VS_CACHE            | 2     | Low — mf_fno_transfer_bar smoke side both datasets |
| BACKBONE_INDUCTIVE_BIAS_MISMATCH      | 4     | Low — transolver_* + v9 orthogonal direction |

**NEW taxonomy promotion:** `NEAR_PARITY_INCREMENTAL` promoted latent → active (`fno_mf_stack`/Poisson at 1.015× over bar; was 1.50× in c002 H4).

### Cross-architecture portability lesson — MFRNP recipes are DO-NOT-RETRY (3 formal REVERTs)

| Cycle    | Hypothesis                                                                  | Result                                                              |
|---       |---                                                                          |---                                                                  |
| c003 H1  | MFRNP HF=2.0/LF=0.25 transplant `fno_mf_stack` → `fno_coreg_residual`       | Poisson +268% regression. REFUTED "PDE-class-bound recipe" framing  |
| c006 H1  | Cross-architecture transplant `fno_coreg_residual` → `fno_mf_stack`         | Cross-architecture transfer failed. REVERT                          |
| c007 H2  | Per-dataset dispatch WITHIN `fno_coreg_residual` (heat keeps, poisson reverts) | Heat invariance falsified at 6.5× noise band (+32.7%). REVERT     |

**Lock-in for c008+ Strategist:** MFRNP HF=2.0/LF=0.25 reweighting is **backbone-coupled AND dataset-entangled within the same family**. Any new hypothesis adding MFRNP-style reweighting must declare (i) heat-invariance kill-switch with band ≥ empirical variance from ≥3 prior fresh-train values, AND (ii) best-of-N (N≥2) seed control with the heat seed frozen. **Prior = REVERT 3/3.**

### Three new transfer-learning ideas surfaced (not yet tested in c008 state)

1. **Re-bind c007 H2 LF→HF two-stage schedule to the repaired `fno_coregionalization` constructor.** Committed code on parent branch but the H1 commit reverted to a one-stage train when fixing the constructor. **Never evaluated.** One-PR addition. Files: `models/fno_coregionalization/smoke_eval.py`.
2. **NEW sibling family `models/fno_coreg_conditioned/`** — single full-resolution HF FNO conditioned on the coregionalization-m basis broadcast as spatial conditioning channel. Decouples m-modulation from the FNO trunk; lets full FNO capacity be reused per-m. **Candidate single-family Heat+Poisson winner.**
3. **Curriculum LF→stack→HF-head on `fno_coreg_residual`** — three-stage training: Stage 1 LF-only fno_mf_stack pretrain (Poisson recipe); Stage 2 freeze LF stack, train HF FNO residual; Stage 3 unfreeze + add coregionalization-residual head. Composes two specialists in stages; needs recipe-fingerprint checkpoint guard.

### Ranked interventions (all within `models/**`)

| # | Intervention                                                          | Category                    | Expected impact            | Scope        |
|---|---|---|---|---|
| 1 | `fno_coregionalization` capacity bump (K=10→20, b_hidden=64→128, n_blocks=4→6) | CAPACITY_PARETO         | heat 0.01551→~0.012, composite →~0.027 | single PR    |
| 2 | NEW family `models/fno_coreg_conditioned/` (m-conditioned single HF FNO) | NEW FAMILY (speculative)    | candidate unified Heat+Poisson winner | new family directory |
| 3 | Re-bind c007 H2 LF→HF schedule on repaired fno_coregionalization      | TRANSFER_SIGNAL_UNUSED      | heat further toward bar 0.01281 | single PR    |
| 4 | Curriculum LF→stack→HF-head on `fno_coreg_residual`                   | F5 staged composition       | speculative; addresses INVERSE_COMPLEMENTARY_FAMILIES | medium PR |
| 5 | `fno_mf_stack` capacity bump on Poisson                               | NEAR_PARITY_INCREMENTAL     | smaller composite lever (12.6× less log-weight) | single PR |

**Defer:** `mf_fno_transfer_bar` smoke-undertraining fix — does not help composite; raises bar to dethrone.

**Do NOT retry:** MFRNP loss-recipe dispatch on `fno_coreg_residual` (prior = REVERT 3/3).

### CEO instructions for downstream (R1.5 Researcher)

From `.factory/reviews/ceo-verdict-failure_analyst.md`:
- Focus web research on: (1) anisotropic-modes FNO and coregionalization-basis capacity tradeoffs at K≥20 on regular-grid PDE benchmarks; (2) m-conditioned single-FNO architectures (FiLM / cross-attention spatial conditioning of fidelity index); (3) curriculum / staged-training schedules for multi-fidelity field prediction (LF-only pretrain → HF residual fine-tune); (4) 2024-2026 multi-fidelity field-prediction work not yet in `papers_summary.csv` targeting the fno_coregionalization / IFC family.
- **Skip:** MFRNP loss-recipe / reweighting research (prior REVERT 3/3; no new evidence will move it).
- Pull from `.factory/archive/` for prior knowledge on c005 H2 / c006 H1 / c007 H1/H2 lineage to avoid re-deriving.

**Detail:** [[failure-analysis-cycle-008]].

---

## Cycle 007 CLOSED (2026-06-02 — verdicts H1 `revert_bookkeeping_keep_intent` + H2 `revert` genuine — net engineering win)

**Close-out doc:** [[cycle-007-summary]] (canonical close-out).

**Headline:** Both hypotheses formally REVERTed but the project's
**reproducible** best moved meaningfully forward:
**composite 0.04420 (prior reproducible best, cycle-002 H3) →
0.030408 (new reproducible best, cycle-007 H1 on
`experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`)**.
The cycle-005 H2 aspirational 0.029357 remains an unreproducible
reference only — the dirty `model.py` it depended on was wiped by
cycle-006 H1's `git reset --hard` and cannot be reattached from the
committed tree. **Cycle-007 H1 closes that reproducibility gap
structurally** by reinstating `fno_coregionalization` end-to-end with
a single-file ≤15-LOC constructor-signature fix that reproduces the
cycle-005 heat 0.01551 winner exactly within rounding (≈+1e-8).

**Two-hypothesis outcome:**

| Hypothesis | Composite Δ | Real outcome | Verdict |
|---         |---:         |---           |---      |
| **H1** — `fno_coregionalization` anisotropic-modes constructor fix | **−23.17%** (0.039578 → 0.030408) | REAL IMPROVEMENT (heat 0.01551, reproduces cycle-005 cache exactly) | **`revert_bookkeeping_keep_intent`** (6-for-6 streak) — formal REVERT due to precheck infra bugs, CEO intent KEEP; branch banked as cycle-008 entry baseline |
| **H2** — `fno_coreg_residual` per-dataset MFRNP recipe dispatch | **+12.36%** (0.039578 → 0.044470) | GENUINE REGRESSION — Heat invariance claim falsified +32.70% (6.5× the 5% band); Poisson improved −17.96% (real but did not take leaderboard) | **`revert` (genuine, substantive)** — 2nd genuine revert in project history (1st: cycle-003 H1 @ +91.7%); branch preserved as reference-only |

**Cycle-008 entry baseline (load-bearing):**
- Composite: **0.030408** (cycle-007 H1 result, the new reproducible
  project best).
- Branch: `experiment/9-fno_coregionalization-constructor-fix`.
- Commit: `1249f2d`.
- Parent: `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`.
- Per-dataset state: `ifc_heat` 0.01551 (`fno_coregionalization`),
  `ifc_poisson` 0.05961 (`fno_mf_stack`).

**Three NEW infrastructure bugs documented in cycle-007:**

1. **Precheck `score_direction` polarity** — now **8-for-8** across
   project history. `composite_nRMSE` lower-is-better, but precheck
   treats as higher-is-better. H1's −23.17% improvement misread as
   +23.17% "regression". Fix lives in `precheck.py` (out-of-cycle).
2. **Precheck `scope` / `fixed_surfaces` empty-detail FPs** — now
   **3-for-3**. Precheck reports violations with empty detail lists
   while standalone `factory guard --check-scope` reports clean.
3. **Leakage-check dataset-name dispatch-key FP** — **NEW sub-class**
   of the existing leakage-check pattern. H2's literal `"ifc_poisson"`
   used as `_DATASET_RECIPES` dispatch key matched research-constraints
   text in `factory.md` and tripped the medium-risk flag. Same
   out-of-cycle scanner-rewrite work as the other sub-classes.

**Two NEW cross-cycle patterns added to [[patterns]]:**

1. **"Fresh-train variance can swamp claimed invariance"** — source-level
   code-path equivalence does NOT imply numerical equivalence when a
   fresh train is involved. Cache-hash flip on a supposedly no-op
   change forces retrain; new trajectory lands at different optimum.
   First observed cycle-007 H2 (empirical variance ≥ 34% vs 5% claimed
   band, 6.5× falsification).
2. **Leakage-check dispatch-key sub-class** — `args.dataset_name`
   tokens used as public dispatch API keys trip the scanner against
   `factory.md` research-constraints text.

**Cycle-008 strategic priorities:**

1. **Build on banked H1 state** — every cycle-008 hypothesis must
   branch from `experiment/9 @ 1249f2d`; monotonic checks anchor at
   0.030408.
2. **Fix `mf_fno_transfer_bar` undertraining** — parallel-bench BAR
   composite 0.02743 still wins by 0.003; BAR underconverged at smoke
   budget (~10 s wall). Smoke-budget allocation on BAR's training
   schedule is the highest-EV move.
3. **Re-attempt Poisson improvement on `fno_coreg_residual`** with
   proper invariance verification — e.g., warm-init from cached state
   to control fresh-train variance, OR in-architecture conditional
   keeping `smoke_eval.py` byte-identical for Heat, OR runtime feature
   flag preserving Heat cache hash.
4. **Add Strategist hard-gate #11** — for any cell claimed "invariant
   by construction" that would be a fresh train, require either a
   kill-switch with band anchored to empirical variance OR explicit
   byte-identical cache-key proof.
5. **Defer:** `mf_fno_bar_residual` new family until after BAR fix.

**Patterns updated in cycle-007:** see [[cycle-007-summary]] for the
full update table.

---

## Cycle 007 H2 CLOSED (2026-06-02 — verdict `revert` — substantive, GENUINE regression — Heat invariance claim falsified)

**Close-out doc:** [[cycle-007-exp-10]] (full R0→R5 lifecycle); build-phase note [[cycle-007-exp-10-build]]. **Hypothesis:** Decouple `fno_coreg_residual` MFRNP HF/LF loss-weight recipe per dataset at `models/fno_coreg_residual/smoke_eval.py` — Poisson-class cells get Wang 2024 MFRNP `Poisson5_config.yaml` prescription (HF=2.0, LF=0.25); Heat-class cells continue with uniform 1.0/1.0 by SMOKE_DEFAULTS. Strategist R2 claimed "Heat path is invariant by construction" because the dispatch dict has no `ifc_heat` entry — claim was empirically falsified by R4.

**Branch + commit:**
- Branch: `experiment/10-fno_coreg_residual-dataset-recipes` (PRESERVED for reference only — cycle-008 baseline UNCHANGED).
- Parent: `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` (NOT chained from H1's `experiment/9-…`; H2 measured independently against honest baseline 0.039578 per Strategist R2 directive).
- Commit: `87f65b1` — `feat(fno_coreg_residual): per-dataset MFRNP recipe dispatch (cycle-007 H2)`. 1 file, +29/-0 LOC (purely additive at source level). Builder used 0 of 2 redirects (caveat: structural easy case — target file was at HEAD pre-edit).

**R4 eval result (Evaluator: FAIL — REVERT):**

| Metric | R0 honest baseline | R4 H2 after | Δ | Δ % | Direction |
|---|---:|---:|---:|---:|---|
| **composite_nRMSE** | **0.039578** | **0.044470** | **+0.004892** | **+12.36%** | ❌ regression |
| ifc_heat best-family nRMSE | 0.02628 (`fno_coreg_residual`) | **0.03317** (`mf_fno_transfer_bar`) | +0.00689 | +26.24% | ❌ regression (leaderboard flipped) |
| ifc_poisson best-family nRMSE | 0.05961 (`fno_mf_stack`) | 0.05961 (`fno_mf_stack`) | 0.0 | 0.0% | ◇ unchanged (winner unmoved) |
| `fno_coreg_residual` / ifc_heat | 0.02628 | **0.03487** | +0.00859 | **+32.70%** | ❌ invariance violated (6.5× the 5% band) |
| `fno_coreg_residual` / ifc_poisson | 0.07419 | **0.06087** | −0.01333 | **−17.96%** | ✅ real improvement (but +9.55% over cycle-005 target 0.05556) |
| Poisson kill-switch (≤ 0.089) | — | 0.06087 | −0.028 headroom | −31.6% under threshold | ✅ NOT tripped |
| Composite bar 0.0274 (parallel-bench) | — | 0.04447 | +0.01707 | +62.3% over | ❌ NOT crossed |

- Eval duration: 186 s wall on `bash scripts/cycle_eval.sh`. Fresh retrains on both `fno_coreg_residual × {ifc_heat, ifc_poisson}` cells (new code hash `528438a274db`). All other cells cache-hit.
- Dispatch mechanism verified working at runtime: `[run] resolve_fidelity_weights: dataset=ifc_heat hf=1.0 lf=1.0` and `dataset=ifc_poisson hf=2.0 lf=0.25` log lines emitted as designed.
- See [[evaluator-latest]], `.factory/research/runs/cycle-007-h2/summary.json`.

**Why H2 is a GENUINE revert (not bookkeeping-revert / keep-intent):**

The cycle-007 H1 `revert_bookkeeping_keep_intent` pattern requires (a) real research metric improves, (b) all real safety checks pass, (c) precheck infra bugs trip. For H2:
- (a) ❌ Composite GENUINELY regressed +12.36%.
- (b) ✅ Real safety checks would pass.
- (c) ⚠️ Precheck bugs trip but are NOT load-bearing — the verdict is REVERT regardless.

This is the **2nd genuine REVERT in project history** (1st was cycle-003 H1 @ +91.7% composite regression). H2's regression magnitude is smaller but the structural class is identical.

**The falsified Strategist claim (the load-bearing failure):**

> **R2 claim:** "Heat path is invariant by construction. Defaults `(1.0, 1.0)`; gate excludes `'heat'` in dataset_name. The Heat code path will execute the same `p["hf_loss_weight"]` and `p["lf_loss_weights"]` as the baseline."
> **R4 reality:** Heat regressed +32.70% (0.02628 → 0.03487). Falsification ratio 6.5× the 5% invariance band.

**Two candidate (non-exclusive) mechanisms** for the falsification:
1. **Code-path side effect.** The new code path unconditionally writes `p["hf_loss_weight"]` and `p["lf_loss_weights"]` even when the dispatch dict returns empty. If the prior code didn't write those keys at that position, or wrote `lf_loss_weights` as a different tensor shape, the runtime wiring CHANGED for Heat — Strategist's "invariant" reasoned over the dispatch dict only, not the unconditional downstream writes.
2. **Fresh-train variance + cache-hash flip.** Code hash flipped `1d967ad6e54c` → `528438a274db`, invalidating cache. Prior fresh-train values on this cell span 0.02628 (cycle-007 R0) → 0.03059 (cycle-006 H1) → 0.03487 (this run) → 0.03519 (cycle-005 R0) — empirical variance ≥ 34%, which exceeds the claimed 5% invariance band by 6.8×. The "invariance" was anchored on a single low value (0.02628) without measuring the variance band.

Both mechanisms likely contribute. See [[cycle-007-exp-10]] §"Key findings — cross-cycle lessons" for the full analysis.

**Per-dataset reality post-H2 (REVERTED — these numbers go away on cycle-008 entry baseline):**
- `ifc_heat` leaderboard winner FLIPPED: `fno_coreg_residual` 0.02628 → `mf_fno_transfer_bar` 0.03317. After revert, cycle-008 entry winner returns to cycle-007 H1's `fno_coregionalization` @ 0.01551 (Heat leaderboard).
- `ifc_poisson` winner UNCHANGED: `fno_mf_stack` 0.05961.
- `fno_coreg_residual / ifc_poisson` 0.06087 is real (−17.96% vs baseline 0.07419) but did NOT take the poisson leaderboard (0.05961 < 0.06087 by 2.1%).

**Cycle-008 entry baseline UNCHANGED:**
- Composite: **0.030408** (from cycle-007 H1).
- Branch: `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d` (cycle-007 H1's preserved branch).
- H2's preserved branch `experiment/10-… @ 87f65b1` is reference-only.

**NEW cross-cycle pattern added to [[patterns]]:**

> **"Fresh-train variance can swamp claimed invariance."** A "no-op" code change that touches loss-aggregation logic, training-loop wiring, or optimizer construction is NEVER truly invariant when fresh trains are involved. Cache hash flip on the supposedly-invariant cell forces retrain; the new trajectory may land at a different optimum than prior runs. Code-path equivalence at the source level does NOT imply numerical equivalence after a fresh train.

**Proposed CEO hard-gate check for cycle-008+:**

> For any hypothesis claiming "invariant by construction" on a cell that would be a fresh train (cache miss expected), require either (a) a kill-switch on the supposedly-invariant cell with a band ≥ 20% anchored to empirical variance, OR (b) explicit evidence the cache hash is preserved (proof of byte-identical input to the cache-key function).

**Cross-cycle reinforcement of existing pattern:** "Cross-architecture recipe portability is NOT guaranteed" (cycle-006 H1, now 2-for-2). MFRNP (2.0, 0.25) recipe on `fno_coreg_residual / ifc_poisson` gave −17.96% (real gain) but fell +9.55% short of the cycle-005 target 0.05556 and did NOT beat `fno_mf_stack`'s native 0.05961. Residual decoder absorbs some of the loss-asymmetry signal.

**What this leaves for cycle-008:**
- Cycle-008 entry baseline remains composite 0.030408 (cycle-007 H1's `experiment/9`).
- Poisson leaderboard remains the geomean bottleneck. The H2 Poisson recipe is partially portable to `fno_coreg_residual` — future cycles can re-attempt with either (i) runtime feature flag preserving heat cache hash, or (ii) in-architecture conditional moving dispatch into `fno_coreg_residual/model.py` so smoke_eval.py stays byte-identical for Heat.
- `mf_fno_bar_residual` new family scaffold (Top-3 deferred from cycle-007 R2) is still the highest-EV cycle-008 architectural move.
- Strategist hard-gate proposal above should be added to cycle-008's R2 contract.

---

## Cycle 007 H1 CLOSED (2026-06-02 — verdict `revert_bookkeeping_keep_intent` — composite improvement banked; precheck infra bugs flip formal verdict)

**Close-out doc:** [[cycle-007-exp-9]] (full R0→R5 lifecycle). **Hypothesis:** Repair `FNOCoregionalization` anisotropic-modes constructor at `models/fno_coregionalization/model.py` so the wrapper accepts the `(modes_h, modes_w, grid: tuple)` signature the smoke harness call site already passes. Single-file ≤15-LOC mechanical fix mirroring sibling pattern at `models/mf_fno_transfer_bar/model.py:62-94`.

**Branch + commit:**
- Branch: `experiment/9-fno_coregionalization-constructor-fix` (preserved, not merged — same protocol as cycle-005 H2 due to the same precheck infra bugs).
- Parent: `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` (cycle-005 H2's frozen project-best branch).
- Commit: `1249f2d` — `fix(fno_coregionalization): repair anisotropic-modes constructor (cycle-007 H1)`. 1 file, +9/-7 LOC. Builder used 0 of 2 redirects.

**R4 eval result (Evaluator: PASS — KEEP):**

| Metric | Before (cycle-007 R0 honest baseline) | After (H1) | Δ | Direction |
|---|---:|---:|---:|---|
| composite_nRMSE | 0.039578 | **0.030408** | **−0.009170 (−23.17%)** | ✅ improvement |
| `fno_coregionalization` / ifc_heat | crashed (TypeError) | **0.01551** (reproduces cycle-005 cache within ≈+1e-8) | recovered | ✅ |
| `fno_coregionalization` / ifc_poisson | crashed (TypeError) | 0.7501 | recovered (not a leaderboard cell) | ◇ |
| Per-dataset ifc_heat winner | `fno_coreg_residual` @ 0.02628 | **`fno_coregionalization` @ 0.01551** | −40.98% | ✅ |
| Per-dataset ifc_poisson winner | `fno_mf_stack` @ 0.05961 | `fno_mf_stack` @ 0.05961 (cache hit) | 0% | ◇ |
| Heat kill-switch (≤ 0.0194) | — | 0.01551 — **NOT tripped**, 20% under threshold | — | ✅ |
| Aspirational bar 0.029357 | — | 0.030408 (+0.001 short, +3.58%) | — | ◇ |
| Composite bar 0.0274 (parallel-bench) | — | 0.030408 (+0.003 short, +10.98%) | — | ◇ |

**Verdict — `revert_bookkeeping_keep_intent` (6-for-6 streak; same protocol as cycle-005 H2 and 5 prior keep-intent evals):**

- **CEO intent = KEEP.** Composite improved −23.17%; `fno_coregionalization` ifc_heat reproduces cycle-005 cache exactly; Reviewer PASS substantive; Evaluator R4 "PASS — KEEP" ("the cleanest H1 validation we have had in 6 cycles"); all 3 real precheck checks (`ground_truth_leakage`, `anti_pattern`, `smoke_test`) PASSED.
- **Formal verdict = REVERT** due to 3 precheck infrastructure bugs the CEO has classified as known false positives:
  1. **`score_direction` polarity bug (8-of-8 across project history).** `composite_nRMSE` is lower-is-better; precheck treats as higher-is-better → −23% improvement read as +23% "regression". `precheck.py` does not honor `primary_metric_lower_is_better` from `eval/smoke_config.json`. See [[patterns]] §"Factory precheck `score_direction` is polarity-buggy".
  2. **`scope` failure with empty-detail violation list (3-of-3).** Standalone `factory guard --check-scope` independently reports `clean` on the same diff at the same commit.
  3. **`fixed_surfaces` failure with empty-detail violation list (3-of-3).** Same parsing bug as `scope`.
- **Branch preserved.** `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d` is the **cycle-008 entry baseline** (monotonic-improvement anchor = 0.030408; NOT 0.039578 or 0.029357).

**Why this is `revert_bookkeeping_keep_intent` and not genuine REVERT:** the cycle-003 H1 and cycle-006 H1 genuine REVERTs corresponded to genuine composite regressions (+91.7% and +1.8% essentially flat with poisson +3.6%). H1 here is the opposite — composite genuinely improved −23.17%. The precheck "agreement" on `score_direction` is coincidental (polarity bug trips in both directions on the same `>0.0` threshold), not corroborating evidence. CEO monotonic-improvement policy demands KEEP intent; the bookkeeping records REVERT until upstream `precheck.py` (in `/orcd/data/faez/001/nick/mf_field/akash/remote-factory-main`, out of cycle-007 mutable surface) is fixed.

**Cross-cycle pattern extended:** [[patterns]] §"Factory precheck `score_direction` is polarity-buggy on lower-is-better metrics" now at **8-of-8 confirmed instances** in project history (was 7). [[patterns]] §"Factory precheck reports empty-detail `scope` / `fixed_surfaces` failures that contradict the standalone guard" now at **3-of-3 confirmed instances** (was 2). Combined effect: any KEEP-intent evaluation on a lower-is-better metric is guaranteed a false-positive REVERT until upstream `precheck.py` is patched.

**What cycle-008 inherits:**
- New reproducible baseline composite = 0.030408 (NOT 0.029357, NOT 0.039578).
- Heat solved at cycle-005 frontier (0.01551, 4.77× over paper); further heat gains require architectural advance below 0.01551, not a recipe fix.
- Poisson is now the geomean bottleneck (`fno_mf_stack` @ 0.05961, 1.65× over paper). H2 (per-dataset recipe decoupling on `fno_coreg_residual`, deferred from cycle-007 R2 budget) is the natural follow-on — could push poisson toward 0.05556 and composite toward ~0.0294 (below bar 0.0274 by small margin).
- `mf_fno_bar_residual` new family deferred to cycle-008 (highest-EV architectural move).
- Precheck infra fix remains an out-of-cycle dependency; every keep-intent eval will continue to record `revert_bookkeeping_keep_intent` until it lands.

**Detail:** [[cycle-007-exp-9]] (full lifecycle), [[cycle-007-exp-9-build]] (R3 build phase), [[ceo-verdict-builder]], [[ceo-verdict-reviewer]], [[ceo-verdict-strategist]], [[ceo-verdict-evaluator]], [[evaluator-latest]].

---

## Cycle 007 R3 H1 Build (PROCEED 2026-06-02 — Evaluator R4 greenlit)

**Close-out docs (R3 H1 build):** [[cycle-007-exp-9-build]] (build-phase experiment note), [[ceo-verdict-builder]] (CEO PROCEED on Builder), [[ceo-verdict-reviewer]] (CEO PROCEED ratifying Reviewer PASS).

### What landed

| Item | Value |
|---|---|
| Hypothesis | H1 — `FNOCoregionalization` constructor fix (COMMITTED_TREE_BROKEN failure mode) |
| Branch | `experiment/9-fno_coregionalization-constructor-fix` |
| Parent | `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` |
| Commit | `1249f2de87bfd15001c67a22ee4ea66343fecd2d` |
| Files changed | **1** (`models/fno_coregionalization/model.py`) |
| LOC delta | **+9 / −7** |
| Constructor signature after | `(modes_h: int, modes_w: int, grid: tuple)` — no fallback `modes=` kwarg |
| Inner `SpectralConv2d` / `FNOBlock` | byte-identical to be36cba |
| `smoke_eval.py` + `manifest.json` | byte-preserved (cycle-005 H2 LF→HF schedule + `SMOKE_DEFAULTS` intact) |
| Param count | 1,190,708 (heat) / 1,190,772 (poisson) |
| Builder redirects used | **0 of 2** |
| `factory guard --check-scope` | `clean` |

### 2-epoch smoke verification — PASSED both datasets

| Dataset | best_val_nRMSE | Status |
|---|---:|---|
| `ifc_heat` | 0.22934 | PASS |
| `ifc_poisson` | 0.27102 | PASS |

2-epoch values are expected for undertrained runs; the R4 kill-switch (`heat ≤ 0.0194`, +25% headroom over cycle-005's 0.01551) is evaluated at the full 200-epoch schedule, not at 2 epochs. The runs completed cleanly with no shape mismatches, confirming `(modes_h, modes_w, grid)` propagates correctly at all call sites.

### CEO Builder verdict — PROCEED

Builder applied only the declared file (`models/fno_coregionalization/model.py`); the 15 pre-existing dirty files (`bench/`, `data_adapters/`, `fairbench/`, `models/_grid_smoketest.py`, `references/external_sota/`, `results/...`, `scripts/smoke_one.sbatch`) were left untouched. `--no-github` honored. Smoke pre-flight passed both datasets before commit.

### CEO Reviewer verdict — PROCEED (ratify Reviewer PASS)

Reviewer's substantive scope verification cited the guard output, byte-preservation of `SMOKE_DEFAULTS` and the H2 LF→HF schedule, the [[dirty-tree-staging]] memory compliance, and the R4 kill-switch deferral. CEO independently spot-checked the diff (`git diff be36cba HEAD models/fno_coregionalization/model.py`) and confirmed all claims.

### Cross-cycle hygiene win (Builder role)

**Same Builder role that triggered the cycle-006 H1 dirty-tree-staging contamination produced a clean named-file commit here on the first attempt — zero redirects burned.**

| Cycle | Dirty files at start | Dirty files committed | Redirects | Outcome |
|---|---:|---:|---|---|
| **cycle-006 H1** ([[cycle-006-exp-8]]) | ~15 | **357 contaminating LOC** | **1 of 2** | Recovery commit `59b741f` (+30/-3) after `git reset --hard` |
| **cycle-007 H1** ([[cycle-007-exp-9-build]]) | **15** | **0** | **0 of 2** | First-attempt commit `1249f2d` (+9/-7) |

**Caveat — rule held by structural easy case, not by improved process discipline.** The mechanical difference: cycle-006 H1's named target files (`smoke_eval.py`, `manifest.json`) were already in the working-tree diff before Builder edits, so `git add <file>` swept in pre-existing dirty state. Cycle-007 H1's target file (`models/fno_coregionalization/model.py`) was at HEAD before Builder edits, so `git add <file>` captured only the hypothesis diff. The [[dirty-tree-staging]] auto-memory rule did its job (Builder noted the 15 dirty files and used `git add <specific file>`), but the test was easier because the target wasn't pre-dirty. The process gates from [[patterns]] §"Builder clean-isolation requires pre-clean working tree" (pre-clean at session start / `git checkout HEAD -- <file>` / staged-diff audit) remain mandatory for general safety.

### Pending (R4)

- 200-epoch run via `bash scripts/cycle_eval.sh` on `experiment/9-fno_coregionalization-constructor-fix`. Cache MISS expected on `models/fno_coregionalization/` cell only (new `__code_hash__`); other 13 cells should cache-hit.
- **R4 kill-switch**: if fresh smoke run does not reproduce heat ≤ 0.0194 (+25% over cycle-005 H2 cached 0.01551) at the cycle-005 H2 schedule (`pretrain_frac=0.25, pretrain_lr=1e-3, finetune_lr=3e-4`), revert immediately.
- **Expected impact at R4**: composite `0.039578 → ≈ 0.0304` (delta ≈ −0.0092); `ifc_heat` via fno_coregionalization `error/NaN → ≈ 0.01551`; stackable with H2 (separate branch from `experiment/7@be36cba`, not yet built) to a projected `≈ 0.0294`.
- **R5 verdict logic**: monotonic check uses **0.039578** as honest baseline (Strategist R2 contract; NOT the unreproducible aspirational 0.029357).

**Detail:** [[cycle-007-exp-9-build]] (full build narrative); `.factory/reviews/builder-latest.md`; `.factory/reviews/reviewer-latest.md`.

---

## Cycle 007 R3 H2 Build (PROCEED 2026-06-02 — Evaluator R4 greenlit)

**Close-out docs (R3 H2 build):** [[cycle-007-exp-10-build]] (build-phase experiment note), [[ceo-verdict-builder]] (CEO PROCEED on Builder with documented leakage-check override), [[ceo-verdict-reviewer]] (CEO PROCEED ratifying Reviewer PASS).

### What landed

| Item | Value |
|---|---|
| Hypothesis | H2 — `fno_coreg_residual` per-dataset MFRNP recipe dispatch (LOSS_RECIPE_GAP / ARCHITECTURE_OVERFIT failure mode) |
| Branch | `experiment/10-fno_coreg_residual-dataset-recipes` |
| Parent | `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` (**NOT** the cycle-007 H1 branch — measured independently per Strategist R2 no-bundling directive) |
| Commit | `87f65b15e882ae285a782d114c96fd0e96ccea10` |
| Files changed | **1** (`models/fno_coreg_residual/smoke_eval.py`) |
| LOC delta | **+29 / −0** (purely additive — zero deletions, zero modifications to existing lines) |
| `model.py` / `manifest.json` / `INSPIRATION.md` / `full_config.json` | byte-identical to be36cba |
| `SMOKE_DEFAULTS` original keys (K=10, b_hidden=64, hidden=64, lr=3e-4) | byte-preserved (only 2 new defaulted-to-1.0 keys appended) |
| Sibling reference implementation | `models/fno_mf_stack/smoke_eval.py` (same `_DATASET_RECIPES` + `resolve_fidelity_weights` pattern, predates this H2) |
| Builder redirects used | **0 of 2** |
| `factory guard --check-scope` | `clean` |

### Mechanism (4 discrete additive blocks)

1. **Module-scope dispatch dict**: `_DATASET_RECIPES = {"ifc_poisson": dict(poisson_hf_weight=2.0, poisson_lf_weight=0.25)}` — only `ifc_poisson` has an entry; Heat path has zero entries (Strategist anti-pattern #5 satisfied).
2. **Two new `SMOKE_DEFAULTS` keys**: `poisson_hf_weight=1.0`, `poisson_lf_weight=1.0` — defaulted to uniform-identity so any dataset not in `_DATASET_RECIPES` falls through unchanged.
3. **`resolve_fidelity_weights(dataset_name, p)` helper** at module scope, gates on `"poisson" in dataset_name.lower()`. Mirrors `models/fno_mf_stack/smoke_eval.py`.
4. **Dispatch site in `run(args)`**: `p.update(_DATASET_RECIPES.get(args.dataset_name, {}))` immediately after `p = dict(SMOKE_DEFAULTS)`, then after `n_levels = len(train_loaders)`: `p["hf_loss_weight"] = hf_w; p["lf_loss_weights"] = tuple([lf_w] * max(n_levels - 1, 0))` and a runtime dispatch log line.

### Heat path invariance — provable by construction

The Heat path is byte-equivalent in **effect** to baseline. Dual gate: (a) `_DATASET_RECIPES` has no Heat entry so `.get("ifc_heat", {}) = {}` → `p.update` is a no-op; (b) `resolve_fidelity_weights` gates on `"poisson" in dataset_name.lower()` → returns hard-coded `(1.0, 1.0)` for Heat regardless of `p` contents. Either layer alone would suffice; together they make Heat regression structurally impossible without a code change. The R4 cache will MISS on the Heat cell because `__code_hash__` content-addresses the source bytes, but the fresh-train result should land within stochasticity of baseline 0.030590.

### 2-epoch smoke verification — PASSED both datasets with correct dispatch logs

| Dataset | best_val_nRMSE (2-ep) | dispatch log | Status |
|---|---:|---|---|
| `ifc_heat` | 0.4198 | `[run] resolve_fidelity_weights: dataset=ifc_heat hf=1.0 lf=1.0` ✓ | PASS |
| `ifc_poisson` | 0.2447 | `[run] resolve_fidelity_weights: dataset=ifc_poisson hf=2.0 lf=0.25` ✓ | PASS |

2-epoch values are diagnostic only — the R4 kill-switch (`poisson > 0.089`) is evaluated at the full 200-epoch schedule, not at 2 epochs. What the 2-epoch smoke proves: dispatch wiring runs without `KeyError` / `TypeError` / shape mismatch; dispatch log lines print the **expected** per-dataset weights; loss is numerically stable.

### CEO Builder verdict — PROCEED (with leakage-check override)

Builder applied only the declared file (`models/fno_coreg_residual/smoke_eval.py`); the 15 pre-existing dirty files were left untouched. `--no-github` honored. Smoke pre-flight passed both datasets before commit.

**Leakage-check override (CEO judgment):** `factory leakage-check` on the diff returned `risk_level: medium` with a single finding — the token `ifc_poisson` in the diff matches `ifc_poisson` in `factory.md` line 42 (`research_constraints[5]` lists smoke datasets). CEO override applied because `ifc_poisson` is the **public DATASET NAME used as the dispatch key via `args.dataset_name`** — it is the API contract that the Strategist's H2 spec explicitly mandates, not a ground-truth value. The hypothesis-level leakage check returned `risk_level: none` before any code was written. This is the same false-positive class as the cycle-001 shared-vocabulary findings (`description`, `frozen`, `ifc_raw`) and cycle-001 H2 numerical-substring findings (`0.10`, `0.20`), now extended to a new **sub-class: dataset-name tokens used as public dispatch keys**.

**Distinction from cycle-007 H1 precheck infra bugs:** the H1 case involved three independent **`precheck.py`** failures (`score_direction` polarity, empty-detail `scope`, empty-detail `fixed_surfaces`); the H2 case here is a different infrastructure subsystem (**`factory leakage-check`**) and a different failure class (substring-collision on a public dispatch key, not polarity inversion or empty-detail). Two separate infra bugs in the same family ("factory scanners produce false positives when their corpus includes `factory.md`"), but the root causes and fix sites are distinct. See [[patterns]] §"Factory precheck `score_direction` is polarity-buggy" (H1 case) vs. §"Factory leakage-check fingerprints `factory.md` itself" (this H2 case, now extended).

### CEO Reviewer verdict — PROCEED (ratify Reviewer PASS)

Reviewer's substantive scope verification cited the guard output, file-by-file spec compliance (`_DATASET_RECIPES` shape, helper signature + gate, dispatch site placement, byte-preserved `SMOKE_DEFAULTS` original keys), Heat path bit-equivalence by construction, and the smoke dispatch logs from both datasets. CEO independently spot-checked the diff (`git diff be36cba 87f65b1 -- models/fno_coreg_residual/smoke_eval.py`) and confirmed all claims — 1 file, +29/-0, all changes additive within `models/fno_coreg_residual/smoke_eval.py`.

### Cross-cycle hygiene update — 2-for-2 clean Builder commits in cycle-007

**Same Builder role that triggered cycle-006 H1 dirty-tree-staging contamination produced its second clean named-file commit in cycle-007 on the first attempt — zero redirects burned again.**

| Cycle | Builder phase | Dirty files at start | Dirty files committed | Redirects | Outcome |
|---|---|---:|---:|---|---|
| **cycle-006 H1** ([[cycle-006-exp-8]]) | `git add` on already-dirty `smoke_eval.py` + `manifest.json` | ~15 | **357 contaminating LOC** | **1 of 2** | Recovery commit `59b741f` (+30/-3) after `git reset --hard` |
| **cycle-007 H1** ([[cycle-007-exp-9-build]]) | `git add models/fno_coregionalization/model.py` (at HEAD) | **15** | **0** | **0 of 2** | First-attempt commit `1249f2d` (+9/-7) |
| **cycle-007 H2** ([[cycle-007-exp-10-build]], this entry) | `git add models/fno_coreg_residual/smoke_eval.py` (at HEAD) | **15** | **0** | **0 of 2** | First-attempt commit `87f65b1` (+29/-0) |

**Caveat (same as H1) — rule held by structural easy case, not by improved process discipline.** Target file `models/fno_coreg_residual/smoke_eval.py` was at HEAD before Builder edits (not in the pre-existing 15-file dirty set), so `git add <file>` captured only the H2 hypothesis diff. The [[dirty-tree-staging]] auto-memory rule held by accident again — both cycle-007 hypotheses happen to target files outside the 15 pre-existing dirty file paths. **The Strategist's hypothesis-design discipline (picking small surgical files for the H1/H2 specs) is incidentally protecting the Builder by avoiding the dirty-file landmines.** A counterfactual where the next hypothesis targets one of the 15 pre-existing dirty files would re-test the actual process compliance per [[patterns]] §"Builder clean-isolation requires pre-clean working tree".

### Pending (R4)

- 200-epoch run via `bash scripts/cycle_eval.sh` on `experiment/10-fno_coreg_residual-dataset-recipes`. Cache MISS expected on **both** `fno_coreg_residual` cells (heat + poisson) — `__code_hash__` for `models/fno_coreg_residual/smoke_eval.py` changes with the +29 LOC diff even though Heat-path behavior is identical. Other 12 cells (7 other families × 2 datasets) should cache-hit.
- **R4 kill-switch**: if fresh smoke run produces `fno_coreg_residual / ifc_poisson > 0.089` (+20% over honest baseline 0.057564), revert immediately.
- **R4 Heat regression check**: if `fno_coreg_residual / ifc_heat` deviates > 5% from baseline 0.030590, flag for fresh-train stochasticity vs. unexpected semantic divergence — Heat path is bit-equivalent **by construction**, so > 5% would be a strong red flag.
- **Expected impact at R4 (standalone)**: composite `0.039578 → ≈ 0.0382` (delta ≈ −0.0016); `fno_coreg_residual / ifc_poisson` `0.057564 → ≈ 0.05556`; `fno_coreg_residual / ifc_heat` invariant. Per-dataset poisson winner may flip from `fno_mf_stack @ 0.05961` → `fno_coreg_residual @ 0.05556`.
- **Stacking with H1 (NOT bundled)**: H1 and H2 touch disjoint files in disjoint families; whether to merge both branches is a cycle-008 entry decision, not in-cycle bundling. Strategist's stacked projection ≈ 0.0294 (aspirational, reachable only if both R4 numbers compose linearly).
- **R5 verdict logic**: monotonic check uses **0.039578** as honest baseline (Strategist R2 contract). The standalone H2 composite improvement (≈ −0.0016) is small and will likely trip the `score_direction` polarity bug (8-of-8 streak); CEO should pre-register the override.

**Detail:** [[cycle-007-exp-10-build]] (full build narrative, including the leakage-check sub-pattern extension and the Heat path invariance proof); `.factory/reviews/builder-latest.md`; `.factory/reviews/reviewer-latest.md`; `.factory/reviews/ceo-verdict-builder.md`; `.factory/reviews/ceo-verdict-reviewer.md`.

---

## Cycle 007 R2 Strategist (PROCEED + PLAN APPROVED 2026-06-02 — Builder R3 greenlit)

**Close-out docs (R2):** [[cycle-007]] (strategy snapshot), [[ceo-verdict-strategist]] (PROCEED + PLAN APPROVED + Builder instructions). Strategy doc: `.factory/strategy/current.md`.

### Approved plan: Option B — 2 hypotheses, different families, NO bundling

CEO hard gate: **10 of 10 checks passed.** Both hypotheses target `models/**` only; both leakage-checks return `risk_level=none, findings=[]`; both have realistic kill-switches.

| Hypothesis | Sole target file | Category | Failure mode | Expected Δ composite | Kill-switch |
|---|---|---|---|---:|---|
| **H1** (highest priority) | `models/fno_coregionalization/model.py` | FIX | COMMITTED_TREE_BROKEN | **−0.0092** (→ ~0.0304) | heat > 0.0194 ⇒ revert |
| **H2** (stackable) | `models/fno_coreg_residual/smoke_eval.py` | FIX | LOSS_RECIPE_GAP / ARCHITECTURE_OVERFIT | **−0.0016** standalone; stacked → ~0.0294 | poisson > 0.089 ⇒ revert |

**Stacked projection:** geomean(0.01551, 0.05556) ≈ **0.0294** — below the bar `0.0274` by a small margin if both land cleanly.

### Honest-baseline framing locked in (R5 contract)

R5 monotonic-improvement check **must** use **0.039578** as previous best, **not** 0.029357. The cycle-005 H2 aspirational best (0.029357) is preserved as a reference but is not reproducible from the current committed tree (cache hashes `9528aeef4a5a` / `9be21a0f9ce9` no longer key-resolve against `4235deb6c27c`).

### Builder sequencing directive (CEO)

1. **H1 first, then H2.** Each hypothesis on its own experiment branch.
2. **H2 cuts a SEPARATE branch from `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`, NOT from H1's branch.** Each hypothesis gets an uncontaminated measurement against the honest baseline. H1's regression test against the cycle-005 cached 0.01551 number is preserved regardless of H2's outcome.
3. **Single-file constraint per hypothesis** — Builder may ONLY modify the declared file. Any other modification = automatic ABORT.
4. **Smoke prerequisite** — `models/<family>/smoke_eval.py --epochs 2 --dataset_dir data/{ifc_heat,ifc_poisson}` must complete (both datasets) before declaring done.
5. **Branch names:** H1 → `experiment/<exp_id>-fno_coregionalization-constructor-fix`; H2 → `experiment/<exp_id>-fno_coreg_residual-dataset-recipes`.
6. **--no-github mode** — local commits on experiment branches suffice.
7. **Clean staging** — 15 pre-existing dirty files (bench/, data_adapters/, fairbench/, etc.); use `git add <specific file>` not `git add -A` (see [[dirty-tree-staging]]).

### Kill-switches (R4)

- **H1:** if fresh smoke run does not reproduce heat ≤ 0.01551 within +25% (i.e. `heat ≤ 0.0194`) at the cycle-005 H2 schedule (`pretrain_frac=0.25, pretrain_lr=1e-3, finetune_lr=3e-4`), revert immediately. Verify `smoke_eval.py:64-82` is byte-for-byte unchanged before the smoke run.
- **H2:** if Poisson on `fno_coreg_residual` regresses >+20% from current 0.07419 (i.e. `poisson > 0.089`), revert immediately. Historical precedent: cycle-002-H3 ancestor drove Poisson 0.074 → 0.273 from MFRNP weights applied without backbone-coupling care.

### Anti-patterns enumerated (8)

- No H1/H2 bundling (confounds regression test).
- No fallback `modes=` kwarg in H1 (silently masks future regressions).
- No `SMOKE_DEFAULTS` drift in H1 (recipe knobs load-bearing for 0.01551).
- No `mf_fno_bar_residual` new family this cycle (deferred to cycle-008).
- No Heat-side `_DATASET_RECIPES` entry on `fno_coreg_residual` in H2 (Heat path stays invariant).
- No transolver changes (eval-protocol gap but does not gate composite).
- No fixed-surface edits (`data/**`, `baselines/**`, `eval/**`, `references/**`, `scripts/**`, `factory.md`, `README.md`).
- No re-deriving expected-effect numbers from ground-truth.

### Deferred to cycle-008

`mf_fno_bar_residual` new family scaffold; LF→HF transfer add-on for `fno_coreg_residual`; restore real training on `mf_fno_transfer_bar`; transolver val/test normalisation audit. Wall-time budget reserved for clean H1+H2 measurement (~6–10 min fresh wall vs 240 min budget; 10 of 14 cells cache-hit).

**Detail:** [[cycle-007]] (strategy snapshot); `.factory/strategy/current.md` (live strategy doc); [[ceo-verdict-strategist]] (CEO close-out).

---

## Cycle 007 R1.5 Researcher (PROCEED 2026-06-02 — Strategist R2 greenlit)

**Close-out docs (R1.5):** `.factory/strategy/research.md` (full report; cycle-007 section appended this round), [[ceo-verdict-researcher]] (PROCEED + strategic prioritization). Web access this cycle: **functional** — fresh WebSearch on F-FNO / anisotropic modes / MF-FNO transfer-schedule literature succeeded.

### Headline

The cycle-007 dominant failure is a **wrapper-level mismatch, not an architectural redesign**. The Researcher re-verified, against the current `experiment/7@be36cba` tree:

- `models/fno_coregionalization/model.py:28-79` — **`SpectralConv2d` and `FNOBlock` ALREADY accept `(modes_h, modes_w)`**. Inner classes are correct.
- `models/fno_coregionalization/smoke_eval.py:265-273` — call site already passes `(modes_h, modes_w, grid)`. Correct.
- `models/fno_coregionalization/smoke_eval.py:64-411` — full cycle-005 H2 two-stage schedule (LF warm-up + joint fine-tune, fresh `Adam` + `CosineAnnealingLR` per stage) is **intact**.
- `models/fno_coregionalization/smoke_eval.py:304-318` — resume guard already checks `grid` tuple identity, so the constructor-fix's scalar `grid_size → tuple grid` swap is **resume-compatible**.

**The ONLY broken file is the outer `FNOCoregionalization.__init__` (model.py:83-128).** A ≤15-LOC edit mirroring the sibling pattern at `models/mf_fno_transfer_bar/model.py:62-94`. Confidence: HIGH. See [[cycle-007-constructor-fix-pattern]].

### Three failure-targeted research findings

| Focus | Backing | What the Builder uses it for |
|---|---|---|
| **F1 — Anisotropic spectral modes** | Li 2020 FNO `(modes1, modes2)` canonical; neuraloperator library ref impl; F-FNO Tran 2023 documents the split as the right abstraction for non-square grids. IFC paper does NOT use FNO (GP-ODE backbone), so the choice is purely backbone-side. | Outer `FNOCoregionalization.__init__` accepts `modes_h, modes_w, grid: tuple[int, int]`; build `coord_grid` from `grid`; propagate `(modes_h, modes_w)` to inner blocks. **Do not** add a `modes=` backwards-compat kwarg. See [[anisotropic-spectral-modes-fno]]. |
| **F2 — Per-dataset training recipes** | MFRNP ships **3 separate YAMLs** (`Poisson5_config.yaml` ships HF=2.0/LF=0.25; `pde_config.yaml` ships uniform; `Fluid_config.yaml` ships uniform). Empirical, in-code evidence that elliptic Poisson needs LF down-weighting and parabolic Heat / NS does not. IFC paper achieves Poisson SOTA at K=20 + 5000 epochs (smoke wall-time rules out the IFC path). | `_DATASET_RECIPES` dispatch in both `fno_coregionalization/smoke_eval.py` and `fno_coreg_residual/smoke_eval.py`: Heat → `pretrain_frac=0.40, K=20, lrs=(1e-3, 3e-4)`; Poisson → `pretrain_frac=0.0, K=20, lr=3e-4, (HF=2.0, LF=0.25)`. See [[per-dataset-recipes-mf-field]]. |
| **F3 — LF→HF pretrain fractions** | Lyu 2023 ≈0.50; GCS MF-FNO ≈0.50; DPOT 2024 0.667; cycle-005 H2 0.25; Pretraining-in-Lower-Dims 2024 warns of saturation. `fresh Adam + fresh CosineAnnealingLR per stage` is canonical (stale momentum is a documented divergence mode). | Keep `pretrain_frac=0.25` for the constructor-fix PR (don't confound the regression test against the cached 0.01551). Bump to `0.40` for Heat under `_DATASET_RECIPES` in a follow-up. Disable on Poisson (`pretrain_frac=0.0`). See [[lf-hf-pretrain-fraction-survey]]. |

### CEO strategic prioritization (R1.5)

1. **TOP-1 is the load-bearing single experiment for cycle-007.** Projection: composite `0.039578 → ~0.0304` by reinstating the cycle-005 cached heat winner @ 0.01551. **Already at-or-near the bar `0.0274`.** Highest single-EV move.
2. **DO NOT BUNDLE Top-2 recipe changes with Top-1** — confounds the regression test against the cached 0.01551. Top-2 (`_DATASET_RECIPES` for `fno_coreg_residual`) is a separate hypothesis. Strategist may propose as H2 if cycle budget allows; otherwise defer.
3. **Top-3 (LF→HF add-on / new `mf_fno_bar_residual` family) deferred to cycle-008.** With Top-1 alone projected to drop composite to ~0.0304 (near the bar), the case for a brand-new family is weaker.
4. **Hypothesis count target: 1 (Top-1 alone), or 2 (Top-1 + Top-2 decoupled).** Three hypotheses would over-extend cycle budget.

### Expected impact bounds for R2 hypothesis review

- **H1 (constructor fix):** heat `0.02628 → ~0.01551` (cycle-005 cache reattach); composite `0.039578 → ~0.0304`.
- **H2 (per-dataset decoupling, if proposed):** Poisson `0.07419 → ~0.05556` (restoring cycle-005 cache); composite gain `~−0.0016` (stackable with H1). R4 kill-switch (carry-forward from cycle-006): if Poisson regresses >+20% from current 0.07419, revert immediately.

### New citations this cycle (not previously in archive)

| Key | arXiv | Role |
|---|---|---|
| `tran2023ffno` | [arXiv:2111.13802](https://arxiv.org/abs/2111.13802) | Factorized FNO — documents `(modes_h, modes_w)` as the right abstraction; not adopted in cycle-007. |
| `freqmoe2025` | [arXiv:2505.06858](https://arxiv.org/pdf/2505.06858) | Low-freq pretrain → high-freq fine-tune frequency-curriculum. Orthogonal to LF→HF data transfer. Future-cycle direction. |
| `pretrain_lowerdims2024` | [arXiv:2407.17616](https://arxiv.org/pdf/2407.17616) | F-FNO pretraining saturates / can hurt past threshold. Supports keeping `pretrain_frac ≤ 0.5`. |
| `dpot2024` | [arXiv:2403.03542](https://arxiv.org/pdf/2403.03542) | PDE foundation-model pretrain 1000ep / fine-tune 500ep (frac=0.667). High-end of the literature range. |

`papers_summary.csv` is still missing at repo root (a fixed-surface that cycle-007 cannot write); Builder should update `models/fno_coregionalization/INSPIRATION.md` with the new bibtex keys on a follow-up.

### Surface compliance + readiness

All file:line pointers live in `models/**` — no fixed-surface recommendations. Strategist R2 cleared to propose 1 or 2 hypotheses; CEO already flagged surface guard + leakage scan as the R2 deliverable.

**Detail:** `.factory/strategy/research.md` (cycle-007 section appended; full report).

---

## Cycle 007 R1 Failure Analysis (PROCEED 2026-06-02 — Strategist R2 greenlit)

**Close-out docs (so far):** [[ceo-verdict-evaluator-r0]] (R0), [[failure-analysis-cycle-007]] (R1), [[ceo-verdict-failure_analyst]] (R1 PROCEED).

**Branch under test:** `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` (the same branch that banked cycle-005 H2's project-best 0.029357). Eval: `bash scripts/cycle_eval.sh`, 81 s wall, 12 cache hits / 2 cache misses (`fno_coregionalization` both datasets).

### Honest baseline ≠ aspirational best

| Reference point                              | composite_nRMSE | ifc_heat (best family)               | ifc_poisson (best family)      |
|---                                           |---:             |---                                   |---                              |
| **R0 cycle-007 honest baseline (reproducible)** | **0.039578**  | 0.02628 `fno_coreg_residual`         | 0.05961 `fno_mf_stack`         |
| Cycle-005 H2 aspirational best (NOT reproducible) | 0.029357    | 0.01551 `fno_coregionalization`      | 0.05556 `fno_coreg_residual`    |
| Bar (parallel-bench `mf_fno_transfer_bar`)   | 0.0274          | 0.0128                               | 0.0587                          |

**Discrepancy = +0.010221 composite (+34.8%).** Cycle-005 H2 baseline cached entries key against code-hashes `9528aeef4a5a` / `9be21a0f9ce9`; current `models/fno_coregionalization/` resolves to `4235deb6c27c`. Cache files are still on disk; they no longer key-match. The CEO locked in at R0: **0.029357 is aspirational, not a regression bar.**

### Dominant failure mode — COMMITTED_TREE_BROKEN

`fno_coregionalization` hard-crashes both datasets with `TypeError: FNOCoregionalization.__init__() got an unexpected keyword argument 'modes_h'` at `models/fno_coregionalization/smoke_eval.py:265`. `model.py` declares `__init__(... modes, grid_size, b_hidden)` (isotropic single `modes`, scalar `grid_size`) but `smoke_eval.py` was extended to pass anisotropic `(modes_h, modes_w)` and tuple `grid`. The two surfaces diverged when the cycle-006 H1 Builder redirect's `git reset --hard` wiped the never-committed dirty `model.py` that was load-bearing for the cycle-005 H2 baseline. Cell count = 2 / 12 actionable cells; **single largest composite lever available** because reinstating the family recovers the cycle-005 cache 0.01551 on `ifc_heat`.

### Top three interventions (ranked by expected composite delta)

| # | Intervention                                                          | Category                    | Expected Δ composite | Scope        |
|---|---|---|---:|---|
| 1 | Repair `fno_coregionalization.__init__` (accept `modes_h, modes_w, grid`) | COMMITTED_TREE_BROKEN       | **−0.0092**          | single PR    |
| 2 | Decouple `fno_coreg_residual` recipe per dataset (gate on `args.dataset_name`; opt poisson into `_poisson_loss_knob`; revert poisson off the K=20/b_hidden=128 bump) | ARCHITECTURE_OVERFIT (carry-over A) | **−0.0016**          | single PR    |
| 3 | Add LF→HF two-stage transfer to `fno_coreg_residual` (port the H2 schedule from `fno_coregionalization`'s smoke_eval) | TRANSFER_SIGNAL_UNUSED      | **−0.0068**          | single PR (stackable with #2) |

#1 closes ~57% of the gap between honest baseline and aspirational best on its own. #2 and #3 are stackable on the residual family.

### Carry-over verdicts from cycle-006

- **Signal A — K=20 / b_hidden=128 vs MFRNP-Poisson recipe must be decoupled — CONFIRMED.** Cycle-006 banked the architectural bump (heat −13.1%); cycle-007 R0 shows the bank settled in: heat 0.03519 → 0.02628 (−25.3% vs c005), poisson 0.05556 → 0.07419 (+33.5% vs c005). The shared-across-datasets recipe is now the dominant ARCHITECTURE_OVERFIT cell. **Decoupling is intervention #2 above.**
- **Signal B — `fno_coregionalization` constructor fix is ~1 PR — CONFIRMED.** Fix surface: `models/fno_coregionalization/model.py` (primary) + minor mirror at `smoke_eval.py:265`. **This is intervention #1 above.**

### NEW cross-cycle pattern — `silent-regression-cache-layer-masks-uncommitted-load-bearing-state`

**Second consecutive cycle (006 → 007) where a silent regression was discovered when the on-disk `smoke_latest.json` no longer matched the cached numbers from the supposed last-keep result.** The pattern (5 steps):

1. Experiment branch accumulates **dirty working-tree state** load-bearing for the eval (cycle-005 H2's dirty `fno_coregionalization/model.py` matched the anisotropic call site).
2. Dirty state **never committed**. Banked composite (0.029357) depends on it.
3. Later cycle issues `git reset --hard` (cycle-006 H1 Builder redirect #1) — wipes the file.
4. **Cache layer hides the loss**: `cycle_eval` keys cache by content-addressed `code_hash` per `models/<family>/`; after the reset the family's code-hash changes, **all old cache entries become orphans** (still on disk, never queried). Crashed cell silently drops out of leaderboard; composite recomputed without it.
5. Disk metric and "last-keep result" diverge; only surfaced when next cycle's R0 evaluator runs end-to-end.

**Cycle-006 incarnation:** H1 R4 composite 0.029357 → 0.04196 (aggregate). Initially framed as H1 regression; cache-hash forensics in R0 diagnostic showed H1 contributed only Heat −13%, Poisson +3.6% — the composite drop was mostly from `fno_coregionalization` going dark.

**Cycle-007 incarnation:** R0 honest baseline **0.039578** vs aspirational 0.029357 — **+34.8% discrepancy** explained by the same root cause.

**Mitigations (cross-cycle):** (i) every cycle eval that bumps the project-best should additionally verify reproducibility from a clean working tree at the commit hash; (ii) `cycle_eval` cache should refuse to bank composite numbers when the working tree is dirty; (iii) a crashed cell that was previously the dataset winner should raise a hard alarm in the composite path, not silently fall out of the leaderboard. **Upstream root cause = [[patterns]] §"Builder clean-isolation requires pre-clean working tree"; downstream consequence = this pattern at the cache-layer + composite-bookkeeping boundary.** Both must be addressed to prevent recurrence.

See [[patterns]] §"Silent regression masked by the cache layer".

### CEO instructions for downstream agents (R2 Strategist)

- Treat **0.039578 as the cycle-007 baseline**; 0.029357 is aspirational reference, NOT a regression bar.
- Largest single composite lever = intervention #1 (constructor repair, single PR).
- Interventions #2 and #3 are stackable on the residual family — addressing the c006 carry-over A and the unused transfer signal respectively.
- Per-dataset frontier: ifc_heat gap-bound by reinstating `fno_coregionalization`; ifc_poisson "almost there" via `fno_mf_stack` near-parity (1.015× over bar at 0.05961).

**Detail:** [[failure-analysis-cycle-007]].

---

## Cycle 006 CLOSED (2026-06-02 — H1 verdict `revert` — genuine regression)

**Close-out doc:** [[cycle-006-summary]]. **Hypothesis:** Port MFRNP `(HF=2.0, LF=0.25)` Poisson loss-weighting recipe + bump K=10→20 + `b_hidden=128` + add `_DATASET_RECIPES` dispatch on `fno_coreg_residual`. Cite-grounded; cycle-003 Strategist Hand-off predicted clean transfer because the receiving family shares the "per-fidelity FNO + coregionalization basis" structural family.

**Branch + commit:**
- Branch: `experiment/8-fno_coreg_residual-mfrnp-poisson-recipe` (preserved, not merged).
- Parent: `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` (cycle-005 H2).
- Commit: `59b741f` — `feat(fno_coreg_residual): MFRNP Poisson recipe + K=20 basis (H1, cycle-006 exp 8, clean isolation)` (+30/-3 LOC). 1 of 2 Builder redirects used; first attempt contaminated by pre-existing dirty tree, recovered via `git reset --hard` + surgical re-application.

**R4 eval result:**

| Metric | Before (cycle-005 R4) | After (H1) | Δ |
|---|---:|---:|---:|
| `fno_coreg_residual` / ifc_heat | 0.03519 | **0.03059** | **−13.1% IMPROVED** (side effect) |
| `fno_coreg_residual` / ifc_poisson | 0.05556 | 0.05756 | **+3.6% regressed** (primary bet) |
| Composite (aggregate, with broken `fno_coregionalization`) | 0.029357 | 0.04196 | (uninterpretable — see operator action) |
| Composite (estimated, if `fno_coregionalization` were runnable) | 0.029357 | ~0.02988 | ~+1.8% essentially flat |

**Verdict — `revert` (CEO override; first genuine REVERT since cycle-003 H1):**

- Precheck `score_direction` polarity bug passed by coincidence; CEO overrode to REVERT per monotonic-improvement policy.
- The Poisson regression is a genuine architectural finding, NOT a metric anomaly — recipe did not transfer.
- `experiment/8` preserved; `main` and `experiment/7` unchanged. Composite project-best (0.029357) still owned by cycle-005 H2.

**NEW CROSS-CYCLE PATTERN (load-bearing for cycle-007 planning):**

**Cross-architecture recipe portability is NOT guaranteed even when the receiving architecture shares structural family.** The MFRNP `(HF=2.0, LF=0.25)` Poisson recipe works on `fno_mf_stack` (0.0596) but does NOT improve `fno_coreg_residual`'s Poisson (0.0556 → 0.0576). **The residual decoder pathway likely already absorbs the LF/HF asymmetry that the MFRNP loss weights were designed to balance** — adding the recipe over-weights an asymmetry that's already handled implicitly. The cycle-003 Strategist Hand-off's "shares structural family → recipe should transfer" reasoning was wrong; cite-grounded reasoning gave **false confidence** because a single-architecture citation is not evidence of cross-architecture portability. See [[patterns]] §"Cross-architecture recipe portability is NOT guaranteed".

**Separable finding (cycle-007 candidate):** K=20 + b_hidden=128 architectural capacity bump (decoupled from loss reweighting) improved `fno_coreg_residual` Heat by −13% (0.03519 → 0.03059). This is an unexpected positive side effect of the architectural bump, NOT of the loss-reweighting recipe. **Worth pursuing as a standalone hypothesis in cycle-007**, since the side effect is now the more interesting signal than the primary bet.

**Operator action required — `experiment/7` committed tree is intrinsically broken:**

- Cycle-005 H2 baseline (composite 0.029357) was load-bearing on a **dirty `fno_coregionalization/model.py` that was never committed**.
- Committed tree has a constructor signature mismatch: `smoke_eval.py` calls `FNOCoregionalization(cond_dim, hidden_channels, K, n_blocks, modes_h, modes_w, grid)` but `model.py` only accepts `(cond_dim, hidden_channels, K, n_blocks, modes, grid_size, b_hidden)`.
- Builder's `git reset --hard` (for clean isolation) wiped the dirty model.
- **Operator must either:** (a) reconstruct dirty `model.py` and commit a coherent `experiment/7-fixed` branch, or (b) accept that cycle-005 baseline cannot be reproduced from the committed tree.
- This is NOT caused by H1 — it is a pre-existing bookkeeping bug surfaced by H1's clean-isolation rebuild.

**CEO retrospective (Builder hygiene):** `git add <named-file>` is insufficient when the file is already dirty — it commits all pre-existing dirty changes too. **Future cycles must either (i) pre-clean working tree at session start, OR (ii) use `git checkout HEAD -- <file>` before staging.** See [[patterns]] §"Builder clean-isolation requires pre-clean working tree".

**Detail:** [[cycle-006-exp-8]], [[cycle-006-summary]].

---

## Cycle 006 Baseline Failure Analysis (PROCEED 2026-06-02 — Researcher R1.5 greenlit)

**Entry state:** composite_nRMSE = `0.029357` (= cycle-005 H2 cache rolled forward; every run is `_cache=hit`, no fresh signal this cycle). Targets composite ≤ 0.026 (MISS +0.00336) and ifc_heat ≤ 0.013 (MISS +0.00251). Branch: `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`.

**Gap decomposition (log-space):** **Poisson contributes +0.76 nats above target while Heat already contributes −0.52 nats below.** Poisson holds the entire composite gap. 1.27× improvement on either dataset alone closes the composite (Heat 0.01551 → ≤0.01217 also clears hard ifc_heat target; Poisson 0.05556 → ≤0.04358 closes composite only).

**CRITICAL framing correction (Failure Analyst §C.1, CEO highlighted in verdict):** H2 did **NOT** cause the `fno_coregionalization` Poisson regression. Cache hash forensics in cycle-006 baseline `summary.json` confirm:

| Stage                                | hash       | fno_coregionalization Poisson nRMSE |
|---                                   |---         |---:                                 |
| Pre-H2 (cycle-005 R0)                | `9528aeef` | **0.77562** (already architecturally broken) |
| Post-H2 (cycle-005 H2 = cycle-006 R0) | `2954a13e` | **0.75015** (−3.3% improvement)      |

**H2's actual effect: Heat −24.2%, Poisson −3.3% (improvement).** The cycle-005 H2 session-summary "broke Poisson 15×" framing was an across-family comparison error — comparing `fno_coregionalization`'s own Poisson (0.75015) against `fno_coreg_residual`'s Poisson winner (0.05556). The architectural Poisson failure on `fno_coregionalization` predates H2 and is **independent of the LF→HF transfer schedule** (root cause: single shared FNO trunk + K=10 basis head cannot encode Poisson's cross-fidelity scale mismatch). This corrects a load-bearing assumption from the sprint standup; [[patterns]] entry "Multi-fidelity transfer-learning recipes are PDE-class-coupled" has been updated with the cache-hash table.

**Dominant failure mode (re-confirmed from cycle-005 H2 NEW PATTERN):** `PDE_CLASS_ARCH_RECIPE_COUPLING` — one global `SMOKE_DEFAULTS` per family, no dataset-name gating; the recipe-tuned good behavior on dataset A breaks the family on B.

**Per-family failure-mode 10-instance breakdown (5 in-tree × 2 datasets):**
- `PDE_CLASS_ARCH_RECIPE_COUPLING`: **2/10 (20%)** — fno_coregionalization·poisson, fno_mf_stack·heat.
- `NO_TRANSFER_SIGNAL_*`: **2/10 (20%)** — fno_coreg_residual·heat (#3), fno_mf_stack·poisson (#3). **NEW sub-categories** named this cycle.
- `ARCH_QUALITY_FAILURE`: **4/10 (40%)** — transolver_residual + transolver_attention_fusion × both datasets.
- `PASS (winner)`: **2/10 (20%)** — fno_coregionalization·heat, fno_coreg_residual·poisson.

**80% of in-tree instances are not the dataset winner.** Half fixable by recipe gating (PDE-coupling); half fixable only by backbone change (arch-quality). Arch-quality 40% does NOT close the composite gap.

**Per-dataset leaderboard (cycle-006 baseline):**
- `ifc_heat`: fno_coregionalization #1 @ 0.01551 (H2). mf_fno_transfer_bar #2 @ 0.03317. fno_coreg_residual #3 @ 0.03519.
- `ifc_poisson`: fno_coreg_residual #1 @ 0.05556 (~1.54× paper). mf_fno_transfer_bar #2 @ 0.08333. fno_mf_stack #3 @ 0.08829. fno_coregionalization #5 @ 0.75015 (architecturally broken; not introduced by H2).

**Recommended interventions (all within `models/**`, ranked by EV):**
1. **F.1** — Dataset-conditional `pretrain_frac`/`pretrain_lr` in `fno_coregionalization/smoke_eval.py` (5-line `_DATASET_RECIPES` dict gated on `args.dataset_name`). Lowest risk; frees Poisson recipes without touching Heat. Does NOT close gap by itself.
2. **F.2** — Short Heat-only LF-warmup in `fno_coreg_residual/smoke_eval.py` (port H2 pattern, gate `dataset_name == "ifc_heat"`). **Highest single-cycle EV for closing composite via Heat path**; could land fno_coreg_residual at Heat #2.
3. **F.3** — NEW family: HF-conditional curriculum (HF-first → LF-residual fine-tune). Inverse of every existing family; explore-direction EV.
4. **F.4** — NEW family: bar's LF→HF transfer + `fno_coreg_residual`'s per-fidelity residual head. **Direct response to NEW DIRECTIVE** — bar at #2 on both; combining both demonstrated strengths into one family. Most ambitious.
5. **F.5** — Diagnose `fno_mf_stack` Heat 0.130 anomaly (suspected: `poisson_*_weight` gating off Heat → uniform LF weights). Cheap if confirmed.

**No-op directions:** transolver_* arch-quality failures (40% of instances) do not close composite gap; leave for free cycle.

**CEO verdict on Failure Analyst output: PROCEED — publish-quality, no issues material.** Researcher R1.5 greenlit on (a) dataset-conditional MF scheduling literature; (b) composition of "bar LF→HF transfer + residual coregionalization head"; (c) Poisson-direct attacks on per-fidelity FNO; (d) HF-first curriculum literature.

**Detail:** [[failure-analysis-cycle-006]]

**Cross-cycle pattern impact:** [[patterns]] entry "Multi-fidelity transfer-learning recipes are PDE-class-coupled" updated with corrected H2 cache-hash table. [[patterns]] entry "`PDE_CLASS_ARCH_RECIPE_COUPLING` is the dominant in-tree failure mode at cycle 006" appended — codifies 10-instance breakdown + cheapest-fix gating prescription + `NO_TRANSFER_SIGNAL_*` sub-categories.

---

## Cycle 005 H2 (CLOSED 2026-06-02 — `revert_bookkeeping_keep_intent` — **NEW PROJECT BEST**)

**Hypothesis (cycle-005 H2):** absorb `mf_fno_transfer_bar`'s two-stage LF→HF transfer-learning schedule (`pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25`, fresh `Adam` + `CosineAnnealingLR` per stage) into the cycle-005 R0 winner on ifc_heat, `fno_coregionalization`. Training-schedule-only — architecture (K=10 basis head, per-fidelity scalers, FNO trunk) is unchanged.

**Branch + commit:**
- Branch: `experiment/7-fno_coreg_lf_hf_transfer` (preserved, not merged).
- Base: `experiment/6-mf_fno_transfer_bar-repo-root-fix` (NOT `main`) — inherits H1's REPO_ROOT fix.
- Single commit: `be36cba` — `feat(fno_coregionalization): two-stage LF→HF transfer schedule (H2)`.
- Diff: +398 / -75, 2 files, all under `models/fno_coregionalization/` (smoke_eval.py + INSPIRATION.md).

**R4 eval result (`bash scripts/cycle_eval.sh`, 124 s wall on cuda):**

| Metric                                            | Value                       |
|---                                                |---                          |
| **composite_nRMSE (project)**                     | **0.029357** (Δ −0.00437, **−13% vs R0 0.033726 — NEW PROJECT BEST**) |
| `fno_coregionalization` ifc_heat                  | **0.01551** (Δ −24% vs R0 0.02047; **#1, gap to #2 mf_fno_transfer_bar 0.03317 grew to 2.1×**) |
| `fno_coregionalization` ifc_poisson               | **0.7501** (Δ +15× vs R0 ~0.05; **dropped to #5**) |
| `fno_coreg_residual` ifc_poisson (still #1)       | 0.05556 (unchanged — composite unaffected by fno_coregionalization's ifc_poisson regression) |

**Acceptance targets — partial success:**

| Target                                                       | Result    | Met?   |
|---                                                           |---        |---     |
| ifc_heat ≤ 0.013 (hard target, bar parallel-bench 0.0128)    | 0.01551   | NO (19% over)  |
| composite ≤ 0.026 (hard target, beats bar parallel-bench)    | 0.029357  | NO (13% over; bar parallel-bench 0.02743 still wins by 0.002) |
| H1-calibration realistic band 0.028–0.032                    | 0.029357  | **YES** (in band, lower third) |
| NEW project-best composite (< 0.033726)                      | 0.029357  | **YES** (−13%) |
| NEW family-best on ifc_heat (< 0.02047)                      | 0.01551   | **YES** (−24%, holds #1) |

**Research-relevant side effect — ifc_poisson regression of `fno_coregionalization`:** the LF→HF schedule mis-fits the poisson loss surface (LF Stage-1 over-fits the value-scale-collapsing LF data; Stage-2 fine-tune at 3e-4 cannot recover within 150 epochs). Composite-level performance is unaffected because the per-dataset best-family partitioning routes poisson to `fno_coreg_residual` (still owns ifc_poisson at 0.05556). New cross-cycle pattern recorded: **LF→HF transfer schedules are PDE-class-coupled** — Heat-class (smooth fidelity correlation) benefits, Poisson-class (stiff value-scale shift) breaks. Variant of the cycle-003 H1 finding "MFRNP per-fidelity loss-weighting recipes are backbone-coupled". Cycle-006 high-EV move: dataset-conditional `n_warmup` gating keyed on `"poisson"` in dataset name (by analogy with cycle-002 H4's `resolve_fidelity_weights`).

> **CORRECTION (cycle-006 baseline failure analysis, 2026-06-02):** the framing above that "H2 broke Poisson 15×" is wrong. Cache hashes in cycle-006 baseline `summary.json` show `fno_coregionalization` Poisson was **already 0.77562 pre-H2** (hash `9528aeef`), then **0.75015 post-H2** (hash `2954a13e`) — a **−3.3% improvement**, not a 15× regression. The "+15×" came from comparing the family's own Poisson against `fno_coreg_residual`'s Poisson winner (0.0556), not against the family's own pre-H2 Poisson. **The architectural Poisson failure on `fno_coregionalization` predates H2 and is independent of the schedule** (root cause: K=10 basis head cannot encode Poisson cross-fidelity scale mismatch). The PDE-class-coupling pattern itself still stands, just with the corrected mechanism. See [[failure-analysis-cycle-006]] §C.1 and [[patterns]] §"Multi-fidelity transfer-learning recipes are PDE-class-coupled" (corrected cache-hash table).

**R5 precheck — FAILED on bookkeeping only (5th consecutive):**

1. **`score_direction` FALSE POSITIVE.** Precheck assumes higher=better; for `composite_nRMSE` lower=better, so 0.0337 → 0.0294 (a 13% improvement) was flagged as "Score regressed: 0.0337 → 0.0294 (delta=−0.00437)". **7-for-7 across project history** — every successful eval (001 H1, 001 H2, 002 H4, 002 H3, 005 H1, 005 H2) has hit this same polarity bug.
2. **`scope` empty-detail.** Pre-existing 15-file dirty tree from data_adapters migration cruft (not from H2). Standalone `factory guard --check-scope` clean against H1 branch base.
3. **`fixed_surfaces` empty-detail.** Same 15-file dirty tree includes `references/v9_baseline/smoke_eval.py` (fixed surface).
4. **`ground_truth_leakage` substring-collision FPs** on `modify`/`satisfy`/`ifc_raw` matched in `factory.md`/`README.md`/schema text (not under `data/**`).

**Hard gates that PASSED:** `anti_pattern` ✓ (all 7 cycle-005 anti-patterns honored), `smoke_test` ✓ (all 7 datasets ran end-to-end, no crashes; 0.7501 is a finite well-typed nRMSE, a regression not a crash).

**Verdict — `revert_bookkeeping_keep_intent` (5th consecutive):**

- The controlling research target (composite_nRMSE) IMPROVED 13% to a new project-best — the **first sub-0.030 composite in project history**.
- All four precheck failures are documented bookkeeping bugs, NOT real regressions. anti_pattern + smoke_test both pass.
- `experiment/7-fno_coreg_lf_hf_transfer @ be36cba` preserved; `main` unchanged.
- **Cycle-006 hypotheses will branch off `experiment/7-fno_coreg_lf_hf_transfer`** (NOT `main`) — second consecutive downstream-branch off a `revert_bookkeeping_keep_intent` preserved branch.

**Detail:** [[factory_mffp-007]]

**Cross-cycle pattern (now 5-for-5 keep-intent reverts; precheck-bookkeeping subsystem overhaul is load-bearing):** `score_direction` polarity bug 7-for-7, scope/fixed_surfaces empty-detail 5+ times, leakage substring-collision 6+ times. **Without an overhaul, cycle-006 will close `revert_bookkeeping_keep_intent` for the 6th consecutive time** even if it lands a new project best. See [[patterns]] §"Factory precheck `score_direction` is polarity-buggy on lower-is-better metrics".

**First training-schedule-only hypothesis to land project-best:** validates "training-schedule edits as a research lever" — no architectural search, no new family directory, no `model.py` change, and a 13% composite improvement. Cheap family of cycle hypotheses moving forward.

## Cycle 005 H1 (CLOSED 2026-06-02 — `revert_bookkeeping_keep_intent`)

**Hypothesis (cycle-005 H1):** 1-line REPO_ROOT fix in
`models/mf_fno_transfer_bar/smoke_eval.py:32` to unblock the bar's
smoke harness so the bar lands on the smoke leaderboard. Stated as a
*comparability prerequisite*, not a research bet — expected impact on
composite was zero.

**Branch + commits:**
- Branch: `experiment/6-mf_fno_transfer_bar-repo-root-fix` (preserved, not merged).
- Base: `bench/all-fno-families`.
- `a415e26` — `fix(mf_fno_transfer_bar): correct REPO_ROOT to two-parent walk` (the 1-line science).
- `17e5234` — `fix(mf_fno_transfer_bar): track supporting model.py and manifest.json` (bookkeeping — base branch never tracked these supporting files).

**R4 eval result (`bash scripts/cycle_eval.sh`):**

| Metric                                            | Value                       |
|---                                                |---                          |
| `composite_nRMSE` (project)                       | **0.033726** (Δ +1.06e-7)   |
| `mf_fno_transfer_bar_present`                     | **true** ✓                  |
| `mf_fno_transfer_bar` smoke composite (geomean)   | **0.05258**                 |
| `mf_fno_transfer_bar` smoke `ifc_heat`            | 0.033175 (rank #2)          |
| `mf_fno_transfer_bar` smoke `ifc_poisson`         | 0.083326 (rank #2)          |

H1's stated goal (bar on leaderboard) achieved. Pre-registered
"composite unchanged" prediction verified — bar is #2 on both ifc
datasets, not #1, so per-dataset leaders (`fno_coregionalization` on
ifc_heat 0.020472, `fno_coreg_residual` on ifc_poisson 0.055561) hold.

**Calibration finding — bar smoke ≠ bar parallel-bench:**

| Source                                              | ifc_heat | ifc_poisson | geomean   |
|---                                                  |---:      |---:         |---:       |
| `results/bench_metrics.csv` (parallel-bench)        | 0.012814 | 0.058715    | 0.02743   |
| `results/smoke_latest.json` (cycle-005 H1 smoke)    | 0.033175 | 0.083326    | 0.05258   |

The smoke harness measures the same bar **1.9× worse** than the
parallel-bench harness. Differences: epochs, train/test splits, grid
resolution. **Operational consequence — future smoke-harness
experiments must beat `0.05258` smoke composite, NOT `0.02743`
parallel-bench composite.** Future strategy snapshots must declare
which harness the bar is in.

**R5 precheck — FAILED on bookkeeping only:**

1. **Pre-existing dirty tree (15 files).** Leftovers from prior
   bench-branch work; not from H1's commits.
2. **Downstream fixed-surface fallout.** Same 15-file dirty tree
   includes `references/v9_baseline/smoke_eval.py` (fixed surface).
   Not from H1.
3. **5 substring-collision leakage false positives.** `"modify"`,
   `"loader"`, `"description"`, `"ifc_raw"`, `"frozen"` — all in
   `factory.md`/`README.md`/`manifest.json` documentation/schema
   text; none from `data/**`. Same scanner bug pinned in
   [[patterns]] across cycles 001 H1/H2, 002 H4/H3, 003 H1.

**Verdict — `revert_bookkeeping_keep_intent`** (per documented
cycle-001/002/003 precedent):

- `experiment/6-mf_fno_transfer_bar-repo-root-fix` preserved
  (commits intact, branch not deleted).
- `main` unchanged (precheck gate honored).
- **Cycle-005 H2 will branch from `experiment/6-mf_fno_transfer_bar-repo-root-fix`** (NOT from `main`) to inherit H1's REPO_ROOT fix in its eval environment. This is a strategy-snapshot update: the original cycle-005 plan said "H2 off post-H1-merge target branch"; the corrected plan is "H2 off `experiment/6-mf_fno_transfer_bar-repo-root-fix`" because H1 did not merge.

**Detail:** [[factory_mffp-006]]

**Cross-cycle pattern (now 6-for-6):** `revert_bookkeeping_keep_intent`
has been the verdict for every eval in this project's history. The
substring-collision precheck scanner bug is the most reliably-triggered
failure mode in the factory. Out-of-scope follow-up (open since cycle
001): scanner needs token-class differentiation (value vs schema vs
documentation tokens).

---

## Cycle 005 (STRATEGY APPROVED 2026-06-02)

**Cycle entry:** R0 composite_nRMSE = **0.033726** on
`bench/all-fno-families` (24% better than cycle-004's 0.04415).
Source: `.factory/research/runs/cycle-005-baseline/failure_analysis.md`.

**Bar to beat:** `mf_fno_transfer_bar` ≈ **0.0274** composite
(`results/bench_metrics.csv`). The bar's smoke harness currently
crashes due to a 1-line `REPO_ROOT` bug; bar is *not* on the smoke
leaderboard yet — current reference comes from the parallel
benchmark pipeline (sbatch full-bench), not the smoke harness.

**Dominant gap (ifc_heat):** winner `fno_coregionalization` at
0.0205 vs bar 0.0128 — a 1.6× gap with **zero >2×-median outliers**
(very tight distribution, n=128). Closing this requires shifting
the whole distribution down, not catching outliers. The bar
achieves this via LF→HF FNO-trunk transfer-learning pretraining;
`fno_coregionalization` trains jointly with no pretrain phase.

**Non-gap (ifc_poisson):** winner `fno_coreg_residual` at 0.0556 ≈
bar (0.0587). Composite gap is dominated entirely by ifc_heat;
closing it alone via H2 takes composite 0.0337 → ~0.026 — beats
the bar directly. H3 (modes/uncertainty) is deferred per
`research.md` §5.

**CEO Strategist verdict: PLAN APPROVED (HARD GATE).** Two
hypotheses, both with line-of-code-level specifications. Backlog
convergence: 2 cleared, 0 added, within `max_new=2` budget.

### H1: Fix `mf_fno_transfer_bar` REPO_ROOT off-by-one (FIX, prerequisite)
- **Branch base:** `bench/all-fno-families`.
- **Branch name:** `experiment/<EXP_ID>-mf_fno_transfer_bar-repo-root-fix`.
- **Mutable surface:** `models/mf_fno_transfer_bar/smoke_eval.py` line 32 ONLY.
- **Change:** `REPO_ROOT = HERE.parent.parent.parent` → `REPO_ROOT = HERE.parent.parent`.
- **Why:** the current `.parent.parent.parent` walks one directory too far up to `mf_field/`, which contains no `data_adapters/` package → `ModuleNotFoundError: No module named 'data_adapters'` in both local-pass and SLURM (job 15313689). With `.parent.parent` the path lands on the project root that owns `data_adapters/`.
- **Acceptance:** diff is EXACTLY one line. `git diff --stat` must show `1 file changed, 1 insertion(+), 1 deletion(-)`. `mf_fno_transfer_bar` composite in `results/smoke_latest.json` lands in [0.025, 0.030] (matching bench-pipeline ~0.0274).
- **Expected impact on cycle-005 composite:** none — this is purely a comparability prerequisite for H2's claim of beating the bar.

### H2: LF→HF transfer-learning pretraining for `fno_coregionalization` (EXPLOIT, main growth bet)
- **Branch base:** post-H1-merge target branch (so H1's fix is included).
- **Branch name:** `experiment/<EXP_ID>-fno_coreg_lf_hf_transfer`.
- **Mutable surface:**
  - `models/fno_coregionalization/smoke_eval.py` — SMOKE_DEFAULTS additions (`pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25`), two-stage train loop, LF-filtered DataLoader, fresh opt+sched per stage, `stage` field in checkpoint, resume guard update.
  - `models/fno_coregionalization/INSPIRATION.md` — append paragraph citing `lyu2023mffno` (LF→HF transfer recipe) and `li2022ifc` (coregionalization basis).
- **Architecture unchanged:** no changes to `model.py`, `data.py`, `manifest.json`, `full_config.json`.
- **Recipe:** all hyperparameters taken directly from `mf_fno_transfer_bar/smoke_eval.py` (the bar's own recipe). Stage 1 = `n_warmup = round(pretrain_frac * args.epochs)` epochs on LF-only DataLoader with fresh `Adam(lr=1e-3)` + fresh `CosineAnnealingLR(T_max=n_warmup)`. Stage 2 = remaining epochs on full DataLoader with fresh `Adam(lr=3e-4)` + fresh `CosineAnnealingLR(T_max=epochs - n_warmup)`. **Same `model` object across stages; weights carry forward; `set_scalers(...)` called ONCE before Stage 1.**
- **Resume schema:** `last.pt` gains a `stage ∈ {1, 2}` field; guard requires `stage == 2 AND epoch == epochs_target`.
- **Expected impact:** ifc_heat 0.0205 → **≤ 0.013** (closes the 1.6× gap to bar's 0.0128); composite 0.0337 → **≤ 0.026** (beats the bar's ~0.0274). ifc_poisson ≤ 0.07 (no >25% regression from 0.0556).

### Compositional framing
H2 absorbs the bar's transfer-learning mechanism into the cycle-005 R0 winner on ifc_heat. The coregionalization head (`li2022ifc`) is a strictly better fidelity-mixing mechanism than the bar's per-stage scaler swap; combining the bar's training recipe with the coregionalization head should equal-or-exceed the bar on ifc_heat while preserving the existing ifc_poisson behavior. Mirrors cycle-002 H3's pattern (compose two SOTA mechanisms onto a single architecture).

### Surface + leakage gates: BOTH CLEAN
- **Surface check PASS:** all files under `models/**`; no fixed-surface touches.
- **Leakage scan PASS (BOTH H1 AND H2):** `flagged: false, risk_level: none, findings: []`. **Notable** — every prior cycle (001/002/003) tripped substring-collision false-positives on `"poisson"` or `"001"`. Cycle-005 hypotheses avoid those failure modes by design. **First cycle without precheck override expected.**

### Branch base plan: H1 first, H2 second (NOT parallel)
- H1 builds first as 1-line prerequisite — H2's claim of "beating the bar in-distribution" is meaningless until the bar appears on the smoke leaderboard.
- H2 builds second off the post-H1-merge branch so H1's fix is included in H2's eval environment.

### Systemic agent-wrapper-timeout caveat (tracked)
- **Researcher and failure_analyst wrappers timed out twice this cycle** (systemic, tracked in `failure_analysis.md` §C). CEO synthesized `research.md` and `failure_analysis.md` from direct source reads (`mf_fno_transfer_bar/smoke_eval.py`, `fno_coregionalization/smoke_eval.py`, `papers_summary.csv`). No new external WebSearch this cycle.
- **If the Builder wrapper exhibits the same pattern** (no PR opened, no output captured), retry once with `--timeout 1800`. If it fails again, escalate to operator (Sprint Standup caveat).
- **Do NOT attempt CEO-direct edits to `smoke_eval.py`** — that would violate the delegation rule even in research mode.
- This is a systemic factory-infrastructure issue, not a model-science issue; documented for ops follow-up.

### Anti-pattern catalog (7 don'ts; all binding)
Do NOT: (1) create a new family directory for H2; (2) freeze the K=10 coregionalization basis during Stage 1; (3) share optimizer/scheduler state across the stage boundary; (4) lower `args.epochs` to "save wall time"; (5) add per-stage rescaling; (6) pursue H3 (modes/uncertainty) this cycle; (7) bundle the H1 fix with other edits to `mf_fno_transfer_bar`.

Plus: do NOT touch fixed surfaces. Three carry-forward Researcher TODOs (`baselines/paper_baselines.json` patch, FIRE row in `papers_summary.csv`, 2024–2026 WebSearch) all require fixed-surface writes or external API access — explicitly deferred per `research.md` §6.

See [[cycle-005-strategy]] for the full strategy snapshot, `.factory/strategy/current.md` for the source, and `.factory/reviews/ceo-verdict-strategist.md` for the verdict.

---

## Cycle 003 (CLOSED 2026-05-15)

**Cycle outcome:** **NO new project best.** First genuine REVERT in
project history (CEO intent and factory state agree for the first
time — all 4 prior cycles' REVERTs were precheck-bookkeeping
discrepancies with CEO=KEEP intent). Project best remains cycle-002
H3 at composite_nRMSE = **0.04420** on
`experiment/4-fno_coreg_residual @ 0c46f43`.

**H1 `fno_coreg_residual_poisson_loss_reweighting` R4 + R5 COMPLETE;
CEO REVERT.** Ported H4's `resolve_fidelity_weights` helper into H3's
`fno_coreg_residual` hybrid (Poisson-conditional MFRNP Poisson5
weighting `hf_fid_w=2.0, lf_fid_w=0.25`; Heat path uniform). Branch
`experiment/5-fno_coreg_residual_poisson_lossweight` commit `a0d932b`
preserved on disk for cycle-004 reference. **Composite_nRMSE 0.04420
→ 0.08472 (+91.7% regression on the research target).** Per dataset:
`ifc_heat` **0.02630** (unchanged from cycle-003 entry within seed
noise — uniform-weight Heat path reproduced by construction; **still
BEATS paper 0.074 by 2.81×**); `ifc_poisson` **0.27287** (3.68×
WORSE than cycle-003 entry 0.07416; 4.58× WORSE than cycle-002 H4
0.05961 on the simpler `fno_mf_stack` backbone; 7.58× over paper
0.036). Val/test gap on H1+poisson `best_val_nRMSE=0.0783` vs
`test=0.27287` suggests the asymmetric weights overconcentrate
gradient budget on a narrow HF feature set that overfits, while
starving the LF supervision the H3 coregionalization stack depends
on for cross-fidelity sharing.

**Refuted scientific framing (cycle-003 H1's load-bearing finding):**
the MFRNP Poisson5 (2.0, 0.25) recipe is **backbone-coupled**, NOT
"PDE-class-bound (elliptic)" as the cycle-003 strategy framed it.
The recipe helps on `fno_mf_stack` (cycle-002 H4: ifc_poisson 0.0999
→ 0.0596) but catastrophically harms `fno_coreg_residual` (cycle-003
H1: ifc_poisson 0.07416 → 0.27287). Same recipe, same PDE-class, same
data — opposite outcome under different MF-aggregation backbones. New
[[patterns]] entry pinned: "MFRNP per-fidelity loss-weighting recipes
are backbone-coupled across MF aggregation architectures." This
**bounds** the cycle-002 H4 finding that "MFRNP recipes port across
architectures" — they port within the residual-stack-on-FNO family
but not across to the hybrid basis-head + MFRNP-residual-stack
family.

**First genuine REVERT in project history.** Cycles 001/002 had 4
reverts (H1, H2, H4, H3) all of which were precheck-bookkeeping
failures with CEO=KEEP intent (score_direction polarity bug,
scope/fixed_surfaces empty-detail, ground_truth_leakage substring
collision). Cycle-003 H1 is the FIRST REVERT where the CEO intent
agrees with the factory state, and the underlying reason is a
genuine research-target regression. Same 4 precheck false-positives
still fired here, but the precheck failure aligns with reality for
the first time.

**Checkpoint-resume contamination discovered + operationally resolved
(but the underlying factory bug remains).** First SLURM run 13973868
resumed from a partial CPU pre-train checkpoint left over from an
earlier 1800s cache-only local pass that timed out and saved
`last.pt` at the last 10% epoch milestone. Poisson resumed
mid-trajectory: `train_seconds=33.31s` for poisson vs heat's 461s on
similar-shape data. CEO moved the contaminated checkpoints to
`.factory/research/runs/cycle-003-H1/contaminated_checkpoints/`,
deleted the stale cache `results/raw/fno_coreg_residual__ifc_poisson__e200__s42__2c3be3539e1c.json`,
and submitted fresh SLURM job 13974837 from an empty ifc_poisson
checkpoint dir. Clean run trained 200 epochs from scratch on cuda
(`train_seconds=549.15`). Clean (0.27287) and contaminated (0.27259)
results matched to within 0.10% — verdict robust either way. **But
the underlying factory bug is systemic**: the checkpoint-resume guard
(`epoch == epochs_target` AND `cond_dim` match) does NOT invalidate
checkpoints when the training recipe changes. The cycle-002 H3
project-best baseline (0.04420) was almost certainly also
checkpoint-contaminated to some unknown degree — its
`fno_coreg_residual_train_seconds: ifc_poisson: 25.0` is implausibly
fast for 200 epochs of training. Two cycle-004 backlog items filed:
(a) recipe-fingerprint checkpoint guard, (b) re-verify the cycle-002
H3 baseline under a clean from-scratch run as a cycle-004
prerequisite.

**Cycle-004 implications (pre-registered):**

1. **Static MFRNP Poisson5 recipe is dead as a portable knob.** Drop
   the "PDE-class-bound" framing; treat per-fidelity loss-weighting as
   per-backbone-tuned.
2. **Loss-weighting on H3 remains a legitimate lever** but must be
   (a) **adaptive** — GradNorm-lite, uncertainty-weighted, or
   PCGrad-style — or (b) **gentler asymmetric** (e.g. (1.5, 0.5))
   tuned per backbone.
3. **Recipe-fingerprint checkpoint guard is a cycle-004 candidate**
   — the contamination this cycle exposed will recur on every future
   experiment that changes a training-recipe knob.
4. **Re-verify cycle-002 H3 baseline** under a clean from-scratch run
   as cycle-004 prerequisite before any further architectural
   experimentation.
5. **Anchor-scaling ablation** (anchor scaled by `hf_fid_weight` vs
   unscaled when asymmetric weighting is on) is cheap; could isolate
   the build-phase design decision from the overall recipe-incompatibility
   signal. Lower priority than the adaptive scheme.

See [[factory_mffp-005-experiment]] for the full H1 outcome,
[[cycle-003-summary]] for the cycle-level close-out, and the
patterns entry "MFRNP per-fidelity loss-weighting recipes are
backbone-coupled across MF aggregation architectures" in
[[patterns]] for the refined cross-cycle rule.

---

## Cycle 003 (BUILD phase, 2026-05-15)

**H1 Build COMPLETE; CEO verdict PROCEED.** Branch
`experiment/5-fno_coreg_residual_poisson_lossweight` cut from
`experiment/4-fno_coreg_residual` (cycle-002 H3 @ `0c46f43`, project
best 0.0442). Single commit `a0d932b` adds 67 / removes 5 lines across
`models/fno_coreg_residual/smoke_eval.py` (new `resolve_fidelity_weights`
helper; SMOKE_DEFAULTS gains `poisson_hf_weight=2.0`,
`poisson_lf_weight=0.25`; `compute_losses` extended with `hf_fid_weight`
/ `lf_fid_weight` kwargs; resolver called once at training-loop entry,
active pair logged) and `models/fno_coreg_residual/INSPIRATION.md`
(cycle-003 paragraph with bibtex for `mfrnp_poisson5_config`,
`boulle2023ellipticdata`, `chen2018gradnorm`). Pre-flight 2-epoch
smoke verifies dataset-name gating: `ifc_heat` logged
`hf_fid_weight=1.0 lf_fid_weight=1.0` (uniform — Heat win preserved
by construction), `ifc_poisson` logged
`hf_fid_weight=2.0 lf_fid_weight=0.25` (MFRNP Poisson5 values active);
both contract JSONs include `metric_value`. **Surface guard clean**
with explicit-SHA baseline (passing the branch ref tripped a
"Branch is not rooted at baseline" violation despite merge-base
equaling tip — guard-tool baseline-resolution bug, NOT a code
violation; filed as factory-infrastructure observation).
**Leakage scan** = 2 findings, both known substring-collision
false-positives (`"poisson"` is the dataset name, `"001"` is the
filesystem path component / cycle index). **Builder design choice
acknowledged**: the aggregator anchor term is now multiplied by
`hf_fid_weight` (=2.0 on Poisson) alongside the HF residual,
because H3 has an anchor regulariser that H4 (where the resolver
was originally written) does not. Net effect on Poisson is a
slightly more aggressive HF/LF ratio than H4's pure 8:1 — may help
further (more HF emphasis with H3's basis-head + hidden=64 capacity)
or may over-correct. Eval will tell. **PROCEED to R4** (200-epoch
`cycle_eval.sh` on the new branch). Cache will MISS on
`models/fno_coreg_residual/` (new code_hash); H1/H2/H4 + v9 caches
unaffected. See [[factory_mffp-005-build]].

**Cycle-003 H1 entry state (failure analysis):** Entry =
cycle-002 H3 at composite_nRMSE **0.04420** (1/2 datasets beating paper).
Dominant failure mode is **`ABSENT_POISSON_LOSS_WEIGHTING`** — a new
sub-category of `DATASET_INVARIANT_TRAINING_RECIPE`.

- `ifc_heat` **PASS** at 0.02634 (beats paper 0.074 by 2.81×).
- `ifc_poisson` **FAIL** at 0.07416 (2.06× over paper 0.036; gap = 0.0381).

**Root cause** (grounded in code diff): `models/fno_coreg_residual/smoke_eval.py`
has no `resolve_fidelity_weights` helper; `SMOKE_DEFAULTS` ships
`hf_loss_weight=1.0, lf_loss_weights=(1.0, 1.0, 1.0)` for *every* dataset.
`models/fno_mf_stack/smoke_eval.py` (H4) has the helper, which returns
`(hf=2.0, lf=0.25)` only when `"poisson"` is in the dataset name and
uniform otherwise. H3's own `full_config.json` documents the alternative
weights under `_poisson_loss_knob` but explicitly says **"Off by default
in the smoke harness; orchestrator must opt in by overriding
hf_loss_weight and lf_loss_weights when running ifc_poisson"** — the
orchestrator (`scripts/cycle_eval.sh` → SLURM → `smoke_eval.py`) never
sets that override. **The Poisson-loss knob is dead code at eval time.**

**Train/val/test gap signature on Poisson:** best val_nRMSE 0.02298 vs
test 0.07416 (3.23× val→test gap) → **capacity is sufficient; gradient
signal allocation is broken** (uniform weights pull gradient toward LF
terms, starving the HF residual that the test split actually scores).
Mechanism explains why Heat improved dramatically (no asymmetry needed)
while Poisson regressed (Heat dominates the composite improvement; Poisson
regression is fully attributable to the missing knob).

**Secondary candidates de-prioritized** (collapse into the same
gradient-allocation root cause once weighting is fixed):
`CAPACITY_OVERALLOC_TO_LF`, `MODES_TUNED_FOR_HEAT`,
`BASIS_HEAD_MISCALIBRATION`.

**CEO verdict on Failure Analyst: PROCEED.** Publish-quality, no issues.
See [[failure-analysis-cycle-003]] for the full archive note;
`.factory/research/runs/cycle-003-baseline/failure_analysis.md` for the
raw output; `.factory/reviews/ceo-verdict-failure_analyst.md` for the
verdict.

**R1.5 Researcher greenlit** with literature-search focus on:
(a) MF loss reweighting theory (grounding for HF/LF asymmetry),
(b) 2024-2026 MF papers confirming elliptic / Poisson-class PDEs benefit
from HF up-weighting vs other PDE classes,
(c) curriculum / adaptive alternatives (dataset-conditional curriculum,
annealed weighting),
(d) provenance of H4's static `(2.0, 0.25)` — hand-tuned or paper-cited?
Plus: alternative balanced-loss formulations for Strategist comparison
(per-fidelity variance normalization, GradNorm-style adaptive balancing,
uncertainty weighting). Findings to `.factory/strategy/research.md`.

**Recommended single intervention for H5** (Failure Analyst's #1, CEO
endorsed): port H4's `resolve_fidelity_weights(dataset_name, p)` into
`models/fno_coreg_residual/smoke_eval.py`, gate strictly on `"poisson"`
in the dataset name. Expected effect anchored to **measured** H4 Poisson
(0.0596), not a forecast: ifc_poisson lands in H4's neighbourhood (~0.060)
at minimum; combination of H3's basis-head capacity + H4's loss weighting
plausibly does better; composite floor ≈ 0.0396 even at exact H4-Poisson
parity (a further −10% from 0.0442). **Risk:** Heat result depends on
existing uniform weighting — override must be strictly Poisson-conditional
to avoid disturbing the Heat win.

---

**Cycle 002 H3 R4 COMPLETE 2026-05-15 — NEW PROJECT BEST.** H3
(`fno_coreg_residual` novel hybrid: H1 continuous-m basis head over H2
MFRNP residual stack with decoder-in-the-aggregation) **composite_nRMSE
1.6595 → 0.04420** (**−97.3% vs project state, 37.5× improvement**;
**−43% vs cycle-002 H4 0.07719**; −60% vs cycle-001 H2 0.11173; −75%
vs cycle-001 H1 0.10919). Per dataset: `ifc_heat` **0.02634** (**beats
paper bar 0.074 by 2.81×** — first family in project history to do so),
`ifc_poisson` **0.07416** (still 2.06× over paper 0.036; -25%
regression vs H4 0.0596 because H4's Poisson-specific HF=2/LF=0.25
loss reweighting was not ported into H3). **FIRST family in project
history to beat the paper composite geomean** (0.0442 < 0.0516, 0.86×).
9.12M params; train wall ~17 min on cuda; sbatch wall 4844 s (~80 min
including queue/startup). Hypothesis hit the strategist's predicted
~0.04 target spot-on. **F5 INVERSE_COMPLEMENTARY_FAMILIES resolved at
the architectural level** — the two parent inductive biases compose,
each surviving in its dominant regime (basis head → Heat smoothness;
MFRNP aggregator → stiff Poisson). **CEO verdict KEEP**; factory
bookkeeping recorded `revert` due to the **same 4 precheck
infrastructure bugs** (4th consecutive cycle override — see
[[patterns]]). Branch `experiment/4-fno_coreg_residual` commit
`0c46f43` intact on disk. See [[factory_mffp-004-outcome]],
[[factory_mffp-004-build]].

**Cycle-003 H5 pre-registered (highest-EV next move)**: port H4's
Poisson-specific HF=2/LF=0.25 loss reweighting into H3's architecture.
Predicted: `ifc_heat` ~0.025 (preserved; Knob-2 inert on Heat),
`ifc_poisson` ~0.05-0.06 (inherits H4's Poisson gain on top of H3's
basis head), composite ~0.035-0.040; likely first crossing of the
published `ifc_poisson` paper bar. Mechanical single-knob extension
of the project-best family. See [[factory_mffp-004-outcome]]
§"Cycle-003 hypothesis pre-register".

**Cycle 002: H4 R4 COMPLETE 2026-05-15.** H4 (`fno_mf_stack` capacity +
Poisson-loss bump) **composite_nRMSE 1.6595 → 0.07719** (−95.3% vs project
state, **21.5× improvement**; **31% improvement over cycle-001 H2 0.11173**).
Per dataset: `ifc_heat` 0.1275 → **0.0999** (22% recovery; 1.35× over paper);
`ifc_poisson` 0.0979 → **0.0596** (39% improvement; 1.66× over paper). **Both
pre-registered MFRNP Poisson5 knobs validated independently**: Knob 1
(capacity bump `hidden 16→32, modes (4,5,5,5)→(4,8,12,12), blocks 2→3`)
drove the Heat recovery; Knob 2 (Poisson-only HF=2/LF=0.25 loss weighting)
drove the Poisson improvement. n_params 2.28M (23.4× larger than H2, half
of H1). Train wall ~28 min on CPU (would be much faster on H100 SLURM).
**CEO verdict KEEP**; factory bookkeeping recorded `revert` due to the
**same 4 precheck infrastructure bugs** (3rd consecutive cycle override —
see [[patterns]]). Branch `experiment/3-fno_mf_stack_v2_capacity_loss`
commit `ddd221d` intact. See [[factory_mffp-003-experiment]].

**Within-family F5 partial resolution**: `fno_mf_stack` at H4 capacity now
wins BOTH datasets within the same family (vs H1 it wins Poisson, vs H2 it
wins both). Only residual gap is H1's Heat 0.0154 (H4 ~6.5× worse on Heat,
the only structural reason to still run the H3 hybrid). H3 (`fno_coreg_residual`
novel hybrid, COMBINE) demoted from "structural necessity" to **optional
upside test** — see [[cycle-002-strategy]] and [[patterns]]
§"Within-family F5 resolution".

**Cycle 002 H3 BUILD COMPLETE 2026-05-15.** Branch
`experiment/4-fno_coreg_residual` cut from master @ `198170f`, single commit
`0c46f43` adds new family directory `models/fno_coreg_residual/` (6 files,
+939/-0). Architecture is a **novel hybrid extension** — H2's MFRNP residual
stack with decoder-in-the-aggregation (`niu2024mfrnp`) as the base anchor,
plus H1's continuous-m basis-head (`li2022ifc`) on the HF residual with
basis-head last layer **zero-initialised** so the architecture **starts as
pure-H2 aggregator** at epoch 0. Pre-flight CPU smoke at `--epochs 2`:
`ifc_heat` 0.5708, `ifc_poisson` 0.3559 (loss-curve checkpoints, NOT target
performance — pre-optimization values with basis-head still at zero
contribution). Surface scope clean (all 6 files under
`models/fno_coreg_residual/**`); leakage scan = 7 documented
substring-collision false-positives (same precheck infra bug as cycles
001-002 H1/H2/H4). CEO PROCEED on Builder; Reviewer PASS/KEEP with all four
guard sub-checks clean; CEO ratified Reviewer PROCEED. Awaiting R4
(`cycle_eval.sh` on H3 branch — cache will MISS because new `models/`
directory; v9 cache hits). H3 only displaces H4 as project best if composite
**well below 0.077**. See [[factory_mffp-004-build]].

**Cycle 002: CLOSED 2026-05-15.** 2 new model families on disk (H4, H3).
H3 = NEW PROJECT BEST at composite 0.04420; first family in project history
to beat the paper composite geomean (0.0442 < 0.0516). F5
INVERSE_COMPLEMENTARY_FAMILIES resolved at the architectural level. Both
CEO KEEP; both auto-reverted by the same 4 precheck false-positives
(4 consecutive cycle overrides). Cycle-003 H5 pre-registered. See
[[cycle-002-summary]] for the full close-out.

**Cycle 001: CLOSED 2026-05-15.** 2 new model families on disk. Awaiting
human merge of `experiment/1-fno_coregionalization` and
`experiment/2-fno_mf_stack`. See [[cycle-001-summary]] for the full close-out.

## Goal

Invent new multi-fidelity field-prediction model families that beat published paper nRMSE numbers in `baselines/paper_baselines.json` on as many of the 17 benchmark datasets in `data/` as possible. The bar is the **paper numbers**, not v9. `references/v9_baseline/` is one worked example kept as reference only.

## Status

- **State**: **Cycle 003 CLOSED 2026-05-15 — FIRST GENUINE REVERT** (cycle-003 H1 `fno_coreg_residual_poisson_loss_reweighting`, composite_nRMSE regressed 0.04420 → 0.08472, +91.7% on the research target). Cycle 002 closed 2026-05-15 — H3 `fno_coreg_residual` remains NEW PROJECT BEST at composite 0.04420. 5 new model branches on disk (H1, H2, H4, H3, cycle-003 H1); H1+H2+H4+H3 all CEO-KEEP intent (auto-reverted by **precheck polarity bug + companion false-positives — 4 consecutive cycle overrides**); cycle-003 H1 CEO=REVERT (genuine research regression — first time CEO intent aligns with factory state). Awaiting human merge of `experiment/1-fno_coregionalization`, `experiment/2-fno_mf_stack`, `experiment/3-fno_mf_stack_v2_capacity_loss`, and `experiment/4-fno_coreg_residual`. Cycle 001 close-out: see [[cycle-001-summary]]. Cycle 002 close-out: see [[cycle-002-summary]]. Cycle-004 backlog: adaptive loss-weighting (GradNorm-lite / uncertainty-weighted), recipe-fingerprint checkpoint guard, re-verify the H3 baseline under a clean from-scratch run.
- **Current Score (best on disk)**: `composite_nRMSE = 0.04420` (**cycle-002 H3**, 200-epoch cuda; ~17 min train wall; 9.12M params). **Unchanged** by cycle-003 H1 (genuine REVERT — H1 regressed to 0.08472; project best preserved). Down from 1.6595 (v9 baseline) — **−97.3% / 37.5× improvement**. **First-ever crossing of the published paper composite geomean** (0.04420 < 0.05157, 0.86×) — status preserved despite the cycle-003 H1 regression.
- **Datasets beating paper**: **2 / 17** (`ifc_heat` via cycle-002 H3 at 0.0263, 2.81× margin; `ifc_heat` via cycle-001 H1 at 0.0154, 4.8× margin). `ifc_poisson` still unbeaten — cycle-002 H4 holds best at 0.0596 (1.66× over paper); cycle-002 H3 is 2.06× over (0.0742); cycle-003 H1 catastrophically regressed to 0.27287 (7.58× over). cycle-002 H3 remains the first family to beat the published paper composite geomean.
- **Experiments Run**: 5 complete. H1 `fno_coregionalization` (CEO KEEP, cycle 001). H2 `fno_mf_stack` (CEO KEEP, cycle 001). H4 `fno_mf_stack` v2 capacity+loss-bump (CEO KEEP, cycle 002). **H3 `fno_coreg_residual` novel hybrid** (CEO KEEP, cycle 002 — project best). **Cycle-003 H1 `fno_coreg_residual_poisson_loss_reweighting`** (CEO REVERT, cycle 003 — first genuine REVERT in project history; hypothesis refuted by data).
- **Kept (intent)**: 4 (H1, H2, H4, H3). **Reverted (intent)**: 1 (cycle-003 H1, first genuine REVERT). **Factory bookkeeping kept**: 0. **Factory bookkeeping reverted**: 5 (cycle-001 H1, H2 + cycle-002 H4, H3 + cycle-003 H1; the first 4 are precheck false-positive cascade with CEO=KEEP intent; the 5th is the first genuine REVERT where CEO=REVERT and factory state agree; see [[factory_mffp-001-experiment]], [[factory_mffp-002-experiment]], [[factory_mffp-003-experiment]], [[factory_mffp-004-outcome]], [[factory_mffp-005-experiment]]).

## Smoke-suite datasets (currently scored)

| dataset      | v9 test nRMSE | H1 test nRMSE     | H2 test nRMSE      | H4 test nRMSE       | **H3 test nRMSE**   | paper bar          | best vs paper                              |
|---           |---:           |---:               |---:                |---:                 |---:                  |---:                |---                                         |
| ifc_heat     | 0.14883       | **0.0154** (H1)    | 0.1275              | 0.0999               | **0.02634** (H3)    | 0.074 (IFC-ODE2)   | **H1 beats by 4.8×, H3 beats by 2.81×** ✓ |
| ifc_poisson  | 18.50344      | 0.7725             | 0.0979              | **0.0596** (H4)      | 0.07416              | 0.036 (IFC-ODE2)   | H4 1.66× over paper (best); H3 2.06× over  |

Composite (geomean):
- v9: √(0.14883 · 18.50344) = **1.6595**
- H1: √(0.0154 · 0.7725) = **0.10919** (**−93.4% vs v9**)
- H2: √(0.1275 · 0.0979) = **0.11173** (**−93.3% vs v9**, +2.3% vs H1)
- H4: √(0.0999 · 0.0596) = **0.07719** (**−95.3% vs v9**, **−31% vs cycle-001 best**)
- **H3: √(0.02634 · 0.07416) = 0.04420** (**−97.3% vs v9**, **−43% vs H4**, **0.86× paper geomean 0.0516 — FIRST CROSSING**)

**F5 architecturally resolved**: H3 composes H1's basis-head (Heat
inductive bias) with H2's MFRNP residual stack (Poisson inductive
bias) into a single network. Heat surges to 0.0263 (beats paper 2.81×;
74% improvement over H4); Poisson stays at 0.0742 (close to H2-family
levels; -25% vs H4 because H4's Poisson loss-weighting was not ported).
The composition pattern is recorded as a reusable recipe in
[[patterns]] §"F5 architectural resolution".

## Cycle 001 plan

- **F1**: `ifc_poisson` val→test value-scale collapse — 95% of composite penalty. Root cause: y-scale collapses ~40× from L1 (8×8) to L4 (64×64); v9 has no continuous fidelity index. → [[cycle-001-failure-diagnosis]].
- **F2**: `ifc_heat` backbone gap (~2× worse than IFC-ODE2). Pure inductive-bias issue — Transolver wrong for regular-grid PDE.
- **F3**: Missing paper numbers in `baselines/paper_baselines.json` (meta-blocker). Human action required → [[paper-baselines-proposals]].

**Approved hypotheses (2 / 2 budget) — CEO PLAN APPROVED 2026-05-15:** → [[cycle-001-strategy]]

1. **H1: `fno_coregionalization`** — FNO backbone + IFC-style continuous-m basis B(m)=MLP([m,m²]). K=10 latent. Files at `models/fno_coregionalization/`. Backlog L27. ~1-3 min smoke. Inspirations: [[li2022ifc]], [[li2020fno]].
2. **H2: `fno_mf_stack`** — 4 FNOs (one per fidelity) + MFRNP-style residual stack with decoder-in-aggregation. Files at `models/fno_mf_stack/`. Backlog L26. ~3-5 min smoke. Inspirations: [[niu2024mfrnp]], [[li2020fno]].

Both tagged `Type: code`, growth dimension `capability_surface`. **Execution: sequential** (research-mode protocol R3; no parallel). `--no-github` is set — no PR/issue creation.

**Shared hygiene (both picks, mandatory)**:
- Per-fidelity output normalization `y / scaler[m]` (Researcher: alone projected to drop ifc_poisson 18.5 → ~1.0).
- `val_frac` 0.2 → 0.1 (preserve 4–5 of 5 HF training samples).
- Continuous fidelity index encoded explicitly (continuous `m` from `cat.pkl` `t_list`).

**Quantitative targets** (geomean composite): conservative `composite_nRMSE ≤ 0.25`, stretch `≤ 0.10` (from baseline 1.6595).
- `ifc_poisson`: 18.50 → ≤ 0.5 conservative, 0.05–0.15 stretch (paper bar 0.036).
- `ifc_heat`: 0.149 → ≤ 0.10 conservative (paper bar 0.074).

**HARD GATE checks (all PASS):** surface, leakage (risk=none both), config validation (VALID), hypothesis count = 2, growth tag, backlog tags (L27 + L26), type=code. → [[cycle-001-strategy]].

**Anti-patterns recorded:** no global prior MLP without continuous m; no val_frac=0.2; no Transolver on regular grid; no full IFC neural ODE at smoke; no skipping per-fidelity output normalization. → [[cycle-001-strategy]].

→ [[cycle-001-candidate-ranking]], [[cycle-001-cross-cutting-findings]].

## Constraints (from config.json)

- **Mutable surface**: `models/**` only.
- **Fixed surfaces**: `data/**`, `baselines/**`, `eval/**`, `references/**`, `factory.md`, `README.md`, `scripts/**`.
- **Hypothesis budget**: `max_new = 2`, `min_growth = 1`.
- **Smoke budget**: ~30 min H100 per cycle.
- **Contract**: every new family must satisfy `eval/MODEL_CONTRACT.md` (manifest.json + smoke_eval.py).

## Human-side TODOs (non-blocking for cycle 001)

- Create `papers_summary.csv` at repo root (referenced by `factory.md`, `models/README.md`, `HOWTO.md`, but file does not exist). → [[papers-summary-csv-state]].
- Append IFC paper numbers to `baselines/paper_baselines.json` for `ifc_heat`/`ifc_poisson`. → [[paper-baselines-proposals]].

## Recent activity

- **2026-06-02** — **Cycle 008 H1 R4 + R5 Evaluator complete; CEO KEEP; NEW REPRODUCIBLE PROJECT BEST.** Branch `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` PRESERVED as cycle-009 entry baseline. `bash scripts/cycle_eval.sh` ran to PASS in 315 s total (heat 169.91 s + poisson 144.75 s) — ~79% under the 25-min smoke kill-switch cap; SLURM H100 ran ~3× faster than the pre-flight 14-15 min projection (Slurm-side dataset-load dominated). **Composite_nRMSE 0.030408 → 0.027729 (−8.81%).** Per family-of-interest: `fno_coregionalization × ifc_heat` **0.01551 → 0.012898 (−16.84%)** — `fno_coregionalization` now sole holder of the heat leaderboard at >2× margin over the second-place family (`fno_coreg_residual @ 0.026277`); `fno_coregionalization × ifc_poisson` 0.7501 → **0.5945 (−20.75%)** — same-family improvement, composite-neutral (`fno_mf_stack @ 0.05961` still owns poisson). Both `fno_coregionalization` cells cache MISS (expected — `__code_hash__` change); other 12 cells cache HIT. **Heat kill-switch (≤ 0.0194) NOT tripped** — 0.012898 sits at 33.5% headroom under threshold. **Both hard component targets MET**: composite ≤ 0.028 ✅ AND heat ≤ 0.013 ✅. **Bar miss**: parallel-bench `mf_fno_transfer_bar @ 0.027429` short by +0.000300 (+1.09%) — **89.93% of bar gap closed by capacity-axis alone**. The aspirational `composite ≤ 0.027429` (dethrone the bar) NOT met by the +0.0003 hair; the next +1.09% must come from elsewhere (most likely `ifc_poisson` — composite is geomean, so closing the family's poisson gap from 0.5945 toward `fno_mf_stack`'s 0.05961 would matter at composite log-weight). **Heat leaderboard ranking** (new project state): 1. fno_coregionalization 0.012898, 2. fno_coreg_residual 0.026277 (2.04×), 3. mf_fno_transfer_bar 0.033175 (2.57×), 4. fno_mf_stack 0.099945 (7.75×), 5. transolver_residual 0.114559, 6. v9_baseline 0.148834, 7. transolver_attention_fusion 0.149230. **Factory `finalize` recorded `revert` again** due to the same precheck infrastructure pattern: (1) `score_direction` polarity bug flips −8.81% improvement to +8.81% "regression" on lower-is-better metric (9-for-9 streak project-wide); (2) `scope` empty-detail / short-SHA mismatch false positive vs independent verification clean against full SHA `1249f2d`; (3) `fixed_surfaces` empty-detail false positive vs independent diff-read clean (1 file under `models/fno_coregionalization/`, no fixed-surface touches). **All real checks PASS**: `ground_truth_leakage` (flagged=false, risk=none — first hypothesis with clean leakage at BOTH the Strategist R2 hypothesis-level AND the actual Builder diff-level), `anti_pattern`, `smoke_test`, and independent `scope`/`fixed_surfaces` re-runs. **Verdict tagged `revert_bookkeeping_keep_intent` — 5th consecutive in cycle-007/008 (7th project-wide); 5th consecutive operator-action request for precheck overhaul** (out of factory scope). **CEO override applied** — branch and code preserved on disk. **All six cycle-008 anti-patterns satisfied**: #1 MFRNP loss-recipe BANNED (no reweighting), #2 per-dataset MFRNP dispatch BANNED (no `_DATASET_RECIPES`), #3 H1/H2/H3 bundling FORBIDDEN (H1 standalone), #4 D1 `mf_fno_transfer_bar` smoke-config bump DEFERRED, #5 A3 F-FNO factorized refactor DEFERRED, #6 `model.py` edit FORBIDDEN (byte-identical to `1249f2d`). **NEW REPRODUCIBLE PROJECT BEST**: composite **0.027729** (prior cycle-007 H1 reproducible 0.030408; cycle-005 H2 aspirational 0.029357 remains NOT reproducible reference only). **Cycle-009 entry baseline**: `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6`. Chain is now `be36cba` (c005 H2 schedule) ← `1249f2d` (c007 H1 constructor fix) ← `18d83a6` (c008 H1 paper capacity). **Pattern note**: paper-config wire-up on a freshly-repaired constructor delivered the dominant composite lever EXACTLY as predicted by cycle-008 failure_analysis (`CAPACITY_PARETO` on `fno_coregionalization × ifc_heat`, 12.6× composite log-weight). The fix-then-bump pattern (c007 H1 repaired the signature; c008 H1 wired the paper values through the repair) is a clean two-cycle decomposition separating structural enabler from science lever. Capacity-axis was the right call; the cycle-008-banned recipe-axis was correctly avoided. **First hypothesis in project history to land both hard component targets in the same R4** (composite ≤ 0.028 ✅ AND heat ≤ 0.013 ✅). → [[cycle-008-exp-11]].
- **2026-06-02** — **Cycle 008 H1 Builder complete; CEO PROCEED.** Branch `experiment/11-fno_coregionalization-paper-capacity` cut from cycle-007 H1 baseline `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d` (the cycle-008 entry baseline @ composite 0.030408). Single commit `18d83a6` = paper-config capacity bump on `fno_coregionalization` SMOKE_DEFAULTS — `hidden_channels 32→128`, `K 10→20`, `n_blocks 4→6`, `modes_cap 12→16`, plus NEW `b_hidden=128` key + one-line plumbing `b_hidden=p["b_hidden"]` at the `FNOCoregionalization(...)` call site so the new key actually reaches the constructor. All five values mirror `models/fno_coregionalization/full_config.json` (li2022ifc paper config). +10/-4 across 1 file all under `models/fno_coregionalization/`. **`model.py` byte-identical to `1249f2d`** per cycle-008 anti-pattern #6 (Strategist R2 explicit clause: cycle-007 H1's repaired anisotropic-modes constructor already accepts all paper kwargs — `K`, `hidden_channels`, `n_blocks`, `modes_h`/`modes_w`, `grid`, `b_hidden`; no constructor signature work needed). **H2 LF→HF schedule preserved verbatim** — `pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25` byte-identical to `1249f2d`; the capacity bump composes on top of the already-banked schedule (no architectural or schedule edits). `manifest.json`, `INSPIRATION.md`, `full_config.json` all UNTOUCHED. **Pre-flight smoke verification PASS** — Builder ran `--epochs 2 --dataset_dir data/ifc_heat --out /tmp/h1_smoke_check.json --ckpt_dir /tmp/h1_ckpt_check --seed 0` on the H100; result `train_seconds=4.31` (~2.15 s/epoch), `params=50,471,592` (50.47M — sanity-consistent with K=20/hidden=128/n_blocks=6/b_hidden=128, the right order of magnitude), `peak_mem=1.73 GB`. **200-epoch projection ≈ 7 min/cell × 2 cells ≈ 14-15 min total**, comfortably under the 25-min smoke kill-switch cap by ~40% margin; kept `epochs=200` and no warmup change needed (Strategist R2 conditional "drop epochs 200 → 120 with cosine warmup if smoke wall > 25 min on first SLURM run" NOT triggered). **Surface guard `factory guard --baseline 1249f2d --check-scope` clean** — 1 file changed; no fixed-surface modifications; sibling families (`fno_mf_stack`, `fno_coreg_residual`, `mf_fno_transfer_bar`, transolver*) untouched. **Leakage scan `flagged: false, risk_level: none` on BOTH the Strategist R2 hypothesis declaration AND the actual Builder diff** — first hypothesis in project history to clear leakage on both passes (cycles 001-007 all tripped substring-collision false positives on `factory.md` / `README.md` / `manifest.json` shared vocabulary or `_DATASET_RECIPES` public-API dispatch keys; the H1 paper-knob-value bump avoids both classes). **Surface modifications outside hypothesis-declared scope: ONE** — the `b_hidden=p["b_hidden"]` kwarg at the `FNOCoregionalization(...)` call site is technically a second line touched beyond the `SMOKE_DEFAULTS` block, but it is strictly-necessary plumbing (without it the new `b_hidden` key would be dead and silently fall back to constructor default 64), it is in the same file already declared mutable, it is one line, and it mirrors the cycle-007 H1 line-discipline precedent (where `K`, `hidden`, `n_blocks` kwargs were similarly plumbed through). CEO approved as inside-the-hypothesis scope. **All six cycle-008 anti-patterns satisfied**: #1 MFRNP loss-recipe BANNED (no reweighting), #2 per-dataset MFRNP dispatch BANNED (no `_DATASET_RECIPES`), #3 H1/H2/H3 bundling FORBIDDEN (H1 on its own branch, single-file, single-family), #4 D1 `mf_fno_transfer_bar` smoke-config bump DEFERRED (not touched), #5 A3 F-FNO factorized spectral conv refactor DEFERRED (not touched), #6 `model.py` edit FORBIDDEN (byte-identical to `1249f2d`). **`--no-github` honored** — no `gh` calls, no `git push`, no PR, no issue. **CEO PROCEED to R3-review** — instructions issued to run `factory guard . --baseline 1249f2d --check-scope`, verify smoke result plausibility (50.47M params in the right order of magnitude), read the +10/-4 1-file diff, print PASS/FAIL. **R4 acceptance** (Strategist R2): `ifc_heat` ≤ 0.013 AND composite ≤ 0.028 → strong KEEP; even low-end composite ~0.029 with heat < 0.01551 is a meaningful smoke-leaderboard KEEP. **R4 kill-switches**: `ifc_heat > 0.0194` → REVERT (the +25% band over 0.01551 reproducible baseline); wall > 25 min → drop epochs 200 → 120. Cache MISS expected on BOTH `fno_coregionalization × ifc_heat` AND `fno_coregionalization × ifc_poisson` at R4 (`__code_hash__` change); other 12 cells cache-hit. → [[cycle-008-exp-11-build]].
- **2026-06-02** — **Cycle 005 H2 Builder complete; CEO PROCEED.** Branch `experiment/7-fno_coreg_lf_hf_transfer` cut from `experiment/6-mf_fno_transfer_bar-repo-root-fix` (NOT `main`) — first downstream-branching off a `revert_bookkeeping_keep_intent` preserved branch in project history; H2 inherits H1's REPO_ROOT fix so the bar appears on the smoke leaderboard for direct post-H2 comparison. Single commit `be36cba`: `feat(fno_coregionalization): two-stage LF→HF transfer schedule (H2)` — converts the single-stage joint training in `models/fno_coregionalization/smoke_eval.py` to a two-stage LF→HF transfer-learning schedule mirroring the `mf_fno_transfer_bar` recipe (verbatim `pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25`) while keeping the K=10 coregionalization head and per-fidelity scalers intact. Two-stage outer loop: `n_warmup = round(pretrain_frac * args.epochs)` epochs of LF-only training (Subset filtered on `m != hf_m`, fresh `Adam` lr=1e-3, fresh `CosineAnnealingLR(T_max=n_warmup)`), then `args.epochs - n_warmup` epochs of joint LF+HF training (fresh `Adam` lr=3e-4, fresh `CosineAnnealingLR`). Stage-1 optimizer/scheduler state deliberately discarded at the boundary; `model.set_scalers(...)` called once before Stage 1 from the full training subset; same model object across stages; basis stays trainable in Stage 1 (LF m-values supervise the K=10 weights). `last.pt` schema gains a `stage ∈ {1,2}` field; resume guard requires `stage == 2 AND epoch == epochs_target` (stage-1-only checkpoints do NOT satisfy the guard). INSPIRATION.md +12 lines citing `lyu2023mffno` (LF→HF transfer recipe) on top of `li2022ifc` (coregionalization basis, unchanged in H2). **Architecture UNCHANGED** — no edits to `model.py`, `data.py`, `manifest.json`, or `full_config.json`. +398/-75 across 2 files all under `models/fno_coregionalization/` (the 457-line smoke_eval.py change reflects the two-stage refactor on top of the existing `data_adapters`-integrated version — most additions are the LF-filter helper, the stage-conditional outer loop, the extended checkpoint schema, and stage logging). **Pre-flight (`--epochs 4` — the right setting to exercise both stages; `--epochs 2` with `pretrain_frac=0.25` gives `n_warmup=0` and skips Stage 1) PASSED end-to-end on `data/ifc_heat`**: Stage 1 (1 epoch LF-only on 153 LF samples filtered from full 157-sample train, lr=1e-3) → Stage 2 (3 epochs joint on full 157-sample train, lr=3e-4); val_nRMSE 0.171 → 0.118 in 4 epochs (sane direction for a smoke check; the test of correctness is that both stages run end-to-end and the resume guard works, NOT that the 4-epoch number predicts the 200-epoch outcome). **Resume guard verified** by re-running with the same `ckpt_dir`: harness printed `[resume] finished checkpoint (stage 2, epoch 4)` and skipped retraining. **All 9 acceptance criteria addressed** (two-stage outer loop with correct `n_warmup` formula; fresh opt+sched per stage; LF-only Subset on `m != hf_m`; `stage` field + correct resume guard; `set_scalers` once before Stage 1; pre-flight end-to-end on ifc_heat; INSPIRATION.md citations; no architectural edits; no edits outside `models/fno_coregionalization/`). **Surface CLEAN** (2 files both under `models/fno_coregionalization/` ⊂ `mutable_surfaces: models/**`; zero touches to fixed surfaces or sibling families). **Leakage scan flagged HIGH with 3 findings — all known substring-collision false positives**: `"satisfy"` matched against the code comment "a stage-1-only checkpoint MUST not satisfy this guard" (internal invariant note about the resume guard); `"dataset"` matched twice against `--dataset_dir`/`--dataset_name` CLI argument names in `factory.md` and `README.md` (CLI flag names per `eval/MODEL_CONTRACT.md`, not ground-truth values). None originate under `data/**`. Same precheck-substring-collision pattern that triggered the 5 prior overrides + cycle-005 H1; H2 introduces only 3 false positives (vs H1's 5) because `manifest.json` is not edited. **No anti-pattern violations** — verified by direct inspection: did NOT create a new family, did NOT freeze the K=10 basis in Stage 1, did NOT share opt/sched state across the boundary, did NOT lower epochs, did NOT add per-stage rescaling, did NOT pursue H3, did NOT bundle H2 with other edits. **Pre-existing 15-file working-tree dirt unchanged from H1** — same `factory.md`, `models/*/manifest.json`, `models/*/model.py`, `models/*/smoke_eval.py`, `references/v9_baseline/smoke_eval.py` modifications that were present at H1 R4; the post-H2 R4 eval will be apples-to-apples consistent with H1's. This dirty state will trigger the same `scope`/`fixed_surfaces` precheck failures at R5 — expect `revert_bookkeeping_keep_intent` again unless the metric improves dramatically. **First training-schedule-only hypothesis in project history** — cycles 001-003 all changed architecture (new families or new model features), cycle-005 H1 was a 1-line path fix, cycle-005 H2 is the first time a hypothesis edits only the training schedule (optimizer / scheduler / data subset / outer-loop structure) without touching `model.py` or `manifest.json`. If H2 KEEPs, it validates "training-schedule edits as a research lever" as a cheap (no architectural search) family of cycle hypotheses. **CEO PROCEED to R4** — `cycle_eval.sh` cache will MISS on `fno_coregionalization` (new code_hash from the 457-line edit); expect a SLURM submit + wait. **R5 acceptance** (cycle-005 strategy original spec): `ifc_heat` ≤ 0.013, composite ≤ 0.026 (beating bar parallel-bench 0.02743). **R5 acceptance** (smoke-harness-realistic per H1 calibration finding): composite ≤ ~0.05 to surpass the bar's smoke score (0.05258); composite ≤ 0.0337 to dethrone the cycle-005 project composite leader (currently itself, `fno_coregionalization` from R0). Even composite to 0.028–0.032 would be a meaningful KEEP for the smoke leaderboard for this family. → [[factory_mffp-007]].
- **2026-06-02** — **Cycle 005 H1 Builder complete; CEO PROCEED.** Branch `experiment/6-mf_fno_transfer_bar-repo-root-fix` cut from `bench/all-fno-families`. **Two-commit split**: `a415e26` = the literal 1-line REPO_ROOT fix in `models/mf_fno_transfer_bar/smoke_eval.py:32` (`HERE.parent.parent.parent` → `HERE.parent.parent` — old walk landed in `/orcd/data/faez/001/nick/mf_field/` which has no `data_adapters/`; new walk lands in the project root that owns `data_adapters/`); `17e5234` = supporting `model.py` + `manifest.json` follow-up because both files existed in the working tree but were never committed on the base branch (without them the H1 fix is not reproducible from a fresh checkout). 321 insertions / 0 deletions across 3 files, all under `models/mf_fno_transfer_bar/**`. Strategist's "1 line; no other edits" instruction assumed `smoke_eval.py` was already tracked; it wasn't, so the +1/-1 diff stat could not literally appear — Strategist modeling miss flagged for future planning accuracy, not a Builder violation. **Pre-flight 2-epoch CPU smoke on ifc_heat PASS** — no `ModuleNotFoundError`, both LF pretrain → HF fine-tune stages of the bar's own training schedule executed end-to-end. **Surface guard CLEAN** (3 files all under `models/mf_fno_transfer_bar/` ⊂ `mutable_surfaces: models/**`; zero touches to fixed surfaces or sibling families). **Leakage scan flagged HIGH with 5 findings — all known substring-collision false positives**: `"modify"` matched `factory.md` sacred-rule text ("Do not modify or delete"); `"loader"` matched a debug log line `print(f"... loader={train['loader']} ...")`; `"description"` / `"ifc_raw"` / `"frozen"` matched standard JSON schema fields in `manifest.json` (plus `"frozen"` also matched README.md). None originate under `data/**`; the H1 change literally only edited one path-resolution line and cannot encode any ground-truth value. Same precheck-infrastructure substring-collision pattern that triggered the 5 prior overrides. **Notable contrast with strategy-phase leakage projection**: strategy recorded `flagged: false, risk_level: none, findings: []` on both H1 and H2 (projected to be the first cycle without substring-collision false-positives); Build phase reintroduced the failure mode by newly tracking `manifest.json` (containing `description`/`ifc_raw`/`frozen` schema fields). Documents that precheck-substring-collision risk depends on what gets committed, not just on the science edit. **CEO PROCEED to R4** — `cycle_eval.sh` cache will MISS on `models/mf_fno_transfer_bar/` (new code_hash from both commits). **R5 acceptance**: `mf_fno_transfer_bar` appears in `results/smoke_latest.json` with `composite_nRMSE ∈ [0.025, 0.030]`, matching the parallel benchmark pipeline's ~0.0274. **Do NOT merge H1 yet** — H2 (`fno_coregionalization` LF→HF transfer pretraining) must branch off post-H1-merge to inherit the fix in its eval environment. **First Builder commit-split in project history** — cycles 001-003 all had single-commit Builder outputs; cycle-005 H1 is the first time the Builder needed two commits (mechanism + bookkeeping) to satisfy both literal-mechanism attribution and reproducibility. → [[factory_mffp-006]].
- **2026-06-02** — **Cycle 005 Strategist complete; CEO PLAN APPROVED (HARD GATE).** Two hypotheses in `.factory/strategy/current.md`, both with line-of-code-level specifications. **H1 = 1-line REPO_ROOT fix in `models/mf_fno_transfer_bar/smoke_eval.py:32`** (FIX, prerequisite — unblocks in-distribution bar comparison; current `.parent.parent.parent` walks one directory too far up to `mf_field/` → `ModuleNotFoundError: No module named 'data_adapters'`; SLURM job 15313689 confirmed). **H2 = LF→HF 2-stage transfer-learning pretraining for `fno_coregionalization`** (EXPLOIT, main growth bet — absorbs the bar's transfer mechanism into the cycle-005 R0 winner on ifc_heat). H2 recipe verbatim from `mf_fno_transfer_bar/smoke_eval.py`: `pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25`; `n_warmup = round(pretrain_frac * args.epochs)` LF-only Stage 1 + remaining-epoch HF+LF Stage 2; fresh `Adam` + fresh `CosineAnnealingLR` at the stage boundary; same `model` object; `set_scalers` once before Stage 1; `last.pt` gains `stage ∈ {1,2}` field with `stage == 2 AND epoch == epochs_target` resume guard. Architecture unchanged (no `model.py`/`data.py`/`manifest.json`/`full_config.json` edits). **Surface check + leakage scan BOTH CLEAN** — `flagged: false, risk_level: none, findings: []` on both H1 and H2. **First cycle without substring-collision false-positives** (cycles 001/002/003 all tripped on `"poisson"` or `"001"`); cycle-005 hypotheses avoid those failure modes by design. **Branch base plan: H1 first** (1-line prerequisite, branch from `bench/all-fno-families`), **H2 second** (branch from post-H1-merge target so H1's fix is included in H2's eval environment); NOT parallel. **Cycle-005 R0** composite_nRMSE = 0.033726 (24% better than cycle-004's 0.04415); bar `mf_fno_transfer_bar` ≈ 0.0274. **Dominant gap is ifc_heat** (winner `fno_coregionalization` at 0.0205 vs bar 0.0128 — 1.6× gap, n=128, zero >2×-median outliers → distribution-shift problem, not outlier-catching). **Expected H2 impact:** ifc_heat ≤ 0.013, composite ≤ 0.026 (beats bar ~0.0274). H3 (modes/uncertainty) deferred per `research.md` §5 because ifc_poisson is already ≈ bar (0.0556 vs 0.0587). **Systemic agent-wrapper-timeout caveat tracked**: Researcher and failure_analyst wrappers timed out twice this cycle (systemic infra issue); CEO synthesized substitutes from direct source reads. If Builder exhibits the same pattern, retry once with `--timeout 1800` then escalate to operator — do NOT attempt CEO-direct edits. **7-item anti-pattern catalog binding** (do not create a new family; do not freeze the K=10 basis during Stage 1; do not share opt/sched state across the stage boundary; do not lower epochs; do not add per-stage rescaling; do not pursue H3; do not bundle H1 with other edits). → [[cycle-005-strategy]].
- **2026-05-15** — **Cycle 003 H1 R4 + R5 Evaluator complete; CEO REVERT — FIRST GENUINE REVERT in project history.** Branch `experiment/5-fno_coreg_residual_poisson_lossweight` commit `a0d932b`. Clean from-scratch SLURM job 13974837 (200 epochs cuda, `train_seconds=549.15s` on poisson) after the contaminated job 13973868 was diagnosed and resolved (poisson resumed from a partial CPU pre-train checkpoint — see contamination handling below). **Composite_nRMSE 0.04420 → 0.08472 (+91.7% REGRESSION on the research target).** Per dataset: `ifc_heat` **0.02630** (unchanged from cycle-003 entry 0.02634 within seed noise — uniform-weight Heat path is benign by construction; still **BEATS paper 0.074 by 2.81×**); `ifc_poisson` **0.27287** (3.68× WORSE than cycle-003 entry 0.07416; 4.58× WORSE than cycle-002 H4 0.05961 on the simpler `fno_mf_stack` backbone; 7.58× over paper 0.036). Val/test gap on H1+poisson `best_val_nRMSE=0.0783` vs `test=0.27287` suggests the asymmetric weights overconcentrate gradient budget on a narrow HF feature set that overfits while starving the LF supervision that H3's coregionalization stack depends on. **Cycle-003 framing REFUTED**: the MFRNP Poisson5 (2.0, 0.25) recipe is **backbone-coupled**, NOT "PDE-class-bound" — it helps `fno_mf_stack` (H4) but catastrophically harms `fno_coreg_residual` (H1). Same recipe, same PDE-class, same data — opposite outcome under different MF-aggregation backbones. **FIRST genuine REVERT in project history**: unlike cycles 001/002 H1/H2/H4/H3 (all CEO=KEEP, factory=REVERT via 4 precheck infrastructure bugs), cycle-003 H1 is the first REVERT where CEO intent and factory state agree, and the underlying reason is a genuine research-target regression. **Contamination handling (operationally resolved; underlying factory bug remains)**: first SLURM job 13973868 resumed poisson from a partial CPU pre-train checkpoint left over from an earlier 1800s cache-only local pass that timed out and saved `last.pt` at the last 10% epoch milestone (poisson `train_seconds=33.31s` vs heat's 461s on similar-shape data). CEO moved the contaminated checkpoints to `.factory/research/runs/cycle-003-H1/contaminated_checkpoints/`, deleted the stale cache file, and submitted fresh SLURM job 13974837 from an empty ifc_poisson checkpoint dir. Clean (0.27287) and contaminated (0.27259) results matched to within 0.10% — verdict robust either way. **Underlying factory bug**: the checkpoint-resume guard (`epoch == epochs_target` AND `cond_dim` match, ignoring recipe changes) is systemic — the cycle-002 H3 project-best baseline (0.04420) was almost certainly also checkpoint-contaminated to some unknown but likely smaller degree (its `fno_coreg_residual_train_seconds: ifc_poisson: 25.0` is implausibly fast for 200 epochs). Two cycle-004 backlog items filed: (a) recipe-fingerprint checkpoint guard, (b) re-verify cycle-002 H3 baseline under a clean from-scratch run as a cycle-004 prerequisite. **Project best preserved**: cycle-002 H3 at 0.04420 on `experiment/4-fno_coreg_residual @ 0c46f43` remains the project best; cycle-003 closes with no new best. **Cycle-004 implications pre-registered**: drop the static-recipe framing; loss-weighting on H3 must be adaptive (GradNorm-lite / uncertainty-weighted) or gentler asymmetric (e.g. (1.5, 0.5)) per-backbone-tuned. New patterns entry pinned: "MFRNP per-fidelity loss-weighting recipes are backbone-coupled across MF aggregation architectures" — bounds the cycle-002 H4 finding that "MFRNP recipes port across architectures" to within the residual-stack-on-FNO family but not across to the hybrid basis-head + MFRNP-residual-stack family. → [[factory_mffp-005-experiment]], [[patterns]].
- **2026-05-15** — **Cycle 003 H1 Builder complete; CEO PROCEED.** Branch `experiment/5-fno_coreg_residual_poisson_lossweight` cut from `experiment/4-fno_coreg_residual` (cycle-002 H3 @ `0c46f43`, project best 0.0442). Single commit `a0d932b`: 67 insertions / 5 deletions across `models/fno_coreg_residual/{smoke_eval.py, INSPIRATION.md}`. Strict additive single-knob — ports H4's `resolve_fidelity_weights(dataset_name, p)` helper into H3's smoke pipeline; SMOKE_DEFAULTS adds `poisson_hf_weight=2.0` / `poisson_lf_weight=0.25` (verbatim MFRNP `Poisson5_config.yaml` values, same numbers H4 used to recover Poisson to 0.0596); `compute_losses` signature extended with `hf_fid_weight` / `lf_fid_weight` kwargs and the kwargs multiply both LF terms (LF block) AND the HF residual + aggregator anchor (HF block) per the working implementation in `compute_losses`. Resolver called once at top of `run()`'s training loop, returns `(2.0, 0.25)` iff `"poisson" in dataset_name.lower()` else `(1.0, 1.0)`, active pair logged via `[loss-weights]` debug line. Pre-flight 2-epoch CPU smoke on both target datasets PASS: `ifc_heat` resolved `(1.0, 1.0)` (uniform — Heat path unchanged by construction, anti-pattern "do NOT activate the Poisson loss override on Heat" satisfied), `ifc_poisson` resolved `(2.0, 0.25)` (MFRNP Poisson5 activation that targets F6); both contract JSONs include `metric_value`. **Surface guard** `factory guard --baseline 0c46f43af50bbc58651fbab4fd425c5440788b89 --check-scope` → `clean`. Note: passing the baseline as a branch ref `experiment/4-fno_coreg_residual` tripped a "Branch is not rooted at baseline" guard-tool bug despite merge-base equalling tip; explicit SHA resolves cleanly — filed as factory-infrastructure observation, NOT a code violation. **Leakage scan** on the diff = 2 findings, both known substring-collision false positives (`"poisson"` is the dataset name as published in MFRNP Poisson5 config; `"001"` is the filesystem path component `/orcd/data/faez/001/...` and the `cycle-001`/`cycle-003` references in INSPIRATION.md). Same precheck-infrastructure substring-collision pattern that triggered the 4 prior cycle overrides. **Builder design choice (CEO-acknowledged, non-blocking)**: aggregator anchor term is multiplied by `hf_fid_weight` (=2.0 on Poisson) alongside the HF residual, because H3 has an `agg_anchor_weight=0.5` regulariser keeping the MFRNP aggregator's LF baseline meaningful — H4 (the resolver's origin family) has no anchor. Net effect on Poisson is a slightly more aggressive HF/LF gradient ratio than H4's pure 8:1; defensible (anchor is an HF-supervision-block element) but may help further with H3's hidden=64 basis-head capacity or may over-correct — R4 eval reveals which. INSPIRATION.md cycle-003 paragraph cites `mfrnp_poisson5_config` (primary provenance — NOT in MFRNP paper, published only in YAML config), `boulle2023ellipticdata` (theoretical grounding for elliptic-PDE LF down-weighting), `chen2018gradnorm` (theoretical context for the cycle-004 GradNorm-lite candidate; no code ported). **CEO PROCEED to R4** — `cycle_eval.sh` cache will MISS on `models/fno_coreg_residual/` (new code_hash). R5 monotonic check: H1 displaces H3 as project best iff composite < 0.04420; floor at exact H4-Poisson parity gives `geomean(0.02634, 0.0596) ≈ 0.0396`. → [[factory_mffp-005-build]].
- **2026-05-15** — **Cycle 002 H3 R4 Evaluator complete; CEO KEEP — NEW PROJECT BEST.** Branch `experiment/4-fno_coreg_residual` commit `0c46f43`. `bash scripts/cycle_eval.sh` ran to completion on cuda (~17 min train wall; sbatch wall 4844 s ~80 min including queue). **Composite_nRMSE 1.6595 → 0.04420** (**−97.3% vs project state, 37.5× improvement; −43% vs cycle-002 H4 0.07719**). Per dataset: `ifc_heat` **0.02634** (**beats paper bar 0.074 by 2.81×** — first family in project history to do so), `ifc_poisson` **0.07416** (2.06× over paper 0.036; -25% regression vs H4 0.0596 because H4's Poisson-specific HF=2/LF=0.25 loss reweighting was not ported). **FIRST family in project history to beat the paper composite geomean** (0.0442 < 0.0516, 0.86×). 9.12M params. Hypothesis hit the strategist's predicted ~0.04 target spot-on — the basis-head + MFRNP residual stack hybrid composes both family inductive biases as predicted. **F5 INVERSE_COMPLEMENTARY_FAMILIES resolved at the architectural level**: H1's continuous-m basis head (li2022ifc) unlocks Heat smoothness while H2's MFRNP aggregator (niu2024mfrnp) preserves the Poisson stiff-HF correction direction. Basis-head zero-init worked exactly as designed — architecture started as pure-H2 aggregator at epoch 0 and optimization grew the Heat-dominant basis residual. **Factory `finalize` recorded `revert` due to the same 4 precheck false positives** as H1+H2+H4 R4 (score_direction polarity bug — this is the largest delta yet -1.6153; empty-detail scope/fixed_surfaces; ground_truth_leakage substring-collision on contract-required tokens `ifc_raw`/`ifc_heat`/`ifc_poisson` and JSON keys `description`/`frozen`) — **4th consecutive cycle override; bug pattern fully reproducible**; CEO override applied; **branch and code preserved intact** for human merge. **Cycle-003 H5 pre-registered (highest-EV next move)**: port H4's Poisson-specific HF=2/LF=0.25 loss reweighting into H3's architecture. Predicted composite ~0.035-0.040; likely first crossing of the published `ifc_poisson` paper bar. New patterns pinned: (a) F5 architectural resolution recipe (compose orthogonal inductive biases as basis-head + MFRNP residual stack with zero-init safety); (b) precheck polarity bug now load-bearing at 4-of-4 cycle overrides. → [[factory_mffp-004-outcome]], [[patterns]].
- **2026-05-15** — **Cycle 002 H4 R4 Evaluator complete; CEO KEEP.** Branch `experiment/3-fno_mf_stack_v2_capacity_loss` commit `ddd221d`. `bash scripts/cycle_eval.sh` ran to completion on CPU (~28 min wall, EXIT=0); `results/smoke_latest.json` fully populated. **Composite_nRMSE 1.6595 → 0.07719** (−95.3% vs project state, **21.5× improvement; 31% better than cycle-001 H2 0.11173**). Per dataset: `ifc_heat` **0.0999** (1.35× over paper; 22% recovery from H2 0.1275), `ifc_poisson` **0.0596** (1.66× over paper; 39% improvement from H2 0.0979). 2.28M params. **Both pre-registered MFRNP Poisson5 knobs validated independently**: Knob 1 (capacity bump `hidden 16→32, modes (4,5,5,5)→(4,8,12,12), blocks 2→3`) drove the Heat recovery (Knob 2 gating-off on Heat); Knob 2 (Poisson-only HF=2.0/LF=0.25 loss weighting) drove the Poisson improvement on top of the capacity bump. The 4-lever Researcher decomposition (capacity / LF-down-weighting / epochs / basis K) is now empirically validated at the first two levers. **Within-family F5 partial resolution**: `fno_mf_stack` at H4 capacity wins BOTH datasets within the same family — only residual gap is H1's Heat 0.0154 (H4 ~6.5× worse on Heat). H3 (`fno_coreg_residual` hybrid) is demoted from "structural necessity" to optional upside test. **Factory `finalize` recorded `revert` due to the same 4 precheck false positives** as H1 R4 + H2 R4 (score_direction polarity bug, empty-detail scope/fixed_surfaces, ground_truth_leakage substring match) — 3rd consecutive cycle override; CEO override applied; **branch and code preserved intact**. **R4 evaluator agent timeout was orthogonal to eval success**: the Claude agent's ClaudeRunner timed out at 3600 s waiting on the CPU run (~28 min wall exceeded its tool-call budget), but `cycle_eval.sh` exited 0 and all artefacts on disk are complete — CEO wrote `summary.json` directly from the populated `results/smoke_latest.json` rather than respawning the evaluator. New patterns pinned: (a) R4 agent timeout vs eval success; (b) MFRNP knob orthogonality + cross-architecture portability; (c) within-family F5 resolution before proposing hybrids. → [[factory_mffp-003-experiment]], [[patterns]].
- **2026-05-15** — **Cycle 002 H4 Builder complete; CEO + Reviewer PROCEED.** Branch `experiment/3-fno_mf_stack_v2_capacity_loss` commit `ddd221d`: 3 files changed under `models/fno_mf_stack/` (+66/-14). **`model.py` byte-identical to H2** (anti-pattern guard PASS — clean one-axis diagnostic of capacity + loss). **Knob 1 (capacity)** in `smoke_eval.py:36-44`: `hidden 16→32`, `agg_hidden 16→32`, `n_blocks 2→3`, `modes_per_level (4,5,5,5)→(4,8,12,12)`. SMOKE_DEFAULTS is now an explicit scaled-down mirror of `full_config.json` (full hidden=64; same modes/blocks) — closes cycle-001 patterns.md anti-pattern "smoke_eval.py may not consume full_config.json". **Knob 2 (Poisson loss)** in `resolve_fidelity_weights()` at `smoke_eval.py:142-148`: returns `(2.0, 0.25)` iff `"poisson" in dataset_name.lower()`, else `(1.0, 1.0)`. Weights multiply **already-normalized** per-fidelity MSE residuals (correct order of ops); HF weight multiplies both `loss_hf` and `loss_base` (both at m=1 — faithful to fidelity-index-keyed weighting). Verbatim MFRNP `Poisson5_config.yaml` (8× HF up-weighting) with the published Heat `pde_config.yaml` uniform-weighting gating. INSPIRATION.md +12 lines documenting both knobs' provenance. **Pre-flight 2-epoch CPU smoke** ran on both datasets: `ifc_heat` printed `hf_fid_weight=1.0 lf_fid_weight=1.0` (uniform, correct for Heat); `ifc_poisson` printed `hf_fid_weight=2.0 lf_fid_weight=0.25` (gating fires, correct); both produced finite `metric_value` + contract-compliant JSON. **Surface clean**: 3 files, all under `models/fno_mf_stack/`; no fixed-surface modifications. **Both CEO and Reviewer verdict PROCEED**; Reviewer ran `factory guard --check-scope` (clean PASS) and verified all 4 Sacred Rules with concrete evidence. Awaiting R4 evaluator for the gate score; cycle_eval.sh cache will MISS on fno_mf_stack (new code_hash). → [[factory_mffp-003-build]].
- **2026-05-15** — **Cycle 002 Strategist complete; CEO PLAN APPROVED (HARD GATE).** Exactly 2 hypotheses in priority order, both surfaces under `models/**`, leakage-check `risk=none` on both, growth tags load-bearing, anti-patterns enumerated (9). **H4 = `fno_mf_stack` capacity + Poisson-loss bump** (EXPLOIT, experiment_diversity, branch from `experiment/2-fno_mf_stack`) — two pre-registered MFRNP Poisson5 knobs: (a) `SMOKE_DEFAULTS` hidden 16→32, modes (4,5,5,5)→(4,8,12,12), blocks 2→3; (b) per-fidelity loss HF=2/LF=0.25 (Poisson-only gated). `model.py` UNTOUCHED. Expected smoke 5–10 min H100, composite ~0.05. Runs FIRST as cheap diagnostic. **H3 = `fno_coreg_residual` novel hybrid extension** (COMBINE, capability_surface, branch from master, new family) — 4 per-fidelity FNOs hidden=64 modes=(4,8,12,12) 3 blocks, MFRNP decoder-in-the-aggregation, HF head = aggregate + Σ_k B_k(m)·h_k(x), `B(m)=MLP_B([m,m²])`, K=10, per-fidelity normalization MANDATORY, val_frac=0.1. Cite `xing2020deepcoreg` + `li2022ifc` + `niu2024mfrnp` + `li2020fno`; INSPIRATION.md must explicitly label "novel hybrid extension — no direct precedent." Expected smoke 10–20 min H100, composite ~0.04 best case. Runs SECOND as bigger swing. Execution order H4 → H3 (complementary, not sequential). → [[cycle-002-strategy]].
- **2026-05-15** — **Cycle 002 Researcher (R1.5) complete; CEO PROCEED.** Mode-4 web research on hybrid composability + Poisson gap decomposition. **Key finding:** the proposed cycle-002 hybrid (continuous-m basis head over MFRNP-style residual stack with FNO backbones and decoder-in-the-aggregation) has **NO published precedent** in 2020-2026 MF field-prediction literature; closest analogue is `xing2020deepcoreg` / ResPCA (residual + low-rank basis on a GP backbone with discrete fidelities) — empirical backing that the compose is viable at lower granularity. **Poisson 0.0979 → 0.036 gap decomposed** into 4 orthogonal levers (capacity, LF-down-weighting, epochs, basis K); the MFRNP `Poisson5_config.yaml` verbatim `fidelity_weight=2, lower_fidelity_weight=0.25` (HF:LF = 8:1) is **a free pre-registered knob** we are not currently using. **7 new 2024-2026 papers proposed for `papers_summary.csv`** (`xing2020deepcoreg`, `lin2024continuar`, `davis2025rmfnn`, `hu2025hufno`, `wen2022ufno`, `rahman2025adaptfno`, `fno_resnet_2024`) — fixed-surface human action, not in-cycle code. **Final CEO-approved hypothesis pair (in priority order):** **H4 = `fno_mf_stack` capacity + Poisson-loss bump** (two pre-registered MFRNP Poisson5 knobs — `SMOKE_DEFAULTS → (hidden=32, modes=(4,8,12,12), 3 blocks)` + `HF_weight=2, LF_weight=0.25`, branch off `experiment/2-fno_mf_stack`); **H3 = `fno_coreg_residual` novel hybrid** (full-config sizes from start, branch off master, INSPIRATION.md must explicitly label as "hybrid extension, no direct precedent"). → [[research-cycle-002]].
- **2026-05-15** — **Cycle 002 baseline re-measure + Failure Analyst complete; CEO PROCEED.** Master composite = 1.6595 (unchanged from cycle 000 — cache hit; 5 s wall; H1/H2 branches not merged). Failure Analyst surfaced 2 new cross-cycle modes (F4 `SMOKE_DEFAULT_UNDER_CAPACITY`, F5 `INVERSE_COMPLEMENTARY_FAMILIES`) on top of F1/F2/F3. F1 still ~95 % of composite (Poisson value-scale collapse); F2 ~5 % (Heat backbone gap). 4 ranked interventions, top-2 endorsed by CEO as cycle-002 hypothesis pair: (1) **`fno_coreg_residual`** hybrid (H1 basis head over H2 residual stack — attacks F5 synthesis gap, expected composite ≈ 0.039); (2) **`fno_mf_stack` smoke-defaults bump** (one-knob `hidden=32–64, modes=(4,8,12,12)` — isolates F4 from inductive-bias on Heat, expected composite ≈ 0.055). Researcher (R1.5) instructed to investigate hybrid composability in 2024–2026 MF literature. → [[failure-analysis-cycle-002]].
- **2026-05-15** — **H2 R4 Evaluator complete; CEO KEEP.** Local CPU run via `score.py` (no SLURM submission, ~530s wall). **`ifc_heat` 0.149 → 0.1275 (1.7× over paper; 8.3× worse than H1); `ifc_poisson` 18.50 → 0.0979 (2.7× over paper; 7.9× better than H1); composite 1.6595 → 0.11173 (−93.3% vs v9 project state, +2.3% advisory regression vs H1).** Factory `finalize` recorded `revert` due to the **same 4 precheck false positives** (score_direction polarity bug, empty-detail scope, empty-detail fixed_surfaces, ground_truth_leakage substring match `0.10` against `factory.md` eval_weights) — CEO override; **branch and code preserved intact**. n_params 97k (49× smaller than H1). Backlog entry `fno_mf_stack` removed. Cycle-002 hypothesis pre-registered: bump `SMOKE_DEFAULTS` to hidden=32, modes=(4,8,12,12). Complementary-pair pattern surfaced (H1 best on Heat, H2 best on Poisson — ensemble candidate). → [[factory_mffp-002-experiment]].
- **2026-05-15** — **H2 Builder complete; CEO PROCEED (with noted concern).** Branch `experiment/2-fno_mf_stack` commits `294d96a` + `73e492d`: 6 files at `models/fno_mf_stack/` (+730 LoC). 4 small FNOs (one per fidelity) + MFRNP-style residual stack with decoder-in-the-aggregation; per-fidelity scaler buffer; continuous m threaded; `val_frac=0.1`; spectral conv from scratch (rfft2/irfft2 + complex einsum) per li2020fno. **Surface clean** (only `models/fno_mf_stack/`). **Leakage scan medium-risk → CEO override** (false positives, identical pattern to H1 — see [[patterns]] §"Factory leakage-check fingerprints `factory.md` itself"). **Builder deviations** (PROCEED-noted, not blocking): smoke defaults `hidden=16` (spec 32–64), `modes_per_level=(4,5,5,5)` (spec k_max≈12) — `smoke_eval.py` ignores `full_config.json` so SLURM also uses smoke sizes; CEO pre-registered "bump hidden=32" hypothesis for cycle 002 if H2 R4 metric ≥ 1.0. **Builder architectural extension**: HF FNO consumes aggregator baseline as extra input channel before predicting δ — minor MFRNP refinement, no spec conflict. **2-epoch CPU smoke (sanity-only, NOT decision signal — model ~50× smaller than H1 at smoke config)**: `ifc_heat` 1.17, `ifc_poisson` 1.91. → [[factory_mffp-002-build]].
- **2026-05-15** — **H1 R4 Evaluator complete; CEO KEEP.** SLURM job `13961993` (L40S, ~12 min) on `experiment/1-fno_coregionalization`. **`ifc_heat` 0.149 → 0.0154 (−89.6%, beats paper 0.074 by 4.8×); `ifc_poisson` 18.50 → 0.7725 (−95.8%, still 21× paper but value-scale collapse structurally fixed); composite 1.6595 → 0.1092 (−93.4%, below stretch target 0.10 band).** Factory `finalize` recorded `revert` due to 4 precheck false positives (score_direction polarity bug on lower-is-better metric, empty-detail scope/fixed_surfaces contradicting standalone guard, leakage-check fingerprinting factory.md vocabulary) — CEO override; **branch and code preserved intact**. Backlog entry `fno_coregionalization` removed. → [[factory_mffp-001-experiment]].
- **2026-05-15** — **H1 Builder complete; Reviewer PASS; CEO PROCEED.** Commit `f1b0e4a` on `experiment/1-fno_coregionalization`: 6 files at `models/fno_coregionalization/` (+594 LoC), n_params ≈ 4.75M, observed per-fidelity scaler `[0.0773, 0.0237, 0.0069, 0.0018]` on `ifc_poisson` confirms diagnosed ~40× value-scale collapse. **2-epoch CPU smoke: ifc_heat 0.149→0.136, ifc_poisson 18.50→0.478, composite 1.66→~0.255 (−85% vs baseline already).** Leakage scan medium with 7 false positives (shared-vocabulary tokens in factory.md/README.md), CEO override. Builder implemented spectral conv + FNO blocks from scratch from li2020fno/li2022ifc — no v9 copying. → [[factory_mffp-001-build]].
- **2026-05-15** — **Strategist complete (cycle 001); CEO PLAN APPROVED.** 2 hypotheses written to `.factory/strategy/current.md` (H1 `fno_coregionalization`, H2 `fno_mf_stack`); all HARD GATE checks pass (surface, leakage=none, validation=VALID, count=2, growth tag, backlog L27+L26, type=code). Execution: sequential, `--no-github`. → [[cycle-001-strategy]].
- **2026-05-15** — Researcher complete (cycle 001). 9 new bibtex_keys identified, F1 diagnosed as value-scale collapse, top-2 candidates confirmed.
- **2026-05-15** — CEO PROCEED verdict on Researcher; instructions issued to Strategist (generate 2 hypotheses matching H1/H2).
- **2026-05-15** — CEO PROCEED verdict on failure_analyst (manual stub — agent skipped due to aggregate-metric / no-instance-axis / prior-timeouts).
- **Earlier (per recent commits)**: v9_baseline moved to `references/`, composite metric switched to geometric mean, scorer reports `vs_paper` per dataset.

## Related notes

- [[cycle-008-exp-12-build]] — **Cycle-008 H2 Build phase note** (CEO PROCEED with leakage-bug override — 5th consecutive Builder-phase 'leakage substring collision' override; NEW family `models/fno_coreg_conditioned/` on branch `experiment/12-fno_coreg_conditioned-film` cut from `1249f2d` independently of H1's `experiment/11` branch per Strategist R2 H1/H2/H3-must-be-independent-branches anti-pattern; single commit `540e684` = 4 NEW files (`model.py` 218 LOC + `smoke_eval.py` 517 LOC copied from `fno_coregionalization` at 1249f2d with K/b_hidden removed and `m_feat_dim=32` added + `manifest.json` 6 LOC + `INSPIRATION.md` 87 LOC with 5 bibtex_keys `li2022ifc + li2020fno + lyu2023mffno + beggs2025pdecond + herde2024poseidon`); +828/-0 across 4 files all under `models/fno_coreg_conditioned/`; ZERO existing-family files modified (`fno_coregionalization`, `fno_coreg_residual`, `fno_mf_stack`, `mf_fno_transfer_bar`, transolver* all byte-identical to `1249f2d`); FiLMNorm = `GroupNorm(affine=False) + MLP([m, m²]) → 2·C → γ, β` with zero-init γ-projection (γ ≈ 1, β ≈ 0 at init); single full-res HF FNO architecture (NOT a per-fidelity ladder, NOT a coregionalization head, NOT a residual stack) — third architectural axis distinct from H1; constructor signature mirrors cycle-007 H1 anisotropic-modes pattern (positional `modes` accepts int OR `(modes_h, modes_w)` tuple); H2 LF→HF schedule preserved verbatim (`pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25`); Mode A succeeded (no Mode B fallback needed); pre-flight 2-epoch smoke PASS on BOTH datasets — `ifc_heat` 4.76M params 2.04s / 222 MB peak / ~3.4 min 200-ep projection AND `ifc_poisson` 4.76M params 1.61s / 222 MB peak / ~2.7 min 200-ep projection — combined ~6 min total wall, **76% headroom under 25-min kill-switch cap** (most R4 wall-budget headroom of any cycle-008 hypothesis); leakage scanner reported HIGH (4 findings: `satisfy`, `description`, `ifc_raw`, `frozen`) — OVERRIDDEN: all 4 are substring collisions with REQUIRED manifest schema fields per `eval/MODEL_CONTRACT.md` (`description`, `frozen`) and REQUIRED `supports` value per research_constraints field 4 (`ifc_raw`) and generic English (`satisfy`); `references/papers_summary.csv` not present in-tree → no fixed-surface append triggered; surface guard `clean` against explicit `1249f2d` baseline; all six cycle-008 anti-patterns satisfied (MFRNP recipe NOT used, per-dataset dispatch NOT used, NO bundling with H1, D1 + A3 DEFERRED, H1 `model.py` edit N/A — H2 does not touch fno_coregionalization at all); `--no-github` honored; pending R3-review and R4 200-epoch SLURM run with heat kill-switch > 0.0194; primary win condition is Poisson leaderboard displacement (≤ 0.05961 to displace `fno_mf_stack`))
- [[cycle-008-exp-11]] — **Cycle-008 H1 full-lifecycle outcome note** (NEW REPRODUCIBLE PROJECT BEST — composite 0.030408 → 0.027729, −8.81%; `fno_coregionalization × ifc_heat` 0.01551 → 0.012898 (−16.84%) — family now sole holder of heat leaderboard at >2× margin over `fno_coreg_residual @ 0.026277`; `fno_coregionalization × ifc_poisson` 0.7501 → 0.5945 (−20.75%, composite-neutral, `fno_mf_stack` retains poisson at 0.05961); bar `mf_fno_transfer_bar @ 0.027429` short by +0.000300 (+1.09%) — 89.93% of bar gap closed by capacity-axis alone; both hard component targets MET (composite ≤ 0.028 ✅ AND heat ≤ 0.013 ✅); heat kill-switch (0.0194) NOT tripped with 33.5% headroom; wall 315 s total (79% under 25-min cap); verdict `revert_bookkeeping_keep_intent` — 5th consecutive in cycle-007/008 (7th project-wide); 5th consecutive operator precheck-overhaul request; first hypothesis with clean leakage on BOTH passes; all six cycle-008 anti-patterns satisfied; branch `experiment/11-fno_coregionalization-paper-capacity @ 18d83a6` PRESERVED as cycle-009 entry baseline)
- [[cycle-008-exp-11-build]] — **Cycle-008 H1 Build phase note** (CEO PROCEED, branch `experiment/11-fno_coregionalization-paper-capacity` cut from cycle-007 H1 baseline `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`, single commit `18d83a6` = paper-config capacity bump on `fno_coregionalization` SMOKE_DEFAULTS — `hidden_channels 32→128`, `K 10→20`, `n_blocks 4→6`, `modes_cap 12→16`, NEW `b_hidden=128` key + one-line plumbing kwarg to constructor call site; +10/-4 across 1 file all under `models/fno_coregionalization/`; `model.py` byte-identical to `1249f2d` per cycle-008 anti-pattern #6; H2 LF→HF schedule preserved verbatim; pre-flight 2-epoch smoke PASS on `ifc_heat` with `train_seconds=4.31`, `params=50.47M`, `peak_mem=1.73 GB`, 200-epoch projection ≈ 14-15 min total under 25-min kill-switch cap; surface guard clean against explicit `1249f2d` baseline; leakage scan `flagged: false, risk_level: none` BOTH at Strategist R2 hypothesis-level AND at Builder diff-level — first hypothesis in project history with clean leakage on both passes; all six cycle-008 anti-patterns satisfied; `--no-github` honored; pending R3-review and R4 200-epoch SLURM run with kill-switch heat > 0.0194 and acceptance heat ≤ 0.013 / composite ≤ 0.028)
- [[cycle-008]] — **Cycle-008 strategy snapshot (PLAN APPROVED 2026-06-02)** — three hypotheses in priority order H1 > H2 > H3 with bundling forbidden: H1 = paper-config capacity bump on `fno_coregionalization` SMOKE_DEFAULTS only (EXPLOIT, HIGH, LOW risk); H2 = NEW family `models/fno_coreg_conditioned/` with FiLM-via-LayerNorm on single full-resolution HF FNO (EXPLORE, MEDIUM-HIGH, highest swing-EV); H3 = three-stage curriculum on `fno_coreg_residual` (LF pretrain → frozen-LF HF residual → basis-head unfreeze) with mandatory `recipe_hash` checkpoint guard (EXPLOIT + EXPLORE, MEDIUM); baseline composite 0.030408 (cycle-007 H1 `experiment/9 @ 1249f2d`), bar `mf_fno_transfer_bar` parallel-bench 0.027429, dethrone target ≤ 0.024686, gap 10.86% (heat 12.6× more composite log-weight than poisson); all three leakage `risk_level: none`; all six cycle-008 anti-patterns binding (MFRNP recipe BANNED 3/3 REVERTs, per-dataset dispatch BANNED, bundling FORBIDDEN, D1 + A3 DEFERRED, `model.py` edit FORBIDDEN for H1); builder-branch-base `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`; `--no-github` active.
- [[failure-analysis-cycle-008]] — Cycle-008 baseline failure analysis (CEO PROCEED 2026-06-02) — dominant failure mode `CAPACITY_PARETO` on `fno_coregionalization × ifc_heat` (12.6× composite log-weight); dominant absolute failure `fno_coregionalization × ifc_poisson` @ 0.7501 (12.61× over bar, composite-neutral); 5-row failure-distribution table; cross-architecture portability lesson MFRNP DO-NOT-RETRY (3/3 REVERTs lock-in); three new transfer-learning ideas surfaced (re-bind H2 schedule on repaired constructor, NEW `fno_coreg_conditioned` family, curriculum LF→stack→HF-head on `fno_coreg_residual`); ranked 5-intervention table; CEO downstream instructions for Researcher R1.5 web focus areas.
- [[anisotropic-spectral-modes-fno]] — **cycle-007 R1.5 source note** — canonical `(modes_h, modes_w)` parameterization in Li 2020 FNO / neuraloperator library; F-FNO Tran 2023 documents the split is the right abstraction for non-square grids; IFC paper uses GP-ODE, not FNO, so the choice is purely backbone-side. Concrete constructor pattern to mirror at `models/fno_coregionalization/model.py:83-128` per `models/mf_fno_transfer_bar/model.py:62-94`.
- [[per-dataset-recipes-mf-field]] — **cycle-007 R1.5 source note** — MFRNP ships 3 YAML configs (`Poisson5_config.yaml` HF=2.0/LF=0.25; `pde_config.yaml` uniform; `Fluid_config.yaml` uniform); 4 convergent theoretical lenses (effective-sample-mass, Green's-function global support, gradient-pathology, in-tree empirical precedent on `fno_mf_stack`). Concrete `_DATASET_RECIPES` dispatch table for `ifc_heat` vs `ifc_poisson`.
- [[lf-hf-pretrain-fraction-survey]] — **cycle-007 R1.5 source note** — survey of pretrain-fraction choices: Lyu 2023 ≈0.50, GCS ≈0.50, DPOT 2024 0.667, cycle-005 H2 0.25, Pretraining-in-Lower-Dims 2024 saturation warning. Cycle-007 recommendation: keep 0.25 for the constructor-fix PR; bump to 0.40 for Heat in a follow-up `_DATASET_RECIPES` PR; disable on Poisson.
- [[cycle-007-constructor-fix-pattern]] — **cycle-007 R1.5 cross-cycle pattern** — Researcher confirms the `fno_coregionalization` crash is a pure wrapper-level mismatch; inner classes (`SpectralConv2d`, `FNOBlock`) already accept `(modes_h, modes_w)`; the cycle-005 H2 smoke_eval.py schedule is intact at lines 64-411; ONLY the outer `FNOCoregionalization.__init__` and `coord_grid` builder need to be brought into alignment. ≤15-LOC edit. Second instance in the project of a dirty load-bearing `model.py` being lost via `git reset` while sibling files retained their state.
- [[factory_mffp-007]] — **Cycle-005 H2 Build phase note** (CEO PROCEED, branch `experiment/7-fno_coreg_lf_hf_transfer` cut from `experiment/6-mf_fno_transfer_bar-repo-root-fix` (NOT `main`) — first downstream-branching off a `revert_bookkeeping_keep_intent` preserved branch in project history; single commit `be36cba` = two-stage LF→HF transfer schedule for `fno_coregionalization` mirroring `mf_fno_transfer_bar`'s recipe (`pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25`); +398/-75 across 2 files all under `models/fno_coregionalization/`; architecture UNCHANGED (no `model.py`/`data.py`/`manifest.json`/`full_config.json` edits); `n_warmup = round(pretrain_frac * args.epochs)` LF-only Stage 1 → joint Stage 2; fresh `Adam` + `CosineAnnealingLR` per stage; `last.pt` schema gains `stage` field with resume guard `stage==2 AND epoch==epochs_target`; `model.set_scalers(...)` once before Stage 1; INSPIRATION.md cites `lyu2023mffno` + `li2022ifc`; pre-flight `--epochs 4` PASS — Stage 1 (1 epoch LF-only on 153 samples, lr=1e-3) → Stage 2 (3 epochs joint on 157 samples, lr=3e-4); val_nRMSE 0.171 → 0.118; resume guard verified by re-run; surface CLEAN; leakage scan HIGH-flagged with 3 known substring-collision false positives (`"satisfy"` in code comment, `"dataset"` ×2 from CLI flag names); first training-schedule-only hypothesis in project history; pending R4 = `bash scripts/cycle_eval.sh` with expected `ifc_heat` ≤ 0.013 and composite ≤ 0.026 — but per H1 cross-harness calibration finding, even composite 0.028–0.032 is a meaningful KEEP in the smoke harness)
- [[factory_mffp-006]] — **Cycle-005 H1 Build phase note** (CEO PROCEED, branch `experiment/6-mf_fno_transfer_bar-repo-root-fix` cut from `bench/all-fno-families`, two-commit split: `a415e26` = literal 1-line REPO_ROOT fix in `models/mf_fno_transfer_bar/smoke_eval.py:32` + `17e5234` = supporting `model.py` + `manifest.json` follow-up because base branch never tracked them; +321/-0 across 3 files all under `models/mf_fno_transfer_bar/**`; pre-flight 2-epoch CPU smoke on ifc_heat PASS — both LF pretrain → HF fine-tune stages executed end-to-end with no `ModuleNotFoundError`; surface guard CLEAN; leakage scan flagged HIGH with 5 known substring-collision false-positives in `factory.md` / `README.md` / `manifest.json` schema fields, none under `data/**`; first Builder commit-split in project history; pending R4 = `bash scripts/cycle_eval.sh` with R5 acceptance composite ∈ [0.025, 0.030] matching parallel-bench ~0.0274)
- [[cycle-005-strategy]] — **Cycle-005 strategy snapshot (PLAN APPROVED 2026-06-02)** — two hypotheses: H1 (1-line REPO_ROOT fix in `mf_fno_transfer_bar/smoke_eval.py:32` to unblock in-distribution bar comparison) + H2 (LF→HF 2-stage transfer-learning pretraining for `fno_coregionalization`, absorbing the bar's transfer mechanism into the cycle-005 R0 winner on ifc_heat); cycle-005 R0 composite 0.033726, bar ≈ 0.0274, dominant gap ifc_heat (winner 0.0205 vs bar 0.0128, distribution-shift problem); H2 expected impact ifc_heat ≤ 0.013, composite ≤ 0.026 (beats bar); surface + leakage gates BOTH CLEAN (first cycle without precheck substring-collision false-positives); branch base plan H1 first then H2 off post-H1-merge (NOT parallel); systemic agent-wrapper-timeout caveat tracked.
- [[cycle-003-summary]] — **Cycle-003 close-out summary** (single-hypothesis cycle; H1 GENUINE REVERT — first in project history; composite 0.04420 → 0.08472 +91.7% regression; refutes "PDE-class-bound" framing — recipe is backbone-coupled; checkpoint-resume contamination discovered + resolved; project best 0.04420 preserved at cycle-002 H3; two cycle-004 prerequisite backlog items filed)
- [[factory_mffp-005-experiment]] — **Cycle-003 H1 Outcome companion (FIRST genuine REVERT in project history)** — composite_nRMSE 0.04420 → 0.08472 (+91.7% regression); ifc_heat 0.02630 unchanged (still BEATS paper 2.81×); ifc_poisson catastrophically regressed 0.07416 → 0.27287 (3.68× worse than entry; 4.58× worse than H4 on simpler backbone); refutes cycle-003 "PDE-class-bound" framing — the MFRNP Poisson5 recipe is backbone-coupled; checkpoint-resume contamination diagnosed + operationally resolved; CEO=REVERT (research-target regression confirmed by clean 200-epoch cuda run); branch `experiment/5-fno_coreg_residual_poisson_lossweight` commit `a0d932b` preserved on disk; cycle-004 backlog: adaptive loss-weighting / recipe-fingerprint checkpoint guard / re-verify H3 baseline under clean run; new pattern pinned in [[patterns]]
- [[factory_mffp-005-build]] — **Cycle-003 H1 Build phase note** (CEO PROCEED, branch `experiment/5-fno_coreg_residual_poisson_lossweight` commit `a0d932b`, +67/-5 across `models/fno_coreg_residual/{smoke_eval.py, INSPIRATION.md}`, ports H4's `resolve_fidelity_weights` helper, SMOKE_DEFAULTS adds `poisson_hf_weight=2.0` / `poisson_lf_weight=0.25`, both pre-flight smokes pass with correct gating, surface clean with explicit-SHA baseline workaround, leakage scan 2 known substring-collision false-positives, aggregator anchor scaling decision documented)
- [[factory_mffp-004-outcome]] — **H3 final outcome (NEW PROJECT BEST)** — composite 1.6595 → 0.04420 (37.5× vs master; 43% better than H4; first family to beat paper composite geomean; first family to beat paper ifc_heat bar 2.81×); F5 INVERSE_COMPLEMENTARY_FAMILIES resolved at architectural level by composing H1 basis head + H2 MFRNP residual stack with zero-init safety; ifc_poisson regression vs H4 attributable to missing H4 loss-reweighting (cycle-003 H5 mechanical fix pre-registered); CEO KEEP, factory bookkeeping REVERT (4th consecutive precheck override); branch `experiment/4-fno_coreg_residual` commit `0c46f43` preserved
- [[factory_mffp-004-build]] — **H3 Build phase note** (CEO + Reviewer PROCEED, branch `experiment/4-fno_coreg_residual` commit `0c46f43`, +939/-0 across 6 files in new `models/fno_coreg_residual/` directory, line-by-line spec-fidelity verification, basis-head zero-init, K=10, 4 per-fidelity FNOs at full-config sizes)
- [[factory_mffp-003-outcome]] — **H4 outcome companion (keep/revert disposition)** — CEO intent KEEP, factory state REVERT (3rd consecutive cycle, same 4 precheck infrastructure bugs); branch `experiment/3-fno_mf_stack_v2_capacity_loss` commit `ddd221d` preserved; composite 1.6595 → 0.077187 (−95.3% vs master, −31% vs cycle-001 H2); both pre-registered MFRNP Poisson5 knobs validated independently (capacity → Heat recovery, loss-weighting → Poisson improvement)
- [[factory_mffp-003-experiment]] — **H4 final outcome (full empirical detail)** (CEO KEEP, composite **0.07719**, both Poisson5 knobs validated independently, within-family F5 partial resolution, 3rd consecutive precheck-bug revert discrepancy, R4 agent timeout vs eval success)
- [[factory_mffp-003-build]] — **H4 Build phase note** (CEO + Reviewer PROCEED, branch `experiment/3-fno_mf_stack_v2_capacity_loss` commit `ddd221d`, both pre-registered MFRNP Poisson5 knobs applied, `model.py` byte-identical to H2, pre-flight CPU smoke on heat + poisson both finite)
- [[cycle-002-strategy]] — **cycle 002 CEO PLAN APPROVED Strategist plan** (H4 EXPLOIT + H3 COMBINE, 9 HARD GATE checks all PASS, anti-patterns, execution order H4→H3)
- [[research-cycle-002]] — **cycle 002 Researcher (R1.5) Mode-4 findings** (hybrid is novel — no published precedent; ResPCA closest analogue; Poisson gap 4-lever decomposition; LF-down-weighting verbatim pre-registered free knob; 7 new papers for papers_summary.csv; final CEO-approved H4 + H3 pair)
- [[failure-analysis-cycle-002]] — **cycle 002 baseline + failure analysis** (master 1.6595 unchanged, F1/F2/F3/F4/F5 taxonomy, CEO-approved hypothesis pair `fno_coreg_residual` + `fno_mf_stack` defaults bump)
- [[cycle-002-summary]] — **cycle 002 close-out summary** (composite 1.6595 → 0.07719 H4 / 0.04420 H3 NEW PROJECT BEST; first family to beat paper composite geomean; F5 INVERSE_COMPLEMENTARY_FAMILIES resolved at architectural level; 4 consecutive precheck overrides; cycle-003 H5 pre-registered)
- [[cycle-001-summary]] — **cycle 001 close-out summary** (composite 1.6595 → 0.10919 H1 / 0.11173 H2, 1/17 datasets beat paper, complementary-pair pattern, 3 cycle-002 hypotheses pre-registered)
- [[factory_mffp-002-experiment]] — H2 final outcome (CEO KEEP, composite 1.6595→0.11173, ifc_poisson 7.9× better than H1, 49× fewer params, same factory-bookkeeping `revert` discrepancy)
- [[factory_mffp-002-build]] — H2 Build phase note (CEO PROCEED with noted concern; 2-epoch CPU smoke sanity-only at ifc_heat 1.17 / ifc_poisson 1.91)
- [[factory_mffp-001-experiment]] — H1 final outcome (CEO KEEP, composite 1.6595→0.1092, ifc_heat beats paper, factory-bookkeeping `revert` discrepancy documented)
- [[factory_mffp-001-build]] — H1 Build phase note (CEO PROCEED, 2-epoch CPU smoke −85% vs v9)
- [[cycle-001-strategy]] — CEO PLAN APPROVED Strategist plan (H1 + H2, anti-patterns, execution strategy)
- [[cycle-001-failure-diagnosis]]
- [[cycle-001-candidate-ranking]]
- [[cycle-001-cross-cutting-findings]]
- [[paper-baselines-proposals]]
- [[papers-summary-csv-state]]
- Source papers: [[li2022ifc]], [[niu2024mfrnp]], [[li2020fno]], [[wu2024transolver]], [[gladstone2024mfgunet]], [[taghizadeh2024mfgnn]], [[yang2025mfdeeponet]], [[nietocentenero2025mfae]], [[sung2026fire]].
