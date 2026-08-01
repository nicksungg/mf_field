# Summary so far — Stream `r2s2_stacked`, Batch 3

Sources read (never guessed): `websearches/r2s2_stacked/batch_3/report.md`;
`experiment_cards/r2s2_stacked/batch_{1,2}/B{1,2}.json`;
`brainstormer/r2s2_stacked/batch_2/report.md`; `program.md` §1–§5, §12, §13;
`state/anchors/{r2s2_stacked,floors}.json`; `state/noise_floor.json`;
`state/orchestrator_flow.md` (tail); `index.md`;
`tools/{zero_gradient_stage_ladder,relative_gain_units_audit,target_scale_spread_audit}.py` headers.

## 1. Websearch findings + prior-art verdict

`websearches/r2s2_stacked/batch_3/report.md` (5/5 iterations, cap hit; 15 WebSearch calls,
13 Bash-`urllib`/`curl` GETs after `WebFetch` was found disabled) returns three verdicts:

- **(i)** Promote `k-NN average of the train LF pool at calib-selected k* -> one closed-form LSI
  Wiener filter` from diagnostic to a first-class **SCORED** panel arm —
  `preempted-but-MF-composition-open (cite)`. Open: *"No fetched source composes retrieval
  intermediate -> one fitted LSI Fourier-diagonal transfer as a multi-fidelity corrector, scores it
  under a copy-LF-skill denominator with no LF at test, or reports the attribution ... Claim the
  composition + attribution, never the filter"*.
