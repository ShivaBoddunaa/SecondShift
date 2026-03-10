"""
Page routes: Home
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from api.src.utils.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="api/templates")


@router.get("/")
def root(request: Request):
    current_user = get_current_user(request)
    if current_user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("home.html", {"request": request, "user_id": None, "current_user": None})
