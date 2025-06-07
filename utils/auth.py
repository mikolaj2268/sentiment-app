import os
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

def login_with_google():
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.environ.get("REDIRECT_URI")

    authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
    token_endpoint = "https://oauth2.googleapis.com/token"
    scope = "openid email profile"

    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]

        oauth2_session = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)
        token = oauth2_session.fetch_token(token_endpoint, code=code)

        try:
            id_info = id_token.verify_oauth2_token(
                token["id_token"],
                google_requests.Request(),
                client_id
            )
            st.session_state["user_id"] = id_info["sub"]
            st.session_state["user_email"] = id_info.get("email", "")
            st.success(f"Logged as {st.session_state['user_email']} ✅")
            st.query_params.clear()
            st.rerun() 

        except Exception as e:
            st.error("Logging failed")
            st.exception(e)

        return

    oauth2_session = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri, scope=scope)
    uri, state = oauth2_session.create_authorization_url(authorization_endpoint)

    st.markdown(f"[🔐 Click here to log in with Google]({uri})")
    st.markdown(f"""
        <script>
            window.location.href = "{uri}";
        </script>
    """, unsafe_allow_html=True)

def get_logged_user():
    return st.session_state.get("user_id"), st.session_state.get("user_email")

def logout_user():
    # Clear user-related data from session state
    # for key in ["user", "token"]:
    #     if key in st.session_state:
    #         del st.session_state[key]
    st.session_state.clear()
    st.query_params.clear()
    st.rerun() 


