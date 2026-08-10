# Summary so far — stream `r3s2_field_reach`, entering batch 2

Written 2026-08-10, before any batch-2 search.
Sources read: `experiment_cards/r3s2_field_reach/batch_1/B1.json` (parts 5-7, `prior_art`), `worktrees/r3s2_field_reach/B1/notes/handoff_experiment_mechanism_analyzer.md`, `state/orchestrator_flow.md` (2026-08-10 entries), `state/anchors/r3s2_field_reach.json`, `state/anchors_repaired/noise_floor.json`, `websearches/r3s2_field_reach/batch_1/report.md`, and the two in-repo literature reports `docs/reports/MF_Sharp_HighFreq_Report.md` / `docs/reports/MF_Leaderboard_Beaters_2026_Report.md`.

## Where the stream stands after B1

B1 ran family `models_r3/r3s2_stack_ic` (FiLM-FNO condition -> pseudo-LF emulator -> vendored `dc_cleaned` closed-form LSI Wiener `T(k)` + `LocalCorrector`), 10 arms, 3 seeds, on the ADR r3-0004 5-dataset scored panel.
Stream anchor certified at panel geomean **12.9556**, per-seed [10.7213, 10.3180, 17.8277] (`state/anchors/r3s2_field_reach.json`), which beats the training-free launch best-floor 34.4198 with the whole interval below it.

Two pre-registered clauses resolved (orchestrator flow, 2026-08-10 batch-1 analysis wave, item 4):

- **F1 (IC-information reach) CONFIRMED.** The exact analytic IC channel is real information, not regularisation — its row-shuffled zero-information null is worse everywhere.
- **F2 (corrector clause) FALSIFIED decisively.** Stack value is unresolvable, 9-163x below one mce; round-2's `cahn_hilliard` null replicates.

## What the mechanism analysis added (the load-bearing part for batch 2)

1. **The reach effect is created entirely at stage 1** and nothing downstream can use it. Fractional emulator-error removal E0->E1 is 63.7% (ac) / 22.3% (ch) / 85.4% (fk); the stage-1 native-LF improvements (3.1x / 1.3x / 8.0x) reproduce the scored F1 ratios to 12%. The 59x ac-vs-ch skill gap is 20.3x copy-LF denominator x 2.14x real effect (card part 6, M5) — F1 must be reported in fractional units as well as skill units.
2. **The residual `cahn_hilliard` gap is approximability, not information.** Model-free map-smoothness probe: median relative HF field difference to the nearest condition-space neighbour, over the median random-pair difference, = 0.791 (ac) / 0.980 (ch) / 0.798 (fk). On ch the nearest condition neighbour is 98% as different as a random sample. The handoff states explicitly: do not propose a B2 that assumes capacity or conditioning fixes ch.
3. **The ifc_poisson seed-2 blow-up is a deterministic, unregularised deconvolution defect**, not seed sensitivity: the closed-form LSI Wiener `T(k)` is fit from `n_fit = 3` HF/LF residual pairs with `S6_LSI_RIDGE = 0`, and band 4 (the octave above the LF Nyquist, where LF carries no power) gives `T_band_mean_abs` 6.24 / 6.24 / **66.22**; 100% of the seed-2 error lands in that band (`band_contribution_profile` [.0012, .0272, .0763, **2311.94**]). Identical to 6 s.f. in the round-2 `r2s2_stacked-B1` anchor. **Cross-stream**: `tools/lsi_transfer_stability_audit.py` (promoted) also fires on the pfc anchor legs (|T| band-4 ~ 9.8-10.4) and the `fluid` guard cell (|T| band-4 = 15.2).
4. **Both ifc cells are closed-form tasks in disguise** (ifc_poisson oracle-affine residual 5.4e-16, rank 5 at 99% variance; ifc_heat affine to 0.0377) and every B1 arm lost `affine_on_hf_train`. `tools/task_linearity_audit.py` promoted.
5. **The corrector itself is fine; the front end is the bottleneck** — the same frozen corrector fed REAL LF beats the affine floors by 2.7x (ifc_poisson) and 16x (ifc_heat), while the stack loses them by 1.6x-36x. This is a distribution-shift statement about generated (pseudo-LF) vs real coarse-solve inputs.

Card part 7 names the B2 direction: a **ROUTE contrast** (direct condition->HF head at matched total budget vs the stack) carrying a **regularised / band-limited `T(k)`** repair with a pre-registered falsifiable prediction (ifc_poisson seed-2 nRMSE 2.041 -> ~0.171; panel 3-seed range [10.32, 17.83] -> ~[10.3, 10.9]), acceptance-checked with `lsi_transfer_stability_audit.py`.

## Certified thresholds now in force

`state/anchors_repaired/noise_floor.json` is no longer provisional (installed 2026-08-10, orchestrator item 7). Per-dataset `min_claimable_effect`: ac 18.6198, ch 0.3612, fk 10.3128, ifc_poisson 0.6910, ifc_heat 0.1640; panel `seed_mce` 0.5083. Both ifc cells certify `mdd_scored = 0.0` (unobservable; `tau_abs` understated ~2.15x) — an ifc claim needs care.

## Batch-1 prior-art record this loop must not re-derive

`websearches/r3s2_field_reach/batch_1/report.md` returned **no `novel` verdict**: D1 (internal zero-parameter analytic IC synthesis) `preempted-but-MF-composition-open`; D2 (stacked pseudo-LF -> corrector) `preempted (cite)`, open only as a measurement; D3 (certified negative) `preempted-but-MF-composition-open`. Its standing warning — "every parameter-conditioned surrogate found still consumes a field or state at inference" — is the stream's one live composition gap.
In-repo prior websearches to cite rather than re-derive: `MF_Sharp_HighFreq_Report.md` line 260 (fit the LF<->HF transfer kernel in one FFT pass, then unroll proximal-gradient steps with the FNO as learned prox — galaxy deblurring, arXiv:2211.01567), lines 224-230 / 293-297 (band-split at the LF/HF cross-spectral coherence < 0.7 cutoff — hard-constrain the low band, predict only k > k_c), and line 101 (the in-repo discrepancy/stack families already run on model-generated LF only and are weak — an in-repo prior negative for the stack route).

## Open questions batch 2 must price against the literature

1. Is **regularised / shrunk spectral transfer-function (Wiener) estimation from tiny samples** — ridge, band-limiting at the LF Nyquist, empirical-Bayes/shrinkage priors, coherence-gated band cutoffs — established methodology (so we may use it as an instrument fix but must not claim it), and is anyone doing it in a multi-fidelity correction stage at `n_fit ~ 3`?
2. Is the **route contrast** — direct parameter->HF vs stacked parameter->pseudo-coarse->corrector at matched budget — published as an ablation anywhere? Batch 1 looked for the attribution ablation and got "no usable results"; retry with corrector/emulator-cascade phrasing.
3. Is **approximability- vs information-limited residual attribution** (parameter-to-solution map non-smoothness / sampling-density limits, not missing input variables) established for parametric PDE surrogates? This is the honest reading of ch, and B1's model-free nearest-neighbour probe is the instrument.
