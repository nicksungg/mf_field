# iteration_1 — s1_poisson batch 2 (slot design)

## Design context considered

- `summary_so_far.md` §6 unknowns 1–6, especially (1) proxy→production transfer, (2) whether the
  composition effect exists at all once the nuisance is removed, (3) which of per_level's two
  simultaneous effects does the work.
- Prior-art verdicts (i), (ii), (iii), (iv), (v) from
  `websearches/s1_poisson/batch_2/report.md` — quoted verbatim in §2 of the summary.
- program.md §12.1 verbatim (summary §2): N_hf = 5, "Prefer designs that reduce variance … or add
  information … over designs that add capacity"; anchor `state/anchors/s1_poisson.json`.
- The immutables block, program.md §5, verbatim (self-check below).
- Anchor **1.5656334** skill (nRMSE 0.056363); noise floor `ifc_poisson`
  `min_claimable_effect` **0.23990756 skill = 0.0086367 nRMSE**.
- Pre-falsified levers (program.md §5): WNO backbone swap, LF low-mode freezing (`mf_fno_spectral`),
  diffusion prior for point accuracy.
- B1 part 7 `next_direction`, which prescribes this card's shape, its two clauses, and the three
  reference lines.
- ADRs 0004 (seed 0 only), 0005 (H100, `--time=02:00:00`), 0007 (propose-many/screen-cheap),
  0009 (no known physics at test time), 0002 (paper_bar reference for `ifc_poisson`).
- Cost: B1 ran four 200+200-epoch arms in **4.45 min** on one H100 (per-arm 34–73 s train).

## Proposal reasoning

### The question this batch must answer

B1 produced one large, clean positive (the correspondence fix, 10.6× floor) and one refutation whose
*mechanism gloss was wrong*. Part 6 established, at reduced capacity, that the refutation was an
artifact of a shared target scaler fighting a 75.7× per-level amplitude law. Two things follow and
they must not be merged again:

- **N (normalization)**: does per-level target scaling fix the pooled ladder at production capacity?
- **C (composition)**: with N fixed, is the all-ordered-pairs pair/level set actually worth anything
  over the two-level control — i.e. is the websearcher's "open composition" (all ordered pairs, one
  shared net, N_hf = 5) worth anything at all?

B1's single clause conflated N and C, which is exactly why it "fired correctly as a PREDICTION test
and incorrectly as a MECHANISM claim" (B1 part 6 `falsification_postmortem`). The 2×2 factorial with
**two separate pre-registered clauses** is the minimal design that separates them. The websearcher
independently scores the factorial itself as verdict (iii) `novel` (design-level, weak) with the
directive: "Value is **internal validity** … Claim 'not previously ablated', never 'novel method'."

### Factor levels chosen

- `MFFP_LADDER_MODE ∈ {two_level, allpairs}`. Drop `adjacent` (B1 C2b: allpairs vs adjacent =
  1.008× floor, i.e. at-the-floor — it adds a cell that measures nothing) and drop `legacy_pairing`
  (its question, the correspondence defect, is already answered at 10.6× floor; re-running it would
  spend an arm on a settled result).
- `MFFP_LADDER_SCALER ∈ {shared, per_level}`. `shared` = B1's `max|Y_all|`, byte-identical default
  so the two shared cells double as a **reproduction gate**. `per_level` = divide each stage-1 row by
  its own **target** level's `max|Y|`, exactly the turn-3 intervention
  (`scratchpad/reanalysis_turn_3.py:114-127`).

### Alternatives weighed and rejected

1. **Hard-coded h² divisor** (scale row targets by (h_f/h_HF)²). *Rejected*: verdict (ii) is
   `preempted (cite)` by Gauss–Richardson Extrapolation, which "literally normalizes level
   differences by b(x)=x^r and estimates r when unknown". The websearcher's explicit instruction is
   "**Do NOT propose an h²-hardcoded scaler**". The empirical per-level scaler is the same fix
   without the assumption, and the measured 4.379/4.196/4.120 ≈ 2² becomes a *reported measurement*
   instead of an unpublishable assumption.
