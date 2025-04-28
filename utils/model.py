from functools import lru_cache
from transformers import pipeline

@lru_cache(None)
def get_sentiment_pipeline():
    """
    DistilBERT sentiment-analysis pipeline,
    forced to run on CPU (device=-1).
    """
    return pipeline(
        "sentiment-analysis",
        model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
        device=-1,               # <— add this
        return_all_scores=False  # optional, as before
    )