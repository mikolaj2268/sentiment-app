FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y build-essential gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt "huggingface_hub[cli]>=0.22"

# Download the HuggingFace model during build using huggingface_hub
RUN mkdir -p /app/models/distilbert-sst2
RUN python -c 'from huggingface_hub import snapshot_download; \
    snapshot_download( \
        repo_id="distilbert/distilbert-base-uncased-finetuned-sst-2-english", \
        local_dir="/app/models/distilbert-sst2", \
        local_dir_use_symlinks=False, \
        allow_patterns=["pytorch_model.bin", "config.json", "tokenizer.json", "vocab.txt"] \
    ); \
    print("✅ Model successfully downloaded")'

# Let Cloud Run tell us which port to open
ENV PORT=8080
EXPOSE 8080
CMD ["sh","-c","streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true --server.enableCORS=false"]