# Placement Portal Application V2

A role-based campus placement portal for institute admins, companies, and students. The app manages the placement workflow from company registration and admin approval to job posting, student applications, interview scheduling, placement offers, notifications, CSV exports, and monthly reports.

## Key Features

- Admin, Company, and Student role-based dashboards
- JWT-based login and protected API routes
- Company registration with admin approval/rejection
- Placement drive creation, approval, rejection, and closure
- Student profile management with resume upload
- Job search with eligibility checks
- Application submission and duplicate-application prevention
- Applicant shortlisting, rejection, interview scheduling, and selection
- Placement offer tracking
- In-app notifications with unread/read status
- CSV export jobs for application and placement history
- Redis-backed caching for frequently used API responses
- Celery background jobs for exports, reminders, and monthly reports
- MailHog-compatible local email workflow

## Tech Stack

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- Flask-Caching
- Celery
- Redis
- SQLite

### Frontend

- Vue 3
- Vue Router
- Axios
- Vite

## Project Structure

```text
Placement-Portal-Application-V2/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── tasks.py
│   ├── celery_worker.py
│   ├── routes/
│   ├── templates/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── api.yaml
├── ER_Diagram.png
└── README.md
```

## Prerequisites

- Python 3.10 or newer
- Node.js 22 or newer
- npm
- Redis server
- MailHog, optional but recommended for viewing local emails

The backend commands below assume Linux or WSL. Redis, Celery, and MailHog are easiest to run from the same Linux/WSL environment as the Flask backend.

## Backend Setup in Linux/WSL

Open a Linux/WSL terminal from the project root.

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The backend runs at:

```text
http://127.0.0.1:5000
```

On startup, the app creates database tables and a default admin account if it does not already exist.

```text
Admin email: admin@placementportal.com
Admin password: admin123
```

## Frontend Setup

Open a second terminal from the project root.

```bash
cd frontend
npm install
npm run dev
```

The frontend usually runs at:

```text
http://localhost:5173
```

Main browser routes:

```text
/admin
/company
/student
```

## Redis

Redis is used by Flask-Caching and Celery. Start Redis before using caching, CSV exports, reminders, or reports.

```bash
sudo service redis-server start
redis-cli ping
```

Expected response:

```text
PONG
```

Default Redis URLs:

```text
Flask-Caching: redis://localhost:6379/0
Celery broker: redis://localhost:6379/1
Celery result backend: redis://localhost:6379/2
```

## Celery Worker and Beat

Run these in separate Linux/WSL terminals after Redis and Flask are running.

Terminal 1:

```bash
cd backend
source venv/bin/activate
celery -A celery_worker.celery_app worker --loglevel=info
```

Terminal 2:

```bash
cd backend
source venv/bin/activate
celery -A celery_worker.celery_app beat --loglevel=info
```

Celery handles CSV exports, interview reminders, application deadline reminders, and monthly placement reports.

## MailHog

MailHog is used for local email testing. It lets you view generated emails without sending real emails.

Default email settings:

```text
SMTP host: localhost
SMTP port: 1025
MailHog UI: http://localhost:8025
```

Start MailHog in Linux/WSL, then open the MailHog UI in your browser to view emails for company approval/rejection, interview scheduling, student selection, exports, and reports.

## Seed Data

Seed scripts are included for demo and manual verification.

Run from the `backend` folder with the virtual environment activated:

```bash
python seed_admin.py
python seed_student_flow_data.py
python seed_company_flow_data.py
```

Useful demo accounts:

```text
Admin:
admin@placementportal.com / admin123

Student:
student.flow@test.com / student123

Company:
company.flow@test.com / company123
```

## API and ER Diagram

- API documentation is included in `api.yaml`.
- The ER diagram image is included as `ER_Diagram.png`.
- The project report is submitted separately and is not required in the GitHub repository.

## Manual Verification Flow

1. Login as admin at `/admin`.
2. Approve a registered company.
3. Login as company at `/company`.
4. Create a placement drive.
5. Login as admin and approve the placement drive.
6. Login as student at `/student`.
7. View eligible jobs and apply for a job.
8. Login as company and shortlist, schedule interview, select, or reject applicants.
9. Check student application status, interview details, and placement offer.
10. Trigger CSV exports and verify notifications/downloads.
11. Check MailHog for generated workflow emails.
