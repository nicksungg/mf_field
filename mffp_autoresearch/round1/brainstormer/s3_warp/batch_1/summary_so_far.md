# Summary so far — Stream `s3_warp`, Batch 1

Stream created 2026-07-29 by ADR 0010 (`docs/adr/0010-s3-replacement.md`);
this is its first batch. No prior `s3_warp` cards exist.

## 1. Websearch findings + prior-art verdict

Source: `websearches/s3_warp/batch_1/report.md` (5 iterations, 15 WebSearch,
10 WebFetch of which 6 usable; cap hit).

Three candidate directions were scanned. All three came back
**`preempted-but-MF-composition-open`**, with different confidence:

- **D1** (`mf_warp_correct`: FNO head predicts a smooth, zero-init,
  smoothness-penalised displacement from up(LF)+cond; `grid_sample` warp; FiLM
  residual correction on the warped field). Verdict row, open part verbatim:
  *"Predicting a displacement **from an LF PDE field** and warping **that
  field** into HF alignment before a learned correction, inside an MF operator
  surrogate at N_hf = 5-25. Already published and NOT claimable: learned
  warping in neural PDE models (Flowers); align-then-correct as a formulation
  (metamorphosis); transport geometry for MF diffuse-interface correction
  (Khamlich, on conservative Allen-Cahn at our own 128^2-512^2 ladder)."*
- **D2** (warp-oracle / displacement-vs-amplitude diagnostic on the panel,
  incl. topology component-count check). Open part verbatim: *"The metric is
  old; no fetched source applies it **between two fidelities of one PDE
  solve**, and none reports an oracle-warp upper bound on MF fusion error. It
  also gates D1: iteration 4's two-regime finding (shape/position vs
  interfacial-thickness error) means D1's premise is an empirical question
  about *our* LF grids."*
- **D3** (OT / soft-warp auxiliary objective) — weakest confidence.

Ruling on the seed claim: *"'No published multi-fidelity operator method
predicts an inter-fidelity displacement field and warps before correcting' —
**survives** 5 dedicated refutation searches. 'The registration-based framing
"align, then correct" is a documented gap' — **does NOT survive**
(metamorphosis; Khamlich MF-OT on Allen-Cahn). The claimable novelty is
narrow: the *neural, cross-fidelity, field-level* instantiation in the
few-HF-sample operator-learning regime."*

Two design-changing findings, both from `iteration_4.md`:
(i) coarse phase-field grids produce **position** error (grid friction /
pinning, shape deformation) *and* **interfacial-thickness** error; only the
first is warpable, and which regime *our* LF grids sit in is unmeasured;
(ii) free-form displacement fields dominate the literature but drop
diffeomorphic guarantees, and global smoothness penalties are documented as
locally insufficient (arXiv:2412.17982) — low-DOF parameterisations
(B-spline control grids, low-Fourier-mode fields) are the small-data prior.

Explicit instructions to me in `## For the brainstormer`: consider making
batch 1 the D2 diagnostic; handle topology explicitly (§12.3 requires it);
carry the **warp-off control** because the champion never consumes LF at test
time; do not claim on helmholtz (floor 9.695).

## 2. §12 conventions (program.md §12.3, verbatim)

