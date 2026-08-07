# Summary so far — Stream `r3s4_audit`, Batch 1

Packed 2026-08-07 for the pre-directed certification slot.
All paths below are repo-root-relative unless absolute.
Repo root: `/resnick/groups/Hippo/ezeng/mf_field`.

## 1. Websearch findings + prior-art verdict

Source: `mffp_autoresearch/round3/websearches/r3s4_audit/batch_1/report.md` (4 iterations, 12 WebSearch, 9 curl-fetches; the `WebFetch` tool was unavailable and every URL was retrieved with `curl` in that loop — the report records this honestly).

The four verdict rows, verbatim:

- **D1** — per-dataset **claim threshold** on the repaired panel combining 3-seed condition→HF spread (numerator noise) with the copy-LF cell's bootstrap min-detectable-delta (denominator noise); replaces provisional `noise_floor.json` → **`preempted-but-MF-composition-open (cite)`**.
  Open column: *"No fetched source fuses training-seed variance and reference-cell sampling error into one claimability threshold, and none does so for a field-valued MF panel whose reference is a coarse PDE solve. Cheap adoptable extras: paired per-seed deltas + bootstrap instead of max−min; the documented ratio-of-normals caveat applies to cahn_hilliard (denominator uncertainty large ⇒ normal approximation fails). NOT open: bare max−min spread."*
  Citations: `SkillScore` (SpecsVerification), the 2026 MDE atlas, the ratio-uncertainty paper, Roth 2026 leakage landscape.
- **D2** — floor certification (`zero`/`train_mean`/`nn_condition`/`affine_on_hf_train`) under a `data_binding` byte certificate → **`preempted (cite)`**.
  *"Every component published; the affine floor in particular is a 2025 paper's stated purpose… Frame D2 as reproduction + certification only. The geomean discrepancy is a bookkeeping defect to fix, not a finding."*
- **D3** — per-cell estimator-integrity audit: leave-top-k-out / case-deletion influence + degenerate-row re-certification after the ac trim and pfc box swap → **`preempted-but-MF-composition-open (cite)`**.
  *"Genuinely uncited: that a copy-LF-referenced cell is silently inflated by rows with no fidelity gap, and that certifying a test split against a per-row-gap threshold is a precondition for the metric to mean anything. Report as a project-local instrument finding backed by the recorded search-negative."*
  The search-negative is explicit (iteration 4, term 2, three framings, "No usable results").
- **D4** (meta) — the preflight/HOLD/ADR architecture → **`preempted (cite)`** (XScientist 2026 and two neighbours). Cite, never claim.

Directives "for the brainstormer" (report §For the brainstormer): frame B1 as instrument certification not method invention; certify TWO thresholds per dataset (numerator seed spread × denominator bootstrap MDD, claim threshold = the larger); use paired per-seed deltas + bootstrap, never max−min; flag cahn_hilliard's ratio-of-normals failure and use the bootstrap; report the degenerate-row defect class as a project-local finding with the negative recorded; and close two bookkeeping items (geomean lineage; cite DeLise et al. for `affine_on_hf_train`).

## 2. §12 conventions verbatim

Round-3 `program.md` §5 states: *"Round-2 §12 methodological rules apply verbatim"*, and round-3 `program.md` line 5: *"Round-2 program: `../round2/program.md` (its §2 score system, §12 methodological rules, and stream conventions apply verbatim except where amended below)."*
So this stream's conventions are `mffp_autoresearch/round2/program.md` §12 common block + §12.4.

§12 common block, verbatim:

> Common to all streams: quote the launch anchor (best-floor geomean 23.06) and the per-dataset floor table verbatim when designing; thresholds must clear the noise floor for the dataset(s) — while `state/noise_floor.json` is provisional, judge falsification clauses directly (§4.3); cite the websearcher's prior-art verdict; every proposal carries a complete `recipe` block; floor arms mandatory on model cards (§2.2).
>
> - **Registration of model-side lifts.** Any family or instrument code that resamples a field between grids (LF→HF lift, working-grid cap, prediction resample) MUST use the ADR r2-0001 per-dataset conventions — vendor the interpolators from `eval/panel_data.py` (the r2s2-B1/r2s3-B2 precedent) or use `factory_mffp/models/_common/lf_registration.py`. A bare `F.interpolate`/`zoom` on a panel dataset is the (r−1)/2 registration defect and is a reviewer FAIL.
> - **Target-scaler pre-flight.** Any model card that trains on `ext__helmholtz_2d` or `sharp__phase_field_crystal_2d` runs `tools/target_scale_spread_audit.py` on those datasets pre-flight; an `OUTLIER_DOMINATED` or `NEAR_ZERO_TARGETS` verdict requires per-sample target normalisation (or a card-recorded justification for keeping a global scaler).

