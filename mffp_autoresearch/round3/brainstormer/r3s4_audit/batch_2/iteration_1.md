# Iteration 1 — r3s4_audit, batch 2

## Design context considered

**Prior-art verdicts (verbatim, `websearches/r3s4_audit/batch_2/report.md` "Prior-art verdict" table).**

- **B2-D1** — *"ckpt<->train-data **content binding** as the sixth-class check: `executed_steps == 0 AND ckpt.data_binding[ds].train_sha256 != current`; train/test hashed **separately**; delete `train_seconds_collapsed`; coverage 0/18 -> measured"* -> **`preempted-but-MF-composition-open (cite)`**.
  Open column verbatim: *"Published halves: cryptographic dataset<->checkpoint attestation (adversarial), position-state binding (duplicate consumption), invariant-based silent-error detection (in-process correctness), structural staleness propagation (no hash). **Open**: the scoring-correctness predicate itself; **separate train/test hashing** as the discriminator between the 18 pfc (train box swap => invalid) and 18 allen_cahn (test trim => valid) legs — uncited anywhere; and the empirical rule pricing on a scored MF corpus (859 legs, 20 ground-truth stale). **Caveat**: the build-system framing failed twice with a tool error — retry in batch 3 before any novelty language ships."*
  Citations: Atlas https://systex-workshop.github.io/2025/papers/systex25-final68.pdf; Check-N-Run https://www.usenix.org/system/files/nsdi22-paper-eisenman.pdf; TRAINCHECK https://www.usenix.org/system/files/osdi25-jiang.pdf; dataflow staleness https://arxiv.org/pdf/2302.14556; Tribuo https://arxiv.org/abs/2110.03022.
- **B2-D2** -> **`preempted (cite)`**. Open column verbatim: *"Methodologically **nothing**. `mdd_scored = 0` is the 'no-imputation' approach the review explicitly discourages; 'certify the pair, use the max' is conservative imputation + sensitivity analysis. Only the project-local instantiation is ours: the paper bar as a missing-variance case, and the licensing bands ifc_heat (0.164, 0.356) / ifc_poisson (0.691, 1.483). **Adopt with citation; do not claim.**"*
  Citations: Batson et al. https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0164827; paired-MDE budget https://arxiv.org/html/2605.28873; paired bootstrap https://arxiv.org/html/2511.19794; Bradley et al. 2008 (snippet).
- **B2-D3** -> **`preempted-but-MF-composition-open (cite)`**. Open column verbatim: *"Tolerance-by-ULP-with-absolute-floor: standard engineering. The `sd == 0 -> 1.0` guard: sklearn's documented idiom, verbatim. 'Test instability' (round-off flipping control flow): a named formal class with a proven warning transformation. **Open**: that a *frozen benchmark reference floor* is the output of an unstable test — measured 3.08e-1 relative move, 53 % NN re-selection, 8.4e6x amplification, invisible to every hash/seam check. Adopt Titolo's remedy shape (drop/flag the degenerate dim, warn on divergence), never tune the tolerance."*
  Citations: Titolo et al. https://arxiv.org/pdf/1808.04289; scikit-learn StandardScaler; MathWorks ULP docs (snippet).
- **B2-D4** -> **`preempted-but-MF-composition-open (cite)`**. Open column verbatim: *"Architecture- and tuning-effort matching is canonical ('comparing against an untuned baseline ... is as good as no comparison at all'). **Open**: fit-set-size matching between a reference arm and the scored arm. **Anti-citation**: the engine's 'matched-n subsample protocol' phrasing is grep-negative in the only fetched candidate (https://arxiv.org/pdf/2606.02959) — must NOT be cited."*
  Citation: Brigato et al. https://arxiv.org/pdf/2108.13122.

**Unknowns driving the design** (summary_so_far §7): (1) role-resolved binding is undecided and is the MF-specific increment; (2) no labelled corpus exists on which any staleness rule's false-positive rate can be measured; (3) the ULP-band estimator's own reproducibility is unmeasured; (4) the sod_1d remedy's no-op-ness elsewhere is unmeasured; (5) the fit-set seam has never been read against the certified `tau_rel`; (7) binding coverage is 0 everywhere and the writer has never been built.

**Certified noise floor** (`state/anchors_repaired/noise_floor.json`, `_provisional:false`, installed 2026-08-10):

| dataset | `seed_mce` | `tau_rel` (= `min_claimable_effect`) | `tau_abs` | `tau_abs/tau_rel` |
|---|---|---|---|---|
| sharp__allen_cahn_2d | 13.2135 | **18.6198** | 58.8109 | 3.1585 |
| sharp__fisher_kpp_2d | 5.8550 | **10.3128** | 72.7743 | 7.0567 |
| sharp__cahn_hilliard | 0.0912 | **0.3612** | 22.4171 | 62.0544 |
| ifc_poisson | 0.5868 | **0.6910** | 0.6910 | 1.0000 |
| ifc_heat | 0.1333 | **0.1640** | 0.1640 | 1.0000 |
| panel geomean | 0.5083 | — | — | — |

Launch anchor: best-floor geomean **34.4198** on the 5-dataset scored panel (`state/anchors/launch_anchors.json`). Stream anchor for r3s4 is B1's certification package itself (panel 19.6438, certifier context only).

