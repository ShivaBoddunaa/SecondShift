"""
Page routes: Dashboard, Buy page, Home
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from src.utils.auth import get_current_user
from src.config.db import db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# ========== ROOT ROUTE ==========
@router.get("/")
def root(request: Request):
    """
    Homepage - redirect based on login status
    """
    user_id = get_current_user(request)
    if user_id:
        return RedirectResponse("/dashboard", status_code=302)
    return RedirectResponse("/login", status_code=302)


# ========== DASHBOARD ==========
@router.get("/dashboard")
def dashboard(request: Request):
    """
    User dashboard - main landing page after login
    """
    user_id = get_current_user(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user_id": user_id}
    )


# ========== BUY PAGE ==========
@router.get("/buy")
def buy_page(request: Request):
    """
    Browse all available items for sale
    Shows items with seller information
    """
    user_id = get_current_user(request)
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    try:
        # Fetch all items from Supabase
        items_response = db.table("items").select("*").order("created_at", desc=True).execute()
        items = items_response.data if items_response.data else []

        # Fetch seller details for each item
        items_with_sellers = []
        for item in items:
            seller_id = item.get("seller_id")
            
            # Get seller information
            seller_response = db.table("users").select("id, email, college").eq("id", seller_id).execute()
            
            if seller_response.data and len(seller_response.data) > 0:
                seller = seller_response.data[0]
            else:
                seller = {"email": "Unknown", "college": "Unknown"}
            
            # Combine item and seller data
            item_full = {
                **item,
                "seller_email": seller.get("email", "N/A"),
                "seller_college": seller.get("college", "N/A")
            }
            items_with_sellers.append(item_full)
        
        print(f"✅ Fetched {len(items_with_sellers)} items for buy page")

        return templates.TemplateResponse(
            "buy.html",
            {
                "request": request, 
                "items": items_with_sellers, 
                "user_id": user_id
            }
        )
        
    except Exception as e:
        print(f"❌ Error fetching items: {str(e)}")
        return templates.TemplateResponse(
            "buy.html",
            {
                "request": request,
                "items": [],
                "user_id": user_id,
                "error": f"Error loading items: {str(e)}"
            }
        )
































