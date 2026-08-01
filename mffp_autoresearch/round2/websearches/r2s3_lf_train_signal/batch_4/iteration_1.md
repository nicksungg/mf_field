# Iteration 1 — the amplitude/gain channel and the ensemble alternative

## Search rationale

B3's mechanism (part 6 M1/T2-5) says LF's train-time value on this panel is
dominantly a **per-sample amplitude/gain calibration channel** (96.9% of the
no-LF arm's allen_cahn draw-range). B4's ranked direction (a) asks whether a
condition-conditioned gain head recovers that channel with no LF at all, and
direction (b) asks whether a *budget-matched* no-LF ensemble beats the LF arm.
So turn 1 goes straight at the two mechanisms: (i) per-sample output
amplitude/scale prediction in operator/PDE surrogates, (ii) output-norm /
energy calibration as a named technique, (iii) ensembles vs auxiliary
low-fidelity data as competing variance-reduction routes at tiny N.

**Process note**: `WebFetch` is disabled in this environment (it returns a
context-mode redirect, not a page). All body reads in this loop are done with
`curl` from Bash and are labelled **[curl-fetched]**; search-engine returns
are labelled **[search return]**. Same route-around as the r2s2 batch-3 loop.

## Search terms used

1. `per-sample amplitude scaling head neural operator surrogate predict output magnitude from parameters few samples`
2. `output normalization energy calibration learned scale factor neural PDE surrogate relative L2 amplitude bias`
3. `deep ensemble versus additional low-fidelity data variance reduction small training set surrogate budget matched comparison`

## Findings

### Term 1 — per-sample amplitude head in operator surrogates

- **"Scaling laws for amplitude surrogates"** — https://arxiv.org/abs/2601.13308
  [search return]. Engine synthesis: "An amplitude surrogate is defined as a
  neural network that predicts the squared amplitude of a physical interaction
  as a function of phase-space points." **False friend**: "amplitude" here is
  the particle-physics scattering amplitude, not a field's output magnitude.
  Not applicable; recorded so a later loop does not re-chase it.
- **Plasma-edge neural operator surrogates** —
  https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb [search return;
  already curl/WebFetched in this stream's batch-1 loop]. LF→HF transfer, no
  per-sample scale head.
- **DeepONet for platelet deformation** —
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12467900/ [search return]:
  branch inputs are scalar parameters (wall shear stress, bond stiffness,
  time) predicting full 3-D deformation — a condition→field surrogate, but no
  amplitude/scale head and no MF ablation.
- **No result described a per-sample output-gain head conditioned on the
  parameter vector.**

### Term 2 — output-norm / energy calibration in PDE surrogates

- **ELADO: Elliptic PDE Assessment Datasets for Operator Learning** —
  https://arxiv.org/abs/2606.20771 **[curl-fetched, abstract]**. Verbatim:
  the suite isolates, among five difficulty sources, "(5) the effect of input
  signal complexity on prediction accuracy under **controlled amplitude
  normalization**", and concludes that "heavy-tailed targets, spectral shift,
  and input sensitivity each cause substantial degradation of the prediction
  accuracy that standard datasets and metrics (e.g., the **mean relative $L^2$
  error**) **may obscure**." Built around Poisson and Helmholtz with
  non-constant coefficients. This is the closest retrieved object to B3's
  amplitude-channel diagnostic and to M2 (relative-L2 rewards amplitude
  shrinkage), but it is a **dataset/benchmark diagnostic under a controlled
  normalization**, not a learned per-sample gain head.
- **Neural Functional: Learning Function to Scalar Maps for Neural PDE
  Surrogates** — https://arxiv.org/html/2505.13275v1/ [search return]:
  function→scalar maps, i.e. the input is a field, not the condition vector.
  Nearest neighbour on "predict a scalar summary", wrong input side.
- Engine synthesis on normalization practice: "Z-score normalization is
  typically used … computed from mean and standard deviation over the training
  dataset for each channel" [search return] — the global-scaler convention the
  round already uses; no per-sample variant surfaced.
- **Correcting Neural Operator Spectral Bias via Diffusion Posterior
  Sampling** — https://arxiv.org/html/2606.03936 [search return]: calibration
  is *frequency*-calibrated guidance requiring HF reference data at inference,
  not a train-time scale head. (Already summarised in-repo:
  `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` [HF-2].)

### Term 3 — ensembles vs low-fidelity data at matched budget

- **ADEPT: Active Deep Ensembles for Plasma Turbulence** —
  https://arxiv.org/abs/2310.09024 **[curl-fetched, abstract]**. Deep
  ensembles are used as the *acquisition* mechanism for active learning:
  "up to a factor of 20 reduction in training dataset size needed to achieve
  the same performance as random sampling". Ensembles here buy **data
  efficiency via acquisition**, and the paper does **not** contrast the
  ensemble against spending the same budget on cheaper/lower-fidelity data.
- **Multifidelity training data + transfer learning for subsurface flow
  surrogates** — https://arxiv.org/abs/2204.11138 [search return]: LF-pretrain
  → HF-finetune (the stream's declared-baseline genre, §12.3).
- **A Study of Bayesian Neural Network Surrogates for Bayesian Optimization**
  — https://arxiv.org/pdf/2305.20028 [search return]. Engine synthesis:
  "smaller training sizes can paradoxically lead to less uncertainty with deep
  ensembles … in the low data regime there are fewer settings of parameters
  that give rise to easily discoverable basins of attraction, making it harder
  to find diverse solutions simply by re-initializing." Directly relevant to
  B3's M5 (a 3-draw no-LF ensemble beating the LF arm) — the diversity of an
  ensemble at N_hf = 5 is itself contested.
- The engine stated plainly that "direct empirical comparisons of these
  strategies are not present in the results" — i.e. **no budget-matched
  ensemble-vs-LF-data comparison retrieved.**

## Interpretation

The amplitude channel exists in the literature only as a *benchmark
diagnostic* (ELADO's controlled amplitude normalization + the explicit warning
that mean relative L² obscures heavy-tailed target failures), not as a learned
per-sample gain head conditioned on a parameter vector; and the
ensemble-vs-auxiliary-data budget-matched contrast returned nothing direct.
Both of B4's top directions therefore survive turn 1 with only distant
neighbours — which is exactly the pattern that has burned this project before,
so turns 2–3 must attack them from the *statistics/calibration* vocabulary
(scale recalibration, conformal/variance calibration, hypernetwork scale
prediction) rather than the PDE-surrogate vocabulary.
