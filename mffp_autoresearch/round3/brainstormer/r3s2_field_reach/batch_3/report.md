# Brainstormer Report — Stream `r3s2_field_reach`, Batch 3

**Stream**: `r3s2_field_reach` (gap) · **Batch**: 3 (final batch, single slot, operator-fixed to the
emulator-ceiling card) · **Total iterations**: 1 · **Slot filled**: 1 of 1 · **Reopen candidates
resolved**: 0 of 0 (none exist)

## Slot

- **Category**: `mf_composition/emulator_ceiling_ladder_with_no_lf_denominator`
- **Card type**: `model`

- **Motivation**: The websearcher's D1 verdict says the *decomposition* is textbook and the
  *regime* is what is open — *"In **every** fetched instance the oracle intermediate is a
  deployable counterfactual — coarsened ERA5, GT masks, GT mels, a real coarse solve. Here the LF
  field exists **at train only** and must be hallucinated from the condition vector at test, so the
  ladder measures a **bound on what the route could ever buy**, not an alternative deployment. No
  fetched source runs it (a) with an intermediate structurally unavailable at inference, (b) at
  N_hf = 5 with a closed-form corrector whose fold population C(5,3) is enumerable, or (c) priced
  against a **certified training-free floor** + certified baseline denominator in skill units. That
  triple is the claim."* The card therefore claims the regime, not the decomposition, and adds the
  rung the retrieved ladders have and ours has never had: *"the direct condition→HF arm at matched
  budget — or the ceiling ratio has no denominator to be read against. This is also how D3 becomes
  decidable without spending a route-contrast card."* Internally, this is B2 part 7's preference #1
  verbatim — *"the real-LF oracle vs pseudo-LF ladder on all five cells, already emitted as S2 and
  needing only a proper scored arm"* — with the two mandates that make it a measurement rather than
  a sidecar: a `no-LF` denominator and a certified floor.

