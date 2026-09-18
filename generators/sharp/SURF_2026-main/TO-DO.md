# TO-DO — Sharp-field PDE datasets for the MFFP benchmark

## Why (motivation)
The existing `mf_field_prediction` benchmark found that **FNO HF-finetuning beats fancier
multi-fidelity (MF) fusion** (deck slide 6; ELO leaderboard top-3 = `mf_fno_transfer*`). But
that result was measured on a **mostly-smooth** dataset suite — FNO is known to excel on smooth,
low-frequency solutions. Open question: **does that conclusion survive on high-frequency fields**
(shocks, sharp interfaces) where FNO's spectral truncation throws away the content that matters?

This round adds the **sharp-aware datasets the suite lacks**, arranged along a single
frequency-content axis — **shock → sharp interface → smooth** — so the eventual modeling
experiments can draw a dose-response curve instead of a single point. More to say in the paper,
and a real test of which MF models to use for field prediction.

## Workflow (do not skip the gate)
1. Generate a **small SAMPLE batch** of LF+HF pairs for each PDE (this doc).
2. **Nicholas reviews the sample** (approval checklist below).
3. Only after approval → regenerate at **full counts** at the agreed fidelity levels.

## Compute policy (RULE)
**Edit on either machine; run computationally intensive work on the box.**
- *Heavy → box only* (`ssh eloise@10.80.6.224`, 4090 GPU): dataset generation (sample *and* full
  runs), training, large/long/high-resolution solves.
- *Light → either machine*: editing, syntax checks, explanatory figures, a 1–2 sample smoke test.
- **Sync via git** (single source of truth = `origin/main`): pull before you edit/run, commit +
  push immediately after editing, never leave uncommitted edits when switching machines, never edit
  the same file on both before syncing. See CLAUDE.md "Dev workflow" for the full discipline.

---

## Portfolio (LOCKED) — all 2D
| PDE | Role on the axis | Solver | LF recipe (biased coarse solve) | HF recipe | Condition vector (~) |
|---|---|---|---|---|---|
| **2D Euler Riemann** | shock (sharpest) | PyClaw/Clawpack | coarse grid, 1st-order Godunov ("Classic") — diffuses shocks | fine grid, high-order WENO ("SharpClaw") | 4 quadrant states (ρ,u,v,p) → ratios, shock Mach, slip angle, γ |
| **2D Cahn–Hilliard** | sharp interface | py-pde | coarse grid **under-resolving** interface width ε | fine grid resolving ε (h ≲ ε/2) | ε, mobility, initial-composition / seed params |
| **2D Kuramoto–Sivashinsky** | smooth **control** | py-pde (custom nD operator) | coarse grid | fine grid | domain size L, IC seed / amplitude |

Three distinct PDEs, one shared methodology template, chosen so only the **frequency content**
changes across them.

---

## Shared methodology template (identical for all three)
- **Fidelity = grid resolution.** Dyadic ladder **32² → 64² → 128²** (HF = 128²), 3 levels.
- **Field = snapshot at a fixed output time T** (these PDEs evolve in time; one field per sample
  needs a defined readout time). Pick a T per PDE where the sharp feature is present and
  well-developed — Euler: shocks still sharp (not yet diffused); Cahn–Hilliard: interfaces formed
  but pre-full-coarsening; KS: past initial transient, in the chaotic-but-statistically-steady
  regime. **LF and HF must use the same physical T.** (Alternative to settle with Nicholas: make
  T part of the condition vector instead of fixing it.)
- **LF = a real coarse *consistent* solve** of the same PDE. **Never** downsampled or noised HF
  (that injects Gibbs/aliasing artifacts and defeats the purpose).
- **Interpolate every fidelity up onto the 128² HF grid** so residuals (HF − LF) are well-defined.
  Dyadic doubling makes this a clean nested interpolation (coarse points land exactly on HF points).
- **Condition vector ≤ ~8–10 scalars** per sample.
- **Output format:** HDF5/NPZ matching the deck's existing dataset layout — fields per fidelity,
  fidelity index, condition vector, and **train-split mean/std stored** for standardization.
  Also store the **raw native-grid LF** (pre-interpolation) for provenance.
- **Metric panel** (rel-L2 alone is misleading on sharp fields — it averages over the smooth bulk
  and hides blur in the thin sharp region):
  - `rel-L2` (kept, to compare against the deck) +
  - `L∞`, `Wasserstein-1`, `interface/shock-position error`,
    `high-wavenumber spectral-band error`, `conservation error`, `SSIM`.

---

## Condition-vector ranges & sampling design (TBD — set in the sample round)
Two separate decisions per PDE: **(1) schema** = which scalars (read off the physics, mostly
forced); **(2) ranges + sampling** = what values and how drawn (NOT yet fixed — coupled to the
fidelity ladder and solver stability; this is what the sample round exists to pin down).

