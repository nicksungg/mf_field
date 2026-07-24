# PDE portfolio — one-page summary

**For:** Nicholas (mentor review) · **Date:** 2026-06-16
*Full reasoning & thought process (with all the plots): [design-rationale.md](design-rationale.md).*

Three 2D PDEs spanning the frequency axis **shock → sharp interface → smooth control**, to add the
high-frequency datasets the MFFP benchmark lacks. For each: governing equation, condition vector
(the per-sample scalars that define it), fidelity ladder, how LF differs from HF, and snapshot time $T$.

![Portfolio HF fields: shock, sharp interface, smooth](figures/pde_portfolio.png)

---

## 1. 2D Euler (Riemann) — SHOCK  [sharp extreme]
<img src="figures/euler_field.png" width="320">

- **Equation:** $\partial_t U + \nabla\cdot F(U) = 0$ (compressible Euler); 4-quadrant Riemann
  initial condition.
- **Condition vector (7):** pressure ratios $p_{TL}/p_{TR},\ p_{BL}/p_{TR},\ p_{BR}/p_{TR}$;
  density ratios $\rho_{TL}/\rho_{TR},\ \rho_{BL}/\rho_{TR},\ \rho_{BR}/\rho_{TR}$; $\gamma$.
- **Sampling:** around the Schulz–Rinne canonical 2D Riemann configs ($+10\%$ jitter); $\gamma = 1.4$.
- **LF vs HF:** LF = coarse 1st-order Godunov (Classic, diffuses shocks); HF = fine WENO (SharpClaw).
- **Ladder:** $32^2 / 64^2 / 128^2$. **Snapshot $T = 0.25$.**
- **Status:** validated. HF spectral slope $\approx -2.9$ (true discontinuity — the sharpest case).
  LF $32^2$-vs-HF rel-L2 $\approx 0.08$ (small — the field is mostly smooth with a thin shock, so LF
  *tracks*). **Suitable.** *(Note: judge on $L_\infty$/shock-position, not rel-L2, which hides the
  thin blurred shock.)*

## 2. 2D Cahn–Hilliard — SHARP INTERFACE  [tunable middle]
<img src="figures/cahn_hilliard_field.png" width="320">

- **Equation:** $\partial_t c = M\,\nabla^2(c^3 - c - \varepsilon^2 \nabla^2 c)$. Two phases
  ($c \approx \pm 1$) separated by interfaces of width $\sim\varepsilon$.
- **Condition vector (3):** $\varepsilon$ (interface width = sharpness knob), $M$ (mobility),
  $\bar c$ (mean composition) (+ IC random seed).
- **Sampling (current):** $\varepsilon \in [0.012, 0.018]$, $M \in [0.5, 1.5]$,
  $\bar c \in [-0.1, 0.1]$; domain $1$.
