# Concept answers — frequency content, spectral decay, and FNO

Graphs that go with these answers are produced by
`mffp_sharp/scripts/explain_frequency.py` (run on the box: `python scripts/explain_frequency.py`,
writes to `data/explain/`). Each figure is named below.

---

## Q1. What is "radial wavenumber"?

Start with a 1D intuition. Any field can be written as a sum of sine/cosine waves. A **wavenumber
`k`** labels a wave by how fast it wiggles: low `k` = slow, large smooth variation; high `k` = fast,
fine-scale variation. Decomposing a field into its wavenumbers is the Fourier transform; the
**power spectrum** says how much "energy" sits at each `k`.

Our fields are 2D, so the Fourier transform gives a 2D grid of wavevectors `(kx, ky)`:
- `kx` = how fast the field varies in the x-direction,
- `ky` = how fast it varies in the y-direction.

A 2D power spectrum is itself a 2D image — awkward to read. So we collapse it to a single curve by
**radial averaging**: for each magnitude

  k_r = sqrt(kx² + ky²)   ("radial wavenumber" = distance from the origin in (kx,ky)-space)

we average the power of all wavevectors lying on that ring (same `k_r`, any direction). The result
is a 1D curve, **power vs radial wavenumber** — the `radial power spectrum` panel in the one-pager.

How to read that curve (`fig2_radial_wavenumber.png` shows the 2D spectrum with the rings drawn on):
- **left (small k_r)** = large, smooth, slowly-varying structure,
- **right (large k_r)** = small, sharp, fine-scale structure,
- y-axis is power on a **log scale** (energies span many orders of magnitude),
- a curve that **stays high on the right** ⇒ lots of fine/high-frequency content (sharp field);
  a curve that **drops fast** ⇒ smooth field.

For LF vs HF: a coarse 32-grid physically *cannot represent* wavenumbers above its Nyquist limit
(≈ 32/2 = 16 cycles across the box). So the LF spectrum is missing or wrong on the right-hand
(high-k) side; HF carries the true high-k energy. **The gap between the LF and HF spectra at high
k_r is precisely the sharp content LF loses.**

---

## Q2. How do we *know* these PDEs have high-frequency solutions, vs the smooth ones in the deck?

This is the heart of the project, and the answer is both **theoretical** (we can predict it) and
**empirical** (the sample round measures it). `fig3_spectral_decay.png` is the money plot.

### The principle: smoothness ⇔ how fast the spectrum decays
A classical fact: **how fast a function's Fourier spectrum decays is set by how smooth the function
is.**
- A **discontinuity** (a true jump) has Fourier amplitude that decays only like **1/k** — a *very
  slow, heavy tail*. Lots of energy survives out to high k. This is the textbook "a step function
  needs all frequencies."
- A **sharp but continuous** feature — an interface of width `ε`, shaped like `tanh(x/ε)` — is
  actually *smooth*, so its spectrum ultimately decays **exponentially**; but that exponential
  cutoff only kicks in at `k ≈ 1/ε`. Below that it looks like a discontinuity's slow `1/k` plateau.
  So `ε` sets *where* the high-k energy stops, not the decay rate itself (see "Q2b" below). Smaller
  `ε` ⇒ cutoff further right ⇒ more high-frequency content.
- A **smooth (infinitely differentiable / analytic)** field has a spectrum that decays
  **exponentially** — energy at high k is negligible.

So "high-frequency content" has a precise meaning: **energy that persists at large radial
wavenumber** (slow spectral decay).

### Where our three PDEs land
- **2D Euler Riemann → shocks = genuine discontinuities.** Slowest decay (~1/k tail). Highest
  frequency content of the three. *This is the sharpest case by construction.*
