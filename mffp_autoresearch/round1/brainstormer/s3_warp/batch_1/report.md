# Brainstormer Report — Stream `s3_warp`, Batch 1

**Stream**: `s3_warp` (created by ADR 0010; first batch of the stream)
**Batch**: 1
**Total iterations**: 1
**Slot filled**: 1 (`diagnostic`)
**Reopen candidates resolved**: 0 (none exist)

---

## Slot

- **Category**: `diagnostic / warp-opportunity oracle — displacement-vs-thickness
  decomposition of the LF->HF discrepancy on the beyond-copy panel`

- **Card type**: `diagnostic`

- **Motivation**: The websearcher's prior-art verdict makes D2 both the least
  preempted direction and the gate on D1. Verbatim, the D2 row's open part:
  *"The metric is old; no fetched source applies it **between two fidelities of
  one PDE solve**, and none reports an oracle-warp upper bound on MF fusion
  error. It also gates D1: iteration 4's two-regime finding (shape/position vs
  interfacial-thickness error) means D1's premise is an empirical question
  about *our* LF grids."* Program.md §12.3's mechanism prior — *"coarse LF
  solves *displace* sharp interfaces, and rel-L2 punishes displacement doubly"*
  — is therefore an untested empirical claim about this benchmark, and the one
  source that would have settled the two-regime question **403'd** (MDPI
  cryst12101496; the websearch marks the claim snippet-level, not
  citation-grade). The cross-stream evidence sharpens rather than removes the
  question: s2_beyond_copy-B1 M4 shows the *champion's* excess error is
  mid-distance on pfc and far-field on cahn_hilliard, but M1 shows the champion
  is **LF-blind at inference** (`lf_at_inference = FALSE`, 5/5 datasets x 3/3
  seeds, zero field-shaped inputs), so its error is not the object a warp acts
  on. The right rows are copy-LF's error-mass/area shares — allen_cahn
  `[2.049, 0.814, 0.560, 0.552]` (interface-tilted), pfc
  `[1.276, 1.811, 0.840, 0.105]`, fisher_kpp `[1.034, 0.637, 0.909, 1.389]`,
  cahn_hilliard `[0.750, 0.562, 0.589, 2.162]`, helmholtz
  `[0.070, 0.248, 0.717, 3.011]` — plus M5a's copy-LF
  `amplitude_share_of_error` (allen_cahn 4.9e-5, fisher_kpp 0.0016, pfc 0.0045,
  cahn_hilliard 0.067, helmholtz 0.691), which says the sharp-dataset LF error
  is structural rather than amplitude. This card measures the ceiling a warp
  can reach, the regime it would be operating in, and the topology constraint
  §12.3 requires — training-free, at s2-B1's demonstrated cost scale.

