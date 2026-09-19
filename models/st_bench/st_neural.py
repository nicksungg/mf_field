"""Neural theta-only multi-fidelity baselines (GPU).  All three consume the coarse pool only for TRAINING.

st_mfdnn      : Meng & Karniadakis (JCP 401:109020, 2020) composite MF-DNN, pointwise on (theta, x):
                NN_L(theta,x) -> y_L ;  y_H = F_lin(theta,x,y_L) + F_nl(theta,x,y_L), F_lin without activations,
                L2 penalty on F_nl; y_L at test comes from NN_L (theta-only).  tanh MLPs, raw coordinates (no Fourier features).
st_mfdeeponet : Howard, Perego, Karniadakis, Stinis (JCP 494:112462, 2023) composite multifidelity DeepONet:
                LF DeepONet G_L(theta)(x);  HF = LinearDeepONet([theta, G_L(theta)(x_1..x_Q)])(x) + NonlinearDeepONet(same)(x),
                L2 penalty on the nonlinear subnet; Q fixed sensor points on the fine grid; unpaired data allowed.
st_dmfal      : Li, Wang, Kirby, Zhe (AISTATS 2022) deep multi-fidelity model used passively (no active learning):
                theta -> MLP -> h_1 -> y_1 = A_1 h_1 (coarse grid);  [theta; h_1] -> MLP -> h_2 -> y_2 = A_2 h_2 (fine grid).
                Trained jointly by MSE on both levels with weight decay (MAP point estimate instead of the variational last layer).
Every arm: fixed optimizer-step budget per stage (100k steps; 20k left most runs still improving at the last step), Adam(W) with cosine decay,
best-validation checkpoint on the held-out fine rows.
"""
from __future__ import annotations
import copy, math, time
import numpy as np
import torch
import torch.nn as nn
from st_common import coordinates, rel_l2_per_sample, seed_all


class MLP(nn.Module):
    def __init__(self, din, hidden, dout, act=nn.Tanh, linear=False):
        super().__init__()
        if linear or not hidden:
            self.net = nn.Linear(din, dout)
        else:
            layers, d = [], din
            for h in hidden:
                layers += [nn.Linear(d, h), act()]; d = h
            layers.append(nn.Linear(d, dout)); self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def _sched(opt, steps):
    return torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(steps, 1), eta_min=1e-5)


def _val_select(step, every, steps, evaluate, best):
    if step % every == 0 or step == steps:
        err = evaluate()
        if err < best[0]:
            best[0], best[1], best[2] = err, step, True
        return err
    return None


# ------------------------------------------------------------------------------------------------------- MF-DNN
def _pointwise_batch(X, Yflat, coords, rows, B, P, g):
    idx = rows[torch.randint(len(rows), (B,), generator=g)]; pidx = torch.randint(coords.shape[0], (P,), generator=g)
    th = X[idx][:, None, :].expand(B, P, X.shape[1]); xy = coords[pidx][None].expand(B, P, 2)
    return torch.cat((th, xy), -1).reshape(B * P, -1), Yflat[idx][:, pidx].reshape(-1)


def _full_field(fn, X, coords, chunk=4):
    out = []
    for i in range(0, len(X), chunk):
        th = X[i:i + chunk]; B, P = th.shape[0], coords.shape[0]
        inp = torch.cat((th[:, None, :].expand(B, P, -1), coords[None].expand(B, P, 2)), -1).reshape(B * P, -1)
        out.append(fn(inp).reshape(B, P))
    return torch.cat(out)


