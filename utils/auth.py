import os
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

def handle_oauth_callback():
    """Handle OAuth callback when returning from Google"""
    query_params = st.query_params
    if "code" in query_params:
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.environ.get("REDIRECT_URI")
        token_endpoint = "https://oauth2.googleapis.com/token"
        
        code = query_params["code"]
        oauth2_session = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)
        
        try:
            token = oauth2_session.fetch_token(token_endpoint, code=code)
            id_info = id_token.verify_oauth2_token(
                token["id_token"],
                google_requests.Request(),
                client_id
            )
            st.session_state["user_id"] = id_info["sub"]
            st.session_state["user_email"] = id_info.get("email", "")
            st.success(f"Logged in as {st.session_state['user_email']} ✅")
            st.query_params.clear()
            st.rerun()
            return True
        except Exception as e:
            st.error("Login failed")
            st.exception(e)
            st.query_params.clear()
            return False
    return False

def login_with_google():
    """Initiate Google OAuth login"""
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.environ.get("REDIRECT_URI")
    
    if not all([client_id, client_secret, redirect_uri]):
        st.error("OAuth configuration missing. Please set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and REDIRECT_URI environment variables.")
        return

    authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
    scope = "openid email profile"

    oauth2_session = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)
    uri, state = oauth2_session.create_authorization_url(authorization_endpoint)
    
    # Store state in session to verify later
    st.session_state["oauth_state"] = state
    
    st.info("Redirecting to Google for authentication...")
    st.markdown(f"[🔐 Click here if not redirected automatically]({uri})")
    st.markdown(f"""
        <script>
            window.location.href = "{uri}";
        </script>
    """, unsafe_allow_html=True)

def get_logged_user():
    return st.session_state.get("user_id"), st.session_state.get("user_email")

def logout_user():
    """Clear user session and logout"""
    # Clear specific user-related data
    keys_to_clear = ["user_id", "user_email", "oauth_state"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.query_params.clear()
    st.success("Logged out successfully!")
    st.rerun() 


