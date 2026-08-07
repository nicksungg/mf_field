# Iteration 1 — `r3s4_audit` batch 1 design

## Design context considered

- `summary_so_far.md` §6 unknowns U1–U8 (all measured or verified at design time, not recalled).
- The prior-art verdict rows D1–D4 (`websearches/r3s4_audit/batch_1/report.md`), in particular D1's `preempted-but-MF-composition-open (cite)` and D3's explicit search-negative.
- `round2/program.md` §12 common block + §12.4 (quoted verbatim in `summary_so_far.md` §2).
- `round3/program.md` §2 (launch anchors, affine-floor rule), §3 (`noise_floor.json` PROVISIONAL; r3s4 re-certifies before any criterion is adjudicated), §5 (immutables).
- `PROGRAM_NOTE.md` MUST #2 (defect ⇒ HOLD), MUST #3 (close on evidence), MUST #4 (in-round seed confirms), MUST #5 (panel mutable only under ADR).
- Stream anchor: `state/anchors/launch_anchors.json` best-floor panel geomean **36.3912** (arithmetic verified at design time from `floors.json`).
- Noise floor: `state/anchors_repaired/noise_floor.json`, `_provisional: true`. Per-dataset `min_claimable_effect`: pfc 8.859540, allen_cahn 16.422285, fisher_kpp 158.332153, cahn_hilliard 1.160357, ifc_poisson 0.239908, helmholtz (report-only) 10.681107; **`ifc_heat` absent**.
- Pre-falsified levers (`round1` §5, carried by round-2 §5): WNO backbone swap, LF low-mode freezing, diffusion prior for point accuracy. None is architectural to this card.
- `state/gates.md`: G1/G2/G3 all GREEN 2026-08-07; `r3s4_audit/current_batch.txt` = 1, `current_stage.txt` = brainstorm.

## Proposal reasoning

### The slot is pre-directed, so the design question is *what the certification must contain*, not *what to do*

`round3/program.md` §3 makes this card a gate on the entire round: no success criterion is adjudicable until the repaired-panel mce exists.
§12.4 fixes the shape (verify floors reproduce, standing zero column; train ONE minimal condition→HF baseline, smoke tier, 3 seeds, per-dataset spread replaces the provisional file).
The websearcher then says everything I would want to invent is published, and the only open thing is the *composition*.
So the design work is entirely in choosing which measurements make the composition correct and complete on **this** panel, and in refusing to claim any of the machinery.

### Alternatives weighed

**(A) Minimal re-run of round-2's r2s4-B1 recipe on the repaired panel.**
Cheapest and directly satisfies §12.4.
Rejected as insufficient: it would reproduce the round-2 *definition* (`max(spread_maxmin, paired_null_95)`) while the websearcher explicitly says "NOT open: bare max−min spread" and demands the denominator half; it would inherit the provisional file's silent `0.10 × mean_skill` term (U1); it would leave `ifc_heat` without a constant (U2); and it would leave the rung seam (U3) and the ifc inapplicability (U4) untouched, which are the two things that would make batch-2 the error-detector for batch-1 all over again — exactly the failure PROGRAM_NOTE MUST #3 was written to stop.

**(B) Overfitting anatomy at N_hf = 5.**
One of the three §12.4 menu options and the directive table's second alternative.
Rejected for batch 1: `r2s4_diag-B4` already executed it on ifc_poisson with an exhaustive 5-row Shapley decomposition, and nothing about it is gating.
It is a good batch-2/3 candidate once thresholds exist to judge its deltas against.

**(C) Floor certification with a standing zero column, as a standalone card.**
Rejected as a *card*: it is genuinely deterministic and takes minutes, so it should be one deliverable inside the certification card, not the whole of it. D2 is `preempted (cite)` and is reproduction-only, so a card built solely on it has no open content.

