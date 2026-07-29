# Websearch Report — Stream `s4_hybrid_routing`, Batch 2

**Stream**: `s4_hybrid_routing`
**Batch**: 2
**Total iterations**: 5 (**cap hit** — noted in `iteration_5.md` header)
**WebSearch calls**: 15 (3 per iteration, never more)
**WebFetch calls**: 14 (10 returned readable content, 1 of those unusable (GAOT's ablation appendix), 4 dead: the AAAI Transolver PDF 1.5 MB binary,
`arxiv.org/html/2605.08318` HTTP 404 — recovered via `/abs/`, `arxiv.org/pdf/2310.03572`
7.3 MB binary, `arxiv.org/pdf/2606.07153` 895 KB binary/metadata-only)
**Cap hit**: **YES**

**What this batch had to decide.** B1 (`experiment_cards/s4_hybrid_routing/batch_1/B1.json`
part 7) licenses exactly two directions — repair the alpha gate's scoring split
(keeping the shrinkage line search) and feed the corrector a dense LF field
instead of 1024 points — and REFUSES spatially-resolved routing on measured
headroom (per-pixel −1.31%/−6.18%/−3.54%; per-sample oracle ≤5.33%; all inside
the floors in `state/noise_floor.json`). s6 owns local dense-LF correction and s2
owns the LF-residual FNO control, so this search had to establish, adversarially,
what of s4's remaining territory — the **attention corrector class** — is new.

## Search trace

### Turn 1 — the shrinkage / held-out gate-fitting axis → `iteration_1.md`
Terms (why): stacking-with-shrinkage theory (the estimator our `alpha` line
search actually is), the MF `rho`-scale-factor literature, and the James–Stein
framing the orchestrator asked for by name. s6-B2 had already nailed plain
out-of-fold stacking, so shrinkage was the open half.
- Shrunk, non-negativity-constrained blend weights are proved theory: *"the
  solution `alpha_hat` to program (8) satisfies `sum alpha_hat_k <= 1`"* and the
  stacked model's risk is *"strictly less than ... the data-selected best single
  model"* (conditionally) [cite: https://arxiv.org/html/2309.09880 — fetched].
  **Adversarial catch**: that variant *"does NOT require cross-validated/out-of-fold
  predictions"*, so it is NOT a citation for the split repair.
- *"combining two linear smoothers by minimizing Mallows' Cp yields a James–Stein
  estimator"*, in a paper the fetch confirms is *"purely statistical regression,
  not PDE/operator learning"* [cite: https://arxiv.org/html/2309.14596 — fetched].
- MF's single scalar is `rho`, fitted by least squares over design variables, on
  GP/RBF/linear-regression surrogates, never on a base-out-of-sample split
  [search-returns: https://arxiv.org/pdf/1705.02956 ,
  https://link.springer.com/article/10.1007/s00158-021-03044-5 ,
  https://arxiv.org/pdf/2508.08517 ].

### Turn 2 — context density for attention correctors → `iteration_2.md`
Terms (why): operator-transformer context-point ablations; Transolver's own
ablations (our corrector IS a Transolver); coarse-field cross-attention.
- The context-count law is published and it SATURATES: *"Increasing M enhances
  contextual information available at each query location without changing the
  amount of model parameters, thereby improving performance up to a saturation
  point"* [cite: https://arxiv.org/html/2502.09692v3 — fetched].
- GAOT's context ablation is unreachable in the fetch; only *"less than 10% of the
  total input points (per batch)"* as a neural-field capability [cite:
  https://arxiv.org/html/2505.18781v4 — fetched, recorded NOT usable].
- Sparse-anchor cross-attention decoders are explicitly *learned interpolators*:
  *"attention weights act as data-adaptive interpolation weights from super-token
  anchors to particles"* [https://arxiv.org/pdf/2605.15305 — search-return].
- An engine-summarised 7.6%→30% / 3.3%→26.4% sampling-coverage ablation could not
  be attributed to a specific fetched paper and is recorded as an **unattributed
  lead, not a citation**.

### Turn 3 — attention vs convolution, and the Transolver premise itself → `iteration_3.md`
Terms (why): head-to-head on regular grids; a text mirror for the AAAI
"Transolver is a linear transformer" claim B1 had to leave uncitable; physics
support for "nonlinear fronts need nonlocal correction".
- **The stream's premise is now citably damaged**: *"Physics-Attention can be
  reformulated as a special case of linear attention, and that the slice attention
  may even hurt the model performance"*, with gains coming from *"the slice and
  deslice operations themselves"*; LinearNO is SOTA on six benchmarks at −40.0%
  params / −36.2% cost [cite: https://arxiv.org/abs/2511.06294 — **fetched via
  `/abs/`** after the AAAI PDF failed; same paper as
  https://dl.acm.org/doi/10.1609/aaai.v40i1.37003 ].
- The one attention-beats-Fourier result is geometry-scoped: *"attention-based
  transformers outperform Fourier methods on problems with complex, irregular
  geometries"*, 3.7× on Heat2D-CG [cite: https://arxiv.org/abs/2605.08318 —
  fetched]. Our panel is regular grids ⇒ does not transfer.
- The best coarse-field corrector in a four-way emulator comparison is
  conv+spectral, not attention: *"The Learned Correction (LC) model consistently
  achieves the lowest error ... by leveraging the coarse solver as a strong
  physical baseline"*, LC being *"a deep FiLMed residual network with spectral
  convolutions"* [cite: https://arxiv.org/html/2511.09729v1 — fetched].
- **No usable results** on "learned corrector for a local reaction-diffusion PDE
  needs a nonlocal receptive field" — the engine returned only nonlocal-PDE
  mathematics. B1's fisher_kpp datapoint stands alone.

### Turn 4 — refutation pass on the MF side of all three verdicts → `iteration_4.md`
Terms (why): MF blend weight fitted on a base-held-out split; MF transformer with
a full coarse field as context; attention-vs-conv ablation inside a coarse
corrector.
- MF residual correctors are a crowded class but their weights are *"learnable"*
  (jointly gradient-trained), and **no** return in three independent phrasings
  fits a blend weight on a split held out from the base's own fit
  [search-returns: https://arxiv.org/pdf/2310.03572 (fetch failed),
  https://www.sciencedirect.com/science/article/abs/pii/S0045782523007193 ,
  https://arxiv.org/pdf/2402.18846 ]. AGMF-Net
  https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X stays
  paywalled/uncitable (B1 already flagged it as the nearest gated-MF artifact).
- **No usable results** for MF PDE correction with a dense coarse-field
  cross-attention context (all returns vision/audio/diffusion).
- P2C2Net's coarse-corrector ablation is conv+FNO with **no attention arm at
  all**: regular conv RMSE 0.1450 vs symmetric-conv full model 0.0064; removing
  the Fourier block 0.1463; the fetch states it *"does not employ attention
  mechanisms anywhere ... nor does it compare attention-based approaches against
  convolutional or spectral methods"* [cite: https://arxiv.org/html/2411.00040 —
  fetched].

### Turn 5 — FINAL, cap hit; verdict work → `iteration_5.md`
Terms (why): a published identity-safe/no-harm validation-selected gate for
neural operators; any LF-context-SIZE ablation in MF operator learning; an
attention-vs-conv head-to-head on our exact PDE family.
- **DIRECT HIT on LICENSED-1's estimator**: stagewise residual correction where
  `eta_m in argmin_{eta in Lambda} (1/N_val) sum_j ||G_{m-1}(a_j) + eta*H_m(a_j) − u_j||^2`,
  the grid `Lambda` **contains 0**, making *"each stage validation-safe: if a
  trained correction does not reduce validation error, it can be rejected"*; base
  is *"the empirical mean output field"*, the fetch confirming *"This is **not**
  multi-fidelity"*; no guarantee — *"several PDE–architecture pairs exhibit
  negative mean gains"* (CNO on 2D NS *"−202% error change"*); and on the split it
  says only *"the same train/validation/test splits within each dataset"*, so it
  *"does not explicitly confirm whether validation data is withheld from previous
  full-size baseline training"* [cite: https://arxiv.org/html/2606.17460 — fetched].
- **No usable results**: MF operator learning ablates the NUMBER of LF samples,
  never the spatial density of the LF field shown to the model (4th independent
  negative) [returns: https://arxiv.org/pdf/2204.06684 ,
  https://arxiv.org/pdf/2507.07292 , https://arxiv.org/pdf/2512.16074 ].
- On our own PDE family, local beats spectral and attention is absent: *"Both
  E-UNO and UNO consistently achieve errors an order of magnitude lower than
  FNO"* on Cahn–Hilliard, −34.32% E-UNO vs UNO at early stages, and the paper
  *"does not include any attention or transformer-based baseline"*
  [cite: https://arxiv.org/html/2509.01293v3 — fetched].
- `https://arxiv.org/pdf/2606.07153` ("No-Harm Physics-Informed Inverse
  Learning") **fetch failed** (metadata only) and is physics-residual-based ⇒
  ADR-0009 disqualified anyway; recorded, not cited as a mechanism source.

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **(i) LICENSED-1 — repair the gate's scoring split (hold `val_idx` out of the stage-1 HF fine-tune) while KEEPING the shrinkage line search containing 0** | **`preempted (cite)`** — the estimator is published for neural operators; only the *diagnosis* is open | https://arxiv.org/html/2606.17460 (**fetched** — validation-selected shrinkage grid containing 0, *"each stage validation-safe: if a trained correction does not reduce validation error, it can be rejected"*, base = empirical mean, *"not multi-fidelity"*, no guarantee, *"−202% error change"* failures) · https://arxiv.org/pdf/1106.1684 (fetched in s6-B2 — Wolpert 1992's rule: *"the combiner must be trained on predictions from base classifiers applied to held-out data"*) · https://arxiv.org/html/2309.09880 (**fetched** — `sum alpha_hat <= 1`; conditional risk beat over the data-selected best single model) · https://arxiv.org/html/2309.14596 (**fetched** — two smoothers + Mallows' Cp = James–Stein; *"purely statistical regression"*) | Three things, none of them the estimator: (a) **the MF instance** — every fetched source's base is a trained model or the empirical mean, never a coarse solve, and none makes copy-LF the fallback; (b) **the failure mode** — no fetched source states that validation-selected shrinkage *inverts* when the base memorised the scoring split, that the bias is one-sided (always toward `eta = 0`), or that 2606.17460 itself is exposed (it *"does not explicitly confirm whether validation data is withheld"*); (c) **the price** — B1's measurement that the wrongly-vetoed weight was the test optimum to 0.9%, worth −43% (skill 5.56→3.16) against a 0.553 floor. **Claim ZERO mechanism novelty. The card is a protocol-defect measurement with a quantified cost, and it should cite 2606.17460 as the published method that shares the hazard.** |
| **(ii) LICENSED-2 — dense LF field as the corrector's context instead of 1024 points, alpha gate retained** | **`preempted-but-MF-composition-open (cite)`** | https://arxiv.org/html/2502.09692v3 (**fetched** — *"Increasing M enhances contextual information ... improving performance up to a saturation point"*) · https://arxiv.org/pdf/2605.15305 (search-return — cross-attention anchors act as *"data-adaptive interpolation weights"*) · https://arxiv.org/abs/2603.29303 (batch-1 fetch — LGFNet: LF as low-frequency carrier + local window + global self-attention + fidelity-gap delta, no router) · negatives: https://arxiv.org/pdf/2507.07292 , https://arxiv.org/pdf/2204.06684 , https://arxiv.org/pdf/2512.16074 (only LF-*count* ablations) | Open: no fetched source ablates **spatial coverage of a coarse-solve LF field used as attention context for a fidelity-gap corrector at N_hf ≈ tens**. But the *same* sources predict the outcome is a better LF **interpolator**, not a fidelity-gap learner — consistent with B1's anatomy (correction ⟂ `hf − copylf`, cosine ≤ 0.02; ceiling skill 1.0, attained 3.10–4.20). **A card must pre-register the skill-1.0 ceiling and the free control that already reaches it** (`base + a*(copylf − base)`: 0.114384 vs 0.125893 on pfc, 0.202549 vs 0.226409 on fisher_kpp, B1 F13), and must not duplicate s6's dense-LF local corrector — s4's version is defensible only as the **attention arm of the (iii) comparison**. |
| **(iii) The attention-vs-local head-to-head for the fidelity-gap defect on regular sharp-interface grids (matched budget, same residual target)** | **`novel`** — as a measurement; and the prior art is **hostile to attention** | Nearest neighbours, none doing the comparison: https://arxiv.org/html/2411.00040 (**fetched** — coarse-corrector ablation is conv+FNO, *"does not employ attention mechanisms anywhere ... nor does it compare"*; conv 0.1450 vs symmetric conv 0.0064; no-Fourier 0.1463) · https://arxiv.org/html/2509.01293v3 (**fetched** — Cahn–Hilliard: *"Both E-UNO and UNO consistently achieve errors an order of magnitude lower than FNO"*, **no attention baseline**) · https://arxiv.org/html/2511.09729v1 (**fetched** — winner is *"a deep FiLMed residual network with spectral convolutions"*) · https://arxiv.org/abs/2605.08318 (**fetched** — attention beats Fourier, but scoped to *"irregular domains"*, 3.7× on Heat2D-CG) · https://arxiv.org/abs/2511.06294 (**fetched** — Physics-Attention *"can be reformulated as a special case of linear attention, and ... the slice attention may even hurt"*; gains from *"the slice and deslice operations themselves"*) | Nobody has run it: matched-parameter cross-attention corrector vs local/LSI corrector on the same `hf − base` (or `hf − copylf`) target, on regular grids with sharp interfaces, at N_hf ≈ tens. The prior predicts attention **loses**, and 2511.06294 supplies the mechanism (the nonlocal content-adaptive part is not what works; slice/deslice pooling is). B1's fisher_kpp band-1 result is the only pro-attention datapoint in this loop, and iteration 3 found **no** published support for "nonlinear fronts need a nonlocal corrector". Either outcome closes the stream's class — the definition of genuine under program.md §1. |

## Citations summary

Every entry below appears with its URL in the named iteration file. Fetched
status is stated explicitly; search-returns are marked and must not be used as
mechanism evidence.

- [Klusowski & Tan] "Error Reduction from Stacked Regressions" — https://arxiv.org/html/2309.09880 (also /pdf/2309.09880) — **fetched** — iteration_1, verdict (i)
- ["Model averaging: A shrinkage perspective"] — https://arxiv.org/html/2309.14596 — **fetched** — iteration_1, verdict (i)
- [MF scale-factor cluster] https://arxiv.org/pdf/1705.02956 ; https://link.springer.com/article/10.1007/s00158-021-03044-5 ; https://arxiv.org/pdf/2508.08517 ; https://www.researchgate.net/publication/361375560_Modified_Multifidelity_Surrogate_Model_Based_on_Radial_Basis_Function_with_Adaptive_Scale_Factor — search-returns — iteration_1
- [Alkin et al., AB-UPT] "Scaling Neural CFD Surrogates ... Anchored-Branched Universal Physics Transformers" — https://arxiv.org/html/2502.09692v3 — **fetched** — iteration_2, verdict (ii)
- [GAOT] "Geometry Aware Operator Transformer" — https://arxiv.org/html/2505.18781v4 — **fetched, NOT usable** (ablation appendix unreachable) — iteration_2
- [WorldParticle] — https://arxiv.org/pdf/2605.15305 — search-return — iteration_2, verdict (ii)
- ["Transolver is a Linear Transformer: Revisiting Physics-Attention through the Lens of Linear Attention"], AAAI 40(1) 408–416 — https://arxiv.org/abs/2511.06294 — **fetched via /abs/** (AAAI PDF https://ojs.aaai.org/index.php/AAAI/article/download/37003/40965 failed; DOI mirror https://dl.acm.org/doi/10.1609/aaai.v40i1.37003) — iteration_3, verdict (iii)
- ["When Attention Beats Fourier: Multi-Scale Transformers for PDE Solving on Irregular Domains"] — https://arxiv.org/abs/2605.08318 — **fetched** (the /html/ URL 404s) — iteration_3, verdict (iii)
- ["Generalizing PDE Emulation with Equation-Aware Neural Operators"] — https://arxiv.org/html/2511.09729v1 — **fetched** — iteration_3, verdict (iii)
- [P2C2Net] "PDE-Preserved Coarse Correction Network" — https://arxiv.org/html/2411.00040 — **fetched** — iteration_4, verdict (iii)
- ["Operator Boosting Produces Pareto-Efficient PDE Surrogates"] — https://arxiv.org/html/2606.17460 — **fetched** — iteration_5, verdict (i)
- ["Equivariant U-Shaped Neural Operators for the Cahn–Hilliard Phase-Field Model"] — https://arxiv.org/html/2509.01293v3 — **fetched** — iteration_5, verdict (iii)
- [Katende] "No-Harm Physics-Informed Inverse Learning with Residual-Calibrated Uncertainty" — https://arxiv.org/pdf/2606.07153 — **fetch failed (metadata only)**, physics-residual ⇒ ADR-0009 — iteration_5, recorded not cited
- [MF residual-corrector cluster] https://arxiv.org/pdf/2310.03572 (fetch failed) ; https://www.sciencedirect.com/science/article/abs/pii/S0045782523007193 ; https://arxiv.org/abs/2306.12047 ; https://arxiv.org/pdf/2210.03008 ; https://arxiv.org/pdf/2402.18846 ; https://github.com/Rose-STL-Lab/MFRNP — search-returns — iterations 4–5
- [AGMF-Net] "Ensemble adaptive gated multi-fidelity neural network for Bayesian optimization" — https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X — **paywalled, uncitable** — iteration_4
- [U-SCANO] U-shaped spatial-channel attention neural operator for NS–Cahn-Hilliard–heat — https://www.sciencedirect.com/science/article/abs/pii/S1007570425009463 — search-return, paywalled — iteration_5
- **In-round siblings cited, NOT re-fetched** (each verified to appear with its URL in `websearches/s4_hybrid_routing/batch_1/iteration_*.md` — 2311.12902 in iteration_4; 2508.21249 in iterations 2–4; 2510.25803 in iterations 1,4; 2602.11197 in iterations 1,2,4; 2604.07421 in iterations 1,3,4; 2605.12965 in iterations 1,3,4): `websearches/s4_hybrid_routing/batch_1/report.md` (D1–D3 verdicts; LGFNet https://arxiv.org/abs/2603.29303 , SPAMoE https://arxiv.org/html/2604.07421 , U-HNO https://arxiv.org/pdf/2605.12965 , MoE-POT https://arxiv.org/abs/2510.25803 , https://arxiv.org/abs/2508.21249 , https://arxiv.org/pdf/2507.07292 , https://arxiv.org/abs/2311.12902 , https://arxiv.org/html/2602.11197) ; `websearches/s6_local/batch_2/report.md` verdict (iv) (Wolpert-1992-through-https://arxiv.org/pdf/1106.1684 , **fetched in that loop**) ; `docs/reports/MF_Sharp_HighFreq_Report.md:102,141,395` (the "16–32 slice tokens" bottleneck note and the Transolver source citation arXiv:2402.02366).

## Dead ends

- `nonlocal attention necessary nonlinear reaction diffusion front sharp interface local convolution insufficient correction operator` → pure applied-math on nonlocal PDEs; **explicit gap**: no published claim that a learned corrector for a local reaction-diffusion PDE needs a nonlocal receptive field. This is why B1's fisher_kpp datapoint cannot be leaned on.
- `transformer multi-fidelity correction full coarse field as context tokens limited high-fidelity samples ...` → vision/audio/diffusion only. No PDE-domain instance of dense coarse-field cross-attention correction.
- `number of low-fidelity points sampled as input multi-fidelity operator learning accuracy versus context size ...` → only LF-**sample-count** ablations, never spatial density (4th independent negative).
- `multi-fidelity neural network blending coefficient fitted on validation split held out from base model training ...` → MF weights are always jointly *learnable*; nobody discusses the split.
- Fetch failures (recorded so nothing is cited from memory): AAAI PDF 37003/40965 (1.5 MB binary — recovered as arXiv:2511.06294); `arxiv.org/html/2605.08318` 404 (recovered via `/abs/`); `arxiv.org/pdf/2310.03572` (7.3 MB binary); `arxiv.org/pdf/2606.07153` (metadata only); GAOT ablation appendix unreachable.
- **Unattributed lead, deliberately NOT cited**: the engine-summarised centroid-sampling ablation (*"7.6% to 30% yields similar accuracy"* on Elasticity; *"3.3% to 26.4% steadily improves ... diminishing returns beyond roughly 20–26%"* on PUC; recommendation *"15–30% of the boundary points"*). Neither fetch confirmed it. If a future batch can attribute it, it is the closest published coverage-threshold result — and it says the answer is dataset-dependent, matching B1's pattern.

## For the brainstormer

The brainstormer MUST quote the verdict above for whatever it proposes.

1. **The gate repair is `preempted (cite)`, not novel — and there is now a named
   published method with the same estimator.** Operator Boosting
   (https://arxiv.org/html/2606.17460, fetched) selects each residual stage's
   weight on a validation split over a grid *containing 0* so that *"if a trained
   correction does not reduce validation error, it can be rejected"*. Propose
   LICENSED-1 as a **protocol-defect measurement** ("this estimator inverts when
   the base memorised the scoring split; here is the 43% it cost"), cite
   2606.17460 as the published instance that shares the hazard (it *"does not
   explicitly confirm whether validation data is withheld from previous full-size
   baseline training"*), and cite Wolpert-through-arXiv:1106.1684 for the rule.
   Pre-declare only the **per-dataset cahn_hilliard claim** (skill ≤ 3.5 against
   the 0.553 floor) — B1 F12 already shows the repaired-gate panel move (5.6649 →
   5.1374, i.e. 0.5275) is **inside** the 0.884 geomean floor.
2. **Keep the shrinkage; you now have theory for it.** Do not "fix" the gate by
   using the least-squares weight — B1 F13 measured an 8.47× regression on pfc
   (`alpha_ls = 0.9944` → 1.066448 vs shipped 0.125893). The shrunk,
   0-containing weight is a studied estimator: `sum alpha_hat <= 1` with a
   conditional risk beat over the data-selected best single model
   (https://arxiv.org/html/2309.09880), and two-smoother Mallows'-Cp blending *is*
   James–Stein (https://arxiv.org/html/2309.14596). Both are pure statistics —
   cite them for the estimator, never for the MF composition.
3. **The strongest card available to this stream is the attention-vs-local
   head-to-head (verdict iii, `novel`), and it should be designed to LOSE.** The
   fetched prior is hostile: Physics-Attention *"may even hurt"* and its gains come
   from *"the slice and deslice operations themselves"* (arXiv:2511.06294);
   attention only beats Fourier on *"irregular domains"* (arXiv:2605.08318); the
   best coarse-field corrector in a four-way comparison is conv+spectral
   (arXiv:2511.09729v1); on Cahn–Hilliard *"E-UNO and UNO consistently achieve
   errors an order of magnitude lower than FNO"* with **no attention baseline**
   (arXiv:2509.01293v3); P2C2Net's coarse-corrector ablation has **no attention
   arm at all** (arXiv:2411.00040). A matched-budget comparison on the same
   fidelity-gap target on regular sharp grids exists nowhere, s4 uniquely owns it
   (s6 owns the local arm's *standalone* use, not the comparison), and either
   outcome retires or promotes the whole class — program.md §1 genuine.
4. **If you propose LICENSED-2, it is `preempted-but-MF-composition-open` and you
   must pre-register the ceiling.** "More context helps up to saturation" is
   published (arXiv:2502.09692v3) and sparse-anchor cross-attention is explicitly a
   *learned interpolator* (arXiv:2605.15305), which together with B1's anatomy
   (cosine ≤0.02 with `hf − copylf`) predicts denser context buys **attainment
   toward skill 1.0, not passage through it**. Include the free scalar control
   `base + a*(copylf − base)` (B1 F13) as a scored arm — any new stage must beat
   *it*, not the base. Nothing in 4 independent searches ablates LF spatial
   coverage in MF operator learning, so the *measurement* is unpreempted; the
   *knob* is not.
5. **Do not resurrect routing, in any spatial form.** B1 F11 priced it under every
   floor and s6's `trust_gate_headroom.py` agrees from the opposite base; batch 1
   already found the published routers (SPAMoE, U-HNO, MoE-POT, arXiv:2508.21249).
   The stream's remaining question is the **corrector class**, not the gate's
   spatial resolution.
6. **Reporting requirement carried forward** (B1 part 7): publish, next to every
   gate value, the correction's RMS relative to the residual and its cosine with
   the residual, plus `cosine(corr, copylf − base)`. Without them a collapsed
   branch is indistinguishable from a vetoed good one — and arXiv:2511.06294 gives
   the mechanistic reason to expect collapse.
