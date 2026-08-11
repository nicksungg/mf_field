# Iteration 1 — `r3s2_field_reach`, Batch 3 (single slot)

## Design context considered

- `summary_so_far.md` §7 (unknowns 1–7) and the batch-3 prior-art verdict (D1
  `preempted-but-MF-composition-open (cite)`, D2 `preempted (cite)`, D3
  `preempted-but-MF-composition-open (cite)`; nothing `novel`, record 0-for-10).
- **The immutables block** (§4.5 of the brainstormer spec, authority `../round2/program.md` §5 as
  inherited by round-3 `program.md` §5) held in view verbatim throughout; the binding one for this
  design is **#9 stripped test view** — *"test LF field files physically absent; `score_panel.py`
  points there and refuses views that leak LF"* (enforced at `../round2/eval/score_panel.py:99`).
- Stream anchor `state/anchors/r3s2_field_reach.json` = **10.0853** 3-seed panel geomean (5-ds,
  A1_stack_ic_reg), superseding 12.9556; declared a MECHANICS anchor, and its own card is falsified
  on its pre-registration.
- Launch best-floor anchor **38.8368** (6-ds, ADR r3-0005); panel `seed_mce` **0.5083**.
- Certified per-cell `min_claimable_effect` (`state/anchors_repaired/noise_floor.json`):
  ac 18.6198 · fk 10.3128 · ch 0.3612 · ifc_poisson 0.6910 · ifc_heat 0.1640.
  **pfc: ABSENT** — the file was certified 2026-08-08 over the ADR r3-0004 five-cell panel, and
  ADR r3-0005 restored pfc on 2026-08-10.
- Film denominator constants `c_ds` (`state/anchors/film_denominator.json`): ac 0.004087 ·
  fk 0.004411 · ch 0.060170 · pfc 0.012971 · ifc_poisson 0.814353 · ifc_heat 2.047957.
- Pre-falsified levers (r1 §5, carried by round-2 §5): WNO backbone swap, LF low-mode freezing,
  diffusion prior for point accuracy. None is touched.
- Batch-3 scope: one card, the emulator-ceiling card; film units; `ckpt_binding.py` save hook;
  clause hygiene; energy-weighted / held-out-loss statistics; G5 bands; REGISTRATION HOLD until
  ADR r3-0007 decides the ifc cells.

Derived constants used below (computed from the two certified files; per-cell delta/tau ratios are
unit-invariant per B2 F12, so each bar is stated in both film-skill and fractional form):

| cell | tau_rel (copy-LF skill) | c_ds | **tau_film** | certified skill level | **tau_phi = tau_rel / level** |
|---|---|---|---|---|---|
| sharp__allen_cahn_2d | 18.6198 | 0.004087 | **0.076103** | 235.0654 | **0.07921** |
| sharp__fisher_kpp_2d | 10.3128 | 0.004411 | **0.045486** | 201.1240 | **0.05128** |
| sharp__cahn_hilliard | 0.3612 | 0.060170 | **0.021736** | 13.1781 | **0.02741** |
| ifc_poisson | 0.6910 | 0.814353 | **0.562718** | 5.1771 | **0.13347** |
| ifc_heat | 0.1640 | 2.047957 | **0.335905** | 0.9099 | **0.18026** |
| sharp__phase_field_crystal_2d | *uncertified* | 0.012971 | — | — | — |

## Proposal reasoning

### The one thing the slot must do

B2 part 7 preference #1 and the operator's batch-3 scope fix the slot: the **emulator-ceiling
card**. The websearcher then fixes its framing twice:

1. *"If the card's headline is 'we decompose stack error into estimator + hallucination terms',
   that is a rebadge. Claim instead the **regime**: the oracle rung is **not a deployable
   configuration** here (LF is train-only), so the ladder is a **ceiling** … measured at N_hf = 5
   against a certified floor."*
