# iteration_2 — WHY local branches help or fail on sharp interfaces (retrieval-grounded)

## Search rationale

Open question 2. `MF_Sharp_HighFreq_Report.md` §0.1 and
`MF_FNO_CNN_Hybrid_Report.md` §3.1 both argue the mechanism (k^-1 decay /
spectral wall / Gibbs) but the *evidence* for "local beats spectral on sharp
data" in-repo is one line of The Well numbers. Since s5-B1 just falsified the
naive spectral-capacity story (H1: +0.507 < 0.884 floor), the local story must
be checked as hard as H1 was — including the case AGAINST it (when do local
branches fail?). Term 3 is deliberately adversarial: the mentor's report §5.2
says LF *misplaces* features, and a purely local operator has a bounded
receptive field, so there is a displacement scale beyond which a conv branch
provably cannot help.

## Search terms used

1. `why convolutional networks outperform Fourier neural operator on discontinuous shock fields Gibbs oscillations spectral truncation evidence benchmark`
2. `The Well benchmark 2024 euler multi quadrants FNO versus ConvNeXt U-Net VRMSE results`
3. `receptive field limitation convolutional refinement cannot correct large displacement misaligned features warping needed super-resolution`

## Findings per term

### Term 1 — the mechanism, from sources

- **SpecB-FNO, "Toward a Better Understanding of Fourier Neural Operators from
  a Spectral Perspective"** — https://arxiv.org/html/2404.07200v2 — FETCHED.
  Key measured claims: FNO behaves *qualitatively differently* below vs above
  its truncation frequency k (above it, frequencies are "learned by the linear
  and MLP components", error patterns resembling DeepONet); the failure is
  **Fourier parameterization bias**, not just budget — *"the prediction
  residual does not decrease as the Fourier kernel size increases"*, with
  error rising near higher frequencies **inside** the truncation window.
  Remedy: **iterative residual staging** (a second FNO fits the first's
  residual, whose energy is spread more evenly across frequencies) — average
  **50%** error reduction (range 8.3–92.5%). It also states FNO has a
  *stronger* bias toward dominant frequencies than spatial convolutions.
  **This is a directly-fetched source that independently predicts s5-B1's
  negative result**: raising the mode cap alone should not have paid off.
- Search-result-level (not fetched): Walsh-Hadamard NO for discontinuous
  coefficients https://arxiv.org/html/2511.07347 ; Shearlet NO for
  shock-dominated PDEs https://arxiv.org/html/2604.25181v1 ; "Fourier Residual
  Networks Achieve Spectral Accuracy for Discontinuous Functions"
  https://arxiv.org/pdf/2605.03549 . Common stated reason for failure: Fourier
  modes are *globally supported and isotropic*, so a localized jump needs
  infinitely many of them (Gibbs ringing that does not vanish with
  resolution), and truncation localizes the error **at** the discontinuity.

### Term 2 — The Well: the numbers, and a correction to the in-repo report

- **The Well (Ohana et al., NeurIPS 2024 D&B)** — benchmark table FETCHED at
  https://polymathic-ai.org/the_well/benchmarks/ (paper
  https://arxiv.org/pdf/2412.00568). `euler_multi_quadrants_periodicBC` VRMSE:

  | model | one-step | rollout 6:12 | rollout 13:30 |
  |---|---|---|---|
  | FNO | 0.4081 | 1.13 | 1.37 |
  | TFNO | 0.4163 | 1.23 | 1.52 |
  | U-Net | 0.1834 | 1.02 | 1.63 |
  | **CNextU-Net** | **0.1531** | **4.98** | **>10** |

  `acoustic_scattering_maze` (also discontinuous): one-step FNO 0.5062 vs
  **CNextU-Net 0.0153 — 33x better**; rollout 6:12 FNO 1.06 vs CNextU-Net 0.78.
- **Correction that matters for this stream**: the in-repo
  `MF_Sharp_HighFreq_Report.md` §1.1 quotes only the one-step column
  ("FNO 0.408 ... ConvNeXt-U-Net 0.153") and reads it as "spectral models
  ~2.7x worse than convolutional ones". The fetched table shows that ordering
  **inverts under autoregressive rollout** (CNextU-Net 4.98 / >10). MFFP is a
  **single-shot** field prediction (X, LF) -> HF with no rollout, so the
  one-step column is the applicable one and the local advantage stands — but
  the stream must not cite The Well as unconditional evidence for locality.

### Term 3 — the receptive-field limit (the case against a local branch)

- No neural-operator-specific source found; the applicable evidence is the
  video-SR/alignment literature. **Fuoli et al., "Fast Online Video
  Super-Resolution with Deformable Attention Pyramid", WACV 2023** —
  https://openaccess.thecvf.com/content/WACV2023/papers/Fuoli_Fast_Online_Video_Super-Resolution_With_Deformable_Attention_Pyramid_WACV_2023_paper.pdf
  (search-summary grade): shallow conv stacks have small receptive fields due
  to locality bias, which "limits the ability to handle large spatial
  displacements"; the field's answer is explicit alignment — deformable
  convolutions / learned offsets / pyramids — not more conv depth.
- Interpretation for MFFP: a 3x3-kernel local branch of depth d can only move
  content by ~d pixels. If the LF solve **misplaces** an interface by more
  than that, the local branch inherits exactly the §5.2 dipole problem, and
  the fix is the *warp* mechanism owned by `s3_warp`, not this stream. A local
  branch is the right tool for **blur/sharpness** error, the wrong tool for
  **displacement** error. This is a testable split and it is the honest scope
  boundary between s6 and s3.

## Interpretation

Locality is a *representation* fix for the sharpening half of the error and is
irrelevant-to-harmful for the displacement half; a fetched source (SpecB-FNO)
independently predicts s5-B1's negative H1 result, which strengthens H2 as the
next hypothesis rather than weakening it. The Well's one-step vs rollout
inversion is the single most important nuance: it makes the local branch a
good bet for MFFP's single-shot setting specifically.
