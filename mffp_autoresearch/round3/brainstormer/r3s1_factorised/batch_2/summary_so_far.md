# Summary so far — stream `r3s1_factorised`, batch 2

(Persisted verbatim by the orchestrator from the brainstormer's inline return, 2026-08-10; the harness blocked that subagent's report-file writes.)

All paths relative to `mffp_autoresearch/` unless absolute.

## 1. Websearch findings + prior-art verdict

Source: `round3/websearches/r3s1_factorised/batch_2/report.md` (5 iterations, cap hit; 15 WebSearch, 9 fetches via `urllib.request`).

- **D1** — replace the `SELECT_MAX = 32` clip with an adaptive **predictability-criterion** basis selection, feeding the OOF-corrected stage 2 — **`preempted-but-MF-composition-open (cite)`**.
  Open residue verbatim: *"A **per-direction inclusion criterion keyed on out-of-fold predictability from the condition vector** — not energy, not reconstruction error, not a certified residual bound — with the retained set feeding an OOF-corrected cascade, in the **no-LF-at-test** regime at N_hf 5–400 on a copy-LF-skill panel. Five refutation queries returned no per-direction predictability screen. **Raising the numeric cap is a bug-fix, not the claim.**"*
  Citations: arXiv:2605.27756, arXiv:2511.18260, par.nsf.gov/biblio/10684905, arXiv:1907.12239, arXiv:2606.29440.
- **D2** — training-free pre-unlock discriminator `n_SET` / `E_rem` × reachability — **`preempted-but-MF-composition-open (cite)`**, flagged a **repeat bet**: *"batch 1's `cond_dim` discriminator was falsified by its own controlled pair, and the replacement statistic was *fitted on the same 5 cells* it would be pre-registered against."* Remedy given: *"pre-register it on a cell or manipulation the mechanism stage did **not** see (e.g. the same cell under a changed `SELECT_MAX`, which D1 gives you for free)."*
- **D3** — certify a scored cell condition-incomplete on ch's 27/73 split — open but **out of scope**: card part 7 forbids it; routed to `r3s3_lf_value`.
- **D4** — feed stage 2 `[predicted SET coefficients, condition]` — **`preempted (cite)`** (arXiv:1211.6581): *"Augmenting the original inputs with OOF-predicted targets **is** SST. Ship as the named minimal repair of batch 1's information loss; never as a contribution."*
- **D5** — gated stagewise residual correction with a rejectable gate — **`preempted (cite)`** (arXiv:2606.17460, Operator Boosting, validation-selected shrinkage whose grid includes zero): *"A card proposing 'a gate that can decline the correction' restates this paper."* Batch 1's stage-2 gate already has that property; cite, never claim.

Threshold discipline (report §For-the-brainstormer 7): certified `_panel_geomean` `seed_mce` = **0.5083**; clauses must be written against `seed_mce` / per-dataset `tau_rel` and **must not enumerate `pfc`**.

## 2. §12 conventions verbatim

Round-3 `program.md` §5: *"Round-2 §12 methodological rules apply verbatim"*. Reproduced byte-for-byte from `round2/program.md` §12 preamble, the ADR r2-0004 additions, and §12.1:

> Common to all streams: quote the launch anchor (best-floor geomean 23.06) and
> the per-dataset floor table verbatim when designing; thresholds must clear
> the noise floor for the dataset(s) — while `state/noise_floor.json` is
> provisional, judge falsification clauses directly (§4.3); cite the
> websearcher's prior-art verdict; every proposal carries a complete `recipe`
> block; floor arms mandatory on model cards (§2.2).

