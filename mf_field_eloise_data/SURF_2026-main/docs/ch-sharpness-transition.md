# Research direction: the frequency-content transition, with Cahn–Hilliard as a tunable knob

**For:** Nicholas (mentor review) · **Status:** proposal + data-side prototype · **Date:** 2026-06-16

## One-line
Use Cahn–Hilliard's interface width **$\varepsilon$** as a *continuous* sharpness control to locate the
**transition point** where multi-fidelity (MF) fusion overtakes FNO-finetuning as the solution
goes from low- to high-frequency — turning the project from "we added sharp datasets" into "we
*characterized* the sharpness-dependence of the MF-vs-finetune crossover."

## The idea
The existing benchmark found FNO-finetuning beats MF fusion **on a mostly-smooth dataset suite**.
We're adding sharp datasets to test whether that survives. The stronger version: rather than a few
discrete points (Euler shock / CH interface / KS smooth), use **$\varepsilon$ to sweep sharpness continuously
within one PDE** and measure where the model ranking flips.

## Why $\varepsilon$ is an unusually clean knob
Comparing *different* PDEs to study frequency content confounds physics, dimensionality, and solver
bias. $\varepsilon$ avoids all of it: **same equation, same solver, same IC distribution, same domain, same
fidelity ladder — only the interface width changes.** So any shift in the model gap is attributable
to frequency content alone. CH becomes a controlled "tunable phantom" spanning the frequency axis;
Euler anchors the discontinuous extreme, KS the smooth extreme.

## Visual intuition
Real CH fields as $\varepsilon$ shrinks (smooth → sharp), with their radial spectra below. Smaller $\varepsilon$ →
visibly sharper interfaces / finer domains → the spectral tail lifts past the FNO mode cutoff
(shaded band) — and that truncated energy is precisely what FNO loses and MF fusion could recover.

![CH sharpness, fields + spectra](figures/ch_sharpness_visual.png)

## Experiment shape
1. Generate CH at an **$\varepsilon$-ladder** ($\approx$0.006 → 0.028).
2. Map each $\varepsilon$ to a **measured sharpness axis** — HF radial-spectrum decay slope and energy fraction
   above FNO's mode cutoff $k_{\max}$ (physical, measurable x-axis, not just "$\varepsilon$").
3. Train **FNO-finetune vs MF-fusion** at each $\varepsilon$; measure the gap (on the sharp-field metric panel,
   not rel-L2 alone).
4. Plot **gap vs sharpness** → the crossover is the transition point.

## The confound that must be controlled (the crux)
As $\varepsilon$ shrinks, **two** things change, not one:
- (a) the HF field gets sharper (the effect of interest), and
- (b) the **LF rungs stop tracking HF** (rel-L2 → >1; the coarse grid under-resolves the interface
  and produces a *different* solution, not a blurred one).

> **What "rung" means.** A *rung* is one resolution level in the fidelity ladder — picture the rungs
> of a ladder, one per grid size. The **LF rungs** are the coarse levels *below* HF: e.g. for a
> $64^2/128^2/256^2$ ladder with HF $=256^2$, the LF rungs are $64^2$ and $128^2$. Below, "**the
> $128\!\to\!256$ rung**" means *how well the $128^2$ level matches the $256^2$ HF* (small rel-L2 =
> it tracks; rel-L2 $\approx 1$ = it's a different field), and "**span**" is their resolution ratio
> ($256/128 = 2\times$). A bigger span (e.g. $64\!\to\!256 = 4\times$) is a harder jump for LF to
> still resemble HF.

These are different mechanisms and can **fight**: if LF turns to noise at small $\varepsilon$, MF fusion has
nothing to fuse and may do *worse*, masking or reversing the effect. So a naive $\varepsilon$-sweep confounds
"FNO can't represent high-k" with "LF became uninformative."

**Design fork:**
- **Clean / mechanistic** (recommended first): keep LF informative across the $\varepsilon$ range — use a
  **shallow, fine ladder** (HF = $256^2$, LF only ~2× coarser) so LF still tracks even at small $\varepsilon$.
  Then only HF sharpness varies.
- **Realistic / coupled**: accept that cheap LF solvers genuinely under-resolve sharp features;
  sweep both, but **measure and report both axes** (HF slope *and* LF-HF gap) so the result is
  attributable.

## Resolution & time considerations
- **HF resolution ceiling:** at $128^2$ the HF reference is only clean down to $\varepsilon$ $\approx$ 0.012; below that
  the HF itself under-resolves. A wide, clean sweep wants **HF = $256^2$** ($512^2$ for the sharpest).
