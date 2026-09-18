# Paper baseline worker provenance

The B6 through B10 ERA5 entries use the frozen release recipes listed in
`PAPER_VENDOR_SOURCES.json`. The vendor files remain byte identical to their
sources. The recipe wrappers are benchmark adaptations and should not be
described as exact reproductions of their motivating publications.

| Entry | Frozen implementation | Recipe retained |
| --- | --- | --- |
| B6 | `nomad_mf` | A NOMAD inspired nonlinear manifold decoder implemented in the benchmark, with 2500 epochs on the lowest fidelity followed by 2500 HF fine tuning epochs. Architecture and AdamW/cosine settings are unchanged. |
| B7 | `mfrnp` | Vendored upstream MFRNP model with the release adapter, nine fidelity levels, 2500 epochs, the existing 90/10 training split and per level normalization. The native loader caps a batch at the smallest training fidelity count. |
| B8 | `fno_coregionalization` | The release FNO coregionalization adaptation, with 128 channels, 20 basis fields, six blocks and a 2500 epoch schedule split into 625 LF warmup epochs and 1875 joint epochs. The existing mixed fidelity validation split and best validation checkpoint selection are retained. |
| B9 | `mf_fno_transfer` | The release FNO transfer adaptation, with 64 channels, four blocks, 12 Fourier modes per axis, 2500 LF pretraining epochs and 2500 HF fine tuning epochs. |
| B10 | `mf_fno_transfer_bar` | An explicit alias of the B9 prediction, with no second fit. This source has an identical model and training recipe; only the import path and output label differ. It is not an independent model or replication. |

The old ERA5 metrics are not reused. The workers use the original audited repair
plan: 55 HF training cases, 10 reserved calibration cases and seven reserved
evaluation cases. The 17 reserved inputs were removed from every training
fidelity. The same full 128 by 256 working grid is retained. All nine staged
query files contain input parameters and zero target placeholders. An audited
NumPy loader rejects other array paths. The wrappers intercept the old metric
writer and export only the 17 predictions. The separate collector may then read
the sealed answers. Neither the test answers nor calibration answers are used
for training, model selection, normalization or smoke checks.

The original recipes intentionally retain their different validation rules,
optimizers and training budgets. This campaign standardizes the input split
and evaluation cases, not total model training cost.

`stage_train.py` adds atomic per stage checkpoints to B6 and B9. For B7,
`paper_resume.py` augments the native checkpoint with RNG state and the loader's
per level row permutations. For B8 it adds optimizer, scheduler and RNG state so
both stages can continue after preemption. These adaptations are applied in
memory. They leave the frozen model source and training objective unchanged.
Explicit module paths also prevent unrelated `model.py` files from shadowing
the frozen imports.

CPU fixture tests compare B7 and B8 with their untouched vendor recipes and
check exact equality of their predictions. They interrupt and resume B7 and
both B8 training stages and check exact equality with uninterrupted training.
A transfer fixture checks exact resumed optimizer and sample order behavior.
The alias test accepts the inspected B9/B10 identity and rejects a changed
learning rate. Full working grid smoke jobs use one epoch for B6, B7 and B9,
and four epochs for B8 to exercise both stages. Smoke outputs are explicitly
separated from scientific results.
