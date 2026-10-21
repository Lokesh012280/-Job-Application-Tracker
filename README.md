# Job Application Tracker

A full-stack job-search tracker built to match the supplied Project 2 assignment: **Python, FastAPI, PostgreSQL, JWT authentication, application lifecycle management, interviews, notes, follow-ups, filtering, pagination, dashboard analytics, and a lightweight HTML/CSS/JavaScript frontend**.

## Features
- Register/login with Argon2 password hashing and JWT bearer tokens.
- Per-user authorization: users can only access their own records.
- Application create, list, view, update, delete, and controlled status transitions.
- Search/filter by company, job title, status, location, source, and applied-date range.
- Sorting and pagination (limit max 100).
- Interview scheduling and interview result/feedback management.
- Notes and follow-up management.
- Dashboard counts, interview/offer rates, company statistics, upcoming interviews and follow-ups.
- Swagger/OpenAPI docs at `/docs`.
- Automated tests.

## Tech stack
- Python 3.11+
- FastAPI / Pydantic
- SQLAlchemy 2
- PostgreSQL with psycopg 3 (SQLite fallback for quick local run/tests)
- JWT (`python-jose`) and Argon2 password hashing (`pwdlib`)
- HTML, CSS, vanilla JavaScript

## Project structure
```text
job-application-tracker/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database/connection.py
│   ├── models/                 # user, application, interview, note, followup
│   ├── schemas/                # request/response validation
│   ├── routers/                # auth, applications, interviews, notes, dashboard
│   ├── services/application_service.py
│   └── utils/                  # security and authentication dependency
├── frontend/                   # single-page UI
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

## 1. Requirements
Install Python 3.11 or newer. For the recommended database, install PostgreSQL and create a database:

```sql
CREATE DATABASE job_tracker;
```

## 2. Setup on Windows PowerShell
Open PowerShell in the project directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `DATABASE_URL` to your PostgreSQL username/password/database. Example:
```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/job_tracker
SECRET_KEY=put-a-long-random-secret-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

If PostgreSQL is not installed yet, use SQLite for initial learning/testing by setting:
```env
DATABASE_URL=sqlite:///./job_tracker.db
```
The app creates tables automatically on startup. For a production deployment, use Alembic migrations rather than `create_all`.

## 3. Run
From the root folder (the folder containing `requirements.txt`):

```powershell
uvicorn app.main:app --reload
```
Open:
- Frontend: http://127.0.0.1:8000/
- Swagger API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## 4. Quick API workflow
1. Register at `POST /auth/register`:
```json
{"name":"Anil Kumar","email":"anil@example.com","password":"Password@123"}
```
2. Login at `POST /auth/login`; copy `access_token`.
3. In Swagger, click **Authorize** and enter the token as `Bearer <token>` if prompted.
4. Create an application at `POST /applications`:
```json
{
  "company_name":"TCS",
  "job_title":"Python Developer",
  "location":"Hyderabad",
  "employment_type":"Full Time",
  "source":"LinkedIn",
  "job_url":"https://example.com/job/123",
  "salary_min":600000,
  "salary_max":900000,
  "applied_date":"2026-10-01",
  "status":"SAVED"
}
```
5. Move it through the allowed lifecycle using `PATCH /applications/{id}/status`. Example: `SAVED -> APPLIED -> SCREENING -> INTERVIEW -> OFFER -> ACCEPTED`. Terminal states (`ACCEPTED`, `REJECTED`, `WITHDRAWN`) cannot be reopened in this implementation.
6. Add interviews, notes, and follow-ups with the endpoints listed below.

## 5. Main API endpoints
| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| POST | `/auth/register` | Create account | No |
| POST | `/auth/login` | Get JWT | No |
| GET | `/auth/me` | Current user | Yes |
| POST | `/applications` | Create application | Yes |
| GET | `/applications` | Filter/sort/page applications | Yes |
| GET | `/applications/{id}` | Get one application | Yes |
| PUT | `/applications/{id}` | Update application | Yes |
| PATCH | `/applications/{id}/status` | Transition status | Yes |
| DELETE | `/applications/{id}` | Delete application | Yes |
| POST/GET | `/applications/{id}/interviews` | Create/list interviews | Yes |
| PUT/DELETE | `/interviews/{id}` | Update/delete interview | Yes |
| POST/GET | `/applications/{id}/notes` | Create/list notes | Yes |
| DELETE | `/notes/{id}` | Delete note | Yes |
| POST/GET | `/applications/{id}/followups` | Create/list follow-ups | Yes |
| PATCH/DELETE | `/followups/{id}` | Update/delete follow-up | Yes |
| GET | `/dashboard` | Personal statistics | Yes |
| GET | `/dashboard/companies` | Company statistics | Yes |
| GET | `/dashboard/upcoming-interviews` | Upcoming interviews | Yes |
| GET | `/dashboard/upcoming-followups` | Upcoming follow-ups | Yes |

Application query parameters: `company`, `job_title`, `status`, `location`, `source`, `from_date`, `to_date`, `sort`, `order`, `page`, `limit`. Sort values: `applied_date`, `company`, `salary`, `status`, `created_at`; order: `asc` or `desc`.

## 6. Database design
- `users` 1-to-many `applications`
- `applications` 1-to-many `interviews`
- `applications` 1-to-many `notes`
- `applications` 1-to-many `followups`

## 7. Business rules
- Passwords are never stored as plain text.
- Email is unique and validated.
- Salary values cannot be negative; maximum cannot be less than minimum.
- Application date cannot be in the future.
- Status values are a defined enum.
- Status transitions are controlled in `app/services/application_service.py`.
- Each query checks ownership before returning or changing a record.
- Date filters may be combined; `from_date` must not exceed `to_date`.
- Interview and follow-up dates can be in the future.

## 8. Run tests
```powershell
pytest -q
```
The tests use a local SQLite test database and cover registration, duplicate email, login failures, validation, CRUD, user isolation, filtering, pagination, status transitions, interviews, notes, follow-ups, and dashboard behavior.

## 9. Security and production notes
- Replace `SECRET_KEY` with a long random value and keep `.env` out of Git.
- Use HTTPS in deployment.
- For production, add Alembic migrations, rate limiting, structured logging, email reminders, and stronger operational monitoring.
- The frontend is intentionally lightweight; the API remains the primary project deliverable.
- Dashboard interview rate is defined as (applications currently in `INTERVIEW` + number of interview rounds) / total applications. This is a simple demo metric; change the definition if your assignment evaluator expects status-only interview rate.
- The current app creates tables at startup for easy local setup; use migrations for team/production work.

## 10. GitHub submission checklist
- [ ] Add screenshots of the running UI and `/docs`.
- [ ] Run all tests.
- [ ] Configure PostgreSQL connection.
- [ ] Record the required 30-second working demo.
- [ ] Never commit `.env`, passwords, or secret keys.
