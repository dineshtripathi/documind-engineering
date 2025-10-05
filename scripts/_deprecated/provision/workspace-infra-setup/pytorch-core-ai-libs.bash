# GPU PyTorch (CUDA 12.1)
conda install -y -c pytorch -c nvidia pytorch pytorch-cuda=12.1

# Core libs
pip install --upgrade pip
pip install "transformers>=4.43" "accelerate>=0.30" \
            "sentence-transformers>=3.0" "qdrant-client>=1.9" \
            "fastapi>=0.111" "uvicorn[standard]>=0.30" \
            "httpx>=0.27" "pydantic>=2.8" \
            "numpy" "pandas" "scikit-learn" "tiktoken" "python-dotenv" \
            "huggingface_hub>=0.24" "hf-transfer>=0.1"
