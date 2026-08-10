# Iteration 1 — Stream `r3s2_field_reach`, Batch 2

## Design context considered

- **Prior-art verdict** (`websearches/r3s2_field_reach/batch_2/report.md`): E1 `preempted (cite)` — repair only; E2 `preempted-but-MF-composition-open (cite)` — *"the only direction with a genuinely unmeasured composition — build the card on it"*; E3 `preempted-but-MF-composition-open (cite)` — only the prospective paired application is open. Nothing `novel` (0-for-7).
- **§12 conventions** (summary §2). Decisive line, round-2 §12.2: *"Failure is informative: if pseudo-LF -> corrector loses to r2s1's direct models, the LF representation is not a useful bottleneck — that is the stream's falsification framing."* The stream's own conventions already name the route contrast as the falsification framing; B1 ran the stack without the direct comparand.
- **Immutables block §4.5 (verbatim, held in view throughout)**:
  1. Data read-only — no regeneration, no extra HF, N_hf fixed, LF never downsampled HF.
  2. Panel + guard set fixed for the round.
  3. Eval layer / spec untouched (no edits to `round2/eval/`, project.yaml, program.md, agent prompts).
  4. One nRMSE definition — training loss free, scored metric fixed.
  5. Contract CLI fixed — env knobs only via the recipe block.
  6. Seeds {0,1,2}, tier epochs fixed (contract 2 / smoke 200; full is post-round, human-approved).
  7. Guarded factory surfaces untouched (factory eval/baselines/references/scripts/data, factory.md, akash/).
  8. Checkpoint-resume from `<ckpt_dir>/last.pt` implementable.
  Plus round-2 §5.9-§5.13 (stripped test view; declared-reuse-only; no new HF data; floor arms mandatory; round-1/2 state immutable).
- **Stream anchor**: 12.9556 (`state/anchors/r3s2_field_reach.json`, 3-seed E1_frozen geomean, per-seed [10.7213, 10.3180, 17.8277]).
- **Certified noise floor** (`state/anchors_repaired/noise_floor.json`, `_provisional: false`): `tau_rel` ac 18.6198 / fk 10.3128 / ch 0.3612 / ifc_poisson 0.6910 / ifc_heat 0.1640; panel `seed_mce` 0.5083. `tau_abs` differs only for absolute-bar claims (r3s4-B1 part 7a: *"Same-reference comparisons (arm vs arm, or vs the affine floor) are unaffected — the bar cancels"*), which licenses `tau_rel` for a route contrast.
- **Certified floors** (`state/anchors_repaired/floors.json` + `launch_anchors.json`): nn_condition / train_mean / zero = ac 475.8568 / 486.4148 / 485.5883; fk 410.2818 / 390.7015 / 6051.5886; ch 23.1803 / 23.9691 / 23.9217; ifc_poisson 8.0409 / 9.0041 / 27.7778; ifc_heat 1.3941 / 1.7666 / 13.5135. `affine_on_hf_train`: ifc_poisson 1.5938, ifc_heat 0.9584.
- **Pre-falsified levers** (round-1 program §5, carried by round-2 §5): WNO backbone swap; LF low-mode freezing; diffusion prior for point accuracy. None is in this proposal.
- **ADR r3-0004**: pfc is report-only; *"Any falsification clause or threshold citing pfc is void for claim purposes"* — no clause below enumerates pfc.

## Proposal reasoning

### What B1 left on the table

B1's own part 7 is unusually specific: *"r3s2-B2 should be a ROUTE contrast, not another front-end contrast, and it should carry two repairs this card's mechanism analysis makes mandatory."*
The two repairs are (1) add the direct arm at matched total budget, (2) regularise `T(k)` before re-using the corrector.
The websearcher independently converged on the same pairing from the literature side: E1 is a repair (not a contribution), E2 is the open composition.
So the E1 repair and the E2 contrast are not two experiments — E1 is the **precondition** for E2 being interpretable, because B1's whole 3-seed panel spread is one unregularised band (M1). Running the route contrast on an unrepaired corrector would compare a direct head against a stack whose variance is an instrument artefact.

### Alternatives weighed and rejected

