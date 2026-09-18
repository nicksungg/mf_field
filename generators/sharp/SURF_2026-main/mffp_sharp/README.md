# mffp_sharp

Sharp-field PDE dataset generation for the MFFP benchmark. Adds three 2D datasets
along a **shock → sharp-interface → smooth** frequency axis, to test whether the
benchmark's "FNO finetuning beats fusion" result (measured on a mostly-smooth
suite) survives on high-frequency fields. Design + approval gate: see
[`../TO-DO.md`](../TO-DO.md).

> **Compute policy:** edit on either machine; run **computationally intensive** work
> (full generation, training, Euler/PyClaw, large solves) on Nicholas's 4090 box
> (`eloise@10.80.6.224`). Light work (figures, CH/KS smoke tests) runs locally in `.venv`.
> Sync via git (pull before edit/run, push after). See `../CLAUDE.md`.

## Layout
```
configs/sample.yaml              # sample-round config (ladder, counts, per-PDE ranges) — values marked (TBD)
src/mffp_sharp/
  common/ladder.py               # dyadic up-interpolation to the HF grid (+ raw provenance)
  common/metrics.py              # metric panel: rel-L2, L-inf, W1, interface-pos, spectral-band, conservation, SSIM
  common/io.py                   # HDF5 writer matching the deck's MF-dataset layout
  common/visualize.py            # one-pager review PNGs: fields / residual / spectrum / metrics
  common/sampling.py             # Latin-hypercube + Schulz-Rinne 2D Riemann configs
  pdes/euler.py                  # PyClaw: LF=Classic(1st-order) / HF=SharpClaw(WENO)  [BOX-ONLY]
  pdes/cahn_hilliard.py          # pure-numpy semi-implicit Fourier; LF under-resolves eps / HF resolves
  pdes/kuramoto_sivashinsky.py   # pure-numpy semi-implicit Fourier 2D KS — smooth CONTROL
  generate.py                    # CLI: sample across ladder, write HDF5, emit LF-vs-HF summary
scripts/setup_env.sh             # (run on the box) build conda env + deps
scripts/run_sample.sh            # (run on the box) generate the sample batch
```

## Status
- **Common modules** (ladder, metrics, io, sampling, visualize): real implementations, PDE-agnostic.
- **Cahn-Hilliard & KS**: custom semi-implicit Fourier solvers, **validated** (run locally + on box).
- **Euler**: PyClaw, **not yet executed** — box-only (needs clawpack); carries a `VALIDATE` note.
- **Provisional / TBD** (in `configs/sample.yaml`): condition-vector ranges,
  snapshot times `T`, the eps↔ladder coupling for Cahn-Hilliard, sample counts.

## Local light runs (`.venv`)
```bash
source .venv/bin/activate                     # repo-root venv (numpy/scipy/mpl/h5py/skimage)
python mffp_sharp/scripts/explain_frequency.py   # explanatory figures -> data/explain/
# CH/KS smoke tests run locally too; Euler + full generation stay on the box.
```

## Quickstart — run on Nicholas's box (per the compute policy)
```bash
# on the box (ssh eloise@10.80.6.224):
git clone https://github.com/eloisezeng/SURF_2026.git
cd SURF_2026/mffp_sharp
bash scripts/setup_env.sh            # one-time: conda env + deps
bash scripts/run_sample.sh all       # generate the sample batch
# review: data/sample/sample_summary.json  (LF-vs-HF bottom-rung check)
#         data/sample/figures/*.png         (one-pager per sample for Nicholas)

# to update later:  git pull  &&  bash scripts/run_sample.sh all
```
Edit code locally → `git push` → `git pull` on the box. Datasets stay on the box
(git-ignored); copy only small summaries/figures back for Nicholas's review.

## The bottom-rung check (what the summary tells you)
`generate.py` prints, per PDE, how different LF is from HF. We WANT:
- **euler, cahn_hilliard**: LF notably worse than HF (shock/interface really blurred).
- **kuramoto_sivashinsky**: LF ≈ HF (the control — small gap by design).

If Cahn-Hilliard's 32² already matches 128², `eps` is too large or the ladder is
wrong (they're coupled) — adjust before the full run. This is part of Nicholas's
approval checklist in `TO-DO.md`.
