# iteration_1 — `s4_hybrid_routing` batch 3 (ROUND SYNTHESIS / ROUTER)

## Design context considered

- `summary_so_far.md` §6 (the seven unknowns) and §1 (the prior-art verdict).
- The immutables block (§4.5 of the brainstormer spec) verbatim — reproduced in
  the self-check below.
- Stream anchor `state/anchors/s4_hybrid_routing.json`: champion panel geomean
  **6.703016262587087** (3-seed, batch 0, `provisional: false`).
- `state/noise_floor.json` relative floors: pfc / allen_cahn / fisher_kpp /
  cahn_hilliard **10.000 %** each, ifc_poisson **15.323 %**, helmholtz
  **70.165 %**, panel geomean **13.183 %**. No guard dataset has an entry.
- program.md §5 pre-falsified levers: WNO backbone swap, LF low-mode freezing
  (`mf_fno_spectral`), diffusion prior for point accuracy. None is re-proposed;
  see self-check item 10.
- The fixed evidence base handed down by the orchestrator: the routing rule
  (s6-B2), D3's dataset-conditional licence (s6-B2 F6), OOF-gate-everything
  (s4-B2), the trust-head reuse spec with CHANGE 1 / CHANGE 2, the honest
  framing mandated by the websearch, the registration-inflation freeze, and the
  cost lesson (`borrow_partner_stages` made s6-B2's characterisation ~0 GPU).

### The arithmetic I did before designing

Using s6-B2's shipped seed-0 numbers (card part 5, `contrast_verdicts` and
`surplus_over_lsi`) and F5's held-out statistic:

| dataset | 1 - rho_LSI(val) | realized DC/LSI test ratio | resolvable vs floor? |
|---|---|---|---|
| `fluid` | 0.51943 | 0.3213 (DC 3.1x better) | guard: no certified floor |
| `sharp__sod_1d` | 0.25016 | 0.0587 (DC 17.0x) | guard: no certified floor |
| `heat_local` | 0.18007 | 0.0856 (DC 11.7x) | guard: no certified floor |
| `sharp__cahn_hilliard` | 0.10017 | 1.0724 (LSI +7.2 %) | **no** (floor 10.000 %) |
| `sharp__fisher_kpp_2d` | 0.01575 | 0.6105 (DC -38.95 %) | **yes** |
| `sharp__allen_cahn_2d` | 0.00342 | 1.1256 (LSI +12.6 %) | **yes** |
| `sharp__phase_field_crystal_2d` | 0.00018 | 1.1762 (LSI +17.6 %) | **yes** |

Two consequences that drove the whole design:

1. **A router that decides by the `1 - rho_LSI >= 0.15` rule alone is already
   known to violate no-harm on `sharp__fisher_kpp_2d` by 63.8 %** (it would pick
   LSI 0.0076951 where DC gets 0.0046978). Pre-registering a no-harm primary on
   a rule-only router would be pre-registering a known failure. So the router's
   *decision procedure* cannot be the rule.
2. The websearch already names the decision procedure that is both preempted
   (so: zero novelty, which is what we want) and correct: *"The discrete Super
   Learner, or cross-validation selector, is the algorithm in the library that
   minimizes the cross-validated empirical risk"* (tlverse, fetched). Selecting
   by **out-of-fold validation risk** picks DC on fisher_kpp and LSI on
   pfc/allen_cahn, i.e. it can satisfy no-harm where the rule cannot.

That splits the card cleanly into (a) a *decision procedure* with zero claimed
novelty carrying the NO-HARM primary, and (b) the `1 - rho_LSI` rule demoted to
a **pre-registered training-free PREDICTION** of what that procedure will
choose — which is the actual mechanistic content, and is falsifiable.

