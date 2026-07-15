from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from extensions import cache
from mail_events import send_interview_scheduled_email, send_student_selected_email
from models import (
    Application,
    ApplicationStatusHistory,
    CompanyProfile,
    ExportJob,
    Interview,
    Notification,
    Placement,
    PlacementDrive,
    User,
    db,
    utc_now,
)


company_bp = Blueprint("company", __name__)

JOB_STATUS_INPUTS = {"active", "closed"}
JOB_STATUS_TO_DB = {
    "active": "approved",
    "closed": "closed",
}
DB_STATUS_TO_JOB_STATUS = {
    "pending": "pending_admin_approval",
    "approved": "active",
    "rejected": "rejected",
    "closed": "closed",
}
APPLICATION_TRANSITIONS = {
    "applied": {"shortlisted", "rejected"},
    "shortlisted": {"interview_scheduled", "selected", "rejected"},
    "interview_scheduled": {"selected", "rejected"},
    "selected": set(),
    "rejected": set(),
    "withdrawn": set(),
}


def validation_error(message):
    return jsonify({"message": message}), 400


def format_datetime(value):
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M")


def format_date(value):
    if value is None:
        return None
    return value.strftime("%Y-%m-%d")


def export_job_to_dict(export_job):
    return {
        "id": export_job.id,
        "export_type": export_job.export_type,
        "status": export_job.status,
        "file_path": export_job.file_path,
        "requested_at": format_datetime(export_job.requested_at),
        "completed_at": format_datetime(export_job.completed_at),
        "error_message": export_job.error_message,
    }


def parse_datetime(value, field_name):
    if not value:
        return None, validation_error(f"{field_name} is required")

    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None, validation_error(f"{field_name} must be a valid ISO datetime")

    if parsed.tzinfo:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)

    return parsed, None


def require_company_user():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if (
        not current_user
        or current_user.role != "company"
        or not current_user.is_active
        or current_user.is_blacklisted
    ):
        return None, None, (
            jsonify({
                "message": "Company access required",
                "role": current_user.role if current_user else None,
            }),
            403,
        )

    company = CompanyProfile.query.filter_by(user_id=current_user.id).first()

    if not company:
        return current_user, None, (
            jsonify({"message": "Company profile is incomplete"}),
            403,
        )

    if company.approval_status != "approved":
        return current_user, company, (
            jsonify({
                "message": "Company approval is required",
                "approval_status": company.approval_status,
            }),
            403,
        )

    return current_user, company, None


def company_job_or_404(company, job_id):
    job = db.session.get(PlacementDrive, job_id)

    if not job or job.company_id != company.id:
        return None, (jsonify({"message": "Job not found"}), 404)

    return job, None


def company_application_or_404(company, application_id):
    application = db.session.get(Application, application_id)

    if (
        not application
        or not application.drive
        or application.drive.company_id != company.id
    ):
        return None, (jsonify({"message": "Application not found"}), 404)

    return application, None


def job_to_dict(job):
    return {
        "id": job.id,
        "company_id": job.company_id,
        "job_title": job.job_title,
        "job_description": job.job_description,
        "location": job.location,
        "salary": job.salary,
        "skills_required": job.skills_required,
        "experience_required": job.experience_required,
        "benefits": job.benefits,
        "employment_type": job.employment_type,
        "min_cgpa": job.min_cgpa,
        "eligible_branches": job.eligible_branches,
        "eligible_year": job.eligible_year,
        "application_deadline": format_datetime(job.application_deadline),
        "drive_date": format_datetime(job.drive_date),
        "status": DB_STATUS_TO_JOB_STATUS.get(job.status, job.status),
        "admin_status": job.status,
        "rejection_reason": job.rejection_reason,
        "applications_count": len(job.applications),
        "created_at": format_datetime(job.created_at),
        "updated_at": format_datetime(job.updated_at),
    }


def company_to_dict(company):
    return {
        "id": company.id,
        "user_id": company.user_id,
        "email": company.user.email if company.user else None,
        "company_name": company.company_name,
        "industry": company.industry,
        "location": company.location,
        "hr_name": company.hr_name,
        "hr_contact": company.hr_contact,
        "website": company.website,
        "description": company.description,
        "approval_status": company.approval_status,
        "rejection_reason": company.rejection_reason,
        "created_at": format_datetime(company.created_at),
        "updated_at": format_datetime(company.updated_at),
    }