- **Concrete config**: new contract family
  `worktrees/s3_warp/B1/models_r1/s3_warp_oracle/` (`manifest.json` with
  `"diagnostic": true`, `smoke_eval.py` on the unchanged six-argument factory
  CLI, `INSPIRATION.md`, helper modules), invoked by unmodified
  `eval/score_panel.py` at `--epochs 0 --seed 0` on the five beyond-copy
  datasets. It trains no model. The warp primitive is
  `torch.nn.functional.grid_sample(LF_up, base_grid + phi)` — deliberately the
  same STN-style bilinear sampling a D1 model would use — with `phi`
  parameterised by a `C x C x 2` control grid bilinearly upsampled to the HF
  grid, `|phi|` clamped to 16 cells, and a Laplacian smoothness penalty.
  Measurements (all from one shared fit pass; sidecar
  `warp_oracle_<dataset>.json` under `${S3W_DIAG_OUT}`):

  - **M0 seam.** Rung `C = 0` (`phi == 0`) is the **warp-off control** and must
    equal `eval/copylf_baselines.json` to <= 1e-9 or the run aborts; every
    nRMSE is computed by importing `eval/nrmse.py` and each sidecar records
    `nrmse_def_hash`.
  - **M1 oracle ladder.** Per test sample, minimise
    `||grid_sample(LF, I + phi) - HF||^2 + lambda ||Laplacian phi||^2` by Adam
    (400 iters), coarse-to-fine over `C in {0, 4, 8, 16, 32, full}` (each rung
    initialised from the upsampled previous rung; loss asserted
    monotone-non-increasing in `C`). Report
    `skill_oracle(C) = nRMSE_warp(C) / nRMSE_copyLF`. The **learnable rung** is
    `C = 16` (512 dof, the low-mode budget a small FNO displacement head can
    plausibly express); `C = full` is the unbounded reference whose only job is
    to price the DOF axis.
  - **M2 regime.** Distribution of `|phi|` in grid cells (median / p90 / max),
    overall and restricted to near-interface pixels, using s2-B1's *identical*
    interface rule (`tau = 0.1` on `|u| / max|u|`, top-decile `|grad u|`
    fallback, pooled-quartile distance strata) so the sidecars are directly
    comparable.
  - **M3 displacement/amplitude decomposition** (Keil & Craig 2009 DAS,
    adopted by citation): split copy-LF's squared error into DIS (removed by
    the warp), AMP (further removed by a post-warp per-sample optimal scalar
    rescale, same `alpha` construction as s2 M5a), RES (remainder — the
    thickness/topology term no diffeomorphism can reach).
  - **M4 thickness probe.** Interface-band gradient-energy ratio
    `||grad HF|| / ||grad(warp(LF))||` before and after warping; a persistent
    ratio > 1 is direct evidence of the un-warpable interfacial-thickness
    regime.
  - **M5 topology** (§12.3 requirement): connected-component counts of the
    phase indicator, LF vs HF, per sample; `mean |dN|` and the fraction of
    samples with `dN != 0`, per dataset. Names which datasets need a
    metamorphosis-style appearance term (MetaRegNet arXiv:2303.09088) and which
    are safely diffeomorphic.
  - **M6 spatial tie-in.** Warp benefit per s2 interface-distance stratum — does
    the removed error sit where copy-LF's error sits?
  - **M7 spectral tie-in.** Dyadic-band decomposition with s2-B1's identical
    band edges of copy-LF error vs post-warp error — is s2's low-band excess
    displacement-explainable, or is band-0 dominance only the 0.961-0.9998 HF
    energy share?
  - **M8 learnability bracket (scored).** Fit displacements on the *train*
    split too, then transfer to each test sample from its nearest neighbour
    (a) in LF-field space — this is the **scored `test_hf` split** — and (b) in
    condition space (`ref_transfer_cond`). Neither consults test-split HF.
    Stated confound: a field-conditioned learned head can exceed retrieval, so
    a poor transfer number does **not** falsify D1.
  - **M9 optimiser self-test (hard-stop).** Apply a known smooth random
    displacement to HF to synthesise a pseudo-LF (in memory only; never
    written, never scored); the fitter must recover it to < 0.25 cells endpoint
    error and drive nRMSE below 5% of unwarped, else the job aborts. This
    prevents "optimiser failed" being reported as "no warp regime". A
    `skimage.registration.optical_flow_tvl1` cross-check is run on the `C=full`
    rung of one dataset as a second opinion.

  Split-key discipline (s2 precedent: `score_panel._extract_test_metric` reads
  only `test*` keys): copy-LF, every oracle rung, and the condition-space
  transfer are written under `ref_*` keys. **`do_not_promote: true` is
  pre-registered in the card** — the scored entry is a training-free
  nonparametric transfer, not a model, and is ineligible for the leaderboard,
  anchors, and top-3 confirmation. Oracle rungs are HF-fitted upper bounds and
  are never scored.

  Dataset scope: the five beyond-copy panel datasets. `ifc_poisson` is excluded
  because its test split ships only the HF fidelity, so copy-LF is undefined
  and there is no LF field to warp (ADR 0002; `eval/copylf_baselines.json`
  `_notes.ifc_poisson`). `ext__helmholtz_2d` is the **built-in negative
  control** and is report-only (far-field copy-LF error, 69% amplitude,
  oscillatory not interface-dominated, floor 9.695).

- **Recipe**:

