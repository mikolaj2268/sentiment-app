import matplotlib.pyplot as plt
import streamlit as st
from wordcloud import WordCloud
import plotly.express as px

def sentiment_bar(df):
    counts = df["sentiment"].value_counts()
    fig = px.bar(
        x=counts.index,
        y=counts.values,
        labels={"x":"Sentiment","y":"Count"},
        title="Sentiment Counts"
    )
    st.plotly_chart(fig)

def score_histogram(df):
    fig, ax = plt.subplots()
    ax.hist(df["confidence"], bins=20)
    ax.set_xlabel("Confidence")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

def ngram_bar(df, title: str):
    fig = px.bar(df.head(15), x="ngram", y="count", title=title)
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

def wordcloud_from_series(series, title: str):
    text = " ".join(series.astype(str).values)
    wc = WordCloud(width=800, height=400, background_color="white").generate(text)
    fig, ax = plt.subplots(figsize=(8,4))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(title)
    st.pyplot(fig)

def content_len_hist(df):
    fig, ax = plt.subplots()
    ax.hist(df["content"].str.len(), bins=30)
    ax.set_xlabel("Content length (chars)")
    ax.set_ylabel("Count")
    st.pyplot(fig)

def score_distribution(df, score_col: str):
    dist = df[score_col].value_counts(normalize=True).sort_index()
    fig = px.bar(
        x=dist.index,
        y=dist.values,
        labels={"x":score_col, "y":"Percentage"},
        title="Score Distribution"
    )
    fig.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig)