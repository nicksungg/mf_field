# ERA5 baseline queue

Submitted September 15, 2026 to ORCD. Maintenance is currently scheduled to end September 15 at 9 p.m. Eastern. Slurm will start eligible work when resources become available. The baseline jobs are queued, not training yet.

| Job | Work | Dependency |
| --- | --- | --- |
| 22776597 | CPU validation and four isolated smoke fits | ORCD availability |
| 22776598 | Full grid H100 validation of seven GPU recipes | CPU validation succeeds |
| 22776599 | Four CPU baseline fits | CPU validation succeeds |
| 22776600 | Seven GPU baseline fits, at most four concurrently | GPU validation succeeds |
| 22776601 | Verify and collect twelve baseline entries | All eleven fits succeed |

B9 and B10 share identical model and training code. B10 is reported as a B9 alias, with zero additional training cost. There is no duplicate fit for it.

All 34 regression tests passed on ORCD before submission. The four CPU smoke fits also passed locally on the real ERA5 input data. The queued H100 validation must pass before any GPU production job starts. Input hashes and exclusions are verified at every fidelity. Nodes 2900 and 4200 remain excluded.

Existing M8, M9 and ensemble work stays on SuperCloud. The cross cluster queue audit found no replicas. No other user jobs were cancelled or changed.

Details: ORCD_LAUNCH.json, INPUT_AUDIT.json and monitor/QUEUED_AUDIT.json. Results will be in results/era5_baselines.csv and results/era5_baselines__summary.json.
