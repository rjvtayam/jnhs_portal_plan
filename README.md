# JNHS Portal

**Jomalig National High School Portal** - A full-stack web application for managing student records, grades, attendance, and school communications.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5, Modern CSS, Vanilla JavaScript |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| API Docs | Auto-generated Swagger UI & ReDoc |

## Features

- **Student Management** - LRN-based student records with profiles
- **Teacher Management** - Faculty records and section advising
- **Grade Management** - DepEd-compliant quarterly grading with transmutation
- **Attendance Tracking** - Daily attendance recording and summary
- **Enrollment System** - Student enrollment with section assignment
- **SF9/SF10 Reports** - DepEd-compliant report card generation
- **Announcements** - School-wide announcements and events
- **Role-Based Access** - Admin, Teacher, Student, Parent roles

## Project Structure

```
jnhs-portal/
├── backend/            # FastAPI backend
│   ├── app/
│   │   ├── main.py     # Entry point
│   │   ├── models/     # SQLAlchemy models
│   │   ├── routes/     # API endpoints
│   │   ├── schemas/    # Pydantic schemas
│   │   ├── services/   # Business logic
│   │   └── utils/      # Helpers (auth, grading)
│   └── requirements.txt
├── frontend/           # Static frontend
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript modules
│   └── pages/          # HTML pages per role
└── database/           # SQL schemas and seeds
```

## Setup

### 1. Database
```bash
psql -U postgres
CREATE DATABASE jnhs_portal;
CREATE USER jnhs_admin WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE jnhs_portal TO jnhs_admin;
\q
psql -U jnhs_admin -d jnhs_portal -f database/schema.sql
psql -U jnhs_admin -d jnhs_portal -f database/seed.sql
```

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access
- **Frontend:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

## Default Login

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |

## DepEd Grading System

The portal implements the DepEd K-12 grading system:

| Component | Weight |
|-----------|--------|
| Written Work | 30% |
| Performance Tasks | 50% |
| Quarterly Assessment | 20% |

Grades are transmuted from raw scores to report card grades (minimum 60 raw = 75 report card).

## API Endpoints

See `/api/docs` for full API documentation with Swagger UI.
