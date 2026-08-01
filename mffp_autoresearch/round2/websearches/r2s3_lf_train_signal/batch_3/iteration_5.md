# Iteration 5 — last refutations and the prior-art verdict (CAP HIT: 5/5)

**Iteration cap reached** (§3.2 max 5). No further search turns.

## Search rationale

Two gaps remained before the verdict could be written: (i) is the *attribution*
of LF benefit to distinct channels (new information vs variance reduction vs
level) an existing diagnostic — the preemption surface for B2's three-channel
taxonomy; (ii) is the round's deployment framing ("a company hands over
historical simulation data but no callable solver", program.md §1) a named
regime in the literature.

## Search terms used

1. `attributing why low-fidelity data helps mechanism decomposition of multi-fidelity benefit variance reduction versus new information`
2. `no solver available at deployment predict simulation field from design parameters using historical simulation database coarse and fine runs`

## Findings

### Term 1 — channel attribution of LF benefit
Search returns (none fetched this turn):
- The established attribution is the **control-variate / variance-reduction**
  account from multi-fidelity UQ: "a multifidelity estimator exploits the
  cross-correlations between the low- and high-fidelity returns to reduce the
  variance"; "a lower-fidelity model is said to be a control variate if it
  exhibits a strong correlation with the high-fidelity model"
  (engine synthesis over https://arxiv.org/pdf/1806.10761 — Peherstorfer,
  Willcox, Gunzburger survey; https://www.sciencedirect.com/science/article/abs/pii/S0925231224007343;
  https://kiwi.oden.utexas.edu/research/multi-fidelity-uncertainty-quantification).
- That framing is about **Monte-Carlo estimators of functionals**, not about
  which subspace of a learned parametric operator improves. It maps onto only
  one of B2's three channels (row-space fit / variance reduction).
- The row-space-vs-null-space half remains https://arxiv.org/html/2510.15337
  (fetched batch 2 iteration 1; re-surfaced as the top hit in this batch's
  iteration 2 term 1).

### Term 2 — solver-free deployment regime
**No usable results.** Returns were patents and vendor documentation
(https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11763046,
https://www.simscale.com/docs/simulation-setup/result-control/field-calculations/,
https://www.intechopen.com/chapters/89743) — no academic work naming
"LF available at training, no solver at inference" as a regime. Third
independent miss for this framing (batch 1 iteration 3; this batch iterations
4 and 5).

## Prior-art verdict (candidate B3 directions)

Candidates are taken from `experiment_cards/r2s3_lf_train_signal/batch_2/B2.json`
part 7 `next_direction` (legs 1–3) and the mechanism alternatives the
brainstormer could reach for given part 5 M1/M5.

### P1 — panel-completion: matched, budget/step-matched ±LF contrast (A0_nolf vs A1_lf_cov) for a condition→field neural surrogate at N_hf = 5, over all 6 panel datasets, priced per dataset against the certified `min_claimable_effect` and reported in copy-LF skill units
**Verdict: `preempted-but-MF-composition-open`** (this **supersedes batch 2's
`novel` verdict for E5**).
- Preempting the *genre*: https://arxiv.org/html/2511.01830v1 (fetched
  iteration 3) sweeps training-set fidelity composition 0→100% HF at fixed
  ~4M-param capacity and fixed generation budget against a "trained on the full
  high-fidelity dataset" reference, concluding that under tight budgets "the
  broader coverage of the data manifold offered by many low-fidelity samples
  outweighs the higher accuracy of a few high-fidelity ones";
  https://arxiv.org/html/2408.17075v1 (fetched iteration 3) benchmarks MF
  surrogates against "their tested single-fidelity counterparts" on five
  functional-output test cases; https://arxiv.org/html/2510.23111v1 (fetched
  iteration 1) scores an LF-trained emulator against the solver that produced
  its data.
