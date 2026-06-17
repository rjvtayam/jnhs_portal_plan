# DepEd Grading Weights Configuration
GRADING_WEIGHTS = {
    "standard": {
        "written_work": 0.30,
        "performance_task": 0.50,
        "quarterly_assessment": 0.20,
    },
    "language": {
        "written_work": 0.30,
        "performance_task": 0.50,
        "quarterly_assessment": 0.20,
    },
    "practical": {
        "written_work": 0.20,
        "performance_task": 0.60,
        "quarterly_assessment": 0.20,
    },
}

SUBJECT_TYPE_MAP = {
    "FIL": "language",
    "ENG": "language",
    "FIL7": "language",
    "FIL8": "language",
    "FIL9": "language",
    "FIL10": "language",
    "ENG7": "language",
    "ENG8": "language",
    "ENG9": "language",
    "ENG10": "language",
    "MAPEH": "practical",
    "TLE": "practical",
    "TVE": "practical",
    "MAPEH7": "practical",
    "MAPEH8": "practical",
    "MAPEH9": "practical",
    "MAPEH10": "practical",
    "TLE7": "practical",
    "TLE8": "practical",
    "TLE9": "practical",
    "TLE10": "practical",
}


def get_subject_type(subject_code: str) -> str:
    return SUBJECT_TYPE_MAP.get(subject_code, "standard")


def compute_percentage(score: float, possible: float) -> float:
    if possible == 0:
        return 0.0
    return round((score / possible) * 100, 2)


def compute_raw_grade(
    ww_pct: float,
    pt_pct: float,
    qa_pct: float,
    subject_type: str = "standard",
) -> float:
    weights = GRADING_WEIGHTS.get(subject_type, GRADING_WEIGHTS["standard"])
    raw = (
        ww_pct * weights["written_work"]
        + pt_pct * weights["performance_task"]
        + qa_pct * weights["quarterly_assessment"]
    )
    return round(raw, 2)


def transmute_grade(raw_score: float) -> int:
    """DepEd transmutation table: raw score to report card grade."""
    if raw_score >= 98:
        return 100
    elif raw_score >= 0:
        return int(51 + (raw_score / 2))
    return 51


def compute_quarterly_grade(
    ww_score: float,
    ww_possible: float,
    pt_score: float,
    pt_possible: float,
    qa_score: float,
    qa_possible: float,
    subject_code: str = "",
) -> dict:
    subject_type = get_subject_type(subject_code)

    ww_pct = compute_percentage(ww_score, ww_possible)
    pt_pct = compute_percentage(pt_score, pt_possible)
    qa_pct = compute_percentage(qa_score, qa_possible)

    raw = compute_raw_grade(ww_pct, pt_pct, qa_pct, subject_type)
    transmuted = transmute_grade(raw)

    return {
        "ww_percentage": ww_pct,
        "pt_percentage": pt_pct,
        "qa_percentage": qa_pct,
        "raw_grade": raw,
        "transmuted_grade": transmuted,
    }
