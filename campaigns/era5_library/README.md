# ERA5 with all nine ensemble experts

This separate extension reuses the seven existing ERA5 expert prediction files and the fine only FNO control. M8 is the slice attention corrector inspired by Transolver. M9 is the ConvNeXt corrector. The running PDE campaign is unchanged.

The split remains 55 fine base training examples, ten calibration examples, and seven evaluation examples. All reserved input identities were purged from every LF and HF base training table in the original campaign.

Coarse level eight supplies 394 observed training fields. Its native 192 by 384 grid and the native fine grid are resized with the existing bilinear convention to the 128 by 256 working grid used by the seven ERA5 experts. Each coarse predictor learns from LF targets only and predicts at HF input parameters, including those without observed LF counterparts. Five folds group HF input identities. Every LF occurrence of a held HF input is removed from that fold's training pool. Four members per fold use plain and heteroscedastic FNOs with two fixed seeds. Each HF training prediction averages four OOF members. Each reserved query averages the four members from fold zero, maintaining ensemble size.

The correctors receive parameters and predicted coarse fields. Observed paired LF targets are unnecessary. The original backbones, six damped refinement steps, 30000 requested coarse updates, and 6000 corrector updates are retained. Correctors use 49 training and six validation examples from the 55 fine training cases. Parameter normalization, field scale, and gain use the 49 training examples only. Fixed array coordinates replace registration selected using observed LF/HF pairs.

The collector requires all nine experts plus the separate fine only control. At calibration budgets five and ten, it refits selected single, inverse error, full convex, uniform, and automatic selection rules with nine weight entries. All pairs remains an individual comparator. Evaluation answers are opened only after the partition's weights are saved. An available expert may receive zero learned weight.

Tests cover input identity exclusions, duplicate grouping, training replay, four member accounting, training subset normalization, and unchanged weights after evaluation answers change. GPU tests use isolated smoke outputs and are never counted as scientific results.

Remote host: archive-host, user review-author.
Remote folder: /archive/user/mf_field/experiments/era5_nine_20260914.
Python environment: /archive/user/mf_field/environments/automl_20260914.

EXPERIMENT.json defines the protocol. SOURCE.json freezes its implementation. LAUNCH.json records production submissions. Final results will appear in results/era5__summary.json, results/era5.csv, and results/NINE_EXPERT_AUDIT.json.
