# ADR 0001 (DRAFT) — Upsample-convention classification evidence for 17 benchmark30 datasets

Status: DRAFT evidence file, 2026-08-12.
Purpose: gather generator/solver evidence to assign each dataset ONE reference convention for LF→HF-grid upsampling, extending ADR r2-0001.
The three conventions and their implementations are defined in `mffp_autoresearch/round2/eval/panel_data.py:41-53` (classification sets), `:91-94` (`_legacy_cell_centred_up`), `:97-111` (`_node_aligned_periodic_up`, variant C, with the nesting assert at `:104-105`), and `:136-143` (`_dirichlet_node_up`, variant E), with a byte-identical vendored copy at `mffp_autoresearch/round3/worktrees/r3s2_field_reach/B2/models_r3/r3s2_route/upsample.py:78-108`.
All paths below are relative to the repo root `/resnick/groups/Hippo/ezeng/mf_field/`.
Grid sizes were read from the actual npz shapes (`train_l*.npz`, key `y` row length) under `mf_field/factory_mffp/data/<name>/`, which symlink to `benchmark_42/{core,ext,sharp}/`.

A registration vocabulary note used throughout.
"Node-endpoint" means samples at `x_j = j/(n-1)` including both boundaries (built by `linspace(0, L, n)`), a registration NONE of the three conventions implements exactly; its exact upsampler would be endpoint-aligned bilinear (`zoom(..., grid_mode=False)`).
"Interior-node" means `x_j = (j+1)/(n+1)` with Dirichlet boundary nodes not stored (variant E's assumption).
"Periodic-node" means `x_j = j·L/n` with the endpoint excluded (variant C's assumption).
"Cell-centred" means `x_j = (j+0.5)/n` (legacy_cell's assumption).
Integer HF/LF count ratios imply shared sample LOCATIONS only for periodic-node grids; for cell-centred, interior-node, and node-endpoint grids, nested counts do NOT give coincident samples (except the two endpoints for node-endpoint).

## Summary table

| dataset | solver type | BCs | registration (evidence) | ladder (nested?) | proposal | confidence | red flags |
|---|---|---|---|---|---|---|---|
| poisson_generated | FD 5-point, sparse direct | Dirichlet (4 side values) + centre source patch | interior-node | 16/32/64 (counts nested) | dirichlet_node | medium-high | ifc_poisson (same lineage) is certified legacy_cell; dx inconsistency |
| poisson_local | external (MFRNP release), solver not in repo | unknown (presumed Dirichlet, IFC lineage) | unknown | 16/32/64/96/128 (96 NON-nested) | legacy_cell | medium | L4=96 breaks variant C nesting; no local solver code |
| heat_generated | FD 1-D implicit (Thomas) | Neumann both ends | space-time image: t interior-offset × x node-endpoint | 16/32/64 (counts nested) | legacy_cell | low-medium | y is a (t,x) field; time window differs per level (n/(n-1)) |
| darcy_generated | FD/FV 5-point, harmonic-mean faces | Dirichlet 0 | interior-node (h=1/(n+1)) | 32/64/128 (counts nested) | dirichlet_node | high | KL coefficient field sampled on endpoint grid (inconsistency) |
| allen_cahn_generated | FD 1-D implicit (banded) | Neumann both ends | 1-D node-endpoint | 64/128/256 1-D (counts nested) | legacy_cell (1-D legacy path) | medium | 1-D, not 2-D; dataset README wrongly says "HF grid 16x16" |
| lid_driven_cavity_generated | FD vorticity–streamfunction | no-slip walls + moving lid (Dirichlet velocity) | node-endpoint, boundary vorticity stored | 32/64/128/256 (counts nested) | legacy_cell | medium | truth is node-endpoint (4th convention); shipped 256 rung exceeds generator's LEVELS |
| era5 | measurement (ECMWF reanalysis) | n/a (lat-lon sphere) | lon periodic-node × lat node-endpoint (poles incl.) | 9 heterogeneous non-square rungs (NONE nested) | legacy_cell | low | non-square, non-nested, per-rung sample counts differ (index alignment doubtful) |
| ext__rayleigh_benard_2d | FD streamfunction-vorticity + T | T: Dirichlet top/bottom (stored), Neumann sides; no-slip | node-endpoint (h=1/(n-1)) | 24/64 (NON-nested) | legacy_cell | medium | non-nested; node-endpoint truth |
| ext__wave_2d | FD leapfrog | Dirichlet 0 (stored zero boundary rows) | node-endpoint (h=1/(n-1)) | 24/80 (NON-nested) | legacy_cell | medium | non-nested; node-endpoint truth |
| ext__eikonal_2d | iterative upwind (fast-sweeping-like) | open boundary; T=0 at source node | node-endpoint (h=1/(n-1)) | 24/64 (NON-nested) | legacy_cell | medium | `np.roll` neighbour wrap can leak travel time across the boundary |
| ext__cahn_hilliard_2d | pseudo-spectral FFT semi-implicit | periodic | periodic-node (`endpoint=False`) | 24/64 (NON-nested, 64%24≠0) | **legacy_cell (ACCEPTED APPROXIMATION, spec D4)** — structurally periodic-node, but variant C's nesting assert rejects the 24→64 ladder | high | the ONLY structurally periodic-node dataset whose ladder is not nested; structural truth recorded, campaign classification is legacy_cell |
| ext__pressure_poisson_poiseuille | analytic field (no solver); LF = block-mean(HF)+noise | n/a | cell-centred ((j+0.5)/n explicit) | 8/16/32/64 (nested) | legacy_cell | high | LF is downsampled-HF + noise (paper-faithful, violates the repo LF rule); LF noise floors any exactness check |
| sharp__euler | finite volume (PyClaw; WENO HF / Godunov LF) | extrap (outflow) all sides | cell-centred (`p_centers`) | 32/64/128 (counts nested) | legacy_cell | high | — |
| sharp__burgers_2d | finite volume (PyClaw) | periodic | cell-centred (`p_centers`) | 64/128/256 (counts nested) | legacy_cell | medium-high | periodic topology: legacy clamp is wrong at the wrap seam ("periodic_cell" hybrid would be exact) |
| sharp__shallow_water_2d | finite volume (PyClaw) | extrap (outflow) all sides | cell-centred (`p_centers`) | 32/64/128 (counts nested) | legacy_cell | high | — |
| sharp__porous_medium_2d | FD explicit, periodic roll stencil | periodic (compact support stays interior) | periodic-node (`j·L/res − L/2`) | 64/128/256 (nested, node-coincident) | periodic_node | high | — |
| sharp__helmholtz_2d | FD 5-point (kron), sparse direct | homogeneous Dirichlet, boundary NOT stored | interior-node (h=L/(res+1), x=(j+1)h) | 64/128/256 (counts nested) | dirichlet_node | high | — |

Proposed totals (campaign classifications, resolved per spec D4's accepted-approximation policy): **legacy_cell 12** (incl. ext__cahn_hilliard_2d as accepted approximation), **dirichlet_node 3**, **periodic_node 1** (sharp__porous_medium_2d) — 16 2-D datasets; allen_cahn_generated is 1-D (`KNOWN_GRIDS` `(1, L)`) and joins the 1d_path records.

## Per-dataset evidence

### poisson_generated

Solver type: 5-point finite-difference Laplacian assembled sparse and solved with `spsolve` — `mf_field/generate_all_datasets.py:46-57` (`_build_laplacian`, stencil diag 4 / off −1) and `:84-85`.
Boundary conditions: Dirichlet on all four sides, with the four boundary values drawn as condition parameters and written into a padded array — `mf_field/generate_all_datasets.py:65-69` (`u_pad[0,:]=u_0_x`, `u_pad[-1,:]=u_1_x`, `u_pad[:,0]=u_y_0`, `u_pad[:,-1]=u_y_1`), plus a centre source patch pinned to `u_dirac` at the middle padded node(s) (`:70-75`; a 2×1 patch when n is even).
Grid registration: the stored `n×n` unknowns are the INTERIOR nodes of an `(n+2)×(n+2)` uniform grid whose outermost nodes carry the Dirichlet data (`:65-86`), i.e. `x_j = (j+1)/(n+1)` in the domain whose boundary is the pinned ring — exactly variant E's map.
The boundary values are NOT stored in `y` (only interior `n×n` is returned, `:86`).
A wrinkle: `dx` is computed as `1/(n-1)` from an n-point linspace (`:62-63`) while the padded geometry implies `h = 1/(n+1)`; this mis-scales the source term `b = dx²·g` (`:83`) by `((n+1)/(n-1))²` and so makes the effective continuous problem drift O(1/n) across fidelity levels, but it does not change WHERE the samples sit.
Ladder: LEVELS `[16, 32, 64]` (`mf_field/generate_all_datasets.py:701`), confirmed by npz (`y` row lengths 256/1024/4096); 64%16=0 and 64%32=0, but interior-node grids of nested counts are not node-coincident (variant E does not require it).
Proposal: **dirichlet_node**, confidence medium-high.
Rationale: the discretization is structurally identical to the certified variant E case (`ext__helmholtz_2d`, `panel_data.py:13-14,46`): interior nodes only, boundary pinned one grid step beyond the stored ring.
The confidence is not "high" because `ifc_poisson` — same `li2022ifc` lineage per `mf_field/datasets_summary.csv` (rows `poisson_generated` → li2022ifc, `ifc_poisson` → li2022ifc) — was empirically certified legacy_cell by the round-2 registration audit ("fixing them makes their references WORSE", `panel_data.py:15-17`).
Interior nodes `(j+1)/(n+1)` sit close to cell centres `(j+0.5)/n`, so legacy_cell is nearly consistent too; the two proposals differ by an O(h/2) coordinate skew that grows toward the edges.
Disambiguating check: sample a smooth analytic field at interior-node coordinates for (16, 64), upsample under E and under legacy, and compare errors (the registration-consistent map wins by an order in h near the boundary); additionally compare the real copy-LF nRMSE under both maps on the actual test split, the audit's own criterion.
Red flags: none for nesting; note the dx inconsistency above and the even-n asymmetric source patch as generator quirks, not registration issues.

### poisson_local

Solver type: external data — the dataset ships from the MFRNP release (`niu2024mfrnp`), not from repo code; `mf_field/factory_mffp/data/poisson_local/README.md:3` ("Paper: niu2024mfrnp") and the `poisson_local` row of `mf_field/datasets_summary.csv` (availability `local`, no code repo).
No solver source exists in this repo, so solver type, BCs, and registration cannot be cited from code.
Circumstantial evidence: the condition vector is 5-dimensional like `poisson_generated`'s (u_0_x, u_1_x, u_y_0, u_y_1, u_dirac) — npz `x` shape (64, 5) — and MFRNP's Poisson task descends from the same IFC problem family, so an interior-node Dirichlet FD solve is plausible but UNVERIFIED.
Grid registration: unknown from primary sources.
Ladder: 16/32/64/96/128 from npz shapes (256/1024/4096/9216/16384), matching `README.md:9-14`; 128%96 ≠ 0, so the L4→L5 pair is NON-nested and variant C's assert (`panel_data.py:104-105`) would raise.
Proposal: **legacy_cell**, confidence medium.
Rationale: `heat_local`, the sister dataset with identical provenance (`niu2024mfrnp`, same 5-rung 16..128 ladder per `datasets_summary.csv`), is already certified legacy_cell (`panel_data.py:47`), and the non-nested 96 rung rules out variant C mechanically; absent solver code, the certified-provenance precedent is the strongest available evidence.
Disambiguating check: if MFRNP's generator can be located upstream, read its grid construction; otherwise run the copy-LF nRMSE comparison across the three maps on the stored test split and check exactness/near-exactness patterns at candidate shared coordinates.
Red flags: non-nested 96 rung; classification rests on provenance analogy, not read code.

### heat_generated

Solver type: 1-D implicit finite-difference heat equation stepped with a Thomas tridiagonal solve — `mf_field/generate_all_datasets.py:116-129` (`_thomas`) and `:142-153` (the time loop).
Boundary conditions: Neumann fluxes at both ends, drawn as condition parameters (`neumann_0`, `neumann_1`) and folded in via one-sided modified first/last rows — `mf_field/generate_all_datasets.py:133,147-152`.
Grid registration: the stored field is a SPACE-TIME image, not an (x, y) snapshot.
`_solve_one` returns `u[1:, 1:-1]` of shape `(n, n)` (`:137,154`): rows are the n time steps `t_k = k·dt` for k=1..n (the t=0 initial row is dropped), columns are the n spatial nodes `x_i = i/(n-1)` from `linspace(0, 1, n)` including both endpoints (`:134`), with the two ghost columns used for the Neumann closure excluded.
So the row axis is interior-offset in time and the column axis is node-endpoint in space — a mixed registration matching none of the three conventions.
Worse, `dt = dx = 1/(n-1)` (`:135-136`) and n steps are taken, so the covered time window is `[1/(n-1), n/(n-1)]`: L1 ends at 16/15 ≈ 1.067 while L3 ends at 64/63 ≈ 1.016.
Fidelity levels therefore cover DIFFERENT physical time spans, and no fixed spatial upsampling convention can make LF and HF rows refer to the same instant.
Ladder: LEVELS `[16, 32, 64]` (`:702`), npz-confirmed (256/1024/4096); counts nested.
Proposal: **legacy_cell**, confidence low-medium.
Rationale: the field is not registration-classifiable in the (x, y) sense the conventions assume; the legacy cell-centred path is the certified everything-else default (`panel_data.py:15-17`), and the same-lineage `ifc_heat` (`li2022ifc` in `datasets_summary.csv`) is certified legacy_cell (`panel_data.py:47`).
Disambiguating check: none can cure the time-window mismatch; a synthetic separable field `u(t,x)` sampled per-level under each axis registration would only quantify which convention minimizes the residual misregistration.
Red flags: (t, x) space-time image sold as a "2-D" field (README says "Domain: 2-D PDE"); level-dependent time window is an intrinsic LF↔HF inconsistency worth an explicit campaign note.

### darcy_generated

Solver type: 5-point finite-difference/finite-volume hybrid for `−div(K∇u) = f` with harmonic-mean face transmissibilities, sparse direct solve — `mf_field/generate_all_datasets.py:517-538` (harmonic means at `:521-524`, `spsolve` at `:538`).
Boundary conditions: homogeneous Dirichlet, implemented by keeping the full diagonal contribution while omitting boundary-crossing neighbour terms (`:521-535`: the `if j > 0` / `if j < nx-1` guards with `k_w = k_c` fallback at the boundary).
Grid registration: interior-node — `hx = 1/(nx+1)`, `hy = 1/(ny+1)` (`mf_field/generate_all_datasets.py:509-510`), so the stored `nx×ny` unknowns sit at `x_j = (j+1)/(n+1)` with the Dirichlet boundary one step beyond, and boundary values are not stored (`:539`).
This is exactly variant E's coordinate map (`panel_data.py:136-143`).
Inconsistency note: the log-permeability KL eigenvectors are built and bilinearly resampled on ENDPOINT grids `linspace(0, 1, n)` (`:467-468,483-486`), so the coefficient field is registered differently from the unknowns; this perturbs cross-level consistency of the continuous problem slightly but does not move the solution samples.
Ladder: LEVELS `[32, 64, 128]` (`:707`), npz-confirmed (1024/4096/16384); counts nested, node coincidence not required by E.
Proposal: **dirichlet_node**, confidence high.
Rationale: the `h = 1/(n+1)` interior-node construction is explicit in the code, matching the certified variant E case verbatim.
Disambiguating check (if desired): analytic-field exactness comparison of E vs legacy maps at (32, 128), as for poisson_generated.
Red flags: only the KL-basis registration inconsistency above.

### allen_cahn_generated

Solver type: 1-D semi-implicit finite-difference Allen-Cahn, banded solve — `mf_field/generate_all_datasets.py:343-351` (`solve_banded` with the diffusion matrix from `_build_neumann_banded`).
Boundary conditions: Neumann at both ends via modified first/last diagonal entries — `mf_field/generate_all_datasets.py:333-341` (`main[0] = 1 + r`, `main[-1] = 1 + r`).
Grid registration: 1-D node-endpoint — `x = linspace(-1, 1, nx)` (`:330`), `dx = 2/(nx-1)` (`:344`); all nx nodes including both endpoints are stored (the returned `u` is the full state, `:351`).
Ladder: LEVELS `[64, 128, 256]` (`:705`); npz `y` row lengths are 64/128/256 — this is a 1-D dataset (`datasets_summary.csv` row: `allen_cahn_pde_1d`, resolutions `64; 128; 256`).
Counts are nested, but node-endpoint grids of counts n and 2n share only the two endpoints.
Proposal: **legacy_cell** (i.e. the legacy 1-D `zoom` path), confidence medium.
Rationale: the eval layer routes all 1-D signals through the legacy 1-D path unconditionally (`panel_data.py:180-191`; `upsample.py:147-155`), the same treatment certified for `sharp__sod_1d` (`panel_data.py:47`); a per-dataset override would require a new 1-D endpoint-aligned variant that does not exist today.
The registration truth, however, is node-endpoint: the exact 1-D upsampler would be `zoom(..., grid_mode=False)` (endpoint-aligned), and the legacy `grid_mode=True` call carries the usual (r−1)/2 cell shift for node data.
Disambiguating check: sample `tanh((x−c)/(√2·ε))` (the dataset's own IC family, `:327-331`) at 64 and 256 endpoint nodes and compare 1-D zoom `grid_mode=False` vs `grid_mode=True` reconstruction error; the sharp interface makes the (r−1)/2 shift clearly visible.
Red flags: the dataset README (`mf_field/factory_mffp/data/allen_cahn_generated/README.md:4-9`) wrongly labels it "Domain: 2-D PDE" with "HF grid 16x16" (a sqrt(256) artifact of README autogeneration); any campaign tooling that reshapes `y` to a square grid will silently corrupt this dataset.

### lid_driven_cavity_generated

Solver type: finite-difference vorticity–streamfunction Navier-Stokes with an interior 5-point Poisson solve (sparse LU) and RK2 time stepping to steady state — `mf_field/generate_all_datasets.py:578-600` (Poisson factor on the `(nx−2)×(ny−2)` interior), `:636-664` (`_solve_one`).
Boundary conditions: no-slip stationary walls plus a moving lid (`U_LID` at the top row), imposed through Thom-formula vorticity boundary values — `mf_field/generate_all_datasets.py:612-616` (`omega[-1,:] = 2(ψ[-1]−ψ[-2])/hy² − 2·U_LID/hy` etc.), with ψ = 0 on the boundary (`:608-609`).
Grid registration: node-endpoint — `hx = 1/(nx−1)`, `hy = 1/(ny−1)` (`:638-639`, also `:582-583`), i.e. nodes at `x_j = j/(n−1)` including the walls; the returned field is the FULL vorticity grid including the stored boundary rows (`:664`).
Ladder: generator LEVELS say `[32, 64, 128]` (`:708`), but the shipped benchmark_42 data has FOUR rungs 32/64/128/256 (npz row lengths 1024/4096/16384/65536; `README.md:9-16`), so the shipped set was produced by a run with an extended ladder — a provenance delta to record.
Counts nested; node-endpoint grids share only the boundary nodes.
Proposal: **legacy_cell**, confidence medium.
Rationale: node-endpoint registration with stored Dirichlet-wall data matches none of the three conventions; variant C is topologically wrong (no periodicity), variant E is wrong because boundary nodes ARE stored; the audit-certified everything-else default is legacy_cell, and the physically exact map would be a fourth, endpoint-aligned convention.
Note the boundary rows carry the largest values in the field (lid vorticity ~ 2·U_LID/hy grows with resolution, `:613`), so edge misregistration is NOT benign here; if any dataset motivates adding an `endpoint_node` variant, it is this one.
Disambiguating check: synthetic smooth field sampled at endpoint nodes for (32, 256): compare endpoint-aligned bilinear vs legacy cell-centred zoom; also compare real copy-LF nRMSE, isolating the boundary band (first/last row/column) where the two maps differ most.
Red flags: resolution-dependent boundary vorticity magnitude means LF and HF boundary rows differ by construction (physical, but it inflates any boundary-band error metric); shipped 4th rung exceeds the in-repo generator's LEVELS.

### era5

Solver type: none — measurement/reanalysis data (ECMWF ERA5), `mf_field/factory_mffp/data/era5/README.md:3` and the `era5` row of `mf_field/datasets_summary.csv` (`era5_reanalysis`).
The data is symlinked from seed data (`README.md:19-24`); no generation code exists in the repo.
Boundary conditions: not applicable; the native domain is the sphere on a regular 0.25° lat-lon grid.
Grid registration: the native L9 grid is 721×1440 (`README.md:17`; npz `y` row length 1,038,240 = 721·1440): 721 latitude NODES including both poles (node-endpoint in latitude) and 1440 longitude nodes with the periodic endpoint excluded (periodic-node in longitude).
The physically right convention is therefore MIXED — periodic-node along one axis, node-endpoint along the other — which none of the three variants implements.
The provenance and construction of rungs L1-L8 (144×192, 160×320, 192×288, 180×288, 120×180, 132×156, 80×96, 192×384; `README.md:9-16`) are undocumented in the repo.
Ladder nesting: no rung pair is integer-nested against 721×1440 (721 is odd), and several rungs are not even mutually ordered by refinement.
Sample counts DIFFER per rung (train N = 1222/815/1222/328/328/408/408/408/65 for L1..L9 from npz shapes; test 305/203/305/81/81/101/101/101/7), so the eval layer's index-aligned truncation assumption (`panel_data.py:172-178`) rests on an alignment that cannot be verified from the arrays alone.
Proposal: **legacy_cell**, confidence low.
Rationale: variant C is mechanically impossible (non-nested, and its assert would raise), variant E is semantically wrong (no Dirichlet interior-node construction), and legacy_cell is the certified fallback for exactly this situation ("everything else", `panel_data.py:15-17`); the misfit is acknowledged rather than resolved.
Disambiguating check: none from code; the honest fix is a documented decision that era5 is scored under legacy_cell as an approximation, plus a one-off measurement of how much a periodic-lon wrap changes the copy-LF reference (the wrap seam is one column out of 1440, so the effect is likely tiny).
Red flags: non-square grids (any tooling assuming square will break), no nesting, per-rung sample-count mismatch (index alignment doubtful), 721-row odd dimension breaks any even-padding spectral path, and the L9 arrays are ~10 GB materialized (`README.md:34`).

### ext__rayleigh_benard_2d

Solver type: explicit finite-difference streamfunction-vorticity Boussinesq convection with an interior elliptic solve via sparse LU — `mf_field_extension_data/solvers.py:65-99` (`solve_rayleigh_benard`; `splu(assemble_elliptic(...))` at `:67`).
Boundary conditions: temperature Dirichlet top/bottom with the values STORED in the boundary rows (`T[0,:]=1`, `T[-1,:]=0`, `solvers.py:74,93`), Neumann (insulating) sides (`Tn[:,0]=Tn[:,1]` etc., `:93`), no-slip walls via ψ=0 and Thom vorticity rows (`:78-79,94-95`).
Grid registration: node-endpoint — `h = 1/(n−1)` (`solvers.py:66`) and `xs = linspace(0, 1, n)` (`:68`); the stored field is the full T grid including boundary rows (`:98`).
Ladder: `[24, 24] → [64, 64]` (`benchmark_42/ext/rayleigh_benard_2d/meta.json` "ladder"), npz-confirmed (576/4096); 64 % 24 = 16 ≠ 0 → NON-nested.
Proposal: **legacy_cell**, confidence medium.
Rationale: non-nested rules out variant C mechanically; boundary values are stored so variant E's interior-node premise fails; the registration truth is node-endpoint (fourth convention), for which legacy_cell is the certified stand-in.
The stored Dirichlet rows (exact 1.0 / 0.0 at both fidelities) give a free consistency probe: an endpoint-aligned map carries them onto each other exactly, the legacy map nearly so, variant E visibly not.
Disambiguating check: synthetic smooth field at endpoint nodes for (24, 64) comparing endpoint-aligned vs legacy maps; plus the boundary-row probe above on the real arrays.
Red flags: non-nested ladder (breaks any variant C assert), n_lf = 24 is very coarse for a convection field.

### ext__wave_2d

Solver type: explicit finite-difference leapfrog for `u_tt = c²Δu` — `mf_field_extension_data/solvers.py:118-141` (`solve_wave`; second-order first step at `:132-133`, leapfrog update at `:137`).
Boundary conditions: homogeneous Dirichlet (reflecting), with zero boundary rows explicitly stored (`cur[0,:]=cur[-1,:]=cur[:,0]=cur[:,-1]=0`, `solvers.py:134,138`; also the save description "Dirichlet 0 (reflecting)" at `mf_field_extension_data/generate_datasets.py:220`).
Grid registration: node-endpoint — `h = 1/(n−1)` (`solvers.py:119`) and `xs = linspace(0, 1, n)` (`:120`); the full grid including the zero boundary is returned (`:140`).
Ladder: `[24, 24] → [80, 80]` (`meta.json`; npz 576/6400); 80 % 24 = 8 ≠ 0 → NON-nested.
Proposal: **legacy_cell**, confidence medium.
Rationale: same shape of argument as rayleigh_benard — non-nested kills variant C, stored boundary kills variant E, node-endpoint truth has no dedicated variant, legacy_cell is the certified fallback.
Disambiguating check: as for rayleigh_benard; the stored zero ring is again an exact probe (any map that fails to carry LF's zero ring onto HF's zero ring is misregistered at the edge).
Red flags: non-nested ladder; a snapshot of a hyperbolic field at t=0.4 is phase-sensitive, so LF (24²) discretization dispersion is large — fidelity gap fine, but edge misregistration compounds visibly.

### ext__eikonal_2d

Solver type: iterative upwind Godunov update for `|∇T| = 1/speed` (fast-sweeping-like fixed-point via repeated vectorized sweeps) — `mf_field_extension_data/solvers.py:144-166` (`solve_eikonal`; the two-value Godunov candidate at `:158-161`).
Boundary conditions: open (no boundary condition applied); the source is pinned as T=0 at the nearest grid node `si = round(sy·(n−1))`, `sj = round(sx·(n−1))` (`solvers.py:154,162`).
Grid registration: node-endpoint — `h = 1/(n−1)` (`:145`) and `xs = linspace(0, 1, n)` (`:146`); the full grid is returned (`:165`).
Solver quirk: neighbour minima are taken with `np.roll` (`:156-157`), which wraps periodically, so boundary nodes see the OPPOSITE edge as a neighbour; when the wrapped value is smaller than the true one-sided neighbour, travel time leaks across the boundary as if the domain were a torus.
This is a solver-legitimacy concern (documented here for the record), not a registration ambiguity: the sample coordinates are unambiguous.
Ladder: `[24, 24] → [64, 64]` (`meta.json`; npz 576/4096); 64 % 24 ≠ 0 → NON-nested.
Proposal: **legacy_cell**, confidence medium.
Rationale: identical to the other ext node-endpoint FD datasets: variant C impossible (non-nested), variant E wrong (no interior-node Dirichlet construction; all nodes stored), legacy_cell is the certified fallback for a node-endpoint truth.
Disambiguating check: as above; additionally, the source-node pin `round(sx·(n−1))` lands on DIFFERENT physical points at 24 vs 64 (rounding), an intrinsic LF↔HF inconsistency near the source worth knowing when reading error maps.
Red flags: roll-wrap leak (above); source-node rounding inconsistency across levels; non-nested ladder.

### ext__cahn_hilliard_2d

Solver type: semi-implicit Fourier pseudo-spectral Cahn-Hilliard — `mf_field_extension_data/solvers.py:191-202` (`solve_cahn_hilliard`; `fftfreq` wavenumbers at `:192`, semi-implicit update at `:198-199`).
Boundary conditions: periodic (spectral), also stated in the save description "periodic (spectral)" at `mf_field_extension_data/generate_datasets.py:310`.
Grid registration: periodic-node — the IC (and hence the field) lives on `xs = linspace(0, 2π, n, endpoint=False)` (`solvers.py:183`), i.e. `x_j = j·L/n` with no endpoint duplication; the resolution-independent fixed-seed IC (`solvers.py:169-188`, with the completeness rationale in the docstring at `:170-181`) guarantees the same continuous field is sampled on every grid.
This is exactly variant C's premise: node-registered samples of a periodic domain.
Ladder: `[24, 24] → [64, 64]` (`meta.json`; npz 576/4096); 64 % 24 = 16 ≠ 0 → NON-nested, so variant C's assert (`panel_data.py:104-105`; `upsample.py:91-92`) RAISES on this dataset.
Note the map itself (`coords = k·h/H` with grid-wrap, `panel_data.py:106-111`) is well-defined without nesting; only the assert restricts it, and 24- and 64-node periodic grids still share 8 coincident nodes per axis (every third LF node).
Proposal (resolved per spec D4 accepted-approximation policy): **legacy_cell for the campaign**, with the structural periodic-node truth and the non-nested-ladder blocker documented in the ADR; confidence high.
Rationale: this is the only dataset of the 16 whose solver is genuinely spectral-periodic node-registered but whose ladder is not nested; a correct treatment would need a non-nested periodic-node variant, which spec D2/D4 rule out for this campaign (no new upsample variants; the vendored metric path stays byte-identical).
Structural-truth record: under a correct periodic-node map, upsampled LF would reproduce LF values exactly at every coordinate `j·L/24` coinciding with a `k·L/64` node; the legacy map misses this by a fixed offset — that known, documented misfit is what "accepted approximation" means here.
RESOLVED per spec D4: campaign classification is legacy_cell (accepted approximation); the misfit above is documented in the ADR and carried as a report caveat; no assert is relaxed and no new variant is minted.

### ext__pressure_poisson_poiseuille

Solver type: NONE — the HF field is a closed-form Hagen-Poiseuille pressure (linear in x inside the channel, constant outside) evaluated analytically; LF rungs are BLOCK-MEAN DOWNSAMPLES of the HF field plus uniform noise, replicating the construction of Partin et al. 2022 — `mf_field_extension_data/generate_pressure_poisson_std.py:1-3` (docstring: "LF = block-mean(HF) + uniform noise"), `:27-28` (analytic field), `:30-40` (block-mean + noise per rung); same construction in the documented original `generate_pressure_poisson_mf.py:74-77,104-137`.
Boundary conditions: not applicable (no PDE is solved; the paper's pressure-Poisson problem is represented by its analytic solution).
Grid registration: cell-centred, EXPLICITLY — `yn = (arange(HF)+0.5)/HF`, `X = (arange(HF)+0.5)[None,:]/HF` (`generate_pressure_poisson_std.py:20`; `generate_pressure_poisson_mf.py:87-88`), and each LF value is the mean of an r×r block of HF cells (`std.py:13-15,36-39`), which is precisely the finite-volume/cell-centred restriction whose adjoint is legacy_cell's `grid_mode=True` zoom.
Ladder: `[8, 16, 32, 64]` (`std.py:9`; `meta.json`; npz 64/256/1024/4096); fully nested (64 % 8 = 64 % 16 = 64 % 32 = 0) in the cell-count sense.
Proposal: **legacy_cell**, confidence high.
Rationale: this is the cleanest cell-centred case in the whole set — the generator names the cell centres and constructs LF by exact block averaging; legacy_cell is the matching convention by construction.
Disambiguating check: not needed for registration; note that the U(0, 0.05·range) noise added to every LF rung (`std.py:39`) makes any exactness-style check stochastic rather than deterministic.
Red flags for the campaign: LF is downsampled-HF-plus-noise, NOT an independent coarse solve — faithful to the source paper but in direct tension with the repo's "LF is always a real coarse consistent solve" rule (`mf_field/CLAUDE.md`, methodology section; `benchmark_42/README.md:116` already cautions that this dataset sits just above the copy-LF threshold); the ADR should record that this dataset's fidelity gap is noise, not discretization error.

### sharp__euler

Solver type: finite volume via Clawpack/PyClaw — HF uses `SharpClawSolver2D` (WENO) and LF the first-order Godunov `ClawSolver2D`, both with the `euler_4wave_2D` Riemann solver — `mf_field_eloise_data/SURF_2026-main/mffp_sharp/src/mffp_sharp/pdes/euler.py:62-67`.
Boundary conditions: zero-order extrapolation (outflow) on all sides — `solver.all_bcs = pyclaw.BC.extrap` (`euler.py:69`).
Grid registration: cell-centred — the domain is `pyclaw.Domain([0,0], [1,1], [res,res])` (`euler.py:71`), i.e. res×res finite-volume CELLS, and the IC is evaluated at `state.grid.p_centers` (`euler.py:41`), PyClaw's physical cell centres `(j+0.5)/res`; the stored field is cell-average data.
Ladder: `[32, 64, 128]` (`meta.json` at `benchmark_42/sharp/euler/meta.json`; npz 1024/4096/16384); counts nested, though cell centres of nested counts do not coincide (legacy_cell's map does not need them to).
Proposal: **legacy_cell**, confidence high.
Rationale: textbook finite-volume cell-centred data with outflow boundaries — the exact profile legacy_cell was certified for (clamped edges even match the extrapolation BC's behaviour at the domain edge); this mirrors the already-certified FV members of LEGACY_CELL_DATASETS.
Red flags: none for registration; note LF and HF differ in solver ORDER as well as grid (WENO vs Godunov, `euler.py:65-67`), which is a fidelity-definition note, not a convention issue.

### sharp__burgers_2d

Solver type: finite volume via PyClaw, 2-D branch — `SharpClawSolver2D` (HF) / `ClawSolver2D` (LF) — `mf_field_eloise_data/SURF_2026-main/mffp_sharp/src/mffp_sharp/pdes/burgers.py:34-35`.
Boundary conditions: periodic on all sides — `solver.all_bcs = pyclaw.BC.periodic` (`burgers.py:38`).
Grid registration: cell-centred — `pyclaw.Domain([0,0], [1,1], [res,res])` (`burgers.py:39`) with the IC at `state.grid.p_centers` (`burgers.py:42`).
Ladder: `[64, 128, 256]` (`meta.json`; npz 4096/16384/65536); counts nested.
Proposal: **legacy_cell**, confidence medium-high.
Rationale: registration is unambiguously cell-centred, so legacy_cell is the only variant whose coordinate map is correct; variant C would impose the known (r−1)/2 half-cell shift on cell-centred data (the exact defect ADR r2-0001 fixed in the other direction).
The residual defect is topological: the domain is periodic, and legacy_cell clamps the wrap seam, so a one-cell-wide band at each edge is interpolated against the wrong neighbour.
The fully exact convention would be a FOURTH variant, "periodic_cell" (cell-centred bilinear with grid-wrap), which currently exists nowhere in the eval layer.
Disambiguating check / defect sizing: on a stored LF/HF test pair, compare copy-LF error restricted to the outermost cell band under legacy_cell vs a periodic-cell prototype (`map_coordinates(..., mode="grid-wrap")` at cell-centre coordinates); if the band contribution is material, the ADR should mint periodic_cell rather than misclassify.
Red flags: periodic seam under a clamped convention; decide explicitly rather than by default.

### sharp__shallow_water_2d

Solver type: finite volume via PyClaw, 2-D branch — `SharpClawSolver2D` (HF) / `ClawSolver2D` (LF) — `mf_field_eloise_data/SURF_2026-main/mffp_sharp/src/mffp_sharp/pdes/shallow_water.py:27`.
Boundary conditions: zero-order extrapolation (outflow) on all sides — `solver.all_bcs = pyclaw.BC.extrap` (`shallow_water.py:30`).
Grid registration: cell-centred — `pyclaw.Domain([0,0], [1,1], [res,res])` (`shallow_water.py:31`) with the IC (radial dam break) at `state.grid.p_centers` (`shallow_water.py:34`).
Ladder: `[32, 64, 128]` (`meta.json`; npz 1024/4096/16384); counts nested.
Proposal: **legacy_cell**, confidence high.
Rationale: identical structural profile to sharp__euler — FV cell centres with outflow edges; legacy_cell's clamped cell-centred zoom is the matching convention.
Red flags: none.

### sharp__porous_medium_2d

Solver type: explicit finite difference for the porous-medium equation `u_t = Δ(u^m)` with a periodic 5-point roll stencil and CFL substepping — `mf_field_eloise_data/SURF_2026-main/mffp_sharp/src/mffp_sharp/pdes/porous_medium.py:23-27` (`_laplacian` via `np.roll`), `:30-43` (`_solve`), with the docstring stating "Periodic stencil (np.roll) on a domain large enough that the compact support stays interior" (`porous_medium.py:8-10`).
Boundary conditions: periodic (by stencil); physically inert because the solution has compact support away from the boundary.
Grid registration: periodic-node — `xs = np.arange(res) * L / res − L/2` (`porous_medium.py:75`), i.e. `x_j = j·L/res` with the endpoint excluded, `h = L/res` (`:33`); the same analytic IC is evaluated on each grid (`:69-78`), so every level samples the same continuous field at node coordinates.
Ladder: `[64, 128, 256]` (`meta.json`; npz 4096/16384/65536); nested, and for periodic-node grids nesting means true node coincidence: LF node j sits exactly at HF node r·j.
Proposal: **periodic_node** (variant C), confidence high.
Rationale: this matches variant C's premise exactly — node-registered periodic domain, nested ladder — the same profile as the certified `sharp__allen_cahn_2d` / `sharp__fisher_kpp_2d` / `sharp__cahn_hilliard` set (`panel_data.py:41-45`); variant C is exact at shared nodes here (`panel_data.py:100`), while legacy_cell would inject the half-cell shift onto a sharp free boundary, the most misregistration-sensitive feature type.
Disambiguating check (confirmatory): verify `up[::r, ::r] == lf` bit-for-bit on a stored pair, variant C's own exactness property.
Red flags: none; the wrap seam is inert (compact support), the assert is satisfied.

### sharp__helmholtz_2d

Solver type: 5-point finite-difference Helmholtz `−Δu − k²u = f` assembled by Kronecker products and solved by sparse direct factorization — `mf_field_eloise_data/SURF_2026-main/mffp_sharp/src/mffp_sharp/pdes/helmholtz.py:30-38` (`_operator`), `:41-45` (`_solve` via `spsolve`), docstring `:6-7`.
Boundary conditions: homogeneous Dirichlet, boundary NOT stored — docstring `helmholtz.py:3` ("homogeneous Dirichlet") and `:9` ("Field stored: u (real) on the interior grid").
Grid registration: interior-node — `h = domain_size/(res+1)` and `xs = (arange(1, res+1))·h` (`helmholtz.py:23-24`, same `h` in the operator at `:31`), i.e. `x_j = (j+1)/(res+1)·L`, exactly variant E's coordinate map (`panel_data.py:136-143`).
LF legitimacy is explicit: "LF = a genuine coarse-grid discretization of the SAME continuous BVP … never a downsample of the fine solution" (`helmholtz.py:10-11`).
Ladder: `[64, 128, 256]` (`meta.json`; npz 4096/16384/65536); counts nested, node coincidence not required by variant E.
Proposal: **dirichlet_node** (variant E), confidence high.
Rationale: byte-for-byte the same discretization pattern as the already-certified `ext__helmholtz_2d` (`panel_data.py:13-14,46`; `mf_field_extension_data/solvers.py:26-28,46-49` uses the identical `h = 1/(n+1)`, `x ∈ [h, 1−h]` construction) — the precedent dataset for variant E.
Disambiguating check: not needed; optionally repeat the analytic-field E-vs-legacy comparison at (64, 256).
Red flags: none; note the oscillatory field (k ∈ [15, 25], `meta.json` note) makes ANY misregistration expensive, so getting E right matters more here than on smooth datasets.

## Cross-cutting red flags for the campaign

Non-nested ladders that would trip variant C's assert (`panel_data.py:104-105`): poisson_local (L4 = 96 vs 128), ext__rayleigh_benard_2d (24→64), ext__wave_2d (24→80), ext__eikonal_2d (24→64), ext__cahn_hilliard_2d (24→64), and every era5 rung pair.
Only ext__cahn_hilliard_2d among these is structurally periodic-node, so it is the one dataset where the assert blocks the RIGHT convention; the others fall to legacy_cell on independent grounds.
Non-square grids: era5 only (all nine rungs); any square-reshape assumption breaks there, and allen_cahn_generated breaks it differently by being 1-D while its README claims 16×16.
Sample-count misalignment across rungs: era5 only (train 1222/815/1222/328/328/408/408/408/65); everything else is 400/100 per rung (LDC: 40/10 visible in npz train shapes).
Missing meta.json: all seven core datasets have README.md only (no meta.json); the ext and sharp sets all carry meta.json.
LF-construction rule violation: ext__pressure_poisson_poiseuille's LF rungs are noisy block-means of HF, not coarse solves (paper-faithful; documented at `generate_pressure_poisson_std.py:3`).
A recurring gap in the convention vocabulary: five datasets (heat_generated's x-axis, lid_driven_cavity_generated, ext__rayleigh_benard_2d, ext__wave_2d, ext__eikonal_2d, plus allen_cahn_generated in 1-D and era5's latitude axis) are truly node-endpoint, a registration none of the three variants implements; the ADR should either mint an `endpoint_node` variant (endpoint-aligned bilinear, `zoom(..., grid_mode=False)` semantics) or record explicitly that legacy_cell is accepted as an approximation for that class.
Similarly, sharp__burgers_2d motivates a `periodic_cell` variant (cell-centred bilinear with grid-wrap) if its seam-band error proves material.
Lineage tension to adjudicate: proposing dirichlet_node for poisson_generated (and structurally for darcy_generated) sits next to the round-2 audit's empirical certification of the same-lineage ifc_poisson/ifc_heat as legacy_cell (`panel_data.py:15-17,47`); before flipping any li2022ifc-lineage dataset, run both the synthetic interior-node exactness check and the real copy-LF nRMSE comparison, per the audit's own criterion that a convention change must not make the reference worse.
