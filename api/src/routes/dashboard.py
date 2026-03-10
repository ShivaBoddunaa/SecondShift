from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from src.utils.auth import get_current_user, require_admin
from src.config.db import db
from datetime import datetime, timezone
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard")
def dashboard(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse("/login", status_code=302)

    user_id = current_user["id"]

    try:
        user_response = db.table("users").select("*").eq("id", user_id).execute()
        user_data = user_response.data[0] if user_response.data else {"email": "Unknown", "college": "Unknown"}

        name = user_data.get("fullname") or user_data.get("email", "").split("@")[0]
        user_data["name"] = name.title()

        items_response = db.table("items").select("*").eq("seller_id", user_id).order("created_at", desc=True).execute()
        listings = items_response.data if items_response.data else []

        stats = {
            "active_listings": 0,
            "total_views": 0,
            "saved_items": 0,
            "college": user_data.get("college", "Unknown")
        }

        for item in listings:
            status = item.get("status", "active")
            item["status"] = status
            if status == "active":
                stats["active_listings"] += 1
            stats["total_views"] += item.get("views", 0)
            if item.get("created_at"):
                try:
                    dt = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
                    item["formatted_date"] = dt.strftime("%b %d, %Y")
                except:
                    item["formatted_date"] = item["created_at"].split("T")[0]
            else:
                item["formatted_date"] = "N/A"

        try:
            wishlist_response = db.table("wishlist").select("id", count="exact").eq("user_id", user_id).execute()
            stats["saved_items"] = wishlist_response.count if hasattr(wishlist_response, 'count') and wishlist_response.count else 0
        except:
            stats["saved_items"] = 0

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user_id": user_id,
                "current_user": current_user,
                "user": user_data,
                "listings": listings,
                "stats": stats
            }
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Dashboard error: {str(e)}")
        print(error_trace)
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user_id": user_id,
                "current_user": current_user,
                "user": {"name": "User", "college": "Unknown"},
                "listings": [],
                "stats": {"active_listings": 0, "total_views": 0, "saved_items": 0, "college": "Unknown"},
                "error": str(e),
                "debug_info": error_trace
            }
        )


@router.get("/admin")
def admin_panel(request: Request):
    current_user = require_admin(request)
    user_id = current_user["id"]

    try:
        # Fetch all users
        users_response = db.table("users").select("*").order("created_at", desc=True).execute()
        all_users = users_response.data if users_response.data else []

        # Fetch all items
        items_response = db.table("items").select("*").order("created_at", desc=True).execute()
        all_items = items_response.data if items_response.data else []

        # Format dates
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        new_today = 0

        for item in all_items:
            if item.get("created_at"):
                try:
                    dt = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
                    item["formatted_date"] = dt.strftime("%b %d, %Y")
                    if dt.strftime("%Y-%m-%d") == today_str:
                        new_today += 1
                except:
                    item["formatted_date"] = item["created_at"].split("T")[0]
            else:
                item["formatted_date"] = "N/A"

        for user in all_users:
            if user.get("created_at"):
                try:
                    dt = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
                    user["formatted_date"] = dt.strftime("%b %d, %Y")
                except:
                    user["formatted_date"] = user["created_at"].split("T")[0]
            else:
                user["formatted_date"] = "N/A"

        active_count = sum(1 for i in all_items if i.get("status", "active") == "active")
        recent_users = all_users[:10]

        admin_stats = {
            "total_users": len(all_users),
            "total_listings": len(all_items),
            "active_listings": active_count,
            "new_today": new_today
        }

        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "user_id": user_id,
                "current_user": current_user,
                "all_users": all_users,
                "all_items": all_items,
                "recent_users": recent_users,
                "admin_stats": admin_stats
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Admin panel error: {str(e)}")
        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "user_id": user_id,
                "current_user": current_user,
                "all_users": [],
                "all_items": [],
                "recent_users": [],
                "admin_stats": {"total_users": 0, "total_listings": 0, "active_listings": 0, "new_today": 0},
                "error": str(e)
            }
        )


@router.put("/admin/user/{user_id}/role")
async def update_user_role(user_id: str, request: Request):
    current_user = require_admin(request)

    try:
        body = await request.json()
        new_role = body.get("role", "user")

        if new_role not in ("user", "admin"):
            raise HTTPException(status_code=400, detail="Invalid role")

        db.table("users").update({"role": new_role}).eq("id", user_id).execute()
        return JSONResponse({"status": "updated", "user_id": user_id, "role": new_role})

    except HTTPException:
        raise
    except Exception as e:
        print(f"Role update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/user/{user_id}")
async def delete_user(user_id: str, request: Request):
    current_user = require_admin(request)

    try:
        # Don't allow deleting yourself
        if str(user_id) == str(current_user["id"]):
            raise HTTPException(status_code=400, detail="Cannot delete your own account")

        # Delete user's items first
        db.table("items").delete().eq("seller_id", user_id).execute()
        # Delete user
        db.table("users").delete().eq("id", user_id).execute()

        return JSONResponse({"status": "deleted", "user_id": user_id})

    except HTTPException:
        raise
    except Exception as e:
        print(f"User delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
