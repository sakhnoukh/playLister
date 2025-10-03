"""Main FastAPI application for PlayLister."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.db import init_db, seed_songs
from app.routers import users, songs, quiz, playlists


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    print("Initializing database...")
    init_db()
    print("Seeding songs...")
    seed_songs()
    print("Application ready!")
    yield
    # Shutdown (nothing to do)


# Create FastAPI app
app = FastAPI(
    title="PlayLister - House Music Playlist Generator",
    description="A retro music playlist generator for house music lovers",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(users.router)
app.include_router(songs.router)
app.include_router(quiz.router)
app.include_router(playlists.router)


# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - user login."""
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/quiz", response_class=HTMLResponse)
async def quiz_page(request: Request):
    """Quiz page."""
    return templates.TemplateResponse("quiz.html", {"request": request})


@app.get("/generate", response_class=HTMLResponse)
async def generate_page(request: Request):
    """Playlist generation page."""
    return templates.TemplateResponse("generate.html", {"request": request})


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile with saved playlists."""
    return templates.TemplateResponse("profile.html", {"request": request})


# Health check
@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "app": "PlayLister", "version": "1.0.0"}
