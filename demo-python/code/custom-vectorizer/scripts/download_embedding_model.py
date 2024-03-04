import os
import subprocess

model_parent_dir_name = 'api/functions/models'
default_embedding_model = 'sentence-transformers/all-MiniLM-L6-v2'
model_env_var = 'SENTENCE_TRANSFORMERS_TEXT_EMBEDDING_MODEL'

def main():
    if model_env_var not in os.environ:
        print(f"Using default embedding model{default_embedding_model}")
        subprocess.run(f"azd env set {model_env_var} {default_embedding_model}", shell=True)

    model_parent_dir = os.path.join(os.getcwd(), model_parent_dir_name)
    # Check if the directory exists
    if not os.path.exists(model_parent_dir):
        # If it doesn't exist, create it
        os.makedirs(model_parent_dir)

    # Check if model is already downloaded
    model_name = os.getenv(model_env_var, default_embedding_model)
    model_dir = os.path.join(model_parent_dir, model_name)
    if os.path.exists(model_dir):
        print(f"Model {model_name} already downloaded")
        return

    # Initialize and download the model
    print(f"Downloading {model_name}...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    model.save(model_dir)

if __name__ == "__main__":
    main()
