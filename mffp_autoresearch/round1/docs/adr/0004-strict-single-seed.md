# ADR 0004 — Strict single-seed in-round protocol (operator action)

**Status:** accepted 2026-07-29 (directed by Eloise via AskUserQuestion:
"Strict 1-seed"; applied by the orchestrator session)

## Decision

The 1+2 seed protocol (§4.4: seed 0, then seeds 1–2 unless cratered) is
replaced for all in-round experiments by **seed 0 only**. Seeds 1–2 run only
as an **end-of-round confirmation pass for the top 3 models** on the
provisional leaderboard (smoke tier, reusing each card's
`submit_seeds_2_3.sh`). Full-tier (2500-epoch) champion runs remain 3-seed
and human-approved. Diagnostics were always single-run and are unaffected.

## Cost/risk trade accepted

- Saves ~2.6 GPU-h per avoided seed (~154 min/seed panel at smoke tier);
  roughly 2/3 of model-card GPU cost.
- Accepted risk (stated to and accepted by the operator): mid-round results
  are single-seed point estimates; winner's-curse selection noise is possible.
  Mitigations retained: (a) every in-round claim is labelled
  `provisional-single-seed`; (b) batch-0's certified 3-seed noise floor
  (`state/noise_floor.json` min_claimable_effect) remains the bar for
  treating any effect as real when designing later batches; (c) the top-3
  confirmation restores CIs before any final claim; (d) the cratered
  category is retained as a seed-0 verdict.
- The recommended promotion-gated variant (seeds 1–2 only when seed 0 clears
  threshold) was offered and declined in favour of maximum cheapness.

## Mechanics

- `project.yaml` seed_protocol → `{seeds: [0], end_of_round_confirm:
  {top_k: 3, seeds: [1, 2]}, cratered_skill_factor: 1.5}`.
- program.md §2.4 tier table, §4.3, §4.4 edited (operator correction with
  this ADR as trail, per the ADR 0003 precedent; agents still may not edit
  the spec).
- Existing cards' locked `recipe.seeds: [0, 1, 2]` fields are NOT edited
  (locked); execution is governed by this ADR — the orchestrator submits
  seed 0 only. Applies to s5_tuning-B1 (already built) and all later cards.
- Anchors from batch 0 keep their 3-seed CIs (already certified).
