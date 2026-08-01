"""Env-knob configuration for `r2s1_stagefree_permode` (card r2s1_direct-B3).

Every knob below is transcribed VERBATIM from the card's `recipe.env` block
(`experiment_cards/r2s1_direct/batch_3/B3.json`) — the dict was generated
programmatically from the card JSON, so no hand-transcription happened. The
in-file defaults are byte-identical to the recipe values, so the family always
runs the card's configuration; the SLURM scripts additionally pass the same
list through `score_panel.py --env` so the knobs enter the eval layer's
`code_hash` (score_panel.py::code_hash folds sorted env items into the cache
key).

The EIGHT keys prefixed `_` in the recipe (`_scored_arm`, `_scored_split`,
`_ref_split_prefix`, `_guard_tier`, `_build_gates`, `_sbatch_time`,
`_prior_art_declarations`, `_note`) are card DIRECTIVES, not env knobs, and are
deliberately absent here (recipe `_note`: "keys prefixed _ are card directives,
NOT passed to --env"; starter handoff says the same).

Seam assertions at the bottom: the card FIXES these values. A different value
means the recipe changed underneath the implementation — raise, never default
(program.md §5.3).
"""
from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field

import numpy as np

# --- verbatim from recipe.env (card r2s1_direct-B3) --------------------------
RECIPE_ENV = {
    'R2S1B3_SCORED_ARM': 'stagefree_permode_set_head',
    'R2S1B3_STAGE_POLICY': 'scored_arm_is_stage_free',
    'R2S1B3_DIRECTION_BANK': 'dc_meanfield,pod_0_49',
    'R2S1B3_POD_BASIS_N': '50',
    'R2S1B3_POD_DC_ORTHOGONALIZE': '1',
    'R2S1B3_CENTER_STAT': 'norm_meanfield_over_geomean_norm_y',
    'R2S1B3_CENTER_TAU': '1.0',
    'R2S1B3_CENTER_FORMS': 'fact,add',
    'R2S1B3_BASIS_FORM_MATCHED': '1',
    'R2S1B3_SELECT_INDEXING': 'set',
    'R2S1B3_SELECT_STAT': 'oof_r2_per_direction_best_family',
    'R2S1B3_SELECT_TAU': '0.1',
    'R2S1B3_SELECT_KFOLD': '5',
    'R2S1B3_SELECT_MIN': '1',
    'R2S1B3_SELECT_MAX': '32',
    'R2S1B3_MAP_BANK': 'affine,quadratic,rbf_kernel_ridge,knn',
    'R2S1B3_MAP_SELECT': 'oof_r2_per_direction',
    'R2S1B3_MAP_RIDGE_ALPHA': 'exact_loo_grid_1e-6:1e2:13',
    'R2S1B3_MAP_KNN_K': '1,2,4,8',
    'R2S1B3_MAP_RBF_GAMMA': 'median_heuristic',
    'R2S1B3_ORACLE_CEILING': '1',
    'R2S1B3_WIENER_BANDS': '6',
    'R2S1B3_WIENER_GRID': '0:1.5:31',
    'R2S1B3_WIENER_PASSES': '2',
    'R2S1B3_WIENER_STANDDOWN': '1',
    'R2S1B3_WIENER_FIT': 'calib_fold_coord_descent',
    'R2S1B3_WIENER_APPLY_TO': 'stage_arms_only',
    'R2S1B3_WIENER_REPORT_LS_OPTIMAL': '1',
    'R2S1B3_BLEND_BASES': 'zero,train_mean,nn_condition,dc_only',
    'R2S1B3_BLEND_DECORR_AUDIT': '1',
    'R2S1B3_BLEND_DECORR_RHO_MAX': '0.95',
    'R2S1B3_BLEND_GRID': '0:1:21',
    'R2S1B3_BLEND_SELECT': 'calib_fold_relL2',
    'R2S1B3_BLEND_APPLY_TO': 'stage_arms_only',
    'R2S1B3_BG_COMBINE': '1',
    'R2S1B3_BG_COV_SOURCE': 'calib_fold_prediction_error_covariance',
    'R2S1B3_BG_SHRINKAGE': 'ledoit_wolf',
    'R2S1B3_BG_CITATION': 'bates_granger_1969_minimum_variance_combination',
    'R2S1B3_RHO_LAW_PRELUDE': '1',
    'R2S1B3_RHO_LAW_FORM': 'bates_granger_two_forecast',
    'R2S1B3_RHO_LAW_PRELUDE_BEFORE_TEST': '1',
    'R2S1B3_FOLD_MODEL_FRAC': '0.10',
    'R2S1B3_FOLD_CALIB_FRAC': '0.10',
    'R2S1B3_FOLD_DISJOINT': '1',
    'R2S1B3_FOLD_RESAMPLES': '5',
    'R2S1B3_SMALL_N_PROTOCOL': 'loo',
    'R2S1B3_SMALL_N_THRESHOLD': '20',
    'R2S1B3_DECODER_ARMS': 'big',
    'R2S1B3_DEC_BIG': 'width64,blocks4,modes16,latent16,film128',
    'R2S1B3_DEC_SELECT': 'model_fold_best_epoch',
    'R2S1B3_DEC_LR': '1e-3',
    'R2S1B3_DEC_WD': '1e-5',
    'R2S1B3_DEC_BATCH': '16',
    'R2S1B3_DEC_CLIP': '1.0',
    'R2S1B3_DEC_SCHED': 'cosine',
    'R2S1B3_DEC_LOSS': 'rel_l2',
    'R2S1B3_DEC_DENOM_FLOOR': 'p25_median',
    'R2S1B3_DEC_WORK_CAP': '256',
    'R2S1B3_DEC_CKPT_EVERY_EPOCH': '1',
    'R2S1B3_DEC_CKPT_RNG_STATE': '1',
    'R2S1B3_DEC_DUMP_PREDS': '1',
    'R2S1B3_PREDS_OUT_PATTERN': 'preds_test_{arm}_{dataset}_s{seed}.npz',
    'R2S1B3_REF_ARMS': ('head_set_affine,head_window_affine,decoder_big,'
                        'stage_wiener_head,stage_wiener_decoder,'
                        'stage_blend_head,stage_blend_decoder,'
                        'stage_bg_head,stage_bg_decoder,'
                        'dc_only,zero,train_mean,nn_condition'),
    'R2S1B3_FLOOR_ARMS': 'nn_condition,train_mean,zero',
    'R2S1B3_FLOOR_SEAM_TOL': '1e-9',
    'R2S1B3_FLOOR_SEAM_RAISE': '1',
    'R2S1B3_H2_PROJECTION': '1',
    'R2S1B3_H2_DATASETS': 'sharp__cahn_hilliard,sharp__allen_cahn_2d',
    'R2S1B3_SET_VS_WINDOW_AUDIT': '1',
    'R2S1B3_LEAKAGE_TRIPWIRE': '1',
    'R2S1B3_NRMSE_IMPORT': 'round2_eval_nrmse',
    'R2S1B3_DIAG_OUT': 'mffp_autoresearch_outputs/round2/r2s1_direct/B3/eval',
}

