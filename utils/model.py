from pathlib import Path
from functools import lru_cache
import os

# Set environment variables to prevent PyTorch/Streamlit file watcher conflicts
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TORCH_USE_CUDA_DSA"] = "false"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# Import transformers with error handling for Streamlit compatibility
try:
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        pipeline,
    )
    from huggingface_hub import snapshot_download
except ImportError as e:
    print(f"Warning: Error importing transformers: {e}")
    raise

# gdzie ma leżeć model w repo/projekcie
_LOCAL_DIR = Path(__file__).resolve().parent.parent / "models" / "distilbert-sst2"
_REPO_ID   = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"

def _ensure_model_is_downloaded() -> None:
    """
    Pobiera wagę z HF tylko wtedy, gdy nie ma jej lokalnie.
    Wymaga dostępu do internetu **tylko przy pierwszym uruchomieniu**.
    """
    if _LOCAL_DIR.exists() and len(list(_LOCAL_DIR.glob("*.bin"))) > 0:
        return

    print("⏬  Model not found locally – downloading from HF Hub...")
    try:
        snapshot_download(
            repo_id=_REPO_ID,
            local_dir=_LOCAL_DIR,
            local_dir_use_symlinks=False,
            allow_patterns=[
                "pytorch_model.bin", "config.json", "tokenizer.json", "vocab.txt"
            ],
        )
        print("✅  Model downloaded to", _LOCAL_DIR)
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        raise

@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    """Get sentiment analysis pipeline with proper error handling."""
    try:
        _ensure_model_is_downloaded()

        print(f"📁 Loading model from: {_LOCAL_DIR}")
        
        # Set environment variable to avoid some PyTorch warnings
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        tokenizer = AutoTokenizer.from_pretrained(_LOCAL_DIR, local_files_only=True)
        model = AutoModelForSequenceClassification.from_pretrained(
            _LOCAL_DIR, local_files_only=True
        )
        
        pipe = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            device=-1,  # CPU
        )
        
        print("✅ Model loaded successfully")
        return pipe
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        # Fallback: try to load from HuggingFace directly
        print("🔄 Trying to load model directly from HuggingFace...")
        try:
            pipe = pipeline(
                "sentiment-analysis",
                model=_REPO_ID,
                device=-1,
            )
            print("✅ Model loaded from HuggingFace Hub")
            return pipe
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            raise