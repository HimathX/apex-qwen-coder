"""Apex Qwen Coder: MCQ answering and experimental direct QA on ZeroGPU."""
import os

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "false")
import spaces  # Must precede CUDA-touching imports on ZeroGPU.

import logging
from pathlib import Path
import gradio as gr

from inference_contract import mcq_messages, qa_messages
from runtime import ModelRuntime, answer_mcq, answer_qa

logging.basicConfig(level=logging.INFO)
ROOT = Path(__file__).resolve().parent
runtime = ModelRuntime(ROOT)
if (ROOT / "model_manifest.json").exists():
    try:
        runtime.load()
    except Exception as error:
        logging.exception("Model startup failed")
        runtime.problem = "Model startup failed. The Space owner can check the runtime logs."


@spaces.GPU(duration=60)
def solve_mcq(question, a, b, c, d):
    try:
        return answer_mcq(runtime, mcq_messages(question, a, b, c, d), [a, b, c, d])
    except (ValueError, RuntimeError) as error:
        raise gr.Error(str(error)) from None


@spaces.GPU(duration=60)
def solve_qa(question, context):
    try:
        return answer_qa(runtime, qa_messages(question, context))
    except (ValueError, RuntimeError) as error:
        raise gr.Error(str(error)) from None


def create_demo():
    with gr.Blocks(title="Apex Qwen Coder") as demo:
        gr.Markdown("# Apex Qwen Coder\nYour Unity C# project assistant.")
        if runtime.ready:
            gr.Markdown("**MCQ benchmark:** 82.53% test (222/269), 95.83% validation (184/192). "
                "These recorded scores apply to the evaluated MCQ format, not question-only answers.")
        else:
            gr.Markdown(f"**Setup pending:** {runtime.problem}")
        with gr.Tab("MCQ mode"):
            gr.Markdown("Enter a question and four choices. The model selects the single best answer.")
            question = gr.Textbox(label="Question", lines=3, placeholder="Ask about the Unity project…")
            with gr.Row():
                with gr.Column():
                    a = gr.Textbox(label="A", lines=3)
                    b = gr.Textbox(label="B", lines=3)
                with gr.Column():
                    c = gr.Textbox(label="C", lines=3)
                    d = gr.Textbox(label="D", lines=3)
            solve = gr.Button("Choose an answer", variant="primary", interactive=runtime.ready)
            choice = gr.Textbox(label="Selected choice", interactive=False)
            answer = gr.Textbox(label="Selected answer", lines=5, interactive=False)
            with gr.Accordion("Response details", open=False):
                details = gr.JSON(label="Generation details")
            solve.click(solve_mcq, inputs=[question, a, b, c, d], outputs=[choice, answer, details],
                api_name="mcq", concurrency_id="inference", concurrency_limit=1)
        with gr.Tab("QA mode"):
            gr.Markdown("**Experimental:** ask a question without choices. "
                "This adapter was trained on MCQs, so direct answers can be unreliable. "
                "Add relevant project code when possible and verify project-specific claims.")
            qa_question = gr.Textbox(label="Question", lines=3, placeholder="What would you like to know?")
            with gr.Accordion("Optional project context", open=False):
                context = gr.Textbox(label="Relevant code or project details", lines=7)
            ask = gr.Button("Ask Apex", variant="primary", interactive=runtime.ready)
            qa_answer = gr.Textbox(label="Answer", lines=14, interactive=False)
            with gr.Accordion("Response details", open=False):
                qa_details = gr.JSON(label="Generation details")
            ask.click(solve_qa, inputs=[qa_question, context], outputs=[qa_answer, qa_details],
                api_name="qa", concurrency_id="inference", concurrency_limit=1)
        gr.Markdown("A fine-tuned Qwen2.5-Coder-7B-Instruct adapter for this Unity project. "
            "Questions are processed to generate a response; this app does not save a question history.")
    return demo.queue(max_size=12, default_concurrency_limit=1)


demo = create_demo()
if __name__ == "__main__":
    demo.launch(show_error=False)
