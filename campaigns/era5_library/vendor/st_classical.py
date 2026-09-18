"""Classical / statistical theta-only baselines (CPU).  Every arm predicts the fine field from theta alone.

st_mean         : mean fine training field.
st_knn          : distance-weighted k-nearest neighbours in normalised theta over the fine training fields (k by leave-one-out).
st_hf_pod_gp    : fine-only POD + Gaussian-process emulator (Higdon et al. 2008; Guo & Hesthaven 2018).
st_lf_affine_pod: rho * LF_emul(theta) + b, (rho, b) least squares on the fine training rows; LF_emul = POD-GP fit on the
                  coarse pool (the two-scalar affine correction, Zhang-Kim-Park-Haftka 2018 form).
st_koh_pod      : Kennedy & O'Hagan (2000) AR(1) co-kriging, theta-only: y_H(theta) = rho * E[y_L(theta)] + delta(theta).
                  The coarse process is a POD-GP emulator on the coarse pool (its posterior mean replaces the coarse solve
                  at test time); rho and the discrepancy GP (POD coefficients, shared ARD-RBF kernel, as in bench_ct's
                  ct_koh_pod) are fit on the fine training rows against the observed coarse field there (nested design)
                  or against the emulator when the rows are not paired.
st_nargp_pod    : Perdikaris et al. (2017) nonlinear autoregressive GP on POD coefficients: level 2 is a GP over
                  (theta, c_L(theta)) with kernel k_rho(theta) k_f(c_L) + k_delta(theta) (ARD on theta, one shared lengthscale on the
                  leading coarse coefficients); at test the coarse coefficients
                  come from the level-1 emulator posterior (Monte-Carlo mean over posterior samples, plug-in mean also reported).
Top coarse level only (as ct_koh_pod); hyperparameters by marginal likelihood with restarts; energy 0.999, <= 64 POD modes.
"""
from __future__ import annotations
import math, time
import numpy as np
import torch
from st_common import PODGP, SharedGP, ard_rbf, fit_gp, pod_fit, rel_l2_per_sample


def _np(t):
    return t.detach().flatten(1).double().cpu().numpy()


def arm_mean(data, args):
    y = data["Y_hf"][data["hf_tr"]].mean(0, keepdim=True)
    return y.expand(len(data["Xtest"]), *y.shape[1:]), dict(method="mean fine training field")


def arm_knn(data, args):
    tr = data["hf_tr"]; X = data["X_hf"][tr].double(); Y = data["Y_hf"][tr].flatten(1).double(); Xte = data["Xtest"].double()
    def predict(Xq, Xref, Yref, k, exclude_self=False):
        D = torch.cdist(Xq, Xref)
        if exclude_self:
            D.fill_diagonal_(float("inf"))
        dist, idx = D.topk(min(k, Xref.shape[0] - int(exclude_self)), largest=False)
        w = 1.0 / dist.clamp_min(1e-9); w = w / w.sum(1, keepdim=True)
        return (w[:, :, None] * Yref[idx]).sum(1)
    loo = {}
    for k in (1, 2, 3, 5, 8, 12):
        if k >= len(tr):
            break
        p = predict(X, X, Y, k, exclude_self=True)
        loo[k] = float(rel_l2_per_sample(p, Y).mean())
    k = min(loo, key=loo.get)
    pred = predict(Xte, X, Y, k).float().reshape(-1, *data["grid"])
    return pred, dict(method="inverse-distance kNN in normalised theta", k=k, loo_rel_l2_by_k=loo)


def arm_hf_pod_gp(data, args):
    t0 = time.time(); tr = data["hf_tr"]
    em = PODGP(data["X_hf"][tr].double().cpu().numpy(), _np(data["Y_hf"][tr]), args.seed, args.pod_energy, args.pod_modes, args.gp_restarts)
    pred = torch.as_tensor(em.predict(data["Xtest"].double().cpu().numpy()), dtype=torch.float32).reshape(-1, *data["grid"])
    return pred, dict(method="fine-only POD + shared-ARD-RBF GP emulator", n_hf_train=int(len(tr)), fit_seconds=time.time() - t0, **em.info("hf_"))


