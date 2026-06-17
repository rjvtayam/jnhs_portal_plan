import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from sqlalchemy.orm import Session
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.section import Section, Subject, SectionSubject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.attendance import Attendance

SCHOOL_NAME = "Jomalig National High School"
SCHOOL_ADDRESS = "Jomalig, Quezon"
SCHOOL_ID = "301366"
DIVISION = "Quezon"
REGION = "IV-A (CALABARZON)"

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_sf9(student_id: int, school_year: str, db: Session) -> str:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError("Student not found")

    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.school_year == school_year,
        Enrollment.status == "enrolled"
    ).first()
    section = None
    if enrollment:
        section = db.query(Section).filter(Section.id == enrollment.section_id).first()

    grades = db.query(Grade).filter(
        Grade.student_id == student_id,
        Grade.school_year == school_year
    ).all()

    filename = f"SF9_{student.lrn}_{school_year}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            topMargin=0.5*inch, bottomMargin=0.5*inch,
                            leftMargin=0.5*inch, rightMargin=0.5*inch)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=12, spaceAfter=6, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=9, spaceAfter=2)
    normal_style = ParagraphStyle('NormalText', parent=styles['Normal'], fontSize=8)
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7)

    elements.append(Paragraph("Republic of the Philippines", subtitle_style))
    elements.append(Paragraph("Department of Education", subtitle_style))
    elements.append(Paragraph(f"Region {REGION} - Division of {DIVISION}", subtitle_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"<b>{SCHOOL_NAME}</b>", title_style))
    elements.append(Paragraph(SCHOOL_ADDRESS, subtitle_style))
    elements.append(Paragraph(f"School ID: {SCHOOL_ID}", subtitle_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<b>School Form 9 (SF9)</b>", title_style))
    elements.append(Paragraph("<b>Learner's Progress Report Card</b>", subtitle_style))
    elements.append(Paragraph(f"School Year: {school_year}", subtitle_style))
    elements.append(Spacer(1, 12))

    name_text = f"<b>Name:</b> {student.last_name}, {student.first_name} {student.middle_name or ''} {student.extension_name or ''}"
    lrn_text = f"<b>LRN:</b> {student.lrn}"
    grade_text = f"<b>Grade:</b> {section.grade_level if section else '-'}"
    section_text = f"<b>Section:</b> {section.name if section else '-'}"

    info_data = [
        [Paragraph(name_text, normal_style), ""],
        [Paragraph(lrn_text, normal_style), Paragraph(f"{grade_text} &nbsp;&nbsp; {section_text}", normal_style)],
    ]
    info_table = Table(info_data, colWidths=[4*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 12))

    subjects_data = [["Learning Areas", "Q1", "Q2", "Q3", "Q4", "Final Grade"]]
    subject_map = {}
    for g in grades:
        subject = db.query(Subject).filter(Subject.id == g.subject_id).first()
        if subject:
            if subject.name not in subject_map:
                subject_map[subject.name] = {}
            subject_map[subject.name][g.quarter] = float(g.transmuted_grade) if g.transmuted_grade else 0

    for subject_name in sorted(subject_map.keys()):
        q_grades = subject_map[subject_name]
        q1 = str(q_grades.get("Q1", "-")) if q_grades.get("Q1") else "-"
        q2 = str(q_grades.get("Q2", "-")) if q_grades.get("Q2") else "-"
        q3 = str(q_grades.get("Q3", "-")) if q_grades.get("Q3") else "-"
        q4 = str(q_grades.get("Q4", "-")) if q_grades.get("Q4") else "-"
        final_grades = [v for v in [q_grades.get("Q1"), q_grades.get("Q2"), q_grades.get("Q3"), q_grades.get("Q4")] if v]
        final = str(round(sum(final_grades) / len(final_grades), 1)) if final_grades else "-"
        subjects_data.append([subject_name, q1, q2, q3, q4, final])

    if not subject_map:
        for _ in range(5):
            subjects_data.append(["", "-", "-", "-", "-", "-"])

    col_widths = [2.5*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.9*inch]
    subjects_table = Table(subjects_data, colWidths=col_widths)
    subjects_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(subjects_table)
    elements.append(Spacer(1, 12))

    present = db.query(Attendance).filter(Attendance.student_id == student_id, Attendance.status == "present").count() or 0
    absent = db.query(Attendance).filter(Attendance.student_id == student_id, Attendance.status == "absent").count() or 0
    late = db.query(Attendance).filter(Attendance.student_id == student_id, Attendance.status == "late").count() or 0

    att_data = [
        ["Attendance", "Days Present", "Days Absent", "Days Tardy"],
        ["Total", str(present), str(absent), str(late)],
    ]
    att_table = Table(att_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    att_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(Paragraph("<b>Attendance Record</b>", header_style))
    elements.append(att_table)
    elements.append(Spacer(1, 20))

    sig_data = [
        ["Prepared by:", "", "Noted by:", ""],
        ["", "", "", ""],
        ["_________________________", "", "_________________________", ""],
        ["Class Adviser", "", "Head of School", ""],
    ]
    sig_table = Table(sig_data, colWidths=[2.5*inch, 1*inch, 2.5*inch, 1*inch])
    sig_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    return filepath


def generate_sf10(student_id: int, db: Session) -> str:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError("Student not found")

    filename = f"SF10_{student.lrn}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=landscape(letter),
                            topMargin=0.5*inch, bottomMargin=0.5*inch,
                            leftMargin=0.5*inch, rightMargin=0.5*inch)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=14, spaceAfter=6, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER)
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=9, spaceAfter=2)
    normal_style = ParagraphStyle('NormalText', parent=styles['Normal'], fontSize=8)

    elements.append(Paragraph("Republic of the Philippines", subtitle_style))
    elements.append(Paragraph("Department of Education", subtitle_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"<b>{SCHOOL_NAME}</b>", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<b>School Form 10 (SF10)</b>", title_style))
    elements.append(Paragraph("<b>Learner's Permanent Record</b>", subtitle_style))
    elements.append(Spacer(1, 12))

    name_text = f"<b>Name:</b> {student.last_name}, {student.first_name} {student.middle_name or ''} {student.extension_name or ''}"
    lrn_text = f"<b>LRN:</b> {student.lrn}"
    dob_text = f"<b>Date of Birth:</b> {student.birth_date.strftime('%B %d, %Y') if student.birth_date else '-'}"
    sex_text = f"<b>Sex:</b> {student.gender or '-'}"

    info_data = [
        [Paragraph(name_text, normal_style), Paragraph(lrn_text, normal_style)],
        [Paragraph(dob_text, normal_style), Paragraph(sex_text, normal_style)],
    ]
    info_table = Table(info_data, colWidths=[5*inch, 5*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>Enrollment History</b>", header_style))
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student_id).all()
    enroll_data = [["School Year", "Grade Level", "Section", "Status"]]
    for e in enrollments:
        section = db.query(Section).filter(Section.id == e.section_id).first()
        enroll_data.append([
            e.school_year,
            f"Grade {section.grade_level}" if section else "-",
            section.name if section else "-",
            e.status,
        ])
    if len(enroll_data) == 1:
        enroll_data.append(["-", "-", "-", "-"])

    enroll_table = Table(enroll_data, colWidths=[2*inch, 1.5*inch, 2*inch, 1.5*inch])
    enroll_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(enroll_table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>Grades</b>", header_style))
    grades = db.query(Grade).filter(Grade.student_id == student_id).order_by(Grade.school_year, Grade.quarter).all()
    grade_data = [["School Year", "Quarter", "Subject", "Raw Grade", "Final Grade"]]
    for g in grades:
        subject = db.query(Subject).filter(Subject.id == g.subject_id).first()
        grade_data.append([
            g.school_year,
            g.quarter,
            subject.name if subject else "-",
            str(float(g.raw_grade)) if g.raw_grade else "-",
            str(float(g.transmuted_grade)) if g.transmuted_grade else "-",
        ])
    if len(grade_data) == 1:
        grade_data.append(["-", "-", "-", "-", "-"])

    grade_table = Table(grade_data, colWidths=[1.5*inch, 1*inch, 3*inch, 1.5*inch, 1.5*inch])
    grade_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(grade_table)
    elements.append(Spacer(1, 20))

    sig_data = [
        ["Prepared by:", "", "Noted by:", ""],
        ["", "", "", ""],
        ["_________________________", "", "_________________________", ""],
        ["Class Adviser", "", "Head of School", ""],
    ]
    sig_table = Table(sig_data, colWidths=[3*inch, 1*inch, 3*inch, 1*inch])
    sig_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    return filepath