- **Concrete config**: new family `models_r3/r3s2_ceiling`, vendored wholesale from this stream's
  own `models_r3/r3s2_route` @ `e606a4f1` with a new `INSPIRATION.md`; shared FiLM-FNO trunk
  (w64 / 4 blocks / 12 modes) + B1's zero-parameter analytic IC-synthesis channel; B2's budget
  accountant (`E_emu + 2·E_dc = 300`, tier 200, split 0.5) unchanged.

  **Splits.** The oracle rung needs a real LF field at evaluation time, which immutable #9 makes
  structurally impossible on the test split (`round2/eval/score_panel.py:99` refuses any view
  exposing test LF). It is therefore measured on **held-out TRAIN rows (HOT)** — the project's own
  enforced precedent (round-2 report §7). Per cell:
  - sharp cells (`ac, fk, ch, pfc`; `n_train_hf` = 400): seeded permutation into **T = 320** fit rows
    / **H = 80** held-out rows — |T| = 320 chosen so the floor comparison lands exactly on the
    certified G5 matched-fit population (`_n_scored = 320`);
  - ifc cells (`n_train_hf` = 5): **all C(5,3) = 10 folds** (T = 3 fit, H = 2 held out), plus the
    C(5,4) = 5 LOO folds as the floor-matched disclosure variant.
  The closed-form corrector stage additionally uses 5 disjoint cross-fit folds inside T on the sharp
  cells. The stripped test split carries the deployable rungs only.

  **Five rungs** (all evaluated on H; the deployable three additionally on the stripped test split):

  | rung | definition | deployable at test? |
  |---|---|---|
  | `R0_absent` | condition → HF, matched 300-epoch budget — **the no-LF denominator** | yes |
  | `R1_predicted` | condition → pseudo-LF emulator → convention lift → frozen corrector → HF | yes |
  | `R1b_degraded` | pseudo-LF lifted, corrector removed (B2's A7 analogue) | yes |
  | `R2_oracle` | **real LF of the H rows** → the same frozen corrector → HF — the ceiling | **NO** (immutable #9) |
  | `R2b_copylf` | real LF of the H rows, convention lift only, zero parameters | **NO** |

  plus mandatory floor arms `nn_condition, train_mean, zero, affine_on_hf_train`.

  **Statistics** per cell per (seed × fold) leg: `phi_ceil = 1 − nRMSE(R2)/nRMSE(R0)`,
  `phi_real = 1 − nRMSE(R1)/nRMSE(R0)`, realization fraction `rho = phi_real / phi_ceil`,
  estimator term `E_est = nRMSE(R2)`, hallucination term `E_hall = nRMSE(R1) − nRMSE(R2)`; all also
  in film skill units; band columns energy-weighted / signed / coherence-checked only
  (`tools/transfer_gain_anatomy.py`), never an unweighted mode mean; the full leg population is
  dumped.

  **Registered clause units** — a per-cell unit REGISTERS iff (i) the cell is scored under the
  ADR r3-0007-decided composition, (ii) it has a certified `min_claimable_effect` in
  `state/anchors_repaired/noise_floor.json` at registration time, and (iii) neither deployable rung
  is floor-disqualified there; otherwise it ships REPORT-ONLY:
  - **C1 (hallucination term certified)** — `min` over legs of `skill_film(R1) − skill_film(R2)` >
    `tau_film(cell)`;
  - **C2 (ceiling existence, the D3 rule)** — `DROP` if `max` over legs `phi_ceil` < `tau_phi`;
    `KEEP-CANDIDATE` if `min` over legs `phi_ceil` > `tau_phi`; else `INDETERMINATE`;
  - **C3 (split-transfer licence, a gate)** — the two deployable rungs rank identically on H and on
    test at every seed, and `|log(nRMSE_H/nRMSE_test)(R1) − log(...)(R0)| ≤ 0.25`
    (≈ 3 × the largest registered `tau_phi`); a cell failing C3 ships its ceiling REPORT-ONLY;
  - **C4 (floor arms, mandatory)** — R0 and R1 against `nn_condition / train_mean / zero`
    (+ `affine_on_hf_train` on ifc) at matched fit-set size, each nn_condition-priced margin
    carrying the G5 fit-set sd.

  **The D2 repair is an instrument footnote, not the idea** (per the verdict): λ and the band-limit
  are selected jointly by an exactly-out-of-sample criterion on the **emulator's held-out pseudo-LF
  output** over `{0, 1e-10, 3.162e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-4, 1e-2, 1e-1} × {bandlimit on, off}`,
  with the real-LF-selected variant as the paired comparand. Grid **floor** justified by B2 F2 (the
  λ actually needed is 5.264e-10–5.707e-10, so the floor must sit a decade below → 1e-10);
  **ceiling** justified by F1 (`loo_sse(0.1)/loo_sse(0)` = 122–160 on ifc_poisson). Pre-registered
  numeric prediction from F10: ridge 1e-9 + k_cut gives held-out explained variance 0.9992 with
  0/10 leg-(iii) trips on ifc_poisson.

  **Zero-GPU pre-flight**: `transfer_gain_anatomy.py --ridge-ladder --enumerate-folds`,
  `amplitude_calibration_audit.py` (constant-norm oracle cap disclosed beside every `phi_ceil` —
  fk 23.37× tau_rel, ch 1.92×, ifc_heat 1.23×), `fitset_matched_n_audit.py` (ifc affine fold band),
  `subset_geomean_unit_audit.py`, target-scaler pre-flight on pfc, and a rung/lift tripwire
  asserting the family's LF rung + lift equal `panel_data.py`'s scored-cell choice per dataset
  (pfc = rung 1 + spectral zero-pad, ADR r3-0005).

- **Recipe**:

```json
{
  "base_family": "r3s2_route",
  "base_commit": "23018cc5e11884b79bb68e80bcc18146a3e8b779",
  "family_dir": "models_r3/r3s2_ceiling",
  "datasets": "sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat",
  "epochs": 200,
  "seeds": [0, 1, 2],
  "env": {
    "R3S2B3_LADDER": "oracle_ceiling_5rung",
    "R3S2B3_RUNGS": "R0_absent,R1_predicted,R1b_degraded,R2_oracle,R2b_copylf",
    "R3S2B3_ORACLE_NONDEPLOYABLE": "1",
    "R3S2B3_TEST_SPLIT_ARMS": "R0_absent,R1_predicted,R1b_degraded",
    "R3S2B3_HOT_SPLIT_SHARP": "seeded_perm_fit320_heldout80",
    "R3S2B3_HOT_SPLIT_IFC": "enumerate_C5_3",
    "R3S2B3_IFC_LOO_DISCLOSURE": "enumerate_C5_4",
    "R3S2B3_SHARP_CLOSEDFORM_FOLDS": "kfold5_within_T",
    "R3S2B3_HOT_SPLIT_KEY": "deterministic_from_dataset_and_seed",
    "R3S2B3_NO_TEST_LF_ASSERT": "1",
    "R3S2B3_STATS": "phi_ceil,phi_real,rho,E_est,E_hall",
    "R3S2B3_REPORT_UNITS": "film_skill,fractional_error_reduction",
    "R3S2B3_BAND_STATS": "energy_weighted_signed_coherence",
    "R3S2B3_MIN_OVER_LEGS_CLAUSES": "1",
    "R3S2B3_LEG_POPULATION_DUMP": "1",
    "R3S2B3_FILM_DENOM_JSON": "mffp_autoresearch/round3/state/anchors/film_denominator.json",
    "R3S2B3_NOISE_FLOOR_JSON": "mffp_autoresearch/round3/state/anchors_repaired/noise_floor.json",
    "R3S2B3_REGISTRATION_PREDICATE": "scored_and_certified_mce_and_not_floor_disqualified",
    "R3S2B3_SPLIT_TRANSFER_GATE": "1",
    "R3S2B3_SPLIT_TRANSFER_TOL_LOGRATIO": "0.25",
    "R3S2B3_CORRECTOR_SELECT_ON": "emulator_heldout_output",
    "R3S2B3_CORRECTOR_SELECT_COMPARAND": "real_lf",
    "S6_LSI_RIDGE": "enumerated_folds_out_of_sample",
    "S6_LSI_RIDGE_GRID": "0,1e-10,3.162e-10,1e-9,1e-8,1e-7,1e-6,1e-4,1e-2,1e-1",
    "S6_LSI_BANDLIMIT": "selected_not_fixed",
    "S6_LSI_BANDLIMIT_GRID": "on,off",
    "S6_LSI_BANDLIMIT_MODE": "zero_above_kcut",
    "S6_LSI_KCUT_SOURCE": "ladder_shape_ratio_adr_r2_0001",
    "S6_LEAKAGE_TRIPWIRE": "1",
    "S6_BAND_EDGES_FRAC": "0,0.125,0.25,0.5,1.0",
    "S6_VARIANT": "local_pixel_gate",
    "S6_SELECTOR": "heldout_scalar",
    "S6_PAD_MODE": "circular_if_periodic",
    "S6_PERIODIC_TEST": "wrap_continuity_ratio_hf_train",
    "S6_PERIODIC_TOL": "1.25",
    "S6_KERNEL": "7",
    "S6_DEPTH": "4",
    "S6_WIDTH": "32",
    "S6_GATE_HOLDOUT_FRAC": "0.2",
    "S6_GATE_INIT": "zero",
    "S6_GATE_LINESEARCH_INCLUDES_ZERO": "1",
    "R3S2_FRONTEND": "ic_synth",
    "R3S2_ARM": "frozen",
    "R3S2_IC_SYNTH": "analytic_modes",
    "R3S2_IC_SYNTH_NORM": "res_min_maxabs",
    "R3S2_IC_SYNTH_SCALE": "1.0",
    "R3S2_IC_NAMES_FROM": "meta_param_names_ic_prefix",
    "R3S2_IC_FALLBACK": "film_only_recorded",
    "R3S2_IC_EQUIV_CHECK": "1",
    "R3S2_IC_SHUFFLE_NULL": "0_established_in_B1",
    "R3S2_EMU_TARGET": "lf_native",
    "R3S2_EMU_RUNG": "scored_cell_lf_from_panel_data",
    "R3S2_EMU_WIDTH": "64",
    "R3S2_EMU_BLOCKS": "4",
    "R3S2_EMU_MODES": "12",
    "R3S2_EMU_LOSS": "rel_l2",
    "R3S2_EMU_SHARED": "1",
    "R3S2_EPOCH_SPLIT": "0.5",
    "R3S2_BUDGET_MATCH": "arm_equal_total",
    "R3S2_UPSAMPLE": "corrected_by_convention",
    "R3S2B3_RUNG_LIFT_TRIPWIRE": "1",
    "R3S2_TARGET_SCALER_PREFLIGHT": "pfc_per_sample_if_outlier_dominated",
    "R3S2_LF_INPUT": "pseudo_and_real_by_rung",
    "R3S2_VAL_DISJOINT": "1",
    "R3S2_REQUIRE_PSEUDO_LF": "1",
    "R3S2_PAIRING_GATE": "1",
    "R3S2_FLOOR_ARMS": "nn_condition,train_mean,zero,affine_on_hf_train",
    "R3S2B3_FLOOR_MATCHED_N": "sharp:320,ifc:C5_4_loo",
    "R3S2B3_G5_BAND_DISCLOSURE": "1",
    "R3S2B3_CKPT_BINDING": "1",
    "R3S2B3_ROLES_READ": "R0_absent=cond_only,R1_predicted=lf_at_train,R1b_degraded=lf_at_train,R2_oracle=lf_at_train,R2b_copylf=lf_at_train",
    "R3S2B3_CKPT_DATA_HASH_BIND": "1",
    "R3S2B3_ANCHOR_REPLICATION_CHECK": "10.0853",
    "R3S2_DIAG_OUT": "mffp_autoresearch_outputs/round3/r3s2_field_reach/B3/eval",
    "_substrate_commit": "e606a4f14f8e870fccee097ed18b6050344a4ace",
    "_vendor_source": "mffp_autoresearch/round3/worktrees/r3s2_field_reach/B2/models_r3/r3s2_route @ e606a4f1 (ALL of smoke_eval.py, model.py, front_end.py, ic_synth.py, lsi_filter.py, local_corrector.py, direct_head.py, bands.py, periodicity.py, upsample.py, floor_arms.py, selector.py, probes.py, sidecars.py). NO code vendored from any round-1 family beyond what r3s2_route already carried (round-1 s4_router via r2s2_stack). IC-synthesis math remains B1's re-implementation from the READ-ONLY generator surfaces with provenance comments (never imported, never edited).",
    "_declared_reuse": "role (a), round-2 program 5.10a: the DC-lineage corrector remains a declared FROZEN test-time sub-component. NEW in B3: the SAME frozen corrector is additionally evaluated on REAL train-side LF (rung R2_oracle) as an explicitly NON-DEPLOYABLE reference arm, in the same role class as the copy-LF reference; it never touches test LF (immutable #9) and never enters a panel geomean claim.",
    "_novelty_declaration": "The contribution is a REGIME and a DECISION RULE, not an architecture and not the oracle/predicted decomposition (which is preempted: arXiv:2602.13416, arXiv:2604.12440, arXiv:1712.05884 3.3.1). New: a ceiling ladder whose oracle intermediate is structurally UNAVAILABLE at inference, measured on held-out TRAIN rows with an enumerated C(5,3) fold population at N_hf = 5, denominated by a matched-budget no-LF direct arm, priced against certified training-free floors at matched fit-set size and the certified film denominator, and converted into a prospective drop/keep rule for the LF intermediate (D3, an established absence in the retrieved corpus).",
    "_preflight": "ZERO-GPU, before submission: tools/transfer_gain_anatomy.py --ridge-ladder 0,1e-10,3.162e-10,1e-9,1e-8,1e-7,1e-6,1e-4,1e-2,1e-1 --enumerate-folds --datasets <all 6>; tools/amplitude_calibration_audit.py --dataset <each> --tau-rel <cell>; tools/fitset_matched_n_audit.py --datasets ifc_heat,ifc_poisson --n-scored 320; tools/subset_geomean_unit_audit.py on every subset sentence; target-scale spread audit on pfc; rung/lift tripwire vs panel_data.py.",
    "_postflight": "tools/zero_work_resume_scan.py --read-ckpt-binding --data-hashes state/data_hashes.json --verify-binding --fail-on-zero-work; tools/stale_checkpoint_audit.py --exclude stale_ckpt; tools/lsi_transfer_stability_audit.py READ ONLY THROUGH transfer_gain_anatomy.py (B2 cross-stream note 1: its AMPLIFYING verdict is an unweighted mode mean).",
    "_script_env": {
      "ROUND2_EVAL_RESULTS": "$OUT_DIR/training",
      "ROUND2_EVAL_CACHE": "$OUT_DIR/cache",
      "_why": "MANDATORY, carried from B1's review-FAIL discharge d5069a74: without these, score_panel.py::_results_dir()/_cache_dir() default to EVAL_DIR/{results,cache} and the job writes per-cell JSONs and multi-GB checkpoint trees into the FROZEN round-2 eval layer (immutable 3). Export both after OUT_DIR= and before BOTH score_panel.py invocations, and mkdir -p $OUT_DIR/cache."
    },
    "_note": "Keys prefixed _ are card directives, NOT passed to --env. score_panel.py --datasets accepts ONLY 'panel' | 'guard' | a comma-list of dataset NAMES; the literal 'panel' resolves to the ROUND-2 six-dataset panel via round2/project.yaml and MUST NOT be used. The guard run is a SEPARATE invocation with --datasets guard (smoke tier 200, seed 0). Checkpoint dirs must be FRESH under mffp_autoresearch_outputs/round3/r3s2_field_reach/B3/ckpt (never reused from B1/B2). Wall-clock: B2 measured 44-55 min/seed on 5 cells x 7 arms; B3 adds pfc and two zero-GPU rungs, so request 03:00:00 as B2 did.",
    "_registration_hold": "state/batch3_scope_2026-08-10.md: NO clause registers until ADR r3-0007 is decided. The registration predicate (R3S2B3_REGISTRATION_PREDICATE) resolves the clause set at registration time under options A/B/C with ZERO redesign: the six cells run regardless; only which per-cell units are REGISTERED vs REPORT-ONLY changes. pfc has NO certified min_claimable_effect (noise_floor.json covers 5 cells, certified 2026-08-08; ADR r3-0005 restored pfc 2026-08-10) so its unit is REPORT-ONLY unless an mce is certified first. Both ifc units are REPORT-ONLY under every option (floor-disqualified, B2)."
  }
}
```

- **Expected outcome**:
  - **P1 — the ceiling exists and is large**: `phi_ceil ≥ 0.9` on ac / fk / ch / pfc, i.e. **11×**
    ac's `tau_phi` 0.07921, **18×** fk's 0.05128, **33×** ch's 0.02741. Basis: round-2 report §5
    item 6 measured raw copy-LF beating fitted condition-only arms by **164.9× / 77.0× / 12.3× /
    49.5×** (ac/ch/fk/pfc) on held-out train rows; a 12× error ratio is `phi_ceil` = 0.92. On
    ifc_poisson B2 F9 gives oracle 0.0195–0.0211 vs deployed 0.119–2.147 ⇒ `phi_ceil ≥ 0.83`,
    **6.2×** `tau_phi` 0.13347 (report-only cell).
  - **P2 — the realization fraction is ~0**: `rho ≤ 0.10` on ac and fk. Basis: B2's `A7 ≈ A1` within
    0.11 skill units on all three sharp cells and B1's F2 (trained corrector earns < 1.05 skill
    units against 1.74 / 24.63 bars).
  - **P3 — the error is hallucination-dominated**: `E_hall / (E_hall + E_est) ≥ 0.9` on ≥ 3 cells
    (B2 F9's 6–100× ratio; round-2 §4's *"99.98% stage-1 error on cahn_hilliard"*).
  - **C1 margins vs the noise floor (film units)**: expected `skill_film(R1) − skill_film(R2)` ≈
    0.8 (ac) / 0.4 (fk) / 0.20 (ch) / 3.4 (ifc_poisson) against `tau_film` **0.076103 / 0.045486 /
    0.021736 / 0.562718** — i.e. **10× / 9× / 9× / 6×** the certified floor. Every bar is a `min`
    over the full 30-leg (3 seeds × 10 folds) or 15-leg population, so no threshold sits inside its
    statistic's own spread (clause-hygiene rule 1, discharged by construction).
  - **Δ vs anchor (mechanics, not a claim)**: R1's 5-cell test geomean is expected within ~1 panel
    `seed_mce` (0.5083) of the stream anchor **10.0853**, with the 320/400 fit-set reduction
    disclosed; cratered gates 15.128 (5-cell subset) and 58.255 (= 1.5 × launch best-floor 38.8368).

- **Expected falsification**: *If on ≥ 2 registered cells the deployed pseudo-LF route realizes more
  than half of its own certified ceiling — `min` over (seed × fold) legs of `rho` > 0.5 while
  `phi_ceil` > `tau_phi` — then the LF intermediate is not emulator-limited on this panel and the
  card's ceiling framing, together with the D3 drop/keep rule derived from it, is falsified.*
  (Secondary registered falsifiers: C1 fails to fire on ≥ 2 registered cells; or C3 fails on ≥ 2
  registered cells, which voids the instrument rather than the hypothesis and is reported as such.)

- **Prior-art verdict quoted** (verbatim, `websearches/r3s2_field_reach/batch_3/report.md`):
  - **D1 — the emulator-ceiling ladder** — `preempted-but-MF-composition-open (cite)` — *"the
    opening is much narrower than batch 2's E2; the **instrument may not be claimed**, only the
    measurement in this regime"*; open: *"In **every** fetched instance the oracle intermediate is a
    deployable counterfactual — coarsened ERA5, GT masks, GT mels, a real coarse solve. Here the LF
    field exists **at train only** and must be hallucinated from the condition vector at test, so
    the ladder measures a **bound on what the route could ever buy**, not an alternative
    deployment. No fetched source runs it (a) with an intermediate structurally unavailable at
    inference, (b) at N_hf = 5 with a closed-form corrector whose fold population C(5,3) is
    enumerable, or (c) priced against a **certified training-free floor** + certified baseline
    denominator in skill units. That triple is the claim."*
    Citations: https://arxiv.org/html/2602.13416 · https://arxiv.org/html/2604.12440 ·
    https://arxiv.org/pdf/2606.07718 · https://arxiv.org/pdf/1712.05884 §3.3.1 ·
    https://arxiv.org/pdf/2301.10937 (snippet-only, no verdict weight:
    https://ieeexplore.ieee.org/document/6521941/).
  - **D2 — selection-input repair** — `preempted (cite)` — *"usable ONLY as an instrument repair,
    exactly like batch 2's E1. Presenting it as the idea is a rebadge"*; open: *"Only the numbers:
    whether at n_fit = 3, with all 10 folds enumerated, selection on emulator-output inputs recovers
    the ifc_poisson gap that band-deletion cost (F9/F10), and whether it beats or loses to the
    shipped band-limit on the sharp cells."*
    Citations: https://arxiv.org/pdf/2305.00974 · https://arxiv.org/pdf/1712.10050 ·
    https://arxiv.org/pdf/1712.05884 · https://arxiv.org/html/2604.12440 ·
    https://arxiv.org/pdf/2506.12007 · https://arxiv.org/html/2602.13416.
  - **D3 — ceiling ratio as a prospective decision rule** — `preempted-but-MF-composition-open
    (cite)` — open: *"Every retrieved use answers **'which stage to improve'**; none answers
    **'should this stage exist at all'** — converting the ceiling ratio into a *drop-the-intermediate*
    decision whose fallback is a direct condition→HF model at matched budget. With batch 2's three
    failed attempts at the direct-vs-two-stage ablation plus this turn's concession, treat as an
    established absence. It is a **methodological** contribution and must be registered as one."*
    Citations: https://arxiv.org/pdf/2606.07718 · https://arxiv.org/html/2602.13416.
  - Standing: *"**Nothing is `novel`** — the project record is now 0-for-10 (program.md §13.3)."*

- **Immutables self-check**: **pass (11/11)** — the 8 core immutables plus the three round-3 extras,
  each with positive evidence, in
  [iteration_1.md](iteration_1.md) §"Immutables self-check". Highlights:
  #9 (stripped test view) is the *design driver*, not a risk — the oracle rung lives on held-out
  TRAIN rows and `R3S2B3_ROLES_READ` makes "never read `test_lf`" machine-checkable through the
  batch-3 `ckpt_binding.py` hook; extra (9) every C1/C2 bar is a certified `min_claimable_effect`
  converted unit-invariantly and cleared by 6–33×, with **pfc explicitly cited by no threshold**
  (no certified mce); extra (10) the nearest pre-falsified lever is B2's own G2(iii) LSI-repair
  hypothesis, re-entered **only** as an out-of-sample-selected instrument with a justified grid
  floor and the energy-weighted acceptance statistic that B2's postmortem demanded; extra (11) C4
  makes the floor arms a gating conjunct, which is what makes both ifc units report-only from the
  outset.

- **Anchor reference**: `null` (per §4.5, all four round-3 streams are gap/lever/diag; the
  own-stream anchor 10.0853 is implicit and used only for the mechanics/cratered comparand).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none — no round-3 card carries `reopen_candidate: true`; scan of `experiment_cards/*/batch_*/*.json`)* | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

