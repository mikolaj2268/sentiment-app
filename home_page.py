import streamlit as st
from utils.auth import login_with_google, get_logged_user, logout_user, handle_oauth_callback
import os

def home_page():
    # Handle OAuth callback first if present
    if handle_oauth_callback():
        return  # Exit early if callback was processed
    
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

    _, user_email = get_logged_user()

    if user_email:
        st.success(f"✅ Logged in as **{user_email}**")

        if st.button("🔓 Log out"):
            logout_user()
    else:
        st.info("You are not logged in.")
        
        # Check if we're in the middle of an OAuth flow
        if "code" in st.query_params:
            st.info("Processing login...")
        elif st.button("🔐 Log in with Google"):
            login_with_google()