```json
{
  "base_family": "none (new diagnostic family; no base model, no checkpoint reload, nothing trains)",
  "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
  "family_dir": "models_r1/s3_warp_oracle",
  "datasets": "ext__helmholtz_2d,sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard",
  "epochs": 0,
  "seeds": [0],
  "env": {
    "S3W_RUNGS": "0,4,8,16,32,full",
    "S3W_LEARNABLE_RUNG": "16",
    "S3W_ITERS": "400",
    "S3W_LR": "0.02",
    "S3W_SMOOTH_LAMBDA": "1e-3",
    "S3W_MAX_DISP_CELLS": "16",
    "S3W_INTERFACE_TAU": "0.1",
    "S3W_BANDS": "4",
    "S3W_TRANSFER_NN": "field,cond",
    "S3W_SELFTEST": "1",
    "S3W_DIAG_OUT": "${OUTPUTS_ROOT}/s3_warp/B1/eval"
  }
}
```

  Submit-time job env (not a scoring knob; s2-B1 precedent, reviewer suggestion
  S1): `ROUND1_EVAL_RESULTS=${OUTPUTS_ROOT}/s3_warp/B1/eval/results` so the
  family writes nothing into `round1/eval/results/`. Wall-clock estimate: 6
  rungs x 400 Adam iters x ~500 fields x 5 datasets, GPU-batched — 10-25 min on
  H100 (s2-B1's inference-only 5-dataset diagnostic was 0.77 min; this adds the
  fit). Suggested `--time 01:00:00`.

- **Expected outcome**: The measured quantity is
  `skill_oracle(C=16) = nRMSE(oracle-warped LF) / nRMSE(copy-LF)` per dataset;
  copy-LF is skill 1.0 by definition, so an effect is `1 - skill_oracle`.
  Predictions, grounded in the s2 copy-LF geometry:
  - `sharp__allen_cahn_2d` — copy-LF error most interface-concentrated
    (2.049x area share in the nearest stratum) and essentially zero amplitude
    (4.9e-5): predict `skill_oracle(16) ~ 0.25-0.45`, i.e. 55-75% of copy-LF's
    error removable; interface-pixel median `|phi| ~ 0.5-2` HF cells.
  - `sharp__fisher_kpp_2d` — travelling-front dataset, flat-ish error profile:
    predict `0.40-0.65`.
  - `sharp__phase_field_crystal_2d` — near+mid error, 128^2: predict
    `0.35-0.60`.
  - `sharp__cahn_hilliard` — far-field-concentrated copy-LF error and the
    largest sharp-dataset amplitude share (0.067): predict `0.70-0.90`, the
    weakest warp candidate of the four.
  - `ext__helmholtz_2d` (report-only, no claim) — predict `> 0.85` and an AMP
    term dominating DIS; a near-zero warp benefit here is the validity signal
    that the fitter is not simply absorbing arbitrary error.
  - `C = full` rung: predict `< 0.15` on every dataset — expected and
    uninformative on its own; its purpose is to price the DOF axis
    (`skill(full)` vs `skill(16)` is the gap a learned low-mode head must not
    be judged against).
  So I expect **leg A not to fire** (>= 2 of the 4 sharp datasets at
  `skill_oracle(16) <= 0.44`), with allen_cahn and pfc the likely carriers, and
  I expect **leg B not to fire** on allen_cahn/pfc but plausibly to fire on
  cahn_hilliard.
  Against the noise floor: a leg-A-passing effect is >= 0.56 skill units, which
  exceeds `min_claimable_effect` on `sharp__cahn_hilliard` (0.553) and
  `sharp__fisher_kpp_2d` (0.418) outright, and exceeds the certified `spread`
  by 40x on `sharp__allen_cahn_2d` (0.0141), 6.8x on
  `sharp__phase_field_crystal_2d` (0.0826), 2.9x on `sharp__cahn_hilliard`
  (0.192) and 6.1x on `sharp__fisher_kpp_2d` (0.0918). On allen_cahn (1.633)
  and pfc (1.151) *no* copy-LF-referenced effect can clear
  `min_claimable_effect`, because that quantity is anchor-referenced
  (`max(spread, 0.1 x anchor mean skill)`, verified against all six entries)
  while a copy-LF-referenced effect lives in [0, 1] by construction — the same
  structural property that round-1 success criterion 2 ("skill < 1") has. This
  is declared, not worked around. `ext__helmholtz_2d` carries no leg and no
  numeric claim (floor 9.695).
  Consequences either way: a passing leg A + leg B licenses the D1 model card
  and fixes its target (the ceiling); a firing leg A retires the warp mechanism
  for this panel with a measured number rather than a failed 200-epoch run.

