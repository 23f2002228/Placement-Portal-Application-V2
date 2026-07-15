from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_

from extensions import cache
from mail_events import send_company_approval_email, send_company_rejection_email
from models import Application, CompanyProfile, PlacementDrive, StudentProfile, User, db


admin_bp = Blueprint("admin", __name__)

COMPANY_STATUSES = {"pending", "approved", "rejected"}
DRIVE_STATUSES = {"pending", "approved", "rejected", "closed"}
APPLICATION_STATUSES = {
    "applied",
    "shortlisted",
    "interview_scheduled",
    "selected",
    "rejected",
    "withdrawn",
}
COMPANY_SEARCH_FIELDS = {"all", "name", "industry", "location", "email"}


def require_admin_user():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if (
        not current_user
        or current_user.role != "admin"
        or not current_user.is_active
        or current_user.is_blacklisted
    ):
        return None, (
            jsonify({
                "message": "Admin access required",
                "role": current_user.role if current_user else None,
            }),
            403,
        )

    return current_user, None


def validation_error(message):
    return jsonify({"message": message}), 400


def require_reason(data, field_name="reason"):
    reason = (data.get(field_name) or "").strip()

    if not reason:
        return None, validation_error("Rejection reason is required")

    return reason, None


def validate_filter(value, allowed_values, field_name):
    if value and value not in allowed_values:
        allowed = ", ".join(sorted(allowed_values))
        return validation_error(f"Invalid {field_name}. Allowed values: {allowed}")

    return None


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
        "is_active": company.user.is_active if company.user else False,
        "is_blacklisted": company.user.is_blacklisted if company.user else False,
        "created_at": company.created_at,
        "updated_at": company.updated_at,
    }


def student_to_dict(student):
    return {
        "id": student.id,
        "user_id": student.user_id,
        "email": student.user.email if student.user else None,
        "full_name": student.full_name,
        "roll_number": student.roll_number,
        "degree": student.degree,
        "branch": student.branch,
        "year": student.year,
        "graduation_year": student.graduation_year,
        "cgpa": student.cgpa,
        "phone": student.phone,
        "resume_url": student.resume_url,
        "skills": student.skills,
        "experience": student.experience,
        "is_active": student.user.is_active if student.user else False,
        "is_blacklisted": student.user.is_blacklisted if student.user else False,
        "created_at": student.created_at,
        "updated_at": student.updated_at,
    }


@cache.memoize(timeout=300)
def get_cached_students(search):
    query = StudentProfile.query.join(User)

    if search:
        pattern = f"%{search}%"
        search_filters = [
            StudentProfile.full_name.ilike(pattern),
            StudentProfile.roll_number.ilike(pattern),
            StudentProfile.phone.ilike(pattern),
            User.email.ilike(pattern),
        ]

        if search.isdigit():
            search_filters.append(StudentProfile.id == int(search))

        query = query.filter(or_(*search_filters))

    students = query.order_by(StudentProfile.full_name.asc()).all()
    return [student_to_dict(student) for student in students]


def drive_to_dict(drive):
    return {
        "id": drive.id,
        "company_id": drive.company_id,
        "company_name": drive.company.company_name if drive.company else None,
        "job_title": drive.job_title,
        "job_description": drive.job_description,
        "location": drive.location,
        "salary": drive.salary,
        "skills_required": drive.skills_required,
        "employment_type": drive.employment_type,
        "min_cgpa": drive.min_cgpa,
        "eligible_branches": drive.eligible_branches,
        "eligible_year": drive.eligible_year,
        "application_deadline": drive.application_deadline,
        "drive_date": drive.drive_date,
        "status": drive.status,
        "rejection_reason": drive.rejection_reason,
        "applications_count": len(drive.applications),
        "created_at": drive.created_at,
        "updated_at": drive.updated_at,
    }


def interview_to_dict(interview):
    return {
        "id": interview.id,
        "application_id": interview.application_id,
        "scheduled_at": interview.scheduled_at,
        "mode": interview.mode,
        "venue_or_link": interview.venue_or_link,
        "round_name": interview.round_name,
        "status": interview.status,
        "feedback": interview.feedback,
        "created_at": interview.created_at,
        "updated_at": interview.updated_at,
    }


def status_history_to_dict(history):
    changed_by = history.changed_by_user

    return {
        "id": history.id,
        "old_status": history.old_status,
        "new_status": history.new_status,
        "note": history.note,
        "changed_at": history.changed_at,
        "changed_by_email": changed_by.email if changed_by else None,
        "changed_by_role": changed_by.role if changed_by else None,
    }


def placement_to_dict(placement):
    return {
        "id": placement.id,
        "application_id": placement.application_id,
        "position": placement.position,
        "salary": placement.salary,
        "joining_date": placement.joining_date,
        "status": placement.status,
        "placed_at": placement.placed_at,
        "created_at": placement.created_at,
        "updated_at": placement.updated_at,
    }