> - **Registration of model-side lifts.** Any family or instrument code that
>   resamples a field between grids (LF→HF lift, working-grid cap, prediction
>   resample) MUST use the ADR r2-0001 per-dataset conventions — vendor the
>   interpolators from `eval/panel_data.py` (the r2s2-B1/r2s3-B2 precedent) or
>   use `factory_mffp/models/_common/lf_registration.py`. A bare
>   `F.interpolate`/`zoom` on a panel dataset is the (r−1)/2 registration
>   defect and is a reviewer FAIL.
> - **Target-scaler pre-flight.** Any model card that trains on
>   `ext__helmholtz_2d` or `sharp__phase_field_crystal_2d` runs
>   `tools/target_scale_spread_audit.py` on those datasets pre-flight; an
>   `OUTLIER_DOMINATED` or `NEAR_ZERO_TARGETS` verdict requires per-sample
>   target normalisation (or a card-recorded justification for keeping a
>   global scaler). Round 1's `lf_resid_fno` helmholtz 4.14 / pfc 8206×-noise
>   failures were exactly these two verdicts left unhandled.

> ### 12.1 `r2s1_direct` (gap)
>
> - **Bar**: the per-dataset floor table (§2.3). Beating NN-in-condition with
>   400 train samples is necessary but nowhere near sufficient; the interesting
>   question is how close a from-scratch condition→HF surrogate gets to
>   skill 1.0 on each dataset.
> - Design priors (spec §6): FiLM-conditioned FNO **decoders** (condition →
>   spectral latent → field), DeepONet-style branch–trunk (branch on condition,
>   trunk on coordinates), spectral/implicit decoders (SIREN/modulated INR
>   class). Condition vectors are 2–19 dims; ifc_poisson's is 5-dim.
> - **ADR r2-0003 (corrects a spec §4 grounding fact)**: on pfc, fisher_kpp
>   and allen_cahn the condition vector is NOT complete — per-sample random
>   ICs live only in the fields, so condition→HF is a stochastic map and
>   deterministic models are bounded by the conditional-mean floor
>   (train_mean > NN on those floors is the symptom). Skill→1 is unreachable
>   there; design and falsify against the conditional-mean floor, and treat
>   bare FiLM-decoders as declared baselines (prior-art verdict: preempted).
> - **Helmholtz lesson** (r1 report §5): the zero field is the floor to beat
>   there — any helmholtz claim must show the zero-floor column.
> - **pfc caveat** (§2.3): denominator 0.007381 under variant C; no
>   fidelity gap under band-limited. State it on every pfc claim.
> - N_hf on ifc_poisson is 5 — every claim there is anecdote-grade; prefer
>   variance-reducing designs (r1 s1 lesson: ensembling, physics residuals are
>   out per ADR 0009 — physics-agnostic at test).
> - Overfitting is THE central threat at these sample counts; r2s4's
>   overfitting-anatomy diagnostics feed this stream. Train/val discipline in
>   the recipe is mandatory (no test-split peeking; the round-1 D3 val_idx
>   double-consumption caveat is the cautionary tale).

Round-3 overrides: launch best-floor anchor **34.4198** (5-dataset ADR r3-0004 panel, `program.md` §2); the **stream** anchor is now `state/anchors/r3s1_factorised.json` = **24.9573** [24.8726, 25.0662]; ADR r2-0003's incompleteness caveat is retired (*"The IC coefficients ARE in the condition vector now"*, §1); `pfc` is **report-only** and void for claim purposes (`adr_r3_0004_addendum`); §2's **affine-floor rule** makes `affine_on_hf_train` a mandatory reported arm on every ifc cell.

## 3. Within-stream prior cards

`experiment_cards/r3s1_factorised/batch_1/B1.json` — `complete`, `reopen_candidate: false`, `card_type: model`, `epochs 0`, build commit `6770381`, family `models_r3/r3s1_twostage_crosscoef`, worktree `round3/worktrees/r3s1_factorised/B1`.

