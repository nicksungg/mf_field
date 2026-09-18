# Design: expanding the sharp-PDE portfolio — wide menu → build all feasible → sample-gate → Nicholas picks

*Status: draft for review (Eloise → Nicholas). Date: 2026-06-17.*

## Context — why this change
The MFFP benchmark's headline result ("HF-finetuning beats fancier multi-fidelity fusion") was
measured on a **mostly-smooth** dataset suite. We are adding **sharp / high-frequency** datasets
along a smooth→sharp axis to test whether that conclusion survives where spectral truncation /
spectral bias actually bites. The **locked** portfolio today is three 2D PDEs: Euler Riemann
(shock) · Cahn–Hilliard (tunable interface) · Kuramoto–Sivashinsky (smooth control).

This design answers "can we find *more* high-frequency PDEs?" Rather than pre-committing to one or
two extra picks, we **build the maximal feasible candidate set (1D + 2D), generate a small sample
batch + one-pager for each, auto-screen out the ones that empirically fail, and present Nicholas the
surviving menu** so he chooses what goes to full counts. This widens — but does not skip — the
existing "sample → Nicholas approves → full counts" gate.

Two framing facts that shape the criteria:

- **The premise is architecture-neutral.** The deck compares ~8 model *families* (3 FNO variants,
  2 attention/transolver operators, baselines `mfrnp` / `mf_deeponet` / `d_mfd`) across **15
  datasets** — so "sharp" cannot mean literally "energy above FNO's $k_{\max}$." We define sharp by
  the **measured HF spectral decay slope**; spectral bias degrades *all* these operators at high
  $k$, FNO just most explicitly.
- **1D is allowed.** The deck already ships 1D datasets (`allen_cahn_gen`, `burgers_gen`,
  `burgers_param_gen` at 64/128/256), so 1D is native to the benchmark format — but our `common/`
  infrastructure is currently 2D-hardcoded and needs a dimension-agnostic refactor first.
