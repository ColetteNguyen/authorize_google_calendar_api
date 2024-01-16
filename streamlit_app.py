import streamlit as st
from pymongo import MongoClient
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import pickle
import base64
import paramiko
from io import BytesIO
import json

# Connect to MongoDB
CONNECTION_STRING = "mongodb+srv://colette:6xUTl6YRSY8mHoaK@telegrambot.zulss7f.mongodb.net/test"
client = MongoClient(CONNECTION_STRING)
dbname = client['new_facility_booking']
collection = dbname["token_files"]

# Google Calendar API credentials
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authorize_google_calendar():
    # Read the contents of credentials.json directly
    client_config = json.loads(st.secrets["GOOGLE_CREDENTIALS_JSON"])

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)
    return creds

def save_to_mongodb(mcst_number, date, token_data):
    # Encode the token data to base64
    token_base64_data = base64.b64encode(pickle.dumps(token_data)).decode('utf-8')

    # Create a MongoDB document
    document = {
        "mcst_number": mcst_number,
        "date": date,
        "token_base64_data": token_base64_data
    }

    collection.insert_one(document)

def get_credentials_from_server():
    # SSH Connection details
    ssh_host = st.secrets["REMOTE_SERVER_HOST"]
    ssh_port = st.secrets["REMOTE_SERVER_PORT"]
    ssh_username = st.secrets["REMOTE_SERVER_USERNAME"]
    ssh_password = st.secrets["REMOTE_SERVER_PASSWORD"]
  
    # Remote file path on the Ubuntu server
    remote_credentials_path = "/root/waha_chatbot/authorise/credentials.json"

    # Connect to the server using SSH
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_host, port=ssh_port, username=ssh_username, password=ssh_password)

        # Fetch the credentials.json file from the server
        stdin, stdout, stderr = ssh.exec_command(f"cat {remote_credentials_path}")
        credentials_json_data = stdout.read().decode('utf-8')

    return credentials_json_data

def main():
    st.title("Google Calendar API Authorization")

    # Input fields
    mcst_number = st.text_input("Enter MCST Number:")
    date = st.date_input("Select Date:")

    # Button to trigger authorization
    if st.button("Authorize Google Calendar"):
        # Connect to Google Calendar API and authorize
        creds = authorize_google_calendar()

        # Save to MongoDB
        save_to_mongodb(mcst_number, date, creds)
        st.success("Authorization successful. Data saved to MongoDB.")

    # Button to retrieve token data from MongoDB
    if st.button("Get Data from MongoDB"):
        result = collection.find_one({"mcst_number": mcst_number, "date": date})
        if result:
            # Decode and load the token data
            token_data = pickle.loads(base64.b64decode(result["token_base64_data"]))

            # Save token.pickle to a local file
            with open("token.pickle", "wb") as token_file:
                token_file.write(token_data)

            st.success("Token data retrieved from MongoDB.")
        else:
            st.warning("Data not found in MongoDB.")

if __name__ == "__main__":
    main()
