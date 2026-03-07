from datetime import datetime, timedelta, timezone
from jose import jwt

SECRET_KEY = "your-super-secret-key-change-in-production-123456789"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 60 * 24

def create_token(user_id: str, email: str = "", role: str = "user") -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