def application_to_dict(application, include_details=False):
    student = application.student
    drive = application.drive
    company = drive.company if drive else None

    data = {
        "id": application.id,
        "student_id": application.student_id,
        "student_name": student.full_name if student else None,
        "student_roll_number": student.roll_number if student else None,
        "student_email": student.user.email if student and student.user else None,
        "student_branch": student.branch if student else None,
        "student_year": student.year if student else None,
        "student_cgpa": student.cgpa if student else None,
        "student_phone": student.phone if student else None,
        "student_resume_url": student.resume_url if student else None,
        "student_skills": student.skills if student else None,
        "student_experience": student.experience if student else None,
        "drive_id": application.drive_id,
        "job_title": drive.job_title if drive else None,
        "company_id": company.id if company else None,
        "company_name": company.company_name if company else None,
        "status": application.status,
        "remarks": application.remarks,
        "application_date": application.application_date,
        "created_at": application.created_at,
        "updated_at": application.updated_at,
    }

    if include_details:
        data["student"] = student_to_dict(student) if student else None
        data["company"] = company_to_dict(company) if company else None
        data["drive"] = drive_to_dict(drive) if drive else None
        data["interviews"] = [
            interview_to_dict(interview)
            for interview in application.interviews
        ]
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


@admin_bp.route("/api/admin/dashboard", methods=["GET"])
@admin_bp.route("/admin/dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():
    _, error = require_admin_user()

    if error:
        return error

    active_approved_companies = (
        CompanyProfile.query
        .join(User)
        .filter(
            CompanyProfile.approval_status == "approved",
            User.is_active.is_(True),
            User.is_blacklisted.is_(False),
        )
        .count()
    )
    blacklisted_companies = (
        CompanyProfile.query
        .join(User)
        .filter(User.is_blacklisted.is_(True))
        .count()
    )

    return jsonify({
        "total_students": StudentProfile.query.count(),
        "total_companies": CompanyProfile.query.count(),
        "approved_companies": CompanyProfile.query.filter_by(
            approval_status="approved"
        ).count(),
        "active_approved_companies": active_approved_companies,
        "blacklisted_companies": blacklisted_companies,
        "pending_companies": CompanyProfile.query.filter_by(
            approval_status="pending"
        ).count(),
        "rejected_companies": CompanyProfile.query.filter_by(
            approval_status="rejected"
        ).count(),
        "total_drives": PlacementDrive.query.count(),
        "approved_drives": PlacementDrive.query.filter_by(status="approved").count(),
        "pending_drives": PlacementDrive.query.filter_by(status="pending").count(),
        "rejected_drives": PlacementDrive.query.filter_by(status="rejected").count(),
        "closed_drives": PlacementDrive.query.filter_by(status="closed").count(),
        "total_applications": Application.query.count(),
        "active_users": User.query.filter_by(is_active=True).count(),
        "blacklisted_users": User.query.filter_by(is_blacklisted=True).count(),
    }), 200


@admin_bp.route("/api/admin/users", methods=["GET"])
@admin_bp.route("/admin/users", methods=["GET"])
@jwt_required()
def get_all_users():
    _, error = require_admin_user()

    if error:
        return error

    users = User.query.all()

    return jsonify([
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "is_blacklisted": user.is_blacklisted,
            "created_at": user.created_at,
        }
        for user in users
    ]), 200


@admin_bp.route("/api/admin/companies", methods=["GET"])
@admin_bp.route("/admin/companies", methods=["GET"])
@jwt_required()
@cache.cached(timeout=300, query_string=True)
def get_companies():
    _, error = require_admin_user()

    if error:
        return error

    search = request.args.get("search", "").strip()
    search_by = request.args.get("search_by", "all").strip()
    status = request.args.get("status", "").strip()

    error = validate_filter(search_by, COMPANY_SEARCH_FIELDS, "search_by")
    if error:
        return error

    error = validate_filter(status, COMPANY_STATUSES, "status")
    if error:
        return error

    query = CompanyProfile.query.join(User)

    if search:
        pattern = f"%{search}%"
        search_options = {
            "name": [CompanyProfile.company_name.ilike(pattern)],
            "industry": [CompanyProfile.industry.ilike(pattern)],
            "location": [CompanyProfile.location.ilike(pattern)],
            "email": [User.email.ilike(pattern)],
            "all": [
                CompanyProfile.company_name.ilike(pattern),
                CompanyProfile.industry.ilike(pattern),
                CompanyProfile.location.ilike(pattern),
                User.email.ilike(pattern),
            ],
        }
        query = query.filter(or_(*search_options.get(search_by, search_options["all"])))

    if status:
        query = query.filter(CompanyProfile.approval_status == status)

    companies = query.order_by(CompanyProfile.created_at.desc()).all()

    return jsonify([company_to_dict(company) for company in companies]), 200


