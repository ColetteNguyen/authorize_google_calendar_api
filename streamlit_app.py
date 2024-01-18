import streamlit as st
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
import os
import pickle
import paramiko
import logging

logging.basicConfig(filename='streamlit_app.log', level=logging.DEBUG)


REMOTE_SERVER_HOST = st.secrets["REMOTE_SERVER_HOST"]
REMOTE_SERVER_PORT = st.secrets["REMOTE_SERVER_PORT"]
REMOTE_SERVER_USERNAME = st.secrets["REMOTE_SERVER_USERNAME"]
REMOTE_SERVER_PASSWORD = st.secrets["REMOTE_SERVER_PASSWORD"]


st.title('Google Calendar Integration with Streamlit')

# Streamlit app variables
SESSION_STATE = st.session_state
SESSION_STATE.mcst_number = None
SESSION_STATE.state = None
SESSION_STATE.google_token = None

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
          'openid']
REDIRECT_URL = 'http://localhost:8501/google_calendar_redirect'
CLIENT_SECRETS_FILE_PATH = '/path/to/client_secrets.json'  # Replace with the actual path

# Function to handle Google Calendar initialization
def google_calendar_init():
    mcst_number = st.text_input('Enter MCST Number:')
    
    if st.button('Initialize Google Calendar'):
        SESSION_STATE.mcst_number = mcst_number
        
        # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE_PATH, scopes=SCOPES)
    
        # The URI created here must exactly match one of the authorized redirect URIs
        # for the OAuth 2.0 client, which you configured in the API Console. If this
        # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
        # error.
        flow.redirect_uri = REDIRECT_URL
    
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')
    
        # Store the state so the callback can verify the auth server response.
        SESSION_STATE.state = state
    
        st.success(f"Visit the following link to authorize the app:\n{authorization_url}")

# Function to handle Google Calendar redirection
def google_calendar_redirect():
    # Specify the state when creating the flow in the callback so that it can
    # verify in the authorization server response.
    state = SESSION_STATE.state
    if state is None:
        st.error("State parameter missing.")
        return
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE_PATH, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URL
    
    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = st.text_input('Enter Authorization Response URL:')
    flow.fetch_token(authorization_response=authorization_response)
    
    # Save credentials to session
    credentials_obj = flow.credentials
    SESSION_STATE.google_token = credentials_obj.to_json()  # Convert to JSON string
    
    # Save credentials to token.pickle file on the remote server
    save_token_to_remote_server(SESSION_STATE.mcst_number, credentials_obj)

    st.success("Google Calendar integration successful!")

# Function to save the token.pickle file on the remote server
def save_token_to_remote_server(mcst_number, credentials_obj):
    # Connect to the remote server via SSH
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(REMOTE_SERVER_HOST, port=REMOTE_SERVER_PORT,
                    username=REMOTE_SERVER_USERNAME, password=REMOTE_SERVER_PASSWORD)
        
        # Create the remote directory if it doesn't exist
        ssh.exec_command(f'mkdir -p /path/to/{mcst_number}/')

        # Write the token.pickle file to the remote server
        with ssh.open_sftp() as sftp:
            with sftp.file(f'/path/to/{mcst_number}/token.pickle', 'wb') as remote_file:
                pickle.dump(credentials_obj, remote_file)

# Streamlit app routing
if st.button('Go to Google Calendar Initialization'):
    google_calendar_init()

if st.button('Complete Google Calendar Authorization'):
    google_calendar_redirect()

