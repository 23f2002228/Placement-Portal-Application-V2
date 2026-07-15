import csv
import os
from datetime import timedelta

from flask import render_template
from sqlalchemy.exc import IntegrityError

from celery_worker import celery_app
from email_utils import send_email
from models import (
    Application,
    CompanyProfile,
    ExportJob,
    Interview,
    MonthlyReport,
    Notification,
    Placement,
    PlacementDrive,
    StudentProfile,
    User,
    db,
    utc_now,
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_DIR = os.path.join(BASE_DIR, "generated")
EXPORT_DIR = os.path.join(GENERATED_DIR, "exports")
REPORT_DIR = os.path.join(GENERATED_DIR, "reports")


def ensure_generated_dirs():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)


def create_notification(user_id, title, message, notification_type):
    db.session.add(Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
    ))


def try_send_email(*args, **kwargs):
    try:
        return send_email(*args, **kwargs)
    except Exception:
        return False


def format_datetime(value):
    return value.strftime("%Y-%m-%d %H:%M") if value else ""


def previous_month(today):
    if today.month == 1:
        return 12, today.year - 1
    return today.month - 1, today.year


def month_range(month, year):
    start = utc_now().replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
    if month == 12:
        end = start.replace(year=year + 1, month=1)
    else:
        end = start.replace(month=month + 1)
    return start, end


def write_csv(file_path, fieldnames, rows):
    ensure_generated_dirs()
    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def student_application_rows(user):
    student = user.student_profile
    applications = (
        Application.query
        .filter_by(student_id=student.id)
        .order_by(Application.application_date.desc())
        .all()
    )

    return [
        {
            "student_id": student.id,
            "company_name": application.drive.company.company_name if application.drive and application.drive.company else "",
            "drive_title": application.drive.job_title if application.drive else "",
            "application_status": application.status,
            "application_date": format_datetime(application.application_date),
            "updated_at": format_datetime(application.updated_at),
            "remarks": application.remarks or "",
        }
        for application in applications
    ]


def student_placement_rows(user):
    student = user.student_profile
    placements = (
        Placement.query
        .join(Placement.application)
        .filter(Application.student_id == student.id)
        .order_by(Placement.placed_at.desc())
        .all()
    )

    return [
        {
            "company_name": placement.application.drive.company.company_name if placement.application and placement.application.drive and placement.application.drive.company else "",
            "job_title": placement.application.drive.job_title if placement.application and placement.application.drive else "",
            "position": placement.position,
            "salary": placement.salary,
            "status": placement.status,
            "placed_at": format_datetime(placement.placed_at),
        }
        for placement in placements
    ]


def company_application_rows(user):
    company = user.company_profile
    applications = (
        Application.query
        .join(Application.drive)
        .filter(PlacementDrive.company_id == company.id)
        .order_by(Application.application_date.desc())
        .all()
    )

    return [
        {
            "student_name": application.student.full_name if application.student else "",
            "student_email": application.student.user.email if application.student and application.student.user else "",
            "job_title": application.drive.job_title if application.drive else "",
            "status": application.status,
            "application_date": format_datetime(application.application_date),
            "remarks": application.remarks or "",
        }
        for application in applications
    ]


def company_placement_rows(user):
    company = user.company_profile
    placements = (
        Placement.query
        .join(Placement.application)
        .join(Application.drive)
        .filter(PlacementDrive.company_id == company.id)
        .order_by(Placement.placed_at.desc())
        .all()
    )

    return [
        {
            "student_name": placement.application.student.full_name if placement.application and placement.application.student else "",
            "student_email": placement.application.student.user.email if placement.application and placement.application.student and placement.application.student.user else "",
            "job_title": placement.application.drive.job_title if placement.application and placement.application.drive else "",
            "position": placement.position,
            "salary": placement.salary,
            "status": placement.status,
            "placed_at": format_datetime(placement.placed_at),
        }
        for placement in placements
    ]


