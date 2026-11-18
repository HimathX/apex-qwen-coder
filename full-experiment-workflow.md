# Canonical fine-tuning experiment workflow and results

**Snapshot:** 18 November 2026, Asia/Colombo. This document consolidates the completed experiments and the prepared follow-up notebook known at this point. It supersedes stale progress counts in older workflow notes; those files and historical artifacts remain unchanged.

**Best recorded test result:** Qwen2.5-Coder-7B-Instruct, original MCQ adapter followed by one augmented continuation epoch: **222/269 = 82.53% test**, **184/192 = 95.83% validation**. This result starts from an already fine-tuned adapter. The requested fresh-start Qwen augmented experiment has been prepared but has no reported GPU result.

## 1. Task, terminology, and evidence

The task is to answer multiple-choice questions about a particular Unity/C# game project. Training knowledge comes from supplied project QA; evaluation uses the supplied MCQ test set. This is a project-knowledge task, not a general coding benchmark.

Terminology used throughout:

- **Fresh start / from base:** load the original pretrained instruction model and initialize a new LoRA adapter and optimizer. It does not mean randomly initializing and pretraining a multi-billion-parameter model.
- **Continuation / warm start:** load a previously trained MCQ adapter as trainable weights on the pinned pretrained model; initialize a fresh optimizer and scheduler.
- **Rotation:** permute the four answer choices while preserving the correct answer text and remapping its letter. A rotation is not a new factual question.
- **Variant:** a newly authored MCQ derived from a training source. The augmented dataset contains original variant 0 and new variants 1 and 2.
- **Three checkpoints:** snapshots near one-third, two-thirds, and the end of one epoch. They are not three epochs, three independent models, or three sequential passes over the full dataset.
- **Invalid answer:** a response the fixed answer parser cannot convert to a valid choice; scored as wrong.
- **pp:** percentage points, distinct from relative percent improvement.

Evidence tiers:

| Evidence | Availability and use |
|---|---|
| Historical Qwen baseline, QA, MCQ, and alignment artifacts | Local summaries, predictions and/or metadata cited below; preferred over old prose summaries |
| Qwen augmented continuation | Saved completed [notebook194c0310c8.ipynb](../notebook194c0310c8.ipynb), user-pasted final summary, and subsequently recovered local [final.zip](../final.zip) with the final adapter and raw outputs |
| OpenCoder final four-arm comparison | Exact final CSV supplied by the user on 18 November; reproduced in section 8.3 |
| OpenCoder intermediate checkpoints | `output.txt` (previously inspected; not present in this organized snapshot), a partial log ending during augmented training; it does not contain the entire final run |
| Fresh-start Qwen augmented run | Notebook, code checks and local tokenizer preflight only; no completed GPU benchmark supplied |

The user-supplied aggregate results are accepted as reported. They do not imply that all corresponding remote raw prediction files have been independently recovered locally. Signed download URLs and credentials are deliberately excluded.

## 2. Data and evaluation contract

### 2.1 Source data and split lineage

| Artifact / cohort | Size | Meaning |
|---|---:|---|
| [TrainData.csv](../TrainData.csv) | 1,910 QA records | Original `class`, `Q`, `A` source |
| [TestData.csv](../TestData.csv) | 269 MCQs | Original supplied test; unchanged |
| Generated original MCQ training CSV | 1,718 MCQs | Training portion of the seeded, question-grouped split |
| Generated validation CSV | 192 MCQs | Training-derived validation, fixed order and bytes retained |
| Admitted original MCQ training sources | 1,717 | Source row 1817 excluded at Qwen's 4,096-token limit |
| New variants | 3,434 | Two per admitted source |
| Final augmented MCQs | 5,151 | 1,717 sources × 3 MCQs |

Original QA training used 1,718 training rows and 192 held-out QA rows. Later OpenCoder QA training uses only the **same 1,717 admitted sources** as its MCQ arms, keeping the source cohort matched. These are different historical training cohorts and must not be conflated.

The original MCQ dataset came from `generate_mcq_deepseek.py`, initially with generation and review calls, later with generator-only continuation. The completed generation had 1,873 accepted examples and 37 rejected examples. The 37 were repaired offline; four source-answer corrections and repair rationales are recorded in [repair-audit.jsonl](../data/mcq/manual-repaired-final/repair-audit.jsonl). Final CSVs total 1,910 examples across training/validation. See [MCQ_GENERATION.md](../MCQ_GENERATION.md).

The split groups identical normalized source questions. Source IDs are isolated between training and validation; this is not proof that all semantic paraphrases or related code facts are disjoint. `source_row` is a zero-based source-record index, not a human CSV line number. Augmented example identity is `(source_row, variant_id)`.

### 2.2 Evaluation behavior

