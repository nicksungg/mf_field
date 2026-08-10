# Summary so far — stream `r3s4_audit`, entering batch 2

## Where the stream stands after batch 1

`r3s4_audit` is the diagnostics stream (program.md §4: "certify the repaired-panel mce and floors; run the training-free instrument audits; own the close-evidence audits of PROGRAM_NOTE MUST #3").
Batch 1 (`experiment_cards/r3s4_audit/batch_1/B1.json`) delivered the certification package and is `complete`.

Certification landed: per-dataset `seed_mce` / `tau_rel` / `tau_abs` were produced by the 3-seed `r3s4_cert_min` leg (panel 19.6438) and the resulting `noise_floor_candidate.json` (`_provisional:false`) is now installed as the round's certified noise floor at `state/anchors_repaired/noise_floor.json` (`state/orchestrator_flow.md`, 2026-08-10 item 7).
Any claim inside an anchor CI or below that floor is noise, not signal.

Pre-registered clause **F1** fired on the letter (ifc_heat `nn_condition` frozen-vs-stripped relative deviation 1.1056e-9 vs a 1e-9 tolerance) and was adjudicated **metrology-limited** (`orchestrator_adjudication_f1_2026_08_10` on the card); F2/F3/F4 confirmed.

## What the mechanism turns changed (source of batch-2 material)

`worktrees/r3s4_audit/B1/notes/handoff_experiment_mechanism_analyzer.md`, card parts 6-7:

1. **The wall-clock staleness rule is worthless.** Priced over 859 live legs, `train_seconds_collapsed` fires 104x, is the sole reason on 62 (all of which trained), and on the 20 ground-truth stale legs it is the sole reason 0 times. Route: delete. The only sound predicate is `executed_steps == 0 AND ckpt.data_binding[ds].train_sha256 != current`, i.e. a **content hash bound into the checkpoint**; mtimes cannot witness it (the STOP-THE-LINE #2 repair copy preserved them) and a global `--data-changed-after` cutoff flags 186-189 innocent legs. **Binding coverage today is 0/18.**
2. **Per-dataset F1 ULP-band tolerance table** (`scratchpad/turn2_loader_seam.json`): 4 of 10 datasets move off 1e-9 (fluid 1.005e-8, ifc_heat 7.854e-9, heat_local 5.457e-9, ifc_poisson 2.297e-9); the band must be defined as the cell's **ULP round-off band**, not the float64-vs-float32 path difference (identically 0 on natively-float32 cells). `sharp__sod_1d`'s band is 3.08e-1 — not a seam but a real instrument defect: `standardize_cond`'s `sd = where(sd>0, sd, 1.0)` guard is exact-equality-gated, so one ULP on a constant condition dimension (`dim2 == 1.4`) amplifies 8.4e6x and re-selects 53% of nearest neighbours. Guard-cell bounded; nothing shipped is wrong.
3. **`mdd_scored = 0` means unobservable, not zero.** On both ifc (paper-bar) cells the reference's own uncertainty is unmeasurable from this round's data, collapsing `tau_abs == tau_rel`; the round's own shipped bootstrap estimator puts the missing term at ~0.211 / ~0.153, i.e. `tau_abs` understated 2.17x / 2.15x. No live claim flips, but ifc_heat absolute-bar claims with |skill-1| in (0.164, 0.356) are licensed only by the certified constants.

## Contract changes already routed to batch 2

Per `state/orchestrator_flow.md` (2026-08-10, "Routed to batch 2"): F1 tolerances -> `max(1e-9, per-dataset ULP band)`; the **fair-comparison seam** (paired reference arms fit on 400 rows vs the scored arm's 320 — from r3s1's mechanism turn 3); **ckpt data-hash binding as the sixth-class check**; the LSI transfer-amplification instrument promoted from r3s2 (`tools/lsi_transfer_stability_audit.py`).

## Prior websearch state (batch 1) — do not re-derive

`websearches/r3s4_audit/batch_1/report.md` verdicts already on file: D1 (fused numerator+denominator claim threshold) `preempted-but-MF-composition-open`; D2 (floor certification incl. `affine_on_hf_train`) `preempted` — cite DeLise et al. 2025 (https://arxiv.org/abs/2508.05831); D3 (case-deletion influence on a benchmark cell) `preempted-but-MF-composition-open`; D4 (the preflight/HOLD architecture itself) `preempted` — XScientist (https://arxiv.org/html/2607.12301).
General ML provenance hashing is already cited as preempted via Tribuo (https://arxiv.org/abs/2110.03022).
Recorded dead ends not to re-run: degenerate-MF-row curation (three framings, search-negative); "MF benchmark reports reference uncertainty" (returns prediction-uncertainty work); training-influence functions (wrong target).

The two in-repo literature reports (`docs/reports/MF_Leaderboard_Beaters_2026_Report.md`, `docs/reports/MF_Sharp_HighFreq_Report.md`) are architecture/model-family syntheses with no audit-methodology content relevant to this stream; not cited further here.

## Open questions batch 2 must weigh with prior art

- **C1** Content-addressed binding of *training data* into *model checkpoints* as a staleness witness — is checkpoint-embedded dataset hashing published as an ML reproducibility mechanism (as opposed to pipeline/experiment-tracker provenance, already found preempted)?
- **C2** Certifying a **minimum detectable effect** for a benchmark cell whose *reference* uncertainty is unobservable (the `mdd_scored = 0` / published-paper-bar case) — is "compare against a published number with no error bar" treated anywhere as a licensing problem with a certified pair?
- **C3** **Numerical-precision-aware tolerance setting** (ULP-band analysis) for reproduction/regression checks in scientific ML benchmarks — plus the degenerate-zero-variance-feature standardization guard as an instrument defect class.
- **C4** (routed, secondary) The **fair-comparison sample-size seam**: reference/baseline arms fit on more rows than the scored arm.
