# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

# ── install Python deps first ───────────────────────────────────────────────
RUN pip install --no-cache-dir -r requirements.txt

# ── download the DistilBERT SST-2 checkpoint into /app/models/ ──────────────
RUN python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    local_dir="/app/models/distilbert-sst2",
    local_dir_use_symlinks=False,
    revision=None,             # latest
    etag_timeout=30
)
PY

# ── make Transformers run strictly offline at container runtime ─────────────
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HOME=/app/models/.cache

EXPOSE 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false"]