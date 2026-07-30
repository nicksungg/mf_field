# Summary so far — Stream `s5_tuning`, Batch 3

Sources read in full: `websearches/s5_tuning/batch_3/report.md`;
`experiment_cards/s5_tuning/batch_2/B2.json` (parts 1–7 + `promotion`);
`worktrees/s5_tuning/B2/notes/handoff_experiment_mechanism_analyzer.md`;
`worktrees/s5_tuning/B2/notes/precheck_scale_ratio.{md,json}`;
`worktrees/s5_tuning/B2/models_r1/mf_fno_transfer_film_scaler/{smoke_eval.py,scalers.py}`;
`experiment_cards/s2_beyond_copy/batch_3/B3.json` (the DRAFTED twin);
`experiment_cards/s1_poisson/batch_3/B3.json` (parts 6–7);
`experiment_cards/s7_loss/batch_{1,2}/B*.json` (recipes);
`state/anchors/s5_tuning.json`; `state/noise_floor.json`; `program.md` §1–5, §9–13;
ADR 0002/0004/0007/0009.

## 1. Websearch findings + prior-art verdict

Five iterations, 15 WebSearch / 19 WebFetch (13 usable). Five verdict rows.

- **E1** — arm A3 `revin_lf` at 200 epochs (per-sample de-normalization of the **raw HF
  target** by `s_i = max|LF_i|`, a statistic of the **LF input field**, scaler-only, zero
  new parameters, across the LF-pretrain -> HF-finetune boundary): **preempted-but-MF-
  composition-open**. WNE proves the wrapper *is* the function class — *"a parameter-free
  wrapper that normalizes the input, applies any backbone, and denormalizes the output. We
  prove every NE function admits this factorization"* (https://arxiv.org/abs/2605.08193);
  MORPH already does normalize/denormalize inside a PDE surrogate (https://arxiv.org/html/2509.21670v3).
  What remains open: **(i)** the statistic comes from a **different fidelity's field**;
  **(ii)** it is applied to a **raw** (non-residual) target — the complement of s2-B3's D1;
  **(iii)** it is a **scaler-only knob** inside a few-HF-sample MF recipe; **(iv)** *"WNE's
  guarantee does not transfer"* — in denoising input and target share a space, across a
  fidelity boundary they do not. The 2024 MF functional-output survey is silent here
  (https://ar5iv.labs.arxiv.org/html/2408.17075); APEX is an operator + flow-matching
  enhancer, **not** a scaler (https://arxiv.org/abs/2605.26732).
- **E2** — LF-free per-sample scale `s_i = max|Y_i|`: **preempted (cite)**, and *"the only
  honest s5-legal form is an **oracle** arm"*. RevIN's statistics are the observed window's,
  *"available at inference"*; DAIN learns the scale and has *"no denormalization module"*
  (https://arxiv.org/html/2603.11869). A scale predictor is architecture and leaves s5.
- **E3** — H3 (was `grad_clip=1.0`, not the scaler, the robustifier?): **preempted (cite)**
  for the mechanism, **open** for the attribution measurement. Clipping *"is equivalent to a
  Huberised-like loss function"* (https://arxiv.org/html/2412.08941v4); the threshold is
  absorbed into the effective LR and *"cancels out"* under adaptive optimizers
  (https://ar5iv.labs.arxiv.org/html/2206.07136 — but for **per-sample** DP clipping, ours
  is whole-batch); a fetched head-to-head has clipping *"does not improve the performance"*
  vs normalization *"improves significantly"* (https://ar5iv.labs.arxiv.org/html/1707.06799).
  Unretrieved: anyone using **clip rate as the explanatory variable for a target-
  normalization result**. Both signs are pre-registrable as informative.
- **E4a** — effective N of the realized per-batch loss: formula **preempted**
  (`n_eff = 1/Sum_i alpha_i^2`, *"a diagnostic control signal"*,
  https://alex.smola.org/posts/40-effective-sample-size/), the **application open** — every
  retrieved use computes ESS from chosen sampling/importance weights, none from the realized
  per-sample energies of an **unweighted** MSE batch. *"Cite the formula, claim only the
  application."*
- **E4b** — eligibility rule `G = max|Y_train|/sd(Y_train) >= 8` gated on a live pattern
  channel: **novel (narrow)**; nearest neighbour is the qualitative version — instance norm
  *"on certain stationary datasets might be detrimental"* (https://arxiv.org/html/2603.11869).
  *"Do not overclaim G"*: present it as **a predictor under test**, not a contribution.
- Mandatory design warning (item 7): *"training via backpropagation in the normalized space
  yields better models ... even when evaluating with the non-normalized MSE"* — state the
  train-space/score-space mismatch rather than leaving it an unexamined confound.

## 2. §12 conventions verbatim

program.md **§12.5 `s5_tuning` (tuning)**:

> - **Anchor**: champion's certified panel geomean (batch 0); later batches
>   re-target the current champion card.
> - Audited knob findings to grind (from `docs/proposals/MODEL_TWEAKS*.md`):
>   **F22** `modes_cap = 12` never scales with resolution (12 of 128 modes at
>   256² — candidate M1 in MODELS_TO_TRY.md proposes 32); **F19** training loss
>   ≠ scored metric in 11 families; **F20** model-selection metric mismatch;
>   normalization choices.
> - Constraint: no new losses-as-mechanisms, no new paradigms, no architectural
>   changes — knobs on existing recipes only. Anything else belongs in another
>   stream.
> - G4's dry-run card (`s5_tuning-B1`, modes_cap 12→32 on the champion) is a
>   REAL batch-1 card for this stream.

program.md **§4.5** (anchors): *"**Every falsification threshold must exceed the noise floor
for its dataset(s).** A claimed effect smaller than the floor is unfalsifiable"*.
`state/anchors/s5_tuning.json`: `mf_fno_transfer_film`, panel geomean **6.703016**,
CI95 [6.218536, 7.102240], `provisional: false`.

## 3. Within-stream prior cards

**s5-B1** (`modes_cap` 12->32): `not_resolvable` on an unfixed basis; its part 7 named the
next knob — *"the leading candidate is the NORMALIZATION knob, not another capacity knob"*.
Left behind: an H100 same-hardware cap-12 seed-0 `maxabs` control (geomean 7.117102;
helmholtz 19.632686 / ifc_poisson 1.545309 / cahn_hilliard 5.562725 / fisher_kpp 4.116518).

**s5-B2** (`MFFP_TARGET_SCALER`, promoted arm A2 `zscore`, job 66056499, 32.03 min/panel on
H100), `status: complete`, falsification `confirmed` (clause did **not** fire).
Per-dataset seed-0 skills: helmholtz **5.766462** (nRMSE 1.899761), ifc_poisson **1.185106**
(0.042664), cahn_hilliard **5.457873** (0.478437), fisher_kpp **4.218984** (0.264245),
pfc 11.215708, allen_cahn 16.642709. Panel geomean 5.554668 (-1.148 vs anchor) but
leave-helmholtz-out delta 0.3287 < the 0.884 geomean floor => recorded as a **tail artefact**.
Only ifc_poisson cleared its floor (0.3805 > 0.2399, on all three bases).

Part 6 mechanism (15 findings), the load-bearing ones:
- **F1**: the "effective-N repair" story is **FALSIFIED** for a global scaler — helmholtz HF
  train effective N is **1.0145/400** (maxabs) vs **1.0179/400** (zscore); *"a global scalar
  divides every sample's energy by the same constant"*.
- **F5/F6**: the correct covariate is `G = max|Y|/sd = (max/rms) x (rms/sd)`, not `|mu|/sd`.
  Panel G: helmholtz 39.47, ifc_poisson 9.858, fisher_kpp 5.997, pfc 3.814, allen_cahn 2.537,
  cahn_hilliard 1.322. Break between 6.0 (nothing) and 9.9 (effect).
- **F7**: G needs a **live pattern channel**; fisher_kpp has G without pattern (LEVEL_ONLY),
  cahn_hilliard has pattern (corr 0.735) without G — both nulls.
- **F9/F11**: ifc_poisson's gain had **no** amplitude component; it was a uniform ~40% cut of
  error energy in the band carrying 99.88% of the signal.
- **SPECULATIVE H3**: *"Under maxabs the helmholtz loss is ~1/1558 of the zscore loss, so the
  clip almost certainly never binds ... If so, whatever robustification the outlier-dominated
  loss received came from the CLIPPER, not from the scaler ... is a B3 item."*

Part 7 `next_direction` (verbatim, abridged): *"arm A3 `revin_lf` ... already implemented and
ranked but never ran at 200 epochs ... plus a per-sample-normalized-MSE arm that needs no LF
... on the two datasets where target scaling is a lever at all (ext__helmholtz_2d,
ifc_poisson) plus one SCALER_INERT control. Pre-register `G ... (>= 8)` AND a live pattern
channel as the eligibility rule ... instrument the per-batch gradient norm and clip rate so
hypothesis H3 ... is settled in the same run ... report effective N of the realized per-batch
loss ... MERGE CANDIDATE: ... s5 owning the raw-target/LF-blind substrate and s2 owning the
residual-target/LF-consuming one."*

**Substrate fact that the pre-scope does not state** (read from
`notes/precheck_scale_ratio.json` and `smoke_eval.py:207-244`): `revin_lf_available` is
**false on ifc_poisson** — `N_lf = 100` vs `N_hf = 5` and **unaligned**, and the test split
ships fidelity 64 only. Arm A3 there is a **declared fallback**, i.e. a no-op. Also
`hf_lf_ratio_cv` <= 0.0173 on all four sharp sets, so `revin_lf` ~ a global `maxabs` there.
So `revin_lf` has real per-sample content on **exactly one** panel dataset: helmholtz
(cv 0.689, p95/p5 1.744, spread 3929x -> 1.74x).

## 4. Cross-stream cards

- **s2_beyond_copy-B3** (DRAFTED, builder running) — the residual-target / LF-consuming twin.
  Arm grammar to share: `A0 global_ctrl` (paired, same job, never promoted) / `A1`
  per-sample candidate (pinned rank 1) / `A3 ref_oracle_truescale` (ORACLE, `ref_*` split,
  never promotable) / `A5 persample_nofloor` (screen-only). Knob namespace `S2B3_*`. Its
  recipe carries **`"sbatch": "TBD: brainstormer did not specify"`** — the defect this report
  must not repeat.
- **s1_poisson-B3** (complete) — the ifc_poisson double-count. Part 7 note (1) verbatim:
  *"SAME AXIS, not two levers ... level rel-err s5 maxabs 0.024773 -> zscore 0.011486 with
  pattern-only 0.090870 -> 0.090934 (unchanged); s1 base 0.024023 -> head 0.008792 with
  pattern-only 0.058118 -> 0.052198. The round report must NOT count them as two stackable
  ifc_poisson levers"*. Note (2): *"Porting the B3 head to `mf_fno_transfer_film` would be
  worth at most 0.0027 nRMSE there = 0.31x the floor - not a batch."* Best ifc_poisson number
  in the round is s1-B3 `self_only__none` **0.021913** (skill 0.608694, below the paper bar).
- **s7_loss-B2** (`reviewed_pass`, seed-0 running, job 66064289) — `MFFP_S7_LOSS=rel` on the
  **same** champion family: the per-sample **loss-weighting** half of this intervention with
  the output space unchanged. s5-B3 must not duplicate it; it is the natural comparator.
- **s7_loss-B1 M6** — denominator-floor design rule for per-sample normalization (the risk of
  up-weighting near-zero-scale samples by `1/s_i^2`).

## 5. Reopen candidates

**None.** Every s5 card is terminal-complete with `reopen_candidate: false`
(`s5_tuning-B1`, `s5_tuning-B2`); no skipped slot exists in this stream.

## 6. What is UNKNOWN

1. **Can anything de-concentrate the realized loss, and does it buy score?** B2 proved a
   global scalar cannot (1.0145 -> 1.0179 of 400). A **per-sample** scale must, arithmetically.
   Nobody has measured whether the repaired loss changes the score. Both outcomes are
   decisive: repair-with-no-gain retires "fix the loss concentration" for this substrate;
   repair-with-gain hands s7/s2 a confirmed lever.
2. **H3 — was it the clipper?** Completely unmeasured. No clip-rate number exists anywhere in
   the round. E3 supplies fetched support for **both** signs.
3. **Does `max|LF_i|` transfer as an HF scale proxy across a fidelity boundary?** WNE's
   equivalence holds because denoising's input and target share a space; ours do not. B2
   measured the residual spread (3929x -> 1.74x on helmholtz) but never trained on it.
4. **Is the ifc_poisson per-sample branch alive at all?** Bounded from one side only: the
   post-hoc per-sample gain oracle on the s5 zscore arm is worth 0.042664 -> 0.039985 =
   **0.31x the floor** (s1-B3 T3-F2). A *trained* per-sample normalization is a different
   function and is unbounded by that number. Unknown.
5. **Does the `G >= 8 AND live-pattern` rule predict?** It was fitted post-hoc on n = 6, single
   seed, two movers. It has never made an out-of-sample prediction. cahn_hilliard
   (pattern-without-G) and fisher_kpp (G-without-pattern) are the two informative cells.
6. **How much of any gain is train-space/score-space realignment rather than representation?**
   (2603.11869). Unseparated anywhere in the round.
7. **Attribution ceiling on helmholtz**: A0's skill is 5.766462 and the floor is 9.694961 —
   `5.766462 - 9.694961 = -3.928500 < 0`, so **no attainable helmholtz skill can ever clear
   its own floor**. Whether that dataset can carry any claim at all in round 1 is settled:
   it cannot. What it *can* carry is diagnostics.
8. **Displacement noise floor (H4)** — still uncalibrated; two same-arm seeds would close it,
   but ADR 0004 forbids a second in-round seed.
