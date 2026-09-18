# Conclusion and reproducibility wording

The previous discussion sentence conflated the scope of the manuscript ZIP with the availability of the research code. Inspection confirmed that surrogate implementations and training drivers exist in the workspace. Examples include:

* `../mf_field_surrogate_bench/models/paper/`: model definitions and training/evaluation entry points for the paper model families.
* `../mf_field_surrogate_bench/models/st_bench/`: classical and neural reference implementations and execution scripts.
* `../mf_field_surrogate_bench/generators/`: simulation generation code. The benchmark README also documents full and metadata-only dataset entries and data retrieval.
* `../mf_field_session_20260905/uqcorr/corr_ens.py` and `corr_backbones.py`: corrector training and backbone implementations.
* `../mf_field_complete25_20260915/expert_worker.py` and `baseline_worker.py`: experiment training and evaluation drivers, with vendored runtime code.

Following the author's clarification, the release limitation was removed from the discussion. The appendix describes the retained research artifacts across data preparation, surrogate training, ensemble fitting, and evaluation. A live read-only inventory confirmed NPZ data archives for all 18 reporting datasets on ORCD, recorded in `REPRODUCIBILITY_AVAILABILITY_20260916.json`. The ERA5 campaign on SuperCloud also contains prepared training data, training metadata, vendored surrogate implementations, corrector code, and shared adapters. This establishes availability at the inspected locations, not a new clean retraining or completeness audit of every dependency. The appendix distinguishes these archives from the manuscript ZIP without implying that training code or data is unavailable. No public release or newly consolidated full training package is claimed. The verified ZIP rebuild covers the manuscript, ensemble fitting, numerical comparisons, and reporting.

The conclusion now follows the empirical story: different problems favor different surrogate models, the library contains strong alternatives to the additional baselines, and reserved fine solutions provide a practical means of selecting or combining those models. It retains the main scope and fitting allowance, the improvement on 13 of 18 datasets, the strength of inverse error weighting, and the lack of consistent benefit from additional fitting flexibility. It mentions the fresh input and climate checks without repeating their case-specific errors or claiming that the ensemble beats every baseline.

No abstract, experimental data, figures, tables, model results, or training code was changed. The original manuscript remains untouched.
