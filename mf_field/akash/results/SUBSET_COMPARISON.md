# Subset comparison — ELO leaderboard

Models: 10 | Datasets: 12 (7 smooth, 5 sharp) | epochs=2500 seed=42

Per-dataset metric = per-sample rel-L2 mean (lower better). geomean = geometric mean across that regime's datasets.

| Rank | Model | ELO | ±std | W-L-T | n_ds | geomean_all | smooth | sharp |
|---|---|---|---|---|---|---|---|---|
| 1 | mf_fno_allpairs | 1624 | 40 | 61-29-0 | 10 | 0.0252 | 0.0090 | 0.0712 |
| 2 | mf_fno_ptr | 1589 | 38 | 64-36-6 | 12 | 0.0266 | 0.0128 | 0.0743 |
| 3 | mf_fno_foundation | 1563 | 40 | 63-43-0 | 12 | 0.0300 | 0.0158 | 0.0735 |
| 4 | mf_fno_transfer_film *(anchor)* | 1552 | 41 | 58-42-6 | 12 | 0.0267 | 0.0129 | 0.0742 |
| 5 | mf_fno_hyperfilm | 1549 | 41 | 60-46-0 | 12 | 0.0255 | 0.0116 | 0.0771 |
| 6 | mf_fno_richardson | 1536 | 41 | 58-48-0 | 12 | 0.0333 | 0.0191 | 0.0726 |
| 7 | mf_fno_spectral | 1465 | 37 | 47-59-0 | 12 | 0.0354 | 0.0184 | 0.0884 |
| 8 | mf_fno_transfer_bar *(anchor)* | 1455 | 40 | 46-60-0 | 12 | 0.0344 | 0.0199 | 0.0741 |
| 9 | mf_fno_lora | 1421 | 40 | 41-65-0 | 12 | 0.0577 | 0.0343 | 0.1197 |
| 10 | mf_fno_diffprior | 1246 | 34 | 18-88-0 | 12 | 0.9823 | 1.3358 | 0.6387 |

**Missing cells** (job failed/timed out — excluded from that model's geomean):
- mf_fno_allpairs × era5
- mf_fno_allpairs × pm_test
