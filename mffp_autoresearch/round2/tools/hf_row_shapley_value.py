#!/usr/bin/env python
"""What is each TRAINING ROW actually worth? Exact coalition Shapley on an
exhaustive-subset dump, plus the per-test-sample concentration that says WHY.

Provenance: promoted from `r2s4_diag-B4` mechanism turns 2-3
(`worktrees/r2s4_diag/B4/scratchpad/reanalysis_turn_{2,3}.py`). There, on
ifc_poisson's 5-row HF design, it refuted the turn-1 reading that the least
representative row was a passenger: that row carried the LARGEST Shapley value
(4.383 skill = 22.5 % of the total, stable in 3/3 inits), the design that drops
it is the worst 4-row design, and the round's descriptive coverage statistic
(nearest-neighbour share of the test set) correlates **-0.60** with measured row
value. It also found the one genuinely redundant row (negative marginal
contribution at |S| = m-1, and it HARMS the test rows it does not serve).

WHEN TO RUN IT
  Any card that trains an exhaustive `C(m, n)` subset design over a small set of
  training rows / atoms / sources / fidelity rungs and dumps one leg per
  coalition. With every coalition present, the cooperative game
  `v(S) = value of training on subset S` is known exactly, so each player's
  Shapley value is closed-form: no sampling, no retraining, no surrogate.
  Run it BEFORE believing any coverage / typicality / centrality diagnostic
  about which rows matter (see `coverage_spearman` below).

WHAT IT MEASURES
  scalar_shapley      exact phi per player, in the dump's own metric units
                      (skill / nRMSE / whatever `--value_key` names), its share
                      of the total, its value in `--mce` units, the per-replicate
                      spread, and the efficiency identity `sum(phi) = v(full)`
  marginals           each player's mean marginal contribution at every coalition
                      size |S| = 0..m-1 — a FLAT profile is a complement (its
                      value does not decay as the coalition grows), a profile
                      decaying to <= 0 is a substitute/passenger
  leave_one_out       every (m-1)-player design scored, best and worst named
  per_sample          (with --preds_npz) the same exact Shapley run on the
                      per-test-sample error vector, so each player's value can be
                      localised on the test set
  partition           (with --cond_train/--cond_test) the per-sample Shapley
                      binned by each test row's NEAREST training row in
                      standardised condition space: `concentration_ratio` >> 1
                      means the player buys COVERAGE of a region no other player
                      serves; the interference test asks whether adding a player
                      HURTS the test rows it does not serve
  channels            (with --channels) the exact Shapley re-run separately on
                      the AMPLITUDE and STRUCTURE channels of the energy-metric
                      twin, so a player's value is attributed to "gets the scale
                      right" vs "gets the shape right" (additivity is checked)
  coverage_spearman   rank correlation of every descriptive per-player statistic
                      against the measured Shapley value. This is the tool's
                      headline warning: on the provenance card the coverage
                      statistic was ANTI-informative.

READ IT AS
  `verdict = COVERAGE_ANTI_INFORMATIVE` -> do NOT select or weight training rows
  on a representativeness statistic on this dataset; it picks the wrong rows.
  `verdict = REDUNDANT_PLAYER` -> some player's marginal contribution at the full
  coalition is negative: the design's effective size is smaller than m.
  A flat marginal profile + a high partition `concentration_ratio` = the player
  is a COMPLEMENT (worst alone, best in company), which is a property of the
  DATA GEOMETRY; confirm by re-running on a second capacity/width arm.

CAVEATS THE TOOL ENFORCES
  * Coalitions must be exhaustive; missing subsets are listed and the run aborts
    (a sampled Shapley is a different estimator and is not offered here).
  * `v(empty) = 0` must be meaningful: with no training rows the only admissible
    prediction is the zero field, so `--zero_value` (or `--zero_json_path`) is
    REQUIRED and is seam-checked against the predictions when they are supplied.
  * The channel split lives on the ENERGY-METRIC TWIN (mean of SQUARED rel-L2),
    never on the round's nRMSE; it is reported under `channels` and labelled.
  * Per-sample rel-L2 recomputed from the predictions is seam-checked against the
    dump's own per-leg metric before any Shapley is taken.

USAGE
  python tools/hf_row_shapley_value.py \
      --legs_json <anatomy.json> --legs_path anatomy.group_A_curve \
      --value_key test_skill --zero_json_path floor_arms.skill.ref_zero \
      --filter width=32 \
      --preds_npz <preds_test.npz> --truth_key hf_true --ref 0.036 \
      --cond_train <stripped>/train/fidelity_64/Xs.npy \
      --cond_test  <stripped>/test/fidelity_64/Xs.npy \
      --noise_floor_json state/noise_floor.json --dataset ifc_poisson \
      --channels --out shapley.json

  Minimal (scalar Shapley only, any dump):
  python tools/hf_row_shapley_value.py --legs_json d.json --legs_path legs \
      --value_key test_skill --zero_value 27.77777777777778 --out s.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

_EVAL = Path(__file__).resolve().parent.parent / "eval"
sys.path.insert(0, str(_EVAL))
import nrmse as nrmse_mod  # noqa: E402  (the round's single metric definition)


# ── helpers ─────────────────────────────────────────────────────────────────
def dotted(obj, path: str):
    """Resolve `a.b.c` (list indices allowed as integers) inside a loaded JSON."""
    cur = obj
    for part in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            cur = cur[part]
    return cur


def spearman(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean()
    rb -= rb.mean()
    den = np.sqrt((ra @ ra) * (rb @ rb))
    return float(ra @ rb / den) if den > 0 else float("nan")


def standardize_cond(c_fit, c_other):
    """Per-dim z-score from `c_fit`; sd == 0 -> 1.0.

    Same convention as `eval/make_floor_anchors.py`, so the partition this tool
    builds is the SAME condition space the frozen `nn_condition` floor uses.
    """
    c_fit = np.asarray(c_fit, dtype=np.float64)
    mu = c_fit.mean(axis=0)
    sd = c_fit.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    return (c_fit - mu) / sd, (np.asarray(c_other, dtype=np.float64) - mu) / sd


def rel_l2_per_sample(pred, truth):
    """The round's per-sample kernel; its MEAN is `eval/nrmse.py::nrmse`."""
    pred = np.asarray(pred, dtype=np.float64)
    truth = np.asarray(truth, dtype=np.float64)
    return np.linalg.norm(pred - truth, axis=1) / np.linalg.norm(truth, axis=1)


