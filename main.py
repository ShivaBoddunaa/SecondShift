from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from src.routes.auth import router as auth_router


app = FastAPI()
app.include_router(auth_router)