None — the single slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| 1 (only) | `mf_composition/emulator_ceiling_ladder_with_no_lf_denominator` | Five-rung ceiling ladder on held-out TRAIN rows (direct no-LF denominator → pseudo-LF degraded → deployed stack → real-LF oracle → training-free copy-LF), fold-enumerated at N_hf = 5, priced against certified floors at matched fit-set size and registered per cell in film units, turning the oracle gap into a prospective drop/keep rule for the LF intermediate | **filled** (registration deferred to the ADR r3-0007 decision; zero redesign under A/B/C) |

## Notes for the starter / builder

1. **Do not transcribe until ADR r3-0007 is decided** (REGISTRATION HOLD). Nothing else in the card
   changes with the decision — only which per-cell clause units are REGISTERED vs REPORT-ONLY, via
   `R3S2B3_REGISTRATION_PREDICATE`.
2. **pfc has no certified `min_claimable_effect`.** Its unit is REPORT-ONLY unless one is certified
   before registration. pfc is still run: it is this stream's never-exercised cell and its scored
   cell is rung 1 + spectral zero-pad (ADR r3-0005), not the `R3S2_EMU_RUNG=max` path B1/B2 used —
   hence the mandatory `R3S2B3_RUNG_LIFT_TRIPWIRE` and the pfc target-scaler pre-flight.
3. **Both ifc units are REPORT-ONLY under every ADR option** (floor-disqualified on B2's evidence),
   so B2's sharpest ceiling measurement (F9, ifc_poisson) is carried as REPORT-ONLY evidence and
   never as a registered clause — as the batch-3 constraint requires.
4. `summary_so_far.md` runs ~2000 words, above the 500–1200 guidance; the excess is the mandated
   verbatim §12 / immutable-#9 / prior-art quotation blocks, which are load-bearing for the design.
