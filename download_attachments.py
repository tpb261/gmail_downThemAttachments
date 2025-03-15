#generated by gemini code assist on 15-March-2025

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import os
import pickle

# Set up the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'

def get_gmail_service():
    """
    Gets the Gmail API service object, handling authentication.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

# Function to search for emails based on criteria
def search_emails(service, user_id, query):
    results = service.users().messages().list(userId=user_id, q=query).execute()
    messages = results.get('messages', [])
    return messages

# Function to download attachments
def download_attachments(service, user_id, messages):
    for message in messages:
        msg = service.users().messages().get(userId=user_id, id=message['id']).execute()
        for part in msg['payload'].get('parts', []):
            if part['filename']:
                attachment_id = part['body'].get('attachmentId')
                attachment = service.users().messages().attachments().get(
                    userId=user_id, messageId=message['id'], id=attachment_id).execute()
                data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                
                # Save the file
                filepath = os.path.join('downloads', part['filename'])
                os.makedirs('downloads', exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(data)
                print(f"Downloaded: {part['filename']}")

# Define your search query (e.g., "from:example@example.com has:attachment")
search_query = 'has:attachment'

# Get the Gmail service
service = get_gmail_service()

# Perform the search and download attachments
messages = search_emails(service, 'me', search_query)
download_attachments(service, 'me', messages)
