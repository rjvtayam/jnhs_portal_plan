from app.schemas.user import UserBase, UserCreate, UserResponse, Token, LoginRequest
from app.schemas.student import StudentBase, StudentCreate, StudentUpdate, StudentResponse, StudentListResponse
from app.schemas.teacher import TeacherBase, TeacherCreate, TeacherUpdate, TeacherResponse
from app.schemas.grade import GradeInput, GradeUpdate, GradeResponse, GradeBulkUpload
from app.schemas.attendance import AttendanceInput, AttendanceUpdate, AttendanceResponse, BulkAttendanceInput
from app.schemas.section import (
    SectionBase, SectionCreate, SectionUpdate, SectionResponse,
    SubjectBase, SubjectCreate, SubjectResponse,
    SectionSubjectBase, SectionSubjectCreate, SectionSubjectResponse,
)
from app.schemas.enrollment import EnrollmentBase, EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse
from app.schemas.announcement import (
    AnnouncementBase, AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse,
    EventBase, EventCreate, EventResponse,
)
