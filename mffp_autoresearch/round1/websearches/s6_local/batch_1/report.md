# Websearch Report — Stream `s6_local`, Batch 1

**Stream**: `s6_local` (lever; ADR 0011) — does adding a local representation
(CNN/ConvNeXt branch, local kernels) to the FNO fix sharp-2D MF fusion (H2)?
**Batch**: 1 (first pipeline agent on a new stream)
**Total iterations**: 5 (cap reached)
**WebSearch calls**: 15 (3+3+3+2+4 — turn 5 used 4 terms, one over the
3-terms/turn cap, recorded in `iteration_5.md`; turn 4 used 2)
**WebFetch calls**: 16 (10 successful, 6 failed: three arXiv PDFs returned raw
binary, one OpenReview PDF hit a browser check, one arXiv HTML 404, one
ScienceDirect 403 — all listed under Dead ends)
**Cap hit**: YES — 5/5 iterations; term cap exceeded once in the final turn.

## Search trace

### Turn 1 — how thoroughly is "FNO + local branch" published? (`iteration_1.md`)
Terms: NO-LIDK localized kernels / U-FNO / CNO alias-free. Chosen because
`MF_FNO_CNN_Hybrid_Report.md` §6.6 flags NO-LIDK as "plausibly tighter prior
art — not fetched" and `MF_Sharp_HighFreq_Report.md` §1.2 calls the local path
"the single most consistently validated fix".
- NO-LIDK (ICML 2024): local differential + local-integral layers are
  **"parallel additions to FNO architectures"**; FNO's global ops are "prone
  to over-smoothing"; **−34–72% rel-L2** [cite: https://arxiv.org/abs/2402.16845 ,
  https://proceedings.mlr.press/v235/liu-schiaffini24a.html] → `iteration_1.md`
