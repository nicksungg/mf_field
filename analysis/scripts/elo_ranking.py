"""Dataset balanced Elo using the release benchmark's shuffled match protocol.

Each pair plays once per dataset. Reset to 1500 for each of 500 independent
orderings, use K=32, and report the average final rating. The across ordering
standard deviation is algorithmic variability, not a confidence interval.
"""
import itertools
import random
import numpy as np


def rank_errors(errors, methods, orders=500):
    methods = sorted(methods)
    datasets = sorted(errors)
    assert len(methods) == len(set(methods)) and len(methods) > 1
    matches = []
    counts = {m: dict(wins=0, losses=0, ties=0) for m in methods}
    for dataset in datasets:
        assert set(methods) <= set(errors[dataset]), dataset
        for a, b in itertools.combinations(methods, 2):
            ea, eb = errors[dataset][a], errors[dataset][b]
            assert np.isfinite(ea) and np.isfinite(eb) and min(ea, eb) >= 0
            if abs(ea - eb) < 1e-12:
                score = .5
                counts[a]['ties'] += 1
                counts[b]['ties'] += 1
            elif ea < eb:
                score = 1.
                counts[a]['wins'] += 1
                counts[b]['losses'] += 1
            else:
                score = 0.
                counts[a]['losses'] += 1
                counts[b]['wins'] += 1
            matches.append((a, b, score))
    samples = {m: [] for m in methods}
    for n in range(orders):
        ordered = matches.copy()
        random.Random(7 + n).shuffle(ordered)
        rating = dict.fromkeys(methods, 1500.)
        for a, b, score in ordered:
            probability = 1 / (1 + 10 ** ((rating[b] - rating[a]) / 400))
            change = 32 * (score - probability)
            rating[a] += change
            rating[b] -= change
        assert abs(sum(rating.values()) - 1500 * len(methods)) < 1e-7
        for m in methods:
            samples[m].append(rating[m])
    result = {m: dict(elo=float(np.mean(samples[m])), order_std=float(np.std(samples[m])),
                      datasets=len(datasets), matches=len(datasets) * (len(methods) - 1),
                      **counts[m]) for m in methods}
    ranking = sorted(methods, key=lambda m: (-result[m]['elo'], m))
    for rank, m in enumerate(ranking, 1):
        result[m]['rank'] = rank
    return dict(protocol=dict(initial_rating=1500, k_factor=32, scale=400, orders=orders,
                             order_seeds=[7, 7 + orders - 1], absolute_tie_threshold=1e-12,
                             dataset_weighting='equal', error_input='unrounded mean relative L2',
                             no_performance_based_dataset_exclusions=True),
                datasets=datasets, methods=methods, match_count=len(matches),
                ranking=ranking, ratings=result)
