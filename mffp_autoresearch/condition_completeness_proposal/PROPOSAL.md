# Fix proposal — condition-vector incompleteness in the sharp panel datasets

**To:** Nicholas (mentor — the generator surface is mentor-owned; this is a recommendation package, nothing has been landed).
**From:** Eloise's agent, 2026-08-03.
**Scope:** `mffp_sharp/pdes/{phase_field_crystal,fisher_kpp,allen_cahn}.py` (`sample_configs` / `generate_sample`), and the pattern they share with the other 12 package-path PDEs.
**References:** ADR r2-0003 (condition-vector incompleteness); round-2 report §5.1; `mf_field_eloise_data/generate_learnable.py` (the 2026-06-28 fix, applied to 9 variants); companion package `../ladder_fix_proposal/`.

## What the defect is

Three of the six round-2 panel datasets draw a **fresh random initial condition per sample and never export it**.

```python
# mffp_sharp/pdes/fisher_kpp.py — the same three lines appear in allen_cahn.py and phase_field_crystal.py
rng = np.random.default_rng(spec["seed"])            # seed = base + sample index
ic_coarse = 0.5 + 0.5 * (2 * rng.random(shape) - 1)  # white noise on the coarse grid
...
cond = np.array([spec["D"], spec["r"]])              # <- the IC is not in here
```

The exported condition vector carries only the physical scalars — `[D, r]` for fisher_kpp, `[r, mean_density]` for pfc, `[eps, mobility, mean_composition]` for allen_cahn.
The realised IC, which is what actually decides the pattern the solver evolves into, lives only in the fields.
So `condition → HF` is a stochastic map on those datasets: a deterministic model can at best estimate the conditional mean, and skill → 1 is unreachable in principle, not merely unreached.

This is not a subtle inference. `certify_condition_completeness.py` finds the closest pair of training samples in standardized condition space and compares their fields:

| dataset | IC params exported | closest-pair condition distance | their relative field difference | verdict |
|---|---|---|---|---|
| `sharp__phase_field_crystal_2d` | 0 | 0.0124 | **1.149** | INCOMPLETE |
| `sharp__fisher_kpp_2d` | 0 | 0.0124 | **0.411** | INCOMPLETE |
| `sharp__allen_cahn_2d` | 0 | 0.0511 | **0.118** | INCOMPLETE |
| `sharp__cahn_hilliard` | 16 (`ic_c0…15`) | 2.8222 | 0.694 | **COMPLETE** (see below) |

Two pfc samples that agree on their conditions to 1.2 % of one standard deviation have fields that differ by more than their own magnitude.

## Root cause: the fix exists, and it was applied on one code path only

The identical bug was found on 2026-06-28 and fixed — the header of `mf_field_eloise_data/generate_learnable.py` states it verbatim: *"these drew a fresh RANDOM band-limited IC per sample but only exposed physical params (L, eps, delta, ...) as x -> the field is set by the unseen IC seed -> rel-L2 > 1 for every model. Fix: the IC is built deterministically from a small set of low Fourier-mode coefficients, and THOSE coefficients are stored in x."*

That fix was written as a **standalone script that imports the package's solvers but bypasses the package's `sample_configs`/`generate_sample`**.
It regenerated 9 variants (KS 1d/2d, cahn_hilliard, sine_gordon 1d/2d, swift_hohenberg 1d/2d, kdv, nls); the originals were moved to `sharp_generated/_unlearnable_backup/`.
The package itself was never changed, so every dataset generated afterwards through the documented pipeline (`mffp_sharp/generate.py`) silently reproduced the original convention — which is exactly what pfc, fisher_kpp and allen_cahn are.
The generation path is still legible in the metadata: the package-path datasets carry a `module` key, and cahn_hilliard instead carries the script's note `"IC-encoded cond (low Fourier modes) so field=f(x) is learnable; fixes rel-L2>1 bug"`.