Panel-geomean arithmetic (used only to pre-register that the geomean is *not*
the claim): if the selector reproduced the rho rule exactly it would cost
(0.0046978/0.0076951)^(1/6) = 0.9211, i.e. **+8.6 %** panel geomean versus the
branch oracle — *inside* the 13.183 % geomean floor, hence unmeasurable. Router
panel geomean is predicted in [0.165, 0.200] (s6-B2 reference points:
`lsi_ctrl` 0.19722, `circ_repair` 0.19258, `trust_head_circ` 0.18759).

## Proposal reasoning (alternatives weighed and rejected)

**Alt A — rule-only router (the literal reading of the handoff).** Rejected:
falsifies its own no-harm primary on fisher_kpp before submission (arithmetic
above). Kept as the `router_forced_wrong` control's cousin and as the
pre-registered prediction table.

**Alt B — router over {s4 `fno_transolver_seq_b2` attention corrector, s6 DC
corrector}.** Rejected on three independent grounds: s4-B2's own part 7 says
*"DO NOT spend batch-3 GPU on the attention corrector's capacity, bandwidth or
gate"*; its failure is a phase failure reproduced in both branches; and the
arm's own scored surface was only `sharp__fisher_kpp_2d`. Adding it costs ~2
trained panel legs for a branch predicted to lose everywhere. The permute-
queries chunking fix therefore does **not** ride along — that family is not
touched — and is handed to the between-rounds list instead.

**Alt C — stacked champion + corrector (the operator's original parked
candidate).** Rejected because s6-B1 part 7 item 7 explicitly *contradicts* it:
the identical held-out-alpha machinery chose `alpha = 0` on **6/6** datasets on
a champion-generated base. Kept only in its licensed form: the champion is the
branch used **where the test split ships no LF fidelity** (`ifc_poisson`), a
pre-registered no-op leg.

**Alt D — promote guard datasets to scored status (s6-B2's own next_direction
item 1).** Rejected as outside this brainstormer's authority: program.md §2.2
immutable 2 fixes the panel and guard set for the round, and §2.3 says the guard
is *"not part of the objective"*. So the guard legs run at 200 epochs (as in
s6-B2) and are **report-only demonstrations**; the D3 novelty leg's positive
direction lives there and is explicitly declared unclaimable. This is stated in
the card rather than worked around.

**Alt E — include the padding repair as a router branch.** Rejected on s6-B2's
direct instruction (*"do NOT bill the padding repair as a router branch"* — the
one-cell rim, 7.1x/7.4x over-concentration, can decide a per-dataset verdict).
The DC branch inherits `circ_repair`'s configuration as its *base*, unchanged
and uncredited, and every reported contrast additionally carries its interior-16
crop number so a rim-decided verdict is visible (`crop_sign_flip`).