- **(ii)** Re-run allen_cahn's gated-CNN increment at the 1+2-seed protocol — `preempted (cite)`
  *as a method*; the answer on this panel is open. Two inherited design constraints: vary the
  **fold/train seed**, not only the corrector init (https://arxiv.org/abs/2510.26714), and
  pre-register against the certified `min_claimable_effect`, never a paired p-value
  (https://arxiv.org/abs/2511.19794 — *"with only three seeds, our paired protocol never declares
  significance in these settings"*).
- **(iii)** Close on B2 and export the filter as the zero-parameter bar — `preempted (cite)` *as a
  framing* (https://arxiv.org/abs/2508.05831 already offers closed-form optimal linear maps as the
  SciML benchmarking baseline); open only as **artefact + measurement in the round's claim unit**.

Mandatory engagement: **Operator Boosting** (https://arxiv.org/abs/2606.17460) — stagewise tiny
residual correctors over a cheap base, *"incorporates each correction through validation-selected
shrinkage"* — is structurally B2's `alpha_nn` line search over a k-NN-mean base and must be named
and differentiated. **The genuinely unpublished item is the negative**: two refutation terms found
*no* MF/PDE result where a learned corrector is switched off out-of-fold while a closed-form stage
carries the gain; every returned ablation credits the learned stage. The websearcher's design
instruction: *"If B3 is scored, design it so that this negative is identifiable per dataset
(LSI-only arm, LSI+CNN arm, same folds, same k*)"*.

## 2. `program.md` §12.2 conventions (verbatim)

> ### 12.2 `r2s2_stacked` (lever)
>
> - **B1 is pre-directed by the spec** (Eloise's stacking proposal): train a FiLM-FNO **pseudo-LF emulator** (condition → LF field) on the TRAIN LF data, feed the best round-1 corrector — the s6 DC lineage / s4-B3 `dc_cleaned` stage (r1 geomean 0.1233–0.19 under OLD denominators; restate under corrected before claiming). Arms: **frozen corrector / fine-tuned corrector / end-to-end**, to separate emulator error from distribution shift (the corrector was trained on real LF; pseudo-LF is off-distribution for it).
> - Declared-reuse rule (§5.10a): the corrector is a frozen test-time sub-component — the reuse IS the experiment. Its code lives in the round-1 worktrees (`round1/worktrees/s6_local/B2`, `round1/worktrees/ s4_hybrid_routing/B3/models_r1/s4_router/`); vendor the needed pieces into the round-2 family dir with provenance comments (round-1 branches are immutable).
> - Round-1 mechanism rules apply to the cleaning stage: **BC-match rule** (eligibility decidable training-free; audit tool `tools/spectral_prestage_bc_audit.py`), the **wrap-seam caveat** (part of dc_cleaned's pfc credit was a boundary-rim artifact of the DEFECTIVE reference — under the corrected reference that credit may vanish; the s4-B3 H4 finding says deep-bulk ratio was 0.908 on pfc), and the **lineage-bound caveat** for any routing/eligibility rule.
> - Failure is informative: if pseudo-LF → corrector loses to r2s1's direct models, the LF representation is not a useful bottleneck — that is the stream's falsification framing.

Also binding (§12 common, ADR r2-0004): **registration of model-side lifts** (vendor the ADR
r2-0001 interpolators; a bare `F.interpolate`/`zoom` is a reviewer FAIL) and **target-scaler
pre-flight** on `ext__helmholtz_2d` / `sharp__phase_field_crystal_2d`.

## 3. Within-stream prior cards

**`r2s2_stacked-B1`** (model, complete): FiLM-FNO pseudo-LF emulator + frozen/fine-tuned/end-to-end
round-1 corrector. Panel geomean **14.0756** (single seed; *"~all margin from the unpaired
`ifc_poisson` column"*). Clean negative with mechanism (I8): *"a stacked intermediate representation
is a re-parameterisation of the condition→HF hypothesis class, not a new information channel"*.
Promoted `reachable_set_rank_audit.py`, `surrogate_coherence_eligibility.py`. Part 7 open question:
can any *realisation-aware* stage 1 clear the 0.52–0.95 coherence band, or is the class dead.

**`r2s2_stacked-B2`** (diagnostic, complete): correctability calibration + DPI closure. Scored
`test_hf` geomean **19.3868** (single seed) vs anchor 23.0636 (−3.677, beyond panel mce 1.1419 but
not anchor-certifying: single-seed diagnostic). Verdict **falsified**, but all three fired clauses
traced to *its own instrument defects* (uncentred coherence statistic; estimator bias against a
DPI-zero truth; endpoint comparison on a k-axis with an interior optimum). Substantive results:

- **H-STAGE**: the condition-only stacked class collapses to a **zero-gradient two-step recipe** —
  average the real train LF solves of the k nearest conditions, then one closed-form
  spatially-invariant Wiener filter fitted on the fit fold.
- **T3/F3.3 attribution** of the scored arm's test gain (LSI / CNN / blend %): pfc 100/0/0,
  cahn_hilliard 97.0/3.0/0.0, fisher_kpp 77.1/22.9/0.0, allen_cahn 32.5/49.1/18.4. In skill units
  CNN = 9.443 (ac) / 0.081 (ch) / 0.000 (pfc) / 0.019 (fisher).
- `alpha_nn = 0.0` out-of-fold on **5 of 8** rung cells — the CNN switched itself off.
- **H-RULE-UNITS**: B1's coherence eligibility gate is retracted (STOP-EXPORT); dimensionless
  thresholds mis-price decisions by 10–817x mce. Ladder rule: never build a rung that is LOO on
  train and no-self on test (`B:all` corrupted three of four clauses).
- k* (fold seed 0): pfc 16, allen_cahn 16, fisher_kpp 64, cahn_hilliard 16, ifc 2, helmholtz 1.
- Wall clock 33.58 min (panel, H200) + 2.4 min (guard, contract tier).
- Promoted `zero_gradient_stage_ladder.py`, `relative_gain_units_audit.py`.

Part 7 open question (verbatim): *"Is there ANY residual on this panel that a nonlinear /
spatially adaptive corrector can remove OUT OF FOLD once the closed-form LSI Wiener stage has been
applied at the calib-selected k*, or is `k-NN average of the train LF pool -> one closed-form Wiener
filter` simply the ceiling of the condition-only stacked class? ... the entire out-of-fold case for a
TRAINED corrector rests on ONE dataset (allen_cahn: gated CNN 9.443 skill units, 49.1 % of the
scored gain) at ONE fold seed and ONE fit."*

## 4. Cross-stream cards (light scan)

- **`r2s1_direct-B2`** (model, complete): panel geomean **18.3622** (single seed, no falsification
  weight). Independently found a post-hoc-blend-stage instrument-error class and a
  decorrelation-payoff law — the same defect family B2 found. Its number is the live comparison for
  §12.2's framing ("if the stacked route loses to r2s1's direct models, the LF representation is not
  a useful bottleneck").
- **`r2s1_direct-B1`**: a ~156-parameter closed-form head matched a 15.9M-parameter decoder
  (0.52x panel mce) — an independent, cross-stream confirmation that closed-form stages carry the
  value in this regime.
- **`r2s4_diag-B2`**: aux-LF-TARGET head worth nothing at any N (15/15 cells) — certified null;
  explicitly does **not** license "LF doesn't help" (input-side + disjoint-supply channels untouched).
- **`r2s3_lf_train_signal-B2`**: LF at uncovered conditions is a coverage-of-design effect.

## 5. Reopen candidates

**None.** `grep -rl '"reopen_candidate": true' experiment_cards/` returns nothing round-wide;
`r2s2_stacked-B1` and `-B2` both carry `reopen_candidate: false` (verified by reading both cards).
Nothing to retry or drop.

## 6. What is UNKNOWN

1. **Does allen_cahn's 9.443-skill-unit gated-CNN increment survive fold/train-seed variation?**
   This single number, at one fold seed and one fit, is the whole out-of-fold case for a trained
   stage in this class. Its certified resolution constant is 0.8797 skill units, so the measured
   effect is 10.7x mce — large enough that fit noise alone is an unlikely explanation, yet the
   *fold* was never varied, and B2's own `alpha_nn` line search rejected the CNN on 5/8 cells.
   2510.26714 says exactly this: extra downstream seeds cannot substitute for training-seed
   variation. Unknown, and one run answers it.
2. **Is the closed-form stage or the LF-derived intermediate what carries the class?** B2 attributed
   *within* the stack (LSI vs CNN vs blend) but never swapped the **base**: nobody has run the same
   corrector, same folds, same budget over a training-free (no-LF) base. Until that is done, "the
   composition works" is untested against Operator Boosting's own recipe (cheap base + trained
   stages + validation-selected shrinkage), which the websearcher names as the closest prior art.
   This swap is also a matched ±LF-intermediate contrast at equal corrector budget — the stream's
   own §12.2 falsification framing, measured in-job instead of across single-seed cards.
3. **Is there a first-class SCORED zero-gradient panel arm anywhere in this round?** No. B2's
   19.3868 came from a *diagnostic* card with a CNN and a blend stage bolted on; the zero-gradient
   recipe itself has never been scored as a model. Direction (iii)'s export needs the artefact and
   the numbers in skill units against the certified mce — that is a run, not a desk note.
4. **How stable is k\*?** B2 emitted k* from fold seed 0 only (reviewer carry-forward 2); every
   k*-conditioned claim currently carries a stability proxy rather than a measurement.
5. **What does the class cost relative to r2s1's direct route?** Predicted A1 ~ 19.6 vs r2s1-B2's
   18.36 — a 1.26-skill-unit gap, 1.10x the panel mce, i.e. right at the edge of claimable. Whether
   the stacked route is *worse* than direct condition→HF is unresolved and single-seed cross-card
   comparison cannot resolve it.
6. **Unknowable in this round**: whether any of this transfers off this panel; whether a genuinely
   realisation-aware stage 1 exists (B1 part 7 option A — the stripped view exposes only the
   condition, so no admissible stage 1 conditions on anything E[LF|c] lacks; ceiling ~1.6 skill
   units, dropped by B2's brainstormer for stated reasons).
