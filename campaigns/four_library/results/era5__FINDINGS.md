# Repaired ensemble: era5

7 ensemble experts; 55 fine base-training cases. Separate fine-only FNO and training-mean controls.

| Method | Mean relative L2 error |
|---|---:|
| b10__allpairs | 17.6992% |
| b10__auto | 6.76534% |
| b10__full | 6.76534% |
| b10__inverse_mse | 6.58512% |
| b10__selected_single | 6.73688% |
| b10__uniform | 7.43475% |
| b5__allpairs | 17.6992% |
| b5__auto | 6.77231% |
| b5__full | 6.77231% |
| b5__inverse_mse | 6.57847% |
| b5__selected_single | 6.73688% |
| b5__uniform | 7.43475% |
| expert:convnext_unet_film | 20.3962% |
| expert:fno_fire_distcond | 12.1677% |
| expert:mf_deeponet | 9.53642% |
| expert:mf_fno_allpairs | 17.6992% |
| expert:mf_fno_transfer_film | 14.2255% |
| expert:st_hf_pod_gp | 6.73688% |
| expert:wno_transfer_film | 9.75314% |
| hf_only_control | 23.3336% |
| training_mean_control | 6.73688% |

`auto` chooses single-expert selection, inverse-MSE weighting, or a full convex mixture using leave-one-out calibration error only. Every method is reported, including losses. Calibration labels count beyond base training labels.
The final targets were opened only after all budget weights were saved for that partition. Training workers received zero-valued placeholder test fields. Repeated partitions reuse the same base models.
ERA5 uses 10 reserved calibration inputs and 7 existing evaluation inputs; these are not fresh years. Its two unpaired-incompatible correctors are explicitly unavailable. Physical units of secondary RMSE are the units stored in the source archive.