Three constraints govern every range: it must (a) produce the **sharp regime** we care about,
(b) keep the **bottom rung genuinely under-resolved** (range ↔ 32² ladder coupling), and
(c) keep the **solver stable** across the whole range. Default sampling: Latin-hypercube /
uniform over physically sensible ranges, unless noted.

- **2D Euler Riemann.** Schema = 4 quadrant states (ρ,u,v,p) + γ, fed as reductions
  (pressure ratios, shock Mach, slip angle, γ). **Don't sample all 17 dims blindly** — most
  draws give degenerate/1D configs. Sample around the **Schulz-Rinne catalog** (~19 canonical
  genuinely-2D Riemann configurations) and jitter their parameters. Ranges: pressure ratios /
  Mach large enough that real shocks form; γ near 1.4 (or a small set).
- **2D Cahn–Hilliard.** Schema = interface width ε, mobility M, IC parameterization
  (mean composition, random seed, initial wavelength/blob count). **ε range is coupled to the
  ladder:** must be chosen so 32² *under-resolves* ε while 128² resolves it (h ≲ ε/2). Validate
  this in the sample round — if 32² already matches 128², shrink ε or adjust the ladder.
- **2D Kuramoto–Sivashinsky (control).** Schema = domain size L, IC seed/amplitude. L large
  enough to be in the chaotic regime but where even 32² stays *close* to HF (control should show
  little LF–HF gap, by design). Sample L over a modest range + random IC seeds.

---

## Sample-round scope (what Nicholas actually sees)
- **~16–32 samples per PDE** (not full counts).
- Deliverable per PDE: saved sample dataset **+ a one-pager** (LF vs HF field, residual, spectrum,
  metric table).
- **Validate the bottom rung per-PDE** (key check): confirm LF is *measurably* blurrier/biased
  vs HF in the metric panel —
  - Euler 32² → shocks visibly smeared. ✅ expected.
  - Cahn–Hilliard 32² → must **under-resolve** ε. If the 32² field already matches 128²,
    the ladder or ε needs adjusting (they're coupled). ⚠️ check this.
  - KS 32² → expected to stay **close** to HF (control working as intended). ✅ by design.

### Approval checklist for Nicholas
- [ ] Is LF a legitimate **biased coarse solve** (not downsampled HF) for each PDE?
- [ ] Is the **32→64→128** ladder right, and does the bottom rung actually under-resolve each case?
- [ ] Is each **condition vector** complete?
- [ ] Is the **metric panel** the right yardstick?
- [ ] What **sample counts per fidelity** for the full run? (IFC-style few-HF, e.g. 100/50/20/5 HF
      with abundant LF; ~128 HF test.)

---

## Deferred to round 2 (noted, not done now)
- **High-k Helmholtz** (oscillatory; needs a direct/MUMPS solver — indefinite system).
- **Phase-field fracture** (literal cracks; FEniCSx; path-dependent → restrict to monotone
  single-crack loading, predict peak-load/final damage).

Add these once the template is approved, reusing the same recipe.

---

## Other open tasks (not part of the sample round)
- [x] **Created CLAUDE.md** (project context, methodology conventions, compute policy, dev workflow).
- [x] **Scaffold created**: `mffp_sharp/` — config, common modules (ladder/io/metrics/sampling),
      per-PDE solver modules, `generate.py` CLI, and `scripts/{setup_remote,run_sample}.sh`.
      All byte-compiles; solver modules carry `VALIDATE on box` notes. See `mffp_sharp/README.md`.
- [x] **GitHub repo**: https://github.com/eloisezeng/SURF_2026 (private). Workflow = edit locally
      → `git push` → `git pull` on the box → run there.
- [ ] On the box: `git clone` → `cd SURF_2026/mffp_sharp` → `bash scripts/setup_env.sh`
      (PyClaw needs gfortran).
- [ ] Run `bash scripts/run_sample.sh all`, review `data/sample/sample_summary.json` (bottom-rung check).
- [ ] (Open) Does the Playwright CLI help here? — likely **no** for data generation; revisit only
      if we need to scrape/automate a browser-based data source.

## Open knobs (defaults chosen; flag to change)
- Ladder 32/64/128 (vs 2-level 64/128, or 256² HF ceiling for shocks).
- Sample count 16–32/PDE.
- py-pde for both CH and KS (could swap KS → Dedalus for spectral accuracy).
- **2D KS is non-standard** (KS is textbook in 1D; 2D needs a custom nD operator in py-pde, not a
  canned class). The control case is slightly off-the-beaten-path — flag for Nicholas.
- Snapshot time T per PDE (fixed vs added to the condition vector).
