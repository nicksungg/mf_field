# Iteration 5 — Stream `s1_poisson`, Batch 1

> Persisted verbatim by the orchestrator from the websearcher's return.

**Cap note: this is iteration 5 of 5. The loop stops here per §3.2 regardless of remaining questions; unresolved items are listed as dead ends in `report.md`.**

## Search rationale
Final iteration = the mandatory prior-art verdict work (§3.3). One targeted refutation search per remaining candidate direction: D2 (multi-level aggregation / control variate) via MFRNP's exact formulation, D3 (ensembling as variance reduction at tiny N), and a last D1 refutation from the "joint training over all levels" angle.

## Search terms used
1. (fetch-only, MFRNP full text — D2 refutation)
2. `deep ensemble neural operator small training set variance reduction seed averaging PDE surrogate accuracy gain`
3. `fidelity as additional input dimension train one neural operator jointly on all fidelity levels coarse fine augmented input`

## Findings

**Term 1 (D2)** — **WebFetch https://arxiv.org/pdf/2402.18846 → FAILED** (binary PDF unparseable). D2's citation therefore rests on the **iteration-1 HTML fetch** of the same paper (https://arxiv.org/html/2402.18846v1), which did give the mechanism and the 0.0076 ± 7.49e-4 Poisson number. Sample counts per fidelity remain unknown.

**Term 2 (D3)** — top results: Operator Boosting (https://arxiv.org/html/2606.17460), calibration-aware uncertainty for neural PDE surrogates (https://arxiv.org/html/2602.11090), physics-based active learning for data-efficient NO training (https://arxiv.org/html/2605.21348), randomized neural operator with fast training + conformal UQ (https://arxiv.org/pdf/2606.29440), data-efficient NOs from fundamental physics knowledge (https://arxiv.org/pdf/2602.15184).
- Engine synthesis: ensemble averaging "tr[ies] to reduce the variance of single deep neural networks by fusing results of differently initialized and trained networks, using methods such as random seeds"; recent operator-level work "quantif[ies] gains in accuracy in **small-data regimes** and robustness across random seeds"; ensembling gives favourable speed–accuracy trade-offs on Burgers/Darcy/NS. **Snippet-level only — no fetch.**

**Term 3 (D1, last angle)** — top results: MF-HNP (https://par.nsf.gov/servlets/purl/10347020 and https://ai4good.org/wp-content/uploads/2022/08/FE2022-Multi-fidelity-Hierarchical-Neural-Processes-for-Climate-Modeling.pdf), MFRNP (https://arxiv.org/html/2402.18846v1), MF physics-constrained NNs / MSPCNN (https://arxiv.org/html/2402.02031v1), MF-FNO carbon storage (https://arxiv.org/pdf/2308.09113), progressive MF learning (https://arxiv.org/pdf/2510.13762).
- Engine synthesis, the most direct hit of the run: *"Neural operators can be trained using multi-resolution strategies, where data sampled at different discretizations are **jointly incorporated during training**, enabling the use of solvers with varying levels of fidelity from coarse low-cost simulations to fine high-accuracy ones."* Also: deep-GP MF "design[s] a single objective to optimize kernel parameters at each fidelity level **jointly**"; MF-HNP "infers latent variables at each fidelity level instead of the global variable"; MSPCNN unifies fidelities "into a unified latent space through a customised multi-fidelity autoencoder".
- **WebFetch https://par.nsf.gov/servlets/purl/10347020 → FAILED** (DNS `ESERVFAIL`). MF-HNP is therefore **snippet-level only**.
- **WebFetch https://arxiv.org/pdf/2510.13762 (Progressive MF learning) → OK (~150w):** sequential/progressive training across fidelity levels, lower-fidelity models serving as initialization/guidance for higher ones; explicitly **not restricted to two levels**; and it "specifically addresses **very small high-fidelity sample counts**, which is a key contribution", quoting "progressively leverage[s] information from multiple data sources of varying accuracy and cost" and integrating fidelity information "structurally during training rather than as a separate fine-tuning phase". Exact HF counts not extracted.

## Interpretation (and the verdicts)
Joint-over-all-levels training is published in the neural-process / deep-GP / MF-FNO branches, and progressive ladder training is published *and explicitly targeted at very small HF counts* — so D1 cannot be called novel at the level of "use the whole ladder". What survives every refutation attempt is narrower: **all ordered (src,tgt) pairs, one shared network, fidelity pair as FiLM conditioning, on a nested 100/50/20/5 ladder at N_hf=5**. D2 and D3 are cleanly preempted.
