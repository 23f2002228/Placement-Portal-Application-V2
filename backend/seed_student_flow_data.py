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


STUDENT_EMAIL = "student.flow@test.com"
STUDENT_PASSWORD = "student123"
COMPANY_PASSWORD = "company123"


def get_or_create_user(email, password, role):
    user = User.query.filter_by(email=email).first()

    if user:
        user.role = role
        user.password_hash = generate_password_hash(password)
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


def get_or_create_company(email, company_name):
    user = get_or_create_user(email, COMPANY_PASSWORD, "company")
    company = CompanyProfile.query.filter_by(user_id=user.id).first()

    if not company:
        company = CompanyProfile(user_id=user.id)
        db.session.add(company)

    company.company_name = company_name
    company.industry = "Technology"
    company.location = "Bengaluru"
    company.hr_name = "Test HR"
    company.hr_contact = "9000000999"
    company.website = f"https://{company_name.lower().replace(' ', '')}.example.com"
    company.description = "Approved dummy company for student dashboard testing."
    company.approval_status = "approved"
    company.rejection_reason = None
    db.session.flush()
    return user, company


def get_or_create_student():
    user = get_or_create_user(STUDENT_EMAIL, STUDENT_PASSWORD, "student")
    student = StudentProfile.query.filter_by(user_id=user.id).first()

    if not student:
        student = StudentProfile(user_id=user.id)
        db.session.add(student)

    student.full_name = "Student Flow Tester"
    student.roll_number = "STU-FLOW-001"
    student.degree = "B.Tech"
    student.branch = "CSE"
    student.year = 4
    student.graduation_year = 2026
    student.cgpa = 8.4
    student.phone = "9000000100"
    student.resume_url = "https://example.com/resumes/student-flow-tester.pdf"
    student.skills = "Python, Flask, Vue, SQL"
    student.experience = "Built class projects with Flask APIs and Vue dashboards."
    db.session.flush()
    return user, student


def get_or_create_job(company, data):
    job = PlacementDrive.query.filter_by(
        company_id=company.id,
        job_title=data["job_title"],
    ).first()

    if not job:
        job = PlacementDrive(company_id=company.id)
        db.session.add(job)

    job.job_title = data["job_title"]
    job.job_description = data["job_description"]
    job.location = data.get("location", "Bengaluru")
    job.salary = data.get("salary", 700000)
    job.skills_required = data.get("skills_required", "Python, SQL")
    job.experience_required = data.get("experience_required", "0-1 years")
    job.benefits = data.get("benefits", "Mentorship and learning support")
    job.employment_type = data.get("employment_type", "Full-time")
    job.min_cgpa = data.get("min_cgpa", 7.0)
    job.eligible_branches = data.get("eligible_branches", "CSE, IT")
    job.eligible_year = data.get("eligible_year", 4)
    job.application_deadline = utc_now() + timedelta(days=data.get("deadline_days", 15))
    job.drive_date = utc_now() + timedelta(days=data.get("drive_days", 25))
    job.status = data.get("status", "approved")
    job.rejection_reason = data.get("rejection_reason")
    db.session.flush()
    return job


def ensure_history(application, changed_by_user, old_status, new_status, note):
    exists = ApplicationStatusHistory.query.filter_by(
        application_id=application.id,
        old_status=old_status,
        new_status=new_status,
        note=note,
    ).first()

    if exists:
        return

    db.session.add(ApplicationStatusHistory(
        application=application,
        changed_by_user=changed_by_user,
        old_status=old_status,
        new_status=new_status,
        note=note,
    ))


def get_or_create_application(student, job, changed_by_user, status, note):
    application = Application.query.filter_by(
        student_id=student.id,
        drive_id=job.id,
    ).first()

    if not application:
        application = Application(student_id=student.id, drive_id=job.id)
        db.session.add(application)
        db.session.flush()

    ensure_history(
        application,
        changed_by_user,
        None,
        "applied",
        "Application submitted by student.",
    )

    if status != "applied":
        ensure_history(application, changed_by_user, "applied", status, note)

    application.status = status
    application.remarks = note
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

    interview.scheduled_at = utc_now() + timedelta(days=4)
    interview.mode = "online"
    interview.venue_or_link = "https://meet.example.com/student-flow"
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
    placement.joining_date = utc_now().date() + timedelta(days=45)
    placement.status = "offered"


