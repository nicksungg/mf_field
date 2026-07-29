# ADR 0001 — Round 1 port decisions

**Status:** accepted 2026-07-28
**Spec:** `docs/superpowers/specs/2026-07-28-mffp-autoresearch-design.md` (the authoritative design; this ADR only records what was fixed there and why, for the round's own trail).

## Decisions

1. **Base scaffold: `playground_test/autoresearch_round5b`** (the no-oracle arm). The paper's own ablation showed structure alone prevents drift; no MFFP taste profile exists. The four oracle consult points remain identifiable in the prompts so an oracle can be added in a later round.
2. **The factory CEO loop is retired for this workstream.** It plateaued (composite 0.0222 for two cycles) and exhibited the drift/bookkeeping pathologies the card scaffold is designed against. It is left untouched for the mentor's use.
3. **Objective: copy-LF skill.** `skill = nRMSE(model) / nRMSE(copy-LF)` per dataset, geomean over the 6-dataset panel, bootstrap CIs over seeds {0,1,2}. Replaces best-per-dataset `composite_nRMSE` (rejected in `docs/planning/AUTORESEARCH_PLAN.md` §2).
4. **Eval layer lives inside the round** (`round1/eval/`), outside every guarded factory surface. Guarded surfaces (`factory_mffp/{eval,baselines,references,scripts,data}`, `factory.md`, `benchmark_42/`, `akash/`) are never edited by the loop.
5. **Streams are gap/lever/tuning-shaped, not model-family-shaped** (5 pilot streams). The zoo is already 45 families deep; the open questions are dataset-shaped.
6. **Worktrees fork from branch `round1-substrate`** (full tree — the repo is code-only; data is git-ignored). Experiment branches: `round1/exp-{stream}-B{N}`. Training/eval outputs go to `mffp_autoresearch_outputs/round1/` (git-ignored, sibling of the round spec), never into worktrees.
7. **Four additions over round 5b**, all from this repo's post-mortems: mandatory retrieval-grounded prior-art verdict (0-for-4 novelty record), diagnostic card type (measurements as first-class experiments), seam assertions with hard-stops (recipe block, train↔eval contract, one nRMSE hash), and a noise-floor batch 0 gating every falsification threshold.
