from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import Notification, User, db


notifications_bp = Blueprint("notifications", __name__)


def format_datetime(value):
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M")


def notification_to_dict(notification):
    return {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "is_read": notification.is_read,
        "created_at": format_datetime(notification.created_at),
    }


def require_current_user():
    current_user_id = int(get_jwt_identity())
    current_user = db.session.get(User, current_user_id)

    if (
        not current_user
        or not current_user.is_active
        or current_user.is_blacklisted
    ):
        return None, (
            jsonify({"message": "Active user access required"}),
            403,
        )

    return current_user, None


@notifications_bp.route("/api/notifications", methods=["GET"])
@notifications_bp.route("/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    current_user, error = require_current_user()

    if error:
        return error

    notifications = (
        Notification.query
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(20)
        .all()
    )
    unread_count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False,
    ).count()

    return jsonify({
        "notifications": [
            notification_to_dict(notification)
            for notification in notifications
        ],
        "unread_count": unread_count,
    }), 200


@notifications_bp.route("/api/notifications/<int:notification_id>/read", methods=["PATCH"])
@notifications_bp.route("/notifications/<int:notification_id>/read", methods=["PATCH"])
@jwt_required()
def mark_notification_read(notification_id):
    current_user, error = require_current_user()

    if error:
        return error

    notification = db.session.get(Notification, notification_id)

    if not notification or notification.user_id != current_user.id:
        return jsonify({"message": "Notification not found"}), 404

    notification.is_read = True
    db.session.commit()

    return jsonify({
        "message": "Notification marked as read",
        "notification": notification_to_dict(notification),
    }), 200


@notifications_bp.route("/api/notifications/read-all", methods=["PATCH"])
@notifications_bp.route("/notifications/read-all", methods=["PATCH"])
@jwt_required()
def mark_all_notifications_read():
    current_user, error = require_current_user()

    if error:
        return error

    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False,
    ).update({"is_read": True})
    db.session.commit()

    return jsonify({"message": "Notifications marked as read"}), 200
