from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import functools
import os

SECRETS = './var'
TOKEN_FILE = SECRETS + '/token.json'
CREDENTIALS_FILE = SECRETS + '/client_secret.json'

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
creds: Credentials = None

class GmailService:

  def __init__(self, credentials) -> None:
    self._credentials = credentials
  
  @functools.cached_property
  def service(self):
    return build('gmail', 'v1', credentials=self._credentials)

  def connect(credentialFileLocation, tokenLocation: str = None) -> Credentials:
    if (not credentialFileLocation):
      credentialFileLocation = CREDENTIALS_FILE

    if (not tokenLocation or not os.path.exists(TOKEN_FILE)):
      os.mkdir(os.path.basename(TOKEN_FILE))
      tokenLocation = TOKEN_FILE

    loadedCreds = None
    
    if os.path.exists(tokenLocation):
      loadedCreds = Credentials.from_authorized_user_file(tokenLocation, SCOPES)

    if not loadedCreds or not loadedCreds.valid:
      if loadedCreds and loadedCreds.expired and loadedCreds.refresh_token:
        loadedCreds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            credentialFileLocation, SCOPES
        )
        loadedCreds = flow.run_local_server(port=0)
      # Save the credentials for the next run

      with open(tokenLocation, "w") as token:
        token.write(loadedCreds.to_json())

    return loadedCreds

