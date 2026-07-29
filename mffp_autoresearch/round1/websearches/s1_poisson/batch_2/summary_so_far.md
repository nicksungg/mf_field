# summary_so_far — s1_poisson, batch 2

## Where the stream stands

Stream `s1_poisson` attacks the one *gap* dataset where the zoo is already near
the published bar: `ifc_poisson`, paper bar 0.036 (IFC-ODE2), stretch 0.018
(program.md §12.1). **N_hf = 5**, so every claim is anecdote-grade by sample
count and the noise-floor convention is the only defensible reporting.

Reference lines batch 2 must carry (from
`experiment_cards/s1_poisson/batch_1/B1.json` part 7,
`state/anchors/s1_poisson.json`, `state/noise_floor.json`):

| line | value | source |
|---|---|---|
| anchor (`mf_fno_transfer_film`) | skill **1.5656** [1.4562, 1.6961], nRMSE 0.05636 | `state/anchors/s1_poisson.json` |
| certified noise floor (`min_claimable_effect`) | **0.23991** skill units (~0.00864 nRMSE) | `state/noise_floor.json` |
| training-free matched-level lookup + one gain | nRMSE **0.24828** | B1 part 7 |
| HF-train-mean field predictor | nRMSE **0.40343** | B1 part 7 |

## What batch 1 established (B1, status `complete`)

B1 built family `mf_fno_ladder` (vendored from `akash/models/mf_fno_allpairs`),
fixed a **sample-correspondence defect** (ifc_poisson's four fidelity levels are
NOT index-aligned; max cond diff 0.58-0.74 across all six pairs), and ran four
arms {`two_level`, `adjacent`, `allpairs`, `legacy_pairing`} at 200+200 epochs,
seed 0 (provisional-single-seed, ADR 0004).

Central *negative* result: the full ladder was **worse**, not better
(`two_level` 0.1027 vs `allpairs` ~0.209/0.214). Part 6/7 localized why:

- ifc_poisson's four levels follow a clean **~h^2 amplitude scale law** -
  adjacent RMS ratios 4.379 / 4.196 / 4.120, **75.7x** end-to-end - while
  agreeing in **shape** (Pearson r 0.94-0.99 after a single per-sample gain).
- The base family normalizes **all levels with ONE shared scaler**, so the
  network must learn that amplitude law along its fidelity axis. Signature:
  right shape, collapsed conditional variance (0.44 of target), **74.7 % of
  squared error removable by a per-sample gain**.
- A reduced-capacity proxy with **per-level** normalization *reversed the
  central result*: `allpairs` 0.2143 -> 0.0874, from 2x worse to 1.69x better
  than `two_level`. Proxy caveats: hidden 16 / 2 blocks / modes 8 / 30 joint
  epochs; attenuated baseline gap (1.17x vs production 2.04x); two seed-1 runs
  killed at the 1200 s cap.

## Batch-2 candidate (B1 part 7 `next_direction`)

Factorial MODEL card: `MFFP_LADDER_SCALER {shared, per_level}` x pair-set
`{two_level, allpairs}` at production tier, with **two separate falsification
clauses** - one on the normalization contrast (`allpairs/per_level` vs
`allpairs/shared`), one on the composition contrast (`allpairs/per_level` vs
`two_level/per_level`) - because conflating them is what made B1's clause
unfalsifiable-as-worded.

## Prior websearch context (do not re-cover)

`websearches/s1_poisson/batch_1/report.md` (5 iterations, cap hit) settled the
**composition** axis: fidelity-as-input conditioning (arXiv:2207.00678),
adjacent-pair nested cascades (arXiv:2605.16118), joint all-levels training
(arXiv:2402.02031), progressive ladders at tiny HF (arXiv:2510.13762), MLMC-NO
telescoping on FNO+Poisson (arXiv:2505.12940), MFRNP Poisson 0.0076
(arXiv:2402.18846). All-ordered-pairs verdict was
`preempted-but-MF-composition-open`. Batch 1 found **nothing at N_hf ~ 5** and
flagged two unresolved items (the 0.036/0.018 attribution; MLMC-NO's hierarchy
construction). Fetch lessons: prefer `arxiv.org/html/`; `arxiv.org/pdf/` and
`openreview.net/pdf` usually fail; `par.nsf.gov` DNS-fails.

`websearches/s7_loss/batch_1/report.md` covers the **single-fidelity**
gain/shape axis: Eigen's scale-invariant log loss (ar5iv 1406.2283) owns the
gain-ambiguity mechanism; "Scale-Consistent Learning for PDEs"
(arXiv:2507.18813) is *spatial* rescaling, not amplitude; verdict C-AMP =
`preempted-but-MF-composition-open`. Batch 2 must **extend, not duplicate**:
the open question here is the *multi-level* case - per-fidelity target
standardization and h^p-aware residual scaling.

The two in-repo literature reports carry no normalization-scheme material:
grepping `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` and
`MF_Sharp_HighFreq_Report.md` for "normaliz|scaler|per-level" returns only an
attribution caveat and the note that all zoo families train in
scaler-normalized space (`MF_Sharp_HighFreq_Report.md:78`).

## Open questions batch 2's search must answer

1. Is the **shared-scaler pitfall** for pooled multi-fidelity targets documented
   anywhere, or is per-level/per-fidelity standardization silently standard
   practice buried in appendices?
2. Does anyone **explicitly exploit a known h^p convergence rate** to rescale
   residuals/targets across discretization levels before learning (the ML analog
   of MLMC variance-weighting or Richardson extrapolation)?
3. Is a **training-free nearest-condition level-matched lookup** published as a
   baseline for elliptic MF problems (it beats 3 of B1's 4 trained arms)?
4. Is the **factorial normalization x composition** design itself preempted?
