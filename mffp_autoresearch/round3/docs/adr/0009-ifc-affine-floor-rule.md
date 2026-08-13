# ADR r3-0009 (RATIFIED — Option B): the ifc affine-floor rule

**Status: RATIFIED 2026-08-12 — operator (Eloise) chose Option B** (keep the rule, complete its numbers), ruled in-session via the decision brief (artifact `44eb5976`) after the recommendation below; recorded in `state/orchestrator_flow.md` (2026-08-12 operator-decisions entry).
Executed the same day: `program.md` §2 line 38 replaced with the Option B text below.
Per the retro-active section, the shipped report is left alone with no footnote — under Option B nothing in it becomes false.

Original proposal follows unchanged.
Nothing in this document is executed, and nothing in it changes a round-3 number.
Raised from round-3 report §12 item 1 ("ifc affine-floor rule change — the explainer was delivered 2026-08-10; program.md §2's rule text stands unchanged until she rules"), drafted 2026-08-12 after re-verifying every cited number against its primary artifact.
The status quo is in force and has been honoured throughout: the mandatory disclosure appears in round-3 report §2 and on every ifc reading in the round.
Sibling document: ADR r3-0008 (PROPOSED) handles panel composition and the one-cell-headline rule; the two do not overlap (see "What this does NOT decide").

## In plain language (read this first)

An "affine floor" is a deliberately dumb baseline: fit a straight-line formula from the handful of expensive examples we have, then see how well that formula does, and require any real model to at least beat it.
On the two `ifc` datasets we have only five expensive (high-fidelity) examples to fit that straight line from — like estimating "the average customer" from five customers.
Drop any one of those five and the number moves enormously: on `ifc_heat` the floor goes from $0.96$ (better than the published benchmark bar) to $1.85$ (worse than it), so the yardstick itself changes sides depending on which four examples you happen to use.
Because our own rules make quoting that floor **mandatory** next to every `ifc` result, a yardstick that flips can flip how a headline reads — "beats the paper bar" versus "does not".
The question for you is only *how we quote it*: as it stands today (one fit, plus its full drop-one spread), as the average over the five drop-one fits, or as a disclosure that no longer disqualifies anything.

## The rule as it stands today

`mffp_autoresearch/round3/program.md`, §2 ("Score system"), **line 38**, quoted verbatim:

> - **Affine-floor rule (degeneracy audit 2026-08-05; fold-fragility measured by r3s4-B2; scope amended by ADR r3-0007):** every card reporting an ifc number (scored `ifc_heat` or report-only `ifc_poisson`) reports the fitted `affine_on_hf_train` floor next to it WITH its leave-one-out fold range — the quoted single-fit values (ifc_poisson skill 1.59, ifc_heat 0.96) are single-draw values of an exactly-determined 6-dof fit on 5 rows, and ifc_heat's floor crosses skill 1.0 under leave-one-out (0.9584 single-fit → LOO mean 1.8469, fold sd ~10.9 tau_rel). An ifc claim that does not beat the DISCLOSED RANGE has learned nothing beyond linearity; skill < 1 on ifc_heat is not by itself a strong claim. The affine arm's exact reproduction adjudicates against its pinned per-arm band (`state/floor_tolerances_install_note.json`), not the dataset-level tolerance.

That is the object under discussion.
It is a *reporting and adjudication* rule, not an aggregation rule — see "What does not move under any option" below.

## Provenance of the 2026-08-10 explainer

**The explainer itself is not on file as a standalone artifact.**
I searched `mffp_autoresearch/` for any 2026-08-10 explainer, brief, or email artifact and found none; `state/transcripts/inbox/` is empty.
What exists is the *record that it was delivered*, in three places, plus the written argument it was drawn from:

- `round3/state/orchestrator_flow.md` (2026-08-10 operator-decisions entry, item 4): "ifc affine-floor rule: explainer delivered to operator; program.md §2 text UNCHANGED until she rules."
- `round3/state/batch3_scope_2026-08-10.md` line 4: she "asked for a fuller explanation of the ifc affine-floor question before deciding it (that decision stays OPEN; nothing in batch 3 depends on it, but every ifc claim keeps the mandatory affine-floor disclosure as written in program.md §2 until she rules)."
- `round3/index.md` line 51 and `round3/state/maintainer_report.md` line 321 carry the same status.

