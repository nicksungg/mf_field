# Summary so far — `s4_hybrid_routing`, Batch 3 (ROUND SYNTHESIS / ROUTER)

## 1. Websearch findings + prior-art verdict

Source: `round1/websearches/s4_hybrid_routing/batch_3/report.md` (5 iterations,
cap hit; 15 searches, 12 usable fetches, 4 recorded fetch failures).

Five directions were priced. Verdict cells (full citations in the report):

- **D1 — per-dataset ROUTER** -> **`preempted-but-MF-composition-open (cite)`**.
  *"The **selection rule is not open** (discrete super learner) and
  **availability-keyed gating is not open** (missing-modality MoE). Open: no
  fetched source routes on **fidelity availability inside a multi-fidelity PDE
  surrogate**, and none routes between a **defect-correction** path and a
  **transfer-learning** path. **Claim zero novelty for the router.**"* The
  mandated framing: *"the discrete super learner applied per dataset over a
  2-element library, where library membership is itself determined by a data
  property (does the test split ship LF?)"*.
- **D2 — OOF-gate EVERY stage** -> **`preempted (cite)` — outright**.
  *"Only the **measurement**"* is claimable: cross-fitting is
  https://arxiv.org/abs/1608.00060 (*"K-fold sample splitting, which we call
  cross-fitting"*); the published artifact is a 10-20 % inflated validation
  score, while s4-B2 measured **16.4x** optimism and a **sign inversion of the
  keep/discard decision on 5/5 cells**. Explicit instruction: *"do NOT
  pre-register a panel claim for the gate arm"*.
- **D3 — change the TARGET (corrector on the fitted-LSI-cleaned residual)** ->
  **`preempted-but-MF-composition-open (cite)` — the card's strongest open
  surface**. *"Nobody fits a |k|-dependent LSI transfer function to the fidelity
  gap and then trains a corrector on ITS residual, and nobody reports the
  zero-parameter filter as a scored floor beside the trained model."*
- **D4 — fitted taper vs hard cutoff** -> **`preempted (cite)` — textbook,
  twice; nothing open.** *"Present as an inherited design constraint, never as a
  finding."*
- **D5 — mandatory LSI-alone + corrector-alone controls** -> **`preempted (cite)`
  as methodology; the practice of reporting them is what is open.**

Directives in the report's "For the brainstormer" section: claim zero novelty
for the router and for the OOF gate; build the card around the D3 TARGET and
pre-register it *"against the **LSI-alone** number, not against copy-LF"*;
expect the transfer branch to contribute nothing (s6-B1 recorded `alpha = 0` on
**6/6** on a champion-generated base); and the honest predicted gain is *"no
dataset is worse than the better of its two branches"*, a **no-harm** claim,
*"with every threshold above the per-dataset `min_claimable_effect` (pfc 1.1511,
allen_cahn 1.6334, fisher_kpp 0.41774, cahn_hilliard 0.55335, ifc_poisson
0.23991; geomean 0.884; helmholtz report-only)"*.

## 2. program.md §12.4 conventions (verbatim)

> ### 12.4 `s4_hybrid_routing` (lever)
>
> - **Anchor**: champion's certified panel geomean (batch 0).
> - Quantified prior: the FNO<->Transolver **pairwise oracle is +30.6%** over FNO
>   alone (Transolver wins 16/38 despite being 2x worse on average).
>   `mf_field/akash/models/fno_transolver_seq` (sequential FNO->Transolver
>   residual hybrid) is BUILT but unbenchmarked — batch 1 should start by
>   scoring it on the panel (cheap, mostly evaluation).
> - The surviving novelty is the **MF composition** (routing, per-band/per-region
>   gating, which fidelity feeds which expert) — the base hybrids themselves are
>   published (WLNO, Park 2507.06133, SINO; see §5 pre-falsified list and the
>   prior-art reports).
> - Transolver-side caveat: `transolver_residual` is best-in-zoo on 4 of the 5
>   beyond-copy datasets — whatever routing is learned should preserve its
>   behavior there.

Also load-bearing, program.md §2.3 verbatim (it governs what a guard number may
claim):

> **Guard set** (`heat_local`, `fluid`, `sharp__sod_1d`): not part of the
> objective. Run at contract tier for any experiment claiming a panel win; a
> guard regression > 2x vs its recorded reference flags the card in part 5 (the
> analyzer interprets; no auto-reject).

**Reading**: guard datasets are *not part of the objective* and carry no entry
in `state/noise_floor.json` (that file holds exactly the 6 panel datasets).
Therefore **no guard number can carry a falsifiable claim in this round** — no
certified floor exists to clear. Guard legs are report-only demonstrations, and
the no-harm primary must live on the panel. Stated explicitly in the card.

Anchor: `state/anchors/s4_hybrid_routing.json` — champion `mf_fno_transfer_film`
panel geomean skill **6.703016262587087** (3-seed, batch 0, `provisional: false`).

