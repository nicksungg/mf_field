# Brainstormer summary-so-far — Stream `s3_warp`, Batch 2

## 1. Websearch findings + prior-art verdict

Source: `websearches/s3_warp/batch_2/report.md` (5 iterations, 15 WebSearch /
13 WebFetch of which 8 usable), read in full.

Verdict rows, verbatim from the report's `## Prior-art verdict` table:

- **(i)** "Narrow **cahn_hilliard-only warp-then-correct** model: a one-sided
  displacement head predicts a smooth low-mode `phi` from LF + condition,
  single-interpolation warp of the RAW LF onto the HF node grid, then a small
  learned correction; comparators = warp-off control, constant-displacement
  arm, registration-corrected copy-LF sidecar" ->
  **`preempted-but-MF-composition-open`**; open part: "The **one-sided**
  instance: displacement predicted from the LF PDE field + condition vector
  with **no target field at inference**, applied to that field before a
  learned correction, inside an MF operator surrogate at small N_hf.
  Registration is pairwise; mesh-movement nets output nodes not fields;
  MF/SR fusion is value-space. Every *component* ... is published -- the claim
  is composition + measurement, on ONE dataset (floor 0.553)."
- **(ii)** single-interpolation warp composition -> **`preempted (cite)`**,
  JUBW = Makansi/Ilg/Brox `arXiv:1707.00471`; "What remains open: **Nothing.**
  ... an implementation obligation to cite, never a contribution."
- **(iii)** warp-vs-defect-correction boundary ->
  **`preempted-but-MF-composition-open` (weak novelty, strong measurement
  value)**; "**No fetched source, in any field, reports a quantitative
  per-term attribution of a displacement-vs-intensity error split** ... Joint-
  vs-sequential cannot be settled by citation (ablations point both ways) ->
  must be a control arm."

Design gifts (report section "For the brainstormer"): sub-voxel residual =>
single-scale head admissible (SuperWarp `PMC9645132`: the optical-flow equation
"holds only when displacement magnitudes remain less than one voxel");
band-limited Fourier `phi` is published and parameter-free on decode
(Fourier-Net `arXiv:2211.16342`); **supervised** warp targets beat self-
supervised by -80 % endpoint error and are legal here (B1's train-split
oracle `phi`; ADR-0009-safe); plain U-Net heads are "worst in **untextured
regions**" -- cahn_hilliard's bulk -- so constrain `phi` instead of trusting a
fully-convolutional head; inverse-consistency error is a GT-free
**diagnostic**, never a loss (many-to-one failure, Guo et al. 2021); do NOT
add a metamorphosis intensity channel -- scope instead; the phase-field
displacement metric is **unsourceable** here and must be re-derived in-repo.

## 2. Section 12 conventions (program.md 12.3, verbatim)

> - **Question**: does geometric alignment (warp-then-correct) beat additive
>   correction on sharp-interface MF fusion?
> - **Anchor**: champion's certified panel geomean (batch 0).
> - **Mechanism prior** ... "coarse LF solves *displace* sharp interfaces, and
>   rel-L2 punishes displacement doubly (the model pays at both the true and
>   the predicted interface). Additive correctors must synthesize the
>   interface; a smooth displacement field that warps LF into alignment (then
>   a small correction net on the warped LF) moves it instead."
> - **Physics-agnostic by construction** (ADR 0009): works from fields alone;
>   no governing equations at train or test time.
> - Known threats ... "warping cannot create or destroy topology (phase-field
>   coarsening changes component counts between LF and HF -- designs must state
>   how the correction stage handles topology mismatch, or scope to datasets
>   where topology is preserved)."
> - Contract CLI unchanged; warp estimation runs inside `smoke_eval.py`.

Floor (`state/noise_floor.json`, `sharp__cahn_hilliard`):
`spread = 0.19182714769533593`, `min_claimable_effect = 0.5533465853654416`,
`mean_skill = 5.533465853654415` (family `mf_fno_pinn_transfer`, 3 seeds).
No `state/anchors/s3_warp.json` exists (B1 was a `do_not_promote` diagnostic
and created none) -- per the batch >= 2 chain, `anchor_reference = "s3_warp-B1"`.

## 3. Within-stream prior cards

`experiment_cards/s3_warp/batch_1/B1.json` -- `diagnostic`, status `complete`,
`reopen_candidate: false`, `anchor_reference: null`. Legs A/B recorded NOT
falsified at face value and **both invert** once the reference is registered
correctly (part 6 `falsification_postmortem`). Load-bearing findings:

- **F1/F2/F3** -- `eval/panel_data.py::copylf_prediction` uses the cell-centred
  `zoom(grid_mode=True)` convention on node-sampled fields => copy-LF is
  misregistered by exactly `(r-1)/2 = 0.5` HF cells. Zero-parameter fixes on
  cahn_hilliard: fixed shift 0.4973, node-aligned bilinear **0.4769**,
  node-aligned band-limited 0.4631.
- **F9** -- corrected-reference residual ceilings: fisher_kpp 1.4 %,
  allen_cahn 11.1 %, pfc 17.0 %, **cahn_hilliard 83.4-85.2 %**, helmholtz
  36.5 %. Stream premise survives on cahn_hilliard alone.
- **F11** -- residual median `|phi|` (corrected C16): pfc 0.000, fisher_kpp
  0.034, allen_cahn 0.045, **cahn_hilliard 0.64 (n=6) / 0.74 (n=8)**,
  helmholtz 1.92; DC <= 0.13 cells everywhere.
- **F12** -- DC-only arm delivers 99.5 / 96.7 / 89.9 % of C16's reduction on
  fisher_kpp / allen_cahn / pfc but only **48.9 %** on cahn_hilliard.
