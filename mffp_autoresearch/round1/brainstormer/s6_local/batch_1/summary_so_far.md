# Summary so far — Stream `s6_local`, Batch 1

Paths relative to `${ROUND_ROOT}` = `/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round1`.

## 1. Websearch findings + prior-art verdict

Source: `websearches/s6_local/batch_1/report.md` (5/5 iterations, cap hit; 15 WebSearch,
16 WebFetch, 10 successful). Verdict rows quoted verbatim from `## Prior-art verdict`:

- **D1** — "parallel local path (U-FNO U-Net path / NO-LIDK differential + local-integral
  kernels) inside the champion `mf_fno_transfer_film`, keeping its LF-pretrain -> HF-finetune
  schedule" | **preempted** (mechanism) | "Only the conjunction, and it is one step from
  overlapping author groups. **Propose D1 only as a MEASUREMENT of H2 (the s5-B1 framing),
  claiming no mechanism novelty.** Untested cell: sharp-2D MF fusion at N_hf = 5 against copy-LF."
- **D2** — "fidelity-asymmetric capacity: LF trains the spectral backbone; the ONLY HF-trained
  module is a small, capacity-constrained, zero-init **local** adapter" |
  **preempted-but-MF-composition-open** | "**Aligning the spectral/local inductive-bias split
  with the LF/HF data split** appears in no fetched source. It also carries a *published opposing
  prediction* (F-Adapter says capacity belongs in LOW bands) — a genuine pre-registered
  falsification risk, which is what makes it a real experiment."
- **D3** — "local corrector consuming the **real interpolated LF field at test time**, with an
  identity-to-copy-LF construction (zero-init gate => at init the model IS copy-LF)" |
  **preempted-but-MF-composition-open** | "A no-harm floor **defined by a real coarse PDE solve**
  (= round success criterion 2, skill < 1), plus the champion's blind spot that it never sees LF
  at inference. **Stream-boundary flag: `s2_beyond_copy`-B1 D2 already owns 'identity-to-LF';
  s6 owns only 'the corrector is LOCAL'.**"
- (anti-direction) pure local backbone replacement | **rejected on in-repo evidence**
  (`convnext_unet_film` 3.599 vs champion 1.526 on `ext__helmholtz_2d`).

Report's instructions to me (`## For the brainstormer`): do not claim the mechanism; the
surviving claim surface is fidelity-alignment (D2) + the no-harm floor (D3); the known-bad recipe
is "a free-form ConvNeXt/CNN refiner fine-tuned on the 5 HF samples"; "**Consume the given LF
field — do not predict it**" (removes the documented exposure-bias failure,
https://arxiv.org/pdf/2606.02661); scope the claim to sharpness, not displacement (displacement
is `s3_warp`); anchor 6.703, helmholtz floor 9.695 => no numeric claim there; ADR 0007 applies.

**Scouting websearch, merged in by coordinator direction**
(`websearches/_scouting/2026-07-29_stream_gap_mining/report.md`, row C1):

> **C1 Guaranteed-fallback, trust-gated MF fusion** — `y = LF_up + g ⊙ Δ(LF,X)`, `g∈[0,1]`
> per-pixel/per-band, `g≡0` at init reproduces copy-LF exactly | **preempted-but-MF-composition-open**
> | MAST https://arxiv.org/html/2602.20974 (GP, **scalar QoI**, no guarantee, ~2.04x worst case);
> physics-guided correction https://arxiv.org/html/2606.03469 (additive, **explicitly ungated**,
> **"no formal guarantee exists"**, physics prior); CV gating
> https://www.emergentmind.com/topics/learnable-skip-and-gate-fusion (hit); safe policy improvement
> (hit) | OPEN: a **field-valued per-pixel/per-band trust gate over the interpolated LF field inside
> a neural operator, parameterized so the scored copy-LF reference is exactly recoverable and is the
> initialization**. -> **NEW STREAM (rank 1)**. Unresolved threat to re-check: AGMF-Net (403)

Same class as D3; the scout independently reached it. Unresolved prior-art threat carried into
the card: **AGMF-Net** (https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X,
HTTP 403, "ensemble adaptive gated multi-fidelity NN", scalar per snippet) — the builder must
attempt a re-fetch and record the outcome. Scope hygiene from the coordinator: C2
(retrieval/exemplar residual banks) is **parked for batch 2** and must not enter B1.