Per-dataset certified floors (`state/noise_floor.json`, `min_claimable_effect`
in skill units -> relative % = effect / certified mean skill):
helmholtz 9.6950 / 13.8173 = **70.165 %**; pfc 1.1511 / 11.5110 = **10.000 %**;
allen_cahn 1.6334 / 16.3341 = **10.000 %**; fisher_kpp 0.41774 / 4.17735 =
**10.000 %**; cahn_hilliard 0.55335 / 5.53347 = **10.000 %**; ifc_poisson
0.23991 / 1.56563 = **15.323 %**; geomean 0.8837 / 6.7030 = **13.183 %**.

## 3. Within-stream prior cards

- **`s4_hybrid_routing-B1`** (`experiment_cards/s4_hybrid_routing/batch_1/B1.json`,
  complete): scored the built-but-unbenchmarked `fno_transolver_seq` on the
  panel and priced routing headroom — **F11: oracle per-sample gate <= 5.3 %,
  honest per-pixel gate NEGATIVE on 2 of 3** (quoted in B2's part-7 handoff).
  Routing-as-mixer is therefore already priced as small.
- **`s4_hybrid_routing-B2`** (`.../batch_2/B2.json`, complete; family
  `models_r1/fno_transolver_seq_b2` @ `4691d1f`): three arms
  (`gate_repair`, `gate_repair_dense`, `attn_gap_fkpp`). Part 7 / handoff
  (`worktrees/s4_hybrid_routing/B2/notes/handoff_experiment_mechanism_analyzer.md`)
  gives B3 three ordered directives:
  1. **OOF-gate every stage.** Stage 3 kept on 5/12 cells; on 5/5 the keep test
     is sign-inverted (claims +14...+85 % val, delivers -5...-28 % test); panel
     cost **+0.3605 / +0.2892** skill units, *"inside the 0.884 geomean floor,
     resolvable on `sharp__cahn_hilliard` (+0.9317 / +0.6216 vs floor 0.5533)"*.
     Two-line fix known; the no-stage-3 counterfactual is *"a free within-run
     leg"*; screening statistic `val_rel_l2_base_oof / val_rel_l2_base_insample`
     = 16.4x / 2.9x where the stage hurt, 0.82-1.09x where it never fired.
  2. **Change the TARGET, not the mixer** — hand the corrector the operator:
     *"a node-aligned / registered base, or an explicit LSI stage whose residual
     the network then corrects"*, band-limited/taper-fitted because *"a pure
     re-registration is clean below 0.5 Nyquist ... and 5.17x HARMFUL above it"*.
  3. **Do not spend batch-3 GPU on the attention corrector's capacity,
     bandwidth or gate** — C3's failure is a *phase* failure (top band cos 0.034
     at 1.058x the needed energy), present in both branches, independent of
     chunking. Ride-along plumbing fix (permute queries before chunking) only
     *if* that family is touched.

## 4. Cross-stream cards that attack this stream's constraints

- **`s6_local-B1`** (complete). Part 7 item 7 is written *to this card*: it
  licenses the LF-consuming corrector and the identity/no-harm gate, and
  **contradicts** investing in the champion as stage 1 wherever a real LF field
  exists: *"The defensible synthesis is therefore a ROUTER, not a stack: use
  LF-defect-correction on every dataset whose test split ships an LF fidelity ...
  fall back to the champion path only where it does not (ifc_poisson ...)"*, and
  *"If the operator still wants the stacked form, it must include the LSI-filter
  control and the LF-corrector-alone control in the same card, or its geomean
  will be uninterpretable."* Item 4: the identical held-out-alpha machinery chose
  **alpha = 0 on all six datasets** on a champion-generated base. F6: the
  zero-parameter filter beats the 72k ConvNeXt on pfc 2.19x, allen_cahn 1.56x,
  cahn_hilliard 1.07x.
