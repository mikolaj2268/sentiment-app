import streamlit as st

def home_page():
    st.title("📊 Sentiment Explorer")
    st.markdown(
        """
        **Sentiment Explorer** helps you quickly understand the mood of any English text dataset.

        **How to use the application**
        1. Switch to **Sentiment Dashboard** using the sidebar.  
        2. **Run Demo** on example tweets or **Upload CSV** of your own texts.  
        3. View interactive charts, extract key phrases, see a word cloud, and download annotated results.
        """
    )
    st.markdown("---")
    st.info("Select **Sentiment Dashboard** from the sidebar to begin.")