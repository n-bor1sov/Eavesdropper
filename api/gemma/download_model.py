import os
from huggingface_hub import hf_hub_download

# Specify the repository ID and the filename you want to download
repo_id = "bartowski/gemma-2-2b-it-GGUF"
filename = "gemma-2-2b-it-Q6_K_L.gguf"
cache_dir = "/gemma/gemma_model"

# Local path to the model file
local_model_path = os.path.join(cache_dir, filename)

# Check if the model file already exists locally
if not os.path.exists(local_model_path):
    print(f"Model file not found at {local_model_path}. Downloading from Hugging Face...")
    # Download the file to the local directory
    local_model_path = hf_hub_download(repo_id=repo_id, filename=filename, cache_dir=cache_dir)
    print(f"Model downloaded to: {local_model_path}")
else:
    print(f"Model file already exists at {local_model_path}. Skipping download.")