def interview_to_dict(interview):
    application = interview.application
    student = application.student if application else None
    user = student.user if student else None
    job = application.drive if application else None
    company = job.company if job else None

    return {
        "id": interview.id,
        "application_id": interview.application_id,
        "application_status": application.status if application else None,
        "application_remarks": application.remarks if application else None,
        "student_name": student.full_name if student else None,
        "student_email": user.email if user else None,
        "job_id": job.id if job else None,
        "job_title": job.job_title if job else None,
        "company_name": company.company_name if company else None,
        "scheduled_at": format_datetime(interview.scheduled_at),
        "mode": interview.mode,
        "venue_or_link": interview.venue_or_link,
        "round_name": interview.round_name,
        "status": interview.status,
        "feedback": interview.feedback,
        "created_at": format_datetime(interview.created_at),
        "updated_at": format_datetime(interview.updated_at),
    }


def status_history_to_dict(history):
    changed_by = history.changed_by_user

    return {
        "id": history.id,
        "old_status": history.old_status,
        "new_status": history.new_status,
        "note": history.note,
        "changed_at": format_datetime(history.changed_at),
        "changed_by_email": changed_by.email if changed_by else None,
        "changed_by_role": changed_by.role if changed_by else None,
    }


def placement_to_dict(placement):
    return {
        "id": placement.id,
        "application_id": placement.application_id,
        "position": placement.position,
        "salary": placement.salary,
        "joining_date": format_date(placement.joining_date),
        "status": placement.status,
        "placed_at": format_datetime(placement.placed_at),
        "created_at": format_datetime(placement.created_at),
        "updated_at": format_datetime(placement.updated_at),
    }


def application_to_dict(application, include_details=False):
    student = application.student
    user = student.user if student else None
    job = application.drive

    data = {
        "id": application.id,
        "student_id": application.student_id,
        "student_name": student.full_name if student else None,
        "student_roll_number": student.roll_number if student else None,
        "student_email": user.email if user else None,
        "student_branch": student.branch if student else None,
        "student_year": student.year if student else None,
        "student_cgpa": student.cgpa if student else None,
        "student_phone": student.phone if student else None,
        "student_resume_url": student.resume_url if student else None,
        "student_skills": student.skills if student else None,
        "student_experience": student.experience if student else None,
        "job_id": application.drive_id,
        "job_title": job.job_title if job else None,
        "status": application.status,
        "remarks": application.remarks,
        "application_date": format_datetime(application.application_date),
        "interviews": [interview_to_dict(interview) for interview in application.interviews],
        "created_at": format_datetime(application.created_at),
        "updated_at": format_datetime(application.updated_at),
    }

    if include_details:
        data["job"] = job_to_dict(job) if job else None
        data["status_history"] = [
            status_history_to_dict(history)
            for history in application.status_history
        ]
        data["placement"] = (
            placement_to_dict(application.placement)
            if application.placement
            else None
        )

    return data


@cache.memoize(timeout=300)
def get_cached_company_dashboard(company_id):
    company = db.session.get(CompanyProfile, company_id)
    job_ids = db.session.query(PlacementDrive.id).filter_by(company_id=company_id)

    return {
        "company": {
            "id": company.id,
            "company_name": company.company_name,
            "approval_status": company.approval_status,
        },
        "total_jobs": PlacementDrive.query.filter_by(company_id=company_id).count(),
        "active_jobs": PlacementDrive.query.filter_by(
            company_id=company_id,
            status="approved",
        ).count(),
        "pending_jobs": PlacementDrive.query.filter_by(
            company_id=company_id,
            status="pending",
        ).count(),
        "closed_jobs": PlacementDrive.query.filter_by(
            company_id=company_id,
            status="closed",
        ).count(),
        "received_applications": Application.query.filter(
            Application.drive_id.in_(job_ids)
        ).count(),
        "shortlisted_candidates": Application.query.filter(
            Application.drive_id.in_(job_ids),
            Application.status.in_(["shortlisted", "interview_scheduled"]),
        ).count(),
        "selected_candidates": Application.query.filter(
            Application.drive_id.in_(job_ids),
            Application.status == "selected",
        ).count(),
    }


@cache.memoize(timeout=300)
def get_cached_company_jobs(company_id, status):
    query = PlacementDrive.query.filter_by(company_id=company_id)

    if status:
        query = query.filter(PlacementDrive.status == JOB_STATUS_TO_DB.get(status, status))

    jobs = query.order_by(PlacementDrive.created_at.desc()).all()
    return [job_to_dict(job) for job in jobs]


