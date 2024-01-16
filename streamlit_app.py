# import os
# import streamlit as st
# from google.oauth2 import service_account
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
import paramiko

# REMOTE_SERVER_HOST = st.secrets["REMOTE_SERVER_HOST"]
# REMOTE_SERVER_PORT = st.secrets["REMOTE_SERVER_PORT"]
# REMOTE_SERVER_USERNAME = st.secrets["REMOTE_SERVER_USERNAME"]
# REMOTE_SERVER_PASSWORD = st.secrets["REMOTE_SERVER_PASSWORD"]

# SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar.events']

# def fetch_credentials_file():
#     try:
#         # Connect to the remote server using SSH
#         with paramiko.Transport((REMOTE_SERVER_HOST, REMOTE_SERVER_PORT)) as transport:
#             transport.connect(username=REMOTE_SERVER_USERNAME, password=REMOTE_SERVER_PASSWORD)
#             sftp = paramiko.SFTPClient.from_transport(transport)

#             # Download credentials.json
#             sftp.get('/root/waha_chatbot/authorise/credentials.json', 'credentials.json')

#             sftp.close()
#     except Exception as e:
#         st.error(f"Error fetching credentials file: {e}")

# def write_file_to_server(local_file_path, remote_file_path):
#     try:
#         # Connect to the remote server using SSH
#         with paramiko.Transport((REMOTE_SERVER_HOST, REMOTE_SERVER_PORT)) as transport:
#             transport.connect(username=REMOTE_SERVER_USERNAME, password=REMOTE_SERVER_PASSWORD)
#             sftp = paramiko.SFTPClient.from_transport(transport)

#             # Upload the local file to the remote server
#             sftp.put(local_file_path, remote_file_path)

#             sftp.close()
#     except Exception as e:
#         st.error(f"Error writing file to server: {e}")

# def authorize_google_calendar(mcst_number):
#     try:
#         # Load credentials from the credentials.json file
#         creds = None
#         token_path = f"./{mcst_number}/token.pickle"

#         if os.path.exists(token_path):
#             creds = service_account.Credentials.from_service_account_file(
#                 'credentials.json', scopes=SCOPES
#             )
#         if not creds or not creds.valid:
#             if creds and creds.expired and creds.refresh_token:
#                 creds.refresh(Request())
#             else:
#                 # Ensure the directory exists before writing the file
#                 os.makedirs(mcst_number, exist_ok=True)
                
#                 flow = InstalledAppFlow.from_client_secrets_file(
#                     'credentials.json', SCOPES,
#                     redirect_uri='https://connectapi.streamlit.app'
#                 )
#                 authorization_url, _ = flow.authorization_url(prompt='consent')
#                 st.markdown(f"Authorize the app by [visiting this link]({authorization_url}).")
#                 creds = flow.run_local_server(port=0)

#                 # Save the credentials to the token file
#                 with open(token_path, 'wb') as token:
#                     pickle.dump(creds, token)

#                 # Write the token file to the server
#                 write_file_to_server(token_path, f"/root/waha_chatbot/authorise/{mcst_number}/token.pickle")

#                 # Authorization successful
#                 st.success("Authorization successful!")
#                 # authorization_url, _ = flow.authorization_url(prompt='consent')
#                 # st.markdown(f"Authorize the app by [visiting this link]({authorization_url}).")
                

#                 # Assuming you have a 'Click to Authorize' button
#                 # if st.button("Click to Authorize"):
#                 #     # Complete the authorization flow
#                 #     creds = flow.run_local_server(port=0)

#                 #     # Save the credentials to the token file
#                 #     with open(token_path, 'wb') as token:
#                 #         pickle.dump(creds, token)

#                 #     # Write the token file to the server
#                 #     write_file_to_server(token_path, f"/root/waha_chatbot/authorise/{mcst_number}/token.pickle")

#                 #     # Authorization successful
#                 #     st.success("Authorization successful!")

#                 # st.stop()

#     except Exception as e:
#         st.error(f"Error authorizing Google Calendar: {e}")
        
# def main():
#     st.title("Google Calendar API Authorization")

#     # Fetch credentials.json from the remote server
#     fetch_credentials_file()

#     # Get MCST number from user input
#     mcst_number = st.text_input("Enter MCST number:")
    
#     # Add an "Authorize" button
#     if st.button("Authorize"):
#         # Check if MCST number is provided
#         if mcst_number:
#             # Create directory if not exists
#             os.makedirs(mcst_number, exist_ok=True)

#             # Authorize
#             authorize_google_calendar(mcst_number)
#         else:
#             st.warning("Please enter the MCST number.")


# if __name__ == "__main__":
#     main()

import os
import logging
import streamlit as st
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import paramiko

# Set up logging
logging.basicConfig(filename='streamlit_app.log', level=logging.DEBUG)

REMOTE_SERVER_HOST = st.secrets["REMOTE_SERVER_HOST"]
REMOTE_SERVER_PORT = st.secrets["REMOTE_SERVER_PORT"]
REMOTE_SERVER_USERNAME = st.secrets["REMOTE_SERVER_USERNAME"]
REMOTE_SERVER_PASSWORD = st.secrets["REMOTE_SERVER_PASSWORD"]

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar.events']
# CLIENT_SECRETS = 'path/to/your/credentials.json'
REDIRECT_URI = 'https://connectapi.streamlit.app'

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
        logging.error(f"Error fetching credentials file: {e}")
        st.error(f"Error fetching credentials file: {e}")

def authorize_google_calendar(mcst_number):
    try:
        # Load credentials from the credentials.json file
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES,
            redirect_uri=REDIRECT_URI
        )
        authorization_url, _ = flow.authorization_url(prompt='consent')

        st.markdown(f"Authorize the app by visiting this link: [{authorization_url}]({authorization_url})")
        st.write("After authorization, click the 'Download token.pickle' button.")
        st.session_state.authorization_url = authorization_url
    except Exception as e:
        logging.error(f"Error authorizing Google Calendar: {e}")
        st.error(f"Error authorizing Google Calendar: {e}")

def download_token_pickle(mcst_number):
    try:
        # Exchange the authorization code for credentials
        auth_code = st.text_input("Enter Authorization Code:")
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES,
            redirect_uri=REDIRECT_URI
        )
        credentials = flow.fetch_token(code=auth_code)

        # Save the credentials to the token file
        token_filename = f'/root/waha_chatbot/authorise/{mcst_number}/token.pickle'
        os.makedirs(os.path.dirname(token_filename), exist_ok=True)
        with open(token_filename, 'wb') as token:
            pickle.dump(credentials, token)

        # Provide a button to download the token.pickle file
        st.download_button(
            label="Download token.pickle",
            data=pickle.dumps(credentials),
            key="token_pickle_download",
            file_name="token.pickle"
        )

        # Authorization successful
        st.success("Authorization successful!")
    except Exception as e:
        logging.error(f"Error downloading token.pickle: {e}")
        st.error(f"Error downloading token.pickle: {e}")

def main():
    st.title("Google Calendar API Authorization")

    # Fetch credentials.json from the remote server
    fetch_credentials_file()

    # Get MCST number from user input
    mcst_number = st.text_input("Enter MCST number:")

    # Add an "Authorize" button
    if st.button("Authorize") and mcst_number:
        # Authorize
        authorize_google_calendar(mcst_number)

    # Check if the authorization_url is in the session state
    if hasattr(st.session_state, 'authorization_url'):
        download_token_pickle(mcst_number)

if __name__ == "__main__":
    main()





