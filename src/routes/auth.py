from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import bcrypt  
from src.config.db import db
from src.config.signup import create_token

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# ---------- LOGIN PAGE ----------
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "user_id": None})


# ---------- LOGIN ACTION ----------
@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        user = db.table("users").select("*").eq("email", email).execute()

        if not user.data:
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password", "user_id": None}, status_code=400)

        # ✅ Verify password with bcrypt directly
        stored_hash = user.data[0]["password_hash"].encode('utf-8')
        if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password", "user_id": None}, status_code=400)

        token = create_token(user.data[0]["id"])
        response = RedirectResponse("/dashboard", status_code=302)
        response.set_cookie("token", token, httponly=True)
        return response
    
    except Exception as e:
        print(f"❌ Login Error: {str(e)}")
        return templates.TemplateResponse("login.html", {"request": request, "error": f"Login failed: {str(e)}", "user_id": None}, status_code=500)


# ---------- SIGNUP PAGE ----------
@router.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "user_id": None})


# ---------- SIGNUP ACTION ----------
@router.post("/signup")
def signup(request: Request, email: str = Form(...), password: str = Form(...), college: str = Form(...)):
    try:
        # Check if user already exists
        existing = db.table("users").select("*").eq("email", email).execute()
        if existing.data:
            return templates.TemplateResponse("signup.html", {"request": request, "error": "Email already registered", "user_id": None})
        
        # ✅ Hash password with bcrypt directly (automatically handles 72-byte limit)
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert into database
        db.table("users").insert({
            "email": email,
            "password_hash": hashed.decode('utf-8'),  # Store as string
            "college": college
        }).execute()

        print(f"✅ User created: {email}")
        return RedirectResponse("/login", status_code=302)
    
    except Exception as e:
        print(f"❌ Signup Error: {str(e)}")
        return templates.TemplateResponse("signup.html", {"request": request, "error": f"Signup failed: {str(e)}", "user_id": None}, status_code=500)


# ---------- LOGOUT ----------
@router.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie("token")
    return response