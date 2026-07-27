# Verification report — SURF_2026 / `mffp_sharp` sharp-field PDE solvers

**Date:** 2026-06-23 · **Verifier:** independent run by Nicholas (mentor side), on the ORCD box
**Repo:** `eloisezeng/SURF_2026` (private) → extracted to `mf_field_eloise_data/SURF_2026-main`
**Verdict:** ✅ **The data-generation is accurate.** Every solver reproduces its exact analytic
solution, conservation law, and/or grid-convergence behavior. Including the box-only PyClaw
shock solvers, which I was able to run here (clawpack built with gfortran).

---

## What "the data" actually is

The repo ships **almost no bulk numeric data** — the datasets are git-ignored and regenerable.
What's version-controlled is the **solver code** that generates the data, plus sample
figures/JSON and one golden fixture (`tests/fixtures/ks_2d_golden.npy`). So "check the data is
accurate" = **validate the solvers**. That's what this report does, three ways:

1. The repo's own test suite (necessary, but the author's tests).
2. My from-scratch independent checks (exact solutions, conservation, mesh/time convergence) —
   `independent_verification.py` + `sod_exact_check.py`, written without using the repo's tests.
3. Cross-check each equation against its cited paper/canonical form.

---

## 1. Repo's own test suite

```
python -m pytest -q     →  131 passed, 0 skipped   (24 s)
```

The documented expectation off-box is "123 passed, 8 skipped" (the 8 PyClaw solve tests skip
without clawpack). **I installed clawpack (gfortran present) and ran all 8 box-only tests too —
they pass.** This closes the gap `PDE_SOLVERS.md` flagged ("Euler's numerics are still
box-unverified"): euler / burgers / sod / shallow-water solve, are finite, density-positive,
deterministic, and LF-smears-vs-HF as designed.

## 2. Independent verification (written from scratch)

`independent_verification.py` → **15/15 PASS**. Each row is an exact analytic solution, a
conservation law, or a convergence study — not a re-run of the repo's asserts.

| # | Solver | Independent check | Result |
|---|--------|-------------------|--------|
| 1 | Porous medium | Barenblatt self-similar exact soln + grid convergence | relL2 8e-4→**2.6e-5** (↓ with h) |
| 2 | KdV | single soliton: speed=c, amp=c/2 preserved | relL2 **3.4e-9**, speed exact |
| 3 | NLS | standing bright soliton shape + mass | shape 1.4e-7, mass drift **9e-13** |
| 4 | sine-Gordon | Klein-Gordon dispersion ω=√(k²+m²) | relL2 **3.1e-8** |
| 5 | sine-Gordon | energy conservation (nonlinear amplitude) | drift **1.6e-3** over 6 t.u. |
| 6 | Fisher-KPP | front speed → c*=2√(Dr) **with Bramson −3/(2t) correction** | 1.89 vs theory 1.906 (**0.7%**) |
| 7 | Cahn-Hilliard | mass (k=0) conserved + bounded ±1 | drift **4e-14** |
| 8 | spectral_interp | band-limited up-interp matches analytic | relL2 **6.6e-16** |
| 9 | Allen-Cahn | mesh self-convergence vs 512 grid | relL2 4.9e-5→**2.3e-6** (↓) |
| 10 | NLS | Strang split-step **temporal order ≈2** | err ratio **17×** per 4× dt (16 ideal) |
| 11 | Helmholtz | linear-solve residual ‖Au−f‖/‖f‖ | **3.5e-12** worst over k∈{10,25,40} |
| 12 | KS (2D) | golden-fixture **bit-reproduction on this machine** | max abs diff **0.0** |
| 13 | Phase-field-crystal | conserved dynamics: mean preserved | drift **3.7e-16** |
| 14 | Swift-Hohenberg | pattern selects k≈1 (spectral peak) | peak at **k=0.992** |
| 15 | Gray-Scott | fields bounded + pattern forms | v∈[0,0.44], σ=0.10 |

**Shock solver — exact Riemann (`sod_exact_check.py`):** my from-scratch exact Sod solver gives
p\*=0.30313, u\*=0.92745 (= Toro's textbook reference). PyClaw WENO **converges to it**: density
relL2 1.08e-2 → 9.3e-3 → **6.05e-3** at res 256/512/1024 — sub-1%, impressive across the contact
discontinuity.

### Notes on two checks that needed care (test-side, not solver-side)
- **Fisher-KPP front speed.** A naïve "rightmost u=0.5" tracker on a *periodic* domain latches
  onto the wrap-around front, and late-time measurement is corrupted because the KPP zero-state
  is linearly unstable (far-field roundoff grows as e^{rt} and floods the box ~t≳25). Measured
  cleanly at early times, the front speed rises 1.76→1.86→1.89, matching the **Bramson
  c*−3/(2t)** correction to 0.7% — i.e. the solver is right; the subtlety is in how you measure.

## 3. Equation ↔ source cross-check

Each implemented PDE matches its canonical published form: KS `u_t=−Δu−Δ²u−½|∇u|²` (APEBench),
Swift-Hohenberg `u_t=ru−(1+Δ)²u−u³` (S-H 1977), PFC `∂ψ/∂t=Δ[(r+(1+Δ)²)ψ+ψ³]` (Elder-Grant,
mass-conserving by the leading Δ), Gray-Scott in Pearson (F,k) form, Cahn-Hilliard / Allen-Cahn
double-well, Fisher-KPP logistic, PME degenerate diffusion (Vázquez/Barenblatt). Shocks correctly
use finite-volume (PyClaw), not spectral, per the APEBench App. B.3 disclaimer. Numerical schemes
(semi-implicit Fourier, IF-RK4, Strang split-step, ETDRK family) are standard and implemented
correctly — confirmed by the order/convergence tests above.

---

## Caveats & open items (none are correctness bugs)

- **Box-only solvers now verified here**, but in a *fresh* clawpack build (not the project's
  `eloise@10.80.6.224` box). Same library, same recipe; results match exact Riemann theory.
- **Cahn-Hilliard ε not yet pinned** to a single canonical value (`PDE_SOLVERS.md` ⚠). This is a
  *dataset-design* choice (how sharp to make the interface vs the 32/64/128 ladder), **not** a
  solver error — CH conserves mass and stays bounded regardless.
- **`allen_cahn` name-collides** with the deck's `allen_cahn_gen`; whether the *regime* differs is
  a design item. The Allen-Cahn *solver* is correct (mesh-convergent).
- These checks validate **numerics/physics**. They do not judge whether the chosen (T, ε, D/r,
  ladder) make each dataset "sharp enough" to stress the MFFP benchmark — that's the sample-round
  review, separate from accuracy.

## How to reproduce

```bash
module load miniforge/25.11.0-0
source mf_field_eloise_data/.venv/bin/activate     # built on the neuralsolver env + pytest/skimage/clawpack
cd mf_field_eloise_data/SURF_2026-main/mffp_sharp
python -m pytest -q                                                  # 131 passed, 0 skipped
python ../../independent_verification.py                             # 15/15 PASS
python ../../sod_exact_check.py                                      # Sod exact-Riemann convergence
```