# Builder-chosen constants that the card does NOT fix. Each is a prior-best
# carried from an earlier card in THIS stream (never a free guess); all are
# declared in the card's build_notes.
#
#   WIENER_BAND_EDGES  inner radial edges of the 6 bands. The card fixes the
#                      COUNT (R2S1B3_WIENER_BANDS=6). These edges are the
#                      promoted tool's default (`tools/band_gain_counterfactual.py
#                      --bands 4,8,16,32`) and exactly what r2s1_direct-B1/B2
#                      measured on -> bands [DC, 0.5<k<=4, 4<k<=8, 8<k<=16,
#                      16<k<=32, k>32].
#   DEC_COND_RFF       random-Fourier condition features for the decoder arm
#                      = 16, i.e. r2s1_direct-B1's `R2S1_COND_RFF`; the card
#                      calls ref_decoder_big the B1-scale decoder, so its front
#                      end is B1's (and B2's `ref_decoder_big`, byte-identical
#                      spec width64,blocks4,modes16,latent16,film128).
WIENER_BAND_EDGES = (4.0, 8.0, 16.0, 32.0)
DEC_COND_RFF = 16


def _get(key: str) -> str:
    if key not in RECIPE_ENV:
        raise KeyError(f"{key} is not a card recipe knob")
    return os.environ.get(key, RECIPE_ENV[key])


