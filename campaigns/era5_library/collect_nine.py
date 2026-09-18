"""Require both correctors before fitting and scoring the nine expert library."""
import json
import sys
import numpy as np
from era5_common import ROOT, sha, verify_source, write_json

def main():
    verify_source()
    plan = json.loads((ROOT/'PLAN.json').read_text())
    expected = plan['datasets']['era5']['pool']
    assert len(expected) == len(set(expected)) == 9
    for model in ['uqcorr_transolver_pred', 'uqcorr_convnext_pred']:
        assert model in expected
        meta = json.loads((ROOT/'metadata'/f'{model}__era5.json').read_text())
        assert not meta.get('smoke', False)
        assert meta['prediction_sha256'] == sha(ROOT/'predictions'/f'{model}__era5.npz')
    import collect_dataset
    sys.argv = ['collect_dataset.py', '--dataset', 'era5']
    collect_dataset.main()
    summary = json.loads((ROOT/'results/era5__summary.json').read_text())
    assert summary['complete'] and summary['models'] == expected
    checked = 0
    for folder in (ROOT/'results/era5').glob('s*'):
        fit = json.loads((folder/'fit.json').read_text())
        assert fit['models'] == expected and fit['final_answers_loaded'] is False
        with np.load(folder/'locked_weights.npz') as weights:
            for name in weights.files:
                w = weights[name]
                assert w.shape == (9,) and np.isfinite(w).all()
                assert (w >= 0).all() and abs(w.sum()-1) < 1e-10
                checked += 1
    write_json(ROOT/'results/NINE_EXPERT_AUDIT.json', dict(passed=True,
        models=expected, mixtures_checked=checked, source_sha256=sha(ROOT/'SOURCE.json'),
        original_roles_preserved=sha(ROOT/'ROLES.json')==sha(ROOT/'source/ROLES.json'),
        both_correctors_available_to_all_rules=True,
        interpretation='A fitted rule may assign zero weight to an available expert.'))
    print('VERIFIED: nine experts included in every calibration and ensemble evaluation')

if __name__ == '__main__':
    main()
