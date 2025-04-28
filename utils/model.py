from pathlib import Path
from functools import lru_cache
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline,
)

_LOCAL_DIR = Path(__file__).resolve().parent.parent / "models" / "distilbert-sst2"

@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    # 1. wczytujemy z dysku – local_files_only=True działa TYLKO tutaj
    tokenizer = AutoTokenizer.from_pretrained(_LOCAL_DIR, local_files_only=True)
    model     = AutoModelForSequenceClassification.from_pretrained(
        _LOCAL_DIR, local_files_only=True
    )

    # 2. budujemy pipeline bez zbędnych argumentów
    return pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tokenizer,
        device=-1,      # CPU
    )