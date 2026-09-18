# How published work generates high-frequency PDE datasets — replication recipes

*Deep-research survey, 2026-06-17. 22 primary sources, 104 claims extracted, 25 adversarially
verified (20 confirmed, 5 killed). This is the "replicate proven recipes, don't invent thresholds"
answer to Nicholas's guidance.*

## Headline
Published scientific-ML datasets get genuine high-frequency content by **matching solver class to
physics**: finite-volume/Godunov for shocks, Fourier pseudo-spectral ETDRK for everything smooth-
but-stiff (dispersive, pattern, phase-field, chaotic). And the central negative result:

> **No surveyed benchmark is BOTH high-frequency AND multi-fidelity-via-independent-coarse-solves.**
> The two properties appear *separately*: the genuinely multi-fidelity datasets that use real coarse
> solves are *smooth* (the MF-surrogate subfield — e.g. the MFFP deck's own `ifc_*` / `*_local`
> sources), while the *high-frequency* datasets are single-fidelity or expose fidelity only as
> **post-hoc downsampling** — VERIFIED only for **PDEBench's `reduced_resolution` loader knob**
> (3-0, code-level), which strided-slices one HF solve.
>
> **Honest scope (do not overstate):** this is NOT "all multi-fidelity data is downsampling" (false —
> independent-coarse-solve MF datasets exist, just smooth). It is a *scoped* negative on the
> intersection. One hole remains: the "The Well MHD_64 = downsample" claim was actually
> **refuted** in verification (0-3) → unresolved, not evidence. The survey also left OPEN whether
> *any* dataset (even smooth) builds independent-coarse-solve LF/HF — i.e. it did not prove a
> universal negative. Treated this way, the intersection gap is the niche the project fills.
>
> **Second pass (BLASTNet / BubbleML / CFDBench / JHTDB) — complete and all four VERIFIED to confirm
> the scoped gap.** None is multi-fidelity-via-independent-coarse-solves; the high-frequency ones
> expose resolution only post-hoc. **BLASTNet is the strongest single datapoint:** its authors
> use Favre-filtered DNS for the low-res inputs and *explicitly state* that an independent-coarse-solve
> (implicit-LES)↔DNS pair is "not feasible … due to the stochastic nature and time-dependency" of
> chaotic turbulence — i.e. our filter-2 (chaotic divergence) failure mode, confirmed by domain
> experts. See "Second pass" below.

## Per-candidate replication recipes (verified)

### Euler Riemann — SHOCK → finite-volume, never spectral
- **Recipe to clone: The Well `euler_multi_quadrants`.** 2D compressible inviscid Euler;
  multi-quadrant Riemann IC (piecewise-constant states → interacting shocks/rarefactions/contacts);
  **Clawpack/AMRClaw** finite-volume; **512×512**, 100 timesteps, 10,000 trajectories (500/param);
  **γ ∈ {1.13, 1.22, 1.3, 1.33, 1.365, 1.4, 1.404, 1.453, 1.597, 1.76}**; BC open(extrap) or
  periodic; fields ρ, E, p, momentum. *Matches our PyClaw Euler plan exactly.*
- **IC sampling: the Schulz-Rinne 19-configuration benchmark** — four constant states meeting at the
  domain center, each interface a shock (S) / rarefaction (R) / slip-contact (J). Canonical set used
  by Lax–Liu (1998) and Kurganov–Tadmor. → condition vector = **config id + γ + BC + snapshot T**.
- **Fully-specified citable numerics (alt to WENO): Kurganov–Tadmor 2002** — Riemann-solver-free
  central scheme, **400×400**, **CFL 0.475**, PL (2nd-order) or ENO/WENO (3rd-order) reconstruction,
  componentwise minmod θ∈[1,1.5], 2nd-order modified-Euler / 3rd-order TVD-RK.
- **Hard constraint: spectral solvers CANNOT produce genuine shocks** — only viscous (smoothed)
  versions (APEBench authors' own disclaimer, arXiv:2411.00180 App. B.3: ETDRK "precludes …
  inviscid Burgers, Euler, or shallow water"). → **shock candidates (Euler, Sod, Burgers-shock,
  shallow-water) MUST use the PyClaw/FV branch, not the spectral branch.**

### Cahn–Hilliard — SHARP INTERFACE → ε ties to interface width
- **Recipe (E-UNO, arXiv:2509.01293):** chemical potential
  $\mu = \lambda\big(\Phi(\Phi^2-1)/\varepsilon - \varepsilon\,\Delta^2\Phi\big)$, double-well
  Ginzburg–Landau energy; **γ (mobility)=1, λ=0.01**, **100×100** unit square, **Neumann BC**,
  COMSOL FEM, **300 stochastic-seed sims** from uniform Φ=0. Equilibrium profile
  $\Phi^{eq}=\tanh\!\big(s/(\varepsilon\sqrt2)\big)$.