The substantive argument that was put to her is `docs/adr/0007-ifc-panel-composition.md` §"Interaction with the open affine-floor question" (lines 58–61), which reads:
"If B is chosen, the affine-floor rule question is MOOT for scored claims (no scored ifc cells).
If A or C, the recommendation on file stands: keep the rule, disclose the fold range (option A of that question); the floor-definition change (fold-averaged) is not needed once poisson — the worse offender — is report-only."
`PROFESSOR_UPDATE_2026-08-10.md` §7.1 (the bullet "Affine floors are now always quoted with their leave-one-out fold range") is the shipped prose version of the same argument.
This ADR reconstructs the two named alternatives from those sources and adds two more; it does not claim to reproduce the delivered explainer's wording.

## Why the rule is being questioned (every number re-verified)

Sources, abbreviated below:
`B2s4` = `round3/experiment_cards/r3s4_audit/batch_2/B2.json`;
`FLOORS` = `round3/state/anchors_repaired/floors.json`;
`FILM` = `round3/state/anchors/film_denominator.json`;
`MEANREM` = `round3/state/adr0007_meanremoved_check_2026-08-10.json`;
`INSTALL` = `round3/state/floor_tolerances_install_note.json`.

**The mandated quantity is the least stable one in the audit.**
`B2s4` turn 2A, verbatim: "ifc_poisson full-fit skill 1.5938 -> LOO mean 4.2335 (systematic +3.820 +- 0.719 tau, 5/5 folds breach); ifc_heat 0.9584 -> LOO mean 1.8469 (systematic +5.417 +- 4.890 tau, sd 10.935 tau, p95 20.534 tau, 3/5 folds breach)."
The same card's `surprises` block names it directly: the affine floor "is the least stable quantity in the whole audit", and the earlier D4 seam scan could not see it because it asked only about $n = 320$ fit sets, which exceeds the $5$ HF train rows (recorded `N_EXCEEDS_TRAIN_ROWS` / seam `UNDEFINED`).
The fit is exactly determined: $6$ degrees of freedom on $5$ rows on `ifc_heat` ($\mathrm{cond\_dim} = 3$), $\mathrm{cond\_dim} = 5$ with a rank-deficient design ($5/6$, documented min-norm pick) on `ifc_poisson` (`FLOORS`; ADR r3-0007 line 17).

**The unit arithmetic, so the two scales are not confused.**
On `ifc_heat` the reference is the paper bar $0.074$ (`FLOORS`, `reference.convention = paper_bar`), and the affine floor is $0.07091834$ nRMSE per-sample-mean (`MEANREM` `floors.affine_on_hf_train.raw_per_sample_mean`).
$0.070918 / 0.074 = 0.95835$, which reproduces the quoted single-fit skill $0.9584$ exactly.
The LOO-mean skill $1.8469$ therefore corresponds to $1.8469 \times 0.074 = 0.13667$ nRMSE.
On `ifc_poisson` the paper bar is $0.036$ (`FLOORS`; program.md §2 line 31).

**It flips a headline in the direction that matters.**
Below skill $1.0$ the dumb baseline beats the published paper bar; above it, it does not.
The single fit sits at $0.9584$ and the drop-one mean at $1.8469$ — the yardstick crosses the bar under a change of *which four rows it was fitted on*, with $3/5$ folds breaching $\tau_{rel}$.

**`ifc_poisson` is exactly affine, so there the floor is not a floor but the answer.**
Oracle-affine residual $5.4 \times 10^{-16}$ (`B2s4`, quoted in ADR r3-0007 line 15 as r3s4-B2 turn 3 / degeneracy audit 2026-08-05) — machine precision.
That cell is already report-only under ADR r3-0007 (option C, ratified 2026-08-10).

**The affine arm is already declared non-adjudicable for reproduction.**
`INSTALL` `_affine_arm_declaration`: "affine_on_hf_train is NOT YET ADJUDICABLE under the installed per-dataset table: its own per-arm band exceeds the recommended tolerance on 8 of 10 datasets."
The rule's last sentence already routes around this by pinning per-arm bands (`ifc_heat` $3.377 \times 10^{-7}$, `ifc_poisson` $5.654 \times 10^{-7}$).
So the rule is internally consistent on *metrology*; the open question is only about the *value* it quotes and the *disqualification* it imposes.

**But the round's one genuine learned win survives the floor at its fold-worst.**
`FILM` `datasets.ifc_heat`: film-transfer nRMSE $0.0361336$ (3-seed mean), `skill_copylf_of_film` $= 0.48829$.
That is below the affine floor under every definition considered here ($0.070918$ single-fit, $0.13667$ fold-averaged).
`MEANREM` also records the mean-removed check that kept `ifc_heat` scored under ADR r3-0007.
So no option below endangers the round's headline ifc result.

