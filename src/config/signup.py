from datetime import datetime, timedelta, timezone
from jose import jwt

# IMPORTANT: Change this to a secure random string in production!
SECRET_KEY = "your-super-secret-key-change-in-production-123456789"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 60 * 24  # 24 hours

def create_token(user_id: str) -> str:
    """
    Create JWT token for user authentication
    
    Args:
        user_id: User's UUID from database
        
    Returns:
        Encoded JWT token string
    """
    payload = {
        "sub": str(user_id),  # Convert UUID to string
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token























