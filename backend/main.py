"""
KisanMitra — FastAPI Backend
=============================
AI Farm Advisory Multi-Agent System.

Run with:
    uvicorn main:app --reload --port 8000
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from models.database import engine, Base

# Import routes
from routes.auth import router as auth_router
from routes.crop import router as crop_router
from routes.market import router as market_router
from routes.weather import router as weather_router
from routes.schemes import router as schemes_router
from routes.alerts import router as alerts_router

# ── App Initialization ────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="KisanMitra AI Farm Advisory System backend. Coordinated crew of 5 CrewAI agents.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ── CORS Middleware ───────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon/dev accessibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static Uploads Mount ──────────────────────────────────────────────────────

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ── Routes Inclusion ──────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(crop_router)
app.include_router(market_router)
app.include_router(weather_router)
app.include_router(schemes_router)
app.include_router(alerts_router)

# ── Startup Database Creation ─────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup():
    # Create all SQLite tables
    Base.metadata.create_all(bind=engine)
    print(f"SUCCESS: {settings.APP_NAME} started — Database tables verified and ready.")
    
    # Try seeding RAG if ChromaDB database is empty
    try:
        from rag.chroma_client import RAGDatabase
        db = RAGDatabase()
        count = len(db.collection.get().get("ids", []))
        if count == 0:
            print("ChromaDB collection is empty. Auto-triggering schemes ingestion...")
            from rag.ingest import run_ingestion
            run_ingestion()
        else:
            print(f"ChromaDB has {count} scheme chunks preloaded.")
    except Exception as e:
        print(f"Auto-ingest note: {e}")

# ── Root / Health ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": "1.0.0"}

@app.get("/", tags=["System"])
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API Portal",
        "docs": "/docs",
        "health": "/health"
    }