2. **A learned/estimated gain ρ head** (fit ρ(f) or ρ(x,f) as in AR1/NARGP). *Rejected for this
   batch, kept as a batch-3 candidate*: it is a new mechanism, it changes the architecture, and it
   confounds the very ablation this batch exists to run. The websearcher's framing — per-level
   scaling "implicitly restor[es] the ρ the pooled formulation deleted" — means the empirical scaler
   already occupies the cheap end of that axis. Measure the free version first; if it works, a
   learned ρ is the natural batch-3 escalation with a measured baseline to beat.
3. **Keeping `adjacent` and `legacy_pairing` for a 4×2 grid** (8 arms, ~10 min). *Rejected*: both
   cells' questions are answered; extra arms dilute the report and invite post-hoc arm-shopping.
4. **Seed ensembling / 3 seeds** (§12.1 does say "prefer designs that reduce variance … ensembling
   across seeds"). *Rejected*: collides with ADR 0004 (strict seed 0) and the websearcher explicitly
   fences it ("Two things to leave alone this batch: … any seed-ensembling (collides with §4.4)").
5. **Attacking the anchor directly** (port per-level normalization into `mf_fno_transfer_film`).
   *Rejected for this batch*: that family is two-level, so the amplitude law barely bites it; and it
   would be a champion-tuning card, which is s5's stream, not s1's.
6. **Telescoping / control-variate targets (D2)**: batch-1 `preempted`; websearcher says leave alone.
7. **Physics-residual information (Poisson operator)**: forbidden at test time by ADR 0009 for
   batch ≥ 2 models. Not proposed.

### The 5th arm, and why it earns its place

Per-level scaling changes **two** things at once (summary §6 unknown 3): it (a) equalizes each
level's contribution to the stage-1 MSE, and (b) removes the 75.7× gain law from the function the
network must represent. B1's mechanism claim ("amplitude-channel capture") is (b). Nothing in B1 or
in the proxy separates them.

Arm 5 `allpairs × shared_reweight` separates them: keep the **shared** scaler (so the target still
carries the level gain law — the network must still represent it) but weight each row's squared
error by `w_f ∝ (S/s_f)²`, normalized to mean 1 over the arm's stage-1 rows, so the per-level
*effective loss contribution* equals per_level's. This is not algebraically the same as per_level
(per_level changes the target function; shared_reweight only changes the loss weights), which is
precisely why it is a disentangler:

- if `shared_reweight ≈ per_level` → the effect is **loss weighting**, and B1 part 6's
  amplitude-channel-capture interpretation is wrong;
- if `shared_reweight ≈ shared` → the effect is the **target gain law**, and B1 part 6 is confirmed
  at production capacity.

Numerics check (so the builder/reviewer can verify, and so this arm is not a crash risk):
`S = max|Y_all| = 0.077146`; per-level `max|Y| = 0.0773 / 0.0237 / 0.0069 / 0.00184` at fid
8/16/32/64 → `(S/s_f)² = 1 / 10.6 / 125 / 1766`. In the 280-row allpairs set the target-level row
counts are 100 / 100 / 60 / 20 (fid 8/16/32/64), so the mean raw weight is
(100·1 + 100·10.6 + 60·125 + 20·1766)/280 = 157.1 and the normalized weights are
0.0064 / 0.0675 / 0.796 / 11.24. Dynamic range ~1766 — comfortably inside float32, no overflow risk.
Cost ~75 s. Arm 5 is **explicitly not part of either falsification clause**; it is an exploratory
mechanism measurement, and if it produced a non-finite loss that itself would be the reported
result.

Arm 6 (`two_level × shared_reweight`) is deliberately **omitted**: the mechanism claim is about the
pooled multi-level ladder, and two_level pools only the two extreme levels where the shared/per_level
gap is small (proxy 1.24×), so the cell would carry little information for the ~40 s it costs and
would blur the clean 2×2 + 1 structure.

### ADR 0007 reconciliation (required by the task)

ADR 0007 (propose-many / screen-cheap / promote-few) applies "for MODEL cards with genuine design
freedom". Its shape is: N *candidate mechanisms* compete, a 2-epoch screen discards the broken ones,
**one** is promoted to the single 200-epoch reportable run. **That shape is inapplicable here**, and
I choose the B1 sweep pattern instead, for three grounded reasons:

1. **The arms are not candidates; they are the levels of the two designed factors.** The scientific
   object is the *contrast between cells*, not any one cell. Promoting one arm would delete the
   experiment: you cannot measure `allpairs/per_level − allpairs/shared` with one arm.
2. **ADR 0007's cost rationale does not bite.** It exists because the H100 made cheap screens nearly
   free relative to a 200-epoch run. Here *all five* 200-epoch arms cost ~6 min total (B1: 4 arms in
   4.45 min) — cheaper than most single-arm cards on this program. There is nothing to economize.
3. **ADR 0007's own guardrail is satisfied differently but equivalently**: "The promoted variant's
   identity is fixed in the card BEFORE the 200-epoch submit (no post-hoc arm switching)." Here
   `_primary_arm = allpairs__per_level` is fixed in the recipe before submit, the two clauses are
   pre-registered on named cells, and **all five arms are reported** — so there is no silent drop and
   no winner's-curse arm-shopping. The contract-tier 2-epoch run still happens, as the §2.4 plumbing
   check on all five arms, and its numbers are never reportable (identical to ADR 0007 step 2's
   status for screens).

## Proposal

- **Category**: `normalization × composition factorial / ladder-data-fusion` (gap stream).
- **Card type**: `model`.

### Motivation

Prior-art verdict (i), quoted verbatim from `websearches/s1_poisson/batch_2/report.md`:

> **(i)** Per-level / per-fidelity **target** normalization (`MFFP_LADDER_SCALER=per_level`) in a
> pooled multi-level ladder | **preempted-but-MF-composition-open** | … Per-level standardization of
> **targets pooled into ONE shared fidelity-conditioned operator**; no published effect size for the
> choice; nothing at N_hf = 5 on an elliptic ladder. Frame as a **hygiene fix measured as an
> ablation**, never as an invention.

and verdict (iii):

> **(iii)** The **factorial** `{shared, per_level} × {two_level, allpairs}` design itself | **novel**
> (design-level, weak claim) … Value is **internal validity** (separating the two contrasts B1
> conflated), not novelty. Claim "not previously ablated", never "novel method".

B1 measured a level-set effect *through* a normalization defect: the family divides all pooled
stage-1 targets by one scalar taken from the coarsest, largest-amplitude level (`max|Y_all|` =
0.077146) while the ifc ladder's levels differ by a clean ~h² law spanning 75.7× in RMS (consecutive
ratios 4.3788 / 4.1957 / 4.1198). 74.73 % of the primary arm's squared test error is removable by a
per-sample scalar gain, retained conditional variance ranks exactly as the arms do, and a
reduced-capacity proxy showed the per-level scaler **reversing the sign of B1's central contrast**
(allpairs 0.2143 → 0.0874, 1.69× better than two_level/per_level). Classical MF *models* this level
amplitude ratio as ρ (AR1 `y_high = ρ·y_low + δ`; NARGP's input-dependent ρ_t(·)); B1's shared scaler
neither models it nor removes it, so per-level scaling implicitly restores the ρ the pooled
formulation deleted. This card measures that hygiene fix as an ablation and, in the same grid,
gives the websearcher's open composition its first *fair* test — motivated by (v): recursive
NARGP-style cascades train each level independently so "no information flows backward from higher to
lower fidelities", which is exactly what one shared pooled-row operator avoids.

### Concrete config

Family `models_r1/mf_fno_ladder_norm`, **vendored deterministically** from B1's build commit
(B2 gets a fresh worktree off `round1-substrate`, so B1's family is not present and must be
re-materialized). From inside the B2 worktree:

```
git checkout d070f86f18028893c59618c291e5bf4ab5c37dba -- models_r1/mf_fno_ladder
git mv models_r1/mf_fno_ladder models_r1/mf_fno_ladder_norm
```

Provenance pins to record in `build_notes` (sha256, first 16 hex, verified before any edit):
`backbone.py f56fa8029fad2ffb` (= `akash/common/backbone.py`, guarded tree untouched),
`model.py 740ed992efcda53e`, `smoke_eval.py a693d77909c14ccc`,
`manifest.json 849c8c390517ca9c`, `INSPIRATION.md 94e9ec5724215e81`.
Everything else (hyperparameters hidden 64 / blocks 4 / modes_cap 12 / batch 16 / lr 1e-3 & 3e-4 /
wd 1e-5 / clip 1.0, the `cond_from=target` correspondence fix, self pairs, the two-stage
200 + 200 schedule, the eval query `(X_test, f_src=0, f_tgt=1)`) is inherited **unchanged**.

**The only code change** — one new env knob `MFFP_LADDER_SCALER ∈ {shared, per_level,
shared_reweight}`, default `shared` (bit-preserving):

1. Replace the scalar at `smoke_eval.py:359` (`scaler = max(float(np.abs(Y_all).max()), 1e-8)`) with
   a per-row vector `scal` of shape `(M,1,1)`, and make `_train` divide by it — a shared and a
   per-level scaler then go through exactly one code path (the pattern already prototyped at
   `scratchpad/reanalysis_turn_3.py:68-69,114-127` on B1's branch).
   - `level_scaler[f] = max(|Y^{(f)}|.max(), 1e-8)` computed from the arm's stage-1 rows grouped by
     each row's **target** fidelity.
   - `shared`: `scal[i] = max_f level_scaler[f]` for all i — must equal `max|Y_all|` = 0.077146 to
     the last bit.
   - `per_level`: `scal[i] = level_scaler[f_tgt(i)]`.
   - `shared_reweight`: `scal[i] = max_f level_scaler[f]` (shared) **plus** a per-row loss weight
     `w[i] ∝ (S/level_scaler[f_tgt(i)])²` normalized so `mean(w) = 1`; loss becomes
     `mean(w_b · (pred − y/S)²)`. `w ≡ 1` in the other two modes.
2. Stage 2 is untouched (`scaler_hf = max|Y_ft|` = 0.0018357) — it is already a single-level stage.
3. **Carry B1's two build traps**: (a) the checkpoint key must include *both* factors —
   `<ckpt_dir>/mode_{MODE}__scal_{SCALER}/last.pt` with the existing meta-mismatch guard extended to
   the scaler; (b) the job script exports a per-arm `ROUND1_EVAL_RESULTS` so per-arm result JSONs and
   ckpt dirs cannot collide (`score_panel._run_one` derives paths from `(family_dir.name, dataset,
   epochs, seed)` only, so the arm is invisible to it).
4. **Score-neutral instrumentation** to add to the result JSON `extra` (all free, none touches the
   metric): (i) the per-level scaler values and per-target-level row counts; (ii) the measured
   consecutive per-level RMS ratios (expect 4.379 / 4.196 / 4.120 ≈ 2²) reported as the empirical
   h^p measurement per verdict (ii); (iii) an f_tgt output-RMS sweep over `f_tgt ∈ {0, 1/3, 2/3, 1}`
   on the test conditions from the final checkpoint (B1 T2 measured 3.4× against the data's 75.7×;
   under `per_level` this should collapse toward ~1×, which measures the amplitude-capture story
   directly instead of inferring it); (iv) keep B1's `preds_test.npz` dump (B1 part 7
   `cross_stream_notes` item 3 — it is what made B1's part 6 possible and cannot be recovered later).

**Five arms** (one SLURM job, seed 0, serial, ~6 min total):

| arm tag | `MFFP_LADDER_MODE` | `MFFP_LADDER_SCALER` | role |
|---|---|---|---|
| `two_level__shared` | two_level | shared | factorial cell (−,−); **B1 reproduction gate** (expect 0.102710) |
| `allpairs__shared` | allpairs | shared | factorial cell (+,−); **B1 reproduction gate** (expect 0.209275); F1 control |
| `two_level__per_level` | two_level | per_level | factorial cell (−,+); F2 control |
| `allpairs__per_level` | allpairs | per_level | factorial cell (+,+); **PRIMARY**; F1 and F2 treatment |
| `allpairs__shared_reweight` | allpairs | shared_reweight | mechanism disentangler; **in no clause** |

**Validity gate (not a falsification clause)**: the two `shared` cells must reproduce B1's seed-0
numbers within 10 % (`two_level` 0.0925–0.1130, `allpairs` 0.1884–0.2302). A miss means the vendoring
or the knob default changed inherited behaviour, and every contrast in the card is suspect — the
debugger should classify it ALGO and fix before any result is read.

### Recipe

```json
{
  "base_family": "mf_fno_ladder",
  "base_commit": "d070f86f18028893c59618c291e5bf4ab5c37dba",
  "family_dir": "models_r1/mf_fno_ladder_norm",
  "datasets": "ifc_poisson",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "MFFP_LADDER_MODE": "allpairs",
    "MFFP_LADDER_SCALER": "per_level",
    "_arms": [
      {"tag": "two_level__shared",          "MFFP_LADDER_MODE": "two_level", "MFFP_LADDER_SCALER": "shared"},
      {"tag": "allpairs__shared",           "MFFP_LADDER_MODE": "allpairs",  "MFFP_LADDER_SCALER": "shared"},
      {"tag": "two_level__per_level",       "MFFP_LADDER_MODE": "two_level", "MFFP_LADDER_SCALER": "per_level"},
      {"tag": "allpairs__per_level",        "MFFP_LADDER_MODE": "allpairs",  "MFFP_LADDER_SCALER": "per_level"},
      {"tag": "allpairs__shared_reweight",  "MFFP_LADDER_MODE": "allpairs",  "MFFP_LADDER_SCALER": "shared_reweight"}
    ],
    "_primary_arm": "allpairs__per_level",
    "_design": "2x2 factorial {two_level,allpairs} x {shared,per_level}, all four cells reported, plus one non-clause mechanism arm allpairs__shared_reweight. No screen-and-promote (see iteration_1 'ADR 0007 reconciliation'): the arms ARE the factor levels, all five are reported, the primary arm is fixed before submit.",
    "_sweep": "one SLURM job, seed 0, runs 5 score_panel.py calls serially, each with --env MFFP_LADDER_MODE=<m> --env MFFP_LADDER_SCALER=<s> and its own --out result_ifc_poisson_<tag>_s0.json; export ROUND1_EVAL_RESULTS=<outputs>/eval/results_<tag> per arm so per-arm result JSONs and ckpt dirs cannot collide (B1 build trap 1). Checkpoint path <ckpt_dir>/mode_<m>__scal_<s>/last.pt with the meta-guard extended to the scaler.",
    "_source": "vendored from branch round1/exp-s1_poisson-B1 @ d070f86 path models_r1/mf_fno_ladder (sha256-16: backbone.py f56fa8029fad2ffb, model.py 740ed992efcda53e, smoke_eval.py a693d77909c14ccc, manifest.json 849c8c390517ca9c, INSPIRATION.md 94e9ec5724215e81), renamed to models_r1/mf_fno_ladder_norm; the ONLY edit is the MFFP_LADDER_SCALER knob + the ckpt key + score-neutral extra{} instrumentation. akash/** and factory_root/{eval,baselines,references,scripts,data} are never touched.",
    "_sbatch": "partition gpu, --gres=gpu:h100:1 (ADR 0005), --time=02:00:00; B1 ran 4 arms in 4.45 min, so 5 arms is ~6 min (5 % of the request)."
  }
}
```

### Expected outcome

Metric: `ifc_poisson` test nRMSE → skill vs paper bar 0.036 (ADR 0002), **seed 0 only**, labelled
`provisional-single-seed` (ADR 0004). Noise floor **0.23991 skill = 0.0086367 nRMSE**.

Four reference lines carried in part 4 (McGreivy & Hakim 2024, https://arxiv.org/abs/2407.07218 —
79 % (60/76) of ML-beats-solver claims use a weak baseline — is the cited reason to carry them):
anchor **1.5656 skill / 0.056363 nRMSE**; noise floor **0.23991 skill units**; training-free
nearest-condition matched-8² lookup with one calibration gain **0.24828 nRMSE / 6.8967 skill**;
HF-train-mean predictor **0.40343 nRMSE / 11.2064 skill**. *Unit warning to print in the card*:
0.23991 is skill, 0.24828 is nRMSE — they are not comparable numbers.

Per-arm predictions. **Honest extrapolation label**: every `per_level` number below is extrapolated
from a **reduced-capacity, scratchpad-only proxy** (hidden 16 / 2 blocks / modes 8, joint 30 ep, 1
CPU core, seed 0, incomplete seed-1 replication) whose own validity gate shows it *attenuates* the
shared-scaler gap (proxy 1.17× vs production 2.04×) — and attenuates it mostly by degrading
`two_level`, the arm the composition clause compares against. Ranges, not points, are the claim.

| arm | predicted nRMSE (range) | predicted skill | basis |
|---|---|---|---|
| `two_level__shared` | 0.1027 (0.0925–0.1130) | 2.85 | B1 seed-0 reproduction |
| `allpairs__shared` | 0.2093 (0.1884–0.2302) | 5.81 | B1 seed-0 reproduction |
| `allpairs__per_level` | **0.085 (0.060–0.130)** | 2.36 (1.67–3.61) | B1 proxy ratio 0.408 applied to 0.2093 |
| `two_level__per_level` | 0.083 (0.065–0.115) | 2.30 (1.81–3.19) | B1 proxy ratio 0.804 applied to 0.1027 |
| `allpairs__shared_reweight` | 0.15–0.35 | 4.2–9.7 | expected nearer `shared` if B1 part 6 is right |

- **F1 (normalization)** predicted Δ = 0.2093 − 0.085 = **0.124 nRMSE = 3.45 skill = 14.4× the
  floor**; even the pessimistic end (per_level = 0.130) gives 0.079 nRMSE = 2.20 skill = 9.2× floor.
  This is the confident clause.
- **F2 (composition)** predicted Δ = 0.083 − 0.085 = **−0.002 nRMSE = −0.06 skill = 0.23× the
  floor** — i.e. *under my primary extrapolation F2 is predicted to FIRE (be falsified)*. The
  alternative extrapolation (transfer the proxy's per_level *gap* rather than each arm's ratio) puts
  allpairs at 0.049 and F2 at +0.95 skill = 4.0× floor. The two extrapolations disagree
  qualitatively; that disagreement is the reason this contrast is worth a run, and either outcome is
  decisive for the stream (B1 part 7: "If batch 2 confirms the fix and still loses to the anchor, s1
  should stop optimizing this family").
- **Cratered-verdict forewarning** (stated so nobody misreads the label): the cratered threshold is
  1.5 × anchor 1.5656 = 2.3485 skill = **0.084544 nRMSE**, and the primary arm's point prediction
  (0.085) sits essentially *on* it. This card will plausibly be marked `cratered` even if F1
  succeeds by 14× the floor. `cratered` is an anchor-relative bookkeeping label; the card's
  scientific content is the two internal contrasts, run with identical code, seed and
  hyperparameters. B1 was cratered and still produced the stream's best mechanism finding.
- **Guard set**: not owed unless an arm claims a panel win over the anchor. If `allpairs__per_level`
  lands below 0.056363 nRMSE (skill < 1.5656) the guard set must be run at contract tier.
- Wall clock: ~6 min/seed on one H100; `--time=02:00:00`.

### Expected falsification (TWO separate clauses — B1 part 7 requirement)

- **F1 — normalization contrast.** Falsified if `allpairs__per_level` fails to beat
  `allpairs__shared` on `ifc_poisson` test nRMSE by more than the certified noise floor — seed-0
  skill improving by ≤ **0.23991 skill units (≤ 0.0086367 nRMSE)** — which would mean the shared
  target scaler was not the cause of B1's ~2× degradation of the pooled ladder and B1 part 6's
  amplitude-channel-capture mechanism does not survive production capacity.
- **F2 — composition contrast.** Falsified if `allpairs__per_level` fails to beat
  `two_level__per_level` by more than the certified noise floor — seed-0 skill improving by ≤
  **0.23991 skill units (≤ 0.0086367 nRMSE)** — which would mean that even with the amplitude
  nuisance removed, the intermediate fidelities and the extra ordered pairs add nothing measurable
  over the 8²→64² transfer at N_hf = 5, and the websearcher's open composition is empirically empty
  on this ladder.

Neither clause references `allpairs__shared_reweight`; that arm is exploratory instrumentation for
the mechanism question and cannot falsify anything.

### Anchor reference

`null` — `s1_poisson` is a **gap** stream, so per program.md §4.5 the own-stream anchor
(`state/anchors/s1_poisson.json`, 1.5656334) is implicit and no card_id re-target applies (the
`card_id` form is reserved for `s5_tuning` batches ≥ 2 re-targeting the champion).

### Prior-art record for the card

`prior_art.verdict = "preempted-pivoted"` (the schema's nearest enum to the websearcher's
`preempted-but-MF-composition-open`, following the B1 precedent), with verdicts (i)–(v) quoted and
these fetched citations: https://arxiv.org/html/2605.07375 (QuadNorm),
https://www.sciencedirect.com/science/article/abs/pii/S0045782523007892 (CMAME multi-level NNs,
**snippet-grade, fetch 403**), https://smt.readthedocs.io/en/latest/_src_docs/applications/mfk.html
(AR1 ρ), https://pmc.ncbi.nlm.nih.gov/articles/PMC11985099/ (Gauss–Richardson Extrapolation),
https://arxiv.org/abs/2507.07292, https://arxiv.org/html/2602.01176v1,
https://www.frontiersin.org/articles/10.3389/fmats.2019.00061/full (the four/five MF sources that do
not state their cross-fidelity normalization at all), https://arxiv.org/abs/2407.07218 (McGreivy &
Hakim, weak baselines), https://arxiv.org/pdf/2306.03144 + https://arxiv.org/pdf/2105.01081 (NARGP,
search-return). The card must say "not previously ablated", never "novel method", and must present
`per_level` as a hygiene fix whose effect size is being measured.

