# Apex Qwen Coder — Unity/C# project MCQ fine-tuning

Fine-tuning experiments that teach 7–8B code models to answer multiple-choice
questions about a Unity/C# game project, plus the deployed demo app.

Start here for the data, model-family notebooks, final model demo and Space app.
This folder is a clean collection; historical source artifacts in the parent
workspace have not been moved, deleted, retrained or rewritten.

## Results at a glance

Best measured pipeline: **Qwen2.5-Coder-7B-Instruct**, original MCQ fine-tuning
followed by one augmented-continuation epoch.

| Experiment | Model | Validation | Test |
|---|---|---:|---:|
| Untuned baseline | Qwen2.5-Coder-7B | — | 182/269 (67.66%) |
| Original MCQs | Qwen2.5-Coder-7B | 182/192 (94.79%) | 210/269 (78.07%) |
| **+ augmented continuation** | **Qwen2.5-Coder-7B** | **184/192 (95.83%)** | **222/269 (82.53%)** |
| Untuned baseline | OpenCoder-8B | 60/192 (31.25%) | 137/269 (50.93%) |
| Original MCQs | OpenCoder-8B | 159/192 (82.81%) | 193/269 (71.75%) |
| Augmented MCQs | OpenCoder-8B | 167/192 (86.98%) | 194/269 (72.12%) |

These are single-seed descriptive results on a fixed 269-question test set that
has been evaluated repeatedly during the project, so it is no longer an untouched
holdout. See [full-experiment-workflow.md](full-experiment-workflow.md) for the
complete ledger, training budgets and stated limitations.

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

CUDA builds of PyTorch must be installed for your own toolkit version; the pinned
Transformers/PEFT/bitsandbytes versions are the ones recorded for the experiments.
Run training and evaluation notebooks on a CUDA GPU.

### Model weights

The 154 MB final adapter is not committed. Download it from the private Hugging
Face Space `himath-nimpura/Apex-Qwen-Coder` into `space/adapter/`, then verify the
SHA-256 matches `space/model_manifest.json`:

```powershell
huggingface-cli download himath-nimpura/Apex-Qwen-Coder adapter/adapter_model.safetensors --local-dir space
```

The app refuses to load missing, changed or older weights.

## Layout

```text
data/
  original_qa/all.json         1,910 original QA records with split/admission metadata
  original_qa/train.json       1,717 admitted training QA records
  mcq/set_1.json               1,717 original MCQs with approved corrections applied
  mcq/variants.json            3,434 new MCQs: variant_id 1 and 2
  evaluation/validation.json   192 held-out validation MCQs
  evaluation/test.json         269 original test MCQs
  manifest.json                counts, source hashes, output hashes and policies
notebooks/
  qwen/                        Qwen3 baseline
  qwen-coder/                  Qwen2.5-Coder training, saved results and final-model demo
  opencoder/                   OpenCoder independent four-arm benchmark
space/                         upload-ready Apex Qwen Coder app (adapter downloaded separately)
results/                       saved Space verification reports
publish_space.py               publishes only to the existing private Space
full-experiment-workflow.md    complete measured results and their limitations
requirements.txt               training and evaluation dependencies
```

## Which files to use

- For original QA **training**, use [train.json](data/original_qa/train.json).
  [all.json](data/original_qa/all.json) includes held-out QA records and must not
  be used wholesale for training. Original `class`, `Q`, and `A` strings are preserved.
- For original-MCQ training, use [set_1.json](data/mcq/set_1.json). This contains
  the active corrected variant0 on the admitted 1,717 sources, rather than the
  historical 1,718-row CSV. Source1817 was excluded for the training context limit.
- For augmented training, concatenate `set_1.json` with [variants.json](data/mcq/variants.json):
  5,151 MCQs. `source_row` maps to zero-based original QA records;
  `(source_row, variant_id)` uniquely identifies each MCQ.
- Keep [validation](data/evaluation/validation.json) and [test](data/evaluation/test.json)
  separate from all training. JSON exports preserve parsed CSV values and order.
- The variants were accepted as supplied under the user's no-semantic-review
  instruction. This organization does not add review or change answers.

These are UTF-8 JSON arrays, not JSONL files. Original QA Q/A and MCQ code text
are not stripped or paraphrased. No `repairs.json` is duplicated here. Historical
approval records remain in the parent workspace and are referenced by the
canonical experiment history.

## Demo and deployment

Open [Qwen_Model_Demo](notebooks/qwen-coder/07_model_demo.ipynb) in a CUDA GPU
runtime for MCQ mode and experimental direct QA. It reuses `space/` code and
the final adapter; it does not train or automatically publish anything.

Best measured model: Qwen2.5-Coder-7B augmented continuation, **222/269 (82.53%)
test / 184/192 (95.83%) validation**. It starts from the original MCQ adapter;
the separate fresh-base experiment has no reported GPU result.

The final adapter has SHA-256
`fb723545c82745a0a34f3ce1bf2103cac563fc97d706ddaa4134f52ba5499c5a`; it is
downloaded into `space/adapter/` as described above rather than committed.
The app verifies its manifest before loading and does not fall back to older weights.

Publish using a normal authenticated terminal:

```powershell
python publish_space.py
```

The target is existing private Space `himath-nimpura/Apex-Qwen-Coder`. The helper
does not change hardware, visibility or billing. The deployed private app passed
MCQ, contextual QA and question-only QA smoke tests on ZeroGPU on 18 November.
Reports are retained under [results/](results/). Use a dedicated CUDA GPU for
the local notebook demo. QA mode is experimental;
the MCQ accuracy does not describe question-only answers.

See [Qwen](notebooks/qwen/README.md), [Qwen Coder](notebooks/qwen-coder/README.md),
[OpenCoder](notebooks/opencoder/README.md), and the
[canonical experiment history](full-experiment-workflow.md) for notebook status.

## Provenance

This repository is the clean collection built from a larger research workspace
by `.tools/build_organized_workspace.py`, which checks counts, source isolation,
variant identity, exact text-value preservation and unchanged original inputs.
Historical source artifacts, training CSVs, generation audits and adapter
archives remain in that parent workspace; they are not committed here. The
builder clears outputs only in runnable copies, so `completed/` notebooks retain
their original saved output bytes.

## License

Code and documentation are Apache-2.0 ([LICENSE](LICENSE)). The upstream Qwen
and OpenCoder models keep their own licenses. No additional license to the
original training source data is granted.
