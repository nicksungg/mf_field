# Parallel websearcher run (invocation B) — s2_beyond_copy batch 3

**Why this file exists.** Two websearcher invocations ran against this same
`websearches/s2_beyond_copy/batch_3/` directory concurrently on 2026-07-30
(08:51-09:00). Invocation A's `iteration_{1,3,4,5}.md` are the files present under
those names; invocation B's writes to those names were clobbered (and B clobbered A's
`iteration_2.md`, which is why `iteration_2.md` is B's). Rather than overwrite A's work
again, B's five turns are recorded here in full so that **every citation in `report.md`
resolves to a file in this directory together with its URL** (program.md §13.3). B ran
12 WebSearch + 12 WebFetch calls across 5 turns; the cap was respected.

---

## B-turn 1 — per-sample / instance-wise target normalization

**Terms**: (1) `per-sample instance normalization of targets neural operator training PDE
surrogate`; (2) `reversible instance normalization RevIN neural operator PDE distribution
shift`; (3) `sample-wise scaling of residual targets multi-fidelity correction network
varying magnitude normalization`.

- Operator-surrogate practice retrieved is **dataset-global** min-max ("variables
  normalized to [-1:1] with respect to the minima/maxima of the entire dataset").
  Search-listed: Operator Boosting https://arxiv.org/html/2606.17460; plasma-edge neural
  operator surrogates https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb;
  Neural-Parareal https://arxiv.org/pdf/2405.01355; NPSolver
  https://arxiv.org/pdf/2605.25786. The one instance-level use, P3D
  https://arxiv.org/html/2509.10186, is **adaptive instance norm as a conditioning
  device** inside a transformer backbone — feature space, not targets.
- **FETCHED** "On the Role of Reversible Instance Normalization"
  https://arxiv.org/html/2603.11869: scope stated as **exclusively time-series
  forecasting** (PatchTST + DLinear; Electricity/Solar/Traffic + synthetic), explicitly
  not PDE/operator learning; the learnable affine gives minimal benefit and does not
  address *conditional* distribution shift; and — load-bearing for us — "**training via
  backpropagation in the normalized space yields better models**" than computing the loss
  on denormalized predictions, even when the evaluation metric is un-normalized MSE.
  RevIN itself: https://openreview.net/forum?id=cGDAkQo1C0p (search-listed),
  project page https://seharanul17.github.io/RevIN/.
- MF residual-scale candidates surfaced: DeepONet MF residual ROM
  https://link.springer.com/article/10.1186/s40323-023-00249-9; MFRNP
  https://github.com/Rose-STL-Lab/MFRNP; RMFNN https://arxiv.org/pdf/2310.03572.

## B-turn 2 — heavy-tailed / ESS framing; is the standard operator loss already per-sample?
(= the surviving `iteration_2.md` in this directory; summarized here for completeness)

**Terms**: (1) `heavy-tailed loss dominated by few samples effective sample size MSE
reweighting scientific machine learning`; (2) `Fourier neural operator relative L2 loss
normalized per sample training objective instead of MSE`.

- **FETCHED** RMFNN via https://ar5iv.labs.arxiv.org/html/2310.03572 (the `/pdf/` URL
  returns raw binary — dead): "the residual is expected to have a small magnitude (or
  norm) relative to that of the high-fidelity quantity Q_HF";
  |F| <= c(h_HF^q + h_LF^q) <= (1+s^q) eps_TOL; "the size of the residual |F| is
  proportional to the small quantity eps_TOL". The scale is characterized **globally**
  and the paper introduces **no explicit scaling factor during training**.
  (Independently corroborates invocation A's iteration_3 fetch of the same paper.)
- Heavy-tail/ESS machinery is developed **outside** SciML: class-balanced effective-number
  reweighting https://arxiv.org/pdf/1901.05555 (search-listed); "standard machine learning
  models trained via MSE minimization are hypersensitive to these values ... forces the
  model to prioritize fitting the outliers at the expense of the structural majority"
  https://arxiv.org/html/2601.15360v1 (search-listed); ESS = (sum w)^2/sum w^2 as the
  standard weight-degeneracy diagnostic https://arxiv.org/pdf/2602.17616 (search-listed);
  imbalance-reweighting-as-inverse-problem https://arxiv.org/html/2605.10047v1.
- "Losses are typically relative" in operator learning appears only in search summaries;
  both attempts to pin an exact quote failed —
  https://arxiv.org/pdf/2512.01421 binary (DEAD), https://arxiv.org/abs/2512.01421
  **FETCHED** but abstract-only (Duruisseaux/Kossaifi/Anandkumar, 96-page practical FNO
  guide tied to NeuralOperator 2.0.0), and
  https://www.emergentmind.com/topics/fourier-neural-operators-fnos **FETCHED** but
  contains nothing on loss/normalization conventions. **Do not cite that claim.**

## B-turn 3 — no-harm / trust gate

**Terms**: (1) `no-harm guarantee corrector network fall back to input when correction
hurts safe residual correction`; (2) `selective prediction abstention neural operator PDE
surrogate fallback to baseline solver confidence gating`.

- **FETCHED** "No-Harm Physics-Informed Inverse Learning with Residual-Calibrated
  Uncertainty" https://arxiv.org/html/2606.07153. **Definition 3 is our gate verbatim**:
  "the learned reconstruction is selected only if R_learn <= R_base + eps_safe. If [this]
  fails, the method returns the baseline reconstruction." R aggregates data residual,
  **PDE residual**, BC/IC residual, optimization residual. Domain: PDE-governed inverse
  problems (source recovery, coefficient ID, tomography, IC reconstruction); "wraps any
  physics-informed inverse solver". Operates **per-sample at test time without ground
  truth**, using only computed residuals, the baseline's residuals, a known noise level
  and a conditional stability constant.
- **FETCHED** "Causality-Inspired Safe Residual Correction for Multivariate Time Series"
  https://arxiv.org/pdf/2512.22428 (partial): "Safety Before Optimality ... CRC is
  intentionally biased toward rejecting uncertain updates rather than risking
  degradation"; "when such structure is weak or absent, correction is naturally
  suppressed"; bounded degradation vs the base model. Domain: time series.
- **FETCHED** "Knowledge-Constrained Shape Optimization with a Mixture-of-Experts Neural
  Operator" https://arxiv.org/html/2607.09763: Mahalanobis-percentile gate in a frozen
  encoder latent space, threshold eta_sigma = 0.6 — "If sigma(theta_sur*) <= eta_sigma,
  the candidate is considered sufficiently supported by the current training database and
  no new physics solve is required" — fallback is an actual **HF solve**, with
  e_phys <= 0.025 and Delta J_val > 0 checks. A **physics-free, data-space** gate key.
- Search-listed: conformal prediction for neural operators
  https://arxiv.org/html/2606.09923; selective abstention overview
  https://www.emergentmind.com/topics/selective-abstention; residual-based error corrector
  operator for neural-operator surrogates
  https://www.sciencedirect.com/science/article/abs/pii/S0045782523007193.

## B-turn 4 — is the registration finding already published?

**Terms**: (1) `half-pixel misalignment align_corners resampling artifact contaminates
super-resolution benchmark evaluation`; (2) `grid staggering cell-centered vs node-centered
interpolation error multi-fidelity coarse-to-fine machine learning benchmark`.

- **FETCHED** "Enhanced Super-Resolution Training via Mimicked Alignment for Real-World
  Scenes" https://arxiv.org/html/2410.05410: "real-world datasets often suffer from
  misalignment issues between LR and HR images" (translations, scaling, rotation);
  "Despite these efforts, residual misalignment remains evident"; and decisively
  "**conventional SR metrics (PSNR/SSIM) cannot be reliably evaluated on the real-world
  dataset due to misalignment in the testing set**" — they switch to no-reference metrics.
  The misalignment there is optical and estimated, not a closed-form resampling convention.
- Search-listed: implicit resampling-based alignment for video SR
  https://arxiv.org/pdf/2305.00163 (fetch DEAD, >10 MB) — "alignment resampling operations
  can lead to the destruction of sub-pixel information ... the role of resampling in
  alignment has been overlooked"; Rethinking Alignment in Video SR Transformers
  https://proceedings.neurips.cc/paper_files/paper/2022/file/ea4d65c59073e8faf79222654d25fbe2-Paper-Conference.pdf.
- CFD/AMR side (all search-listed): "Grid staggering creates directional bias in
  interpolants due to source data nodes not being symmetrically placed about the target
  node location but offset" —
  https://resources.system-analysis.cadence.com/blog/dual-grid-interpolation-for-cell-centered-overset-grid-systems;
  cell- vs vertex-centred AMR https://arxiv.org/pdf/2406.09139; local ML CFD correction
  https://arxiv.org/pdf/2305.00114; CG-CFD error prediction
  https://www.anl.gov/event/coarsegrid-computational-fluid-dynamics-error-prediction-using-machine-learning.
- **No** result reports an ML MF/SR benchmark whose *no-learning coarse reference* was
  misregistered by the cell-centred-vs-node convention. (Invocation A reached the same
  conclusion from four independent framings, and additionally fetched the textbook
  statement of the convention mismatch — Gmunu, https://ar5iv.labs.arxiv.org/html/2001.05723.)

## B-turn 5 — refutation turn (cap)

**Terms**: (1) `ablation global versus per-sample normalization training data neural
operator accuracy scaling strategy PDE`; (2) `gating between low-fidelity solution and
neural correction per sample multi-fidelity fusion selecting best of two predictions`;
(3) `"multi-fidelity" learnable gating parameter alpha balance low-fidelity prediction and
correction term arXiv`.

- **FETCHED** QuadNorm, "Resolution-Robust Normalization for Neural Operators"
  https://arxiv.org/html/2605.07375: replaces "discrete averages with quadrature-weighted
  integrals" (trapezoidal weights, endpoints half weight),
  mu_c = sum_i w_i x_c(r_i)/sum_i w_i and matching sigma_c^2 — i.e. **per-sample,
  per-channel spatial statistics**, but applied to **feature activations**, "not inputs or
  targets", and the paper "does not explicitly ablate global vs. instance normalization"
  (it introduces BlendQuadNorm with a blending coefficient alpha). Also search-listed:
  NESTOR https://arxiv.org/html/2602.22059; LLT https://arxiv.org/html/2607.07718;
  PDE-Refiner https://papers.neurips.cc/paper_files/paper/2023/file/d529b943af3dba734f8a7d49efcb6d09-Paper-Conference.pdf;
  SPDEBench https://arxiv.org/pdf/2505.18511.
- **FETCHED** MF-BPINN, "Multi-Fidelity PINNs with Bayesian UQ and Adaptive Residual
  Learning" https://arxiv.org/html/2602.01176v1: an **input-dependent per-sample gate**
  alpha(x,t;mu) = sigma(N_g(x,t,mu,u_LF(x,t;mu); theta_g)) in (0,1) — it **reads the LF
  prediction** — forming a convex combination of linear and nonlinear correctors,
  reflecting "where the fidelity gap is primarily linear versus nonlinear", with explicit
  negative-transfer mitigation ("if a low-fidelity model is misleading in a region of
  parameter space, the gate can reduce reliance on the linear correlator") and
  **no explicit no-harm guarantee**.
- Search-listed: Multifidelity KAN https://arxiv.org/pdf/2410.14764 ("the high-fidelity
  prediction is a convex combination of the linear and nonlinear networks, given by a
  trainable parameter alpha"); AGMF-Net
  https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X (fetch **403
  DEAD**), "deep gated expert fusion with ensemble-based UQ ... under limited
  high-fidelity data"; MF-PINN survey context https://arxiv.org/pdf/2503.08408.

## B dead ends
- `https://arxiv.org/pdf/2310.03572` → raw binary; recovered via ar5iv.
- `https://arxiv.org/pdf/2512.01421` → binary (8.5 MB); `/abs/` had no loss/norm section.
- `https://www.emergentmind.com/topics/fourier-neural-operators-fnos` → fetched, contains
  nothing on losses/normalization.
- `https://arxiv.org/pdf/2305.00163` → maxContentLength exceeded.
- `https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X` → HTTP 403.