- MCQ prompts contain the question and four options, without the answer label. The shared implementation is [benchmark.py](../benchmark.py).
- The requested response ends in `Answer:a`, `Answer:b`, `Answer:c`, or `Answer:d`. The parser also accepts a standalone choice letter; invalid/missing answers count as wrong.
- Main Qwen2.5/OpenCoder comparisons use the model's chat template, greedy decoding and at most 128 generated tokens per question. No retries or post-hoc semantic rescue enter official accuracy.
- Fixed validation has 192 questions; test has 269. Rotated validation has 768 presentations: all four orders for each validation question.
- Training receives neither test labels nor validation examples. Validation is used for monitoring; test is evaluated after each completed full arm. The baseline also scores test without training.
- The original assessment [Finetune_Test.ipynb](../Finetune_Test.ipynb), including its prohibited-to-edit `test_model` cell, remains separate and unchanged. These results come from the explicit benchmark workflows.
- Test labels are imbalanced: `a=97`, `b=82`, `c=49`, `d=41`. Uniform random choice has 25% expected accuracy; always choosing `a` scores 36.06%.

The test set has been evaluated repeatedly during the project. It remains excluded from training but is no longer a prospectively untouched final holdout. Results describe this fixed test set.

## 3. Complete experiment ledger

Percentages below are rounded to two decimals; integer counts and raw aggregates are authoritative. A dash means unavailable or not comparable, not zero.

| ID | Model and experiment | Initialization | Training presentations | Validation | Test correct / 269 | Test accuracy | Test invalid |
|---|---|---|---:|---:|---:|---:|---:|
| Z0 | Qwen3-4B early zero-shot | Pretrained, no training | 0 | — | 66 | 24.54% | 192 |
| Q0 | Qwen2.5-Coder-7B zero-shot | Pretrained, no training | 0 | — | 182 | 67.66% | 24 |
| Q1 | Qwen original free-form QA | Fresh LoRA on pretrained Qwen | 1,718 | QA loss only; not the later MCQ accuracy cohort | 115 | 42.75% | 109 |
| Q2 | Qwen original MCQs, four rotations | Fresh LoRA on pretrained Qwen | 6,868 | 182/192 = 94.79% | 210 | 78.07% | 0 |
| Q3 | Qwen original MCQs + simplified alignment | Fresh LoRA on pretrained Qwen | 6,868 | 182/192 = 94.79% | 208 | 77.32% | 0 |
| Q4 | Qwen augmented continuation | **Q2 trained adapter**, fresh optimizer | 5,151 additional | 184/192 = 95.83% | 222 | **82.53%** | 0 |
| O0 | OpenCoder-8B untuned | Pretrained, no training | 0 | 60/192 = 31.25% | 137 | 50.93% | 61 |
| O1 | OpenCoder original QA | Fresh LoRA on pretrained OpenCoder | 1,717 | 23/192 = 11.98% | 53 | 19.70% | 194 |
| O2 | OpenCoder original MCQs | Fresh LoRA on pretrained OpenCoder | 1,717 | 159/192 = 82.81% | 193 | 71.75% | 0 |
| O3 | OpenCoder augmented MCQs | Fresh LoRA on pretrained OpenCoder | 5,151 | 167/192 = 86.98% | 194 | 72.12% | 0 |
| Q5 | Qwen augmented MCQs, fresh start | Fresh pretrained Qwen + fresh LoRA | 5,151 planned | **No GPU result reported** | — | — | — |

Each completed trained arm uses one epoch on its specified presentation dataset. Q4 is **one additional epoch after Q2**: its complete learning history includes 6,868 original MCQ presentations plus 5,151 augmented presentations, or 12,019 presentations across two stages. O1/O2/O3 start independently; they do not inherit one another's adapters.

## 4. Early zero-shot and original-QA experiments

### 4.1 Qwen3-4B zero-shot

Recorded result: 66/269 correct (24.54%), 192 invalid answers and 188 responses reaching the token budget; elapsed scoring time 2,435.49 seconds. This is near the uniform-random expectation and below the majority-label baseline, with severe generation/format-budget failures.

Evidence is an aggregate extracted from saved notebook stdout; per-question artifacts were not recovered in that snapshot. Do not generalize it into a claim about Qwen3's underlying coding ability. See [summary.from-notebook.json](../results/history/20261113-zero-shot/summary.from-notebook.json) and [BASELINE.md](../BASELINE.md).

### 4.2 Qwen2.5-Coder-7B baseline and free-form QA fine-tuning

The baseline scored 182/269 (67.66%); one epoch on original free-form QA scored 115/269 (42.75%). The change is **−24.91 pp**, a **36.81% relative accuracy decline**. Paired prediction counts recorded 20 wrong-to-correct and 87 correct-to-wrong changes.

Invalid outputs increased from 24 to 109. Only two baseline responses and no tuned responses hit the generation budget. Answer-format/task mismatch is a plausible explanation: QA training teaches open-ended answers while evaluation requires a choice. This remains an interpretation, not a complete diagnosis of all errors.

Recorded QA train loss was 1.11837 and QA validation loss 1.00382. These are different targets from MCQ loss and do not imply good MCQ accuracy. Adapter reload succeeded.

This run used max length 2,048, 1,718 training examples, 192 QA validation examples, seed 42 and the common LoRA settings below. Source artifacts: [comparison.json](../qwen25-coder-7b-20261113T053732139734Z/comparison.json), [metadata.json](../qwen25-coder-7b-20261113T053732139734Z/metadata.json). Earlier historical notes claiming raw artifacts were still remote are superseded where these local copies exist.

