import altair as alt
import os
import streamlit as st
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import paramiko

REMOTE_SERVER_HOST = st.secrets["REMOTE_SERVER_HOST"]
REMOTE_SERVER_PORT = st.secrets["REMOTE_SERVER_PORT"]
REMOTE_SERVER_USERNAME = st.secrets["REMOTE_SERVER_USERNAME"]
REMOTE_SERVER_PASSWORD = st.secrets["REMOTE_SERVER_PASSWORD"]

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def fetch_credentials_file():
    # Connect to the remote server using SSH
    with paramiko.Transport((REMOTE_SERVER_HOST, REMOTE_SERVER_PORT)) as transport:
        transport.connect(username=REMOTE_SERVER_USERNAME, password=REMOTE_SERVER_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Download credentials.json
        sftp.get('/root/waha_chatbot/credentials.json', 'credentials.json')

        sftp.close()

def authorize_google_calendar(mcst_number):
    creds = None
    token_path = f"/root/waha_chatbot/{mcst_number}/token.pickle"

    if os.path.exists(token_path):
        creds = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES
        )
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            token.write(creds.to_bytes())
        
        # Authorization successful, stop the app
        st.success("Authorization successful. You can close this window.")
        st.stop()

def main():
    st.title("Google Calendar API Authorization with Streamlit")

    # Get MCST number from user input
    mcst_number = st.text_input("Enter MCST number:")
    
    # Check if MCST number is provided
    if mcst_number:
        # Fetch credentials.json from the remote server
        fetch_credentials_file()

        # Create directory if not exists
        os.makedirs(mcst_number, exist_ok=True)

        # Authorize and stop the app on success
        authorize_google_calendar(mcst_number)
    else:
        st.warning("Please enter the MCST number.")

if __name__ == "__main__":
    main()
