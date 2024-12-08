# Start with a Python 3.9 base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /gemma

# Copy the current directory contents into the container at /app
COPY . .

# Install necessary build tools and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install llama-cpp-python using pre-built wheels
RUN pip install --no-cache-dir llama-cpp-python==0.3.2 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124

# Define the local model path
ENV LOCAL_MODEL_PATH=/app/gemma_model/gemma-2-2b-it-Q6_K_L.gguf

# Run the download script to ensure the model is downloaded
RUN python download_model.py

# Expose the port for the Flask application
EXPOSE 8000

# Set the entry point to run the Flask application
CMD ["python", "gemma_api.py"]