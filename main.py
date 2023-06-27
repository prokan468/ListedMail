import random
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64



GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
LABEL_NAME = 'AutoResponder'
MIN_INTERVAL = 45
MAX_INTERVAL = 120

SERVICE_ACCOUNT_FILE = "listedcrawler-65fa92d72906.json"
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=GMAIL_SCOPES
)
gmail_service = build('gmail', 'v1', credentials=credentials)

def get_unreplied_emails():
    try:
        response = gmail_service.users().messages().list(userId='me', q='is:unread').execute()
        messages = response.get('messages', [])
        return messages
    except HttpError as e:
        print(f'An error occurred: {e}')

def send_reply(email_id):
    try:
        
        message = gmail_service.users().messages().get(userId='me', id=email_id).execute()
        email_subject = ''
        email_from = ''
        for header in message['payload']['headers']:
            if header['name'] == 'Subject':
                email_subject = header['value']
            elif header['name'] == 'From':
                email_from = header['value']

        
        reply_message = f"Thank you for your email with the subject '{email_subject}'. " \
                       f"I am currently on vacation and will get back to you as soon as possible."

        
        reply = {
            'message': {
                'raw': base64.urlsafe_b64encode(reply_message.encode('utf-8')).decode('utf-8')
            },
            'threadId': message['threadId']
        }
        gmail_service.users().messages().send(userId='me', body=reply).execute()

        
        label = {'labelListVisibility': 'labelShow', 'messageListVisibility': 'show', 'name': LABEL_NAME}
        gmail_service.users().messages().modify(userId='me', id=email_id, body={'addLabelIds': [label['name']]}).execute()

        print(f"Replied to email from '{email_from}' with subject '{email_subject}'")

    except HttpError as e:
        print(f'An error occurred: {e}')

def auto_responder():
    while True:
        unreplied_emails = get_unreplied_emails()
        for email in unreplied_emails:
            email_id = email['id']
            send_reply(email_id)
        wait_interval = random.randint(MIN_INTERVAL, MAX_INTERVAL)
        time.sleep(wait_interval)

if __name__ == '__main__':
    auto_responder()
