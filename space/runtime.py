"""Quantized inference; app.py imports spaces before this module."""
import importlib.metadata
import logging
from pathlib import Path
import time

from inference_contract import BASE_MODEL, BASE_REVISION, parse_answer, verify_adapter

LOGGER = logging.getLogger(__name__)


def load_adapter_for_inference(base, path):
    from peft import PeftModel
    # ZeroGPU has no real CUDA device during startup. Read safetensors on CPU;
    # PEFT then copies weights into the base model's emulated CUDA parameters.
    return PeftModel.from_pretrained(base, str(path), is_trainable=False, torch_device="cpu").eval()


class ModelRuntime:
    def __init__(self, root):
        self.root = Path(root)
        self.model = None
        self.tokenizer = None
        self.manifest = None
        self.problem = "The final trained adapter has not been installed yet."

    def load(self):
        # Called at module scope for ZeroGPU CUDA placement and startup packing.
        self.manifest = verify_adapter(self.root)
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        quantization = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16)
        self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, revision=BASE_REVISION)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, revision=BASE_REVISION,
            dtype=torch.float16, quantization_config=quantization,
            device_map="cuda", attn_implementation="sdpa")
        self.model = load_adapter_for_inference(base, self.root / "adapter")
        self.model.config.use_cache = True
        self.problem = None
        versions = {name: importlib.metadata.version(name) for name in
                    ("torch", "transformers", "peft", "bitsandbytes", "gradio", "spaces")}
        LOGGER.info("Loaded pinned final adapter; runtime versions=%s", versions)

    @property
    def ready(self):
        return self.model is not None and self.tokenizer is not None and self.problem is None

    def generate(self, messages, max_new_tokens):
        if not self.ready:
            raise RuntimeError("The model is not ready. Ask the Space owner to finish installing it.")
        import torch
        started = time.perf_counter()
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(text, add_special_tokens=False, return_tensors="pt")
        prompt_tokens = int(inputs.input_ids.shape[-1])
        if prompt_tokens > 4096:
            raise ValueError("This input exceeds 4,096 tokens. Shorten the question or context.")
        if prompt_tokens + max_new_tokens > self.model.config.max_position_embeddings:
            raise ValueError("This input leaves insufficient model context for an answer.")
        inputs = inputs.to("cuda")
        with torch.inference_mode():
            output = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id)
        new_ids = output[0, prompt_tokens:]
        response = self.tokenizer.decode(new_ids, skip_special_tokens=True).strip()
        return response, {"prompt_tokens": prompt_tokens, "generated_tokens": len(new_ids),
            "token_budget_reached": len(new_ids) >= max_new_tokens,
            "seconds": round(time.perf_counter() - started, 3)}


def answer_mcq(runtime, messages, options):
    response, details = runtime.generate(messages, 128)
    letter = parse_answer(response)
    details.update(raw_response=response, valid_answer=letter is not None)
    if letter is None:
        return "No valid choice returned", "The response did not match the required answer format. Try rewording the question.", details
    return letter.upper(), options["abcd".index(letter)], details


def answer_qa(runtime, messages):
    response, details = runtime.generate(messages, 256)
    details["mcq_style_response"] = parse_answer(response) is not None
    if details["mcq_style_response"]:
        response += "\n\nThe model returned an MCQ-style answer without choices. Question-only mode is experimental; try supplying four options or relevant project code."
    return response or "No answer was generated. Try adding relevant project context.", details
