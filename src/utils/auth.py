from fastapi import Request, HTTPException, Depends
from jose import jwt, JWTError
from src.config.signup import SECRET_KEY, ALGORITHM


def get_current_user(request: Request):
    token = request.cookies.get("token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        return {
            "id": payload.get("sub"),
            "email": payload.get("email", ""),
            "role": payload.get("role", "user")
        }
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        return None
    except Exception as e:
        print(f"Auth error: {str(e)}")
        return None


def require_admin(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Login required")
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")
    return current_user
