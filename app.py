import streamlit as st
from home_page import home_page
from sentiment_analysis_page import sentiment_analysis_page
import time, logging
logging.basicConfig(level=logging.INFO)
logging.info("Starting model load at %s", time.strftime("%X"))

st.set_page_config(
    page_title="Sentiment Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Sidebar navigation ----------------
pages = {
    "Home": home_page,
    "Sentiment Dashboard": sentiment_analysis_page,
}

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", list(pages.keys()))
pages[choice]()