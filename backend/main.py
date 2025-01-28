from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI()

# Configure CORS
allowed_origins = [
    "http://localhost:3000",  # Local development
    os.getenv("FRONTEND_URL", ""),  # App Runner URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in allowed_origins if origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NameRequest(BaseModel):
    name: str

@app.post("/api/greet")
async def greet(request: NameRequest):
    return {"message": f"Hello, {request.name}!"}

@app.get("/")
async def root():
    return {"status": "API is running"}