2. *"Register a rung the literature does not have: the `no-LF` rung … the direct condition→HF arm at
   matched budget — or the ceiling ratio has no denominator to be read against. This is also how D3
   becomes decidable without spending a route-contrast card."*

### The design constraint that decides the whole card

The oracle rung needs a **real LF field at evaluation time**. Immutable #9 makes that structurally
impossible on the test split — the files are not there and `score_panel.py` refuses the view. So
the ceiling can only be measured on **held-out TRAIN rows**, where train-side LF use is explicitly
free. This is not a workaround: it is the project's own enforced precedent (round-2 report §7 —
*"stale killed-agent turn-3 partials for r2s2-B3 had read unstripped test LF; they were rejected and
re-derived on the held-out train fold with `_no_test_lf_read=true`"*), and it is exactly what B2's
S2 sidecar did. What "a proper scored arm" therefore has to mean here is:

- all five rungs measured on the **same held-out train rows (HOT)** with the one nRMSE definition
  (`../round2/eval/nrmse.py`), fold-enumerated, floor-priced;
- the two **deployable** rungs additionally scored on the stripped test split;
- an explicit **split-transfer licence gate** (C3) that measures whether the HOT split ranks and
  scales the deployable rungs the same way the test split does. Without that gate the ceiling is a
  statement about held-out train rows and nothing else; with it, the ceiling transfers. Nothing in
  the retrieved literature runs this gate, because in every fetched instance the oracle rung is
  itself deployable and no split substitution is needed.

### Alternatives weighed and rejected

- **Score the oracle rung on the test split.** Rejected: immutable #9 violation, reviewer FAIL, and
  the round has already rejected exactly this once.
