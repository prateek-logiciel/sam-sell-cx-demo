import os
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from asyncpg import create_pool
from urllib.parse import urlparse

load_dotenv()


class SessionData(BaseModel):
    browser_info: Optional[Dict] = None  # JSON object
    location: Optional[str] = None
    ip_address: Optional[str] = None
    name: Optional[str] = None
    website: str
    status: str = 'active'


# Define the lifespan context manager for database connection pool
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await create_pool(
        host=os.getenv("STATE_HOST"),
        user=os.getenv("STATE_USER"),
        password=os.getenv("STATE_PASSWORD"),
        port=os.getenv("STATE_PORT"),
        database=os.getenv("STATE_DATABASE"),
    )
    yield
    await app.state.db_pool.close()


# Define FastAPI application with lifespan
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins if you want to restrict access
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

def extract_domain(url: str) -> str:
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract the netloc (domain) from the parsed URL
    domain = parsed_url.netloc

    # If the domain includes 'www.', remove it
    if domain.startswith('www.'):
        domain = domain[4:]

    return domain

async def visitor_exists(data: SessionData):
    query_visitor = """
    SELECT
        v.id AS visitor_id,
        v.session_id,
        s.id AS smb_id,
        s.name AS smb_name
    FROM
        visitors v
    JOIN
        smbs s ON s.id = v.smb_id
    WHERE
        s.website = $1
        AND v.ip_address = $2;
    """
    try:
        async with app.state.db_pool.acquire() as connection:
            async with connection.transaction():
                # Fetch visitor/smb info for per existing visitor.
                visitor_result = await connection.fetchrow(query_visitor, data.website, data.ip_address)

                return visitor_result

    except Exception as e:
        return format_response(status.HTTP_500_INTERNAL_SERVER_ERROR, {"message": "Internal error raised.", "details": str(e)})


@app.post("/create_session", status_code=status.HTTP_201_CREATED)
async def create_session(data: SessionData):
    query_visitor = """
    INSERT INTO visitors (browser_info, location, ip_address, status, smb_id, session_id)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING id, session_id;
    """

    query_smb = """
    WITH upsert AS (
        INSERT INTO smbs (name, website, status)
        VALUES ($1, $2, $3)
        ON CONFLICT (name, website) DO UPDATE
        SET status = EXCLUDED.status
        RETURNING id, name, website, status
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

    try:
        # extract only the domain from SMB URL.
        data.website = extract_domain(data.website)

        visitor_info = await visitor_exists(data)
        
        if visitor_info:
            return format_response(200, visitor_info)

        async with app.state.db_pool.acquire() as connection:
            async with connection.transaction():
                # Insert into smb_info and get the new smb_id
                smb_result = await connection.fetchrow(query_smb, data.name, data.website, data.status)
                
                # Insert into smb_preferences and get the new smb_id
                await connection.fetchval(query_smb_preferences, smb_result['id'])

                # Insert into visitor using the generated smb_id
                visitor_result = await connection.fetchrow(query_visitor, json.dumps(data.browser_info), data.location, data.ip_address, data.status, smb_result['id'], str(uuid.uuid4()))
                
                response = {
                    "visitor_id": visitor_result['id'],
                    "session_id": visitor_result['session_id'],
                    "smb_id": smb_result['id'],
                    "smb_name": smb_result['name']
                }
                return format_response(200, response)

    except Exception as e:
        return format_response(status.HTTP_500_INTERNAL_SERVER_ERROR, {"message": "Internal error raised.", "details": str(e)})


def format_response(status_code, body):
    return {
        "statusCode": status_code,
        "data": body
    }


def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

    raise TypeError(f"Type {type(obj)} not serializable")