def _lf_emulator(data, args):
    lf_tr = data["lf_tr"]
    em = PODGP(data["X_lf"][lf_tr].double().cpu().numpy(), _np(data["Y_lf_up"][lf_tr]), args.seed + 7, args.pod_energy, args.pod_modes, args.gp_restarts)
    Xte = data["Xtest"].double().cpu().numpy()
    lf_te = torch.as_tensor(em.predict(Xte), dtype=torch.float32).reshape(-1, *data["grid"])
    # coarse field at the fine training rows: observed when paired (nested design), emulated otherwise
    hf_tr = data["hf_tr"]
    if data["paired"]:
        lf_at_hf = data["Y_lf_up"][hf_tr]; src = "observed coarse field (nested design)"
    else:
        lf_at_hf = torch.as_tensor(em.predict(data["X_hf"][hf_tr].double().cpu().numpy()), dtype=torch.float32).reshape(-1, *data["grid"]); src = "emulated coarse field (rows not paired)"
    info = dict(n_lf_train=int(len(lf_tr)), lf_level="top coarse", coarse_at_fine_rows=src, **em.info("lf_emul_"))
    if data.get("Ytest_lf_up") is not None:
        info["lf_emulator_test_rel_l2"] = float(rel_l2_per_sample(lf_te, data["Ytest_lf_up"]).mean())     # diagnostic only (test LF never used for prediction)
    return em, lf_te, lf_at_hf, info


def arm_lf_affine_pod(data, args, cache=None):
    t0 = time.time(); hf_tr = data["hf_tr"]
    em, lf_te, lf_at_hf, info = cache or _lf_emulator(data, args)
    A = torch.stack((lf_at_hf.flatten(), torch.ones_like(lf_at_hf.flatten())), 1).double(); b = data["Y_hf"][hf_tr].flatten().double()
    sol = torch.linalg.lstsq(A, b[:, None]).solution.flatten(); rho, off = float(sol[0]), float(sol[1])
    return rho * lf_te + off, dict(method="rho * LF_emul(theta) + b, least squares on fine training rows", rho=rho, b=off, fit_seconds=time.time() - t0, **info)


def arm_koh_pod(data, args, cache=None):
    t0 = time.time(); hf_tr = data["hf_tr"]
    em, lf_te, lf_at_hf, info = cache or _lf_emulator(data, args)
    hf = data["Y_hf"][hf_tr]
    rho = float((lf_at_hf * hf).sum() / lf_at_hf.square().sum().clamp_min(1e-20))
    R = _np(hf - rho * lf_at_hf)
    dgp = PODGP(data["X_hf"][hf_tr].double().cpu().numpy(), R, args.seed, args.pod_energy, args.pod_modes, args.gp_restarts)
    delta = torch.as_tensor(dgp.predict(data["Xtest"].double().cpu().numpy()), dtype=torch.float32).reshape(-1, *data["grid"])
    pred = rho * lf_te + delta
    return pred, dict(method="Kennedy-O'Hagan AR(1) co-kriging on POD coefficients, coarse process emulated at test", rho=rho,
                      n_hf_train=int(len(hf_tr)), fit_seconds=time.time() - t0, **info, **dgp.info("delta_"))