def shapley(vfun, players):
    """Exact Shapley over all 2^m coalitions. `vfun(tuple_sorted) -> scalar|vec`."""
    m = len(players)
    fact = math.factorial
    phi = {}
    for r in players:
        rest = [p for p in players if p != r]
        tot = None
        for k in range(m):
            w = fact(k) * fact(m - 1 - k) / fact(m)
            for S in itertools.combinations(rest, k):
                d = vfun(tuple(sorted(S + (r,)))) - vfun(tuple(S))
                tot = w * d if tot is None else tot + w * d
        phi[r] = tot
    return phi


# ── main ────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--legs_json", required=True,
                    help="JSON holding the per-coalition legs")
    ap.add_argument("--legs_path", default="anatomy.group_A_curve",
                    help="dotted path to the leg LIST inside --legs_json "
                         "(use '.' for a top-level list)")
    ap.add_argument("--subset_key", default="subset")
    ap.add_argument("--rep_key", default="rep",
                    help="replicate/seed key; pass '' if the dump has one leg per subset")
    ap.add_argument("--leg_key", default="leg", help="key naming the leg (= npz key)")
    ap.add_argument("--value_key", default="test_skill",
                    help="the scalar metric per leg that the game is played in")
    ap.add_argument("--higher_is_better", action="store_true",
                    help="set when --value_key is higher-better (default: lower-better)")
    ap.add_argument("--filter", action="append", default=[], metavar="KEY=VAL",
                    help="keep only legs with leg[KEY] == VAL (repeatable)")
    ap.add_argument("--zero_value", type=float, default=None,
                    help="value of the ZERO/empty-coalition predictor in --value_key units")
    ap.add_argument("--zero_json_path", default=None,
                    help="dotted path to that value inside --legs_json")
    ap.add_argument("--preds_npz", default=None,
                    help="npz with one (N, n_cells) array per leg key + the truth")
    ap.add_argument("--truth_key", default="hf_true")
    ap.add_argument("--ref", type=float, default=None,
                    help="denominator that converts nRMSE to the card's skill "
                         "(e.g. the paper bar); required with --preds_npz")
    ap.add_argument("--cond_train", default=None, help=".npy of the training-row conditions")
    ap.add_argument("--cond_test", default=None, help=".npy of the test-row conditions")
    ap.add_argument("--channels", action="store_true",
                    help="also Shapley the amplitude/structure channels (needs --preds_npz)")
    ap.add_argument("--mce", type=float, default=None,
                    help="min_claimable_effect to express phi in claim units")
    ap.add_argument("--noise_floor_json", default=None)
    ap.add_argument("--dataset", default=None,
                    help="key inside --noise_floor_json for the mce")
    ap.add_argument("--descriptive_json", default=None,
                    help="JSON {stat_name: {player: value}} to rank-correlate against phi")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = {"tool": "hf_row_shapley_value.py",
         "nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH,
         "inputs": {k: v for k, v in vars(args).items()}}

    raw = json.loads(Path(args.legs_json).read_text())
    legs = raw if args.legs_path in ("", ".") else dotted(raw, args.legs_path)
    for f in args.filter:
        key, val = f.split("=", 1)
        def _match(e, key=key, val=val):
            got = e.get(key)
            return str(got) == val
        legs = [e for e in legs if _match(e)]
    if not legs:
        print("FAILURE: no legs after filtering", file=sys.stderr)
        return 2

    mce = args.mce
    if mce is None and args.noise_floor_json and args.dataset:
        mce = json.loads(Path(args.noise_floor_json).read_text())[args.dataset][
            "min_claimable_effect"]

    zero = args.zero_value
    if zero is None and args.zero_json_path:
        zero = float(dotted(raw, args.zero_json_path))
    if zero is None:
        print("FAILURE: --zero_value or --zero_json_path is required "
              "(v(empty) must be defined for the Shapley axioms to apply)",
              file=sys.stderr)
        return 2

    # index: subset tuple -> {rep: leg}
    W = {}
    for e in legs:
        S = tuple(sorted(int(x) for x in e[args.subset_key]))
        rep = e[args.rep_key] if args.rep_key else 0
        W.setdefault(S, {})[rep] = e
    players = sorted({p for S in W for p in S})
    m = len(players)
    if m > 16:
        print(f"FAILURE: {m} players -> 2^{m} coalitions; exhaustive Shapley refused",
              file=sys.stderr)
        return 2
    want = [tuple(sorted(S)) for k in range(1, m + 1)
            for S in itertools.combinations(players, k)]
    missing = [S for S in want if S not in W]
    if missing:
        print(f"FAILURE: coalition set is not exhaustive; {len(missing)} of "
              f"{len(want)} subsets missing, e.g. {missing[:5]}", file=sys.stderr)
        return 2
    reps = sorted({r for d in W.values() for r in d})
    R["design"] = {"players": players, "n_coalitions": len(W), "replicates": reps,
                   "exhaustive": True, "zero_value": zero,
                   "value_key": args.value_key,
                   "higher_is_better": bool(args.higher_is_better),
                   "mce": mce}

    sign = 1.0 if args.higher_is_better else -1.0

    def raw_value(S, rep=None):
        d = W[tuple(sorted(S))]
        if rep is None:
            return float(np.mean([d[q][args.value_key] for q in sorted(d)]))
        return float(d[rep][args.value_key])

    def v(S, rep=None):
        """v(S) = improvement over the empty coalition; ALWAYS higher-better."""
        if len(S) == 0:
            return 0.0
        return sign * (raw_value(S, rep) - zero)

    phi = shapley(lambda S: v(S), players)
    phi_rep = {r: shapley(lambda S, r=r: v(S, r), players) for r in reps}
    tot = sum(phi.values())
    R["scalar_shapley"] = {
        "definition": "v(S) = value(S) - value(empty), oriented higher-is-better; "
                      "exact Shapley over all 2^m coalitions",
        "v_full": v(tuple(players)),
        "phi": {str(p): phi[p] for p in players},
        "phi_share_pct": {str(p): 100.0 * phi[p] / tot for p in players},
        "phi_in_mce_units": ({str(p): phi[p] / mce for p in players} if mce else None),
        "phi_per_replicate": {str(r): {str(p): phi_rep[r][p] for p in players}
                              for r in reps},
        "phi_replicate_range": {str(p): float(max(phi_rep[r][p] for r in reps)
                                              - min(phi_rep[r][p] for r in reps))
                                for p in players},
        "rank_best_to_worst": [int(p) for p in sorted(players, key=lambda q: -phi[q])],
        "efficiency_check_sum_phi_minus_v_full": float(tot - v(tuple(players))),
        "rank_stable_across_replicates": bool(
            len({tuple(sorted(players, key=lambda q: -phi_rep[r][q])) for r in reps}) == 1),
    }

    marg = {}
    for p in players:
        rest = [q for q in players if q != p]
        marg[str(p)] = {}
        for k in range(m):
            vals = [v(tuple(sorted(S + (p,)))) - v(tuple(S))
                    for S in itertools.combinations(rest, k)]
            marg[str(p)][f"|S|={k}"] = {
                "mean": float(np.mean(vals)), "min": float(np.min(vals)),
                "max": float(np.max(vals)), "n_negative": int((np.asarray(vals) < 0).sum()),
                "n": len(vals)}
    R["marginals_by_coalition_size"] = {
        "note": "flat profile = COMPLEMENT; decays to <= 0 = substitute/passenger",
        "per_player": marg}

    loo = {"".join(map(str, S)): raw_value(S)
           for S in itertools.combinations(players, m - 1)}
    pick_best = max if args.higher_is_better else min
    pick_worst = min if args.higher_is_better else max
    R["leave_one_out"] = {
        "value_key": args.value_key,
        "all_m_minus_1_designs": loo,
        "best": pick_best(loo, key=lambda k: loo[k]),
        "worst": pick_worst(loo, key=lambda k: loo[k]),
        "full_design_value": raw_value(tuple(players)),
        "solo_value": {str(p): raw_value((p,)) for p in players},
        "marginal_at_full": {str(p): marg[str(p)][f"|S|={m-1}"]["mean"] for p in players},
        "redundant_players_negative_marginal_at_full":
            [int(p) for p in players if marg[str(p)][f"|S|={m-1}"]["mean"] < 0],
    }

    # ── per-sample + partition + channels ───────────────────────────────────
    nn_share = None
    if args.preds_npz:
        if args.ref is None:
            print("FAILURE: --ref is required with --preds_npz", file=sys.stderr)
            return 2
        z = np.load(args.preds_npz)
        Y = np.asarray(z[args.truth_key], dtype=np.float64)
        n_test = Y.shape[0]
        y_n2 = (Y * Y).sum(1)
        ps, amp2, str2 = {}, {}, {}
        seam = []
        for S, d in W.items():
            for r, e in d.items():
                k = e[args.leg_key]
                if k not in z.files:
                    continue
                P = np.asarray(z[k], dtype=np.float64)
                ps[k] = rel_l2_per_sample(P, Y)
                seam.append(abs(float(ps[k].mean()) - nrmse_mod.nrmse(P, Y)))
                g = (P * Y).sum(1) / y_n2
                amp2[k] = (1.0 - g) ** 2
                str2[k] = ((P - g[:, None] * Y) ** 2).sum(1) / y_n2
        R["seam"] = {
            "legs_with_preds": len(ps), "legs_total": sum(len(d) for d in W.values()),
            "max_abs_diff_mean_persample_vs_eval_nrmse": float(max(seam)) if seam else None,
            "max_abs_violation_rel_l2sq_eq_amp_plus_str":
                float(max(float(np.abs(ps[k] ** 2 - (amp2[k] + str2[k])).max()) for k in ps))
                if ps else None,
            "zero_predictor_implied_value": 1.0 / args.ref,
            "declared_zero_value": zero,
            "zero_value_matches_zero_predictor":
                bool(abs(1.0 / args.ref - zero) < 1e-9),
        }
        if len(ps) < sum(len(d) for d in W.values()):
            R["seam"]["warning"] = "not every leg has predictions; per-sample sections skipped"

        if len(ps) == sum(len(d) for d in W.values()):
            def v_vec(S):
                if len(S) == 0:
                    return np.zeros(n_test)
                d = W[tuple(sorted(S))]
                arr = np.mean([ps[d[q][args.leg_key]] for q in sorted(d)], axis=0)
                return (1.0 - arr) / args.ref     # zero predictor has rel-L2 == 1

            phi_vec = shapley(v_vec, players)
            R["per_sample_shapley"] = {
                "units": f"per-test-sample value vs the zero predictor, / {args.ref}",
                "vec_mean_vs_scalar_phi": {
                    str(p): {"vec_mean": float(phi_vec[p].mean()), "scalar": phi[p],
                             "abs_diff": abs(float(phi_vec[p].mean()) - phi[p])}
                    for p in players},
                "frac_test_rows_negative": {str(p): float((phi_vec[p] < 0).mean())
                                            for p in players},
            }

            if args.cond_train and args.cond_test:
                c_tr = np.load(args.cond_train)
                c_te = np.load(args.cond_test)
                c_tr_z, c_te_z = standardize_cond(c_tr, c_te)
                d2 = ((c_te_z[:, None, :] - c_tr_z[None, :, :]) ** 2).sum(2)
                nn_idx = np.argmin(d2, axis=1)
                hist = {str(p): int((nn_idx == p).sum()) for p in players}
                nn_share = [hist[str(p)] for p in players]
                part = {}
                for p in players:
                    own = nn_idx == p
                    mu = float(phi_vec[p].mean())
                    part[str(p)] = {
                        "partition_size": int(own.sum()),
                        "partition_share_of_test": float(own.mean()),
                        "phi_on_own_partition": float(phi_vec[p][own].mean()) if own.any() else None,
                        "phi_off_own_partition": float(phi_vec[p][~own].mean()),
                        "concentration_ratio":
                            float(phi_vec[p][own].mean() / mu) if (own.any() and mu != 0) else None,
                    }
                # interference: add p to the other m-1 and split by partition
                inter = {}
                full = tuple(players)
                for p in players:
                    base = tuple(sorted(q for q in players if q != p))
                    bm = np.mean([ps[W[base][q][args.leg_key]] for q in sorted(W[base])], axis=0)
                    fm = np.mean([ps[W[full][q][args.leg_key]] for q in sorted(W[full])], axis=0)
                    own = nn_idx == p
                    dsk = (fm - bm) / args.ref     # NEGATIVE = adding p helped
                    inter[str(p)] = {
                        "delta_skill_all": float(dsk.mean()),
                        "delta_skill_own_partition": float(dsk[own].mean()) if own.any() else None,
                        "delta_skill_off_partition": float(dsk[~own].mean()),
                        "frac_test_rows_helped": float((dsk < 0).mean()),
                        "interferes_off_partition": bool(dsk[~own].mean() > 0),
                    }
                R["nn_partition"] = {
                    "definition": "each test row assigned to its nearest TRAINING row in "
                                  "standardised condition space (sd==0 -> 1.0)",
                    "hist": hist, "per_player": part,
                    "interference_test": inter,
                    "reading": "concentration_ratio >> 1 = the player buys COVERAGE of a "
                               "region no other player serves; interferes_off_partition = "
                               "it costs the rows it does not serve",
                }

            if args.channels:
                def chan(S):
                    d = W[tuple(sorted(S))]
                    a = np.mean([amp2[d[q][args.leg_key]] for q in sorted(d)], axis=0)
                    s = np.mean([str2[d[q][args.leg_key]] for q in sorted(d)], axis=0)
                    return float(a.mean()), float(s.mean())

                def v_amp(S):
                    return 0.0 if len(S) == 0 else float(1.0 - chan(S)[0])

                def v_str(S):
                    return 0.0 if len(S) == 0 else float(0.0 - chan(S)[1])

                pa = shapley(v_amp, players)
                pstr = shapley(v_str, players)
                pen = shapley(lambda S: v_amp(S) + v_str(S), players)
                R["channels"] = {
                    "metric": "ENERGY-METRIC TWIN (mean of SQUARED rel-L2) split into "
                              "amplitude (1-g)^2 and structure ||p-g y||^2/||y||^2; "
                              "NOT the round's nRMSE — never substitute it",
                    "phi_energy": {str(p): pen[p] for p in players},
                    "phi_amplitude": {str(p): pa[p] for p in players},
                    "phi_structure": {str(p): pstr[p] for p in players},
                    "amplitude_share_of_player_value":
                        {str(p): (pa[p] / pen[p] if pen[p] != 0 else None) for p in players},
                    "players_with_negative_structure_value":
                        [int(p) for p in players if pstr[p] < 0],
                    "additivity_check": {str(p): float(pa[p] + pstr[p] - pen[p])
                                         for p in players},
                    "spearman_energy_vs_primary_metric":
                        spearman([pen[p] for p in players], [phi[p] for p in players]),
                    "full_design_channel_gain": {
                        "amplitude": v_amp(tuple(players)),
                        "structure": v_str(tuple(players))},
                }

    # ── descriptive statistics vs measured value ────────────────────────────
    desc = {"solo_value": [raw_value((p,)) for p in players],
            "marginal_at_full": [marg[str(p)][f"|S|={m-1}"]["mean"] for p in players]}
    if nn_share is not None:
        desc["nn_share_of_test"] = nn_share
    if args.descriptive_json:
        for name, dd in json.loads(Path(args.descriptive_json).read_text()).items():
            desc[name] = [float(dd[str(p)]) for p in players]
    phis = [phi[p] for p in players]
    sp = {k: spearman(vals, phis) for k, vals in desc.items()}
    R["coverage_spearman"] = {
        "definition": "rank correlation of each descriptive per-player statistic against "
                      "the MEASURED Shapley value",
        "spearman_vs_phi": sp,
        "per_player_statistics": {k: {str(p): vals[i] for i, p in enumerate(players)}
                                  for k, vals in desc.items()},
        "reading": "a NEGATIVE correlation for a coverage/representativeness statistic "
                   "means selecting rows on it picks exactly the wrong rows",
    }

    verdicts = []
    if nn_share is not None and sp.get("nn_share_of_test", 0.0) < 0:
        verdicts.append("COVERAGE_ANTI_INFORMATIVE")
    if R["leave_one_out"]["redundant_players_negative_marginal_at_full"]:
        verdicts.append("REDUNDANT_PLAYER")
    # complement signature: the most valuable player is the WORST one alone and the
    # BEST one to add to the full-minus-one coalition (value that does not decay)
    top = R["scalar_shapley"]["rank_best_to_worst"][0]
    solo = {p: marg[str(p)]["|S|=0"]["mean"] for p in players}
    last = {p: marg[str(p)][f"|S|={m-1}"]["mean"] for p in players}
    if min(solo, key=lambda q: solo[q]) == top and max(last, key=lambda q: last[q]) == top:
        verdicts.append("TOP_PLAYER_IS_COMPLEMENT")
    R["complement_signature"] = {
        "top_player_by_phi": int(top),
        "marginal_alone": {str(p): solo[p] for p in players},
        "marginal_at_full_minus_one": {str(p): last[p] for p in players},
        "top_is_worst_alone": bool(min(solo, key=lambda q: solo[q]) == top),
        "top_is_best_in_company": bool(max(last, key=lambda q: last[q]) == top),
    }
    R["verdict"] = verdicts or ["NO_FLAG"]

    Path(args.out).write_text(json.dumps(R, indent=2))
    print(json.dumps({"design": R["design"],
                      "scalar_shapley": R["scalar_shapley"],
                      "leave_one_out": R["leave_one_out"],
                      "coverage_spearman": R["coverage_spearman"]["spearman_vs_phi"],
                      "verdict": R["verdict"],
                      "seam": R.get("seam")}, indent=2))
    print(f"WROTE {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
