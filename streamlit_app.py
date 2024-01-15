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

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar.events']

def fetch_credentials_file():
    try:
        # Connect to the remote server using SSH
        with paramiko.Transport((REMOTE_SERVER_HOST, REMOTE_SERVER_PORT)) as transport:
            transport.connect(username=REMOTE_SERVER_USERNAME, password=REMOTE_SERVER_PASSWORD)
            sftp = paramiko.SFTPClient.from_transport(transport)

            # Download credentials.json
            sftp.get('/root/waha_chatbot/authorise/credentials.json', 'credentials.json')

            sftp.close()
    except Exception as e:
        st.error(f"Error fetching credentials file: {e}")
        


        
def main():
    st.title("Google Calendar API Authorization with Streamlit")

    # Fetch credentials.json from the remote server
    fetch_credentials_file()

    # Get MCST number from user input
    mcst_number = st.text_input("Enter MCST number:")
    
    # Add an "Authorize" button
    if st.button("Authorize"):
        # Check if MCST number is provided
        if mcst_number:
            # Create directory if not exists
            os.makedirs(mcst_number, exist_ok=True)

            # Authorize
            authorize_google_calendar(mcst_number)
        else:
            st.warning("Please enter the MCST number.")


if __name__ == "__main__":
    main()
