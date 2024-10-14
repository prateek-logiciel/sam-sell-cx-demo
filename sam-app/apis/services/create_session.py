import uuid
import json
from typing import Dict, Optional
from pydantic import BaseModel
from utils.helper import *


class SessionData(BaseModel):
    browser_info: Optional[Dict] = None  # JSON object
    location: Optional[str] = None
    ip_address: Optional[str] = None
    name: Optional[str] = None
    source: Optional[str] = 'ew'
    website: str
    status: str = 'active'
    email: str = None
    phone: str = None
    is_email_verified: Optional[bool] = True


class ContactData(BaseModel):
    visitor_contact: str
    smb_contact: str
    source: Optional[str] = 'voip'
    status: Optional[str] = 'active'
    is_phone_verified: Optional[bool] = True

class CreateSession:
    def __init__(self, event, db_pool, loop):
        self.event = event
        self.db_pool = db_pool
        self.loop = loop
        self.user_id = None

    async def session_exists(self, data: SessionData):
        query_visitor = """
        SELECT *
        FROM
            visitors v
        WHERE
            v.ip_address = $1;
        """
        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    result = await connection.fetchrow(query_visitor, data.ip_address)
                    return result

        except Exception as e:
            raise Exception(f"An error occurred while fetching session info: {str(e)}")

    async def visitor_exists(self, data: SessionData):
        query_visitor = """
        SELECT *
        FROM
            visitors v
        WHERE
            v.ip_address = $1
            and (v.email = $2 AND $2 != '')
            and (v.phone = $3 AND $3 != '');
        """
        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    result = await connection.fetchrow(query_visitor, data.ip_address, data.email, data.phone)
                    return result

        except Exception as e:
            raise Exception(f"An error occurred while fetching visitor info: {str(e)}")

    async def create_session_handler(self):
        try:
            body = json.loads(self.event['body'])
            data = SessionData(**body)

            query_visitor = """
            INSERT INTO visitors (browser_info, location, ip_address, status, smb_id, session_id, email, phone, is_email_verified, source, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
            RETURNING id, session_id, smb_id, name, email, source, is_phone_verified, phone, created_at, updated_at;
            """

            query_smb = """
            WITH upsert AS (
                INSERT INTO smbs (name, website, status, created_at, updated_at)
                VALUES ($1, $2, $3, NOW(), NOW())
                ON CONFLICT (website) DO UPDATE
                SET status = EXCLUDED.status,
                    updated_at = NOW()
                RETURNING id, name, website, status, created_at, updated_at
            )
            SELECT id, name, website, status
            FROM upsert;
            """

            query_smb_preferences = """
            INSERT INTO smb_preferences (smb_id)
            VALUES ($1)
            ON CONFLICT (smb_id) DO NOTHING
            RETURNING id;
            """

            # extract only the domain from SMB URL.
            data.website = extract_domain(data.website)

            session_info = await self.session_exists(data)
            visitor_info = await self.visitor_exists(data)

            if session_info:
                print("In Session")
                result = dict_from_record(session_info)
                return self.set_response(result)

            if visitor_info:
                print("In Visitor")
                result = dict_from_record(visitor_info)
                return self.set_response(result)

            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    # Insert into smb_info and get the new smb_id
                    smb_result = await connection.fetchrow(query_smb, data.name, data.website, data.status)

                    # Insert into smb_preferences and get the new smb_id
                    await connection.fetchval(query_smb_preferences, smb_result['id'])

                    # Insert into visitor using the generated smb_id
                    visitor_result = await connection.fetchrow(query_visitor, json.dumps(data.browser_info), data.location, data.ip_address, data.status, smb_result['id'], str(uuid.uuid4()), data.email, data.phone, data.is_email_verified, data.source)
                    visitor_result = dict_from_record(visitor_result)

                    return self.set_response(visitor_result)
        except Exception as e:
            raise Exception(f"An error occurred while creating session: {str(e)}")

    async def create_contact_session_handler(self):
        try:
            body = json.loads(self.event['body'])
            data = ContactData(**body)

            query_visitor = """
            WITH upsert AS (
                INSERT INTO visitors (status, smb_id, session_id, phone, is_phone_verified, source, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
                ON CONFLICT (phone, smb_id) DO UPDATE
                SET updated_at = NOW(),
                session_id = $3,
                source = $6,
                is_phone_verified = $5
                RETURNING id, session_id, smb_id, name, email, phone, source, is_phone_verified, created_at, updated_at
            )
            SELECT id, session_id, smb_id, name, email, phone, source, is_phone_verified, created_at, updated_at
            FROM upsert;
            """

            smb_result = await self.get_smb_user_by_phone(data.smb_contact)
            if not smb_result:
                raise Exception(f"User not found.")

            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    # Insert into visitor using the generated smb_id
                    visitor_result = await connection.fetchrow(query_visitor, data.status, smb_result['id'], str(uuid.uuid4()), data.visitor_contact, data.is_phone_verified, data.source)
                    visitor_result = dict_from_record(visitor_result)

                    response = {
                        "id": visitor_result['id'],
                        "session_id": visitor_result['session_id'],
                        "name": visitor_result['name'],
                        "email": visitor_result['email'],
                        "contact": visitor_result['phone'],
                        "source": visitor_result['source'],
                        "is_phone_verified": visitor_result['is_phone_verified'],
                        "created_at": visitor_result['created_at'],
                        "updated_at": visitor_result['updated_at'],
                        "smb_id": smb_result['id'],
                        "smb_contact": smb_result['phone']
                    }
                    return response
        except Exception as e:
            print(e)
            raise Exception(f"An error occurred while creating session: {str(e)}")


    async def get_smb_user_by_phone(self, phone):
        query_smbs = """
        SELECT id, name, website, email, phone, status
        FROM
            smbs
        WHERE
            phone = $1;
        """
        try:
            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    result = await connection.fetchrow(query_smbs, phone)
                    result = dict_from_record(result)
                    return result

        except Exception as e:
            raise Exception(
                f"An error occurred while fetching User's info: {str(e)}")

    def set_response(self, response):
        return {
            "id": response['id'],
            "smb_id": response['smb_id'],
            "session_id": response['session_id'],
            "name": response['name'],
            "email": response['email'],
            "contact": response['phone'],
            "source": response['source'],
            "is_phone_verified": response['is_phone_verified'],
            "created_at": response['created_at'],
            "updated_at": response['updated_at'],
        }
