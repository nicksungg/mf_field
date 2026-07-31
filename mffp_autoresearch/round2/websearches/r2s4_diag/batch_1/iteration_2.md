# Iteration 2 — `r2s4_diag` batch 1

## Search rationale

Iteration 1 covered floors and seed variance. r2s4's other owned question is
**value-of-LF accounting** — matched with/without-LF-training arms at fixed
architecture and budget (program.md §12.4). Open question 3 from
`summary_so_far.md`. The relevant literatures are (a) multi-fidelity surrogate
modelling's own "how much does LF data buy you" question, (b) learning using
privileged information (LUPI) — the exact formal framing of "auxiliary signal
at train, absent at test", and (c) the negative-transfer literature, which is
where a *measurement* protocol would live if one exists.

## Search terms used

1. `value of information low-fidelity training data multi-fidelity surrogate how much does low-fidelity data help quantify`
2. `learning using privileged information when does it help theory quantify gain auxiliary training-only signal`
3. `multi-fidelity machine learning negative transfer when low fidelity data hurts ablation study matched budget`

## Findings per term

### Term 1 — value of LF data in MF surrogates

Top results: MAGPI (https://arxiv.org/html/2603.22050), MF Gaussian-process
surrogates for physics regression (https://arxiv.org/html/2404.11965),
Multifidelity DeepONets (https://arxiv.org/pdf/2204.09157), MF reduced-order
surrogate modelling
(https://royalsocietypublishing.org/rspa/article/480/2283/20230655/101080/Multi-fidelity-reduced-order-surrogate),
MF force fields for cathode materials (https://arxiv.org/pdf/2511.11361),
"Efficient Selection of Low-Fidelity Data for Multi-fidelity Surrogate Models"
(https://findanexpert.unimelb.edu.au/scholarlywork/2282466-efficient-selection-of-low-fidelity-data-for-multi-fidelity-surrogate-models).
Search-summary level claim worth noting: LF benefit is "particularly pronounced
when high-fidelity data is relatively scarce (e.g., fewer than 400 structure
frames)" — i.e. the field's own prior is that our regime (N_hf = 5–400) is where
LF should matter most.

**Fetched — MAGPI (https://arxiv.org/html/2603.22050)**: LF predictions are used
as *engineered input features* augmenting the HF GP's input space; each surrogate
is "directly conditioned on the predictions of all available lower-fidelity
surrogate models". Crucially for r2s4: "**The paper lacks explicit ablation
studies** quantifying low-fidelity contributions in isolation" — it compares
against single-fidelity kriging, Kennedy–O'Hagan AR, and NARGP, which is a
with/without-LF contrast at the *method* level but not at matched architecture
and budget. HF sample counts studied: 10 (analytical), 16 (laminar flame speed),
45 (flow-field interpolation) — squarely the scarce-HF regime, comparable to our
ifc_poisson N_hf = 5 rung.

### Term 2 — LUPI (privileged information)

Top results: Vapnik & Vashist "A new learning paradigm: Learning using
privileged information" (https://www.researchgate.net/publication/26695927_A_new_learning_paradigm_Learning_using_privileged_information),
"On the Theory of Learning with Privileged Information"
(https://www.researchgate.net/publication/220270210_On_the_Theory_of_Learning_with_Privileged_Information),
"Learning using privileged information: Similarity control and knowledge
transfer" (https://www.researchgate.net/publication/301362871_Learning_using_privileged_information_Similarity_control_and_knowledge_transfer),
Retaining Privileged Information for Multi-Task Learning
(https://pmc.ncbi.nlm.nih.gov/articles/PMC8596492/), Self-Improved Privilege
Learning (https://arxiv.org/pdf/2505.24207), AVSD adaptive-view
self-distillation (https://arxiv.org/pdf/2605.20643). **This is the exact formal
name for round 2's setting**: LF fields are privileged information (available at
train, absent at test); the two standard mechanism families are
distillation-based transfer (teacher with PI → student without) and
PI-inference-based.

**Fetched — Retaining Privileged Information for Multi-Task Learning
(https://pmc.ncbi.nlm.nih.gov/articles/PMC8596492/)**: PI is "available
exclusively at training time"; three conventional exploitation mechanisms are
parameter sharing (PI as auxiliary prediction task), regularization via prior
constraints, and data fusion (PI as auxiliary features), with the noted failure
mode that "if X is under-utilized during training, h(z) will likely lead to poor
generalization at test time". On measurement: "the related-work section does
**not** describe a standard matched-arm protocol for isolating PI's
contribution... lacks explicit ablation designs measuring marginal PI value
independently."

### Term 3 — negative transfer / when LF hurts

Top results: Understanding multi-fidelity training of machine-learned force
fields (https://arxiv.org/abs/2506.14963), MF transfer learning for quantum
chemical data with a DFTB baseline
(https://iopscience.iop.org/article/10.1088/2632-2153/adc222 ;
https://chemrxiv.org/engage/chemrxiv/article-details/673fa4a15a82cea2fa4a01eb),
multi-channel-fusion MF transfer learning
(https://www.sciencedirect.com/science/article/abs/pii/S0021999124002018),
practical MF ML fusion of deterministic and Bayesian models
(https://arxiv.org/html/2407.15110), Transfer learning on multifidelity data
(https://www.dl.begellhouse.com/journals/558048804a15188a,441149b76421eaa9,1171f2446ae04ad7.html).
Named phenomenon: **negative transfer** — "if the correlation between the two
different fidelity datasets is not strong enough, transfer learning is not
effective and can even deteriorate the learning performance". This is the
falsifiable outcome r2s4's value-of-LF card must be able to report.

**Fetched — Understanding multi-fidelity training of machine-learned force
fields (https://arxiv.org/abs/2506.14963)**: abstract-level only (the fetch saw
the abstract). It "systematically investigates two multi-fidelity strategies"
and reports a **log–log linear relationship between pre-trained and fine-tuned
accuracies**, that "multi-headed models learn method-independent backbone
representations", and that relative to pretrain→finetune those shared
representations "marginally reduce model performance in most cases"; success
depends on "the quantity and quality of available pre-training data, and,
critically, the inclusion of force labels". The fetch could NOT confirm
matched-budget with/without-LF arms, a redundancy analysis, or a threshold for
when LF stops helping — noted as not visible in the abstract, so I do not claim
it either way.

## Interpretation

Round 2's regime has an exact published name — **LUPI / privileged information**
— and its two mechanism families (distillation, auxiliary-feature/multi-task)
are precisely r2s3's candidate levers, so r2s3's *mechanisms* are certainly
preempted. What three independently fetched sources agree on is the **absence of
a standard protocol for measuring the marginal value of the privileged/LF
signal**: MAGPI has no isolating ablation, the LUPI multi-task paper says the
related work has no matched-arm protocol, and the MF-force-field study's
matched-budget design could not be confirmed. Next iteration: tiny-N
overfitting anatomy / effective sample size, then the targeted refutation
searches.
