---
title: Apex Qwen Coder
emoji: 🧑‍💻
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.0.2
python_version: 3.12
app_file: app.py
pinned: false
license: apache-2.0
short_description: Unity C# MCQ assistant with experimental question-only QA
models:
  - Qwen/Qwen2.5-Coder-7B-Instruct
tags:
  - unity
  - csharp
  - peft
  - zerogpu
---

# Apex Qwen Coder

Private Space: `himath-nimpura/Apex-Qwen-Coder`.

Two modes share the final augmented-continuation adapter:

- **MCQ mode** uses the exact evaluated prompt, greedy decoding and 128-token
  response limit. It returns the selected letter, its option text and raw response.
- **QA mode** uses a separate system instruction and 256-token limit for direct
  explanations, optionally grounded in user-supplied project code. It is experimental;
  switching the prompt does not establish question-only accuracy.

The final Kaggle model recorded **222/269 (82.53%) test** and **184/192 (95.83%)
validation**. Its training history is original MCQ fine-tuning followed by one
additional epoch over originals plus two variants per admitted source. These are
MCQ benchmark scores, not QA scores or a guarantee of deployment accuracy.

## Included final adapter

This organized copy already includes `adapter/` and `model_manifest.json`.
They were verified against the completed Kaggle continuation run in `final.zip`:
222/269 test and 184/192 validation. Model weights SHA-256:
`fb723545c82745a0a34f3ce1bf2103cac563fc97d706ddaa4134f52ba5499c5a`.

The app downloads the public Qwen base at pinned revision
`c03e6d358207e414f1eca0bb1891e29f1db0e242` and loads this final adapter.
It verifies the manifest and refuses missing, changed or older weights.
No original QA/MCQ training data, access tokens, starting adapter or smoke
checkpoint is included in this Space folder.

## Hardware and runtime

Select **ZeroGPU** in the Space hardware settings. The app imports `spaces`
before CUDA-related modules, loads the NF4 model and PEFT adapter at module scope
with `device_map="cuda"`, and decorates the actual Gradio handlers with
`@spaces.GPU`. GPU reservation is initially 60 seconds per call; generation time
is returned in response details so this can be adjusted after live measurements.

The same app can use an ordinary dedicated CUDA GPU; the decorator is a no-op
outside ZeroGPU. It does not attempt to run this 7B model on CPU Basic. Hardware
selection is manual; this repository does not activate paid hardware or billing.

The inference stack is pinned to Transformers4.57.3/PEFT0.17.1/bitsandbytes0.48.2
and torch2.8.0. This differs from the evaluated Kaggle torch2.11.0 runtime.
Recheck representative MCQs after deployment; identical weights and prompts do
not establish identical scores across hardware/software versions.

## Publish from a local authenticated environment

```powershell
hf auth login
python organized/publish_space.py
```

Keep the token in the HF credential store, never source files or chat. The helper
only updates the named existing private Space and refuses to proceed without a
verified final adapter. It never changes visibility or paid hardware.

If CLI network access is blocked, upload the same folder using the Space's
**Files → Add file → Upload files** interface.

## Validation status

The final adapter has now been staged from local `final.zip`. Verified weights
SHA-256: `fb723545c82745a0a34f3ce1bf2103cac563fc97d706ddaa4134f52ba5499c5a`.
The ZIP's final summaries confirm 222/269 test, 184/192 fixed validation, and
724/768 (94.27%) rotated validation. The adapter differs from the older Q2
starting adapter. These verify artifact selection, not a new inference run.

Local tests cover prompt/parser parity with the benchmark, mode separation,
selection-to-option mapping, rejection of missing/wrong adapters, and staging
provenance and CPU adapter-file loading for ZeroGPU. All six contract/staging
unit tests passed. The Gradio UI was checked with model/GPU loading stubbed.

Live ZeroGPU checks passed on 18 November 2026 at commit
`6ab3b902fe28e5644110a852731aa691030d28c9`: MCQ selected B/Rigidbody;
contextual QA read moveSpeed=6.0; question-only QA correctly explained
Time.deltaTime. Generation times were 0.889s, 2.284s and 2.163s respectively.
Client wall times, including scheduling/network overhead, were 9.11s, 4.77s and
8.86s. Model load and these short requests worked on ZeroGPU; maximum-context
memory fit and full benchmark parity were not measured. These smoke tests do
not establish broad QA accuracy or replace the recorded MCQ benchmark.

Relevant references:

- https://huggingface.co/docs/hub/spaces-zerogpu
- https://github.com/huggingface/skills/blob/main/skills/huggingface-spaces/references/zerogpu.md
- https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct

## License and scope

App code is Apache-2.0. The upstream Qwen model uses Apache-2.0; retain its
license and notices. No additional license to the original training source data
is granted by this app. Questions are used for inference, with no application
chat-history persistence. The hosting service may retain its own operational logs.
