import os
import json
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Set up the OAuth 2.0 Flow
# Path to your client_secret.json file
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:3001")


# Load client secrets from JSON file
def load_client_secrets(file_path: str = None) -> dict:
    if not file_path:
        file_path = CLIENT_SECRETS_FILE

    with open(file_path, 'r') as file:
        client_secrets = json.load(file)

    return client_secrets['web']


def get_google_credentials(code: str, uri: str = None):
    global REDIRECT_URI
    if uri:
        REDIRECT_URI = uri

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    # Exchange the authorization code for access and refresh tokens
    flow.fetch_token(code=code)

    # Get the credentials (includes access token)
    return flow.credentials


def get_user_details(credentials, email_only=True):
    # Now use the access token to get user info from the OAuth2 service
    user_info_service = build('oauth2', 'v2', credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()

    print(f"User info retrieved: {user_info}")

    if email_only:
        # Get the credentials (includes access token)
        return user_info.get('email', None)
    
    return user_info

def get_calendar_list(credentials):
    # Load client secrets
    client_secrets = load_client_secrets()

    # Create credentials using the access token, refresh token, and client info
    credentials = Credentials(
        token=credentials['access_token'],
        refresh_token=credentials['refresh_token'],

        token_uri=client_secrets['token_uri'],
        client_id=client_secrets['client_id'],
        client_secret=client_secrets['client_secret'],
        scopes=SCOPES
    )

    # If the credentials are expired, refresh them
    if credentials.expired:
        credentials.refresh(Request())

    # Build the service
    service = build("calendar", "v3", credentials=credentials)

    try:
        # Get the list of calendars
        calendar_list = service.calendarList().list().execute()

        # Process the calendar list
        calendars = []
        for calendar in calendar_list.get('items', []):
            calendars.append({
                'id': calendar['id'],
                'summary': calendar['summary'],
                'description': calendar.get('description', ''),
                'primary': calendar.get('primary', False)
            })

        return calendars

    except Exception as e:
        raise Exception(f"An error occurred while getting calendar list: {str(e)}")
