from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from api.src.routes.auth import router as auth_router
from api.src.routes.pages import router as pages_router
from api.src.routes.items import router as items_router
from api.src.routes.dashboard import router as dashboard_router

app = FastAPI()

if os.path.exists("api/src/static"):
    app.mount("/static", StaticFiles(directory="api/src/static"), name="static")
elif os.path.exists("src/static"):
    app.mount("/static", StaticFiles(directory="api/src/static"), name="static")

app.include_router(auth_router)
app.include_router(pages_router)
app.include_router(items_router)
app.include_router(dashboard_router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)










# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# import os
# import uvicorn
# from dotenv import load_dotenv

# load_dotenv() 

# from api.src.routes.auth import router as auth_router
# from api.src.routes.pages import router as pages_router
# from api.src.routes.items import router as items_router
# from api.src.routes.dashboard import router as dashboard_router

# app = FastAPI()

# app.mount("/static", StaticFiles(directory="api/src/static"), name="static")

# app.include_router(auth_router)
# app.include_router(pages_router)
# app.include_router(items_router)
# app.include_router(dashboard_router)

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8000))
#     uvicorn.run("main:app", host="0.0.0.0", port=port)
















# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from api.src.routes.auth import router as auth_router
# from api.src.routes.pages import router as pages_router
# from api.src.routes.items import router as items_router
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
# from api.src.routes.auth import router as auth_router
# from api.src.routes.pages import router as pages_router
# from api.src.routes.items import router as items_router
# import os

# app = FastAPI()

# # Mount static files if the directory exists
# if os.path.exists("static"):
#     app.mount("/static", StaticFiles(directory="static"), name="static")

# app.include_router(auth_router)
# app.include_router(pages_router)
# app.include_router(items_router)