- **F13** -- on the corrected image C4 buys ~nothing; only C16 pays
  (0.060459 -> 0.030621 -> 0.008965).
- **F10/F17** -- the second bilinear resample is what injects mid-band error:
  the oracle warp's band ratios `[0.0147, 0.0678, 2.800, 1.042]` vs a fixed
  shift `[0.0074, 0.0390, 0.985, 0.995]`.
- **F14/F15/F18** -- 88 % of s6's LSI filter on cahn_hilliard is the half-cell
  phase ramp; after correction the ramp is gone and the genuine remainder
  moves 0.4631 -> **0.4402**; best free reference 0.4402 with 85 % oracle
  extra on top.
- Topology (leg C): **5-6 %** of cahn_hilliard samples have an LF/HF component
  mismatch, mean `|dN| = 0.11` -- the panel's most nearly diffeomorphic set, so
  12.3's appearance-term requirement is satisfiable **by scoping**.
- Part 7 mandates for any B2/D1 card: (1) architecture-level **warp-off
  control**; (2) **CONSTANT-DISPLACEMENT-ONLY arm -- now MANDATORY**;
  (3) **registration-corrected reference alongside the frozen skill**;
  (a) do NOT `grid_sample` an interpolated LF; (b) budget DOF from the
  corrected image; (c) scope, don't metamorphose. Its open question is exactly
  our slot: "is that displacement field PREDICTABLE from the LF field a model
  actually receives, or is it only visible to an HF-fitted oracle?"
- Reusable assets: `worktrees/s3_warp/B1/models_r1/s3_warp_oracle/warp_core.py`
  (branch `round1/exp-s3_warp-B1` @ `4799abd`) and
  `.../B1/eval/warp_oracle_sharp__cahn_hilliard_phi.npz` (`p_train (400,2,16,16)`,
  `p_test (100,2,16,16)` -- fitted on the **misregistered** image, so B2 must
  **re-fit** on the corrected path).

## 4. Cross-stream cards

- **`s6_local-B1`** (`complete`) -- the trained 77 k-param local corrector on
  the real interpolated LF scores **skill 0.4686 (nRMSE 0.041076)** on
  `sharp__cahn_hilliard`, 282 s train. This is the numeric definition of "the
  s6-class correction baseline" on this substrate and it upper-bounds any
  arm-vs-arm margin my card can produce (see section 6).
- **`s6_local-B2`** (`running`) -- `circ_repair` / `lsi_ctrl` / trust-head arms
  on the full panel; its trained-corrector comparison lands separately. Its
  boundary with me: s6 owns the **intensity/defect** corrector, I own the
  **coordinate** term. `tools/defect_correction_learnability.py`
  (`fit_transfer` / `apply_transfer`) is the shared LSI definition.
- **`s2_beyond_copy-B1`** -- M1: the champion is **LF-blind at inference**
  (`lf_at_inference = FALSE`, 5/5 x 3/3), which is why the champion is not a
  legitimate comparator for an LF-consuming warp model.
- `docs/operator_notes/2026-07-30-benchmark-registration-note.md` -- the
  mentor-facing registration note is already filed; round-1 practice is
  "cards may carry a registration-corrected reference alongside the frozen one".

## 5. Reopen candidates

None. `s3_warp-B1` has `reopen_candidate: false`, `status: complete`. The
retired `s3_testtime-B1` belongs to a different (retired) stream, ADR 0010,
and is not a reopen candidate for `s3_warp`.

## 6. What is UNKNOWN

1. **The gate question (B1 part 7).** Is cahn_hilliard's 0.64-0.74-cell
   residual displacement **predictable from LF + condition alone**, or only
   visible to an HF-fitted oracle? B1's only learnability evidence (leg D,
   retrieval captures 63-99 % of the C16 ceiling) was measured against the
   **misregistered** reference where the retrieved quantity was ~a constant --
   i.e. it measured retrievability of the grid convention, not of transport.
   Nothing about learnability on the corrected path has been measured.
2. **Warp vs intensity attribution.** Unreported anywhere in the literature
   (verdict iii). On the corrected path, does a displacement arm own error the
   correction class cannot reach? F18 says the oracle's extra over the best
   free reference is 85 % -- but the *achievable* share is unknown.
3. **Does the constant-displacement arm still buy anything once the input path
   is registration-correct?** F12's 48.9 % was measured on the misregistered
   image; F11's residual DC <= 0.13 cells predicts ~0, but that is an oracle
   statistic, not a trained-arm one. This is the single cleanest way to
   separate "registration fixing" from "one-sided warping".
4. **Whether the head can behave in the untextured bulk.** SuperWarp says a
   plain conv head fails exactly there; a band-limited `phi` plus a
   gradient-evidence-masked supervision loss is the untested remedy.
5. **The floor arithmetic.** *Newly identified here and load-bearing.* All
   correction-class arms on cahn_hilliard sit at skill ~ 0.44-0.48
   (s6-B1 0.4686; LSI 0.4402; F3 variant C 0.4769) and skill >= 0, so the
   **maximum attainable arm-vs-arm margin is ~ 0.47 < `min_claimable_effect`
   0.5533**. Whether any attribution clause on this dataset can clear the
   anchor-referenced floor is therefore not an experimental unknown but an
   arithmetic impossibility -- it must be declared, and it is the card's second
   deliverable to the mentor (B1's part 4 set the precedent of declaring, not
   working around, this structural property).
6. **Unknown-but-deferred**: `ext__helmholtz_2d`'s transport (36.5 % ceiling,
   1.92 cells) is the only other candidate; its LF/HF grids (24/96 Dirichlet
   interior-node, non-nested) need a *different* node-alignment convention
   than the dyadic periodic one, i.e. a second implementation surface, and its
   floor 9.695 makes it report-only regardless.
