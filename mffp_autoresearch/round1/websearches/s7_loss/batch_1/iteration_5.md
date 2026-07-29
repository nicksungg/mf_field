# iteration_5 — s7_loss / batch 1 (ITERATION CAP: k = 5, loop ends here)

## Search rationale

Final iteration = §3.3 refutation work. Iterations 1-4 established the field
context (ENOUGH declared at the top of iteration 4). Here I run one targeted
"has this been done?" search per candidate direction that batch 1 is likely to
propose, aiming to REFUTE novelty, and then record verdicts. Candidate set,
derived from program.md §12.7 + ADR 0012 + the s2-B1 findings:

- **C-REL** — metric-aligned objective: per-sample relative-L2 training loss
  (and per-sample selection metric) in place of globally max-abs-scaled MSE
  (F19/F20).
- **C-AMP** — amplitude/gain-vs-shape decomposed (scale-invariant) objective,
  motivated by M5a (helmholtz error 86.5% amplitude; per-sample rescale takes
  6.202 -> 0.839).
- **C-BAND** — band-weighted objective emphasizing the LOW wavenumber band,
  motivated by M3 (excess error in the lowest band, 5/5 datasets).
- **C-LFANCHOR** — training-time loss term anchoring the prediction's low-k
  band to the LF field (LF exists at training time even though the champion is
  LF-blind at inference).
- **C-STRUCT** — Sobolev/H1, gradient-domain, Charbonnier, SSIM-family
  structural objectives (the literal "interface-aware" reading of ADR 0012).

## Search terms used

1. `multi-fidelity neural network loss term consistency with low-fidelity input anchoring prediction coarse solution regularization`
2. `scale-invariant amplitude-decomposed loss neural operator surrogate per-sample gain shape decomposition PDE field`
3. `upweight low wavenumber band loss neural operator large-scale error dominant band-weighted objective surrogate`

(plus one follow-up fetch of the FNO paper for C-REL, below)

## Findings

### Term 1 — LF-anchoring / MF loss composition (refutes C-LFANCHOR?)

- **"Residual Multi-Fidelity Neural Network Computing" (arXiv:2310.03572)** —
  https://arxiv.org/abs/2310.03572 (fetched). Formulates "the correlation
  between an inexpensive low-fidelity model and an expensive high-fidelity
  model as a possibly non-linear residual function" mapping "the shared input
  space of the models along with the low-fidelity model output" to the
  discrepancy; two sequential networks, the first generating synthetic HF data
  for the second. The fetch classifies it as an **architecture/training-strategy
  change, not a loss modification**, and it works from "a small set of high- and
  low-fidelity data".
- Search-page context (not fetched): MF loss functions in the literature are
  `L_lf + L_hf (+ physics)` with **gradient-norm balancing** so no term
  dominates — "loss term normalization is especially important in multi-fidelity
  settings, where the model must reconcile abundant low-fidelity supervision
  with scarce high-fidelity labels". Also: computing the physics-constraint loss
  in the LF field rather than the HF field as a cost reduction.
- **Refutation outcome**: LF enters published MF methods as an *input* or as a
  separate data term with a scalar weight. I found **no** published objective
  whose term anchors a specified *spectral band* of the prediction to the LF
  field.

### Term 2 — scale/amplitude-invariant objectives in the PDE domain (refutes C-AMP?)

- **Li, Lanthaler, Deng, Chen, Wang, Azizzadenesheli, Anandkumar (2025),
  "Scale-Consistent Learning for Partial Differential Equations"** —
  https://arxiv.org/abs/2507.18813 (fetched). This is the nearest-named-neighbor
  and it is **not** the same object: their "scale" is **spatial domain
  rescaling**, not solution amplitude — "a given domain can be re-scaled to unit
  size, and the parameters and the boundary conditions of the PDE can be
  appropriately adjusted". Data-augmentation + consistency loss across
  sub/super-sampled domains; Burgers, Darcy, Helmholtz, Navier-Stokes; 34%
  average error reduction and Re 1000 -> 250-10,000 generalization.