**(D) Chosen: fused claim-threshold certification with the fifth-class instruments re-pointed at the scored cell.**
This is (A) plus the four things that make it correct, and it is precisely D1's open composition plus D3's uncited project-local finding.
Every mechanism is adopted by citation (`SkillScore` for the denominator half; the 2026 MDE atlas for paired deltas / design effect; Agarwal IQM + stratified bootstrap and Du paired deltas from round-2 B1; Stata LOO meta-analysis / Cook–Weisberg case deletion for leave-top-k-out; DeLise et al. 2025 for `affine_on_hf_train`; Tribuo for provenance hashing; XScientist for the preflight/HOLD architecture).
The card claims **no** method.

### The one design decision that is genuinely mine: two thresholds, not one

The websearcher's directive is "claim threshold is the larger of the two".
That is right for one comparison class and wrong for the other, and the distinction is worth 1.65× on cahn_hilliard (U5).
Skill = model nRMSE / reference nRMSE.
When two arms are scored against the **same** reference cell, the reference is a shared multiplicative constant: the arms' skill *ratio* is exactly reference-free, and their skill *difference* is (nRMSE_A − nRMSE_B)/ref, whose significance is governed by the paired per-row numerator difference, not by the reference's own sampling error.
When a claim is made against an **absolute** bar (skill < 1, the ifc paper bar, a pre-repair number, a cross-round comparison), the reference does not cancel and its sampling error propagates in full.
The websearcher's own fetched source ("The measurement uncertainty of ratios which share uncertainty components in numerator and denominator") is the citation for exactly this cancellation, so this is adoption, not invention.
I therefore certify two constants per dataset and pre-register which one a given claim must use:

- `tau_rel(ds)` = max( `seed_mce(ds)`, `row_paired_95(ds)` ) — for same-reference, within-era arm-vs-arm comparisons.
  `seed_mce` = max(`spread_maxmin`, `paired_null_95`) (round-2 B1's definition, kept so the two rounds' constants are comparable; both components reported separately so the max−min term is visible and never used alone).
  `row_paired_95` = 95th percentile of |mean paired per-row skill difference| under a seeded 10 000-resample bootstrap over test rows, computed between two same-model seeds (a true null contrast).
