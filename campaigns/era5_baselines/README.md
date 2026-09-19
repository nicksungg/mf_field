# ERA5 baseline completion on CLUSTER

This campaign fills B1 through B12 for the current 21 dataset paper. It reuses the exact ERA5 input roles already used for the seven completed experts and the nine expert extension. It does not start the deferred 25 dataset campaign.

There are 55 fine base training rows, ten separate calibration rows, and seven separate evaluation rows. All seventeen reserved input identities are absent from all nine training fidelities. Every prediction uses only input parameters. Final errors are evaluated on the same 128 by 256 grid. The original input tables, PLAN.json, ROLES.json, and sealed answers are preserved by SHA256.

B1, B2, B11 and B12 are CPU fits. B3 through B9 are GPU fits. B9 and B10 have identical architecture and executable training recipes after normalizing import locations and the output label. B10 is therefore explicitly recorded as a B9 alias with zero additional training cost. Twelve displayed entries require eleven independent fits.

The statistical baselines retain the released POD and GP settings. The three neural statistical baselines retain 100000 optimizer updates per stage and use 49 training plus six internal validation rows. Paper adapters retain 2500 epochs and their original internal validation procedures. Base data identity is matched, but architecture specific validation and training budgets still differ and should remain disclosed in the paper.

CPU validation tests and isolated smoke runs precede CPU training. GPU smoke runs on the full working grid precede GPU training. Production jobs require successful preflight dependencies and matching source and input hashes. Smoke results are stored separately and never enter the paper table.

The CLUSTER scheduler monitors availability and starts eligible jobs after maintenance and resource limits permit. GPU jobs request nonpreemptible H100 resources on research_gpu, at most four concurrently, with a 96 hour wall limit. This protects the three released neural loops that lack optimizer resume. Nodes 2900 and 4200 remain excluded, as do the inherited 2901 and 4002 exclusions. No job is duplicated on ComputeCluster. The existing ERA5 M8/M9/ensemble chain remains assigned exclusively to ComputeCluster.

CLUSTER root: /archive/mf_field/experiments/era5_baselines_20260915

The isolated .venv inherits the existing CLUSTER scientific packages and adds pytest for validation. Scripts do not modify the shared training environment. SOURCE.json freezes code and protocol, INPUT_MANIFEST.json freezes data, and CLUSTER_LAUNCH.json records submissions. Rerunning the launcher is idempotent. Task locks prevent concurrent copies of a fit.

Final outputs: results/era5_baselines.csv, results/era5_baselines_per_case.npz, results/era5_baselines__summary.json, results/BASELINES_AUDIT.json. Collection requires all twelve entries and independently checks the existing training mean control. A failed preflight or missing result cannot be silently presented as complete.
