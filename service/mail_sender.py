from __future__ import print_function

import requests
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
# https://developers.google.com/gmail/api/auth/scopes
# service endpoint
SCOPES = ['https://mail.google.com/']#['https://www.googleapis.com/auth/gmail.readonly']

def mail_api_open():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file google_auth_token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('service/google_auth_token.json'):
        creds = Credentials.from_authorized_user_file('service/google_auth_token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'service/mail_token.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('service/google_auth_token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='jasuil1212@gmail.com').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        print('Labels:')
  #      for label in labels:
   #         print(label['name'])

    except HttpError as error:
        print(f'An error occurred: {error}')

def gmail_create_draft(title, msg, user_mail):
    """Create and insert a draft email.
       Print the returned draft's message and id.
       Returns: Draft object, including draft id and message meta data.

      Load pre-authorized user credentials from the environment.
      for guides on implementing OAuth2 for the application.
    """

    creds, _ = '', '' # google.auth.default()
    if os.path.exists('service/google_auth_token.json'):
        creds = Credentials.from_authorized_user_file('service/google_auth_token.json', SCOPES)

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        message.set_content(msg)

        message['To'] = user_mail
        message['From'] = 'jasuil1212@gmail.com'
        message['Subject'] = title

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = service.users().messages().send(userId="jasuil1212@gmail.com",
                                                body=create_message)\
            .execute()
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None

    return send_message

