# MFFP Autoresearch — Update for Mentor (Round 3, Batch 1 Close)

Date: 2026-08-10. Author: Eloise (with the autoresearch orchestrator).
Authoritative sources: `round3/state/orchestrator_flow.md` (decision log), `round3/state/gates.md`, per-experiment cards under `round3/experiment_cards/`, `round3/index.md` (dashboard).
Companion to the 2026-08-02 update (round-2 results and the benchmark-repair pipeline are described there and are not repeated).

Rendered versions of this update:
[Claude artifact](https://claude.ai/code/artifact/a03c7fd2-cf39-42d6-8ec5-cf5ee44449cc)
(private until shared from its share menu) ·
[`PROFESSOR_UPDATE_2026-08-10.html`](PROFESSOR_UPDATE_2026-08-10.html) (same page, in-repo).
Companion decision page for §5.1: [ADR r3-0005 decision memo](https://claude.ai/code/artifact/df42daf9-e82d-4746-93f0-fe06e1b93e08).

## TL;DR

- **Round 3 launched 2026-08-05 on the repaired, completeness-certified panel; batch 1 (4 experiment cards, one per stream) is closed with every card at 3 seeds.**
  All four models beat the training-free floor anchor (34.4198 panel geomean skill, lower is better); the range is 11.08–24.96.
- **The round survived two stop-the-line integrity events, both caught by the system's own instruments.**
  First, the phase-field-crystal scored cell was found task-void (the coarse solve is spectrally converged to the fine one, so the certified reference was ~100% our own interpolation error) — pfc moved to report-only and the scored panel is now 5 datasets (ADR r3-0004).
  Second, a stale-checkpoint audit found that several launch-anchor cells had been re-*scored* on repaired data without being re-*trained* (the mandatory checkpoint-resume made the retrain a silent no-op) — 32 legs were quarantined and fresh-trained, anchors rebuilt, and a permanent gate now blocks the defect class at every anchor build.
- **The most consequential correction: r3s3's headline "LF-at-train improves the panel by 10.1% (ifc_poisson by 39%)" was entirely the stale-anchor artifact.**
  Against the repaired anchors there is no resolvable vs-anchor delta anywhere on that card (panel −0.81% at 0.08× the certified noise floor); the honest deliverable is its mechanism decomposition, which survived.
- **Mechanism findings replaced two pre-registered stories with sharper ones** (§2): the factorised head's discriminator is stage-1 residual saturation, not condition dimension; and the initial-condition "reach" effect lives entirely in stage 1 while the corrector stage is a certified null for the second consecutive round.
- **The audit stream certified the round's noise floor** (per-dataset minimum claimable effects now price every claim) **and priced the audit instruments themselves**: one staleness heuristic had 0 unique true positives against 62 false alarms in 859 legs and is being deleted in favor of content hashes bound into checkpoints.
- **Batch 2 is designed, reviewed, and launching now** (first two jobs on the cluster today); prior-art discipline held — nothing in 7 searched directions is claimed as novel, each card claims only its measured composition.
- **One decision is pending operator + mentor sign-off: ADR r3-0005** (re-point pfc's scored cell to the coarsest rung with a spectral reference — the only amendment to the frozen round-2 eval convention on the table). A plain-language decision page accompanies this update.

## 1. What round 3 asked, and how it ran

**Regime**: unchanged from round 2 — models see LF fields only during training; at test they receive the condition vector alone (the stripped view physically omits test LF).
Round 3 runs on the repaired benchmark: completeness-certified condition vectors (the IC coefficients are now *in* the vector, so ADR r2-0003's stochastic-map caveat is retired), repaired nested IFC ladders, and `ifc_heat` promoted to the scored panel.
Scored panel after ADR r3-0004: `allen_cahn_2d`, `fisher_kpp_2d`, `cahn_hilliard`, `ifc_poisson`, `ifc_heat` (helmholtz and pfc report-only).

**Scale so far**: 4 streams (factorised heads / IC reach / value-of-LF / audit), 4 batch-1 cards closed at 3 seeds each, 5 ADRs, 7 new probe tools promoted, ~2 days of stop-the-line repair in the middle, and the full websearch → pre-registered design → build → adversarial review → GPU → two-stage analysis pipeline on every card.
The certified noise floor is no longer provisional: r3s4-B1's certification (per-dataset `seed_mce` / `tau_rel` / `tau_abs`, panel `seed_mce` 0.5083) was installed 2026-08-10 and prices every claim below.

## 2. Round 3 batch-1 results (condition vector → HF; no solver at test)

Leaderboard (3-seed panel geomean skill, lower is better; training-free floor anchor 34.4198):

| Rank | Card | Panel geomean [3-seed range/CI] | Verdict | What it is |
|---|---|---|---|---|
| 1 | r3s3-B1 LF-channels | **11.0789** [10.84, 11.25] | confirmed (mechanism card) | Budget-matched ±LF contrast; **no resolvable vs-anchor delta after the repair** — the value is the decomposition |
| 2 | r3s2-B1 IC-stack | **12.9556** [10.32, 17.83] | F1 confirmed / **F2 falsified** | IC information helps (stage 1); the corrector stage is unresolvable — round 2's null replicates |
| 3 | r3s4-B1 certifier | **19.6438** [19.42, 19.93] | F2–F4 confirm; F1 fired at metrology margin | The round's certified noise-floor source |
| 4 | r3s1-B1 two-stage factorised head | **24.9573** [24.87, 25.07] | confirmed (L1/L2/L4) | Closed-form condition→coefficient cascade; win is one cell (cahn_hilliard) |

Headline mechanism results (each from a causal probe, not a hunch):

- **The factorised head's discriminator is stage-1 residual saturation, not condition dimension.**
  The controlled pair: allen_cahn and cahn_hilliard share cond_dim 19, yet their stage-2 margins differ 47×; fisher_kpp has the largest cond_dim (50) and the smallest margin.
  What separates them is how much predictable energy stage 1 leaves behind — and on fisher_kpp the head's loss to the affine floor is a hyperparameter clip (`SELECT_MAX = 32` strands 0.0713 of condition-reachable energy; the head is *better* than affine inside its selected subspace, losing 17× more outside it).
  The cahn_hilliard win is broad-based (78–82 of 100 rows improve; survives an adversarial 10-row trim at 2.9–3.2× the certified floor), not outlier exploitation.
- **The IC-reach effect is created at stage 1 and is approximability-limited, not information-limited.**
  Fractional emulator-error removal: 63.7% (allen_cahn) / 22.3% (cahn_hilliard) / 85.4% (fisher_kpp); the zero-information IC null is worse than the no-IC control everywhere, so the effect is IC *information*.
  The residual cahn_hilliard gap is approximability: its nearest-condition neighbour is 98% as different as a random sample.
- **The corrector stage is dead weight, decisively, for the second round in a row**: the best stack arm beats its own front-end-matched emulator-only control by 9–163× *less* than one minimum-detectable effect; round 2's 0.0061 null replicates at 0.0056 [0.0053, 0.0061].
  Its one dramatic failure (ifc_poisson seed-2 nRMSE 2.04 vs 0.15) was root-caused to a deterministic instrument defect: an unregularised spectral Wiener transfer fit from **3** samples amplifying 66× in a band where the LF carries no power — the identical mode as round 2's anchor instability, and the same audit tool flags the pfc anchor legs and the `fluid` guard cell.
- **LF-at-train's value is identifiability supply, quantified.**
  The covered-input control arm (extra LF only at parameters HF already covers) learns the *same function* as the no-LF arm (as-functions distance ratios 0.098–0.307); supplying new distinct condition rows accounts for E_cov/E_total ∈ [0.972, 1.024] on 30/30 cells.
  Recovery is a near-deterministic function of a measurable intermediate (condition-response alignment, Pearson r = 0.985) — batch 2 tests whether that mediator makes the LF-row ↔ HF-row exchange rate a law.
- **A seed-invariant hard subpopulation exists on cahn_hilliard**: 27 of 100 test rows whose conditions are indistinguishable from training (max gap 0.45σ, nearest-neighbour ratio 1.02) but whose fields are 3.29× farther — and LF-at-train specifically repairs them (92 of the no-LF arm's worse-than-zero rows; 97% of that pair's gain).

## 3. Benchmark-integrity findings (the part most relevant to the benchmark paper)

- **The pfc scored cell was task-void** (stop-the-line #1, 2026-08-07): the eval convention scores at `max(lf_fids)` = 64²→128², where the crystalline fields are band-limited below the coarse Nyquist — exact per-row copy gap ≤ 1.66e-6 on all 100 test rows.
  The certified reference 0.018257 was ~100% linear-interpolation error of the frozen lift.
  The real fidelity gap lives at 32²→128², which the convention never scores; the rung-convention mismatch is how the box-swap repair certified.
  Interim resolution: pfc report-only, 5-dataset scored panel (ADR r3-0004); the durable repair is ADR r3-0005, pending sign-off (§5).
- **Checkpoint-resume can silently void a re-score campaign** (stop-the-line #2, 2026-08-08): re-scoring anchor models on repaired data resumed completed checkpoints (`resumed_from_step = 5000`, train 1.3–2.9 s), so pre-repair weights were scored on post-repair arrays.
  Every existing hash/floor seam passed, because references recompute live while only the weights were stale.
  Blast radius: launch-anchor ifc_poisson columns (and, found later by the audit stream's tooling, 18 report-only pfc legs); round-3's own experiment legs audited clean (0/225).
  Repair: 32 legs quarantined + fresh-trained, anchors rebuilt with the diff confined to the contaminated columns, and a stale-checkpoint gate now runs inside the anchor builder.
  Notably, fresh training *improved* every contaminated anchor — the contamination had been biasing comparisons in the flattering direction.
- **The audit instruments were themselves priced** (r3s4-B1 mechanism): the `train_seconds` staleness heuristic contributes 0 unique true positives and 62 false alarms over 859 legs (strictly dominated by checkpoint-mtime evidence) and is being deleted; file mtimes are *not* a witness (the repair copy preserved them); only a content hash bound into the checkpoint separates a train-invalidating mutation from a benign test-split trim.
  Checkpoint↔data binding coverage today: 0/18 — building that instrument is r3s4's batch-2 card.
- **Tolerance-setting now has a measured metrology floor**: r3s4's F1 clause fired at 1.106e-9 against a 1e-9 tolerance — ~70× *below* the float64→float32 loader seam's own spread — and the per-dataset ULP-band analysis shows the correct tolerances range from 2e-9 to **0.31** (sod_1d, where an exact-equality `std == 0` guard amplifies one ULP 8.4e6×; guard-cell bounded, nothing shipped is wrong).
  Batch-2 contract change: floor F1-class tolerances at max(1e-9, measured per-dataset band).
- **`mdd_scored = 0` means unobservable, not zero**: on both ifc cells the reference's own uncertainty cannot be observed from this round's data, understating `tau_abs` ~2.15×; no live claim flips, but absolute-bar claims in the affected band are licensed by the certified constants only.

## 4. How the harness itself is performing

- **Throughput**: batch 1 closed at 3 seeds on all four streams in ~5 days wall clock, of which ~2 were the stop-the-line repair; batch 2 went websearch → brainstorm → pre-registered card → build → adversarial review → first SLURM jobs in under a day.
- **The discipline is doing its job in both directions**: the pre-registration + certified-floor rules turned two would-be headlines into precise retractions (r3s3's −10.1% panel "win"; r3s1's cond_dim mechanism story), and the adversarial reviews caught real defects pre-submission (a falsification clause gated on the wrong statistic; an admission rule differing measurably from its pre-registered prose, adjudicated *ex ante* on the card before any result existed).
- **Honest accounting**: the only numbers called certified carry the r3s4 certification; every retraction is annotated in place on the card with the historical numbers preserved; the prior-art record across 7 batch-2 directions is 0-for-7 on outright novelty and is reported that way, with each card claiming only its measured composition.
- **Autonomy**: the launch orchestrator session died 2026-08-08; a fresh session resumed from state files losslessly, executed the repair under the standing delegation (with the stop-the-line held for operator adjudication per the global rule), and has run the round since.
  One operational note: the cluster's SLURM job-ID space reset mid-round (8-digit → 5-digit IDs); job accounting was re-anchored and old IDs still resolve.

## 5. Gated next steps

1. **ADR r3-0005 (pfc spectral-rung repair) — RATIFIED 2026-08-10, option A** (Eloise, deciding for the mentor); phase 1 executed, phase 2 gated on batch-2 compute close.
   Two inseparable changes: serve pfc rungs {1, 3} so the scored cell becomes 32²→128² (where the measured per-row gap is real: mean 0.0124, 0/100 task-void), and give the copy-LF reference a pfc-specific spectral lift (the linear lift's error at 32²→128² is ~0.07, which would again swamp the ~0.012 true gap).
   The measured caveat, stated up front: the repaired cell is outlier-dominated (top-5 rows carry 38.8% of the denominator; min-detectable delta **65.8%**), so it returns to the panel as an honest but low-resolution cell — every claim on it must be priced against that MDD.
   Alternatives on the table: keep pfc report-only permanently (conservative, loses the panel's only stiff-map dataset), or regenerate with a higher-resolution ladder (most compute; the sweep suggests the same convergence reappears one rung up, since the crystal wavelength, not the grid, sets it).
2. **Batch 2 completes**: 4 cards through the SLURM → analysis pipeline (first two seed-0 jobs running as of this update).
3. **Round-1 2500-epoch full runs** — still on hold (unchanged).