- **`s6_local-B2`** (complete, family `models_r1/s6_local_repair` @ `caff5c9`;
  handoff `worktrees/s6_local/B2/notes/handoff_experiment_mechanism_analyzer.md`).
  The three ROUTER ingredients: (a) the training-free eligibility statistic
  **1 - rho_LSI(val) >= 0.15** (Spearman -0.857, p = 0.0137, n = 7), decided
  *before a gradient step*; (b) D3 licensed **dataset-conditionally**
  (cos(C_NN - C_LSI, R - C_LSI) = 0.9984 / 0.9960 / 0.9441 on
  sod_1d / heat_local / fluid vs 0.767 / 0.763 / 0.274 / 0.037 on
  fisher_kpp / pfc / allen_cahn / cahn_hilliard); (c) the **trust-head reuse
  spec** — keep OOF ridge on standardized features, `{persample_head,
  global_scalar, zero}` CV selection, exact alpha_hat = 0 fallback, the
  own-correction band fractions (67-83 % of weight mass), and
  `borrow_partner_stages` (which *"made this entire characterization cost ~0
  GPU"*); **CHANGE 1** weight the alpha-regression by the scored metric
  (w^2 = (||C_i||/||Y_i||)^2); **CHANGE 2** a per-sample no-harm cap (35/100
  helmholtz, 27/100 pfc currently end worse). Also: *"do NOT bill the padding
  repair as a router branch"* (one-cell rim, 7.1x/7.4x over-concentration).
  Measured panel geomeans (seed 0): `lsi_ctrl` 0.19722, `circ_repair` 0.19258,
  `trust_head_circ` 0.18759; the trained-vs-closed-form panel surplus is
  **-2.355 %**, *inside* the 13.183 % geomean floor. Guard: trained beats LSI
  11.7x / 3.1x / 17.0x.
- **`s3_warp-B1`** + **`s2_beyond_copy-B2`** (both complete; orchestrator_flow
  2026-07-30T04:15Z and T09:30/09:50Z): the sharp-panel copy-LF denominators are
  **registration-inflated 2.0-8.6x** (`copylf_prediction`'s cell-centred zoom on
  node-sampled data -> a fixed (r-1)/2-cell misregistration); the beyond-copy win
  is **registration repair, not physics** (correction-intersect-registration
  0.975-0.9987; node-aligned geomean 10.31 vs free-fix 0.0369). The metric stays
  frozen for the round; the standing rule is that batch-3 clauses pre-register
  against corrected references, not `copylf_baselines.json`.
- **`s7_loss-B2`** (stream CLOSED, 2026-07-30T16:15Z): exports the
  **amplitude-calibration remedy** — p25-median denominator floor +
  inference-time per-sample amplitude calibration; *"60 % of damage is the
  amplitude channel"*. Same axis as trust-head CHANGE 1.

## 5. Reopen candidates

**None.** A scan of all 19 cards in `experiment_cards/*/batch_*/B*.json` returns
`reopen_candidate: false` on every card (the only non-`complete`/`built` status
is `s3_testtime-B1 retired_by_operator`, which is not a reopen candidate).

## 6. What is UNKNOWN

1. **Does an honest per-dataset selector actually realise the branch oracle?**
   Everything so far measures *branch* numbers; nothing in the round has run a
   selector over them and reported whether the selected branch is the
   test-better branch. s4-B1's F11 priced *per-sample* mixing at <= 5.3 %; the
   per-*dataset* selection question is untouched, and it is the one whose payoff
   (fisher_kpp DC -38.95 % vs pfc/allen_cahn LSI +17.6/+12.6 %) is resolvable.
2. **Does the `1 - rho_LSI >= 0.15` rule survive contact with a second family and
   a changed target?** It was fitted post hoc on seven (dataset, NN/LSI-ratio)
   pairs from one family at one seed. Its single known inversion is
   `sharp__fisher_kpp_2d` (rule says LSI, truth says DC by 38.95 %) — the exact
   dataset s6-B1 flagged as *"the one panel dataset whose PDE defect involves a
   local nonlinearity"*. Nobody has asked whether the rule predicts the
   **selector's** choice as well as it predicts the test outcome.
3. **Is D3 worth anything where it is claimable?** The cosine measurement says
   the network's surplus points along the LSI residual on the guard set
   (0.944-0.998) — which carries no claim (§2.3) — and only 0.767 / 0.763 on
   fisher_kpp / pfc, ~0 on cahn_hilliard. So D3's *demonstrable* value and D3's
   *claimable* value may sit on disjoint datasets. Unknown: does handing the
   corrector `R - C_LSI` instead of `R` change anything resolvably on
   fisher_kpp, the one panel dataset with resolvable trained-model content?
4. **Does s4-B2's 5/5 selection sign-inversion reproduce in a different
   family?** The 16.4x optimism was measured on one staged family. Whether an
   in-sample-selected version of *this* card's selector would also invert its
   decision is free to measure (both bases already exist on the val slice) and
   would turn a one-family anomaly into a protocol finding.
5. **Can the repaired trust head clear any floor?** s6-B2 captured 59 % of the
   per-sample oracle on helmholtz — whose floor is 70.165 %, so it is
   unclaimable there by construction. Which dataset has both per-sample spread
   *and* a clearable floor is unknown; the answer decides whether CHANGE 1 +
   CHANGE 2 can ever be demonstrated rather than argued.
6. **What does no-harm cost?** A conservative selector that never loses may also
   never win. Unknown whether the router's panel geomean equals the branch
   oracle's or sits measurably above it (my arithmetic in `iteration_1.md`
   predicts +8.7 %, *inside* the 13.183 % floor — i.e. predicted to be
   unmeasurable, which is itself a pre-registrable statement).
7. **How much of any panel number is registration?** With the frozen inflated
   denominators, an absolute panel geomean from this card is uninterpretable as
   a physics claim. Unknown until stated: which of the card's contrasts are
   denominator-invariant. (They are: every branch-vs-branch and router-vs-branch
   ratio is taken within one dataset, so the copy-LF denominator cancels
   exactly. That is the design's escape hatch and it must be said out loud.)
