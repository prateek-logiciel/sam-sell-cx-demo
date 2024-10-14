import json
import uuid
from datetime import datetime, timedelta
from utils.jwt_utils import generate_token, token_required, hash_password, verify_password
from utils.google_calendar import *
from utils.helper import dict_from_record
from repositories.smb_preference_repository import SMBPreferences as SMBPreferencesRepository
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class UserInfo:
    def __init__(self, event, db_pool, loop):
        self.event = event
        self.db_pool = db_pool
        self.loop = loop
        self.user_id = None

    async def authenticate_user(self):
        try:
            body = json.loads(self.event['body'])

            # Extract access_token from the JSON body
            authorization_code = body.get('code')
            user_email = body.get('email')
            password = body.get('password')
            redirect_uri = body.get('redirect_uri', None)
            user_details = {}

            if authorization_code:
                credentials = get_google_credentials(authorization_code, redirect_uri)
                user_details = get_user_details(credentials, email_only=False)

                email = user_details.get('email', None)
                if email is None:
                    raise Exception(f"Email not found.")

                smb_result = await self.get_smb_user(email)
                if smb_result is None:
                    raise Exception(f"User is not registered.")

                await self.update_smb_token(smb_result.get('id', None), credentials)
            elif user_email and password:
                smb_result = await self.get_smb_user(user_email)
                if smb_result is None:
                    raise Exception(f"User is not registered.")
                
                if not verify_password(smb_result['password'], password):
                    raise Exception(f"User's Email/Password mismatch.")

            token = generate_token(smb_result['id'], smb_result['email'])
            return user_details | smb_result | {"token": token}
        except Exception as e:
            print(f"Error retrieving user info: {str(e)}")
            raise Exception(f"An error occurred while authenticating user: {str(e)}")

    async def get_smb_user(self, email):
        query_smbs = """
        SELECT *
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

    async def get_smb_user_by_id(self, id):
        query_smbs = """
        SELECT *
        FROM
            smbs
        WHERE
            id = $1;
        """
        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    result = await connection.fetchrow(query_smbs, id)
                    result = dict_from_record(result)
                    return result

        except Exception as e:
            raise Exception(f"An error occurred while fetching User's info: {str(e)}")

    async def update_smb_token(self, id, credentials):
        # Query to update refresh_token and access_token
        update_tokens_query = """
            UPDATE smbs
            SET refresh_token = $2, access_token = $3, updated_at = now()
            WHERE id = $1;
        """

        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    await connection.execute(update_tokens_query, id, credentials.refresh_token, credentials.token)
                    return True

        except Exception as e:
            raise Exception(f"An error occurred while updating User's info: {str(e)}")

    
    async def forget_password(self):
        body = json.loads(self.event['body'])
        email = body.get('email')
        if email is None:
            raise Exception("Email is required.")
        
        # Generate reset token
        reset_token = str(uuid.uuid4())
        expiration_time = datetime.utcnow() + timedelta(hours=4)
        
        # Query to insert password reset token
        insert_token_query = """
            INSERT INTO password_reset_tokens (email, token, expiration_time)
            VALUES ($1, $2, $3)
        """

        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    await connection.execute(insert_token_query, email, reset_token, expiration_time)

            # Send email with reset link
            reset_link = f"{os.getenv('SMB_DOMAIN')}/reset-password?token={reset_token}"
            subject = 'Password Reset Request'
            body = f'Click the following link to reset your password: {reset_link}'

            await self.send_email(email, subject, body)

            return True
        except Exception as e:
            raise Exception(f"An error occurred while processing forget password request: {str(e)}")

    async def reset_password(self):
        body = json.loads(self.event['body'])
        token = body['token']
        new_password = body['new_password']
        
        # Verify token and get associated email
        verify_token_query = """
            SELECT email FROM password_reset_tokens
            WHERE token = $1 AND expiration_time > NOW()
        """

        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    result = await connection.fetchrow(verify_token_query, token)
                    if not result:
                        raise Exception("Invalid or expired token.")

                    email = result['email']

                    hashed = hash_password(new_password)
                    # Update password
                    update_password_query = "UPDATE smbs SET password = $1, updated_at = NOW() WHERE email = $2"
                    await connection.execute(update_password_query, hashed, email)

                    # Delete used token
                    delete_token_query = "DELETE FROM password_reset_tokens WHERE token = $1"
                    await connection.execute(delete_token_query, token)

            return True
        except Exception as e:
            raise Exception(f"An error occurred while resetting password: {str(e)}")
        
    async def send_email(self, to_email, subject, body):
        # Email configuration
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('SMTP_FROM_EMAIL')

        # Create message
        message = MIMEMultipart()
        message['From'] = from_email
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

    @token_required
    async def get_calendar_list(self):
        try:
            result = await self.get_smb_user_by_id(self.user_id)
            response = get_calendar_list(result)
            smb_preference_repo = SMBPreferencesRepository(self.event, self.db_pool, self.loop, self.user_id)
            await smb_preference_repo.update_calendar_settings({"calendars": response})

            return response
        except Exception as e:
            print(f"Error retrieving user info: {str(e)}")
            raise Exception(f"An error occurred while calendar processing: {str(e)}")