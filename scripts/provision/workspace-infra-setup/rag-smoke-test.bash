# add at the top of any script before `conda activate`
#!/usr/bin/env bash
set -e
source ~/miniconda3/etc/profile.d/conda.sh
conda activate documind
export OLLAMA_URL=${OLLAMA_URL:-http://127.0.0.1:11435}  # if you’re on 11435
python rag_smoketest.py
