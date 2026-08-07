# Iteration 1 — `r3s2_field_reach` B1 design

## Design context considered

- `summary_so_far.md` §6 (unknowns 1-7) and the prior-art verdict quoted in §1.
- The stream directive: **batch 1 MUST be the stacking design (round-2 §12.2)** — FiLM-FNO pseudo-LF emulator (condition -> LF) feeding the best round-1 DC-lineage corrector, with frozen / fine-tuned / end-to-end arms, declared round-1 reuse role (a).
- The immutables block (§4.5 of my prompt, authority `round2/program.md` §5 + `round3/program.md` §5) — reproduced verbatim in the self-check below.
- Stream anchor: launch best-floor panel geomean **36.3912** (`state/anchors/launch_anchors.json`); per-dataset best floors pfc 48.0773 (train_mean), ac 475.8568 (nn_condition), fk 390.7015 (train_mean), ch 23.1803 (nn_condition), ifc_poisson 8.0409 (nn_condition), ifc_heat 1.3941 (nn_condition); mandatory ifc `affine_on_hf_train` 1.5938 / 0.9584.
- In-lineage comparator: **r2s2_stacked-B1 CERTIFIED at 27.5068** on this exact panel (per-seed 24.2391 / 22.3658 / 35.9154) — the round-2 stack already retrained on the repaired arrays. This is the pre-registered null the websearcher demands.
- Provisional noise floor (`state/anchors_repaired/noise_floor.json`, `_provisional: true`): pfc 8.8595, ac 16.4223, fk 158.3322, ch 1.1604, ifc_poisson 0.2399; **no ifc_heat, no panel-geomean entry**.
- Pre-falsified levers (round-1 §5): WNO backbone swap, LF low-mode freezing (`mf_fno_spectral`), diffusion prior for point accuracy.
- Generator ground truth read (read-only) for the IC parameterization: `mffp_sharp/common/ic_encoding.py::ic_2d/build_ic` (modes (kx,ky) in 0..m-1 minus DC, `f/(max|f|+1e-12)*scale`, m inferred from `2*(m^2-1)` coefficients) and the per-PDE use `ic_coarse = <level> + build_ic(coeffs, res_min, scale, ndim)` followed by `spectral_interp` to each rung (`pdes/{allen_cahn,cahn_hilliard,phase_field_crystal,fisher_kpp}.py`). **The IC is built on the coarsest rung and band-limited to <= 4 modes, so it is exactly evaluable analytically at any rung resolution.**

## Proposal reasoning

### The scientific question this batch can actually decide

Round 2 closed this stream on a *conditional* impossibility statement (r2s2-B3 part 7): *"If the missing variable really is the realised random initial condition (ADR r2-0003), then no architecture, capacity or budget can move this panel further."* Round 3 exports precisely that variable. The batch is therefore the direct test of round-2's terminal claim, which is also round-3's stream question ("can any architecture ... recover field-level structure beyond the scalar-deep law, or is the negative certifiable?").

The certified anchors already deliver half the answer and constrain the design: r2s2-B1 **retrained on the repaired, completeness-certified arrays** lands at 27.5068 — barely better than the best-floor anchor 36.3912 and worse than r2s3-B3's 15.5893. So exporting the IC coefficients into the condition vector did **not**, by itself, unlock the stack. Two mutually exclusive explanations remain, and no measurement separates them:

- **(H-info)** the information is there but the panel's residual structure is genuinely unreachable at this support (400 rows, median standardized pair distance 5.95-9.98 in 18-50 dims); or
- **(H-path)** the information is there but the **FiLM-on-condition conditioning path cannot read it** — round-2 measured that exact path collapsing to eff-rank 1.00/1.00/1.00/1.00 of 128 channels on a map that was demonstrably continuous.

The decisive intervention is a **front-end contrast at matched everything-else**: feed the emulator the IC *field* it would otherwise have to interpolate 16-48 coefficients into. The synthesis is closed-form, has zero learned parameters, uses only the condition vector, and is not a PDE solve (it is one trigonometric sum, band-limited to <= 4 modes) — explicitly in scope per `round3/program.md` §1.

### Alternatives weighed and rejected

