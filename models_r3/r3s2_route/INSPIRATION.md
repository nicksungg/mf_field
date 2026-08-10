# INSPIRATION — `r3s2_route` (card `r3s2_field_reach-B2`)

## What this family claims, in one sentence

Nothing about the components is claimed as new.
The claim is a **measurement**: whether a low-fidelity intermediate earns its place in a condition-only prediction graph *when the intermediate must itself be hallucinated from the condition*, measured against a budget-matched direct condition→HF head at a shared trunk, shared folds and shared front end.

## The open direction (prior-art verdict E2, `preempted-but-MF-composition-open (cite)`)

Verbatim from the batch-2 websearch verdict:

> No fetched source runs a **direct parameter→HF arm against a coarse-intermediate arm at matched total optimizer budget where the coarse field cannot be produced at inference**.
> Every MF comparison retrieved either calls the LF model online (2512.02868's "exact LF"; the MF-ROM line) or feeds a real coarse solve to the corrector (2411.07576, INC).
> The open question is exactly: *is the LF intermediate worth its place in the graph when it must itself be hallucinated from the condition?*
> Prior is two-sided — 2512.02868 predicts the stack wins, 2606.17460 + in-repo `MF_Sharp_HighFreq_Report.md` line 101 predict it loses, B1's F2 already measured no resolvable value.

The prior is two-sided and the card pre-registers **both** directions (clause G1), so the affirmative negative — "the LF intermediate is a strict tax" — is a publishable result of this family, not a failure of it.

### E2 citations (the MF-composition literature this family is measured against)

- <https://arxiv.org/abs/2411.07576> — implicit neural corrector fed a *real* coarse solve.
- <https://arxiv.org/abs/2512.02868> — multi-fidelity operator stack with an "exact LF" call at inference; predicts the stack wins, "particularly in data-scarce scenarios".
- <https://arxiv.org/abs/2511.12764>
- <https://arxiv.org/abs/2510.23111>
- <https://arxiv.org/html/2606.17460v2> — predicts the coarse intermediate loses.
- <https://arxiv.org/abs/2302.12682>
- <https://arxiv.org/abs/2310.00057>

## The instrument repair is preempted, and is carried as a gate (verdict E1, `preempted (cite)`)

> "usable ONLY as an instrument repair, never as a contribution" … "Presenting ridge/band-limiting as the *idea* is a rebadge".

The `lsi_filter.py` APPEND-ONLY block adds a LOOCV-selected Tikhonov ridge and zeroes `T(k)` above `k_cut = k_Nyq_HF · N_LF/N_HF`.
It is **falsification clause G2 (instrument acceptance)** on the card, not a contribution, and arm `A5_stack_ic_unreg` keeps the unrepaired estimator so the repair is attributable rather than assumed.
The three sources below are cited as **preemption**, not inspiration:

- <https://arxiv.org/abs/1810.08360> — leave-one-out cross-validation for selecting a Tikhonov/ridge coefficient.
- <https://arxiv.org/pdf/1511.07030> — shrinkage rationale at very low sample support (this family fits a full complex operator from `n_fit = 3` on the ifc cells).
- <https://arxiv.org/pdf/2606.03936> — per-band weighting of a frozen operator.

Classical local Fourier analysis of coarse-grid defect operators is standard multigrid; the vendored `lsi_filter.py` header already carries that lineage (<https://arxiv.org/pdf/2102.01010>, <https://arxiv.org/html/2103.09962v2>, <https://arxiv.org/abs/2304.02117>).

## The approximability instrument (verdict E3), used prospectively

Only the **paired, prospective** use is open: "used prospectively to rule a cell off-limits for capacity spending".
`sidecars.map_smoothness` re-measures the model-free nearest-neighbour/random field-difference ratio on every cell in-job, so the card's **pre-run** declaration — `sharp__cahn_hilliard` is approximability-limited (ratio 0.980), therefore the ROUTE is not the binding constraint there — is a genuine prediction (clause G3) rather than a retrofit.
Arithmetic identical to `round3/tools/task_linearity_audit.py::audit`, cited and never imported.

## Reporting standard

Four-band error columns for every arm follow Duraisamy's reporting standard (<https://arxiv.org/abs/2604.20061>), and every route delta is published in both skill and **fractional error-reduction** units because B1's M5 measured that a 59× per-dataset skill gap on this panel was 20.3× denominator and only 2.14× effect.

## Backbone and vendored code

The FNO backbone (`model.py`), the FiLM/IC front end (`front_end.py`), the analytic IC synthesis (`ic_synth.py`), the local defect corrector and pixel gate (`local_corrector.py`), the band grid (`bands.py`), the periodicity switch (`periodicity.py`), the ADR r2-0001 upsamplers (`upsample.py`), the floor arms (`floor_arms.py`), the training-free probes (`probes.py`) and the sidecars (`sidecars.py`) are vendored **byte-identical** from this stream's own B1 family `r3s2_stack_ic` @ `d5069a74` (per-file sha256 in `_vendor_manifest.json`), which in turn vendors `r2s2_stack` @ `6b4e1d48` and round-1 `s4_router` @ `b90d4662`.
The IC-synthesis math is B1's re-implementation from the READ-ONLY generator surfaces `mffp_sharp/common/ic_encoding.py::ic_2d` and `common/spectral.py::spectral_interp` (never imported, never edited).

**No code is vendored from `r2s1_direct` or any other direct-head family.**
The `direct_*` arms are declared **matched controls** inside the route contrast (recipe `_novelty_declaration`): they are the same `Emulator` trunk instantiated on the HF grid, they carry the analytic IC channel that `r2s1_direct`'s FiLM-only heads do not have, and they are budget-locked to the stack.
`A4_direct_film` is the pre-registered `r2s1_direct-B2` calibration arm; if it lands far from that card's certified 23.7753 panel geomean, the family and not the route is the story.

## FNO lineage

- Li et al., *Fourier Neural Operator for Parametric PDEs* — <https://arxiv.org/abs/2010.08895>
- Perez et al., *FiLM: Visual Reasoning with a General Conditioning Layer* — <https://arxiv.org/abs/1709.07871>
