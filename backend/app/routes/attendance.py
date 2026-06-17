from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models.attendance import Attendance
from app.models.user import User
from app.schemas.attendance import AttendanceInput, AttendanceUpdate, AttendanceResponse, BulkAttendanceInput
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.get("/section/{section_id}", response_model=list[AttendanceResponse])
def get_section_attendance(
    section_id: int,
    date_filter: date = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "registrar", "teacher")),
):
    query = db.query(Attendance).filter(Attendance.section_id == section_id)
    if date_filter:
        query = query.filter(Attendance.date == date_filter)
    return query.order_by(Attendance.date.desc()).all()


@router.get("/student/{student_id}", response_model=list[AttendanceResponse])
def get_student_attendance(
    student_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).order_by(Attendance.date.desc()).all()


@router.post("/", response_model=AttendanceResponse)
def record_attendance(
    attendance: AttendanceInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "teacher")),
):
    existing = db.query(Attendance).filter(
        Attendance.student_id == attendance.student_id,
        Attendance.date == attendance.date,
        Attendance.section_id == attendance.section_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already recorded for this date")

    new_attendance = Attendance(
        student_id=attendance.student_id,
        section_id=attendance.section_id,
        subject_id=attendance.subject_id,
        date=attendance.date,
        status=attendance.status,
        remarks=attendance.remarks,
        recorded_by=user.id,
    )
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    return new_attendance


@router.post("/bulk", response_model=list[AttendanceResponse])
def bulk_record_attendance(
    bulk: BulkAttendanceInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "teacher")),
):
    records = []
    for record in bulk.records:
        attendance = Attendance(
            student_id=record["student_id"],
            section_id=bulk.section_id,
            subject_id=bulk.subject_id,
            date=bulk.date,
            status=record["status"],
            remarks=record.get("remarks"),
            recorded_by=user.id,
        )
        db.add(attendance)
        records.append(attendance)

    db.commit()
    for r in records:
        db.refresh(r)
    return records


@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: int,
    update: AttendanceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "teacher")),
):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)

    db.commit()
    db.refresh(attendance)
    return attendance