@cache.memoize(timeout=300)
def get_cached_company_applications(company_id, status):
    query = (
        Application.query
        .join(Application.drive)
        .filter(PlacementDrive.company_id == company_id)
    )

    if status:
        query = query.filter(Application.status == status)

    applications = query.order_by(Application.application_date.desc()).all()
    return [application_to_dict(application) for application in applications]


@cache.memoize(timeout=300)
def get_cached_company_interviews(company_id):
    interviews = (
        Interview.query
        .join(Interview.application)
        .join(Application.drive)
        .filter(PlacementDrive.company_id == company_id)
        .order_by(Interview.scheduled_at.asc())
        .all()
    )

    return [interview_to_dict(interview) for interview in interviews]


def create_notification(user_id, title, message, notification_type):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
    )
    db.session.add(notification)


def change_application_status(application, new_status, note, changed_by_user):
    old_status = application.status

    if new_status == old_status:
        application.remarks = note or application.remarks
        return

    allowed_statuses = APPLICATION_TRANSITIONS.get(old_status, set())
    if new_status not in allowed_statuses:
        allowed = ", ".join(sorted(allowed_statuses)) or "none"
        return validation_error(
            f"Cannot change application status from {old_status} to {new_status}. "
            f"Allowed next statuses: {allowed}"
        )

    application.status = new_status
    application.remarks = note or application.remarks
    db.session.add(ApplicationStatusHistory(
        application=application,
        changed_by_user=changed_by_user,
        old_status=old_status,
        new_status=new_status,
        note=note,
    ))

    if application.student and application.student.user:
        create_notification(
            application.student.user.id,
            "Application status updated",
            f"Your application for {application.drive.job_title} is now {new_status}.",
            "application_status",
        )

    return None


def ensure_placement_for_selected_application(application):
    if application.status != "selected" or application.placement:
        return

    drive = application.drive
    placement = Placement(
        application=application,
        position=drive.job_title,
        salary=drive.salary,
    )
    db.session.add(placement)


def close_interviews_for_final_application_status(application, feedback=None):
    if application.status not in {"selected", "rejected"}:
        return

    now = utc_now()
    for interview in application.interviews:
        if interview.status != "scheduled":
            continue

        interview.status = "completed" if interview.scheduled_at <= now else "cancelled"
        if feedback and not interview.feedback:
            interview.feedback = feedback


def required_text(data, field_name):
    value = data.get(field_name)

    if value is None or str(value).strip() == "":
        return None, validation_error(f"{field_name} is required")

    return str(value).strip(), None


def number_value(data, field_name, minimum=None, maximum=None):
    value = data.get(field_name)

    if value in (None, ""):
        return None, validation_error(f"{field_name} is required")

    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None, validation_error(f"{field_name} must be a number")

    if minimum is not None and parsed < minimum:
        return None, validation_error(f"{field_name} must be at least {minimum}")

    if maximum is not None and parsed > maximum:
        return None, validation_error(f"{field_name} must be at most {maximum}")

    return parsed, None


def integer_value(data, field_name, minimum=None, maximum=None):
    parsed, error = number_value(data, field_name, minimum, maximum)

    if error:
        return None, error

    if int(parsed) != parsed:
        return None, validation_error(f"{field_name} must be a whole number")

    return int(parsed), None


def apply_job_payload(job, data, partial=False):
    text_fields = [
        "job_title",
        "job_description",
        "location",
        "skills_required",
        "experience_required",
        "benefits",
        "employment_type",
        "eligible_branches",
    ]

    for field_name in text_fields:
        if partial and field_name not in data:
            continue

        value, error = required_text(data, field_name)
        if error:
            return error
        setattr(job, field_name, value)

    numeric_fields = [
        ("salary", 0, None),
        ("min_cgpa", 0, 10),
    ]

    for field_name, minimum, maximum in numeric_fields:
        if partial and field_name not in data:
            continue

        value, error = number_value(data, field_name, minimum, maximum)
        if error:
            return error
        setattr(job, field_name, value)

    if not partial or "eligible_year" in data:
        value, error = integer_value(data, "eligible_year", 1, 4)
        if error:
            return error
        job.eligible_year = value

    if not partial or "application_deadline" in data:
        value, error = parse_datetime(data.get("application_deadline"), "application_deadline")
        if error:
            return error
        if value <= utc_now():
            return validation_error("application_deadline must be in the future")
        job.application_deadline = value

    if "drive_date" in data:
        if data.get("drive_date") in (None, ""):
            job.drive_date = None
        else:
            value, error = parse_datetime(data.get("drive_date"), "drive_date")
            if error:
                return error
            if job.application_deadline and value < job.application_deadline:
                return validation_error("drive_date cannot be before application_deadline")
            job.drive_date = value

    return None


