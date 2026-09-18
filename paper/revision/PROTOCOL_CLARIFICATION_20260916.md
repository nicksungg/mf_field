# Comparison coverage and training settings

Rewrote the main experimental coverage paragraph to state that all nine models and ensembles cover the 18 paper datasets. All reported methods use common evaluation cases within each dataset and calibration partition. The two baseline gaps are fidelity basis FNO on Heat II and Burgers. Historical run JSON files exist for both, but the current matching audit lacks source identity or saved target evidence establishing correspondence with the ensemble evaluation cases. Their historical aggregate scores were not substituted for the missing matched scores.

The paragraph now states that baselines retain their benchmark implementation settings, with documented adaptations. It identifies the 2,500 epoch schedule for transfer and distribution stages and refers readers to the appendix for the other schedules. The correctors use 6,000 optimizer steps, their coarse ensembles request 30,000 steps, retrieved DeepONet uses 125,000 iterations for its nominal 2,500 epoch argument, and POD GP does not have a neural epoch budget. Training and internal validation allocations differ across implementations.

No model was trained, no result or abstract changed, and no baseline coverage gap was hidden. The manuscript compiles and passes verification with nine main text pages. The original manuscript was not edited.