1. **Regularised-corrector card alone (E1 as headline).** Rejected: the verdict is explicit — *"Presenting ridge/band-limiting as the *idea* is a rebadge"* of 2606.03936 and classical regularised Wiener deconvolution. It also cannot advance the stream question; it only repairs a comparand.
2. **A capacity/conditioning card on `cahn_hilliard`.** Rejected on two independent grounds: the handoff's explicit caution (*"Do not propose a B2 that assumes capacity or conditioning will fix ch"*, M7, nn/random field-difference ratio 0.980) and the websearcher's item 5 (*"Do not spend the batch on cahn_hilliard capacity or conditioning, and say why with a citation"*). Its content is folded in as a **prospective** E3 clause instead, which costs nothing.
3. **An ifc-only card (selector between affine closed form and LF route).** Rejected as the whole slot: N_hf = 5 makes it anecdote-grade by round-2 §12.1, `mdd_scored = 0` on both cells removes absolute-bar headroom (r3s4-B1 part 7a), and E3 preempts the affine accounting as an instrument. Folded in as a **zero-GPU-cost LOO selector arm** inside the route card, which is where part 7 item (4) put it.
4. **A new decoder architecture (spectral/implicit/DeepONet).** Rejected: that is r3s1/r3s1-adjacent territory, and it would answer none of summary §7's unknowns; B1 established the bottleneck is the condition->field stage-1 map, which a route contrast isolates and a decoder swap confounds.
5. **End-to-end training of the stack as the primary contrast.** Rejected: B1 already ran `E1_end_to_end`; its apparent win was a shadow of the seed-2 defect (M1). Re-running it adds budget without addressing the open question.

### Why the composed design is the right single slot

The card measures ONE thing — *does the hallucinated LF intermediate earn its place in the graph at matched total optimizer budget* — with the corrector's known instrument defect repaired first, and it does so on a 2x2 (route x front end) so that "route" is never confounded with "IC channel".
The ifc cells give the contrast its sharpest form: the LF route's stage 1 trains on **18** LF rows while any direct head sees **5** HF rows (read from B1's diag JSONs), so if 2512.02868's data-scarcity prediction is right anywhere on this panel it is there — and B1 measured the stack losing a 5-row closed form on exactly those cells. That tension is the experiment.

## Proposal

