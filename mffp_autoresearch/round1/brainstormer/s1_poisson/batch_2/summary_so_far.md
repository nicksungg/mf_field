# Summary so far — Stream `s1_poisson`, Batch 2

## 1. Websearch findings + prior-art verdict

Source: `${ROUND_ROOT}/websearches/s1_poisson/batch_2/report.md` (5 iterations, cap hit;
15 WebSearch, 12 WebFetch attempted / 8 usable).

Five verdict rows. The ones that govern this batch, quoted verbatim:

> **(i)** Per-level / per-fidelity **target** normalization (`MFFP_LADDER_SCALER=per_level`) in a
> pooled multi-level ladder | **preempted-but-MF-composition-open** | … | Per-level standardization
> of **targets pooled into ONE shared fidelity-conditioned operator**; no published effect size for
> the choice; nothing at N_hf = 5 on an elliptic ladder. Frame as a **hygiene fix measured as an
> ablation**, never as an invention.

> **(ii)** h^p-aware residual/target scaling as an explicit inductive bias (hard-coded h² divisor) |
> **preempted (cite)** | https://pmc.ncbi.nlm.nih.gov/articles/PMC11985099/ (fetched — GRE: b(x)=x^r
> in the kernel; "the normalized error (f(x)−f(0))/b(x) behaves regularly"; r estimated when
> unknown) … **Do not hard-code h²**; use the empirical per-level scaler and report the measured
> 4.379/4.196/4.120 ≈ 2² agreement as a result.

> **(iii)** The **factorial** `{shared, per_level} × {two_level, allpairs}` design itself | **novel**
> (design-level, weak claim) … Value is **internal validity** (separating the two contrasts B1
> conflated), not novelty. Claim "not previously ablated", never "novel method".

> **(iv)** Training-free level-matched nearest-condition lookup as a reported floor (0.24828) |
> **novel** for elliptic MF; report, do not claim

> **(v)** All-ordered-pairs composition … Batch 2 adds: NARGP-style recursive MF trains each level
> independently so "no information flows backward from higher to lower fidelities" (iteration_5) —
> the deficiency the pooled shared network is supposed to avoid, and a sharper motivation for
> `allpairs` than batch 1 had.

The batch's strongest empirical result is a *systematic absence*: "*five* fetched multi-fidelity
sources do not state their cross-fidelity normalization at all. The question is not buried in
appendices — it is **absent**." Framing upgrade offered (iteration_3/5): classical MF *models* the
level amplitude ratio as ρ (AR1 `y_high = ρ·y_low + δ`; NARGP input-dependent ρ_t(·)); B1's shared
scaler does neither — it leaves the 75.7× ratio in the targets and offers no ρ to fit, so per-level
scaling "implicitly restor[es] the ρ the pooled formulation deleted".

Two directions the websearcher explicitly fences off for this batch: the D2 telescoping /
control-variate direction (batch-1 `preempted`) and any seed-ensembling (collides with §4.4 / ADR
0004).

## 2. §12 conventions verbatim

From `program.md` §12.1 `s1_poisson` (gap):

> - **Bar**: paper 0.036 (IFC-ODE2); stretch IFC-GPODE 0.018. Current best zoo: 0.042
>   (`mf_fno_pinn_transfer`, factory bench). Anchor: `state/anchors/s1_poisson.json`.
> - **N_hf = 5.** Every claim is anecdote-grade by sample count; the CI + noise floor conventions
>   are the only defensible reporting. Prefer designs that reduce variance (ensembling across
>   seeds, all-pairs training) or add information (physics residuals) over designs that add
>   capacity.
> - Batch-1 seed direction: **all-pairs fidelity training** applied to the gap —
>   `mf_field/akash/models/mf_fno_allpairs` was the mentor's best on the hard subset (gm 0.0094 vs
>   FiLM 0.0121, FINDINGS.md); its known failure is O(L²) pair cost on many-level datasets (era5
>   timeout) — irrelevant here (ifc ladder L=4).
> - Physics fact: Poisson is elliptic with global coupling; the IFC papers' ODE/GPODE methods
>   exploit the fidelity-ladder structure directly.

And the §12 preamble:

> Common to all streams: quote these anchors verbatim when designing; thresholds must clear
> `state/noise_floor.json`; cite the websearcher's prior-art verdict; every proposal carries a
> complete `recipe` block.