def arm_nargp_pod(data, args, cache=None):
    t0 = time.time(); hf_tr = data["hf_tr"]; d = data["cond_dim"]
    em, lf_te, lf_at_hf, info = cache or _lf_emulator(data, args)
    X = data["X_hf"][hf_tr].double().cpu().numpy(); Xte = data["Xtest"].double().cpu().numpy()
    # level-1 coarse coefficients (standardised) at the fine rows and (posterior) at test
    q = min(args.nargp_lf_modes, em.r)                         # leading coarse POD coefficients used as level-2 inputs
    cL_tr = em.coefficients(_np(lf_at_hf))[:, :q]; cm, cs = cL_tr.mean(0), np.maximum(cL_tr.std(0), 1e-12); cL_tr = (cL_tr - cm) / cs
    mL, vL = em.gp.predict(Xte, return_var=True); mL = (mL[:, :q] - cm) / cs; sL = np.sqrt(vL[:, :q]) / cs
    # level-2 targets: fine POD coefficients
    mean, basis, CH, energy = pod_fit(_np(data["Y_hf"][hf_tr]), args.pod_energy, args.pod_modes); rL = cL_tr.shape[1]
    Z = np.concatenate((X, cL_tr), 1)
    # one shared lengthscale for the (standardised) coarse coefficients: keeps the numerical-gradient L-BFGS fit at 2d+4 params
    def kern(p, A, B):
        lr, sr = p[:d], p[d]; lf = np.full(rL, p[d + 1]); ld, sd = p[d + 2:2 * d + 2], p[2 * d + 2]
        return ard_rbf(A[:, :d], B[:, :d], lr, sr) * ard_rbf(A[:, d:], B[:, d:], lf, 0.0) + ard_rbf(A[:, :d], B[:, :d], ld, sd)
    rng = np.random.default_rng(args.seed)
    def x0(jit):
        return np.concatenate((np.zeros(d) + jit * rng.normal(0, 0.3, d), [0.0], [0.5 + jit * rng.normal(0, 0.3)], np.zeros(d) + jit * rng.normal(0, 0.3, d), [-1.0], [math.log(0.1)]))
    bounds = [(-3.0, 4.0)] * d + [(-4.0, 3.0)] + [(-3.0, 4.0)] + [(-3.0, 4.0)] * d + [(-6.0, 3.0), (-7.0, 1.0)]
    chm, chs = CH.mean(0), np.maximum(CH.std(0), 1e-12); Cs = (CH - chm) / chs
    fit = fit_gp(Z, Cs, kern, [x0(0.0)] + [x0(1.0) for _ in range(args.gp_restarts - 1)], bounds); p = fit.x
    K = kern(p, Z, Z) + (np.exp(2 * p[-1]) + 1e-8) * np.eye(len(Z)); L = np.linalg.cholesky(K); A = np.linalg.solve(L.T, np.linalg.solve(L, Cs))
    def level2(cL):
        return kern(p, np.concatenate((Xte, cL), 1), Z) @ A * chs + chm
    plug = level2(mL)
    S = args.nargp_samples; mc = np.zeros_like(plug)
    for s in range(S):
        mc += level2(mL + sL * rng.standard_normal(mL.shape))
    mc /= S
    to_field = lambda C: torch.as_tensor(C @ basis + mean, dtype=torch.float32).reshape(-1, *data["grid"])
    pred, pred_plug = to_field(mc), to_field(plug)
    extra = dict(method="NARGP (Perdikaris 2017) on POD coefficients; level-1 = POD-GP coarse emulator, level-2 kernel k_rho*k_f + k_delta, shared across fine coefficients",
                 n_hf_train=int(len(hf_tr)), hf_pod_modes=int(basis.shape[0]), hf_pod_energy_captured=energy, lf_modes_as_inputs=int(rL),
                 mc_samples=S, gp_nlml=float(fit.fun), gp_converged=bool(fit.success), gp_log_noise=float(p[-1]),
                 gp_log_ell_rho=p[:d].tolist(), gp_log_sf_rho=float(p[d]), gp_log_ell_f=float(p[d + 1]), gp_log_ell_delta=p[d + 2:2 * d + 2].tolist(), gp_log_sf_delta=float(p[2 * d + 2]),
                 plugin_test_rel_l2=float(rel_l2_per_sample(pred_plug, data["Ytest"]).mean()), fit_seconds=time.time() - t0, **info)
    return pred, extra


ARMS = {"st_mean": arm_mean, "st_knn": arm_knn, "st_hf_pod_gp": arm_hf_pod_gp, "st_lf_affine_pod": arm_lf_affine_pod, "st_koh_pod": arm_koh_pod, "st_nargp_pod": arm_nargp_pod}