**One gap in the current text, noted for the record.**
The rule mandates disclosing the leave-one-out fold range but its own quoted values carry the LOO number for `ifc_heat` only; `ifc_poisson`'s "skill 1.59" appears with no LOO companion, although `4.2335` (5/5 folds breach) is measured and is printed in round-3 report §2.

## What does not move under any option

- **No panel aggregate.**
  `affine_on_hf_train` is not an arm of the best-floor anchor: `FLOORS` carries only `nn_condition`, `train_mean` and `zero` for both ifc cells, and the installed tolerance table (`INSTALL`) was computed over those same three arms.
  The launch best-floor geomean $53.2146$ and its lineage are untouched by every option here.
- **No nRMSE, no re-score, no GPU.**
  Every option is a change of quoted reference value and/or adjudication wording.
- **No card verdict on `ifc_heat` or `ifc_poisson` that was gated on a falsification clause.**
  Verified on the one card where this was least obvious: r3s1-B1's `expected_falsification` gates L1/L2 on the panel geomean and the closed-form law, L3 on per-direction OOF margins, and L4 on the best frozen floor *of the four sharp cells only*, with the clause stating in terms that "the two ifc cells carry no falsification weight (N_hf = 5, anecdote-grade)".
  Its ifc affine reading is a mandatory *disclosure* line, not a clause.

## Options

Each option gives the text exactly as it would replace `program.md` §2 line 38.

### Option A — keep the rule verbatim (pure status quo)

Replacement text: **none**; line 38 stands as quoted above.

Effect on shipped round-3 numbers: **nothing changes.**
No published claim changes sign.
Cost: the `ifc_poisson` LOO gap above stays in the text, and every future ifc card re-derives "the disclosed range" from prose rather than from a pinned pair of numbers.

### Option B — keep the rule, complete its numbers (RECOMMENDED)

Replacement text:

> - **Affine-floor rule (degeneracy audit 2026-08-05; fold-fragility measured by r3s4-B2; scope amended by ADR r3-0007; numbers completed by ADR r3-0009):** every card reporting an ifc number (scored `ifc_heat` or report-only `ifc_poisson`) reports the fitted `affine_on_hf_train` floor next to it WITH its leave-one-out fold range. The quoted single-fit values are single-draw values of an exactly-determined 6-dof fit on 5 HF train rows, and BOTH cells are fold-catastrophic under exhaustive leave-one-out (r3s4-B2 turn 2A): `ifc_poisson` 1.5938 single-fit → LOO mean 4.2335 (systematic +3.820 ± 0.719 tau_rel, 5/5 folds breach); `ifc_heat` 0.9584 single-fit → LOO mean 1.8469 (systematic +5.417 ± 4.890 tau_rel, fold sd 10.935 tau_rel, p95 20.534 tau_rel, 3/5 folds breach — the floor crosses skill 1.0 under leave-one-out). The DISCLOSED RANGE for adjudication is the pair (single-fit, LOO mean) as stated here; an ifc claim that does not beat BOTH has learned nothing beyond linearity; skill < 1 on ifc_heat is not by itself a strong claim. The affine arm's exact reproduction adjudicates against its pinned per-arm band (`state/floor_tolerances_install_note.json`), not the dataset-level tolerance.

Effect on shipped round-3 numbers: **nothing changes, and no published claim changes sign.**
Every number added is already printed in round-3 report §2 (the report quotes both LOO means and both breach counts verbatim), so this option makes the rule text say what the report already says.
The adjudication set is unchanged in practice: it names "beat both" where the current text says "beat the DISCLOSED RANGE", and on both cells the LOO mean is the *looser* of the pair, so nothing that passed before fails now.

### Option C — fold-averaged floor definition

Replacement text:

> - **Affine-floor rule (degeneracy audit 2026-08-05; fold-fragility measured by r3s4-B2; scope amended by ADR r3-0007; definition changed by ADR r3-0009):** every card reporting an ifc number (scored `ifc_heat` or report-only `ifc_poisson`) reports the `affine_on_hf_train` floor next to it. The floor IS the exhaustive leave-one-out fold mean over the 5 HF train rows — `ifc_poisson` 4.2335, `ifc_heat` 1.8469 (r3s4-B2 turn 2A) — not the single all-rows fit; the single-fit values (1.5938 / 0.9584) are quoted beside it as provenance only, with the fold spread (5/5 and 3/5 folds breaching tau_rel; ifc_heat fold sd 10.935 tau_rel). An ifc claim that does not beat the fold-averaged floor has learned nothing beyond linearity. The affine arm's exact reproduction adjudicates against its pinned per-arm band (`state/floor_tolerances_install_note.json`), not the dataset-level tolerance.

