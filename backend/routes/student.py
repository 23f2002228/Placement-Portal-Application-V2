from datetime import date

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

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


student_bp = Blueprint("student", __name__)


def validation_error(message):
    return jsonify({"message": message}), 400


def isoformat(value):
    if value is None:
        return None
    return value.isoformat()


def require_student_user():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if (
        not current_user
        or current_user.role != "student"
        or not current_user.is_active
        or current_user.is_blacklisted
    ):
        return None, None, (
            jsonify({
                "message": "Student access required",
                "role": current_user.role if current_user else None,
            }),
            403,
        )

    student = StudentProfile.query.filter_by(user_id=current_user.id).first()

    if not student:
        return current_user, None, (
            jsonify({"message": "Student profile is incomplete"}),
            403,
        )

    return current_user, student, None


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
        "created_at": isoformat(student.created_at),
        "updated_at": isoformat(student.updated_at),
    }


def branch_list(value):
    return [
        branch.strip().lower()
        for branch in (value or "").split(",")
        if branch.strip()
    ]


def check_job_eligibility(student, job):
    if job.status != "approved":
        return False, "Only approved jobs are open for applications"

    if job.application_deadline <= utc_now():
        return False, "Application deadline is over"

    if student.cgpa < job.min_cgpa:
        return False, f"Minimum CGPA required is {job.min_cgpa}"

    if student.year != job.eligible_year:
        return False, f"Only year {job.eligible_year} students are eligible"

    allowed_branches = branch_list(job.eligible_branches)
    if "all" not in allowed_branches and student.branch.lower() not in allowed_branches:
        return False, "Your branch is not eligible for this job"

    return True, "Eligible"


def job_to_dict(job, student=None, application=None):
    company = job.company
    eligible = None
    eligibility_message = None

    if student:
        eligible, eligibility_message = check_job_eligibility(student, job)

    return {
        "id": job.id,
        "company_id": job.company_id,
        "company_name": company.company_name if company else None,
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
        "application_deadline": isoformat(job.application_deadline),
        "drive_date": isoformat(job.drive_date),
        "status": job.status,
        "already_applied": application is not None,
        "application_id": application.id if application else None,
        "application_status": application.status if application else None,
        "eligible": eligible,
        "eligibility_message": eligibility_message,
    }


def interview_to_dict(interview):
    application = interview.application
    job = application.drive if application else None
    company = job.company if job else None

    return {
        "id": interview.id,
        "application_id": interview.application_id,
        "job_title": job.job_title if job else None,
        "company_name": company.company_name if company else None,
        "scheduled_at": isoformat(interview.scheduled_at),
        "mode": interview.mode,
        "venue_or_link": interview.venue_or_link,
        "round_name": interview.round_name,
        "status": interview.status,
        "feedback": interview.feedback,
        "created_at": isoformat(interview.created_at),
        "updated_at": isoformat(interview.updated_at),
    }


def status_history_to_dict(history):
    return {
        "id": history.id,
        "old_status": history.old_status,
        "new_status": history.new_status,
        "note": history.note,
        "changed_at": isoformat(history.changed_at),
    }


def placement_to_dict(placement):
    application = placement.application
    job = application.drive if application else None
    company = job.company if job else None

    return {
        "id": placement.id,
        "application_id": placement.application_id,
        "job_title": job.job_title if job else None,
        "company_name": company.company_name if company else None,
        "position": placement.position,
        "salary": placement.salary,
        "joining_date": isoformat(placement.joining_date),
        "status": placement.status,
        "placed_at": isoformat(placement.placed_at),
        "created_at": isoformat(placement.created_at),
        "updated_at": isoformat(placement.updated_at),
    }


def application_to_dict(application, include_details=False):
    job = application.drive
    company = job.company if job else None

    data = {
        "id": application.id,
        "drive_id": application.drive_id,
        "job_title": job.job_title if job else None,
        "company_name": company.company_name if company else None,
        "location": job.location if job else None,
        "salary": job.salary if job else None,
        "status": application.status,
        "remarks": application.remarks,
        "application_date": isoformat(application.application_date),
        "created_at": isoformat(application.created_at),
        "updated_at": isoformat(application.updated_at),
    }

    if include_details:
        data["job"] = job_to_dict(job) if job else None
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


def student_application_or_404(student, application_id):
    application = db.session.get(Application, application_id)

    if not application or application.student_id != student.id:
        return None, (jsonify({"message": "Application not found"}), 404)

    return application, None