§12.4 `r2s4_diag` (diagnostics), verbatim:

> - **B1 is pre-directed**: floor + spread certification. (a) Verify the frozen floors reproduce (standing zero-predictor column included); (b) train ONE minimal condition→HF baseline (smallest reasonable FiLM-FNO decoder or MLP→field) at smoke tier, seeds {0,1,2}, on the panel — its per-dataset seed spread replaces the provisional `state/noise_floor.json` (§4.3). Diagnostic card, but WITH training (3 seeds) — the exception is the point; cheap by design (small model).
> - Later batches: **value-of-LF accounting** — matched architecture ± LF training signal (coordinates with r2s3: r2s4 measures, r2s3 optimizes); **overfitting anatomy** at N_hf ∈ {5, 20, 50} (ifc ladder) and N=400 (sharp): train/test gap decomposition, effective sample counts (the **drift-class rule**: when n_eff/N < 1%, only in-job paired controls are controls).
> - The round-1 probe library is seeded in `tools/` (37 files; index header notes they were written against round-1 eval paths — adapt on use, promote adapted versions via the register turn).

Round-3 amendments that bind this stream (`round3/program.md`):

> §2: **Launch anchors** live in `state/anchors/launch_anchors.json`: best-floor geomean **36.3912** on the final 6-dataset panel (lineage: 75.0673 pre-A1 5-ds → 38.6300 after ifc_heat promotion → 36.3912 after the ac trim + pfc box swap, ADR r3-0002/r3-0003).
>
> §2 **Affine-floor rule**: … Every card reporting an ifc number therefore reports the fitted `affine_on_hf_train` floor next to it (ifc_poisson skill 1.59, ifc_heat 0.96); an ifc claim that does not beat this floor has learned nothing beyond linearity, and skill < 1 on ifc_heat is not by itself a strong claim.
>
> §3: `state/anchors_repaired/noise_floor.json` is PROVISIONAL; r3s4 re-certifies mce on the repaired panel before any criterion is adjudicated (round-1 §4.5 discipline).
>
> §4 stream table: `r3s4_audit` | diag | Certify the repaired-panel mce and floors; run the training-free instrument audits (including the repaired-ifc audit); own the close-evidence audits of PROGRAM_NOTE MUST #3.

## 3. Within-stream prior cards

Round 3 has **no** `experiment_cards/` directory yet (verified: `ls mffp_autoresearch/round3/experiment_cards` → does not exist).
This is the round's first card in this stream, so the within-stream lineage is the round-2 stream `r2s4_diag` (immutable read-only input, round-2 §5.13).

- **`r2s4_diag-B1`** (`round2/experiment_cards/r2s4_diag/batch_1/B1.json`, status `complete`, `reopen_candidate: false`) — the direct ancestor of this slot. Family `r2s4_cert_min` (condition-only FiLM-FNO decoder, width 32 / 2 blocks / 16 modes / FiLM-MLP 64, ~1M params, 200 epochs, seeds {0,1,2}, no field input anywhere). Delivered: exact floor reproduction, `noise_floor.json` with `min_claimable_effect = max(spread_maxmin, paired_null_95)` (Agarwal IQM + stratified bootstrap, Du paired per-seed deltas), and the conditional-mean-floor k*-NN probe. Part 6 measured training-free aleatoric barriers (fisher_kpp 1.010×, pfc 1.139×, allen_cahn ~1.11× — the certifier sits *at* the information barrier there) and found cahn_hilliard + ifc_poisson admit **no** training-free ceiling estimate. Part 7 asks for exactly what this slot must do: *"re-certify the seed spread on whatever arm B2 actually compares, because the installed constants were measured on a model that is collapsed on 3 of 6 datasets and therefore under-state the noise of any less-collapsed successor."*
- **`r2s4_diag-B2`** — value-of-LF accounting (DOPD advantage-gap ported to fields), complete, `reopen_candidate: false`.
- **`r2s4_diag-B3`** — teacher-projection channel ledger (reachable vs unreachable privileged advantage), complete, `reopen_candidate: false`.
- **`r2s4_diag-B4`** — ifc_poisson few-HF anatomy, complete, `reopen_candidate: false`. Records the ifc `min_claimable_effect` 0.9377 used in round 2 and the seed-provenance finding that its 3-init range **is** the ifc mce.

