# Iteration 3 — Stream `s5_tuning`, Batch 1

## Search rationale

Iterations 1-2 answered the generic question ("does raising modes help?" — not
reliably) and the fairness question ("is fixed-LR mode scaling mis-tuned?" — yes). What
is still missing is **panel-specific** evidence: five of six panel datasets are sharp-2D
phase-field/reaction fronts, and the generic FNO mode literature is built on
Darcy/Navier-Stokes. Three probes:

1. Phase-field-specific (Allen-Cahn / Cahn-Hilliard) neural-operator work — note that
   `sharp__cahn_hilliard/meta.json` names **E-UNO (arXiv:2509.01293)** as its own source
   paper, so that paper's FNO baseline config is the closest published comparator we have.
2. Is there a **principled selection rule** for mode count (power spectrum / Nyquist /
   explained energy)? This decides whether a flat 32 is the right instrument or whether a
   per-dataset value is derivable for free (relevant to the D1 diagnostic idea).
3. **Aliasing**: the practical-perspective survey claimed too many modes inject
   unresolved high-frequency energy that folds back through the pointwise nonlinearity.
   If true this is the concrete mechanism by which 12 -> 32 could make things *worse*,
   and it is a measurable signature.

## Search terms used
1. "Fourier neural operator phase field sharp interface Allen-Cahn Cahn-Hilliard spectral resolution number of modes"
2. "selecting number of Fourier modes from power spectrum energy criterion neural operator Nyquist rule"
3. "aliasing Fourier neural operator pointwise nonlinearity high frequency spectral neural operator"

## Findings

### Term 1: "FNO phase field sharp interface Allen-Cahn Cahn-Hilliard ... number of modes"

- [2025] **"Equivariant U-Shaped Neural Operators for the Cahn-Hilliard Phase-Field
  Model" (E-UNO)** — the cited source of this project's own `sharp__cahn_hilliard`
  dataset (`data/sharp__cahn_hilliard/meta.json`: `source: E-UNO (arXiv:2509.01293)`).
  URL: https://arxiv.org/html/2509.01293v3 (fetched below)
- [2025] "Learning coupled Allen-Cahn and Cahn-Hilliard phase-field equations using
  Physics-informed neural operator (PINO)" — reports that using **Fourier derivatives
  (pseudo-spectral + Fourier extension) instead of finite differences improved the
  Cahn-Hilliard loss by twelve orders of magnitude**, i.e. spectral representation of
  the *operator* matters enormously for this family. URL: https://arxiv.org/abs/2507.18731
- [review] "Fourier Spectral Methods for Phase Field and Interface Dynamics" — if the
  interface is **not resolved by the grid, Gibbs oscillations** appear; Fourier spectral
  schemes are favoured for phase-field precisely because of the Laplacian / bi-Laplacian
  (the grad^4 Cahn-Hilliard term). URL:
  https://www.authorea.com/users/957555/articles/1326468/master/file/data/main2/main2.pdf?inline=true
- [2024] "An end-to-end deep learning method for solving nonlocal Allen-Cahn and
  Cahn-Hilliard phase-field models" — nonlocal phase-field interfaces can be **one grid
  cell wide**. URL: https://arxiv.org/pdf/2410.08914

**WebFetch (arXiv:2509.01293v3, E-UNO).** Trained on **100x100** grids. Baselines:
plain **FNO/E-FNO use a single mode configuration of (16, 16)**; **UNO/E-UNO use a
per-level mode schedule `[[32,32],[16,16],[8,8],[4,4],[8,8],[16,16],[32,32]]`** with
channels `[32,64,64,128,64,64,32]`. Result: "E-UNO and UNO consistently achieve errors
an **order of magnitude lower than FNO**"; E-UNO gives a further 34.32% error reduction
vs UNO at early stages and ~11% median overall. On error structure: FNO shows
"substantially larger and more spatially correlated error structures, **particularly
along evolving phase boundaries**". The paper does not give a mechanistic explanation
for FNO's failure.

### Term 2: "selecting number of Fourier modes from power spectrum energy criterion ... Nyquist rule"

- [2025 survey] "Fourier Neural Operators Explained: A Practical Perspective" — the
  search snippet reports the operative guidance: respect the **Nyquist limit** (too many
  modes relative to resolution makes the model learn artificial/aliased components);
  select by **power-spectrum inspection**; canonical values **12 modes for 2-D, 10 for
  3-D "based on the Nyquist criterion"**; accuracy improves steeply while modes are too
  few and then becomes **marginal past a threshold**. URL: https://arxiv.org/pdf/2512.01421
  **WebFetch attempted and FAILED** to surface the mode-selection subsection (8.5 MB PDF;
  the extractor returned only the background sections and said the guidance was not in
  the accessible portion). The bullet above therefore rests on the search-result snippet,
  not on fetched body text — flagged as lower-confidence.
- [2024] "Toward a Better Understanding of FNOs from a Spectral Perspective" (re-hit) —
  supplies the *energy-based* framing: decompose the **prediction residual** in Fourier
  space; the summed energy spectrum equals the normalized MSE, so residual-energy-by-band
  is the quantity that determines the needed mode budget. URL: https://arxiv.org/abs/2404.07200
- [2024] "Plasma Surrogate Modelling using FNOs" (re-hit) — concrete plateau at 8 modes.
  URL: https://arxiv.org/pdf/2311.05967

### Term 3: "aliasing Fourier neural operator pointwise nonlinearity high frequency"

- [2026] **"Limits of Resolution Equivariance in Fourier Neural Operators"** — URL:
  https://arxiv.org/html/2606.00677 (fetched below)
- [2026] "Performance of Neural and Polynomial Operator Surrogates" — in nonlinear
  regimes with significant high-frequency content, FNOs show **artificial dissipation,
  spectral aliasing and broadband error that are irreducible regardless of training-set
  size**. URL: https://arxiv.org/pdf/2604.00689
- Mechanism statement recurring across these: pointwise nonlinearities are the main
  source of cross-mode interaction; on a discrete grid this appears as **aliasing —
  content generated beyond Nyquist folds back into lower frequencies**.

**WebFetch (arXiv:2606.00677).** Finds an **"encode-process-decode" pattern**:
intermediate feature maps progressively concentrate energy in low frequencies under
spectral truncation, and high-frequency output emerges mainly from the **late decoder
stages** — the network compresses through the limited mode budget and reconstructs detail
nonlinearly. Aliasing is double-edged: **in-distribution it is beneficial**, because
pointwise nonlinearity mixes information across the retained band and lets the net work
despite severe truncation; **under resolution shift it is harmful**, producing "spurious
high-frequency tails". They also report that training at s=85 and running directly at
S=211 often loses to predicting at training resolution and upsampling by Fourier
zero-padding.

## Interpretation (1-3 sentences)

The panel's own source paper (E-UNO, for `sharp__cahn_hilliard`) shows plain FNO at
(16,16) modes losing by an **order of magnitude** to a U-shaped operator whose mode
budget is a **per-level schedule peaking at 32 on the full-resolution levels** — so the
published win on this exact PDE family is not "flat cap = 32" but "32 where the
resolution is high, 4-8 where it is coarse", which the zoo already precedents in
`fno_coreg_residual`'s `(4, 8, 12, 12)` schedule. The aliasing literature supplies the
falsifiable *downside* mechanism for a flat bump — extra modes beyond what the data
resolves fold back through the pointwise nonlinearity into the low band — and the
residual-energy-spectrum framing (2404.07200) gives the zero-training measurement that
would say, per dataset, whether 32 is under- or over-shooting.
