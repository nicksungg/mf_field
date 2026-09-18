# Sample-round report: from 3 PDEs to a 24-dataset screened menu

*Status: report for Nicholas. Date: 2026-06-18. Companion to
[design-rationale.md](design-rationale.md) (which covered the original 3-PDE portfolio) and the
design spec [docs/superpowers/specs/2026-06-17-sharp-pde-portfolio-expansion-design.md](superpowers/specs/2026-06-17-sharp-pde-portfolio-expansion-design.md).*

---

## TL;DR — what happened since `design-rationale.md`

`design-rationale.md` justified the **locked 3-PDE portfolio**: 2D Euler Riemann (shock), 2D
Cahn–Hilliard (tunable interface), 2D Kuramoto–Sivashinsky (smooth control). That doc ends with the
honest worry that 3 discrete points on the smooth→sharp axis is thin, and always risks confounding
"sharpness" with "different physics."

Since then we did **not** pre-commit to one or two extra PDEs. We instead:

1. Wrote a design spec that reframes the choice as **"build the maximal feasible candidate set, sample
   each, auto-screen, and hand Nicholas the survivors to pick from."** This *widens* the existing
   "sample → Nicholas approves → full counts" gate without skipping it.
2. Broke that spec into **8 implementation plans** and executed them.
3. Built **16 PDE solvers** (up from 3), exposing **24 sample datasets** (1D + 2D variants).
4. Generated a sample batch on the box and ran the auto-screen → **72 review one-pagers**
   (24 datasets × 3 samples each), plus `sample_summary.json` and `screen_report.json`.

**The 72 figures are the deliverable of this round: a screened menu of candidate datasets for you to
choose from.** Nothing has been generated at full counts — that still waits on your sign-off.

---

## Why expand at all (the framing that drove the spec)

Two facts reshaped the selection criteria away from "pick a couple more sharp PDEs":

- **The premise is architecture-neutral.** The benchmark compares ~8 model *families* (3 FNO
  variants, 2 attention/transolver operators, and the `mfrnp` / `mf_deeponet` / `d_mfd` baselines)
  across 15 datasets. So "sharp" can't literally mean "energy above FNO's $k_{\max}$" — it has to mean
  a **measured high-wavenumber content** that degrades *all* these operators (FNO just most
  explicitly). That makes "sharp enough" a measured quantity, which is exactly what the screen
  computes.
- **1D is allowed.** The benchmark already ships 1D datasets (`allen_cahn_gen`, `burgers_gen`,
  `burgers_param_gen`), so 1D is native to the format — it roughly doubles the candidate pool for
  cheap, *if* our `common/` infrastructure stops being 2D-hardcoded.

A literature survey ([docs/research/2026-06-17-hf-pde-generation-recipes.md](research/2026-06-17-hf-pde-generation-recipes.md))
pinned **published generation recipes** for the candidates (so our parameter regimes replicate
precedent rather than inventing thresholds) and confirmed the **scoped contribution gap**: no surveyed
benchmark is simultaneously high-frequency *and* multi-fidelity-via-independent-coarse-solves. That
intersection is what we're filling.

---

## The 8 plans (the recap you asked for)

The spec was decomposed into 8 implementation plans, all living in
[`docs/superpowers/plans/`](superpowers/plans/). They form a dependency chain: **one refactor unlocks
1D → the registry plumbing → five parallel solver-build plans → one box-generation + screen plan.**

