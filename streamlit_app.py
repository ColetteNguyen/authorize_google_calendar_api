# google_calendar_app.py

import streamlit as st
import httpx_oauth
import os

# Load your Google API credentials
CLIENT_ID = st.secrets['CLIENT_ID']
CLIENT_SECRET = st.secrets['CLIENT_SECRET']
REDIRECT_URI = st.secrets['REDIRECT_URI']

# Import the GoogleOAuth2 client
from httpx_oauth.clients.google import GoogleOAuth2

def authorize_google_calendar():
    # Create the GoogleOAuth2 client
    client = GoogleOAuth2(
        CLIENT_ID,
        CLIENT_SECRET,
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        authorize_params={"scope": ["https://www.googleapis.com/auth/calendar"]},
        token_url="https://oauth2.googleapis.com/token",
    )

    # Get the authorization URL and redirect the user
    authorization_url = client.get_authorization_url(REDIRECT_URI)
    st.experimental_set_query_params(code="")  # Clear any previous code in the URL
    st.markdown(f"[Authorize Google Calendar]({authorization_url})", unsafe_allow_html=True)

    # Get the authorization code from the URL
    code = st.experimental_get_query_params().get("code", "")
    if code:
        # Exchange the authorization code for an access token
        token = client.get_access_token(code, REDIRECT_URI)

        # Store the access token in session state
        st.session_state.access_token = token["access_token"]

        st.success("Authorization successful!")

def display_user():
    # Create the GoogleOAuth2 client
    client = GoogleOAuth2(
       CLIENT_ID,
        CLIENT_SECRET,
    )

    # Display user information
    user_info = client.get("https://www.googleapis.com/oauth2/v2/userinfo").json()
    st.write(f"You're logged in as {user_info['email']}")
def main():
    st.title("Google Calendar API Authorization")

    # Check if the user is already authorized
    if 'access_token' not in st.session_state:
        # If not authorized, show the login button
        if st.button("Authorize Google Calendar"):
            authorize_google_calendar()

    else:
        # If authorized, display user information
        display_user()
if __name__ == "__main__":
    main()