**Alt F — fix the corrector's input wrap seam (s6-B2 F7's 4x discontinuity).**
Tempting (the register note says the s6-B3 candidate was "absorbed into the
ROUTER"), but rejected for this card: it changes the DC branch's base and would
confound the D3 contrast (trained-on-cleaned vs trained-on-raw) with a base
repair. It is recorded as the first between-rounds / next-batch item.

**Selected design.** One card, five arms, two of them genuinely trained:

- **Library membership by a data property** (availability): if the test split
  ships no LF fidelity -> **transfer/champion branch** (`ifc_poisson` only,
  already implemented as `S6_FALLBACK_NO_TEST_LF=champion`); otherwise the
  2-element library {**LSI branch** (closed-form fitted `T(k)`, zero trained
  parameters), **DC branch** (local corrector trained on the LSI-cleaned
  residual, D3)}.
- **Decision procedure**: discrete super learner / cross-validation selector —
  pick the library member with the lower **out-of-fold** validation risk on a
  slice neither member was fitted on, with a pre-registered tie-band (if the two
  val risks are within the dataset's certified relative floor, prefer the
  zero-parameter branch). Zero novelty claimed; citation is the tlverse text.
- **Per-sample no-harm layer**: the s6-B2 trust head, reused with CHANGE 1
  (weight the alpha-regression by `w^2 = (||C_i||/||Y_i||)^2`, i.e. regress the
  alpha that minimises the SCORED relative-L2) and CHANGE 2 (per-sample no-harm
  cap: shrink alpha_hat to 0 whenever the predicted relative gain is inside the
  dataset's certified floor). `alpha_hat = 0` reproduces the selected branch
  bit-exactly, which is also validity gate V4.
- **OOF discipline everywhere**: every selection statistic in the card is
  computed against an out-of-fold base; the screening ratio
  `val_rel_l2_base_oof / val_rel_l2_base_insample` is printed per stage; a
  **no-selection counterfactual** (selector off, alpha_hat = 0) and an
  **in-sample-selection counterfactual** (the same selector re-run against the
  in-sample base, recording what it *would* have chosen and what that costs on
  test) are free within-run legs. The second is the s4-B2 sign-inversion
  measurement transplanted to a second family at zero GPU.
- **Mandatory controls in the same JSON** (s6-B1 part-7 round-wide rule, D5):
  `lsi_alone`, `dc_raw` (corrector-alone on the raw residual = s6-B2's
  `circ_repair` reproduced inside this family, doubling as validity gate V1),
  `dc_cleaned` (corrector-alone on the cleaned residual), and
  `router_forced_wrong` (the router forced to the branch the rho rule says
  loses) — the rule's own information-content control.

## Proposal

- **Category**: `mf_composition / per-dataset discrete super learner over a
  2-element library (closed-form LSI branch vs corrector-on-LSI-cleaned-residual),
  library membership set by test-time LF availability, with OOF selection at
  every stage and a per-sample no-harm layer`
- **Card type**: `model`

### Motivation (quotes the prior-art verdict)

D1, verbatim from `websearches/s4_hybrid_routing/batch_3/report.md`:

> **D1 — per-dataset ROUTER: LF-defect-correction wherever the test split ships
> an LF fidelity, champion transfer path only where it does not (`ifc_poisson`),
> each branch OOF-gated** | **`preempted-but-MF-composition-open (cite)`** | ...
> The **selection rule is not open** (discrete super learner) and
> **availability-keyed gating is not open** (missing-modality MoE). Open: no
> fetched source routes on **fidelity availability inside a multi-fidelity PDE
> surrogate**, and none routes between a **defect-correction** path and a
> **transfer-learning** path. **Claim zero novelty for the router.** The card's
> contribution is the composition + its controls; the honest framing is "the
> discrete super learner applied per dataset over a 2-element library, where
> library membership is itself determined by a data property (does the test
> split ship LF?)".

D3, verbatim (the card's novelty leg):

> **D3 — change the TARGET: train the corrector on the node-aligned / LSI-cleaned
> residual (fitted linear pre-stage -> neural residual on what it leaves), with
> LSI-alone and corrector-alone controls in the same JSON** | **`preempted-but-
> MF-composition-open (cite)`** — **the card's strongest open surface** | ... In
> **every** fetched source the pre-stage is a *fixed classical solver*, a
> *learned* deconvolution layer, or a *scalar/affine* fidelity correlation.
> **Nobody fits a |k|-dependent LSI transfer function to the fidelity gap and
> then trains a corrector on ITS residual**, and nobody reports the
> zero-parameter filter as a scored floor beside the trained model.

D2, verbatim (why the gate arm carries a measurement and not a panel claim):

> **D2 — OOF-gate EVERY stage** ... | **`preempted (cite)`** — outright | ...
> Only the **measurement**: the published artifact is an *inflated validation
> score* of order 10-20 %, whereas B2 measured a **16.4x** optimism ratio and a
> **sign inversion of the keep/discard decision on 5/5 cells** ... No fetched
> source states that validation-selected shrinkage can flip a *decision*'s sign.
> The card cites the estimator and claims only the number.

D5, verbatim (why four of five arms are controls):

> **D5 — mandatory LSI-alone + corrector-alone controls** | **`preempted (cite)`**
> as methodology; the *practice of reporting them* is what is open | ... **no
> fetched MF source reports a zero-parameter fitted-filter floor next to its
> trained model** ... The transferable output is the *reporting standard*.

### Concrete config

New family `models_r1/s4_router`, vendored byte-verified from
`models_r1/s6_local_repair` @ `caff5c97d7365c2c200daa30f67c6db3b627aee0`
(branch `round1/exp-s6_local-B2`), sha256-pinned per file before any edit. All
`S6_*` knob semantics are preserved; the arm table is re-pointed at a new
`S4R_ARM` and the following are added:

1. `S4R_TARGET=lsi_cleaned` — fit the closed-form `T(k)` on the **train** split
   only (existing `lsi_filter.py`, `S6_LSI_RIDGE=0`), form `C_LSI`, and train the
   local corrector on `R - C_LSI` instead of `R`; the forward becomes
   `y_hat = LF_up + C_LSI + A * G * Delta`. `S4R_TARGET=raw` is the existing
   behaviour and is the D3 control.
2. `S4R_ROUTER_DECIDER=oof_val_risk` — per dataset, evaluate both library
   members on the held-out slice (`S6_GATE_HOLDOUT_FRAC=0.2`) that neither was
   fitted on, and select the lower-risk member; `S4R_SELECTOR_TIEBAND=floor`
   prefers the zero-parameter LSI branch when the two val risks are within the
   dataset's certified relative floor. `rule_inverted` (forced-wrong control)
   and `off` (branch-alone arms) are the other settings. The rho rule is
   **always** computed and recorded (`S4R_RULE_STAT=one_minus_rho_lsi_val`,
   `S4R_RULE_THRESH=0.15`) as a prediction, never as the decision.
3. `S4R_HEAD=on` with `S4R_HEAD_WEIGHTING=relative_l2` (CHANGE 1) and
   `S4R_HEAD_NOHARM_CAP=floor` (CHANGE 2), all other head knobs inherited
   unchanged from s6-B2 including the own-correction band-fraction features.
4. `S4R_BORROW_FROM` — `borrow_partner_stages` reused verbatim so `router` and
   `router_forced_wrong` load the donor arm's trained corrector rather than
   retraining (s6-B2 measured this at 1.22 min/panel-leg vs 20.42 trained).
5. Free sidecars: `S4R_OOF_SCREEN=1`, `S4R_INSAMPLE_COUNTERFACTUAL=1`,
   `S4R_NOSEL_LEG=1`, `S4R_BRANCH_ORACLE_SIDECAR=1` (test-fitted CEILING, never
   a score), `S4R_BOUNDARY_SPLIT=1` (interior-16 crop + `crop_sign_flip` on every
   reported contrast), `S4R_CORRECTED_REF_SIDECAR=C,D` (registration-corrected
   reference beside the frozen scored number; sidecar only, never a score).

**Arms** (all reported; primary per clause fixed here, pre-submit, per ADR 0007's
guardrail — and this is a spec-pre-scoped synthesis slot, which ADR 0007 exempts
from screen-and-promote; the contract screen is plumbing + no-harm only and is
never quoted in parts 5-7):

| tag | branch / target | selector | head | trained? | role |
|---|---|---|---|---|---|
| `lsi_alone` | LSI, closed form | off | off | no (0 gradient steps) | mandatory D5 control + validity gate V2 |
| `dc_raw` | DC on raw `R` | off | off | **YES** | D3 control + validity gate V1 (must reproduce s6-B2 `circ_repair`) |
| `dc_cleaned` | DC on `R - C_LSI` | off | off | **YES** | D3 novelty leg (corrector-alone on the cleaned target) |
| `router` | availability -> {LSI, DC-cleaned} | `oof_val_risk` | on | no (borrows `dc_cleaned`) | **PRIMARY** for the NO-HARM claim and the rule table |
| `router_forced_wrong` | rule-inverted branch | `rule_inverted` | on | no (borrows `dc_cleaned`) | the rule's information-content control |

Datasets: `panel` (6) for all five arms; `guard` (3) at 200 epochs for all five
arms (report-only — §2.3). `ifc_poisson` runs the champion fallback in every arm
(pre-registered no-op, no claim).

### Recipe

```json
{
  "base_family": "s6_local_repair",
  "base_commit": "caff5c97d7365c2c200daa30f67c6db3b627aee0",
  "family_dir": "models_r1/s4_router",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
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
      {"tag": "lsi_alone", "role": "mandatory zero-parameter floor (D5) + validity gate V2", "datasets": "panel,guard",
       "S4R_ARM": "lsi_alone", "S4R_ROUTER_DECIDER": "off", "S4R_TARGET": "raw", "S4R_HEAD": "off",
       "S4R_BORROW_FROM": "", "S6_VARIANT": "lsi_ctrl", "S6_SELECTOR": "heldout_scalar"},
      {"tag": "dc_raw", "role": "corrector-alone on the RAW residual: the D3 control and validity gate V1", "datasets": "panel,guard",
       "S4R_ARM": "dc_raw", "S4R_ROUTER_DECIDER": "off", "S4R_TARGET": "raw", "S4R_HEAD": "off",
       "S4R_BORROW_FROM": "", "S6_VARIANT": "local_pixel_gate", "S6_SELECTOR": "heldout_scalar"},
      {"tag": "dc_cleaned", "role": "corrector-alone on the LSI-CLEANED residual: the D3 novelty leg; donor for both router arms", "datasets": "panel,guard",
       "S4R_ARM": "dc_cleaned", "S4R_ROUTER_DECIDER": "off", "S4R_TARGET": "lsi_cleaned", "S4R_HEAD": "off",
       "S4R_BORROW_FROM": "", "S6_VARIANT": "local_pixel_gate", "S6_SELECTOR": "heldout_scalar"},
      {"tag": "router", "role": "PRIMARY: discrete super learner over {lsi, dc_cleaned}, availability-keyed library, + repaired per-sample no-harm head", "datasets": "panel,guard",
       "S4R_ARM": "router", "S4R_ROUTER_DECIDER": "oof_val_risk", "S4R_TARGET": "lsi_cleaned", "S4R_HEAD": "on",
       "S4R_BORROW_FROM": "dc_cleaned", "S6_VARIANT": "local_pixel_gate", "S6_SELECTOR": "oof_persample_head"},
      {"tag": "router_forced_wrong", "role": "rule information-content control: forced to the branch the rho rule says LOSES", "datasets": "panel,guard",
       "S4R_ARM": "router_forced_wrong", "S4R_ROUTER_DECIDER": "rule_inverted", "S4R_TARGET": "lsi_cleaned", "S4R_HEAD": "on",
       "S4R_BORROW_FROM": "dc_cleaned", "S6_VARIANT": "local_pixel_gate", "S6_SELECTOR": "oof_persample_head"}
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

### Expected outcome

Every contrast below is a **within-dataset ratio between two arms**, so the
frozen (registration-inflated) copy-LF denominator cancels exactly — the card's
claims are denominator-invariant by construction. Absolute skills and the panel
geomean are reported but carry **no claim**.

1. **NO-HARM (primary, panel).** For each of the four sharp panel datasets,
   `nRMSE(router) <= min(nRMSE(lsi_alone), nRMSE(dc_cleaned)) x (1 + floor_d)`
   with `floor_d = 10.000 %` on all four. Predicted realised branch: LSI on pfc /
   allen_cahn / cahn_hilliard, DC on fisher_kpp. `ext__helmholtz_2d`
   report-only (floor 70.165 %; both branches collapse to alpha = 0 = copy-LF,
   and the repaired head is the only thing that can move it — s6-B2 measured
   -29.009 %, unclaimable). `ifc_poisson` is the availability leg: predicted
   equal to the champion path to within 1e-6 relative (s6-B2 measured 1.5453
   +/- 0.0002 skill across five arms), **no claim**, and s6-B1's `alpha = 0` on
   6/6 predicts the transfer branch contributes nothing.
2. **Panel geomean**: predicted in [0.165, 0.200] (reference points: s6-B2
   `lsi_ctrl` 0.19722, `circ_repair` 0.19258, `trust_head_circ` 0.18759) versus
   the stream anchor 6.703016. **This is explicitly NOT the card's claim**: it
   is inherited from the s6/DC lineage, and s2-B2 showed the beyond-copy win is
   registration repair (correction-intersect-registration 0.975-0.9987). The
   router-vs-branch-oracle gap is predicted at **+8.6 %**, inside the 13.183 %
   geomean floor, i.e. predicted unmeasurable.
3. **Routing rule (mechanistic).** Predicted branch per dataset from
   `1 - rho_LSI(val) >= 0.15` (values from s6-B2 F5); the realized best branch is
   counted only where the branch gap is **resolvable** (exceeds the dataset's
   certified relative floor; guard cells have no floor and are counted only when
   the gap exceeds 2x, which all three do at 3.1x/11.7x/17.0x):

   | dataset | 1 - rho_LSI(val) | rule predicts | predicted realized best | agree? |
   |---|---|---|---|---|
   | `fluid` (guard) | 0.51943 | DC | DC (3.1x) | agree |
   | `sharp__sod_1d` (guard) | 0.25016 | DC | DC (17.0x) | agree |
   | `heat_local` (guard) | 0.18007 | DC | DC (11.7x) | agree |
   | `sharp__cahn_hilliard` | 0.10017 | LSI | tie (+7.2 % < 10.000 % floor) | untestable |
   | `sharp__fisher_kpp_2d` | 0.01575 | LSI | **DC (-38.95 %)** | **DISAGREE (known, predicted to reproduce)** |
   | `sharp__allen_cahn_2d` | 0.00342 | LSI | LSI (+12.6 %) | agree |
   | `sharp__phase_field_crystal_2d` | 0.00018 | LSI | LSI (+17.6 %) | agree |

   Pre-registered: **exactly 1 disagreement (fisher_kpp)** among 6 testable
   cells, and Spearman(1 - rho_LSI(val), realized DC/LSI test ratio) over all 7
   datasets stays at or below **-0.714** (s6-B2 measured -0.857, p = 0.0137).
4. **D3 (the novelty leg).** `dc_cleaned` vs `dc_raw`:
   - **Guard set, report-only** (§2.3: not part of the objective; no entry in
     `state/noise_floor.json`, hence no certified floor and no claim):
     predicted **positive on >= 2 of 3**, magnitude 0-15 % relative, because
     s6-B2 measured cos(C_NN - C_LSI, R - C_LSI) = 0.9984 / 0.9960 / 0.9441 on
     sod_1d / heat_local / fluid — the trained surplus already points along the
     cleaned target.
   - **Panel, claimable on `sharp__fisher_kpp_2d`** (cos 0.767; the one panel
     dataset with a resolvable trained-model surplus, -38.95 % vs LSI): point
     prediction **-12 %** relative nRMSE vs `dc_raw`, band [-25 %, 0 %], against
     the **10.000 %** certified floor. A null here is an admissible
     pre-registered outcome and would confine D3's demonstrated value to the
     guard set.
   - **Panel NULL on pfc / allen_cahn / cahn_hilliard** (cos 0.763 / 0.274 /
     0.037 and `1 - rho_LSI <= 0.10`, so almost nothing survives the filter):
     predicted `|delta| < 10.000 %` on **>= 2 of 3**.
5. **OOF protocol (measurement only, no panel claim — D2's instruction).** The
   in-sample-selection counterfactual is predicted to choose a *different* branch
   or a materially larger alpha on **>= 1 of 6** panel datasets, with the
   screening ratio `val_base_oof / val_base_insample` above 2x wherever it does
   (s4-B2 measured 16.4x / 2.9x where its stage hurt and 0.82-1.09x where it did
   not). Reported as a protocol number; the panel move is *inside* the 0.884
   geomean floor by s4-B2's own measurement, so no panel claim is attached.
6. **Forced-wrong control.** `router_forced_wrong` is predicted resolvably worse
   than `router` on the three guard datasets (3.1x / 11.7x / 17.0x, report-only)
   and on `sharp__phase_field_crystal_2d` / `sharp__allen_cahn_2d`
   (+17.6 % / +12.6 %, both above the 10.000 % floor), and predicted *better* on
   `sharp__fisher_kpp_2d` — which is exactly the rule's known inversion, and is
   the honest way to show it.

### Expected falsification (one sentence)

The card is falsified if **any** of: (i) the router's test nRMSE exceeds the
better of its two branches by more than that dataset's certified relative floor
(10.000 % on each of `sharp__phase_field_crystal_2d`, `sharp__allen_cahn_2d`,
`sharp__fisher_kpp_2d`, `sharp__cahn_hilliard`) on **>= 1** of those four
datasets, or the `ifc_poisson` availability leg deviates from the champion path
by more than 1e-6 relative; (ii) the routing rule disagrees with the realized
best branch on **>= 3** of the resolvable cells (against exactly 1 predicted), or
Spearman(`1 - rho_LSI(val)`, realized DC/LSI ratio) over the 7 LF-bearing
datasets rises above **-0.714** (the n = 7, one-tailed alpha = 0.05 critical
value; s6-B2 measured -0.857, p = 0.0137); or (iii) the D3 leg inverts, i.e.
`dc_cleaned` is **worse** than `dc_raw` by more than 10.000 % on
`sharp__fisher_kpp_2d`, or the pre-registered panel NULL breaks with
`|dc_cleaned - dc_raw| > 10.000 %` on **>= 2** of {pfc, allen_cahn,
cahn_hilliard}, or the guard-set direction (report-only) is negative on all
three.

### Anchor reference

`null`. Per program.md §4.5 the own-stream anchor is implicit for a lever
stream; the operative numeric bars in this card are the in-batch controls
(`lsi_alone`, `dc_raw`) plus the certified per-dataset floors, and the stream
anchor 6.703016262587087 is quoted for context only.

## Status

- Slot **covered** — one `model` card, five arms, two trained.
- Reopen candidates: **none exist** (all 19 cards carry
  `reopen_candidate: false`); nothing to resolve.
- Immutables self-check: **pass (10/10)** — below.

## Immutables self-check (10 items, positive evidence each)

1. **Data read-only.** Every dataset is read through the vendored
   `data_adapters.load_mf_dataset` + `round1/eval/panel_data.copylf_prediction`
   exactly as s6-B2 did; `S6_LF_SOURCE=dataset_lf_fidelity` / `S6_LF_FID=max`
   pins the LF to the dataset's own highest real coarse solve (never a
   downsampled HF), no arm writes under `benchmark_42/**` or
   `factory_root/data/**`, and `N_hf` is untouched — the `ifc_poisson` leg is the
   unchanged champion fallback at N_hf = 5.
2. **Panel + guard fixed.** `datasets: panel` (the 6 in `project.yaml panel:`)
   and `--datasets guard` (the 3 in `guard_set:`); no dataset is added, removed,
   or promoted — Alt D (promoting guard to scored) was explicitly rejected above
   for this reason, and guard numbers are declared report-only.
3. **Eval layer / spec untouched.** The family *imports* `nrmse.py` and
   `panel_data.py` read-only (the same import pattern s6-B2 shipped) and every
   edit is confined to `models_r1/s4_router/`; `_source` states that
   `round1/eval/`, `tools/`, `project.yaml`, `program.md`, ADRs and subagent
   prompts are never written, and the promoted tools are **vendored with
   citation**, not imported or modified.
4. **One nRMSE definition.** The scored number comes only from
   `score_panel.py` -> `eval/nrmse.py` (`nrmse_def_hash` d3d0ade9... asserted in
   every JSON); the D3 change is to the **training target** (`R - C_LSI`), which
   §5 lists under "training loss is free", and the head's CHANGE 1 reweights a
   *fitting* objective, never the scored metric.
5. **Contract CLI fixed.** `smoke_eval.py` keeps the six-argument signature
   (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`) inherited
   byte-for-byte from s6-B2; every new knob is an env var and **all of them are
   listed in the recipe `env` block**, so they enter the cache key.
6. **Seeds and tier epochs fixed.** `seeds: [0]`, `epochs: 200` (smoke tier) for
   the sweep and `epochs: 2` (contract tier) for the screen; `submit_seeds_2_3.sh`
   is written parameterized but **not launched** (ADR 0004 strict single seed);
   no full-tier run is proposed.
7. **Guarded factory surfaces untouched.** The only write target is the worktree
   path `worktrees/s4_hybrid_routing/B3/models_r1/s4_router/` plus
   `scripts/`; `factory_root/{eval,baselines,references,scripts,data}`,
   `factory.md` and `mf_field/akash/**` are read-only inputs (the base family's
   `model.py` is a byte-identical *copy* of `mf_fno_transfer_film/model.py`
   @967562e, already vendored in the lineage).
8. **Checkpoint-resume implementable.** Inherited verbatim from s6-B2, which
   shipped it: `<ckpt_dir>/arm_<tag>/last.pt` mirrored to `<ckpt_dir>/last.pt`
   with a meta guard extended to `(arm, target, decider, head, variant,
   padding_mode, stage, epochs_target, grid, seed)`; the two borrowing arms
   resume by re-loading the donor checkpoint, and the sweep script is idempotent.
9. **Falsification thresholds exceed the noise floor (numbers quoted).** Clause
   (i) fires only at a harm **strictly greater than** the dataset's certified
   relative floor: pfc `1.1511 / 11.5110 = 10.000 %`, allen_cahn
   `1.6334 / 16.3341 = 10.000 %`, fisher_kpp `0.41774 / 4.17735 = 10.000 %`,
   cahn_hilliard `0.55335 / 5.53347 = 10.000 %`; the `ifc_poisson` leg is an
   identity check (1e-6) declared **no-claim**, and `ext__helmholtz_2d` (floor
   70.165 %) is declared **report-only** so no unfalsifiable claim is attached to
   it. Clause (iii) fires at `> 10.000 %` on the same certified floors. The
   guard legs, which have **no** entry in `state/noise_floor.json` and therefore
   no certifiable floor, carry **no** falsifying threshold — they are report-only
   demonstrations, stated as such. The panel geomean (floor 13.183 %) is
   explicitly not a claim, and the predicted router-vs-oracle gap (+8.6 %) is
   pre-registered as *inside* that floor.
10. **Not a pre-falsified lever.** Nearest §5 entry is **LF low-mode freezing
    (`mf_fno_spectral`: "worst on sharp, catastrophic on lid-cavity")**, which
    also touches the LF spectrum. The difference: `mf_fno_spectral` *froze* LF
    low modes inside the network's forward pass as an architectural constraint;
    this card fits a **full-band, train-fitted LSI transfer function `T(k)`** as
    an explicit, separately scored pre-stage whose residual is the corrector's
    target, with the filter reported as a zero-parameter floor beside the trained
    model — nothing is frozen, no band is cut (D4's textbook constraint: a fitted
    taper, never a hard cutoff), and the arm is falsifiable against its own
    `dc_raw` control. No other pre-falsified lever (WNO backbone swap, diffusion
    prior) is touched.
