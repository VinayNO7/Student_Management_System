import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.config import DEBUG, db_info
from app.database import init_db
from app.routers import students, departments, courses, enrollments, attendance, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed sample data on startup
    print(f"[Startup] Initializing database tables (Backend: {db_info['engine']})...")
    init_db()
    print("[Startup] Database ready.")
    yield
    print("[Shutdown] Cleaning up resources...")

app = FastAPI(
    title="Student Management System",
    description="A complete, modern Student Management System with MySQL DBMS, FastAPI backend, and interactive frontend.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "app", "templates")

# Mount static files and templates
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Include Routers
app.include_router(students.router)
app.include_router(departments.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(attendance.router)
app.include_router(analytics.router)

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serve the single page application frontend."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "db_engine": db_info["engine"],
            "db_connected": db_info["connected"],
            "db_message": db_info["message"],
            "db_name": db_info["database"]
        }
    )

if __name__ == "__main__":
    import uvicorn
    from app.config import APP_HOST, APP_PORT
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=DEBUG)

