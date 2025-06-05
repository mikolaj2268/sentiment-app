import streamlit as st
import streamlit as st
import os
from authlib.integrations.requests_client import OAuth2Session

def login_with_google():
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.environ.get("REDIRECT_URI")

    authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
    token_endpoint = "https://oauth2.googleapis.com/token"
    scope = "openid email profile"

    # Użycie nowej metody st.query_params
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]

        oauth2_session = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)
        token = oauth2_session.fetch_token(token_endpoint, code=code)

        st.success("Zalogowano pomyślnie!")
        st.write("Token:", token)
        return

    # Generujemy URL autoryzacyjny
    oauth2_session = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)
    uri, state = oauth2_session.create_authorization_url(authorization_endpoint)

    # Link do logowania lub automatyczne przekierowanie
    st.markdown(f"[🔐 Kliknij tutaj, aby zalogować się przez Google]({uri})")
    st.write("Redirect URI:", redirect_uri)
    st.write("Redirect URI:", client_secret)
    st.write("Redirect URI:", client_id)

    st.markdown(f"""
        <script>
            window.location.href = "{uri}";
        </script>
    """, unsafe_allow_html=True)

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
    
    # --- Dodany guzik logowania ---
    if st.button("🔐 Log in with Google"):
        # Tutaj wywołujesz funkcję logowania
        login_with_google()
