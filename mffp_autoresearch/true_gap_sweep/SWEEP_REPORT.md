# true_gap_sweep — LF-vs-HF fidelity-gap measurement for fisher_kpp_2d and phase_field_crystal_2d

Date: 2026-08-05.
Status: MEASUREMENT ONLY — no shipped dataset, generator default, or guarded surface was modified.
All artifacts live under `mffp_autoresearch/true_gap_sweep/` (scripts, per-cell JSONs in `results/`, SLURM logs in `logs/`).

## Method (shared)

Gap measure is the canonical one throughout: rel-L2 of (HF − spectrally-interpolated LF), i.e. `||HF − spectral_interp(LF→128)|| / ||HF||`, median over the batch.
The superseded block-average measure (operator-mismatch floor ~0.02–0.05, per `condition_completeness_proposal/PROPOSAL.md`) was not used anywhere.
Solvers, IC encoding, sampling, and ladder come unmodified from the installed `mffp_sharp` package (`pdes/fisher_kpp.py`, `pdes/phase_field_crystal.py`, `common/spectral.py`, `common/ic_encoding.py`).
Production ladder from `configs/sample.yaml`: resolutions [32, 64, 128], HF = 128; production seed 42; batches of n = 8 Latin-hypercube specs.
Predictability-horizon check: re-solve 3 samples per cell at HF with the HF initial condition perturbed by 1e-6 relative (rms-scaled) Gaussian noise, record rel-L2 divergence at T.
Front-structure sanity: p95 of |∇u| on the HF field, plus field mean/std.

## Task 1 — fisher_kpp_2d solve-time sweep

Recipe under test: the current production recipe — `ic_modes=5`, `D_range=[1e-4, 1e-3]`, `r_range=[5, 20]`, `domain_size=1.0`, band-limited IC in [0,1] centered at 0.5.

### Main T sweep (production D_range)

| T | gap32 (median) | gap64 (median) | divergence (median) | grad p95 | HF mean |
|---|---|---|---|---|---|
| 0.05 | 2.87e-4 | 1.42e-4 | 2.0e-7 | 7.19 | 0.627 |
| 0.10 | 9.76e-4 | 1.73e-4 | 1.0e-7 | 6.41 | 0.739 |
| 0.15 | 1.54e-3 | 2.30e-4 | 6.5e-8 | 4.85 | 0.829 |
| 0.20 | 2.06e-3 | 2.79e-4 | 4.2e-8 | 3.15 | 0.892 |
| 0.30 | 2.04e-3 | 3.05e-4 | 1.7e-8 | 1.21 | 0.961 |
| 0.60 | 9.32e-5 | 1.76e-5 | 6.5e-10 | 0.04 | 0.999 |
| 1.0 | 7.92e-7 | 1.47e-7 | 6.6e-12 | 0.00 | 1.000 |
| 1.5 | 2.59e-9 | 5.0e-10 | 2.6e-14 | 0.00 | 1.000 |
| 2.0 | 9.9e-12 | 1.9e-12 | 6.5e-15 | 0.00 | 1.000 |
| 3.0 | 5.5e-14 | 4.0e-14 | 5.9e-15 | 0.00 | 1.000 |
| 4.5 | 5.4e-14 | 3.3e-14 | 1.4e-14 | 0.00 | 1.000 |
| 6.0 | 5.4e-14 | 3.3e-14 | 1.4e-14 | 0.00 | 1.000 |

The gap is unimodal in T: it rises to ~2.1e-3 at T ≈ 0.2–0.3 and then collapses super-exponentially to machine epsilon.
The mechanism is visible in the sanity columns: the logistic reaction saturates the whole domain to u = 1 (mean 0.999 by T = 0.6, grad p95 → 0), so the fronts — and with them all LF-vs-HF disagreement — cease to exist.
This is a **certified negative for the "longer output_time" lever** from the PROPOSAL trilemma discussion: unlike cahn_hilliard (whose coarsening runs indefinitely and holds a 1.5e-2 gap at T = 5), Fisher–KPP's dynamics terminate in a uniform absorbing state, so more solve time can only destroy the gap.
Divergence stays ≤ 2e-7 everywhere and *decreases* with T (perturbations die in the saturated state); Fisher–KPP is nowhere near a predictability horizon, so every measured gap is honest learnable structure.

