"""Reporting roster extended by the author's 17 September 2026 instruction.

Archived predictions and fit records remain unchanged. Apply these exclusions
before computing any paper aggregate or choosing illustrative dataset panels.
The diagnostic archive retains seventeen PDE datasets. Primary comparisons add
four completed PDE datasets and the separate ERA5 climate task.
"""
import copy
import math

REMOVED_DATASETS = frozenset({'poisson_generated', 'lid_driven_cavity_generated', 'ext__helmholtz_2d'})
HISTORICAL_COUNT = 17
EXTENSION_DATASETS = ('sharp__cahn_hilliard', 'sharp__fisher_kpp_2d', 'sharp__allen_cahn_2d', 'sharp__phase_field_crystal_2d')
PDE_COUNT = HISTORICAL_COUNT + len(EXTENSION_DATASETS)
PAPER_COUNT = PDE_COUNT + 1


def retained(dataset):
    return dataset not in REMOVED_DATASETS


def filtered_summary(original, class_of):
    """Filter stored per-dataset values and recompute every ratio summary."""
    def visit(value):
        if isinstance(value, list):
            return [visit(v) for v in value if not isinstance(v, str) or retained(v)]
        if not isinstance(value, dict):
            return value
        out = {k: visit(v) for k, v in value.items() if retained(k)}
        if 'dataset_ratios' in out:
            ratios = out['dataset_ratios']
            classes = sorted({class_of[d] for d in ratios})
            class_ratios = {
                c: math.exp(sum(math.log(v) for d, v in ratios.items() if class_of[d] == c)
                            / sum(class_of[d] == c for d in ratios))
                for c in classes}
            out.update(class_ratios=class_ratios,
                       class_balanced_ratio=math.exp(sum(map(math.log, class_ratios.values())) / len(classes)),
                       dataset_balanced_ratio=math.exp(sum(map(math.log, ratios.values())) / len(ratios)),
                       improved_over_1pct=sum(v < .99 for v in ratios.values()),
                       worsened_over_1pct=sum(v > 1.01 for v in ratios.values()))
        return out
    result = visit(copy.deepcopy(original))
    for record in result.values():
        assert len(record['mean_errors']) == HISTORICAL_COUNT
        # This source statistic contains only pooled counts, not dataset identities.
        # Do not carry its old denominator into a restricted reporting scope.
        record.pop('norm_only_choices', None)
    return result
