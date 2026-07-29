# Iteration 4 — Stream `s1_poisson`, Batch 1

> Persisted verbatim by the orchestrator from the websearcher's return.

## Search rationale
Last chance to refute D1 before committing a verdict. Attack it from the classical-MF vocabulary ("pairwise", "cross-fidelity mapping", "input augmentation") rather than the deep-learning vocabulary, since the idea is old enough to have a GP-era name; and pin down the strongest recent ladder-refinement competitor spotted in iteration 1.

## Search terms used
1. `"all pairs" OR "pairwise" fidelity level augmentation multi-fidelity surrogate training every pair of levels cross-fidelity mapping`
2. (fetches only — see below)

## Findings

**Term 1** — top results: MF-GP topic page (https://www.emergentmind.com/topics/multi-fidelity-gaussian-process-surrogate-modeling), MAST (https://arxiv.org/html/2602.20974), MFRNP (https://arxiv.org/pdf/2402.18846), co-kriging→MF-NN survey (https://arxiv.org/pdf/2605.02871), MF-BO review (https://arxiv.org/pdf/2311.13050), non-hierarchical LF fusion (https://www.sciencedirect.com/science/article/abs/pii/S1474034621001828), multifidelity cross-validation (https://arxiv.org/html/2407.01495).
- Engine synthesis, the closest named relative of D1: **"input-augmentation GP-based multi-fidelity modeling"** — MF surrogates built "as functions of both **input and fidelity variables**". So *fidelity-as-an-input* is a named classical family. Also returned: MFRNP "includes decoders in cross-fidelity information sharing"; and methods that remove hierarchical assumptions via "model reification", allowing fusion "**without requiring paired observations or nested designs**" (the converse of our nested ladder).
- Still **no** source describing training over **all ordered (src,tgt) fidelity pairs** as a data-amplification scheme.

**Fetches**
- **WebFetch https://arxiv.org/html/2605.16118v1 (Multi-Fidelity Flow Matching, MFFM) → OK (~150w):** cascade-refinement framework that models only the residual δ = u_HF − u_LF. Uses a **multi-resolution hierarchy of more than two levels**, nested grids **G₀ ⊂ G₁ ⊂ … ⊂ G_L**, applying "the same construction independently between **adjacent** fidelities". **Each level gets its own velocity network**, pretrained per-level with flow-matching, then **end-to-end cascade fine-tuning** with deterministic one-step rollouts. Eight benchmarks (2-D Darcy, 1-D Burgers, Shallow Water, Diffusion-Reaction, two Shear Flow variants, Active Matter, 2-D NS) from PDEBench / The Well / the FNO dataset — **not** the IFC benchmark. NRMSE reported as mean ± std over 33 seeds. **512–896 training samples per benchmark** (Darcy 512/128/128).
- **WebFetch https://arxiv.org/pdf/2308.09113 (MF-FNO carbon storage) → FAILED** (binary PDF unparseable). Its training scheme (joint vs pretrain→finetune) is therefore **unknown and not cited**.

## Interpretation
D1's nearest published neighbours are now sharp: **fidelity-as-input augmentation** (classical MF-GP family, snippet-level) and **adjacent-level cascade residual refinement** (MFFM, fetched). Neither is all-ordered-pairs with one shared network, and MFFM's regime (per-level networks, 512+ samples, 33 seeds) is the opposite of ours (one shared network, 5 HF samples, 3 seeds). The composition remains open; the ingredients do not.
