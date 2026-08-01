# Iteration 3 — reading the two dangerous preemptions

## Search rationale

Iteration 2 flagged arXiv:2511.01830 (MF scaling laws for neural surrogates)
as the single most dangerous preemption for a panel-scale value-of-LF
accounting, with an abstract too thin to judge. This turn reads its body,
then attacks the two remaining B3 claims from the design side: is
"LF at conditions that already carry an HF row is wasteful" (B2 M5) a known
design-of-experiments fact, and does a **multi-PDE-family** fidelity-mix
ablation already exist?

## Search terms used

1. `"multi-fidelity" scaling law how many low-fidelity samples equivalent to one high-fidelity sample surrogate quantify` (+ body fetch of arXiv:2511.01830)
2. `low-fidelity samples at same design points versus different design points multi-fidelity surrogate redundant replication wasteful experimental design`
3. `fidelity mix training data composition ablation across several PDE families neural surrogate parameter-to-solution map scarce high-fidelity 2026`

## Findings

### Term 1 — MF scaling laws (FETCHED body)
https://arxiv.org/html/2511.01830v1 — "Towards Multi-Fidelity Scaling Laws of
Neural Surrogates in CFD" (fetched; the /abs/ page in iteration 2 was
uninformative):
- **One problem family only**: "We identify aerodynamic airfoil simulations as
  an ideal testbed, since they are industrially relevant, well studied and
  allow for different fidelity levels based on physical modeling assumptions."
- **It DOES run the ±LF axis**: training-set fidelity composition is swept from
  0% to 100% high-fidelity at fixed model size (~4M params) and fixed
  generation budget; "dashed line indicates model performance when trained on
  the full high-fidelity dataset".
- **Headline** (search return of the same paper, consistent with the fetch):
  "under tight compute constraints, the broader coverage of the data manifold
  offered by many low-fidelity samples outweighs the higher accuracy of a few
  high-fidelity ones"; "the smaller the available budget, the more the optimal
  dataset composition shifts towards allocating more budget to lower fidelity
  samples"; above a budget threshold accuracy is "primarily limited by the
  fidelity of the data rather than its quantity".
- **Inputs are spatial fields** ("initial conditions and mesh node positions"),
  not a condition vector; value is reported in error units, **not** converted
  to equivalent HF samples; no minimum-HF-sample regime is specified; no
  seed-noise floor / claimability threshold.

### Term 2 — replicated vs distinct design points
- Engine synthesis with a directly usable statement, confirmed by the fetched
  survey below: nested sampling "requires high-fidelity input points to be a
  subset of low-fidelity input points", a condition inherited from co-Kriging,
  which "relied on output differences at shared input locations".
- **FETCHED**: https://arxiv.org/html/2408.17075v1 — "A survey on multi-fidelity
  surrogates for simulators with functional outputs: unified framework and
  benchmark" (batch 2 could only cite its existence; the HTML parses):
  - corrective approaches: "if the computational cost of the high-fidelity
    simulator is especially high, the small number of high-fidelity snapshots
    will limit the number of exploitable low-fidelity snapshots. Hence, the
    surrogate may not take full advantage of the multi-fidelity context";
  - mapping approaches: "the same number n of high- and low-fidelity latent
    variables snapshots (corresponding to the same input variable vectors) is
    required";
  - fusion approaches: "it is possible to have a different number of snapshots
    for different fidelities (i.e., n₁≠n₂)".
- Other returns: LF-guided DoE for MF surrogates
  (https://www.sciencedirect.com/science/article/abs/pii/S1474034625009693),
  non-hierarchical LF fusion
  (https://www.sciencedirect.com/science/article/abs/pii/S1474034621001828),
  MF review https://arxiv.org/pdf/1609.07196.

### Term 3 — multi-PDE-family fidelity-mix ablation
- Same survey (https://arxiv.org/html/2408.17075v1) is the closest: its
  benchmark spans **five test cases** (viscous free fall ×2, NACA 0015,
  RAE 2822 RANS/RANS, RAE 2822 RANS/Euler) and reports "most multi-fidelity
  surrogates outperform their tested single-fidelity counterparts" and "no
  particular surrogate is performing better on every test case". It does **not**
  quantify when LF fails to help, and the fetch could not confirm input
  dimension or HF sample counts.
- Adjacent MF-neural families (search returns only): multifidelity GNNs
  https://onlinelibrary.wiley.com/doi/10.1111/mice.13312; MF reduced-order
  https://royalsocietypublishing.org/doi/10.1098/rspa.2023.0655; MF residual
  neural processes https://arxiv.org/html/2402.18846v1; disentangled MF
  Bayesian active learning
  https://proceedings.mlr.press/v202/wu23p/wu23p.pdf; diffusion-generative MF
  https://arxiv.org/pdf/2311.05606. None is a value-of-LF *accounting* paper.

## Interpretation

The genre "compare multi-fidelity training against a single-fidelity/HF-only
baseline over several test problems" is **published**: 2511.01830 sweeps the
fidelity mix at fixed capacity and budget on one CFD family, and 2408.17075's
benchmark compares MF against single-fidelity counterparts on five
functional-output test cases. Batch 2's `novel` verdict for E5 can therefore
no longer stand unqualified — it must be restated as
`preempted-but-MF-composition-open`, with the open part named precisely.
Separately, "LF replicated at the HF design points wastes the MF context" is
an explicit, quotable statement of the surveyed literature, so B2's M5 is a
confirmation, not a discovery.