1. **Literal round-2 replay (E0 front end only), scored as a completeness re-measurement.** Rejected as the *whole* card: it is exactly what the certified anchor r2s2-B1 already is, so it would spend a batch reproducing a number we hold at 3 seeds. Kept as the **in-job pre-registered null arm** (and a replication check on the anchor), which is what the websearcher asked for.
2. **Realisation-aware stochastic stage 1** (r2s2-B1 part 7 option A: sample from p(LF | c) instead of E[LF | c]). Rejected because under completeness p(LF | c) is a **point mass** — the entire motivation for a stochastic head evaporates when the realised IC is in the vector. Proposing it now would be re-proposing a lever whose premise the data repair removed.
3. **Re-exporting the coherence eligibility gate as a build/no-build precondition.** Rejected: r2s2-B2 stop-exported it (COARSE + PANEL_INCONSISTENT + MISCALIBRATED, its 0.05 relative-gain floor is 10-817x the certified mce). Kept only as a **directional, ensemble-centred, affine-ceiling** sidecar with a permutation null, never as a gate and never in a falsification clause.
4. **A condition->level (scalar) arm.** Rejected as belonging to r3s1 (factorised closed-form head) — r2s2-B3 part 7 hands that direction to a closed-form head stream, and duplicating it here would collide with r3s1's batch-1 mandate.
5. **Dropping `end_to_end` or `condmean_lf` to cut cost.** Rejected: the three stage-2 arms are directive-mandated, and `condmean_lf` is the zero-information null that makes "value of the emulator" decidable (round-2 §6 zero-information-null publication rule).
6. **Running the IC channel as a direct condition->HF model instead of inside the stack.** Rejected for this batch: the directive fixes the topology, and running it inside the stack additionally prices the corrector, which is the stream's second open question. If E1 wins, the direct-model version is the obvious B2 (recorded as such).

### Repairs to round-2 defects that the design must carry

- **Budget matching** (reviewer caveat F8): every arm spends the same total optimizer epochs; the frozen arm's extra `E_dc` is spent continuing its fit on **real** LF, so A2-A3 isolates the *data* the extra epochs saw, not the budget.
- **Paired-only reporting** (B1 anomaly 2): the panel geomean is reported all-6 *and* over the pairing-valid subset, because round-2's headline gain was entirely an artifact of one degraded column.
- **Pairing gate**: the ifc ladders are repaired; the gate stays armed and records `paired_real_lf` per dataset, and an unpaired column voids that cell's attribution rather than silently re-routing the fit.
- **Zero-information nulls**: the shuffled-IC front end (E1n) and the shuffled-coefficient cos sidecar publish the zero-information score of every diagnostic the card gates on.
- **Closed-form comparator**: `tools/zero_gradient_stage_ladder.py` prices the closed-form LSI alternative on the same intermediate out of fold before any trained stage is credited (B2 cross-stream note 3).
- **Registration**: no bare `F.interpolate`/`zoom`; the analytic IC channel is evaluated directly on each rung's node grid (no resampling of any dataset array), and the LF->HF lift keeps the vendored convention-keyed upsampler.
- **Target-scaler pre-flight** on pfc (round-2 §12; pfc is now the stiff crystalline box and `cell_stability` warns as priced).

## Proposal

