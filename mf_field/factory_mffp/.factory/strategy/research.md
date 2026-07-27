# Research — Cycle-010 — Failure-Targeted Solutions (Mode 4)

**Date:** 2026-06-02
**Cycle:** cycle-010
**Source failure analysis:** `.factory/research/runs/cycle-010-baseline/failure_analysis.md`
**CEO priority signal:** `.factory/reviews/ceo-verdict-failure_analyst.md`
**Researcher note on web access:** WebSearch returned 10/10 queries successfully across the 5 focus areas. WebFetch landed two readable HTML excerpts (PI-RINO; UFNO-FiLM) and consistently returned PDF-binary or 403 for arXiv PDFs / ScienceDirect — load-bearing protocol numbers are sourced from the in-tree MFRNP YAML configs, prior-cycle archive (which deep-read these papers in cycles 005-009), and search-result snippets.

## Context

- **Research target:** minimize `composite_nRMSE` (geomean of best-per-dataset on smoke ifc_heat × ifc_poisson). Hard target → 0.
- **Current metric:** `composite_nRMSE = 0.022161` on commit `0b6e6eb` (cycle-009-h1h2 banked, identical reproduction of cycle-009-h1h2 in cycle-010 baseline).
- **Cycle-010 bar shift:** IFC-ODE2 paper composite (0.0516) already beaten 2.33×; **new strategic target is IFC-GPODE composite ≈ 0.0331** (sqrt(0.061 × 0.018)). Current ratio = 0.67×, i.e. we are already 33% under GPODE; the per-dataset residual lives almost entirely on Poisson.
- **Dominant failure mode:** `POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY`. Heat is 4.7× under GPODE (zero residual to chase); Poisson best `fno_mf_stack × ifc_poisson = 0.038120` is 1.06× ODE2 / 2.12× GPODE. **Load-bearing cell** — no challenger within 1.9× (next: `fno_coreg_residual × poisson = 0.0720` at 89% over best).
- **Composite sensitivity** (from failure_analysis): closing Poisson best → 0.018 GPODE unlocks **−31% composite**; closing it to 0.036 ODE2 unlocks just −2.8%. Heat closure unlocks **0%** (already past every published bar).
- **Mutable surfaces:** `models/**` only. New families must support `ifc_raw` loader, cite source paper(s) in `INSPIRATION.md`, fit smoke wall ≤ 30 min on a single H100.
- **NK-zones in force (cycle-010):**
  - **NK1** — pure m-conditioning on HF-only FNO (cycle-008 H2 falsified `fno_coreg_conditioned` with `γ(m, m²)` at 12.6× over leader); HF-only γ(m) without LF→HF pathway closed.
  - **NK2** — frozen-LF curricula on **co-evolved residual ladders** (`fno_coregionalization`, `fno_coreg_residual`). Carve-out: LF/HF-**independent** stacks like `fno_mf_stack`, `mf_fno_transfer_bar` are NK2-clear with mandatory dual kill-switches.
  - **NK3** — MFRNP-style loss-weight transfer to coregionalization family (3/3 REVERT). Closed.

## Prior Knowledge from Archive

