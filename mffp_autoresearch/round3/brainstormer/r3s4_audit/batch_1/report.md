# Brainstormer Report — Stream `r3s4_audit`, Batch 1

**Stream**: `r3s4_audit` · **Batch**: 1 · **Total iterations**: 1 (cap 5) · **Slot filled**: 1/1 · **Reopen candidates resolved**: 0 (none existed)

> **Escalation attached — read before dispatch.** At design time I found a reproducible convention mismatch between two instruments: `preflight/preflight.py` computes its ADR r3-0003 fifth-class checks on the **coarsest** LF rung (`levels[0]`), while the scoring path `round2/eval/panel_data.py::copylf_prediction` uses the **finest** LF rung (`max(lf_fids)`). ADR r3-0003 D2 turns the shipped `min_detectable_delta` into a claim-licensing rule for cahn_hilliard, and on the scored cell that rule is 1.52× too permissive (109.14 % shipped vs 165.30 % scored — the latter matching ADR D2's own "~166 %" prose). pfc's shipped `OUTLIER_DOMINATED` warning is 43.9× over-priced and clears on the scored cell. No shipped *score* is affected (the frozen eval layer is untouched); the affected object is a claim-licensing constant. I did not set a HOLD because this is a convention discrepancy, not yet a proven defect, and my write scope excludes the HOLD file — the orchestrator should adjudicate PROGRAM_NOTE MUST #2 before dispatch. The card is designed to work either way: it is deliverable D0.

## Slot

- **Category**: diagnostic / repaired-panel claim-threshold + floor certification (numerator seed noise × reference-cell row noise), with the fifth-class estimator-integrity instruments re-pointed at the scored cell and extended to the paper-bar (ifc) reference type.
- **Card type**: `diagnostic` (with training — the §12.4 exception, 3 seeds).
- **Motivation**: the batch-1 verdict row **D1** reads `preempted-but-MF-composition-open (cite)`, open column verbatim — *"No fetched source fuses training-seed variance and reference-cell sampling error into one claimability threshold, and none does so for a field-valued MF panel whose reference is a coarse PDE solve. Cheap adoptable extras: paired per-seed deltas + bootstrap instead of max−min; the documented ratio-of-normals caveat applies to cahn_hilliard (denominator uncertainty large ⇒ normal approximation fails). NOT open: bare max−min spread."* — and row **D3** reads `preempted-but-MF-composition-open (cite)`, open column verbatim — *"Genuinely uncited: that a copy-LF-referenced cell is silently inflated by rows with no fidelity gap, and that certifying a test split against a per-row-gap threshold is a precondition for the metric to mean anything. Report as a project-local instrument finding backed by the recorded search-negative."*
  This card **is** that composition and that project-local finding; D2 (`preempted (cite)`) is executed as reproduction-only and D4's preflight/HOLD architecture (`preempted (cite)`) is cited, never claimed. `round3/program.md` §3 makes the card gating: *"`state/anchors_repaired/noise_floor.json` is PROVISIONAL; r3s4 re-certifies mce on the repaired panel before any criterion is adjudicated (round-1 §4.5 discipline)."*
- **Concrete config**: one family + four worktree probes; no `state/` writes (the orchestrator installs the certified file).
  - **D0 rung-seam reconciliation** (`probes/cell_seam.py`, training-free): per-row copy-LF gaps computed twice — through the vendored `eval/panel_data.py::copylf_prediction` (SCORED cell, finest LF rung, ADR r2-0001 convention) and through `preflight.py`'s coarsest-rung construction — with a ≤1e-9 seam assertion against `floors.json[ds].reference.test_nrmse`; both variants' `degenerate_rows` and seeded `cell_stability` (n_boot 10 000: top-5 share, CI95 half-width, `min_detectable_delta`); re-adjudication of ADR r3-0003 D1 (ac trim) and D2 (ch MDD) on the scored cell.
  - **D1 floor + anchor reproduction certificate** (`probes/floor_repro.py`, deterministic, 6 panel + 3 guard): `nn_condition` / `train_mean` / `zero` / `affine_on_hf_train` recomputed **from the stripped view**, diffed at 1e-9; `zero ≡ 1.0`; best-floor panel geomean `= 36.3912`; lineage 75.0673 → 38.6300 → 36.3912 reproduced from the archived floor files; `affine_on_hf_train` extended to all six panel datasets and cited to DeLise et al. 2025 (https://arxiv.org/abs/2508.05831) with its oracle-affine residual; `data_binding.py verify` against `state/data_hashes.json` at job start.
  - **D2 numerator (seed) noise re-certification** (family `models_r3/r3s4_cert_min`): round-2's `r2s4_cert_min` vendored **verbatim** with provenance comments, hyperparameters byte-identical, smoke tier 200 epochs, seeds {0,1,2}, explicit 6-dataset round-3 panel; emits `per_seed_skill`, `iqm`, `ci95_stratified_bootstrap`, `spread_maxmin`, `paired_null_95`, sign-flip p, `seed_mce = max(spread_maxmin, paired_null_95)`.
  - **D3 row noise + two-threshold fusion** (`probes/certify_thresholds.py`): seeded 10 000-resample paired row bootstrap for the reference cell and for a same-model seed-pair null contrast, producing per dataset `row_paired_95`, `mdd_scored`, and the two certified constants — `tau_rel = max(seed_mce, row_paired_95)` for same-reference within-era arm comparisons (the reference cancels in the ratio), and `tau_abs = tau_rel + mdd_scored × skill_level` for absolute-bar or cross-era claims; `reference_type` recorded per dataset, with `mdd_scored ≡ 0` certified for the two paper-bar (ifc) cells; cahn_hilliard by bootstrap only, with the ratio-of-normals caveat recorded verbatim. Emits `noise_floor_candidate.json` including an **`ifc_heat` entry (its first)**.
  - **D4 per-cell estimator-integrity audit** (`probes/cell_integrity.py`): leave-top-k-out case deletion (k ∈ {1,3,5,10}) on each panel cell's per-row ratio sum for the certifier and each floor arm (cited to Cook–Weisberg / LOO meta-analysis); re-certification of the ac trim (n=78) and pfc box swap (n=100) against the **scored**-cell gap threshold; the D3 search-negative recorded verbatim; on ifc, a certified statement that the shipped fifth-class checks are **inapplicable** (ifc_raw layout, test ships HF only, paper-bar reference) plus the substitute instrument (n_test=128 numerator row bootstrap + the mandatory affine floor, ifc_poisson 1.5938 / ifc_heat 0.9584).
- **Recipe**:

```json
{
  "base_family": "r2s4_cert_min (round-2 diagnostic certifier, vendored VERBATIM with provenance comments from mffp_autoresearch/round2/worktrees/r2s4_diag/B1/models_r2/r2s4_cert_min/; declared INSTRUMENT reuse — this is a diagnostic card that makes no performance claim, and byte-identical reuse is what makes the re-certified constants attributable to the data repair rather than to a model change)",
  "base_commit": "8aae33a7fab11ef8234f4bb7158c2bc1a8b4bf51",
  "family_dir": "models_r3/r3s4_cert_min",
  "datasets": "sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat",
  "epochs": 200,
  "seeds": [0, 1, 2],
  "env": {
    "R3S4B1_WIDTH": "32",
    "R3S4B1_BLOCKS": "2",
    "R3S4B1_MODES": "16",
    "R3S4B1_FILM_MLP_WIDTH": "64",
    "R3S4B1_BATCH": "16",
    "R3S4B1_LR": "1e-3",
    "R3S4B1_WD": "1e-5",
    "R3S4B1_CLIP": "1.0",
    "R3S4B1_SCHED": "cosine",
    "R3S4B1_TARGET_NORM": "train_zscore_global",
    "R3S4B1_VAL_FRAC": "0.1",
    "R3S4B1_VAL_MIN_N": "20",
    "R3S4B1_FLOOR_ARMS": "nn_condition,train_mean,zero,affine_on_hf_train",
    "R3S4B1_FLOORS_JSON": "mffp_autoresearch/round3/state/anchors_repaired/floors.json",
    "R3S4B1_ANCHORS_JSON": "mffp_autoresearch/round3/state/anchors/launch_anchors.json",
    "R3S4B1_FLOORS_LINEAGE_JSONS": "mffp_autoresearch/round3/state/anchors_repaired/floors_pre_ifc_swap_2026-08-05.json,mffp_autoresearch/round3/state/anchors_repaired/floors_pre_ac_trim_2026-08-06.json,mffp_autoresearch/round3/state/anchors_repaired/floors_pre_pfc_box_2026-08-06.json",
    "R3S4B1_FLOOR_TOL": "1e-9",
    "R3S4B1_EXPECTED_BEST_FLOOR_GEOMEAN": "36.3912",
    "R3S4B1_SEED_BOOTSTRAP_B": "10000",
    "R3S4B1_ROW_BOOTSTRAP_B": "10000",
    "R3S4B1_BOOT_SEED": "0",
    "R3S4B1_CELL_RUNGS": "finest_lf,coarsest_lf",
    "R3S4B1_LEAVE_TOP_K": "1,3,5,10",
    "R3S4B1_DEGEN_MEDIAN_FRAC": "0.01",
    "R3S4B1_DEGEN_ABS_FLOOR": "1e-6",
    "R3S4B1_GUARD_DATASETS": "heat_local,fluid,sharp__sod_1d",
    "R3S4B1_DATA_MANIFEST": "mffp_autoresearch/round3/state/data_hashes.json",
    "R3S4B1_DIAG_OUT": "mffp_autoresearch_outputs/round3/r3s4_audit/B1/eval"
  }
}
```

  Recipe notes: `base_commit` = `round3-substrate` HEAD (resolved at design time). **`datasets` MUST stay an explicit comma list** — `score_panel.py` resolves the literal `panel` through `round2/project.yaml`, i.e. the ROUND-2 panel (helmholtz in, ifc_heat out), which would silently score the wrong six datasets. `family_dir` follows the `models_r1/` → `models_r2/` progression that `round3/program.md` §5 calls "`models_r2/`-style"; `score_panel.py` takes an explicit `--family_dir`. Timing: `round2/state/timing_ledger.json` records this family at ~20.1 min/seed at 200 epochs × 6 datasets on h200 ⇒ request the project.yaml default `02:00:00`, mail `END,FAIL`. Guard leg runs separately at contract tier (`--datasets guard --epochs 2`).

- **Expected outcome**:
  1. **Floors reproduce exactly** — 6 panel + 3 guard × 4 arms within 1e-9, `zero ≡ 1.0`, best-floor geomean **= 36.3912** (arithmetic verified at design time), lineage 75.0673 → 38.6300 → 36.3912 reproduced. Δ vs anchor: none — this arm *is* the anchor's own arithmetic. A miss is the card's highest-value outcome (it would invalidate every denominator in the round).
  2. **Rung seam confirmed** — scored-cell MDD vs shipped `preflight_launch_2026-08-07.json`: pfc 0.0150 vs 0.6583 (43.9×), ch 1.6530 vs 1.0914 (1.52×), ac 0.1729 vs 0.2228, fkpp 0.3028 vs 0.2963; pfc's `OUTLIER_DOMINATED` clears on the scored cell (top-5 0.0528, half-width 0.0075), ch's worsens (0.7593, 0.8265); ADR r3-0003 D2's "~166 %" confirmed as the scored-cell number (165.30 %).
  3. **`seed_mce` far below the provisional constants** — predicted pfc 0.2–1.5 (vs 8.8595), ac 2–12 (vs 16.4223), fkpp 0.5–25 (vs 158.3322), ch 0.15–0.8 (vs 1.1604), ifc_poisson 0.0–1.0 (vs 0.2399), ifc_heat 0.00–0.05 (**no provisional constant exists — first certification**). Grounded in the four certified anchor cards' observed 3-seed spreads on this exact panel (pfc 0.20–0.89, ac 2.74–10.11, fkpp 0.55–23.74, ch 0.15–0.68, ifc_poisson 0.00–51.85, ifc_heat 0.00–0.03).
  4. **The two thresholds separate on exactly one dataset** — predicted `tau_abs/tau_rel`: pfc ≈ 1.0–1.5, ac ≈ 2–5, fkpp ≈ 2–6, ch ≈ **10–30** (reference term ~20 skill units vs the entire 11.09–13.02 ch range spanned by all four certified anchors) ⇒ pre-registered: **no cahn_hilliard claim is currently distinguishable against an absolute bar**, while same-reference ch comparisons stay licensed at `tau_rel ≈ 0.7`. On both ifc datasets `tau_abs ≡ tau_rel` exactly (paper-bar reference, `mdd_scored = 0`).
  5. **Certifier panel geomean 25–45** against the 36.3912 best-floor anchor (round-2's identical certifier: 19.82 vs a 23.06 anchor). Context only — the card's claim is about instruments, not performance.
  6. **Floor arms reported on every dataset** — `nn_condition` / `train_mean` / `zero` / `affine_on_hf_train` beside the certifier, with the per-dataset best floor (pfc 48.0773, ac 475.8568, fkpp 390.7015, ch 23.1803, ifc_poisson 8.0409, ifc_heat 1.3941) and the §2 affine floor on both ifc numbers (1.5938 / 0.9584).

  **vs noise floor**: F1/F2/F3 are deterministic recomputations with fixed bootstrap seeds — floor exactly 0.0, thresholds 1e-9 / 5 % / 0.05. F4's boundaries are set at 2× each dataset's provisional `min_claimable_effect` (pfc 17.7191 > 8.8595, ac 32.8446 > 16.4223, fkpp 316.6643 > 158.3322, ch 2.3207 > 1.1604, ifc_poisson 0.4798 > 0.2399), so every clause exceeds its floor by one further whole floor. `ifc_heat` is deliberately cited in no falsification clause — it has no provisional constant and therefore no floor to clear; its threshold is a first-time output reported without a pass/fail test.

- **Expected falsification**: the hypothesis — *"the repaired panel's training-free floors reproduce exactly, its shipped fifth-class instruments price a different cell than the one that scores it, and a byte-identical 3-seed certifier plus a paired row bootstrap yields two per-dataset claim thresholds materially different from each other and from the provisional level-proportional constants"* — is falsified if ANY of: **(F1)** any floor arm on any of the 9 datasets deviates from `floors.json` by > 1e-9 relative, or `zero ≠ 1.0`, or the best-floor geomean ≠ 36.3912 to 4 dp, or the lineage does not reproduce, or `data_binding.py verify` exits 3; **(F2)** the scored-cell `min_detectable_delta` agrees with the shipped preflight value within 5 % relative on **all four** copy-LF panel datasets (the seam is not real); **(F3)** `mdd_scored < 0.05` on ≥ 3 of the 4 copy-LF panel datasets (reference noise negligible panel-wide ⇒ the two-threshold composition is empty); or **(F4)** the certified `seed_mce` exceeds **twice** the provisional `min_claimable_effect` on ≥ 2 of {pfc 17.7191, ac 32.8446, fkpp 316.6643, ch 2.3207, ifc_poisson 0.4798} — which invalidates the round's 3-seed protocol (PROGRAM_NOTE MUST #4) and must be escalated to the operator, not absorbed.

- **Prior-art verdict quoted** (verbatim from `websearches/r3s4_audit/batch_1/report.md`):
  - **D1** — *per-dataset **claim threshold** on the repaired panel combining 3-seed condition→HF spread (numerator noise) with the copy-LF cell's bootstrap min-detectable-delta (denominator noise); replaces provisional `noise_floor.json`* → **`preempted-but-MF-composition-open (cite)`** · citations: https://search.r-project.org/CRAN/refmans/SpecsVerification/html/SkillScore.html · https://www.tmls.nyc/research/eval-sample-complexity · https://www.researchgate.net/publication/226389256_The_measurement_uncertainty_of_ratios_which_share_uncertainty_components_in_numerator_and_denominator · https://arxiv.org/abs/2604.04199 · open: *"No fetched source fuses training-seed variance and reference-cell sampling error into one claimability threshold, and none does so for a field-valued MF panel whose reference is a coarse PDE solve. Cheap adoptable extras: paired per-seed deltas + bootstrap instead of max−min; the documented ratio-of-normals caveat applies to cahn_hilliard (denominator uncertainty large ⇒ normal approximation fails). NOT open: bare max−min spread."*
  - **D3** — *per-cell estimator-integrity audit: leave-top-k-out / case-deletion influence on the per-row ratio sum + degenerate-row re-certification after the ac trim (n_test 100→78) and pfc box swap* → **`preempted-but-MF-composition-open (cite)`** · citations: https://www.stata.com/stata17/leave-one-out-meta-analysis/ · https://arxiv.org/pdf/2212.04612 · https://deep-and-shallow.com/2020/10/01/forecast-error-measures-scaled-relative-and-other-errors/ · https://arxiv.org/html/2605.29283v2 · **explicit search-negative**, iteration 4 · open: *"The statistics (case deletion) and the remedy (trim/Winsorize/median) are textbook — claim neither. Genuinely uncited: that a copy-LF-referenced cell is silently inflated by rows with no fidelity gap, and that certifying a test split against a per-row-gap threshold is a precondition for the metric to mean anything. Report as a project-local instrument finding backed by the recorded search-negative."*
  - **D2** — floor certification under a `data_binding` byte certificate → **`preempted (cite)`** · *"Every component published… Frame D2 as reproduction + certification only. The geomean discrepancy is a bookkeeping defect to fix, not a finding."* (executed as reproduction-only; the lineage is verified and closed, not claimed).
  - **D4** — the preflight/HOLD/ADR architecture → **`preempted (cite)`** · https://arxiv.org/html/2607.12301 · *"Convergently published 2026-07… Cite, never claim."*

- **Immutables self-check**: **pass (11/11)** — full positive evidence per item in [iteration_1.md](iteration_1.md) §"Immutables self-check". Nothing was flagged; no revision was needed. Summary of the load-bearing evidence: recipe `datasets` is `project.yaml panel:` verbatim in order and `R3S4B1_GUARD_DATASETS` is `guard_set:` verbatim (#2); every score flows through the byte-frozen `round2/eval/score_panel.py` and the probes vendor `panel_data`/`nrmse` rather than editing them, so no spec/eval/prompt edit is required and the D0 finding is reported as evidence for an operator decision rather than as a `preflight.py` patch (#3, #4); every knob is an `R3S4B1_*` env var in the recipe and therefore in the cache key (#5); `epochs: 200` = `tiers.smoke_epochs`, `seeds: [0,1,2]` = the §12.4 pre-directed exception, no full tier requested (#6); the vendored family already ran to completion under `<ckpt_dir>/last.pt` resume in round 2 (#8); F1–F3's noise floor is exactly 0 because I reproduced `floors.json` to 6 significant figures and the geomean to 4 dp from the same deterministic code path at design time, and F4's boundaries sit at 2× each dataset's provisional mce (#9); the nearest precedent is `r2s4_diag-B1`, superseded rather than falsified, with the four differences stated on the card (#10); all four floor arms including the standing zero column are reported on all nine datasets and are F1's comparison object (#11).

- **Anchor reference**: `null` (per-stream policy: all four round-3 streams are gap/lever/diag, so the own-stream anchor — best-floor panel geomean **36.3912** — is implicit; round 3 has no champion-re-targeting tuning stream).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none)* | — | Round 3 has no prior cards (`round3/experiment_cards/` does not exist), and all four round-2 `r2s4_diag` cards carry `reopen_candidate: false` (verified by reading B1–B4 JSON). | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| `r3s4_audit-B1` | diagnostic / claim-threshold + floor certification (repaired panel) | Byte-identical 3-seed certifier + paired row bootstrap certify TWO per-dataset thresholds (`tau_rel` for same-reference comparisons, `tau_abs` for absolute-bar claims), the training-free floors and the 36.3912 anchor are reproduced at 1e-9, and the fifth-class estimator-integrity instruments are re-pointed from the coarsest LF rung to the cell that actually scores the panel — including the first `ifc_heat` constant and a certified inapplicability statement for the two paper-bar cells. | filled |
