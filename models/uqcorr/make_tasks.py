"""Build the pending task list for the UQ-corrector diagnostic from the st_bench roster:
every roster dataset x every coarse level x {plain, hetero} x seeds, minus tasks that are done (raw JSON),
claimed (claims/<tag>), or over the attempt limit.  Unpaired datasets (rows not aligned across levels, e.g. era5) are
skipped and recorded in excluded.json instead of burning GPU slots."""
import argparse, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from diag_coarse import ROSTER, level_files  # noqa: E402

import os as _os, sys as _sys
if _os.path.exists("/archive/mf_field/experiments/uqcorr/STOPPED"):
    Path_out = [a for a in _sys.argv if a.startswith("/")] 
    print("STOPPED marker present: emitting 0 tasks (user halted the uqcorr pipeline 2026-09-10)")
    import argparse as _ap
    _p = _ap.ArgumentParser(add_help=False); _p.add_argument("--out", default="")
    _a, _ = _p.parse_known_args()
    if _a.out: open(_a.out, "w").write("")
    _sys.exit(0)

ap = argparse.ArgumentParser()
ap.add_argument("--seeds", default="42,123"); ap.add_argument("--only", default=""); ap.add_argument("--levels", default="all", choices=["top", "all"])
ap.add_argument("--variants", default="plain,hetero"); ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "tasks.txt"))
ap.add_argument("--max-attempts", type=int, default=3, help="skip tasks submitted this many times without a result")
ap.add_argument("--folds", type=int, default=0, help="also emit K-fold OOF ensemble tasks (top coarse level) for --fold-datasets")
ap.add_argument("--fold-seeds", default="42,123"); ap.add_argument("--fold-datasets", default="", help="comma list; empty = all non-excluded roster sets")
ap.add_argument("--fold-exclude", default="")
ap.add_argument("--exclude", default="", help="datasets to skip entirely (seed and fold tasks)")
ap.add_argument("--no-seed-sweep", action="store_true", help="emit only K-fold ensemble tasks (the ensemble-size sweep is halted)")
a = ap.parse_args()
U = Path(__file__).resolve().parent
names = [n for n in (a.only.split(",") if a.only else sorted(ROSTER)) if n not in a.exclude.split(",")]
lines, done, claimed, gaveup, excluded = [], 0, 0, [], {}
for name in names:
    d = ROSTER[name]
    try:
        trains, tests = level_files(d)
    except AssertionError as e:
        excluded[name] = str(e); continue
    with np.load(trains[-1]) as z: x_hf = z["x"]
    ok = True
    for t in trains[:-1]:
        with np.load(t) as z: x = z["x"]
        if not (len(x) >= len(x_hf) and np.allclose(x[:len(x_hf)], x_hf)):
            ok = False; break
    if not ok:
        excluded[name] = "rows not aligned across levels (unpaired): no coarse-to-fine gap defined"; continue
    if a.no_seed_sweep: continue
    L = len(trains); levels = [L - 1] if a.levels == "top" else list(range(1, L))
    for lf in levels:
        for variant in a.variants.split(","):
            for seed in a.seeds.split(","):
                tag = f"{variant}__{name}__L{lf}__s{seed}"
                if (U / "raw" / f"{tag}.json").exists():
                    done += 1; continue
                if (U / "claims" / tag).exists():
                    claimed += 1; continue
                att = U / "attempts" / tag
                if att.exists() and int(att.read_text().strip() or 0) >= a.max_attempts:
                    gaveup.append(tag); continue
                lines.append(f"{name} {lf} {variant} {seed}")
fold_lines = []
if a.folds > 0:
    fd = [n for n in (a.fold_datasets.split(",") if a.fold_datasets else names) if n not in excluded and n not in a.fold_exclude.split(",")]
    for name in fd:
        trains, _ = level_files(ROSTER[name]); lf = len(trains) - 1
        for k in range(a.folds):
            for variant in a.variants.split(","):
                for seed in a.fold_seeds.split(","):
                    tag = f"{variant}__{name}__L{lf}__F{k}of{a.folds}__s{seed}"
                    if (U / "raw" / f"{tag}.json").exists(): done += 1; continue
                    if (U / "claims" / tag).exists(): claimed += 1; continue
                    att = U / "attempts" / tag
                    if att.exists() and int(att.read_text().strip() or 0) >= a.max_attempts: gaveup.append(tag); continue
                    fold_lines.append(f"{name} {lf} {variant} {seed} {k}")
lines = fold_lines + lines          # OOF generation first: it unblocks the corrector; the 10-member seed sweep follows
Path(a.out).write_text("\n".join(lines) + ("\n" if lines else ""))
(U / "excluded.json").write_text(json.dumps(excluded, indent=1))
print(f"wrote {len(lines)} tasks to {a.out} ({len(fold_lines)} K-fold; done {done}, claimed {claimed}, gave up {len(gaveup)}; excluded datasets: {list(excluded)})")
if gaveup: print("gave up after max attempts:", gaveup)
