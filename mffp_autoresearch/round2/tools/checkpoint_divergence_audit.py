#!/usr/bin/env python
"""checkpoint_divergence_audit.py -- is my "paired control" actually the same run?
Weight-space distance between two checkpoints, next to the scores they produced.

Promoted from `s2_beyond_copy-B3` mechanism turn 1
(`worktrees/s2_beyond_copy/B3/scratchpad/reanalysis_turn_1.py`); provenance card
`experiment_cards/s2_beyond_copy/batch_3/B3.json` part 6, findings F2-F4.

WHY THIS EXISTS
---------------
Cards routinely compare a new arm against a control that is either a rebuilt
copy of a previous card's family or a paired arm in the same job, and then
explain any mismatch with a code-path story. s2_beyond_copy-B3's control missed
its predecessor by 52 % on one dataset and 25 % on another while reproducing it
to 5e-07 on three others; the recorded suspicion was a deliberate float32 ->
float64 change. The checkpoints settle it in seconds and with no GPU:

* **all tensors bit-identical** -> the rebuild is faithful and 200 epochs of
  training were bit-reproducible across nodes; any score difference is eval-side
  (partial batches, kernel selection) and is microscopic.
* **weights differ** -> the two runs learned different functions. No code
  argument can explain a score gap the weights already explain, and the right
  follow-up is the run-to-run reproducibility of THIS dataset, not a diff.

On the round-1 stack the split was by working GRID, not by family: three 256x256
datasets came out 39/39 tensors bit-identical between two different jobs on two
different nodes with two different (vendored) copies of the family, while
128x128 and 96x96 datasets diverged (0.078 / 0.319 relative weight distance) and
already differed by ~1e-04 at 2 epochs.

WHAT IT REPORTS (per dataset)
-----------------------------
| key | meaning |
|---|---|
| `global_rel_l2` | `\|\|W_a - W_b\|\| / \|\|W_a\|\|` over all tensors (complex-safe) |
| `n_bit_identical` / `n_tensors` | how many tensors match exactly |
| `worst_tensors` | the five largest per-tensor relative distances |
| `score_a` / `score_b` / `score_rel_delta` | the round metric (`splits.<split>.rel_l2_mean`) from the two result JSONs, if given |
| `verdict` | `BIT_IDENTICAL` \| `NEAR_IDENTICAL` (<1e-6) \| `DIVERGED` |
| `_summary.divergence_is_dataset_specific` | true when some datasets are bit-identical and others are not -- the signature of dataset-dependent training nondeterminism rather than a code difference |

INVOKE
------
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/checkpoint_divergence_audit.py \
      --datasets sharp__phase_field_crystal_2d,sharp__allen_cahn_2d \
      --ckpt_a '<OUT>/B2/eval/results/<fam>/ckpt_{dataset}_e200_s0/last.pt' \
      --ckpt_b '<OUT>/B3/eval/results/<arm>/<fam>/ckpt_{dataset}_e200_s0/last.pt' \
      [--result_a '<OUT>/B2/.../{dataset}_e200_s0.json'] \
      [--result_b '<OUT>/B3/.../{dataset}_e200_s0.json'] \
      [--state_key model] [--split test_hf] [--metric_key rel_l2_mean] \
      --out /path/divergence.json

Torch on the login node, CPU only, ~1 s per checkpoint pair. Nothing it prints
is a score: the result JSONs remain the source of truth.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "eval"))


def _resolve(names: str):
    if names in ("PANEL", "GUARD"):
        from panel_data import load_config
        cfg = load_config()
        return list(cfg["panel"] if names == "PANEL" else cfg["guard_set"])
    return [d for d in names.split(",") if d]


def _state(path, key):
    import torch
    sd = torch.load(path, map_location="cpu", weights_only=False)
    if isinstance(sd, dict) and key in sd:
        meta = {k: v for k, v in sd.items()
                if isinstance(v, (str, int, float, bool, list)) and k != key}
        return sd[key], meta
    return sd, {}


def _score(path, split, metric_key):
    if path is None:
        return None
    p = pathlib.Path(path)
    if not p.exists():
        return None
    j = json.loads(p.read_text())
    return float(j["splits"][split][metric_key])


def one(ds, a_path, b_path, state_key, res_a, res_b, split, metric_key):
    out = {"dataset": ds, "ckpt_a": str(a_path), "ckpt_b": str(b_path)}
    for p in (a_path, b_path):
        if not pathlib.Path(p).exists():
            out["error"] = f"missing checkpoint {p}"
            return out
    sa, ma = _state(a_path, state_key)
    sb, mb = _state(b_path, state_key)
    out["meta_a"], out["meta_b"] = ma, mb
    keys = [k for k in sa if k in sb]
    out["n_keys_only_in_a"] = int(len(set(sa) - set(sb)))
    out["n_keys_only_in_b"] = int(len(set(sb) - set(sa)))
    num = den = 0.0
    per = {}
    for k in keys:
        va, vb = sa[k], sb[k]
        if hasattr(va, "shape") and va.shape != vb.shape:
            per[k] = float("inf")
            continue
        d = float((va - vb).abs().double().pow(2).sum())
        n = float(va.abs().double().pow(2).sum())
        num += d
        den += n
        per[k] = float(np.sqrt(d / n)) if n > 0 else 0.0
    g = float(np.sqrt(num / den)) if den > 0 else 0.0
    out["global_rel_l2"] = g
    out["n_tensors"] = len(keys)
    out["n_bit_identical"] = int(sum(1 for v in per.values() if v == 0.0))
    out["worst_tensors"] = sorted(per.items(), key=lambda kv: -kv[1])[:5]
    out["verdict"] = ("BIT_IDENTICAL" if out["n_bit_identical"] == len(keys)
                      else "NEAR_IDENTICAL" if g < 1e-6 else "DIVERGED")
    sa_, sb_ = _score(res_a, split, metric_key), _score(res_b, split, metric_key)
    out["score_a"], out["score_b"] = sa_, sb_
    out["score_rel_delta"] = (None if not (sa_ and sb_) else float(sb_ / sa_ - 1.0))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datasets", required=True, help="PANEL | GUARD | comma list")
    ap.add_argument("--ckpt_a", required=True, help="path with an optional {dataset}")
    ap.add_argument("--ckpt_b", required=True)
    ap.add_argument("--result_a", default=None)
    ap.add_argument("--result_b", default=None)
    ap.add_argument("--state_key", default="model")
    ap.add_argument("--split", default="test_hf")
    ap.add_argument("--metric_key", default="rel_l2_mean",
                    help="the round's per-sample-mean convention, never `nRMSE`")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = {"_args": vars(a)}
    verdicts = []
    for ds in _resolve(a.datasets):
        f = lambda s: (None if s is None else s.format(dataset=ds))
        r = one(ds, f(a.ckpt_a), f(a.ckpt_b), a.state_key,
                f(a.result_a), f(a.result_b), a.split, a.metric_key)
        out[ds] = r
        verdicts.append(r.get("verdict"))
        print(f"{ds[:34]:34s} {r.get('verdict', r.get('error'))!s:16s} "
              f"relL2 {r.get('global_rel_l2', float('nan')):.4g}  "
              f"bit-identical {r.get('n_bit_identical')}/{r.get('n_tensors')}  "
              f"score delta "
              f"{'n/a' if r.get('score_rel_delta') is None else format(r['score_rel_delta'], '+.3e')}",
              flush=True)
    out["_summary"] = {
        "verdicts": verdicts,
        "divergence_is_dataset_specific":
            bool("BIT_IDENTICAL" in verdicts and "DIVERGED" in verdicts),
        "reading": "mixed verdicts => dataset-dependent training nondeterminism, "
                   "not a code-path difference between the two builds",
    }
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
