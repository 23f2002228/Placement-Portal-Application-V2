from datetime import timedelta

from werkzeug.security import generate_password_hash

from app import app
from models import (
    Application,
    ApplicationStatusHistory,
    CompanyProfile,
    Interview,
    Placement,
    PlacementDrive,
    StudentProfile,
    User,
    db,
    utc_now,
)


COMPANY_EMAIL = "company.flow@test.com"
COMPANY_PASSWORD = "company123"


def get_or_create_user(email, password, role):
    user = User.query.filter_by(email=email).first()

    if user:
        user.role = role
        user.is_active = True
        user.is_blacklisted = False
        return user

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        is_active=True,
        is_blacklisted=False,
    )
    db.session.add(user)
    db.session.flush()
    return user


def get_or_create_company():
    user = get_or_create_user(COMPANY_EMAIL, COMPANY_PASSWORD, "company")
    company = CompanyProfile.query.filter_by(user_id=user.id).first()

    if not company:
        company = CompanyProfile(
            user_id=user.id,
            company_name="Flow Test Technologies",
            industry="Software Development",
            location="Bengaluru",
            hr_name="Asha Mehta",
            hr_contact="9876501234",
            website="https://flowtest.example.com",
            description="Dummy approved company for testing application and interview flows.",
        )
        db.session.add(company)

    company.approval_status = "approved"
    company.rejection_reason = None
    db.session.flush()
    return user, company


def get_or_create_job(company):
    job = PlacementDrive.query.filter_by(
        company_id=company.id,
        job_title="Frontend Developer Intern",
    ).first()

    if not job:
        job = PlacementDrive(company_id=company.id)
        db.session.add(job)

    job.job_title = "Frontend Developer Intern"
    job.job_description = "Work with Vue, APIs, forms, and dashboard screens."
    job.location = "Bengaluru"
    job.salary = 600000
    job.skills_required = "Vue, JavaScript, HTML, CSS, REST APIs"
    job.experience_required = "0-1 years"
    job.benefits = "Mentorship, hybrid work, PPO opportunity"
    job.employment_type = "Internship"
    job.min_cgpa = 7.0
    job.eligible_branches = "CSE, IT, ECE"
    job.eligible_year = 4
    job.application_deadline = utc_now() + timedelta(days=20)
    job.drive_date = utc_now() + timedelta(days=30)
    job.status = "approved"
    job.rejection_reason = None
    db.session.flush()
    return job


def get_or_create_student(student_data):
    user = get_or_create_user(student_data["email"], "student123", "student")
    student = StudentProfile.query.filter_by(user_id=user.id).first()

    if not student:
        student = StudentProfile(user_id=user.id, roll_number=student_data["roll_number"])
        db.session.add(student)

    student.full_name = student_data["full_name"]
    student.roll_number = student_data["roll_number"]
    student.degree = "B.Tech"
    student.branch = student_data["branch"]
    student.year = 4
    student.graduation_year = 2026
    student.cgpa = student_data["cgpa"]
    student.phone = student_data["phone"]
    student.resume_url = student_data["resume_url"]
    student.skills = student_data["skills"]
    db.session.flush()
    return student


def set_application_status(application, status, note, changed_by_user):
    old_status = application.status
    application.status = status
    application.remarks = note

    latest_history = (
        ApplicationStatusHistory.query
        .filter_by(application_id=application.id, new_status=status, note=note)
        .first()
    )

    if not latest_history:
        history = ApplicationStatusHistory(
            application=application,
            changed_by_user=changed_by_user,
            old_status=old_status if old_status != status else "applied",
            new_status=status,
            note=note,
        )
        db.session.add(history)


def get_or_create_application(student, job, status, note, changed_by_user):
    application = Application.query.filter_by(
        student_id=student.id,
        drive_id=job.id,
    ).first()

    if not application:
        application = Application(student_id=student.id, drive_id=job.id)
        db.session.add(application)
        db.session.flush()

    set_application_status(application, status, note, changed_by_user)
    db.session.flush()
    return application


def add_interview(application):
    interview = Interview.query.filter_by(
        application_id=application.id,
        round_name="Technical Round",
    ).first()

    if not interview:
        interview = Interview(application_id=application.id)
        db.session.add(interview)

    interview.scheduled_at = utc_now() + timedelta(days=5)
    interview.mode = "online"
    interview.venue_or_link = "https://meet.example.com/flow-test-interview"
    interview.round_name = "Technical Round"
    interview.status = "scheduled"
    interview.feedback = None


def add_placement(application, job):
    placement = Placement.query.filter_by(application_id=application.id).first()

    if not placement:
        placement = Placement(application_id=application.id)
        db.session.add(placement)

    placement.position = job.job_title
    placement.salary = job.salary
    placement.status = "offered"


def seed_company_flow_data():
    with app.app_context():
        db.create_all()
        company_user, company = get_or_create_company()
        job = get_or_create_job(company)

        students = [
            {
                "full_name": "Riya Nair",
                "roll_number": "FLOW001",
                "branch": "CSE",
                "cgpa": 8.7,
                "phone": "9000000001",
                "email": "riya.flow@test.com",
                "resume_url": "https://example.com/resumes/riya.pdf",
                "skills": "Vue, JavaScript, CSS",
                "status": "applied",
                "note": "New application received.",
            },
            {
                "full_name": "Arjun Rao",
                "roll_number": "FLOW002",
                "branch": "IT",
                "cgpa": 8.4,
                "phone": "9000000002",
                "email": "arjun.flow@test.com",
                "resume_url": "https://example.com/resumes/arjun.pdf",
                "skills": "JavaScript, REST APIs, HTML",
                "status": "shortlisted",
                "note": "Good frontend basics.",
            },
            {
                "full_name": "Meera Iyer",
                "roll_number": "FLOW003",
                "branch": "CSE",
                "cgpa": 9.1,
                "phone": "9000000003",
                "email": "meera.flow@test.com",
                "resume_url": "https://example.com/resumes/meera.pdf",
                "skills": "Vue, TypeScript, UI testing",
                "status": "interview_scheduled",
                "note": "Interview scheduled.",
            },
            {
                "full_name": "Kabir Khan",
                "roll_number": "FLOW004",
                "branch": "ECE",
                "cgpa": 8.9,
                "phone": "9000000004",
                "email": "kabir.flow@test.com",
                "resume_url": "https://example.com/resumes/kabir.pdf",
                "skills": "JavaScript, Python, APIs",
                "status": "selected",
                "note": "Selected after interview.",
            },
            {
                "full_name": "Nisha Patel",
                "roll_number": "FLOW005",
                "branch": "CSE",
                "cgpa": 7.6,
                "phone": "9000000005",
                "email": "nisha.flow@test.com",
                "resume_url": "https://example.com/resumes/nisha.pdf",
                "skills": "HTML, CSS, basic JavaScript",
                "status": "rejected",
                "note": "Needs stronger JavaScript practice.",
            },
        ]

        applications = []
        for student_data in students:
            student = get_or_create_student(student_data)
            application = get_or_create_application(
                student,
                job,
                student_data["status"],
                student_data["note"],
                company_user,
            )
            applications.append(application)

            if student_data["status"] == "interview_scheduled":
                add_interview(application)

            if student_data["status"] == "selected":
                add_placement(application, job)

        db.session.commit()

        print("Dummy company flow data is ready.")
        print(f"Company login: {COMPANY_EMAIL} / {COMPANY_PASSWORD}")
        print(f"Approved job: {job.job_title}")
        print(f"Applications added/updated: {len(applications)}")
        print("Student password for all dummy students: student123")


if __name__ == "__main__":
    seed_company_flow_data()
