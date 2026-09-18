# How we got here: choosing the PDEs, condition vectors, and the sharpness-transition idea

**A plain-language walkthrough of the reasoning.** Companion to the concise
[pde-summary.md](pde-summary.md) (the quick reference) and
[ch-sharpness-transition.md](ch-sharpness-transition.md) (the study proposal).

---

## 0. The question we're answering
The MFFP benchmark predicts an expensive **high-fidelity (HF)** PDE solution field from a cheap
**low-fidelity (LF)** field + a few HF training samples. Its headline result was that simple
**FNO-finetuning beats fancier multi-fidelity (MF) fusion** — *but that was measured on a
dataset suite that is mostly **smooth***. Our job: **add high-frequency (shock / crack) PDEs** and
test whether that conclusion still holds when the solution is sharp.

So the whole project hinges on one axis: **smooth → sharp**. Everything below is about (1) making
that axis precise, (2) picking PDEs that span it, and (3) realizing we can *tune along it* with one
knob.

---

## 1. What "high frequency" actually means
Any field can be written as a sum of waves. A wave's **wavenumber $k$** says how fast it wiggles —
low $k$ = big smooth features, high $k$ = fine sharp features. In 2D we summarize this with the
**radial wavenumber** $k_r=\sqrt{k_x^2+k_y^2}$ (distance from the center of the 2D spectrum); the
**radial power spectrum** is how much energy sits at each $k_r$.

![radial wavenumber](figures/fig2_radial_wavenumber.png)

The key fact: **how fast that spectrum decays tells you how smooth the field is.**
- A **sharp feature** (a jump/shock) decays *slowly* — like $1/k$ — so it keeps energy out to high
  $k_r$.
- A **smooth feature** decays *fast* — exponentially — so it has almost no high-$k_r$ energy.

![sharp vs smooth spectral decay](figures/fig3_spectral_decay.png)

So **"high frequency" = a slowly-decaying spectrum = energy at high wavenumbers = sharp features.**
That is the precise version of "shock / crack."

---

