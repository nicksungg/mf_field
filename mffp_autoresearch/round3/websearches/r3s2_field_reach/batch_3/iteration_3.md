# Iteration 3 — the named practice ("ceiling analysis") and the canonical two-stage GT-vs-predicted design

## Search rationale

Iteration 1 found the oracle-vs-predicted ladder under the name "oracle ablation" in compound-AI evaluation. Two follow-ups are decisive for the verdict: (i) whether the *upper-bound-by-perfect-component* reading — "how much of the stack's error would vanish if this stage were perfect" — has a textbook name, because that is precisely what the card calls the **emulator ceiling**; (ii) whether the *crossed* design (fit the downstream stage on GT vs on predicted intermediates, evaluate on GT vs predicted) is already canonical somewhere. Two-stage TTS is the obvious place for (ii): the acoustic model → vocoder stack has exactly our topology (upstream generates the intermediate representation; downstream is a separately trained, often frozen, decoder).

## Search terms used

1. `vocoder fine-tuned on predicted mel-spectrograms instead of ground truth mismatch two-stage TTS ground-truth-aligned`
2. `"ceiling analysis" machine learning pipeline replace component with ground truth upper bound which module to improve`
3. (third slot spent on fetches; recorded ENOUGH on field context at the end of this iteration — see Interpretation)

## Findings

### Term 1 — two-stage TTS: the crossed GT/predicted design is canonical

Returned: <https://arxiv.org/pdf/1712.05884> (Tacotron 2), <https://arxiv.org/pdf/2308.02867> (systematic exploration of joint training for SVS), <https://arxiv.org/pdf/2207.04646> (DelightfulTTS 2), <https://arxiv.org/pdf/2203.01080>, <https://arxiv.org/html/2306.11327> (eCat). Engine summary (snippet-level): *"vocoders are trained with ground-truth mel-spectrograms while mel-spectrograms predicted by acoustic models are used in inference, causing training-inference mismatch and inferior audio quality"*, and a *"counterintuitive"* SVS result where the vocoder trained on **generated** mel-spectrograms beat the one trained on ground-truth mels.

**Fetched — Shen et al., "Natural TTS Synthesis by Conditioning WaveNet on Mel Spectrogram Predictions" (Tacotron 2), arXiv:1712.05884** (PDF, 29,984 chars). §3.3.1 is titled *"Predicted Features versus Ground Truth"* and runs the **full 2×2 crossed matrix** of {train on predicted, train on GT} × {synthesise from predicted, synthesise from GT}, MOS:

| Training \ Synthesis | Predicted | Ground truth |
|---|---|---|
| Predicted | 4.526 ± 0.066 | 4.449 ± 0.060 |
| Ground truth | 4.362 ± 0.066 | 4.522 ± 0.055 |

Verbatim: *"As expected, the best performance is obtained when the features used for training match those used for inference. However, when trained on ground truth features and made to synthesize from predicted features, the result is worse than the opposite. This is due to the tendency of the predicted spectrograms to be **oversmoothed and less detailed** than the ground truth … When trained on ground truth spectrograms, the network does not learn to generate high quality speech waveforms from oversmoothed features."* Their default recipe is already the fix: *"We then train our modified WaveNet on the **ground truth-aligned predictions** of the feature prediction network."*

**Fetched — Wu, Yu, Shi, Qian & Jin, "A Systematic Exploration of Joint-training for Singing Voice Synthesis", arXiv:2308.02867** (PDF, 26,091 chars): *"since the acoustic model and the vocoder are not jointly optimized, **a gap can exist between the two models, leading to suboptimal performance**"*; they parameterise the interpolation between a frozen two-stage pipeline and full joint training (their `K`: *"If K is 1, it becomes a joint-training system that directly passes the predicted acoustic feature to the vocoder"*; their `r = 0` case *"is equivalent to a finetuned system where the SVS system is jointly finetuned with a pretrained acoustic model and a pretrained vocoder"*). Note this is the same frozen / fine-tuned / end-to-end arm ladder round 2 already ran (round-2 program §12.2).

### Term 2 — "ceiling analysis" is a named textbook method

Returned: <https://ieeexplore.ieee.org/document/6521941/> ("Ceiling analysis of pedestrian recognition pipeline for an autonomous car application", IEEE conference), <https://timewithai.wordpress.com/2019/07/09/ceiling-analysis-in-machine-learning/>, <https://github.com/juincc0/tilap/issues/105>, <https://link.springer.com/chapter/10.1007/978-3-031-72946-1_15>. The IEEE page **could not be fetched** (`urllib` returned a zero-length body — publisher block); it is recorded **snippet-only** and carries no verdict beyond the existence of the title.

Engine summary (snippet-level, consistent across three independent sources): *"Ceiling analysis is a way to determine what to improve next by making the prediction of components 100% accurate and seeing how much it will improve the overall accuracy"*; *"replacing each component with perfect predictions to see which component yields the most improvement"*; canonical example is the photo-OCR pipeline (text detection 17% vs character segmentation 1%). This is the standard Ng-lecture method; the IEEE title shows it is also used as a published research instrument.

## Interpretation

**ENOUGH on field context** — three independent literatures (compound-AI oracle ablation, textbook ceiling analysis, two-stage TTS GT-vs-predicted) all run the card's instrument, and Tacotron 2 §3.3.1 runs the *crossed* version of components (a)+(b) together with the same qualitative explanation we measured (the upstream's outputs are systematically oversmoothed relative to the real intermediate, so a downstream stage fitted on real intermediates is mis-specified at deployment). Iterations 4–5 go entirely to §3.3 refutation: can this be found *inside* the multi-fidelity surrogate literature, i.e. with a physical LF field as the intermediate?