Stream anchor: no `state/anchors/r3s4_audit.json` exists; the certified launch anchor for every round-3 stream is `state/anchors/launch_anchors.json` best-floor panel geomean **36.3912** (verified at design time: `exp(mean(ln[48.0773, 475.8568, 390.7015, 23.1803, 8.0409, 1.3941])) = 36.3912`).

## 4. Cross-stream cards

None in round 3 (no cards exist yet).
From round 2, one card's part 7 speaks directly to this stream: `r2s4_diag-B1`'s `cross_stream_notes` supplies the training-free aleatoric barriers in copy-LF skill units for every stream and warns that `r2s1-B1`'s `certificate.implied_max_skill` is **not** a ceiling.
Those barriers were measured on the **pre-repair** panel and are void as numbers on the repaired data; the direction survives.

## 5. Reopen candidates

None.
All four round-2 `r2s4_diag` cards carry `reopen_candidate: false` (verified by reading each card JSON), and round 3 has no prior cards.

## 6. What is UNKNOWN

**(U1) The provisional `noise_floor.json` constants are not measured noise, and nobody has said so.**
`state/anchors_repaired/noise_floor.json` carries `_provisional: true`, `_source: "round1-batch0-rescaled"`.
Reading the file arithmetically at design time: every entry is reproduced exactly by `max(spread_maxmin, 0.10 × mean_skill)` — pfc `8.859540 = 0.10 × 88.595401` (spread 0.6361), allen_cahn `16.422285 = 0.10 × 164.222846` (spread 0.1423), fisher_kpp `158.332153 = 0.10 × 1583.321532` (spread 34.7904), cahn_hilliard `1.160357 = 0.10 × 11.603569` (spread 0.4023); only ifc_poisson (0.2399) and report-only helmholtz (10.6811) are spread-bound.
So on 4 of 6 datasets the binding term is a **level-proportional 10 % rule**, not noise — and the levels it is proportional to are the *round-1* skill levels, which the repairs changed by up to 7× (provisional ifc_poisson mean skill 1.5656 vs 8.25–21.14 across the four certified round-3 anchor cards; provisional fisher_kpp 1583.32 vs 172.25–374.84).
Consequence, measured at design time from `mffp_autoresearch_outputs/round3_anchors/*/eval/result_*.json` (4 certified cards × 3 seeds each): observed repaired-panel 3-seed spreads are pfc 0.1998–0.8919, allen_cahn 2.7352–10.1112, fisher_kpp 0.5505–23.7376, cahn_hilliard 0.1547–0.6753, ifc_poisson 0.0000–51.8527, ifc_heat 0.0000–0.0254.
The provisional constant is therefore **6.7×–288× too large** on fisher_kpp (forbidding every fisher_kpp claim) and **216× too small** on ifc_poisson relative to that dataset's worst observed instability (licensing pure seed noise).
Both error directions are live simultaneously.

**(U2) `ifc_heat` has no noise constant at all.**
It entered the panel by ADR r3-0001 A1 after `noise_floor.json` was written; the file has no `ifc_heat` key (verified).
Its certified anchor skills span 0.0725–1.5737 and its `affine_on_hf_train` floor is 0.9584 — i.e. the whole interesting range is inside one affine floor, and there is currently **no threshold that says whether an ifc_heat delta is real**.

**(U3) The fifth-class instruments price a different cell than the one that scores the panel.**
`preflight/preflight.py` selects the LF rung as `levels[0]` (the **coarsest**, `train_l1`/`test_l1`) — verified by reading lines 290–345 — while `round2/eval/panel_data.py::copylf_prediction` selects `lf_fid = max(data["lf_fids"])` (the **finest** LF rung, `l2`) under the ADR r2-0001 per-dataset convention.
The `preflight/README.md` nonetheless describes its fifth-class checks as running "on the canonical per-row copy-LF construction".
I recomputed `cell_stability` at design time on the **scored** cell through `eval/panel_data.py` + `eval/nrmse.py` (my per-row mean reproduces `floors.json` `reference.test_nrmse` exactly on all four copy-LF panel datasets — ac 0.00205936 vs 0.0020593576, ch 0.041803 vs 0.041802963, pfc 0.0182574 vs 0.018257409, fkpp 0.000165246 vs 0.00016524587, so the row vector *is* the scored cell), with the same seeded 1000-resample bootstrap:

