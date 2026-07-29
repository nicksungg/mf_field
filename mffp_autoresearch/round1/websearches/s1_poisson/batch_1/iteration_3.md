# Iteration 3 — Stream `s1_poisson`, Batch 1

> Persisted verbatim by the orchestrator from the websearcher's return.

## Search rationale
Q2 is the decisive question for batch 1: if all-pairs fidelity training is published, the seed direction is a measurement of an existing family, not a contribution — and §13.3's 0-for-4 record says assume it is published until a search fails to find it. Two angles: POSEIDON's all2all itself (is it already recast onto fidelity?), and the broader class "one network conditioned on fidelity, trained on all levels".

## Search terms used
1. `POSEIDON all2all training pairs adapted to multi-fidelity levels neural operator fidelity-conditioned pretraining`
2. `fidelity-conditioned neural operator single network trained on all fidelity levels FiLM embedding multi-fidelity FNO`
3. (no third term — budget spent on resolving the iteration-2 MLMC contradiction; see fetch below)

## Findings

**Term 1** — top results: POSEIDON emergentmind (https://www.emergentmind.com/papers/2405.19101), NeurIPS 2024 poster (https://nips.cc/virtual/2024/poster/95731), project page (https://camlab-ethz.github.io/poseidon/), PI fine-tuning of foundation models (https://arxiv.org/html/2603.15431v1), multi-task DeepONet (https://www.sciencedirect.com/science/article/abs/pii/S0893608024010426).
- Engine synthesis: POSEIDON is a multiscale operator transformer with **time-conditioned layer norms**; its all2all strategy "leverages the **semi-group property**", pairing **time snapshots** within a trajectory to expose the model to diverse Δt mappings. Pretrained on compressible Euler + incompressible NS.
- Explicit negative: "the specific **multi-fidelity levels and fidelity-conditioned pretraining** aspects mentioned in your query are **not** explicitly detailed in these particular sources."

**Term 2** — top results: MF-FNO carbon storage (https://arxiv.org/pdf/2308.09113 and https://www.sciencedirect.com/science/article/abs/pii/S0022169424000350), MF-FNO transfer learning (https://arxiv.org/pdf/2304.06972), MF-BNN (https://www.sciencedirect.com/science/article/abs/pii/S0021999121002564), correlation-based MF emulator assessment (https://arxiv.org/pdf/2512.02868), MF flow matching (https://arxiv.org/html/2605.16118v1).
- Engine synthesis: MF-FNO exists and exploits FNO's **grid-invariance** so that "low-fidelity and high-fidelity data ... utilize the same network structure without structural modifications"; reported "accuracy comparable to high-fidelity models trained with the same amount of high-fidelity data with **81% less data generation cost**". FiLM conditioning "maps metadata to per-level affine parameters" and is used in neural-operator architectures.
- Explicit negative: "I didn't find a paper that specifically combines all these elements (FiLM embedding, single network trained on all fidelity levels, and FNO) in one unified approach within these search results."

**Fetch (attached to iteration 2, term 1)** — **WebFetch https://arxiv.org/abs/2505.12940 → OK but inconclusive:** the abstract does not state how coarse data is produced; the only relevant sentence is *"Our framework relies on using gradient corrections from fewer samples of fine-resolution data to decrease the computational cost of training while maintaining a high level accuracy."* The downsample-vs-separate-solve contradiction stands **unresolved**.

## Interpretation
POSEIDON's all2all is confirmed to be a **time/semigroup** construction, not a fidelity construction, and two independent searches explicitly failed to find a fidelity-conditioned single-network FNO trained over all levels with FiLM. That is the strongest novelty signal of the run — but it is an *absence of evidence* from an engine, which under §13.3 warrants "MF-composition-open", not "novel".
