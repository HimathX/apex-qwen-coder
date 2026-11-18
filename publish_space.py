"""Upload the completed app/model to the named existing private HF Space."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SPACE = ROOT / "space"
sys.path.insert(0, str(SPACE))
from inference_contract import verify_adapter


def main():
    verify_adapter(SPACE)
    from huggingface_hub import HfApi, get_token
    if not get_token():
        raise RuntimeError("Authenticate locally with `hf auth login`; never put tokens in source or chat")
    repo_id = "himath-nimpura/Apex-Qwen-Coder"
    api = HfApi()
    info = api.space_info(repo_id)
    if info.private is not True:
        raise ValueError("The existing Space must remain private; no upload attempted")
    result = api.upload_folder(repo_id=repo_id, repo_type="space", folder_path=str(SPACE),
        allow_patterns=["app.py", "runtime.py", "inference_contract.py", "requirements.txt", "README.md", "LICENSE",
            ".gitignore", "model_manifest.json", "adapter/adapter_config.json", "adapter/adapter_model.safetensors"],
        commit_message="Add verified final Qwen adapter with MCQ and experimental QA modes",
        parent_commit=info.sha)
    print(f"Uploaded private Space: https://huggingface.co/spaces/{repo_id}")
    print(f"Commit: {result.oid}")
    print("Hardware and visibility unchanged. Check the build logs and test both modes before declaring deployment ready.")


if __name__ == "__main__":
    main()