def _grid(spec: str) -> np.ndarray:
    lo, hi, n = spec.split(":")
    return np.linspace(float(lo), float(hi), int(n))


def _alpha_grid(spec: str) -> np.ndarray:
    """`exact_loo_grid_1e-6:1e2:13` -> logspace(log10(1e-6), log10(1e2), 13)."""
    if not spec.startswith("exact_loo_grid_"):
        raise ValueError(f"unsupported R2S1B3_MAP_RIDGE_ALPHA={spec!r}")
    lo, hi, n = spec[len("exact_loo_grid_"):].split(":")
    return np.logspace(np.log10(float(lo)), np.log10(float(hi)), int(n))


def _dec_spec(spec: str) -> dict:
    """`width64,blocks4,modes16,latent16,film128` -> dict of ints."""
    out = {}
    for tok in spec.split(","):
        tok = tok.strip()
        for key in ("width", "blocks", "modes", "latent", "film"):
            if tok.startswith(key):
                out[key] = int(tok[len(key):])
                break
        else:
            raise ValueError(f"unparsed decoder spec token {tok!r} in {spec!r}")
    missing = {"width", "blocks", "modes", "latent", "film"} - set(out)
    if missing:
        raise ValueError(f"decoder spec {spec!r} missing {sorted(missing)}")
    return out


@dataclass
class Config:
    scored_arm: str
    stage_policy: str
    direction_bank: list
    pod_basis_n: int
    pod_dc_orthogonalize: bool
    center_stat: str
    center_tau: float
    center_forms: list
    basis_form_matched: bool
    select_indexing: str
    select_stat: str
    select_tau: float
    select_kfold: int
    select_min: int
    select_max: int
    map_bank: list
    map_select: str
    map_ridge_alpha: str
    map_knn_k: list
    map_rbf_gamma: str
    oracle_ceiling: bool
    wiener_bands: int
    wiener_grid: str
    wiener_passes: int
    wiener_standdown: bool
    wiener_fit: str
    wiener_apply_to: str
    wiener_report_ls_optimal: bool
    blend_bases: list
    blend_decorr_audit: bool
    blend_decorr_rho_max: float
    blend_grid: str
    blend_select: str
    blend_apply_to: str
    bg_combine: bool
    bg_cov_source: str
    bg_shrinkage: str
    bg_citation: str
    rho_law_prelude: bool
    rho_law_form: str
    rho_law_prelude_before_test: bool
    fold_model_frac: float
    fold_calib_frac: float
    fold_disjoint: bool
    fold_resamples: int
    small_n_protocol: str
    small_n_threshold: int
    decoder_arms: list
    dec_big: dict
    dec_select: str
    dec_lr: float
    dec_wd: float
    dec_batch: int
    dec_clip: float
    dec_sched: str
    dec_loss: str
    dec_denom_floor: str
    dec_work_cap: int
    dec_ckpt_every_epoch: int
    dec_ckpt_rng_state: bool
    dec_dump_preds: bool
    preds_out_pattern: str
    ref_arms: list
    floor_arms: list
    floor_seam_tol: float
    floor_seam_raise: bool
    h2_projection: bool
    h2_datasets: list
    set_vs_window_audit: bool
    leakage_tripwire: bool
    nrmse_import: str
    diag_out: str
    band_edges: tuple = WIENER_BAND_EDGES
    dec_cond_rff: int = DEC_COND_RFF
    env_snapshot: dict = field(default_factory=dict)

    def alpha_grid(self) -> np.ndarray:
        return _alpha_grid(self.map_ridge_alpha)

    def wiener_gains(self) -> np.ndarray:
        return _grid(self.wiener_grid)

    def blend_lambdas(self) -> np.ndarray:
        return _grid(self.blend_grid)


