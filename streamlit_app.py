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
REDIRECT_URL = 'https://connectapi.streamlit.app/google_calendar_redirect'
CLIENT_SECRETS_FILE_PATH = '/root/waha_chatbot/authorise/streamlit/credentials.json'  # Replace with the actual path

# Function to handle Google Calendar initialization
def step1_authorize():
    st.header('Step 1: Enter MCST Number')
    SESSION_STATE.mcst_number = st.text_input('Enter MCST Number:')
    
    if st.button('Next Step: Authorize Google Calendar'):
        st.success('MCST Number saved. Proceed to the next step.')

# Function to handle Google Calendar authorization
def step2_authorize_google_calendar():
    st.header('Step 2: Authorize Google Calendar')
    
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

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = st.text_input('Enter Authorization Response URL:')
    if st.button('Authorize Google Calendar'):
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
        ssh.exec_command(f'mkdir -p /root/waha_chatbot/authorise/streamlit/{mcst_number}/')

        # Write the token.pickle file to the remote server
        with ssh.open_sftp() as sftp:
            remote_file_path = f'/root/waha_chatbot/authorise/streamlit/{mcst_number}/token.pickle'
            with sftp.file(remote_file_path, 'wb') as remote_file:
                pickle.dump(credentials_obj, remote_file)
        
        st.success(f"Token.pickle file saved on the remote server: {remote_file_path}")

# Streamlit app routing
if not SESSION_STATE.mcst_number:
    step1_authorize()
else:
    step2_authorize_google_calendar()
