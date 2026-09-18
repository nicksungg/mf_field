# Surrogate implementations

These are the adapted implementations used in the experiments. Citations identify sources of components or ideas, not claims of verbatim reproduction. Full references and derivations are in `paper/references.bib` and the manuscript appendix.

| ID | Manuscript name | Implementation identifier | Adaptation |
|---|---|---|---|
| M1 | FiLM FNO transfer | `mf_fno_transfer_film` | Coordinate input and parameter FiLM at every FNO block, with LF to HF transfer. Tests repeated conditioning and spectral transfer. Sources: li2021fno,perez2018. |
| M2 | All pairs FNO | `mf_fno_allpairs` | Fidelity labels and repeated target supervision. Poseidon is pair enumeration inspiration only. No source field input. Sources: li2021fno,herde2024. |
| M3 | ConvNeXt transfer | `convnext_unet_film` | ConvNeXt blocks in a U shaped field decoder, parameter FiLM, and LF to HF transfer. Tests local spatial processing. Sources: liu2022convnext. |
| M4 | Distribution FNO | `fno_fire_distcond` | FIRE distribution summaries become spatial channels from five LF FNOs. A trained residual FNO replaces foundation model inference. Sources: yu2026fire. |
| M5 | Wavelet transfer | `wno_transfer_film` | WNO motivates a custom single level db4 coefficient mixer with FiLM and transfer training. Sources: tripura2022wno. |
| M6 | Retrieved field DeepONet | `mf_deeponet` | Parameters and a nearest neighbour LF training field enter the branch. The residual needs no new coarse solve. Sources: lu2022mf. |
| M7 | POD GP | `st_hf_pod_gp` | HF field SVD and shared coefficient GP hyperparameters. Basis emulation inspiration, not the original Bayesian model. Sources: higdon2008. |
| M8 | Slice attention corrector | `uqcorr_transolver_pred` | Changed pooling and cell to slice attention, parameter FiLM, and six corrections of a predicted coarse field. Sources: wu2024transolver. |
| M9 | ConvNeXt corrector | `uqcorr_convnext_pred` | ConvNeXt blocks in a U shaped corrector with FiLM. Six updates refine a predicted coarse field rather than generating it directly. Sources: liu2022convnext. |
| B1 | Autoregressive POD GP | `st_koh_pod` | KOH inspired scalar field coupling plus a separate residual POD GP. Not joint probabilistic co kriging. Sources: kennedy2000. |
| B2 | Nonlinear POD GP | `st_nargp_pod` | NARGP inspired coefficient kernel with shared covariance hyperparameters and Monte Carlo LF uncertainty. Sources: perdikaris2017. |
| B3 | Composite MF MLP | `st_mfdnn` | Meng inspired pointwise LF network and staged linear plus nonlinear HF corrections. Sources: meng2020. |
| B4 | Composite MF DeepONet | `st_mfdeeponet` | Howard inspired LF sensor prediction and staged linear plus nonlinear DeepONets. Sources: howard2023. |
| B5 | Latent MF network | `st_dmfal` | DMFAL inspires two latent levels. Deterministic MSE replaces the probabilistic objective and acquisition. Sources: li2022dmfal. |
| B6 | Nonlinear decoder transfer | `nomad_mf` | NOMAD motivates a custom nonlinear coordinate decoder. Multifidelity behavior comes from transfer training. Sources: seidman2022. |
| B7 | MFRNP adapter | `mfrnp` | Upstream MFRNP model with data, normalization, resize, batching, context, and training adaptations. Sources: niu2024. |
| B8 | Fidelity basis FNO | `fno_coregionalization` | IFC inspires fidelity dependence. Spatial basis FNO omits the original neural ODE and GP. Sources: li2022ifc. |
| B9 | FNO transfer I | `mf_fno_transfer` | Parameters concatenated with coordinates and LF to HF transfer. Same inspected recipe as B10. Sources: lyu2023. |
| B10 | FNO transfer II | `mf_fno_transfer_bar` | Separately archived transfer run with the same inspected model and training code as B9. Sources: lyu2023. |
| B11 | Affine POD GP | `st_lf_affine_pod` | One affine slope and intercept across fields applied to an LF POD GP. Conceptual inspiration only. Sources: zhang2018. |
| B12 | Parameter kNN | `st_knn` | Training-field nearest-neighbor reference. Sources: . |
| B13 | Training mean | `st_mean` | Input-independent fine-training mean. Sources: . |

## Code locations

M1 to M6 and B6 to B10: `models/paper/<identifier>/`. M7, B1 to B5 and B11 to B13: `models/st_bench/`. M8 and M9: `models/uqcorr/`. Exact later campaign copies, including unpaired ERA5 adapters, are under `campaigns/`.

## Ensembles

Selected model puts all weight on the member with the lowest mean relative L2 error on the fitting examples. Inverse error mixture uses normalized inverse mean squared relative error. Fitted mixture solves a nonnegative, sum-to-one quadratic weight problem using cross-model error inner products. All three use one weight per model, shared across query inputs and spatial cells. No evaluation target is used to fit those weights.

## Archived implementation identities

B9 and B10 use identical inspected transfer code. The newer ERA5 and four-PDE campaigns deliberately reuse their predictions for those two table entries. M8 and M9 have identical archived Darcy predictions; this release preserves and documents that identity rather than inventing independent results. The nine-entry library should not be interpreted as nine independent error sources on every dataset. Historical and later campaign training settings differ.

The release includes code and saved predictions, not a complete bank of trained checkpoint states. Training scripts write new checkpoints. Exact historical score replay uses the archived predictions or sufficient error statistics, and does not require the original optimizer states.
