# qwen-coder notebooks

| Notebook | Purpose / status |
|---|---|
| [01_zero_shot.ipynb](01_zero_shot.ipynb) | Runnable baseline notebook; historical Qwen2.5 score 67.66% |
| [02_original_qa.ipynb](02_original_qa.ipynb) | Original QA experiment; historical test 42.75% |
| [03_original_mcq_rotations.ipynb](03_original_mcq_rotations.ipynb) | Four rotations; recorded test 78.07%, validation 94.79% |
| [04_alignment.ipynb](04_alignment.ipynb) | Simplified alignment; recorded test 77.32% |
| [05_augmented_continuation.ipynb](05_augmented_continuation.ipynb) | Warm start from original MCQ adapter; recorded test 82.53% |
| [06_augmented_fresh_base.ipynb](06_augmented_fresh_base.ipynb) | Prepared fresh-base comparison; no GPU results reported |
| [diagnostics/memory_smoke_tests.ipynb](diagnostics/memory_smoke_tests.ipynb) | GPU memory diagnostics; not a benchmark result |
| [07_model_demo.ipynb](07_model_demo.ipynb) | Final 82.53% adapter; MCQ and experimental QA demo; no training |

Runnable copies have outputs cleared; their training code and cloud input requirements are preserved. They do not automatically consume the new JSON exports. Kaggle notebooks still need their matching private input dataset; Colab notebooks retain their original data setup. For the current final-model demo, use `qwen-coder/07_model_demo.ipynb`.

## Historical saved outputs

- [completed/zero_shot_executed.ipynb](completed/zero_shot_executed.ipynb) — byte-identical historical saved copy.
- [completed/original_qa_executed.ipynb](completed/original_qa_executed.ipynb) — byte-identical historical saved copy.
- [completed/augmented_continuation_executed.ipynb](completed/augmented_continuation_executed.ipynb) — byte-identical historical saved copy.

See [the canonical experiment history](../../full-experiment-workflow.md) for provenance, budgets and comparison limits.
