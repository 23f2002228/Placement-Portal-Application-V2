import sqlite3
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()


def utc_now():
    """Return the current UTC time in the naive format used by SQLite."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """Make SQLite enforce the foreign keys declared by the models."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_blacklisted = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )

    __table_args__ = (
        db.CheckConstraint(
            "role IN ('admin', 'company', 'student')",
            name="check_user_role"
        ),
    )

    student_profile = db.relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    company_profile = db.relationship(
        "CompanyProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    notifications = db.relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    application_status_changes = db.relationship(
        "ApplicationStatusHistory",
        back_populates="changed_by_user"
    )

    export_jobs = db.relationship(
        "ExportJob",
        back_populates="requested_by_user",
        cascade="all, delete-orphan"
    )

class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    full_name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)

    degree = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)

    phone = db.Column(db.String(20))
    resume_url = db.Column(db.String(255))
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )

    __table_args__ = (
        db.CheckConstraint("year BETWEEN 1 AND 4", name="check_student_year"),
        db.CheckConstraint("cgpa BETWEEN 0 AND 10", name="check_student_cgpa"),
    )

    user = db.relationship("User", back_populates="student_profile")

    applications = db.relationship(
        "Application",
        back_populates="student",
        cascade="all, delete-orphan"
    )

class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    company_name = db.Column(db.String(120), nullable=False)
    industry = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    hr_name = db.Column(db.String(120), nullable=False)
    hr_contact = db.Column(db.String(120), nullable=False)

    website = db.Column(db.String(255))
    description = db.Column(db.Text)

    approval_status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )

    rejection_reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )

    __table_args__ = (
        db.CheckConstraint(
            "approval_status IN ('pending', 'approved', 'rejected')",
            name="check_company_approval_status"
        ),
    )

    user = db.relationship("User", back_populates="company_profile")

    drives = db.relationship(
        "PlacementDrive",
        back_populates="company",
        cascade="all, delete-orphan"
    )

    monthly_reports = db.relationship(
        "MonthlyReport",
        back_populates="company",
        cascade="all, delete-orphan"
    )

class PlacementDrive(db.Model):
    """A job position and its associated campus recruitment drive."""

    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company_profiles.id"),
        nullable=False
    )

    job_title = db.Column(db.String(120), nullable=False)
    job_description = db.Column(db.Text, nullable=False)

    location = db.Column(db.String(120), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    skills_required = db.Column(db.Text, nullable=False)
    experience_required = db.Column(
        db.String(120),
        nullable=False,
        default="Not specified"
    )
    benefits = db.Column(db.Text)
    employment_type = db.Column(db.String(50), nullable=False)

    min_cgpa = db.Column(db.Float, nullable=False)

    eligible_branches = db.Column(db.Text, nullable=False)

    eligible_year = db.Column(db.Integer, nullable=False)

    application_deadline = db.Column(db.DateTime, nullable=False)
    drive_date = db.Column(db.DateTime)

    status = db.Column(db.String(20), nullable=False, default="pending")

    rejection_reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )

    __table_args__ = (
        db.CheckConstraint("salary >= 0", name="check_drive_salary"),
        db.CheckConstraint(
            "min_cgpa BETWEEN 0 AND 10",
            name="check_drive_min_cgpa"
        ),
        db.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'closed')",
            name="check_drive_status"
        ),
        db.CheckConstraint(
            "eligible_year BETWEEN 1 AND 4",
            name="check_drive_eligible_year"    
        )
    )

    #many side of the relationship with CompanyProfile
    company = db.relationship("CompanyProfile", back_populates="drives")

    #one side of the relationship with Application
    applications = db.relationship(
        "Application",
        back_populates="drive",
        cascade="all, delete-orphan"
    )

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student_profiles.id"),
        nullable=False
    )

    drive_id = db.Column(
        db.Integer,
        db.ForeignKey("placement_drives.id"),
        nullable=False
    )

    application_date = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now
    )


    status = db.Column(db.String(30), nullable=False, default="applied")

    remarks = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        default=utc_now,
        onupdate=utc_now
    )

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "drive_id",
            name="unique_student_drive_application"
        ),
        db.CheckConstraint(
            "status IN ('applied', 'shortlisted', 'interview_scheduled', "
            "'selected', 'rejected', 'withdrawn')",
            name="check_application_status"
        ),
    )

    
    student = db.relationship("StudentProfile", back_populates="applications")
    drive = db.relationship("PlacementDrive", back_populates="applications")

    
    interviews = db.relationship(
        "Interview",
        back_populates="application",
        cascade="all, delete-orphan"
    )

    status_history = db.relationship(
        "ApplicationStatusHistory",
        back_populates="application",
        cascade="all, delete-orphan"
    )

    placement = db.relationship(
        "Placement",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan"
    )