- **Expected falsification**: **Leg A (primary)** — the stream premise ("the
  LF->HF discrepancy on sharp-interface panel datasets is substantially a
  geometric displacement of features") is **falsified** if the oracle warp at
  the learnable rung (`C = 16`, smoothness-penalised, `|phi| <= 16` cells)
  leaves `skill_oracle > 0.44` (i.e. removes < 56% of copy-LF's error) on **3
  or more** of the four sharp datasets `{sharp__allen_cahn_2d,
  sharp__phase_field_crystal_2d, sharp__cahn_hilliard,
  sharp__fisher_kpp_2d}` — with `ext__helmholtz_2d` excluded from the count as
  report-only (floor 9.695) and the M9 self-test having passed, so the result
  cannot be an optimiser artefact. **Leg B (regime)** — the premise is
  falsified *as a displacement story* even if leg A passes, if the median
  `|phi_oracle|` at near-interface pixels is `< 0.5` grid cells on 3 or more of
  those four datasets (a sub-cell "warp" is resampling/sharpening, not
  transport; 0.5 cells is 2x the pre-registered 0.25-cell self-test accuracy
  floor). **Leg C (topology, reported)** — if `> 25%` of test samples show a
  LF/HF connected-component mismatch on 2 or more sharp datasets, any future D1
  card must carry a metamorphosis-style appearance term or scope to the
  topology-preserving subset. **Leg D (learnability, reported, non-falsifying)**
  — nearest-neighbour displacement transfer at skill `>= 1.0` on 4 or more of
  the 5 datasets means the benefit cannot be retrieved and must be *predicted
  from the field*; the confound (a learned head sees more than a retrieval
  index) is stated in the card.

- **Prior-art verdict quoted** (verbatim from
  `websearches/s3_warp/batch_1/report.md`):
  - D2 row — **`preempted-but-MF-composition-open`**; citations: Keil & Craig
    2009 DAS
    `https://journals.ametsoc.org/view/journals/wefo/24/5/2009waf2222247_1.pdf`
    (search-result level, primary-source PDF URL, **not fetched in-loop**);
    Gowrachari et al. snapshot-registration ROM
    `https://arxiv.org/html/2501.01299v1` (**fetched**). Open part: *"The metric
    is old; no fetched source applies it **between two fidelities of one PDE
    solve**, and none reports an oracle-warp upper bound on MF fusion error. It
    also gates D1: iteration 4's two-regime finding (shape/position vs
    interfacial-thickness error) means D1's premise is an empirical question
    about *our* LF grids."*
  - The D1 usable form this card gates (report's `## For the brainstormer`):
    *"preempted-but-MF-composition-open — learned warping in neural PDE
    architectures is published (Flowers, arXiv:2603.04430, but strictly
    single-fidelity with no LF->HF mapping), warp-plus-appearance-correction is
    published as metamorphosis (MetaRegNet, arXiv:2303.09088), and transport
    geometry for MF diffuse-interface correction is published (Khamlich,
    arXiv:2603.04232, classical OT on residual fields, no NN); what is open is a
    learned displacement predicted from the LF field and applied to it before a
    learned correction, in an MF operator surrogate."*
  - Seed-claim ruling: *"'No published multi-fidelity operator method predicts
    an inter-fidelity displacement field and warps before correcting' —
    **survives** 5 dedicated refutation searches. 'The registration-based
    framing "align, then correct" is a documented gap' — **does NOT survive**
    (metamorphosis; Khamlich MF-OT on Allen-Cahn)."*
  - Card `prior_art` fields for the starter: `verdict:
    "preempted-pivoted"`; `citations` (fetched-in-loop only):
    `["https://arxiv.org/html/2501.01299v1", "https://arxiv.org/html/2603.04232v2",
    "https://arxiv.org/pdf/2303.09088", "https://arxiv.org/html/2603.04430"]`.
    Keil & Craig 2009 is the source of the adopted DIS/AMP decomposition and is
    cited in `INSPIRATION.md` with its provenance caveat (search-result level,
    not fetched).

- **Immutables self-check**: **pass (10/10)** — item-by-item positive evidence
  in [iteration_1.md](iteration_1.md) (§ "Immutables self-check"). Summary: data
  read-only (read through `eval/panel_data.py`, synthetic self-test field in
  memory only); panel subset, no redefinition; eval layer byte-untouched
  (`score_panel.py` invoked unmodified, `eval/nrmse.py` imported); one nRMSE
  definition (`nrmse_def_hash` recorded per sidecar; the fitting objective is a
  training objective, which §5 leaves free, and is never scored); contract CLI
  unchanged with all 11 knobs in `recipe.env` and therefore in `code_hash`;
  `seeds [0]` (ADR 0004) and `epochs 0` (SCHEMA.md: legal for diagnostics);
  guarded factory surfaces untouched, outputs redirected via
  `ROUND1_EVAL_RESULTS`; per-rung `<ckpt_dir>/last.pt` resume (s2-B1 pattern);
  floor analysis quoted above; nearest pre-falsified lever is `mf_fno_spectral`
  LF low-mode freezing — this card freezes no *value-space* mode, constrains a
  *coordinate map* instead, and trains nothing.

- **Anchor reference**: `null` (lever stream, program.md §4.5 — own-stream
  anchor implicit). Note for the maintainer: `state/anchors/s3_warp.json` does
  not exist (the stream postdates batch 0); the certification §12.3's anchor
  line refers to lives in `state/anchors/s3_testtime.json` (champion
  `mf_fno_transfer_film`, panel geomean 6.703, per-seed 7.102/6.219/6.788).
  This card makes no anchor-referenced claim and never runs the champion, so
  the gap is not blocking.

- **Source iteration**: [iteration_1.md](iteration_1.md)

---

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _none_ | n/a | n/a | [iteration_1.md](iteration_1.md) |

No card under `experiment_cards/**` carries `reopen_candidate: true` (verified
across all five extant cards); `s3_warp` has no prior batches, and
`s3_testtime-B1` is `retired_by_operator` with `reopen_candidate: false` under
ADR 0010, which is an operator scope decision, not a skip.

---

## Skipped slot

n/a — the slot is filled.

---

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| s3_warp-B1 | diagnostic / warp-opportunity oracle | Training-free per-sample oracle warp of copy-LF onto HF over a control-grid DOF ladder (rung 0 = warp-off = copy-LF), measuring the removable-error ceiling, the displacement-vs-thickness-vs-amplitude split, topology mismatch, and a retrieval-transfer learnability bracket on the five beyond-copy datasets | filled |

---

## Notes for downstream agents

1. **The starter** transcribes the recipe JSON above verbatim; `prior_art` uses
   the `verdict` / `citations` given in the "Prior-art verdict quoted" bullet;
   part 4 must carry `do_not_promote: true` **pre-registered** (s2-B1 needed
   the reviewer to add it after the fact).
2. **The builder** must implement M9 (self-test) as a hard abort before any
   reported number, must assert rung 0 == `eval/copylf_baselines.json` to
   <= 1e-9, and must reuse s2-B1's interface rule and band edges byte-for-byte
   so the sidecars are comparable.
3. **The next brainstormer in this stream** inherits a pre-registered
   requirement: any D1 (`mf_warp_correct`) model card must carry the
   architecture-level **warp-off control** (identical network, displacement
   forced to zero) as its comparator, not the champion alone — because s2-B1 M1
   proves the champion is LF-blind at inference and a warp model would be the
   round's first LF-consuming model.
4. **Summary length**: `summary_so_far.md` is ~1.68k words, above the 500-1200
   guide; the overage is the mandatory verbatim §12.3 block (~430 words) plus
   the verbatim prior-art verdict quotes.