## Immutables self-check (program.md §5 + two round-1 extras)

1. **Data read-only** — POSITIVE: the family only *reads* `ifc_poisson` through
   `load_mf_dataset` / the round eval layer's `panel_data.py`; no generation path, no new HF
   samples, N_hf stays 5, and no arm downsamples HF to make LF (the LF levels are the dataset's own
   coarse solves at fid 8/16/32). The one new computation over the data is `max|Y^{(f)}|` per level,
   a read-only statistic.
2. **Panel + guard set fixed** — POSITIVE: `recipe.datasets = "ifc_poisson"`, a member of the
   `project.yaml panel:` list; guard set is `heat_local, fluid, sharp__sod_1d` from project.yaml and
   is invoked only by the standard rule (run at contract tier if a panel win over the anchor is
   claimed). Neither list is edited or extended.
3. **Eval layer / spec untouched** — POSITIVE: the whole diff lives under the B2 worktree's
   `models_r1/mf_fno_ladder_norm/`, `scripts/`, `notes/`, `scratchpad/`; the proposal's only
   interface to the eval layer is CLI flags of `round1/eval/score_panel.py` (`--family_dir
   --datasets --epochs --seed --out --env`), which already exist. No edit to `round1/eval/`,
   `project.yaml`, `program.md`, ADRs, or subagent prompts is required for any part of the design,
   including the `extra{}` instrumentation (written by the family into its own result JSON).