def student_placement_or_404(student, placement_id):
    placement = db.session.get(Placement, placement_id)

    if (
        not placement
        or not placement.application
        or placement.application.student_id != student.id
    ):
        return None, (jsonify({"message": "Placement not found"}), 404)

    return placement, None


def apply_student_profile_payload(student, data):
    text_fields = [
        "full_name",
        "roll_number",
        "degree",
        "branch",
        "phone",
        "resume_url",
        "skills",
        "experience",
    ]

    required_text_fields = {"full_name", "roll_number", "degree", "branch"}

    for field_name in text_fields:
        if field_name not in data:
            continue

        value = data.get(field_name)
        if field_name in required_text_fields and (value is None or str(value).strip() == ""):
            return validation_error(f"{field_name} is required")

        setattr(student, field_name, str(value).strip() if value else None)

    if "year" in data:
        try:
            year = int(data.get("year"))
        except (TypeError, ValueError):
            return validation_error("year must be a whole number")

        if year < 1 or year > 4:
            return validation_error("year must be between 1 and 4")
        student.year = year

    if "graduation_year" in data:
        try:
            student.graduation_year = int(data.get("graduation_year"))
        except (TypeError, ValueError):
            return validation_error("graduation_year must be a whole number")

    if "cgpa" in data:
        try:
            cgpa = float(data.get("cgpa"))
        except (TypeError, ValueError):
            return validation_error("cgpa must be a number")

        if cgpa < 0 or cgpa > 10:
            return validation_error("cgpa must be between 0 and 10")
        student.cgpa = cgpa

    return None


@student_bp.route("/api/student/profile", methods=["GET"])
@student_bp.route("/student/profile", methods=["GET"])
@jwt_required()
def get_student_profile():
    _, student, error = require_student_user()

    if error:
        return error

    return jsonify(student_to_dict(student)), 200


@student_bp.route("/api/student/profile", methods=["PATCH"])
@student_bp.route("/student/profile", methods=["PATCH"])
@jwt_required()
def update_student_profile():
    _, student, error = require_student_user()

    if error:
        return error

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Request body must be a JSON object"}), 400

    error = apply_student_profile_payload(student, data)
    if error:
        return error

    try:
        db.session.commit()
    except (IntegrityError, ValueError, TypeError):
        db.session.rollback()
        return validation_error("Student profile data is invalid or already exists")

    return jsonify({
        "message": "Student profile updated successfully",
        "student": student_to_dict(student),
    }), 200


@student_bp.route("/api/student/dashboard", methods=["GET"])
@student_bp.route("/student/dashboard", methods=["GET"])
@jwt_required()
def student_dashboard():
    _, student, error = require_student_user()

    if error:
        return error

    applications = Application.query.filter_by(student_id=student.id)

    return jsonify({
        "student": {
            "id": student.id,
            "full_name": student.full_name,
            "roll_number": student.roll_number,
        },
        "available_jobs": PlacementDrive.query.filter_by(status="approved").count(),
        "total_applications": applications.count(),
        "applied": applications.filter_by(status="applied").count(),
        "shortlisted": applications.filter_by(status="shortlisted").count(),
        "interview_scheduled": applications.filter_by(status="interview_scheduled").count(),
        "selected": applications.filter_by(status="selected").count(),
        "rejected": applications.filter_by(status="rejected").count(),
        "placements": (
            Placement.query
            .join(Placement.application)
            .filter(Application.student_id == student.id)
            .count()
        ),
    }), 200


@student_bp.route("/api/student/jobs", methods=["GET"])
@student_bp.route("/student/jobs", methods=["GET"])
@jwt_required()
def get_student_jobs():
    _, student, error = require_student_user()

    if error:
        return error

    search = request.args.get("search", "").strip()
    query = (
        PlacementDrive.query
        .join(PlacementDrive.company)
        .filter(PlacementDrive.status == "approved")
    )

    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(
            PlacementDrive.job_title.ilike(pattern),
            PlacementDrive.skills_required.ilike(pattern),
            CompanyProfile.company_name.ilike(pattern),
        ))

    jobs = query.order_by(PlacementDrive.application_deadline.asc()).all()
    applications = Application.query.filter_by(student_id=student.id).all()
    applications_by_drive = {
        application.drive_id: application
        for application in applications
    }

    return jsonify([
        job_to_dict(job, student, applications_by_drive.get(job.id))
        for job in jobs
    ]), 200


@student_bp.route("/api/student/jobs/<int:job_id>", methods=["GET"])
@student_bp.route("/student/jobs/<int:job_id>", methods=["GET"])
@jwt_required()
def get_student_job(job_id):
    _, student, error = require_student_user()

    if error:
        return error

    job = db.session.get(PlacementDrive, job_id)

    if not job or job.status != "approved":
        return jsonify({"message": "Job not found"}), 404

    application = Application.query.filter_by(
        student_id=student.id,
        drive_id=job.id,
    ).first()

    return jsonify(job_to_dict(job, student, application)), 200


