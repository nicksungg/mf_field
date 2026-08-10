# Handoff from experiment-builder — 2026-08-10T15:20Z

**For**: code-reviewer, experiment-debugger
**Experiment**: r3s2_field_reach-B2

## Commit discrepancy — RESOLVED
`recipe.base_commit` **76d15c2d is wrong for vendoring**: it is a trunk commit
(the batch-2 websearch report) and `git ls-tree` shows it carries **no**
`models_r3/` tree. `env._substrate_commit` **d5069a74 is correct** — it is the
tip of `round3/exp-r3s2_field_reach-B1` and carries all 14 files of
`models_r3/r3s2_stack_ic`. Vendored from d5069a74; per-file sha256 in
`models_r3/r3s2_route/_vendor_manifest.json`. Card fields untouched.

## Provenance of every hyperparameter
Recipe: all 68 env knobs (verified byte-equal to `recipe.env` in both the family
table and `scripts/01_train_eval.sh`), arms, budget, LOOCV grid, k_cut rule.
Base family (`SMOKE`, unchanged): widths, lr 1e-3/3e-4, batch 16, clip, cosine.
Card's `source_iteration` (brainstormer iteration_2 item 4): direct-head loss
`rel_l2`. **No TBD.** Two builder judgment calls, both recorded in-file and in
the diag: (a) the band-limit zeroes `kr >= k_cut` (ring included) — makes band 4
exactly 0 so G2 leg (iii) is decidable on bands 1–3; (b) A6 does not refit the
trained candidates (0-epoch budget), so its asymmetry is directional and
recorded — an affine win is conservative, a trained win is an upper bound only.

## Smoke evidence
`score_panel.py --datasets ifc_heat --epochs 2 --seed 0 --no_cache` → exit 0,
nRMSE **0.2291626**, `scratchpad/contract_smoke_ifc_heat.json`. ifc has no
`ic_c*` columns, so a second **debug-only** run on a synthetic fixture exercised
the ic_synth branch on both routes (`scratchpad/icfixture_result.json`; numbers
never enter the card). In-job affine == certified floor to 8 s.f.

## What to watch
Login node has 1 core / no GPU: no full-panel timing evidence. Band 4 |T| goes
33.9 → 0.0 under the repair on the fixture; on ifc_heat LOOCV picked ridge 0
(band-limit does the work at n_fit=3). Watch `V3.chains_degenerate` — if true,
A5 == A1 and G2 attribution is empty on that cell.
