from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.routes.auth import router as auth_router
from src.routes.pages import router as pages_router
from src.routes.items import router as items_router
import os

app = FastAPI()

# Mount static files if the directory exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(pages_router)
app.include_router(items_router)





















# from fastapi import FastAPI
# from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
# from src.routes.auth import router as auth_router
# from src.routes.pages import router as pages_router
# from src.routes.items import router as items_router
# import os

# app = FastAPI()

# # Mount static files if the directory exists
# if os.path.exists("static"):
#     app.mount("/static", StaticFiles(directory="static"), name="static")

# app.include_router(auth_router)
# app.include_router(pages_router)
# app.include_router(items_router)