def seed_student_flow_data():
    with app.app_context():
        db.create_all()

        student_user, student = get_or_create_student()
        nova_user, nova = get_or_create_company(
            "nova.student.flow@test.com",
            "Nova Student Flow Labs",
        )
        orbit_user, orbit = get_or_create_company(
            "orbit.student.flow@test.com",
            "Orbit Campus Systems",
        )

        open_apply_job = get_or_create_job(nova, {
            "job_title": "Backend Developer Trainee",
            "job_description": "Build Flask APIs and database-backed placement features.",
            "salary": 650000,
            "skills_required": "Python, Flask, SQL",
            "min_cgpa": 7.0,
            "eligible_branches": "CSE, IT, ECE",
        })

        jobs_with_applications = [
            (
                get_or_create_job(nova, {
                    "job_title": "Vue Frontend Intern",
                    "job_description": "Work on Vue components, forms, and API integration.",
                    "salary": 600000,
                    "skills_required": "Vue, JavaScript, HTML, CSS",
                    "min_cgpa": 7.0,
                    "eligible_branches": "CSE, IT",
                }),
                "applied",
                "Application submitted and waiting for review.",
                nova_user,
            ),
            (
                get_or_create_job(nova, {
                    "job_title": "QA Automation Intern",
                    "job_description": "Write test cases and automate browser checks.",
                    "salary": 550000,
                    "skills_required": "Testing, Python, Selenium",
                    "min_cgpa": 7.2,
                    "eligible_branches": "CSE, IT, ECE",
                }),
                "shortlisted",
                "Shortlisted for the next round.",
                nova_user,
            ),
            (
                get_or_create_job(orbit, {
                    "job_title": "Full Stack Interview Track",
                    "job_description": "Build and debug full-stack placement workflows.",
                    "salary": 800000,
                    "skills_required": "Flask, Vue, REST APIs",
                    "min_cgpa": 7.5,
                    "eligible_branches": "CSE, IT",
                }),
                "interview_scheduled",
                "Technical interview scheduled.",
                orbit_user,
            ),
            (
                get_or_create_job(orbit, {
                    "job_title": "Software Engineer Offer Track",
                    "job_description": "Selected flow used to test offers and confirmations.",
                    "salary": 950000,
                    "skills_required": "Python, SQL, APIs",
                    "min_cgpa": 7.5,
                    "eligible_branches": "CSE",
                }),
                "selected",
                "Selected after interview.",
                orbit_user,
            ),
            (
                get_or_create_job(nova, {
                    "job_title": "Data Analyst Rejected Track",
                    "job_description": "Rejected flow used to test application history display.",
                    "salary": 500000,
                    "skills_required": "SQL, Excel, Python",
                    "min_cgpa": 7.0,
                    "eligible_branches": "CSE, IT",
                }),
                "rejected",
                "Rejected after resume screening.",
                nova_user,
            ),
            (
                get_or_create_job(orbit, {
                    "job_title": "DevOps Withdrawn Track",
                    "job_description": "Withdrawn flow used to test status filtering.",
                    "salary": 720000,
                    "skills_required": "Linux, Docker, CI",
                    "min_cgpa": 7.0,
                    "eligible_branches": "CSE, IT",
                }),
                "withdrawn",
                "Student withdrew the application.",
                orbit_user,
            ),
        ]

        for job, status, note, changed_by_user in jobs_with_applications:
            application = get_or_create_application(
                student,
                job,
                changed_by_user,
                status,
                note,
            )

            if status == "interview_scheduled":
                add_interview(application)

            if status == "selected":
                add_placement(application, job)

        ineligible_jobs = [
            get_or_create_job(nova, {
                "job_title": "High CGPA Research Intern",
                "job_description": "Requires a very high CGPA.",
                "salary": 900000,
                "skills_required": "Machine Learning, Research",
                "min_cgpa": 9.5,
                "eligible_branches": "CSE",
            }),
            get_or_create_job(orbit, {
                "job_title": "Mechanical Systems Trainee",
                "job_description": "Branch-restricted role for eligibility testing.",
                "salary": 580000,
                "skills_required": "CAD, Manufacturing",
                "min_cgpa": 7.0,
                "eligible_branches": "MECH",
            }),
            get_or_create_job(nova, {
                "job_title": "Second Year Internship",
                "job_description": "Year-restricted role for eligibility testing.",
                "salary": 300000,
                "skills_required": "HTML, CSS",
                "min_cgpa": 6.5,
                "eligible_branches": "CSE, IT",
                "eligible_year": 2,
            }),
            get_or_create_job(orbit, {
                "job_title": "Expired Application Deadline",
                "job_description": "Approved but past deadline for deadline testing.",
                "salary": 700000,
                "skills_required": "Python, APIs",
                "min_cgpa": 7.0,
                "eligible_branches": "CSE, IT",
                "deadline_days": -2,
                "drive_days": 5,
            }),
        ]

        hidden_jobs = [
            get_or_create_job(nova, {
                "job_title": "Pending Approval Hidden Job",
                "job_description": "Students should not see this pending drive.",
                "status": "pending",
            }),
            get_or_create_job(orbit, {
                "job_title": "Rejected Hidden Job",
                "job_description": "Students should not see this rejected drive.",
                "status": "rejected",
                "rejection_reason": "Dummy rejected drive.",
            }),
        ]

        db.session.commit()

        print("Dummy student flow data is ready.")
        print(f"Student login: {STUDENT_EMAIL} / {STUDENT_PASSWORD}")
        print(f"Company logins use password: {COMPANY_PASSWORD}")
        print(f"Open job to apply successfully: {open_apply_job.job_title}")
        print(f"Ineligible visible jobs: {len(ineligible_jobs)}")
        print(f"Hidden non-approved jobs: {len(hidden_jobs)}")
        print("Application statuses ready: applied, shortlisted, interview_scheduled, selected, rejected, withdrawn")


if __name__ == "__main__":
    seed_student_flow_data()