def arm_mfdnn(data, args, device):
    seed_all(args.seed); g = torch.Generator(device="cpu").manual_seed(args.seed); t0 = time.time()
    d = data["cond_dim"]; H = list(args.hidden)
    cL = coordinates(data["grid_lf"], data["registration"], device); cH = coordinates(data["grid"], data["registration"], device)
    X_lf, Y_lf = data["X_lf"], data["Y_lf"].flatten(1); X_hf, Y_hf = data["X_hf"], data["Y_hf"].flatten(1)
    lf_rows = torch.as_tensor(data["lf_tr"]); hf_rows = torch.as_tensor(data["hf_tr"]); va = data["hf_va"]
    nn_l = MLP(d + 2, H, 1).to(device); opt = torch.optim.Adam(nn_l.parameters(), lr=args.lr); sch = _sched(opt, args.steps)
    for step in range(1, args.steps + 1):
        inp, tgt = _pointwise_batch(X_lf, Y_lf, cL, lf_rows, args.batch, args.points, g)
        loss = (nn_l(inp).squeeze(-1) - tgt).square().mean(); opt.zero_grad(); loss.backward(); opt.step(); sch.step()
        if step % 2000 == 0:
            print(f"[mfdnn LF {step}/{args.steps}] mse={loss.item():.3e}", flush=True)
    nn_l.eval()
    with torch.no_grad():
        lf_fit = float(rel_l2_per_sample(_full_field(nn_l, X_lf[lf_rows[:64]], cL), Y_lf[lf_rows[:64]]).mean())
    h1 = MLP(d + 3, [], 1, linear=True).to(device); h2 = MLP(d + 3, H, 1).to(device)
    opt = torch.optim.AdamW([dict(params=h1.parameters(), weight_decay=0.0), dict(params=h2.parameters(), weight_decay=args.wd)], lr=args.lr); sch = _sched(opt, args.steps)
    def composite(inp):                                   # inp (N, d+2) -> y_H
        with torch.no_grad():
            yl = nn_l(inp)
        z = torch.cat((inp, yl), -1); return h1(z) + h2(z)
    def evaluate():
        h1.eval(); h2.eval()
        with torch.no_grad():
            e = float(rel_l2_per_sample(_full_field(composite, X_hf[va], cH), Y_hf[va]).mean())
        h1.train(); h2.train(); return e
    best, best_state, log = [float("inf"), 0, False], None, []
    for step in range(1, args.steps + 1):
        inp, tgt = _pointwise_batch(X_hf, Y_hf, cH, hf_rows, args.batch, args.points, g)
        loss = (composite(inp).squeeze(-1) - tgt).square().mean(); opt.zero_grad(); loss.backward(); opt.step(); sch.step()
        e = _val_select(step, args.eval_every, args.steps, evaluate, best)
        if e is not None:
            log.append(dict(step=step, val_rel_l2=e, train_mse=loss.item()))
            if best[2]:
                best_state = (copy.deepcopy(h1.state_dict()), copy.deepcopy(h2.state_dict())); best[2] = False
            if step % (args.eval_every * 8) == 0:
                print(f"[mfdnn HF {step}/{args.steps}] val {e:.4e} best {best[0]:.4e}@{best[1]}", flush=True)
    h1.load_state_dict(best_state[0]); h2.load_state_dict(best_state[1]); h1.eval(); h2.eval()
    with torch.no_grad():
        pred = _full_field(composite, data["Xtest"], cH).reshape(-1, *data["grid"])
    n_params = sum(p.numel() for m in (nn_l, h1, h2) for p in m.parameters())
    extra = dict(method="Meng-Karniadakis composite MF-DNN (pointwise, tanh, linear + nonlinear HF nets)", hidden=H, steps_per_stage=args.steps,
                 point_batch=args.batch * args.points, lr=args.lr, nonlinear_weight_decay=args.wd, lf_train_rel_l2_first64=lf_fit,
                 selected_step=best[1], best_val_rel_l2=best[0], n_lf_train=int(len(lf_rows)), n_hf_train=int(len(hf_rows)), training_log=log)
    return pred, extra, time.time() - t0, n_params


# ------------------------------------------------------------------------------------------------------- MF-DeepONet (Howard)
class DeepONet(nn.Module):
    def __init__(self, din_branch, hidden, p, linear=False):
        super().__init__()
        self.branch = MLP(din_branch, hidden, p, linear=linear); self.trunk = MLP(2, hidden, p, linear=linear)
        self.bias = nn.Parameter(torch.zeros(1))

    def forward(self, u, x):                              # u (B, din), x (P, 2) -> (B, P)
        return self.branch(u) @ self.trunk(x).T + self.bias


