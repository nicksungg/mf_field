# Per-dataset defect status — all 42 datasets

Status of every dataset in this benchmark against the defect classes found between 2026-07-30 and 2026-08-06.
Audited 2026-08-06.

Each dataset falls into exactly one of four categories.
The category reflects the **dataset's own data lineage**.
Live harness or publication issues that affect a dataset without being defects *in* it are carried in a separate ⚠ column and summarised at the end.

| category | count |
|---|---|
| 1 — nothing wrong | 16 |
| 2 — fixed by regenerating | 8 |
| 3 — fixed by patching code | 9 |
| 4 — needs to be fixed | 9 |
| **total** | **42** |

## How this was verified

- Every dataset was confirmed to ship **native-grid** arrays at each fidelity level (e.g. `sharp/allen_cahn_2d` = $64^2$ / $128^2$ / $256^2$).
  No pre-aligned HF-grid copies exist anywhere in `benchmark_42/` or `mf_field/sharp_generated/`.
- Registration conventions come from the per-PDE dispatch in `mffp_sharp/common/ladder.py` and the per-dataset dispatch in `mffp_autoresearch/round2/eval/panel_data.py` (ADR r2-0001).
- Regeneration was established by hashing all 416 files of the corrected HuggingFace release (`eloisezeng/mf_field`) against the frozen defective release (`nicksung/mf_field`, 2026-07-28) and against the local working tree.

## 1 — Nothing wrong (16)

These come from finite-volume solvers, where the cell-centred lift was already the correct convention.
The half-pixel registration defect never applied to them.

| dataset | note |
|---|---|
| `core/poisson_generated` | — |
| `core/heat_generated` | — |
| `core/burgers_generated` | flagged operator-hard — a disclosed property, not a defect |
| `core/advection_diffusion_generated` | flagged copy-LF-trivial |
| `core/allen_cahn_generated` | — |
| `core/darcy_generated` | — |
| `core/lid_driven_cavity_generated` | — |
| `core/poisson_local` | audit-certified `LEGACY_CELL` |
| `core/heat_local` | audit-certified `LEGACY_CELL` |
| `core/fluid` | audit-certified `LEGACY_CELL` |
| `sharp/euler` | PyClaw finite-volume → `cell_centered` was already right |
| `sharp/sod_1d` | as above; also certified `LEGACY_CELL` in the eval dispatch |
| `sharp/burgers_1d` | as above |
| `sharp/burgers_2d` | as above |
| `sharp/shallow_water_1d` | as above |
| `sharp/shallow_water_2d` | as above |

## 2 — Fixed by regenerating (8)

None of these regenerations was driven by the half-pixel defect.
The 2026-08-03 wave ran *under* the landed ladder fix (`c29c269`, 15:02 EDT, before the swap at 15:31 EDT) so that anything regenerated afterward would be correct by construction — but the fix contributed zero bytes, since the ladder fix's own acceptance test records `a_raw_bit_identical = PASS` on every audited dataset.

| dataset | what was wrong | ⚠ open |
|---|---|---|
| `core/burgers_param_generated` | IC phases unexported; re-derived through the generation RNG chain and appended, no re-solve (reconstruction rel-L2 = 0.0 over all 500 rows) | — |
| `core/ifc_heat` | parameter vectors drawn independently per fidelity, so no sample existed at more than one fidelity and $HF - LF$ was undefined; regenerated with nested parameter sets | — |
| `core/ifc_poisson` | same | — |
| `sharp/allen_cahn_1d` | condition-vector incompleteness — per-sample IC coefficients consumed but not exported | `WORK_CAP` |
| `sharp/allen_cahn_2d` | condition incompleteness (2026-08-03), **plus** 22 task-void test rows trimmed to $n = 78$ (ADR r3-0003 D1, 2026-08-06) | **stale on HuggingFace** |
| `sharp/fisher_kpp_1d` | condition incompleteness | `WORK_CAP` |
| `sharp/fisher_kpp_2d` | condition incompleteness | — |
| `sharp/phase_field_crystal_2d` | condition incompleteness (2026-08-03), **plus** NO_GAP → crystalline-box regeneration, median bottom-rung gap 1.2e-6 → 9.8e-3 (ADR r3-0002, 2026-08-06) | **stale on HuggingFace** |

`phase_field_crystal_2d` is the one regeneration that traces back to the half-pixel repair, and only indirectly.
The corrected node-aligned reference collapsed its copy-LF gap from 0.0448 to 7.1e-06, exposing that the dataset had no fidelity gap at all.
That verdict drove `true_gap_sweep`, which then **overturned** the original defect note's diagnosis: the note blamed a resolution-independent continuous symbol and prescribed a coarser LF rung, but the real cause was sampling composition — under the production box roughly half the samples satisfied $\sigma = -(r + 3\bar\psi^2) < 0$, sat in the uniform phase, and decayed to flat fields.
The regeneration changed the sampling box, not the registration.

## 3 — Fixed by patching code (9)

All half-pixel registration.
Repaired in `mffp_sharp/common/ladder.py` (per-PDE convention dispatch, raising on an unclassified PDE rather than defaulting) and in `round2/eval/panel_data.py` (per-dataset dispatch).
No data change was needed or made, because the shift lived only in the generator's unpublished aligned copies, the self-reported fidelity-gap metrics, and the eval layer's copy-LF reference.

