---
name: research-cycle-002
description: Cycle-002 Researcher (R1.5) Mode-4 findings for factory_mffp. The proposed hybrid (continuous-m basis head over MFRNP-style residual stack with FNO backbones and decoder-in-the-aggregation) has NO published precedent in 2020-2026 MF field-prediction literature. Closest analogue is xing2020deepcoreg / ResPCA (residual + low-rank basis on a GP backbone with discrete fidelities) — empirical backing that the compose itself is viable at lower granularity. Poisson 0.0979 → 0.036 paper-bar gap decomposes into 4 orthogonal levers (capacity, LF-down-weighting, epochs, basis K); MFRNP Poisson5 config's HF:LF = 2:0.25 LF-down-weighting is verbatim pre-registered and free. 7 new 2024-2026 papers proposed for papers_summary.csv (fixed-surface human action). CEO-approved direction — H4 (fno_mf_stack capacity + Poisson-loss bump) + H3 (fno_coreg_residual hybrid), in priority order.
metadata:
  type: project
tags:
  - factory
  - source
  - factory_mffp
  - cycle-002
  - research
project: factory_mffp
cycle: 002
phase: research
date: 2026-05-15
source: factory-archivist
ceo_verdict: PROCEED
---

# Research — Cycle 002 (factory_mffp)

## Cycle Setup
- **Phase:** R1.5 Researcher Mode-4 web research (post-failure-analysis, pre-strategist).
- **Trigger:** Failure Analyst surfaced F5 `INVERSE_COMPLEMENTARY_FAMILIES` — H1 wins `ifc_heat` outright (0.0154, beats paper 0.074 by 4.8×), H2 wins `ifc_poisson` (0.0979, 2.7× over paper). Neither family beats the paper bar on both datasets on its own. CEO requested literature spot-check on (a) hybrid composability (b) smoke-vs-full config best practices (c) Poisson 0.0979 → 0.036 gap decomposition.
- **CEO verdict:** **PROCEED**. All five posed questions answered concretely with citations; no material issues. See [[ceo-verdict-researcher-cycle-002]] (file `.factory/reviews/ceo-verdict-researcher.md`).
- **Source-of-truth:** `.factory/strategy/research.md` §"Cycle-002 Research — Hybrid Architectures & Capacity Diagnostics (Mode 4)" (lines ~280+).

## Headline Findings

### (a) Hybrid novelty — proposed cycle-002 H3 `fno_coreg_residual` is NOVEL

The specific compose **"FNO + continuous-m coregionalization head OVER an MFRNP-style residual stack with decoder-in-the-aggregation"** appears to be **novel** in the published MF field-prediction literature (2020-2026). Five literature traces are relevant; **none** composes the exact hybrid. Three are direct architectural precedents at lower granularity:

