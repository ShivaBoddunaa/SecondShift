from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from supabase import create_client
from fastapi.responses import RedirectResponse, JSONResponse

# from src.config.db import db


router = APIRouter()
# templates = Jinja2Templates(directory="templates")


@router.get('/')
def home():
    return {"hello":"hello"}