def apply_company_profile_payload(company, data):
    required_fields = [
        "company_name",
        "industry",
        "location",
        "hr_name",
        "hr_contact",
    ]
    optional_fields = ["website", "description"]

    for field_name in required_fields:
        if field_name not in data:
            continue

        value, error = required_text(data, field_name)
        if error:
            return error
        setattr(company, field_name, value)

    for field_name in optional_fields:
        if field_name in data:
            value = data.get(field_name)
            setattr(company, field_name, str(value).strip() if value else None)

    return None


@company_bp.route("/api/company/profile", methods=["GET"])
@company_bp.route("/company/profile", methods=["GET"])
@jwt_required()
def get_company_profile():
    _, company, error = require_company_user()

    if error:
        return error

    return jsonify(company_to_dict(company)), 200


@company_bp.route("/api/company/profile", methods=["PATCH"])
@company_bp.route("/company/profile", methods=["PATCH"])
@jwt_required()
def update_company_profile():
    _, company, error = require_company_user()

    if error:
        return error

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Request body must be a JSON object"}), 400

    error = apply_company_profile_payload(company, data)
    if error:
        return error

    db.session.commit()
    cache.clear()

    return jsonify({
        "message": "Company profile updated successfully",
        "company": company_to_dict(company),
    }), 200


@company_bp.route("/api/company/dashboard", methods=["GET"])
@company_bp.route("/company/dashboard", methods=["GET"])
@jwt_required()
def company_dashboard():
    _, company, error = require_company_user()

    if error:
        return error

    return jsonify(get_cached_company_dashboard(company.id)), 200


@company_bp.route("/api/company/jobs", methods=["GET"])
@company_bp.route("/company/jobs", methods=["GET"])
@jwt_required()
def get_company_jobs():
    _, company, error = require_company_user()

    if error:
        return error

    status = request.args.get("status", "").strip()

    if status:
        if status not in {"pending", "active", "rejected", "closed"}:
            return validation_error("Invalid status filter")

    return jsonify(get_cached_company_jobs(company.id, status)), 200


@company_bp.route("/api/company/jobs", methods=["POST"])
@company_bp.route("/company/jobs", methods=["POST"])
@jwt_required()
def create_company_job():
    _, company, error = require_company_user()

    if error:
        return error

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Request body must be a JSON object"}), 400

    job = PlacementDrive(company_id=company.id, status="pending")
    error = apply_job_payload(job, data)

    if error:
        return error

    try:
        db.session.add(job)
        db.session.commit()
    except (IntegrityError, ValueError, TypeError):
        db.session.rollback()
        return validation_error("Job data is invalid")

    cache.clear()

    return jsonify({
        "message": "Job posted successfully and is pending admin approval",
        "job": job_to_dict(job),
    }), 201


@company_bp.route("/api/company/jobs/<int:job_id>", methods=["GET"])
@company_bp.route("/company/jobs/<int:job_id>", methods=["GET"])
@jwt_required()
def get_company_job(job_id):
    _, company, error = require_company_user()

    if error:
        return error

    job, error = company_job_or_404(company, job_id)
    if error:
        return error

    return jsonify(job_to_dict(job)), 200


@company_bp.route("/api/company/jobs/<int:job_id>", methods=["PATCH"])
@company_bp.route("/company/jobs/<int:job_id>", methods=["PATCH"])
@jwt_required()
def update_company_job(job_id):
    _, company, error = require_company_user()

    if error:
        return error

    job, error = company_job_or_404(company, job_id)
    if error:
        return error

    if job.status in {"rejected", "closed"}:
        return validation_error("Rejected or closed jobs cannot be edited")

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Request body must be a JSON object"}), 400

    error = apply_job_payload(job, data, partial=True)

    if error:
        return error

    try:
        db.session.commit()
    except (IntegrityError, ValueError, TypeError):
        db.session.rollback()
        return validation_error("Job data is invalid")

    cache.clear()

    return jsonify({
        "message": "Job updated successfully",
        "job": job_to_dict(job),
    }), 200