@admin_bp.route("/api/admin/companies/<int:company_id>/approve", methods=["PATCH"])
@admin_bp.route("/admin/companies/<int:company_id>/approve", methods=["PATCH"])
@jwt_required()
def approve_company(company_id):
    _, error = require_admin_user()

    if error:
        return error

    company = db.session.get(CompanyProfile, company_id)

    if not company:
        return jsonify({"message": "Company not found"}), 404

    if company.user and company.user.is_blacklisted:
        return validation_error("Blacklisted companies cannot be approved")

    company.approval_status = "approved"
    company.rejection_reason = None
    company.user.is_active = True
    db.session.commit()
    cache.clear()
    send_company_approval_email(company)

    return jsonify({
        "message": "Company approved successfully",
        "company": company_to_dict(company),
    }), 200


@admin_bp.route("/api/admin/companies/<int:company_id>/reject", methods=["PATCH"])
@admin_bp.route("/admin/companies/<int:company_id>/reject", methods=["PATCH"])
@jwt_required()
def reject_company(company_id):
    _, error = require_admin_user()

    if error:
        return error

    company = db.session.get(CompanyProfile, company_id)

    if not company:
        return jsonify({"message": "Company not found"}), 404

    data = request.get_json(silent=True) or {}
    reason, error = require_reason(data)
    if error:
        return error

    company.approval_status = "rejected"
    company.rejection_reason = reason
    company.user.is_active = False
    db.session.commit()
    cache.clear()
    send_company_rejection_email(company)

    return jsonify({
        "message": "Company rejected successfully",
        "company": company_to_dict(company),
    }), 200


@admin_bp.route("/api/admin/students", methods=["GET"])
@admin_bp.route("/admin/students", methods=["GET"])
@jwt_required()
def get_students():
    _, error = require_admin_user()

    if error:
        return error

    search = request.args.get("search", "").strip()
    return jsonify(get_cached_students(search.lower())), 200


@admin_bp.route("/api/admin/drives", methods=["GET"])
@admin_bp.route("/admin/drives", methods=["GET"])
@jwt_required()
def get_drives():
    _, error = require_admin_user()

    if error:
        return error

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    error = validate_filter(status, DRIVE_STATUSES, "status")
    if error:
        return error

    query = PlacementDrive.query.join(CompanyProfile)

    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(
            PlacementDrive.job_title.ilike(pattern),
            PlacementDrive.location.ilike(pattern),
            PlacementDrive.skills_required.ilike(pattern),
            CompanyProfile.company_name.ilike(pattern),
            CompanyProfile.industry.ilike(pattern),
        ))

    if status:
        query = query.filter(PlacementDrive.status == status)

    drives = query.order_by(PlacementDrive.created_at.desc()).all()

    return jsonify([drive_to_dict(drive) for drive in drives]), 200


@admin_bp.route("/api/admin/drives/<int:drive_id>/approve", methods=["PATCH"])
@admin_bp.route("/admin/drives/<int:drive_id>/approve", methods=["PATCH"])
@jwt_required()
def approve_drive(drive_id):
    _, error = require_admin_user()

    if error:
        return error

    drive = db.session.get(PlacementDrive, drive_id)

    if not drive:
        return jsonify({"message": "Placement drive not found"}), 404

    if drive.status != "pending":
        return validation_error("Only pending drives can be approved")

    company = drive.company
    if not company or company.approval_status != "approved":
        return validation_error("Drive company must be approved before the drive can be approved")

    if not company.user or not company.user.is_active:
        return validation_error("Drive company account must be active before the drive can be approved")

    if company.user.is_blacklisted:
        return validation_error("Drive company account must not be blacklisted")

    drive.status = "approved"
    drive.rejection_reason = None
    db.session.commit()
    cache.clear()

    return jsonify({
        "message": "Placement drive approved successfully",
        "drive": drive_to_dict(drive),
    }), 200


@admin_bp.route("/api/admin/drives/<int:drive_id>/reject", methods=["PATCH"])
@admin_bp.route("/admin/drives/<int:drive_id>/reject", methods=["PATCH"])
@jwt_required()
def reject_drive(drive_id):
    _, error = require_admin_user()

    if error:
        return error

    drive = db.session.get(PlacementDrive, drive_id)

    if not drive:
        return jsonify({"message": "Placement drive not found"}), 404

    data = request.get_json(silent=True) or {}
    reason, error = require_reason(data)
    if error:
        return error

    if drive.status != "pending":
        return validation_error("Only pending drives can be rejected")

    drive.status = "rejected"
    drive.rejection_reason = reason
    db.session.commit()
    cache.clear()

    return jsonify({
        "message": "Placement drive rejected successfully",
        "drive": drive_to_dict(drive),
    }), 200


