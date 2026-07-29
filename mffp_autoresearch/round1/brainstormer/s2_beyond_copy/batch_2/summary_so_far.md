# Summary so far — Stream `s2_beyond_copy`, Batch 2

## 1. Websearch findings + prior-art verdict

Source: `websearches/s2_beyond_copy/batch_2/report.md` (5 iterations, cap hit; 14
WebSearch / 12 WebFetch, 8 usable).

Verdict rows (from the `## Prior-art verdict` table):

- **(i)** LF field as an **input channel** to the FiLM-FNO backbone, predicting `hf - lf`,
  copy-LF added back -> **`preempted (cite)`**. Citations: LRC-FNO
  <https://arxiv.org/html/2606.17733> ("upsampled coarse solution ... concatenated as the
  input of the Residual-Closure FNO"; "adding the coarse solution and the residual
  correction"); MFFM <https://arxiv.org/html/2605.16118> (residual `u_HF-u_LF` "conditioned
  on u_LF"; **`FNO-residual` is one of its baselines**); Multifidelity DeepONet
  <https://arxiv.org/abs/2204.06684> ("residual learning and input augmentation").
  What remains open: "**Nothing at the mechanism level.** ... **Propose it as the missing
  literature-standard control**, given batch-1 F14 (0/27 families read the test LF field),
  not as a new model."
- **(ii)** Zero-parameter LF-keyed residual transfer as a **training-free floor** ->
  **`preempted-but-MF-composition-open`**. Ancestors: AtmoSwing analog method
  <https://gmd.copernicus.org/articles/12/2915/2019/> (retrieval keyed on coarse fields,
  Teweles-Wobus **S1 gradient** criterion), DeltaPhi <https://arxiv.org/pdf/2406.09795>,
  LOCA (search-listed), hybrid-MF overview
  <https://www.emergentmind.com/topics/hybrid-multi-fidelity-models> (corrector "often from
  a neural network, RBFN, or GP"), baseline discipline <https://arxiv.org/html/2508.05831>.
  Open: "transferring the **fidelity residual** (`HF-LF`) of retrieved neighbours onto the
  query's **own** coarse field ... used as a **floor in an MF operator benchmark**".
- **(iii)** Hybrid trained + retrieved residual under a blend weight ->
  **`preempted-but-MF-composition-open`**; open is "the **multi-fidelity binding** ...
  parameterized so copy-LF is exactly recoverable ... Thin, but the only arguable
  *mechanism* claim of the three."

Mandatory correction the card must carry (report "For the brainstormer" item 2):
batch 1's prior-art cell claimed no MF paper baselines against the interpolated LF field --
**MFFM's `Bilinear` no-learning baseline IS copy-LF**. The surviving gap is narrower: "no
fetched source *requires* the trained model to beat that baseline, and none reports a
dataset class where it cannot (our Class B)."

Two free design steals licensed by the report: (a) gradient-based (S1) retrieval key vs our
16x16 block-mean key; (b) LOCA region-then-local, i.e. per-patch retrieval.
ADR 0009 excludes every published hybrid corrector that needs the PDE residual at test time
-- retrieval is the compliant route.

## 2. §12 conventions (program.md §12.2, verbatim)

> - **Anchor: skill 1.0 = copy-LF.** The five datasets and their copy-LF test
>   nRMSE: helmholtz_2d 0.3295, phase_field_crystal_2d 0.0448, allen_cahn_2d
>   0.0162, fisher_kpp_2d 0.0626, cahn_hilliard 0.0877. Best zoo skills range
>   1.45–15.1 (§2.3) — every model DESTROYS LF information it was handed.
> - **Batch 1 is a diagnostic card** (pre-directed by the spec): localize where
>   and how models lose to copy-LF — per-frequency-band error vs copy-LF,
>   spatial error maps vs interface distance, error vs LF-HF residual magnitude.
>   Falsification framing: "the failure is concentrated in X" is falsified if
>   the error excess is spatially/spectrally uniform.
> - Candidate mechanisms for later batches (from the two literature reports):
>   additive-residual misalignment (the residual `HF−LF` is interface-hugging
>   and models blur it), rel-L2 blur preference, normalization destroying
>   amplitude structure, `modes_cap = 12` spectral wall on 96²–128² grids.
> - **Warning**: if the diagnostic finds LF/HF misalignment that looks like a
>   data defect, the honest output is a dataset bug report to the mentor, not a
>   model (spec §12).

Anchor file `state/anchors/s2_beyond_copy.json`: `anchor_type: copylf_bar`, `value: 1.0`,
`provisional: false`; certified batch-0 best skills helmholtz 13.817290, pfc 11.511001,
allen_cahn 16.334071, cahn_hilliard 5.533466, fisher_kpp 4.177355.

Noise floor (`state/noise_floor.json`, `min_claimable_effect` / raw seed `spread`):
helmholtz 9.694961 / 9.694961 - pfc 1.151100 / 0.082643 - allen_cahn 1.633407 / 0.014150 -
cahn_hilliard 0.553347 / 0.191827 - fisher_kpp 0.417735 / 0.091789.
Rescaled to a model living at skill ~= 1.0 (spread / certified skill): helmholtz **0.70166**
(nothing claimable), pfc **0.007180**, allen_cahn **0.000866**, cahn_hilliard **0.034667**,
fisher_kpp **0.021973**. Both framings are used in §4 of `iteration_1.md`.

## 3. Within-stream prior cards