> ### 12.3 `s3_warp` (lever) — REPLACED STREAM, see ADR 0010
> *(`s3_testtime` was retired by operator direction 2026-07-29 before any SLURM run; its B1 card is `retired_by_operator`. Rationale: ADR 0009 — methods must not assume known physics at test time — plus the stream's own findings: a true residual exists on 1/6 panel datasets, and where it exists the dataset is two-FFT-solvable without a model.)*
> - **Question**: does geometric alignment (warp-then-correct) beat additive correction on sharp-interface MF fusion?
> - **Anchor**: champion's certified panel geomean (batch 0).
> - **Mechanism prior** (docs/proposals/NEW_MODELS.md Candidate D, un-ingested at round start; its own scan found the mechanism NOT prior-art-preempted — batch-1 websearch must re-verify): coarse LF solves *displace* sharp interfaces, and rel-L2 punishes displacement doubly (the model pays at both the true and the predicted interface). Additive correctors must synthesize the interface; a smooth displacement field that warps LF into alignment (then a small correction net on the warped LF) moves it instead.
> - **Physics-agnostic by construction** (ADR 0009): works from fields alone; no governing equations at train or test time.
> - Known threats to verify in batch-1 websearch: optical-flow / deformable-registration warping is heavily published in video SR and medical imaging — the novelty question is its use for multi-fidelity PDE fusion; warping cannot create or destroy topology (phase-field coarsening changes component counts between LF and HF — designs must state how the correction stage handles topology mismatch, or scope to datasets where topology is preserved).
> - Synergy: s2_beyond_copy-B1's M4 interface-distance stratification will quantify how much of the champion's excess error sits at interfaces — read it before designing batch 2 here.
> - Contract CLI unchanged; warp estimation runs inside `smoke_eval.py`.

Anchors: `state/anchors/s3_warp.json` does **not** exist (the stream postdates
batch 0). `state/anchors/s3_testtime.json` carries the identical batch-0
certification the §12.3 anchor line refers to — `mf_fno_transfer_film`, panel
geomean skill **6.703** (per-seed 7.102 / 6.219 / 6.788, ci95 [6.219, 7.102]).

`state/noise_floor.json` (`min_claimable_effect` / `spread`, skill units):
helmholtz 9.695 / 9.695; allen_cahn 1.633 / 0.0141; pfc 1.151 / 0.0826;
cahn_hilliard 0.553 / 0.192; fisher_kpp 0.418 / 0.0918; ifc_poisson 0.240 /
0.240. `min_claimable_effect = max(seed_spread, 0.1 x anchor mean skill)`
(verified arithmetically against every entry).

## 3. Within-stream prior cards

None — `experiment_cards/s3_warp/` does not exist. The retired
`s3_testtime/batch_1/B1.json` (`status: retired_by_operator`,
`reopen_candidate: false`) is a different stream and a different mechanism; its
usable residue is negative evidence (ADR 0009: no known physics at test time),
which `s3_warp` satisfies by construction.

## 4. Cross-stream prior cards

**`s2_beyond_copy-B1`** (`experiment_cards/s2_beyond_copy/batch_1/B1.json`,
part 5, `status: analyzing`) — a completed diagnostic that reshapes this
design. Findings, sourced verbatim from `5_actual_result`:

- **M1**: `lf_at_inference = FALSE` for `mf_fno_transfer_film` on 5/5 datasets
  x 3/3 seeds; `n_field_shaped_inputs_at_eval = 0`; the only tensor entering
  the champion at eval is the `[16, cond_dim]` condition vector. The champion
  is **X-only**; copy-LF is the only LF-using predictor in the round.
- **M3**: `R_low > 1` on 5/5 datasets x 3/3 seeds (11.18-209.56 on the four
  sharp; 1.23-8.63 helmholtz). Excess is a **low-band** phenomenon. Caveat I
  must respect: `hf_energy_share_by_band[0]` is 0.961-0.9998 on every dataset,
  so band-0 dominance is partly a bookkeeping fact, not a mechanism.
- **M4** (champion): pfc `[0.53, 1.17, 1.78, 0.58]` — peaks **mid-distance**,
  not at interfaces; cahn_hilliard far-field `[0.61,0.68,0.61,2.18]`;
  fisher_kpp near-flat. "The champion's spatial error is nowhere
  interface-localized beyond ~1.3x area share."
- **M4 (copy-LF rows — the ones that matter here, since a warp acts on the
  LF->HF discrepancy, not on the champion's error)**: allen_cahn
  `[2.049, 0.814, 0.560, 0.552]` (strongly interface-concentrated); pfc
  `[1.276, 1.811, 0.840, 0.105]` (near+mid); fisher_kpp
  `[1.034, 0.637, 0.909, 1.389]` (flat-ish); cahn_hilliard
  `[0.750, 0.562, 0.589, 2.162]` (far-field); helmholtz
  `[0.070, 0.248, 0.717, 3.011]` (far-field, where 89% of HF energy lives).
- **M5a (copy-LF)** `amplitude_share_of_error`: allen_cahn 4.9e-5, fisher_kpp
  0.0016, pfc 0.0045, cahn_hilliard 0.067, **helmholtz 0.691**. On the four
  sharp datasets copy-LF's error is essentially *not* a global amplitude
  error — it is structural (position / shape / thickness), which is exactly the
  precondition D1 needs, and helmholtz is the opposite case.
- **M5b**: aligned/index-shifted residual 0.008-0.176; "the LF/HF alignment is
  sound and program.md 12.2's data-defect branch is CLOSED."
- Shapes: helmholtz 96^2, cond 3; allen_cahn / cahn_hilliard / fisher_kpp
  256^2, cond 3 / 19 / 2; pfc 128^2, cond 2. All 400 train HF / 100 test HF.
- Operational precedent: that diagnostic ran `--epochs 0 --seed 0` on the five
  beyond-copy datasets, cost **0.77 min on H100**, and its scored `test_hf`
  split (a training-free lookup) had to be flagged `do_not_promote` by the
  reviewer *after the fact*.

`s1_poisson-B1`, `s4_hybrid_routing-B1`, `s5_tuning-B1`: scanned; none
references `s3_warp` or attacks a constraint relevant to it.

## 5. Reopen candidates

None. No card in `experiment_cards/**` carries `reopen_candidate: true`
(all five existing cards are `false`).

## 6. What is UNKNOWN

1. **The regime question — the single biggest unknown.** Is the LF->HF
   discrepancy on our grids a *position* error (interfaces in the right shape,
   wrong place) or a *thickness/sharpness* error (interfaces in the right
   place, wrong profile)? Nothing in the repo measures this. The websearch
   could only establish that both regimes are documented for coarse
   phase-field grids, and its primary source for that (MDPI cryst12101496)
   **403'd** — the claim is snippet-level, not citation-grade. A warp fixes
   the first and cannot touch the second, so D1's entire premise is
   undetermined. Unknown per-dataset, and the four sharp datasets have
   visibly different copy-LF error geometry (§4, M4 copy-LF rows), so a
   single global answer is unlikely.
2. **The magnitude of the optimal displacement.** If the best aligning
   displacement is sub-cell (< 0.5 grid cells) then "warp" degenerates into
   resampling/sharpening and the mechanism story is wrong even if the number
   looks good. Unmeasured.
3. **The ceiling.** Nobody knows how much of copy-LF's error a *perfect*
   smooth warp removes — the upper bound on any D1 variant. Without it, a D1
   model card cannot be sized: a 200-epoch run could "fail" at 5% of a 7%
   ceiling and we would not know we were near the ceiling.
4. **DOF dependence of that ceiling.** The ceiling is meaningless without a
   DOF axis: a free-form per-pixel displacement can transport values
   arbitrarily and would trivially report a huge ceiling. What a learned
   low-mode head could reach is a different number, and the gap between them
   is the quantity that decides whether D1 is worth a model card.
5. **Topology.** §12.3 demands the design state how topology mismatch is
   handled. Nobody has counted connected components of LF vs HF phase
   indicators on these datasets. Unknown which panel datasets are even
   topology-preserving.
6. **Learnability.** Even if the ceiling is high, is the displacement field
   *predictable* from what a model sees (LF field + cond)? s2's
   `train_degeneracy.nn_over_random` (pfc 0.023, allen_cahn 0.201, helmholtz
   0.419, cahn_hilliard 0.865, fisher_kpp 0.937) says the condition vector
   alone carries very different amounts of information per dataset — but says
   nothing about displacement fields specifically.
7. **Confound risk.** Because the champion is LF-blind (M1), any D1 win could
   be a "consume LF at test time" win rather than a "warp" win. The
   architecture-level warp-off control is mandatory for any future model card;
   what is unknown is whether the LF-consumption effect alone already beats
   the anchor.
8. **Whether s2's low-band excess (M3) is displacement-explainable.** A
   displaced sharp interface produces broadband error, but energy-share
   bookkeeping puts almost everything in band 0 on these datasets. Whether a
   warp removes band-0 error specifically is untested.
9. **A floor-convention gap.** `min_claimable_effect` is anchor-referenced
   (10% of a champion at skill 4-16). Any copy-LF-referenced effect lives in
   [0, 1] skill units by construction, so on allen_cahn (1.633) and pfc
   (1.151) *no* copy-LF-referenced effect of any size can clear it — including
   round-1 success criterion 2 itself (skill < 1). This needs stating
   explicitly rather than being silently violated.
