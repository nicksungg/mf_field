# Summary so far — Stream `r2s3_lf_train_signal`, Batch 3

## 1. Websearch findings + prior-art verdict

Source: `websearches/r2s3_lf_train_signal/batch_3/report.md` (5 iterations, cap
hit; 14 WebSearch / 7 WebFetch calls).

The decisive row, verbatim from the `## Prior-art verdict` table:

> **P1** — panel-completion: matched, step/budget-matched ±LF contrast
> (`A0_nolf` vs `A1_lf_cov`) for a condition→field neural surrogate at
> N_hf = 5, all 6 panel datasets, per-dataset claimability vs certified
> `min_claimable_effect`, reported in copy-LF skill units | **preempted-but-MF-composition-open**
> — **supersedes batch 2's `novel` verdict for E5** | https://arxiv.org/html/2511.01830v1
> (fetched: fidelity-mix sweep 0→100% HF at fixed capacity + fixed budget vs a
> full-HF reference; coverage-beats-accuracy under tight budgets);
> https://arxiv.org/html/2408.17075v1 (fetched: MF vs "their tested
> single-fidelity counterparts" over 5 functional-output test cases);
> https://arxiv.org/html/2510.23111v1 (fetched: LF-trained emulator scored
> against the solver that produced its data);
> https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb (fetched: LF→HF
> transfer, order-of-magnitude gain at small data, no matched ablation) |
> (a) **condition-vector-only test input, LF strictly out of the prediction
> path**; (b) **N_hf ≈ 5**; (c) a **certified 3-seed claimability threshold**
> per dataset; (d) the **copy-the-LF-solve denominator**; (e) a panel spanning
> PDE families that **differ in condition completeness** (ADR r2-0003). The
> claim is the composition (a)+(d)+(e), not the ablation genre.

Other rows: **P2** (uncovered-conditions-pay) **preempted** — reportable as a
quantified neural instance only, never as a mechanism claim; **P3** (three-channel
taxonomy) preempted-but-composition-open, travels as vocabulary + instrument;
**P4** (amplitude-corrected null penalty) **preempted**, admissible as at most one
cheap ablation leg; **P5** (gated/adaptive LF weighting) **preempted**, a rebadge
risk. The `For the brainstormer` section states: "**The panel completion is
still the right card** … Frame the deliverable as the *regime-specific
composition*, not as a new mechanism", and item 6 requires per-dataset
falsification clauses worded "must beat X on EACH of …".

## 2. §12.3 conventions (program.md, verbatim)

> - **Question**: LF as training-only signal. Candidate mechanisms (spec §6):
>   distillation from an LF-consuming teacher (round-1 families in role §5.10b
>   — teacher at train, absent at test), LF-pretrain → HF-finetune, auxiliary
>   multi-fidelity losses (predict LF and HF jointly from condition).
> - **The stream has a mandatory declared baseline**: `mf_fno_transfer_film`
>   (factory zoo champion) IS LF-pretrain→HF-finetune from the condition
>   vector (verified 2026-07-31: its test input is `cond_by_fid` only; it runs
>   on the stripped view unmodified). Any r2s3 pretrain/finetune proposal must
>   either score it as the baseline arm or cite how it differs — an
>   undifferentiated re-proposal is a rebadge (reviewer FAIL, §5.10).
> - **revin_lf two-scaler finding** (r1 s5): exact at LF-pretrain, 3.1% proxy
>   at HF — normalization transfer across fidelities is a solved sub-problem;
>   reuse it, don't rediscover it.
> - **Nested-ladder degeneracy** (r1 report §6) directly constrains this
>   stream: with aligned/nested ladders, "multi-fidelity" training pairs
>   degenerate toward top-rung replication — LF-as-signal designs must state
>   what information the LF rungs add that the HF rung does not already
>   contain (spectral truncation structure, more samples at low rungs on
>   ifc_poisson: 70 lower-fidelity vs 5 HF).
> - The **unified normalization eligibility rule** (r1 s2, checks 0–6) governs
>   any per-sample normalization proposal; spread is not the decider.
> - Uses the existing 400 aligned samples only (§5.11).

Stream anchor (`state/anchors/r2s3_lf_train_signal.json`): best-floor panel
geomean **23.063616857615774**, `provisional: false`.

## 3. Within-stream prior cards

**B1** (`experiment_cards/r2s3_lf_train_signal/batch_1/B1.json`, complete,
`falsified`) — family `r2s3_rung_supervised`, multi-rung native-resolution
supervision. Delivered **−7.3497** skill units on ifc_poisson (LF hurt), while
its own linear probe showed the LF rows were worth **+3.2317** (affine channel
reaching 0.2427). Three priced defects: shared scaler (1772× HF-loss
deflation), unsupervised `|k|>4` band, null-direction gain 2.653× too large.
Its part 7 demanded the repaired arm B2 shipped, plus the guard that the affine
channel is ifc-specific (affine-LOO residual 0.2507–2.3141 on the other five).

**B2** (`.../batch_2/B2.json`, complete, `confirmed`, `proceed_to_seeds_1_2`) —
family `r2s3_null_supply`, 17 legs / 3 datasets / one 41.63 min h200 job (job
66185845). Headline numbers (seed 0, corrected denominators):