Effect on shipped round-3 numbers: no number is recomputed, but the floor a claim is read against becomes looser, and **two published per-cell readings change sign**:

1. **r3s1-B1's mandatory floor-arm reading on `ifc_heat` flips from LOSS to WIN.**
   `experiment_cards/r3s1_factorised/batch_1/B1.json`, `5_actual_result.falsification_3seed_readings.mandatory_floor_arm_readings.vs_ref_affine_on_hf_train`, verbatim: "test_hf LOSES on 4 of 5 cells at the 3-seed mean (… ifc_heat 0.9964 vs 0.9584)".
   Against $1.8469$, $0.9964$ wins, and that sentence becomes "loses on 3 of 5".
   The card's verdict (`falsification_verdict = confirmed`) does not move — the ifc cells carry no falsification weight in its clause set (verified above).
2. **r3s2-B2's `ifc_poisson` claimability annotation flips.**
   `experiment_cards/r3s2_field_reach/batch_2/B2.json`, `5_actual_result.falsification_3seed.G1_route.per_dataset_leg.ifc_poisson.claimable_reason`, verbatim: "floor-arm rule: at the 3-seed mean A1 (3.1298) and A3 (5.0553) BOTH lose the mandatory affine_on_hf_train floor (1.5938), so this cell yields no claimable route delta".
   Against $4.2335$, A1 ($3.1298$) wins while A3 ($5.0553$) still loses.
   `affine_on_hf_train` is `ifc_poisson`'s *tightest* floor (`FLOORS`: `nn_condition` $8.0409$, `train_mean` $9.0041$, `zero` $27.7778$), so nothing else re-disqualifies the cell, and the same card's G3 reading — "Numerically the affirmative branch holds; claimably it does not" — would have to be re-read.
   `ifc_poisson` is report-only under ADR r3-0007, so no panel headline and no aggregate moves; what changes is a per-cell narrative on a non-scoring cell.

Explicitly **not** affected under Option C:
r3s2-B2's `ifc_heat` leg (A1 $1.5755$, A3 $1.6862$ now beat affine $1.8469$ but both still lose `nn_condition` $1.3941$, so "no claimable route delta" stands — only its stated reason changes);
r3s3-B3's mandatory floor-arm supporting condition (`satisfied: true`, `first_rung_beating_all_floors_per_seed.ifc_heat = [0,0,0]`, i.e. the no-LF arm already beats every floor — a looser floor cannot unsatisfy it);
r3s3-B2's `ifc_heat` disclosure (A1_lf_all $0.004862$ nRMSE against floor $0.070918$, quoted at $11.9\times$ below; against $0.136671$ it is $28.1\times$ below — margin widens, sign unchanged);
film's `ifc_heat` win ($0.0361$ nRMSE, skill $0.4883$) beats the floor at either definition.

### Option D — demote the affine floor to a disclosure with no adjudication power

Replacement text:

> - **Affine-floor rule (degeneracy audit 2026-08-05; fold-fragility measured by r3s4-B2; scope amended by ADR r3-0007; adjudication withdrawn by ADR r3-0009):** every card reporting an ifc number (scored `ifc_heat` or report-only `ifc_poisson`) reports the fitted `affine_on_hf_train` floor next to it WITH its full leave-one-out fold range (`ifc_poisson` 1.5938 → LOO mean 4.2335, 5/5 folds breach; `ifc_heat` 0.9584 → LOO mean 1.8469, fold sd 10.935 tau_rel, 3/5 folds breach), as a DIAGNOSTIC ONLY. On 5 HF train rows the affine arm is not adjudicable — consistent with its non-adjudicable declaration for reproduction in `state/floor_tolerances_install_note.json` — and no claim is disqualified by it; ifc claims adjudicate against `nn_condition` / `train_mean` / `zero` alone. skill < 1 on ifc_heat is not by itself a strong claim. This suspension lifts when the ifc pair is regenerated with ≥ 40 HF train rows and a non-degenerate condition design (ADR r3-0007 round-4 note), at which point the floor returns as an adjudicating arm.