**Operator correction (Eloise, mid-task) overriding the report's `## Diagnosis of the mentor's
FNO→CNN attempt`**: the mentor's FNO→CNN hybrid **and** iFNO **were actually trained**, off-repo;
code/results were likely never pushed to GitHub. The report's "It was never run" (inferred from
in-repo absence, program.md §13.2) is **wrong on that point**. Operative framing: *empirically
attempted, poor results per the mentor's own report ("not going well"), details unavailable*.
Consequences: (i) no part of my motivation may rest on "it was never tried"; (ii) the
literature-grounded known-bad recipe stands and is now weakly corroborated by the mentor's
experience; (iii) I must state the axes on which this design differs from the plausible naive
recipe rather than claim novelty by absence. D1/D2/D3 verdicts are unaffected — they rest on
fetched publications.

## 2. §12 conventions, verbatim

program.md **§12.6 `s6_local` (lever) — ADDED STREAM, see ADR 0011**:

> - **Question**: does adding a local representation (CNN/ConvNeXt branch,
>   local kernels) to the FNO fix sharp-2D fusion (hypothesis H2)?
> - **Anchor**: champion's certified panel geomean (batch 0).
> - **Motivating result**: s5-B1 (H1 test): modes_cap 12→32 improved geomean
>   0.507 < 0.884 floor (provisional-single-seed) — spectral capacity alone is
>   not the claimable lever.
> - **Priors to interrogate, not assume**: the mentor's FNO→CNN two-stage
>   hybrid attempt performed poorly (docs/reports/MF_FNO_CNN_Hybrid_Report.md
>   — batch-1 websearcher MUST read and the brainstormer MUST state the failure
>   mode); `convnext_unet_film` is rank-2 overall in the zoo but loses to
>   `mf_fno_transfer_film` on the panel (bench check 2026-07-29) — capacity is
>   not the question, composition is.
> - ADR 0009 applies (no physics at test time). ADR 0007 applies at the
>   brainstormer (propose 3-5 hybrid compositions, screen at contract tier).
> - Contract CLI unchanged; hybrids live inside the family dir.

Anchor: no `state/anchors/s6_local.json` exists; the lever-class anchor is the batch-0 champion
panel geomean, identical in `state/anchors/{s3_testtime,s4_hybrid_routing,s5_tuning}.json`:
**6.703016262587087** (`mf_fno_transfer_film`, ci95 [6.21853605194748, 7.102239525443188],
per_seed [7.1022, 6.2185, 6.7883], `provisional: false`).

`state/noise_floor.json` `min_claimable_effect` (skill units): helmholtz **9.694961**,
allen_cahn **1.633407**, pfc **1.151100**, cahn_hilliard **0.553347**, fisher_kpp **0.417735**,
ifc_poisson **0.239908**. Rule verified arithmetically against the file:
`mce = max(seed_spread, 0.10 × mean_skill)`. Geomean-level floor used by s5-B1 = **0.884**
(the anchor ci95 width).

## 3. Within-stream prior cards

**None.** `experiment_cards/s6_local/` does not exist (verified by `ls experiment_cards/`);
this is the stream's first card (ADR 0011, stream added 2026-07-29). No stream anchor file,
no prior brainstormer report for `s6_local`.

## 4. Cross-stream prior cards (light scan)

`experiment_cards/s2_beyond_copy/batch_1/B1.json` part 5 (diagnostic, COMPLETE, SLURM 65991328,
46 s on H100) is directly load-bearing:

- **M1 (decisive)**: `lf_at_inference = FALSE` for `mf_fno_transfer_film` on 5/5 datasets × 3/3
  seeds; `n_field_shaped_inputs_at_eval = 0`; "the only tensor entering the network at eval is the
  `[16, cond_dim]` condition vector". Verified independently against the source:
  `mf_field/factory_mffp/models/mf_fno_transfer_film/model.py::FNO2d.forward` lifts **coordinates
  only** and modulates by FiLM(X). The champion is an X->field generator; MF lives entirely in the
  training schedule (`smoke_eval.py`: LF-pretrain -> HF-finetune).
- **M2**: no predictor in the ladder beats copy-LF anywhere (min skill 3.980). `fisher_kpp` is at
  the X-only information floor (champion 4.179 vs meanfield 4.107, gap 0.070 << floor 0.418;
  `nn_over_random` 0.937, cond_dim 2). `pfc`: training buys nothing (champion 11.511 vs knn1
  11.299). `allen_cahn` / `cahn_hilliard`: training beats lookups.
- **M3**: `R_low > 1` on **5/5 datasets × 3/3 seeds** (11.18–209.56 on the four low-floor sets;
  1.23–8.63 helmholtz). "The excess over copy-LF is present in the LOWEST band. The failure is NOT
  high-k spectral localization." Secondary: "The champion injects spurious high-k energy that a
  lookup does not" (pfc bands 1/2/3 `R_b` = 2557 / 843 / 23.4).
- **M4**: the champion's error is nowhere interface-localized beyond ~1.3× area share.
- **M5b**: "NO dataset defect of the LF<->HF pairing kind" — §12.2's data-defect branch is CLOSED.
- Per-dataset facts extracted from the same part 5 (grid / cond_dim / n_train_hf / n_test_hf /
  copy-LF nRMSE): helmholtz 96²/3/400/100/0.329450; allen_cahn 256²/3/400/100/0.0161518;
  cahn_hilliard 256²/19/400/100/0.0876600; fisher_kpp 256²/2/400/100/0.0626323;
  pfc 128²/2/400/100/0.0447804. LF<->HF band coherence: fisher_kpp
  [0.9996, 0.9481, 0.8911, 0.0231] is the outlier — LF carries real information into band 2 there.

`experiment_cards/s4_hybrid_routing/batch_1/B1.json` — `fno_transolver_seq`: base = the champion
(X-only), plus a zero-init alpha-gated Transolver corrector on out-of-fold residuals; LF enters
only as a **context point cloud**, and the alpha=0 floor is *the champion* (geomean ~6.7). Stream
boundary: my design must differ by making the **base prediction itself the LF field** (floor 1.0)
and the corrector **local**.

`experiment_cards/s5_tuning/batch_1/B1.json` — modes_cap 12->32; geomean moved 0.507 < 0.884 floor.
Its `expected_falsification` is the prose template for floor-clearing thresholds.

## 5. Reopen candidates

**None.** No `s6_local` card exists, so no card carries `reopen_candidate: true` for this stream.

## 6. What is UNKNOWN

1. **What "adding a local representation to the FNO" even means for THIS champion.** M1 kills the
   naive reading: the champion has no field input, so a conv kernel has nothing to act on. A local
   operator needs a field, and the only field available at test time is the interpolated LF field.
   H2 is therefore not testable on the champion as-is without first deciding *what field the local
   branch reads*. Largest unknown; it forces the design toward D3/C1.
2. **Whether the low-band excess is a generation artefact or a fusion artefact.** `R_low` 11–209
   says the champion's field is wrong at the longest wavelengths, where 94–99.99% of HF energy
   lives; copy-LF has `R_low = 1` by definition. UNKNOWN: does a model that *inherits* the low band
   from the real coarse solve, instead of regenerating it, keep `R_low ~ 1` after training? No
   round-1 model has copy-LF as its base prediction, so this has never been measured.
3. **Whether a local corrector on the real LF field can beat copy-LF at all.** Success criterion 2
   still has zero models at skill < 1 on any of the five. UNKNOWN whether the residual
   `HF - LF_up` is learnable from `(LF_up, X, coords)` with a bounded receptive field. The
   residual's own spectral/spatial structure has never been measured (s2-B1 measured the
   *champion's error*, not the LF residual).
4. **Whether locality-as-spatial-kernel matters, or only pointwise recalibration.** s2-B1 M5a:
   amplitude is 69% of copy-LF's helmholtz error, and the champion systematically under-predicts
   amplitude on cahn_hilliard (alpha 0.76–0.78) and pfc (0.73). A 1x1 (receptive-field-1) corrector
   captures pure recalibration. UNKNOWN whether a 7x7 depthwise stack adds anything over it — and
   that comparison IS H2's real content.
5. **Whether the F-Adapter prediction transfers.** F-Adapter (https://arxiv.org/html/2509.23173v1)
   says scarce fine-tuning capacity belongs in LOW spectral bands; a local adapter is all-band and
   spatially restricted. UNKNOWN which wins here — a real pre-registered falsification risk.
6. **Whether a field-valued trust gate buys anything over one scalar.** The scout's C1 says the
   open composition is specifically a *per-pixel/per-band* gate. UNKNOWN whether spatial trust
   structure exists in this data (s2-B1 M4 found the champion's error is NOT interface-localized,
   which weakly argues against strong spatial structure — but that was the champion's error, not
   the LF residual).
7. **The N_hf regime is NOT what the s6 websearch assumed.** Measured: `n_train_hf = 400` on all
   five beyond-copy datasets (s2-B1 part 5). N_hf = 5 applies to **`ifc_poisson` only**
   (program.md §12.1; verified on disk: `data/ifc_poisson/train/fidelity_64/ys.npy` is
   `(5, 64, 64)`). The fetched overfitting sources therefore bind hardest on the ifc_poisson leg,
   not on the sharp five. UNKNOWN how much of the "free-form refiner overfits" prior survives at
   400 samples; capacity constraints are kept anyway (cheap, and the mentor's off-repo failure is
   weak independent corroboration), but justified per-dataset rather than by a blanket few-shot claim.
8. **`ifc_poisson` has no LF at test time.** Verified on disk: `data/ifc_poisson/test/` contains
   only `fidelity_64`; train has 8/16/32/64. Any LF-consuming model is structurally unable to run
   its LF path there. This forces an explicit, pre-registered fallback and makes ifc_poisson a
   no-op leg for this card.
9. **What the guard set does under an LF-based prediction.** `heat_local`, `fluid`,
   `sharp__sod_1d` all ship LF at test (verified: `test_l*.npz` present in each). A copy-LF-floored
   model should be guard-safe by construction; never measured.
10. **The gaming hazard.** With an identity-init gate, `skill <= 1.0` is reachable AT
    INITIALIZATION, so raw skill cannot be the win condition (coordinator direction). UNKNOWN
    until measured: how much the *trained* gate contributes over the identity path, and in which
    bands. That contribution — not the skill number — is what this card must report.
