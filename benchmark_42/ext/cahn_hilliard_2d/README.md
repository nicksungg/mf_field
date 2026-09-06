# cahn_hilliard_2d_generated

**PDE:** c_t = M∇²(c³-c-γ∇²c)  
**Source:** Cahn & Hilliard 1958, JCP 28(2):258 (DOI 10.1063/1.1744102)  
**Ladder:** [[24, 24], [64, 64]]  
**Params (2):** log10_gamma, mean_composition  
**Train/Test (per fidelity):** 400/100

Factory npz: `train_l*.npz`/`test_l*.npz`, keys `x`(N,d) params, `y`(N,prod grid). Aligned MF (same params across fidelities).

## IC provenance note (2026-08-03)

All samples share ONE fixed band-limited IC realization (12 low Fourier modes, seed 5000); per-sample variation comes only from the exported `(log10_gamma, mean_composition)`.
Verified by exact reconstruction: re-solving from the stored condition vector reproduces the on-disk fields at rel-L2 = 0.0 (checked rows 0/1/100/250/399, both batch-wise and per-sample calls).
The condition vector is therefore complete, at the cost of a diversity limitation: the dataset spans one IC pattern family, not the IC distribution.
(The generator's pre-2026-08-03 code seeded the IC by batch position, which made outputs depend on call batching; fixed to an explicit constant seed in `mf_field_extension_data/solvers.py::ch_ic`.)

## ⚠️ Condition vector NOT complete on the shipped arrays (found 2026-09-06)
Re-solving the stored `(log10_gamma, mean_composition)` with the current `solvers.py` (`ch_ic(n, sd, mean)`) reproduces
train row 0 to rel-L2 0.09 but rows 1 and 2 to 1.59 and 1.06, i.e. the shipped initial conditions are not a function of
the stored condition vector (consistent with the pre-2026-08-03 batch-position seeding). The "verified by exact
reconstruction" note above does not hold for the arrays on disk. Consequences: theta does not determine the field, so
surrogate-track scores are bounded by IC variance; the correction track is unaffected (the coarse solve carries the IC).
No LF-abundant variant was generated (new coarse rows would use a different IC family than the paired rows).
