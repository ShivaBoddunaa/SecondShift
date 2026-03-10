from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import bcrypt  
from api.src.config.db import db
from api.src.config.signup import create_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "user_id": None, "current_user": None})


@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        user = db.table("users").select("*").eq("email", email).execute()

        if not user.data:
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password", "user_id": None, "current_user": None}, status_code=400)

        stored_hash = user.data[0]["password_hash"].encode('utf-8')
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password", "user_id": None, "current_user": None}, status_code=400)

        user_data = user.data[0]
        user_role = user_data.get("role", "user")
        user_email = user_data.get("email", "")

        token = create_token(user_data["id"], email=user_email, role=user_role)
        response = RedirectResponse("/dashboard", status_code=302)
        response.set_cookie("token", token, httponly=True)
        return response
    
    except Exception as e:
        print(f"Login Error: {str(e)}")
        return templates.TemplateResponse("login.html", {"request": request, "error": f"Login failed: {str(e)}", "user_id": None, "current_user": None}, status_code=500)


@router.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "user_id": None, "current_user": None})


@router.post("/signup")
def signup(request: Request, email: str = Form(...), password: str = Form(...), college: str = Form(...), fullname: str = Form(default=""), role: str = Form(default="user")):
    try:
        # Check if email exists
        existing = db.table("users").select("*").eq("email", email).execute()
        if existing.data:
            return templates.TemplateResponse("signup.html", {"request": request, "error": "Email already registered", "user_id": None, "current_user": None})
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Prepare user data
        user_data = {
            "email": email,
            "password_hash": hashed.decode('utf-8'),
            "college": college
        }

        # DYNAMIC SCHEMA CHECK: Fetch existing columns to avoid insert errors
        try:
            sample = db.table("users").select("*").limit(1).execute()
            if sample.data:
                available_cols = sample.data[0].keys()
                # Only add columns that actually exist in the DB
                if "fullname" in available_cols:
                    user_data["fullname"] = fullname
                elif "full_name" in available_cols:
                    user_data["full_name"] = fullname
                
                if "role" in available_cols:
                    user_data["role"] = role
            else:
                # If table is empty, we must try a safe insert or default to what we know
                # Usually best to just try to add these and catch the specific error
                user_data["fullname"] = fullname
                user_data["role"] = role
        except:
            # Fallback to standard if check fails
            user_data["fullname"] = fullname
            user_data["role"] = role

        try:
            db.table("users").insert(user_data).execute()
        except Exception as insert_error:
            # Final fallback: Try a bare-minimum insert if above failed
            if "fullname" in str(insert_error) or "role" in str(insert_error):
                print("Schema mismatch detected, retrying with minimum data...")
                minimal_data = {
                    "email": email,
                    "password_hash": hashed.decode('utf-8'),
                    "college": college
                }
                db.table("users").insert(minimal_data).execute()
            else:
                raise insert_error

        print(f"User created: {email}")
        return RedirectResponse("/login", status_code=302)
    
    except Exception as e:
        print(f"Signup Error: {str(e)}")
        return templates.TemplateResponse("signup.html", {"request": request, "error": f"Signup failed: {str(e)}", "user_id": None, "current_user": None}, status_code=500)


@router.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie("token")
    return response