| Source note | Cycle-010 relevance |
|---|---|
| [[niu2024mfrnp]] | Architectural template for `fno_mf_stack`. **In-tree `Poisson5_config.yaml` re-verified:** `hidden_dim=32, z_dim=32, batch_size=2048, base_lr=1e-3, epochs=50000, patience=10000, lr_decay_ratio=0.85 at step 10000, fidelity_weight=2, lower_fidelity_weight=0.25, max_grad_norm=1, clip_grad=True`. No staged training in published MFRNP — joint loss across all fidelities throughout. |
| [[li2022ifc]] | Source paper for `ifc_*`. K=20, ODE-driven `B(m)`. ODE2 m=1: Poisson 0.036, Heat 0.074. GPODE m=1: Poisson 0.018, Heat 0.061. IFC's per-fidelity scaler ladder on Poisson spans ~42× (cf. failure_analysis §1.2); on Heat ≈1×. The ladder asymmetry is **dataset-intrinsic**, not architecture-tunable. |
| [[li2020fno]] | Standard FNO ablation range: `modes=8-32 per axis, width=30-100`. Below `modes=8` per axis on 64×64 is under-resolved; above `modes=32` waste weights in elliptic regimes. |
| [[anisotropic-spectral-modes-fno]] | `(modes_h, modes_w)` canonical split is in place across all FNO families. `models/fno_mf_stack/model.py:37-78` correctly auto-clamps via `min(self.modes1, H // 2 + 1, H - 1)`. |
| [[lf-hf-pretrain-fraction-survey]] | Published pretrain fractions: Lyu 2023 ≈ 0.50, GCS-MFFNO ≈ 0.50, DPOT ≈ 0.667, in-tree `mf_fno_transfer_bar` = 0.50, cycle-005 H2 on `fno_coregionalization` = 0.25. Saturation warning from `pretrain_lowerdims2024` ([arXiv:2407.17616]): pretrain budget plateaus and can hurt generalization past ≈0.50. |
| [[research-cycle-009]] | Cycle-009 H1+H2 capacity bump on `fno_mf_stack`: `hidden 32→64, modes_per_level (4,8,12,12)→(4,8,16,20), n_blocks 3→4`. Nyquist analysis: L0/L1 already at 80-89% Nyquist (BOUND); L2 went from 71% to 100% (filled); L3 went from 36% to 60% (still has runway to ≈85% at modes=28). Wall: 414s (well below 1500s kill). Result: Poisson −36% (0.0596→0.0381), Heat −62% (0.0383 vs prior cycle-008 0.10x range — actually `fno_mf_stack × heat` went from 0.10269→0.0383 between c008 and c009-h1h2). |
| [[research-cycle-008]] | Cycle-008 H1 `fno_coregionalization` paper-capacity bump (K=10→20, b_hidden=64→128, n_blocks=4→6, hidden_channels=32→128, modes_cap=12→16) delivered Heat 0.01551→0.0129. NK1 (γ(m, m²) on HF-only) falsified by cycle-008 H2 on Poisson. NK3 confirmed 3/3. |
| [[cao2025mflno]] | MF-LNO (arXiv:2502.00550) — non-monotone fidelity-correlation; LF base + parallel linear + nonlinear HF correctors. Architectural inspiration for splitting the K-basis into linear-LF and nonlinear-HF parts on `fno_coregionalization`. |
| [[beggs2025pdecond]] | FiLM-via-LayerNorm (arXiv:2509.09599) — direct blueprint for `γ(m)·LayerNorm(z)+β(m)` inside FNOBlock. Confirmed in cycle-008 as standard 2024-2025 PDE-operator conditioning channel. |
| [[herde2024poseidon]] | Poseidon / scOT (arXiv:2405.19101, NeurIPS 2024) — foundation-model-scale FiLM-via-LayerNorm precedent. Uses **time-modulated LayerNorm** as the conditioning channel. |
| [[rahman2024codano]] | CoDA-NO (arXiv:2403.12553, NeurIPS 2024) — codomain-attention complement. >36% few-shot transfer gain. Speculative for K-basis input-dependence (treat m as codomain axis). |
| [[stresstest2025fno]] (cycle-009 new) | "Forcing and Diagnosing Failure Modes of FNO" ([arXiv:2601.11428], Jan 2026 — note: archive note had 2501.11428, actual is 2601.11428). **Re-verified in cycle-010 web round:** the paper uses `FNO width=64, depth=4, 16 Fourier modes in 1D` as their *fixed* config across all 5 PDE families including elliptic Poisson. Confirms `modes=16` is treated as sufficient for elliptic problems in published practice. |
| [[lyu2023mffno]] (carry, [arXiv:2304.06972]) | Lyu 2023 — LF-pretrain → HF-finetune protocol. Published reports: ≈0.50 pretrain fraction, fresh Adam + fresh CosineAnnealingLR per stage (stale momentum is a documented divergence mode), no explicit freezing (full-network fine-tune; reuses LF weights as init), HF stage LR 3-10× smaller than LF stage. **No explicit kill-switch in paper** — relies on val-loss monitoring. |
| [[lf-hf-pretrain-fraction-survey]] (re-stated) | The in-tree `mf_fno_transfer_bar` uses `pretrain_frac=0.50` at full args.epochs each, which matches Lyu. |

---

## O1 — FNO capacity scaling for elliptic PDE (Poisson)

**Question.** What does the modes-vs-hidden trade look like at ~1-4M params for `fno_mf_stack` on Poisson at 64×64? Any 2025/2026 papers on FNO Poisson saturation curves? Where does spectral-mode-cap saturate for elliptic problems at 64×64? Hidden width vs depth?

### External findings

1. **muTransfer-FNO** ([arXiv:2506.19396], Jun 2025) — derives Maximal Update Parametrization for FNO. Practical claims (from abstract): learning rates **transfer across hidden widths** under proper μP — i.e., a tuned 64-channel FNO LR will work at 128/256/512 channels without re-search. Implies the **width axis is monotonically helpful given correct LR scaling** until data/capacity ceiling. They do not publish an explicit Poisson saturation curve in the abstract.

2. **stresstest2025fno** ([arXiv:2601.11428], Jan 2026) — fixed config across 5 PDE families (dispersive, elliptic Poisson, multi-scale fluid, financial, chaotic): `width=64, depth=4, 16 Fourier modes in 1D`. Implication: practitioners treat `modes≈16` as **sufficient for elliptic** problems — they did not need to push higher. **However**, this is a 1D experimental setup; on 2D 64×64 our HF Nyquist limit is 33, so cycle-009's HF=20 (≈60% Nyquist) is mid-range — still has headroom toward 28 (~85%) before hitting strict diminishing returns.

3. **"Toward a Better Understanding of FNO from a Spectral Perspective"** ([arXiv:2404.07200], Apr 2024) — observation: enlarging the Fourier kernel does **not necessarily improve accuracy**. High-order modes containing minimal energy mostly encode structural details; eliminating them can **enhance generalization**. Implication: pushing HF modes past ≈60-70% Nyquist risks val→test inflation, not just compute cost. Argues for the **conservative** end of the cycle-010 sweep.

4. **PhysicsX FNO blog (2024)** — "For elliptic and laminar problems, the dominant physics tends to be concentrated in the first few Fourier modes." Echoes (3).

5. **Cycle-009 measured outcome** (in-tree, the strongest local data point): single capacity step `hidden 32→64, modes (4,8,12,12)→(4,8,16,20), blocks 3→4` delivered **−36% Poisson, −62% Heat on `fno_mf_stack`**, wall 414s (full kill at 1500s). Param count went ~250k → ~1.0M (cf. fno_coregionalization paper-config at ~2.6M and not yet saturated on Poisson).

### Where this lands in the codebase

- **File:** `models/fno_mf_stack/smoke_eval.py:39-55` (SMOKE_DEFAULTS).
- **File:** `models/fno_mf_stack/full_config.json` (in-tree TODO — current full-config still at the cycle-009 capacity, no further reference target).
- **File:** `models/fno_mf_stack/model.py:32-78` (SpectralConv2d auto-clamp guard is already correct — no model.py change needed for a capacity bump).