@student_bp.route("/api/student/jobs/<int:job_id>/apply", methods=["POST"])
@student_bp.route("/student/jobs/<int:job_id>/apply", methods=["POST"])
@jwt_required()
def apply_for_job(job_id):
    current_user, student, error = require_student_user()

    if error:
        return error

    job = db.session.get(PlacementDrive, job_id)

    if not job or job.status != "approved":
        return jsonify({"message": "Job not found"}), 404

    existing_application = Application.query.filter_by(
        student_id=student.id,
        drive_id=job.id,
    ).first()

    if existing_application:
        return validation_error("You have already applied for this job")

    eligible, message = check_job_eligibility(student, job)
    if not eligible:
        return validation_error(message)

    application = Application(
        student_id=student.id,
        drive_id=job.id,
        status="applied",
    )
    db.session.add(application)
    db.session.flush()

    db.session.add(ApplicationStatusHistory(
        application=application,
        changed_by_user=current_user,
        old_status=None,
        new_status="applied",
        note="Application submitted by student",
    ))

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return validation_error("You have already applied for this job")

    return jsonify({
        "message": "Application submitted successfully",
        "application": application_to_dict(application, include_details=True),
    }), 201


@student_bp.route("/api/student/applications", methods=["GET"])
@student_bp.route("/student/applications", methods=["GET"])
@jwt_required()
def get_student_applications():
    _, student, error = require_student_user()

    if error:
        return error

    status = request.args.get("status", "").strip()
    query = Application.query.filter_by(student_id=student.id)

    if status:
        allowed_statuses = {
            "applied",
            "shortlisted",
            "interview_scheduled",
            "selected",
            "rejected",
            "withdrawn",
        }
        if status not in allowed_statuses:
            return validation_error("Invalid application status filter")
        query = query.filter_by(status=status)

    applications = query.order_by(Application.application_date.desc()).all()

    return jsonify([
        application_to_dict(application)
        for application in applications
    ]), 200


@student_bp.route("/api/student/applications/<int:application_id>", methods=["GET"])
@student_bp.route("/student/applications/<int:application_id>", methods=["GET"])
@jwt_required()
def get_student_application(application_id):
    _, student, error = require_student_user()

    if error:
        return error

    application, error = student_application_or_404(student, application_id)
    if error:
        return error

    return jsonify(application_to_dict(application, include_details=True)), 200


@student_bp.route("/api/student/interviews", methods=["GET"])
@student_bp.route("/student/interviews", methods=["GET"])
@jwt_required()
def get_student_interviews():
    _, student, error = require_student_user()

    if error:
        return error

    interviews = (
        Interview.query
        .join(Interview.application)
        .filter(Application.student_id == student.id)
        .order_by(Interview.scheduled_at.asc())
        .all()
    )

    return jsonify([
        interview_to_dict(interview)
        for interview in interviews
    ]), 200


@student_bp.route("/api/student/placements", methods=["GET"])
@student_bp.route("/student/placements", methods=["GET"])
@jwt_required()
def get_student_placements():
    _, student, error = require_student_user()

    if error:
        return error

    placements = (
        Placement.query
        .join(Placement.application)
        .filter(Application.student_id == student.id)
        .order_by(Placement.placed_at.desc())
        .all()
    )

    return jsonify([
        placement_to_dict(placement)
        for placement in placements
    ]), 200


@student_bp.route("/api/student/placements/<int:placement_id>/confirmation", methods=["GET"])
@student_bp.route("/student/placements/<int:placement_id>/confirmation", methods=["GET"])
@jwt_required()
def download_placement_confirmation(placement_id):
    _, student, error = require_student_user()

    if error:
        return error

    placement, error = student_placement_or_404(student, placement_id)
    if error:
        return error

    application = placement.application
    job = application.drive
    company = job.company
    today = date.today().isoformat()
    content = (
        "Placement Confirmation\n"
        f"Date: {today}\n\n"
        f"Student: {student.full_name}\n"
        f"Roll Number: {student.roll_number}\n"
        f"Company: {company.company_name}\n"
        f"Position: {placement.position}\n"
        f"Salary: {placement.salary}\n"
        f"Status: {placement.status}\n"
    )

    filename = f"placement-confirmation-{placement.id}.txt"
    return Response(
        content,
        mimetype="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        },
    )
