from app.services.grading_service import compute_quarterly_grade, transmute_grade


def compute_final_grade(grades: list[dict]) -> dict:
    if not grades:
        return {"average_raw": 0, "final_grade": 51}

    total_raw = sum(g.get("raw_grade", 0) for g in grades)
    count = len(grades)
    average_raw = round(total_raw / count, 2)
    final = transmute_grade(average_raw)

    return {"average_raw": average_raw, "final_grade": final}


def compute_semester_grade(q1_grade: float, q2_grade: float) -> dict:
    average = round((q1_grade + q2_grade) / 2, 2)
    semester_grade = transmute_grade(average)
    return {"average": average, "semester_grade": semester_grade}


def compute_year_grade(sem1_grade: float, sem2_grade: float) -> dict:
    average = round((sem1_grade + sem2_grade) / 2, 2)
    year_grade = transmute_grade(average)
    return {"average": average, "year_grade": year_grade}


def compute_class_ranking(student_grades: list[dict]) -> list[dict]:
    ranked = []
    for student in student_grades:
        grades = student.get("grades", [])
        if grades:
            avg = sum(g.get("transmuted_grade", 0) for g in grades) / len(grades)
            ranked.append({
                "student_id": student["student_id"],
                "average": round(avg, 2),
            })

    ranked.sort(key=lambda x: x["average"], reverse=True)
    for i, s in enumerate(ranked, 1):
        s["rank"] = i

    return ranked