class Placement(db.Model):
    __tablename__ = "placements"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id"),
        unique=True,
        nullable=False
    )
    position = db.Column(db.String(120), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    joining_date = db.Column(db.Date)
    status = db.Column(db.String(20), nullable=False, default="offered")
    placed_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now
    )

    __table_args__ = (
        db.CheckConstraint("salary >= 0", name="check_placement_salary"),
        db.CheckConstraint(
            "status IN ('offered', 'accepted', 'declined', 'joined')",
            name="check_placement_status"
        ),
    )

    application = db.relationship("Application", back_populates="placement")


class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id"),
        nullable=False
    )
    scheduled_at = db.Column(db.DateTime, nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    venue_or_link = db.Column(db.String(255))
    round_name = db.Column(db.String(100))
    status = db.Column(db.String(20), nullable=False, default="scheduled")
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now
    )

    __table_args__ = (
        db.CheckConstraint(
            "mode IN ('online', 'offline')",
            name="check_interview_mode"
        ),
        db.CheckConstraint(
            "status IN ('scheduled', 'completed', 'cancelled')",
            name="check_interview_status"
        ),
    )

    application = db.relationship("Application", back_populates="interviews")


class ApplicationStatusHistory(db.Model):
    __tablename__ = "application_status_history"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(
        db.Integer,
        db.ForeignKey("applications.id"),
        nullable=False
    )
    changed_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    old_status = db.Column(db.String(30))
    new_status = db.Column(db.String(30), nullable=False)
    note = db.Column(db.Text)
    changed_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    __table_args__ = (
        db.CheckConstraint(
            "old_status IS NULL OR old_status IN ('applied', 'shortlisted', "
            "'interview_scheduled', 'selected', 'rejected', 'withdrawn')",
            name="check_history_old_status"
        ),
        db.CheckConstraint(
            "new_status IN ('applied', 'shortlisted', "
            "'interview_scheduled', 'selected', 'rejected', 'withdrawn')",
            name="check_history_new_status"
        ),
    )

    application = db.relationship("Application", back_populates="status_history")
    changed_by_user = db.relationship(
        "User",
        back_populates="application_status_changes"
    )


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(
        db.String(30),
        nullable=False,
        default="system"
    )
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    __table_args__ = (
        db.CheckConstraint(
            "notification_type IN ('system', 'application_status', "
            "'interview', 'approval', 'deadline', 'export', 'report')",
            name="check_notification_type"
        ),
    )

    user = db.relationship("User", back_populates="notifications")


class ExportJob(db.Model):
    __tablename__ = "export_jobs"

    id = db.Column(db.Integer, primary_key=True)
    requested_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    export_type = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    file_path = db.Column(db.String(255))
    requested_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)

    __table_args__ = (
        db.CheckConstraint(
            "export_type IN ('application_history', 'placement_history')",
            name="check_export_type"
        ),
        db.CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed')",
            name="check_export_status"
        ),
    )

    requested_by_user = db.relationship("User", back_populates="export_jobs")


class MonthlyReport(db.Model):
    __tablename__ = "monthly_reports"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company_profiles.id"),
        nullable=False
    )
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_drives = db.Column(db.Integer, nullable=False, default=0)
    total_applications = db.Column(db.Integer, nullable=False, default=0)
    total_selected = db.Column(db.Integer, nullable=False, default=0)
    report_html_path = db.Column(db.String(255))
    sent_to_company = db.Column(db.Boolean, nullable=False, default=False)
    generated_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    __table_args__ = (
        db.UniqueConstraint(
            "company_id",
            "month",
            "year",
            name="unique_company_monthly_report"
        ),
        db.CheckConstraint("month BETWEEN 1 AND 12", name="check_report_month"),
        db.CheckConstraint(
            "total_drives >= 0 AND total_applications >= 0 "
            "AND total_selected >= 0",
            name="check_report_totals"
        ),
    )

    company = db.relationship("CompanyProfile", back_populates="monthly_reports")
