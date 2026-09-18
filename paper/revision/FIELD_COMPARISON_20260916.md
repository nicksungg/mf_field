# Prediction and error figure

Removed the standalone main text subsection “Data quality and new input checks.” Dataset defects, input separation limits, and the new versus retrospective evaluation distinction remain in Appendix C.1, with a concise main text pointer. The automatic rule aggregate table is moved to Appendix E so the manuscript keeps nine main pages.

New Figure 3 places ground truth, M1 to M9, inverse weighting, fitted weighting, and automatic rule selection in 13 columns. Predictions are above their absolute error maps. Each row uses a common color scale, with logarithmic error colors linear near zero. Numerical relative L2 errors are reported below each column. No field is smoothed or rescaled independently.

The dataset is Heat I, chosen to illustrate a successful ensemble. The case is row zero, the first evaluation input of the first partition, not the maximum improvement case. Its five fitting rows are disjoint from evaluation. All weights are the previously locked values. Automatic selection picks inverse weighting, so those two panels correctly coincide.

The best individual model is M4 with 0.0053226662 percent error. Fitted weighting gives 0.0029612621 percent, a 44.3651 percent relative reduction. Inverse weighting gives 0.0029307704 percent. Fitted weighting beats every individual on all 20 evaluation inputs in this partition. The aggregate paper results remain unchanged and retain failures on other datasets.

The saved prediction arrays were extracted from ORCD using the source hashes and row mappings of the nine model experiment. Their error matrix reproduces the archived matrix. The source archive includes the extracted arrays, their manifest, the plotting script, and replay checks. Appendix H.3 explains selection and display conventions. The standalone figure is available as PDF and PNG.

The original manuscript is untouched. A backup of the latest revision before this edit is in `../automf_revision_backups_20260916/before_field_comparison.zip`.