| Precedent | What it composes | Why it differs |
|---|---|---|
| **xing2020deepcoreg / ResPCA** ([arXiv:1910.07577](https://arxiv.org/abs/1910.07577), J. Comput. Phys. 2020) | Sequential per-fidelity PCA-GP models *on the residual* between LF prediction and HF ground truth. Both **low-rank basis** (PCA) and **residual stacking** are present, sequentially across discrete fidelities. | GP backbone (not FNO/NP); per-fidelity discrete bases (not continuous-m); residual is GP-only, no decoder in the aggregation. **The most direct architectural precedent** — confirms residual + low-rank basis is a viable compose — but fundamentally different backbone and discrete fidelity index. |
| **niu2024mfrnp / MFRNP** ([arXiv:2402.18846](https://arxiv.org/abs/2402.18846), ICML 2024) | Residual stack with decoder-in-the-aggregation across discrete fidelity levels. No continuous-m basis. | Already H2. |
| **li2022ifc / IFC-ODE2, IFC-GPODE** ([arXiv:2207.00678](https://arxiv.org/abs/2207.00678), NeurIPS 2022) | Continuous-m basis `B(m)·h(x,m)` with neural-ODE (or GP) on the basis function. No residual stacking across fidelities. | Already H1. |
| **lin2024continuar / ContinuAR** ([ACM DL](https://dl.acm.org/doi/10.5555/3666122.3668170)) | Continuous autoregression via a fidelity differential equation (FiDE); rank-1 approximation. Continuous fidelity, but no residual stack + decoder. | Confirms continuous-m is an active research line; closer to H1 than to a hybrid. |
| **davis2025rmfnn / Residual MFNN Computing** ([arXiv:2310.03572](https://arxiv.org/abs/2310.03572), [BIT Numer. Math. 2025](https://link.springer.com/article/10.1007/s10543-025-01058-9)) | Two-network residual MF: net1 learns LF→HF residual; net1 then generates synthetic HF data to train net2 as the final HF surrogate. Residual learning + data augmentation, no coregionalization basis. | Orthogonal lever (data augmentation); future hypothesis on top of H1 or H2. |

**Verdict:** the proposed hybrid is **first-principles defensible** with weak (non-FNO, non-NP) empirical backing from ResPCA. Builder must cite ResPCA + IFC + MFRNP + FNO in `models/fno_coreg_residual/INSPIRATION.md` and explicitly label as **"hybrid extension, no direct precedent in published MF field-prediction literature."**

### (b) Poisson 0.0979 → 0.036 gap — 4 orthogonal levers with literature backing

The paper bar `li2022ifc` IFC-ODE2 at K=20 = **0.036** is 2.7× lower than H2's 0.0979. MFRNP's 0.0046-0.0076 numbers come from a *different* setup (5 vs 4 fidelities; different ns split) and are **not directly comparable**. The architectural template that matches our paper bar is IFC, not MFRNP — yet H2 (MFRNP-template) already wins Poisson over H1 (IFC-template) in our setup. The 3× gap to paper bar is therefore a **capacity / training / loss-weighting gap, not an architectural gap**:

| Lever | Evidence | Cost | Apply where |
|---|---|---|---|
| **Bump hidden / z_dim 16 → 32–64** | MFRNP paper uses hidden=32 (Heat/Poisson) and 128 (Fluid). H1 ran at hidden=64 (4.75M params). H2 ran at hidden=16 (97k params). | Param ↑4-16×, wall ↑2-3×. Within smoke budget at 32. | H2 `SMOKE_DEFAULTS` (pre-registered). |
| **LF-down-weighting (`lower_fidelity_weight=0.25` for Poisson)** | MFRNP paper Poisson5 config explicitly uses HF:LF = 2:0.25 = 8:1. The published `pde_config.yaml` (uniform) is for Heat. **Poisson-specific, verbatim pre-registered.** | **Free** (loss-coefficient edit only). | Both H1 and H2; per-dataset loss weighting in `data.py` or `smoke_eval.py`. |
| **Bump epochs (200 → as many as fit)** | MFRNP trains 50,000 epochs. IFC trains 5,000. We train 200. Order-of-magnitude underfit. | Wall-time-bound. At hidden=32, modes=(4,8,12,12), 3 blocks, ~5–10 min smoke leaves 500–2000 epochs of headroom. | Both H1 and H2 smoke. |
| **Larger basis K in H1 / larger z_dim in H2** | IFC paper: K=20 → 0.036; K=5,10,15 worse (K-sweep explicit). H1 currently K=10. MFRNP Poisson5: z_dim=32. | Param ↑2-3× linear in K. | H1 if revisited; H2 stack-decoder hidden could go to 32. |

**The LF-down-weighting knob is the standout free win** — verbatim in MFRNP `Poisson5_config.yaml` (`fidelity_weight=2, lower_fidelity_weight=0.25`), not in our H1/H2 code, and adds zero compute. Strategist must include it in cycle-002 H4 as a second knob, not as an "extension" — both knobs are pre-registered in the MFRNP Poisson-tuned config.

### (c) Smoke-vs-full config — three references on capacity-vs-ranking

1. **IFC paper** sweeps `K ∈ {5,10,15,20}` on Poisson and Heat; K=20 produces the 0.036 paper bar; smaller K under-performs. Architecture: `g_width=f_width=A_width=40, g_depth=f_depth=A_depth=2, max_epochs=5000, max_lr=1e-2, min_lr=1e-3, solver=dopri5, int_steps=2` (see [github.com/shib0li/Infinite-Fidelity-Coregionalization/infras/configs.py](https://github.com/shib0li/Infinite-Fidelity-Coregionalization/blob/main/infras/configs.py)). **K-sweep is explicit** — confirms rank/basis dim is the canonical capacity knob, and small K can flip a within-family ranking.

2. **MFRNP Poisson5 vs default `pde_config.yaml`**: Poisson5 uses `hidden_dim=32, z_dim=32, hidden_layers=2, epochs=50000, batch_size=2048, fidelity_weight=2, lower_fidelity_weight=0.25`. The default (for Heat5, Poisson2/3) uses identical sizes but `lower_fidelity_weight=1` (uniform). Fluid bumps to `hidden_dim=z_dim=128`. **Three insights:**
   - Hidden-dim is task-bound, not budget-bound (Heat/Poisson 32 in published config; bumping past that is feasible).
   - **Poisson specifically uses LF-down-weighting** — a Poisson-only training-hyperparameter trick the published paper found load-bearing. Our H2 currently uses uniform per-sample MSE.
   - Epoch count is 50,000 (250× our 200). Even after capacity bump, our training schedule is short.

3. **Spectral-bias / capacity-bound rule of thumb** ([arXiv:2404.07200](https://arxiv.org/html/2404.07200v1) "Toward a Better Understanding of FNO"): FNO ablations at `modes=24-32, width=30-100` are standard. Below `modes=8` per axis on 64×64, dominant Fourier components of smooth PDE solutions are clipped. **H2's smoke `modes_per_level=(4,5,5,5)`** on fidelities (8,16,32,64) means the L4 FNO retains only 5 of 32 possible modes — **almost certainly under-resolved** for Heat's smooth-but-not-trivial dynamics. The cycle-002 spec-aligned `(4,8,12,12)` is in the standard FNO range; `hidden=32` is the MFRNP/IFC-baseline minimum; `hidden=64` is H1-class.

**Smoke-vs-full guidance:** no MF surrogate paper explicitly reports an ablation where a smaller smoke config *flips* the architecture ranking between families — but the IFC K-sweep and the MFRNP hidden-dim difference between Poisson (32) and Fluid (128) imply authors expected capacity to matter qualitatively, not just quantitatively. The H2 cycle-001 Heat regression (8.3× worse at 1/49 the params) is consistent with capacity flipping a within-suite ranking even if the literature doesn't pre-register this kind of regression. Builder rule: `smoke_eval.py` should read non-budget-bound hyperparameters from `full_config.json`. See [[patterns]] §"`smoke_eval.py` may not consume `full_config.json`".

### (d) Recommendation — order operations: H4 (capacity+loss) first as gate; H3 (hybrid) second

- **H4 / `fno_mf_stack` capacity + Poisson-loss bump** is cheap, decisive, pre-registered. **Run first.** If `hidden=32, modes=(4,8,12,12), 3 blocks` recovers `ifc_heat ≤ 0.05` and preserves `ifc_poisson ≤ 0.10`, H2 becomes a **strict superset of H1**. At that point the hybrid (H3) is no longer needed for the synthesis goal — it would only matter if the hybrid additionally drops Poisson toward 0.036.
- **H3 / `fno_coreg_residual`** is the bigger swing. **Novel compose** (no published precedent), but the underlying inductive biases are independent and the closest precedent (ResPCA) supports residual + basis as a viable architecture. **Expected best case:** `sqrt(0.0154 · 0.0979) ≈ 0.039` composite, both datasets near or below paper bar. **Risk:** model is heavier; optimization may not preserve both wins. Builder must ship with full-config sizes (no SMOKE_DEFAULTS regression).
- **Two-track logic for `hypothesis_budget.max_new = 2`:** run **H4** and **H3** as the two cycle-002 hypotheses — complementary, not competing. H4 establishes whether the H2 inductive bias is sufficient at full capacity; H3 establishes whether composing both inductive biases is strictly better than either.
- **Cross-cutting Poisson knob (apply to both):** add HF-up-weighted loss (`HF_weight=2, LF_weight=0.25`, per MFRNP Poisson5 config) — free and published-Poisson-tuned.

## New 2024-2026 Paper Rows Proposed for `papers_summary.csv` (fixed-surface human action)

The cycle-001 archive already covers `li2022ifc, niu2024mfrnp, gladstone2024mfgunet, taghizadeh2024mfgnn, yang2025mfdeeponet, nietocentenero2025mfae, sung2026fire, li2020fno, wu2024transolver, penwarden2022mfpinns`. Cycle-002 surfaced **7 additional rows**. Since `papers_summary.csv` is at repo root (referenced by `factory.md:39`, `models/README.md:36`, `HOWTO.md:61`) and **outside `models/**`**, populating these is **human action**, not in-cycle code:

| bibtex_key | source | one-line summary | relevance |
|---|---|---|---|
| **xing2020deepcoreg** | Xing, Shi, Kirby, Zhe. J. Comput. Phys. 2020. [arXiv:1910.07577](https://arxiv.org/abs/1910.07577), [code](https://github.com/wayXing/DC) | ResPCA — sequential per-fidelity PCA-GP on the LF→HF residual. Combines low-rank basis + residual stacking. | **Direct precedent for H3 `fno_coreg_residual`.** Cite in INSPIRATION.md alongside `li2022ifc` + `niu2024mfrnp`. |
| **lin2024continuar** | ContinuAR — continuous autoregression for infinite-fidelity fusion. [ACM DL](https://dl.acm.org/doi/10.5555/3666122.3668170) | Generalizes autoregression to a linear fidelity differential equation; rank-1; arbitrary MF data structure. | Alternative continuous-m architecture; backlog candidate. |
| **davis2025rmfnn** | Davis, Motamed, Tempone. BIT Numer. Math. 2025. [arXiv:2310.03572](https://arxiv.org/abs/2310.03572), [DOI](https://doi.org/10.1007/s10543-025-01058-9) | Two-network residual MF: net1 learns LF→HF residual; trained net synthesizes additional HF data for net2 surrogate. | Orthogonal lever (synthetic HF data augmentation); future hypothesis on top of H1 or H2. |
| **hu2025hufno** | "Hybrid U-Net + FNO for turbulent flows with mixed BCs." [arXiv:2504.13126](https://arxiv.org/abs/2504.13126) | FNO + UNet hybrid for non-periodic BCs; UNet handles local skip-connection multiscale, FNO handles spectral. | Architectural precedent for **hybrid backbones inside a single network**. |
| **wen2022ufno** | "U-FNO — enhanced FNO for multiphase flow." [Semantic Scholar](https://www.semanticscholar.org/paper/U-FNO-an-enhanced-Fourier-neural-operator-learning-Wen-Li/bd1a1cea6fab16c00e3519745ff798195332fcdd) | U-Net path inside FNO blocks. Improves FNO in data-limited and multiscale regimes. | Confirms FNO can be composed with auxiliary modules inside one network. |
| **rahman2025adaptfno** | AdaptFNO — adaptive FNO with global low-res + local high-res branches and cross-attention. [NeurIPS ML4PS 2025](https://ml4physicalsciences.github.io/2025/files/NeurIPS_ML4PS_2025_96.pdf) | Cross-resolution attention; implicit multi-fidelity via global/local split. | Cross-resolution attention as fidelity-fusion primitive — backlog. |
| **fno_resnet_2024** | "FResNet++" — FNO in ResNet residual blocks for two-phase flow (cited in U-FNO survey). | Residual-block-of-FNOs structural pattern (single-fidelity). | Single-fidelity cousin of H2's per-fidelity FNO stack. |

See [[papers-summary-csv-state]] for the human-action context.

## CEO-Approved Cycle-002 Hypothesis Pair (final, post-Researcher)

1. **H4 = `fno_mf_stack` capacity + Poisson-loss bump.** Branch from `experiment/2-fno_mf_stack` (cycle-001 H2 code on disk, off-master). Two pre-registered MFRNP Poisson5 knobs:
   - (a) bump `SMOKE_DEFAULTS` from `(hidden=16, modes=(4,5,5,5))` to `(hidden=32, modes=(4,8,12,12), 3 blocks)`.
   - (b) add per-fidelity loss weighting `HF_weight=2, LF_weight=0.25` (Poisson-specific, verbatim from MFRNP `Poisson5_config.yaml`).
   Mutable surface: `models/fno_mf_stack/**`. Growth dimension: `experiment_diversity` (capacity dimension on existing inductive bias). Backlog item: cycle-001 archive's "fno_mf_stack smoke-defaults bump" pre-registration.

2. **H3 = `fno_coreg_residual` (novel hybrid).** Brand-new family at `models/fno_coreg_residual/`. Branch from master. Architecture: H2's per-fidelity FNO stack with MFRNP-style decoder-in-the-aggregation, HF head replaced with H1's continuous-m basis: `y(x) = aggregate(decoded_LFs upsampled to 64×64) + Σ_k B_k(m)·h_k(x)`, `B(m) = MLP_B([m, m²])`, `K=10`. Full-config sizes from start (`hidden=64, modes=(4,8,12,12), 3 blocks`) to avoid F4. Per-fidelity output normalization mandatory. INSPIRATION.md cites `xing2020deepcoreg` + `li2022ifc` + `niu2024mfrnp` + `li2020fno` and explicitly labels as "hybrid extension, no direct precedent in published MF field-prediction literature." Mutable surface: `models/fno_coreg_residual/**`. Growth dimension: `capability_surface` (new family). Backlog item: cycle-001 archive's "H1+H2 hybrid" candidate.

**CEO scope/leakage checks** (re-verified at hard gate): every mentioned file is in `mutable_surfaces` (`models/**`); no specific ground-truth values encoded in hypothesis text.

## Cycle-002 References (new this cycle)

- `xing2020deepcoreg` / ResPCA — [arXiv:1910.07577](https://arxiv.org/abs/1910.07577), [code](https://github.com/wayXing/DC)
- `lin2024continuar` — [ACM DL](https://dl.acm.org/doi/10.5555/3666122.3668170)
- `davis2025rmfnn` — [arXiv:2310.03572](https://arxiv.org/abs/2310.03572), [BIT Numer. Math.](https://link.springer.com/article/10.1007/s10543-025-01058-9)
- `hu2025hufno` — [arXiv:2504.13126](https://arxiv.org/abs/2504.13126)
- `wen2022ufno` — [Semantic Scholar](https://www.semanticscholar.org/paper/U-FNO-an-enhanced-Fourier-neural-operator-learning-Wen-Li/bd1a1cea6fab16c00e3519745ff798195332fcdd)
- `rahman2025adaptfno` — [NeurIPS ML4PS 2025](https://ml4physicalsciences.github.io/2025/files/NeurIPS_ML4PS_2025_96.pdf)
- MFRNP Poisson5 / Fluid / default training configs — [github.com/Rose-STL-Lab/MFRNP](https://github.com/Rose-STL-Lab/MFRNP) (verbatim: `hidden_dim=32, z_dim=32, epochs=50000, batch_size=2048, fidelity_weight=2, lower_fidelity_weight=0.25` on Poisson5)
- IFC default training config — [github.com/shib0li/Infinite-Fidelity-Coregionalization/infras/configs.py](https://github.com/shib0li/Infinite-Fidelity-Coregionalization/blob/main/infras/configs.py) (verbatim: `max_epochs=5000, max_lr=1e-2, min_lr=1e-3, g_width=f_width=A_width=40, g_depth=f_depth=A_depth=2, solver=dopri5, int_steps=2`)
- "Toward a Better Understanding of FNO" — [arXiv:2404.07200](https://arxiv.org/html/2404.07200v1)

## Related Notes

- [[factory_mffp]] — project dashboard
- [[cycle-001-summary]] — cycle-001 close-out, pre-registered cycle-002 hypotheses
- [[failure-analysis-cycle-002]] — cycle-002 failure analysis (F1/F2/F3 + new F4/F5)
- [[factory_mffp-001-experiment]] — H1 final outcome (FNO + coregionalization)
- [[factory_mffp-002-experiment]] — H2 final outcome (FNO + MFRNP residual stack)
- [[patterns]] §"Coregionalization head and MFRNP residual stack are a complementary architecture pair" — F5 in patterns form
- [[patterns]] §"`smoke_eval.py` may not consume `full_config.json`" — F4 in patterns form
- [[patterns]] §"Per-fidelity output normalization" — mandatory cross-cutting hygiene
- [[patterns]] §"Continuous-fidelity index" — architectural rule satisfied by both H4 and H3
- [[paper-baselines-proposals]] — human-action sibling for `baselines/paper_baselines.json`
- [[papers-summary-csv-state]] — human-action sibling for `papers_summary.csv` (7 new rows queued)
- Source papers: [[li2022ifc]], [[niu2024mfrnp]], [[li2020fno]], [[gladstone2024mfgunet]], [[taghizadeh2024mfgnn]], [[yang2025mfdeeponet]], [[nietocentenero2025mfae]], [[sung2026fire]], [[wu2024transolver]]
- New this cycle (pending source notes if/when promoted to in-depth study): `xing2020deepcoreg`, `lin2024continuar`, `davis2025rmfnn`, `hu2025hufno`, `wen2022ufno`, `rahman2025adaptfno`, `fno_resnet_2024`