| # | Plan | What it delivered | Solvers added |
|---|---|---|---|
| 1 | **`common/` dimension-agnostic refactor** | Made `ladder`, `metrics`, `io`, `visualize` accept **1D** fields as well as 2D, by branching each module on `field.ndim` rather than rewriting. 2D paths preserved byte-for-byte (golden-fixture regression test); the only new code is a 1D one-pager (line plots vs. heatmaps). **This is what unlocked every 1D candidate.** | — (infrastructure) |
| 2 | **Solver-registration plumbing + parabolic spectral** | Built the plugin registry (`generate._MODULES`) + `common/spectral.py` (`spectral_interp`, `neg_laplacian_symbol`) that every later solver clones, and added the parabolic reaction-diffusion fronts. | Allen–Cahn, Fisher–KPP |
| 3 | **Single-field spectral** | Generalized the validated KS solver to **1D** (the textbook smooth control) and added a characteristic-$k$ pattern former. | 1D KS, Swift–Hohenberg |
| 4 | **Dispersive spectral** | Dispersive high-$k$ via oscillation, not jumps: KdV (integrating-factor RK4) and NLS (defocusing/sub-critical split-step, to avoid collapse). | KdV, NLS |
| 5 | **Distinct-paradigm spectral** | Three distinct sharpness mechanisms: kinks/breathers, multi-front spots/stripes, and a periodic sharp lattice (stiff 6th-order). Each carries an *exact* correctness check (e.g. Klein–Gordon dispersion, Gray–Scott fixed point, PFC mass conservation). | sine-Gordon, Gray–Scott, phase-field crystal |
| 6 | **PyClaw/WENO shock solvers** | The genuine-discontinuity branch. **Spectral solvers cannot produce true shocks** (only viscous/smoothed ones — APEBench authors' own disclaimer), so all shock candidates *must* use the finite-volume/WENO path. | Burgers, Sod, shallow-water |
| 7 | **Special solvers** | The two "special but tractable" picks: a **steady-state** high-$k$ Helmholtz (sparse direct solve — dodges the chaos & snapshot-time criteria entirely) and the porous-medium equation (degenerate diffusion with a compact-support sharp edge, positivity-preserving FD). | high-$k$ Helmholtz, porous-medium |
| 8 | **Box generation + auto-screen + survivor menu** | Built `common/screen.py` (energy-above-cutoff, sharpness coordinate $s$, LF–HF high-$k$ gap, dimension-matched KS floor) and the report builder, then **ran the sample batch on the box** and emitted the ranked menu. | — (the screen + the run) |

Every solver was built **light** (locally, in `.venv`, with structural unit tests — shape,
finiteness, determinism, ladder-IC consistency, exact-solution checks). Per the compute policy,
**physics validation — is it actually sharp? does LF track HF? — was deferred to the box sample
round**, which is Plan 8.

---

## What got built: 16 solvers → 24 sample datasets

The portfolio went from 3 to **16 solver modules**:

```
allen_cahn   burgers   cahn_hilliard   euler   fisher_kpp   gray_scott
helmholtz    kdv       kuramoto_sivashinsky    nls           phase_field_crystal
porous_medium    shallow_water    sine_gordon    sod    swift_hohenberg
```

Because several solvers run in **both 1D and 2D**, these 16 modules expose **24 sample datasets**
(e.g. `burgers_1d` + `burgers_2d`, `allen_cahn_1d` + `allen_cahn_2d`, `kuramoto_sivashinsky_1d` +
the original 2D, etc.).

---

## How the 72 figures were generated

Each of the 24 datasets was sampled **3 times**, and each sample produced **one review one-pager** →
**24 × 3 = 72 figures**, under
[`mffp_sharp/data/sample/figures/`](../mffp_sharp/data/sample/figures/) (named
`<dataset>_sample{0,1,2}.png`). The pipeline per sample, all driven by `generate.py`:

1. **Sample the condition vector.** `sample_<pde>_configs(...)` draws a config (Latin-hypercube /
   per-PDE recipe) — the complete, small ($\le\sim10$ scalars) vector that, with the solver and
   snapshot time $T$, fully determines the field.
2. **Solve the fidelity ladder *consistently*.** The solver builds **one continuous initial
   condition**, spectrally interpolates it onto each grid in the dyadic ladder
   ($32^2/64^2/128^2$ for 2D; the deck's $64/128/256$ for 1D), and **solves independently at each
   level**. The coarse solve is a *real* coarse solve — **never a downsampled or noised HF field**
   (the single most important methodology rule; downsampling injects Gibbs/aliasing artifacts and
   invalidates the benchmark).
3. **Align onto the HF grid.** Every level is interpolated up to HF so residuals
   $u_{HF}-u_{LF}^{\uparrow}$ are well-defined.
4. **Compute the metric panel** (`common/metrics.py`): not rel-L2 alone (it averages over the smooth
   bulk and hides blur in the thin sharp region) but the panel — $L^\infty$, Wasserstein-1,
   interface/shock position, high-wavenumber band, conservation, SSIM (1D-adapted or skipped where it
   loses meaning).
5. **Emit the one-pager** (`common/visualize.py`): **LF / IF / HF** fields (never "MF"), the residual
   each coarse grid makes vs. HF, and the radial power spectrum with its decay descriptor. 2D = heatmaps;
   1D = line plots (the new code from Plan 1).
6. **Write HDF5 + summary.** Fields go to git-ignored HDF5 on the box; only the small
   `sample_summary.json` + the PNG one-pagers come back to the Mac for review.

Then **Plan 8's auto-screen** post-processed the saved HDF5s into `screen_report.json` — the ranking
that turns 72 raw one-pagers into a *menu*.

---

## The auto-screen results (the menu)

The screen computes, per dataset, the spec's **energy-above-cutoff**
$f(k_c)=\big(\sum_{|k|>k_c}|\hat u|^2\big)/\big(\sum_{|k|>0}|\hat u|^2\big)$ swept over $k_c\in\{12,16,20,24\}$, then derives:

- **Floor (the only hard gate):** a candidate is dropped only if it is **smoother than the
  dimension-matched KS control** ($f_{\text{cand}}<f_{\text{KS}}$). This is the
  "CH-first-$\varepsilon$ was smoother than the control" catch, stated robustly.
- **Sharpness coordinate $s=(f_{\text{cand}}-f_{\text{KS}})/(f_{\text{Euler}}-f_{\text{KS}})$:** where
  the candidate sits on the smooth→sharp axis, with KS$\to 0$ and 2D Euler$\to 1$ as anchors. This is
  exactly the project's x-axis — "sharp enough" becomes a *coordinate*, not a pass/fail.
- **LF–HF high-$k$ gap:** the high-$k$ content the cheap LF carries that HF-finetuning misses — the
  quantity the whole MF-fusion hypothesis rides on.

**⚠ Read before the tables — $s$ is NOT comparable across dimensions.** The screen normalizes *every*
candidate's $s$ by the **2D Euler** anchor (see "One screen fix to flag" below). For **2D** candidates
both anchors (KS, Euler) are 2D, so $s$ is **decision-grade**. For **1D** candidates the numerator is
dimension-matched (1D KS) but the denominator is the *2D* Euler — so the 1D magnitudes are inflated
artifacts (this is why a naïve single ranking would put `nls_1d`/`kdv_1d` on top). The 1D $s$ is
therefore valid **only as a within-1D ordering, never as a magnitude and never against the 2D table.**
So the menu is split by dimension, and the cross-dimension fix (a 1D sharp anchor) is an action item
below. Everything is at the provisional cutoff $k_c=16$ (until FNO's $k_{\max}$ is known).

**2D candidates — ranked by $s$ at $k_c=16$ (decision-grade):**

| Dataset | $s$ | floor | LF–HF gap |
|---|---|---|---|
| sine_gordon_2d | 7.67 | PASS | 0.71 |
| fisher_kpp_2d | 5.90 | PASS | 0.67 |
| gray_scott_2d | 5.38 | PASS | 0.18 |
| burgers_2d | 1.10 | PASS | 0.45 |
| **euler** (sharp anchor) | 1.00 | PASS | 0.29 |
| porous_medium_2d | 0.21 | PASS | 0.14 |
| allen_cahn_2d | 0.04 | PASS | 0.13 |
| phase_field_crystal_2d | 0.03 | PASS | 0.09 |
| helmholtz_2d | 0.02 | PASS | 0.00 |
| cahn_hilliard | 0.02 | PASS | 0.01 |
| shallow_water_2d | 0.01 | PASS | 0.00 |
| swift_hohenberg_2d | 0.00 | PASS | 0.01 |
| **kuramoto_sivashinsky** (smooth anchor) | 0.00 | PASS | 0.01 |

**1D candidates — ordered by within-1D sharpness at $k_c=16$ (the $s^{*}$ column is 2D-anchored, ordering only):**

| Dataset | $s^{*}$ | floor | LF–HF gap |
|---|---|---|---|
| nls_1d | 14.95 | PASS | 0.66 |
| kdv_1d | 9.03 | PASS | 0.02 |
| burgers_1d | 3.01 | PASS | 0.82 |
| sod_1d | 1.08 | PASS | 0.04 |
| fisher_kpp_1d | 0.46 | PASS | 0.48 |
| **kuramoto_sivashinsky_1d** (smooth anchor) | 0.00 | PASS | 0.04 |
| allen_cahn_1d | 0.00 | **fail** | 0.26 |
| porous_medium_1d | 0.00 | **fail** | 0.12 |
| sine_gordon_1d | 0.00 | **fail** | 0.45 |
| shallow_water_1d | 0.00 | **fail** | 0.00 |
| swift_hohenberg_1d | 0.00 | **fail** | nan |

*$s^{*}$ = the raw `screen_report.json` value, divided by the 2D Euler anchor. **Magnitude is not
decision-grade** — use it only to rank 1D candidates against each other, never against the 2D table or
the $s=1$ Euler anchor. Re-running with a 1D sharp anchor (Sod / 1D Burgers shock) makes these numbers
meaningful (action item below).*

**Read carefully — these are sample-round signals, not final verdicts:**

- **19 of 24 clear the floor** at $k_c=16$. The 5 floor-failures are all **1D** variants
  (`allen_cahn_1d`, `porous_medium_1d`, `sine_gordon_1d`, `shallow_water_1d`, `swift_hohenberg_1d`)
  whose sampled regime came out *smoother than the 1D KS control* — they should either be retuned
  (the provisional `(TBD-box)` parameters) or dropped. Their one-pagers are kept for the record.
- **The anchors validate (within each dimension).** Euler sits at $s=1.00$ and 2D KS at $s=0.00$ by
  construction, and the 2D candidates spread sensibly between and beyond them — the sanity check that
  the 2D coordinate is meaningful. The 1D anchors aren't both present (no 1D Euler), which is exactly
  the gap the action item fixes.
- **$s>1$ is fine *within the 2D table*.** It means "carries *more* high-$k$ energy than the 2D Euler
  shock at this cutoff" — true for the sharp 2D fronts (sine-Gordon, Fisher–KPP, Gray–Scott). It does
  **not** automatically make them better picks; the LF–HF gap and a visual one-pager check matter just
  as much. (The large *1D* $s^{*}$ values are the anchoring artifact, not evidence of extreme sharpness.)
- **The cutoff is provisional.** All of this is reported at $k_c=16$; the full $f(k_c)$ curve is in
  `screen_report.json`. The moment you give us FNO's $k_{\max}$, the tables re-rank to the
  decision-relevant cutoff (and if $k_{\max}\ge$ HF Nyquist = 64, the premise is untestable at $128^2$
  and we need a finer HF grid — that's the built-in sanity check).

---

## What's open for you (Nicholas)

### The decision that drives everything else: centerpiece + dimension

The portfolio's dimension is **not** a free parameter to set independently — it is a *consequence* of
what we make the centerpiece. To be explicit about a confusion worth heading off: the benchmark's
"FNO-finetuning beats MF fusion" result was **not** a 2D-only finding — the deck's suite spans both
1D (`allen_cahn_gen`, `burgers_gen`, `burgers_param_gen`) and 2D, and every operator (FNO included)
has a 1D form. So nothing in the *benchmark* forces 2D. What forces the dimension is the **centerpiece
study**:

- **Option A — centerpiece = the 2D Cahn–Hilliard $\varepsilon$-sweep transition study** (the strong
  framing from `design-rationale.md` §7: tune sharpness *continuously* with one knob, hold physics
  fixed, *map the crossover* rather than show discrete points). CH-as-locked is 2D, so this pins the
  whole axis to **2D** — which in turn means the discrete supporting datasets that share that axis
  (the sharp bracket + the control) should also be **2D**, with **2D KS** as the dimension-matched
  control. **Cost:** `design-rationale.md` §7 itself concluded the CH study needs a **$2\times$ ladder
  ($128/256$)** *and* averaging over **many ICs** (the LF divergence is erratic) — a dense
  $\varepsilon$-grid × many ICs at $128/256$ is heavy box compute.

- **Option B — centerpiece = a cheaper 1D transition vehicle** (a 1D CH $\varepsilon$-sweep, or
  another 1D knob). 1D makes the fine sweep + many-IC averaging nearly free. **Risk:** a 1D CH field is
  information-poor (≈ one width parameter + a few front locations), so FNO may reconstruct it well even
  when sharp — the MF-vs-finetune **crossover may not appear at all in 1D**. *(This last point is an
  expectation, not a measured result — it is exactly what the pilot would settle.)* This is a
  *different, weaker/simpler test*, not a free dimension swap of the same study.

**Net:** pick the centerpiece first; the dimension and the rest of the portfolio follow. If A, we go
2D throughout and the cross-dimension anchor wrinkle (below) is moot. If B, we commit to a 1D axis and
accept the simpler-physics risk.

### Smaller open items (downstream of the call above)

1. **Pick the menu.** Which of the 19 floor-passing datasets go to full counts? The one-pagers +
   this ranking are the input; mechanism diversity (shock / interface / dispersive / pattern /
   control) is tagged in the spec if you want spread rather than just top-$s$.
2. **The 5 floor-failures.** Retune their sampled ranges, or drop them? (All 1D, all currently
   smoother than the 1D control — a *tuning* miss, not a verdict on 1D; several other 1D cases —
   `burgers_1d`, `sod_1d`, `fisher_kpp_1d` — passed cleanly.)
3. **FNO's $k_{\max}$** — sets the decision-relevant cutoff and re-ranks the whole table.
4. **Full-count sample sizes / ranges** per chosen dataset.

### One screen fix to flag

The sharpness coordinate $s$ is currently **not comparable across dimensions**: `screen_samples.py`
divides *every* candidate — 1D included — by the *single 2D Euler* anchor curve. That is why the 1D
rows read implausibly high ($s_{\text{nls\_1d}}=14.95$, $s_{\text{kdv\_1d}}=9.03$); it's a 1D numerator
over a 2D denominator, not evidence they out-sharp the Euler shock. The **floor is correctly
dimension-matched** (1D-vs-1D-KS, 2D-vs-2D-KS) and is the trustworthy signal. Before quoting $s$ across
dimensions, anchor 1D against a 1D sharp reference (Sod / 1D Burgers shock). *(Within a single
dimension — e.g. an all-2D portfolio under Option A — $s$ is already fine as-is.)*

### Name-collisions with the deck — regime, not duplicate (verify before full counts)

Two candidates share a *name* with a dataset already in the benchmark's (mostly-smooth) suite:
**Burgers** (`burgers_gen`, `burgers_param_gen`) and **Allen–Cahn** (`allen_cahn_gen`). This is **not**
accidental re-generation of smooth data — in both cases we deliberately built the *sharp regime* of the
same equation:

- **Burgers.** `pdes/burgers.py` solves the **inviscid** equation $u_t+(u^2/2)_x=0$ (no diffusion) via
  PyClaw — a smooth sinusoid that **steepens into a genuine shock** by $t=0.3$; HF = WENO/SharpClaw
  (sharp shock), LF = 1st-order Godunov (smeared shock). The screen confirms it landed sharp
  (`burgers_1d` $s=3.01$, `burgers_2d` $s=1.10$; LF–HF gaps 0.82 / 0.45). The deck's `burgers_gen`, by
  contrast, is in the *smooth* suite — for Burgers that almost always means the **viscous** equation
  $u_t+(u^2/2)_x=\nu u_{xx}$ at a $\nu$/time with no shock. **Same equation, opposite end of the
  sharpness axis** — which makes our Burgers potentially the cleanest *controlled contrast* in the
  portfolio (hold the equation fixed, move only viscosity into the shock regime — the CH-$\varepsilon$
  idea with viscosity as the knob). The spec tags it **"redundant-shock"** precisely because its
  *mechanism* (a scalar jump) duplicates Euler/Sod; its value is the contrast, never novelty.

- **Allen–Cahn** carries the same caveat (sharpness set by the interface-width parameter; the deck's
  version may sit at a smooth operating point).

**Action item (box):** confirm the deck's `burgers_gen` / `allen_cahn_gen` operating points (viscosity,
interface width, snapshot time) **before either goes to full counts.** If the deck's version is smooth
→ ours is a valuable controlled contrast; if the deck's version is *already* sharp → ours is a
near-duplicate (of it, and of Euler/Sod) → demote or drop. *Caveat: the deck lives in the separate
MFFP codebase, not this repo, so this regime check cannot be done from here — it is a box task.*

No full generation runs until you sign off — that gate is intact.

---

### Pointers
- Spec: [docs/superpowers/specs/2026-06-17-sharp-pde-portfolio-expansion-design.md](superpowers/specs/2026-06-17-sharp-pde-portfolio-expansion-design.md)
- 8 plans: [docs/superpowers/plans/](superpowers/plans/)
- Generation recipes (literature): [docs/research/2026-06-17-hf-pde-generation-recipes.md](research/2026-06-17-hf-pde-generation-recipes.md)
- 72 one-pagers: `mffp_sharp/data/sample/figures/*.png`
- Machine-readable: `mffp_sharp/data/sample/sample_summary.json`, `mffp_sharp/data/sample/screen_report.json`
</content>
</invoke>
