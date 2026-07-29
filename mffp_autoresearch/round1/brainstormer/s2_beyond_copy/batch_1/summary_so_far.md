# Summary so far — Stream `s2_beyond_copy`, Batch 1

Sources read (paths relative to repo root `/resnick/groups/Hippo/ezeng/mf_field`):
`mffp_autoresearch/round1/program.md`, `project.yaml`,
`websearches/s2_beyond_copy/batch_1/report.md`, `state/noise_floor.json`,
`state/anchors/s2_beyond_copy.json`, `state/gates.md`, `state/timing_ledger.json`,
`eval/{nrmse,panel_data,score_panel,make_copylf_baselines}.py`,
`eval/copylf_baselines.json`, `experiment_cards/SCHEMA.md`,
`mf_field/factory_mffp/models/mf_fno_transfer_film/{smoke_eval,model}.py`,
`mf_field/factory_mffp/models/mf_fno_pinn_transfer/smoke_eval.py`,
`mf_field/factory_mffp/data/*/meta.json`.

## 1. Websearch findings + prior-art verdict

`websearches/s2_beyond_copy/batch_1/report.md` ran the full 5-iteration cap
(15 searches, 8 usable fetches). Verdict row for the direction this batch owns
(D1, the copy-LF excess-error decomposition diagnostic): **`preempted-but-MF-
composition-open`**. Every *metric* is published — band-energy relative error and
the frequency-response lens (arXiv:2604.20061), banded `rFFT`/`H(k)`/coherence
(2606.03936), per-scale coherence (2605.26412), shock-window / gradient-weighted /
distance-stratified error (2510.17887), permutation feature importance (Molnar
ch. 23). What is open is **the reference and the setting**: no fetched source
decomposes error *relative to the model's own LF input*, and 2604.20061 names the
missing coarse-solution baseline as *"a notable gap"* in its own field.

Directives the report gives the brainstormer (report.md §"For the brainstormer"):
adopt the metrics by citation, never as novelty; design the diagnostic to
**separate three mechanisms** — (a) the model never uses the LF field, (b) the
excess is spectral, (c) the excess is interface-localized; make falsification
**structural / concentration-based**; keep the data-defect branch live with a
same-parameter-vector pairing sanity check; and **do not propose D3 (band-split)
before D1 reports**, because freezing LF low modes is adjacent to the pre-falsified
`mf_fno_spectral` lever (program.md §5).

## 2. §12.2 conventions (verbatim from program.md)

> ### 12.2 `s2_beyond_copy` (gap)
>
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

Anchor file `state/anchors/s2_beyond_copy.json`: `value: 1.0`,
`anchor_type: copylf_bar`, `provisional: false`, certified best skills
helmholtz 13.817, allen_cahn 16.334, cahn_hilliard 5.533, fisher_kpp 4.177,
pfc 11.511.

Noise floor (`state/noise_floor.json`, `min_claimable_effect`, skill units):
helmholtz **9.6950** (seed spread — a diverging seed; gates.md flags helmholtz
claims as unfalsifiable at smoke tier), allen_cahn **1.6334**, pfc **1.1511**,
cahn_hilliard **0.5533**, fisher_kpp **0.4177**.

## 3. Within-stream prior cards

**None.** `experiment_cards/` contains only `SCHEMA.md` (verified by
`ls -R experiment_cards/`); this is the stream's first card. Batch 0 is not a
card: it is the G3 anchor-certification array (job 65956106, 36/36 COMPLETED),
whose artifacts are `mffp_autoresearch_outputs/round1/batch0/eval/*.json` and,
importantly, **200-epoch checkpoints preserved at
`round1/eval/results/{mf_fno_transfer_film,mf_fno_pinn_transfer}/ckpt_<dataset>_e200_s{0,1,2}/last.pt`**
(730 MB + 658 MB on disk, verified present).

## 4. Cross-stream cards

**None** (no cards exist anywhere in the round yet).

## 5. Reopen candidates

**None** (no prior cards ⇒ no `reopen_candidate: true` entries).

## 6. What is UNKNOWN

**U1 — Do the certified models see the LF field at all at inference?** Reading
`mf_fno_transfer_film/smoke_eval.py` (eval loop: `xb = X_te[...]; model(xb) *
scaler_hf`) and `mf_fno_pinn_transfer/smoke_eval.py` (lines 212-214, same shape),
both certified families appear to be **X-only at inference**: the multi-fidelity
mechanism is the *training schedule* (LF pretrain → HF fine-tune), and no LF field
enters the forward pass. If true, "the model destroys LF information" is a
category error — the model was never handed the LF field at test time; copy-LF
sees the realization and the model does not. This is code-reading, not
measurement: it is unverified, and it is unknown how much of the 45-family zoo
shares the property (`transolver_residual` demonstrably does consume LF tokens at
inference — `model(list_of_lf_toks, hf_tok)` — and §12.4 records it as best-in-zoo
on 4 of the 5 beyond-copy datasets, which would be consistent).

**U2 — Is the condition vector a sufficient statistic for the HF field?** The
repo methodology rule says it must be ("those scalars + solver + snapshot time
fully determine the field"). But `data/*/meta.json` shows `sharp__fisher_kpp_2d`
`param_names = [D, r]` (2 scalars), `sharp__phase_field_crystal_2d` `[r,
mean_density]` (2), `sharp__allen_cahn_2d` `[eps, mobility, mean_composition]`
(3) — with no IC encoding — while `sharp__cahn_hilliard` carries 19 params and an
explicit note: *"IC-encoded cond (low Fourier modes) so field=f(x) is learnable;
fixes rel-L2>1 bug"*. That note implies the other three datasets may still have
random ICs that the condition vector does not encode. If so, an X-only predictor
is bounded below by the intrinsic spread over ICs, and no architecture can close
the gap to copy-LF. **This is the highest-value unknown and it is measurable
without training a single model.**

**U3 — Where does the excess error sit?** §12.2's three candidate localizations
(band, interface distance, LF-HF residual magnitude) have never been measured on
this panel. Critically, the *low-band* answer discriminates: a blur/spectral-bias
failure leaves low-k error at copy-LF level, whereas a wrong-realization failure
is large even at k→0. That single number gates D3 (band-split) for batch 2.

**U4 — Is `ext__helmholtz_2d` an information problem or a divergence?**
`state/noise_floor.json` records per-seed nRMSE 6.20 / 3.01 / 4.45 against a
copy-LF reference of 0.3295 — errors of 300-600%. Unknown whether that is
amplitude/normalization failure (the family de-normalizes by `scaler_hf = max|Y_hf|`)
or pattern failure. An optimal-scalar-rescale decomposition separates them and
costs nothing.

**U5 — Is the LF/HF pairing sound?** §12.2's data-defect branch and the
websearcher's point 7 both demand a same-parameter-vector check. Unmeasured; the
tiny copy-LF errors (allen_cahn 0.0162) argue against a gross pairing bug, but no
per-band coherence or cross-pair control has been computed.

**U6 — Are any of this reportable without the eval layer?** No: program.md §2.1
says every score flows through `eval/nrmse.py`. Any number computed ad hoc is a
prior, not a result.