- **⚠ OPEN — the one number we still need:** the paper uses *two* length params (λ "interface
  thickness" AND a separate ε); the **ε that actually sets sharpness in standard CH notation is not
  pinned in the source**. We still must source the canonical ε and the ε↔grid scaling so 32²
  under-resolves while 128² resolves it (the MFFP bottom-rung requirement).

### Dispersive / pattern / control → off-the-shelf Fourier ETDRK (Exponax / APEBench)
- **Exponax (github.com/Ceyron/exponax)** implements, ready-made on periodic domains:
  `KortewegDeVries`, `KuramotoSivashinsky`(+Conservative), `reaction.AllenCahn`,
  `reaction.CahnHilliard` ($u_t=\nu\Delta(u^3+c_1 u-\gamma\Delta u)$), `reaction.GrayScott`,
  `reaction.SwiftHohenberg` ($u_t=ru-(k+\Delta)^2u+g(u)$), `Burgers`,
  `NavierStokesVorticity`/`KolmogorovFlow` (2D). Numerics: linear part exact via matrix-exp in
  Fourier space, nonlinear via **ETDRK orders 1–4 (Cox–Matthews 2002, Kassam–Trefethen** contour
  integral), dealiasing validated vs FourierFlows.jl.
- **Caveat:** periodic domains + *normalized* coefficients — needs adaptation for our domain
  sizes/BCs and to couple to the dyadic ladder. Use as **reference + validation** for our custom
  spectral solvers (CH/KS already validated), not necessarily a wholesale dependency.

### Gray–Scott — PATTERN → The Well recipe
- $\partial_t A=\delta_A\Delta A-AB^2+f(1-A)$, $\partial_t B=\delta_B\Delta B-AB^2-(f+k)B$;
  **Fourier spectral + ETDRK4 (Chebfun)**; **128×128**, periodic $[-1,1]^2$; fixed
  **$\delta_A=2\!\times\!10^{-5},\ \delta_B=10^{-5}$**; **6 canonical Pearson (f,k) regimes** —
  Gliders (0.014,0.054), Bubbles (0.098,0.057), Maze (0.029,0.057), Worms (0.058,0.065),
  Spirals (0.018,0.051), Spots (0.03,0.062); 200 ICs each. Condition vector = **(f,k) + IC type**.

### Shallow water — BORES → PDEBench radial dam break
- **`gen_radial_dam_break.py`** (PDEBench `data_gen/`): circular water bump (**inner_height=2.0,
  grav=1.0**), **dam_radius ~ U[0.3,0.7]**, **PyClaw `riemann.shallow_roe_with_efix_2D`** (FV
  hyperbolic, captures bores), **128×128**, Neumann BC, 1000 runs × 100 timesteps. Directly clonable.
  (Path correction: the solver is `data_gen/src/sim_radial_dam_break.py`, not `src/swe/`.)

### PDEBench compressible (reference for FV scheme, NOT a "sharp" exemplar)
- Scheme: **2nd-order HLLC Riemann solver + MUSCL/van-Leer** reconstruction (`CFD_multi_Hydra.py`).
  *But* the claim that PDEBench compressible-NS is a *deliberately sharp* benchmark was **REFUTED** —
  cite it for the solver recipe only, don't call it a high-frequency exemplar.

## Second pass — large fluid/turbulence benchmarks (BLASTNet, BubbleML, CFDBench, JHTDB)
Targeted follow-up to close holes #2 in the original open-questions list. **Every one confirms the
scoped gap** — none pairs genuine high-frequency content with multi-fidelity-via-independent-coarse-
solves. (Verification was partly truncated by a session limit; per-item confidence noted.)

| Dataset | Solver / data | Fidelity mechanism | High-freq? | Verdict |
|---|---|---|---|---|
| **CFDBench** | ANSYS Fluent 2021R1, pressure-based FV (laminar / SST k-ω); smooth low-Re flows Re∈[20,1000] | single fixed **64×64** grid via **post-hoc interpolation** | No (smooth, laminar) | Not MF, not HF. **Confirms gap.** (verified) |
| **JHTDB** | DNS (isotropic 100TB, MHD 50TB, channel 130TB, buoyancy 27TB, BL 105TB) | single stored DNS + **on-the-fly Lagrange/spline interpolation** — multi-resolution is a *query of one DNS*, not independent coarse solves | **Yes** (genuine high-wavenumber turbulence) | HF but **not** MF-via-coarse-solve. **Confirms gap.** (verified) |
| **BubbleML** | multiphase boiling DNS, single converged resolution (16×16 per 0.5×0.5 block) | ships **downsampled** examples; low-res sims listed as **future work** → no independent coarse solves | partial (boiling fronts) | Not MF-via-coarse-solve. **Confirms gap.** (verified) |
| **BLASTNet 2.0** (Momentum128 3D SR, NeurIPS 2023, arXiv:2309.13457) | 34 compressible reacting/non-reacting **turbulence DNS**; 128³ DNS-fidelity labels | low-res = **Favre-filtered DNS** at 8×/16×/32× (filtered *from the labels*) — a "finite-volume optimal LES" surrogate for implicit LES | **Yes** (turbulence DNS) | HF but **not** MF-via-coarse-solve. **Confirms gap.** ✅ **VERIFIED** (App. E.1.6, primary source) |

**BLASTNet's authors state our filter-2 reasoning verbatim** (App. E.1.6): *"While having an implicit
LES solution and corresponding DNS data as a feature-label pair within BLASTNet would be ideal, it is
not feasible to obtain a matching implicit LES-DNS pair due to the stochastic nature and
time-dependency of fluid simulations. Specifically, small changes in the system (such as grid size)
can result in widely different flow behavior due to the chaotic nature of turbulence … works … have
conventionally employed filtered DNS in place of implicit LES flowfields."* → a citable, expert
statement that **independent-coarse-solve LF/HF pairs are infeasible for chaotic turbulence**, which
is exactly why our portfolio drops 2D NS / 2D incompressible Euler (filter 2) and why the high-freq×MF
intersection is empty in practice, not just unattempted.

**Net:** the second pass *strengthens* the scoped negative — the two genuinely high-frequency
benchmarks examined (JHTDB, BLASTNet) expose resolution only as post-hoc access to / filtering of a
single DNS, never as independent coarse solves; the MF-looking ones (CFDBench) are smooth. The
intersection (high-freq **and** independent-coarse-solve LF/HF) remains unoccupied.

## What the verification KILLED (honesty)
- ✗ "The Well shows FNO/spectral does **not** uniformly win on sharp/turbulent physics" — **refuted
  0-3.** We cannot cite The Well as evidence for our hypothesis; the spatial-vs-spectral split claim
  did not survive.
- ✗ Several framings of The Well MHD pairing as relevant to us — refuted (it's downsampling, and the
  "independent coarse solve" readings were wrong); the PDEBench `reduced_resolution` downsampling
  fact **stands** and carries the gap argument.
- ✗ "PDEBench compressible-NS is the suite's deliberately-sharp case driven by viscosity" — refuted.

## Open questions (carry into the spec / a second pass)
1. **The canonical CH ε** (standard notation) and its grid-scaling — the single unpinned number we
   need before CH replication.
2. ~~**BLASTNet, BubbleML, CFDBench, JHTDB** were named but didn't surface surviving recipes.~~
   **DONE (second pass, see above)** — all four examined and **verified**; all confirm the scoped gap
   (none is high-freq *and* independent-coarse-solve MF). BLASTNet now verified from primary source
   (App. E.1.6) and is the strongest datapoint. No residual on this item.
3. **Canonical Mach / near-inviscid regimes + snapshot-T conventions**, and which of the 19 Riemann
   configs best stress FNO's spectral truncation along our smooth→sharp axis.
4. **Any** published PDE-surrogate dataset that builds LF/HF via independent coarse *solves* (even
   non-sharp) — would be the precedent to cite for the MFFP-compliant method.

## Key sources
- The Well (NeurIPS 2024): euler_multi_quadrants, gray_scott — proceedings.neurips.cc …4f9a5acd…; polymathic-ai.org/the_well
- PDEBench (NeurIPS 2022): arXiv:2210.07182; github.com/pdebench/PDEBench
- Schulz-Rinne 1993 (DOI 10.1137/0524006); Kurganov–Tadmor 2002 (NMPDEs 18:584-608)
- APEBench / Exponax: arXiv:2411.00180; github.com/Ceyron/exponax
- E-UNO Cahn–Hilliard: arXiv:2509.01293
- BLASTNet 2.0 / Momentum128 3D SR (NeurIPS 2023): arXiv:2309.13457; blastnet.github.io (filtered-DNS
  low-res + App. E.1.6 infeasibility-of-coarse-solve-pairing statement)
