
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.routes.auth import router as auth_router
from src.routes.pages import router as pages_router
from src.routes.items import router as items_router
import os
import uvicorn

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(auth_router)
app.include_router(pages_router)
app.include_router(items_router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)


















# from fastapi import FastAPI
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


# import os
# import uvicorn

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8000))
#     uvicorn.run("main:app", host="0.0.0.0", port=port)


















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

