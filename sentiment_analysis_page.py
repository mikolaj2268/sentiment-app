# src/sentiment_analysis_page.py
import streamlit as st
import pandas as pd
import nltk
from wordcloud import WordCloud
import re

from utils.model import get_sentiment_pipeline
from utils.text_stats import top_ngrams
from utils.auth import get_logged_user  # zmiana na get_logged_user z auth.py
from utils.storage import save_user_csv, list_user_files, load_user_file

# ─── NLTK resources ─────────────────────────────────────────────────────────
for pkg in ["punkt", "stopwords", "vader_lexicon"]:
    try:
        path = "tokenizers/punkt" if pkg == "punkt" else f"corpora/{pkg}"
        nltk.data.find(path)
    except LookupError:
        nltk.download(pkg)

pipe = get_sentiment_pipeline()

def sentiment_analysis_page():
    st.header("Sentiment Dashboard")
    user_id,user_email = get_logged_user()
    if user_email:
        st.markdown((f"✅ Logged in as **{user_email}**"))
    # ----------------------------------------------------------------------
    # 0.  Initialise session storage
    # ----------------------------------------------------------------------
    ss = st.session_state
    for k in ["mode", "results_df", "text_col"]:
        ss.setdefault(k, None)

    # ----------------------------------------------------------------------
    # 6. User files from storage
    # ----------------------------------------------------------------------
    if user_id:
        st.markdown("### 📁 Your saved files")
        files = list_user_files(user_id=user_id)
        if files:
            selected_file = st.selectbox("Choose a file to analyze", files)
            if st.button("🔍 Analyze this file again"):
                df_loaded = load_user_file(user_id, selected_file)
                if df_loaded is not None:
                    ss.results_df = df_loaded
                    ss.mode = "CGS"
                    ss.text_col = df_loaded.columns[0]  # or store col name as metadata
                    st.rerun()
        else:
            st.info("You have no saved files.")
            
    # ----------------------------------------------------------------------
    # 1.  Choose mode (demo vs upload) *only* if we haven't produced results
    # ----------------------------------------------------------------------
    if ss.results_df is None:
        col_demo, col_upload = st.columns(2)
        if col_demo.button("► Run Demo"):
            ss.mode = "demo"
        if col_upload.button("► Upload CSV"):
            ss.mode = "upload"

    if ss.mode is None:
        st.info("Click **Run Demo** or **Upload CSV** to start.")
        return

    # ----------------------------------------------------------------------
    # 2.  Load raw data according to mode
    # ----------------------------------------------------------------------
    
    filename = "demo_results.csv"  # Default filename
    
    if ss.mode == "demo":
        raw = [
            "Just had an amazing cup of coffee! ☕️",
            "Terrible service; very disappointed.",
            "Pretty good, but could be better.",
            "Absolutely fantastic experience!",
            "I will not recommend this to anyone."
        ]
        df_raw = pd.DataFrame({"content": raw})
        ss.text_col = "content"
        st.success("Demo mode — analysing example tweets.")
    elif ss.mode == "upload":
        up = st.file_uploader("Upload a CSV file", type="csv", key="uploader")
        if up is None:
            st.info("Upload a CSV to continue.")
            return
        filename = up.name  # Use uploaded file name
        df_raw = pd.read_csv(up)
        if ss.text_col is None:  # ask only once
            ss.text_col = st.selectbox("Choose the column containing text:", df_raw.columns, key="textcol_selector")
            if ss.text_col is None:
                return
        
        df_raw = df_raw[df_raw[ss.text_col].notna()]          # usuń NaN
        df_raw[ss.text_col] = df_raw[ss.text_col].astype(str)  # zamień na string
        df_raw = df_raw[df_raw[ss.text_col].str.strip() != ""] # usuń puste i białe znaki   
    
    # ----------------------------------------------------------------------
    # 3.  Run DistilBERT once, store results
    # ----------------------------------------------------------------------
    if ss.results_df is None:
        if st.button("Run sentiment analysis"):
            with st.spinner("Scoring…"):
                preds = pipe(df_raw[ss.text_col].astype(str).tolist())
                df_res = df_raw.copy()
                df_res["Sentiment"] = [p["label"].capitalize() for p in preds]
                df_res["Confidence"] = [p["score"] for p in preds]
                ss.results_df = df_res

                if user_id:
                    # Zapisz do GCS
                    save_user_csv(user_id=user_id, filename=filename, df=df_res)
                    st.success(f"Results saved to private folder of: {user_email}")
        else:
            return
        
    # ----------------------------------------------------------------------
    # 4.  Interactive filters (live; do NOT clear session data)
    # ----------------------------------------------------------------------
    st.markdown("### Filters")
    col_f1, col_f2 = st.columns([2, 2])

    with col_f1:
        sentiments = ss.results_df["Sentiment"].unique().tolist()
        show_sent = st.multiselect("Sentiments to display", sentiments, default=sentiments, key="sent_filter")
    with col_f2:
        n_val = st.selectbox("n-gram size", [1, 2, 3, 4], index=0, key="ngram_n")
        k_val = st.slider("Top-k phrases", 5, 30, 10, 5, key="ngram_k")

    df_view = ss.results_df[ss.results_df["Sentiment"].isin(show_sent)]

    # ----------------------------------------------------------------------
    # 5.  Tabs with plots and tables
    # ----------------------------------------------------------------------
    tab_preview, tab_dist, tab_ngrams = st.tabs(
        ["📋 Preview & Download", "📊 Distribution", "🔢 N-grams & Word-cloud"]
    )

    with tab_preview:
        st.dataframe(df_view, use_container_width=True)
        st.download_button(
            "⬇ Download CSV",
            df_view.to_csv(index=False).encode(),
            "sentiment_results.csv",
            "text/csv",
        )

    with tab_dist:
        st.subheader("Sentiment counts")
        st.bar_chart(df_view["Sentiment"].value_counts())

        st.subheader("Confidence histogram")
        conf_hist = pd.cut(df_view["Confidence"], 10).astype(str).value_counts().sort_index()
        st.bar_chart(conf_hist)

        st.subheader("Content-length histogram")
        # Jest to wcześniej przy wczytywaniu ale raz wrzuciłem ramke bez tego i były błędy na wszelki wypadek niech zostanie
        df_view = df_view[df_view[ss.text_col].notna()]          # usuń NaN
        df_view[ss.text_col] = df_view[ss.text_col].astype(str)  # zamień na string
        df_view = df_view[df_view[ss.text_col].str.strip() != ""] # usuń puste i białe znaki   
        lengths = df_view[ss.text_col].str.len()
        len_hist = pd.cut(lengths, 10).astype(str).value_counts().sort_index()
        st.bar_chart(len_hist)

    with tab_ngrams:
        st.subheader(f"Top {k_val} {n_val}-grams")
        ng_df = top_ngrams(df_view[ss.text_col].tolist(), (n_val, n_val), top_k=k_val)
        st.dataframe(ng_df, use_container_width=True)
        st.bar_chart(ng_df.set_index("ngram")["count"])

        st.subheader("Word cloud")
        corpus = " ".join(df_view[ss.text_col].tolist())
        # Wydobądź tylko słowa alfabetyczne
        words = re.findall(r"\b\w+\b", corpus.lower())

        if words:
            filtered_corpus = " ".join(words)
            img = WordCloud(width=800, height=400, background_color="white").generate(filtered_corpus)
            st.image(img.to_array(), use_container_width=True)
        else:
            st.info("No valid words found to generate the word cloud.")


    # ----------------------------------------------------------------------
    # 7.  Reset button (clears results & mode)
    # ----------------------------------------------------------------------
    if st.button("↺ Start over"):
        for k in ["mode", "results_df", "text_col"]:
            ss[k] = None
        st.rerun()
    