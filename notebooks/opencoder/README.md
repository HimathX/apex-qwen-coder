# opencoder notebooks

| Notebook | Purpose / status |
|---|---|
| [01_four_arm_benchmark.ipynb](01_four_arm_benchmark.ipynb) | Independent base / QA / original MCQ / augmented MCQ arms; best test 72.12% |

Runnable copies have outputs cleared; their training code and cloud input requirements are preserved. They do not automatically consume the new JSON exports. Kaggle notebooks still need their matching private input dataset; Colab notebooks retain their original data setup. For the current final-model demo, use `qwen-coder/07_model_demo.ipynb`.

## Final reported results

| Setup | Validation | Test | Test correct | Invalid test answers |
|---|---:|---:|---:|---:|
| Base | 31.25% | 50.93% | 137/269 | 61 |
| QA | 11.98% | 19.70% | 53/269 | 194 |
| Original MCQ | 82.81% | 71.75% | 193/269 | 0 |
| Augmented MCQ | 86.98% | 72.12% | 194/269 | 0 |

These final aggregates were supplied by the user; no completed OpenCoder notebook with all final outputs was supplied.

See [the canonical experiment history](../../full-experiment-workflow.md) for provenance, budgets and comparison limits.
