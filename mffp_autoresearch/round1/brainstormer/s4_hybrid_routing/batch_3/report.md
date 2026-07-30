# Brainstormer Report — Stream `s4_hybrid_routing`, Batch 3

**Stream**: `s4_hybrid_routing`
**Batch**: 3 (the round's pre-scoped ROUND SYNTHESIS / ROUTER slot)
**Total iterations**: 1
**Slot filled**: 1 / 1
**Reopen candidates resolved**: 0 (none exist — all 19 cards carry `reopen_candidate: false`)

## Slot

- **Category**: `mf_composition / per-dataset discrete super learner over a
  2-element library (closed-form LSI branch vs corrector-on-LSI-cleaned-residual),
  library membership set by test-time LF availability, with OOF selection at
  every stage and a per-sample no-harm layer`

- **Card type**: `model`

- **Motivation**: The round's synthesis slot composes three already-measured
  pieces — s6-B2's training-free eligibility statistic, s6-B2's closed-form LSI
  branch and repaired trust head, and s4-B2's OOF-gate discipline — into the one
  object the websearch says is still open as a *composition*, while claiming
  **zero** novelty for the router itself. Verdict D1 verbatim:
  *"The **selection rule is not open** (discrete super learner) and
  **availability-keyed gating is not open** (missing-modality MoE). Open: no
  fetched source routes on **fidelity availability inside a multi-fidelity PDE
  surrogate**, and none routes between a **defect-correction** path and a
  **transfer-learning** path. **Claim zero novelty for the router.** The card's
  contribution is the composition + its controls; the honest framing is "the
  discrete super learner applied per dataset over a 2-element library, where
  library membership is itself determined by a data property (does the test
  split ship LF?)"*. The card's one genuinely open surface is D3, verbatim:
  *"**the card's strongest open surface** ... In **every** fetched source the
  pre-stage is a *fixed classical solver*, a *learned* deconvolution layer, or a
  *scalar/affine* fidelity correlation. **Nobody fits a |k|-dependent LSI
  transfer function to the fidelity gap and then trains a corrector on ITS
  residual**, and nobody reports the zero-parameter filter as a scored floor
  beside the trained model."* D2 fixes the gate's status —
  *"Only the **measurement** ... The card cites the estimator and claims only
  the number"* — and D5 makes the LSI-alone / corrector-alone controls
  mandatory: *"no fetched MF source reports a zero-parameter fitted-filter floor
  next to its trained model ... The transferable output is the *reporting
  standard*."*

- **Concrete config**: New family `models_r1/s4_router`, vendored sha256-verified
  from `models_r1/s6_local_repair` @ `caff5c9` (the `circ_repair` lineage) with
  all `S6_*` semantics preserved. Four additions: (1) the fitted `T(k)` LSI
  filter promoted from sidecar to an optional **pre-stage** so the corrector is
  trained on `R - C_LSI` (`S4R_TARGET=lsi_cleaned`, D3); (2) `router.py` — the
  availability key (`test_lf_present`; where false, the champion transfer branch,
  i.e. `ifc_poisson` only), the **discrete super learner** decision
  (`S4R_ROUTER_DECIDER=oof_val_risk`: pick the library member with the lower
  out-of-fold validation risk on a slice neither was fitted on, tie-band = the
  dataset's certified relative floor, ties go to the zero-parameter branch), and
  the **recorded-but-not-deciding** rho rule
  (`1 - rho_LSI(val) >= 0.15` -> DC, pre-registered as a *prediction*); (3) the
  repaired trust head as a per-sample no-harm layer — CHANGE 1
  `S4R_HEAD_WEIGHTING=relative_l2` (weight the alpha-regression by
  `w^2 = (||C_i||/||Y_i||)^2`) and CHANGE 2 `S4R_HEAD_NOHARM_CAP=floor`; (4) free
  sidecars — no-selection counterfactual, in-sample-selection counterfactual
  (s4-B2's sign-inversion measurement transplanted at zero GPU), per-stage
  `val_base_oof / val_base_insample`, branch-oracle ceiling, interior-16 crop
  with `crop_sign_flip`, and a registration-corrected-reference sidecar.
  **Why the rule does not decide**: a rule-only router is *already known* to
  violate no-harm on `sharp__fisher_kpp_2d` by 63.8 % (rule says LSI 0.0076951,
  DC gets 0.0046978) — pre-registering no-harm on it would pre-register a known
  failure. Five arms, two of them trained:

  | tag | branch / target | selector | head | trained? | role |
  |---|---|---|---|---|---|
  | `lsi_alone` | LSI, closed form | off | off | **no** (0 gradient steps) | mandatory D5 floor + gate V2 |
  | `dc_raw` | DC on raw `R` | off | off | **YES** | D3 control + gate V1 (reproduces s6-B2 `circ_repair`) |
  | `dc_cleaned` | DC on `R - C_LSI` | off | off | **YES** | D3 novelty leg; donor for both router arms |
  | `router` | availability -> {LSI, DC-cleaned} | `oof_val_risk` | on | **no** (borrows) | **PRIMARY** — no-harm claim + rule table |
  | `router_forced_wrong` | rule-inverted branch | `rule_inverted` | on | **no** (borrows) | the rule's information-content control |

  All five run `panel` (6) and `guard` (3) at 200 epochs, seed 0. Guard legs are
  **report-only** (program.md §2.3: the guard set is *"not part of the
  objective"*, and `state/noise_floor.json` has no guard entry, so no certified
  floor exists to clear). Every claim is a **within-dataset ratio between arms**,
  so the frozen registration-inflated copy-LF denominator cancels exactly.

- **Recipe**:

```json
{
  "base_family": "s6_local_repair",
  "base_commit": "caff5c97d7365c2c200daa30f67c6db3b627aee0",
  "family_dir": "models_r1/s4_router",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [
    0
  ],
  "env": {
    "S4R_ARM": "router",
    "S4R_LIBRARY": "lsi,dc",
    "S4R_AVAILABILITY_KEY": "test_lf_present",
    "S4R_ROUTER_DECIDER": "oof_val_risk",
    "S4R_SELECTOR_TIEBAND": "floor",
    "S4R_RULE_STAT": "one_minus_rho_lsi_val",
    "S4R_RULE_THRESH": "0.15",
    "S4R_TARGET": "lsi_cleaned",
    "S4R_HEAD": "on",
    "S4R_HEAD_WEIGHTING": "relative_l2",
    "S4R_HEAD_NOHARM_CAP": "floor",
    "S4R_BORROW_FROM": "dc_cleaned",
    "S4R_OOF_SCREEN": "1",
    "S4R_INSAMPLE_COUNTERFACTUAL": "1",
    "S4R_NOSEL_LEG": "1",
    "S4R_BRANCH_ORACLE_SIDECAR": "1",
    "S4R_BOUNDARY_SPLIT": "1",
    "S4R_CORRECTED_REF_SIDECAR": "C,D",
    "S4R_DIAG_OUT": "mffp_autoresearch_outputs/round1/s4_hybrid_routing/B3/eval",
    "S6_FALLBACK_NO_TEST_LF": "champion",
    "S6_VARIANT": "local_pixel_gate",
    "S6_SELECTOR": "oof_persample_head",
    "S6_PAD_MODE": "circular_if_periodic",
    "S6_PERIODIC_TEST": "wrap_continuity_ratio_hf_train",
    "S6_PERIODIC_TOL": "1.25",
    "S6_LF_SOURCE": "dataset_lf_fidelity",
    "S6_LF_FID": "max",
    "S6_KERNEL": "7",
    "S6_DEPTH": "4",
    "S6_WIDTH": "32",
    "S6_GATE_HOLDOUT_FRAC": "0.2",
    "S6_GATE_INIT": "zero",
    "S6_GATE_LINESEARCH_INCLUDES_ZERO": "1",
    "S6_HEAD_MODEL": "ridge",
    "S6_HEAD_CANDIDATES": "persample_head,global_scalar,zero",
    "S6_HEAD_CV_FOLDS": "4",
    "S6_HEAD_FEATURES": "X,log_lf_l2,log_lf_grad_ratio,log_lf_band_frac4,log_corr_l2_ratio,log_corr_band_frac4",
    "S6_HEAD_RIDGE_GRID": "1e-3,1e-2,1e-1,1,10",
    "S6_HEAD_ALPHA_CLIP": "0,1.5",
    "S6_HEAD_MIN_GAIN": "1e-3",
    "S6_LSI_SIDECAR": "1",
    "S6_LSI_RIDGE": "0",
    "S6_LSI_F6_TOL": "0.02",
    "S6_BAND_EDGES_FRAC": "0,0.125,0.25,0.5,1.0",
    "S6_ASSERT_PAIRED_CORRECTOR": "1",
    "S6_LEAKAGE_TRIPWIRE": "1",
    "S6_REPLICA_TOL": "0.10",
    "_note": "keys prefixed _ are card directives, NOT passed to --env. The --env set per arm is every non-underscore key above with that arm's deltas from _arms applied.",
    "_arms": [
      {
        "tag": "lsi_alone",
        "role": "mandatory zero-parameter floor (D5) + validity gate V2",
        "datasets": "panel,guard",
        "S4R_ARM": "lsi_alone",
        "S4R_ROUTER_DECIDER": "off",
        "S4R_TARGET": "raw",
        "S4R_HEAD": "off",
        "S4R_BORROW_FROM": "",
        "S6_VARIANT": "lsi_ctrl",
        "S6_SELECTOR": "heldout_scalar"
      },
      {
        "tag": "dc_raw",
        "role": "corrector-alone on the RAW residual: the D3 control and validity gate V1",
        "datasets": "panel,guard",
        "S4R_ARM": "dc_raw",
        "S4R_ROUTER_DECIDER": "off",
        "S4R_TARGET": "raw",
        "S4R_HEAD": "off",
        "S4R_BORROW_FROM": "",
        "S6_VARIANT": "local_pixel_gate",
        "S6_SELECTOR": "heldout_scalar"
      },
      {
        "tag": "dc_cleaned",
        "role": "corrector-alone on the LSI-CLEANED residual: the D3 novelty leg; donor for both router arms",
        "datasets": "panel,guard",
        "S4R_ARM": "dc_cleaned",
        "S4R_ROUTER_DECIDER": "off",
        "S4R_TARGET": "lsi_cleaned",
        "S4R_HEAD": "off",
        "S4R_BORROW_FROM": "",
        "S6_VARIANT": "local_pixel_gate",
        "S6_SELECTOR": "heldout_scalar"
      },
      {
        "tag": "router",
        "role": "PRIMARY: discrete super learner over {lsi, dc_cleaned}, availability-keyed library, + repaired per-sample no-harm head",
        "datasets": "panel,guard",
        "S4R_ARM": "router",
        "S4R_ROUTER_DECIDER": "oof_val_risk",
        "S4R_TARGET": "lsi_cleaned",
        "S4R_HEAD": "on",
        "S4R_BORROW_FROM": "dc_cleaned",
        "S6_VARIANT": "local_pixel_gate",
        "S6_SELECTOR": "oof_persample_head"
      },
      {
        "tag": "router_forced_wrong",
        "role": "rule information-content control: forced to the branch the rho rule says LOSES",
        "datasets": "panel,guard",
        "S4R_ARM": "router_forced_wrong",
        "S4R_ROUTER_DECIDER": "rule_inverted",
        "S4R_TARGET": "lsi_cleaned",
        "S4R_HEAD": "on",
        "S4R_BORROW_FROM": "dc_cleaned",
        "S6_VARIANT": "local_pixel_gate",
        "S6_SELECTOR": "oof_persample_head"
      }
    ],
    "_primary_arms": {
      "C1_no_harm": "router vs per-dataset min(lsi_alone, dc_cleaned), per panel dataset",
      "C2_routing_rule": "the rho-rule predicted branch vs the realized best branch, 7 datasets",
      "C3_D3_target": "dc_cleaned vs dc_raw (panel: fisher_kpp claimable, other three pre-registered NULL; guard: report-only)",
      "C4_oof_protocol": "router's OOF selection vs the in-sample-selection counterfactual (free sidecar, measurement only)"
    },
    "_design": "SWEEP, not screen-and-promote. ADR 0007 exempts spec-pre-directed slots, and four of five arms are CONTROLS whose value is being REPORTED (D5: dropping one destroys a measurement). All five are reported; the primary arm per clause is fixed above BEFORE submit (ADR 0007 guardrail). The contract screen is plumbing + no-harm only and is NEVER quoted in parts 5-7.",
    "_borrowed_vs_trained": "TRAINED (new gradient steps): dc_raw, dc_cleaned only. BORROWED / ZERO-GRADIENT: lsi_alone (closed form), router and router_forced_wrong (borrow_partner_stages from dc_cleaned; corrector_state_sha256 equality asserted). FREE within-run legs (no extra pass): no-selection counterfactual, in-sample-selection counterfactual, branch-oracle ceiling, per-stage val_base_oof/val_base_insample screen, interior-16 crop, corrected-reference sidecar.",
    "_sbatch": "MAIN: #SBATCH --job-name=r1-s4_hybrid_routing-B3-s0 --partition=gpu --nodes=1 --ntasks=1 --cpus-per-task=4 --gres=gpu:h100:1 --mem=32G --time=03:00:00; logs mffp_autoresearch_outputs/round1/s4_hybrid_routing/B3/slurm/%x-%j.{out,err}. Ledger basis (s6-B2 job 66056503, same family lineage, H100): trained panel leg 18.05-20.42 min, trained guard leg 5.3 min, closed-form panel leg 1.02 min / guard 0.27 min, borrowed arm 1.22 min. Estimate: dc_raw 20.4+5.3, dc_cleaned 21.5+5.5 (LSI fit adds ~1 min), lsi_alone 1.0+0.3, router 1.3+0.5, router_forced_wrong 1.3+0.5, sidecars ~5 = ~63 min = 35% of the 3 h request. SCREEN: same directives with --time=01:00:00 (s6-B2's 5-arm screen analogue 8.6 min). The ORCHESTRATOR submits, never the builder.",
    "_screen": "ONE contract-tier job before the sweep: --epochs 2 --seed 0, all five arms, --datasets panel AND --datasets guard. Plumbing + no-harm only (every arm must score skill <= 1.02 on the five beyond-copy datasets; a violation means the identity construction broke => ALGO). Screen numbers are NEVER reportable (ADR 0007) and appear only in build_notes.",
    "_sweep": "one SLURM job, seed 0, five score_panel.py panel calls + five guard calls, serial, in the order lsi_alone, dc_raw, dc_cleaned, router, router_forced_wrong (donors before borrowers - the pairing assert needs the donor record on disk). Export ROUND1_EVAL_RESULTS=<outputs>/eval/results_<tag> per arm so per-arm result JSONs and ckpt dirs cannot collide (s1-B2 build trap: score_panel._run_one derives paths from (family_dir.name, dataset, epochs, seed) only). Checkpoints at <ckpt_dir>/arm_<tag>/last.pt mirrored to <ckpt_dir>/last.pt; the meta guard covers (arm, target, decider, head, variant, padding_mode, stage, epochs_target, grid, seed). Idempotent: safe to resubmit, every arm resumes (immutable 8).",
    "_validity_gates": "V1 dc_raw reproduces s6-B2 circ_repair seed-0 panel nRMSE within S6_REPLICA_TOL=10% on all six (helmholtz 0.3294501260438018, pfc 0.0007204126530396635, allen_cahn 0.0009363332709684444, fisher_kpp 0.004697840233022452, cahn_hilliard 0.04136137418852845, ifc_poisson 0.05562937038722282). V2 lsi_alone reproduces s6-B2 lsi_ctrl within S6_LSI_F6_TOL=2% (pfc 0.0006124684737243416, allen_cahn 0.0008318192821, fisher_kpp 0.007695081137159533, cahn_hilliard 0.03856875162347986) and selects alpha=0 on ext__helmholtz_2d. V3 the identity path is bit-equal to eval/copylf_baselines.json within 1e-9 (inherited hard assert). V4 the router's no-selection leg (selector off, alpha_hat=0) equals the selected branch's own prediction to 0. V5 on ifc_poisson every arm equals the champion fallback within 1e-6 relative. V6 router_forced_wrong's per-dataset branch choice is the exact complement of the rho rule's on all 7 LF-bearing datasets. Any miss is ALGO: fix before reading any contrast.",
    "_source": "vendor models_r1/s6_local_repair from caff5c97d7365c2c200daa30f67c6db3b627aee0 (branch round1/exp-s6_local-B2) to models_r1/s4_router, sha256-verified per file via `git show <commit>:<path>` BEFORE any edit. Edits: (1) ARM_SPEC re-pointed at S4R_ARM with the five arms above; (2) lsi_filter.py's fitted T(k) promoted from sidecar to an optional PRE-STAGE feeding the corrector's target (S4R_TARGET); (3) new router.py holding the availability key, the OOF val-risk selector with the floor tie-band, the recorded rho rule, and the forced-wrong inversion; (4) trust_head.py gains the w^2=(||C||/||Y||)^2 regression weighting and the per-sample no-harm cap; (5) new score-neutral diag keys: branch_selected, rule_predicted_branch, one_minus_rho_lsi_val, val_risk_lsi, val_risk_dc, val_base_oof_over_insample, insample_counterfactual_choice, insample_counterfactual_test_cost, nrmse_no_selection, nrmse_branch_oracle, interior16_nrmse, crop_sign_flip, corrected_ref_C_nrmse, corrected_ref_D_nrmse, corrector_provenance, corrector_state_sha256. model.py stays the byte-identical copy of mf_fno_transfer_film/model.py @967562e. round1/eval/, tools/, akash/** and factory_root/{eval,baselines,references,scripts,data} are never touched; tools are VENDORED with citation, never imported."
  }
}
```

- **Expected outcome**:
  1. **NO-HARM primary (panel).** `nRMSE(router) <= min(nRMSE(lsi_alone),
     nRMSE(dc_cleaned)) x (1 + floor_d)` on all four sharp panel datasets, with
     `floor_d = 10.000 %` each. Predicted realised branch: **LSI** on pfc /
     allen_cahn / cahn_hilliard, **DC** on fisher_kpp. `ext__helmholtz_2d`
     report-only (floor 70.165 %); `ifc_poisson` = champion path to 1e-6
     relative, **no claim** (s6-B1: `alpha = 0` on 6/6 on a champion base;
     s6-B2 measured 1.5453 +/- 0.0002 skill across five arms).
  2. **Panel geomean**: predicted [0.165, 0.200] versus the stream anchor
     **6.703016** (s6-B2 reference points: `lsi_ctrl` 0.19722, `circ_repair`
     0.19258, `trust_head_circ` 0.18759). **Explicitly NOT the claim** — it is
     inherited from the s6/DC lineage and s2-B2 showed the beyond-copy win is
     registration repair (overlap 0.975-0.9987). The router-vs-branch-oracle gap
     is predicted at **+8.6 %**, *inside* the 13.183 % geomean floor, i.e.
     pre-registered as unmeasurable.
  3. **Routing-rule prediction table** (`1 - rho_LSI(val)` from s6-B2 F5;
     realized best counted only where the branch gap is resolvable):

     | dataset | 1 - rho_LSI(val) | rule predicts | predicted realized best | agree? |
     |---|---|---|---|---|
     | `fluid` (guard) | 0.51943 | DC | DC (3.1x) | agree |
     | `sharp__sod_1d` (guard) | 0.25016 | DC | DC (17.0x) | agree |
     | `heat_local` (guard) | 0.18007 | DC | DC (11.7x) | agree |
     | `sharp__cahn_hilliard` | 0.10017 | LSI | tie (+7.2 % < 10.000 % floor) | untestable |
     | `sharp__fisher_kpp_2d` | 0.01575 | LSI | **DC (-38.95 %)** | **DISAGREE (known; predicted to reproduce)** |
     | `sharp__allen_cahn_2d` | 0.00342 | LSI | LSI (+12.6 %) | agree |
     | `sharp__phase_field_crystal_2d` | 0.00018 | LSI | LSI (+17.6 %) | agree |

     Pre-registered: **exactly 1 disagreement** among 6 testable cells, and
     Spearman(`1 - rho_LSI(val)`, realized DC/LSI ratio) over all 7 stays
     **<= -0.714** (s6-B2 measured -0.857, p = 0.0137).
  4. **D3 leg (the novelty leg).** Guard (report-only, no floor exists):
     `dc_cleaned` better than `dc_raw` on **>= 2 of 3**, 0-15 % relative
     (s6-B2 cos(C_NN - C_LSI, R - C_LSI) = 0.9984 / 0.9960 / 0.9441 on
     sod_1d / heat_local / fluid). Panel, **claimable on
     `sharp__fisher_kpp_2d`** (cos 0.767; the only panel dataset with a
     resolvable trained surplus): point prediction **-12 %** vs `dc_raw`, band
     [-25 %, 0 %], against the **10.000 %** certified floor — a null is an
     admissible pre-registered outcome and would confine D3's demonstrated value
     to the guard set. Panel **NULL** on pfc / allen_cahn / cahn_hilliard
     (cos 0.763 / 0.274 / 0.037): `|delta| < 10.000 %` on >= 2 of 3.
  5. **OOF protocol (measurement only, no panel claim — D2's instruction).** The
     in-sample-selection counterfactual changes the decision on >= 1 of 6 panel
     datasets, with `val_base_oof / val_base_insample > 2x` wherever it does
     (s4-B2: 16.4x / 2.9x where its stage hurt, 0.82-1.09x where it did not).
  6. **Forced-wrong control**: resolvably worse than `router` on the three guard
     sets (report-only) and on pfc / allen_cahn (+17.6 % / +12.6 %, both above
     the 10.000 % floor), and *better* on fisher_kpp — the rule's known
     inversion, shown rather than hidden.

- **Expected falsification**: The card is falsified if **any** of: (i) the
  router's test nRMSE exceeds the better of its two branches by more than that
  dataset's certified relative floor (10.000 % on each of
  `sharp__phase_field_crystal_2d`, `sharp__allen_cahn_2d`,
  `sharp__fisher_kpp_2d`, `sharp__cahn_hilliard`) on **>= 1** of those four, or
  the `ifc_poisson` availability leg deviates from the champion path by more than
  1e-6 relative; (ii) the routing rule disagrees with the realized best branch on
  **>= 3** of the resolvable cells (against exactly 1 predicted), or
  Spearman(`1 - rho_LSI(val)`, realized DC/LSI ratio) over the 7 LF-bearing
  datasets rises above **-0.714** (n = 7, one-tailed alpha = 0.05 critical value;
  s6-B2 measured -0.857, p = 0.0137); or (iii) the D3 leg inverts, i.e.
  `dc_cleaned` is **worse** than `dc_raw` by more than 10.000 % on
  `sharp__fisher_kpp_2d`, or the pre-registered panel NULL breaks with
  `|dc_cleaned - dc_raw| > 10.000 %` on **>= 2** of {pfc, allen_cahn,
  cahn_hilliard}, or the guard-set direction (report-only) is negative on all
  three.

- **Prior-art verdict quoted**: see the Motivation above — D1
  (`preempted-but-MF-composition-open (cite)`), D3
  (`preempted-but-MF-composition-open (cite)`, *"the card's strongest open
  surface"*), D2 (`preempted (cite)` outright), D5 (`preempted (cite)` as
  methodology) are each quoted verbatim from
  `websearches/s4_hybrid_routing/batch_3/report.md`. Citations to carry into the
  card's `prior_art`: https://tlverse.org/csp2020-workshop/sl3.html (fetched —
  the *"cross-validation selector"*, *"proven to be asymptotically as accurate as
  the best possible prediction algorithm in the library"*);
  https://arxiv.org/html/2511.11460v2 (fetched — routing gated on *"the
  modality-missing type"*); https://arxiv.org/abs/1608.00060 (fetched —
  *"K-fold sample splitting, which we call cross-fitting"*);
  https://ar5iv.labs.arxiv.org/html/2102.01010 (fetched — `u_t = u_t* +
  LC(u_t*)`; *"LI performs best, although learned correction (LC) is not far
  behind"*); https://arxiv.org/html/2310.03572 (fetched — the canonical
  residual-MF method has **no** linear stage);
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4915073/ and
  https://vincmazet.github.io/bip/restoration/deconvolution.html (fetched — D4's
  fitted-taper-not-hard-cutoff design constraint, inherited, never claimed);
  https://arxiv.org/pdf/2605.15179 (fetched — MoE's stated benefit is avoiding
  *"negative transfer"*, which is why the primary is a **no-harm** claim).

- **Immutables self-check**: **pass (10/10)** — full positive evidence per item
  in [iteration_1.md](iteration_1.md) §"Immutables self-check". Headlines: data
  read-only via the inherited `dataset_lf_fidelity` / `copylf_prediction` path
  (item 1); panel + guard untouched, and the tempting alternative — promoting
  guard datasets to scored status, which is s6-B2's own next_direction item 1 —
  was **rejected** as an immutable-2 violation (item 2); the D3 change is to the
  **training target**, never to the scored metric (item 4); every new knob is an
  env var listed in the recipe (item 5); seed 0 / 200 epochs / 2-epoch screen
  only (item 6); every falsification threshold is the dataset's **certified**
  relative floor with the numbers quoted, guard legs carry **no** threshold
  because no floor exists for them, and helmholtz + the panel geomean are
  declared non-claiming (item 9); nearest pre-falsified lever is **LF low-mode
  freezing (`mf_fno_spectral`)** — the difference is that nothing here is frozen
  and no band is cut: a full-band train-fitted `T(k)` is a separately scored
  pre-stage, falsifiable against its own `dc_raw` control (item 10).

- **Anchor reference**: `null` (program.md §4.5 — lever stream, own-stream anchor
  implicit; the operative bars are the in-batch controls `lsi_alone` / `dc_raw`
  and the certified per-dataset floors, with the stream anchor
  6.703016262587087 quoted for context only).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _none_ | n/a — a scan of all 19 cards in `experiment_cards/*/batch_*/B*.json` returns `reopen_candidate: false` on every one | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| B3 | `mf_composition / per-dataset discrete super learner over an availability-keyed 2-element library, OOF everywhere, per-sample no-harm layer` | Route per dataset between a zero-parameter fitted-LSI branch and a corrector trained on the LSI-cleaned residual by out-of-fold validation risk (zero novelty claimed), with the training-free `1 - rho_LSI >= 0.15` rule pre-registered as a *prediction* of that choice, LSI-alone / corrector-alone / forced-wrong controls in the same JSON, and a **no-harm** primary claim floored at each dataset's certified 10.000 % | filled |

## Notes carried to the starter / builder

1. **Two prior cards' lesson**: the recipe above is complete and includes the
   `_sbatch` block (main `--time=03:00:00`, screen `--time=01:00:00`, partition
   `gpu`, `--gres=gpu:h100:1`, job name `r1-s4_hybrid_routing-B3-s0`). Transcribe
   it verbatim.
2. **Cost**: genuinely trained = `dc_raw` + `dc_cleaned` only (~52 min of the
   ~63 min estimate). `lsi_alone` takes zero gradient steps; `router` and
   `router_forced_wrong` borrow `dc_cleaned`'s stages via
   `borrow_partner_stages` (s6-B2 measured borrowed arms at 1.22 min/panel-leg);
   all six diagnostic legs are free within-run measurements.
3. **Explicitly NOT in this card** (each with its reason): the attention
   corrector's capacity / bandwidth / gate (s4-B2 part 7 directive); therefore
   also **not** the permute-queries chunking fix — that family is not touched,
   and the fix is handed to the between-rounds list; the padding repair as a
   billed router branch (s6-B2: inherits the one-cell rim); the corrector-input
   wrap-seam fix (would confound the D3 contrast — first next-batch item);
   promoting guard datasets to scored status (immutable 2).
4. **Registration**: the sharp panel's denominators are frozen and inflated
   2.0-8.6x. Expect the router to sit at **parity with LSI** on the sharp panel
   and say so in advance; every clause is a within-dataset arm ratio so the
   denominator cancels, and the corrected-reference sidecar (`C,D`) is emitted
   beside the frozen score as a sidecar only, never as a score.