## 2. Why FNO struggles with high frequency (the hypothesis)
An FNO (Fourier Neural Operator) works by keeping only Fourier modes **below a cutoff** $k_{\max}$
and discarding the rest, every layer. Consequences:
- **Smooth field:** all its energy is below $k_{\max}$ → truncation loses nothing → FNO is excellent.
  *(This is why FNO-finetuning won on the deck's smooth suite.)*
- **Sharp field:** real energy lives **above** $k_{\max}$ → FNO throws it away → it blurs the
  shock/interface, no matter how much HF data it sees.

In the figure above, that's the shaded band right of the cutoff. **The hypothesis:** MF fusion —
which can use the cheap LF to carry the sharp structure — should win back ground exactly where FNO's
truncation bites. We add sharp PDEs to test it.

---

## 3. Choosing the PDEs — span the axis, and include a control
We want datasets that **span smooth → sharp**, plus a deliberate **control** at the smooth end so
that, if MF fusion wins on the sharp cases, we can prove the effect is *about sharpness* and not
"our models are just better everywhere." Three picks:

![portfolio: shock, interface, smooth](figures/pde_portfolio.png)

- **2D Euler (Riemann) — SHOCK.** Gas dynamics; the solution has genuine **discontinuities**
  (shocks). The sharpest possible case (a true jump → $1/k$ tail). *The sharp extreme.*
- **2D Cahn–Hilliard — SHARP INTERFACE.** Phase separation; thin **interfaces** of tunable width
  $\varepsilon$ between two phases. Sharp but continuous. *The tunable middle (this becomes important
  in §7).*
- **2D Kuramoto–Sivashinsky — SMOOTH.** Looks chaotic/busy but is **spectrally smooth** (no sharp
  features). *The control — FNO should do fine here.*

Real spectra of two of them confirm the spread — the sharp CH field carries far more high-$k$ energy
than the smooth KS field:

![CH vs KS spectra](figures/fig_spectra_compare.png)

---

## 4. Low- vs high-fidelity: the ladder, and the one rule that matters
**Fidelity = grid resolution.** HF is a fine-grid solve (accurate, expensive); LF is a coarse-grid
solve (blurry, cheap). We use a **ladder** of resolutions — $32^2 / 64^2 / 128^2$ — with $128^2$ as
HF, all interpolated onto the HF grid so the model can compare them.

**The one rule: LF must be a *real coarse-grid solve* of the same PDE — never a downsampled HF.**
Downsampling a sharp HF field injects fake ringing (Gibbs/aliasing artifacts) that no real solver
produces; a model would learn to undo that artifact instead of the true physics. A genuine coarse
solve is *biased and blurry in a physical way* — and that honest bias is exactly what MF fusion
learns to correct.

The figure below shows the idea: the same field at a coarse grid (genuinely blocky), upsampled
(same pixels, still blurry — no detail invented), and the true fine field; the difference is the
sharp content the coarse grid misses.

![LF vs HF resolution](figures/fig1_resolution.png)

**What we generate per sample** is a one-pager like these (LF/IF/HF fields, the error each coarse
grid makes vs HF, and the spectrum with its decay slope), so a reviewer can judge each dataset —
one per PDE:

*Euler (shock):*
![sample one-pager (Euler)](figures/euler_one_pager.png)

*Cahn–Hilliard (sharp interface):* — note the LF/IF panels look *different* from HF, not just
blurrier; that's the sharp-$\varepsilon$ under-resolution issue we unpack in §6.
![sample one-pager (Cahn–Hilliard)](figures/cahn_hilliard_one_pager.png)

*Kuramoto–Sivashinsky (smooth control):* — here LF/IF *do* track HF (just blurrier), as a control
should.
![sample one-pager (KS)](figures/ks_one_pager.png)

---

## 5. Choosing the condition vectors
Each sample is the *same* PDE with *different settings*; the **condition vector** is the short list
of scalars that pick out one instance (and the model's input, alongside the LF field). Choosing it
has two separate parts:

1. **Schema (which scalars)** — read off each PDE's definition; barely a choice:
   - **Euler:** the 4 quadrant states → pressure & density ratios + $\gamma$ (7 numbers).
   - **Cahn–Hilliard:** interface width $\varepsilon$, mobility $M$, mean composition $\bar c$.
   - **KS:** domain size $L$, IC amplitude $A_0$.
2. **Ranges (what values)** — *not* free: they're coupled to the fidelity ladder and to solver
   stability, so we set provisional ranges and **validate them in the sample round** (next section).
   The condition vector must be *complete* — those scalars (+ solver + snapshot time) must fully
   determine the field — which is why the snapshot time also had to be pinned down.

(Full schemas + ranges are in [pde-summary.md](pde-summary.md).)

---

## 6. What generating the samples taught us (validation)
Two provisional choices turned out to be wrong, and measuring caught both:

**KS control — the snapshot time was wrong.** KS is *chaotic*: tiny differences grow exponentially.
At a late time ($T\approx50$) the coarse and fine solves drift into **completely different** chaotic
states, so LF and HF disagree for reasons that have **nothing to do with frequency** — a confound.
The fix is a *tracking-window* time ($T=15$) where they still follow one trajectory:

![KS chaos vs T](figures/fig_ks_chaos.png)

**Cahn–Hilliard — the first $\varepsilon$ was too smooth.** We *measured* the HF spectral decay
slope (steeper = smoother) and found CH at our first range was $\le-13$ — **smoother than the KS
control!** It wasn't a high-frequency case at all. Smaller $\varepsilon$ = sharper, so we narrowed
the range; but pushing $\varepsilon$ smaller also makes the coarse grids unable to resolve the
interface, so **LF stops resembling HF** (a different pattern, not a blurred one). That tension —
sharper HF vs faithful LF — is the CH "operating point" decision still open for Nicholas.

The lesson: **don't assume sharpness — measure the spectrum.** That measuring habit is what led
straight to the next idea.

---

## 7. The idea: $\varepsilon$ is a continuous sharpness knob → study the *transition*
Here's the realization. Comparing *different* PDEs (Euler vs CH vs KS) gives a few **discrete**
points on the smooth→sharp axis, and always risks confounds (different physics). But **Cahn–Hilliard's
$\varepsilon$ lets us tune sharpness *continuously*, holding everything else fixed** — same equation,
same solver, same initial conditions. You can literally watch the field sharpen and its spectral
tail grow as $\varepsilon$ shrinks:

![CH fields + spectra vs eps](figures/ch_sharpness_visual.png)

So instead of asking "does MF fusion win on sharp PDEs?", we can ask the much sharper question:
**at what sharpness does MF fusion overtake FNO-finetuning?** — i.e. *map the transition point* by
sweeping $\varepsilon$ from smooth to sharp. That reframes the contribution from "we added sharp
datasets" to "we *characterized* the sharpness-dependence of the crossover," which is a stronger,
more mechanistic result.

We prototyped the **data side** of this (the model comparison itself lives in the MFFP codebase):

![CH sharpness sweep](figures/ch_sharpness_sweep.png)

- **Left — it works:** the sharpness axis is clean and monotonic. $\varepsilon$ smoothly dials the
  HF decay slope from $-19.6$ (smooth) to $-5.2$ (sharpest), spanning ~3 orders of magnitude of
  high-$k$ energy. A precise, controllable knob.
- **Right — the catch:** the **LF divergence is erratic** (not a smooth function of $\varepsilon$) —
  whether a coarse grid's pattern happens to match HF is noisy and IC-sensitive. So the right design
  is a **2× ladder** (e.g. $128/256$, where LF tracks) and **averaging over many initial conditions**.

Full proposal, confounds, and decisions in
[ch-sharpness-transition.md](ch-sharpness-transition.md).

---

## 8. Where we are
- **Portfolio chosen and validated:** Euler (shock), CH (tunable interface), KS (smooth control) —
  spanning the frequency axis, with the control anchoring the smooth end.
- **Condition vectors:** schemas fixed; ranges validated (and corrected — KS $T$, CH $\varepsilon$).
- **A stronger framing emerged:** CH $\varepsilon$ as a continuous knob to map the smooth→sharp
  **transition** in model performance.
- **Open for Nicholas:** the CH operating point (milder $\varepsilon$ vs a 2× ladder vs the full
  transition study), the sample counts/ranges for full generation, and FNO's $k_{\max}$ (which sets
  "sharp enough"). See [pde-summary.md](pde-summary.md).
