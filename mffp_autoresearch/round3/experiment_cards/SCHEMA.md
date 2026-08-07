# Experiment card schema — Round 1

One card per experiment: `experiment_cards/{stream}/batch_{N}/B{N}.json`,
id `{stream}-B{N}`. Update rules: `subagents/_shared/card_update.md`.

```jsonc
{
  // ── identity (starter; LOCKED) ─────────────────────────────────────
  "id": "s5_tuning-B1",
  "stream": "s5_tuning",
  "batch": 1,
  "category": "tuning",              // free tag from the brainstormer
  "card_type": "model",              // "model" | "diagnostic"  (round-1 addition)
  "created_utc": "2026-07-28T00:00:00Z",
  "worktree_path": "mffp_autoresearch/round1/worktrees/s5_tuning/B1",
  "source_iteration": "brainstormer/s5_tuning/batch_1/iteration_1.md",
  "reopened_from": null,

  // ── planning (starter, verbatim from brainstormer; LOCKED) ─────────
  "1_id_category": "...",
  "2_motivation": "...",             // must cite a prior finding or open question
  "3_description": "...",            // concrete config, what differs from base
  "4_expected_result": "...",        // which metric moves, by how much, why
  "expected_falsification": "...",   // one sentence; threshold must exceed the
                                     // dataset noise floor (state/noise_floor.json)
  "anchor_reference": null,          // per-stream policy, program.md §4.5/§12
  "prior_art": {                     // round-1 addition; from the websearcher
    "verdict": "novel",              // "novel" | "preempted-pivoted" | "preempted"
    "citations": ["..."]             // only sources actually fetched in the loop
  },
  "recipe": {                        // round-1 addition; builder HARD-STOPs
                                     // (BLOCKED: recipe-missing) if absent/empty
    "base_family": "mf_fno_transfer_film",
    "base_commit": "<sha of the substrate/base family state>",
    "family_dir": "models_r1/<family>",   // worktree-relative
    "datasets": "panel",
    "epochs": 200,
    "seeds": [0, 1, 2],
    "env": {}                        // every env knob; enters the cache key
  },

  // ── experiment (builder / reviewer / debugger) ─────────────────────
  "status": "drafted",               // drafted|blocked|built|reviewed_pass|
                                     // reviewed_suggest|reviewed_fail|running|
                                     // analyzing|complete|skipped
  "skipped_reason": null,
  "reopen_candidate": false,
  "scripts_path": {},                // {"submit": "...", "seeds_2_3": "..."}
  "output_paths": {},                // under outputs_root/{stream}/B{N}/
  "build_commit": null,              // sha on branch round1/exp-{stream}-B{N}
  "job_ids": [],
  "logs": {},
  "build_notes": [],
  "review_notes": [],
  "debug_notes": [],                 // each: {attempt, classification: "ALGO"|"INFRA",
                                     //        diagnosis, fix, relaunched_job_ids}

  // ── results & analysis ─────────────────────────────────────────────
  "5_actual_result": null,           // initial-analyzer: per-dataset nRMSE+skill
                                     // table, panel geomean ± CI, cratered verdict,
                                     // guard-set flags; NEVER hand-recomputed —
                                     // parsed from score_panel result JSONs
  "6_analysis": null,                // mechanism-analyzer turn 3: findings vs
                                     // interpretation, separated
  "7_gap_and_future": null,          // register turn: open question, next direction
  "reanalysis_progress": null        // {"turns_done": 0..3, "registered": bool}
}
```

Diagnostic cards (`card_type: "diagnostic"`): no training, single run, no
seeds 1–2; `recipe.epochs = 0` is legal; `5_actual_result` records the
measurement against the falsification clause.

---
Round-3 note (2026-08-07): schema inherited verbatim from round 2 (program.md §"pipeline, card format, agents"). Round-3 additions: `adr_r3_0004_addendum` (orchestrator-written, pfc report-only), `recipe.datasets_pre_adr_r3_0004` / `recipe.base_commit_pre_adr_r3_0004` (pre-amendment values preserved).