| dataset | correct convention | ⚠ open |
|---|---|---|
| `sharp/cahn_hilliard` | `node_periodic` | outlier-dominated cell — top-5 of 100 test rows carry 76% of the copy-LF denominator; every claim must report the bootstrap min-detectable-delta (ADR r3-0003 D2) |
| `sharp/porous_medium_1d` | `node_periodic` | — |
| `sharp/porous_medium_2d` | `node_periodic` | — |
| `sharp/kuramoto_sivashinsky_2d` | `node_periodic` | — |
| `sharp/kuramoto_sivashinsky_1d` | `node_periodic` | `WORK_CAP` |
| `sharp/nls_1d` | `node_periodic` | `WORK_CAP` |
| `sharp/sine_gordon_1d` | `node_periodic` | `WORK_CAP` |
| `sharp/helmholtz_2d` | `node_dirichlet` | — |
| `ext/helmholtz_2d` | `node_dirichlet` | **closed-form solvable** — HF test fields reproduce to 2.2e-13 via two FFTs, so an exact-operator method trivialises it with no learning involved |

## 4 — Needs to be fixed (9)

| dataset | what's wrong | severity |
|---|---|---|
| `core/era5` | **byte-identical duplicate of `pm_test`** — all 18 npz match by sha256. Separately, the $721\times1440 \to 128\times256$ target resample retains 3.2% of pixels through a two-pixel stencil and aliases everything above the new Nyquist | active |
| `core/pm_test` | same, both ways | active |
| `ext/cahn_hilliard_2d` | periodic-spectral nodes; **never assigned a registration convention** in either dispatch | latent |
| `ext/eikonal_2d` | `linspace(0, 1, n)` endpoint-inclusive nodes; unclassified | latent |
| `ext/gray_scott_2d` | periodic `np.roll` stencil nodes; unclassified. Also MF-useless (LF–HF pearson 0.008) | latent + degenerate |
| `ext/kuramoto_sivashinsky_1d` | periodic-spectral nodes; unclassified. Also MF-useless and operator-hard | latent + degenerate |
| `ext/rayleigh_benard_2d` | node-sampled; unclassified | latent |
| `ext/wave_2d` | node-sampled; unclassified | latent |
| `ext/pressure_poisson_poiseuille` | convention never audited — the solver is not in `mf_field_extension_data/solvers.py` | latent |

**Latent** means the eval layer *raises* on an unclassified 2-D dataset rather than silently defaulting.
These are not producing wrong numbers today, but no convention has been assigned to them, and the pre-round-1 ELO pool scored them under the legacy cell-centred map.

## Cross-cutting items not attributable to any single dataset

### `WORK_CAP = 256` is still live

Every model family caps the working grid at a longest side of 256 (`mf_field/factory_mffp/models/_common/fire_core.py:140`, and a copy in each family's `smoke_eval.py`).
Any dataset with a side above 256 has its **scored target** pushed through the same defective `align_corners=False` map that the registration note identified.
That is 7 datasets: `core/era5`, `core/pm_test`, and the five sharp 1D sets at 512 points (`allen_cahn_1d`, `fisher_kpp_1d`, `kuramoto_sivashinsky_1d`, `nls_1d`, `sine_gordon_1d`).

The comment at `mf_field/factory_mffp/models/fno_coreg_conditioned/smoke_eval.py:64` reads "only era5/pm_test exceed it".
That is wrong — the 512-point 1D datasets exceed it too.

### Two datasets are stale on HuggingFace

`eloisezeng/mf_field` was uploaded 2026-08-05 23:48 – 2026-08-06 02:42 UTC.
40 of 42 datasets are byte-identical to the local working tree.
Two diverge, both from round-3 work that postdates the upload:

- `sharp/allen_cahn_2d` — test split only (ADR r3-0003 trim, commit `792d243`); train splits still match.
- `sharp/phase_field_crystal_2d` — all arrays plus `README.md` and `meta.json` (ADR r3-0002 box swap, commit `c677b00`).

Both need a re-push, after which `MANIFEST.csv` must be recomputed — it is derived data and has gone stale silently once before.

### `README.md` undercounts the changed datasets

`README.md` states "Seven datasets changed; the other 35 are byte-identical" for the 2026-08-05 corrected release.
The content hashes say **eight**: the five IC-encoded sharp datasets, the two re-paired `ifc` datasets, and `core/burgers_param_generated`, whose npz do change even though its parameters were appended without re-solving.

## Reproducing this

```bash
# category assignment inputs
sed -n '43,63p' mf_field_eloise_data/SURF_2026-main/mffp_sharp/src/mffp_sharp/common/ladder.py   # per-PDE conventions
sed -n '40,48p' mffp_autoresearch/round2/eval/panel_data.py                                      # per-dataset conventions

# the half-pixel fix changes no native array
python -c "import json;print(json.load(open('mffp_autoresearch/ladder_fix_proposal/verification_results.json'))['checks'])"

# which datasets actually changed between releases
MFFP_HF_REPO=nicksung/mf_field python hf_download_benchmark_42.py   # then diff sha256 against eloisezeng/mf_field
```