- Nothing in the retrieved set decomposes the training loss into a per-sample
  **gain** and a **shape** component for field regression. Combined with
  iteration 4's Eigen et al. (2014) finding (scale-invariant log loss owns this
  mechanism in monocular depth, with the same oracle-substitution evidence
  pattern as our M5a), the picture is: **mechanism published in vision, name
  taken but meaning different in the PDE literature, composition unoccupied.**

### Term 3 — low-band-weighted objectives (refutes C-BAND?)

- **Sen & Maulik (2026), "Scale-Aware Learning of Chaotic Dynamics on
  Unstructured Meshes via Binned Spectral Losses"** —
  https://arxiv.org/html/2607.19387 (fetched). Binned spectral power (BSP) loss
  generalized to unstructured meshes via graph-Laplacian eigenvectors;
  frequencies partitioned into M disjoint bands weighted **uniformly via a
  relative energy-ratio formulation** that "penalizes relative under- or
  over-allocation of energy in each graph-frequency band"; the constant mode
  (lambda_1 = 0) is *excluded* from supervision. **Loss-only, backbone
  unchanged.** Tested on EAGLE, backward-facing step, 3-D wing pressure;
  improves long-horizon rollout (e.g. pressure-force error ~0.5 -> ~0.12-0.15
  over 1000 steps).
  This is the closest prior art to C-BAND: a relative, per-band energy-ratio
  objective is *exactly* the construction that would fix a low-band-dominant
  error, and it is published — albeit motivated by the opposite concern.
- Consistent framing across the retrieved set: "standard L2 error metrics
  overweigh low-wavenumber (high-energy) errors and underweigh high-wavenumber
  discrepancies"; radial r^alpha frequency weighting; adversarial training to
  fix high-k under-penalization. Every published motivation is high-k.
- With iteration 4's fetched sources (focal frequency loss, dynamic weight
  `w = |F_r − F_f|^alpha`, up-weights whichever band is currently worst
  regardless of type; the FNO spectrogram-loss study, loss-only, with
  documented over-constraint and conflicting-gradient failures; the
  spectral-bias survey that never discusses a low-band-dominant regime),
  C-BAND's mechanism is comprehensively preempted.

### Follow-up fetch for C-REL

- **Li et al. (2020), "Fourier Neural Operator for Parametric Partial
  Differential Equations"** — https://ar5iv.labs.arxiv.org/html/2010.08895
  (fetched). Honest result: the paper **reports** relative L2 error throughout
  (Tables 1, 3, 4; Figure 3) but **does not explicitly state the training
  loss**, and makes no relative-vs-MSE training comparison. So the widely
  repeated "relative-L2 training halves the error" claim remains **unverified by
  any source I fetched** and must not be cited. What IS established: relative L2
  is the reporting convention of the founding FNO paper, and the in-repo
  precedent for a per-sample relative training term is verified in
  `MODEL_TWEAKS_EVIDENCE.md` F19 (`transolver_residual/smoke_eval.py:65-69`,
  from `references/v9_baseline/train_v9.py:157-163`).

## PRIOR-ART VERDICT

