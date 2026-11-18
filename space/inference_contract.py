"""Prompts and artifact checks for the evaluated Qwen continuation adapter."""
import hashlib
import json
from pathlib import Path
import re

BASE_MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"
BASE_REVISION = "c03e6d358207e414f1eca0bb1891e29f1db0e242"
OLD_ADAPTER_SHA256 = "11ccee4e737ddadc11258d5e3ac6820b82804036a7ca3b3f05ae45c4c44f9f95"
RUN_ID = "mcq-augmentation-20261117T051401617175Z"
QA_SYSTEM_PROMPT = (
    "You are a technical assistant for a particular Unity C# game project. "
    "Answer the user's question directly in plain language, using C# code when useful. "
    "Do not output an MCQ choice letter when no choices are supplied. "
    "Distinguish project-specific facts from general Unity guidance. "
    "Use any context supplied by the user as evidence. If you do not know a "
    "project-specific detail, say that you are unsure and ask for the relevant code. "
    "Do not invent identifiers, event names, constants, or project behavior."
)


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Enter {name}.")
    return value


def mcq_messages(question, a, b, c, d):
    question = require_text(question, "a question")
    options = dict(zip("abcd", [a, b, c, d]))
    for letter, option in options.items():
        require_text(option, f"option {letter.upper()}")
    if len({v.strip() for v in options.values()}) != 4:
        raise ValueError("The four choices must be distinct.")
    choices = "\n".join(f"{key}) {options[key]}" for key in "abcd")
    # Exact evaluated prompt. Do not add a different system instruction in MCQ mode.
    prompt = (
        "Answer the following multiple-choice question about a Unity C# game project.\n"
        "Choose the single best answer. End your response with Answer:a, Answer:b, "
        "Answer:c, or Answer:d.\n\n"
        f"{question}\n{choices}"
    )
    if len(prompt) > 32000:
        raise ValueError("The question and choices are too long. Shorten them and try again.")
    return [{"role": "user", "content": prompt}]


def qa_messages(question, context=""):
    question = require_text(question, "a question")
    context = context or ""
    if len(question) + len(context) > 24000:
        raise ValueError("The question and context are too long. Shorten them and try again.")
    content = f"Project context supplied by the user:\n{context}\n\nQuestion:\n{question}" if context.strip() else question
    return [{"role": "system", "content": QA_SYSTEM_PROMPT}, {"role": "user", "content": content}]


def parse_answer(response):
    if "<think>" in response and "</think>" not in response:
        return None
    final = response.rsplit("</think>", 1)[-1].strip()
    match = re.search(r"Answer\s*:\s*([abcd])\s*[.!]?\s*$", final, re.I)
    if match:
        return match.group(1).lower()
    return final.lower() if re.fullmatch(r"[abcd]", final, re.I) else None


def verify_adapter(root):
    """Fail closed if the final adapter is missing, altered, or an older adapter."""
    root = Path(root)
    manifest_path = root / "model_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError("The final trained adapter has not been installed yet.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("base_model") != BASE_MODEL or manifest.get("base_revision") != BASE_REVISION:
        raise ValueError("The deployed model does not match the pinned evaluated Qwen model.")
    if manifest.get("run_id") != RUN_ID:
        raise ValueError("The adapter is from a different experiment.")
    for filename in ("adapter_config.json", "adapter_model.safetensors"):
        path = root / "adapter" / filename
        expected = manifest.get("sha256", {}).get(filename)
        if not expected or not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"Missing or changed trained adapter file: {filename}")
    if manifest["sha256"]["adapter_model.safetensors"] == OLD_ADAPTER_SHA256:
        raise ValueError("This is the older 78.07% starting adapter, not the final 82.53% adapter.")
    if manifest.get("test", {}).get("correct") != 222 or manifest.get("test", {}).get("questions") != 269:
        raise ValueError("Final test provenance does not match the requested model.")
    if manifest.get("validation", {}).get("correct") != 184 or manifest.get("validation", {}).get("questions") != 192:
        raise ValueError("Final validation provenance does not match the requested model.")
    config = json.loads((root / "adapter/adapter_config.json").read_text(encoding="utf-8"))
    if config.get("base_model_name_or_path") != BASE_MODEL or config.get("peft_type") != "LORA":
        raise ValueError("Unexpected adapter base or format.")
    if config.get("r") != 16 or config.get("lora_alpha") != 32:
        raise ValueError("Unexpected LoRA configuration.")
    return manifest
