from app.routes.auth import router as auth_router
from app.routes.student import router as student_router
from app.routes.teacher import router as teacher_router
from app.routes.grades import router as grades_router
from app.routes.attendance import router as attendance_router
from app.routes.sections import router as sections_router
from app.routes.enrollment import router as enrollment_router
from app.routes.announcements import router as announcements_router

__all__ = [
    "auth_router",
    "student_router",
    "teacher_router",
    "grades_router",
    "attendance_router",
    "sections_router",
    "enrollment_router",
    "announcements_router",
]
