# Websearch Report — Stream `r2s3_lf_train_signal`, Batch 3

**Stream**: `r2s3_lf_train_signal` (lever — "how much does LF, available only
during training, help a condition→HF model?")
**Batch**: 3
**Total iterations**: 5 (cap 5 — **CAP HIT**, noted in `iteration_5.md`)
**WebSearch calls**: 14 (turns 1–4: 3 each; turn 5: 2)
**WebFetch calls**: 7 (all usable; **no `/pdf/` arXiv URL was ever fetched** —
`/abs/` and `/html/` only, per the round's process rule)
**Cap hit**: yes (5/5)

## Search trace

### Turn 1 — the coverage explanation and the panel-scale measurement
Terms: nested-vs-non-nested MF design (where "LF at uncovered parameter
locations" would live); benchmark-scale ±LF ablation for neural operators;
LF augmentation / bias correction with few HF samples. Chosen because B2's
part 5 M5 makes **design coverage** the active ingredient and part 7 asks B3
to scale the ±LF contrast from 3 to 6 panel datasets.
- Non-nested MF designs are standard; "data augmentation procedure that samples
  the missing low-fidelity responses" [search return:
  https://www.sciencedirect.com/science/article/abs/pii/S2352012425024324].
- Plasma-edge neural operator surrogates: "Transfer learning significantly
  reduced errors for small dataset sizes … an order-of-magnitude reduction when
  transferring from low- to high-fidelity datasets", but **field inputs** and
  **no matched ±LF ablation** [cite (fetched):
  https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb].
- **Emulator superiority**: emulators trained **purely on LF** can beat that
  solver against a better reference; authors distinguish this from work that
  "mixed low-fidelity data with high-fidelity data" [cite (fetched):
  https://arxiv.org/html/2510.23111v1].
- Engine stated it "did not find a single study that exactly matches" the ±LF
  ablation query. → `iteration_1.md`

### Turn 2 — subspace decomposition, negative transfer, penalty calibration
Terms: row-space/null-space decomposition of transfer gain; negative transfer
with LF data; calibrating a penalty toward a biased LF-estimated target.
- The row/null decomposition is generic and published across domains
  [https://arxiv.org/html/2510.15337 (fetched in batch 2, top hit again);
  search returns https://arxiv.org/pdf/2506.04244, https://arxiv.org/pdf/2507.02248].
- "LF can hurt" is the named phenomenon **negative transfer**, with a standard
  gating/adaptive-weighting remedy family [search returns:
  https://hal.science/hal-04602579/document,
  https://www.sciencedirect.com/science/article/pii/S0021999124002018,
  https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X;
  cite (fetched, thin abstract): https://arxiv.org/abs/2002.04495].
- LF/HF **scale-factor** calibration inside a penalized objective is standard
  bi-fidelity practice [search return:
  https://link.springer.com/article/10.1007/s00158-024-03887-8].
- Flagged https://arxiv.org/abs/2511.01830 (fetched; abstract too thin) as the
  most dangerous preemption → deferred body read. → `iteration_2.md`

### Turn 3 — reading the two dangerous preemptions
Terms: MF scaling laws / equivalent-sample accounting; replicated vs distinct
design points; multi-PDE-family fidelity-mix ablation.
- **MF scaling laws (fetched body)**: fidelity composition swept 0→100% HF at
  fixed ~4M-param capacity and fixed budget, with a "trained on the full
  high-fidelity dataset" reference; "under tight compute constraints, the
  broader coverage of the data manifold offered by many low-fidelity samples
  outweighs the higher accuracy of a few high-fidelity ones"; **one CFD family,
  field inputs, error units, no minimum-HF regime, no noise floor**
  [cite (fetched): https://arxiv.org/html/2511.01830v1].
- **MF survey+benchmark for functional outputs (fetched; batch 2 could only
  cite its existence)**: mapping approaches need "the same number n of high-
  and low-fidelity … snapshots (corresponding to the same input variable
  vectors)"; corrective approaches are limited so "the surrogate may not take
  full advantage of the multi-fidelity context"; fusion allows "n₁≠n₂"; the
  benchmark spans **five test cases** and finds "most multi-fidelity surrogates
  outperform their tested single-fidelity counterparts"
  [cite (fetched): https://arxiv.org/html/2408.17075v1]. → `iteration_3.md`

### Turn 4 — refutation pass on the exact round-2 regime
Terms: LF only at training with no LF solve at inference; beating the coarse
solver itself; rank/coverage as a predictor of auxiliary-data value.
- **MARIO** predicts full fields with "no CFD solves at inference time" from
  parametric inputs, but its cheap training data is "significantly downsampled
  meshes" — **downsampled HF, not a coarse consistent solve** (the project's
  own methodology rule rejects that as LF) — and there is **no MF value
  ablation** [cite (fetched): https://arxiv.org/abs/2505.14704].
- Nothing retrieved uses a **copy-the-LF-solution denominator** for a
  condition-only surrogate.
- Rank/coverage as a training-free predictor of auxiliary-data value:
  **No usable results.** → `iteration_4.md`

### Turn 5 — channel attribution, deployment framing, verdict (cap hit)
Terms: attribution of MF benefit (variance reduction vs new information);
solver-free deployment from historical simulation data.
- The established attribution is the **control-variate/variance-reduction**
  account of MF *estimators*, not of learned operators [search returns:
  https://arxiv.org/pdf/1806.10761,
  https://www.sciencedirect.com/science/article/abs/pii/S0925231224007343,
  https://kiwi.oden.utexas.edu/research/multi-fidelity-uncertainty-quantification].
- "LF at training, no solver at inference" as a named regime: **No usable
  results** (patents/vendor docs only) — third independent miss.
  → `iteration_5.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched/returned) | What remains open |
|---|---|---|---|
| **P1** — panel-completion: matched, step/budget-matched ±LF contrast (`A0_nolf` vs `A1_lf_cov`) for a condition→field neural surrogate at N_hf = 5, all 6 panel datasets, per-dataset claimability vs certified `min_claimable_effect`, reported in copy-LF skill units | **preempted-but-MF-composition-open** — **supersedes batch 2's `novel` verdict for E5** | https://arxiv.org/html/2511.01830v1 (fetched: fidelity-mix sweep 0→100% HF at fixed capacity + fixed budget vs a full-HF reference; coverage-beats-accuracy under tight budgets); https://arxiv.org/html/2408.17075v1 (fetched: MF vs "their tested single-fidelity counterparts" over 5 functional-output test cases); https://arxiv.org/html/2510.23111v1 (fetched: LF-trained emulator scored against the solver that produced its data); https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb (fetched: LF→HF transfer, order-of-magnitude gain at small data, no matched ablation) | (a) **condition-vector-only test input, LF strictly out of the prediction path** (the three preemptors are field-in emulators or keep LF in the pipeline); (b) **N_hf ≈ 5**; (c) a **certified 3-seed claimability threshold** per dataset; (d) the **copy-the-LF-solve denominator** — "is the model worth more than running the coarse solver"; (e) a panel spanning PDE families that **differ in condition completeness** (ADR r2-0003). The claim is the composition (a)+(d)+(e), not the ablation genre. |
| **P2** — the coverage result: LF at conditions with no HF row is what pays; LF replicated at the 5 HF conditions does not (B2 M5) | **preempted** | https://arxiv.org/html/2408.17075v1 (fetched: mapping needs snapshots at "the same input variable vectors"; corrective is limited by the HF snapshot count so the surrogate "may not take full advantage of the multi-fidelity context"; fusion allows n₁≠n₂); https://arxiv.org/abs/2511.20183 (fetched batch 2: non-nested MF-GP); search returns https://www.sciencedirect.com/science/article/abs/pii/S2352012425024324, https://www.sciencedirect.com/science/article/abs/pii/S1474034625009693 | Only the quantified **neural** instance: a fully nested (paired) LF pool being *actively harmful* (−0.83 skill units = 9.1× threshold) for a condition→field network on a multistable PDE. Report as measurement with these citations; never card as mechanism. |
| **P3** — three-channel taxonomy (direction supply / row-space fit / level-amplitude) + `tools/null_family_ceiling_audit.py` as reporting instrument | **preempted-but-MF-composition-open** | https://arxiv.org/html/2510.15337 (fetched batch 2; row-space vs null-space split, source info transferred into the null space); search returns https://arxiv.org/pdf/2506.04244, https://arxiv.org/pdf/2507.02248 (same split elsewhere); https://arxiv.org/pdf/1806.10761 (control-variate/variance-reduction account of MF benefit) | The **three-way** split adding a level/amplitude channel, and **measured shares** for a PDE field surrogate (ifc 57–60/~40/n.a.; ch 68/40/23; fk 0/small/77). Vocabulary + instrument, not theory. |
| **P4** — optional leg: amplitude-corrected null-direction penalty (A1′ on `sharp__cahn_hilliard`) | **preempted** | https://arxiv.org/html/2510.01608 and https://iopscience.iop.org/article/10.1088/1361-6420/aaf14a (batch 2 iter 3: null-space-targeted regularization); https://link.springer.com/article/10.1007/s00158-024-03887-8 (search return: LF/HF scale factor inside penalty minimization) | Nothing at mechanism level. Admissible only as one cheap ablation leg closing B2's `open_question`; the mechanism already measured net-negative (B2 M1), so a retune sits close to the pre-falsified-lever line (program.md §5). |
| **P5** — alternative mechanism: gated / adaptively weighted LF loss to avoid negative transfer | **preempted** | https://arxiv.org/abs/2002.04495 (fetched abstract; engine synthesis: LF transfer can give "less accurate surrogates compared to when the network is trained based only on large high-fidelity datasets"); search returns https://hal.science/hal-04602579/document (LOL-GP per-location gate), https://www.sciencedirect.com/science/article/pii/S0021999124002018, https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X (Ada2MF); with batch 2's https://arxiv.org/abs/2403.08118 | Nothing. Gating is mandatory engineering at best; a card claiming it is a rebadge risk under §5.10. |

## Citations summary

- [Setinek et al. 2025] "Towards Multi-Fidelity Scaling Laws of Neural Surrogates in CFD" — https://arxiv.org/html/2511.01830v1 (abs: https://arxiv.org/abs/2511.01830) — used in: iteration_2 (term 2, /abs/ fetched), iteration_3 (term 1, /html/ body fetched), P1 verdict.
- [—] "A survey on multi-fidelity surrogates for simulators with functional outputs: unified framework and benchmark" — https://arxiv.org/html/2408.17075v1 — used in: iteration_3 (terms 2–3, fetched), iteration_4 (term 2, engine synthesis), P1/P2 verdicts.
- [—] "Neural Emulator Superiority: When Machine Learning for PDEs Surpasses its Training Data" — https://arxiv.org/html/2510.23111v1 — used in: iteration_1 (term 2, fetched), iteration_4 (term 2), P1 verdict.
- [—] "Neural operator surrogate models of plasma edge simulations: feasibility and data efficiency" (Nucl. Fusion) — https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb — used in: iteration_1 (term 2, fetched), P1 verdict.
- [Catanach/… — MARIO] "Towards scalable surrogate models based on Neural Fields for large scale aerodynamic simulations" — https://arxiv.org/abs/2505.14704 — used in: iteration_4 (term 1, fetched), P1 verdict (nearest neighbour on the no-solve-at-inference axis; its cheap data is downsampled, not a coarse consistent solve).
- [—] "On transfer learning of neural networks using bi-fidelity data" — https://arxiv.org/abs/2002.04495 — used in: iteration_2 (term 2, fetched abstract; the negative-transfer sentence is an **engine synthesis, flagged as a search return**), P5 verdict.
- [2025] "Transfer Learning for Benign Overfitting in High-Dimensional Linear Regression" — https://arxiv.org/html/2510.15337 — fetched in `websearches/r2s3_lf_train_signal/batch_2/iteration_1.md`; re-surfaced as a search return in this batch's iteration_2 (term 1); P3 verdict.
- [2025] "Bayesian hierarchical surrogate model for reliability analysis under nested and non-nested multi-fidelity data" — https://www.sciencedirect.com/science/article/abs/pii/S2352012425024324 — used in: iteration_1 (term 1, search return), P2 verdict.
- [2025] "A novel low-fidelity-guided design of experiments for multi-fidelity surrogate modeling" — https://www.sciencedirect.com/science/article/abs/pii/S1474034625009693 — used in: iteration_3 (term 2, search return), P2 verdict.
- [2024] "Bi-fidelity surrogate modeling via scaled correlation construction and penalty minimization" — https://link.springer.com/article/10.1007/s00158-024-03887-8 — used in: iteration_2 (term 3, search return), P4 verdict.
- [Peherstorfer, Willcox & Gunzburger] "Survey of multifidelity methods in uncertainty propagation, inference, and optimization" — https://arxiv.org/pdf/1806.10761 — used in: iteration_5 (term 1, **search return only, never fetched**), P3 verdict.
- [—] "Multi-fidelity reinforcement learning with control variates" — https://www.sciencedirect.com/science/article/abs/pii/S0925231224007343 — used in: iteration_5 (term 1, search return).
- [—] Multi-fidelity UQ overview (Oden Institute) — https://kiwi.oden.utexas.edu/research/multi-fidelity-uncertainty-quantification — used in: iteration_5 (term 1, search return).
- [—] "A multi-fidelity transfer learning strategy based on multi-channel fusion" — https://www.sciencedirect.com/science/article/pii/S0021999124002018 — used in: iteration_2 (term 2, search return), P5 verdict.
- [—] "Ensemble adaptive gated multi-fidelity neural network …" (Ada2MF) — https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X — used in: iteration_2 (term 2, search return), P5 verdict.
- [—] "Adaptivity and uncertainty of multi-fidelity surrogate models" (LOL-GP) — https://hal.science/hal-04602579/document — used in: iteration_2 (term 2, search return; also batch 2 iteration 5), P5 verdict.
- [—] PEFT / matrix-completion instances of the row/null decomposition — https://arxiv.org/pdf/2506.04244, https://arxiv.org/pdf/2507.02248, https://arxiv.org/html/2503.00174v1 — used in: iteration_2 (term 1, search returns), P3 verdict.
- [—] MF-PINN with Bayesian UQ + adaptive residual learning — https://arxiv.org/html/2602.01176v1 — used in: iteration_1 (term 3, search return; physics-residual arm out of scope per r1 ADR 0009).
- Carried from prior loops (cited, not re-derived): batch 2's fetched
  https://arxiv.org/abs/2511.20183, https://arxiv.org/abs/2403.08118,
  https://arxiv.org/html/2510.01608,
  https://iopscience.iop.org/article/10.1088/1361-6420/aaf14a,
  https://arxiv.org/abs/1705.02956; batch 1's D1/D2 rows; in-repo
  `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` (line 46:
  `mf_fno_transfer_film` = LF-pretrain → HF-finetune, the stream's mandatory
  declared baseline).

## Dead ends

- `parameter space coverage rank deficient design predicts when auxiliary training data helps surrogate few samples` → engine explicitly reported no match; the rank/coverage predictor remains unretrieved as a *feature*, but it lives inside the preempted gating framework (batch 2 E4).
- `no solver available at deployment predict simulation field from design parameters using historical simulation database …` → patents and vendor docs only; the round's deployment framing is not a named academic regime (third independent miss).
- `benchmark study value of low-fidelity data ablation across multiple PDE datasets …` → the engine stated no exact match; the closest objects were found only by the *scaling-law* and *functional-output survey* framings in turns 2–3, which is why those two now carry the P1 verdict.
- Standard PDE benchmark suites (PDEBench / PDEArena / APEBench / The Well) carry no LF-ablation axis in any retrieved description.

## For the brainstormer

The brainstormer MUST quote the prior-art verdict above for whatever it proposes.

1. **Batch 2's `novel` verdict for the measurement (E5) no longer holds.** Any
   B3 card must quote **P1 `preempted-but-MF-composition-open`** and name the
   five open items verbatim — especially (a) condition-vector-only test input
   with genuine coarse consistent solves used only at train, (d) the
   copy-LF skill denominator, and (e) the condition-completeness-varying panel.
   The ±LF-ablation genre itself is published
   (https://arxiv.org/html/2511.01830v1, https://arxiv.org/html/2408.17075v1).
2. **Do not card the coverage story as a finding (P2, preempted).** "LF
   replicated at the HF design points wastes the MF context" is stated
   explicitly in the fetched survey. What B3 may report is the *quantified
   harm* in a neural condition→field setting, with the citation attached.
3. **The panel completion is still the right card** — it is the only route to
   a 6-dataset value-of-LF statement (3 of 6 today), it directly serves round-2
   success criterion 1, and B2 part 7 prices legs (1)+(2) at ≈1.5 h of H200
   time. Frame the deliverable as the *regime-specific composition*, not as a
   new mechanism.
4. **Do not propose a new LF-weighting/gating mechanism (P5, preempted)** and
   keep the amplitude-corrected penalty (P4, preempted) to at most one cheap
   ablation leg that closes B2's `open_question` — its mechanism already
   measured net-negative (B2 M1, −1.286 ifc / −0.708 ch).
5. **The three-channel taxonomy (P3) may travel as vocabulary + instrument
   only**, citing https://arxiv.org/html/2510.15337 for the row/null split and
   https://arxiv.org/pdf/1806.10761 for the variance-reduction channel; the
   open part is the third (level/amplitude) channel and the measured shares.
6. **Per-dataset falsification clauses, priced against
   `state/noise_floor.json`** (ifc 0.9377041, ch 0.0912454, fk 0.0007137,
   ac 0.8797047, pfc 0.2130273, helmholtz 2.9529916; panel geomean 1.1418668)
   — B2's F5 wording ambiguity is the cautionary tale; write "must beat X on
   EACH of …", never "on both".
7. **Standing caveats to carry on any new panel row**: helmholtz is
   report-only (best floor = the zero field, 3.3441); pfc claims carry the
   band-limited-denominator caveat; allen_cahn/fisher_kpp/pfc have incomplete
   condition vectors (ADR r2-0003), so a conditional-mean floor bounds every
   deterministic arm there — B2 already lost that floor on fisher_kpp with and
   without LF, and a 6-dataset sweep will meet it again on allen_cahn and pfc.