- **Category**: `mf_composition / completeness-conditioned re-measurement of the condition->pseudo-LF->corrector stack, with an exact zero-parameter analytic IC-synthesis front end as the matched contrast (conditioning-path vs information attribution)`
- **Card type**: `model`
- **Motivation**: the prior-art verdict permits exactly this shape. D2 verbatim: *"`preempted (cite)` (mechanism); open only as a measurement ... Only whether completeness changes the round-2 **attribution** (99.98% stage-1 error; corrector worth 0.0061 units). A measurement of this benchmark, never a mechanism."* D1 verbatim: *"No fetched source uses a **fixed exact reconstruction of a known band-limited parameterization** as an internal zero-parameter layer, and **every** parameter-conditioned emulator found still consumes a field or state at inference."* The card claims the **regime + contrast + attribution**, never the architecture, exactly as the websearcher instructs.
- **Concrete config**: family `models_r3/r3s2_stack_ic`, vendored from `models_r2/r2s2_stack` @ `6b4e1d48` (which itself vendors round-1 `s4_router` @ `b90d4662`) with provenance headers. Emulator: FiLM-FNO, width 64, 4 blocks, 12 modes, target `lf_native` at `S6_LF_FID=max`, rel-L2 loss, one emulator per front end shared by all its stage-2 arms. Stage 2: vendored `dc_cleaned` (closed-form LSI Wiener `T(k)` + alpha line search including 0; `LocalCorrector` k7/d4/w32, zero-init head), lifted to the HF grid by the convention-keyed upsampler.
  Three front ends x stage-2 arms (10 arms total, one emulator training each for E0/E1/E1n):
  | front end | stage-2 arms | role |
  |---|---|---|
  | **E0** FiLM-on-condition only (round-2 replay) | emul_only, frozen, finetuned, end_to_end | pre-registered NULL; replication check against certified 27.5068 |
  | **E1** analytic IC channel + FiLM on non-`ic_*` dims | emul_only, frozen, finetuned, end_to_end | the contrast; **scored arm = `E1/frozen`** |
  | **E1n** E1 with row-shuffled IC coefficients | emul_only | zero-information null for the IC channel |
  | (front-end-free) | condmean_lf | ADR r2-0003 null; value of the emulator |
  IC synthesis: `ic_c*` indices resolved from the dataset's own `param_names`; the trigonometric sum evaluated analytically on each rung's node grid with the max-abs normalisation constant computed on `res_min` (bit-faithful to `build_ic` + `spectral_interp`, verified in-job to <= 1e-12 against the build-then-zero-pad path); `scale` set to 1 (a known global constant on an input channel) and recorded. On ifc_poisson / ifc_heat there are no `ic_*` dims, so E1 == E0 **by explicit record** (`ic_synth_applicable: false`), never silently.
  Mandatory reported arms on every cell: `nn_condition`, `train_mean`, `zero` from `state/anchors_repaired/floors.json`, plus `affine_on_hf_train` on both ifc cells.
