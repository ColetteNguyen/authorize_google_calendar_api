import streamlit as st
import paramiko
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
import os
import pickle
import logging

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

CLIENT_SECRETS_FILE = "/root/waha_chatbot/authorise/streamlit/credentials.json"
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]
REDIRECT_URL = 'https://connectapi.streamlit.app/google_calendar_redirect'
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

# Set up logging
logging.basicConfig(filename='streamlit_app.log', level=logging.DEBUG)

# Streamlit app
st.title("Google Calendar Authorization")

mcst_number = st.text_input("MCST Number:")
if st.button("Authorize"):
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = REDIRECT_URL

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    # Display the authorization URL
    st.write(f"Click [here]({authorization_url}) to authorize.")

    # Save the state and MCST number to the session (for simplicity, you can use Streamlit's session_state)
    st.session_state.state = state
    st.session_state.mcst_number = mcst_number

# Streamlit callback for handling redirection
@st.cache(allow_output_mutation=True)
def get_flow():
    return None

if st.session_state.state is not None:
    flow = get_flow()
    if flow is None:
        # Create flow instance with the saved state
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, state=st.session_state.state)
        flow.redirect_uri = REDIRECT_URL
        st.session_state.flow = flow

    # Display the authorization response URL
    authorization_response = st.text_input("Authorization Response URL:")
    if st.button("Fetch Token"):
        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        flow.fetch_token(authorization_response=authorization_response)

        # Save credentials to token.pickle file
        credentials_obj = flow.credentials
        token_dir = f'/root/waha_chatbot/authorise/streamlit/{st.session_state.mcst_number}/'
        os.makedirs(token_dir, exist_ok=True)
        token_path = os.path.join(token_dir, 'token.pickle')
        with open(token_path, 'wb') as token_file:
            pickle.dump(credentials_obj, token_file)

        st.success("Token fetched and saved successfully.")

        # SSH connection to upload token.pickle to the server
        try:
            with paramiko.SSHClient() as ssh:
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    st.secrets["REMOTE_SERVER_HOST"],
                    port=st.secrets["REMOTE_SERVER_PORT"],
                    username=st.secrets["REMOTE_SERVER_USERNAME"],
                    password=st.secrets["REMOTE_SERVER_PASSWORD"]
                )

                # Upload the token.pickle file to the server
                with ssh.open_sftp() as sftp:
                    sftp.put(token_path, f'/root/waha_chatbot/authorise/streamlit/{st.session_state.mcst_number}/token.pickle')
                    
            st.success("Token uploaded to the server.")
        except Exception as e:
            st.error(f"Error uploading token to the server: {str(e)}")
            logging.error(f"Error uploading token to the server: {str(e)}")