- **Replicate published recipes, don't invent thresholds** (per Nicholas). A 2026-06-17 literature
  survey ([docs/research/2026-06-17-hf-pde-generation-recipes.md](../../research/2026-06-17-hf-pde-generation-recipes.md))
  extracted verified generation recipes for our candidates and supports a **scoped gap: no surveyed
  benchmark is both high-frequency AND multi-fidelity-via-independent-coarse-solves.** The properties
  appear separately — genuinely-coarse-solve MF datasets exist but are *smooth* (the MF-surrogate
  subfield, incl. the deck's own `ifc_*`/`*_local`); high-frequency datasets are single-fidelity or
  expose fidelity only as downsampling (verified for PDEBench's `reduced_resolution` knob). *Not* a
  universal "all MF = downsampling" claim. The second pass (BLASTNet/BubbleML/CFDBench/JHTDB) is now
  complete and **all four are verified to confirm the scoped gap** (CFDBench smooth+post-hoc-interp;
  JHTDB & BubbleML high-freq but resolution is post-hoc DNS access; BLASTNet high-freq but low-res =
  Favre-filtered DNS — and its authors *explicitly state* that an independent-coarse-solve↔DNS pair is
  infeasible for chaotic turbulence, App. E.1.6, which is exactly our filter-2). Only residual hole is
  The Well MHD (refuted/unresolved). That intersection gap is the contribution; the recipes below pin
  regimes so
  "sharp enough" is matched to
  precedent, and the spectral metrics become *verification that our data matches the source*, not an
  invented bar. **Note:** the survey could *not* confirm "FNO/spectral fails to win on sharp physics"
  (that claim was refuted on The Well) — so the open modeling question stays genuinely open; we are
  building the datasets to *test* it, not assuming the answer.

## Selection criteria — what gates the build set vs. what is just a label
Because Nicholas chooses at the end, **mechanism-distinctness is metadata, not a cut**. A candidate
enters the build set if it can pass criteria 1–5; redundancy (criterion 6) is recorded as a tag.

1. **Genuinely sharp when measured** — see the "Sharpness screen" section below. In short: the HF
   spectral slope vs. a *dimension-matched* smooth baseline is only a **necessary floor** (a
   candidate smoother than the smooth control is disqualified); the signals that actually predict
   whether spectral bias bites are **energy-above-cutoff** (swept over plausible $k_c$) and the
   **LF–HF high-$k$ gap**. Candidates are *ranked* on these, not hard-dropped on slope alone.
   *Enforced empirically by the sample round.*
2. **LF faithfully blurs, not diverges** — LF must be a real coarse *consistent* solve that tracks
   HF, never downsampled/noised HF. Killed by chaos / sensitive dependence (the KS-at-$T{=}50$
   confound) or by under-resolution that produces a *qualitatively different* field (the CH
   operating-point tension). *Enforced empirically by the bottom-rung check.*
3. **Complete, small condition vector** ($\le \sim 10$ scalars; solver + vector + snapshot $T$ fully
   determine the field). Killed by path-dependence / history (e.g. fracture).
4. **One field at a fixed $T$ fits the template** — no time-series, integral, or bifurcation output.
5. **Solver practical on the box** — stable across the whole sampled range, runs on the single 4090.
6. **Distinct failure mechanism** (Euler = localized jump, CH = thin interface, KS = smooth) —
   *label only*. Redundant picks are still built and shown, just tagged.

**Plugin contract** (`generate.py`): a PDE module provides
`generate_sample(spec, resolutions, hf_res, output_time, **kwargs) -> ({res: field}, cond_vec, labels)`
plus a `sample_<pde>_configs(...)` in `sampling.py`. Proven solver families to clone: **Fourier
spectral** (Cahn–Hilliard, KS) and **PyClaw/WENO** (Euler).

## Prerequisite — `common/` dimension-agnostic refactor ($\approx 470$ LoC, unlocks all 1D)
Not a rewrite: branch four modules on `field.ndim`. The only genuinely new code is the 1D one-pager
(line plots vs. heatmaps). Risk concentrates in `visualize` (new layout) and `metrics` (SSIM /
interface-position lose their natural 2D meaning → 1D analogue or marked N/A).

| Module | 2D-locked today | Change | ~LoC |
|---|---|---|---|
| `common/ladder.py` | asserts `(res,res)`; 2D unit-grid interp | relax assert; 1D → `np.interp`, 2D → existing `RegularGridInterpolator` | 80 |
| `common/metrics.py` | `spectral_band`/radial use `fft2`; ssim, interface 2D | branch `fft` ↔ `fft2`; radial $|k|$ in 1D; ssim 1D-or-skip | 120 |
| `common/io.py` | HDF5 layout hard-codes `[N,R,R]` | store `ndim`/`shape` attr; write `[N, *spatial]`; read generically | 80 |
| `common/visualize.py` | `one_pager` uses `imshow` + `fft2` | 1D one-pager line plots; shared spectrum code | 150 |
| `generate.py` / `sampling.py` | thread `ndim` through | minor | 40 |

## The large menu (≈30 candidates, by sharpness mechanism)

**A. True discontinuities — hyperbolic conservation laws** (slope $\approx -1 \ldots -3$):
A1 Burgers (1D/2D) · A2 Euler/Sod shock tube (1D) · **A3 2D Euler Riemann — IN PORTFOLIO** ·
A4 Shallow water / dam-break (1D/2D) · A5 Buckley–Leverett (1D/2D) · A6 Traffic/LWR (1D) ·
A7 Detonation / compressible NS (1D/2D) · A8 Ideal MHD (1D/2D).

**B. Sharp interfaces / pattern fronts — phase-field & reaction-diffusion** (tunable):
**B1 2D Cahn–Hilliard — IN PORTFOLIO** · B2 Allen–Cahn (1D/2D) · B3 Fisher–KPP (1D/2D) ·
B4 Gray–Scott (2D) · B5 Swift–Hohenberg (1D/2D) · B6 Phase-field crystal (2D) ·
B7 Porous-medium eq. degenerate (1D/2D) · B8 Stefan / phase change (1D/2D).

**C. Dispersive / oscillatory — high-$k$ via oscillation, not jumps:**
C1 High-$k$ Helmholtz (2D, steady) · C2 NLS (1D/2D) · C3 KdV / KP-II (1D/2D) ·
C4 Sine-Gordon (1D/2D) · C5 Klein–Gordon / forced wave (1D/2D).

**D. Singularities / cracks / derived-field fronts:**
D1 Phase-field fracture (2D) · D2 Eikonal (2D) · D3 Hamilton–Jacobi / level-set (2D).

**E. Turbulence / chaotic with sharp structures:**
E1 2D Navier–Stokes vorticity · E2 2D incompressible Euler ·
**E3 Kuramoto–Sivashinsky — IN PORTFOLIO (1D is the textbook fix).**

## Build set — generate samples for all of these (pass criteria 1–5; tagged for 6)

### Spectral template (clone CH/KS — cheapest, $\sim$80–150 LoC each)
| ID | PDE | Dim | Sharpness mechanism | Tag |
|---|---|---|---|---|
| C3 | KdV / KP-II | 1D / 2D | dispersive soliton trains | distinct (dispersion) |
| C2 | NLS (**defocusing / sub-critical** to avoid collapse) | 1D / 2D | oscillatory wavepackets | distinct |
| C4 | Sine-Gordon | 1D / 2D | kinks + breathers | distinct |
| B4 | Gray–Scott | 2D | many sharp spots / stripes | distinct (multi-front) |
| B5 | Swift–Hohenberg | 1D / 2D | characteristic-$k$ banding | distinct (pattern) |
| B6 | Phase-field crystal | 2D | periodic sharp lattice (stiff 6th order) | distinct |
| B2 | Allen–Cahn | 1D / 2D | single interface | near-CH |
| B3 | Fisher–KPP | 1D / 2D | sharp traveling front | semi-distinct |
| E3 | **1D KS** | 1D | smooth control (textbook) | resolves "2D-KS non-standard" knob |

### PyClaw/WENO template (clone Euler — $\sim$80–100 LoC each)
| ID | PDE | Dim | Mechanism | Tag |
|---|---|---|---|---|
| A1 | Burgers shock | 1D / 2D | scalar jump | redundant-shock |
| A2 | 1D Euler / Sod | 1D | jump, canonical | redundant-shock |
| A4 | Shallow water (dam break, bores) | 1D / 2D | jump + wet/dry front | semi-distinct |
| A5 | Buckley–Leverett | 1D / 2D | non-convex-flux saturation front | semi-distinct |

### Special but tractable on the box (moderate new code)
| ID | PDE | Dim | Mechanism | Note |
|---|---|---|---|---|
| C1 | High-$k$ Helmholtz | 2D | sustained oscillation, **steady-state** | sparse direct solve ($\sim$120 LoC); dodges criteria 2 & 4 entirely — strongest *distinct* pick |
| B7 | Porous-medium eq. | 1D / 2D | compact-support sharp edge | positivity-preserving FD |

### Defer this round (fail criterion 3 or 5)
D1 fracture (path-dependent → FEniCSx; monotone-loading restriction = round 2) · A7 detonation ·
A8 MHD · D3 Hamilton–Jacobi · B8 Stefan · D2 Eikonal.

### Drop (fail criterion 1 or 2 inherently)
E1 2D Navier–Stokes & E2 2D incompressible Euler — chaotic divergence (criterion 2) **and** a
fast-decaying spectrum that makes "sharp" borderline (criterion 1). (1D scalar shocks A1/A2/A6 are
*kept* as redundant-tagged, not dropped, since Nicholas chooses.)

**Build-set size:** $\approx 16$ PDEs $\times$ {1D and/or 2D variants} $\approx$ **20–24 sample datasets.**

### Generation recipes (literature-grounded — see the research doc for citations)
Parameter regimes now follow *published* recipes rather than provisional guesses:
- **Hard solver constraint (verified):** spectral solvers **cannot** produce genuine shocks — only
  viscous/smoothed versions (APEBench authors' own disclaimer). So **all shock candidates (Euler,
  Sod, Burgers-shock, shallow-water) MUST use the PyClaw/FV branch**, never the spectral template.
  This is no longer a preference — it's a correctness requirement.
- **Euler Riemann:** clone The Well `euler_multi_quadrants` (Clawpack/AMRClaw, multi-quadrant
  piecewise-constant Riemann IC, γ ∈ {1.13…1.76}); sample ICs from the **Schulz-Rinne 19-config**
  benchmark → condition vector = config-id + γ + BC + T.
- **Shallow water:** clone PDEBench `gen_radial_dam_break.py` (PyClaw `shallow_roe_with_efix_2D`,
  inner_height=2.0, grav=1.0, dam_radius ~ U[0.3,0.7], Neumann BC).
- **Gray–Scott:** The Well recipe — ETDRK4, periodic, $\delta_A{=}2e{-}5,\ \delta_B{=}1e{-}5$, the
  **6 Pearson (f,k) regimes**; condition vector = (f,k)+IC type.
- **Dispersive / pattern / control (KdV, KS, Allen–Cahn, Swift–Hohenberg, NLS):** validate against
  **Exponax/APEBench** ETDRK steppers (off-the-shelf, periodic, normalized — adapt to our domain &
  ladder); our CH/KS spectral solvers already match this class.
- **Cahn–Hilliard:** E-UNO form $\mu=\lambda(\Phi(\Phi^2-1)/\varepsilon-\varepsilon\Delta^2\Phi)$,
  mobility=1. **⚠ The canonical sharpness $\varepsilon$ + its grid-scaling is still unpinned** (the
  source uses two length params) — must be sourced before CH full generation (see open dependencies).

## Workflow — built to parallelize, heavy compute on the box
Compute policy: *light* work (edit, byte-compile, 1–2-sample smoke, figures) → either machine;
*heavy* work (full sample-batch solves, 2D $128^2$ runs) → **box only**
(`ssh eloise@10.80.6.224`, 4090). Data stays on the box (git-ignored); only
`sample_summary.json` + one-pager PNGs come back for review.

| Phase | Work | Parallelism | Where |
|---|---|---|---|
| 0 | Persist this design + brainstorming review gate | serial | Mac |
| 1 | **`common/` 1D refactor** (modules largely independent) | **4 parallel agents** (one per module) + 1 integration pass (`generate.py` threading) | Mac (light) |
| 1b | No-regression: existing 2D Euler/CH/KS byte-compile + 1–2-sample smoke | serial gate after Phase 1 | Mac (light) |
| 2 | **Solver modules** (~16) — independent once Phase 1 lands | **fan out by template** (spectral / PyClaw / special); each agent owns several `pdes/<name>.py` + `sample_<name>_configs` | Mac (light) |
| 3 | **Sample generation** (~20–24 batches, ~8–16 samples each) — embarrassingly parallel across PDEs | **box batch-runner across cores**, tiered by cost: cheap 1D spectral many-concurrent; 2D $128^2$ fewer-concurrent; GPU for any CUDA solver, else saturate CPU/FFT cores | **box (HEAVY)** |
| 4 | **Auto-screen + one-pagers** — per-candidate independent | parallel | Mac (light; small summaries/PNGs back) |
| 5 | Synthesize survivor menu for Nicholas | serial | Mac |

**Dependency edges (the only non-parallel parts):** Phase 2 needs the dimension-agnostic API from
Phase 1; Phase 3 needs the solver modules from Phase 2; everything *within* a phase fans out. The
long pole is Phase 3 (box compute) — minimize wall-clock by running the cheap 1D batch and the heavy
2D-$128^2$ batch on **separate core pools concurrently**, not in sequence.

### Sharpness screen — what "sharp enough" actually means
The single metric is **energy-above-cutoff** $f(k_c)=\big(\sum_{|k|>k_c}|\hat u|^2\big)/\big(\sum_{|k|>0}|\hat u|^2\big)$
(DC excluded), computed once per HF field as the complementary cumulative radial spectrum so any
$k_c$ is read off one curve. It is **form-agnostic** — correct whether the spectrum is a power law,
a knee, an exponential, or a spectral peak — which most candidate spectra are *not* simple power
laws (shocks ≈ power-law; finite-width interfaces have a knee at $k\sim1/\varepsilon$; KS/solitons
decay exponentially; Swift–Hohenberg/PFC are spectral *peaks*). **Spectral *slope* is demoted to a
descriptor** (reported only for genuine power-law cases, e.g. Euler, + a one-pager annotation);
it is never the gate. Two flavors of $f$:
- `f_radial(k_c)` (disk) — geometry-neutral high-$k$ content, the architecture-agnostic proxy.
- `f_box(k_max)` (per-axis box $\{|n_x|,|n_y|\le k_{\max}\}$) — *exactly* what FNO's truncation
  discards each layer; the most decision-relevant version once $k_{\max}$ is known.

**Determining the cutoff $k_c$ — not ours to invent; the model sets it.** The principled $k_c$ is
**FNO's $k_{\max}$** (the line between energy FNO keeps vs. discards). Bounds regardless of model:
**above** the energy-containing/forcing low modes, **below** the HF Nyquist ($=64$ at $128^2$), and
**below** the numerical-dissipation range (where the solver, not physics, damps modes). **Sanity
check the moment we have $k_{\max}$:** if $k_{\max}\ge$ HF Nyquist, FNO loses nothing and the premise
is untestable at $128^2$ → need a finer HF grid. Until $k_{\max}$ arrives, report the whole $f(k_c)$
curve over $k_c\in\{12,16,20,24\}$; Nicholas's number just selects a point on it.

**Determining the decision level on $f$ — no magic constant; anchors + a pilot.**
1. **Floor (the only binary, needs no constant):** drop a candidate only if $f_{\text{cand}}(k_c)<
   f_{\text{smooth-control}}(k_c)$ measured identically and *dimension-matched* (1D vs 1D KS, 2D vs
   2D KS). "Outside the smooth population the benchmark conclusion was measured on." This is the
   CH-first-$\varepsilon$ catch, stated robustly.
2. **Sharpness coordinate (turns the threshold into the dose-response axis):** we control two
   anchors — KS (smoothest) and Euler shock (sharpest). Place each candidate at
   $s=(f_{\text{cand}}-f_{\text{KS}})/(f_{\text{Euler}}-f_{\text{KS}})\in[0,1]$. "Sharp enough" stops
   being a gate and becomes *where on the smooth→sharp axis* a candidate sits — which is exactly the
   x-axis the project is built around.
3. **The rigorous threshold is downstream (discovered, not assumed):** the operational "sharp
   enough" is where HF-finetuning measurably degrades / MF fusion measurably helps. Calibrate with a
   small pilot — FNO-finetune on 2–3 datasets spanning a range of $s$, find the $s$ at which rel-L2 /
   high-$k$ error breaks — folding into the existing "map the transition" plan.
4. **LF–HF high-$k$ gap:** compute the same $f$ on the LF field and on the residual
   $u_{HF}-u_{LF}^{\uparrow}$. MF fusion can only help where the cheap LF carries recoverable high-$k$
   content HF-finetuning misses — this gap is the quantity the whole hypothesis rides on.

Net: **don't set a hard $f$ threshold for the menu.** Gate only the floor (1); report $s$ (2) and the
$f(k_c)$ curve; let the pilot (3) + Nicholas fix the operational line.

**Stronger baseline (data-gated enhancement):** replace "KS only" with the **smooth-suite envelope**
— the measured spectra of the deck's smooth `*_gen` datasets (`burgers_gen`, `darcy_gen`,
`heat_gen`, `poisson_gen`; skip `era5`). That is the population the benchmark's conclusion was
actually measured on, so "outside its envelope, trending toward Euler" is the honest bar. Cost: the
*computation* is ~minutes (reuses `radial_spectrum`/`spectral_band`), but the **benchmark datasets
are not in this repo** — they live in the separate MFFP codebase (likely on the box). Sequencing:
use the dimension-matched KS floor now (zero data dependency); upgrade to the smooth-suite envelope
once the data is confirmed on the box, or **regenerate smooth-reference spectra from our own solvers**
(Fisher–KPP / heat-like / smooth Burgers / Poisson) as a faithful-proxy fallback if it is not.

### Auto-screen (the pre-filter before Nicholas), per candidate
- **Sharpness:** apply the screen above — auto-drop only floor failures (1); otherwise **rank** by
  sharpness coordinate $s$ + LF–HF gap (never hard-drop on slope or a hand-picked $f$ threshold).
- **Bottom rung:** LF measurably blurrier than HF **and** still tracking (rel-L2 below the
  CH-breakdown regime, not $> 1$).
- **Reproducibility:** condition vector + solver + $T$ reproduce the field on re-solve.
- Emit a one-line report per candidate (floor PASS/FAIL, sharpness coordinate $s$, $f(k_c)$ sweep,
  LF–HF gap, optional slope-for-power-law-cases, bottom-rung status); drop only floor / bottom-rung /
  repro failures (keep their one-pagers for the record).

Then **hand Nicholas the ranked survivors** — a menu of one-pagers with mechanism tags + the spectral
signals above; he picks which go to full counts.

## Critical files
- Refactor: `mffp_sharp/src/mffp_sharp/common/{ladder,metrics,io,visualize}.py`, `generate.py`.
- New solvers: `mffp_sharp/src/mffp_sharp/pdes/<name>.py` (clone `cahn_hilliard.py` /
  `kuramoto_sivashinsky.py` for spectral; `euler.py` for PyClaw).
- Sampling: `mffp_sharp/src/mffp_sharp/common/sampling.py` (add `sample_<name>_configs`).
- Config: `mffp_sharp/configs/sample.yaml` (per-PDE block: sampling, `output_time`, ranges flagged TBD).
- Screen: extend `scripts/run_sample.sh` + the `sample_summary.json` bottom-rung report.

## Open dependencies / risks
- **FNO $k_{\max}$ is unknown** → the absolute "sharp enough" threshold is not pinned. Handled by
  the energy-above-cutoff *sweep* ($k_c \in \{12,16,20,24\}$); it collapses to one value once Nicholas
  provides $k_{\max}$. (Same blocker as the CH study.)
- **Benchmark smooth-suite data is not in this repo** → it lives in the separate MFFP codebase
  (likely on the box). The stronger smooth-suite-envelope baseline is gated on confirming its
  location; until then the dimension-matched KS floor + regenerate-our-own fallback apply.
- **Some build-set candidates may fail the sample gate** — that is by design; the gate exists to
  catch the CH-first-$\varepsilon$ "smoother than the control" surprise before Nicholas sees them.
- **Condition-vector ranges per new PDE are provisional** — now anchored to published recipes (see
  the research doc) and finalized in the sample round, as for the original three.
- **Cahn–Hilliard $\varepsilon$ ↔ grid scaling — RESOLVED (focused search 2026-06-17).** The
  equilibrium profile $\Phi^{eq}=\tanh(s/\varepsilon\sqrt2)$ gives 10–90% interface width
  $W\approx 4.2\,\varepsilon$ (O(1) convention-dependent → use $W\approx 3$–$4\varepsilon$). Literature
  resolution rule: **4–5 points across $W$ to resolve (5–8 conservative)**, i.e. $h\lesssim\varepsilon$
  to $\varepsilon/2$ (matches the CLAUDE.md `h ≲ ε/2`). Points-across $=4.2\varepsilon N$ on a unit
  domain ⇒ for the **32/64/128 ladder, $\varepsilon\approx 0.012$** gives 32²≈1.6 pts (under-resolved
  ✓) / 128²≈6.4 pts (resolved ✓) — a clean bottom rung; $\varepsilon=0.018$ is too mild (32² starts
  to resolve). This **validates the existing CH range and recommends tightening to $\varepsilon\approx
  0.010$–$0.013$**; for a sharper $\varepsilon$, use the 128/256 ladder. Note: no dataset paper gives
  a clean "canonical" $\varepsilon$ (normalization-dependent; E-UNO leaves it unstated) — the
  determination is the width-rule above, not a copied constant.
- **BLASTNet / BubbleML / CFDBench / JHTDB — second pass DONE and verified; all confirm the scoped
  gap.** None is high-freq *and* independent-coarse-solve MF (CFDBench smooth + post-hoc interp; JHTDB
  & BubbleML high-freq but resolution is post-hoc DNS access; BLASTNet high-freq but low-res =
  Favre-filtered DNS). No new clonable recipe and no MF precedent to cite emerged. **Bonus:** BLASTNet
  App. E.1.6 is a citable expert statement that independent-coarse-solve↔DNS pairs are infeasible for
  chaotic turbulence — supports our filter-2 drop of 2D NS / incompressible Euler. No residual.

## Verification
Per candidate, on the box: generate the sample batch, confirm the four auto-screen checks, emit the
standard one-pager (LF/IF/HF + residual + spectrum with slope). After the `common/` refactor, run the
no-regression smoke test on the existing three 2D PDEs (Euler/CH/KS) before adding anything new.
Full-count generation only after Nicholas's approval gate.