- **Recipe**: see `report.md` (complete JSON, transcribed verbatim by the starter).
- **Expected outcome**: scored `E1/frozen` panel geomean **20-28** (point estimate ~25), i.e. Delta vs the launch anchor 36.3912 of **-8 to -16** skill units; the E0 arms reproduce the certified 27.5068 within its wide seed band [19.20, 35.82]. Per dataset, the discriminating prediction is `E1/emul_only` vs `E0/emul_only`: ch 11.09 -> 4-9 (Delta 2-7 vs 1.5 x provisional mce = 1.7406), ac 231.77 -> 140-215 (Delta 17-92 vs 1.5 x mce = 24.6334), pfc no resolvable change (stiff map, ~1e4 amplification; 1.5 x mce = 13.2893), fk undecidable (mce 158.3322 is ~79% of the cell's own value — reported, never claimed), ifc unchanged by construction. On the corrector I expect the round-2 null to **replicate**: best stack arm minus its own `emul_only` below 1 mce on all three decidable cells (round 2 measured 0.0061 on ch).
- **Expected falsification**: H — *"the round-2 stacking ceiling was caused by the realised IC being absent from the condition vector, so under the completeness-repaired panel an exact zero-parameter IC-synthesis front end reaches field structure the FiLM-only path cannot, and a realisation-faithful pseudo-LF restores the defect corrector's value"* — is FALSIFIED if **(F1)** `E1/emul_only` fails to beat `E0/emul_only` by >= 1.5 x the in-force per-dataset `min_claimable_effect` on at least 2 of {sharp__cahn_hilliard, sharp__allen_cahn_2d, sharp__phase_field_crystal_2d} (interim provisional thresholds 1.7406 / 24.6334 / 13.2893 skill units) **OR (F2)** the best stack arm fails to beat its own front-end-matched `emul_only` arm by >= 1.5 x that same effect on all three of those datasets — the two clauses are disjunctive and independently reportable, because round-2's conjunctive clause hid a decisive sub-failure (r2s2-B1 `falsification_verdict` reading).
- **Anchor reference**: `null` (gap-class stream, own-stream anchor implicit — round-3 policy for all four streams).

## Status

- Slot covered (1 proposal, `model` card).
- Skipped: no.
- Reopen candidates resolved: none exist (all 14 round-2 cards `reopen_candidate: false`; no round-3 cards yet).
- Immutables self-check: **pass (11/11)** — see below.

## Immutables self-check (positive evidence per item)

1. **Data read-only** — the card reads `stripped_data_root` train/test arrays through the frozen `round2/eval/panel_data.py` loaders only; the IC channel is synthesised in-memory from the `cond` array already on disk, N_hf stays 5 (ifc) / 400 (sharp), and no generator, regeneration or downsampling path is touched (§5.11 new-data ban respected: 400 aligned train samples only).
2. **Panel + guard fixed** — `datasets: "panel"` resolves to the 6 ADR-D4+A1 datasets; the guard set (`heat_local`, `fluid`, `sharp__sod_1d`) runs as the separate `--datasets guard` invocation recorded in the recipe `_note`, exactly as r2s2-B1 did.
3. **Eval layer / spec untouched** — the card requires zero edits to `round2/eval/` (score_panel.py takes `--family_dir` as a free path and `--env KEY=VAL`), to `project.yaml`, `program.md`, or any agent prompt; all new code lives in the worktree family dir.
4. **One nRMSE definition** — scoring goes through `score_panel.py` / `round2/eval/nrmse.py` unchanged (`nrmse_def_hash d3d0ade9...`); the emulator's rel-L2 training loss is a training loss, which the immutable leaves free.
5. **Contract CLI fixed** — `smoke_eval.py` keeps the six-arg signature (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`); every new knob is an `R3S2_*` env key listed in the recipe `env`, and the vendored `read_knobs` refuses unknown keys so a silent default is impossible.
6. **Seeds / tier fixed** — `seeds: [0]`, `epochs: 200` (project.yaml `smoke_epochs`); seeds 1-2 are the in-round confirm run only if the card becomes claimable (MUST #4); no 2500-epoch full tier is requested.
7. **Guarded factory surfaces untouched** — nothing under `mf_field/factory_mffp/{data,baselines,eval,references,scripts}`, `factory.md`, `akash/`, `mf_field_eloise_data` or `benchmark_42` generation code is written; `ic_encoding.py` / `spectral.py` were **read** and their math is re-implemented in the family dir with a provenance comment (the round-2 vendoring precedent).
8. **Checkpoint resume** — the vendored `train_stage` already resumes each stage from `<ckpt_dir>/last.pt` (`[resume] {tag} continues from epoch ...`); every new stage (E1/E1n emulators, the budget-matched extra `E_dc`) registers in the same per-stage checkpoint dict, keyed by `frontend|arm|stage`.
9. **Threshold exceeds the noise floor** — every cited dataset's threshold is **1.5x** its `min_claimable_effect`: ch 1.5 x 1.1604 = **1.7406**, ac 1.5 x 16.4223 = **24.6334**, pfc 1.5 x 8.8595 = **13.2893**, all strictly above the floor. `sharp__fisher_kpp_2d` (mce 158.3322) and `ifc_heat` (**no floor entry at all**) are deliberately excluded from both clauses and reported only. The clause is written against the floor **in force at analysis time** (r3s4-B1's certification if landed) with these provisional numbers quoted as the interim, per the `_provisional: true` discipline.
10. **Not a pre-falsified lever** — nearest is round-1's **LF low-mode freezing** (`mf_fno_spectral`: "worst on sharp, catastrophic on lid-cavity"). Difference: nothing here freezes or truncates LF modes; the LSI stage is a *fitted* per-band Wiener transfer with an alpha line search that includes 0, applied to a **pseudo**-LF the model generated from the condition, and no LF is present at test at all. The other two levers (WNO backbone swap, diffusion prior) appear nowhere in the design.
11. **Floor arms** — `R3S2_FLOOR_ARMS=nn_condition,train_mean,zero,affine_on_hf_train` puts every floor column in the diag next to every arm, and the falsification reasoning is denominated against them: the scored arm must be read against pfc 48.0773 / ac 475.8568 / fk 390.7015 / ch 23.1803 / ifc_poisson 8.0409 / ifc_heat 1.3941, plus the ifc affine floors 1.5938 / 0.9584 (round-3 affine-floor rule) — noting that the round-2 stack **loses** to the floor on ifc_poisson, ifc_heat and marginally pfc, so a "beats the anchor" panel number is not by itself a claim.
