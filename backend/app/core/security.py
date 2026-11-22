import os
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("JWT_SECRET")
ALGO = "HS256"
EXPIRE_MIN = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MIN),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=[ALGO])