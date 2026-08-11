# Handoff from experiment-starter — 2026-08-11T03:43:37Z

**For**: experiment-builder, code-reviewer
**Experiment**: r3s3_lf_value-B3

## What I did
- Transcribed the batch-3 brainstormer report verbatim into the card (parts 2/3/4, `expected_falsification`, `prior_art` with its five citations and the K1 quote, and the full `recipe` JSON block).
- Created this worktree on `round3/exp-r3s3_lf_value-B3` from `round3-substrate`.
- Applied the two ADR-declared transcription-time edits ONLY, per ADR r3-0007 RATIFIED as OPTION C: `R3S3B3_CELLS` now reads the four sharp cells + `ifc_heat`; added `recipe.env._ifc_clause_status` recording the ADR outcome and the deleted `ifc_poisson` clause. Nothing else changed.

## What to watch for
- **No TBD fields.** Two placeholders remain BY DESIGN from the brainstormer:
  - `R3S3B3_PREREG_SHA256` is still the `<filled at transcription from the phase-P seal...>` placeholder — the seal (`state/r3s3_lf_value/prereg_knees_B3.json`) does not exist yet, so it cannot be filled. Run phase P (CPU, no GPU), then fill it. **No sbatch before the seal exists.**
  - `R3S3B3_LF_COND_CAP` is per-leg (`<r1|r2|r3 from the sealed ladder>`).
- `recipe.datasets` is preserved verbatim with its bracketed conditional; the resolved option-C list is authoritative in `R3S3B3_CELLS` / `_ifc_clause_status`. `ifc_poisson` is report-only.
- `_ifc_clause_status` is the one string I authored (the brainstormer named the key but supplied no text); it is flagged as starter-transcribed inside the field.

## Suggested next steps
- Phase P first (seal + sha256), then vendor the base family @ `eedcc655` and `_common/ckpt_binding.py` @ `da855da`, then the three per-seed sbatch jobs.