The current production point T = 0.30 sits at the peak of the curve and clears the ≥ 1e-3 preflight threshold with margin: batch median 2.04e-3, per-sample minimum 1.35e-3 (all 8 samples clear 1e-3).
Note this batch median is ~6× the ~3.2e-4 quoted for T = 0.30 in the PROPOSAL (measured 2026-08-03); both are canonical-measure numbers, so the difference is batch composition (this run: n = 8, seed 42, per-sample median), and the discrepancy should be kept in mind when quoting a single headline number.
No T in the requested grid reaches the 1e-2 cahn_hilliard-class threshold under the production D_range.

### D_range leg (thinner fronts at the peak-T window)

| tag | D_range | T = 0.2 | T = 0.3 | T = 0.45 |
|---|---|---|---|---|
| prod | [1e-4, 1e-3] | 2.06e-3 | 2.04e-3 | — |
| lowD | [3e-5, 3e-4] | 2.64e-3 | 5.28e-3 | 2.93e-3 |
| lowD2 | [1e-5, 1e-4] | 3.05e-3 | 7.47e-3 | 7.06e-3 |

Lowering D_range one decade (lowD2) raises the T = 0.30 gap to 7.5e-3 median (per-sample max 1.2e-2), with gap64 = 1.7e-3 — the mid rung then clears preflight too.
HF-convergence audit (`fk_hf_convergence_*.json`): a 256-grid reference solve gives HF-128 error 1–5% of the measured gap for prod, lowD, and lowD2 alike, so the gap is genuinely LF error, not HF discretization error.
Divergence in the lowD2 leg is ≤ 2.1e-7 — still no horizon issue.
Going below D ≈ 1e-5 is not recommended without raising HF resolution: front width √(D/r) reaches ~7e-4 against h_HF = 7.8e-3, and the HF-convergence ratio is already creeping up (0.04 on the thinnest-front sample).

### Fisher–KPP deliverable

The T at which gap ≥ 1e-3 while divergence ≪ 1 is the window T ∈ [0.15, ~0.45], and the current production T = 0.30 is at its center and at the curve's peak.
Recommendation, minimal change: keep the shipped recipe (T = 0.30, ic_modes = 5, D_range [1e-4, 1e-3]) and record its certified canonical gap of ~2e-3 (preflight-class, not cahn_hilliard-class).
Recommendation, if a stronger gap is wanted: keep T = 0.30 and lower D_range to [1e-5, 1e-4] → median gap 7.5e-3 on the bottom rung and 1.7e-3 on the mid rung, HF still certified converged; this changes the sampled physics (thinner fronts), so it is a recipe change, not a re-measurement.
Certified negative: no output_time ≥ 0.6 is viable for this PDE under any D_range measured, because the absorbing state u ≡ 1 erases the field.

## Task 2 — phase_field_crystal_2d structural audit

Recipe under test: production — T = 200, domain 32 (lattice wavelength 2π → points-per-wavelength = 0.196·res), `r_range=[-0.4, -0.1]`, `mean_density_range=[-0.4, -0.2]`, `ic_amplitude=0.05`, encoded IC (m = 3).
The uniform state is linearly unstable at k = 1 iff σ = −(r + 3ψ̄²) > 0; the production box straddles the phase boundary.

### (a) Gap vs LF resolution (production sampling box, HF = 128)

| LF res | pts per lattice λ | outcome over 8 samples |
|---|---|---|
| 8 | 1.6 (below Nyquist) | crystalline samples: solver blow-up (NaN); uniform samples: garbage (rel-L2 up to 7.0) or noise |
| 16 | 3.1 | crystalline samples: solver blow-up (NaN); uniform samples: gap ≤ 2.6e-8 |
| 32 | 6.3 | crystalline: 2.2e-3 – 5.2e-2; uniform: ~1e-15 |
| 64 | 12.6 | crystalline: ~1e-6; uniform: ~1e-15 |

