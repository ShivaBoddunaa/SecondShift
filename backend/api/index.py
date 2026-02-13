from fastapi import FastAPI
from ..database import supabase

app = FastAPI(title="SecondShift API")

@app.get("/")
def root():
    return {"message": "SecondShift backend running"}