## 5. Qwen original MCQ training and position rotations

Q2 starts from pretrained Qwen2.5-Coder-7B-Instruct, not from the failed QA adapter. Training targets are exactly `Answer:<letter>` with assistant-only causal loss.

Each original MCQ is deterministically shuffled by source ID and seed, then cyclically rotated four times. Every option and the correct answer visit each letter once. Code capitalization and option text are preserved. The training examples are shuffled globally.

At max length 4,096, source row 1817 requires 5,176 tokens and is excluded as a whole group, leaving **1,717 MCQs × 4 = 6,868 presentations**. Every answer letter is correct 1,717 times. All 192 validation questions are admitted. There is no silent truncation.

| Q2 metric | Result |
|---|---:|
| Fixed validation | 182/192 = 94.79% |
| Test | 210/269 = 78.07% |
| Rotated validation | 720/768 = 93.75% |
| Correct-answer position a / b / c / d | 94.27% / 92.71% / 93.75% / 94.27% |
| Same answer text selected across all four orders | 173/192 = 90.10% |
| Correct in all four orders | 171/192 = 89.06% |
| Training loss / epoch | 0.04678 / 1.0 |
| Training runtime | 10,040.89 s, about 2.79 h |
| Peak allocated GPU memory | 13.98 GiB |

Compared with the historical Q0 baseline, test improvement is **+10.41 pp**, 28 more correct answers, a 15.38% relative accuracy gain and a 32.18% relative error reduction. Paired historical predictions record 43 fixes and 15 regressions. However, this was not a same-run baseline rerun, and package versions differed.

There is no matched-exposure nonrotation control. The improvement cannot be attributed specifically to position rotation rather than MCQ-format targets, training exposure or their combination.

Evidence: [canonical retained results](../results/README.md), [comparison.json](../results/latest-run/comparison.json), [analysis summary](../analysis/kaggle-mcq-20261114/summary.json), [MCQ_ROTATION.md](../MCQ_ROTATION.md).

## 6. Simplified QA-conditioned alignment experiment

Q3 is a separate fresh-base Qwen run with the same original MCQs and four training rotations, plus a weighted representation objective. It does not continue Q2.

The reference prompt includes original QA then the rotated MCQ. Reference vectors use LoRA-disabled, eval, no-gradient decoder representations; the student uses MCQ-only input with LoRA enabled. The alignment is cosine-based, weighted **0.05**, computed on the fly. Original QA text is preserved. The maximum reference cap is 16,384 and observed maximum reference length is 5,000. Validation remains MCQ-only.

This is a **simplified alignment experiment, not an exact KEFT reproduction**.

| Metric | Q2 without alignment | Q3 with alignment | Change |
|---|---:|---:|---:|
| Fixed validation | 182/192 = 94.79% | 182/192 = 94.79% | 0 pp |
| Test | 210/269 = 78.07% | 208/269 = 77.32% | −0.74 pp; two fewer correct |
| Rotated validation | 720/768 = 93.75% | 723/768 = 94.14% | +0.39 pp |

Validation had one wrong-to-correct and one correct-to-wrong change. Both runs had zero invalid test responses. Alignment training took 16,477.32 seconds (about 4.58 h), with training loss 0.04807 and peak allocated memory 14.00 GiB.

The observed result does not support a test-accuracy benefit from this alignment setup. It did improve aggregate rotated validation slightly. Alignment was disabled for the later augmented continuation.

Evidence: [alignment comparison](../mcq-alignment-20261115T044618514334Z/alignment/comparison.json), [validation comparison](../mcq-alignment-20261115T044618514334Z/validation_comparison.json), [alignment implementation](../mcq_alignment.py).

Do not confuse Q3's measured 208 correct with an older post-hoc semantic diagnostic that also reported 208: the latter was not an official replacement score for the original QA run.

## 7. Two new MCQ variants and Qwen continuation

### 7.1 Generation, acceptance policy, and repairs

Three `gpt-6-luna` workers received deterministic disjoint assignments of 573/572/572 admitted sources. Each received the original QA, original MCQ and related admitted training QA. They did not receive validation/test questions, answers or individual failure cases.

- Variant 1: rephrase the question, keep the correct answer/code verbatim, and generate new distractors.
- Variant 2: ask a focused condition, consequence, identifier or factual distinction supported by the same evidence; otherwise fall back to another faithful same-answer variant.
- Requested general targets included missed conditions, reversed actions, confused events, exact constants and generic answers.

The initial plan required primary semantic reviews. The user subsequently instructed: **“don't do reviews accpe them as it is.”** Final variants are therefore accepted **as generated**, not claimed to have passed a complete semantic review. Historical reviews and rejection/repair records are retained. Technical checks still cover schema, identities, split isolation, deterministic merge, answer remapping, context fit and integrity.

All **3,434 variants** are complete: worker counts 1,146 / 1,144 / 1,144. The final dataset has **5,151 MCQs**, exactly three per source. Technical missing-option repairs and raw lineage are retained in worker provenance.

