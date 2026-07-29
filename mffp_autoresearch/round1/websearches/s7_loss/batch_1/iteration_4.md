# iteration_4 — s7_loss / batch 1

## Search rationale

ENOUGH on general field context after iteration 3 — the three loss families and
the MF-regime picture are established. This iteration begins the §3.3
refutation work by pinning down *fetched* sources for the three candidate
directions I expect the brainstormer to propose, in the order the s2-B1
evidence ranks them:
- **C-AMP** amplitude/gain-vs-shape decomposed objective (M5a: 86.5% amplitude);
- **C-BAND** band-weighted objective aimed at the LOW band (M3: excess error in
  the lowest band, 5/5) — note this is the *reverse* of the published direction;
- **C-REL** metric-aligned per-sample relative-L2 training + selection loss
  (F19/F20).

## Search terms used

1. `scale-invariant loss scale-and-shift invariant training regression depth estimation Eigen MiDaS amplitude ambiguity`
2. `focal frequency loss spectral loss neural operator PDE emphasize low frequency band error reweighting`
3. `"relative L2" loss training Fourier neural operator standard practice Li 2020 loss function`

## Findings

### Term 1 — scale/amplitude-invariant objectives (refutation target for C-AMP)

- **Eigen, Puhrsch, Fergus (2014), "Depth Map Prediction from a Single Image
  using a Multi-Scale Deep Network"** — https://ar5iv.labs.arxiv.org/html/1406.2283
  (fetched). The scale-invariant log-space loss is
  `D(y,y*) = (1/n) Σ (log y_i − log y*_i + α(y,y*))²` with
  `α = (1/n) Σ (log y*_i − log y_i)` chosen to minimize the error for the pair;
  in training they interpolate to the scale-dependent loss with `λ = 0.5`.
  Motivation: "the global scale of a scene is a fundamental ambiguity in depth
  prediction", supported by an **oracle-substitution experiment** — replacing
  the predicted mean depth with ground-truth mean depth gives a 20% relative
  improvement for Make3D (0.41 -> 0.33 log-RMSE) and 0.28 -> 0.22 for their own
  system, i.e. "a large fraction of the total error".
  **This is methodologically the same experiment as s2-B1's M5a** (optimal
  per-sample rescale, 6.202 -> 0.839) and the same remedy family.
- MiDaS (Ranftl et al., 2022) scale-**and-shift**-invariant loss appeared only
  as search-page text (motivation: mixing datasets with different scales and
  shifts). Not fetched -> not citable here; recorded as a lead.
- **Verdict material**: gain/scale-invariant training objectives are firmly
  published — in monocular depth estimation, not in PDE surrogate learning. The
  open composition is the transplant + the multi-fidelity twist.

### Term 2 — frequency-weighted objectives (refutation target for C-BAND)

- **Cardoni et al. / "Fourier Neural Operators for Structural Dynamics Models:
  Challenges, Limitations and Advantages of Using a Spectrogram Loss"
  (2025/2026)** — https://arxiv.org/html/2511.08753 (fetched). Strictly a
  **loss-only** change with unchanged FNO architecture:
  `L_total = α L_MSE + (1−α) L_spectral` (α = 0.8), spectral term =
  magnitude (normalized Frobenius of STFT magnitude differences) + circular
  phase error, weighted 1.0 : 0.1, masked to f ≤ 4 Hz. Three findings that
  directly shape our design and our falsification clause: (i) loss modification
  **cannot** overcome architectural mode truncation ("FNOs fail catastrophically
  for non-linear systems, regardless of training data size"); (ii) the
  spectrogram loss **overconstrains** and collapses out-of-distribution because
  "the model was explicitly trained to suppress exactly the spectral features"
  needed; (iii) "non-monotonic behavior" from **conflicting gradients between
  time and frequency objectives**. This is the single most useful cautionary
  citation for s7.
- **Jiang, Dai, Wu, Loy (2020), "Focal Frequency Loss for Image Reconstruction
  and Synthesis"** — https://ar5iv.labs.arxiv.org/html/2012.12821 (fetched).
  `FFL = (1/MN) Σ w(u,v) |F_r(u,v) − F_f(u,v)|²` with dynamic spectrum weight
  `w(u,v) = |F_r(u,v) − F_f(u,v)|^α` normalized to [0,1]. Crucially, it
  **up-weights whichever frequencies are currently hardest — low OR high** —
  "not frequency band type". Tested on autoencoders, VAEs, pix2pix, SPADE,
  StyleGAN2 (i.e. **no PDE / operator-learning evaluation**).
  So an error-adaptive band weighting that happens to emphasize the low band is
  *mechanically* preempted by FFL, even though FFL was never run on PDE fields.
- **Khodakarami et al. (2025), "Spectral bias in physics-informed and operator
  learning: Analysis and mitigation guidelines"** —
  https://arxiv.org/html/2602.19265v1 (fetched). Investigates a **binned
  spectral power (BSP) loss** as an alternative to L², but concludes optimizer
  choice (SS-Broyden) and activations (SIREN) matter more than loss redesign.
  Explicitly: the paper **does not discuss scenarios where the low-frequency
  band is error-dominant** — it frames spectral bias uniformly as "high-frequency
  modes converge slower". Our M3 regime is outside the framing of the survey
  that owns this topic.

### Term 3 — relative-L2 as the training loss (refutation target for C-REL)

- Search-page result (Li et al. 2020 FNO): "Li et al. use the relative L2 error
  to measure performance. Using relative error to train the model has a good
  normalization and regularization effect that prevents overfitting, and
  training with the relative L2 loss results in around half the testing error
  rate compared to training with the MSE loss." I could not fetch a primary
  source for this in-loop (the two candidate PDFs, arXiv:2108.08481 and the
  engrxiv FNO-limitations preprint, both returned unparsable binary), so I
  record it as **strong but unverified**; the in-repo precedent
  (`transolver_residual/smoke_eval.py:65-69` <- `references/v9_baseline/train_v9.py:157-163`,
  per MODEL_TWEAKS_EVIDENCE F19) is verified and is enough to justify the change
  without any novelty claim.

## Interpretation

Every mechanism in the candidate pool has a published ancestor, but each
ancestor sits in a different regime: scale-invariant losses in monocular depth,
error-adaptive frequency weighting in image synthesis, spectrogram losses in
structural dynamics with a documented over-constraint failure, and the operator-
learning spectral-bias literature framed exclusively around the *opposite* band.
One more iteration is needed to test the two genuinely MF-specific claims
(LF-anchored objective; objective-vs-architecture at N_hf small).