Part 5 (certified, 3 seeds): panel geomean **24.9573** [24.8726, 25.0662], spread 0.1937; per-cell mean skill ac **279.1165**, fk **374.8381**, ch **11.2577**, ifc_poisson **8.2507**, ifc_heat **0.9964**. Verdict `confirmed` on L1/L2/L4; **L3 VOID** (it enumerated report-only `pfc`), its descriptive margins *adverse* to the cond_dim mechanism. Paired panel delta vs the matched one-stage control **+0.5546** [0.5246, 0.5747], sign-identical at 3 seeds = **1.09×** `seed_mce`. Anomalies on record: stage 2 is a **bitwise empty-gate no-op on 4 of 5 cells at every seed** (gate 9/10/9 on ch only); `test_hf` loses to `ref_dc_only` on fisher_kpp at every seed (374.84 vs 282.76); loses to `ref_affine_on_hf_train` on 4 of 5 cells; both ifc cells exactly seed-invariant (N=5 LOO + empty gate).

Part 7 sets batch 2's priority order verbatim: *"(1) RAISE SELECT_MAX ABOVE 32 [...] the largest identified, unexploited gain in the stream and it costs one env knob. (2) FEED STAGE 2 [predicted SET coefficients, condition] [...] the minimal repair for the M2 information loss [...] (3) PRE-REGISTER THE REPLACEMENT DISCRIMINATOR: n_SET and E_rem x reachability"*, plus hygiene (*"fit every paired reference arm on the scored arm's own fit fold"*) and *"Do NOT spend a batch on cahn_hilliard's hard 27%"*.

Mechanism handoff `worktrees/r3s1_factorised/B1/notes/handoff_experiment_mechanism_analyzer.md`: cond_dim is **not** the discriminator (ac vs ch both cond_dim 19, n_SET 17 vs 3, E_rem 6.3 % vs 32.0 %, residual reachability −0.0038 vs 0.67); fisher_kpp's negative is a **clip**, not a factorisation failure (`clip_rule = "raw set oversized -> top-32 by OOF R^2"`; 0.0713 of encoded energy stranded at OOF R² 0.29–0.31 from the raw condition; head better *inside* its SET (−0.0072), losing entirely *outside* it (+0.1202), 17× asymmetry); under a **matched 320-row** budget the affine gaps become ac −2.5150, fk −104.2939, ch **+1.8367**, leaving fisher_kpp the only resolvable sharp-cell negative.

## 4. Cross-stream cards

`experiment_cards/r3s4_audit/batch_1/B1.json` part 7 (a), addressed to r3s1: on the two paper-bar (ifc) cells `mdd_scored == 0` means *"the reference's uncertainty is unobservable from this round's data, not zero"*, so `tau_abs == tau_rel` there, and any **absolute-bar** ifc claim with |skill − 1| in (0.164, 0.356) on ifc_heat or (0.691, 1.483) on ifc_poisson is licensed by the certified constants but not by the counterfactual. *Same-reference arm-vs-arm comparisons are unaffected — the bar cancels.* Also: do not read `stale_checkpoint_audit.py::train_seconds_collapsed` as staleness evidence. The r3s4 batch-2 contract owns the reference-arm row-budget seam B1's mechanism stage surfaced. No other round-3 card's part 7 references this stream.

## 5. Reopen candidates

**None.** All four round-3 batch-1 cards carry `reopen_candidate: false` (verified by reading each JSON); `r3s1_factorised-B1` is `complete` with no skipped slot. Resolution recorded in `iteration_1.md` §Status.

## 6. Prior-round record — tested directions relevant to this stream

