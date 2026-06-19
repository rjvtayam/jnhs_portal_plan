from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models.attendance import Attendance
from app.models.user import User
from app.models.student import Student
from app.models.parent import Parent, ParentStudent
from app.schemas.attendance import AttendanceInput, AttendanceUpdate, AttendanceResponse, BulkAttendanceInput
from app.utils.auth import get_current_user, require_role
from app.routes.notifications import create_notification
from app.routes.activity import log_activity

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

    # Notify parents if absent or late
    if attendance.status in ("absent", "late"):
        _notify_absence(db, attendance.student_id, attendance.status, attendance.date)

    return new_attendance


@router.post("/bulk", response_model=list[AttendanceResponse])
def bulk_record_attendance(
    bulk: BulkAttendanceInput,
    request: Request,
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

    # Notify parents for absent/late students
    for record in bulk.records:
        if record.get("status") in ("absent", "late"):
            _notify_absence(db, record["student_id"], record["status"], bulk.date)

    log_activity(
        db=db, user_id=user.id, username=user.username, user_role=user.role,
        action="record", category="attendance",
        description=f"Recorded attendance for {len(bulk.records)} students on {bulk.date}",
        target_type="attendance", target_id=bulk.section_id,
        ip_address=request.client.host if request.client else None,
        details={"section_id": bulk.section_id, "date": str(bulk.date), "count": len(bulk.records)},
    )

    return records


def _notify_absence(db, student_id, status, att_date):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return
    parent_links = db.query(ParentStudent).filter(ParentStudent.student_id == student_id).all()
    for pl in parent_links:
        parent = db.query(Parent).filter(Parent.id == pl.parent_id).first()
        if parent and parent.user_id:
            create_notification(
                db=db,
                user_id=parent.user_id,
                title=f"Attendance Notice: {student.first_name} {student.last_name}",
                message=f"{student.first_name} was marked {status} on {att_date}.",
                notif_type="attendance",
                reference_type="attendance",
                link="/pages/parent/child-progress.html",
            )


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