| dataset | preflight (coarsest LF) MDD / top-5 share / status | scored cell (finest LF) MDD / top-5 share |
|---|---|---|
| pfc | 0.6583 / 0.3884 / `OUTLIER_DOMINATED` | **0.0150 / 0.0528** |
| allen_cahn | 0.2228 / 0.1310 / `OK` | 0.1729 / 0.1109 |
| fisher_kpp | 0.2963 / 0.1569 / `OK` | 0.3028 / 0.1475 |
| cahn_hilliard | 1.0914 / 0.6528 / `OUTLIER_DOMINATED` | **1.6530 / 0.7593** |

Two consequences that are currently unknown-but-decidable: pfc's shipped `OUTLIER_DOMINATED` warning is 43.9× over-priced and would **clear** on the scored cell, and cahn_hilliard's shipped min-detectable-delta understates the scored cell by 1.52× (109 % vs 165 %).
The 165 % figure matches ADR r3-0003 D2's own text ("~166 % minimum distinguishable model delta"), which suggests the red-team measured the scored cell and the shipped instrument re-implemented it on the coarsest rung.
Because D2 makes the shipped MDD a **claim-licensing rule**, the anti-conservative gap (109 %→165 %) is live: a ch delta between those two numbers is currently licensed and should not be.
This is not yet a proven defect — the coarsest rung is a defensible *screening* choice — but the README's canonicality claim and the ADR's own number disagree with the shipped values, and the resolution is a minutes-long training-free computation.

**(U4) The fifth-class instruments have never run on ifc at all.**
`state/preflight_launch_2026-08-07.json` reports `status: NO_DATA` for `ifc_poisson` and `ifc_heat` (verified), because `preflight.py` only understands the factory-npz `train_l*.npz` layout and ifc ships `ifc_raw` (`train/fidelity_<F>/{Xs,ys}.npy`).
Additionally both ifc datasets score against a **fixed paper bar** (`copylf_baselines.json`: `reference_type: paper_bar`, 0.036 / 0.074, "test ships HF only"), so `degenerate_rows` and `cell_stability` are not merely un-run there — in their shipped form they are **inapplicable**, and the correct denominator-noise statement for ifc is *exactly zero* (a constant), with all sampling noise living in the numerator over n_test = 128 rows.
Nobody has written that down.

**(U5) Does reference noise even belong in a within-panel threshold?**
The websearcher's own fetched source (*"The measurement uncertainty of ratios which share uncertainty components in numerator and denominator"*) implies the answer is *not always*: two arms scored against the **same** reference cell share the denominator, so it cancels in their ratio and only partially propagates into their difference.
The websearcher's directive ("claim threshold is the larger of the two") is therefore right for comparisons against an **absolute** bar (skill < 1, the paper bar, a cross-era comparison) and over-conservative for **same-reference** arm-vs-arm comparisons, which is what almost every round-3 card actually does.
Which of the two regimes a given round-3 claim falls into has never been specified, and getting it wrong is worth a factor of ~1.65 on cahn_hilliard alone.

**(U6) Bookkeeping — already closed, and the card should say so rather than reopen it.**
The websearcher's item 6(a) asks to reconcile 38.63 against program.md's 75.0673.
Verified at design time by recomputing best-floor geomeans from the archived floor files: `floors_pre_ac_trim_2026-08-06.json` gives **75.0673** on 5 datasets (no ifc_heat) and **38.6300** on 6; current `floors.json` gives **36.3912** on 6.
That is exactly the lineage `program.md` §2 already records, so the item is a resolved bookkeeping trail, not a stale number — the card should confirm the arithmetic and close it, not treat it as an open defect.

**(U7) Whether the round's 3-seed protocol can license anything at all on the repaired panel.**
PROGRAM_NOTE MUST #4 fixed 1-seed screening + seeds {1,2} as a close precondition, on the round-2 evidence that the only 3-seed CI was ~1.14 units wide against a certified mce of 1.1419.
On the repaired panel, `r2s2_stacked-B1`'s ifc_poisson per-seed skills are [4.9095, 3.3283, 55.1810] — a 51.85-unit spread inside one card.
Whether that is an ifc-specific pathology or the general condition of the panel is unknown until a byte-identical certifier is run across all six datasets.

**(U8) Which reference-era comparisons are legal.**
Three denominator changes have landed since round 2 (ifc swap, ac trim, pfc box). `copylf_baselines.json` `_notes` warns "Skills across the trim are not comparable", but no machine-checkable era tag exists on a result JSON beyond `nrmse_def_hash` / `copylf_def_hash`, and `data_binding.py` verify is a launch-time gate, not a per-result stamp.
Nothing currently stops a round-3 card from quoting a round-2 skill next to a round-3 skill.