- **2D Cahn–Hilliard → interfaces of width ε.** Energy out to `k ~ 1/ε`; sharp but not
  discontinuous. Medium. (And ε is a knob — we choose it so the coarse grid can't resolve it.)
- **2D Kuramoto–Sivashinsky → spectrally smooth.** Looks chaotic/busy, but its energy decays fast
  in k (no shocks, no fronts). This is the **control**: low high-frequency content on purpose.

### Why the deck's datasets are "low-frequency"
The deck's suite is dominated by **diffusive / elliptic / smoothed** problems — heat, Poisson,
Darcy (smooth coefficients), lid-cavity, viscous Burgers at smoothing settings. Diffusion and
elliptic smoothing *kill* high wavenumbers (that's literally what they do), so those solutions are
smooth and their spectra decay fast. Telling detail from the deck's own results
(`mf_field_prediction.pptx`, slide 7 per-dataset rel-L2): the **hardest** existing datasets are
exactly the sharpest ones available there — `allen_cahn` and `burgers` — while the smooth ones sit
orders of magnitude lower in error. The suite simply doesn't contain genuinely shock/interface-
dominated 2D fields. That gap is what we're filling.

### The FNO connection (why this is the right axis to probe)
FNO works by keeping only Fourier modes **below a cutoff** in each layer and discarding the rest.
- If a solution's energy lives **below** the cutoff (smooth) → truncation throws away ~nothing →
  FNO is excellent. (This is why FNO wins on the deck's smooth suite.)
- If energy extends **above** the cutoff (sharp) → truncation **discards real content** → FNO
  blurs the shock/interface, no matter how much HF data it's finetuned on.

So "do these PDEs have high-frequency solutions?" is the same question as "do they put energy above
FNO's mode cutoff?" — and `fig3_spectral_decay.png` draws that cutoff as a vertical line so you can
see which fields have energy to its right.

### How we *verify* it (not just assert it)
We don't assume the sharpness — we **measure** it. `explain_frequency.py` computes the radial
spectra of representative fields (a step, tanh interfaces at two ε's, a smooth field) and overlays
them; the sharp ones show heavy high-k tails, the smooth one drops off a cliff. On the **real**
generated HF fields, the same check runs inside `generate.py` (the bottom-rung check + the
one-pager spectrum panel): if a "sharp" PDE's spectrum decayed as fast as the control's, it would
*not* be high-frequency and we'd revisit the parameters. **Theory predicts it; the sample round
confirms it.**

---

## Q2b. What makes exponential decay "smoother" than `1/k` — and what `1/ε` really is

**The one rule behind all of it:** differentiating a field multiplies its spectrum by `ik`. So
`f̂(k) = (FT of f')/(ik)` — **every genuine derivative a function has buys one extra power of `1/k`
of decay.** Smoothness = number of well-behaved derivatives = number of `1/k` factors.

The ladder, roughest → smoothest:

| Function | Smoothness | Spectral amplitude decay |
|---|---|---|
| jump / shock | not differentiable (derivative is a spike) | `~ 1/k` (slowest) |
| kink (`\|x\|`) | continuous, 1st derivative jumps | `~ 1/k²` |
| `m` continuous derivatives | — | `~ 1/k^{m+1}` |
| infinitely differentiable **+ analytic** | smoothest | `~ e^{-ak}` (exponential) |

**Why exponential is the smoothest class:** `e^{-ak}` decays faster than `1/k^m` for *every* `m`
(pick any power law — eventually the exponential is below it). So an exponential spectrum =
a function that acts as if it has infinitely many controlled derivatives (analytic). A `1/k`
spectrum = a function too rough to differentiate even once. `fig4_smoothness_decay.png` shows this:
in log-log the power laws are straight lines and the exponential curves down through all of them;
in semi-log the exponential is the straight line that ends up below every power law.

**Intuition:** a sharp corner is built from high-frequency waves that have to keep adding up without
dying — the sharpness lives in that surviving high-k amplitude. A smooth field needs only a few
gentle low-frequency waves, so its high-k coefficients are tiny (fast decay).

**The honest fix on `1/ε`:** `1/ε` is **not a decay rate** like `1/k` or `e^{-ak}`. A finite-width
`tanh(x/ε)` interface *is* smooth, so it ultimately decays **exponentially** (`~ e^{-(π/2)εk}`); ε
just sets the **knee** — where the `1/k` plateau ends and the exponential cutoff begins (`k ≈ 1/ε`).
One unifying knob = *where the exponential knee sits*:
- **shock** = `ε → 0` → knee at `k = ∞` → pure `1/k` forever (roughest),
- **interface width ε** → `1/k` plateau, then exponential cutoff at `k ~ 1/ε` (smaller ε = sharper),
- **smooth field** (heat / Poisson / KS) → knee at low `k` → exponential almost from the start.

FNO's mode cutoff is a fixed vertical line; only fields whose knee sits to its **right** carry
content FNO truncates away. So the project's frequency axis is precisely "how far right is the knee."

---

## Q2c. Concrete analytic functions for each decay rate (`fig5_analytic_pairs.png`)

Functions with **closed-form** Fourier transforms, so the decay is exact and provable. The
numerical FFT lands on each analytic envelope (run `scripts/explain_decay_examples.py`).

| Function | Smoothness | Fourier transform | Decay |
|---|---|---|---|
| sawtooth `f(x)=x` on (−π,π) | jump (discontinuous) | `b_n = 2(−1)^{n+1}/n` | `1/k` |
| parabola `f(x)=x²` on (−π,π) | kink (continuous, `f′` jumps) | `a_n = 4(−1)^n/n²` | `1/k²` |
| Lorentzian `1/(1+x²)` | analytic (poles at `±i`) | `π e^{−|k|}` | `e^{−|k|}` |
| Gaussian `e^{−x²/2}` | entire (analytic everywhere) | `√(2π) e^{−k²/2}` | `e^{−k²/2}` |

- The parabola is "one integral smoother" than the sawtooth and its coefficients gain exactly one
  power (`1/n → 1/n²`) — the differentiation ⇔ ×k rule made literal.
- The exponential rate is the **distance to the nearest complex pole** (Lorentzian: `±i` ⇒
  `e^{−1·|k|}`). Analyticity in a strip of half-width `a` ⇒ decay `e^{−a|k|}`. Real-line smoothness
  isn't enough — you need analyticity in the complex plane.
- The Gaussian (no poles anywhere) curves down even on a log axis — `e^{−k²}` beats every straight
  exponential — the smoothest possible.

## Q2d. Why FNO truncates the energy to the right of the cutoff

It's architectural. Each FNO **Fourier layer** does: FFT the feature field → multiply by a learned
weight tensor `R(k)` → inverse FFT → add a pointwise (1×1) linear skip → nonlinearity. The catch:
**`R(k)` is only defined for `|k| ≤ k_max`; every mode above `k_max` is multiplied by zero and
dropped.** That is a hard low-pass filter inside *every* layer.

**Why on purpose:** `R` has shape `[modes × channels × channels]`. Keeping all modes up to Nyquist
would make the parameter count grow with grid resolution `N` and break resolution-invariance.
Keeping a fixed `k_max` makes the weights `O(k_max^d · C²)`, independent of `N` — FNO's selling
point. `k_max` (~12) is a hyperparameter.

**Why it blurs sharp fields:** above `k_max` the only paths for information are the pointwise skip
`W` (acts per-point, can't coordinate neighbors → can't build a sharp edge) and the nonlinearity
(weak, uncontrolled harmonics). The learned spatially-coupled capacity is **zero** above `k_max`.
So a field with real energy at `k > k_max` (shock `1/k` tail; interface content out to `~1/ε`)
can't be reproduced — FNO outputs a band-limited, smoothed version. That is the **spectral bias**,
and it's why only fields with energy to the right of the cutoff line are the ones FNO provably
misses — the regime where multi-fidelity fusion can add value.

---

## Q2e. Given the Fourier transform, how do you compute the decay rate?

**Recipe.** (1) Take the magnitude `|c_n|` (drop sign/phase). (2) Keep the leading large-`n` term.
(3) Pin the exponent two equivalent ways:
- *multiply-by-`n^p`*: the `p` for which `|c_n|·n^p →` nonzero constant.
- *log–log slope*: `log|c_n| = log C − p·log n`, so **decay exponent = −(slope on a log–log plot)**.

Worked (numerically measured via FFT in `explain_decay_examples.py`):
- sawtooth `|b_n|=2/n`: `(2/n)·n=2` ⇒ p=1; log–log slope **−1.000** → `1/k`.
- parabola `|a_n|=4/n²`: `(4/n²)·n²=4` ⇒ p=2; log–log slope **−1.999** → `1/k²`.

**Why the multiply-by-`n^p` rule works — a balancing test.** "Decays like `1/n^p`" means
`|c_n| ≈ C n^{-p}` for a nonzero constant `C`. Multiplying by a known anti-decay `n^p` tries to
*cancel* the unknown decay: `|c_n|·n^p ≈ C n^{-p}·n^p = C`. The limit has a sharp threshold that
pins `p` uniquely:

| guess | `\|c_n\|·n^p` as `n→∞` | meaning |
|---|---|---|
| `p` too small | `→ 0` | correction too weak; still decaying ⇒ true rate is **steeper** |
| `p` exact | `→ C` (nonzero, finite) | powers cancel ⇒ **this is the rate** |
| `p` too big | `→ ∞` | over-corrected; now growing ⇒ true rate is **shallower** |

So as you raise `p` the product goes `0 → C → ∞`, and the transition between vanishing and blowing
up *is* the exponent. You need the limit **nonzero** (rules out too-small) **and finite** (rules out
too-big). E.g. parabola at `p=1`: `4/n → 0`, correctly flagging `1/n²` as steeper than `1/n`.

This is the **same** statement as the log–log slope: take logs of `|c_n|·n^p → C` to get
`log|c_n| ≈ log C − p·log n`. Multiplying by `n^p` *tilts* the log–log line's slope up by `p`; the
right `p` rotates it to **horizontal** (a constant = flat line), and that `p` is `−(slope)`. It also
explains why the rule *fails* for exponentials: no fixed power cancels `e^{-ak}` (`e^{-ak}·n^p → 0`
for **every** `p`), and that collapse-to-0-for-all-`p` is itself the signal to switch to semi-log.

**Power-law vs exponential = which axis linearizes it.** Power law `k^{−p}` is straight on
**log–log** (slope −p); exponential `e^{−ak}` is straight on **semi-log** (slope −a). Lorentzian
`|F|=π e^{−|k|}`: semi-log slope **−1.000** ⇒ rate a=1 (log–log would curve → not a power law).

**Predict `p` before plotting — integration by parts.** `c_n=\frac1{2π}\int_{-π}^{π}f e^{-inx}dx`;
each IBP pulls out `1/(in)` plus a boundary term.
- sawtooth `f=x`: `f(π)≠f(-π)` (jumps by 2π) → first boundary term survives → `~1/n` (p=1).
- parabola `f=x²`: `f` continuous at the seam → first term vanishes; `f'=2x` jumps → second term
  survives → `~1/n²` (p=2).

Rule: **p = (order of the first derivative with a jump) + 1.** Jump in `f` → `1/k`; jump first in
`f'` → `1/k²`; … If no derivative ever jumps (analytic in a complex strip) every boundary term
vanishes forever → no power law → exponential `e^{-ak}`, `a` = strip half-width.

---

## Q2f. Comparing radial spectra: sharp (high-freq) vs smooth (low-freq) — `fig_spectra_compare.png`

Higher radial wavenumber `k_r = √(kx²+ky²)` = finer spatial scale = **higher spatial frequency**
(left of the spectrum = smooth/large-scale, right = sharp/fine-scale). Overlaying the HF radial
spectra of our real fields — Cahn-Hilliard (sharp interface) vs Kuramoto-Sivashinsky (smooth):

- In the **high-wavenumber band (`k_r≈30–60`) the sharp CH field carries ~6 orders of magnitude
  more energy** than smooth KS. That gap *is* the high-frequency content (and exactly what FNO's
  mode cutoff discards — present for CH, absent for KS).
- **KS collapses early:** peak at its characteristic scale (`k_r≈2–3`), then a cliff to the floor
  by `k_r≈15`. Smooth = structure at one scale, nothing finer.
- **CH spreads energy across all scales** (near-discontinuous interface → heavy `1/k`-type tail).

Caveats: the flat `~1e-17` tail on both is the numerical **noise floor** (round-off), not signal;
and at the *lowest* `k_r` KS actually sits higher (it concentrates energy at its own scale) — the
sharp-vs-smooth distinction is specifically about the **high-`k` tail**, not total energy.
Reproduce: `scripts/explain_spectra_compare.py`.

---

### One-line summary
- **Q1:** radial wavenumber `k_r = sqrt(kx²+ky²)` = distance from the origin in 2D frequency space;
  the spectrum curve is power averaged over each ring — left = smooth/large-scale, right =
  sharp/fine-scale.
- **Q2:** sharpness ⇔ slow spectral decay; shocks (Euler) and thin interfaces (Cahn–Hilliard) keep
  energy at high k, while diffusive/elliptic deck problems (and the KS control) decay fast — and we
  measure the spectra to confirm it rather than assume it.
