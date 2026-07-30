# summary_so_far — `s4_hybrid_routing`, batch 3 (ROUTER synthesis slot)

## What this stream now knows

`state/anchors/s4_hybrid_routing.json` certifies the champion panel geomean
**6.7030** (`mf_fno_transfer_film`, 3 seeds, `provisional: false`); per-dataset
`min_claimable_effect` from `state/noise_floor.json` (geomean floor 0.884; pfc
1.1511, allen_cahn 1.6334, fisher_kpp 0.41774, cahn_hilliard 0.55335,
ifc_poisson 0.23991, helmholtz 9.695 = report-only).

B1 priced routing itself and found no headroom (per-pixel gate -1.31/-6.18/-3.54%,
oracle per-sample gate <= 5.33% — all inside the floors). B2
(`experiment_cards/s4_hybrid_routing/batch_2/B2.json` parts 5-7 +
`worktrees/s4_hybrid_routing/B2/notes/handoff_experiment_mechanism_analyzer.md`)
converted the stream's question from "which mixer" to "which target":

1. **Stage-3 keep test sign-inverted on 5/5 kept cells** (claims +14...+85 % val,
   delivers -5...-28 % test) because stage 3 trains *and* scores against the
   in-sample base; the screening ratio `val_base_oof / val_base_insample` was
   16.4x on cahn_hilliard. Panel cost +0.3605 / +0.2892 skill units; resolvable
   on `sharp__cahn_hilliard` (+0.9317 vs floor 0.5533).
2. **The dense attention corrector is confined to `span(copylf - base)`**
   (cos with `copylf - base` 0.946-0.988; cos with `hf - copylf`
   0.028 / 0.106 / -0.218). Its ceiling is skill 1.0, and the free one-scalar
   control `base + a*(copylf - base)` degenerates to `a = 1` (= copy-LF).
3. **The fidelity gap is an operator, not a content problem**: on fisher_kpp it
   is a fixed |k|-dependent pi/2-phase resample that a 0-parameter LSI filter
   nails at cos 0.996, while arm C (given `hf - copylf` explicitly) recovers
   only cos 0.632 and injects phase-random top-band energy (cos 0.034,
   1.058x the needed energy).
4. **Spectral caveat**: pure re-registration removes 97.6 % of copy-LF error
   below 0.5 Nyquist and is **5.17x harmful above it** (cos 0.205); only the
   *fitted* LSI transfer function is clean in every band.

## What the other streams handed in (2026-07-30)

- `s6_local`-B1 part 6/7: the winning mechanism is **machine-learned Richardson
  defect correction on the real coarse solve** + a held-out scalar switch; a
  zero-parameter LSI filter beats the 72k ConvNeXt on 3/4 winners (F6), the
  optimal operator is compact (94-99 % energy in 12 cells, F15), and the
  held-out rho of an LF->R fit orders the panel with Spearman 1.000 (F14). Its
  part-7 item 7 **writes this card's charter**: "use LF-defect-correction on
  every dataset whose test split ships an LF fidelity ..., fall back to the
  champion path only where it does not (ifc_poisson) ... If the operator still
  wants the stacked form, it must include the LSI-filter control and the
  LF-corrector-alone control in the same card."
- `s3_warp`-B1 (`state/orchestrator_flow.md` 04:15Z): the sharp panel's copy-LF
  reference is **misregistered by (r-1)/2 cells** (cell-centred zoom on
  node-sampled data); node-aligned band-limited reference gives pfc 7.1e-06.
  Metric stays frozen this round; mentor note
  `docs/operator_notes/2026-07-30-benchmark-registration-note.md`.
- `s2_beyond_copy`-B2 (09:30/09:50Z): the beyond-copy win is ~100 %
  **re-learned registration** (pfc 2578x worse than the free fix, allen_cahn
  97.5 % by projection, fisher_kpp 95.9 %), plus a **global target-scaler**
  defect (helmholtz effective N = 1.2/400; pfc scaler 7.9e4x median per-sample
  scale). Standing rule: decompose with `tools/registration_skill_split.py`
  before reading any sharp-panel number.
- `s5_tuning`-B2 (10:10/10:45Z): z-score target normalization moves helmholtz
  and ifc_poisson only; the three sharp-2D nulls **held** — normalization is
  not the sharp-2D explanation, but it interacts with the amplitude machinery.
- `s6_local`-B2 landed 11:35Z with `validity_gates all_pass TRUE`; card part 5
  not yet written (status `running`) — the LSI control arm and the OOF
  per-sample trust head are its primaries.

## In-repo literature already searched (cite, don't re-derive)

`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` L266 already proposes
"train a small dictionary of correction operators ... and select/compose at eval
by minimizing LF-consistency" and L270/335 the ARC-STAR risk-routed block
refiner — i.e. the *within-field* routing idea is already on file.
`docs/reports/MF_Sharp_HighFreq_Report.md` supplies the Transolver slice-token
bottleneck note. Prior loops:
`websearches/s4_hybrid_routing/batch_2/report.md` (verdicts i/ii/iii:
gate repair `preempted`, dense context `preempted-but-open`, attention-vs-local
head-to-head `novel`) and `websearches/s6_local/batch_2/report.md` verdict (iv)
(held-out-fold gate = Wolpert 1992, cited through arXiv:1106.1684; the Super
Learner PDF **403'd** and Wolpert's own PDF **425'd** in that loop).

## Open questions this batch's search must answer

1. Is a **per-dataset router between a correction path and a transfer path,
   keyed on test-LF availability**, published anywhere in scientific ML?
2. What are the **canonical, fetchable** citations for the OOF gate
   (super learner / stacked generalization / DML cross-fitting) so the card
   cites rather than claims? (Both canonical PDFs failed in the s6 loop.)
3. Is "**corrector on an operator-cleaned residual**" (residual net on top of a
   fixed fitted linear/deconvolution pre-stage) published?
4. Is the **fitted-taper vs hard-cutoff** distinction in band-limited
   correction composition published?
5. Does any MF architecture **route on fidelity availability at inference**
   (some samples have LF, some do not)?