Six approved field edits affect only augmented originals:

| Source row | Field | Approved correction |
|---:|---|---|
| 6 | option a | Reverse the player/beast direction in one distractor to remove equivalent correct options |
| 533 | keyed option a | Puzzle-indicator behavior |
| 536 | keyed option b | `turnedOnAfterPuzzle` lights behavior |
| 539 | keyed option c | `puzzleMainDoor` unlock behavior |
| 715 | question | Ask for handler implementation rather than event name; preserve options |
| 833 | question | Ask about local-Y movement over 0.5 seconds rather than serialization; preserve options |

These edits are distinct from the earlier manual generation repairs. The historical QA/MCQ control, evaluation files and starting adapter were preserved. Before/after values, evidence and approvals are in [original_repairs.json](../data/mcq/augmentation/original_repairs.json) and [approved_five_fixes_receipt.json](../data/mcq/augmentation/approved_five_fixes_receipt.json).

### 7.2 Final budget and initialization

The original augmentation plan proposed 20,604 presentations through four rotations. The user changed this to **one randomized option order per MCQ and one epoch**. The actual run is **5,151 presentations**, not 20,604. Seed42 answer counts are `a=1268`, `b=1313`, `c=1292`, `d=1278`; exact four-way balance is not expected for one random order.

Actual tokenizer preflight: **1,079,377 input tokens**, **20,604 supervised tokens**, **4,005 longest-presentation tokens**, zero exclusions and **322 optimizer updates**. The value 20,604 here is supervised token count, not training presentations.

Q4 loads Q2's original trained MCQ adapter with trainable PEFT loading and a fresh optimizer/scheduler. It does not load the alignment adapter. The pinned starting-adapter weights hash is `11ccee4e737ddadc11258d5e3ac6820b82804036a7ca3b3f05ae45c4c44f9f95`. Loaded LoRA tensors are verified against the saved adapter, gradients are finite/nonzero, and base weights remain frozen.

The GPU smoke includes the longest used presentation. The full run reloads Q2's original starting adapter independently, discarding smoke weights. Adapter save/reload and the interactive demo completed successfully.

### 7.3 Three within-epoch checkpoints and final results

| Checkpoint | Optimizer step | Epoch fraction | Validation correct / 192 | Validation accuracy | Validation loss |
|---|---:|---:|---:|---:|---:|
| 1 | 108 | 0.3355 | 182 | 94.79% | 0.045794 |
| 2 | 215 | 0.6678 | 183 | 95.31% | 0.054336 |
| 3 | 322 | 1.0000 | 184 | 95.83% | 0.045505 |

Full-epoch training runtime was 6,793.11 seconds (about 1.89 h), with mean training loss 0.06842. This is training runtime, not total notebook runtime.

| Final metric | Q2 original adapter | Q4 augmented continuation | Change |
|---|---:|---:|---:|
| Validation | 182/192 = 94.79% | 184/192 = 95.83% | +1.04 pp; net +2 correct |
| Test | 210/269 = 78.07% | 222/269 = 82.53% | +4.46 pp; net +12 correct |
| Test invalid / token-budget hits | 0 / 0 | 0 / 0 | No failures of either kind |

Validation paired predictions show four fixes and two regressions. A paired test breakdown was not supplied, so net +12 must not be described as exactly 12 fixes and zero regressions. Test relative accuracy gain is 5.71%; relative error reduction is 20.34% (59 errors to 47).

The pasted final test summary reports model `Qwen/Qwen2.5-Coder-7B-Instruct`, 269 questions, 222 correct, accuracy `0.8252788104089219`, zero invalid answers, zero token-budget hits and 135.31747 seconds of test scoring.

The completed notebook ran fixed validation, test and rotated validation after adapter reload. The subsequently recovered `final.zip` confirms **724/768 = 94.27% rotated validation**, versus Q2's 720/768 = 93.75% (+0.52 pp). This value was unavailable in the earlier notebook-only summary.

Both fixed validation and test improved, but that does not prove absence of overfitting or a paraphrasing-specific effect. This comparison changes cumulative training, the data, option exposure and approved source repairs. It has no matched extra-training-only control.

