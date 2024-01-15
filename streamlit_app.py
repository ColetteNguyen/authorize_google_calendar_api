# import os
# import streamlit as st
# from google.oauth2 import service_account
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# import paramiko

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
import streamlit as st
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
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

def simulate_authorization(mcst_number):
    try:
        # Simulate an automatic authorization by hardcoding an authorization code
        auth_code = "YOUR_HARDCODED_AUTH_CODE"  # Replace with the actual authorization code

        # Load credentials from the credentials.json file
        token_path = f"./{mcst_number}/token.pickle"
        creds = ""

        if os.path.exists(token_path):
            creds = service_account.Credentials.from_service_account_file(
                'credentials.json', scopes=SCOPES
            )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Ensure the directory exists before writing the file
                os.makedirs(mcst_number, exist_ok=True)

                # Exchange the authorization code for credentials
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                )

                credentials = flow.fetch_token(code=auth_code)

                # Save the credentials to the token file
                with open(token_path, 'wb') as token:
                    pickle.dump(credentials, token)

                # Authorization successful
                st.success("Authorization successful!")

    except Exception as e:
        st.error(f"Error simulating authorization: {e}")

def main():
    st.title("Google Calendar API Authorization")

    # Fetch credentials.json from the remote server
    fetch_credentials_file()

    # Get MCST number from user input
    mcst_number = st.text_input("Enter MCST number:")

    # Add a "Simulate Authorization" button
    if st.button("Simulate Authorization"):
        # Check if MCST number is provided
        if mcst_number:
            # Simulate an automatic authorization
            simulate_authorization(mcst_number)
        else:
            st.warning("Please enter the MCST number.")

if __name__ == "__main__":
    main()


