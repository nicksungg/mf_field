# Websearch Report — Stream `s7_loss`, Batch 1

**Stream**: s7_loss (lever, ADR 0012) — new stream, first pipeline agent
**Batch**: 1
**Total iterations**: 5 (cap hit: YES — k = 5 reached, noted in iteration_5.md)
**WebSearch calls**: 15 (3 per iteration)
**WebFetch calls**: 17 attempted / 13 usable (4 arXiv/engrxiv PDF fetches
returned unparsable binary and are reported as failures, not findings)

## Search trace

### Turn 1 — the three loss families
Terms: `Sobolev H1 loss training neural operator PDE surrogate sharp discontinuous
fields`; `frequency-weighted spectral loss training Fourier neural operator high
frequency band`; `loss function comparison neural PDE surrogate relative L2 vs MSE
normalization ablation`. Chosen to cover the derivative-domain, frequency-domain
and normalization axes named in the task before narrowing.
Key findings: Sobolev training for operator learning is published
[cite: https://arxiv.org/abs/2402.09084]; Cut-DeepONet trains with **L1 not L2**
for discontinuities and documents that a correctly-sharp-but-displaced jump is
"evaluated on both sides of the jump, effectively doubling the contribution"
[cite: https://arxiv.org/html/2605.19823]; the leading spectral-bias fix in
neural operators is an **architecture** change, not a loss
[cite: https://arxiv.org/abs/2503.13695]. → iteration_1.md

### Turn 2 — amplitude calibration, normalized losses, low-frequency faithfulness
Terms: `amplitude calibration scale mismatch neural operator prediction per-sample
normalization scale-equivariant training field regression`; `PDEBench PDEArena
normalized RMSE training loss choice nRMSE relative error benchmark`;
`low-frequency consistency loss preserve input low band super-resolution avoid
degrading coarse input`. Chosen because s2-B1's M5a (86.5% amplitude) and M3
(low-band excess) promote (b) and (c) above the ADR's literal interface framing.
Key findings: no published *training objective* decomposing amplitude vs shape
for PDE surrogates (term 1 returned UQ "calibration" instead); PDEBench's metric
panel already includes per-band fRMSE and the near-zero-magnitude nRMSE caveat
[cite: https://arxiv.org/abs/2210.07182, https://www.emergentmind.com/topics/pdebench];
low-frequency replacement in audio SR is **post-processing with no loss term**
[cite: https://arxiv.org/html/2604.09188v2]. → iteration_2.md

### Turn 3 — MF regime, SSIM family, interface weighting
Terms: `multi-fidelity operator learning loss function weighting few high-fidelity
samples training objective`; `structural similarity SSIM loss gradient loss
training surrogate model turbulence field prediction sharper`; `interface-aware
weighted loss phase field simulation deep learning gradient magnitude weight map
sharp interface`.
Key findings: MF fusion is carried by architecture + scalar per-fidelity loss
weights, not by objective shape [cite: https://arxiv.org/abs/2204.06684]; the
SSIM-loss literature records **no PDE-field application** and a gradient-vanishing
hazard [cite: https://www.emergentmind.com/topics/structural-similarity-loss];
the published "interface-localized" losses are PINN losses whose weights are
equation-derived — and the top hit does not even use band localization, it uses
gradient-norm balancing [cite: https://arxiv.org/html/2502.02440v1]. Declared
**ENOUGH** on field context at the end of this turn. → iteration_3.md

### Turn 4 — refutation, part 1
Terms: `scale-invariant loss scale-and-shift invariant training regression depth
estimation Eigen MiDaS amplitude ambiguity`; `focal frequency loss spectral loss
neural operator PDE emphasize low frequency band error reweighting`; `"relative
L2" loss training Fourier neural operator standard practice Li 2020 loss function`.
Key findings: Eigen's scale-invariant log loss owns the gain-ambiguity mechanism,
with an oracle-substitution experiment isomorphic to our M5a
[cite: https://ar5iv.labs.arxiv.org/html/1406.2283]; focal frequency loss
up-weights whichever bins are currently worst, low or high, with no PDE evaluation
[cite: https://ar5iv.labs.arxiv.org/html/2012.12821]; a loss-only spectrogram
objective for FNOs exists and **fails by over-constraint OOD** with conflicting
time/frequency gradients [cite: https://arxiv.org/html/2511.08753]; the
operator-learning spectral-bias survey never treats a low-band-dominant regime and
ranks optimizer choice above loss redesign [cite: https://arxiv.org/html/2602.19265v1].
→ iteration_4.md

### Turn 5 — refutation, part 2 + verdict (CAP)
Terms: `multi-fidelity neural network loss term consistency with low-fidelity input
anchoring prediction coarse solution regularization`; `scale-invariant
amplitude-decomposed loss neural operator surrogate per-sample gain shape
decomposition PDE field`; `upweight low wavenumber band loss neural operator
large-scale error dominant band-weighted objective surrogate`; plus a follow-up
fetch of the FNO paper for C-REL.
Key findings: residual MF networks put LF in as an **input** (architecture)
[cite: https://arxiv.org/abs/2310.03572]; "Scale-Consistent Learning for PDEs"
means **spatial** rescaling, not amplitude [cite: https://arxiv.org/abs/2507.18813];
binned spectral power losses with **relative per-band energy ratios** are published
and loss-only [cite: https://arxiv.org/html/2607.19387]; the founding FNO paper
reports relative L2 but **does not state its training loss**, so the popular
"rel-L2 training halves the error" claim is unverified
[cite: https://ar5iv.labs.arxiv.org/html/2010.08895]. → iteration_5.md

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **C-REL** — per-sample relative-L2 training loss + matching model-selection metric (F19/F20) | **preempted** | https://ar5iv.labs.arxiv.org/html/2010.08895 ; https://arxiv.org/abs/2210.07182 ; https://www.emergentmind.com/topics/pdebench | Nothing novel; in-repo precedent already exists (`transolver_residual/smoke_eval.py:65-69`). Defensible ONLY as a controlled measurement of how much panel gap is loss/metric mismatch. Must never be written up as a contribution. |
| **C-AMP** — gain/shape-decomposed (per-sample amplitude-calibrating) objective | **preempted-but-MF-composition-open** | https://ar5iv.labs.arxiv.org/html/1406.2283 (Eigen 2014 scale-invariant log loss + oracle-rescale evidence) ; https://arxiv.org/abs/2507.18813 (PDE "scale-consistent" = spatial rescaling, NOT amplitude) | Open: amplitude/shape-decomposed objective for **multi-fidelity PDE field regression scored on unchanged per-sample rel-L2**. No fetched source applies gain-invariant training to neural PDE surrogates. Design constraint: full scale-invariance is unscoreable under rel-L2 — use a two-term (shape + explicit gain) objective, not an invariant one. |
| **C-BAND** — band-weighted objective emphasizing the LOW-k band (fixed or error-adaptive) | **preempted-but-MF-composition-open** | https://arxiv.org/html/2607.19387 (BSP relative per-band energy ratio, loss-only) ; https://ar5iv.labs.arxiv.org/html/2012.12821 (FFL error-adaptive bin weights) ; https://arxiv.org/html/2511.08753 (loss-only FNO spectrogram loss + its failure modes) ; https://arxiv.org/html/2602.19265v1 (survey never treats low-band-dominant error) | Mechanism fully preempted — claim no new loss. Open: the **regime inversion** (all published band losses target high-k under-weighting; our M3 measures low-band-dominant excess with spurious high-k injection) and the **MF composition** (HF stage of an LF→HF fusion model, small N_hf). |
| **C-LFANCHOR** — training-time loss anchoring predicted low-k band to the LF field | **preempted-but-MF-composition-open** (but likely degenerate here) | https://arxiv.org/html/2604.09188v2 (LFR is post-processing; "no explicit loss function incorporating low-frequency constraints") ; https://arxiv.org/abs/2310.03572 (LF as input = architecture change) | Open as an objective-only construction, BUT with the champion LF-blind at inference (s2-B1 M1) it is near-identical to C-BAND (LF/HF low-band coherence 0.9999 allen_cahn, 0.875 helmholtz) and transmits no per-sample LF information at test time. Real LF anchoring needs LF at inference = architecture = s3_warp/s6_local, not s7. |
| **C-STRUCT** — Sobolev/H1, gradient-domain, Charbonnier, SSIM-family | **preempted** | https://arxiv.org/abs/2402.09084 (Sobolev training for operator learning) ; https://www.emergentmind.com/topics/structural-similarity-loss (MS-SSIM/S3IM/Watson/additive; gradient-vanishing hazard; no PDE application) ; https://arxiv.org/html/2605.19823 (L1 over L2 for discontinuities; jump double-count) | No novelty available. Additionally contraindicated by our own diagnostics (M3 low-band excess; M4 pfc error not interface-peaked). Keep only as a control arm if the card wants to test the ADR's literal interface hypothesis and falsify it cheaply. |

## Citations summary

- [Cho, Ryu & Hwang 2024] "Sobolev Training for Operator Learning" — https://arxiv.org/abs/2402.09084 — used in: iteration_1.md, verdict C-STRUCT
- [Dang, Schmidt & Hesser 2026] "Smooth Piecewise Cutting for Neural Operator to Handle Discontinuities and Sharp Transitions" — https://arxiv.org/html/2605.19823 — used in: iteration_1.md, verdict C-STRUCT
- [Khodakarami, Oommen, Bora & Karniadakis 2025] "Mitigating Spectral Bias in Neural Operators via High-Frequency Scaling for Physical Systems" — https://arxiv.org/abs/2503.13695 — used in: iteration_1.md
- [Takamoto et al. 2022] "PDEBench: An Extensive Benchmark for Scientific Machine Learning" — https://arxiv.org/abs/2210.07182 (+ metric enumeration https://www.emergentmind.com/topics/pdebench) — used in: iteration_2.md, verdict C-REL
- [Liu et al. 2026] "LatentFlowSR: High-Fidelity Audio Super-Resolution via Noise-Robust Latent Flow Matching" — https://arxiv.org/html/2604.09188v2 — used in: iteration_2.md, verdict C-LFANCHOR
- [Lu, Pestourie, Johnson & Romano 2022] "Multifidelity deep neural operators ... nanoscale heat transport" — https://arxiv.org/abs/2204.06684 — used in: iteration_3.md
- [SSIM-loss survey] "Structural Similarity Loss" (MS-SSIM Snell 2015; S3IM Xie 2023; Watson Czolbe 2020; additive Cao 2025) — https://www.emergentmind.com/topics/structural-similarity-loss — used in: iteration_3.md, verdict C-STRUCT
- [Mullins, Kamila, Fahsi & Soulaimani 2025] "PINNs for solving moving interface flow problems using the level set approach" — https://arxiv.org/html/2502.02440v1 — used in: iteration_3.md
- [Eigen, Puhrsch & Fergus 2014] "Depth Map Prediction from a Single Image using a Multi-Scale Deep Network" — https://ar5iv.labs.arxiv.org/html/1406.2283 — used in: iteration_4.md, verdict C-AMP
- ["Fourier Neural Operators for Structural Dynamics Models: ... Spectrogram Loss" 2025/26] — https://arxiv.org/html/2511.08753 — used in: iteration_4.md, verdict C-BAND
- [Jiang, Dai, Wu & Loy 2020] "Focal Frequency Loss for Image Reconstruction and Synthesis" — https://ar5iv.labs.arxiv.org/html/2012.12821 — used in: iteration_4.md, verdict C-BAND
- [Khodakarami et al. 2025] "Spectral bias in physics-informed and operator learning: Analysis and mitigation guidelines" — https://arxiv.org/html/2602.19265v1 — used in: iteration_4.md, verdict C-BAND
- ["Residual Multi-Fidelity Neural Network Computing" 2023] — https://arxiv.org/abs/2310.03572 — used in: iteration_5.md, verdict C-LFANCHOR
- [Li, Lanthaler, Deng, Chen, Wang, Azizzadenesheli & Anandkumar 2025] "Scale-Consistent Learning for Partial Differential Equations" — https://arxiv.org/abs/2507.18813 — used in: iteration_5.md, verdict C-AMP
- [Sen & Maulik 2026] "Scale-Aware Learning of Chaotic Dynamics on Unstructured Meshes via Binned Spectral Losses" — https://arxiv.org/html/2607.19387 — used in: iteration_5.md, verdict C-BAND
- [Li, Kovachki, Azizzadenesheli, Liu, Bhattacharya, Stuart & Anandkumar 2020] "Fourier Neural Operator for Parametric Partial Differential Equations" — https://ar5iv.labs.arxiv.org/html/2010.08895 — used in: iteration_5.md, verdict C-REL

**Unverified leads — MUST NOT be cited**: MiDaS scale-and-shift-invariant loss
(Ranftl et al.); the engrxiv "Limitations of FNO" amplitude-error statement;
DRIFT-Net's radial r^alpha frequency weight (arXiv:2509.24868); SR^2-Net
degradation-consistency loss (arXiv:2601.21338); PairDropGS low-frequency
consistency loss (arXiv:2605.12072); the "relative-L2 training halves test
error vs MSE" claim; the "nRMSE gives up to 9.3% lower training loss" claim.

## Dead ends

- `amplitude calibration ... neural operator` → returns conformal-prediction /
  UQ "calibration", a different sense of the word. No objective-design results.
- `interface-aware weighted loss phase field ...` → entirely PINN/physics-embedded
  (fracture, level-set, PINO); weights are equation-derived, so ADR-0009-blocked,
  and the top hit uses gradient-norm balancing rather than band localization.
- PDF endpoints (arxiv.org/pdf/*, papers.neurips.cc/*, engrxiv.org/*) returned
  unparsable binary 4/4 times. Use `arxiv.org/abs`, `arxiv.org/html`, or
  `ar5iv.labs.arxiv.org/html` instead — that worked 9/9.
- Searching for a primary source for "relative-L2 training halves error" →
  the claim is repeated everywhere and substantiated nowhere I could fetch.

## For the brainstormer

The brainstormer MUST quote the verdict row for whatever it proposes.

1. **Re-rank away from the ADR's literal framing.** ADR 0012 seeds
   "interface-aware" objectives; the fetched literature makes C-STRUCT
   **preempted** and s2-B1's M3/M4 make it *empirically contraindicated*
   (excess error in the LOWEST band 5/5; pfc error not interface-peaked). The
   two directions with open composition are **C-AMP** (amplitude/gain) and
   **C-BAND** (low-band-weighted), in that order.
2. **C-AMP is the best-supported card.** Eigen 2014's oracle-substitution
   experiment (20% relative improvement from substituting the true mean depth)
   is the same experiment as M5a (6.202 → 0.839 from one per-sample scalar), and
   the remedy — a loss that separates gain from shape — is unoccupied in the PDE
   literature (https://arxiv.org/abs/2507.18813 takes the *word* "scale" for
   spatial rescaling only). **Design constraint from the verdict**: do not
   propose a scale-*invariant* loss — rel-L2 scores amplitude, so invariance
   would be self-defeating. Propose a two-term objective (normalized-shape term
   + explicit per-sample gain term, e.g. predicted-vs-optimal alpha) and
   pre-register the trade-off.
3. **C-BAND must be framed as a regime test, not a new loss.** Sen & Maulik's
   relative per-band energy-ratio BSP loss and Jiang's error-adaptive FFL
   already own the mechanism. The claimable content is that every published
   band loss exists to *add* high-k energy, whereas our champion injects
   spurious high-k and fails in the low band — so the honest card asks "does
   inverting the published weighting direction help on a low-band-dominant MF
   problem?" Cite https://arxiv.org/html/2607.19387 and
   https://ar5iv.labs.arxiv.org/html/2012.12821 in `prior_art`.
4. **Pre-register the two documented failure modes of loss-only interventions.**
   From https://arxiv.org/html/2511.08753 (loss-only, FNO, architecture fixed —
   the closest methodological analogue to this whole stream): (i) a frequency
   objective **over-constrains** and collapses off-distribution because the
   model "was explicitly trained to suppress exactly the spectral features"
   needed; (ii) time-domain and frequency-domain terms produce **conflicting
   gradients** and non-monotonic behavior; (iii) loss changes **cannot** repair
   an architectural truncation limit. Falsification clauses should name these.
   Mitigation with a fetched precedent: gradient-norm balancing of multi-term
   losses (iteration_3.md, https://arxiv.org/html/2502.02440v1).
5. **C-LFANCHOR is probably degenerate for this stream — say so rather than
   proposing it.** The champion is LF-blind at inference (s2-B1 M1), and LF/HF
   low-band coherence is 0.9999 (allen_cahn) / 0.875 (helmholtz), so anchoring
   the low band to LF ≈ upweighting the low band against HF. A real LF-anchored
   objective needs LF at inference, which is an architecture change and belongs
   to s6_local / s3_warp.
6. **C-REL belongs in the card as the control arm, not the headline.** It is
   preempted and has in-repo precedent (F19/F20), but under ADR 0007's screen
   it is the natural baseline arm: it isolates how much of the gap is pure
   loss/metric mismatch before any structured objective is credited. Note the
   PDEBench caveat that normalized errors diverge for near-zero-magnitude
   solutions (https://www.emergentmind.com/topics/pdebench) — clamp the
   denominator as `transolver_residual` already does.
7. **Thresholds**: helmholtz's `min_claimable_effect` is 9.695 skill
   (`state/noise_floor.json`) — the dataset that motivates C-AMP is the one
   where **no numeric claim is defensible**. Falsification must be stated on
   allen_cahn (1.633) / pfc (1.151) / cahn_hilliard (0.553) / fisher_kpp
   (0.418), or on the panel geomean against the 6.703 anchor
   (`state/anchors/s5_tuning.json`), with helmholtz reported qualitatively.
