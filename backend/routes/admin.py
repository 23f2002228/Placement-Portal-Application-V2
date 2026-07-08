from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import User, db


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/api/admin/users", methods=["GET"])
@admin_bp.route("/admin/users", methods=["GET"])
@jwt_required()
def get_all_users():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if not current_user or current_user.role != "admin":
        return jsonify({
            "message": "Admin access required",
            "role": current_user.role if current_user else None,
        }), 403

    users = User.query.all()

    return jsonify([
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }
        for user in users
    ]), 200