@company_bp.route("/api/company/jobs/<int:job_id>/status", methods=["PATCH"])
@company_bp.route("/company/jobs/<int:job_id>/status", methods=["PATCH"])
@jwt_required()
def update_company_job_status(job_id):
    _, company, error = require_company_user()

    if error:
        return error

    job, error = company_job_or_404(company, job_id)
    if error:
        return error

    data = request.get_json(silent=True) or {}
    requested_status = (data.get("status") or "").strip().lower()

    if requested_status not in JOB_STATUS_INPUTS:
        return validation_error("status must be active or closed")

    if job.status in {"pending", "rejected"}:
        return validation_error("Only active or closed jobs can be managed by company")

    if requested_status == "active" and job.application_deadline <= utc_now():
        return validation_error("Cannot reactivate a job after the application deadline")

    job.status = JOB_STATUS_TO_DB[requested_status]
    db.session.commit()
    cache.clear()

    return jsonify({
        "message": "Job status updated successfully",
        "job": job_to_dict(job),
    }), 200


@company_bp.route("/api/company/jobs/<int:job_id>/applications", methods=["GET"])
@company_bp.route("/company/jobs/<int:job_id>/applications", methods=["GET"])
@jwt_required()
def get_job_applications(job_id):
    _, company, error = require_company_user()

    if error:
        return error

    job, error = company_job_or_404(company, job_id)
    if error:
        return error

    applications = (
        Application.query
        .filter_by(drive_id=job.id)
        .order_by(Application.application_date.desc())
        .all()
    )

    return jsonify([application_to_dict(application) for application in applications]), 200


@company_bp.route("/api/company/applications", methods=["GET"])
@company_bp.route("/company/applications", methods=["GET"])
@jwt_required()
def get_company_applications():
    _, company, error = require_company_user()

    if error:
        return error

    status = request.args.get("status", "").strip()

    if status:
        if status not in set(APPLICATION_TRANSITIONS.keys()):
            return validation_error("Invalid application status filter")

    return jsonify(get_cached_company_applications(company.id, status)), 200


@company_bp.route("/api/company/applications/<int:application_id>", methods=["GET"])
@company_bp.route("/company/applications/<int:application_id>", methods=["GET"])
@jwt_required()
def get_company_application(application_id):
    _, company, error = require_company_user()

    if error:
        return error

    application, error = company_application_or_404(company, application_id)
    if error:
        return error

    return jsonify(application_to_dict(application, include_details=True)), 200


def update_application_status_with_payload(application_id, data):
    current_user, company, error = require_company_user()

    if error:
        return error

    application, error = company_application_or_404(company, application_id)
    if error:
        return error

    new_status = (data.get("status") or "").strip().lower()
    feedback = (data.get("feedback") or data.get("remarks") or "").strip()

    if new_status not in {"shortlisted", "selected", "rejected"}:
        return validation_error("status must be shortlisted, selected, or rejected")

    if new_status == "rejected" and not feedback:
        return validation_error("feedback is required when rejecting an applicant")

    old_status = application.status
    error = change_application_status(application, new_status, feedback, current_user)
    if error:
        return error

    close_interviews_for_final_application_status(application, feedback)
    ensure_placement_for_selected_application(application)
    db.session.commit()
    cache.clear()

    if new_status == "selected" and old_status != "selected":
        send_student_selected_email(application)

    return jsonify({
        "message": "Application status updated successfully",
        "application": application_to_dict(application),
    }), 200


@company_bp.route("/api/company/applications/<int:application_id>/status", methods=["PATCH"])
@company_bp.route("/company/applications/<int:application_id>/status", methods=["PATCH"])
@jwt_required()
def update_application_status(application_id):
    data = request.get_json(silent=True) or {}
    return update_application_status_with_payload(application_id, data)


@company_bp.route("/api/company/applications/<int:application_id>/shortlist", methods=["PATCH"])
@company_bp.route("/company/applications/<int:application_id>/shortlist", methods=["PATCH"])
@jwt_required()
def shortlist_application(application_id):
    data = request.get_json(silent=True) or {}
    data["status"] = "shortlisted"
    return update_application_status_with_payload(application_id, data)


@company_bp.route("/api/company/applications/<int:application_id>/reject", methods=["PATCH"])
@company_bp.route("/company/applications/<int:application_id>/reject", methods=["PATCH"])
@jwt_required()
def reject_application(application_id):
    data = request.get_json(silent=True) or {}
    data["status"] = "rejected"
    return update_application_status_with_payload(application_id, data)