@admin_bp.route("/api/admin/drives/<int:drive_id>/close", methods=["PATCH"])
@admin_bp.route("/admin/drives/<int:drive_id>/close", methods=["PATCH"])
@jwt_required()
def close_drive(drive_id):
    _, error = require_admin_user()

    if error:
        return error

    drive = db.session.get(PlacementDrive, drive_id)

    if not drive:
        return jsonify({"message": "Placement drive not found"}), 404

    if drive.status != "approved":
        return validation_error("Only approved drives can be closed")

    drive.status = "closed"
    db.session.commit()
    cache.clear()

    return jsonify({
        "message": "Placement drive closed successfully",
        "drive": drive_to_dict(drive),
    }), 200


@admin_bp.route("/api/admin/applications", methods=["GET"])
@admin_bp.route("/admin/applications", methods=["GET"])
@jwt_required()
def get_applications():
    _, error = require_admin_user()

    if error:
        return error

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    error = validate_filter(status, APPLICATION_STATUSES, "status")
    if error:
        return error

    query = (
        Application.query
        .join(Application.student)
        .join(Application.drive)
        .join(PlacementDrive.company)
    )

    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(
            StudentProfile.full_name.ilike(pattern),
            StudentProfile.roll_number.ilike(pattern),
            PlacementDrive.job_title.ilike(pattern),
            CompanyProfile.company_name.ilike(pattern),
        ))

    if status:
        query = query.filter(Application.status == status)

    applications = query.order_by(Application.application_date.desc()).all()

    return jsonify([
        application_to_dict(application)
        for application in applications
    ]), 200


@admin_bp.route("/api/admin/applications/<int:application_id>", methods=["GET"])
@admin_bp.route("/admin/applications/<int:application_id>", methods=["GET"])
@jwt_required()
def get_application(application_id):
    _, error = require_admin_user()

    if error:
        return error

    application = db.session.get(Application, application_id)

    if not application:
        return jsonify({"message": "Application not found"}), 404

    return jsonify(application_to_dict(application, include_details=True)), 200


@admin_bp.route("/api/admin/users/<int:user_id>/deactivate", methods=["PATCH"])
@admin_bp.route("/admin/users/<int:user_id>/deactivate", methods=["PATCH"])
@jwt_required()
def deactivate_user(user_id):
    admin_user, error = require_admin_user()

    if error:
        return error

    if admin_user.id == user_id:
        return jsonify({"message": "Admin cannot deactivate their own account"}), 400

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.role == "admin":
        return validation_error("Admin accounts cannot be managed from this dashboard")

    user.is_active = False
    db.session.commit()
    cache.clear()

    return jsonify({"message": "User deactivated successfully"}), 200


@admin_bp.route("/api/admin/users/<int:user_id>/activate", methods=["PATCH"])
@admin_bp.route("/admin/users/<int:user_id>/activate", methods=["PATCH"])
@jwt_required()
def activate_user(user_id):
    _, error = require_admin_user()

    if error:
        return error

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.role == "admin":
        return validation_error("Admin accounts cannot be managed from this dashboard")

    if user.is_blacklisted:
        return validation_error("Blacklisted users must be unblacklisted before activation")

    user.is_active = True
    db.session.commit()
    cache.clear()

    return jsonify({"message": "User activated successfully"}), 200


@admin_bp.route("/api/admin/users/<int:user_id>/blacklist", methods=["PATCH"])
@admin_bp.route("/admin/users/<int:user_id>/blacklist", methods=["PATCH"])
@jwt_required()
def blacklist_user(user_id):
    admin_user, error = require_admin_user()

    if error:
        return error

    if admin_user.id == user_id:
        return jsonify({"message": "Admin cannot blacklist their own account"}), 400

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.role == "admin":
        return validation_error("Admin accounts cannot be managed from this dashboard")

    user.is_blacklisted = True
    user.is_active = False
    db.session.commit()
    cache.clear()

    return jsonify({"message": "User blacklisted successfully"}), 200


@admin_bp.route("/api/admin/users/<int:user_id>/unblacklist", methods=["PATCH"])
@admin_bp.route("/admin/users/<int:user_id>/unblacklist", methods=["PATCH"])
@jwt_required()
def unblacklist_user(user_id):
    _, error = require_admin_user()

    if error:
        return error

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.role == "admin":
        return validation_error("Admin accounts cannot be managed from this dashboard")

    user.is_blacklisted = False
    db.session.commit()
    cache.clear()

    return jsonify({"message": "User removed from blacklist successfully"}), 200
