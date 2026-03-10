"""
Items routes: Sell, Buy, Edit, Delete with permission checks
"""
from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from api.src.utils.auth import get_current_user
from api.src.config.db import db
import os
import shutil
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="api/templates")

# Use /tmp for Vercel (read-only filesystem), fallback to static/uploads locally
UPLOAD_DIR = "/tmp/uploads" if os.environ.get("VERCEL") else "static/uploads"
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except OSError:
    pass


@router.get("/sell")
def sell_page(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse(
        "sell.html",
        {"request": request, "user_id": current_user["id"], "current_user": current_user}
    )


@router.post("/sell")
async def sell_item(
    request: Request,
    title: str = Form(...),
    description: str = Form(default=""),
    price: int = Form(...),
    contact: str = Form(...),
    negotiable: bool = Form(default=False),
    image: UploadFile = File(None)
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    user_id = current_user["id"]

    try:
        if price < 0:
            return templates.TemplateResponse(
                "sell.html",
                {"request": request, "user_id": user_id, "current_user": current_user, "error": "Price cannot be negative"},
                status_code=400
            )

        image_url = None
        if image and image.filename:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_extension = os.path.splitext(image.filename)[1]
                filename = f"item_{timestamp}{file_extension}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                image_url = f"/static/uploads/{filename}"
            except Exception as e:
                print(f"Image upload failed: {str(e)}")

        db.table("items").insert({
            "title": title,
            "description": description,
            "price": price,
            "contact": contact,
            "negotiable": negotiable,
            "image_url": image_url,
            "seller_id": user_id
        }).execute()

        return RedirectResponse("/dashboard", status_code=302)

    except Exception as e:
        print(f"Error creating item: {str(e)}")
        return templates.TemplateResponse(
            "sell.html",
            {"request": request, "user_id": user_id, "current_user": current_user, "error": f"Failed to create item: {str(e)}"},
            status_code=500
        )


@router.get("/buy")
def buy_page(request: Request):
    current_user = get_current_user(request)

    try:
        response = db.table("items").select("*").execute()
        items = response.data if response.data else []
    except Exception as e:
        print(f"BUY PAGE ERROR: {e}")
        items = []

    return templates.TemplateResponse("buy.html", {
        "request": request,
        "items": items,
        "user_id": current_user["id"] if current_user else None,
        "current_user": current_user,
        "category": "",
        "min_price": "",
        "max_price": "",
        "condition": "",
        "search": "",
        "sort": "newest"
    })


@router.delete("/item/{item_id}/delete")
async def delete_item(item_id: str, request: Request):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Login required")

    try:
        item_response = db.table("items").select("*").eq("id", item_id).execute()
        if not item_response.data:
            raise HTTPException(status_code=404, detail="Item not found")

        item = item_response.data[0]

        is_admin = current_user.get("role") == "admin"
        is_seller = str(item.get("seller_id")) == str(current_user.get("id"))

        if not (is_admin or is_seller):
            raise HTTPException(status_code=403, detail="You do not have permission to delete this listing")

        db.table("items").delete().eq("id", item_id).execute()
        return JSONResponse({"status": "deleted", "item_id": item_id})

    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/item/{item_id}")
async def edit_item(
    item_id: str,
    request: Request,
    title: str = Form(...),
    description: str = Form(default=""),
    price: int = Form(...),
    contact: str = Form(...)
):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Login required")

    try:
        item_response = db.table("items").select("*").eq("id", item_id).execute()
        if not item_response.data:
            raise HTTPException(status_code=404, detail="Item not found")

        item = item_response.data[0]

        is_admin = current_user.get("role") == "admin"
        is_seller = str(item.get("seller_id")) == str(current_user.get("id"))

        if not (is_admin or is_seller):
            raise HTTPException(status_code=403, detail="You do not have permission to edit this listing")

        db.table("items").update({
            "title": title,
            "description": description,
            "price": price,
            "contact": contact
        }).eq("id", item_id).execute()

        return JSONResponse({"status": "updated", "item_id": item_id})

    except HTTPException:
        raise
    except Exception as e:
        print(f"Edit error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/item/{item_id}/status")
async def update_item_status(item_id: str, request: Request, status: str = Form(...)):
    current_user = get_current_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Login required")

    try:
        item_response = db.table("items").select("*").eq("id", item_id).execute()
        if not item_response.data:
            raise HTTPException(status_code=404, detail="Item not found")

        item = item_response.data[0]

        is_admin = current_user.get("role") == "admin"
        is_seller = str(item.get("seller_id")) == str(current_user.get("id"))

        if not (is_admin or is_seller):
            raise HTTPException(status_code=403, detail="Permission denied")

        db.table("items").update({"status": status}).eq("id", item_id).execute()
        return JSONResponse({"success": True, "status": status})

    except HTTPException:
        raise
    except Exception as e:
        print(f"Status update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-items")
def my_items_page(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    user_id = current_user["id"]

    try:
        response = db.table("items").select("*").eq("seller_id", user_id).order("created_at", desc=True).execute()
        items = response.data if response.data else []
        return templates.TemplateResponse(
            "my_items.html",
            {"request": request, "user_id": user_id, "current_user": current_user, "items": items}
        )
    except Exception as e:
        print(f"Error fetching items: {str(e)}")
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)
