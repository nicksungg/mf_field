# st_bench — surrogate track: theta -> fine field, coarse data for training only

Every arm predicts the fine test field from theta alone; the coarse solves are used only to train.  Metric: per-sample
relative L2 on the fine grid (bench_ct conventions: native fine grid for paired mf_field_final datasets, 256-capped
working grid for the three leaderboard-format unpaired sets).  Results: raw/<arm>__<dataset>__est__s<seed>.json.

| arm | what | where |
|---|---|---|
| st_mean, st_knn, st_hf_pod_gp | fine-only floors (mean field, inverse-distance kNN in theta, POD+GP emulator) | st_classical.py, CPU |
| st_lf_affine_pod | rho * LF_emul(theta) + b, LF_emul = POD-GP on the coarse pool | st_classical.py, CPU |
| st_koh_pod | Kennedy-O'Hagan AR(1) co-kriging on POD coefficients, coarse process emulated at test | st_classical.py, CPU |
| st_nargp_pod | NARGP (Perdikaris 2017) on POD coefficients, MC through the level-1 posterior | st_classical.py, CPU |
| st_mfdnn | Meng-Karniadakis composite MF-DNN (pointwise, linear + nonlinear HF nets) | st_neural.py, GPU |
| st_mfdeeponet | Howard et al. 2023 composite MF-DeepONet (linear + nonlinear DeepONets on [theta, G_L at sensors]) | st_neural.py, GPU |
| st_dmfal | DMFAL deep multi-fidelity model (Li-Wang-Kirby-Zhe 2022), passive, MAP | st_neural.py, GPU |
| st_film_hf_only | FiLM-FNO fine-only, 2500 epochs | st_film.py --mode hf_only, GPU |
| st_film_lf_only, st_film_affine | FiLM-FNO coarse-only (top coarse level) evaluated on the fine target; + two-scalar affine correction | st_film.py --mode lf_only, GPU |
| st_film_pooled | FiLM-FNO fidelity-blind pooling of all levels, same optimizer steps as hf_only | st_film.py --mode pooled, GPU |
| st_film_transfer | the family's pretrain(coarsest)->finetune schedule (anchor; leaderboard results reused by collect_st.py) | st_film.py --mode transfer, GPU |

Run: `python make_st_tasks.py` -> cpu_tasks.txt / gpu_tasks.txt; `bash submit_st.sh all` (arrays on standard_cpu / standard_gpu / preemptible_gpu);
`python collect_st.py` -> results/ST_TABLE.md.  Smoke: `OUT_DIR=$ST/raw_smoke EXTRA_ARGS="--steps 300 --eval-every 100" FILM_ARGS="--epochs 3 --tag esmoke" sbatch ...`.
Seeds 42, 123.  Classical arms use all training rows; neural arms hold out 10% of the fine rows for checkpoint selection.
