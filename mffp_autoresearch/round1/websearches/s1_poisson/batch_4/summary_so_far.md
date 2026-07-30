# Summary so far — `s1_poisson`, batch 4

## Where the stream stands (B3 closed)

`experiment_cards/s1_poisson/batch_3/B3.json` part 5 reports five seed-0 arms at
the 200-epoch smoke tier on `ifc_poisson` (paper bar 0.036, ADR 0002; skill =
nRMSE / 0.036, lower better):

- `base__none` (ladder_mode `allpairs`, no head): nRMSE **0.034264**, skill 0.9518
- `gain__ladder_level_intercept` (PRIMARY): **0.024970**, skill 0.6936
- `gain__hf_only`: 0.034243 (a numerical no-op; `g_hat` = 1.0000079 +/- 5.5e-05)
- `gain__ladder_pooled`: 0.057489 (transferred intercept costs +0.0275 nRMSE)
- `self_only__none`: **0.021913** — the best claimable `ifc_poisson` number in the
  round so far

The mechanism analyzer's findings (part 6, and
`worktrees/s1_poisson/B3/notes/handoff_experiment_mechanism_analyzer.md`) are the
reason batch 4 exists:

- **T1-F1**: `allpairs` carries ZERO extra supervision over `self_only`. Rebuilt
  with the family's own `build_rows`, all six cross-level blocks are *exact*
  duplicates of the self block at their target level — cond `max|diff| = 0.0`,
  target-field `max|diff| = 0.0`, 6/6 pairs, differing only in the `f_src` tag.
  280 rows, 175 distinct. Consequence of B2's `cond_from = target` correction.
- **T1-F2**: what `allpairs` *is*, is a per-level replication schedule
  x1/x2/x3/x4 at levels 8/16/32/64. Level shares 0.357/0.357/0.214/0.0714 vs
  0.571/0.286/0.114/0.0286, i.e. share ratio **0.625x on the 100-condition level,
  2.5x on the 5-row HF level**. Under `per_level` normalization row share *is*
  effective loss weight. Gradient steps/epoch at bs=16: **18 vs 11 — a 1.64x
  optimization-budget difference that rides along as an open confound.**
- **T1-F5**: `allpairs` fits its 5 HF rows 1.34x tighter and generalizes 1.56x
  worse (test/train ratio 7.12 vs 3.39).
- Cross-stream note (3): `tools/ladder_pair_row_audit.py` shows the same
  REPLICATION_ONLY verdict on `heat_local` (5 levels x 1024 -> 15360 rows, 5120
  distinct). So this is a property of the *construction on aligned/nested
  ladders*, not of one dataset.

## The open question batch 4 must settle

Card part 7 `open_question`: is the `self_only` win a **condition-coverage /
effective-N (loss-reweighting)** effect or an **optimization-budget (steps)**
effect? Nothing measured in B3 separates them, because separating them needs a
training run. The planned B4 design is a cheap in-repo A/B: (i) an
allpairs-dedup arm (duplicates removed -> self_only's data, allpairs' step
count), (ii) self_only with steps matched to allpairs via epoch scaling, (iii)
frozen controls.

## Noise floor and immutables

`state/noise_floor.json` -> `ifc_poisson` `min_claimable_effect` **0.23990756**
skill (spread of the 3-seed anchor), anchor `state/anchors/s1_poisson.json`
mean skill 1.5656, CI95 [1.4562, 1.6961]. `self_only` vs the control is 1.43x
the floor (claimable); `self_only` vs the PRIMARY head is 0.354x the floor (NOT
rankable). Immutables: ADR 0009, ADR 0004 (seed 0 in-round), metric frozen
(program.md §5.4), data read-only (§5.1).

## What this batch's search is and is not

This is **measurement hygiene, not novelty**. The expected verdict shape for
directions 1-3 is `preempted (ML-general), open only as an in-repo measurement`
— and that is a fine outcome. The one place a genuine novelty check matters is
direction 4: **does any multi-fidelity paper note that aligned/nested LF-HF
ladders make cross-level (all-pairs) supervision degenerate — duplicate
targets, hence pure replication/reweighting?** If unreported, B3's T1-F1 is
itself a round-report-worthy observation.

## Prior websearch state

`websearches/s1_poisson/batch_3/report.md` established: (a) route rules — use
`arxiv.org/abs`, `arxiv.org/html`, **ar5iv** for pre-2024, PMC, raw.github;
never `arxiv.org/pdf`, ScienceDirect, Springer, OpenReview; (b) single table
digits from a fetch need two independent renderings; (c) the literature supplies
mechanisms and no effect sizes at N_hf = 5 (three batches running). The in-repo
reports `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` and
`MF_Sharp_HighFreq_Report.md` were checked by grep for
duplicate/dedup/replication/reweight/step-matched/all-pairs/nested — **no
coverage of this batch's questions**; they are not cited below.
