# Iteration 3 — attention vs convolution for defect correction; the Transolver premise itself

## Search rationale

The orchestrator's item (d): given s6 owns the local/closed-form filter class,
the only question s4 uniquely owns is whether **attention (nonlocal,
content-adaptive) beats a local filter for the fidelity-gap residual**. Two
things must be established adversarially: (1) is there a published head-to-head
on regular grids, and (2) is the Transolver premise itself sound -- iteration 2
found an AAAI paper claiming Physics-Attention is just linear attention and that
slice attention "may even hurt", which B1's report had listed as UNCITABLE. If a
text mirror exists, that claim becomes citable and it changes the framing of the
whole stream. Term 3 probes the physics side of B1's one pro-attention datapoint
(fisher_kpp's band-1 nonlinearity).

## Search terms used

1. `attention versus convolution head-to-head comparison residual correction regular grid PDE surrogate local kernel outperforms transformer`
2. `"Transolver is a linear transformer" physics attention revisiting arxiv`
3. `nonlocal attention necessary nonlinear reaction diffusion front sharp interface local convolution insufficient correction operator`

## Findings

### Term 1 — the head-to-head that exists favours attention ONLY on irregular geometry
- **"When Attention Beats Fourier: Multi-Scale Transformers for PDE Solving on
  Irregular Domains"**, https://arxiv.org/abs/2605.08318 — **FETCHED** (the
  `/html/` URL 404s; `/abs/` worked). Compares transformer attention against
  *"FNO, DeepONet, GNOT, and Mamba-NO"* on *"Five benchmark problems from the
  PINNacle suite"*. Headline per the fetch: *"attention-based transformers
  outperform Fourier methods on problems with complex, irregular geometries"*,
  with *"a 3.7x improvement over FNO on Heat2D-CG"*. The fetch's explicit
  scope note: the paper *"explicitly focuses on 'irregular domains' as stated in
  its title"*. **This is the strongest published pro-attention result I found,
  and its winning condition is geometry, not sharpness — the MFFP panel is on
  REGULAR grids, so it does not transfer.** Recorded as a *negative* for the
  attention premise on our panel.
- **"Generalizing PDE Emulation with Equation-Aware Neural Operators"**,
  https://arxiv.org/html/2511.09729v1 — **FETCHED.** Verbatim: *"The Learned
  Correction (LC) model consistently achieves the lowest error ... Its
  effectiveness stems from reframing the learning problem: by leveraging the
  coarse solver as a strong physical baseline, the network's task is simplified
  to predicting small, well-conditioned residual."* Per the fetch, LC is *"a deep
  FiLMed residual network with spectral convolutions in its residual blocks"* --
  i.e. **the best corrector in that paper's four-way comparison is
  convolution+spectral, NOT attention**; attention appears only inside the
  LSC-FNO variant for global modulation. Compared architectures: PI-FNO-UNET,
  LSC-FNO, PINO, LC.
- Also returned (not fetched): https://arxiv.org/pdf/2509.20770 ("Extrapolating
  Phase-Field Simulations in Space and Time with Purely Convolutional
  Architectures" — title alone is an adversarial datapoint for our phase-field
  panel), https://arxiv.org/pdf/2206.04675, https://arxiv.org/pdf/2308.02137.

### Term 2 — the Transolver-is-linear-attention claim is now CITABLE (FETCHED)
- **"Transolver is a Linear Transformer: Revisiting Physics-Attention through the
  Lens of Linear Attention"**, arXiv mirror https://arxiv.org/abs/2511.06294
  (AAAI 40(1) 408-416; also https://dl.acm.org/doi/10.1609/aaai.v40i1.37003 and
  the PDF https://arxiv.org/pdf/2511.06294) — **FETCHED via `/abs/`** after the
  AAAI PDF fetch failed in iteration 2. Verbatim from the fetch: *"Physics-Attention
  can be reformulated as a special case of linear attention, and that the slice
  attention may even hurt the model performance."* And: performance gains
  *"primarily stem from the slice and deslice operations themselves"*, not from
  inter-slice interactions; their LinearNO reaches SOTA on six PDE benchmarks
  while *"reducing the number of parameters by an average of 40.0% and
  computational cost by 36.2%"*.
  **This is the single most important finding of this batch.** It says the
  attention in our corrector is, mechanistically, a learned soft
  pooling/unpooling (slice/deslice) -- which is exactly what B1 measured
  empirically ("read the coarse solve through a 1024-point cloud and drag the FNO
  toward it", correction collinear with `copylf - base`). Independent published
  confirmation that the *nonlocal content-adaptive* part is not what is doing the
  work.
- Also: GeoTransolver https://arxiv.org/html/2512.20399v1, Transolver-3
  https://arxiv.org/html/2602.04940v2, reference implementation
  https://github.com/thuml/Transolver/blob/main/Physics_Attention.py.

### Term 3 — No usable results for the ML question
- The engine returned pure applied-mathematics on nonlocal reaction-diffusion
  fronts (https://arxiv.org/pdf/2601.05832, https://arxiv.org/pdf/1410.4611,
  https://arxiv.org/pdf/2606.00594, https://link.springer.com/chapter/10.1007/978-3-031-77772-1_7)
  — i.e. papers where *the PDE itself* has a nonlocal operator. Nothing about
  whether a **learned corrector** for a local reaction-diffusion PDE needs a
  nonlocal receptive field. **No usable results.** This matters: it means there
  is no published support for "fisher_kpp needs attention", and B1's single
  datapoint stands alone.

## Interpretation

The prior art is *hostile* to the attention premise on this panel: the one clear
attention-beats-spectral result is scoped to irregular geometry
(arXiv:2605.08318), the best coarse-field corrector in a four-way comparison is
convolutional+spectral (arXiv:2511.09729v1), and the Transolver mechanism itself
has been shown to be linear attention whose slice attention *"may even hurt"*
(arXiv:2511.06294). Any s4-B2 card that spends GPU time on an attention
corrector must therefore be framed as **testing that hostile prior**, not as
riding a promising one — and its natural control is a local/convolutional
corrector of matched parameter count.