### Recommendation

**O1 is a buildable cycle-010 H1 (capacity-axis second step on `fno_mf_stack`).** Specifically:

- **Conservative:** `hidden=96, modes_per_level=(4, 8, 16, 24), n_blocks=4` (Nyquist analysis: HF 24/33=73%, slightly past published-prior comfort zone but within `tran2023ffno`'s anisotropic split; param count ≈2.0-2.2M).
- **Aggressive (if conservative leaves wall-time):** `hidden=128, modes_per_level=(4, 8, 16, 24), n_blocks=5` (HF 73% Nyquist; param count ≈3.5M; matches `fno_coregionalization` paper-config in magnitude).
- **Hold:** `modes_per_level[3] ≤ 24` (i.e., do not push HF past ~73% Nyquist) — the `arXiv:2404.07200` and `stresstest2025fno` evidence argues against modes > ~24 on 64×64 elliptic.
- **Hold:** `hf_loss_weight=1.0, baseline_anchor_weight=0.5, poisson_hf_weight=2.0, poisson_lf_weight=0.25` (canonical MFRNP; NK3-blocked from perturbation).

**Mandatory dual kill-switches** (carrying cycle-009's pattern):
- Absolute: `Poisson_test > 0.0594` (cycle-008-baseline level) → REVERT.
- Absolute: `Heat_test > 0.0594` → REVERT.
- Wall: > 1500s (~25 min) → REVERT.
- `recipe_hash` checkpoint guard (already in `_common/recipe_hash.py` from cycle-009 H2) MUST gate resume, so a stale c009-h1h2 ckpt cannot silently load against c010 weights.

**Expected impact** (cross-cycle prior, see §"Cross-Cycle Pattern" below):
- Cycle-009-h1h2 went from `(hidden=32, HF-modes=12, blocks=3)` → `(64, 20, 4)`. The fractional capacity step was hidden ×2, HF-modes ×1.67, blocks ×1.33. Poisson dropped −36%.
- Cycle-010 H1 proposed (hidden=96, HF-modes=24, blocks=4): hidden ×1.5, HF-modes ×1.2, blocks ×1.0. **Smaller fractional step than cycle-009 H1+H2 on every axis.** Linear extrapolation in log-Poisson predicts −15 to −25% Poisson (i.e., 0.0381 → 0.029-0.032), but log-linear extrapolation across capacity is empirically optimistic on second-step bumps in elliptic FNO literature (see (3) above on saturation warning). **Realistic range: Poisson 0.030-0.035 → composite 0.0197-0.0212 (−5% to −11%).**

**Citations for the H1 PR / INSPIRATION.md:** [[niu2024mfrnp]], [[li2020fno]], [[lyu2023mffno]] (for the MF spirit), `stresstest2025fno` ([arXiv:2601.11428]), `muTransferFNO` ([arXiv:2506.19396]), `fnospectralperspective2024` ([arXiv:2404.07200]).

**Confidence: HIGH.** The capacity-axis prior is the strongest evidence type in this project's history (H1 c008 +H1 c009 +H2 c009 all positive). Realistic ceiling is diminishing returns, not a regression risk, given the kill-switch.

**Recommendation tag:** USE AS CYCLE-010 H1.

---

## O2 — Two-stage curriculum on LF/HF-independent MF-FNO designs

**Question.** What does the LF-pretrain → HF-fine-tune protocol look like in practice for `fno_mf_stack`-style stacked architectures? What learning rate schedules, freeze/unfreeze policies, kill-switches did published work use? Critical NK2 carve-out: `fno_mf_stack` has LF/HF-independent design, so freezing the LF stack is theoretically safe — need protocol details and dual-kill-switch evidence.

### External findings

1. **lyu2023mffno** ([arXiv:2304.06972]). Two-stage LF→HF for MF-FNO. Protocol (synthesized from abstract + archive notes from prior cycles' deep reads):
   - **Stage 1 (LF pretrain):** train FNO on abundant LF data with `Adam @ lr=1e-3, CosineAnnealingLR(T_max=stage1_epochs), epochs ≈ 0.50 × total_budget`.
   - **Stage 2 (HF fine-tune):** **fresh `Adam @ lr=1e-4 (or 3e-4)`** + **fresh `CosineAnnealingLR(T_max=stage2_epochs)`**. NO weight freezing — full-network fine-tune. Stale momentum is documented as a divergence mode → fresh optimizer/scheduler per stage is the load-bearing invariant.
   - **No explicit kill-switch in paper** — relies on val-loss monitoring.

2. **gcs2023mffno** ([arXiv:2308.09113], Sci Total Env 2024). Same Lyu-style protocol on geological CCS; achieves 81% data-cost reduction at HF-matched accuracy. **Did not freeze**.

3. **DPOT** ([arXiv:2403.03542], ICML 2024). Auto-Regressive Denoising Operator Transformer, pretrain → fine-tune. Pretrain 1000 epochs, fine-tune 500 epochs (`pretrain_frac = 0.667`). AdamW @ lr=1e-3 throughout. Pretrain-finetune is the standard, NOT staged freeze/unfreeze. No layer freezing.

4. **engstruct2025mfft** (Pretrain-Finetune Neural Operator, Eng Struct 2025, paywalled — abstract reviewed in cycle-008 archive). Two-stage with **option to freeze** Fourier modes if their count is preserved across stages — but the cited variant is to freeze **projection layers** during HF fine-tune, not the LF FNO body. This is the *closest* explicit-freeze precedent.

5. **yang2025mfdeeponet** (Physics-Guided MF-DeepONet, arXiv:2503.17941). Branch+trunk DeepONet pretrained on LF; **branch and trunk frozen; only merge net trainable on HF**. Reports up to 76% improvement over conventional MF frameworks. Different architecture (branch-trunk) but the freezing pattern is informative — they freeze the LF-task representation, train only the cross-fidelity merge. The `fno_mf_stack` analogue: freeze the LF FNOs, train only the HF FNO + MFRNP aggregator.

6. **pretrain_lowerdims2024** ([arXiv:2407.17616]). Saturation warning: pretrain budgets > ≈0.50 plateau and can hurt generalization in F-FNO. Argues *against* DPOT's 0.667. Sets a soft ceiling.

7. **MFRNP `Poisson5_config.yaml`** (re-read in-tree this cycle): `epochs=50000, base_lr=1e-3, steps=[10000], lr_decay_ratio=0.85, patience=10000, fidelity_weight=2, lower_fidelity_weight=0.25`. **Joint training, no staging.** This is the canonical MFRNP recipe and the parent of `fno_mf_stack` — no staged-training precedent in this family's lineage paper.

### NK2 carve-out analysis (load-bearing)

NK2 closed frozen-LF curricula on **co-evolved residual ladders** — `fno_coregionalization`, `fno_coreg_residual` — where LF latents and HF residuals share parameters via the `B(m)·h(x)` decomposition. The shared K-basis breaks the freeze: when you freeze the LF stack, the K-basis loses its joint gradient signal and the HF residual collapses.

`fno_mf_stack`'s structural difference (`models/fno_mf_stack/model.py:136-242`):
- 4 **independent** `SmallFNO` modules (`self.lf_fnos[0..2]` + `self.hf_fno`), no shared weights.
- Coupling only through the `MFRNPAggregator` MLP (`self.aggregator`) — a 3-layer 1×1 conv stack with ≈ 10k params that fuses upsampled LF predictions + m into a baseline.
- HF residual is `delta = hf_fno(input | baseline)` — depends on the aggregator output, not on shared LF weights.

**Conclusion:** the NK2 anti-pattern's mechanism does not apply. Freezing `lf_fnos[0..2]` after stage 1 leaves the LF-loss-supervised stack intact while stage 2 trains `hf_fno + aggregator` only. This matches `yang2025mfdeeponet`'s pattern precisely.

### Where this lands in the codebase

- **File:** `models/fno_mf_stack/smoke_eval.py:171-291` (training loop). Add a stage gate at the top of the per-epoch loop reading `args.pretrain_frac` (new flag) and `args.stage2_freeze_lf` (new flag).
- **File:** `models/fno_mf_stack/smoke_eval.py:182-194` (optimizer construction). Build a fresh optimizer + scheduler at stage transition (`epoch == round(pretrain_frac * epochs)`).
- **File:** `models/fno_mf_stack/smoke_eval.py:62-107` (`compute_losses`). Stage 1: skip the HF loss term (LF-only). Stage 2: full joint loss with frozen `lf_fnos[0..2]`.
- **File:** `models/fno_mf_stack/model.py:165-168` (no change — just need `.requires_grad_(False)` applied per-module in smoke_eval).
- **File:** `models/_common/recipe_hash.py` (read-only; `pretrain_frac` and `stage2_freeze_lf` get hashed into `SMOKE_DEFAULTS` so resume guard catches a cross-recipe ckpt swap).

### Recommendation

**O2 is a buildable cycle-010 H2 (curriculum on `fno_mf_stack`, NK2-carved-out).** Specifically:

- `pretrain_frac=0.40` (within the 0.25-0.50 published band; below the `pretrain_lowerdims2024` 0.50 saturation flag). At epochs=200 → 80 LF + 120 HF.
- **Stage 1 (LF-only):** fresh `Adam @ lr=1e-3, weight_decay=1e-5`, fresh `CosineAnnealingLR(T_max=80, eta_min=1e-6)`. `compute_losses` returns only the LF terms (skip HF residual and aggregator-anchor terms).
- **Stage 2 (joint with LF frozen):** at `epoch == 80`, freeze `lf_fnos[0..2]` via `.requires_grad_(False)` on each module. Build **fresh `Adam @ lr=3e-4`** + fresh `CosineAnnealingLR(T_max=120, eta_min=1e-6)`. Resume full joint loss as in the current smoke (HF + aggregator-anchor; LF terms now contribute zero gradient).
- Poisson-specific recipe `(hf_loss_weight=2.0, lf_loss_weight=0.25)` unchanged across stages (NK3 invariant).

**Mandatory dual kill-switches** (this carve-out is novel — extra paranoia):
- **Absolute (per stage):** Poisson test > 0.0594; Heat test > 0.0594.
- **Inter-stage:** stage-2 best_val ≥ 0.90 × stage-1 best_val (i.e., stage-2 must reduce val by ≥10%) — if not, REVERT to stage-1 checkpoint and report failure category `STAGE_2_NO_IMPROVEMENT`. **Mirrors cycle-008 H3 dual-kill-switch.**
- **Wall:** > 1800s (~30 min) → REVERT.
- **Resume safety:** `recipe_hash` must hash `pretrain_frac, stage2_freeze_lf` into the ckpt key (already gates via cycle-009 H2's `_common/recipe_hash.py` if the new flags are added to `SMOKE_DEFAULTS`).

**Expected impact:**
- Lyu 2023's 99% modeling accuracy on fluid/temperature transfers to a regime where LF data is abundant; in our `ifc_*` setup, LF/HF are well-balanced (ns = 100/50/20/5), so the lever's strength is moderated.
- Freezing the LF stack after stage 1 leaves capacity room for the HF FNO + aggregator to specialize on the residual. Expected: Poisson 0.0381 → 0.030-0.035 (mirrors yang2025mfdeeponet's 76% gain regime, but on a tighter ladder with smaller HF data scarcity — realistic 10-20%).
- Heat: should hold or improve marginally (Heat already at 0.0383 for this family — there is room).

**Bundling guidance:** **DO NOT bundle H1 (capacity bump) with H2 (curriculum) in a single PR.** They share `smoke_eval.py:39-55` (SMOKE_DEFAULTS); confounded H1+H2 will not let us attribute Poisson reduction. Land H1 first, attest the new baseline, then land H2 on top.

**Citations for H2 PR / INSPIRATION.md:** [[lyu2023mffno]] (primary protocol), [[yang2025mfdeeponet]] (freeze pattern), `gcs2023mffno`, `pretrain_lowerdims2024` (saturation warning), [[niu2024mfrnp]] (parent architecture).

**Confidence: MEDIUM-HIGH.** The published protocol is well-defined and the NK2 carve-out reasoning is structurally sound. Risk: if the MFRNP aggregator MLP is the load-bearing Poisson mechanism (failure_analysis §1.3 says it is), then freezing the LF stack might **deny it the cross-fidelity signal it learned during joint training**. Mitigation: the dual kill-switch will catch this within stage 2.

**Recommendation tag:** USE AS CYCLE-010 H2 (after H1 lands; do not bundle).

---

## O3 — K-basis parametrization for coregionalization

**Question.** Published work conditioning the coregionalization basis on input features? `B(m, LF)` vs `B(m)`. Speculative.

### External findings

1. **Scalable Multi-Task GPs with Neural Embedding of Coregionalization** ([arXiv:2109.09261], 2021, KBS 2022). Replaces the LMC's static coregionalization matrix with a **neural embedding** mapping inputs to latent coregionalization weights — i.e., `B(x)` instead of static `B`. This is the canonical pre-FNO precedent for **input-dependent coregionalization**. Bibtex key: `liu2022neuralcoreg`.

2. **MFHoGP** ([arXiv:2006.04972], AISTATS 2021). Nonlinear coregionalization that propagates **bases throughout fidelities** with deep matrix GP prior on basis weights. The bases themselves are fidelity-conditional; inputs enter via the GP kernel. Closer to `B(m)` than `B(m, x)` but the deep-prior idea is portable. Bibtex key: `wang2021mfhogp`.

3. **deepICMGP** (Deep Intrinsic Coregionalization, ResearchGate 2024) — hierarchical ICM with multiple outputs. Hierarchical structure but B is still input-independent. Less novel for our problem.

4. **cao2025mflno** (already in archive). Splits residual into linear LF→HF + nonlinear corrector. Not strictly `B(m, x)` but explicitly **drops the single-basis assumption** in favor of a two-branch decomposition.

5. **rahman2024codano**. Treats codomain (channel) axis as attention-tokenized. Treating m as a codomain axis is a strong precedent for **m → set of context vectors**, which the K-basis could attend to.

6. **UFNO-FiLM** ([arXiv:2511.20543], Nov 2025). FiLM context vector derived from **both scalar parameters AND spatial low-fidelity features** (permeability field). 21% MAE reduction on multiphase flow. Direct precedent for the **`(m, LF_features)` input axis** being the right place to condition. Bibtex key: `ufnofilm2025`.

### Where this lands in the codebase

- **File:** `models/fno_coregionalization/model.py` — replace `self.b_mlp` (currently `MLP([m, m²]) → R^K`) with `B_basis(m, lf_feat)` where `lf_feat` is a pooled LF feature vector. Two options:
  - **Mode A (mean-pool LF features):** `lf_feat = mean over spatial dims of intermediate LF FNO activations at m<1`. Cheap.
  - **Mode B (cross-attention):** treat m as a query, LF feature maps as key+value, return per-K attention-weighted basis. More expensive; defer to Mode A in cycle-010.
- **File:** `models/fno_coregionalization/smoke_eval.py` — guard with `heat_test ≤ 0.0194` and `wall ≤ 1800s`.

### Recommendation

**O3 is exploratory. DEFER TO BACKLOG OR USE AS CYCLE-010 H3 (RESERVE).** Reasoning:

- The dominant residual gap is on `fno_mf_stack × poisson`, not `fno_coregionalization × poisson`. Recovering `fno_coregionalization` from 0.598 (16.6× over best) to even 0.030 would not change the composite leader, only create a second contender. Composite movement comes from beating the load-bearing cell (`fno_mf_stack × poisson = 0.038`).
- The `fno_coregionalization × poisson` failure is val→test inflation (×11), not a training-loss failure (best_val 0.054 already beats the IFC-ODE2 paper bar). The K-basis B(m) does not generalize the fidelity-conditioning pattern. Adding LF-features as input MIGHT close this gap if the val→test shift is a fidelity-magnitude-ladder issue, but it could equally make it worse (more capacity to overfit).
- NK1 is **adjacent**: NK1 closed pure-m HF conditioning. `B(m, lf_feat)` is **NOT NK1-blocked** (the LF features are precisely the "LF→HF pathway" NK1 required), but the cycle-008 falsification means we should treat this family with extra caution.

**If pursued (RESERVE only):**
- Pre-register a hard guard: heat test ≤ 0.0194 (current best is 0.0129, allow +50%).
- Pre-register: if heat test > 0.0194 OR wall > 1800s, REVERT and mark as NK4 (proposed: `INPUT_DEPENDENT_K_BASIS_ON_FNO_COREGIONALIZATION_FALSIFIED`).
- Use Mode A only (mean-pool LF features); defer cross-attention to a later cycle.

**Citations for H3 / INSPIRATION.md if pursued:** [[li2022ifc]], `liu2022neuralcoreg` ([arXiv:2109.09261]), `wang2021mfhogp` ([arXiv:2006.04972]), `ufnofilm2025` ([arXiv:2511.20543]), [[rahman2024codano]].

**Confidence: LOW-MEDIUM.** Mechanism is supported by 2021-2025 literature, but composite-mover prior is weak — recovering a non-leader cell doesn't move the metric.

**Recommendation tag:** DEFER (or RESERVE-only H3 if Strategist has budget for 3 hypotheses).

---

## O4 — γ(m, LF_features) FiLM conditioning prior art

**Question.** NK1-safe alternative to cycle-008 H2. How is LF_features pooled (mean, max, attention)?

### External findings

1. **UFNO-FiLM** ([arXiv:2511.20543], Nov 2025) — discussed in O3. Context = scalar parameters + spatial LF features (permeability field). The paper doesn't explicitly disclose pooling strategy in the abstract, but FiLM context vectors are conventionally fixed-length, so a pooling step is implicit. **First direct precedent for γ(scalar, LF_field) in an FNO-family architecture.** 21% MAE gain on multiphase flow. Bibtex key: `ufnofilm2025`.

2. **beggs2025pdecond**, **herde2024poseidon** (in archive). Both use γ(scalar) without LF features — these are HF-only conditioning, exactly the NK1 anti-pattern in our project. Not directly useful as NK1-safe precedent.

3. **rahman2024codano**. Codomain-attention conditioning. Treating m as a codomain axis allows attention-pooling over LF feature tokens. NeurIPS 2024.

4. **Conditional FiLM for molecular property prediction** ([arXiv:2604.06558], 2026) — uses γ and β parameterized by MLPs with mean+max pooled context. The dual-pool pattern is the modern recommended choice (vs. mean-only).

5. **PI-RINO** ([arXiv:2510.23810], Oct 2025) — function-encoder dictionary learning. Two-stage: encode LF function via SIREN dictionary, then condition operator MLP on the embedding. Different mechanism (dictionary projection vs. FiLM) but the **two-stage LF-encode-then-condition pattern** is the same architectural family.

### Where this lands in the codebase

If pursued as a new family:
- **NEW family:** `models/fno_coreg_conditioned_v2/` (or rewrite the empty `models/fno_coreg_conditioned/` package).
- **File:** `model.py` — FNOBlock with FiLMNorm replacing GroupNorm; `γ, β = MLP([m, m², pooled_lf_feat])`.
- **File:** `smoke_eval.py` — needs a forward pass that **runs LF FNO first, pools its features, then runs HF FNO conditioned on the pooled vector**. Two-pass inference; ~1.5× wall vs single FNO.
- **File:** `INSPIRATION.md` — cite [[beggs2025pdecond]], [[herde2024poseidon]], `ufnofilm2025`, [[rahman2024codano]], [[li2020fno]], [[li2022ifc]].

### Recommendation

**O4 is the right NK1-safe formulation but is HIGHER COST than H1/H2 and lower in composite prior.** Reasoning:

- A fresh family takes a full package-scaffold build (model.py, smoke_eval.py, data.py, manifest.json, INSPIRATION.md, full_config.json) — significant Builder surface vs. H1 (one-file SMOKE_DEFAULTS edit) or H2 (one-file logic addition).
- The same composite-mover analysis as O3 applies: even a successful new family lands on Poisson as a **second contender** unless it beats 0.0381. Cycle-008 B1 (`fno_coreg_conditioned` with γ(m, m²) only) landed at 12.6× over leader. The LF-features addition is a structural fix to the NK1 failure, but the family is otherwise unchanged and was untested on the IFC datasets.

**Recommendation tag:** DEFER TO BACKLOG. Pursue only if H1+H2 both fail to break the 0.030 Poisson floor. Add to `.factory/strategy/backlog.md` with citations.

**Confidence: LOW for cycle-010 (high implementation surface, weak composite prior).** Confidence MEDIUM for the **technique itself** at later cycles.

**Recommendation tag:** DEFER TO BACKLOG.

---

## O5 — 2025/2026 MF surrogate / multi-fidelity field-prediction work not yet in papers_summary.csv

**Question.** Search broadly for 2025-2026 MF surrogate work not yet catalogued.

### New citation candidates (cycle-010 web round)

| Candidate bibtex_key | Paper | Year/Venue | Use |
|---|---|---|---|
| `mutransferfno2025` | μTransfer-FNO: Maximal Update Parametrization for FNO ([arXiv:2506.19396]) | arXiv Jun 2025 | O1 — supports width-scaling with LR-transfer for FNO. Backs the cycle-010 H1 hidden=96 step. |
| `ufnofilm2025` | Feature-Modulated UFNO for Multiphase Flow ([arXiv:2511.20543]) | arXiv Nov 2025 | O3/O4 — direct precedent for γ(scalar, LF_field) on FNO-family. 21% MAE gain. |
| `pirino2025` | Physics-informed Multi-resolution Neural Operator (PI-RINO) ([arXiv:2510.23810]) | arXiv Oct 2025 | Multi-resolution (NOT multi-fidelity) — function-encoder dictionary learning. Backlog reference. |
| `fnospectralperspective2024` | Toward Better Understanding of FNO from Spectral Perspective ([arXiv:2404.07200]) | arXiv Apr 2024 | O1 — saturation warning on enlarging Fourier kernel. Backs cycle-010 H1's HF-modes ≤ 24 hold. |
| `mfbpinn2026` | MF-BPINN: Multi-Fidelity PINN with Bayesian UQ ([arXiv:2602.01176]) | arXiv 2026 | Adjacent (PINN family, not FNO). Hierarchical residual learning across fidelities. Backlog reference. |
| `liu2022neuralcoreg` | Scalable Multi-Task GPs with Neural Embedding of Coregionalization ([arXiv:2109.09261]) | KBS 2022 | O3 — canonical input-dependent coregionalization precedent. **Pre-2024 but new to our archive.** |

Total ready for `papers_summary.csv` after cycle-010: **15 keys** (10 prior + 5 new validated; the `stresstest2025fno` arXiv ID was corrected from `2501.11428` to `2601.11428` this cycle).

### Recommendation

These citations populate the `INSPIRATION.md` and `papers_summary.csv` (human-action). They do not by themselves constitute a hypothesis — most are inputs to H1/H2/H3.

**Confidence: HIGH (citations validated via search abstracts).**

**Recommendation tag:** ARCHIVE-ONLY (no direct hypothesis from O5 alone).

---

## Cross-Cycle Pattern: capacity-axis returns on `fno_mf_stack`

Cycle-by-cycle capacity progression and the per-step Poisson elasticity:

| Cycle | hidden | modes_per_level | n_blocks | params | Poisson nRMSE | Δ Poisson | Δ wall |
|---|---|---|---|---|---|---|---|
| 002-H4 | 32 | (4,8,12,12) | 3 | ~250k | 0.0596 | (baseline) | (baseline) |
| 008 baseline | 32 | (4,8,12,12) | 3 | ~250k | 0.0596 | 0% (no change) | — |
| 009-h1h2 | 64 | (4,8,16,20) | 4 | ~1.0M | 0.0381 | **−36%** | 414s |
| 010 H1 (proposed) | 96 | (4,8,16,24) | 4 | ~2.0M | 0.030-0.034 | **−10 to −22%** | est. 700-900s |
| 010 alt-aggressive | 128 | (4,8,16,24) | 5 | ~3.5M | 0.027-0.032 | **−15 to −29%** | est. 1100-1400s |

**Interpretation:**
- Cycle-009 step (4× params, ~+1.0M absolute) moved Poisson −36% — the slope of `log(nRMSE) / log(params)` was approximately **−0.39**.
- A second 2× param step (1.0M → 2.0M) at the **same slope** would imply −27% (0.0381 → 0.028). However, the published evidence (`stresstest2025fno`, `fnospectralperspective2024`, `pretrain_lowerdims2024`) and the in-tree fno_coregionalization saturation (paper-config at 2.6M, Heat plateaued at 0.0129) both argue for **slope flattening on the second step**. Realistic expectation: **−10 to −22%** Poisson, i.e., 0.030-0.034.
- The slope flattens but is positive — there IS more capacity-axis runway, just less than a naive linear-in-log extrapolation predicts. **The capacity axis is not yet exhausted on `fno_mf_stack`**, but cycle-011 is likely to hit diminishing returns at the hidden=128 / modes=24 ceiling unless we change axis (curriculum, architecture).

This is the central evidence backing **H1 (capacity bump) as composite-mover and H2 (curriculum) as the next axis once H1 saturates.**

---

## Synthesis — Cycle-010 buildable interventions, ranked

### Buildable interventions

| Rank | Hyp | Family | Surface | Expected Poisson | Expected composite | Wall | Risk | NK status |
|---:|---|---|---|---|---|---|---|---|
| **1** | **H1 (LEAD)** | `fno_mf_stack` | `smoke_eval.py:39-55` SMOKE_DEFAULTS only | 0.030-0.034 (−10 to −22%) | 0.0197-0.0212 (−5 to −11%) | ~700-900s (kill 1500s) | LOW (in-family capacity; cycle-009 H1+H2 precedent) | NK-clear |
| **2** | **H2 (SECONDARY)** | `fno_mf_stack` | `smoke_eval.py:171-291` training loop + `compute_losses` | 0.030-0.035 (−10 to −20%) | 0.0197-0.0220 (−1 to −11%) | ~1500-1700s (kill 1800s) | MEDIUM (novel NK2 carve-out; dual kill-switch) | NK2-carve-out-clear |
| 3 | H3 (RESERVE) | `fno_coregionalization` | `model.py` B-basis + smoke guard | 0.10-0.30 (recovers from 0.598 but not leader) | 0.022 (no composite move) | ~600-800s | MEDIUM-LOW composite-impact; LOW-MED loss | NK1-adjacent |
| 4 | (DEFER) NEW `fno_coreg_conditioned_v2` | full new family | full scaffold | speculative | speculative | est. 25-30 min | HIGH implementation, MED composite | NK1-safe |

### Ranking rationale

The top 2 are both buildable on `fno_mf_stack` (the load-bearing composite cell). H1 (capacity bump) carries the strongest prior — the cycle-009 −36% Poisson result is the project's largest in-family delta. H2 (curriculum carve-out) is a fresh-axis lever with NK2-clear status and a structural precedent ([[yang2025mfdeeponet]]'s freeze-LF pattern); confidence is one notch lower because the freeze-LF carve-out has not been measured in this codebase yet.

**Recommended Strategist allocation** (Strategist owns final hypothesis count; this is informative):
- If `max_new ≥ 2`: H1 + H2, landed as SEPARATE PRs in order (H1 first, attest new baseline, then H2).
- If `max_new = 1`: H1 only.
- If `max_new ≥ 3`: H1 + H2 + H3 (RESERVE — only if Strategist confirms backlog has bandwidth).

**Do NOT bundle H1 + H2** — they share `smoke_eval.py:39-55` and would confound attribution.

**Do NOT pursue O4 (new `fno_coreg_conditioned_v2` family)** this cycle — high implementation cost, weak composite prior. Add to backlog with citations.

---

## NK-zone sidesteps (all proposed hypotheses)

- **NK1** (pure m-conditioning on HF-only FNO, cycle-008 H2):
  - H1 sidesteps (no FiLM, no conditioning change).
  - H2 sidesteps (no conditioning change; curriculum on existing arch).
  - H3 is NK1-adjacent — `B(m, lf_feat)` includes the LF pathway, so structurally distinct from NK1, but the family is the one where NK1 was set. Pursue with caution.

- **NK2** (frozen-LF curricula on **co-evolved residual ladders**, cycle-008 H3):
  - H1 sidesteps (no curriculum).
  - H2 takes the published carve-out. `fno_mf_stack`'s LF/HF-independent design (`models/fno_mf_stack/model.py:165-168` — 4 separate `SmallFNO` modules) is the precise structural condition NK2 calls out. **Dual kill-switch (absolute + inter-stage) is MANDATORY.**
  - H3 sidesteps (no curriculum).

- **NK3** (MFRNP loss-weight transfer to coregionalization family, cycles 003/006/007):
  - H1 sidesteps (canonical (2.0, 0.25) Poisson weights unchanged).
  - H2 sidesteps (canonical weights unchanged; staging only).
  - H3 sidesteps (basis parametrization change is not loss-weight transfer).

All three hypotheses are NK-clear modulo the named carve-outs.

---

## Mutable-surface map (cycle-010)

- `models/fno_mf_stack/smoke_eval.py` — H1 (SMOKE_DEFAULTS at lines 39-55) ; H2 (training loop / `compute_losses` / optimizer construction).
- `models/fno_mf_stack/full_config.json` — H1 (optional reference target bump; smoke is canonical source).
- `models/fno_mf_stack/model.py` — H2 (no edit; `lf_fnos[*].requires_grad_(False)` invoked from `smoke_eval.py`).
- `models/_common/recipe_hash.py` — H2 (read-only; SMOKE_DEFAULTS additions auto-hashed).
- `models/fno_coregionalization/model.py` + `smoke_eval.py` — H3 RESERVE only.

---

## Builder must-verify checklist (constraint from factory.md)

- [ ] `cd /orcd/data/faez/001/nick/mf_field/factory_mffp && uv run python -m models.fno_mf_stack.smoke_eval --epochs 2 --dataset_dir data/ifc_heat --out /tmp/x.json --ckpt_dir /tmp/c --seed 0` passes (catches H2's stage-transition edge cases with epochs=2 = 1 LF + 1 HF).
- [ ] `models/fno_mf_stack/INSPIRATION.md` cites the new bibtex keys.
- [ ] `recipe_hash` reflects new SMOKE_DEFAULTS (H1: capacity fields; H2: `pretrain_frac`, `stage2_freeze_lf`).
- [ ] No external API / weight downloads.
- [ ] Wall ≤ 25-30 min on H100.

---

## References

External (web round this cycle):

- [μTransfer-FNO (Li et al. 2025, arXiv:2506.19396)](https://arxiv.org/abs/2506.19396)
- [Forcing and Diagnosing Failure Modes of FNO (stresstest2025fno, arXiv:2601.11428)](https://arxiv.org/abs/2601.11428)
- [Toward a Better Understanding of FNO from a Spectral Perspective (arXiv:2404.07200)](https://arxiv.org/abs/2404.07200)
- [Feature-Modulated UFNO (arXiv:2511.20543)](https://arxiv.org/abs/2511.20543)
- [Pretraining a Neural Operator in Lower Dimensions (arXiv:2407.17616)](https://arxiv.org/abs/2407.17616)
- [Lyu 2023 MF-FNO (arXiv:2304.06972)](https://arxiv.org/abs/2304.06972)
- [Jiang 2023 MF-FNO GCS (arXiv:2308.09113)](https://arxiv.org/abs/2308.09113)
- [DPOT (Hao et al. 2024, arXiv:2403.03542)](https://arxiv.org/abs/2403.03542)
- [Physics-Guided MF-DeepONet (arXiv:2503.17941)](https://arxiv.org/abs/2503.17941)
- [Scalable Multi-Task GPs with Neural Embedding of Coregionalization (arXiv:2109.09261)](https://arxiv.org/abs/2109.09261)
- [MFHoGP (arXiv:2006.04972)](https://arxiv.org/abs/2006.04972)
- [Physics-informed Multi-resolution Neural Operator (arXiv:2510.23810)](https://arxiv.org/abs/2510.23810)
- [MF-BPINN (arXiv:2602.01176)](https://arxiv.org/abs/2602.01176)

Archive (read this cycle):

- `[[niu2024mfrnp]]`, `[[li2022ifc]]`, `[[li2020fno]]`, `[[anisotropic-spectral-modes-fno]]`, `[[lf-hf-pretrain-fraction-survey]]`, `[[research-cycle-008]]`, `[[research-cycle-009]]`, `[[cao2025mflno]]`, `[[beggs2025pdecond]]`, `[[herde2024poseidon]]`, `[[rahman2024codano]]`, `[[pan2022hyperfno]]`, `[[yang2025mfdeeponet]]`, `[[papers-summary-csv-state]]`.

In-tree (read this cycle):

- `models/fno_mf_stack/model.py`, `models/fno_mf_stack/smoke_eval.py`, `models/fno_mf_stack/full_config.json`
- `references/external_sota/mfrnp/upstream/Poisson5_config.yaml`, `pde_config.yaml`
- `.factory/research/runs/cycle-010-baseline/failure_analysis.md`
- `.factory/reviews/ceo-verdict-failure_analyst.md`
