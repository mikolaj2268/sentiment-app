from pathlib import Path
from functools import lru_cache
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline,
)
from huggingface_hub import snapshot_download

# gdzie ma leżeć model w repo/projekcie
_LOCAL_DIR = Path(__file__).resolve().parent.parent / "models" / "distilbert-sst2"
_REPO_ID   = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"

def _ensure_model_is_downloaded() -> None:
    """
    Pobiera wagę z HF tylko wtedy, gdy nie ma jej lokalnie.
    Wymaga dostępu do internetu **tylko przy pierwszym uruchomieniu**.
    """
    if _LOCAL_DIR.exists():
        return

    print("⏬  Model not found locally – downloading from HF Hub...")
    snapshot_download(
        repo_id=_REPO_ID,
        local_dir=_LOCAL_DIR,
        local_dir_use_symlinks=False,
        allow_patterns=[
            "pytorch_model.bin", "config.json", "tokenizer.json", "vocab.txt"
        ],
    )
    print("✅  Model downloaded to", _LOCAL_DIR)

@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    _ensure_model_is_downloaded()

    tokenizer = AutoTokenizer.from_pretrained(_LOCAL_DIR, local_files_only=True)
    model     = AutoModelForSequenceClassification.from_pretrained(
        _LOCAL_DIR, local_files_only=True
    )
    return pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tokenizer,
        device=-1,          # CPU
    )