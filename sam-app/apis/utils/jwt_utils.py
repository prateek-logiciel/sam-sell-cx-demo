import jwt
import datetime
import os
import json
import uuid
from functools import wraps
from dotenv import load_dotenv
import bcrypt
import hashlib
import base64

load_dotenv()
JWT_SECRET = os.getenv('JWT_SECRET')
SECRET_KEY = os.getenv('SECRET_KEY')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 3600  # 1 hour


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def hash_password(password: str) -> tuple[bytes, bytes]:
    """
    Hash a password using bcrypt.
    
    :param password: The password to hash
    :return: Hash
    """

    # Create a unique input for each password, influenced by SECRET_KEY
    unique_input = hashlib.sha256(SECRET_KEY.encode() + password.encode()).hexdigest()

    # Use bcrypt's built-in salt generation
    salt = bcrypt.gensalt(rounds=12)

    # Hash the unique input
    hashed = bcrypt.hashpw(unique_input.encode('utf-8'), salt)

    return base64.b64encode(hashed).decode('utf-8')

def verify_password(stored_hash: str, password: str) -> bool:
    """
    Verify a password against its stored hash.
    
    :param password: The password to check
    :param stored_hash: The stored hashed password (base64 encoded string)
    :return: True if the password matches, False otherwise
    """
    unique_input = hashlib.sha256(SECRET_KEY.encode() + password.encode()).hexdigest()
    stored_hash_bytes = base64.b64decode(stored_hash.encode('utf-8'))
    return bcrypt.checkpw(unique_input.encode('utf-8'), stored_hash_bytes)

def generate_token(user_id: int, email: str):
    payload = {
        'user_id': str(user_id),
        'email': email,
        'jti': str(uuid.uuid4()),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS),
        'iat': datetime.datetime.utcnow(),
    }

    return jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)

def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload['user_id'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired", 401)
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token", 401)

def token_required(f):
    @wraps(f)
    async def decorated(self, *args, **kwargs):
        token = extract_token(self.event)
        if not token:
            raise AuthenticationError("Token is missing", 401)

        try:
            self.user_id = decode_token(token)
            return await f(self, *args, **kwargs)
        except AuthenticationError as e:
            raise e

    return decorated

def extract_token(event):
    headers = event.get('headers', {})
    if 'Authorization' in headers:
        try:
            return headers['Authorization'].split(" ")[1]
        except IndexError:
            return None
    
    if event.get('body'):
        try:
            body = json.loads(event['body'])
            return body.get('token')
        except json.JSONDecodeError:
            return None
    
    return None