def load_config() -> Config:
    snap = {k: _get(k) for k in RECIPE_ENV}
    cfg = Config(
        scored_arm=_get("R2S1B3_SCORED_ARM"),
        stage_policy=_get("R2S1B3_STAGE_POLICY"),
        direction_bank=[s for s in _get("R2S1B3_DIRECTION_BANK").split(",") if s],
        pod_basis_n=int(_get("R2S1B3_POD_BASIS_N")),
        pod_dc_orthogonalize=_get("R2S1B3_POD_DC_ORTHOGONALIZE") == "1",
        center_stat=_get("R2S1B3_CENTER_STAT"),
        center_tau=float(_get("R2S1B3_CENTER_TAU")),
        center_forms=[s for s in _get("R2S1B3_CENTER_FORMS").split(",") if s],
        basis_form_matched=_get("R2S1B3_BASIS_FORM_MATCHED") == "1",
        select_indexing=_get("R2S1B3_SELECT_INDEXING"),
        select_stat=_get("R2S1B3_SELECT_STAT"),
        select_tau=float(_get("R2S1B3_SELECT_TAU")),
        select_kfold=int(_get("R2S1B3_SELECT_KFOLD")),
        select_min=int(_get("R2S1B3_SELECT_MIN")),
        select_max=int(_get("R2S1B3_SELECT_MAX")),
        map_bank=[s for s in _get("R2S1B3_MAP_BANK").split(",") if s],
        map_select=_get("R2S1B3_MAP_SELECT"),
        map_ridge_alpha=_get("R2S1B3_MAP_RIDGE_ALPHA"),
        map_knn_k=[int(s) for s in _get("R2S1B3_MAP_KNN_K").split(",") if s],
        map_rbf_gamma=_get("R2S1B3_MAP_RBF_GAMMA"),
        oracle_ceiling=_get("R2S1B3_ORACLE_CEILING") == "1",
        wiener_bands=int(_get("R2S1B3_WIENER_BANDS")),
        wiener_grid=_get("R2S1B3_WIENER_GRID"),
        wiener_passes=int(_get("R2S1B3_WIENER_PASSES")),
        wiener_standdown=_get("R2S1B3_WIENER_STANDDOWN") == "1",
        wiener_fit=_get("R2S1B3_WIENER_FIT"),
        wiener_apply_to=_get("R2S1B3_WIENER_APPLY_TO"),
        wiener_report_ls_optimal=_get("R2S1B3_WIENER_REPORT_LS_OPTIMAL") == "1",
        blend_bases=[s for s in _get("R2S1B3_BLEND_BASES").split(",") if s],
        blend_decorr_audit=_get("R2S1B3_BLEND_DECORR_AUDIT") == "1",
        blend_decorr_rho_max=float(_get("R2S1B3_BLEND_DECORR_RHO_MAX")),
        blend_grid=_get("R2S1B3_BLEND_GRID"),
        blend_select=_get("R2S1B3_BLEND_SELECT"),
        blend_apply_to=_get("R2S1B3_BLEND_APPLY_TO"),
        bg_combine=_get("R2S1B3_BG_COMBINE") == "1",
        bg_cov_source=_get("R2S1B3_BG_COV_SOURCE"),
        bg_shrinkage=_get("R2S1B3_BG_SHRINKAGE"),
        bg_citation=_get("R2S1B3_BG_CITATION"),
        rho_law_prelude=_get("R2S1B3_RHO_LAW_PRELUDE") == "1",
        rho_law_form=_get("R2S1B3_RHO_LAW_FORM"),
        rho_law_prelude_before_test=_get("R2S1B3_RHO_LAW_PRELUDE_BEFORE_TEST") == "1",
        fold_model_frac=float(_get("R2S1B3_FOLD_MODEL_FRAC")),
        fold_calib_frac=float(_get("R2S1B3_FOLD_CALIB_FRAC")),
        fold_disjoint=_get("R2S1B3_FOLD_DISJOINT") == "1",
        fold_resamples=int(_get("R2S1B3_FOLD_RESAMPLES")),
        small_n_protocol=_get("R2S1B3_SMALL_N_PROTOCOL"),
        small_n_threshold=int(_get("R2S1B3_SMALL_N_THRESHOLD")),
        decoder_arms=[s for s in _get("R2S1B3_DECODER_ARMS").split(",") if s],
        dec_big=_dec_spec(_get("R2S1B3_DEC_BIG")),
        dec_select=_get("R2S1B3_DEC_SELECT"),
        dec_lr=float(_get("R2S1B3_DEC_LR")),
        dec_wd=float(_get("R2S1B3_DEC_WD")),
        dec_batch=int(_get("R2S1B3_DEC_BATCH")),
        dec_clip=float(_get("R2S1B3_DEC_CLIP")),
        dec_sched=_get("R2S1B3_DEC_SCHED"),
        dec_loss=_get("R2S1B3_DEC_LOSS"),
        dec_denom_floor=_get("R2S1B3_DEC_DENOM_FLOOR"),
        dec_work_cap=int(_get("R2S1B3_DEC_WORK_CAP")),
        dec_ckpt_every_epoch=int(_get("R2S1B3_DEC_CKPT_EVERY_EPOCH")),
        dec_ckpt_rng_state=_get("R2S1B3_DEC_CKPT_RNG_STATE") == "1",
        dec_dump_preds=_get("R2S1B3_DEC_DUMP_PREDS") == "1",
        preds_out_pattern=_get("R2S1B3_PREDS_OUT_PATTERN"),
        ref_arms=[s for s in _get("R2S1B3_REF_ARMS").split(",") if s],
        floor_arms=[s for s in _get("R2S1B3_FLOOR_ARMS").split(",") if s],
        floor_seam_tol=float(_get("R2S1B3_FLOOR_SEAM_TOL")),
        floor_seam_raise=_get("R2S1B3_FLOOR_SEAM_RAISE") == "1",
        h2_projection=_get("R2S1B3_H2_PROJECTION") == "1",
        h2_datasets=[s for s in _get("R2S1B3_H2_DATASETS").split(",") if s],
        set_vs_window_audit=_get("R2S1B3_SET_VS_WINDOW_AUDIT") == "1",
        leakage_tripwire=_get("R2S1B3_LEAKAGE_TRIPWIRE") == "1",
        nrmse_import=_get("R2S1B3_NRMSE_IMPORT"),
        diag_out=_get("R2S1B3_DIAG_OUT"),
        env_snapshot=snap,
    )

    # ── seam assertions (assert, never default) ──────────────────────
    if cfg.scored_arm != "stagefree_permode_set_head":
        raise ValueError(f"unsupported R2S1B3_SCORED_ARM={cfg.scored_arm!r}")
    if cfg.stage_policy != "scored_arm_is_stage_free":
        raise ValueError(
            f"unsupported R2S1B3_STAGE_POLICY={cfg.stage_policy!r}; the card's "
            "load-bearing move is that the SCORED column carries no Wiener gains "
            "and no blend")
    if cfg.direction_bank != ["dc_meanfield", "pod_0_49"]:
        raise ValueError(f"unsupported R2S1B3_DIRECTION_BANK={cfg.direction_bank!r}")
    if not cfg.pod_dc_orthogonalize:
        raise ValueError("R2S1B3_POD_DC_ORTHOGONALIZE=0 is not implemented "
                         "(the card fixes a DC-removed POD basis)")
    if cfg.center_stat != "norm_meanfield_over_geomean_norm_y":
        raise ValueError(f"unsupported R2S1B3_CENTER_STAT={cfg.center_stat!r}")
    if sorted(cfg.center_forms) != ["add", "fact"]:
        raise ValueError(f"unsupported R2S1B3_CENTER_FORMS={cfg.center_forms!r}")
    if not cfg.basis_form_matched:
        raise ValueError("R2S1B3_BASIS_FORM_MATCHED=0 is not implemented (that is "
                         "B2's defect T1-F7, which this card repairs)")
    if cfg.select_indexing != "set":
        raise ValueError(f"unsupported R2S1B3_SELECT_INDEXING={cfg.select_indexing!r}")
    if cfg.select_stat != "oof_r2_per_direction_best_family":
        raise ValueError(f"unsupported R2S1B3_SELECT_STAT={cfg.select_stat!r}")
    if cfg.map_bank != ["affine", "quadratic", "rbf_kernel_ridge", "knn"]:
        raise ValueError(f"unsupported R2S1B3_MAP_BANK={cfg.map_bank!r}")
    if cfg.map_select != "oof_r2_per_direction":
        raise ValueError(f"unsupported R2S1B3_MAP_SELECT={cfg.map_select!r}")
    if cfg.map_rbf_gamma != "median_heuristic":
        raise ValueError(f"unsupported R2S1B3_MAP_RBF_GAMMA={cfg.map_rbf_gamma!r}")
    if cfg.wiener_fit != "calib_fold_coord_descent":
        raise ValueError(f"unsupported R2S1B3_WIENER_FIT={cfg.wiener_fit!r}")
    if cfg.wiener_apply_to != "stage_arms_only":
        raise ValueError(
            f"unsupported R2S1B3_WIENER_APPLY_TO={cfg.wiener_apply_to!r}; the "
            "scored column is stage-free in this card")
    if cfg.wiener_bands != len(cfg.band_edges) + 2:
        raise ValueError(
            f"R2S1B3_WIENER_BANDS={cfg.wiener_bands} but the band edges "
            f"{cfg.band_edges} define {len(cfg.band_edges) + 2} bands")
    gains = cfg.wiener_gains()
    if float(gains.max()) > 1.5 + 1e-12:
        raise ValueError(
            f"BUILD GATE G-D: R2S1B3_WIENER_GRID={cfg.wiener_grid!r} exceeds the "
            "capped range [0, 1.5] (B2 part 7 item 3: widening past 1.5 makes "
            "cahn_hilliard strictly worse)")
    if not cfg.wiener_standdown:
        raise ValueError("BUILD GATE G-D requires the explicit stand-down candidate")
    if cfg.blend_select != "calib_fold_relL2":
        raise ValueError(f"unsupported R2S1B3_BLEND_SELECT={cfg.blend_select!r}")
    if cfg.blend_apply_to != "stage_arms_only":
        raise ValueError(f"unsupported R2S1B3_BLEND_APPLY_TO={cfg.blend_apply_to!r}")
    if not cfg.blend_decorr_audit:
        raise ValueError("BUILD GATE G-E requires the blend decorrelation audit")
    if cfg.bg_cov_source != "calib_fold_prediction_error_covariance":
        raise ValueError(f"unsupported R2S1B3_BG_COV_SOURCE={cfg.bg_cov_source!r}")
    if cfg.bg_shrinkage != "ledoit_wolf":
        raise ValueError(f"unsupported R2S1B3_BG_SHRINKAGE={cfg.bg_shrinkage!r}")
    if cfg.rho_law_form != "bates_granger_two_forecast":
        raise ValueError(f"unsupported R2S1B3_RHO_LAW_FORM={cfg.rho_law_form!r}")
    if not (cfg.rho_law_prelude and cfg.rho_law_prelude_before_test):
        raise ValueError("BUILD GATE G-B requires the rho prelude to be written "
                         "BEFORE any test tensor is read")
    if not cfg.fold_disjoint:
        raise ValueError("R2S1B3_FOLD_DISJOINT=0 is not implemented (card fixes disjoint)")
    if cfg.small_n_protocol != "loo":
        raise ValueError(f"unsupported R2S1B3_SMALL_N_PROTOCOL={cfg.small_n_protocol!r}")
    if cfg.decoder_arms != ["big"]:
        raise ValueError(f"unsupported R2S1B3_DECODER_ARMS={cfg.decoder_arms!r}")
    if cfg.dec_select != "model_fold_best_epoch":
        raise ValueError(f"unsupported R2S1B3_DEC_SELECT={cfg.dec_select!r}")
    if cfg.dec_sched != "cosine":
        raise ValueError(f"unsupported R2S1B3_DEC_SCHED={cfg.dec_sched!r}")
    if cfg.dec_loss != "rel_l2":
        raise ValueError(f"unsupported R2S1B3_DEC_LOSS={cfg.dec_loss!r}")
    if not cfg.dec_dump_preds:
        raise ValueError("BUILD GATE G-A requires per-arm preds_test.npz for every "
                         "decoder arm (B2 part 7 item 4)")
    if not cfg.floor_seam_raise:
        raise ValueError("BUILD GATE G-C requires the floor seam check to RAISE")
    if sorted(cfg.floor_arms) != ["nn_condition", "train_mean", "zero"]:
        raise ValueError(f"unsupported R2S1B3_FLOOR_ARMS={cfg.floor_arms!r}")
    if cfg.nrmse_import != "round2_eval_nrmse":
        raise ValueError(
            f"unsupported R2S1B3_NRMSE_IMPORT={cfg.nrmse_import!r}; the card "
            "requires the round eval nrmse.py to be imported, not re-implemented")
    return cfg


def config_dict(cfg: Config) -> dict:
    d = asdict(cfg)
    d["band_edges"] = list(cfg.band_edges)
    return d