- **Category**: `mf_composition/route_contrast_with_instrument_repair`
- **Card type**: `model`
- **Motivation**: the E2 verdict, verbatim: *"No fetched source runs a **direct parameter->HF arm against a coarse-intermediate arm at matched total optimizer budget where the coarse field cannot be produced at inference** ... The open question is exactly: *is the LF intermediate worth its place in the graph when it must itself be hallucinated from the condition?* Prior is two-sided — 2512.02868 predicts the stack wins, 2606.17460 + in-repo `MF_Sharp_HighFreq_Report.md` line 101 predict it loses, B1's F2 already measured no resolvable value"*. Paired with the E1 verdict's open piece: *"Only the **measurement**: that this published stack's whole panel-level 3-seed spread was 100 % attributable to an unregularised band above the LF Nyquist, and that a one-line ridge/band-limit removes it against the pre-registered prediction (ifc_poisson seed-2 2.041 -> ~0.171; panel range [10.32, 17.83] -> ~[10.3, 10.9])"*.
- **Concrete config**: new family `models_r3/r3s2_route`, vendored wholesale from B1's `models_r3/r3s2_stack_ic` @ `d5069a74` (front_end, ic_synth, lsi_filter, local_corrector, bands, periodicity, upsample, floor_arms, probes, sidecars, model, smoke_eval), with three additions:
  - **(i) LSI repair** — `S6_LSI_BANDLIMIT=lf_nyquist_from_ladder` (zero `T(k)` above `k_cut = k_Nyq_HF * N_LF/N_HF`, computed from the actual ladder shapes under the ADR r2-0001 registration conventions, recorded in the diag) and `S6_LSI_RIDGE=loocv` over the fixed grid `{0, 1e-6, 1e-4, 1e-3, 1e-2, 1e-1}`, selected by leave-one-out CV **on the fit fold only** (never val_a/val_b, never test; `S6_LEAKAGE_TRIPWIRE=1` already enforces this), per arXiv:1810.08360.
  - **(ii) direct route** — a `direct` arm: the same FiLM-FNO trunk and the same zero-parameter analytic IC-synthesis channel, trained condition -> **HF** on the HF train rows, spending `E_emu + 2*E_dc = 300` optimizer epochs (identical to what every stage-2 arm spends under `R3S2_BUDGET_MATCH=arm_equal_total`).
  - **(iii) accounting** — fractional-error-reduction columns beside skill (M5), 4-band error columns (Duraisamy reporting standard), a model-free map-smoothness sidecar on all 5 cells (the E3 instrument), a zero-GPU LOO selector on the ifc cells over {`affine_on_hf_train`, repaired stack, direct}, and a dataset content hash bound into the checkpoint (discharges r3s4-B1's open question at zero cost).
  - **Arms (7 scored + closed-form floors)**: `A1 stack_ic_reg`, `A2 stack_film_reg`, `A3 direct_ic`, `A4 direct_film`, `A5 stack_ic_unreg` (B1 replay, ridge 0 — repair attribution + replication check vs the 12.9556 anchor), `A6 ifc_loo_selector` (closed form, ifc only), `A7 emul_only_ic` (stage-1 reference), plus the mandatory floor arms.
- **Recipe**: see report.md (complete JSON).
- **Expected outcome**: (a) `A5` reproduces the stream anchor 12.9556 within 1 panel `seed_mce` (0.5083); (b) `A1` lands at panel geomean ~10.6 (per-seed ~[10.3, 10.9]) — a ~2.4-unit improvement on the anchor, 4.7x the panel `seed_mce`, essentially all of it ifc_poisson seed 2 (skill 56.69 -> ~4.75); (c) the route delta `A1 - A3` is genuinely two-sided; my own prior, weighting B1's M11/M12 over 2512.02868, is that the direct route wins on the ifc cells (where the stack loses `affine_on_hf_train` by 1.63x-35.6x) and is within +-1 `tau_rel` on ac and ch, with fk the least predictable cell; (d) `A4` should land near r2s1_direct-B2's certified 23.7753 as a cross-card calibration.
- **Expected falsification**: three independently reportable clauses — **G1 (route)**, **G2 (repair acceptance)**, **G3 (prospective approximability)** — full text in report.md.
- **Anchor reference**: `null` (round-3 gap stream; own-stream anchor implicit).

## Status

- Slot covered: YES (one model card).
- Skipped: no.
- Reopen candidates resolved: none exist (all four round-3 batch-1 cards `reopen_candidate: false`).
- Immutables self-check: **PENDING** -> run now.

## Immutables self-check (attempt 1)

1. **Data read-only** — the family reads only the frozen `stripped_data_root` mirror through `round2/eval/panel_data.py`; no generator call, no array write, N_hf stays 5 (ifc) / 400 (sharp), and the LF used at train is the dataset's own coarse solve at `S6_LF_FID=max`, never a downsample of HF. POSITIVE EVIDENCE: identical data path to B1, whose reviewer PASSed it and whose diag records `n_hf_train_samples = 5` / `n_fit = 320` unchanged.
2. **Panel + guard set fixed** — `recipe.datasets` is the literal ADR r3-0004 5-dataset string (`sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat`), and the guard run is a separate `--datasets guard` invocation (heat_local, fluid, sharp__sod_1d) exactly as B1. POSITIVE EVIDENCE: string copied from B1's `recipe.datasets`, which the orchestrator itself wrote under ADR r3-0004.
3. **Eval layer / spec untouched** — all new code lives in the worktree at `models_r3/r3s2_route`; scoring uses the frozen `round2/eval/score_panel.py` unchanged, with write roots redirected out of the frozen tree by the env vars B1's review-fix commit `d5069a74` introduced (`ROUND2_EVAL_RESULTS`, `ROUND2_EVAL_CACHE`). POSITIVE EVIDENCE: `git show --stat d5069a7` touches only `scripts/`, `notes/`, `scratchpad/` — no file under `round2/eval/`.
4. **One nRMSE definition** — the scored metric is `round2/eval/nrmse.py` (`nrmse_def_hash d3d0ade9...`, re-verified by B1's turn-3 probe); the training losses (`rel_l2` for the emulator and the direct head) are free by rule and are recorded separately. POSITIVE EVIDENCE: the def hash is asserted in the family's own provenance block, inherited unchanged.
5. **Contract CLI fixed** — `smoke_eval.py` keeps `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`; every new behaviour (`S6_LSI_BANDLIMIT`, `S6_LSI_RIDGE=loocv`, `R3S2B2_ROUTE`, the sidecars) is an env knob enumerated in `recipe.env`. POSITIVE EVIDENCE: the vendored `read_knobs()` already fails closed on unknown arm tags, so the builder cannot smuggle a flag past the recipe.
6. **Seeds / tier** — `seeds: [0, 1, 2]`, `epochs: 200` (smoke tier from `project.yaml tiers.smoke_epochs`); no full tier anywhere. Seed 2 is load-bearing (G2 is a statement about it), which is why all three are in the recipe rather than deferred. POSITIVE EVIDENCE: `project.yaml` `tiers: {contract_epochs: 2, smoke_epochs: 200, full_epochs: 2500}` and PROGRAM_NOTE MUST 4 (in-round confirm) are both satisfied by running 0/1/2 in-round.
7. **Guarded factory surfaces untouched** — nothing under `mf_field/factory_mffp/{data,baselines,eval,references,scripts}`, `factory.md`, or `akash/` is read-write; the IC-synthesis math is re-implemented from the read-only generator surfaces with provenance comments (never imported, never edited), exactly as B1 declared. POSITIVE EVIDENCE: B1's `_vendor_source` note records this arrangement and passed review.
8. **Checkpoint-resume** — every training leg (2 emulators, 2 direct heads, 2 corrector legs) writes and resumes `<ckpt_dir>/last.pt`; the direct head is a single-stage trainer, the simplest case. POSITIVE EVIDENCE: the vendored `smoke_eval.py` already implements per-stage resume for the emulator and corrector; the direct head reuses the same `train_stage` helper.
9. **Thresholds exceed the certified noise floor** — G1 panel leg 0.7624 > `seed_mce` 0.5083; G1 per-dataset legs 27.9296 / 15.4692 / 0.5419 / 1.0365 / 0.2460 vs `tau_rel` 18.6198 / 10.3128 / 0.3612 / 0.6910 / 0.1640 (each 1.5x); G2's ifc_poisson leg is a 1.54-nRMSE move (2.041 -> <= 0.50) = 42.8 skill units vs `tau_rel(ifc_poisson)` 0.6910; G2's spread leg 2.0 vs panel `seed_mce` 0.5083 (3.9x); G3's leg 0.5419 vs `tau_rel(ch)` 0.3612 (1.5x). ALL EXCEED.
10. **Not a pre-falsified lever** — nearest is none of {WNO backbone swap, LF low-mode freezing, diffusion prior}. The *closest* refuted object in our own record is the `ridge = 0` LSI corrector, which this card does not re-propose: it repairs it and uses it as a comparand, citing M1's falsification and stating the difference (LOOCV ridge + band-limit above the LF Nyquist).
11. **Floor arms in the falsification reasoning** — the clause text names the certified `nn_condition` / `train_mean` / `zero` values per cell and the `affine_on_hf_train` floor on both ifc cells, with the rule that an arm not beating the best of them on a cell contributes no claimable route delta there.

### Flags raised by the self-check

- **FLAG A (immutable 5.10, novelty guarantee / rebadge test).** The reviewer asks *"is this a rebadge of a round-1 family?"* on every card, and round-3 inherits it. The `direct_ic`/`direct_film` arms are structurally close to `r2s1_direct`'s FiLM-FNO condition->HF head. As written, iteration 1 does not say, on the card, what makes the family a new pathway rather than an r2s1 re-run with an extra channel. This is a real exposure and must be closed in the recipe/description, not left to the reviewer.
- **FLAG B (E1 framing).** Iteration 1's clause ordering lists G1 then G2, but the *prose* of the concrete config leads with the LSI repair. The verdict is explicit that presenting the regularisation as the idea is a rebadge. The card's hypothesis must be the route hypothesis, with G2 demoted in wording to an **instrument acceptance gate**, not a finding.
- **FLAG C (ifc read).** Iteration 1's expected outcome asserts a direct-vs-stack sign on ifc without recording that the two routes see different amounts of training data there (18 LF rows vs 5 HF rows). Reporting a route delta on ifc without that disclosure would be the same class of error as B1's F8 budget confound.

Self-check verdict: **REVISE** -> `iteration_2.md`.
