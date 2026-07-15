import json
import os
import shutil
import subprocess
from huggingface_hub import snapshot_download

model_parent_dir_name = 'api/functions/models'
default_embedding_model = 'sentence-transformers/all-MiniLM-L6-v2'
model_env_var = 'SENTENCE_TRANSFORMERS_TEXT_EMBEDDING_MODEL'
model_weight_files = ["model.safetensors", "pytorch_model.bin"]
model_weight_index_files = ["model.safetensors.index.json", "pytorch_model.bin.index.json"]

def has_complete_sharded_weights(model_dir):
    for index_name in model_weight_index_files:
        index_path = os.path.join(model_dir, index_name)
        if not os.path.isfile(index_path):
            continue
        try:
            with open(index_path, encoding="utf-8") as index_file:
                shards = set(json.load(index_file).get("weight_map", {}).values())
        except (OSError, ValueError):
            continue
        if shards and all(os.path.isfile(os.path.join(model_dir, shard)) for shard in shards):
            return True
    return False

def is_complete_model(model_dir):
    has_config = os.path.isfile(os.path.join(model_dir, "config.json"))
    has_weights = (
        any(os.path.isfile(os.path.join(model_dir, path)) for path in model_weight_files)
        or has_complete_sharded_weights(model_dir)
    )
    return has_config and has_weights

def main():
    if model_env_var not in os.environ:
        print(f"Using default embedding model {default_embedding_model}")
        azd_path = shutil.which("azd.cmd") or shutil.which("azd.exe") or shutil.which("azd")
        if not azd_path:
            raise RuntimeError("Azure Developer CLI (azd) was not found on PATH.")
        subprocess.run(
            [azd_path, "env", "set", model_env_var, default_embedding_model],
            check=True,
        )

    model_parent_dir = os.path.join(os.getcwd(), model_parent_dir_name)
    # Check if the directory exists
    if not os.path.exists(model_parent_dir):
        # If it doesn't exist, create it
        os.makedirs(model_parent_dir)

    # Check if model is already downloaded
    model_name = os.getenv(model_env_var, default_embedding_model)
    model_dir = os.path.join(model_parent_dir, model_name)
    if is_complete_model(model_dir):
        print(f"Model {model_name} already downloaded")
        return

    staging_dir = f"{model_dir}.download"
    shutil.rmtree(model_dir, ignore_errors=True)
    shutil.rmtree(staging_dir, ignore_errors=True)

    print(f"Downloading {model_name}...")
    try:
        snapshot_download(
            repo_id=model_name,
            local_dir=staging_dir,
            local_dir_use_symlinks=False,
            allow_patterns=["*.json", "*.txt", "*.model", "*.safetensors"],
        )
        if not is_complete_model(staging_dir):
            snapshot_download(
                repo_id=model_name,
                local_dir=staging_dir,
                local_dir_use_symlinks=False,
                allow_patterns=["*.bin"],
            )
        if not is_complete_model(staging_dir):
            raise RuntimeError(f"Downloaded model {model_name} is incomplete.")
        os.makedirs(os.path.dirname(model_dir), exist_ok=True)
        os.replace(staging_dir, model_dir)
    except Exception:
        shutil.rmtree(staging_dir, ignore_errors=True)
        raise

if __name__ == "__main__":
    main()