Effect on shipped round-3 numbers: no number changes, but the disqualification language disappears, so it flips the same `ifc_poisson` annotation as Option C plus every "floor-disqualified" statement that rests on the affine arm.
Concretely: r3s2-B2's `ifc_poisson` leg becomes claimable (its best remaining floor is `nn_condition` $8.0409$, which A1 $3.1298$ and A3 $5.0553$ both beat), and r3s1-B1's ifc affine reading becomes non-adjudicating rather than a loss.
`ifc_heat` is unaffected in verdict terms: `nn_condition` $1.3941$ remains and still disqualifies r3s2-B2's arms there.
Cost: this is the widest retroactive edit of the four, and it discards a genuinely informative diagnostic on the one scored ifc cell precisely because it is noisy — the round's own evidence says the floor is fragile, not that it is uninformative.

### Option summary

| Option | What the floor becomes | Numbers recomputed | Published claims that change sign |
|---|---|---|---|
| A — keep verbatim | single fit + prose "disclosed range" | none | none |
| **B — keep, complete the numbers (recommended)** | single fit **and** LOO mean, both pinned | none | none |
| C — fold-averaged | LOO mean (single fit as provenance) | none | 2 per-cell readings (r3s1-B1 `ifc_heat`, r3s2-B2 `ifc_poisson`) |
| D — diagnostic only | disclosed, adjudicates nothing | none | the same 2, plus every affine-based disqualification |

## Recommendation

**Option B.**

Three reasons, in order of weight.

1. **It fixes the only defect actually measured.**
   The audit's finding is that the *quoted value* was a single draw presented without its spread — not that the floor is the wrong yardstick.
   Option B pins both values and both breach counts into the rule, which is precisely what r3s4-B2's cross-stream finding asked for ("its two quoted numbers … are SINGLE-FOLD values"), and it closes the `ifc_poisson` LOO gap in the current text.
2. **It costs nothing retroactively.**
   No number moves, no claim changes sign, no report is re-issued, and no card annotation is re-read — the decision is separable from everything already shipped, which is the property you want in a rule change taken after a round has closed.
3. **It matches the recommendation already on file, without inheriting its blind spot.**
   ADR r3-0007 line 61 recommends "keep the rule, disclose the fold range … the floor-definition change (fold-averaged) is not needed once poisson — the worse offender — is report-only".
   That reasoning holds, and Option B is that recommendation plus the numeric completion.
   Option C is the alternative that reasoning rejects, and its own arithmetic confirms the rejection: the cell it would most change (`ifc_poisson`) is exactly the report-only cell whose claims cannot count.

Against Option C specifically: adopting a fold-averaged floor makes the yardstick *looser* on both cells, which is the wrong direction for a benchmark whose stated concern is that trivial baselines are hard to beat, and it buys that looseness at the price of re-reading two shipped annotations.
Against Option D: the floor's fragility is a reason to disclose it fully, not a reason to stop letting it disqualify — and on `ifc_heat`, the cell that actually scores, the film baseline clears the floor at its fold-worst, so the rule is not blocking any real result.
Against Option A: it leaves a rule that mandates a fold range while itself quoting one for only one of the two cells it governs.

## The retro-active question, stated explicitly

**If the rule changes, is the shipped round-3 report re-issued, footnoted, or left alone?**

Recommendation, by option:

- **Under A or B: left alone, with no footnote.**
  Nothing in `docs/round3_report.md` becomes false.
  Report §2's disclosure paragraph already prints both single-fit values, both LOO means, both breach counts and the fold sd, so under Option B the report is already compliant with the amended rule as written.
- **Under C or D: footnoted, not re-issued.**
  Add a dated footnote to report §2's disclosure paragraph and to §12 item 1 recording the ratification and the new definition, and append a dated `_adr0009_reread` note (not an edit) to the two affected card fields named above.
  Do **not** regenerate the report, the figures, or the mentor update.