@celery_app.task
def export_history_csv(export_job_id):
    export_job = db.session.get(ExportJob, export_job_id)
    if not export_job:
        return "Export job not found"

    user = export_job.requested_by_user
    if not user:
        export_job.status = "failed"
        export_job.error_message = "User not found"
        db.session.commit()
        return export_job.error_message

    export_job.status = "running"
    db.session.commit()

    try:
        if user.role == "student" and export_job.export_type == "application_history":
            rows = student_application_rows(user)
            fieldnames = [
                "student_id",
                "company_name",
                "drive_title",
                "application_status",
                "application_date",
                "updated_at",
                "remarks",
            ]
        elif user.role == "student" and export_job.export_type == "placement_history":
            rows = student_placement_rows(user)
            fieldnames = ["company_name", "job_title", "position", "salary", "status", "placed_at"]
        elif user.role == "company" and export_job.export_type == "application_history":
            rows = company_application_rows(user)
            fieldnames = ["student_name", "student_email", "job_title", "status", "application_date", "remarks"]
        elif user.role == "company" and export_job.export_type == "placement_history":
            rows = company_placement_rows(user)
            fieldnames = ["student_name", "student_email", "job_title", "position", "salary", "status", "placed_at"]
        else:
            raise ValueError("This export type is not available for your role")

        filename = f"export_{export_job.id}_{user.role}_{export_job.export_type}.csv"
        file_path = os.path.join(EXPORT_DIR, filename)
        write_csv(file_path, fieldnames, rows)

        export_job.status = "completed"
        export_job.file_path = file_path
        export_job.completed_at = utc_now()
        export_job.error_message = None
        create_notification(
            user.id,
            "CSV export ready",
            f"Your {export_job.export_type.replace('_', ' ')} export is ready to download.",
            "export",
        )
        db.session.commit()

        html = render_template("export_complete.html", user=user, export_job=export_job)
        try_send_email(
            user.email,
            "Your Placement Portal CSV export is ready",
            html,
            content="html",
            attachment=file_path,
        )
        return f"Export job {export_job.id} completed"
    except Exception as exc:
        export_job.status = "failed"
        export_job.error_message = str(exc)
        create_notification(
            user.id,
            "CSV export failed",
            f"Your {export_job.export_type.replace('_', ' ')} export could not be generated.",
            "export",
        )
        db.session.commit()
        return f"Export job {export_job.id} failed: {exc}"


def student_is_eligible_for_drive(student, drive):
    if drive.status != "approved":
        return False

    if drive.application_deadline <= utc_now():
        return False

    if student.cgpa < drive.min_cgpa:
        return False

    if student.year != drive.eligible_year:
        return False

    allowed_branches = [
        branch.strip().lower()
        for branch in (drive.eligible_branches or "").split(",")
        if branch.strip()
    ]

    return "all" in allowed_branches or student.branch.lower() in allowed_branches


@celery_app.task
def send_application_deadline_reminders():
    now = utc_now()
    reminder_until = now + timedelta(days=1)
    drives = (
        PlacementDrive.query
        .filter_by(status="approved")
        .filter(PlacementDrive.application_deadline >= now)
        .filter(PlacementDrive.application_deadline <= reminder_until)
        .order_by(PlacementDrive.application_deadline.asc())
        .all()
    )

    students = (
        StudentProfile.query
        .join(User)
        .filter(User.is_active.is_(True))
        .filter(User.is_blacklisted.is_(False))
        .all()
    )

    sent_count = 0
    for drive in drives:
        for student in students:
            user = student.user

            if not user or not student_is_eligible_for_drive(student, drive):
                continue

            existing_application = Application.query.filter_by(
                student_id=student.id,
                drive_id=drive.id,
            ).first()
            if existing_application:
                continue

            marker = f"drive #{drive.id}"
            existing_notification = (
                Notification.query
                .filter_by(user_id=user.id, notification_type="deadline", title="Application deadline reminder")
                .filter(Notification.message.contains(marker))
                .first()
            )
            if existing_notification:
                continue

            html = render_template(
                "application_deadline_reminder.html",
                student=student,
                drive=drive,
                company=drive.company,
            )
            try_send_email(user.email, f"Application Deadline Reminder - {drive.job_title}", html, content="html")
            create_notification(
                user.id,
                "Application deadline reminder",
                f"{drive.job_title} applications close at {format_datetime(drive.application_deadline)} ({marker}).",
                "deadline",
            )
            sent_count += 1

    db.session.commit()
    return f"Sent {sent_count} application deadline reminders"


@celery_app.task
def send_interview_reminders():
    now = utc_now()
    reminder_until = now + timedelta(days=1)
    interviews = (
        Interview.query
        .filter(Interview.status == "scheduled")
        .filter(Interview.scheduled_at >= now)
        .filter(Interview.scheduled_at <= reminder_until)
        .order_by(Interview.scheduled_at.asc())
        .all()
    )

    sent_count = 0
    for interview in interviews:
        application = interview.application
        student = application.student if application else None
        user = student.user if student else None
        drive = application.drive if application else None
        company = drive.company if drive else None

        if not user or not drive:
            continue

        marker = f"interview #{interview.id}"
        existing_notification = (
            Notification.query
            .filter_by(user_id=user.id, notification_type="interview", title="Interview reminder")
            .filter(Notification.message.contains(marker))
            .first()
        )
        if existing_notification:
            continue

        html = render_template(
            "interview_reminder.html",
            student=student,
            interview=interview,
            drive=drive,
            company=company,
        )
        try_send_email(user.email, f"Interview Reminder - {drive.job_title}", html, content="html")
        create_notification(
            user.id,
            "Interview reminder",
            f"Reminder for {drive.job_title} scheduled at {format_datetime(interview.scheduled_at)} ({marker}).",
            "interview",
        )
        sent_count += 1

    db.session.commit()
    return f"Sent {sent_count} interview reminders"


