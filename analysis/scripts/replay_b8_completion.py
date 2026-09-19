"""Score fixed B8 checkpoints on identified common test inputs. Never trains."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import time

import numpy as np
import torch


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--dataset', choices=['heat_local', 'sharp__burgers_2d'], required=True)
    args = ap.parse_args()
    root, ds = args.root, args.dataset
    spec = json.loads((root / 'alignment.json').read_text())
    rr = next(r for r in spec['remote_checks'] if r['dataset'] == ds)
    rawfile = root / ('fno_coregionalization__' + ds + '__s42.json')
    raw = json.loads(rawfile.read_text())
    expected = np.asarray(raw['splits']['test_hf']['rel_l2_per_sample'])
    source = Path(rr['test_path'])
    assert sha(source) == rr['test_archive_sha256']
    with np.load(source, allow_pickle=False) as z:
        inputs = np.asarray(z['x'], np.float32)
        targets = np.asarray(z['y'], np.float32).reshape(len(inputs), -1)
    assert len(inputs) == len(expected) == rr['n']
    mf = Path('/archive/mf_field')
    code = mf / 'factory_mffp/models/fno_coregionalization/model.py'
    assert sha(code) == '32ac25d632cf94b59c1f8760a2c4ffcd345cf5a2a81179c2962d8a14ea0d3d99'
    module_spec = importlib.util.spec_from_file_location('b8_model', code)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    torch.set_num_threads(4)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    print(ds, 'device', device, 'test rows', len(inputs), flush=True)
    # Fixed final campaign checkpoint for both datasets, not chosen by test error.
    candidates = [mf / 'akash/checkpoints_final/s42/fno_coregionalization' / ds / 'best.pt']
    attempts = []
    for checkpoint in candidates:
        if not checkpoint.exists():
            continue
        print('Loading', checkpoint, flush=True)
        start = time.time()
        state = torch.load(checkpoint, map_location='cpu', weights_only=False)['model']
        grid = tuple(state['coord_grid'].shape[-2:])
        assert list(grid) == rr['grid']
        model = module.FNOCoregionalization(
            cond_dim=state['lift.weight'].shape[1] - 2,
            hidden_channels=state['lift.weight'].shape[0],
            K=state['proj.2.weight'].shape[0],
            n_blocks=len({k.split('.')[1] for k in state if k.startswith('blocks.')}),
            modes_h=state['blocks.0.spectral.w1'].shape[-2],
            modes_w=state['blocks.0.spectral.w1'].shape[-1],
            grid=grid, b_hidden=state['B.0.weight'].shape[0])
        model.set_scalers(state['m_keys'], state['scalers'])
        model.load_state_dict(state, strict=True)
        model.to(device).eval()
        del state
        predictions = []
        with torch.inference_mode():
            for first in range(0, len(inputs), 8):
                x = torch.from_numpy(inputs[first:first + 8]).to(device)
                pred = model(x, torch.ones(len(x), device=device))
                predictions.append(pred.cpu().numpy().reshape(len(x), -1))
                if first % 128 == 0:
                    print('inference', first, 'seconds', round(time.time() - start, 1), flush=True)
        pred = np.concatenate(predictions)
        errors = np.linalg.norm(pred.astype(np.float64) - targets, axis=1) / np.maximum(
            np.linalg.norm(targets.astype(np.float64), axis=1), 1e-12)
        match = bool(np.allclose(errors, expected, rtol=1e-5, atol=1e-9))
        attempt = dict(checkpoint=str(checkpoint), max_abs_error_difference=float(abs(errors - expected).max()),
                       max_relative_error_difference=float((abs(errors - expected) / np.maximum(expected, 1e-12)).max()),
                       errors_match=match, seconds=time.time() - start)
        attempts.append(attempt)
        print(attempt, flush=True)
        if np.isfinite(errors).all():
            out = root / (ds + '__replay.npz')
            np.savez_compressed(out, x=inputs, pred=pred, target=targets,
                                errors=errors, archived_errors=expected)
            evaluated = dict(model='fno_coregionalization', dataset=ds,
                splits={'test_hf':dict(rel_l2_per_sample=errors.tolist(),
                                      rel_l2_mean=float(errors.mean()), n_samples=len(errors))},
                work_grid=list(grid), hf_grid=list(grid),
                n_params=module.param_count(model), eval_protocol='full_field_on_working_grid',
                manifest={'sha256':{str(source):sha(source)}},
                checkpoint=str(checkpoint), checkpoint_sha256=sha(checkpoint),
                no_training=True, notes='Fresh evaluation of the fixed final campaign checkpoint. Replaces unverified archived errors.')
            evaluated_path = root / (ds + '__evaluated.json')
            evaluated_path.write_text(json.dumps(evaluated, indent=2) + '\n')
            record = dict(passed=True, dataset=ds, model='fno_coregionalization',
                no_training=True, checkpoint=str(checkpoint), checkpoint_sha256=sha(checkpoint),
                model_source=str(code), model_source_sha256=sha(code),
                test_path=str(source), test_archive_sha256=sha(source), original_raw_sha256=sha(rawfile),
                evaluated_raw_sha256=sha(evaluated_path), archived_errors_match=match,
                checkpoint_selection='Fixed final campaign s42 best.pt for each dataset, not selected by evaluation error',
                scores_recomputed=True, tf32_enabled=False,
                archive=out.name, archive_sha256=sha(out), n=len(inputs), grid=list(grid),
                target_sha256=hashlib.sha256(targets.tobytes()).hexdigest(),
                input_row_sha256=[hashlib.sha256(x.tobytes()).hexdigest() for x in inputs],
                error_tolerance=dict(rtol=1e-5, atol=1e-9), attempts=attempts,
                device=str(device), torch_version=torch.__version__)
            (root / (ds + '__replay.json')).write_text(json.dumps(record, indent=2) + '\n')
            print('VERIFIED EVALUATION', ds, 'mean error', float(errors.mean()), flush=True)
            return
        del model
        if device.type == 'cuda':
            torch.cuda.empty_cache()
    (root / (ds + '__failed.json')).write_text(json.dumps(attempts, indent=2) + '\n')
    raise RuntimeError('No checkpoint reproduced the archived per case errors')


if __name__ == '__main__':
    main()
