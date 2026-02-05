import jwt
import os
from models.pymodel import token_payload
from datetime import datetime, timedelta

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this")  
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")  

def generate_token(data: token_payload, expires_delta: timedelta = timedelta(hours=24)):
    """Generate a JWT token with expiration"""
    try:
        payload = data.model_dump()
        payload["exp"] = datetime.utcnow() + expires_delta
        token = jwt.encode(payload=payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    except Exception as e:
        print(f"Token generation error: {e}")
        return None

def verify_token(token: str):
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM])
        data = token_payload(**payload)
        return data
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None
    except Exception as e:
        print(f"Token verification error: {e}")
        return None