from fastapi import Request
from jose import jwt, JWTError
from src.config.signup import SECRET_KEY, ALGORITHM


def get_current_user(request: Request):
    """
    Extract and verify JWT token from cookies
    
    Args:
        request: FastAPI request object
        
    Returns:
        User ID (UUID string) if valid token, None otherwise
    """
    # Get token from cookie
    token = request.cookies.get("token")
    
    if not token:
        return None

    try:
        # Decode and verify JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract user ID from token
        user_id = payload.get("sub")
        
        if not user_id:
            return None
            
        return user_id
        
    except JWTError as e:
        print(f"⚠️ JWT Error: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Auth error: {str(e)}")
        return None











