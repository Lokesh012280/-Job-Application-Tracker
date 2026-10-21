from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database.connection import Base, engine
from app import models  # registers ORM models
from app.routers import auth, applications, interviews, notes, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Application Tracker API",
    description="Secure API to manage job applications, interviews, notes, follow-ups, and job-search analytics.",
    version="1.0.0",
)

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(interviews.router)
app.include_router(notes.router)
app.include_router(dashboard.router)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

web_dir = Path(__file__).resolve().parent.parent / "frontend"
if web_dir.exists():
    app.mount("/", StaticFiles(directory=web_dir, html=True), name="frontend")