- **Coarsening / output time T:** CH morphology coarsens at $\varepsilon$-dependent rates. Snapshot at
  *comparable morphology* (similar domain size / interface count), not a fixed T, or $\varepsilon$ confounds
  with "amount of coarsening."

## What's prototyped (data side, done)
`mffp_sharp/scripts/ch_sharpness_sweep.py` — sweeps $\varepsilon$ at HF = $256^2$ and reports, per $\varepsilon$: the HF decay
slope, energy fraction above $k_{\max}$, and the LF-HF rel-L2 for the $128^2$ and $64^2$ rungs (the
divergence confound). Figure: `docs/figures/ch_sharpness_sweep.png`.

Anchoring measurements (HF spectral slope, k 5–40; steeper = smoother):
- **Euler shock:** $\approx$ −2.9 (discontinuity, the sharp extreme)
- **KS control:** $\approx$ −12.7

### Sweep results (HF = $256^2$, T = 1, dt = 5e-5; single IC, seed 42)

| $\varepsilon$ | cells @$256^2$ | HF slope | energy > k=12 | rel-L2 128→256 | rel-L2 64→256 |
|---|---|---|---|---|---|
| 0.006 | 1.5 | −5.16 | 2.3e-3 | 0.85 | 1.22 |
| 0.008 | 2.0 | −6.39 | 1.1e-3 | 0.06 | 1.11 |
| 0.010 | 2.6 | −7.54 | 1.2e-3 | 0.92 | 1.21 |
| 0.013 | 3.3 | −9.62 | 2.2e-4 | 0.06 | 1.77 |
| 0.016 | 4.1 | −11.56 | 8.2e-5 | 0.03 | 0.08 |
| 0.020 | 5.1 | −14.18 | 2.0e-5 | 0.02 | 1.29 |
| 0.028 | 7.2 | −19.64 | 2.1e-6 | 0.02 | 0.07 |

![CH sharpness sweep](figures/ch_sharpness_sweep.png)

**Sharpness axis (left panel) — clean and monotonic.** $\varepsilon$ is an excellent *continuous* frequency
knob: the HF slope rises smoothly from −19.6 ($\varepsilon$=0.028, effectively smooth) to −5.2 ($\varepsilon$=0.006,
sharpest), and energy above k=12 spans ~3 orders of magnitude. We can dial sharpness precisely.
*Caveats:* even the sharpest stable CH (−5.2) is milder than Euler (−2.9); the very sharp end is
capped by **solver stability** (dt=2e-4 overflowed at sharp $\varepsilon$ on $256^2$ — needed dt=5e-5, ~4× slower)
and by the **resolution floor** ($\varepsilon$=0.006 $\approx$ 1.5 cells).

**LF divergence (right panel) — erratic, NOT a clean function of $\varepsilon$.** This is the key caveat for the
experiment design:
- The **128→256 rung (2× span) mostly tracks** (rel-L2 $\approx$ 0.02–0.06) — with one spike to 0.92.
- The **64→256 rung (4× span) mostly diverges** (rel-L2 > 1).
- Neither is monotonic in $\varepsilon$ — the divergence is dominated by **pattern/mode-selection noise**
  (whether the coarse grid's spinodal pattern happens to align with HF's), highly sensitive to the
  single IC used here.

**Implications for the design:**
- A **2× ladder (128/256) is the right "clean" choice** — LF mostly tracks, so frequency content is
  the dominant variable — *but average over many ICs to tame the spikes.*
- The **4× ladder bottom rung is unreliable** for sharp CH (confirms the earlier concern).
- The LF-divergence axis must be **measured per-dataset (averaged over ICs)**, not assumed smooth.
- Generating sharp CH at $256^2$ costs ~4× more (small dt) — budget for it.

## What's needed next (model side)
The crossover itself is measured by training **FNO-finetune vs MF-fusion** at each $\varepsilon$ — that lives in
the existing MFFP modeling codebase, not here. The data side (controlled $\varepsilon$ datasets + sharpness
axis) is what this repo provides.

## Decision for Nicholas
1. **Scope:** adopt the transition study as the framing (stronger, more mechanistic) vs. keeping
   "add sharp datasets"?
2. **Ladder:** clean ($256^2$ HF, $128^2$ LF, 2× span) vs realistic (64/128/256) — or run both?
3. **k_max:** what is FNO's mode cutoff in the benchmark? It sets the "sharp enough" threshold and
   the sharpness-axis units.
