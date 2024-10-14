import json
from googleapiclient.discovery import build
from pydantic import BaseModel
from typing import Optional

from utils.helper import extract_domain, dict_from_record
from utils.google_calendar import *

from dotenv import load_dotenv
load_dotenv()


class SMBData(BaseModel):
    name: Optional[str] = None
    website: str
    status: str = 'active'
    email: str = None

class UserInfo:
    def __init__(self, event, db_pool, loop):
        self.event = event
        self.db_pool = db_pool
        self.loop = loop

    def save_user_info_handler(self):
        try:
            # Extract access_token from request parameters (assuming it's in the query string)
            body = json.loads(self.event['body'])
            data = SMBData(**body)
            data.website = extract_domain(data.website)

            # Extract access_token from the JSON body
            authorization_code = body.get('code')

            if not authorization_code:
                return {"message": "Missing Authorization Code"}

            credentials = get_google_credentials(authorization_code)
            email = get_user_details(credentials)

            if email:
                data.email = email

            query_smb = """
            WITH upsert AS (
                INSERT INTO smbs (name, website, email, status, created_at, updated_at)
                VALUES ($1, $2, $3, $4, NOW(), NOW())
                ON CONFLICT (website) DO UPDATE
                SET status = EXCLUDED.status,
                    email = EXCLUDED.email,
                    updated_at = NOW()
                RETURNING id, name, website, email, status, phone, created_at, updated_at
            )
            SELECT id, name, website, email, phone, status
            FROM upsert;
            """

            query_smb_preferences = """
            INSERT INTO smb_preferences (smb_id)
            VALUES ($1)
            ON CONFLICT (smb_id) DO NOTHING
            RETURNING id;
            """

            async def db_operations():
                async with self.db_pool.acquire() as connection:
                    async with connection.transaction():
                        # Insert into smb_info and get the new smb_id
                        smb_result = await connection.fetchrow(query_smb, data.name, data.website, data.email, data.status)
                        smb_result = dict_from_record(smb_result)

                        # Insert into smb_preferences and get the new smb_id
                        await connection.fetchval(query_smb_preferences, smb_result['id'])

                        response = {
                            "id": smb_result['id'],
                            "name": smb_result['name'],
                            "website": smb_result['website'],
                            "email": smb_result['email'],
                            "contact": smb_result['phone']
                        }

                        return response

            return self.loop.run_until_complete(db_operations())
        except Exception as e:
            print(f"Error retrieving user info: {str(e)}")
            raise Exception(f"An error occurred while fetching user info: {str(e)}")


    def create_calendar_event_handler(self):
        try:
            body = json.loads(self.event['body'])

            # Extract access_token from the JSON body
            authorization_code = body.get('code')

            if not authorization_code:
                raise Exception("Missing Authorization Code.")

            credentials = get_google_credentials(authorization_code)
            email = get_user_details(credentials)

            if not email:
                raise Exception(f"User email address not found.")

            # Authenticate user is exists in our DB or not.
            smb_info = self.loop.run_until_complete(self.get_smb_user(email))
            if not smb_info:
                raise Exception(f"User not found.")

            service = build("calendar", "v3", credentials=credentials)
            # Fetch list of calendars
            # calendar_list = service.calendarList().list().execute()

            # Create a new event example
            g_event = {
                'summary': 'Meeting with someone',
                'location': 'Virtual',
                'description': 'A chance to collaborate and learn.',
                'start': {
                    'dateTime': '2024-09-5T09:00:00-07:00',
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': '2024-09-5T10:00:00-07:00',
                    'timeZone': 'America/Los_Angeles',
                },
                'attendees': [
                    {'email': 'amit@logiciel.io'},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }

            event_result = service.events().insert(calendarId='primary', body=g_event).execute()

            credentials_json = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'scopes': credentials.scopes
            }
            data = {"credentials": credentials_json, "event": event_result}
            data = json.dumps(data)

            query_smb_preferences = """
            UPDATE smb_preferences
            SET calendar_settings = $1
            WHERE smb_id = $2
            RETURNING id;
            """

            async def db_operations():
                async with self.db_pool.acquire() as connection:
                    async with connection.transaction():
                        # Insert into smb_preferences.
                        await connection.fetchval(query_smb_preferences, data, smb_info['id'])
                        
                        return {"message": "Calendar Event has been created successfully."}

            return self.loop.run_until_complete(db_operations())
        except Exception as e:
            print(f"Error retrieving user info: {str(e)}")
            raise Exception(f"An error occurred while fetching user info: {str(e)}")

    def authenticate_user(self):
        try:
            body = json.loads(self.event['body'])

            # Extract access_token from the JSON body
            authorization_code = body.get('code')

            if not authorization_code:
                raise Exception("Missing Authorization Code.")

            credentials = get_google_credentials(authorization_code)
            user_details = get_user_details(credentials, email_only=False)
            response = {
                'user_details': user_details,
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
            }

            email = user_details.get('email', None)
            if email is None:
                raise Exception(f"Email not found.")

            if self.get_smb_user(email) is None:
                raise Exception(f"User is not registered.")

            return response
        except Exception as e:
            print(f"Error retrieving user info: {str(e)}")
            raise Exception(f"An error occurred while authenticating user: {str(e)}")

    async def get_smb_user(self, email):
        query_smbs = """
        SELECT id, name, website, email, phone, status
        FROM
            smbs
        WHERE
            email = $1;
        """
        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    result = await connection.fetchrow(query_smbs, email)
                    result = dict_from_record(result)
                    return result

        except Exception as e:
            raise Exception(f"An error occurred while fetching User's info: {str(e)}")