`experiment_cards/s2_beyond_copy/batch_1/B1.json` — `s2_beyond_copy-B1`, diagnostic,
`status: complete`, `reopen_candidate: false`, `anchor_reference: null`.
Parts 5–7 (read in full) give the evidence base:

- **F14 / M1**: 0 of 27 factory families read the TEST split's LF field at inference; the
  champion's only eval input is `[batch, cond_dim]` (`n_field_shaped_inputs_at_eval: 0`).
  The champion also pretrains on `min(lf_fids)` while copy-LF uses `max(lf_fids)`.
- **F6 (headline)**: training-free `copy-LF + mean of the 5 nearest train residuals`, keyed
  on a 16x16 block-mean signature of the test LF field -> skill **0.562** (pfc), **0.625**
  (cahn_hilliard), **0.785** (helmholtz), **1.042** (allen_cahn), **1.062** (fisher_kpp);
  panel geomean **0.7886** vs certified champion **9.6362**.
- **F7**: the lever is the *query key* — the same machinery keyed on X gives 1.5413.
- **F9**: signature resolution converged by 16; no duplication leak (test->train NN distance
  ratio 1.31 / 1.00 / 1.00 / 0.99 / 1.00).
- **F11/F13**: the LF-keyed corrector has `R_b < 1` in every band on the three Class-A sets;
  on allen_cahn / fisher_kpp it *adds* error in every band (Class B).
- **Part 6 partition**: Class A (residual-learnable) = pfc, cahn_hilliard, helmholtz;
  Class B (residual-unlearnable at N=400) = allen_cahn, fisher_kpp, where "the honest target
  is MATCHING copy-LF, not beating it".
- **Part 7**: "build the missing family ... falsification clause should be anchored on the
  training-free floor ... a trained operator that cannot match a 5-NN lookup has a
  representation or optimization defect, not an information one."
- **Part 5 `do_not_promote`**: a training-free lookup "MUST NOT enter any leaderboard,
  anchor, or top-3 eligibility" — binding on this card's floor arms.

Promoted tools available to the builder: `tools/lf_conditioned_headroom.py` (the L5 rule,
verified to reproduce 0.5620 / 0.7851) and `tools/lf_at_inference_audit.py`.

## 4. Cross-stream cards (light scan)

- `experiment_cards/s6_local/batch_1/B1.json` (`status: drafted`, in build) — consumes the
  same real LF field (`LF_up = interp(field_by_fid[max(lf_fids)])`, `y = LF_up + G (*) Delta`)
  but owns the **LOCAL corrector + trust gate** question with a depthwise ConvNeXt-lite
  `C_theta`. Boundary: B2 stays on the **global spectral** substrate (the literature-standard
  FNO-residual control) and owns the *residual-learnability* question and the training-free
  floor discipline. No arm in B2 uses a local depthwise stack or a learned spatial trust gate.
- `s5_tuning-B1` (modes_cap 12->32, `status: analyzing`) — B2 pins `modes_cap = 12`
  (champion default) so the LF-input effect is not confounded with s5's knob.
- B1 part 7 `cross_stream_notes` flags F14 as round-wide: s3_warp, s4, s5, s6, s7 all train
  LF-blind families; B2 is the direct test of the implied fix.

## 5. Reopen candidates

None. `s2_beyond_copy-B1` is `status: complete`, `reopen_candidate: false`; it is the only
prior card in this stream, so there is nothing to retry or drop.

## 6. What is UNKNOWN

1. **Can a trained operator beat a training-free lookup on Class A?** F6 gives a lower bound
   with zero parameters (0.562 / 0.625 / 0.785). Nothing in the round measures whether an
   FNO handed the same input does better, worse, or the same. The three outcomes read
   completely differently: better => the trained operator extracts LF structure the 5-NN
   average cannot (success criterion 2 met on >=2 datasets); equal => the operator is a smooth
   interpolator of the same neighbourhood statistic; worse => representation/optimization
   defect on an input the information is demonstrably in.
2. **Does an LF-input residual model correctly no-op on Class B?** The zero-parameter rule
   *adds* error there (1.042 / 1.062). A trained residual head with a zero-init output can in
   principle learn ~0 and land at 1.00 — but MSE on an unpredictable residual usually returns
   a small non-zero conditional mean. Whether that costs >5% skill is unmeasured, and it is
   exactly the "graceful degradation" property the whole LF-input class needs.
3. **Is the query key the whole story, or only the coarsest version of it?** F7 shows key
   choice moves the geomean 1.5413 -> 0.7886. Untested: the analog literature's S1 **gradient**
   key and LOCA's **per-patch** key. If a better key moves the floor below the trained model,
   the discipline verdict flips.
4. **Does the fidelity ladder add anything past `max(lf_fids)`?** 4 of the 5 datasets ship two
   LF rungs (verified on disk this session: pfc 32²/64² -> 128²; allen_cahn, fisher_kpp,
   cahn_hilliard 64²/128² -> 256²; helmholtz only 24² -> 96²). Nobody has measured whether the
   coarser rung, or a coarse-pair residual pretraining stage, buys anything.
5. **Is the trained + retrieved hybrid more than the sum?** Direction (iii) is the only
   arguable mechanism claim, and it is untested in any framing the websearcher could find.
6. **Does helmholtz's amplitude pathology survive an LF input?** M5a: 86.5% of the champion's
   error is amplitude; 3% of samples carry 50% of copy-LF's error. Its floor (relative 0.70)
   makes it report-only regardless — but the *sign* of the effect is informative.
7. **Unknowable this batch**: everything is single-seed (ADR 0004), so effects below the
   rescaled floors above are noise-compatible and must not be claimed.