The reason to footnote rather than re-issue is a threshold that should be stated once and reused: **re-issue when a rule change moves a panel aggregate or a card verdict; footnote when it moves only a per-cell annotation.**
No option here moves a panel aggregate (the affine arm is not in the best-floor anchor) and none moves a card verdict (the two affected readings are mandatory-disclosure lines, and the cards' falsification clauses do not gate on them).
The `ifc_poisson` annotation additionally sits on a report-only cell, which cannot carry a claim under ADR r3-0007 regardless of how its floor is defined.

If the operator prefers a stricter posture, the next step up is a dated addendum section appended to `docs/round3_report.md` rather than an in-place edit, which preserves the shipped artifact byte-for-byte while carrying the correction.
A full re-issue is not recommended under any option in this ADR.

## What this does NOT decide

- It does **not** reopen **ADR r3-0007** (RATIFIED 2026-08-10, option C).
  `ifc_poisson` stays report-only and `ifc_heat` stays scored under every option here.
  No option's arithmetic bears on that call, and the mean-removed check that retained `ifc_heat` (`MEANREM`) is independent of the floor definition.
- It does **not** decide **panel composition or the one-cell-headline rule** (report §12 item 2).
  That is **ADR r3-0008**, in flight separately; its Options A–E all leave the floor definition to whatever is in force, and this ADR's options all leave the panel to whatever ADR r3-0008 decides.
  The two are independent in both directions.
- It does **not** decide the **`nn_condition` floor-definition question** (report §12 item 9: bagged-1NN expectation floor vs carrying the fit-set band).
  That question is about a different arm on all five scored cells; this ADR touches only `affine_on_hf_train` on the two ifc cells.
- It does **not** change **floor-reproduction metrology.**
  The pinned per-arm bands in `state/floor_tolerances_install_note.json` and the G5 blanket rule (operator-adopted 2026-08-10) stand unchanged under every option; the last sentence of the rule is carried verbatim into every replacement text.
- It does **not** re-score anything, authorise GPU spend, or touch `data/`, `baselines/`, `eval/`, `references/`, `scripts/` or `factory.md`.
- It does **not** amend `program.md`. This ADR *proposes* rule text; the amendment happens on ratification.
- It does **not** decide the **reporting-convention reconciliation** (report §12 item 4, the $\sim 1.27\times$ aggregate-nRMSE vs per-sample-mean rel-L2 ifc bias). All floor values quoted here are per-sample-mean rel-L2, the convention the floor records use.

## Execution sketch if ratified (no GPU; text and annotations only)

1. Replace `program.md` §2 line 38 with the ratified option's text, in one commit that changes nothing else.
2. Under C or D only: append the dated `_adr0009_reread` annotation to `experiment_cards/r3s1_factorised/batch_1/B1.json` (`mandatory_floor_arm_readings.vs_ref_affine_on_hf_train`) and `experiment_cards/r3s2_field_reach/batch_2/B2.json` (`G1_route.per_dataset_leg.ifc_poisson.claimable_reason` and the G3 conjunct-2 reading), without editing the original strings.
3. Under C or D only: add the dated footnote to `docs/round3_report.md` §2 and §12 item 1.
4. Update this ADR's status line and `state/gates.md`; record the ruling in `state/orchestrator_flow.md` and the report's §10 operator-decision ledger row for the ratification date.
5. Carry the round-4 note forward under every option: regenerate the ifc pair with $\geq 40$ HF train rows and a non-degenerate condition design, then readmit — the defect is the instance, not the physics (ADR r3-0007).

## Verification status of every number in this ADR

All quantities above were read from their primary artifacts for this document:
`0.9584` / `1.8469` / `10.935` $\tau_{rel}$ / `20.534` p95 / 3-of-5 folds and `1.5938` / `4.2335` / 5-of-5 folds — `B2s4` turn 2A;
`0.07091834` nRMSE and `0.03768816` oracle-affine residual (per-sample-mean) — `MEANREM`;
`0.074` / `0.036` paper bars, `nn_condition` `1.3941` / `8.0409`, `train_mean` `1.7666` / `9.0041`, `zero` `13.5135` / `27.7778`, `n_train_hf = 5` — `FLOORS`;
film `ifc_heat` `0.0361336` nRMSE and skill `0.48829` — `FILM`;
per-arm affine bands `3.377e-07` / `5.654e-07` and the non-adjudicable declaration — `INSTALL`;
the arm values `0.9964`, `3.1298`, `5.0553`, `1.5755`, `1.6862`, `0.004862` — the cited card fields;
`5.4e-16` — `B2s4` (mechanism finding on `ifc_poisson`'s condition-independent discretisation error), matching ADR r3-0007 line 15.
The skill/nRMSE consistency check $0.070918 / 0.074 = 0.95835$ was recomputed here.

**Unverified:** the delivered 2026-08-10 explainer's own wording — no standalone artifact exists (see "Provenance" above).
The options in this ADR are reconstructed from ADR r3-0007 lines 58–61, `PROFESSOR_UPDATE_2026-08-10.md` §7.1, and the flow/scope records; they are not transcribed from the explainer.