Anchor (`state/anchors/s1_poisson.json`, batch-0, 3-seed, `provisional: false`): family
`mf_fno_transfer_film`, `best_skill_on_dataset` = **1.5656334** [1.4562, 1.6961] = nRMSE 0.056363
(skill vs paper bar 0.036, ADR 0002). Noise floor (`state/noise_floor.json`, `ifc_poisson`):
`min_claimable_effect` = **0.23990756 skill units = 0.0086367 nRMSE**.

**Unit trap to carry into the card**: the noise floor 0.23991 is in *skill* units; the training-free
matched-level floor 0.24828 is in *nRMSE* units (= skill 6.8967). The two numbers look alike and
mean unrelated things.

## 3. Within-stream prior cards

`experiment_cards/s1_poisson/batch_1/B1.json` — `status: complete`, `card_type: model`, category
`mf_composition / ladder-data-fusion`, build commit `d070f86` on branch `round1/exp-s1_poisson-B1`,
family `models_r1/mf_fno_ladder` (vendored from `akash/models/mf_fno_allpairs` @ `967562e`).

Part 5 (seed 0, 200 ep, one H100 job 65991280, 4.45 min for four arms, `provisional-single-seed`):
`two_level` nRMSE 0.102710 / skill 2.85306 (110 rows) · `adjacent` 0.217983 / 6.05510 (250) ·
`allpairs` 0.209275 / 5.81320 (280) · `legacy_pairing` 0.301027 / 8.36187 (280).
Verdict `cratered` (primary arm allpairs = 2.48× the 1.5× threshold) and `falsified`.
Positive result C1: the cross-row correspondence fix is worth **2.5487 skill units (10.6× floor)**.
C2a reversed the prediction: allpairs is **2.96 skill units WORSE** than two_level (12.3× floor),
125/128 per-sample paired wins for two_level, a near-uniform ~2× multiplicative degradation.
C2b (allpairs vs adjacent) = 1.008× floor, i.e. at-the-floor.

Part 6 mechanism (**amplitude-channel capture**, high confidence): the ladder's levels differ by a
clean ~h² law — per-level RMS|Y| 0.0245499 / 0.0056065 / 0.0013362 / 0.00032434 at fid 8/16/32/64,
consecutive ratios **4.3788 / 4.1957 / 4.1198**, 75.7× spread in RMS (42.1× in max|Y|). Stage 1
divides every row by ONE scalar `max|Y_all|` = 0.077146 taken from the coarsest level; stage 2
renormalizes by `scaler_hf` = 0.0018357 (ratio 42.06). **74.73 %** of allpairs' squared test error is
removable by a per-sample scalar gain (two_level 30.88 %); an oracle per-sample gain collapses the
2.04× arm gap to 1.13×; a single *global* oracle gain changes nothing (0.209275 → 0.210222). Retained
conditional variance ranks exactly as the arms do (0.8574 / 0.4408 / 0.4206 / 0.2652). After stage 2
no arm encodes more than a 3.5× f_tgt gain response against the data's 75.69×.

Part 6 turn 3 [REDUCED-CAPACITY PROXY: hidden 16 / 2 blocks / modes 8, joint 30 ep, ft 200 ep, 1 CPU
core, scratchpad-only, never a card number]: validity gate reproduced the production *ordering* with
attenuated magnitude (allpairs/shared 0.214313 vs two_level/shared 0.183150 = 1.17× vs production
2.04×). **The decisive intervention**: dividing each row by its OWN level's `max|Y|` takes allpairs
0.214313 → **0.087352** (2.45×), making it the best of the grid, **1.69× better than
two_level/per_level (0.147214)** — i.e. the intervention *reverses the sign of B1's central
contrast*. two_level gains only 1.24×. Matched step budget falsified the optimization-budget
alternative (allpairs j12 = 0.215912). Honesty flag: seed-1 replication incomplete (both allpairs
seed-1 runs killed at the 1200 s cap; two_level/shared/seed1 = 0.151104, so the proxy baseline spans
±10 % across two seeds).

Part 6 falsification postmortem: "The clause fired correctly as a PREDICTION test and incorrectly as
a MECHANISM claim." Part 7 `next_direction` prescribes exactly this batch: the 2×2 with the
normalization as the measured variable, **two separate clauses**, three reference lines carried.

Reference lines from part 6/7: anchor **1.5656** (nRMSE 0.056363); training-free nearest-condition
matched-8² predictor with one calibration gain **nRMSE 0.24828** (skill 6.8967) — better than three
of B1's four trained arms; HF-train-mean predictor **nRMSE 0.40343** (skill 11.2064); zero predictor
nRMSE 1.0.

