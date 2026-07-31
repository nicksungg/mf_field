# Websearch Report — Stream `r2s1_direct`, Batch 1

**Stream**: `r2s1_direct` (class: gap)
**Batch**: 1
**Total iterations**: 4 (cap 5)
**WebSearch calls**: 10 (turn 1: 3, turn 2: 2, turn 3: 3, turn 4: 2)
**WebFetch calls**: 9 — 7 usable, 1 failed on content-length (arXiv:2604.09664 PDF; retried successfully on the /abs page), 1 returned no extractable text (arXiv:2512.01421 PDF, therefore NOT used as evidence)
**Cap hit**: no — stopped at 4 with `ENOUGH` recorded in iteration_4.md

## Search trace

### Turn 1 — map the three §12.1 decoder classes before proposing anything
Terms: FiLM-conditioned neural-operator decoder from a parameter vector;
DeepONet branch–trunk on a parameter vector at few samples; modulated-INR /
CORAL-class neural fields for parametric PDEs.
- FiLM parameter→field decoding is a documented standard pattern
  [cite: https://arxiv.org/html/2601.22654v1, https://arxiv.org/html/2511.09729v1].
- **RB-DeepONet** fixes the trunk to a greedy reduced-basis space; the branch
  emits only RB coefficients from parameter/source encodings
  [cite (fetched): https://arxiv.org/abs/2511.18260].
- Conditioning neural fields on simulation parameters is established
  (VCNeF, FA-INR, instance-pattern composers)
  [cite: https://arxiv.org/pdf/2406.03919, https://arxiv.org/html/2506.06858v3].
→ `iteration_1.md`

### Turn 2 — floor methodology, and what to do when parameters do not determine the field
Terms: trivial/NN/mean baselines in neural-surrogate benchmarks; phase-field
microstructure prediction from process parameters with stochastic ICs.
- REALM (the strongest 2025-26 surrogate benchmark hit) compares architectures
  against HF references and **not** against trivial baselines; its headline is a
  metric-vs-physics gap, not a floor argument
  [cite (fetched): https://arxiv.org/html/2512.18595].
- The stochastic-phase-field line builds noise into the model and validates on
  **ensemble statistics rather than pointwise metrics**
  [cite (fetched): https://arxiv.org/abs/2604.09664]; the phase-field surrogate
  literature always takes the initial microstructure as an *input*, or generates
  it with a conditional diffusion model
  [cite: https://www.nature.com/articles/s41524-020-00471-8].
→ `iteration_2.md`

### Turn 3 — targeted refutation of D1/D2/D3
Terms: POD-NN/POD-DeepONet coefficient regression; scalar-only FNO conditioning;
irreducible/aleatoric floor and the conditional-mean barrier.
- PODNO states PCA-Net/POD-NN "map coefficients with simple DNNs" and describes
  POD-DeepONet [cite (fetched): https://arxiv.org/html/2504.18513v1/].
- ModAFNO = AFNO + modulation for conditioning on parameters, shipped in NVIDIA
  PhysicsNeMo [cite: https://archive.docs.nvidia.com/physicsnemo/26.03/physicsnemo/api/models/fnos.html];
  the FNO practical review PDF did not text-extract, so nothing is quoted from it
  [attempted: https://arxiv.org/pdf/2512.01421].
- **Conditional-mean barrier** paper gives the aleatoric-floor diagnostic and
  prescribes reporting the floor beside model error, and does *not* address
  unidentified random inputs such as random ICs
  [cite (fetched): https://arxiv.org/html/2605.28076].
→ `iteration_3.md`

### Turn 4 — the remaining refutation, then verdict (final)
Terms: coarse solve as carrier of information the parameters lack; operator
learning at extreme data scarcity.
- **No usable result** for "LF carries the omitted driver"; nearest neighbor is
  train-on-coarse/score-on-fine generalization
  [cite (fetched): https://arxiv.org/pdf/2510.23111].
- The field's answer to scarcity is smarter acquisition, not floor certification
  [cite (fetched): https://arxiv.org/html/2603.02066]; that paper explicitly does
  not use low-fidelity data as a training signal.
→ `iteration_4.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **D1** FiLM/modulation-conditioned spectral (FNO) decoder: condition → latent → HF field, no field input | **preempted** | https://arxiv.org/html/2601.22654v1; https://arxiv.org/html/2511.09729v1; ModAFNO https://archive.docs.nvidia.com/physicsnemo/26.03/physicsnemo/api/models/fnos.html | Nothing mechanism-level. Admissible only as a *measurement/baseline arm* on this panel against the mandatory floor arms. |
| **D2** Condition → coefficients of a fixed/learned output basis (POD/RB trunk), as the low-variance shape at N_hf=5 | **preempted** | PODNO https://arxiv.org/html/2504.18513v1/ (fetched); RB-DeepONet https://arxiv.org/abs/2511.18260 (fetched) | Only the number is unmeasured (fixed basis vs free decoder at N_hf=5). Declare as a baseline arm; it is POD-NN/PCA-Net prior art under a new name. |
| **D3** Per-dataset identifiability certification: estimate the conditional-mean/aleatoric floor for condition→HF, and validate it by showing the missing driver lives in the withheld LF field | **preempted-but-MF-composition-open** | Conditional-mean barrier arXiv:2605.28076v3 https://arxiv.org/html/2605.28076 (fetched); REALM https://arxiv.org/html/2512.18595 (fetched, shows floors are not standard practice) | Open: (i) the barrier diagnostic has never been instantiated where the unobserved driver is a *stored coarse solve*, making the floor validatable rather than assumed; (ii) NN-in-condition / train-mean / zero as a standing certification panel is not done in the fetched benchmark literature. |

## Citations summary

- [Duruisseaux et al. 2026] "Fourier Neural Operators Explained: A Practical Perspective" — https://arxiv.org/pdf/2512.01421 — iteration_3.md (**fetch failed to extract text; not used as evidence**)
- [anon 2026] "Parameter conditioned interpretable U-Net surrogate model …" — https://arxiv.org/html/2601.22654v1 — iteration_1.md (search return)
- [anon 2025] "Generalizing PDE Emulation with Equation-Aware Neural Operators" — https://arxiv.org/html/2511.09729v1 — iteration_1.md (search return)
- [NVIDIA 2026] PhysicsNeMo FNO model docs (ModAFNO) — https://archive.docs.nvidia.com/physicsnemo/26.03/physicsnemo/api/models/fnos.html — iteration_3.md (search return)
- [RB-DeepONet 2025] "Reduced-Basis Deep Operator Learning for Parametric PDEs with Independently Varying Boundary and Source Data", arXiv:2511.18260 (2025-11-23) — https://arxiv.org/abs/2511.18260 — iteration_1.md (**fetched**)
- [PODNO 2025] "PODNO: Proper Orthogonal Decomposition Neural Operators", arXiv:2504.18513v1 (2025-04) — https://arxiv.org/html/2504.18513v1/ — iteration_3.md (**fetched**)
- [REALM 2025] "Benchmarking neural surrogates on realistic spatiotemporal multiphysics flows", arXiv:2512.18595v2 — https://arxiv.org/html/2512.18595 — iteration_2.md (**fetched**)
- [anon 2026] "Learning noisy phase transition dynamics from stochastic PDEs", arXiv:2604.09664 (2026-03-31) — https://arxiv.org/abs/2604.09664 — iteration_2.md (**fetched**)
- [anon 2026] "Diagnosing the Conditional-Mean Barrier in Scientific Machine-Learning Surrogates", arXiv:2605.28076v3 (2026-07-06) — https://arxiv.org/html/2605.28076 — iteration_3.md (**fetched**)
- [anon 2026] "Neural Emulator Superiority: When ML for PDEs Surpasses its Training Data", arXiv:2510.23111v2 — https://arxiv.org/pdf/2510.23111 — iteration_4.md (**fetched**)
- [RLMesh 2026] "Accelerating PDE Surrogates via RL-Guided Mesh Optimization", arXiv:2603.02066v1 (2026-03-02) — https://arxiv.org/html/2603.02066 — iteration_4.md (**fetched**)
- [VCNeF] "Vectorized Conditional Neural Fields …" — https://arxiv.org/pdf/2406.03919 — iteration_1.md (search return)
- [FA-INR 2025] "Adaptive INRs for Interpretable Exploration of Simulation Ensembles" — https://arxiv.org/html/2506.06858v3 — iteration_1.md (search return)
- [npj 2020] "Accelerating phase-field-based microstructure evolution predictions via surrogate models …" — https://www.nature.com/articles/s41524-020-00471-8 — iteration_2.md (search return)
- In-repo (prior websearch by another agent, cited not re-derived):
  `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` §4.2 [LF-11] MF-DeepONet
  https://arxiv.org/abs/2503.17941; `docs/reports/MF_Sharp_HighFreq_Report.md`
  line 180 Lanthaler et al. https://arxiv.org/abs/2210.01074 (linear-reconstruction
  operators — DeepONet, PCA-Net — provably inefficient for **discontinuous**
  solution operators).

**Provenance note (audit)**: every URL in the Prior-art verdict table appears in
an `iteration_*.md` file of THIS loop. The two URLs that do not
(https://arxiv.org/abs/2503.17941, https://arxiv.org/abs/2210.01074) are carried
from the in-repo prior-websearch reports per §3.1 — verified present at
`docs/reports/MF_Leaderboard_Beaters_2026_Report.md:227,417` and
`docs/reports/MF_Sharp_HighFreq_Report.md:180,404` — and are used only as
context, never as a novelty verdict.

## Dead ends

- `coarse solve carries initial condition information … condition-only surrogate fails` → no usable results; the MF literature motivates residual learning by variance reduction, never by identifiability. (This is what leaves D3's composition open.)
- `operator learning few training samples 5 samples extreme data scarcity` → returns *acquisition* methods (RLMesh, adaptive sampling, data-generation schemes) that are inadmissible here: program.md §5.11 forbids new HF data.
- `FiLM conditioning FNO … no input function` → returned tooling/docs rather than a paper stating the contribution; the one review PDF failed text extraction. Treated as "standard practice", which is enough to refute novelty but not enough to cite a paper.

## For the brainstormer

1. **Quote the verdict.** Any FiLM-FNO-decoder or branch–trunk proposal is
   `preempted` (D1/D2 above) — it may be proposed only as an explicitly declared
   *baseline/measurement arm*, never as the card's contribution. The reviewer's
   rebadge check (program.md §5.10) will look for exactly this.
2. **The only open composition found is D3**
   (`preempted-but-MF-composition-open`, arXiv:2605.28076): instantiate the
   conditional-mean-barrier diagnostic on this panel, where the omitted driver is
   not abstract noise but the *stored LF coarse solve*, so the floor can be
   validated rather than assumed. That is a genuine-either-way experiment in the
   program.md §1 sense.
3. **Read `summary_so_far.md` §"Load-bearing fact" before designing.** Measured
   on the train split: `sharp__phase_field_crystal_2d`'s two closest-in-condition
   samples (standardized distance 0.0124) differ by rel-field 1.149, and their LF
   fields differ by 1.148 — the random IC is in the LF field, not in the
   condition vector (pfc/fisher_kpp/allen_cahn `param_names` carry no IC; only
   `sharp__cahn_hilliard` does, via 16 `ic_c*` dims). On those datasets a
   deterministic condition→HF model is estimating a conditional mean, which is
   why `train_mean` beats `nn_condition` in `state/anchors/floors.json` for
   exactly pfc and fisher_kpp. Do not propose a card whose falsification clause
   assumes skill→1 is reachable there.
4. **Do not propose ensemble-statistic / distributional metrics as the primary
   score** — arXiv:2604.09664 validates on ensemble statistics, but program.md
   §2.1 fixes one nRMSE definition and the eval layer is byte-frozen (§5). A
   distributional claim must be a *secondary* reported quantity.
5. **Floor arms are a contribution, not overhead.** REALM (arXiv:2512.18595) does
   not compare against trivial baselines at all; the mandatory NN/mean/zero panel
   (program.md §2.2) has no precedent found in this loop. Report it prominently.
6. **Two constraints to respect while proposing**: scarcity fixes from the
   literature are *acquisition* methods (RLMesh arXiv:2603.02066) and are barred
   by §5.11 (no new HF data); and Lanthaler et al. (arXiv:2210.01074, via the
   in-repo sharp report) proves linear-reconstruction architectures — DeepONet,
   PCA-Net, and therefore any fixed-POD-basis D2 arm — are provably inefficient
   for *discontinuous* operators, which is what 4 of the 6 panel datasets are.
   If D2 is run as a baseline, predict its failure mode in advance.