@company_bp.route("/api/company/applications/<int:application_id>/select", methods=["PATCH"])
@company_bp.route("/company/applications/<int:application_id>/select", methods=["PATCH"])
@jwt_required()
def select_application(application_id):
    data = request.get_json(silent=True) or {}
    data["status"] = "selected"
    return update_application_status_with_payload(application_id, data)


@company_bp.route("/api/company/applications/<int:application_id>/interviews", methods=["POST"])
@company_bp.route("/company/applications/<int:application_id>/interviews", methods=["POST"])
@jwt_required()
def schedule_interview(application_id):
    current_user, company, error = require_company_user()

    if error:
        return error

    application, error = company_application_or_404(company, application_id)
    if error:
        return error

    if application.status not in {"shortlisted", "interview_scheduled"}:
        return validation_error("Only shortlisted applicants can be scheduled for interview")

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Request body must be a JSON object"}), 400

    scheduled_at, error = parse_datetime(data.get("scheduled_at"), "scheduled_at")
    if error:
        return error

    if scheduled_at <= utc_now():
        return validation_error("scheduled_at must be in the future")

    mode = (data.get("mode") or "").strip().lower()
    if mode not in {"online", "offline"}:
        return validation_error("mode must be online or offline")

    interview = Interview(
        application=application,
        scheduled_at=scheduled_at,
        mode=mode,
        venue_or_link=(data.get("venue_or_link") or "").strip() or None,
        round_name=(data.get("round_name") or "").strip() or None,
    )
    db.session.add(interview)

    error = change_application_status(
        application,
        "interview_scheduled",
        "Interview scheduled",
        current_user,
    )
    if error:
        return error

    if application.student and application.student.user:
        create_notification(
            application.student.user.id,
            "Interview scheduled",
            f"Your interview for {application.drive.job_title} is scheduled.",
            "interview",
        )

    db.session.commit()
    cache.clear()
    send_interview_scheduled_email(application, interview)

    return jsonify({
        "message": "Interview scheduled successfully",
        "interview": interview_to_dict(interview),
        "application": application_to_dict(application),
    }), 201


@company_bp.route("/api/company/interviews", methods=["GET"])
@company_bp.route("/company/interviews", methods=["GET"])
@jwt_required()
def get_company_interviews():
    _, company, error = require_company_user()

    if error:
        return error

    return jsonify(get_cached_company_interviews(company.id)), 200


@company_bp.route("/api/company/exports/<export_type>", methods=["POST"])
@company_bp.route("/company/exports/<export_type>", methods=["POST"])
@jwt_required()
def start_company_export(export_type):
    current_user, _, error = require_company_user()

    if error:
        return error

    if export_type not in {"application_history", "placement_history"}:
        return validation_error("export_type must be application_history or placement_history")

    export_job = ExportJob(
        requested_by_user_id=current_user.id,
        export_type=export_type,
        status="pending",
    )
    db.session.add(export_job)
    db.session.commit()

    try:
        from tasks import export_history_csv
        export_history_csv.delay(export_job.id)
    except Exception as exc:
        export_job.status = "failed"
        export_job.error_message = str(exc)
        db.session.commit()
        return jsonify({
            "message": "Could not queue export job. Please make sure Redis is running.",
            "export_job": export_job_to_dict(export_job),
        }), 503

    return jsonify({
        "message": "Export started. You will be notified when it is ready.",
        "export_job": export_job_to_dict(export_job),
    }), 202


@company_bp.route("/api/company/exports", methods=["GET"])
@company_bp.route("/company/exports", methods=["GET"])
@jwt_required()
def get_company_exports():
    current_user, _, error = require_company_user()

    if error:
        return error

    exports = (
        ExportJob.query
        .filter_by(requested_by_user_id=current_user.id)
        .order_by(ExportJob.requested_at.desc())
        .all()
    )

    return jsonify([export_job_to_dict(export_job) for export_job in exports]), 200


@company_bp.route("/api/company/exports/<int:export_id>/download", methods=["GET"])
@company_bp.route("/company/exports/<int:export_id>/download", methods=["GET"])
@jwt_required()
def download_company_export(export_id):
    current_user, _, error = require_company_user()

    if error:
        return error

    export_job = db.session.get(ExportJob, export_id)

    if not export_job or export_job.requested_by_user_id != current_user.id:
        return jsonify({"message": "Export not found"}), 404

    if export_job.status != "completed" or not export_job.file_path:
        return validation_error("Export is not ready yet")

    return send_file(export_job.file_path, as_attachment=True)