| dataset | `A0_nolf` | `A1_lf_cov` | `A2_lf_cov_null` (primary) | `A3_lf_paired` |
|---|---|---|---|---|
| ifc_poisson | 8.1344 | **2.1690** | 3.4550 | n/a (disjoint design) |
| cahn_hilliard draw 0/1/2 | 30.0783 / 27.2499 / 24.7591 | **12.6346** / — / — | 13.3425 / 13.1790 / 12.8294 | 30.9058 |
| fisher_kpp draw 0/1 | 16.9436 / 16.1862 | ≡ A2 (m=0) | 15.2500 / 15.4341 | n/a |

F1–F4 confirmed; F5 has a wording ambiguity and its fisher_kpp limb fails (no
arm beats `train_mean_n5` there — ADR r2-0003). Anomaly **M1**: the card's own
headline mechanism (the null-direction penalty) is **net harmful** wherever
active (ifc −1.2860 = 1.37× the certified floor; ch −0.7080 = 7.8×), so the
value-of-LF result is carried by the plain coverage arm `A1_lf_cov`. Part 6
measured the three-channel split (ifc 57–60% direction / ~40% row-space;
ch 68% / 40% / 23% level; fk 0 / small / 77% level). Part 7 `next_direction`
asks for a **measurement-completion** B3: (1) `A1` on ch draws 1–2, (2) a
coverage-audited extension to more panel datasets, (3) at most one optional A1′
amplitude leg — and explicitly authorises a close-on-B2 fallback.

## 4. Cross-stream cards touching this stream

- `r2s4_diag-B2` (complete, **falsified**): the *target-side* matched ±LF
  contrast — `T0` (condition-only) vs `T1` (condition-only + LF auxiliary
  head) at N_fit ∈ {20, 80, 320} on 5 datasets — found `|T1 − T0|` **inside**
  the operative threshold in 15/15 cells. LF as an auxiliary *target* buys
  nothing. Its input-side teacher advantage is large (e.g. pfc 36.363 → 0.384).
  Turf: r2s4 owns the accounting; this stream owns the coverage mechanism at
  N_hf = 5.
- `r2s4_diag-B3` (drafted): teacher-projection channel ledger (reachable vs
  unreachable privileged advantage). No overlap with a ±LF panel completion.
- `r2s1_direct-B2`: every fisher_kpp arm collapses to `dc_only` — corroborates
  the fk floor loss as a task property (B2 cross-stream note 3).

## 5. Reopen candidates

None. Every card in `experiment_cards/` carries `reopen_candidate: false`
(verified by reading all 9 card JSONs).

## 6. What is UNKNOWN

1. **Is the value of LF at N_hf = 5 an affine-rank phenomenon or a generic
   sampling phenomenon?** B2's positive results sit on the only two panel
   datasets with an affine coverage deficit. I ran the pre-flight B2's part 7
   demanded (`tools/design_coverage_audit.py`, 9 runs, outputs in the session
   scratchpad): at N_hf = 5 the null dimension is **m = 15** (cahn_hilliard,
   d = 19) and **m = 1** (ifc_poisson, d = 5), but **m = 0** for
   `sharp__fisher_kpp_2d`, `ext__helmholtz_2d`, `sharp__allen_cahn_2d` and
   `sharp__phase_field_crystal_2d` on all three draws (verdict
   `NO_DEFICIT_TO_FIX`, `m_reduction_full = 0`, 395 uncovered LF conditions per
   rung). So 4 of 6 panel datasets have **no affine coverage story at all** —
   yet fisher_kpp still showed a claimable +1.2228. Whether ac/pfc/helmholtz
   behave like fisher_kpp (small, level-only) or like cahn_hilliard (large) is
   unmeasured and is the single most informative unknown left in this stream.
2. **Does the effect survive the removal of the failed mechanism?** The clean
   `A0 − A1` contrast exists on exactly two legs (ifc; ch draw 0). Everything
   else in the round's positive ±LF evidence is `A0 − A2`, i.e. contaminated by
   a mechanism B2 itself measured as net-negative.
3. **Is there a panel-level value-of-LF number at all?** No card in the round
   has a 6-dataset matched ±LF contrast; a panel geomean has never been
   computed for either arm (B2's is 3-of-6 and explicitly not comparable).
4. **Training-free predictors of the effect.** The HF 5-row designs are wildly
   ill-conditioned (κ = 2.0–2.4 ch, 58.7 ifc, 14–25 pfc, 221–251 helmholtz,
   234–1175 ac, 50 382–78 566 fk), and κ ordering is **anti-correlated** with
   B2's measured effects (fk has the worst conditioning and the smallest
   effect). So conditioning is not the predictor; condition-explainable field
   variance probably is — untested.
5. **Whether the amplitude-corrected penalty (A1′) is worth a leg.** B2's own
   turn-3 numbers say the cahn_hilliard defect is *alignment* (Frobenius
   cos +0.2172), not amplitude (ratio 0.8861), which is what A1′ would correct.
6. **Reproducibility of B2's legs from a fresh worktree** — never checked; any
   cross-card pooling of draws depends on it.