There is **no viable under-resolving rung**: once the LF grid cannot carry the k ≈ 1 lattice peak plus its nonlinear-saturation harmonics, the semi-implicit solver does not produce a blurrier field — it diverges to NaN (the linear instability grows and the truncated/de-aliased cubic has no channel to saturate it).
The IC-build consistency check passed (building the encoded IC on res 8 vs res 32 and interpolating to 128 differs by < 3e-17), so the blow-ups are solver physics, not IC artifacts.
LF = 64 is a dead rung (~1e-6), and coarser-than-32 rungs are unusable, so the resolution-pair lever is a certified dead end.

### (b) Crystalline-region restriction (the live lever)

Production box, per-sample split: 4/8 samples have σ < 0, sit in the uniform phase, decay to a flat field (HF std = 0), and have gap ~1e-15; the crystalline half has gap32 2.2e-3 – 5.2e-2.
The shipped NO_GAP verdict (8.3e-6 / 1.2e-6) is therefore a **composition artifact**: machine-zero uniform-phase samples drag the aggregate onto the no-gap floor and mask a real gap in the crystalline half.
Dedicated all-crystalline box (`r ∈ [-0.4, -0.3]`, `ψ̄ ∈ [-0.25, -0.2]`, σ ≥ 0.11 everywhere), n = 8, existing 32/64/128 ladder:

| quantity | value |
|---|---|
| gap32 median | **9.80e-3** (range 2.8e-3 – 1.36e-1) |
| gap64 median | 1.03e-6 |
| HF pattern amplitude (std) | 0.37 – 0.43 (all crystalline) |
| divergence at ε = 1e-6 | 7.7e-3 / 1.1e-2 / 2.8e-2 (3 samples) |
| divergence scaling | exactly linear in ε down to 1e-10 (amplification ~0.7–2.8e4, constant) |

The horizon check passes: divergence at the physical perturbation scale is ≪ 1, and the linear ε-scaling certifies a smooth (non-chaotic, non-saturated) finite-time map — the gap is deterministic resolution error, not decorrelation noise.
Caveat to carry into any adoption decision: the finite-time amplification factor is ~1e4, and the measured gap (~1e-2) is of the same order as the response to a 1e-6 IC perturbation, so the cond→field map is smooth but stiff; a nearest-pair-style sensitivity witness will report ~1e4 relative amplification, and per-sample gaps span 1.5 decades.

### PFC deliverable

This is **not** a certified structural negative — a candidate recipe exists.
Candidate recipe: restrict sampling to the crystalline region (σ = −(r + 3ψ̄²) ≥ ~0.1, e.g. `r_range=[-0.4, -0.3]`, `mean_density_range=[-0.25, -0.2]`), keep the existing 32/64/128 ladder and T = 200 → canonical bottom-rung gap ~1e-2 (cahn_hilliard-class), with the sensitivity caveat above and a dead mid rung (gap64 ~1e-6).
Certified negatives within the audit: (i) no LF resolution below 32 is usable (solver blow-up, not blur); (ii) the unrestricted production (r, ψ̄) box can never show a gap because half its mass generates identical flat fields at every resolution.
If the round-3 panel wants pfc as a copy-LF-denominated MF dataset, the crystalline restriction is the only lever this solver design offers.

## Files

- `fk_sweep.py`, `fk_sweep.sbatch` — Task 1 sweep (SLURM array job 66574227, partition expansion, all 8 cells COMPLETED).
- `pfc_audit.py`, `pfc_divergence.py` — Task 2 audit and horizon checks (run locally, ~4 min total).
- `results/fk_prod_T*.json`, `results/fk_lowD*_T*.json` — per-cell fisher_kpp results with per-sample rows.
- `results/fk_hf_convergence_*.json` — 256-grid HF-convergence audits.
- `results/pfc_prod.json`, `results/pfc_cryst.json`, `results/pfc_cryst_divergence*.json` — pfc cells.

## Next step

Nothing has been regenerated and no recipe has been changed.
Regeneration + panel swap for either dataset requires an in-round panel-mutation ADR (PROGRAM_NOTE MUST #5) and operator approval.
