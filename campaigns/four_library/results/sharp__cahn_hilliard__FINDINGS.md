# Repaired ensemble: sharp__cahn_hilliard

9 ensemble experts; 400 fine base-training cases. Separate fine-only FNO and training-mean controls.

| Method | Mean relative L2 error |
|---|---:|
| b10__allpairs | 48.3102% |
| b10__auto | 47.1314% |
| b10__full | 51.4823% |
| b10__inverse_mse | 47.2366% |
| b10__selected_single | 50.1523% |
| b10__uniform | 49.3259% |
| b20__allpairs | 48.3102% |
| b20__auto | 46.9243% |
| b20__full | 49.6485% |
| b20__inverse_mse | 47.1192% |
| b20__selected_single | 50.1523% |
| b20__uniform | 49.3259% |
| b5__allpairs | 48.3102% |
| b5__auto | 49.9365% |
| b5__full | 49.259% |
| b5__inverse_mse | 47.2139% |
| b5__selected_single | 52.2253% |
| b5__uniform | 49.3259% |
| expert:convnext_unet_film | 51.9257% |
| expert:fno_fire_distcond | 50.754% |
| expert:mf_deeponet | 99.8482% |
| expert:mf_fno_allpairs | 48.3102% |
| expert:mf_fno_transfer_film | 46.9074% |
| expert:st_hf_pod_gp | 64.8111% |
| expert:uqcorr_convnext_pred | 47.8453% |
| expert:uqcorr_transolver_pred | 55.8893% |
| expert:wno_transfer_film | 60.8258% |
| hf_only_control | 48.4054% |
| training_mean_control | 100.408% |

`auto` chooses single-expert selection, inverse-MSE weighting, or a full convex mixture using leave-one-out calibration error only. Every method is reported, including losses. Calibration labels count beyond base training labels.
The final targets were opened only after all budget weights were saved for that partition. Training workers received zero-valued placeholder test fields. Repeated partitions reuse the same base models.
ERA5 uses 10 reserved calibration inputs and 7 existing evaluation inputs; these are not fresh years. Its two unpaired-incompatible correctors are explicitly unavailable. Physical units of secondary RMSE are the units stored in the source archive.
