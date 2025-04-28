# ---------- Dockerfile -------------------------------------------------------
FROM python:3.11-slim

# 0. create workdir and copy code
WORKDIR /app
COPY . .

# 1. install Python deps + huggingface-hub CLI
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt "huggingface_hub[cli]>=0.22"

# 2. download DistilBERT (4 files) into /app/models/distilbert-sst2
RUN huggingface-cli download \
        distilbert/distilbert-base-uncased-finetuned-sst-2-english \
        --local-dir /app/models/distilbert-sst2 \
        --local-dir-use-symlinks False \
        --include "pytorch_model.bin" "config.json" "tokenizer.json" "vocab.txt" \
    && rm -rf ~/.cache/huggingface

# 3. make Transformers work strictly offline
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HOME=/app/models/.cache

EXPOSE 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false"]