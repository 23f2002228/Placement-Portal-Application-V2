from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
import re
from models import CompanyProfile, StudentProfile, User, db


auth_bp = Blueprint("auth", __name__)
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

@auth_bp.route("/api/register", methods=["POST"])
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Request body must be a JSON object"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password")
    role = data.get("role")

    if not email or not password or not role:
        return jsonify({"message": "email, password and role are required"}), 400

    if not re.match(EMAIL_PATTERN, email):
        return jsonify({"message": "Invalid email format"}), 400

    if role not in ["student", "company"]:
        return jsonify({"message": "role must be student or company"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "email already exists"}), 409

    new_user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
    )

    if role == "student":
        required_fields = [
            "full_name",
            "roll_number",
            "degree",
            "branch",
            "year",
            "graduation_year",
            "cgpa",
        ]
    else:
        required_fields = [
            "company_name",
            "industry",
            "location",
            "hr_name",
            "hr_contact",
        ]

    missing_fields = [
        field for field in required_fields if data.get(field) in (None, "")
    ]

    if missing_fields:
        return jsonify({
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400

    try:
        db.session.add(new_user)
        db.session.flush()

        if role == "student":
            profile = StudentProfile(
                user_id=new_user.id,
                full_name=data["full_name"].strip(),
                roll_number=data["roll_number"].strip(),
                degree=data["degree"].strip(),
                branch=data["branch"].strip(),
                year=data["year"],
                graduation_year=data["graduation_year"],
                cgpa=data["cgpa"],
                phone=data.get("phone"),
                skills=data.get("skills"),
            )
        else:
            profile = CompanyProfile(
                user_id=new_user.id,
                company_name=data["company_name"].strip(),
                industry=data["industry"].strip(),
                location=data["location"].strip(),
                hr_name=data["hr_name"].strip(),
                hr_contact=data["hr_contact"].strip(),
                website=data.get("website"),
                description=data.get("description"),
                approval_status="pending",
            )

        db.session.add(profile)
        db.session.commit()
    except (IntegrityError, ValueError, TypeError):
        db.session.rollback()
        return jsonify({
            "message": "Registration data is invalid or already exists"
        }), 400

    return jsonify({
        "message": "User registered successfully",
        "role": role,
    }), 201


def authenticate_user(email, password, required_role=None):
    user = User.query.filter_by(email=email).first()

    if (
        not user
        or not check_password_hash(user.password_hash, password)
        or (required_role and user.role != required_role)
    ):
        return None, (jsonify({"message": "Invalid email or password"}), 401)

    if not user.is_active or user.is_blacklisted:
        return None, (jsonify({"message": "This account is not allowed to log in"}), 403)

    if user.role == "company":
        company = CompanyProfile.query.filter_by(user_id=user.id).first()

        if not company:
            return None, (jsonify({"message": "Company profile is incomplete"}), 403)

        if company.approval_status != "approved":
            return None, (
                jsonify({
                    "message": "Company approval is pending",
                    "approval_status": company.approval_status,
                }),
                403,
            )

    return user, None


def login_response(user, message="Login successful"):
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
    )

    return jsonify({
        "message": message,
        "data": {
            "email": user.email,
            "role": user.role,
            "access_token": access_token,
        },
    }), 200


@auth_bp.route("/api/login", methods=["POST"])
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Request body must be a JSON object"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "email and password are required"}), 400

    user, error = authenticate_user(email, password)

    if error:
        return error

    if user.role == "admin":
        return jsonify({"message": "Invalid email or password"}), 401

    return login_response(user)


@auth_bp.route("/api/admin/login", methods=["POST"])
@auth_bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Request body must be a JSON object"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "email and password are required"}), 400

    user, error = authenticate_user(email, password, required_role="admin")

    if error:
        return error

    return login_response(user, message="Admin login successful")


@auth_bp.route("/api/profile", methods=["GET"])
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    current_user_id = int(get_jwt_identity())
    user = db.session.get(User, current_user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.is_active or user.is_blacklisted:
        return jsonify({"message": "This account is not active"}), 403

    if user.role == "company":
        company = CompanyProfile.query.filter_by(user_id=user.id).first()

        if not company or company.approval_status != "approved":
            return jsonify({"message": "Company approval is required"}), 403

    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role,
    }), 200
