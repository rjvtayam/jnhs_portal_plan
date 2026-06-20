from app.routes.auth import router as auth_router
from app.routes.student import router as student_router
from app.routes.teacher import router as teacher_router
from app.routes.grades import router as grades_router
from app.routes.attendance import router as attendance_router
from app.routes.sections import router as sections_router
from app.routes.enrollment import router as enrollment_router
from app.routes.announcements import router as announcements_router
from app.routes.system import router as system_router
from app.routes.principal import router as principal_router
from app.routes.registrar import router as registrar_router
from app.routes.student_portal import router as student_portal_router
from app.routes.parent_portal import router as parent_portal_router
from app.routes.teacher_portal import router as teacher_portal_router
from app.routes.notifications import router as notifications_router
from app.routes.messages import router as messages_router
from app.routes.activity import router as activity_router
from app.routes.profile import router as profile_router

__all__ = [
    "auth_router",
    "student_router",
    "teacher_router",
    "grades_router",
    "attendance_router",
    "sections_router",
    "enrollment_router",
    "announcements_router",
    "system_router",
    "principal_router",
    "registrar_router",
    "student_portal_router",
    "parent_portal_router",
    "teacher_portal_router",
    "notifications_router",
    "messages_router",
    "activity_router",
    "profile_router",
]