| # | Candidate direction | Verdict | Fetched citations | What remains open |
|---|---|---|---|---|
| C-REL | Per-sample relative-L2 training loss + matching selection metric (F19/F20) | **preempted** | Li et al. 2020 FNO (https://ar5iv.labs.arxiv.org/html/2010.08895) reports rel-L2 as the field's convention; PDEBench (https://arxiv.org/abs/2210.07182, https://www.emergentmind.com/topics/pdebench) makes nRMSE a standard metric | Nothing novel. Legitimate ONLY as a controlled lever measurement ("how much of the panel gap is loss/metric mismatch?"), never as a contribution. In-repo precedent already exists. |
| C-AMP | Gain/shape-decomposed or scale-invariant objective (per-sample amplitude calibration) | **preempted-but-MF-composition-open** | Eigen et al. 2014 (https://ar5iv.labs.arxiv.org/html/1406.2283) owns the scale-invariant log loss + the oracle-rescale evidence pattern; Li et al. 2025 (https://arxiv.org/abs/2507.18813) owns "scale-consistent" in PDE learning but means SPATIAL rescaling, not amplitude | Open: an amplitude/shape-decomposed objective for **multi-fidelity PDE field regression**, evaluated on unchanged per-sample rel-L2. No fetched source applies gain-invariant training to neural PDE surrogates, and the PDE paper that owns the word "scale" means something else. Caveat: a *fully* scale-invariant loss cannot be scored well by rel-L2 (which does penalize amplitude); the defensible design is a **two-term decomposition** (shape term + explicit gain-calibration term), not scale invariance. |
| C-BAND | Band-weighted objective emphasizing the LOW-k band (fixed or error-adaptive) | **preempted-but-MF-composition-open** | Sen & Maulik 2026 (https://arxiv.org/html/2607.19387) BSP relative per-band energy-ratio loss, loss-only; Jiang et al. 2020 FFL (https://ar5iv.labs.arxiv.org/html/2012.12821) error-adaptive per-bin weights, up-weights whichever band is worst; FNO spectrogram loss (https://arxiv.org/html/2511.08753) loss-only frequency supervision with documented over-constraint failure; Khodakarami et al. 2025 (https://arxiv.org/html/2602.19265v1) surveys spectral bias and never treats a low-band-dominant regime | Mechanism is preempted; do NOT claim a new loss. Open: (i) the **regime** — every published band loss is motivated by high-k under-weighting, whereas s2-B1 M3 measures low-band-dominant excess error with spurious high-k injection, so this would be the first reported *inversion*; (ii) the **MF composition** — band-weighted objectives applied to the HF stage of an LF->HF fusion model at small N_hf. |
| C-LFANCHOR | Training-time loss term anchoring the prediction's low-k band to the LF field | **preempted-but-MF-composition-open** | Liu et al. 2026 LatentFlowSR (https://arxiv.org/html/2604.09188v2): low-frequency replacement is **post-processing, "no explicit loss function incorporating low-frequency constraints"**; arXiv:2310.03572 residual MF NN (https://arxiv.org/abs/2310.03572): LF enters as an **input**, an architecture change | Open as an *objective-only* construction. BUT flag for the brainstormer: with the champion **LF-blind at inference** (s2-B1 M1), an LF-anchoring term is nearly identical in effect to C-BAND (LF/HF low-band coherence is 0.9999 on allen_cahn, 0.875 on helmholtz), and it can transmit **no per-sample LF information at test time**. Genuinely testing LF-anchoring requires LF at inference, which is an architecture change and belongs to s3_warp/s6_local, not s7. |
| C-STRUCT | Sobolev/H1, gradient-domain, Charbonnier, SSIM-family objectives | **preempted** | Cho, Ryu, Hwang 2024 (https://arxiv.org/abs/2402.09084) Sobolev training for operator learning; SSIM-loss family survey (https://www.emergentmind.com/topics/structural-similarity-loss): MS-SSIM (Snell 2015), S3IM (Xie 2023), Watson (Czolbe 2020), additive forms (Cao 2025), with documented gradient-vanishing in the multiplicative form; Dang, Schmidt, Hesser 2026 (https://arxiv.org/html/2605.19823) use L1 over L2 for discontinuities and document the jump double-count | Nothing meaningful for a *novelty* claim. Also **contraindicated by our own evidence**: M3 (excess error in the LOW band) and M4 (pfc error not interface-peaked) argue against derivative/interface upweighting as the first move; and the SSIM survey records no PDE-field application, so an SSIM transplant would be exploratory with a known optimization hazard. |

Citation-integrity note: every URL in this table was fetched in iterations 1-5
of THIS loop and appears in the corresponding iteration file. Leads that I
could not fetch (MiDaS scale-and-shift loss; the engrxiv FNO-limitations
preprint's amplitude-error statement; DRIFT-Net's radial r^alpha term;
SR^2-Net's degradation-consistency loss; PairDropGS's LFC loss; the "relative-L2
training halves error" claim) are recorded as **unverified leads** and must NOT
be cited by the brainstormer.