4. **One nRMSE definition** — POSITIVE: every reported number comes from
   `score_panel.py`-produced JSONs carrying `nrmse_def_hash` (B1's was
   `d3d0ade9191c13bacc40702f3eb26ad290e01641cacee22a1d2233b74c035850`,
   `metric_source per_sample_mean`, `split test_hf`). The scaler knob changes only the **training**
   target normalization (training loss is explicitly free under §5 "What CAN be changed"); the model
   output is multiplied back by `scaler_hf` before scoring, so the scored quantity is the raw HF
   field prediction in every arm. `shared_reweight`'s weights live inside the training loss only.
5. **Contract CLI fixed** — POSITIVE: `smoke_eval.py` keeps the exact six-argument signature
   (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`); the new knob is an *environment
   variable* `MFFP_LADDER_SCALER`, declared in `recipe.env` (and in `_arms`), so it enters the eval
   cache key exactly as `MFFP_LADDER_MODE` did in B1 (B1 proved this: four distinct `code_hash`
   values in the four committed contract-smoke JSONs).
6. **Seeds and tier epochs fixed** — POSITIVE: `recipe.seeds = [0]` (ADR 0004 strict single seed) and
   `epochs = 200` = the smoke tier from `project.yaml tiers.smoke_epochs`; the contract-tier plumbing
   check uses `--epochs 2` = `tiers.contract_epochs`. No 2500-epoch run is proposed; `scripts/
   submit_seeds_2_3.sh` is still written, parameterized by seed, and parked for the end-of-round
   confirmation pass.
7. **Guarded factory surfaces untouched** — POSITIVE: the vendoring source is B1's *own worktree
   branch* commit `d070f86` (a round-1 artifact), not `akash/**`; `backbone.py` is carried at
   sha256 `f56fa8029fad2ffb` unchanged, which is the same hash the B1 reviewer verified against
   `akash/common/backbone.py`, i.e. the guarded file is only ever read. The single external import
   remains `factory_root/data_adapters` (the ungated read-only adapter every round-1 family uses);
   nothing under `factory_root/{eval,baselines,references,scripts,data}`, `factory.md`, or
   `mf_field/akash/**` is written.
8. **Checkpoint-resume from `<ckpt_dir>/last.pt`** — POSITIVE: B1's implementation already resumes
   from `<ckpt_dir>/mode_<arm>/last.pt` with finished / mid-joint / mid-finetune branches restoring
   optimizer, scheduler, generator state and `start_ep` (`smoke_eval.py:379-419, 286-291`, atomic
   `os.replace` save at `:257-262`), and the B1 reviewer verified all three resume paths against
   committed evidence JSONs. This card inherits that code verbatim and only *extends the key* to
   `mode_<m>__scal_<s>/last.pt` (plus a meta-guard field for the scaler), so resume remains
   implemented and is now safe against cross-arm checkpoint reuse in both factors.
9. **Falsification thresholds exceed the noise floor** — POSITIVE, with numbers: the only dataset
   cited is `ifc_poisson`, whose certified floor is `min_claimable_effect = 0.23990756` skill units
   (= 0.0086367 nRMSE at paper_bar 0.036). **F1** requires an improvement **> 0.23991 skill
   (> 0.0086367 nRMSE)** and is predicted at 3.45 skill (14.4× the floor; pessimistic end 2.20 skill
   = 9.2×). **F2** requires the same **> 0.23991 skill (> 0.0086367 nRMSE)**. Both clauses are
   written *as* strict-exceedance of the floor, so neither can be satisfied by a sub-floor effect.
   (F2's *predicted* effect is sub-floor — that is a prediction that the clause will fire, not a
   sub-floor threshold; the threshold itself is the floor.)
10. **Not a pre-falsified lever** — POSITIVE: nearest pre-falsified lever is **LF low-mode freezing
    (`mf_fno_spectral`)**, which freezes/copies the LF field's low Fourier modes into the prediction
    as an architectural constraint. This proposal shares nothing with it: no modes are frozen,
    copied or masked, `modes_cap` stays at 12 in every arm, and the intervention is a *target
    normalization statistic* applied before the loss, not a spectral inductive bias. The other two
    (WNO backbone swap; diffusion prior for point accuracy) are unrelated — the backbone stays the
    inherited FiLM-FNO and no generative prior appears. Nothing in the design re-proposes a falsified
    lever, and no falsified mechanism is being re-attacked, so the "cite the falsification and say
    what is different" clause is not triggered beyond this note.

## Status

- Slot **covered** — one proposal, `card_type: model`, complete recipe block.
- Skipped: no.
- Reopen candidates resolved: **none existed** (verified: no card in any stream carries
  `reopen_candidate: true`).
- Immutables self-check: **pass (10/10)**, positive evidence recorded for each above. No revision
  pass needed; no `iteration_2.md`.