- **Another corrector-repair card** (B2's E1 lineage). Rejected by B2 part 7 (*"twice-falsified …
  there is no third measurement worth 3 GPU-seeds there"*) and by the operator scope
  (*"NOT another corrector-repair or route-contrast card"*). The one concrete correction
  (ridge 1e-9, F10) is carried as an instrument footnote, per the same instruction.
- **Another direct-vs-stack route contrast.** Rejected: F11 shows 74.2% of the panel win lives in
  the two floor-disqualified ifc cells, so the contrast cannot produce a claimable per-cell result
  on this panel. The direct arm survives here only as the ladder's **denominator**, which is a
  different role and is what makes D3 decidable without a route card.
- **§12.2's `fine-tuned` / `end-to-end` arms.** Rejected for this slot: that ladder separates
  *distribution shift* from *emulator error*, which is a repair of the deployed rung; the ceiling
  question is answered by the oracle rung, and adding two more trained arms would double GPU cost
  while diluting the pre-registration. Recorded as the natural follow-on if C1 fires everywhere.
- **A panel-level registered claim.** Rejected: F12 (subset geomeans are unit-dependent and must be
  read against a subset-calibrated bar) plus ADR r3-0007 (panel composition undecided). Every
  registered clause is **per cell**, which makes the card exactly robust to A / B / C.
- **Spending seeds instead of enumerating folds at n_fit ≤ 5.** Rejected by clause hygiene and by
  B2 cross-stream note 5 (seeds 0 and 1 draw the identical fit set at Ntr = 5).
- **Registering a clause on pfc.** Deferred, not dropped: pfc has no certified mce, so its clause
  unit registers only if one is certified before card registration; otherwise pfc ships
  report-only. pfc is still RUN — it is the only never-exercised sharp cell in this stream and its
  rung-1 + spectral-lift path is a real code-path test.

### Why the design is zero-redesign under every ADR r3-0007 outcome

The experiment runs all six cells regardless. What the ADR changes is only which per-cell clause
units are REGISTERED, via a registration predicate evaluated at card-registration time:

> A per-cell clause unit is REGISTERED iff (i) the cell is scored under the decided ADR r3-0007
> composition, AND (ii) the cell has a certified `min_claimable_effect` in
> `state/anchors_repaired/noise_floor.json` at registration time, AND (iii) neither deployable rung
> is floor-disqualified on that cell (C4). Otherwise the unit ships as REPORT-ONLY evidence.

- **Option A (keep both ifc):** registered = ac, fk, ch (+ pfc iff mce certified). Both ifc units
  fail (iii) on B2's evidence (A1 loses `affine_on_hf_train` 3.1298 vs 1.5938 and 1.5755 vs 0.9584)
  → report-only.
- **Option B (demote both):** the ifc units fail (i) → report-only. **No other change.**
- **Option C (demote poisson only):** ifc_poisson fails (i), ifc_heat fails (iii) → both
  report-only. **No other change.**

In all three, B2's sharpest ceiling measurement (F9, on ifc_poisson) is carried as REPORT-ONLY
evidence and never as a registered clause — as the operator's constraint requires.

### The instrument repair (D2), demoted to a footnote

Per the verdict (*"D2 is a repair, not a hypothesis"*), λ and the band-limit are chosen jointly by
an **exactly out-of-sample** criterion on the **emulator's held-out pseudo-LF output** — the
deployment input distribution — with the real-LF-selected variant carried as the paired comparand
(B2's shipped rule). Grid `{0, 1e-10, 3.162e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-4, 1e-2, 1e-1}` × band-limit
`{on, off}`:

- **FLOOR justified** (clause hygiene): F2 computed the λ needed to bring ifc_poisson band-3 mean
  |T| to 1 as 5.264e-10–5.707e-10; a grid whose smallest non-zero point is 1e-6 cannot express it,
  so the floor must sit at least a decade below the requirement → 1e-10.
- **CEILING justified**: F1 measured `loo_sse(0.1)/loo_sse(0)` = 122/122/160 on ifc_poisson and
  1.35–1.94 elsewhere, so 1e-1 is already far past useful.
- Band-limit is a *selected* setting, not a fixed one, because F10 measured it costing 28% of
  held-out explained variance on ifc_heat (a cell that never trips) and F8 showed it KEEPS the
  artefact on ac/fk/ch (signed T = -1.0000, a canceller, not an amplifier).
- Pre-registered numeric prediction, from F10: on ifc_poisson, ridge 1e-9 + k_cut gives held-out
  explained variance 0.9992 with 0/10 leg-(iii) trips.

### Clause hygiene, discharged item by item

- *"no falsification leg whose threshold sits inside the fold-to-fold spread of its own statistic"*
  → **every** clause bar is evaluated as `min over (seed × fold) legs > bar` (or `max < bar` for the
  DROP direction), so the entire measured spread lies on one side of the bar by construction; the
  full leg population is reported.
- *"any pre-registered repair grid must justify its FLOOR"* → done above, from F2's computed
  requirement.
- *"no 0-epoch selector admitting candidates unscorable out-of-sample at that budget"* → every one
  of the 20 corrector candidates is closed-form and scored on held-out rows it never saw.
- *"enumerate the C(Ntr, n_fit) fold population instead of spending seeds"* → ifc: all
  C(5,3) = 10 folds (B2 F10's population), plus the C(5,4) = 5 LOO folds as the floor-matched
  disclosure; sharp: 5 disjoint cross-fit folds inside T for the closed-form stage.
- *"statistics on ENERGY-weighted or held-out-loss quantities, never an unweighted mode mean"* →
  every band column via `tools/transfer_gain_anatomy.py` (energy-weighted + signed aggregate +
  coherence); the unweighted mean |T| appears only as a labelled reproduction of B2's defect.
- *"calibrate every subset bar on the subset it is read against"* → no subset geomean carries a
  clause; `tools/subset_geomean_unit_audit.py` runs pre-flight on every subset sentence.

## Proposal

- **Category**: `mf_composition/emulator_ceiling_ladder_with_no_lf_denominator`
- **Card type**: `model`
- **Motivation** (quotes the prior-art verdict): see report.md §Slot — the ladder's *decomposition*
  is preempted (arXiv:2602.13416, arXiv:2604.12440, Tacotron 2 §3.3.1); the *regime* is open:
  *"In **every** fetched instance the oracle intermediate is a deployable counterfactual … No
  fetched source runs it (a) with an intermediate structurally unavailable at inference, (b) at
  N_hf = 5 with a closed-form corrector whose fold population C(5,3) is enumerable, or (c) priced
  against a certified training-free floor + certified baseline denominator in skill units. That
  triple is the claim."*

- **Concrete config** — new family `models_r3/r3s2_ceiling`, vendored wholesale from this stream's
  own `models_r3/r3s2_route` @ `e606a4f1` with a new `INSPIRATION.md`. One shared FiLM-FNO trunk
  (width 64, 4 blocks, 12 modes) + B1's zero-parameter analytic IC-synthesis channel, budget
  accountant unchanged from B2 (`E_emu + 2·E_dc = 300`, tier 200, split 0.5).

  **Splits.** Per cell, a HOT (held-out train) evaluation set on which real LF is present and test
  LF is never touched:
  - sharp cells (ac, fk, ch, pfc; `n_train_hf` = 400): seeded permutation into **T = 320** fit rows
    / **H = 80** held-out rows. |T| = 320 is chosen so the floor comparison lands exactly on the
    certified G5 matched-fit population (`reanalysis_turn_2_repricing.json::_n_scored = 320`);
  - ifc cells (`n_train_hf` = 5): **all C(5,3) = 10 folds** (T = 3, H = 2), plus the C(5,4) = 5 LOO
    folds as the floor-matched disclosure variant.
  The stripped test split is used for the deployable rungs only.

  **Five rungs** (all on H; R0/R1/R1b additionally on the stripped test split):
  | rung | definition | deployable? |
  |---|---|---|
  | `R0_absent` | condition → HF (FiLM-FNO + IC channel), matched 300-epoch budget — **the no-LF denominator** | yes |
  | `R1_predicted` | condition → pseudo-LF (FiLM-FNO emulator) → convention lift → frozen corrector → HF | yes |
  | `R1b_degraded` | pseudo-LF lifted, corrector removed (B2's A7 analogue) | yes |
  | `R2_oracle` | **real LF of the H rows** → the same frozen corrector → HF | **NO** (immutable #9) |
  | `R2b_copylf` | real LF of the H rows, convention lift only, zero parameters | **NO** |
  plus the mandatory floor arms `nn_condition, train_mean, zero, affine_on_hf_train`.

  **Per-cell statistics**, per (seed × fold) leg: `phi_ceil = 1 − nRMSE(R2)/nRMSE(R0)`,
  `phi_real = 1 − nRMSE(R1)/nRMSE(R0)`, realization fraction `rho = phi_real / phi_ceil`,
  estimator term `E_est = nRMSE(R2)`, hallucination term `E_hall = nRMSE(R1) − nRMSE(R2)`, each also
  in film skill units; energy-weighted band columns; the full leg population always reported.

  **Registered clause units** (registration predicate above):
  - **C1 — hallucination term certified**: `min` over legs of `skill_film(R1) − skill_film(R2)` >
    `tau_film(cell)`.
  - **C2 — ceiling existence / the D3 decision rule**: `DROP` if `max` over legs `phi_ceil` <
    `tau_phi`; `KEEP-CANDIDATE` if `min` over legs `phi_ceil` > `tau_phi`; else `INDETERMINATE`.
  - **C3 — split-transfer licence (gate, not a claim)**: on every seed the two deployable rungs rank
    identically on H and on test, and
    `|log(nRMSE_H/nRMSE_test)(R1) − log(nRMSE_H/nRMSE_test)(R0)| ≤ 0.25`
    (0.25 ≈ 3× the largest registered-cell `tau_phi`, 0.07921). A cell failing C3 ships its ceiling
    REPORT-ONLY.
  - **C4 — floor arms (mandatory)**: R0 and R1 vs `nn_condition / train_mean / zero`
    (+ `affine_on_hf_train` on ifc) at matched fit-set size, each nn_condition-priced margin
    carrying the G5 fit-set sd (ac 13.78 · fk 16.41 · ch 0.65 · ifc_p 0.36 · ifc_h 0.097 skill).
    Both rungs losing the best floor ⇒ no registered unit on that cell.

  **Pre-flight (all zero-GPU, before submission)**: `tools/transfer_gain_anatomy.py --ridge-ladder
  --enumerate-folds` (the corrector grid and the fold population), `tools/amplitude_calibration_audit.py`
  (constant-norm oracle cap disclosed beside every `phi_ceil` — fk 23.37× tau_rel, ch 1.92×,
  ifc_heat 1.23×), `tools/fitset_matched_n_audit.py` (ifc affine fold band),
  `tools/subset_geomean_unit_audit.py` (every subset sentence), target-scaler pre-flight on pfc,
  and a rung/lift tripwire asserting the family's LF rung and lift equal
  `panel_data.py`'s scored-cell choice per dataset (pfc = rung 1 + spectral zero-pad, ADR r3-0005).

- **Recipe**: see report.md (complete JSON, transcribed verbatim by the starter).

- **Expected outcome**:
  - **P1 (ceiling exists, large)** — `phi_ceil ≥ 0.9` on ac / fk / ch / pfc, i.e. ≥ 11× the largest
    sharp `tau_phi` (0.07921) and ≥ 33× ch's (0.02741). Basis: round-2 report §5 item 6 measured
    raw copy-LF beating fitted condition-only arms by **164.9× / 77.0× / 12.3× / 49.5×**
    (ac/ch/fk/pfc) on held-out train rows; a 12× error ratio is `phi_ceil` = 0.92. On ifc_poisson,
    B2 F9 gives oracle 0.0195–0.0211 against a deployed 0.119–2.147 ⇒ `phi_ceil` ≥ 0.83,
    6.2× `tau_phi` = 0.13347.
  - **P2 (realization ~0)** — `rho ≤ 0.10` on ac and fk. Basis: B2's A7 ≈ A1 within 0.11 skill
    units on all three sharp cells (the corrector adds nothing once LF is hallucinated) and B1's F2
    (trained stage-2 corrector earns < 1.05 skill units against 1.74 / 24.63 bars).
  - **P3 (hallucination-dominated)** — `E_hall / (E_hall + E_est) ≥ 0.9` on ≥ 3 cells. Basis: B2 F9
    (ifc_poisson 6–100× ratio) and round-2 §4 (*"The stack's error is 99.98% stage-1 error on
    cahn_hilliard"*).
  - **C1 margin vs the noise floor**: expected `skill_film(R1) − skill_film(R2)` on ch is
    ≥ 0.20 film units against `tau_film` = 0.021736 (**9×**); on ac ≥ 0.8 against 0.076103
    (**10×**); on fk ≥ 0.4 against 0.045486 (**9×**); on ifc_poisson ≥ 3.4 against 0.562718 (**6×**,
    report-only). Every bar is cleared by an order of magnitude, and every bar is a `min` over the
    30 (3 seeds × 10 folds) / 15 (3 seeds × 5 folds) leg population, so no threshold sits inside its
    own spread.
  - **Mechanics (not claims)**: R1's 5-cell test geomean expected within ~1 panel `seed_mce`
    (0.5083) of the stream anchor 10.0853 once the 320/400 fit-set reduction is disclosed; cratered
    gates 15.128 (5-cell subset) and 58.255 (= 1.5 × launch best-floor 38.8368, 6-cell).

- **Expected falsification** (one sentence): *If on ≥ 2 registered cells the deployed pseudo-LF
  route realizes more than half of its own certified ceiling — `min` over (seed × fold) legs of
  `rho` > 0.5 while `phi_ceil` > `tau_phi` — then the LF intermediate is not emulator-limited on
  this panel, the hallucination term is not what caps the route, and this card's ceiling framing
  together with the D3 drop/keep rule derived from it is falsified.*
  Secondary registered falsifiers: **C1 fails to fire on ≥ 2 registered cells** (the hallucination
  term is not resolvable above the certified floor), or **C3 fails on ≥ 2 registered cells** (the
  held-out-train split does not transfer, which voids the instrument rather than the hypothesis and
  is reported as such).

- **Anchor reference**: `null` (per §4.5: all four round-3 streams are gap/lever/diag; own-stream
  anchor 10.0853 is implicit and used only for the mechanics/cratered comparand).

## Immutables self-check — PASS (11/11)

1. **Data read-only.** No regeneration, no extra HF, `N_hf` untouched: the sharp cells keep their
   400 train rows (320 used for fitting, 80 held out — a *split of existing rows*, not new data),
   the ifc cells keep their 5, and LF is read from the shipped nested ladders only. No LF is
   produced by downsampling HF anywhere; the pseudo-LF is a *model output* and is labelled as such.
2. **Panel + guard set fixed.** `datasets` names the six ADR r3-0005 scored cells verbatim, never
   the literal `panel` (which would resolve to the ROUND-2 panel via `round2/project.yaml`);
   the guard run is the separate `--datasets guard` invocation at tier 200 / seed 0, unchanged.
   ADR r3-0007 changes only which per-cell clause units register, never which cells run.
3. **Eval layer / spec untouched.** The card needs no edit to `round2/eval/`, `project.yaml`,
   `program.md` or any agent prompt: it consumes `nrmse.py` and `panel_data.py` as imports, and the
   HOT ladder is computed inside the family from train-side arrays the loader already returns.
   `ROUND2_EVAL_RESULTS` / `ROUND2_EVAL_CACHE` are exported to `$OUT_DIR` so nothing is written into
   the frozen eval tree (B1's review-FAIL discharge, carried verbatim).
4. **One nRMSE definition.** Every rung, both splits, and every floor arm are scored with
   `round2/eval/nrmse.py` (`nrmse_def_hash` d3d0ade9…); `phi`, `rho`, `E_est` and `E_hall` are
   arithmetic *on* those numbers, not alternative metrics. Training losses (rel-L2 for the emulator)
   are free and are not scored quantities.
5. **Contract CLI fixed.** `smoke_eval.py` keeps the contract signature
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`; every new behaviour is reached
   through `--env` keys listed in the recipe block, exactly as B1/B2 did.
6. **Seeds {0,1,2}, tier epochs fixed.** `seeds: [0,1,2]`, `epochs: 200` (smoke tier); the budget
   accountant holds every trained arm at 300 optimizer epochs total, B2's own accounting. Seeds are
   spent only on the NN stages; the closed-form stages use the enumerated fold population instead
   (clause-hygiene rule 3). No full tier is requested.
7. **Guarded factory surfaces untouched.** All code lives in the card's worktree under
   `models_r3/r3s2_ceiling`; nothing under `factory_mffp/{data,baselines,eval,references,scripts}`,
   `factory.md`, `akash/`, or any generator surface is read for writing or edited.
8. **Checkpoint-resume implementable.** Each trained stage (emulator, direct trunk) saves to
   `<ckpt_dir>/last.pt` every epoch and resumes from it, exactly as `r3s2_route` already does;
   the HOT split is derived deterministically from `(dataset, seed)` so a resumed run reconstructs
   the identical split. Fresh ckpt dirs under
   `mffp_autoresearch_outputs/round3/r3s2_field_reach/B3/ckpt`, never reused from B1/B2, and the
   batch-3 contract hook `models_r3/_common/ckpt_binding.py` writes `data_binding` at every save
   with `roles_read = lf_at_train` for the stack/oracle arms and `cond_only` for the direct arm —
   which additionally makes the "this arm never read `test_lf`" claim machine-checkable.
9. **Falsification threshold exceeds the noise floor on every cited dataset.** C1's bars are the
   certified `min_claimable_effect` converted to film units — ac **0.076103**, fk **0.045486**,
   ch **0.021736**, ifc_poisson **0.562718**, ifc_heat **0.335905** — and the expected effects are
   0.8 / 0.4 / 0.20 / 3.4 film units respectively, i.e. **10× / 9× / 9× / 6×** the floor. C2's bars
   are the same constants in unit-invariant fractional form (`tau_phi` = 0.07921 / 0.05128 /
   0.02741 / 0.13347 / 0.18026) against expected `phi_ceil` ≥ 0.9 / 0.9 / 0.9 / 0.83, i.e.
   **11× / 18× / 33× / 6×**. Every bar is applied as a `min` over the full (seed × fold) leg
   population, so the threshold cannot sit inside the statistic's own spread. **pfc is not cited by
   any registered threshold**: it has no certified mce (`noise_floor.json` covers five cells; ADR
   r3-0005 restored pfc two days after certification), so its unit is report-only unless an mce is
   certified before registration. The panel `seed_mce` 0.5083 is cited only by the mechanics /
   cratered gates, which are procedural and carry no claim.
10. **Not a pre-falsified lever.** Nearest pre-falsified items: (a) round-1 §5's *LF low-mode
    freezing* — this card freezes nothing in the LF spectrum; the band-limit is a *selected*
    corrector setting whose alternative (off) is in the grid, precisely because F8 showed the fixed
    band-limit keeps the artefact. (b) r3s2-B2's own falsified G2(iii) *LSI repair hypothesis* —
    re-proposed **not** as a hypothesis but as an instrument setting chosen out-of-sample, with a
    justified grid floor (1e-10 vs F2's required 5.3e-10) and with its acceptance statistic replaced
    by the energy-weighted one (F7), which is the defect B2's postmortem identified. (c) r3s2-B2's
    *route contrast* — not re-proposed; the direct arm appears only as the ladder's denominator.
    WNO backbone swap and diffusion priors: n/a, untouched.
11. **Mandatory floor arms in the falsification reasoning.** C4 makes
    `nn_condition / train_mean / zero` (+ `affine_on_hf_train` on ifc, per program.md §2) a
    gating conjunct: a cell where both deployable rungs lose the best training-free floor from
    `state/anchors_repaired/floors.json` yields **no registered clause unit**. Pre-registered
    readings: ac best floor `nn_condition` 475.86 (matched-fit 483.46 ± 13.78) vs R1 ≈ 82.7 →
    passes by ~21× tau_rel; fk `train_mean` 390.70 (390.93 ± 2.84) vs ≈ 30.0 → ~36×;
    ch `nn_condition` 23.18 (23.48 ± 0.65) vs ≈ 8.6 → ~40×; ifc_poisson passes `nn_condition` 8.04
    but **loses** `affine_on_hf_train` 1.5938 (fold band to 4.2335) and ifc_heat loses both
    `nn_condition` 1.3941 and `affine` 0.9584 → both ifc units report-only from the outset;
    pfc floors `train_mean` 71.03 / `nn_condition` 96.11 / `zero` 80.92 are reported but carry no
    registered clause (no mce). Every nn_condition-priced margin carries the G5 fit-set sd.

## Status

- Slot **covered** — one proposal, category `mf_composition/emulator_ceiling_ladder_with_no_lf_denominator`,
  card type `model`.
- Skipped: none.
- Reopen candidates resolved: **none exist** for this stream (scan of all round-3 cards returns no
  `reopen_candidate: true`).
- Immutables self-check: **pass** (11/11, including the three round-3 extras). No revision pass
  needed; iteration count 1.
- Registration note carried to the card: clauses may not be registered until ADR r3-0007 is decided
  (`state/batch3_scope_2026-08-10.md` REGISTRATION HOLD); the design requires **zero** redesign
  under options A, B or C.