A secondary reason the three were not caught by the same sweep: the 2026-06-28 symptom was **rel-L2 > 1 for every model**.
pfc / fisher_kpp / allen_cahn do not trip that symptom, because their fields are level-dominated and `mean_density` / `mean_composition` predicts the bulk — a model scores respectably while still being blind to the driver that sets the pattern.
The bug was triaged by symptom rather than by construction, so the datasets that hid the symptom kept the bug.

## The fourth dataset is a misclassification, and it changes a round-2 conclusion

Round-2 report §5.1 and PROFESSOR_UPDATE_2026-08-02 §3 say the condition vector is not complete on **4 of 6** panel datasets, extending the finding to cahn_hilliard on the strength of the r2s2-B3 paired-LF cosine measurement.
That extension is wrong, and it is wrong in the specific way the round's own §6 "unidentifiable phrasing rule" was written to prevent.

cahn_hilliard's IC is *built from* `ic_c0…ic_c15` by construction, so its field must be a deterministic function of its condition vector.
`certify_condition_completeness.py` verifies this directly rather than arguing it: rebuild the IC from the stored `x`, re-solve, compare to the on-disk field.

```
rel-L2(reconstructed from x alone, vs on-disk field)  =  1.7e-14, 5.2e-15, 1.7e-14   (3 samples)
control — same physics, another sample's IC coefficients =  1.346
```

Machine precision, against a control of 1.35 that shows what a genuinely missing driver looks like.
The condition vector on cahn_hilliard is **complete**.

What r2s2-B3 measured there is therefore an *identifiability* limit, not an information limit, and this proposal's own witness row says why: cahn_hilliard's closest pair in 19-dim condition space sits at standardized distance **2.82** (median pair distance 6.12) — 400 training points spread over 19 dimensions have no near-neighbour support anywhere.
The information is present in `x` and is not recoverable from this many rows at this dimension. That is the round's own "support-not-identifiability rule" (§6, r2s4-B2).

This matters beyond phrasing, because cahn_hilliard is the **only dataset that survives the r2s3-B4 ceiling gate and the only grade A** in the round's value-of-LF table.
Under the corrected reading, LF's grade-A contribution on cahn_hilliard is not "LF supplies information the condition vector lacks" — it is "LF supplies a *statistically efficient encoding* of information the condition vector already contains but that 400 rows in 19 dimensions cannot identify."
Both are real and useful results; they are different claims, they generalise differently, and only the second one is what was measured.

## Recommended fix (three parts, in order)

1. **Land the IC encoding in the package, not beside it.**
   Move `generate_learnable.py`'s `ic_1d` / `ic_2d` into `mffp_sharp/common/`, and have each stochastic-IC PDE's `sample_configs` draw the IC coefficients as part of the Latin-hypercube design and its `generate_sample` return them in `cond` / `param_names`.
   This is the same change that was already validated on 9 variants; the point is to put it where new datasets inherit it instead of where they can miss it.
   Note that a *repair* of the existing pfc / fk / ac files is not available: their ICs are full white-noise fields on the coarse grid (64² = 4096 degrees of freedom), so no small condition vector can describe them after the fact, and a complete one would violate the ≤ ~10-dimension methodology rule. They must be regenerated with a band-limited IC.

2. **Make the certificate a generation gate.**
   `certify_condition_completeness.py` is training-free and takes under a minute per dataset.
   Run it at the end of generation, write the result into `meta.json` (`condition_completeness: {verdict, rel_L2, witness}`), and fail generation on INCOMPLETE unless the dataset is *deliberately* stochastic and says so.
   The claim "each `meta.json` certifies the HF field is a learnable function of the condition vector" appeared in the round-2 launch spec §4 and in program §12.1/§13.1 and was false for three of six datasets; a certificate in the file makes that claim checkable rather than asserted.

3. **Record the stochastic-map semantics for any dataset kept that way on purpose.**
   A stochastic-IC dataset is a legitimate benchmark — it is just a benchmark for *distributional* prediction, judged against the conditional-mean floor rather than against skill 1.0.
   If pfc / fisher_kpp / allen_cahn are meant to stay stochastic, they should say so in `meta.json` and ship their aleatoric floor, so no future round re-derives it (r2s4-B1 measured it at ~38.6–42.1 / ~11.44 / ~132.7 in copy-LF skill units).

