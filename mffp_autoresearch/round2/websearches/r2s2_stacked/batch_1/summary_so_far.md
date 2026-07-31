# Summary so far — stream `r2s2_stacked`, batch 1

## The stream's question

From `mffp_autoresearch/round2/project.yaml` (`streams[1]`) and program.md §4.1/§12.2:
*does a condition→pseudo-LF emulator feeding the frozen round-1 DC corrector beat direct
condition→HF prediction, and how much is lost to pseudo-LF distribution shift?*

Round 2's regime (program.md §1, §5.9): **no LF field at test**. Models see only the
condition vector (2–19 scalars, complete by construction, §13.1); test LF field files are
physically absent from `${STRIPPED_DATA_ROOT}`. Train-side LF use is free — that is the
round's question. The stacked design is the one place where a round-1 model may legally
reappear: as a **declared frozen test-time sub-component** behind a new condition→pseudo-LF
front end (§5.10a — "the reuse IS the experiment").

## Current state (no experiments have run in this stream)

- `experiment_cards/r2s2_stacked/` contains only `.gitkeep` — batch 1 is the stream's first
  card; there is no prior websearch batch for this stream.
- Anchor (`state/anchors/r2s2_stacked.json`): `best_floor_panel_geomean` = **23.0636**,
  `provisional: false`, source `training_free_floors`. Per-dataset best training-free
  floors: helmholtz 3.344 (zero), pfc 59.81 (mean), allen_cahn 269.20 (NN), fisher_kpp
  11.99 (mean), cahn_hilliard 23.18 (NN), ifc_poisson 10.05 (NN). Any claim inside a CI of
  this anchor, or below `state/noise_floor.json`, is noise.
- `state/noise_floor.json` is **provisional** (`_source: round1-batch0-rescaled`,
  `_provisional: true`); per program.md §4.3 falsification clauses are judged directly
  until r2s4-B1 certifies a condition→HF 3-seed spread.
- Prior-round assets this stream must vendor (§12.2): the s6 DC lineage corrector
  (`round1/worktrees/s6_local/B2`) and the s4-B3 `dc_cleaned` stage
  (`round1/worktrees/s4_hybrid_routing/B3/models_r1/s4_router/`). Round-1 report
  (`round1/docs/round1_report.md` §1, §4) records `dc_cleaned` panel geomean **0.1233**
  under the OLD inflated denominators — a prior, not a bar (program.md §3).

## Carried mechanism constraints (round-1 rules that bind this stream)

- **BC-match rule** (r1 report §6 / §4.1): spectral pre-stage eligibility = boundary-condition
  match, decidable training-free (`tools/spectral_prestage_bc_audit.py`).
- **Wrap-seam caveat** (§12.2, r1 report §5.2): part of `dc_cleaned`'s pfc credit was a
  boundary-rim artifact of the DEFECTIVE reference; s4-B3 H4 says deep-bulk ratio on pfc was
  0.908, so under the corrected reference some credit may vanish.
- **Lineage-bound caveat**: static routing/eligibility rules name the library they were fit on;
  the s6-B2 rho rule was obsolete against the cleaned lineage.
- **Nested-ladder degeneracy** (r1 report §6): with aligned/nested ladders MF training tends to
  degenerate to top-rung replication — a live threat for a pseudo-LF emulator whose target LF
  is a band-limited version of the same field.

## In-repo prior websearches (cite, don't re-derive)

- `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` — §4.3 MF fusion for smooth problems,
  [LF-13] correlation-based MF **neural emulators** benchmark (arXiv:2512.02868 — https://arxiv.org/abs/2512.02868), including
  *corrupted LF sources* — directly relevant to pseudo-LF distribution shift, but pointwise
  emulation not field prediction (line 150 caveat). §5 N4 `mf_fno_multistage`: stagewise
  residual stacking with residue rescaling.
- `docs/reports/MF_Sharp_HighFreq_Report.md` — line 101: existing zoo families
  (`fno_additive`, `fno_autoregressive`, `fno_multilevel`, `fno_mf_stack`) already run on
  **"model-generated LF only"**, i.e. an in-repo precedent for stacking on emulated LF; their
  additive `LF + δ` aggregation is a known negative result on sharp fields.

## Open questions this batch must answer with retrieval

1. Is "emulate the coarse solve, then apply a corrector trained on real coarse solves" already
   published (neural emulators of coarse solvers feeding learned correctors)?
2. Is the **frozen vs fine-tuned vs end-to-end** ablation of a stacked surrogate under
   generated-input distribution shift published, and with what verdict?
3. Does the literature quantify the loss from feeding a downstream module generated rather
   than real inputs (exposure bias / cascaded-model input shift), and does it name a fix that
   would be legal here (no test-time LF, no new data — §5.11)?
