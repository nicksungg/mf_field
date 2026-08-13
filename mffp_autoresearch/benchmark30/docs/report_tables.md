## Headline — film-relative skill (common eligible set, 29 datasets)

Panel geomean of `nrmse_film / nrmse_model`, per seed: 0.5934, 0.6047, 0.6032.
**0.6004** [0.5934, 0.6047] (seed_plus_run_interval; >1 means the certified stack beats film transfer).

## Per-group geomeans

| group | n | mean | interval |
| --- | --- | --- | --- |
| core | 10 | 0.3982 | [0.3900, 0.4121] |
| ext | 6 | 0.7845 | [0.7479, 0.8461] |
| sharp | 13 | 0.7290 | [0.6921, 0.7584] |

## Per-dataset rel-L2 (3-seed mean [min, max])

| dataset | r3s2_route_b30 | mf_fno_transfer_film | skill (film/model) |
| --- | --- | --- | --- |
| allen_cahn_generated | 0.0049 [0.0046, 0.0052] | 0.0013 [0.0011, 0.0015] | 0.2642 |
| darcy_generated | 0.0339 [0.0333, 0.0348] | 0.0278 [0.0277, 0.0279] | 0.8206 |
| era5 | — | 0.0451 [0.0449, 0.0453] | — |
| ext__cahn_hilliard_2d | 0.4109 [0.4016, 0.4292] | 0.1698 [0.1673, 0.1733] | 0.4132 |
| ext__eikonal_2d | 0.0301 [0.0287, 0.0310] | 0.0192 [0.0184, 0.0200] | 0.6376 |
| ext__helmholtz_2d | 0.8588 [0.8418, 0.8696] | 4.4294 [3.1344, 5.7503] | 5.1576 |
| ext__pressure_poisson_poiseuille | 0.0032 [0.0025, 0.0045] | 0.0027 [0.0023, 0.0032] | 0.8425 |
| ext__rayleigh_benard_2d | 0.0008 [0.0007, 0.0009] | 0.0004 [0.0003, 0.0005] | 0.5113 |
| ext__wave_2d | 0.1370 [0.1338, 0.1400] | 0.0552 [0.0534, 0.0570] | 0.4029 |
| fluid | 0.0660 [0.0626, 0.0684] | 0.0231 [0.0229, 0.0232] | 0.3495 |
| heat_generated | 0.0029 [0.0025, 0.0037] | 0.0012 [0.0011, 0.0014] | 0.4155 |
| heat_local | 0.0010 [0.0009, 0.0011] | 0.0007 [0.0006, 0.0007] | 0.7002 |
| ifc_heat | 0.1166 [0.1159, 0.1175] | 0.0272 [0.0231, 0.0318] | 0.2338 |
| ifc_poisson | 0.1137 [0.0961, 0.1225] | 0.0420 [0.0412, 0.0436] | 0.3696 |
| lid_driven_cavity_generated | 0.7073 [0.6657, 0.7562] | 0.3243 [0.2848, 0.3764] | 0.4585 |
| poisson_generated | 0.0175 [0.0171, 0.0178] | 0.0022 [0.0021, 0.0023] | 0.1232 |
| poisson_local | 0.0173 [0.0164, 0.0180] | 0.0161 [0.0150, 0.0172] | 0.9352 |
| sharp__allen_cahn_2d | 0.1769 [0.1677, 0.1841] | 0.4656 [0.4137, 0.5420] | 2.6316 |
| sharp__burgers_1d | 0.0029 [0.0027, 0.0030] | 0.0014 [0.0013, 0.0016] | 0.4749 |
| sharp__burgers_2d | 0.0230 [0.0230, 0.0231] | 0.0092 [0.0086, 0.0101] | 0.4015 |
| sharp__cahn_hilliard | 0.3600 [0.3518, 0.3675] | 0.4857 [0.4798, 0.4908] | 1.3491 |
| sharp__euler | 0.0616 [0.0608, 0.0628] | 0.0569 [0.0563, 0.0576] | 0.9241 |
| sharp__fisher_kpp_2d | 0.0048 [0.0045, 0.0049] | 0.0306 [0.0297, 0.0312] | 6.4190 |
| sharp__helmholtz_2d | 0.6110 [0.5665, 0.6573] | 0.0993 [0.0867, 0.1160] | 0.1625 |
| sharp__phase_field_crystal_2d | 0.7719 [0.7668, 0.7813] | 0.9394 [0.9304, 0.9504] | 1.2171 |
| sharp__porous_medium_1d | 0.0025 [0.0024, 0.0027] | 0.0015 [0.0014, 0.0017] | 0.6087 |
| sharp__porous_medium_2d | 0.0044 [0.0042, 0.0046] | 0.0031 [0.0027, 0.0035] | 0.6931 |
| sharp__shallow_water_1d | 0.0147 [0.0135, 0.0158] | 0.0039 [0.0036, 0.0042] | 0.2646 |
| sharp__shallow_water_2d | 0.0145 [0.0131, 0.0162] | 0.0065 [0.0056, 0.0070] | 0.4457 |
| sharp__sod_1d | 0.0024 [0.0021, 0.0029] | 0.0010 [0.0009, 0.0011] | 0.4198 |

## Coverage gaps and exclusions

| dataset | family | seeds present / reason |
| --- | --- | --- |
| era5 | r3s2_route_b30 | 0/3 seeds |
| era5 | r3s2_route_b30 | LEDGERED: unsupported-by-frozen-family (spec D11, PREDECLARED): R3S2ContractError 'the 256 cap fired on era5 ((721, 1440) -> (128, 256)); this family requires working grid == native HF grid' — 3/3 attempts, jobs 552488+558642, deterministic |

Provenance: manifest `eac7b48eea76b77e`, registry `b30-0001`, inputs `score_jsons_only_arm_A1`.