def _sensor_points(grid, coords, q):
    H, W = grid
    if H == 1:
        idx = torch.linspace(0, W - 1, min(q, W)).round().long()
    else:
        s = max(1, int(round(math.sqrt(q)))); ii = torch.linspace(0, H - 1, min(s, H)).round().long(); jj = torch.linspace(0, W - 1, min(s, W)).round().long()
        idx = (ii[:, None] * W + jj[None, :]).reshape(-1)
    return idx.to(coords.device)


def arm_mfdeeponet(data, args, device):
    seed_all(args.seed); g = torch.Generator(device="cpu").manual_seed(args.seed); t0 = time.time()
    d = data["cond_dim"]; H = list(args.hidden); p = args.latent
    cL = coordinates(data["grid_lf"], data["registration"], device); cH = coordinates(data["grid"], data["registration"], device)
    X_lf, Y_lf = data["X_lf"], data["Y_lf"].flatten(1); X_hf, Y_hf = data["X_hf"], data["Y_hf"].flatten(1)
    lf_rows = torch.as_tensor(data["lf_tr"]); hf_rows = torch.as_tensor(data["hf_tr"]); va = data["hf_va"]
    don_l = DeepONet(d, H, p).to(device); opt = torch.optim.Adam(don_l.parameters(), lr=args.lr); sch = _sched(opt, args.steps)
    for step in range(1, args.steps + 1):
        idx = lf_rows[torch.randint(len(lf_rows), (args.batch,), generator=g)]
        loss = (don_l(X_lf[idx], cL) - Y_lf[idx]).square().mean(); opt.zero_grad(); loss.backward(); opt.step(); sch.step()
        if step % 2000 == 0:
            print(f"[mfdeeponet LF {step}/{args.steps}] mse={loss.item():.3e}", flush=True)
    don_l.eval()
    sidx = _sensor_points(data["grid"], cH, args.sensors); xs = cH[sidx]; Q = len(sidx)
    with torch.no_grad():
        lf_fit = float(rel_l2_per_sample(don_l(X_lf[lf_rows[:64]], cL), Y_lf[lf_rows[:64]]).mean())
    lin = DeepONet(d + Q, H, p, linear=True).to(device); nl = DeepONet(d + Q, H, p).to(device)
    opt = torch.optim.AdamW([dict(params=lin.parameters(), weight_decay=0.0), dict(params=nl.parameters(), weight_decay=args.wd)], lr=args.lr); sch = _sched(opt, args.steps)
    def composite(th, x):
        with torch.no_grad():
            u = torch.cat((th, don_l(th, xs)), 1)
        return lin(u, x) + nl(u, x)
    def predict(th, x, chunk=8):
        return torch.cat([composite(th[i:i + chunk], x) for i in range(0, len(th), chunk)])
    def evaluate():
        lin.eval(); nl.eval()
        with torch.no_grad():
            e = float(rel_l2_per_sample(predict(X_hf[va], cH), Y_hf[va]).mean())
        lin.train(); nl.train(); return e
    best, best_state, log = [float("inf"), 0, False], None, []
    for step in range(1, args.steps + 1):
        idx = hf_rows[torch.randint(len(hf_rows), (args.batch,), generator=g)]
        loss = (composite(X_hf[idx], cH) - Y_hf[idx]).square().mean(); opt.zero_grad(); loss.backward(); opt.step(); sch.step()
        e = _val_select(step, args.eval_every, args.steps, evaluate, best)
        if e is not None:
            log.append(dict(step=step, val_rel_l2=e, train_mse=loss.item()))
            if best[2]:
                best_state = (copy.deepcopy(lin.state_dict()), copy.deepcopy(nl.state_dict())); best[2] = False
            if step % (args.eval_every * 8) == 0:
                print(f"[mfdeeponet HF {step}/{args.steps}] val {e:.4e} best {best[0]:.4e}@{best[1]}", flush=True)
    lin.load_state_dict(best_state[0]); nl.load_state_dict(best_state[1]); lin.eval(); nl.eval()
    with torch.no_grad():
        pred = predict(data["Xtest"], cH).reshape(-1, *data["grid"])
    n_params = sum(p_.numel() for m in (don_l, lin, nl) for p_ in m.parameters())
    extra = dict(method="Howard et al. 2023 composite MF-DeepONet (LF DeepONet -> linear + nonlinear DeepONets on [theta, G_L at sensors])", hidden=H, latent=p,
                 sensors=int(Q), steps_per_stage=args.steps, row_batch=args.batch, lr=args.lr, nonlinear_weight_decay=args.wd, lf_train_rel_l2_first64=lf_fit,
                 selected_step=best[1], best_val_rel_l2=best[0], n_lf_train=int(len(lf_rows)), n_hf_train=int(len(hf_rows)), training_log=log)
    return pred, extra, time.time() - t0, n_params