Code-reviewer note S2 (`state/s1_poisson/review_B1.md`) pre-registered the amplitude confound before
launch and was right. S3: the minibatch generator is `torch.Generator().manual_seed(0)`,
seed-independent. S4: the cratered rule is scoped to the primary arm.

## 4. Cross-stream cards

Light scan of every card `part 7` for references to `s1_poisson` or to constraints relevant to it.
B1's own `cross_stream_notes` is the outbound traffic (shared-scaler trap; split the gap before
attributing it to architecture; dump predictions; quote a training-free floor; ifc levels are not
index-aligned). Two tools were promoted out of it and are live in `tools/`:
`ladder_level_diagnostic.py`, `field_error_decomposition.py`. **Inbound: none** — no other stream's
part 7 references `s1_poisson` or the ifc ladder (s2/s3/s4/s5/s6/s7 all target the sharp-2D panel or
the champion recipe). ADR 0009 (no known-physics at test time, batch ≥ 2) constrains this stream's
option space — it forecloses a Poisson-residual test-time lever — but does not bear on this
proposal, which is physics-free by construction.

## 5. Reopen candidates

None. `grep -l '"reopen_candidate": true' experiment_cards/*/batch_*/B*.json` returns empty across
all streams; s1_poisson-B1 is `status: complete, reopen_candidate: false`. Nothing to resolve.

## 6. What is UNKNOWN

1. **Does the per-level fix survive production capacity?** Every per_level number in existence is a
   hidden-16 / 2-block / modes-8 / 30-joint-epoch CPU proxy. The proxy's own validity gate shows it
   *attenuates* the shared-scaler gap (1.17× vs 2.04×), and it attenuates it mostly by making
   two_level *worse* (proxy 0.1832 vs production 0.1027) while allpairs is nearly unchanged (0.2143
   vs 0.2093). So the proxy→production multiplier is not a clean transfer: the arm that moved most
   between tiers is the one the composition clause compares against. This is the single largest
   quantitative unknown and any prediction must be stated as a range, not a point.
2. **Is the composition (pair-set) effect real once the normalization nuisance is removed?** B1's
   part 6 corollary says "the pair set was never the operative variable" — the card measured a
   level-set effect through a normalization defect. The websearcher's open composition (all ordered
   pairs, one shared net, N_hf = 5) has therefore **never been fairly tested**. Whether the 70 extra
   parameter points at fid 16/32 — which are *closer in condition space to the test distribution
   than the 5 HF training points are* (mean scaled NN distance 1.2145 / 1.4523 vs 2.0726) — buy
   anything at production capacity is unknown, and a single proxy run (1.69×) is the only evidence.
3. **Which of per_level's two simultaneous effects does the work?** Per-level scaling both (a)
   equalizes each level's contribution to the stage-1 MSE and (b) removes the 75.7× gain law from
   the function the network must represent. B1's mechanism claim is (b) ("amplitude-channel
   capture"); nothing in B1 separates them, because turn 3 changed both at once. T1's energy-share
   measurement (fid-64 share 0.0011158 in two_level vs 0.0018028 in allpairs) argues weakly against
   the naive "HF rows squeezed out" version of (a), but not against (a) generally.
4. **Does anything in this family reach the anchor?** The best B1 arm (two_level, 0.102710) is
   1.287 skill units = 5.4× the floor away from the anchor 1.5656. Even the best proxy per_level
   number (0.087352 → skill 2.43) is ~1.55× the anchor skill. Whether this family is structurally
   2–4× off the champion for reasons unrelated to the ladder is untested — B1 part 7 says that if
   batch 2 confirms the fix and still loses to the anchor, s1 should stop optimizing this family.
5. **Whether the h² agreement is a reportable finding.** The measured ratios 4.379 / 4.196 / 4.120
   sit within ~5 % of 2². The websearcher directs that this be *reported as a measurement*, never
   used as a hard-coded divisor (GRE preempts that). Nothing has yet been logged in a card as such.
6. **Stage-1/stage-2 interaction.** Turn 2 showed stage 2 destroys whatever level law stage 1 learned
   (3.5× residual response vs 75.69× in data). Under per_level normalization stage 1's targets no
   longer carry a level law at all, so the two stages should stop fighting — but that prediction has
   never been instrumented, only inferred. Nothing in the round has logged an f_tgt output sweep
   from a *production* checkpoint.
