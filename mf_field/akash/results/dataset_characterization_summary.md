# Dataset characterization (42 datasets)

- **MF-useless** (LF<->HF corr < 0.3; multi-fidelity cannot help): ['gray_scott_2d', 'kuramoto_sivashinsky_1d']
- **Operator-hard** (param->field corr < 0.15; chaotic map, nothing predicts it): ['burgers_generated', 'burgers_param_generated', 'ifc_heat', 'kuramoto_sivashinsky_1d', 'allen_cahn_1d', 'fisher_kpp_1d', 'kuramoto_sivashinsky_1d', 'kuramoto_sivashinsky_2d', 'nls_1d', 'sine_gordon_1d']

Sorted by HF<->LF correlation (low = MF can't help):

| dataset | coll | ndim | hf_corr | rel_resid | hi_freq | spec_slope | tv_rel | pca95 | pf_corr | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| kuramoto_sivashinsky_1d | ext | 2D | -0.0572 | 1.4129 | 0.1325 | -2.421 | 1.3392 | 63 | 0.0789 | MFU,OPH |
| gray_scott_2d | ext | 2D | 0.0076 | 191110738349.2284 | 0.0001 | -7.204 | 0.1961 | 13 | 0.3546 | MFU |
| cahn_hilliard_2d | ext | 2D | 0.3334 | 0.8589 | 0.9203 | 1.353 | 2.988 | 25 | 0.2895 |  |
| shallow_water_1d | sharp | 1D | 0.7225 | 0.0351 | 0.0 | -5.046 | 0.0018 | 1 | 0.3756 |  |
| fisher_kpp_2d | sharp | 2D | 0.7583 | 0.1951 | 0.0016 | -4.469 | 0.2703 | 88 | 0.1816 |  |
| lid_driven_cavity_generated | core | 2D | 0.7995 | 0.5969 | 0.088 | -2.16 | 0.1893 | 1 | 0.9472 |  |
| ifc_poisson | core | 2D | 0.827 | 80.2893 | 0.0008 | -5.565 | 0.0822 | 2 | 0.6485 |  |
| wave_2d | ext | 2D | 0.8464 | 0.518 | 0.0001 | -7.134 | 0.3078 | 42 | 0.5059 |  |
| pressure_poisson_poiseuille | ext | 2D | 0.9266 | 0.0151 | 0.0216 | -3.664 | 0.003 | 7 | 0.2585 |  |
| burgers_param_generated | core | 2D | 0.9267 | 0.352 | 0.0234 | -4.002 | 0.4876 | 8 | 0.0989 | OPH |
| phase_field_crystal_2d | sharp | 2D | 0.9301 | 0.1471 | 0.0 | -29.633 | 0.1095 | 20 | 0.1757 |  |
| allen_cahn_generated | core | 2D | 0.9361 | 0.3001 | 0.0434 | -4.107 | 0.1424 | 5 | 0.7351 |  |
| burgers_1d | sharp | 1D | 0.9387 | 0.307 | 0.0174 | -1.915 | 0.1117 | 2 | 0.7499 |  |
| ifc_heat | core | 2D | 0.9395 | 0.2103 | 0.0033 | -4.727 | 0.0533 | 2 | 0.1273 | OPH |
| shallow_water_2d | sharp | 2D | 0.9416 | 0.0509 | 0.0 | -5.611 | 0.0077 | 1 | 0.2942 |  |
| burgers_generated | core | 2D | 0.9468 | 0.3228 | 0.0033 | -5.334 | 0.4757 | 5 | 0.0588 | OPH |
| fluid | core | 2D | 0.9721 | 0.2394 | 0.0009 | -5.704 | 0.2415 | 8 | 0.8581 |  |
| euler | sharp | 2D | 0.9741 | 0.0681 | 0.0033 | -4.247 | 0.0169 | 3 | 0.4921 |  |
| poisson_local | core | 2D | 0.9751 | 72.4513 | 0.0003 | -5.5 | 0.0415 | 3 | 0.4626 |  |
| poisson_generated | core | 2D | 0.9767 | 17.3148 | 0.002 | -4.924 | 0.0545 | 4 | 0.653 |  |
| burgers_2d | sharp | 2D | 0.9772 | 0.2071 | 0.0048 | -3.441 | 0.1456 | 3 | 0.8719 |  |
| helmholtz_2d | ext | 2D | 0.9831 | 0.2046 | 0.0 | -8.333 | 0.1173 | 4 | 0.2483 |  |
| allen_cahn_2d | sharp | 2D | 0.984 | 0.0414 | 0.0 | -18.636 | 0.0457 | 1 | 0.1593 |  |
| porous_medium_1d | sharp | 1D | 0.9843 | 0.1481 | 0.0003 | -3.375 | 0.0638 | 3 | 0.4632 |  |
| heat_local | core | 2D | 0.989 | 0.085 | 0.0016 | -5.011 | 0.0266 | 3 | 0.2263 |  |
| heat_generated | core | 2D | 0.9894 | 0.0788 | 0.0029 | -4.658 | 0.0532 | 2 | 0.2136 |  |
| eikonal_2d | ext | 2D | 0.9901 | 0.0721 | 0.0 | -5.441 | 0.0546 | 6 | 0.5096 |  |
| cahn_hilliard | sharp | 2D | 0.9901 | 0.1379 | 0.0 | -10.532 | 0.1275 | 7 | 0.2419 |  |
| helmholtz_2d | sharp | 2D | 0.991 | 3.0118 | 0.0 | -8.18 | 0.2124 | 4 | 0.1931 |  |
| sod_1d | sharp | 1D | 0.9938 | 0.0573 | 0.0088 | -2.018 | 0.0125 | 1 | 0.7937 |  |
| porous_medium_2d | sharp | 2D | 0.9943 | 0.1011 | 0.0005 | -3.781 | 0.1665 | 3 | 0.7422 |  |
| era5 | core | 2D | 0.9945 | 0.1148 | 0.0023 | -3.389 | 0.1073 | 38 | 0.6559 |  |
| pm_test | core | 2D | 0.9945 | 0.1148 | 0.0023 | -3.389 | 0.1073 | 38 | 0.6914 |  |
| kuramoto_sivashinsky_2d | sharp | 2D | 0.9946 | 0.1033 | 0.0 | -28.158 | 0.1722 | 11 | 0.1041 | OPH |
| darcy_generated | core | 2D | 0.9952 | 0.0864 | 0.0 | -8.447 | 0.047 | 7 | 0.3028 |  |
| advection_diffusion_generated | core | 2D | 0.9959 | 0.078 | 0.0 | -11.29 | 0.1744 | 5 | 1.0 |  |
| fisher_kpp_1d | sharp | 1D | 0.9967 | 0.0378 | 0.4018 | -0.24 | 0.4152 | 40 | 0.1355 | OPH |
| rayleigh_benard_2d | ext | 2D | 0.9988 | 0.024 | 0.0164 | -8.043 | 0.0372 | 1 | 0.7219 |  |
| allen_cahn_1d | sharp | 1D | 0.9996 | 0.0102 | 0.0011 | -4.384 | 0.1019 | 9 | 0.0813 | OPH |
| kuramoto_sivashinsky_1d | sharp | 1D | 1.0 | 0.0028 | 0.0 | -14.819 | 0.2813 | 14 | -0.2117 | OPH |
| nls_1d | sharp | 1D | 1.0 | 0.0059 | 0.0 | -13.975 | 0.2438 | 25 | -0.0456 | OPH |
| sine_gordon_1d | sharp | 1D | 1.0 | 0.003 | 0.0 | -15.809 | 0.2419 | 14 | -0.016 | OPH |
