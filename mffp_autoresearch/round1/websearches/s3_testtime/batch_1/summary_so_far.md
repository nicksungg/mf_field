# Summary so far — `s3_testtime`, batch 1

Stream question (project.yaml): *"how far does test-time refinement go when the
governing residual is real?"* Class: **lever**. Batch 1 is the stream's first
card; no prior batch, no prior websearch for this stream.

## State of the round

`state/anchors/` is **empty** and `state/noise_floor.json` **does not exist** —
batch 0 (gate G3) is queued on SLURM (`state/gates.md`: "G3 - batch 0
(anchors + noise floor): PENDING"; G1/G2 PASS). Consequence for this batch,
per program.md 4.5: the stream anchor (champion certified panel geomean) is
**unavailable**, so the brainstormer must write a falsification clause that is
*self-contained* (an absolute, mechanism-level threshold) rather than a
delta against an anchor number, and must re-check it against
`state/noise_floor.json` once G3 lands. `experiment_cards/` contains only
`SCHEMA.md` - no cards exist in any stream yet. The only sibling websearch is
`websearches/s5_tuning/batch_1/` (a different stream; its transferable finding
is that fixed-LR mode-count comparisons are known to be mis-tuned).

## The stream's quantified prior is WRONG - verified in-repo

program.md 12.3 states: "`mf_fno_ptr` achieved **-21%** on era5/pm_test with a
*placeholder Laplacian* residual". I checked the source and the underlying
numbers:

- `mf_field/akash/models/mf_fno_ptr/refine.py` - `RESIDUAL_REGISTRY` has
  **exactly two keys**, `ifc_poisson` and `ifc_heat`. Every other dataset gets
  `residual_fn = None` -> `refine_field` returns `u_pred` unchanged (documented
  NO-OP), i.e. on era5/pm_test **the mechanism never ran**.
- `mf_field/akash/results/bench_metrics_subset.csv` - `mf_fno_ptr` and
  `mf_fno_transfer_film` on era5 are byte-identical to 17 digits
  (rel_l2 0.07231217372227801, nRMSE 0.07374730986307398, same CI). era5 and
  pm_test rows are themselves identical (same data, n_samples = **7**).
- The `0.0585` in `FINDINGS.md` is **`mf_fno_foundation`'s** era5 number
  (0.058549...), not ptr's. The -21% is a mis-attribution across rows.

**What the mechanism actually bought**, on the only panel-adjacent dataset
where it ran: `ifc_poisson` rel_l2 0.04756 (ptr) vs 0.04836 (film) = **-1.6%**;
nRMSE 0.04234 vs 0.04297 = -1.5%. Both sit deep inside the reported CIs
([0.0406, 0.0553] vs [0.0412, 0.0563]) - **not a signal**. Cost:
`latency_ms` 17.61 vs 0.108 = **163x inference time** for a null effect.
So the honest prior for this stream is: *placeholder-residual test-time
refinement on the field tensor has never been shown to help here*, and the
open question is whether a **real** residual changes that.

## What a "real governing residual" is actually available for

Checked `benchmark_42/*/meta.json` + `README.md` + npz keys for all 6 panel
datasets:

| panel dataset | governing eq. | residual computable from one snapshot + `x`? |
|---|---|---|
| `ext__helmholtz_2d` | `du + k^2 u = f`, `x = [wavenumber_k, source_x, source_y]` | **YES** - f is a located source; steady, elliptic. The one clean target. |
| `ifc_poisson` | elliptic Poisson, `x` 5-D | **NO** - refine.py records that the source decode from X is not shipped with this data copy. |
| `sharp__allen_cahn_2d` | Allen-Cahn @ `output_time` 0.5, `x = [eps, mobility, mean_composition]` | **NO** - time-dependent; a single snapshot has no du/dt, and the IC is not in `x`. |
| `sharp__cahn_hilliard` | Cahn-Hilliard @ t=5.0, `x` includes `ic_c0..ic_c6` | Partially - IC *is* parameterized, so a residual would require re-integrating in time, not a pointwise operator. |
| `sharp__fisher_kpp_2d` | Fisher-KPP @ t=0.05, `x = [D, r]` | **NO** - same reason as Allen-Cahn. |
| `sharp__phase_field_crystal_2d` | PFC (Elder & Grant 2004) @ t=200, `x = [r, mean_density]` | **NO** as a PDE residual; but t=200 is late-time, so a *free-energy / equilibrium* surrogate is plausible. |

This is the batch's central design tension and drives the search terms: a
literal "true governing residual" only exists for **1 of 6** panel datasets
(Helmholtz). For the four phase-field/reaction datasets the candidate is a
**variational / energy-functional / equilibrium surrogate**, not a PDE
residual - and I need literature on whether that works and whether it is
already published.

## Open questions this batch's search must answer

1. Is field-space test-time optimization against the true residual a published
   mechanism for neural-operator outputs (NITO-style), and what is reported
   when the residual is exact vs a prior?
2. IRNO (arXiv:2605.24041, program.md 12.3 second lever) - verify first-hand;
   is its frozen-base fixed-point refinement already claimed in an MF setting?
3. For time-snapshot phase-field data with no du/dt, is there a published
   energy/variational test-time correction?
4. Does test-time refinement have a known failure mode (overfitting to the
   residual, destroying the LF information - exactly the s2 "skill > 1"
   pathology)? Is there a mechanism with a *guarantee* it cannot do worse?

## In-repo literature already read (cite, don't re-derive)

- `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` 3.1 + proposal **N1**
  (`mf_fno_irno`, frozen-base iterative corrector, progressive spectral loss,
  claims ~50x high-frequency-band error cut, refinement module transfers
  across base operators) and proposal **N3** (`mf_fno_solve`, predict-then-CG
  on known-PDE datasets - the "residual is real" idea in its strongest form).
- `docs/reports/MF_Sharp_HighFreq_Report.md` line 98: `mf_fno_pinn_transfer`'s
  FD-residual loss is "the zoo's *only* position-exact supervision - Poisson-
  gated, so inactive on SURF", i.e. the physics path has never been switched
  on for the five sharp-2D datasets.
