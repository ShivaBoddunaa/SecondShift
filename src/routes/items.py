"""
Items routes: Sell item functionality
THIS IS THE FIXED VERSION - Now includes all required fields!
"""
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from src.utils.auth import get_current_user
from src.config.db import db
import os
import shutil
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ========== SELL PAGE ==========
@router.get("/sell")
def sell_page(request: Request):
    """Display sell item form"""
    user_id = get_current_user(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse(
        "sell.html", 
        {"request": request, "user_id": user_id}
    )


# ========== CREATE ITEM (POST) ==========
@router.post("/sell")
async def sell_item(
    request: Request,
    title: str = Form(...),
    description: str = Form(default=""),
    price: int = Form(...),
    contact: str = Form(...),
    negotiable: bool = Form(default=False),
    image: UploadFile = File(None)  # Optional image upload
):
    """
    Create new item for sale
    
    FIXED VERSION - Now includes:
    - Title
    - Description
    - Price
    - Contact details
    - Negotiable option
    - Image upload (optional)
    """
    user_id = get_current_user(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    try:
        # Validate price
        if price < 0:
            return templates.TemplateResponse(
                "sell.html",
                {
                    "request": request,
                    "user_id": user_id,
                    "error": "❌ Price cannot be negative"
                },
                status_code=400
            )
        
        # Handle image upload
        image_url = None
        if image and image.filename:
            try:
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_extension = os.path.splitext(image.filename)[1]
                filename = f"item_{timestamp}{file_extension}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                
                # Save file
                with open(filepath, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                # Store relative path for database
                image_url = f"/static/uploads/{filename}"
                print(f"✅ Image saved: {image_url}")
                
            except Exception as e:
                print(f"⚠️ Image upload failed: {str(e)}")
                # Continue without image
        
        # Insert item into database
        response = db.table("items").insert({
            "title": title,
            "description": description,
            "price": price,
            "contact": contact,
            "negotiable": negotiable,
            "image_url": image_url,
            "seller_id": user_id
        }).execute()
        
        print(f"✅ Item created successfully: {title}")
        
        # Redirect to dashboard
        return RedirectResponse("/dashboard", status_code=302)
    
    except Exception as e:
        # Log detailed error
        print(f"❌ Error creating item: {str(e)}")
        
        # Return user-friendly error page
        return templates.TemplateResponse(
            "sell.html",
            {
                "request": request,
                "user_id": user_id,
                "error": f"Failed to create item: {str(e)}"
            },
            status_code=500
        )


# ========== MY ITEMS PAGE (BONUS) ==========
@router.get("/my-items")
def my_items_page(request: Request):
    """Display user's own items"""
    user_id = get_current_user(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)
    
    try:
        # Fetch user's items
        response = db.table("items").select("*").eq("seller_id", user_id).order("created_at", desc=True).execute()
        items = response.data if response.data else []
        
        return templates.TemplateResponse(
            "my_items.html",
            {
                "request": request,
                "user_id": user_id,
                "items": items
            }
        )
    except Exception as e:
        print(f"❌ Error fetching items: {str(e)}")
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)



























