---
name: anisotropic-spectral-modes-fno
description: Canonical (modes_h, modes_w) parameterization for SpectralConv2d on non-square grids — Li 2020 FNO, neuraloperator library, and F-FNO (Tran 2023) abstraction
metadata:
  type: reference
tags:
  - factory
  - source
  - fno
  - spectral-conv
source: factory-archivist
date: 2026-06-02
cycle: cycle-007
---

# Anisotropic Spectral Modes in FNO Literature

Compiled during cycle-007 R1.5 to back the constructor-fix recommendation for
`models/fno_coregionalization/model.py` (the `FNOCoregionalization.__init__`
that lost its anisotropic-modes signature in a `git reset`).

## Canonical pattern: Li et al. 2020 FNO

- **Citation**: `li2020fno` — [arXiv:2010.08895](https://arxiv.org/abs/2010.08895).
- **Constructor signature**: `SpectralConv2d(in_ch, out_ch, modes1, modes2)`.
- **Semantics**:
  - `modes1` truncates **height-axis** Fourier modes. Under `rfft2` (which
    leaves the full H axis intact), the kept modes are taken symmetrically
    as the `[:mh, :]` and `[-mh:, :]` blocks to preserve the conjugate-
    symmetric `+k_y / -k_y` pair.
  - `modes2` truncates **width-axis** Fourier modes — the half-spectrum
    `[:, :mw]` from `rfft2`'s `W//2+1`-length axis.
- The two axes are **independent integer knobs**. There is no canonical
  constraint that `modes1 == modes2`; rectangular grids motivate splitting.

## Reference implementation: neuraloperator library

- **URL**: <https://neuraloperator.github.io/dev/user_guide/fno.html>.
- Public PyPI package; identical `(modes1, modes2)` convention as Li 2020.
  Confirms the split is the published reference — not a project-local choice.

## Factorized variant: F-FNO (Tran et al. ICLR 2023)

- **Citation**: `tran2023ffno` — [arXiv:2111.13802](https://arxiv.org/abs/2111.13802);
  [code: github.com/alasdairtran/fourierflow](https://github.com/alasdairtran/fourierflow).
- F-FNO **factorizes** the spectral conv across dimensions: separate 1-D
  FFTs over each axis with independent (smaller) weight tensors. Reports
  ≈85% improvement over vanilla FNO.
- This is an **architectural refactor** (separable spectral layers), not
  just a mode-truncation rename. F-FNO is **out of scope** for the cycle-007
  constructor fix.
- Documents that the `(modes_h, modes_w)` split is the well-recognised
  right abstraction for non-square grids — a defensible follow-up direction.

## In-tree references (already correct; bug is local to one wrapper)

- `models/mf_fno_transfer_bar/model.py:30-48` —
  `SpectralConv2d(in_ch, out_ch, modes_h, modes_w)`, rectangular- and
  1-D-safe. Verified correct; ships in the bar family.
- `models/fno_coreg_residual/model.py:43-80` — same anisotropic pattern,
  verified correct.
- `models/fno_coregionalization/model.py:28-79` — `SpectralConv2d` **and**
  `FNOBlock` **already accept `(modes_h, modes_w)`**. The bug is **only**
  in the outer `FNOCoregionalization.__init__` (lines 82-101): it still
  declares `modes: int, grid_size: int` and passes `modes, modes` into the
  inner block at line 100. ≤15-LOC edit, not a refactor.

## Why IFC does not constrain the spectral-mode choice

- **Citation**: `li2022ifc` — [arXiv:2207.00678](https://arxiv.org/abs/2207.00678).
- IFC uses a **GP-ODE basis**, not FNO; the upstream code
  (`references/external_sota/ifc/upstream/core/inf_fid_ode_2d.py`) confirms
  it does **NOT** use spectral convolutions at all.
- The coregionalization head sits on top of any backbone, so the
  `(modes_h, modes_w)` choice is **entirely a backbone-side decision**,
  decoupled from the basis-head design. The fno+IFC combination is
  in-repo only — no external implementation to copy.

## How to apply (Builder)

Mirror the verified pattern from `mf_fno_transfer_bar/model.py:62-94`:

- Outer `FNOCoregionalization.__init__` accepts
  `modes_h: int, modes_w: int, grid: tuple[int, int]`.
- Propagate `(modes_h, modes_w)` into the inner `FNOBlock`s (already
  anisotropic).
- Build the `coord_grid` buffer from `grid = (H, W)` instead of scalar
  `grid_size`. In `forward()`, replace `H = W = self.grid_size` with
  `H, W = self.grid`.
- **Do not** add a fallback `modes=` kwarg — all callers live inside
  `models/fno_coregionalization/` and the smoke harness is the only call
  site (`smoke_eval.py:265`).

## Related notes

- [[li2020fno]] — FNO backbone canonical reference (pre-existing in archive).
- [[li2022ifc]] — Source paper for `ifc_*` datasets and the basis head.
- [[failure-analysis-cycle-007]] — Diagnoses `COMMITTED_TREE_BROKEN` as
  the dominant cycle-007 failure mode.
- [[cycle-007-constructor-fix-pattern]] — Cross-cycle pattern: dirty
  edits lost via `git reset` resurface as constructor mismatches.
