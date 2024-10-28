# Use the NVIDIA CUDA base image with Ubuntu 22.04
FROM nvidia/cuda:12.6.0-cudnn-runtime-ubuntu22.04

# Set environment variables
ENV PATH="/opt/conda/bin:$PATH"

# Install dependencies, Miniconda, and ffmpeg
RUN apt-get update && \
    apt-get install -y wget bzip2 ffmpeg git && \
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Update conda and Python packages
RUN conda update -n base -c defaults conda && \
    conda install python=3.9 -y && \
    conda clean -a -y

# Set default shell to bash
SHELL ["/bin/bash", "-c"]

WORKDIR /app

RUN conda create -n whisperx python=3.10 -y
SHELL ["conda", "run", "-n", "whisperx", "/bin/bash", "-c"]

RUN conda install pytorch==2.0.0 torchaudio==2.0.0 pytorch-cuda=11.8 -c pytorch -c nvidia -y
RUN pip install git+https://github.com/m-bain/whisperx.git -q
RUN pip install pyannote.audio==3.1.0 -q
RUN pip uninstall -y onnxruntime
RUN pip install --force-reinstall onnxruntime-gpu -q
RUN pip install -U torch torchaudio -q
RUN pip install numpy==1.26.4 -q
RUN pip install nvidia-cudnn-cu12==8.9.7.29 -q
RUN pip install ctranslate2==4.4.0 -q
RUN conda install fastapi uvicorn python-multipart -y

COPY . .

RUN apt-get update && \
    apt-get install -y libcudnn8 libcudnn8-dev

WORKDIR /app/api

EXPOSE 8080

CMD ["bash", "-c", "source activate whisperx && uvicorn main:app --host 0.0.0.0 --port 8080"]