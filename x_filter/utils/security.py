# x_filter/utils/security.py
import bcrypt
import base64
from datetime import datetime, timedelta
from dotenv import load_dotenv
from functools import wraps
import os
import json
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt as jose_jwt, JWTError
import logging
import uuid

from x_filter import Database
load_dotenv()

db = Database()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def authenticate(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logging.log(logging.INFO, f"Token: {token}   first")
        payload = jose_jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        logging.log(logging.INFO, f"Payload: {payload}   second")
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        logging.log(logging.ERROR, f"JWTError: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logging.log(logging.ERROR, f"Unexpected error: {str(e)}")
        raise credentials_exception
    user = db.query("users", user_id)
    return user_id


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return base64.b64encode(hashed).decode("utf-8")

def check_password(hashed_password: str, user_password: str) -> bool:
    hashed_password_bytes = base64.b64decode(hashed_password.encode("utf-8"))
    return bcrypt.checkpw(user_password.encode("utf-8"), hashed_password_bytes)

def generate_tokens(user_id: str):
    access_token_payload = {
        'user_id': user_id,
        'exp': datetime.now() + timedelta(days=30),
        'iat': datetime.now()
    }
    refresh_token_payload = {
        'user_id': user_id,
        'exp': datetime.now() + timedelta(days=365),
        'iat': datetime.now()
    }
    access_token = jose_jwt.encode(access_token_payload, os.getenv("JWT_SECRET"), algorithm='HS256')
    refresh_token = jose_jwt.encode(refresh_token_payload, os.getenv("JWT_SECRET"), algorithm='HS256')
    return access_token, refresh_token

def generate_uuid() -> str:
    return str(uuid.uuid4())

def authenticate_user(func):
    """
    Decorator function to authenticate user using JWT tokens.
    """
    @wraps(func)
    def wrapper(req: func.HttpRequest, *args, **kwargs):
        access_token = req.headers.get('Authorization')
        if not access_token:
            refresh_token = req.headers.get('Refresh-Token')
            if not refresh_token:
                return func.HttpResponse(
                    json.dumps({'error': 'No token provided.'}),
                    status_code=401,
                    mimetype='application/json'
                )
            try:
                payload = jose_jwt.decode(refresh_token, os.getenv("JWT_SECRET"), algorithms=['HS256'])
                user_id = payload['user_id']
                access_token, refresh_token = generate_tokens(user_id)
                kwargs['user_id'] = user_id
                req.headers['Authorization'] = access_token
                req.headers['Refresh-Token'] = refresh_token
                return func(req, *args, **kwargs)
            except jose_jwt.ExpiredSignatureError:
                return func.HttpResponse(
                    json.dumps({'error': 'Refresh token expired.'}),
                    status_code=401,
                    mimetype='application/json'
                )
        else:
            try:
                payload = jose_jwt.decode(access_token, os.getenv("JWT_SECRET"), algorithms=['HS256'])
                user_id = payload['user_id']
                kwargs['user_id'] = user_id
                return func(req, *args, **kwargs)
            except jose_jwt.ExpiredSignatureError:
                return func.HttpResponse(
                    json.dumps({'error': 'Access token expired.'}),
                    status_code=401,
                    mimetype='application/json'
                )
    return wrapper
