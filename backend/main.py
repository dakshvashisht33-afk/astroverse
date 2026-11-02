import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .auth_router import router as auth_router
from .profile_router import router as profile_router
from .chart_router import router as chart_router
from .varga_router import router as varga_router
from .timing_router import router as timing_router
from .horoscope_router import router as horoscope_router
from .ai_router import router as ai_router
from .billing_router import router as billing_router
from .payment_router import router as payment_router
from .compatibility_router import router as compatibility_router

app = FastAPI(title="AstroVerse API", version="0.1.0")

# Initialize database on startup
@app.on_event("startup")
async def on_startup():
    init_db()

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001",
        ).split(",")
        if origin.strip()
    ],
    allow_origin_regex=os.getenv("CORS_ORIGIN_REGEX", r"https://[a-z0-9.-]+\.vercel\.app"),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(chart_router)
app.include_router(varga_router)
app.include_router(timing_router)
app.include_router(horoscope_router)
app.include_router(ai_router)
app.include_router(billing_router)
app.include_router(payment_router)
app.include_router(compatibility_router)

@app.get("/")
async def root():
    return {"message": "Welcome to AstroVerse API - The Cosmic Engine is Online"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
