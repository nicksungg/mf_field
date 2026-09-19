# Provenance & verification — the PDE solvers

This guide helps readers (1) confirm each dataset/solver is **legitimate** (citation + exact code to read)
and (2) **verify it works** (how to run the correctness tests). Provenance first, verification second.

## How to read — two kinds of legitimacy

Not every solver is "cloned from a published dataset," and claiming so would overstate it:

- **clone** — the generation recipe replicates a specific *published benchmark dataset* (parameters,
  scheme, regimes). Recipes verified in
  [docs/research/2026-06-17-hf-pde-generation-recipes.md](docs/research/2026-06-17-hf-pde-generation-recipes.md).
- **classic** — a canonical PDE solved by a standard textbook scheme. There's no single dataset to
  clone; legitimacy = the method is standard **and** an exact-solution test passes (Barenblatt,
  Klein–Gordon dispersion, mass conservation, residual ≈ 0). Still grounded — in the numerical-analysis
  literature, not a dataset paper.

The **Type** column says which. The **Source** column uses short tags `[n]` → full citation + URL in
**References** below.

## The solvers

**File convention (the module name *is* the pointer):** module `<m>` → code
`mffp_sharp/src/mffp_sharp/pdes/<m>.py`, test `mffp_sharp/tests/test_<m>.py`. Per-dataset parameters:
`mffp_sharp/configs/sample.yaml`. (Euler's *solver* runs only on the box — see ⓘ in References.)

| PDE (datasets) | Method | Source | Type | Code | Test |
|---|---|---|---|---|---|
| `euler` | PyClaw/WENO FV | The Well [1] | clone | `euler.py` | `test_euler` (4 pass local; 3 solve tests box-pending) ⓘ |
| `cahn_hilliard` | semi-impl. Fourier | E-UNO [4] ⚠ | clone | `cahn_hilliard.py` | `test_cahn_hilliard` (mass conservation + bounded) |
| `kuramoto_sivashinsky` (+`_1d`) | semi-impl. Fourier | APEBench [3] | clone | `kuramoto_sivashinsky.py` | `test_ks_1d` (golden fixture) |
| `kdv_1d` | int-factor RK4 | APEBench [3] | clone | `kdv.py` | `test_kdv` |
| `allen_cahn` (`_1d/2d`) | semi-impl. Fourier | APEBench [3] ⚠ | clone | `allen_cahn.py` | `test_allen_cahn` |
| `swift_hohenberg` (`_1d/2d`) | semi-impl. Fourier | APEBench [3] | clone | `swift_hohenberg.py` | `test_swift_hohenberg` |
| `gray_scott_2d` | Fourier + ETDRK4 | The Well [1], Pearson [7] | clone | `gray_scott.py` | `test_gray_scott` |
| `shallow_water` (`_1d/2d`) | PyClaw FV, dam-break | PDEBench [2] | clone | `shallow_water.py` | `test_shallow_water` |
| `nls_1d` | split-step Fourier | classical | classic | `nls.py` | `test_nls` |
| `sine_gordon` (`_1d/2d`) | Fourier semilinear wave | classical | classic | `sine_gordon.py` | `test_sine_gordon` |
| `phase_field_crystal_2d` | semi-impl. Fourier, 6th-ord | Elder–Grant [10] | classic | `phase_field_crystal.py` | `test_phase_field_crystal` |
| `fisher_kpp` (`_1d/2d`) | semi-impl. Fourier | Fisher/KPP [14] | classic | `fisher_kpp.py` | `test_fisher_kpp` |
| `burgers` (`_1d/2d`) | PyClaw FV, inviscid shock | classical; FV-forced [3] | classic | `burgers.py` | `test_burgers` |
| `sod_1d` | PyClaw 1D Euler FV | Sod [8] | classic | `sod.py` | `test_sod` |
| `helmholtz_2d` | sparse direct, steady BVP | classical | classic | `helmholtz.py` | `test_helmholtz` |
| `porous_medium` (`_1d/2d`) | positivity-preserving FD | Vázquez [13] | classic | `porous_medium.py` | `test_porous_medium` |

⚠ `cahn_hilliard`: canonical $\varepsilon$ still unpinned. `allen_cahn`: name-collides with the deck's
`allen_cahn_gen` — regime must be checked on the box. See **Honest notes**.

## References

**Dataset / benchmark recipes (clone):**
- [1] The Well (NeurIPS 2024 D&B) — [arXiv:2412.00568](https://arxiv.org/abs/2412.00568) · [data repo](https://github.com/PolymathicAI/the_well) (`euler_multi_quadrants`, `gray_scott`)
- [2] PDEBench (NeurIPS 2022 D&B) — [arXiv:2210.07182](https://arxiv.org/abs/2210.07182) · [code](https://github.com/pdebench/PDEBench) (shallow-water radial dam break)
- [3] APEBench (NeurIPS 2024) — [arXiv:2411.00180](https://arxiv.org/abs/2411.00180) · [Exponax](https://github.com/Ceyron/exponax) · [code](https://github.com/tum-pbs/apebench). App. B.3 = the "spectral cannot make true shocks → use FV" disclaimer (FV-forced).
- [4] E-UNO Cahn–Hilliard — [arXiv:2509.01293](https://arxiv.org/abs/2509.01293)
- [5] Schulz-Rinne 1993, *SIAM J. Math. Anal.* 24(1):76–88 — [doi:10.1137/0524006](https://doi.org/10.1137/0524006) (19-config Riemann IC)
- [6] Kurganov & Tadmor 2002, *NMPDE* 18:584–608 — [doi:10.1002/num.10025](https://doi.org/10.1002/num.10025) (2D Riemann FV scheme)
- [7] Pearson 1993, *Science* 261:189–192 — [doi:10.1126/science.261.5118.189](https://doi.org/10.1126/science.261.5118.189) (Gray–Scott (f,k) regimes)

**Classical model / scheme origins (classic):**
- [8] Sod 1978, *J. Comput. Phys.* 27(1):1–31 — [doi:10.1016/0021-9991(78)90023-2](https://doi.org/10.1016/0021-9991(78)90023-2) (shock tube)
- [9] Cox & Matthews 2002, *J. Comput. Phys.* 176:430–455 — [doi:10.1006/jcph.2002.6995](https://doi.org/10.1006/jcph.2002.6995) (ETDRK family; underpins the spectral steppers)
- [10] Elder & Grant 2004, *Phys. Rev. E* 70:051605 — [doi:10.1103/PhysRevE.70.051605](https://doi.org/10.1103/PhysRevE.70.051605) (phase-field crystal)
- [11] Swift & Hohenberg 1977, *Phys. Rev. A* 15:319–328 — [doi:10.1103/PhysRevA.15.319](https://doi.org/10.1103/PhysRevA.15.319)
- [12] Kassam & Trefethen 2005, *SIAM J. Sci. Comput.* 26:1214–1233 — [doi:10.1137/S1064827502410633](https://doi.org/10.1137/S1064827502410633) (ETDRK4)
- [13] Vázquez 2007, *The Porous Medium Equation* (Oxford) — [doi:10.1093/acprof:oso/9780198569039.001.0001](https://doi.org/10.1093/acprof:oso/9780198569039.001.0001) (Barenblatt; the PME exact test)
- [14] **Fisher–KPP reaction–diffusion equation**, $u_t=\nu\Delta u + r\,u(1-u)$ — the PDE the
  `fisher_kpp` solver implements (a standard sharp-traveling-front model, used in combustion, ecology,
  phase transitions; plain-language [overview](https://en.wikipedia.org/wiki/Fisher%27s_equation),
  textbook treatment: Murray, *Mathematical Biology I*, Springer 2002). Introduced — with its
  traveling-front analysis — by **Fisher 1937**, *Ann. Eugenics* 7:355–369
  ([Wiley](https://onlinelibrary.wiley.com/doi/10.1111/j.1469-1809.1937.tb02153.x); that journal was
  renamed *Annals of Human Genetics* in 1954) and, independently, by
  **Kolmogorov–Petrovsky–Piskunov 1937**, *Bull. Moscow Univ.* 1:1–25 (English reprint:
  [*Selected Works of A. N. Kolmogorov, Vol. I*](https://link.springer.com/book/10.1007/978-94-011-3030-1),
  pp. 242–270). Cited only as the equation's mathematical origin — not its 1937 biological framing.

*`classical` rows without a numbered source (NLS split-step, sine-Gordon, Helmholtz) are standard
textbook methods with no single citable dataset — their legitimacy is the exact-solution test in the
Test column (NLS: finiteness/structural; sine-Gordon: Klein–Gordon dispersion $\omega=\sqrt{k^2+m^2}$;
Helmholtz: linear-solve residual ≈ 0).*

ⓘ **Euler test coverage — stated plainly.** `test_euler.py` now exists. Its config/condition-vector
checks (4 tests) **pass locally**; its PyClaw **solve** checks — finiteness, **density positivity**
(physical invariant), **LF-smears-vs-HF** (Classic Godunov should be blurrier than SharpClaw WENO),
and determinism — **skip without clawpack and have not yet been run** (box-pending, like
`test_burgers`/`test_sod`/`test_shallow_water`). So Euler's *numerics* are still box-unverified; until
that run, its assurance is PyClaw (a trusted FV library) + the The Well recipe [1] + box validation
(2026-06-15) + the sample-round run. Note also: the only true *golden-fixture* regression in the suite
is **KS** (`test_ks_1d.py` pins the 2D KS output bit-for-bit vs `ks_2d_golden.npy`);
`test_regression_2d.py`, despite its name, exercises the `common/` pipeline on synthetic arrays, not a
solver; Cahn–Hilliard now has an exact-invariant value check (`test_cahn_hilliard.py`: mass
conservation — the k=0 mode is preserved to ~machine precision — plus boundedness/determinism).

---

# Verifying the solvers work

## Why run tests if we already have the 72 sample figures?

The figures and the tests answer **different** questions — you want both:

- **The one-pagers show *plausibility*** — that the output *looks* physically right (shock where a
  shock belongs, interface of the right width), by eye, for the 24 sampled cases, generated **once on
  the box**. A figure can look perfectly plausible while the solver has a subtle bug (a wrong
  constant, a boundary mishandled) that the eye won't catch.
- **The tests show *correctness + reproducibility*** — things a picture cannot:
  - **exact-solution agreement** (Barenblatt profile, Klein–Gordon dispersion, mass conservation,
    residual ≈ 0) — a hard numeric check, not a visual impression;
  - **determinism** — same inputs reproduce the same field;
  - **it runs on the researcher's machine**, not just "a PNG exists from one box run."

So: figures = "looks right for these samples"; tests = "provably right, reproducible, and runs for
you." For a benchmark contribution you want the provable check, not only the render.

## Quick — one command

```bash
cd mffp_sharp
bash scripts/verify.sh
```

Expected **without** clawpack (e.g. the Mac `.venv`): `123 passed, 8 skipped`. The 8 skips are the
PyClaw solve tests (`euler`, `burgers`, `sod`, `shallow_water`) — **expected off-box, not a failure**.
On the box with clawpack they run too (~131 passed, 0 skipped, *if the box solve tests pass*).

## One PDE at a time

These are **pytest** files — run them with pytest, *not* `python test_nls.py` (which won't execute the
test functions):

```bash
cd mffp_sharp
python -m pytest tests/test_nls.py -v        # one PDE
python -m pytest tests/test_porous_medium.py # the Barenblatt exact-solution check
python -m pytest -q                          # everything (same as verify.sh)
```

## Two verification tiers

| Tier | Solvers | Verify where | Local status |
|---|---|---|---|
| pure numpy/scipy | CH, KS (1D/2D), Allen–Cahn, Fisher–KPP, KdV, NLS, sine-Gordon, Gray–Scott, PFC, Swift–Hohenberg, porous-medium, Helmholtz | **any machine** | ✅ 123 pass |
| PyClaw/WENO | euler, burgers, sod, shallow-water | **box only** (needs `clawpack`) | ⏭ skip locally; ran on box for the sample round |

## Deeper confidence (optional)

- **Reproduce a sample** end-to-end (generate → ladder → align → metric → one-pager → HDF5):
  `python -m mffp_sharp.generate --config configs/sample.yaml --pde cahn_hilliard` (any pure-numpy PDE
  locally; PyClaw ones need the box).
- **Eyeball the 72 one-pagers** in `mffp_sharp/data/sample/figures/` — the plausibility layer above.

---

## Honest notes
- **Shocks must be finite-volume.** Euler, Burgers, Sod, shallow-water use PyClaw/WENO, not spectral —
  a *correctness requirement*: spectral/ETDRK "precludes inviscid Burgers, Euler, or shallow water"
  (APEBench [3] App. B.3).
- **Cahn–Hilliard's canonical $\varepsilon$ is still open** — E-UNO [4] uses two length params; the
  $\varepsilon$ that sets sharpness in standard CH notation isn't pinned in the source. Open dependency
  before CH full-count generation.
- **APEBench/Exponax [3] is a *reference + validation*, not a dependency** — its solvers are periodic +
  normalized; ours are custom (to couple to our domain + dyadic ladder), validated *against* that
  class. The citation legitimizes the *recipe*; the code is ours to review (the Code column).
- **Name-collisions with the deck** (`allen_cahn_gen`, `burgers_gen`): we build the *sharp regime* of
  those equations; whether that differs from the deck's regime is a box verification item (see the
  sample-round report).

## Pointers
- Solvers: [`mffp_sharp/src/mffp_sharp/pdes/`](mffp_sharp/src/mffp_sharp/pdes/) · Tests:
  [`mffp_sharp/tests/`](mffp_sharp/tests/) · Config:
  [`mffp_sharp/configs/sample.yaml`](mffp_sharp/configs/sample.yaml)
- Literature survey (full recipes + what was refuted):
  [docs/research/2026-06-17-hf-pde-generation-recipes.md](docs/research/2026-06-17-hf-pde-generation-recipes.md)
</content>