- **Widening the head's basis by relaxing the SET gate** — `round2/experiment_cards/r2s1_direct/batch_3/B3.json` T3-F20: *"A DEPLOYABLE sweep of the head's own SET gate gives panel geomeans 18.7500 (shipped tau = 0.1), 18.7738 (0.05), 18.7884 (0.02), 18.8199 (0.01), 18.8212 (0.005), 18.8260 (0.0), 18.8310 (tau = -inf, all directions) - monotonically worse"*, and M11 *"tau = 0.1 is an essentially optimal deployable gate on this panel"*. → **REFUTED as a `tau` relaxation; UNTESTED as a cap lift on the repaired panel.** F20 swept **tau** only; `SELECT_MAX` was never varied, and on the round-2 panel fisher_kpp had `cond_dim` 2 with 0.9213 of its centered test energy **off** the 51-direction bank (T3-F21), so the cap could not fire. Round-3 B1 is the first artifact where `clip_rule` records the cap firing. The stranded directions sit at OOF R² **0.29–0.31**, i.e. ~3× *above* the tau F20 held fixed: lifting the cap admits the **most**-predictable rejected directions, whereas F20 admitted the **least**-predictable ones. The repair that changed the data is option-A regeneration (`program.md` §1; fisher_kpp cond_dim 2 → 50).
- **Two-stage cross-coefficient head with an OOF-corrected gate** — **CONFIRMED** on the repaired panel (round-3 B1), one cell.
- **`cond_dim` as the discriminator (M15)** — **REFUTED** by B1's own controlled pair (ac vs ch at cond_dim 19, margins 0.0148 vs 0.6945; fisher_kpp largest cond_dim, smallest margin).
- **True-input (non-propagation-aware) stage-2 gate (F25)** — **CONFIRMED directionally, magnitude unresolved** (+0.366 = 1.01× ch `tau_rel`); recorded as a rediscovery of arXiv:1211.6581.
- **Round-2 §5 pre-falsified levers** (WNO backbone swap, LF low-mode freezing, diffusion prior for point accuracy) — none touched by this stream.
- **Inherited methodological rules, live here**: never price a tolerance for a fold-level statistic against the panel's between-seed mce (B3 M14 postmortem — the clause that was unpassable by construction); a low per-direction OOF R² licenses only *"unidentifiable BY THIS MAP FAMILY, at this condition dimension and this row count"* (B3 M12 standing correction).

## 7. What is UNKNOWN

1. **How much of fisher_kpp's ~104-unit matched-budget affine gap is recoverable by lifting an arbitrary integer?** The mechanism stage localised it but never ran the head with the cap off. Panel arithmetic on the certified cells: a fisher_kpp gain of **36.65** skill units is exactly one panel `seed_mce`, while 10.31 (its own `tau_rel`) is only 0.27× the panel floor. Cell and panel can therefore disagree; both must be pre-registered separately.
2. **Is a *criterion* better than a *cap lift*, or is the batch a hyperparameter fix?** Nobody has measured a per-direction OOF-R² inclusion rule calibrated against its own permutation null (as opposed to the shipped fixed `tau = 0.1`). F20 says fixed-tau relaxation is monotonically harmful; it says nothing about a threshold that adapts per direction and per dataset.
3. **Does the ch win survive a changed stage-1 set?** ch's `n_SET = 3` was never cap-limited, so the cap lift alone should leave it bitwise unchanged — but a calibrated criterion could move the stage-2 gate that carries 100 % of the panel effect. This is the card's main downside risk.
4. **Is `n_SET`/`E_rem`×reachability anything more than a curve fitted to 5 cells?** Its three anchor values (ac ≈ 0.000, ch ≈ 0.214, fk ≈ 0.000 measured from the stage-2 input) come from the same artifacts that produced it. The only honest test is out-of-sample *configurations*.
5. **Is stage 2 a real architectural principle or a lucky 3-d reduction?** B1's own `open_question`: swap stage 2's input for PCA-3 of the condition, a random 3-d projection, the true SET coefficients, or `[predicted SET, condition]`. Never run.
6. **What does the D4/SST concat cost or buy?** Stage 2's input currently discards the condition entirely; the repair is textbook, untested here, and could plausibly *hurt* (3-d → 22-d input at 320 rows for kernel/kNN maps).
7. **Do the ifc cells move at all?** With N_hf = 5 and LOO, a permutation-null calibration is degenerate, and F22 already showed the OOF R² statistic fails to transfer on ifc_poisson (0.7934 → 0.4301). Whether the family falls back to the shipped rule there must be closed by assertion, not hope.
8. **What is the real wall clock of a permutation-calibrated selection?** B1 ran 0.92 min/seed. A B-draw null multiplies the selection pass by B — the only place in an `epochs: 0` card where preemption becomes a live risk.