- **What remains open**: none of the three has (a) a **condition-vector-only
  test input with LF strictly absent from the prediction path** — 2511.01830
  and 2510.23111 are field-in/field-out emulators, 2408.17075's corrective and
  mapping families keep the LF snapshot in the pipeline; (b) the
  **N_hf ≈ 5** regime (2511.01830 does not specify a minimum HF count;
  2408.17075's counts were not recoverable from the fetch); (c) a
  **certified seed-noise claimability threshold** per dataset; (d) the
  **copy-the-LF-solve denominator** (`skill`), i.e. "is the model worth more
  than running the coarse solver"; (e) a panel spanning PDE families that
  **differ in condition completeness** (ADR r2-0003), which is what makes the
  fisher_kpp/allen_cahn/pfc rows interpretable at all. The composition of
  (a)+(d)+(e) is the card's only defensible claim.

### P2 — the coverage result: LF at conditions carrying no HF row is what pays; LF replicated at the 5 HF conditions does not (B2 M5, `A3_lf_paired` worse than no-LF)
**Verdict: `preempted`.**
- https://arxiv.org/html/2408.17075v1 (fetched iteration 3): mapping approaches
  need "the same number n of high- and low-fidelity latent variables snapshots
  (corresponding to the same input variable vectors)", corrective approaches
  are limited because "the small number of high-fidelity snapshots will limit
  the number of exploitable low-fidelity snapshots … the surrogate may not take
  full advantage of the multi-fidelity context", while for fusion approaches
  "it is possible to have a different number of snapshots for different
  fidelities (i.e., n₁≠n₂)".
- Nested-vs-non-nested design is a standard axis (search returns:
  https://www.sciencedirect.com/science/article/abs/pii/S2352012425024324,
  https://www.sciencedirect.com/science/article/abs/pii/S1474034625009693;
  fetched in batch 2: https://arxiv.org/abs/2511.20183).
- **What remains open**: only the *quantified neural instance* — that a paired
  (fully nested) LF pool is not merely uninformative but **actively harmful**
  (−0.83 skill units, 9.1× the dataset threshold) for a condition→field network
  on a multistable PDE. Report it as a measurement citing the above; never card
  it as the mechanism.

### P3 — the three-channel taxonomy (direction supply / row-space fit / level-amplitude) plus `tools/null_family_ceiling_audit.py` as the reporting instrument
**Verdict: `preempted-but-MF-composition-open`.**
- The row-space/null-space split is published:
  https://arxiv.org/html/2510.15337 (fetched batch 2 iteration 1; top hit again
  here in iteration 2), with the same decomposition recurring in other domains
  (https://arxiv.org/pdf/2506.04244, https://arxiv.org/pdf/2507.02248 —
  search returns). The variance-reduction channel is the classical
  control-variate account (https://arxiv.org/pdf/1806.10761 — search return).
- **What remains open**: the **three-way** split that adds a level/amplitude
  channel, and **measured shares** for a PDE field surrogate
  (ifc 57–60/~40/n.a.; ch 68/40/23; fk 0/small/77). No retrieved work reports
  such an attribution for a learned parametric operator. Card it as
  vocabulary + instrument with the citations attached, not as theory.

### P4 — the optional leg: amplitude-corrected null-direction penalty (A1′ = A1 + penalty × measured 0.5510 gain) on `sharp__cahn_hilliard`
**Verdict: `preempted`.**
- Null-space-targeted regularization: https://arxiv.org/html/2510.01608,
  https://iopscience.iop.org/article/10.1088/1361-6420/aaf14a (batch 2
  iteration 3). Scale-factor calibration between LF and HF inside a penalized
  objective: https://link.springer.com/article/10.1007/s00158-024-03887-8
  (search return, iteration 2 term 3).
- **What remains open**: nothing at the mechanism level. Round-2 discipline
  also disfavours it: the mechanism measured **net-negative** in B2 (M1), so a
  retune is a pre-falsified-lever-style move (program.md §5). Admissible only
  as a single cheap ablation leg explicitly framed as closing B2's
  `open_question`, never as the card's headline.

### P5 — (alternative mechanism, if the brainstormer abandons measurement) gated / adaptively weighted LF loss to prevent negative transfer
**Verdict: `preempted`.**
- Negative transfer with LF data and its gating remedies are a populated
  family: https://arxiv.org/abs/2002.04495 (fetched abstract; engine synthesis
  reports LF transfer can yield "less accurate surrogates compared to when the
  network is trained based only on large high-fidelity datasets"),
  https://hal.science/hal-04602579/document (LOL-GP per-location borrow gate),
  https://www.sciencedirect.com/science/article/pii/S0021999124002018
  (multi-channel fusion), https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X
  (Ada2MF gated residual + adaptive loss weighting) — the last three are search
  returns. Combined with batch 2's E4 row (https://arxiv.org/abs/2403.08118),
  gating is engineering, not a claim.

## Interpretation

Every mechanism-shaped candidate for B3 is preempted; the only defensible
claim left is the **composition** in P1 — and it is now weaker than batch 2
believed, because the ±LF-ablation genre itself is published. The stream's
honest B3 is a measurement-completion card that cites 2511.01830 / 2408.17075
as the genre's prior art and claims only the regime-specific composition.