Evidence: [completed Qwen notebook](../notebook194c0310c8.ipynb), [augmented manifest](../data/mcq/augmented-final/augmentation_manifest.json), [acceptance policy](../data/mcq/augmentation/acceptance_policy.json). Kaggle run: [notebook194c0310c8](https://www.kaggle.com/code/himathdhanapala/notebook194c0310c8). Remote run directory: `mcq-augmentation-20261117T051401617175Z`; final score path: `continuation/finetuned/test/summary.json`.

## 8. OpenCoder independent four-arm experiment

### 8.1 Experimental design and execution fix

Model: `infly/OpenCoder-8B-Instruct`, pinned revision `cc9efae8dc513fe21e4b2572ea6ccacd4e68998b`. Its configuration uses native Llama architecture with an 8,192-token context. Its tokenizer is custom `INFLMTokenizer` code supplied by the official model repository.

The four arms are untuned baseline, original QA, original MCQ variant0, and all three MCQ variants. Each trained arm starts independently from pretrained OpenCoder with fresh LoRA and optimizer. There is no QA-to-MCQ chain and no Qwen adapter loading. All three trained arms use one epoch. Both MCQ arms use a single deterministically shuffled option order per example; rotated validation is evaluation only.

The first uploaded notebook failed **before training**, at tokenizer preflight: the custom tokenizer requested interactive permission, causing `EOFError` followed by a `trust_remote_code` error in a background subprocess. The corrected tokenizer load explicitly enables `trust_remote_code=True`, pins `code_revision` to the same commit and sets `use_fast=False`. No original dataset re-upload was required for the hotfix notebook.

Notebook/data definitions: [opencoder_benchmark.py](../opencoder_benchmark.py), [OpenCoder fixed notebook](../OpenCoder_Four_Arm_Benchmark_FIXED.ipynb), [manual bundle](../Kaggle_OpenCoder_Four_Arm_Benchmark.zip). The local [notebookf5373d8eeb.ipynb](../notebookf5373d8eeb.ipynb) copy had the hotfix but no saved execution outputs when inspected; `output.txt` (previously inspected; not present in this organized snapshot) supplies intermediate execution evidence. Kaggle notebook identifier: `himathdhanapala/notebookf5373d8eeb`.

### 8.2 Actual training budgets

| Arm | Presentations | Input tokens | Supervised tokens | Longest example | Updates |
|---|---:|---:|---:|---:|---:|
| Original QA | 1,717 | 193,222 | 98,490 | 1,421 | 108 |
| Original MCQs | 1,717 | 492,044 | 6,868 | 4,055 | 108 |
| Augmented MCQs | 5,151 | 1,080,351 | 20,604 | 4,055 | 322 |

The configured cap is 8,192 with no truncated or silently excluded groups. A tokenizer warning in the log mentions a 1,300-token metadata limit; the model's actual configured context is 8,192, and training continued. The warning alone is not evidence that examples were truncated. Installed runtime metadata should be retained alongside these numbers.

The one-epoch augmented arm has 2.98× the optimizer updates of the original-MCQ arm. It is not an equal-compute comparison.

### 8.3 Final reported results

| Arm | Fixed validation | Test | Correct / 269 | Invalid | Rotated validation | Arm wall time |
|---|---:|---:|---:|---:|---:|---:|
| Untuned | 31.25% | 50.93% | 137 | 61 | 32.81% | 7,659.82 s / 2.13 h |
| Original QA | 11.98% | 19.70% | 53 | 194 | 13.02% | 12,832.64 s / 3.56 h |
| Original MCQs | 82.81% | 71.75% | 193 | 0 | 82.94% | 4,450.83 s / 1.24 h |
| Augmented MCQs | 86.98% | 72.12% | 194 | 0 | 87.37% | 8,122.18 s / 2.26 h |

The reported per-arm seconds include preparation/loading/training where applicable and evaluations, rather than training alone. Their sum is about 9.18 hours and excludes separately run smoke/setup overhead; it is not directly comparable to Qwen's training-only runtime.

Exact aggregate CSV supplied by the user:

```csv
arm,validation_accuracy,test_accuracy,test_correct,test_invalid,rotated_validation_accuracy,training_presentations,optimizer_steps,seconds
base,0.3125,0.5092936802973977,137,61,0.328125,0,0,7659.820081938
qa,0.11979166666666667,0.1970260223048327,53,194,0.13020833333333334,1717,108,12832.644610372
mcq_original,0.828125,0.7174721189591078,193,0,0.8294270833333334,1717,108,4450.831552832999
mcq_augmented,0.8697916666666666,0.7211895910780669,194,0,0.8736979166666666,5151,322,8122.179269448003
```

### 8.4 Intermediate checkpoint values and final-reload differences

All checkpoint validation rows below use 192 questions. Accuracy values of 50% from tiny CPU tests and 0% from two-question GPU smoke checks are deliberately excluded.

| Arm | Step | Validation correct | Accuracy | Validation loss |
|---|---:|---:|---:|---:|
| QA checkpoint1 | 36 | 29 | 15.10% | 1.463881 |
| QA checkpoint2 | 72 | 24 | 12.50% | 1.557554 |
| QA checkpoint3 | 108 | 24 | 12.50% | 1.596781 |
| Original MCQ checkpoint1 | 36 | 140 | 72.92% | 0.159818 |
| Original MCQ checkpoint2 | 72 | 154 | 80.21% | 0.138945 |
| Original MCQ checkpoint3 | 108 | 159 | 82.81% | 0.132574 |
| Augmented MCQ checkpoint1 | 108 | 159 | 82.81% | 0.132015 |
| Augmented MCQ checkpoint2 | 215 | 170 | 88.54% | 0.097557 |
| Augmented MCQ checkpoint3 | 322 | Not recovered in local partial log | Not recovered | Not recovered |

The final **reloaded-model** comparison is authoritative for the final-results table. QA final validation is **23/192 = 11.98%**, whereas checkpoint3 reports 24/192 = 12.50%. These refer to different evaluation stages; the reason for the one-question difference is not established by available aggregates.

Augmented final reloaded validation is **167/192 = 86.98%**, below checkpoint2's 170/192 = 88.54% by three questions (−1.56 pp). Because the checkpoint3 record was not recovered locally, this should not be presented as proof that the final training segment alone caused the difference. Save/reload and evaluation-stage differences have not been fully isolated.

No earlier checkpoint's test score is reported; selecting one for a fresh test run based on validation would be a new experiment, not an already measured improvement.

### 8.5 What the OpenCoder results support

1. **MCQ-format training improves measured task performance.** O2 gains 56 correct test answers over O0: +20.82 pp, 40.88% relative accuracy gain and 42.42% relative error reduction. Invalid answers drop from 61 to zero. This combines answer-format learning and whatever factual/task learning occurred; aggregates cannot separate them.
2. **QA fine-tuning performs poorly under the fixed MCQ parser.** There are 194 invalid test outputs, leaving 75 valid responses and 53 correct. The observed 19.70% official accuracy includes these failures. It is not a clean estimate of factual knowledge alone. Raw outputs would be needed to diagnose the failure mechanism.
3. **Augmentation adds little measured test improvement here.** O3 gains just one correct answer over O2: +0.37 pp, 0.52% relative accuracy gain and 1.32% relative error reduction, despite nearly three times the updates. Fixed validation gains 4.17 pp and rotated validation gains 4.43 pp.
4. **An accuracy decline appears between the best observed intermediate and final reloaded validation.** It is a monitoring signal, not definitive proof of overfitting. One seed and aggregate scores do not establish statistical significance or the cause of the change.

## 9. Training and software configuration

Common Qwen MCQ / OpenCoder recipe unless explicitly noted:

| Setting | Value |
|---|---|
| Seed | 42 |
| Adaptation | QLoRA, base weights frozen |
| Quantization | 4-bit NF4, double quantization |
| Compute | float16 on one GPU; SDPA attention |
| LoRA | Rank16, alpha32, dropout0.05, no bias |
| LoRA target projections | q/k/v/o and gate/up/down |
| Loss | Assistant-only masked causal language-model loss |
| Vocabulary projection | Only positions predicting supervised assistant tokens |
| Epochs | One per trained stage/arm |
| Batch / accumulation | 1 / 16 |
| Learning rate | 1e-4; a lower rate was discussed but not adopted in these reported runs |
| Optimizer | Paged AdamW8bit |
| Schedule | Cosine, warmup ratio0.05 |
| Weight decay / gradient clipping | 0.01 / 0.3 |
| Memory | Gradient checkpointing; longest-example GPU smoke |
| Qwen MCQ context cap | 4,096 |
| Qwen historical QA context cap | 2,048 |
| OpenCoder context cap | 8,192 |
| Evaluation | Greedy, max128 new tokens, invalid answers wrong |
| Checkpoint selection | Full one-epoch run; no automatic best-checkpoint selection |

Qwen revision: `c03e6d358207e414f1eca0bb1891e29f1db0e242`. OpenCoder revision: `cc9efae8dc513fe21e4b2572ea6ccacd4e68998b`.

Qwen Q2/Q3/Q4 retained records report Tesla T4, torch2.11.0+cu130, transformers4.57.3, PEFT0.17.1, accelerate1.15.0, bitsandbytes0.48.2. Historical Q0/Q1 records report torch2.14.1+cu130 and bitsandbytes0.50.2, with the same listed Transformers/PEFT/Accelerate versions. These are recorded artifact values, not a claim about current package availability.

The OpenCoder notebook pins Transformers/PEFT/Accelerate/bitsandbytes to the latter recipe and records actual runtime versions. Its complete actual runtime metadata was not supplied with the final aggregate CSV, so exact environment equality with Qwen is not claimed.

CPU checks exercise source/variant identity handling, deterministic rotations/merge, answer preservation, token masking and sparse-loss equivalence. Tiny Qwen/PEFT and native-Llama tests verify actual gradient/loss behavior, checkpoint saves and reloads. Accuracy generation is stubbed only inside identified tiny CPU tests; those test scores are never benchmark results. Actual quantized GPU smoke is a separate gate in each notebook.

## 10. Fresh-start Qwen request and prepared artifact

After seeing Q4's result, the user clarified that they wanted to start from the pretrained Qwen model rather than Q2's trained adapter. The prepared replacement is [Qwen_MCQ_Fresh_Base_OneEpoch.ipynb](../Qwen_MCQ_Fresh_Base_OneEpoch.ipynb).

It uses the existing private Qwen augmented dataset, calls `--fresh-base`, omits `--starting-adapter`, initializes fresh LoRA matrices, checks zero-initialized LoRA B weights, and starts a fresh optimizer. It retains one epoch, 5,151 examples, one shuffled option order, three checkpoint evaluations and unchanged validation/test. Smoke and full training initialize independently. Results go under `fresh_training/`, with final scores explicitly printed.

Manifest checks in fresh mode preserve data hashes, pinned base revision, source groups and completeness, while rejecting any supplied starting adapter. Historical adapter hashes remain dataset lineage, not loaded model state. A locally saved tokenizer may be reused in prepare-only checks without loading learned adapter weights.

Local checks passed: fresh-mode manifest acceptance/rejection tests, full-size deterministic merge compatibility, notebook format/code compilation and tokenizer-only preflight. The latter admits all 5,151 presentations with no exclusions. **No completed fresh-start Qwen GPU result has been reported; do not assign Q4's 82.53% to this notebook.**

## 11. Cross-model interpretation and limits

| Comparison | Observed test difference | What can be said |
|---|---:|---|
| Qwen Q4 vs Qwen Q2 | +12 correct; +4.46 pp | Additional augmented continuation improved the measured score |
| Qwen Q3 vs Qwen Q2 | −2 correct; −0.74 pp | This alignment setup showed no test gain |
| OpenCoder O3 vs O2 | +1 correct; +0.37 pp | Small observed incremental test gain despite larger budget |
| Qwen Q2 vs OpenCoder O2 | +17 correct; +6.32 pp for Qwen | Qwen is higher in recorded runs; four vs one presentation per original MCQ differs |
| Qwen Q4 vs OpenCoder O3 | +28 correct; +10.41 pp for Qwen | Qwen is the best measured pipeline; Qwen includes prior MCQ training |

These are single-seed descriptive results. There are no multiple-seed means/standard deviations, training-variability estimates or demonstrated significance claims. A one-question test difference is especially weak evidence of a repeatable advantage. Marginal counts alone do not establish per-question paired improvements or allow a paired significance conclusion.

The Qwen/OpenCoder comparison changes model family, tokenizer, context allowance, cumulative exposure and sometimes environment. It supports ranking the measured pipelines on this test; it does not isolate inherent model quality under equal compute.

Validation questions are generated from training-source QA, whereas test questions are supplied independently and have a different distribution. Higher validation than test accuracy can reflect distribution and task-format differences. It is not by itself proof of overfitting. Conversely, gains on both sets do not prove absence of memorization or overfitting.

The later augmented data uses user-authorized as-generated acceptance. Semantic defects or source contradictions may remain. Technical uniqueness and context checks do not prove one defensible factual answer per question. The specific approved repairs should be disclosed in any comparison with the historical original MCQ control.

## 12. Artifact map and reproducibility

| Purpose | Local artifact |
|---|---|
| Original data / protected assessment | `TrainData.csv`, `TestData.csv`, `Finetune_Test.ipynb` |
| Historical baseline and QA outputs | `qwen25-coder-7b-20261113T053732139734Z/`, `results/history/` |
| Original MCQ train/validation | `data/mcq/generated-mcqs-final/` |
| Historical generation repairs | `data/mcq/manual-repaired-final/repair-audit.jsonl` |
| Q2 preserved adapter/evaluation | `results/latest-run/` |
| Q2 analysis and hashes | `analysis/kaggle-mcq-20261114/summary.json` |
| Q3 alignment artifacts | `mcq-alignment-20261115T044618514334Z/alignment/` |
| Variant provenance, approvals and policy | `data/mcq/augmentation/` |
| Final augmented input and manifest | `data/mcq/augmented-final/` |
| Main Qwen trainer / checkpoint callback | `finetune_qwen_mcq.py`, `mcq_checkpointing.py` |
| Manifest / generation merge | `mcq_augmentation.py`, `prepare_mcq_variants.py` |
| Q4 manual upload bundle | `Kaggle_MCQ_OneEpoch_ThreeCheckpoints.zip` |
| Q4 completed notebook | `notebook194c0310c8.ipynb` |
| OpenCoder runner / bundle builder | `opencoder_benchmark.py`, `.tools/build_opencoder_bundle.py` |
| OpenCoder manual upload bundle | `Kaggle_OpenCoder_Four_Arm_Benchmark.zip` |
| OpenCoder importable fixed notebook | `OpenCoder_Four_Arm_Benchmark_FIXED.ipynb` |
| OpenCoder partial logs | `output.txt` |
| Q5 prepared notebook / builder | `Qwen_MCQ_Fresh_Base_OneEpoch.ipynb`, `.tools/build_qwen_fresh_notebook.py` |
| Q5 tokenizer preflight | `data/mcq/augmentation/preflight-fresh-base-v1/` |

Artifact names can be historical: for example, `results/latest-run` still refers to Q2, not the newest user-reported Kaggle run. Use experiment IDs and provenance rather than assuming that a filename containing “latest” identifies the best/latest model.

Manual Kaggle datasets:

- Qwen augmented data: `mcq-1ep-3scores-1117-data` (private).
- OpenCoder comparison data: `opencoder-8b-four-arm-benchmark-data` (private).

Import the matching notebook, attach its dataset, enable GPU and Internet, and Save Version → Save & Run All. Existing resources are preserved; these manual bundles do not imply automatic publication or job launch by the agent. Never place credentials in notebooks or outputs.

For completed cloud runs, retain the result ZIP, metadata, exact scripts, input checksums, console logs, final adapters, all three checkpoint adapters, `checkpoint_scores.csv/json`, per-question predictions, summaries, loss plots and rotation diagnostics. Q4's final test is under `continuation/finetuned/test/summary.json`; OpenCoder's consolidated table is `comparison.csv/json`, with per-arm `test/summary.json` and predictions. The fresh Qwen output is under `fresh_training/finetuned/test/summary.json`.

## 13. Wrap-up and unresolved work

1. **Best recorded pipeline:** Qwen Q4 at 82.53% test and 95.83% validation. Its correct description is augmented continuation from Q2.
2. **Most consistent practical finding:** matching training targets to MCQ evaluation removes many invalid responses and improves measured accuracy for both model families.
3. **Unsupported stronger claims:** neither rotation-only benefit, augmentation-only benefit, exact KEFT reproduction, statistical significance nor equal-budget model superiority has been demonstrated.
4. **OpenCoder augmentation outcome:** stronger validation and rotated validation, but only one additional correct test answer over original MCQ training. A substantial test benefit is not established.
5. **No automatic new training is scheduled by this wrap-up.** The fresh-start Qwen notebook is a prepared follow-up, not a completed result.

If further work is chosen, priorities are to archive the full Q4/OpenCoder raw outputs and actual runtime metadata; run the already prepared Q5 only if the fresh-start question remains necessary; and use equal-exposure controls and multiple seeds before attributing gains to augmentation. Any new tuning should use validation, with a new untouched test cohort for stronger prospective claims.

Final unresolved evidence gaps: OpenCoder raw predictions/runtime metadata and checkpoint3 aggregate were not recovered locally; its QA checkpoint/final-reload discrepancy is unexplained; and Q5 has no GPU benchmark. These are explicitly missing values, not failed or zero-scoring experiments. Q4's adapter and rotated-validation summary were subsequently recovered from `final.zip`.

## 14. Apex Qwen Coder deployment preparation

The user created private Hugging Face Space `himath-nimpura/Apex-Qwen-Coder`.
The upload-ready app lives in [hf-space/](../hf-space/README.md), with MCQ mode
and experimental question-only QA mode. MCQ mode preserves the evaluated prompt
and parser. QA mode uses its own system instruction; the 82.53% score does not
apply to free-form QA.

The final Q4 adapter was staged from `final.zip`, after checking the final scores,
base revision, run metadata and successful reload record. Its weight SHA-256 is
`fb723545c82745a0a34f3ce1bf2103cac563fc97d706ddaa4134f52ba5499c5a`,
distinct from the older 78.07% starting adapter. The safetensors header contains
392 LoRA tensors. [model_manifest.json](../hf-space/model_manifest.json) binds the
adapter files to their provenance. No original QA/MCQ dataset or access tokens
are included in the upload package.

Six CPU contract/staging tests passed, and the real Gradio interface was built
in pending/ready states with GPU scheduling and model loading stubbed. Linux
Python3.12 dependency resolution succeeded. These are not live GPU inference
checks. Live short-request verification subsequently succeeded as recorded below;
maximum-context memory/latency and full benchmark parity remain unmeasured.

The initial direct upload attempt was blocked by session network restrictions
(`WinError10013`) before the existing Space's metadata could be retrieved.
No remote files, visibility, hardware or billing settings were changed by that attempt.
The upload helper is `.tools/publish_apex_space.py`; run it from a normal local
terminal with the existing Hugging Face credential store to complete publication.
The verified manual upload archive is `Apex-Qwen-Coder-Space.zip`.

### Live Space verification on 18 November 2026

An authenticated check from the Python3.12 client environment reached the deployed
private Space on ZeroGPU. The remote adapter weight hash matched the final Q4
adapter. Both initial inference calls failed. Runtime logs identified PEFT's
automatic CUDA safetensors load during startup, before ZeroGPU assigned a physical
GPU. The fix explicitly reads adapter tensors on CPU (`torch_device="cpu"`) before
PEFT copies them into the base model's emulated CUDA parameters. HTTP request
logging was reduced to avoid recording signed URLs.

Only `app.py` and `runtime.py` were changed in remote commit
`6ab3b902fe28e5644110a852731aa691030d28c9`. Weights, visibility, hardware and
billing configuration were unchanged. The new revision reached RUNNING and
enabled both inference-mode buttons.

| Live check | Observed result | Model generation time | Client wall time |
|---|---|---:|---:|
| Synthetic Unity physics MCQ | B / Rigidbody, correct; `Answer:b` | 0.889 s | 9.11 s |
| QA with supplied `moveSpeed = 6f` code | Correctly answered 6.0, not a choice letter | 2.284 s | 4.77 s |
| Question-only QA: `Time.deltaTime` | Correctly explained elapsed frame time in seconds and frame-rate-independent logic | 2.163 s | 8.86 s |

None reached its generation-token budget. These are three live functional smoke
checks, not a measured QA accuracy estimate or a fresh 269-question test run.
The recorded 82.53% MCQ test score remains the Kaggle experiment result.

Reports: [two-mode smoke](results/space-smoke-after-startup-fix.json),
[question-only QA](results/space-question-only.json), and
[fix receipt](results/space-startup-fix.json).