@celery_app.task
def generate_monthly_admin_report(month=None, year=None):
    today = utc_now()
    if month is None or year is None:
        month, year = previous_month(today)

    start, end = month_range(month, year)
    total_drives = (
        PlacementDrive.query
        .filter(PlacementDrive.created_at >= start)
        .filter(PlacementDrive.created_at < end)
        .count()
    )
    total_applications = (
        Application.query
        .filter(Application.application_date >= start)
        .filter(Application.application_date < end)
        .count()
    )
    total_selected = (
        Application.query
        .filter(Application.updated_at >= start)
        .filter(Application.updated_at < end)
        .filter(Application.status == "selected")
        .count()
    )

    ensure_generated_dirs()
    filename = f"admin_{year}_{month:02d}.html"
    file_path = os.path.join(REPORT_DIR, filename)
    html = render_template(
        "admin_monthly_report.html",
        month=month,
        year=year,
        total_drives=total_drives,
        total_applications=total_applications,
        total_selected=total_selected,
    )

    with open(file_path, "w", encoding="utf-8") as report_file:
        report_file.write(html)

    admins = User.query.filter_by(role="admin", is_active=True, is_blacklisted=False).all()
    sent_count = 0
    for admin in admins:
        if try_send_email(
            admin.email,
            f"Monthly Placement Activity Report - {month:02d}/{year}",
            html,
            content="html",
        ):
            sent_count += 1

        create_notification(
            admin.id,
            "Monthly placement report",
            f"Institute activity report for {month:02d}/{year} has been generated.",
            "report",
        )

    db.session.commit()
    return f"Generated admin monthly report and sent {sent_count} emails"


@celery_app.task
def generate_monthly_company_reports(month=None, year=None):
    today = utc_now()
    if month is None or year is None:
        month, year = previous_month(today)

    start, end = month_range(month, year)
    companies = CompanyProfile.query.filter_by(approval_status="approved").all()
    generated_count = 0

    for company in companies:
        drives_query = PlacementDrive.query.filter_by(company_id=company.id)
        month_drives = drives_query.filter(
            PlacementDrive.created_at >= start,
            PlacementDrive.created_at < end,
        ).count()
        applications_query = (
            Application.query
            .join(Application.drive)
            .filter(PlacementDrive.company_id == company.id)
            .filter(Application.application_date >= start)
            .filter(Application.application_date < end)
        )
        total_applications = applications_query.count()
        total_selected = applications_query.filter(Application.status == "selected").count()
        total_placements = (
            Placement.query
            .join(Placement.application)
            .join(Application.drive)
            .filter(PlacementDrive.company_id == company.id)
            .filter(Placement.placed_at >= start)
            .filter(Placement.placed_at < end)
            .count()
        )

        report = MonthlyReport.query.filter_by(
            company_id=company.id,
            month=month,
            year=year,
        ).first()
        if not report:
            report = MonthlyReport(company_id=company.id, month=month, year=year)
            db.session.add(report)

        report.total_drives = month_drives
        report.total_applications = total_applications
        report.total_selected = total_selected

        filename = f"company_{company.id}_{year}_{month:02d}.html"
        file_path = os.path.join(REPORT_DIR, filename)
        ensure_generated_dirs()
        html = render_template(
            "monthly_report.html",
            company=company,
            month=month,
            year=year,
            total_drives=month_drives,
            total_applications=total_applications,
            total_selected=total_selected,
            total_placements=total_placements,
        )
        with open(file_path, "w", encoding="utf-8") as report_file:
            report_file.write(html)

        report.report_html_path = file_path
        if company.user:
            report.sent_to_company = try_send_email(
                company.user.email,
                f"Monthly Placement Report - {month:02d}/{year}",
                html,
                content="html",
            )
            create_notification(
                company.user.id,
                "Monthly placement report",
                f"Your placement report for {month:02d}/{year} has been generated.",
                "report",
            )

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            continue

        generated_count += 1

    return f"Generated {generated_count} monthly reports"
