# Websearch Report — Stream `s2_beyond_copy`, Batch 2

**Stream**: s2_beyond_copy
**Batch**: 2
**Total iterations**: 5 (cap hit)
**Total WebSearch calls**: 14 (3+3+3+2+3; never more than 3 per turn)
**Total WebFetch calls**: 12 (8 usable, 4 dead — all four were `arxiv.org/pdf/`
URLs returning undecoded binary; each is named in its iteration file)
**Cap hit**: **YES** — 5 of 5 iterations used; noted in `iteration_5.md` header.

**What this batch had to decide**: batch 1 (card `B1.json` parts 6-7) found that
0 of 27 zoo families read the test LF field at inference, and that a
ZERO-PARAMETER rule (`copy-LF + mean of the 5 nearest training residuals`,
keyed on a 16x16 LF-field signature) reaches panel geomean skill 0.7886 vs the
champion's 9.6362. Part 7 prescribes B2: LF field as an input channel to the
FiLM-FNO, residual target, falsification anchored on the 0.79 floor. This
search had to establish, adversarially, what of that is new.

## Search trace

### Turn 1 — coarse-field-in / residual-out neural operators
**Terms** (and why): the prescribed candidate's exact composition, in the
operator vocabulary, in the MF vocabulary, and in the SR/coarse-correction
vocabulary — three names for the same shape.
- `neural operator takes coarse solution as input channel predicts correction residual multi-fidelity fine grid`
  → **LRC-FNO**: "The upsampled coarse solution and the source proxy are then
  concatenated as the input of the Residual-Closure FNO"; "The final
  full-resolution solution field is obtained by adding the coarse solution and
  the residual correction"; and it does **not** baseline against the coarse
  solution alone. [cite: https://arxiv.org/html/2606.17733] → `iteration_1.md`
- `multi-fidelity fusion model concatenate low-fidelity field input channel FNO predict HF-LF residual few high-fidelity samples`
  → MF-FNO transfer learning is the *champion's* mechanism ("jointing abundant
  low-fidelity data and limited high-fidelity data under transfer learning
  paradigm"), not the candidate's. [cite: https://arxiv.org/abs/2304.06972]
- `deep learning super-resolution coarse simulation field input predict fine-grid residual compared to bicubic interpolation baseline PDE`
  → "residual training" (predict `F - Upsample(F_LR)`) is standard SR practice
  (search-listed via https://arxiv.org/pdf/2311.14464; PDF fetch dead).

### Turn 2 — retrieval / analog residual transfer (the F6 rule's ancestors)
**Terms**: the scouting sweep found only an image-domain neighbour; §13.3 says
distrust a clean gap, so go at the two literatures nobody had searched — the
weather **analog method** and query-vs-retrieved-example residual learning.
- `analog ensemble method nearest neighbor past forecasts correction bias coarse model output statistics downscaling`
  → **AtmoSwing**: analog methods "search in the past for similar days to a
  target day in order to infer the predictand of interest", keyed on coarse
  fields, compared by the **Teweles-Wobus S1 gradient criterion** ("a
  comparison of the gradients ... instead of ... the actual values at the grid
  points"). [cite: https://gmd.copernicus.org/articles/12/2915/2019/]
- `retrieval-augmented neural operator PDE surrogate nearest neighbor retrieval from training set 2026`
  → retrieval is now a named category in operator benchmarking (cross-Reynolds
  study comparing "spectral, retrieval, and multi-scale methods",
  https://arxiv.org/pdf/2605.30112, search-listed).
- `learning residual between query solution and retrieved similar training example neural operator data-limited DeltaPhi`
  → **DeltaPhi** (NeurIPS 2025): retrieve the most similar training example by
  **input field similarity**; learn "the residual between the ground truth
  solution and the prediction from the auxiliary example"; predict "retrieved
  output + learned residual correction"; data-limited regime.
  [cite: https://arxiv.org/pdf/2406.09795] → `iteration_2.md`

### Turn 3 — hybrid parametric+nonparametric, and the "beat the lookup" discipline
- `hybrid neural network plus k-nearest-neighbor residual correction nonparametric memory augmented regression scientific`
  → **NNTNNR**: network "predict[s] differences between regression targets
  rather than the targets themselves", assembled over "the nearest neighbors of
  the unknown data point"; "outperform[s] both neural networks and k-nearest
  neighbor regression on small to medium-sized data sets".
  [cite: https://arxiv.org/abs/2310.00664]
- `simple nearest neighbor lookup baseline outperforms trained deep learning surrogate benchmark evaluation criticism`
  → the weak-baseline genre is well established in ML generally (Baseline
  Manifesto, tabular-NN revisited, SimpleShot) but **no PDE/operator instance**.
- `neural PDE surrogate benchmarks weak baselines linear model outperforms evaluation protocol critique operator learning`
  → **Optimal Linear Baselines for SciML**: "nonlinearity in the system does not
  guarantee that nonlinear neural network models outperform linear ones";
  "neural network-based methods can and should be evaluated against
  well-understood baselines". [cite: https://arxiv.org/html/2508.05831]
  → `iteration_3.md`

### Turn 4 — refutation part 1 (ENOUGH on field context declared here)
- `multifidelity DeepONet low-fidelity network output as input to high-fidelity network residual composite Howard Karniadakis`
  → **Multifidelity DeepONet**: "two standard DeepONets coupled by **residual
  learning and input augmentation**"; "significantly reduces the required
  amount of high-fidelity data". [cite: https://arxiv.org/abs/2204.06684]
- fetch of **MFFM**: "We pose the refinement as conditional residual flow
  matching, learning a velocity model on the residual delta = u_HF - u_LF
  **conditioned on u_LF**"; its nine-method baseline table contains
  **Bilinear (no-learning)**, **FNO-residual**, **DeepONet-residual**; the
  bilinear error is reported as "the relative L2 norm of the residual
  ||delta||/||u_HF||". [cite: https://arxiv.org/html/2605.16118]
- `multi-fidelity deep learning coarse grid solution correction phase field Allen-Cahn Cahn-Hilliard sharp interface surrogate`
  → only single-fidelity, physics-loss phase-field DL (NPF-Net,
  https://arxiv.org/abs/2410.08914). **No usable MF phase-field result.**
  → `iteration_4.md`

### Turn 5 — refutation part 2 + verdict (cap reached)
- `training-free nearest neighbor analog correction from coarse simulation to fine simulation multi-fidelity baseline no training`
  → **Hybrid-MF overview**: additive correction "fMF(x) = fLF(x) + Delta(x)",
  Delta "often from a neural network, RBFN, or GP", and the overview "does not
  discuss nonparametric/nearest-neighbor or retrieval-based approaches for the
  additive correction specifically".
  [cite: https://www.emergentmind.com/topics/hybrid-multi-fidelity-models]
- `combine neural operator prediction with retrieved nearest neighbor residual correction hybrid memory multi-fidelity PDE`
  → every hybrid found couples the operator to the **PDE residual or a solver**
  (ADR-0009-excluded). No retrieval component. Third independent framing, same
  answer.
- `constructed analog downscaling add residual of nearest analogs to coarse field bias correction method definition`
  → **LOCA / constructed analogs** (search-listed, not fetched): coarsen the
  fine observations, match the coarse field, "weighted average of these analog
  days"; LOCA adds multiscale region-then-local matching; MACA adds a bias
  correction afterwards. → `iteration_5.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched in this loop) | What remains open |
|---|---|---|---|
| **(i)** LF field (max fidelity, interpolated per `panel_data.copylf_prediction`) as an **input channel** to the FiLM-FNO backbone, predicting `hf - lf`, copy-LF added back at output; MF few/moderate-shot | **preempted (cite)** | LRC-FNO https://arxiv.org/html/2606.17733 ("upsampled coarse solution ... concatenated as the input of the Residual-Closure FNO"; "adding the coarse solution and the residual correction"); MFFM https://arxiv.org/html/2605.16118 (residual `u_HF-u_LF` "conditioned on u_LF"; **`FNO-residual` is one of its baselines**; bilinear no-learning baseline reported); Multifidelity DeepONet https://arxiv.org/abs/2204.06684 ("residual learning and input augmentation") | **Nothing at the mechanism level.** Only setting: (a) our LF is a real coarse *consistent* solve (immutable 1) rather than a coarse-network output or a downsample; (b) no retrieved MF/coarse-correction work runs on sharp-interface 2-D phase-field data; (c) the Class-A/Class-B partition (fidelity residual unlearnable on 2/5 datasets) is a data finding. **Propose it as the missing literature-standard control**, given batch-1 F14 (0/27 families read the test LF field), not as a new model. |
| **(ii)** The zero-parameter LF-keyed residual transfer (`copy-LF + mean_k[HF_j - LF_j]`, `j` retrieved by LF-field signature) reported as a **training-free floor** a trained model must clear | **preempted-but-MF-composition-open** | AtmoSwing analog method https://gmd.copernicus.org/articles/12/2915/2019/ (retrieval keyed on coarse fields; S1 gradient criterion; empirical conditional distribution from retrieved dates); DeltaPhi https://arxiv.org/pdf/2406.09795 (retrieve by input-field similarity, `retrieved output + learned residual`, data-limited); Hybrid-MF overview https://www.emergentmind.com/topics/hybrid-multi-fidelity-models (additive `fLF + Delta`, Delta parametric — "not ... nearest-neighbor or retrieval-based"); baseline discipline https://arxiv.org/html/2508.05831 ("can and should be evaluated against well-understood baselines"). Search-listed only: LOCA https://journals.ametsoc.org/view/journals/hydr/15/6/jhm-d-14-0082_1.xml | Open: transferring the **fidelity residual** (`HF-LF`) of retrieved neighbours onto the query's **own** coarse field, keyed on the LF solution field, used as a **floor in an MF operator benchmark**. Analog methods substitute/average the retrieved fine fields instead; the MF additive-correction corrector is parametric. Reportable **with the analog family cited as its ancestor** — not a novelty claim. |
| **(iii)** Hybrid: trained LF-input residual operator **+** a retrieved-residual term under a confidence/blend weight | **preempted-but-MF-composition-open** | NNTNNR https://arxiv.org/abs/2310.00664 (learned differences anchored on k-NN neighbours; beats both NN and k-NN on small/medium data); DeltaPhi https://arxiv.org/pdf/2406.09795; image-domain KRF https://www.sciencedirect.com/science/article/abs/pii/S0952197626000977 (search-listed) | Open: the **multi-fidelity binding** — correction = learned term + retrieved fidelity-residual term over a **real coarse solve**, parameterized so copy-LF is exactly recoverable (the scouting sweep's C1 guaranteed-fallback question, still unrefuted in three framings). Thin, but the only arguable *mechanism* claim of the three. |

## Citations summary

- LRC-FNO, "Latent Residual-Closure Fourier Neural Operator ... Particle-in-Cell
  Simulations" — https://arxiv.org/html/2606.17733 — FETCHED — iteration_1 term 1
- MF-FNO transfer learning, "Multi-fidelity prediction of fluid flow and
  temperature field ... using FNO" — https://arxiv.org/abs/2304.06972 —
  FETCHED (abstract) — iteration_1 term 2
- AtmoSwing (analog technique model, GMD 12:2915) —
  https://gmd.copernicus.org/articles/12/2915/2019/ — FETCHED — iteration_2 term 1
- DeltaPhi, "Physical States Residual Learning for Neural Operators in
  Data-Limited PDE Solving" (NeurIPS 2025;
  OpenReview https://openreview.net/forum?id=ppOCvEonKT) —
  https://arxiv.org/pdf/2406.09795 — FETCHED — iteration_2 term 3
- NNTNNR, "Twin Neural Network Improved k-Nearest Neighbor Regression" —
  https://arxiv.org/abs/2310.00664 — FETCHED (abstract; PDF fetch dead) —
  iteration_3 term 1
- "Optimal Linear Baseline Models for Scientific Machine Learning" —
  https://arxiv.org/html/2508.05831 — FETCHED — iteration_3 term 3
- Multifidelity DeepONet — https://arxiv.org/abs/2204.06684 — FETCHED
  (abstract; PDF fetch dead) — iteration_4 term 1
- MFFM, "Multi-Fidelity Flow Matching: Cascaded Refinement of PDE Solutions" —
  https://arxiv.org/html/2605.16118 — FETCHED — iteration_4
- "Hybrid Multi-Fidelity Models" overview —
  https://www.emergentmind.com/topics/hybrid-multi-fidelity-models — FETCHED —
  iteration_5 term 1
- NPF-Net, end-to-end DL for nonlocal Allen-Cahn / Cahn-Hilliard —
  https://arxiv.org/abs/2410.08914 — search-listed — iteration_4 term 2
- LOCA, "Statistical Downscaling Using Localized Constructed Analogs" —
  https://journals.ametsoc.org/view/journals/hydr/15/6/jhm-d-14-0082_1.xml —
  search-listed — iteration_5 term 3
- "Striding Across Reynolds Numbers" (retrieval as a benchmarked category) —
  https://arxiv.org/pdf/2605.30112 — search-listed — iteration_2 term 2
- FV features + residual training — https://arxiv.org/pdf/2311.14464 —
  search-listed (PDF fetch dead) — iteration_1 term 3
- KRF, "K-nearest neighbor-enhanced Residual Learning ... image restoration" —
  https://www.sciencedirect.com/science/article/abs/pii/S0952197626000977 —
  search-listed — iteration_3 term 1

## Dead ends

- `https://arxiv.org/pdf/2204.06684`, `https://arxiv.org/pdf/2311.14464`,
  `https://arxiv.org/pdf/2310.00664` and the initial
  `https://arxiv.org/pdf/2406.09795` attempt → undecoded PDF binary. Three were
  recovered via `/abs/` or `/html/`; **prefer `/abs/` and `/html/` in future
  loops**.
- Term `simple nearest neighbor lookup baseline outperforms trained deep
  learning surrogate ...` → returned general ML methodology (tabular, few-shot,
  captioning) with **no PDE/operator instance**; the PDE-specific version had to
  be reached through the linear-baseline paper.
- Term `multi-fidelity deep learning ... phase field Allen-Cahn Cahn-Hilliard
  sharp interface` → only single-fidelity physics-loss phase-field DL. The
  sharp-2D MF setting genuinely has no retrieved occupant.
- Term `combine neural operator prediction with retrieved nearest neighbor
  residual ...` → all hits are PDE-residual/solver hybrids (ADR 0009 excludes
  them at test time), not retrieval.

## For the brainstormer

The brainstormer **MUST quote the verdict row** for whichever direction it
proposes, verbatim, in the card's `prior_art` field.

1. **Direction (i) is `preempted (cite)`. Do not dress it as novel.** MFFM lists
   `FNO-residual` (an FNO conditioned on `u_LF` predicting `u_HF - u_LF`) as one
   of nine *baselines* [https://arxiv.org/html/2605.16118]; LRC-FNO concatenates
   the upsampled coarse field and adds the residual back
   [https://arxiv.org/html/2606.17733]; multifidelity DeepONet is
   "residual learning and input augmentation" [https://arxiv.org/abs/2204.06684].
   The defensible framing is: **the zoo is missing the literature-standard
   baseline** (batch-1 F14: 0/27 families read the test LF field at inference),
   and B2 supplies it. That is a genuine experiment under program.md §1 — it
   tests the mechanism claim of card part 6 — but its value is the *measurement*,
   not the architecture.
2. **Correct an overclaim inherited from batch 1.** Batch 1's prior-art cell said
   no MF paper baselines against the interpolated LF field. MFFM does: its
   **Bilinear** no-learning baseline error is "the relative L2 norm of the
   residual ||delta||/||u_HF||" — copy-LF under another name. The surviving gap
   is narrower: no fetched source *requires* the trained model to beat that
   baseline, and none reports a dataset class where it cannot (our Class B).
3. **If the card reports the F6 zero-parameter rule as a floor, cite its
   ancestors.** It is an analog-MOS construction: retrieval keyed on the coarse
   field is operational climate downscaling
   [https://gmd.copernicus.org/articles/12/2915/2019/, LOCA search-listed]. What
   is open is the *fidelity-residual transfer onto the query's own coarse field*
   and its use as a benchmark floor. Verdict (ii),
   `preempted-but-MF-composition-open`, must be quoted with that sentence.
4. **Two free design steals from the retrieval literature, both cheap enough for
   the ADR 0007 contract-tier screen**: (a) the analog family keys on
   **gradients** (Teweles-Wobus S1), not raw values — testable against our 16x16
   block-mean signature, which batch-1 F9 showed is resolution-converged but was
   never compared to a gradient key; (b) LOCA uses **region-then-local**
   matching — i.e. a per-patch retrieval key rather than one global signature.
5. **Direction (iii) is where the only arguable mechanism claim lives**, and it
   is thin: a correction that is the sum of a learned term and a retrieved
   fidelity-residual term, blended by a confidence weight, parameterized so
   copy-LF is exactly recoverable. Three independent framings found no MF
   operator with a nonparametric corrector — the hybrid-MF overview states the
   corrector is "often from a neural network, RBFN, or GP"
   [https://www.emergentmind.com/topics/hybrid-multi-fidelity-models]. If the
   card proposes this, it must also state the Class-B risk: on allen_cahn and
   fisher_kpp every training-free rung is a no-op (1.000 / 0.9988), so the blend
   weight must be able to go to zero.
6. **ADR 0009 kills the adjacent literature.** Every retrieved hybrid corrector
   in the operator space (Error-Conditioned Neural Solvers, solver-in-the-loop
   hybrids, NPF-Net) needs the PDE residual at test time. Do not cite them as
   support for a test-time mechanism; they are excluded, and the exclusion is
   itself the reason the retrieval route is interesting.
