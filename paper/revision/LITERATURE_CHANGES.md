# Literature and implementation scope revisions

Only the new revision directory was edited. The original manuscript was read for comparison and was not changed.

## Verified additions

- `acar2009`: Acar and Rais Rohani, *Ensemble of metamodels with optimized weight factors*, Structural and Multidisciplinary Optimization 37, 279–294 (2009), DOI [10.1007/s00158-008-0230-y](https://link.springer.com/article/10.1007/s00158-008-0230-y). The publisher abstract confirms optimization of ensemble weights and evaluation using training error estimates or a few validation points. The manuscript now treats this as a direct precedent for fitted weights.
- `viana2009`: Viana, Haftka, and Steffen Jr., *Multiple surrogates: how cross-validation errors can help us to obtain the best predictor*, Structural and Multidisciplinary Optimization 39, 439–457 (2009), DOI [10.1007/s00158-008-0338-0](https://link.springer.com/article/10.1007/s00158-008-0338-0). The publisher abstract explicitly compares selection, weighting, and library subsets. The manuscript no longer presents those questions as new.
- `brunel2025`: Brunel, Balesdent, Brévault, Le Riche, and Sudret, *A survey on multi-fidelity surrogates for simulators with functional outputs: unified framework and benchmark*, Computer Methods in Applied Mechanics and Engineering 435, 117577 (2025), DOI [10.1016/j.cma.2024.117577](https://doi.org/10.1016/j.cma.2024.117577). The [author institutional record](https://sudret.ibk.ethz.ch/publications/preprints-archive/2024-006.html) and [author preprint](https://arxiv.org/abs/2408.17075) establish the implemented functional output benchmark and varying model strengths. Related work explicitly acknowledges that both functional output benchmarking and prediction from parameters have precedent.

The existing `ghiotto2025` key is preserved, but HyperNOs now cites its final journal record: volume 19, 709–743 (2026), first online 21 October 2025, DOI [10.1007/s40574-025-00516-0](https://link.springer.com/article/10.1007/s40574-025-00516-0). The review's 2025 publication remark refers to first online publication. The current publisher issue date is September 2026.

## Scientific positioning

Related work is 315 whitespace separated words, leaving the main page budget intact. It identifies the incremental contribution as the implemented field library and its calibration study, conditional on this library and data. It explicitly states that no complete EL MFS, AQBMF, or MAESTRO comparison has been performed. Existing ML ensemble, operator, engineering, and dataset citations remain. All 48 bibliography entries are cited and no citation key is undefined in the checked source.

Model adaptation and appendix text distinguish implemented references from faithful reproductions. B1, B5, and B8 omit central probabilistic components. B9 and B10 are retained archived result entries of the same inspected recipe with unresolved score provenance, not independent method families. Matching evaluation rows alone does not establish architectural superiority, fidelity specific gains, equal tuning budgets, or equal compute. The appendix illustrates the fine label allocation difference using the inspected Darcy recipes and explains why export timestamps cannot measure training cost.

The visual inventory now identifies native ERA5 illustration resolution versus working evaluation resolution. It describes stored target values rather than asserting known physical temperature units.

These are literature and scope corrections, not replacements for the missing complete workflow comparisons, matched controls, or physical metadata. No new experiment or baseline result was asserted.

## Files edited

- `references.bib`
- `sections/related_work.tex`
- `sections/model_adaptations.tex`
- `sections/visual_appendix.tex`
- This record

Static checks found no prose hyphens or semicolons in the three section files. Reference titles and author names retain correct source spelling. Full compilation and page inspection are handled by the coordinating agent.