- U-FNO: U-Net path inside the Fourier block, motivated by **sharp saturation
  fronts**; "only a third of the training data" vs CNN
  [cite: https://arxiv.org/abs/2109.03697] → `iteration_1.md`
- LOGLO-FNO (TMLR 2025): same motif again — **parallel** local-convolution
  branch + global Fourier branch, plus high-frequency loss terms, tested on
  "problems with sharp discontinuities"; no few-shot or MF claims
  [cite: https://arxiv.org/pdf/2504.04260] → `iteration_1.md`
- CNO: alias-free operator; but on **Discontinuous Transport OOD a plain U-Net
  (1.35%) beats CNO (1.61%)**
  [cite: https://papers.nips.cc/paper_files/paper/2023/file/f3c1951b34f7f55ffaecada7fde6bd5a-Paper-Conference.pdf]
  → `iteration_1.md`

### Turn 2 — why locality helps or fails on sharp fields (`iteration_2.md`)
- SpecB-FNO: FNO's failure above truncation is **parameterization bias**, not
  budget — *"the prediction residual does not decrease as the Fourier kernel
  size increases"*; remedy is residual staging, ~50% mean error reduction.
  **This independently predicts s5-B1's negative H1 result**
  [cite: https://arxiv.org/html/2404.07200v2] → `iteration_2.md`
- The Well: `euler_multi_quadrants` one-step FNO 0.4081 vs CNextU-Net **0.1531**
  — but rollout 13:30 FNO 1.37 vs CNextU-Net **>10**; `acoustic_scattering_maze`
  one-step FNO 0.5062 vs CNextU-Net **0.0153**
  [cite: https://polymathic-ai.org/the_well/benchmarks/ ,
  https://arxiv.org/pdf/2412.00568] → `iteration_2.md`.
  **Corrects the in-repo report**, which quotes only the one-step column.
  MFFP is single-shot, so the local advantage applies; the rollout blow-up does
  not.
- Receptive-field limit: conv stacks cannot handle "large spatial
  displacements"; the field's fix is explicit alignment/deformable offsets
  [cite: https://openaccess.thecvf.com/content/WACV2023/papers/Fuoli_Fast_Online_Video_Super-Resolution_With_Deformable_Attention_Pyramid_WACV_2023_paper.pdf]
  → `iteration_2.md`. **Scope boundary: local = blur fix, warp (s3) = displacement fix.**

### Turn 3 — composition: parallel vs sequential vs routed (`iteration_3.md`)
- SINO (Starter-Iterator): spectral starter → **CNN iterator**, unrolled and
  **weight-shared**, trained **end-to-end with one relative-L2 loss**;
  "high-fidelity" = accuracy, **not** multi-fidelity; no few-sample runs; no
  FiLM [cite: https://arxiv.org/html/2606.18305] → `iteration_3.md`
- U-HNO: *"at every spatial location, a per-pixel hard mask selects whether the
  global Fourier branch or the local multi-scale Gaussian branch should
  dominate"*, shock-aligned regions get different mixtures; H1 + spectral
  consistency losses; **not MF, no no-harm guarantee**
  [cite: https://arxiv.org/abs/2605.12965] → `iteration_3.md`
- Exposure bias at a stage boundary is a **named, documented** failure ("training
  relies on ground-truth low-frequency conditions but inference uses
  model-generated ones"), mitigated by a coarse-to-fine curriculum
  [cite: https://arxiv.org/pdf/2606.02661] → `iteration_3.md`

### Turn 4 — the tiny-N_hf regime and MF instances (`iteration_4.md`)
- MF-FNO for carbon storage: LF-pretrain → HF-finetune, "81% less data
  generation costs", accurate "even when the high-fidelity data are extremely
  limited"; abstract shows **no local branch**; N_hf ≈ 100
  [cite: https://arxiv.org/abs/2308.09113] → `iteration_4.md`
- Spectral-Inspired NO (a *different* "SINO"): **no local convolutions**, and
  *"with only 5 training trajectories ... outperforms data-driven methods
  trained on 200 trajectories"*; baselines overfit badly there
  [cite: https://arxiv.org/html/2505.21573v3] → `iteration_4.md`.
  **The strongest fetched argument against a free-form local branch at N_hf=5.**

### Turn 5 — adversarial refutation of the three candidate directions (`iteration_5.md`)
- F-Adapter: PEFT on FNO Fourier layers with per-band bottlenecks; **low bands
  get MORE capacity**, high bands "sparse and susceptible to numerical noise";
  scarcity down to 24 trajectories; **single fidelity**
  [cite: https://arxiv.org/html/2509.23173v1] → `iteration_5.md`
- Learned coarse-grid correction `u = u* + LC(u*)` is standard
  [cite: https://arxiv.org/pdf/2102.01010] but no fetched source gives a
  **no-harm guarantee vs the interpolated coarse solve** → `iteration_5.md`
- Fidelity-split subnetworks are published for DeepONet (LF subnet + HF
  correction subnet) [cite: https://arxiv.org/abs/2204.09157]; **no source
  aligns the spectral/local split with the LF/HF split** → `iteration_5.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **D1** — parallel local path (U-FNO U-Net path / NO-LIDK differential + local-integral kernels) inside the champion `mf_fno_transfer_film`, keeping its LF-pretrain → HF-finetune schedule | **preempted** (mechanism) | https://arxiv.org/abs/2402.16845 + https://proceedings.mlr.press/v235/liu-schiaffini24a.html (parallel local layers in FNO, −34–72%); https://arxiv.org/abs/2109.03697 (U-FNO dual path, sharp fronts); https://arxiv.org/abs/2308.09113 (MF LF-pretrain/HF-finetune); https://arxiv.org/pdf/2504.04260 (LOGLO-FNO, parallel local branch + high-frequency loss, sharp-discontinuity problems) | Only the conjunction, and it is one step from overlapping author groups. **Propose D1 only as a MEASUREMENT of H2 (the s5-B1 framing), claiming no mechanism novelty.** Untested cell: sharp-2D MF fusion at N_hf = 5 against copy-LF. |
| **D2** — fidelity-asymmetric capacity: LF trains the spectral backbone; the ONLY HF-trained module is a small, capacity-constrained, zero-init **local** adapter | **preempted-but-MF-composition-open** | https://arxiv.org/html/2509.23173v1 (F-Adapter: PEFT on FNO, per-band widths, N=24, single fidelity); https://arxiv.org/abs/2204.09157 (MF DeepONet: LF subnet + HF correction subnet, no locality); https://arxiv.org/html/2505.21573v3 (5-trajectory spectral model beats data-driven at 200) | **Aligning the spectral/local inductive-bias split with the LF/HF data split** appears in no fetched source. It also carries a *published opposing prediction* (F-Adapter says capacity belongs in LOW bands) — a genuine pre-registered falsification risk, which is what makes it a real experiment. |
| **D3** — local corrector consuming the **real interpolated LF field at test time**, with an identity-to-copy-LF construction (zero-init gate ⇒ at init the model IS copy-LF) | **preempted-but-MF-composition-open** | https://arxiv.org/pdf/2102.01010 and https://www.sciencedirect.com/science/article/abs/pii/S0045793023001962 (learned coarse-grid correction); https://arxiv.org/abs/2605.12965 (U-HNO per-pixel spectral/local routing, shock-aware, **no** no-harm guarantee); https://arxiv.org/pdf/1901.09321 (Fixup identity-at-init; fetched by s2-B1) | A no-harm floor **defined by a real coarse PDE solve** (= round success criterion 2, skill < 1), plus the champion's blind spot that it never sees LF at inference. **Stream-boundary flag: `s2_beyond_copy`-B1 D2 already owns "identity-to-LF"; s6 owns only "the corrector is LOCAL".** |
| (anti-direction) pure local backbone replacement | **rejected on in-repo evidence** | `mf_field/akash/results/bench_full_metrics.csv`: `convnext_unet_film` 3.599 vs champion 1.526 on `ext__helmholtz_2d` | Nothing — ADR 0011 already settles it. |

## Diagnosis of the mentor's FNO→CNN attempt

**It was never run.** `program.md` §13.2: the FNO→CNN two-stage hybrid "was
never built". What "went poorly" is the **prior-art outcome** of
`docs/reports/MF_FNO_CNN_Hybrid_Report.md` §6.0: *"Every individual component
of this design is published prior art, and one paper combines three of the
four"* — the project's 0-for-4 novelty record (§13.3) claiming its fifth
victim. Three design-level failure modes were identified there and this loop
confirms or refines each:

1. **Prior-art collapse (the actual failure).** Confirmed and *strengthened*:
   NO-LIDK (ICML 2024, peer-reviewed, the "not fetched — likely tighter prior
   art" item in §6.6) is now fetched and is indeed the tightest match for
   "parallel local kernels in an FNO"; SINO re-fetched and confirmed as
   sequential spectral→CNN, end-to-end, single-fidelity.
2. **Exposure bias at the stage boundary (§5.1).** Confirmed as a *documented*
   phenomenon [cite: https://arxiv.org/pdf/2606.02661] — but **this benchmark
   dodges it for free**: the LF field is a real dataset input available at test
   time, so a stage-2 refiner can be trained and evaluated on the *same* true
   LF field. The mentor's design created the risk by making stage 1 *predict*
   LF; consuming the given LF instead removes it. This is the single most
   important correction to the recipe.
3. **Overfitting at N_hf = 5 (§5.3).** Now supported by two independent fetched
   sources: a purely spectral, low-parameter model beats data-driven baselines
   trained on 40× more data at N=5 [https://arxiv.org/html/2505.21573v3], and
   F-Adapter's scarcity study puts adapter capacity in LOW bands, not high
   [https://arxiv.org/html/2509.23173v1]. **A free-form ConvNeXt refiner
   fine-tuned on 5 HF samples is the known-bad recipe; capacity-constrained,
   zero-init, identity-safe locality is the surviving form.**
4. **The dipole/displacement failure (§5.2).** Out of scope for a local
   operator by receptive-field argument
   [https://openaccess.thecvf.com/content/WACV2023/papers/Fuoli_Fast_Online_Video_Super-Resolution_With_Deformable_Attention_Pyramid_WACV_2023_paper.pdf]
   — it belongs to `s3_warp`. s6 should scope its claim to **blur/sharpness**
   error and say so.

## Citations summary

- [Liu-Schiaffini et al. 2024] "Neural Operators with Localized Integral and Differential Kernels", ICML — https://arxiv.org/abs/2402.16845 , https://proceedings.mlr.press/v235/liu-schiaffini24a.html — used in: iteration_1 (fetched), iteration_5 (D1)
- [Wen et al. 2022] "U-FNO", *Advances in Water Resources* — https://arxiv.org/abs/2109.03697 — used in: iteration_1 (search), iteration_5 (D1)
- [LOGLO-FNO 2025] "Efficient Learning of Local and Global Features in Fourier Neural Operators", TMLR — https://arxiv.org/pdf/2504.04260 — used in: iteration_1 (fetched)
- [Raonić et al. 2023] "Convolutional Neural Operators", NeurIPS — https://papers.nips.cc/paper_files/paper/2023/file/f3c1951b34f7f55ffaecada7fde6bd5a-Paper-Conference.pdf — used in: iteration_1 (search)
- [Qin et al. 2024] SpecB-FNO / "Toward a Better Understanding of FNOs from a Spectral Perspective" — https://arxiv.org/html/2404.07200v2 — used in: iteration_2 (fetched)
- [Ohana et al. 2024] "The Well", NeurIPS D&B — https://polymathic-ai.org/the_well/benchmarks/ , https://arxiv.org/pdf/2412.00568 — used in: iteration_2 (benchmark table fetched)
- [Fuoli et al. 2023] "Fast Online Video SR with Deformable Attention Pyramid", WACV — https://openaccess.thecvf.com/content/WACV2023/papers/Fuoli_Fast_Online_Video_Super-Resolution_With_Deformable_Attention_Pyramid_WACV_2023_paper.pdf — used in: iteration_2 (search)
- [Qin et al. 2026] SINO "Starter-Iterator Neural Operator" — https://arxiv.org/html/2606.18305 — used in: iteration_3 (fetched)
- [U-HNO 2026] "U-shaped Hybrid Neural Operator with Sparse-Point Adaptive Routing" — https://arxiv.org/abs/2605.12965 — used in: iteration_3 (fetched), iteration_5 (D3)
- ["Learning to Refine" 2026] spectral-decoupled iterative refinement, precipitation nowcasting — https://arxiv.org/pdf/2606.02661 — used in: iteration_3 (search; exposure bias)
- [Tang et al. 2024] "Multi-fidelity Fourier Neural Operator ... Geological Carbon Storage", *J. Hydrology* — https://arxiv.org/abs/2308.09113 — used in: iteration_4 (abstract fetched), iteration_5 (D1)
- [Spectral-Inspired NO 2025] "Spectral-Inspired Neural Operator Learning with Limited Data and Unknown Physics" — https://arxiv.org/html/2505.21573v3 — used in: iteration_4 (fetched), iteration_5 (D2)
- [F-Adapter 2025] "Frequency-Adaptive Parameter-Efficient Fine-Tuning in Scientific ML" — https://arxiv.org/html/2509.23173v1 — used in: iteration_5 (fetched)
- [Kochkov et al. 2021] "Machine learning accelerated CFD" — https://arxiv.org/pdf/2102.01010 — used in: iteration_5 (search)
- ["Data-driven correction of coarse grid CFD simulations"] — https://www.sciencedirect.com/science/article/abs/pii/S0045793023001962 — used in: iteration_5 (search)
- [Multifidelity DeepONets 2022] — https://arxiv.org/abs/2204.09157 — used in: iteration_5 (search)
- [Zhang et al. 2019] Fixup initialization — https://arxiv.org/pdf/1901.09321 — fetched by `websearches/s2_beyond_copy/batch_1/`, cited here as an in-round sibling report, NOT re-fetched.

## Dead ends

- arXiv PDF fetches (`/pdf/2402.16845`, `/pdf/2308.09113`, `/pdf/2605.12965`) → returned raw/compressed binary; use `/abs/` or `/html/` instead.
- OpenReview PDF (NO-LIDK) → browser-verification wall; PMLR landing page worked.
- ScienceDirect (`S0022169424000350`, MF-FNO journal version) → HTTP 403; arXiv abstract substituted.
- `https://arxiv.org/html/2402.16845v3` → 404 (no HTML rendering for that paper).
- "receptive field limitation ... neural operator" framed searches → returned only video-SR/image-SR literature; no operator-learning source states the displacement limit directly. Recorded as a gap, not as a finding.

## For the brainstormer

The brainstormer MUST quote the verdict row above for whatever it proposes.

1. **Do not claim the mechanism.** "Local branch in parallel with a Fourier
   layer" is peer-reviewed prior art (NO-LIDK ICML 2024, −34–72%; U-FNO AWR
   2022). Any s6 card proposing D1 must be written as a **measurement of H2**,
   exactly as s5-B1 was written as a measurement of H1 — with the same
   "no novelty claimed" sentence in its motivation.
2. **The claim surface that survives is fidelity-alignment (D2) and the
   no-harm floor (D3).** No fetched source aligns the spectral/local split with
   the LF/HF data split, and none guarantees a corrector cannot underperform
   the interpolated coarse solve.
3. **The known-bad recipe is specific: a free-form ConvNeXt/CNN refiner
   fine-tuned on the 5 HF samples.** Two fetched sources predict it overfits
   (5-trajectory spectral model beating 200-trajectory data-driven baselines;
   F-Adapter putting scarce fine-tuning capacity in LOW bands). Constrain the
   local module: few channels, zero-init output, gated, and preferably the
   *only* HF-trained parameters.
4. **Consume the given LF field — do not predict it.** That deletes the
   documented exposure-bias failure of the mentor's two-stage design at zero
   cost, and it attacks the champion's known blind spot (§0.4 of
   `MF_Sharp_HighFreq_Report.md`: the winners never look at LF at inference).
5. **Scope the claim to sharpness, not displacement.** By the receptive-field
   argument a local branch cannot move a misplaced interface; that is
   `s3_warp`'s question. Say so in the falsification clause, and prefer a
   dataset-stratified prediction (largest effect where LF blurs, none where LF
   displaces).
6. **Watch the thresholds.** Anchor = champion panel geomean **6.703**
   [6.219, 7.102]; `min_claimable_effect` per dataset from
   `state/noise_floor.json` (helmholtz **9.695** — no numeric claim there;
   fisher_kpp 0.418 and cahn_hilliard 0.553 are the sensitive ones). ADR 0007
   applies: propose 3–5 compositions and screen at contract tier before
   committing SLURM.
7. **Coordinate with `s2_beyond_copy`** before proposing D3 — its B1 report
   already lists "identity-to-LF fusion" as its own batch-2 candidate.
