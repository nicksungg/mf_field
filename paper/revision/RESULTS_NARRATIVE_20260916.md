# Results narrative revision

The previous results section interleaved its main argument with per dataset errors, alternative aggregate ratios, retrospective selection counts, subset sizes, and implementation caveats. This made the reader reconstruct the conclusion from a sequence of numbers. The revision uses four connected subsections, each organized around one empirical question.

1. **Different models lead on different datasets.** Establish that the library contains useful alternatives to the additional baselines and that its strongest member varies by problem. Keep the retrospective meaning of the best model comparison explicit. The tables retain the full errors and Elo ranking.
2. **Combining predictions often improves accuracy.** State the practical comparison with the Selected model, the common five example fitting allowance, and the headline improvements across the full reporting scope. Retain the distinction between this comparison and choosing a best model after evaluation, without repeating every ratio. Individual success and failure examples remain in Table 1.
3. **Simple weighting captures most of the benefit.** Bring the inverse mixture, fitted mixture, and automatic rule selection into a single discussion of whether additional fitting flexibility helps. Keep the findings about uniform weighting and automatic selection, with detailed numerical evidence in the existing appendices.
4. **New inputs support the simpler weighting rule.** Lead with the fresh heat check and state its limited scope. Summarize dataset sensitivity and the fitting objective control without listing every subset size or diagnostic score. The control remains explicitly retrospective and separate from the original selector.

Removed the training resource and duplicate Darcy archive sentences from Section 5.1. Training resources and adaptations remain documented in the comparison captions, implementation appendix, and discussion. The duplicate M8/M9 archive finding remains in the dedicated appendix subsection. Removed the main text phrase about the 15 datasets excluding recovered B8 entries. Its precise definition and results remain in the sensitivity appendix.

The user specifically requested no discussion of the error patterns in Figure 3. The results prose therefore contains only a brief pointer to that illustrative field example. The figure and its descriptive caption are unchanged. No spatial interpretation paragraph was added.

The abstract, numerical results, models, trained weights, dataset scope, figures, tables, and original manuscript were not changed. The revised main text remains within the nine page limit. Numerical and structural checks pass, and rendered results pages were inspected.