**Routed contract changes** (`state/orchestrator_flow.md`, 2026-08-10 "Routed to batch 2"): *"(a) r3s4 contract — fair-comparison seam (paired reference arms fit on 400 rows vs scored arm's 320; worth 27% of ac's affine gap), F1 tolerances -> max(1e-9, per-dataset ULP band), train_seconds rule deletion, ckpt data-hash binding (coverage currently 0/18)"*.

**Pre-falsified levers (program.md §5 / round-2 §12)** re-read at design time: registration-of-lifts, zero-information nulls, matched-procedure arm comparisons, target-scaler pre-flight, the "unidentifiable" phrasing rule, the zero-information-null publication rule. None of these is a lever this proposal re-proposes; three of them are *reused as design constraints* (see the self-check, item 10).

## Proposal reasoning

### Alternatives weighed

**A. "Value-of-LF accounting with matched with/without-LF-training arms"** (the §4.2 menu option, also §12.4's later-batch direction). Rejected for batch 2, not on merit but on ownership and timing: `r3s3_lf_value` batch 2 has been routed the seam-invariant 27-row ch hard mask (flow 2026-08-10 item (b)) and is running exactly the matched-arm optimisation; §12.4's own division of labour is *"r2s4 measures, r2s3 optimizes"*, and measuring before r3s3's B2 lands would price a superseded arm. It also does not consume a single one of the four routed contract changes, all four of which are this stream's to close, and success criterion 2 (a certified matched-arm LF measurement on >= 3 scored datasets) is licensed by constants only this stream can certify. Deferred to batch 3 with r3s3-B2's arms in hand.

**B. "Overfitting anatomy at N_hf = 5"** (the §4.2 menu option). Rejected: the ifc ladder at N_hf = 5 is precisely where the affine-floor rule (program.md §2) says a 6-dof closed form already beats the paper bar (ifc_heat nRMSE 0.0709, skill 0.96), so the anatomy would decompose the train/test gap of a model that a linear map dominates. It is also the option least connected to the routed contract changes, and B1's part 7 does not name it.

**C. "Floor certification including a standing zero-predictor column"** (the §4.2 menu option). Rejected as *already delivered*: B1's probe D1 recomputed `nn_condition` / `train_mean` / `zero` / `affine_on_hf_train` from the stripped view on 9 datasets at 1e-9 with `zero == 1.0` and the 36.3912 lineage reproduced; re-proposing it is a re-run, not an experiment. What is *not* delivered is the tolerance that check should have used (F1 fired at 1.1056e-9 against a 1e-9 tolerance and was adjudicated metrology-limited), and the certificate's silence about the degenerate condition dimension that makes one arm discontinuous. Those two survive as D2 below, folded into the chosen proposal rather than standing alone.

**D. The chosen direction — the sixth-class staleness witness, built as a *validated instrument* rather than as a patch.** B2-D1 is the only verdict row the websearcher calls *"the only direction with real headroom"*, its open part is narrow and named, and B1's part 7 lists it as priority (1). The design decision inside it is what to build:

- **D-i (rejected): ship the predicate as a patch and assert it works.** This is the failure mode round-2 §5 item 4 names — seven instrument-arithmetic defects, falsification clauses failing from instrument arithmetic rather than model behaviour. An unvalidated audit rule is exactly what `train_seconds_collapsed` was, and it survived 859 legs before anyone priced it.
- **D-ii (rejected): validate on the existing live corpus.** Impossible: the 859 live legs carry no binding (coverage 0), and all 20 ground-truth stale legs are train-invalidating, so the corpus contains **zero** labelled negatives. A rule's false-positive rate cannot be measured on a corpus with no negatives — that is the reason `train_seconds_collapsed` shipped in the first place.
- **D-iii (CHOSEN): build a pre-registered labelled mutation fixture and price every candidate rule on it in one job.** Construct read-only copies of three datasets, apply six labelled mutation classes to the *copies*, train v0 checkpoints, then resume-and-score under each mutation. Ground truth is known **by construction**, negatives exist by construction, and every rule (the new content predicate, the whole-dataset-hash ablation, the train/test-split-without-roles ablation, and the three wall-clock rules) is scored on the identical legs with the identical checkpoints — an in-job paired control, satisfying round-1's drift-class rule.

### The MF-specific increment (the reason this is not just the routed patch)

The routed fix says "train and test hashed separately". Reading the datasets on disk shows that binary split is not the honest partition in *this* regime. `mffp_autoresearch/preflight/data_binding.py::hash_dataset` streams every array file of a dataset into ONE sha256 (verified by reading it), and `state/data_hashes.json` records exactly that (`{sha256, n_files, total_bytes, files}` per dataset, 6 datasets). In the round-3 regime:

- **train LF** is a training-only input (LF at train, condition-only at test);
- **test LF** is read by nobody at test — it exists only to build the copy-LF *denominator*;
- **test HF / test cond** are the scoring target.

So a mutation has three distinct remedies, not two: **RETRAIN** (a role the family *read at train* changed), **RESCORE** (the target changed; weights valid — the allen_cahn case), **REREFERENCE** (only the copy-LF denominator changed; weights and predictions both valid). And the correct verdict for a *train-LF-only* change **differs between two arms on the identical dataset**: it invalidates an LF-consuming arm and is a no-op for a condition-only arm. No timestamp, no whole-dataset hash, and no train/test split alone can produce that distinction; it requires the checkpoint to record which roles its dataloader read. That is the composition the verdict calls open, and it is specific to multi-fidelity training where the fidelity ladder is an input at one phase and a reference at another.

### Why the other three routed items ride along rather than forming their own cards

The websearcher's directive 5 is explicit: *"`max(1e-9, ULP band)` needs no novelty framing at all... Ship it as a contract fix and spend the card's argument budget on B2-D1 and the unstable-test measurement."* D2 (tolerance table + sod_1d unstable test), D3 (mdd pair, adoption) and D4 (fit-set seam, measurement) are all training-free, all cheap, and all already routed by the orchestrator; giving each its own card would burn the stream's batch budget on bookkeeping. They are carried as secondary deliverables with their own pre-registered clauses.

## Proposal

- **Category**: diagnostic / instrument — **role-resolved checkpoint<->data content binding as the round's sixth-class staleness witness, validated on a pre-registered labelled mutation fixture with priced false-positive/false-negative rates**, bundled with the three routed contract fixes (ULP-band F1 tolerances + the sod_1d unstable-test remedy; the mdd-unobservable conservative pair; the fit-set-size fairness seam).
- **Card type**: `diagnostic` (WITH training — the §12.4 exception, seeds {0,1,2}; all training is on **fixture** datasets at contract tier and scores **no** panel cell).
- **Anchor reference**: `null`.

### Motivation

Quoting the batch-2 prior-art verdict for **B2-D1**, verbatim: **`preempted-but-MF-composition-open (cite)`** — *"Published halves: cryptographic dataset<->checkpoint attestation (adversarial), position-state binding (duplicate consumption), invariant-based silent-error detection (in-process correctness), structural staleness propagation (no hash). **Open**: the scoring-correctness predicate itself; **separate train/test hashing** as the discriminator between the 18 pfc (train box swap => invalid) and 18 allen_cahn (test trim => valid) legs — uncited anywhere; and the empirical rule pricing on a scored MF corpus (859 legs, 20 ground-truth stale)."*

Plus **B2-D3**'s open column verbatim — *"**Open**: that a *frozen benchmark reference floor* is the output of an unstable test — measured 3.08e-1 relative move, 53 % NN re-selection, 8.4e6x amplification, invisible to every hash/seam check."* — and **B2-D4**'s — *"**Open**: fit-set-size matching between a reference arm and the scored arm."*
**B2-D2** is executed as **adoption**, per its `preempted (cite)` verdict: *"Adopt with citation; do not claim."*

Honesty flag carried onto the card verbatim from the websearch report: *"the build-system/content-addressed-cache framing of B2-D1 never completed (two tool errors). Until batch 3 retries it, B2-D1's write-up must say 'not refuted, not confirmed on that angle' rather than 'nothing close found'."*

### Concrete config

**New tool (added, nothing edited): `tools/ckpt_data_binding.py`.**
Partitions each dataset's array files into roles by on-disk layout — `npz_l*`: `train_l*.npz` -> `{train_cond, train_hf, train_lf}` (per-key digests inside the npz), `test_l*.npz` -> `{test_cond, test_hf, test_lf}`; `ifc_raw`: `train/fidelity_*/Xs.npy|ys.npy` -> `{train_cond, train_hf, train_lf}` by rung (finest rung = HF, coarser rungs = LF, `Xs` = cond), `test/fidelity_*/` -> `{test_cond, test_hf}` — and emits `{role: sha256}` plus a `union_sha256`. Sub-commands: `record`, `verify-legs` (consumes `zero_work_resume_scan.py --out scan.json`, emits per-leg action verdicts), `price-rules` (the confusion-matrix table).
**Backwards-compatibility seam (pre-registered):** the role partition's `union_sha256` must reproduce `preflight/data_binding.py`'s per-dataset `sha256` **byte-exactly** on all 6 datasets recorded in `state/data_hashes.json`, and the role census must be exhaustive and disjoint (file counts and byte totals sum to `n_files` / `total_bytes`) on all 10 `floors.json` datasets. `preflight/data_binding.py` is **not edited**.

**New family-side helper: `models_r3/_common/ckpt_binding.py`.** Writes, at every `torch.save` of `<ckpt_dir>/last.pt`, a block
`data_binding = {ds: {roles: {role: sha256}, union_sha256, roles_read: [...], tool_version, recorded_utc}}`,
where `roles_read` is declared by the family's own dataloader (the roles it actually touched at train time). The key `data_binding` is already in `zero_work_resume_scan.py`'s `BINDING_KEYS` tuple (verified by reading the tool), so its `--read-ckpt-binding` coverage counter picks the block up with **no edit to that tool**; the action predicate itself lives in the new tool, because `zero_work_resume_scan.py` compares the binding value to a whole-dataset entry and would report a spurious MISMATCH against a role dict.

**Predicate (the sixth-class check):**

```
roles_train_read(leg) = ckpt.data_binding[ds].roles_read  intersect  {train_cond, train_hf, train_lf}
RETRAIN     if executed_steps == 0 and any r in roles_train_read has ckpt.roles[r] != current.roles[r]
RESCORE     elif ckpt.roles[test_cond] != current or ckpt.roles[test_hf] != current
REREFERENCE elif ckpt.roles[test_lf] != current
NONE        otherwise
```

**D1 — the fixture and the pricing table.**
Fixture bases (read-only copies into the worktree, originals never opened for write): `sharp__sod_1d` (npz_l*, guard cell, 834 KB), `fluid` (npz_l*, guard cell, 8.6 MB), `ifc_heat` (ifc_raw, 4.6 MB) — three bases covering **both** on-disk layouts. Copies are named `fixture__sod1d_*`, `fixture__fluid_*`, `fixture__ifcheat_*` so they cannot collide with a panel name, a cache key or a panel aggregate. **The mutated copies are byte/array perturbations and are NOT physically valid solutions; they carry no fidelity relationship and are never used for any performance number** (they exist only to give the instrument labelled inputs). No LF is ever produced by downsampling HF.

Mutation classes applied to the copy only, with ground-truth action:

| class | mutation | truth (cond_only arm) | truth (lf_at_train arm) |
|---|---|---|---|
| M0 | none | NONE | NONE |
| M1 | train HF + train cond values perturbed (pfc box-swap analogue) | RETRAIN | RETRAIN |
| M2 | test rows trimmed (ac test-split-trim analogue) | RESCORE | RESCORE |
| M3 | test LF arrays changed (denominator only) | REREFERENCE | REREFERENCE |
| M4 | train rows permuted (content set identical, bytes differ) | NONE (declared conservative blind spot) | NONE (same) |
| M5 | **train LF only** changed | **NONE** | **RETRAIN** |

Two arms: `cond_only` (`roles_read = {train_cond, train_hf}`, the vendored B1 certifier unchanged) and `lf_at_train` (`roles_read = {train_cond, train_hf, train_lf}`, the identical network with an auxiliary MSE term on the registered LF residual). The LF lift uses the ADR r2-0001 registered interpolators (`round2/eval/panel_data.py` / `factory_mffp/models/_common/lf_registration.py`) per the §12 registration-of-lifts rule — never a bare `F.interpolate`.

Legs: 3 bases x 2 arms x 3 seeds = **18 v0 training legs**; 3 bases x 6 mutations x 2 arms x 3 seeds = **108 resume legs**; 126 legs total at contract tier (`epochs: 2`; B1 measured contract-tier legs at 0.41-4.89 s of training each).
Class counts over the 108 resume legs: RETRAIN positives 27 (M1 both arms 18 + M5 lf arm 9); RESCORE positives 18; REREFERENCE positives 18; NONE negatives 27 (M0 both arms 18 + M5 cond arm 9); declared blind-spot class M4 18 (excluded from the FPR denominator **by pre-registration**, reported separately).

Rules priced on the identical 108 legs (in-job paired control, drift-class rule):
R1 role-resolved binding (this card) · R2 whole-dataset single hash (`preflight/data_binding.py` semantics — the non-discriminating ablation) · R3 train/test split without `roles_read` (isolates the MF role increment) · R4 `ckpt_older_than_result` · R5 `train_seconds_collapsed` · R6 global `--data-changed-after` cutoff.
Output: a 4-class confusion matrix per rule with Wilson 95 % intervals on every rate.

**Live-corpus coverage:** re-run `zero_work_resume_scan.py --read-ckpt-binding --exclude stale_ckpt` **UNSCOPED** (default pattern — B1 part 7's fourth item: *"verification scoped to the known blast radius cannot bound the blast radius"*) over the four anchor trees and four round-3 stream trees, and report `data_binding` coverage. Plus the residual question B1 part 7 left open: walk the anchor-consumer graph (`tools/make_round3_anchors.py` inputs -> `launch_anchors.json` -> every card citing an anchor) and certify whether any live reported number reads a pre-box-swap pfc column. pfc is **report-only** (ADR r3-0004) and appears in no falsification clause of this card.

**D2 — tolerance table + the unstable test.** Re-run `tools/floor_precision_seam.py --nn-stability` over all 10 `floors.json` datasets x 3 frozen arms at an **independent** dither seed (1) and B = 64 (batch 1 used seed 0, B = 8); emit `floor_tolerances.json` with `tol[ds] = max(1e-9, band)`. Then implement and measure Titolo et al.'s remedy shape: drop condition dimensions whose **fit-set** std is exactly 0 from the standardized distance (rather than rescaling them by the exact-equality-gated guard), record the dropped dims in the floor certificate, and re-measure every band.

**D3 — the mdd pair (adoption).** Emit `noise_floor_candidate_v2.json` adding, for the two paper-bar cells, `mdd_reference_unobservable` (the shipped `preflight.cell_stability_check`, n_boot 10000, seed 0) beside the certified `mdd_scored = 0`, and `tau_abs_conservative = max(tau_abs_certified, tau_rel + mdd_reference_unobservable * skill_level)`, with the surrogate re-validated on the copy-LF cells (ac/fkpp reproduce; the ch failure declared, top-5 share 0.76). Written as **adoption**: `mdd_scored = 0` is the "no-imputation" approach Batson et al. explicitly discourage, and "certify the pair, license on the max" is conservative imputation + sensitivity analysis; the pre-registration template and the analytic-reference-SD move are cited to arXiv:2605.28873. The probe never writes `state/`; the orchestrator installs.

**D4 — the fit-set-size fairness seam.** For each of the 5 scored panel datasets, refit `affine_on_hf_train`, `train_mean` and `nn_condition` on the scored arm's fit set (`fit_idx`, n = 320 on the sharp cells) alongside the recorded 400-row fit, with the `@full` refits asserted equal to `floors.json` at 1e-12, and report each per-dataset gap shift **in units of the certified `tau_rel`**. Reported as a fairness recommendation with the matched-procedure rule (Brigato et al.) cited; **no floor is re-frozen by this card** — that is an ADR/orchestrator decision. The anti-citation is recorded on the card: the "matched sample size protocol / matched-n interval" phrasing is an unattributed search-engine synthesis and must not appear.

### Recipe

```json
{
  "base_family": "r3s4_cert_min (the round-3 r3s4_audit-B1 certifier at mffp_autoresearch/round3/worktrees/r3s4_audit/B1/models_r3/r3s4_cert_min/, itself round-2's r2s4_cert_min vendored verbatim; declared INSTRUMENT reuse - this card makes no performance claim and scores no panel cell. Two additions only: (i) models_r3/_common/ckpt_binding.py, which writes the role-resolved data_binding block into <ckpt_dir>/last.pt at every save; (ii) an lf_at_train arm identical to the network but adding an auxiliary MSE on the ADR r2-0001 registered LF residual, so that roles_read differs between arms. The network, optimiser and hyper-parameters are byte-identical to B1.)",
  "base_commit": "44f2404a2561cf4e7faaf70105fa0845dd69e804",
  "family_dir": "models_r3/r3s4_binding_fixture",
  "datasets": "fixture__sod1d,fixture__fluid,fixture__ifcheat",
  "epochs": 2,
  "seeds": [0, 1, 2],
  "env": {
    "R3S4B2_FIXTURE_BASES": "sharp__sod_1d,fluid,ifc_heat",
    "R3S4B2_FIXTURE_ROOT": "mffp_autoresearch_outputs/round3/r3s4_audit/B2/fixture",
    "R3S4B2_FIXTURE_SOURCE_ROOT": "mffp_autoresearch/round2/stripped_data",
    "R3S4B2_MUTATIONS": "M0_none,M1_train_hf_cond,M2_test_trim,M3_test_lf,M4_train_permute,M5_train_lf",
    "R3S4B2_MUTATION_EPS": "1e-3",
    "R3S4B2_MUTATION_TRIM_K": "10",
    "R3S4B2_MUTATION_SEED": "0",
    "R3S4B2_ARMS": "cond_only,lf_at_train",
    "R3S4B2_ROLES": "train_cond,train_hf,train_lf,test_cond,test_hf,test_lf",
    "R3S4B2_RULES": "R1_role_binding,R2_whole_hash,R3_traintest_split,R4_ckpt_older_than_result,R5_train_seconds_collapsed,R6_global_cutoff",
    "R3S4B2_BLINDSPOT_CLASSES": "M4_train_permute",
    "R3S4B2_WILSON_ALPHA": "0.05",
    "R3S4B2_DATA_MANIFEST": "mffp_autoresearch/round3/state/data_hashes.json",
    "R3S4B2_MANIFEST_VERIFY_TWICE": "1",
    "R3S4B2_LIVE_AUDIT_ROOTS": "mffp_autoresearch_outputs/round3_anchors/r2s1_direct-B2,mffp_autoresearch_outputs/round3_anchors/r2s1_direct-B3,mffp_autoresearch_outputs/round3_anchors/r2s2_stacked-B1,mffp_autoresearch_outputs/round3_anchors/r2s3_lf_train_signal-B3,mffp_autoresearch_outputs/round3/r3s1_factorised,mffp_autoresearch_outputs/round3/r3s2_field_reach,mffp_autoresearch_outputs/round3/r3s3_lf_value,mffp_autoresearch_outputs/round3/r3s4_audit",
    "R3S4B2_LIVE_AUDIT_PATTERN": "*_e*_s*.json",
    "R3S4B2_LIVE_AUDIT_EXCLUDE": "stale_ckpt",
    "R3S4B2_SEAM_DATASETS": "sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat,heat_local,fluid,sharp__sod_1d,ext__helmholtz_2d",
    "R3S4B2_SEAM_ARMS": "nn_condition,train_mean,zero",
    "R3S4B2_SEAM_DITHER_B": "64",
    "R3S4B2_SEAM_DITHER_SEED": "1",
    "R3S4B2_SEAM_BATCH1_TABLE": "mffp_autoresearch/round3/worktrees/r3s4_audit/B1/scratchpad/turn2_loader_seam.json",
    "R3S4B2_SEAM_REPRO_TOL_RATIO": "2.0",
    "R3S4B2_DEGEN_DIM_POLICY": "drop_zero_variance_fit_set_dims",
    "R3S4B2_PANEL_DATASETS": "sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat",
    "R3S4B2_FLOORS_JSON": "mffp_autoresearch/round3/state/anchors_repaired/floors.json",
    "R3S4B2_NOISE_FLOOR_JSON": "mffp_autoresearch/round3/state/anchors_repaired/noise_floor.json",
    "R3S4B2_ANCHORS_JSON": "mffp_autoresearch/round3/state/anchors/launch_anchors.json",
    "R3S4B2_FITSET_ARMS": "affine_on_hf_train,train_mean,nn_condition",
    "R3S4B2_FITSET_N": "320,400",
    "R3S4B2_FITSET_FULL_ASSERT_TOL": "1e-12",
    "R3S4B2_MDD_ESTIMATOR": "preflight.cell_stability_check",
    "R3S4B2_MDD_BOOT_B": "10000",
    "R3S4B2_MDD_BOOT_SEED": "0",
    "R3S4B2_WIDTH": "32",
    "R3S4B2_BLOCKS": "2",
    "R3S4B2_MODES": "16",
    "R3S4B2_FILM_MLP_WIDTH": "64",
    "R3S4B2_BATCH": "16",
    "R3S4B2_LR": "1e-3",
    "R3S4B2_WD": "1e-5",
    "R3S4B2_CLIP": "1.0",
    "R3S4B2_SCHED": "cosine",
    "R3S4B2_TARGET_NORM": "train_zscore_global",
    "R3S4B2_LF_AUX_WEIGHT": "0.1",
    "R3S4B2_LF_LIFT": "adr_r2_0001_registered",
    "R3S4B2_DIAG_OUT": "mffp_autoresearch_outputs/round3/r3s4_audit/B2/eval"
  }
}
```

Recipe notes. `base_commit` = `round3-substrate` HEAD resolved at design time (`git rev-parse round3-substrate` -> `44f2404a...`, the same substrate B1 shipped on). `datasets` MUST stay the explicit fixture list — the literal `panel` resolves through `round2/project.yaml` to the ROUND-2 panel and would silently score the wrong datasets (B1's recorded recipe note; and here it would additionally score real panel cells from a diagnostic card). `epochs: 2` is the project.yaml `contract_epochs` tier verbatim and is deliberate: the contract tier is exactly the regime that produced 53 of the 62 `train_seconds_collapsed` false alarms, so it is the right regime in which to price the rule. Timing: 126 contract-tier legs at 0.41-4.89 s of training each plus fixture I/O; request the project.yaml default `02:00:00`, `gpu:nvidia_h200:1`, mail `END,FAIL`. D2/D3/D4 are training-free probes in the same job.

### Expected outcome

1. **D1 rule pricing (the headline).** R1 attains RETRAIN recall 27/27, RESCORE 18/18, REREFERENCE 18/18, and **0/27 false RETRAIN** on the NONE class (Wilson 95 % upper bound 0.126). Predicted ablation prices on the identical legs: **R2** (whole-dataset hash) cannot emit RESCORE or REREFERENCE at all (recall 0/18 and 0/18) and makes **45 false RETRAIN calls** (M2 18 + M3 18 + M5-cond 9) out of 90 mutated legs; **R3** (train/test split, no `roles_read`) is correct on M1/M2/M3 but makes **9 false RETRAIN calls** on M5-cond (FPR 9/27 = 0.333) — that number is the size of the MF-specific increment; **R4** `ckpt_older_than_result` fires on all 108 resume legs (FPR 27/27 on the NONE class, no action resolution); **R5** `train_seconds_collapsed` fires on essentially all 126 legs at the contract tier (FPR ~27/27), replicating B1's 859-leg pricing in a controlled setting; **R6** global cutoff fires on all 108 (FPR 27/27).
   Δ vs anchor: **not defined** — the card scores no panel cell, so it moves no panel geomean against the 34.4198 best-floor anchor; its output is a validated instrument and four contract constants.
2. **D1 coverage.** `data_binding` coverage today: **0** on every live leg across the eight audited roots (B1 measured 0/18 on the flagged legs); after this card, **126/126** on its own legs — the first legs in the round carrying a binding. The unscoped audit reproduces B1's 36 zero-work legs (18 pfc, 18 allen_cahn) and the anchor-consumer walk returns a yes/no on whether any live reported number reads a pre-box-swap pfc column.
3. **D2 tolerances.** Batch 1's bands reproduce within 2x on 10/10 datasets at seed 1 / B = 64, with `band(B=64) >= band(B=8)` on >= 8/10 (the estimator is a max over dithers, so more dithers is a tighter lower bound). Pinned `tol[ds] = max(1e-9, band)`: 4 of 10 datasets move off 1e-9 (fluid 1.005e-8, ifc_heat 7.854e-9, heat_local 5.457e-9, ifc_poisson 2.297e-9); the four sharp panel cells stay at 1e-9. Under the new ifc_heat tolerance B1's F1 fire (1.1056e-9) does not fire — the metrology-limited adjudication becomes structural rather than case-by-case.
4. **D2 unstable test.** `sharp__sod_1d`'s `nn_condition` band drops from 3.078e-1 to below 1e-6 (>= 5 orders of magnitude) and NN re-selection from 53 % to 0 % once the zero-variance condition dimension is dropped from the distance; the nine other datasets' floors change by < 1e-12 (the remedy must be a no-op where no degenerate dimension exists). sod_1d is a **guard** cell: no scored number moves either way.
5. **D3 mdd pair.** `mdd_reference_unobservable` ~ 0.211 (ifc_heat) / ~ 0.153 (ifc_poisson), reproducing B1's turn-3 estimates within the surrogate's validated band (0.94x / 0.98x on ac / fkpp); `tau_abs_conservative` 0.3563 (ifc_heat) / 1.4827 (ifc_poisson), i.e. 2.17x / 2.15x the certified constants. No live claim flips (ifc_heat "beats the bar" margin 0.0901 is unlicensed under both; ifc_poisson margin 4.1771 is licensed under both).
6. **D4 fit-set seam.** Refitting at n = 320 shifts the reference-arm gaps by, in units of each cell's certified `tau_rel`: allen_cahn 0.9128 / 18.6198 = **0.049x**, fisher_kpp 4.0627 / 10.3128 = **0.394x**, cahn_hilliard 0.2233 / 0.3612 = **0.618x**; ifc_poisson and ifc_heat predicted < 0.3x (N_hf = 5 / small fit sets, no 400-vs-320 split). All five below one certified `tau_rel` => the seam is real, systematically in the direction that flatters the reference arm, and **sub-verdict** on the scored panel.

**vs the certified noise floor.** The card scores no panel cell, so D1/D2/D3 carry **no** skill-valued threshold: their clauses are counts and metrology bands, and their pre-registered rates are priced with Wilson 95 % intervals (D1) or against the estimator's own re-measured reproducibility at an independent dither seed (D2). D4 is the one clause read in skill units, and its threshold is set **strictly above** each cell's certified `tau_rel` from `state/anchors_repaired/noise_floor.json`: allen_cahn 18.6198, fisher_kpp 10.3128, cahn_hilliard 0.3612, ifc_poisson 0.6910, ifc_heat 0.1640 — the clause fires only on a shift **greater than** those numbers, so every effect it would treat as real strictly exceeds the certified floor. The predicted shifts (0.9128 / 4.0627 / 0.2233 skill units) sit at 0.049x / 0.394x / 0.618x of their floors, so the clause is a genuine test that can fire and is not vacuous. **`sharp__phase_field_crystal_2d` is report-only (ADR r3-0004) and appears in no falsification clause of this card**; it appears only as a metrology row in D2's 10-dataset tolerance census and as the narrative motivating case (18 zero-work legs) in D1.

### Expected falsification

The hypothesis — *"a role-resolved checkpoint<->data content binding is the exact scoring-correctness witness for this regime: it recovers the required remedy (retrain / rescore / re-reference) on a labelled MF mutation corpus with zero false retrains, strictly dominating both the whole-dataset hash and the round's wall-clock rules; the round's F1-class tolerances are metrology-limited and its one discontinuous floor arm is an unstable test with a no-op remedy; and the reference-side terms the round is missing (unobservable paper-bar noise, 400-vs-320 fit sets) are real but sub-verdict"* — is falsified if ANY of:

- **(G1)** R1 fails to attain RETRAIN recall 27/27, RESCORE 18/18, REREFERENCE 18/18 with **0/27** false RETRAIN calls on the NONE class; **or** the R2 (whole-dataset-hash) ablation makes **0** false RETRAIN calls on the M2 union M3 classes (the train/test split buys nothing); **or** the R3 (train/test split without `roles_read`) ablation also attains 0/27 false RETRAIN (the MF role increment buys nothing — the composition the verdict calls open is empty).
- **(G2)** The role partition's `union_sha256` fails to reproduce `preflight/data_binding.py`'s recorded `sha256` byte-exactly on any of the 6 datasets in `state/data_hashes.json`; or the role census is not exhaustive and disjoint (`n_files` / `total_bytes`) on any of the 10 `floors.json` datasets; or `data_binding.py verify --manifest state/data_hashes.json` does not report MATCH 6/6 **both** at job start **and** at job end (which would mean the fixture touched an original).
- **(G3)** The independently re-measured ULP bands (seed 1, B = 64) disagree with B1's table (seed 0, B = 8) by more than 2x relative on >= 2 of the 10 datasets, or `band(B=64) < band(B=8)` on >= 3 of 10 — either would mean the estimator the round is about to pin its F1 tolerances to is not reproducible.
- **(G4)** Dropping zero-variance fit-set condition dimensions fails to reduce `sharp__sod_1d`'s `nn_condition` band below 1e-6 (from 3.078e-1), **or** changes any floor arm on the other nine datasets by more than 1e-12 (a remedy that perturbs a floor is worse than the defect it fixes).
- **(G5)** Refitting the reference arms at the scored arm's fit-set size (n = 320) shifts the reference-arm gap by **more than** that cell's certified `tau_rel` on >= 1 of the 5 scored cells — allen_cahn 18.6198, fisher_kpp 10.3128, cahn_hilliard 0.3612, ifc_poisson 0.6910, ifc_heat 0.1640 — which would mean the fit-set seam alone can flip a licensed verdict and must be escalated to the operator as a fair-comparison defect, not absorbed as a recommendation; **or** the `@full` refit fails to reproduce `floors.json` at 1e-12 (an instrument check on the refitter itself).

## Immutables self-check

Positive evidence, one sentence each, against `program.md` §5 (authority) as distilled in the brainstormer prompt §4.5.

1. **Data read-only.** Every panel/guard dataset is opened read-only; the fixture is built by copying `${R3S4B2_FIXTURE_SOURCE_ROOT}` into `${R3S4B2_FIXTURE_ROOT}` under the outputs tree and mutating only the copy, and `R3S4B2_MANIFEST_VERIFY_TWICE=1` makes `data_binding.py verify` run at job start **and** job end with a required MATCH 6/6 — a mismatch at the end is falsification clause G2, so an accidental write to an original cannot pass silently; no regeneration or PDE solve occurs, N_hf is untouched, and no LF anywhere is produced by downsampling HF (M3/M5 perturb existing LF arrays in the copy and the card states explicitly that the mutated arrays are not physically valid and carry no fidelity relationship).
2. **Panel + guard set fixed.** The card scores **no** panel cell; `datasets` names only the three fixture copies, the D2 census enumerates exactly the 10 `floors.json` datasets, `R3S4B2_PANEL_DATASETS` is the 5-dataset ADR r3-0004 scored panel verbatim in order, and the guard set `heat_local,fluid,sharp__sod_1d` is unchanged (two of its members are used, read-only, as fixture *sources*).
3. **Eval layer / spec untouched.** All scoring flows through the byte-frozen `round2/eval/` (the probes import `nrmse.py` / `panel_data.py` read-only, the B1 precedent); the proposal adds `tools/ckpt_data_binding.py` and `models_r3/_common/ckpt_binding.py` as **new files** and explicitly edits neither `preflight/data_binding.py` nor `tools/zero_work_resume_scan.py` nor `project.yaml` / `program.md` / any agent prompt; every contract change is delivered as an emitted artifact (`floor_tolerances.json`, `noise_floor_candidate_v2.json`, the rule-pricing table) for the orchestrator to adjudicate and install.
4. **One nRMSE definition.** The card reports no new metric: D2/D4 recompute existing floor arms through the frozen `round2/eval/nrmse.py` (with the `_nrmse_def_hash` seam check B1 already runs), D1's outputs are counts and verdicts with no metric at all, and the `lf_at_train` auxiliary term is a *training* loss only — the scored metric is untouched (and no fixture leg's nRMSE is claimed for anything).
5. **Contract CLI fixed.** The fixture legs are invoked through the unchanged `smoke_eval.py` signature (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`) — a fixture is just another `--dataset_dir` — and every knob (mutation classes, arms, dither seed, rule list, fit-set sizes) is an `R3S4B2_*` env var carried in the recipe and therefore in the cache key.
6. **Seeds {0,1,2}, tier epochs fixed.** `seeds: [0,1,2]` is the §12.4 diagnostic-with-training exception that B1 already used, `epochs: 2` is `project.yaml tiers.contract_epochs` verbatim, and no full (2500-epoch) tier is requested anywhere.
7. **Guarded factory surfaces untouched.** Nothing under `mf_field/factory_mffp/{data,baselines,eval,references,scripts}`, `factory.md`, `akash/`, or any generator surface is written; the only factory-side file referenced is `factory_mffp/models/_common/lf_registration.py`, and it is **imported** by the `lf_at_train` arm to satisfy the registration-of-lifts rule, not modified.
8. **Checkpoint-resume from `<ckpt_dir>/last.pt`.** Resume is not merely implementable here, it is the experiment: the 108 resume legs are executed by pointing a fresh job at the v0 leg's `<ckpt_dir>/last.pt`, and the binding block is written **inside** that same `last.pt` at every save by `models_r3/_common/ckpt_binding.py`, so the resume path is exercised 108 times and its correctness is directly observable in the `executed_steps == 0` counter.
9. **Falsification thresholds vs the certified noise floor.** The only skill-valued clause is G5, whose firing threshold is *strictly greater than* each cited cell's certified `tau_rel` from `state/anchors_repaired/noise_floor.json` — allen_cahn **18.6198**, fisher_kpp **10.3128**, cahn_hilliard **0.3612**, ifc_poisson **0.6910**, ifc_heat **0.1640** — against predicted shifts of 0.9128 (0.049x), 4.0627 (0.394x) and 0.2233 (0.618x), so the clause can fire but only on an effect above the floor; G1 is a pre-registered false-positive/false-negative protocol with Wilson 95 % intervals (0/27 -> [0, 0.126]) on a corpus whose labels are true by construction; G2 and G4 are deterministic byte/1e-12 identities with a noise floor of exactly 0; and G3 prices the metrology estimator against its own re-measurement at an independent dither seed rather than against any panel constant.
10. **Not a pre-falsified lever.** Nearest prior: **`train_seconds_collapsed`** and the wall-clock staleness family, falsified in B1 part 6 (104 fires, sole reason on 62 legs that all trained, sole reason on **0** of 20 ground-truth stale legs, and work-normalisation gives 42/552 fresh false positives). This proposal does not re-propose it — it deletes it and *scores it as an ablation* (R5) on the same corpus, which is the zero-information-null publication rule applied to an audit instrument; the mechanism attacked is content, not wall clock. Second-nearest: round-2's `data_binding` byte certificate (r2s4-B1) — confirmed as a dataset-side certificate, but structurally unable to be a staleness witness (one sha256 per dataset, nowhere near a checkpoint); the difference is role resolution plus checkpoint embedding, and R2 scores the old semantics as the ablation. Third: B1's own floor-reproduction probe D1 — this card does not re-run it, it fixes the tolerance the probe should have used.
11. **Floor arms.** Not applicable in the model-card sense (this is a `diagnostic` card that scores no panel cell and makes no performance claim), and satisfied in substance: the standing `nn_condition` / `train_mean` / `zero` columns are the *objects under audit* in D2 (all three arms x 10 datasets) and in D4 (`affine_on_hf_train` / `train_mean` / `nn_condition` refit at both fit-set sizes on all 5 scored cells), with `zero == 1.0` re-asserted as part of G4's no-op check.

## Status

- Slot covered: **1/1 filled** (`r3s4_audit-B2`).
- Skipped: none.
- Reopen candidates resolved: none existed (B1 is the only prior card in the stream and carries `reopen_candidate: false`).
- Immutables self-check: **pass (11/11)** — no violation found, no revision needed, so no `iteration_2.md`.
