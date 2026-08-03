# Sign-off request — generator-surface changes (one page)

> **Superseded 2026-08-03, same day:** Eloise directed that her operator approval is sufficient (see `APPROVAL.md`); this document remains as the technical one-pager, and sending it to Nicholas is optional/informational.

**To:** Nicholas.
**From:** Eloise (prepared by her agent, 2026-08-03).
**Branch:** `mffp-trunk-eloise` on `nicksungg/mf_field` (all changes committed there; nothing merged, nothing regenerated at production scale, no cluster compute spent).

## What you are being asked to approve

1. **The IC-encoding refactor** (`condition_completeness_proposal/`, this package).
   The validated 2026-06-28 fix moves from the standalone `generate_learnable.py` into `mffp_sharp` itself: all ten stochastic-IC PDE modules now export their 16 IC Fourier coefficients in the condition vector, and generation hard-fails on an INCOMPLETE completeness certificate (written into `meta.json`) unless a dataset explicitly declares stochastic-map semantics.
   Evidence: 149-test suite green; certified sample round at production ladders with exact (rel-L2 = 0) reconstruction from the exported condition vector; review figures in `sample_round/figures/`.
2. **Regeneration of `phase_field_crystal_2d`, `fisher_kpp_2d`, `allen_cahn_2d`** through the fixed path (solver time only, 500 samples × 3 levels each; in-place repair is impossible — the shipped ICs are 4096-dof white-noise fields no small vector can describe).
3. **One recipe decision before full regeneration** (from the sample round): the band-limited IC weakens fisher_kpp's LF-vs-HF gap 8× (0.196 → 0.024).
   Options: (a) longer `output_time` so fronts develop and sharpen; (b) smaller `D_range` for thinner fronts; (c) more IC modes (grows the condition vector).
   allen_cahn is unaffected; pfc's NO_GAP predates this change and is a round-3 panel-composition question.
4. **The `ladder_fix_proposal/` patch** (companion package, unchanged in content, rebased so `git apply --check` passes at current HEAD) — same surface, same sign-off, and it also regenerates derived arrays, so the two land together.

## What is NOT in scope

No model, eval, or baseline changes; no round-2 numbers change (the round's report stands, with its already-committed corrections); no round-3 launch (its prerequisites are in `round3/PROGRAM_NOTE.md` and remain operator-gated).

## Post-approval runbook (queued, not launched)

```bash
# on the cluster, after `git pull` on mffp-trunk-eloise and the ladder patch applied:
for v in phase_field_crystal_2d fisher_kpp_2d allen_cahn_2d; do
  sbatch --mail-user=ezeng@caltech.edu --mail-type=END,FAIL \
    --wrap "python mf_field_eloise_data/generate_standardized.py $v"   # gate runs inside; INCOMPLETE aborts
done
# then, from the Mac: verify every meta.json carries condition_completeness: COMPLETE,
# re-run mffp_autoresearch/preflight/preflight.py over the regenerated panel (must PASS),
# and only then consider the 3-seed anchor runs (operator-gated, round3/PROGRAM_NOTE.md §7).
```