- `tau_abs(ds)` = `tau_rel(ds)` + `mdd_scored(ds)` × (the arm's own skill level) — for absolute-bar or cross-era claims, where `mdd_scored` is the scored-cell bootstrap min-detectable-delta (relative).
  On the two ifc datasets the reference is a fixed paper-bar constant, so `mdd_scored ≡ 0` and `tau_abs ≡ tau_rel` — that identity is itself a certified output, and it is the first time the panel's two reference *types* have been given different noise treatments.

### The rung seam (U3) makes this urgent rather than merely tidy

I read both code paths and then measured the consequence.
`preflight.py` builds its per-row copy-LF gaps from `levels[0]` (the coarsest rung); `eval/panel_data.py::copylf_prediction` uses `max(lf_fids)` (the finest LF rung) under the ADR r2-0001 convention.
Recomputing on the scored cell reproduces `floors.json` `reference.test_nrmse` to 6 significant figures on all four copy-LF panel datasets, so the recomputation is the scored cell by construction, and it gives pfc MDD 0.0150 (vs shipped 0.6583, 43.9×), ac 0.1729 (vs 0.2228), fkpp 0.3028 (vs 0.2963), ch 1.6530 (vs shipped 1.0914, 1.52×).
ADR r3-0003 D2 turns the shipped MDD into a claim-licensing rule for cahn_hilliard; on the scored cell that rule is 1.52× too permissive, and ADR D2's own prose ("~166 %") agrees with my scored 165.30 % rather than with the shipped 109.14 %.
This is a live, anti-conservative error in a scoring rule, discovered before batch 1 spends anything — which is what the preflight architecture was built to do, just one layer up.

**Why I am not setting a HOLD myself.** PROGRAM_NOTE MUST #2 requires an agent that *finds a defect* on a scoring instrument to set the HOLD before writing it up. What I have is a reproducible **discrepancy between two instruments' conventions**, not a demonstrated defect: the coarsest rung is a defensible screening choice for a pre-launch gate, and no shipped *score* is affected (nRMSE/skill come from the frozen eval layer, untouched). What *is* affected is a claim-licensing constant in an ADR. My write scope is `brainstormer/{stream}/batch_1/` + `state/blocked.md`, and `blocked.md` is a precondition log, not the HOLD file. So I escalate: the orchestrator should adjudicate this before dispatch, and if it agrees the mismatch is unintended, MUST #2 requires the HOLD to be set first and ADR r3-0003 D2's constant to be re-issued. The card is designed to work either way — under a HOLD it becomes the repair's certification evidence; without one it is deliverable D0.

### Scope control

Deliberately excluded, with reasons recorded so a later batch can pick them up: the conditional-mean/k*-NN barrier probe (round-2 B1 §3.3 and B2/B3 already own it, and the repaired-panel re-measurement is a batch-2 job once thresholds exist); overfitting anatomy (B4 executed it); any value-of-LF arm (that is r3s3's question and this stream's batch-2 mandate); helmholtz beyond a report-only column.

## Proposal

**Category**: diagnostic / repaired-panel claim-threshold + floor certification (numerator seed noise × reference-cell row noise), with the fifth-class estimator-integrity instruments re-pointed at the scored cell and extended to the paper-bar (ifc) reference type.

**Card type**: `diagnostic` (with training — the §12.4 exception, 3 seeds).

**Motivation** (quotes the prior-art verdict): the batch-1 verdict row **D1** reads `preempted-but-MF-composition-open (cite)`, open column verbatim — *"No fetched source fuses training-seed variance and reference-cell sampling error into one claimability threshold, and none does so for a field-valued MF panel whose reference is a coarse PDE solve. Cheap adoptable extras: paired per-seed deltas + bootstrap instead of max−min; the documented ratio-of-normals caveat applies to cahn_hilliard (denominator uncertainty large ⇒ normal approximation fails). NOT open: bare max−min spread."* — and row **D3** reads `preempted-but-MF-composition-open (cite)`, open column verbatim — *"Genuinely uncited: that a copy-LF-referenced cell is silently inflated by rows with no fidelity gap, and that certifying a test split against a per-row-gap threshold is a precondition for the metric to mean anything. Report as a project-local instrument finding backed by the recorded search-negative."*
This card **is** that composition and that project-local finding, and nothing else in it is claimed: D2 (`preempted (cite)`) is executed as reproduction-only, and D4's preflight/HOLD architecture (`preempted (cite)`) is cited, never claimed.
`round3/program.md` §3 makes the card gating: *"`state/anchors_repaired/noise_floor.json` is PROVISIONAL; r3s4 re-certifies mce on the repaired panel before any criterion is adjudicated (round-1 §4.5 discipline)."*

**Concrete config** — one family + four worktree probes, all under the worktree, no `state/` writes (the orchestrator installs the certified file):

- **D0 — rung-seam reconciliation and instrument re-pointing** (`probes/cell_seam.py`, training-free, CPU, minutes).
  For each of the 4 copy-LF panel datasets and the 3 guard datasets, compute the per-row copy-LF gap vector twice: (i) through `eval/panel_data.py::copylf_prediction` (the SCORED cell, finest LF rung, ADR r2-0001 convention — vendored, not re-implemented, per the registration-of-lifts rule) and (ii) through `preflight.py`'s coarsest-rung construction.
  Seam assertion: the scored per-row mean must equal `floors.json[ds].reference.test_nrmse` to ≤1e-9 relative.
  Emit both variants' `degenerate_rows` (threshold `max(1e-6, 0.01 × median_row_gap)`) and `cell_stability` (seeded bootstrap, `n_boot` 10 000, top-5 share, CI95 half-width, `min_detectable_delta`), plus the ratio between them, and re-adjudicate ADR r3-0003 D1 (ac trim) and D2 (ch MDD) on the scored cell.
- **D1 — floor + anchor reproduction certificate** (`probes/floor_repro.py`, training-free, deterministic, seed 0, 6 panel + 3 guard datasets).
  Recompute `nn_condition`, `train_mean`, `zero`, and `affine_on_hf_train` (min-norm least squares, cited to DeLise et al. 2025 — https://arxiv.org/abs/2508.05831 — never presented as a project invention, and reported with its oracle-affine residual) **from the stripped view**, diff against `state/anchors_repaired/floors.json` at 1e-9 relative, assert `zero ≡ 1.0` exactly, recompute the best-floor panel geomean and assert `= 36.3912`, and reproduce the lineage 75.0673 (5-ds, `floors_pre_ac_trim_2026-08-06.json`) → 38.6300 (6-ds, same file) → 36.3912 (6-ds, current `floors.json`), closing the websearcher's bookkeeping item 6(a).
  Extend `affine_on_hf_train` to all six panel datasets so every dataset carries a fitted closed-form floor, not just ifc.
  Run `preflight/data_binding.py verify --manifest state/data_hashes.json` at job start and record the per-dataset sha256 in the card (Tribuo, https://arxiv.org/abs/2110.03022, cited for the provenance-hashing rationale).
- **D2 — numerator (seed) noise re-certification** (family `models_r3/r3s4_cert_min`).
  Vendor round-2's `r2s4_cert_min` **verbatim** from `round2/worktrees/r2s4_diag/B1/models_r2/r2s4_cert_min/` with provenance comments (round-2 branches are immutable), hyperparameters byte-identical (width 32, 2 FNO blocks, 16 modes, FiLM-MLP 64, batch 16, AdamW lr 1e-3 / wd 1e-5, cosine, clip 1.0, global train-z-scored targets, 10 % seeded val split disabled when N_hf < 20, native HF grid, checkpoint-resume from `<ckpt_dir>/last.pt`).
  Byte-identical reuse is the point: it makes the delta between the round-2 and round-3 constants attributable to the **data repair**, not to a model change.
  Scored at smoke tier (200 epochs), seeds {0,1,2}, on the explicit 6-dataset round-3 panel.
  Emit per-dataset `per_seed_skill`, `iqm`, `ci95_stratified_bootstrap`, `spread_maxmin`, `paired_null_95`, sign-flip permutation p, and `seed_mce = max(spread_maxmin, paired_null_95)`.
- **D3 — row (denominator / test-sampling) noise + the two-threshold fusion** (`probes/certify_thresholds.py`, CPU, after all 3 seeds).
  Seeded 10 000-resample paired row bootstrap over the test split for (a) the reference cell (copy-LF datasets only) and (b) the same-model seed-pair null contrast; produce `row_paired_95`, `mdd_scored`, `tau_rel`, `tau_abs` per dataset, plus an explicit `reference_type` field (`copylf` vs `paper_bar`) and, for the two `paper_bar` datasets, the certified statement `mdd_scored = 0` with the reason.
  Cahn_hilliard is handled by bootstrap only, with the ratio-of-normals caveat recorded verbatim: naive error propagation is invalid there because the denominator's relative uncertainty exceeds the numerator's.
  Emit `noise_floor_candidate.json` in the round-3 schema (including an `ifc_heat` entry — its first) for the orchestrator to install over `state/anchors_repaired/noise_floor.json`.
- **D4 — per-cell estimator-integrity audit** (`probes/cell_integrity.py`, training-free).
  Leave-top-k-out case deletion (k ∈ {1,3,5,10}) on each panel cell's per-row ratio sum, for the certifier and for each floor arm, cited to Cook–Weisberg case deletion / LOO meta-analysis (https://www.stata.com/stata17/leave-one-out-meta-analysis/); the influence table is reported, the statistics are not claimed.
  Re-certify the ac trim (n_test 78) and the pfc box swap (n_test 100) against the **scored**-cell per-row gap threshold, and record the D3 search-negative verbatim (websearch iteration 4, term 2, three framings, "No usable results") as the evidence that the degenerate-row framing is uncited.
  On ifc, certify that `degenerate_rows` / `cell_stability` are **inapplicable in their shipped form** (ifc_raw layout, test ships HF only, paper-bar reference) and substitute the applicable instrument: the n_test = 128 numerator row bootstrap plus the mandatory `affine_on_hf_train` column (ifc_poisson 1.5938, ifc_heat 0.9584).

**Recipe**:

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

Recipe notes for the starter/builder:

- `base_commit` is `round3-substrate` HEAD, resolved at design time (`git rev-parse round3-substrate` → `8aae33a7fab11ef8234f4bb7158c2bc1a8b4bf51`).
- **`datasets` MUST stay an explicit comma list.** `round2/eval/score_panel.py` resolves the literal string `panel` through `panel_data.load_config()`, which reads `round2/project.yaml` — i.e. the ROUND-2 panel (helmholtz in, ifc_heat out). Passing `panel` here would silently score the wrong six datasets. Verified by reading `score_panel.py` lines 266–270 and `panel_data.py::load_config`.
- `family_dir` uses `models_r3/` following the `models_r1/` → `models_r2/` progression that `round3/program.md` §5 calls "`models_r2/`-style"; `score_panel.py` takes an explicit `--family_dir` path, so the name is free.
- Timing: `round2/state/timing_ledger.json` records `r2s4_cert_min` at ~20.1 min per seed for 200 epochs × 6 datasets on h200. This card swaps helmholtz for ifc_heat (smaller) and adds only CPU probes ⇒ request the project.yaml default `02:00:00`, mail `END,FAIL` to `ezeng@caltech.edu`.
- Guard datasets are scored at contract tier in a separate leg (`--datasets guard --epochs 2`), per the round-2 precedent, and are used by D0/D1 as training-free controls.

**Expected outcome** (a diagnostic measures; these are predictions to be scored):

1. **Floor reproduction exact.** All 6 panel + 3 guard datasets × 4 arms match `floors.json` to ≤1e-9 relative; `zero ≡ 1.0` exactly; recomputed best-floor panel geomean **= 36.3912** (I verified this arithmetic at design time); lineage reproduces 75.0673 → 38.6300 → 36.3912. A miss is the highest-value outcome of the card because it would invalidate every denominator in the round. Δ vs anchor: none — this arm *is* the anchor's own arithmetic.
2. **Rung seam confirmed.** Scored-cell `cell_stability` differs from the shipped `preflight_launch_2026-08-07.json` values by pfc 43.9× (MDD 0.0150 vs 0.6583), ch 1.52× (1.6530 vs 1.0914), ac 1.29×, fkpp 1.02×; pfc's `OUTLIER_DOMINATED` status **clears** on the scored cell (top-5 share 0.0528 < 0.4, half-width 0.0075 < 0.25) and ch's persists and worsens (0.7593, 0.8265); ADR r3-0003 D2's "~166 %" is confirmed as the scored-cell number (165.30 %) and the shipped 109.14 % identified as the coarsest-rung variant.
3. **Certified `seed_mce` far below the provisional constants on the sharp panel.** Prediction ranges, against the provisional values: pfc 0.2–1.5 (vs 8.8595), allen_cahn 2–12 (vs 16.4223), fisher_kpp 0.5–25 (vs 158.3322), cahn_hilliard 0.15–0.8 (vs 1.1604), ifc_poisson 0.0–1.0 (vs 0.2399), ifc_heat 0.00–0.05 (**no provisional constant exists — first certification**). Grounded in the observed 3-seed spreads of the four certified anchor cards on this exact panel (pfc 0.20–0.89, ac 2.74–10.11, fkpp 0.55–23.74, ch 0.15–0.68, ifc_poisson 0.00–51.85, ifc_heat 0.00–0.03).
4. **The two thresholds separate materially on exactly one dataset.** Predicted `tau_abs / tau_rel`: pfc ≈ 1.0–1.5 (`mdd_scored` 0.0150 is negligible), ac ≈ 2–5, fkpp ≈ 2–6, ch ≈ **10–30** (`mdd_scored` 1.6530 × a skill level of ~12–13 ⇒ a reference term of ~20 skill units, larger than the entire 11.09–13.02 range that all four certified anchor cards span on ch). Pre-registered consequence: **no cahn_hilliard claim is currently distinguishable against an absolute bar**, while same-reference within-panel ch comparisons stay licensed at `tau_rel ≈ 0.7`. On ifc_poisson and ifc_heat, `tau_abs ≡ tau_rel` exactly (paper-bar reference, `mdd_scored = 0`).
5. **Certifier panel geomean** (secondary, not a claim): 25–45 against the 36.3912 best-floor anchor, i.e. at or somewhat better than the floor. Round-2's identical certifier scored 19.82 on the round-2 panel against a 23.06 anchor; the repaired panel's harder ac/fkpp cells and the ifc_heat-for-helmholtz swap widen the band. This number is reported for context only — the card's claim is about instruments, not performance.
6. **Floor-arm comparison** (spec §3, mandatory even though this is a diagnostic): the certifier's per-dataset skill is reported beside all four floor arms from `state/anchors/floors.json` — `nn_condition` / `train_mean` / `zero` / `affine_on_hf_train` — and beside the per-dataset best floor (pfc 48.0773 train_mean, ac 475.8568 nn_condition, fkpp 390.7015 train_mean, ch 23.1803 nn_condition, ifc_poisson 8.0409 nn_condition, ifc_heat 1.3941 nn_condition). Both ifc numbers additionally carry the §2 affine floor (ifc_poisson 1.5938, ifc_heat 0.9584); an ifc number that does not beat those has learned nothing beyond linearity.

**Expected falsification**: the card's hypothesis — *"the repaired panel's training-free floors reproduce exactly, its shipped fifth-class instruments price a different cell than the one that scores it, and a byte-identical 3-seed certifier plus a paired row bootstrap yields two per-dataset claim thresholds that are materially different from each other and from the provisional level-proportional constants"* — is falsified if ANY of:

- **(F1, deterministic)** any of the 4 floor arms on any of the 6 panel + 3 guard datasets deviates from `state/anchors_repaired/floors.json` by > 1e-9 relative, or `zero ≠ 1.0` exactly, or the recomputed best-floor panel geomean ≠ 36.3912 to 4 dp, or the lineage does not reproduce 75.0673 / 38.6300 / 36.3912, or `data_binding.py verify` exits 3.
- **(F2, deterministic)** the rung seam is not reproducible: the scored-cell `min_detectable_delta` agrees with the shipped preflight value within 5 % relative on **all four** copy-LF panel datasets — i.e. my design-time measurement of a 43.9× pfc and 1.52× ch discrepancy was an artifact of my own reading, and no instrument re-pointing is warranted.
- **(F3, composition empty)** `mdd_scored < 0.05` on ≥ 3 of the 4 copy-LF panel datasets — i.e. reference-cell sampling noise is negligible panel-wide, `tau_abs ≈ tau_rel` everywhere, and the two-threshold composition carries no information. (Design-time measurement: only pfc, 0.0150, is below 0.05; ac 0.1729, fkpp 0.3028, ch 1.6530 are not.)
- **(F4, protocol viability)** the certified `seed_mce(ds)` **exceeds twice the provisional `min_claimable_effect`** on ≥ 2 of {pfc, allen_cahn, fisher_kpp, cahn_hilliard, ifc_poisson} — thresholds `> 17.7191`, `> 32.8446`, `> 316.6643`, `> 2.3207`, `> 0.4798` respectively. Each boundary sits one full provisional mce above the provisional value, so the clause clears the dataset's noise floor by construction. Firing means condition→HF training on the repaired panel is noisier than the borrowed constants and 3 seeds license only enormous effects — an outcome that invalidates the round's seed protocol (PROGRAM_NOTE MUST #4) and must be escalated to the operator, not absorbed.

*Attached floor-arm reasoning* (spec §3): F1's comparison object is the mandatory floor-arm set itself (`nn_condition` / `train_mean` / `zero` from `state/anchors/floors.json`, plus the §2 `affine_on_hf_train` column), reported as `ref_*` splits beside the certifier on every dataset; the standing zero-predictor column is present on all nine datasets, and the certifier's per-dataset skill is judged against the per-dataset best floor quoted in expected-outcome item 6. A certifier that does not beat the best floor on a dataset has learned nothing there, and that is reported as such rather than hidden.

**Anchor reference**: `null` (per §4.5 of the brainstormer spec: all four round-3 streams are gap/lever/diag, so the own-stream anchor — best-floor panel geomean 36.3912 — is implicit and no champion re-targeting applies).

## Status

- Slot covered: yes, one proposal (`r3s4_audit-B1`, diagnostic).
- Skipped: no.
- Reopen candidates resolved: none existed (round 3 has no prior cards; all four round-2 `r2s4_diag` cards carry `reopen_candidate: false`).
- Immutables self-check: **pass (11/11)** — see below.
- **Escalation attached (not a blocker for this slot):** the U3 rung seam is a candidate defect in a claim-licensing constant (ADR r3-0003 D2). The orchestrator should adjudicate MUST #2 before dispatch. I did not set the HOLD because I have a reproducible convention discrepancy, not a proven defect, and my write scope excludes the HOLD file.

## Immutables self-check (round-3 §4.5, 8 + 3)

1. **Data read-only.** The card writes nothing under any dataset root: D0/D1/D4 read the stripped view and (for offline reference computation only, the documented `panel_data.load_split` path) the original arrays; D2 trains on the existing HF train splits at their shipped sizes (400 sharp, 5 ifc HF rows); no regeneration, no extra HF, no LF downsampled from HF anywhere. `data_binding.py verify` at job start proves the bytes are the launch-manifest bytes.
2. **Panel + guard set fixed.** The recipe's `datasets` string is exactly `project.yaml panel:` in order, and `R3S4B1_GUARD_DATASETS` is exactly `project.yaml guard_set:`. The card proposes no panel change; the ac trim and pfc swap it audits are already-landed ADR decisions (r3-0002/r3-0003), and re-certifying them changes no data.
3. **Eval layer / spec untouched.** Every scored number flows through the frozen `round2/eval/score_panel.py` with unmodified bytes; the probes *import and vendor* `panel_data.copylf_prediction` / `nrmse.nrmse` rather than editing them, and write only to the worktree and `outputs_root`. The card requires no edit to `round2/eval/`, `project.yaml`, `program.md`, `preflight/`, or any agent prompt — the D0 finding is reported as evidence for an operator/ADR decision, and the proposed re-pointing happens in the card's own probe, not in `preflight.py`.
4. **One nRMSE definition.** All scores come from `round2/eval/nrmse.py` (`nrmse = mean_i ||pred_i − y_i||₂ / ||y_i||₂`); `NRMSE_DEF_HASH` and `_copylf_def_hash` are asserted identical across all seeds and all probe outputs. The bootstrap resamples rows of that metric; it does not redefine it.
5. **Contract CLI fixed.** The family exposes the unchanged six-arg `smoke_eval.py` signature; every knob the card introduces is an `R3S4B1_*` env var listed in the recipe `env` block and passed via `score_panel.py --env`, so all of it enters the cache key.
6. **Seeds {0,1,2}, tier epochs fixed.** `seeds: [0,1,2]` and `epochs: 200` = `project.yaml tiers.smoke_epochs`; guard leg at `contract_epochs: 2`. No full tier (2500) is requested. The 3-seed run is exactly the §12.4 pre-directed exception for this card.
7. **Guarded factory surfaces untouched.** Nothing in the card touches `mf_field/factory_mffp/{data,baselines,eval,references,scripts}`, `factory.md`, `akash/`, or any generator surface; the only factory imports are the read-only `data_adapters` plumbing (`loaders.load_mf_dataset`, `geometry.resolve_grid`, `metrics.finalize_and_write`) that round-2 families already use.
8. **Checkpoint-resume implementable.** The vendored `r2s4_cert_min` already implements resume from `<ckpt_dir>/last.pt` keyed on `(epochs_target, grid, seed)` and ran to completion under it in round 2 (three COMPLETED jobs, `round2/state/timing_ledger.json`); the vendoring is verbatim, so the behaviour carries over. The CPU probes are idempotent and re-runnable from their inputs.
9. **Falsification threshold exceeds the noise floor on every cited dataset.**
   F1 and F2 are deterministic recomputations on fixed bytes with fixed bootstrap seeds (`R3S4B1_BOOT_SEED=0`): their noise floor is exactly **0.0**, and the thresholds are 1e-9 relative (F1) and 5 % relative (F2) — both strictly greater. Positive evidence that the floor really is 0: I reproduced `floors.json` `reference.test_nrmse` at design time to 6 significant figures on all four copy-LF datasets (0.00205936 / 0.041803 / 0.0182574 / 0.000165246 vs 0.0020593576 / 0.041802963 / 0.018257409 / 0.00016524587) and the best-floor geomean to 4 dp (36.3912), from the same code path, with no seed involved.
   F3's threshold (0.05 relative) is likewise on a deterministic, seeded-bootstrap quantity (floor 0.0) and sits 3.5×–33× away from the three design-time measurements it must discriminate (ac 0.1729, fkpp 0.3028, ch 1.6530).
   F4 is the only seed-dependent clause, and its boundaries are set at **2× the provisional `min_claimable_effect`** for each cited dataset — pfc 17.7191 > 8.8595, allen_cahn 32.8446 > 16.4223, fisher_kpp 316.6643 > 158.3322, cahn_hilliard 2.3207 > 1.1604, ifc_poisson 0.4798 > 0.2399 — i.e. every boundary exceeds that dataset's noise floor by one further whole floor, and also exceeds every 3-seed spread actually observed on the repaired panel for that dataset (max observed: pfc 0.8919, ac 10.1112, fkpp 23.7376, ch 0.6753; ifc_poisson's 51.8527 outlier is a single known-unstable card, `r2s2_stacked-B1`, and is reported rather than used as the floor). `ifc_heat` is deliberately **not** cited in any falsification clause because it has no provisional constant and therefore no floor to clear — its threshold is a first-time output, reported without a pass/fail test.
10. **Not a pre-falsified lever.** Nearest pre-falsified levers (round-1 §5, carried by round-2 §5): WNO backbone swap, LF low-mode freezing, diffusion prior for point accuracy. None is architectural to this card — the model is round-2's already-run FiLM-FNO certifier, reused verbatim as a measuring instrument with no architectural change proposed and no performance claim attached. The nearest *methodological* precedent is round-2 `r2s4_diag-B1`, which is not falsified but **superseded**: it certified constants on the pre-repair panel with a definition (`max(spread_maxmin, paired_null_95)`) that has no denominator term, on a panel whose ac/pfc/ifc denominators have since changed and which did not contain `ifc_heat`. The differences are stated on the card: two thresholds instead of one, scored-cell instrument re-pointing, paper-bar reference type handled explicitly, `ifc_heat` added.
11. **Mandatory floor arms present.** All four arms (`nn_condition`, `train_mean`, `zero`, `affine_on_hf_train`) are computed from `state/anchors/floors.json` / `state/anchors_repaired/floors.json` and reported beside the certifier on every one of the 6 panel + 3 guard datasets; the standing zero column is unconditional; F1's comparison object is that arm set; and expected-outcome item 6 states the per-dataset best floor the certifier is judged against, with the §2 affine floor attached to both ifc numbers.
