"""Task list for stage 2b (corrector arms).  A dataset is eligible once assemble_oof.py has written a COMPLETE OOF ensemble
file oof/<name>__L<lf>.npz.  Arms = backbones x inputs (+ FiLM R0/R1 controls); seeds; claims/attempts under *_corr/."""
import argparse, glob, sys
from pathlib import Path
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
ap.add_argument("--seeds", default="42,123"); ap.add_argument("--backbones", default="irno,convnext,transolver")
ap.add_argument("--inputs", default="pred,pred_spread,real"); ap.add_argument("--controls", default="film_r0,film_r1")
ap.add_argument("--only", default=""); ap.add_argument("--exclude", default="")
ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "tasks_corr.txt")); ap.add_argument("--max-attempts", type=int, default=3)
a = ap.parse_args(); U = Path(__file__).resolve().parent
ready = {}
for f in glob.glob(str(U / "oof" / "*__L*.npz")):
    stem = Path(f).stem; name, lf = stem.rsplit("__L", 1); ready[name] = int(lf)
names = sorted(n for n in ready if (not a.only or n in a.only.split(",")) and n not in a.exclude.split(","))
arms = [f"{b}:{i}" for b in a.backbones.split(",") for i in a.inputs.split(",")] + [c for c in a.controls.split(",") if c]
lines, done, claimed, gaveup = [], 0, 0, []
for name in names:
    lf = ready[name]
    for arm in arms:
        for seed in a.seeds.split(","):
            tag = f"{arm.replace(':', '-')}__{name}__L{lf}__s{seed}"
            if (U / "raw_corr" / f"{tag}.json").exists(): done += 1; continue
            if (U / "claims_corr" / tag).exists(): claimed += 1; continue
            att = U / "attempts_corr" / tag
            if att.exists() and int(att.read_text().strip() or 0) >= a.max_attempts: gaveup.append(tag); continue
            lines.append(f"{name} {arm} {seed}")
Path(a.out).write_text("\n".join(lines) + ("\n" if lines else ""))
print(f"wrote {len(lines)} corrector tasks to {a.out} ({len(names)} datasets with complete OOF ensembles; done {done}, claimed {claimed}, gave up {len(gaveup)})")
if gaveup: print("gave up after max attempts:", gaveup)
