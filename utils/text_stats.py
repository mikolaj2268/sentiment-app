from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import pandas as pd
from typing import List, Tuple

def top_ngrams(
    docs: List[str],
    ngram_range: Tuple[int,int],
    top_k: int = 20,
    stop_words: str = "english"
) -> pd.DataFrame:
    vec = CountVectorizer(
        stop_words=stop_words,
        ngram_range=ngram_range,
        lowercase=True,
        strip_accents="unicode"
    )
    X = vec.fit_transform(docs)
    counts = X.sum(axis=0).A1
    vocab = vec.get_feature_names_out()
    freq = Counter(dict(zip(vocab, counts)))
    common = freq.most_common(top_k)
    return pd.DataFrame(common, columns=["ngram", "count"])