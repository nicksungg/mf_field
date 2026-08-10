# Iteration 4 — §3.3 refutation pass 1 (three candidate directions)

## Search rationale

Field context is **ENOUGH** as of iteration 3 (the three candidate mechanisms all have identified literatures: energy-vs-task mode selection, slice discovery, stagewise gated residual boosting).
Remaining iterations go to §3.3 refutation.
The three candidate directions this batch is likely to propose, from `B1.json:7_gap_and_future.next_direction` and the orchestrator's batch-2 routing:

- **D1 — adaptive/predictability truncation.** Replace `SELECT_MAX = 32` with a criterion that admits a reduced-basis direction when its coefficient is out-of-fold predictable from the condition, at N_hf 5–400. Refute by finding a published per-mode predictability screen.
- **D2 — the replacement discriminator.** `n_SET` / `E_rem` x reachability as a *training-free, pre-unlock* predictor of whether the two-stage cascade pays (successor to the falsified cond_dim discriminator). Refute by finding a published pre-fit criterion keyed on residual energy / selected-target count.
- **D3 — two-population certification.** Certify a scored cell as condition-**incomplete** on an identified, seed-invariant subpopulation. Refute by finding a published benchmark-audit procedure that does this.

## Search terms used

1. `select which POD modes to regress by predictability from parameters out-of-fold R2 screening modal coefficients` (D1)
2. `predict in advance whether multi-target stacking chaining will help criterion residual variance number of targets before fitting` (D2)
3. `benchmark audit parameter vector does not determine solution field identify samples PDE dataset incomplete conditioning` (D3)

## Findings

### Term 1 (D1) — no per-mode predictability screen returned; nearest neighbour is a mode-count sweep (one fetch)

**FETCHED** — Nonomura, Nankai, Iwasaki, Komuro & Asai, *Quantitative Evaluation of a Linear Reduced-order Model based on PIV Data of Separated Flow Field around Airfoil*, arXiv:1907.12239 v2 — [cite: https://arxiv.org/abs/1907.12239].
Verbatim: "The present evaluation method can be used for the evaluation of the estimation error and the **model predictability**. The model was constructed using **different numbers of POD or DMD modes** … and the effects of these conditions on the model performance were quantitatively evaluated. The results illustrates that forward (standard) model works the best with **two to ten significant DMD modes selected by sparsity promoting DMD**."
So: mode **count** swept against downstream predictability, and mode **selection** by sparsity-promoting DMD — but the selection objective is dynamic-mode sparsity, not out-of-fold predictability from a *parameter/condition vector*, and it is a temporal ROM.
Also returned (snippet only, not fetched): the out-of-sample R² as an estimand with inference [https://arxiv.org/pdf/2302.05131]; active-subspace reconstruction of POD modal coefficients [https://www.sciencedirect.com/science/article/pii/S1631072119301834]; KSPOD emulation [https://arxiv.org/pdf/1802.08812].
Verbatim from the turn's summary of these returns: "the **balance between adding accuracy by including POD modes and the increase in forecasting error with increasing numbers of POD coefficients to be predicted** is a key consideration."
**No result screens modes individually by regression skill and drops the unpredictable ones.**

### Term 2 (D2) — the bias–variance answer is published; the specific statistic is not

Returns are the multi-target-regression core, headed by the batch-1 citation of record [https://arxiv.org/pdf/1211.6581] (SST/ERC), plus random linear target combinations [https://www.researchgate.net/publication/261761352], DSTARS [https://www.sciencedirect.com/science/article/abs/pii/S1568494620301551], regressor chains with repetitive permutation [https://www.sciencedirect.com/science/article/pii/S0303243421003640], the multi-output survey [https://oa.upm.es/40804/1/INVE_MEM_2015_204213.pdf], and *Interpretable Target-Feature Aggregation for Multi-Task Learning based on Bias-Variance Analysis* [https://arxiv.org/pdf/2406.07991].
Verbatim from the turn's summary: "by introducing additional features to single-target models through stacking and chaining methods, the effect is to **decrease bias at the expense of increased variance** … whenever the increase in variance is outweighed by the decrease in bias, one should expect gains"; and "some targets may have **no relationships with others**, and an effective MTR method should treat these uncorrelated outputs as separate single-target tasks."
So the *qualitative* rule ("stack when the targets are related and the variance cost is affordable") is published and is exactly what `n_SET`/`E_rem` x reachability would operationalise.
**No returned work computes a pre-fit statistic from the reduced-basis residual energy and its condition-reachability to decide the cascade.** All snippet-level; nothing fetched this turn because the class is already anchored by the batch-1 fetched citation 1211.6581.

### Term 3 (D3) — post-hoc auditing of learned PDE models exists, but audits the model, not the benchmark's conditioning (one fetch)

**FETCHED** — Shikhman, *A Diagnostic Software Suite for Auditing Learned PDE Simulators*, arXiv:2606.18200, 16 Jun 2026 — [cite: https://arxiv.org/abs/2606.18200].
Verbatim: "standard relative $L^2$ error **does not determine whether a learned model behaves as a coherent numerical time propagator**"; the suite gives "architecture-independent, post hoc diagnostics for relative state error, semigroup consistency, finite-difference generator discrepancy, energy behavior, integral balance, admissibility constraints, perturbation response, and scaling-law consistency"; and "relative $L^2$ error can remain moderate, or even improve, while **structural diagnostics deteriorate substantially**."
This is a strong methodological cousin — a *diagnostic panel instead of a single error score*, which is the same instinct as this project's metric panel — but every diagnostic is a property of the **learned propagator**; none asks whether the dataset's parameter vector determines its field.
Also returned (snippet only): PDEInvBench [https://arxiv.org/abs/2605.25353], whose framing is the *inverse* map (fields → parameters) with in-/out-of-distribution splits, i.e. the identifiability question run backwards; PDEBench [https://papers.neurips.cc/paper_files/paper/2022/file/0a9747136d411fb83f0cf81820d44afb-Paper-Datasets_and_Benchmarks.pdf].

## Interpretation

D1 and D2 survive this pass with their *general* forms preempted and their *specific statistics* unreturned; D3's nearest published neighbours audit the model, not the benchmark's input completeness.
Iteration 5 (cap) runs the last three refutation queries and records the verdict.
