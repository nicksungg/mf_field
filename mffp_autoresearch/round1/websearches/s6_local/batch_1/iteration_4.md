# iteration_4 — the tiny-N_hf regime, and multi-fidelity instances of hybrid/local operators

## Search rationale

Open questions 4 and 5, and the hinge of the whole stream. `program.md` §12.1
records N_hf = 5 on the IFC datasets and the mentor's report §5.3 predicts the
local branch's extra HF-fitted parameters are "a plausible route to *worse*
results than the incumbent through overfitting alone". If the literature shows
(a) hybrids evaluated only at N in the hundreds-to-thousands, and (b) MF-FNO
work that stops at N_hf ~ 100, then the tiny-N_hf x local-branch cell is
empirically unoccupied and that — not the architecture — is where any claim
must live. Term 1 targets the two anchors `MF_FNO_CNN_Hybrid_Report.md` §6.6
lists as "cited second-hand, not fetched".

## Search terms used

1. `multi-fidelity Fourier neural operator coarse simulation few high-fidelity samples transfer learning U-FNO carbon storage`
2. `neural operator small training data regime overfitting local convolutional branch versus spectral data efficiency 10 samples PDE surrogate`
3. (none — budget spent on fetches; the third slot was folded into the fetch of
   arXiv:2505.21573 surfaced by term 2)

## Findings per term

### Term 1 — MF-FNO for geological carbon storage (the §6.6 "not fetched" anchor)

- **Tang et al., "Multi-fidelity Fourier Neural Operator for Fast Modeling of
  Large-Scale Geological Carbon Storage", arXiv:2308.09113** (*Journal of
  Hydrology* 2024, https://www.sciencedirect.com/science/article/abs/pii/S0022169424000350 ,
  paywalled 403) — **abstract FETCHED verbatim** from
  https://arxiv.org/abs/2308.09113 . Confirmed content: multi-fidelity FNO,
  motivated by "the available training data are always limited"; grid
  invariance is the stated reason FNO makes **transfer between differently
  discretized datasets** easy; "predict with accuracy comparable to a
  high-fidelity model ... with **81% less data generation costs**"; and, on the
  1M-cell case with LF and HF from **different geostatistical models and
  reservoir simulators**, "can predict pressure fields with reasonable
  accuracy even when the high-fidelity data are **extremely limited**".
  What the fetched abstract does **not** state: the backbone variant, whether
  any U-Net/local path exists, the fine-tuning protocol, or the HF sample
  count. The search-result summary (not the paper) reports "only **100**
  high-fidelity datasets to fine tune". **So: MF + FNO + LF-pretrain/HF-finetune
  is unambiguously published (this is the acknowledged basis of the repo's own
  `mf_fno_transfer` family) — and no local/convolutional branch is evidenced
  in it.** N_hf ~ 100, an order of magnitude above this benchmark's 5.
- Related, not fetched: transfer learning with FNOs across saline aquifers
  https://www.sciencedirect.com/science/article/abs/pii/S1568494625005836 ;
  multifidelity training data + transfer learning for subsurface flow
  https://www.sciencedirect.com/science/article/abs/pii/S0021999122008634 .

### Term 2 — the small-data regime

- **CAUTION, name collision:** arXiv:2505.21573 is *also* abbreviated
  **SINO* — "Spectral-Inspired Neural Operator Learning with Limited Data and
  Unknown Physics", https://arxiv.org/html/2505.21573v3 — and is a **different
  paper** from arXiv:2606.18305 (Starter-Iterator SINO, iteration_3). FETCHED.
  Architecture: Freq2Vec frequency embeddings, spectral learning blocks,
  Pi-block multiplicative nonlinearity, 2/3-rule de-aliasing low-pass, RK4 —
  **explicitly "does not rely on local convolution operations"**. Data claim:
  *"with only **5 training trajectories**, SINO outperforms data-driven
  methods trained on 200 trajectories"*; baselines in that regime "produce
  severe artifacts or become numerically unstable". **Not multi-fidelity.**
  This is the strongest fetched counter-evidence to H2: at N=5 a *purely
  spectral, structure-heavy* model beats data-driven ones, i.e. tiny-N favors
  strong inductive bias / few parameters, which is an argument against adding
  a free-form local branch and for a **structurally constrained** one.
- Search-summary-grade corroboration of the same point: "spectral methods
  offer better data efficiency for PDE surrogates compared to purely local
  convolutional approaches, especially in very small data regimes"; iFNO's
  incremental spectral curriculum is cited as an overfitting mitigation.
- Also surfaced, not fetched: **DyMixOp** — "a neural operator designed from a
  complex dynamics perspective with **local-global mixing**"
  https://arxiv.org/pdf/2508.13490 ; the same summary names **Conv-FNO** as an
  existing "hybridization with local convolutional or differential/integral
  kernels ... to inject locality".

## Interpretation

The two cells that matter are now measured. (1) **Multi-fidelity FNO with
LF-pretrain/HF-finetune: published, no local branch, N_hf ~ 100.** (2)
**Local/hybrid operators: published, single-fidelity, N in the hundreds+.**
Nothing fetched occupies MF x local-branch x N_hf = 5. But iteration 4 also
produced the strongest *negative* prior for this stream: at N = 5, the fetched
evidence favors fewer, more constrained parameters — so a proposal that simply
bolts a ConvNeXt branch onto the champion and fine-tunes it on 5 HF samples is
predicted by the literature to overfit, exactly as the mentor's report §5.3
warned. Any s6 design must make the local branch **capacity-constrained and
identity-safe**, and must be judged on whether HF-supervised locality can be
made cheap enough to survive N_hf = 5.
