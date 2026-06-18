from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import get_settings
from app.routes import (
    auth_router, student_router, teacher_router,
    grades_router, attendance_router, sections_router,
    enrollment_router, announcements_router,
    system_router, principal_router,
    registrar_router, student_portal_router, parent_portal_router,
    teacher_portal_router,
)

settings = get_settings()

app = FastAPI(
    title="JNHS Portal API",
    description="Jomalig National High School Portal Backend",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def no_cache_static(request: Request, call_next):
    response: Response = await call_next(request)
    path = request.url.path
    if path.endswith(('.html', '.js', '.css')):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Register API routers
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(grades_router)
app.include_router(attendance_router)
app.include_router(sections_router)
app.include_router(enrollment_router)
app.include_router(announcements_router)
app.include_router(system_router)
app.include_router(principal_router)
app.include_router(registrar_router)
app.include_router(student_portal_router)
app.include_router(parent_portal_router)
app.include_router(teacher_portal_router)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}


# Mount frontend static files
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
