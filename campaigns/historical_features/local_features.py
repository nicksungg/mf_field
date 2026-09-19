"""Additional summaries of predictions; no targets, labels, or fitted quantities."""
import numpy as np

REGIONS = ['top_left', 'top_right', 'bottom_left', 'bottom_right', 'edge_band', 'interior']
STATISTICS = ['log_rms_ratio', 'signed_disagreement', 'log_rms_disagreement', 'log_gradient_ratio']
LOCAL_NAMES = [f'{region}:{stat}' for region in REGIONS for stat in STATISTICS]

def region_masks(h, w):
    assert h >= 4 and w >= 4
    yy, xx = np.mgrid[:h, :w]
    edge_h, edge_w = max(1, int(np.ceil(.1*h))), max(1, int(np.ceil(.1*w)))
    edge = (yy < edge_h) | (yy >= h-edge_h) | (xx < edge_w) | (xx >= w-edge_w)
    return [(yy<h//2)&(xx<w//2), (yy<h//2)&(xx>=w//2),
            (yy>=h//2)&(xx<w//2), (yy>=h//2)&(xx>=w//2), edge, ~edge]

def local_features(predictions):
    p = np.asarray(predictions, np.float64)
    assert p.ndim == 4 and np.isfinite(p).all()
    n, m, h, w = p.shape
    median = np.median(p, axis=1)
    scale = np.maximum(np.sqrt(np.mean(median**2, axis=(-2,-1))), 1e-20)
    own_scale = np.maximum(np.sqrt(np.mean(p**2, axis=(-2,-1))), scale[:,None]*1e-12)
    difference = p-median[:,None]
    # Gradients use unit-domain spacing. Edge bands are spatial summaries, not BC assertions.
    gy, gx = np.gradient(p, 1/h, 1/w, axis=(-2,-1))
    grad2 = gy**2+gx**2
    parts = []
    for mask in region_masks(h,w):
        local_rms = np.sqrt(np.mean(p[:,:,mask]**2, axis=-1))/own_scale
        signed = np.mean(difference[:,:,mask], axis=-1)/scale[:,None]
        disagreement = np.sqrt(np.mean(difference[:,:,mask]**2,axis=-1))/scale[:,None]
        gradient = np.sqrt(np.mean(grad2[:,:,mask],axis=-1))/own_scale
        parts.extend([np.log1p(local_rms), signed, np.log1p(disagreement), np.log1p(gradient)])
    result = np.stack(parts,axis=-1)
    assert result.shape == (n,m,24) and np.isfinite(result).all()
    return result

def parameter_blocks(theta_by_dataset, dataset_order, rows, datasets, fit_indices):
    """Raw parameters keep their dataset meaning. Zero-centered inactive blocks are zero.

    Every mean and std is computed only on fitting rows of that dataset.
    Returns (N,total input dimensions), names, fitted scaling metadata.
    """
    datasets = np.asarray(datasets); rows = np.asarray(rows)
    width = sum(theta_by_dataset[d].shape[1] for d in dataset_order)
    result = np.zeros((len(rows),width),np.float64)
    names=[]; scales={}; offset=0
    for d in dataset_order:
        idx=np.flatnonzero(datasets==d)
        fitting=np.asarray(fit_indices)[datasets[fit_indices]==d]
        assert len(fitting)>0, ('No fitting inputs for dataset',d)
        source=np.asarray(theta_by_dataset[d],np.float64)
        fit=source[rows[fitting]]
        mu=fit.mean(0);sd=fit.std(0)
        constant=sd < 1e-10
        safe_sd=np.where(constant,1.,sd)
        value=np.clip((source[rows[idx]]-mu)/safe_sd,-8,8)
        # A parameter never varied in fitting cannot supply a calibrated response.
        value[:,constant]=0.
        dim=source.shape[1]
        result[idx,offset:offset+dim]=value
        names.extend(f'{d}:input_{j}' for j in range(dim))
        scales[d]=dict(offset=offset,dimensions=dim,mean=mu.tolist(),std=safe_sd.tolist(),
                       constant=constant.tolist(),fitting_count=len(fitting))
        offset+=dim
    assert np.isfinite(result).all()
    return result,names,scales