## Cost

Regeneration of the three datasets is solver time only: 500 samples × 3 ladder levels each, the same cost as the original generation, with no algorithmic change to the solvers.
Landing the encoding in the package is a small refactor (two helper functions plus three `sample_configs` / `generate_sample` pairs) and is covered by the existing `mffp_sharp` test suite once a completeness test is added per PDE.
Nothing here requires re-running any round-2 model: the round's numbers stand as measurements of the panel as it exists, and the correction is to their *interpretation* on cahn_hilliard.

## Implementation status (2026-08-03, same day — awaiting sign-off; nothing regenerated at production scale)

All three parts of the recommended fix are implemented on branch `mffp-trunk-eloise` and verified locally; see `IMPLEMENTATION_PLAN.md` for the task-by-task record and `SIGNOFF.md` for the one-page ask.

1. **IC encoding lives in the package.** `mffp_sharp/common/ic_encoding.py` (math byte-identical to `generate_learnable.py`, pinned by test) + all ten stochastic-IC modules now draw `ic_c0..ic_c15` in their Latin-hypercube design and export them in `cond`/`param_names`; per-module tests assert the field is a function of the exported cond alone. Full suite: 149 passed, 9 skipped.
2. **The certificate is a generation gate.** `mffp_sharp/common/completeness.py` (witness + generic reconstruction), wired into both `mffp_sharp/generate.py` and `generate_standardized.py`; `condition_completeness` is written into `meta.json` and INCOMPLETE hard-fails unless the block declares `stochastic_map`.
3. **Sample round (SURF gate) generated and certified.** `sample_round/`: 10 samples × 3 production-ladder levels per dataset; every `meta.json` reads COMPLETE with reconstruction rel-L2 = 0.0; review figures in `sample_round/figures/`.

Sample-round findings that need a recipe decision at sign-off:

| dataset | LF-vs-HF gap, shipped (white-noise IC) | gap, sample round (band-limited IC) | reading |
|---|---|---|---|
| fisher_kpp_2d | 0.196 | **0.024** | the 8-mode IC weakens the front regime 8×; options: longer `output_time`, smaller `D_range`, or more IC modes (larger cond) |
| allen_cahn_2d | 0.033 | 0.041 | preserved (interface width is set by $\varepsilon$, not the IC) |
| phase_field_crystal_2d | 8.3e-6 | 1.2e-6 | NO_GAP before and after — the pre-existing round-2 finding; a panel-composition decision, not an IC-fix regression. Part of the sampled $(r, \bar\psi)$ range also sits in the uniform (non-crystalline) phase (see figure sample 1) |

**Recipe resolution (2026-08-03, operator-approved — see `APPROVAL.md`):** fisher_kpp_2d regenerates with `ic_modes: 5` (48 coefficients, condition dim 50).
The measured sweep (`fk_option_sweep`): longer `output_time` *reduces* the gap (logistic domain-fill outruns front densification: 0.022 → 0.019 at $T{=}0.15$, mean $u \to 0.91$); 10× smaller $D$ changes nothing (0.0219 — front *density*, not width, is what white noise supplied); 48 coefficients reach 0.041 (allen_cahn's accepted level) and 96 only 0.048.
The shipped 0.196 is unreachable under any small complete condition vector — it was largely a property of the unexported broadband IC, i.e. of the defect itself.

## Files in this package

- `PROPOSAL.md` — this document.
- `certify_condition_completeness.py` — the two training-free tests; reproduces ADR r2-0003's pfc/fisher_kpp numbers and adds the cahn_hilliard reconstruction certificate.
- `certificate_results.json` — measured output, 2026-08-03, `benchmark_42/sharp`, ladder level `l1`.
- `IMPLEMENTATION_PLAN.md` — the executed implementation plan (all tasks verified).
- `SIGNOFF.md` — the one-page ask + post-approval runbook.
- `sample_round/` — certified sample data (meta/README/figures in git; field npz local-only), ablation stubs pinning the production ladders, and the figure render script.