- **LF vs HF:** same solver, only the grid changes (coarse grid under-resolves $\varepsilon$).
- **Ladder:** $32^2 / 64^2 / 128^2$. **Snapshot $T = 5.0$.**
- **Status: NEEDS A DECISION — the current samples aren't usable yet.** Here's the problem, step by step:

  **What a usable multi-fidelity dataset needs.** LF should be a *blurry version of HF* — the **same**
  solution, just less detailed — so the model can learn to sharpen LF into HF. If LF is instead a
  **different** solution, there's nothing useful for the model to learn from it.

  **Why the current CH samples fail that.** An interface of width $\varepsilon$ needs roughly **2 grid
  cells across it** to be represented at all. At $\varepsilon \in [0.012, 0.018]$ (domain size 1):
  - On the **HF grid ($128^2$, cell size $\approx 0.008$)** the interface is ~1.5–2 cells wide — *just*
    resolved. Good.
  - On the **coarse grids ($32^2$, cells $\approx 0.031$; $64^2$, cells $\approx 0.016$)** the interface
    is **less than one cell** wide. The coarse grid literally *can't represent the interface* — so
    instead of blurring the HF pattern, it grows a **different** phase pattern (the blobs end up in
    different places).

  **How we know.** The relative error between LF and HF is **rel-L2 $\approx 1.27$**. *(rel-L2 = the
  size of the LF–HF difference ÷ the size of the field; $0$ = identical, $\approx 1$ = as different as
  two unrelated fields.)* So a value **above 1** means LF and HF are essentially **uncorrelated** —
  different solutions, not blurry-vs-sharp versions of one. That's a broken fidelity ladder, and it's
  why the LF/IF panels in the one-pager look nothing like HF.

  **Two ways to fix it (pick one):**
  - **(a) Use a wider interface — milder $\varepsilon$ ($\sim 0.025$–$0.04$).** Now the interface is
    ~3–5 cells even on the coarse grids, so LF resolves it and becomes a faithful blurry HF.
    *Cost:* a wider interface is less sharp (HF slope $\sim -11$, i.e. closer to smooth) — so we partly
    give up the high-frequency content that is the whole point.
  - **(b) Shift the whole ladder up — $128/256$ instead of $32/64/128$.** Spanning $32\!\to\!128$ is a
    4× resolution jump (too big for a sharp interface); spanning $128\!\to\!256$ is only 2×. With
    HF $=256^2$ the sharp interface is cleanly resolved, and LF $=128^2$ is only 2× coarser so it still
    resolves it — a blurry-but-faithful LF. *Result:* sharp HF **and** a working ladder (slope
    $\sim -7$). *Cost:* ~4× heavier compute ($256^2$), and CH would use a different ladder than
    Euler/KS. This is the "clean" option — see
    [ch-sharpness-transition.md](ch-sharpness-transition.md).

  (Note: $\varepsilon$ being a *continuous sharpness knob* is also exactly what makes CH the candidate
  for the transition study.)

## 3. 2D Kuramoto–Sivashinsky — SMOOTH  [control]
<img src="figures/kuramoto_sivashinsky_field.png" width="320">

- **Equation:** $\partial_t u = -\nabla^2 u - \nabla^4 u - \tfrac{1}{2}\lvert\nabla u\rvert^2$.
  Spatiotemporally chaotic but spectrally smooth.
- **Condition vector (2):** $L$ (domain size), $A_0$ (IC amplitude) (+ IC random seed).
- **Sampling:** $L \in [22, 36]$, $A_0 \in [0.05, 0.2]$.
- **LF vs HF:** same solver, only the grid changes.
- **Ladder:** $32^2 / 64^2 / 128^2$. **Snapshot $T = 15$** (tracking window — *not* 50: by
  $T \sim 50$ KS chaotically decorrelates, so LF/HF become different states; $T=15$ keeps them on one
  trajectory). Store the zero-mean fluctuation $u - \bar u$.
- **Status:** validated. HF slope $\approx -12.7$ (smooth, as intended); LF $32^2$-vs-HF
  $\approx 0.23$ (tracks). **Suitable** as the smooth anchor of the frequency axis.

---

## The axis at a glance
| PDE | role | HF spectral slope | LF tracks HF? |
|---|---|---|---|
| Euler | shock (discontinuity) | $\approx -2.9$ | yes ($\approx 0.08$) |
| Cahn–Hilliard | sharp interface (tunable $\varepsilon$) | $-7 \ldots -13$ | **depends on $\varepsilon$ / ladder — decision pending** |
| KS | smooth control | $\approx -12.7$ | yes ($\approx 0.23$) |

## Open decisions for Nicholas
1. **CH operating point:** milder $\varepsilon$ (faithful LF) vs 2× ladder (sharp + faithful) vs
   adopt $\varepsilon$ as the transition-study knob.
2. Condition-vector **ranges** and **sample counts** for full generation.
3. FNO's **mode cutoff $k_{\max}$** (sets the "sharp enough" threshold).