# ------------------------------------------------------------------------------------------------------- DMFAL (passive)
class DMFAL(nn.Module):
    def __init__(self, d, hidden, k, cells_l, cells_h):
        super().__init__()
        self.enc1 = MLP(d, hidden, k); self.A1 = nn.Linear(k, cells_l); self.enc2 = MLP(d + k, hidden, k); self.A2 = nn.Linear(k, cells_h)

    def forward(self, th):
        h1 = self.enc1(th); h2 = self.enc2(torch.cat((th, h1), 1)); return self.A1(h1), self.A2(h2)


def arm_dmfal(data, args, device):
    seed_all(args.seed); g = torch.Generator(device="cpu").manual_seed(args.seed); t0 = time.time()
    d = data["cond_dim"]; X_lf, Y_lf = data["X_lf"], data["Y_lf"].flatten(1); X_hf, Y_hf = data["X_hf"], data["Y_hf"].flatten(1)
    lf_rows = torch.as_tensor(data["lf_tr"]); hf_rows = torch.as_tensor(data["hf_tr"]); va = data["hf_va"]
    model = DMFAL(d, list(args.hidden), args.latent, Y_lf.shape[1], Y_hf.shape[1]).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.wd); sch = _sched(opt, args.steps)
    def evaluate():
        model.eval()
        with torch.no_grad():
            e = float(rel_l2_per_sample(model(X_hf[va])[1], Y_hf[va]).mean())
        model.train(); return e
    best, best_state, log = [float("inf"), 0, False], None, []
    for step in range(1, args.steps + 1):
        il = lf_rows[torch.randint(len(lf_rows), (args.batch,), generator=g)]; ih = hf_rows[torch.randint(len(hf_rows), (args.batch,), generator=g)]
        y1, _ = model(X_lf[il]); _, y2 = model(X_hf[ih])
        loss = (y1 - Y_lf[il]).square().mean() + (y2 - Y_hf[ih]).square().mean(); opt.zero_grad(); loss.backward(); opt.step(); sch.step()
        e = _val_select(step, args.eval_every, args.steps, evaluate, best)
        if e is not None:
            log.append(dict(step=step, val_rel_l2=e, train_loss=loss.item()))
            if best[2]:
                best_state = copy.deepcopy(model.state_dict()); best[2] = False
            if step % (args.eval_every * 8) == 0:
                print(f"[dmfal {step}/{args.steps}] val {e:.4e} best {best[0]:.4e}@{best[1]}", flush=True)
    model.load_state_dict(best_state); model.eval()
    with torch.no_grad():
        pred = model(data["Xtest"])[1].reshape(-1, *data["grid"])
    extra = dict(method="DMFAL deep multi-fidelity model (Li-Wang-Kirby-Zhe 2022), passive, MAP training", hidden=list(args.hidden), latent=args.latent,
                 steps=args.steps, row_batch=args.batch, lr=args.lr, weight_decay=args.wd, selected_step=best[1], best_val_rel_l2=best[0],
                 n_lf_train=int(len(lf_rows)), n_hf_train=int(len(hf_rows)), training_log=log)
    return pred, extra, time.time() - t0, sum(p.numel() for p in model.parameters())


ARMS = {"st_mfdnn": arm_mfdnn, "st_mfdeeponet": arm_mfdeeponet, "st_dmfal": arm_dmfal}
