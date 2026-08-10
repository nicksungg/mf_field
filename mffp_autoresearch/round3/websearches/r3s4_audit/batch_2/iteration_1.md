# Iteration 1 — checkpoint↔training-data binding as a staleness witness (C1)

## Search rationale

The single biggest routed contract change for batch 2 is the **sixth-class check**: bind `state/data_hashes.json` sha256 values *inside* `last.pt` so the audit predicate becomes `executed_steps == 0 AND ckpt.data_binding[ds].train_sha256 != current`.
Batch 1 already established that generic *pipeline/experiment-tracker* provenance is preempted (Tribuo, https://arxiv.org/abs/2110.03022).
The open question is narrower: is **binding the training-data content hash into the model artifact itself, and using the mismatch as a correctness predicate for a resumed run**, published?
Terms 1 and 2 attack the provenance/versioning side; term 3 attacks the "silent training error detector" side, because our defect (a resumed checkpoint silently carrying weights fitted to superseded arrays) is a silent-error-detection problem, not a supply-chain problem.

## Search terms used

1. `embed dataset hash in model checkpoint provenance verify training data reproducibility`
2. `content-addressed data versioning stale model detection retraining trigger machine learning pipeline`
3. `silent stale checkpoint resume wrong data experiment integrity bug scientific machine learning benchmark audit`

## Findings

### Term 1 — dataset hash embedded in checkpoint provenance

Top results: Atlas (SysTEX'25, Intel Labs) https://systex-workshop.github.io/2025/papers/systex25-final68.pdf ; federated-learning provenance DB https://arxiv.org/html/2403.01451v1 ; ML supply-chain security https://arxiv.org/pdf/2602.19021 ; clinical-NLP provenance https://arxiv.org/pdf/2601.19191 ; two vendor guides (inferensys.com, smart-labs.cloud).

**FETCHED — Atlas: A Framework for ML Lifecycle Provenance & Transparency** (Spoczynski, Melara, Szyller; Intel Labs), https://systex-workshop.github.io/2025/papers/systex25-final68.pdf (75,960 chars extracted via `pypdf`).
Atlas proposes "fully attestable ML pipelines": runtime pipeline monitoring (PyTorch hooks, filesystem monitor, config wrappers) collects **signed cryptographic measurements** of every artifact, and a verification service later checks that the model's training lineage is intact.
Its Figure-1 workflow explicitly measures **"Upload Dataset / Checkpoint Files"** in one attested chain, with design requirement **R1: "Artifact tampering is detectable ... detect unexpected modifications to model [artifacts]"**.
Related work in the same paper: EQTY Lineage Explorer "tracks model artifacts throughout the training process, capturing relationships between datasets, model checkpoints and hyperparameters", criticized only for lacking cryptographic authenticity; and OpenSSF Model Signing for integrity/authenticity of trained models.
Framing: adversarial (poisoning, dishonest MLaaS providers, EU AI Act evidence), **not** accidental staleness; the verification target is "was this artifact tampered with", not "were these weights fitted to a superseded revision of the training array".

### Term 2 — content-addressed versioning / stale-model triggers

Results: Modyn (data-centric pipeline orchestration) https://arxiv.org/pdf/2312.06254 ; Azure ML drift-triggered retraining; SageMaker drift retraining; martinfowler.com CD4ML; lakefs.io model versioning; ml-ops.org principles.
Snippet-level content (not fetched): DVC-style content checksums trigger pipeline re-execution when file contents change; "stale model" in this literature means **statistical drift** (accuracy decay, distribution shift), and the trigger is a monitoring alarm, not a hash mismatch between an artifact and its training inputs.
This is the key distinction for the verdict: the MLOps sense of "stale" is *the world changed*, ours is *the training array changed under a resumed checkpoint*.

### Term 3 — silent training errors / integrity audit

Results: TRAINCHECK (OSDI'25) https://www.usenix.org/system/files/osdi25-jiang.pdf ; SDC in LLM training https://arxiv.org/pdf/2502.12340 and https://arxiv.org/html/2604.00726v1 ; OCP SDC-in-AI whitepaper; silent bugs in DL frameworks https://arxiv.org/pdf/2112.13314.

**FETCHED — "Training with Confidence: Catching Silent Errors in Deep Learning Training with Automated Proactive Checks" (TRAINCHECK, Jiang et al., OSDI 2025)**, https://www.usenix.org/system/files/osdi25-jiang.pdf (95,632 chars).
TRAINCHECK automatically **infers training invariants** ("rules that should hold throughout the training"; violation ⇒ potential error), attaches **preconditions** to each invariant explicitly to *reduce false positives* and to make violations explainable, and checks them proactively at runtime.
Evaluation: reproduces **20 real-world silent training errors**, detects 18, mostly in the first few iterations; the two misses include an error where "the trainer stops early ... while the training process itself is correct".
**False-positive measurement is a first-class section (§5.3): 63 diverse known-good training programs are run to price FPs**, grouped into four task classes to control confounding.
Implementation detail directly relevant to us: they explicitly considered dumping model state and instead **log hashes of tensors** because full state dumps are "unbearable" in cost.
Framing: in-process correctness of the training stack (dtype/optimizer/parallelism bugs); the data-identity dimension (which arrays these weights were fitted to) is not part of its invariant space.

## Interpretation

Both halves of C1 have strong, fetched neighbours — Atlas for cryptographically binding dataset and checkpoint artifacts in one attested lineage, TRAINCHECK for proactive rule-based detection of silent training errors *including* the practice of pricing a rule's false positives against known-good runs (the exact methodology this stream applied to `train_seconds_collapsed`: 0 unique TPs / 62 FPs).
Neither addresses the specific predicate we need: a *benchmark-scoring* correctness condition of the form "zero optimizer steps executed AND embedded train-array hash ≠ current train-array hash", with **train and test arrays hashed separately** so a test-split trim does not invalidate weights.
The next iteration must attack that residual directly (and the MDE/unobservable-reference question, C2) rather than re-establishing that provenance hashing exists.
