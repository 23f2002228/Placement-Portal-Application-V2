import os

from werkzeug.security import generate_password_hash

from app import app
from models import User, db


ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@placementportal.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


def seed_admin():
    """Create the default admin once and leave an existing admin unchanged."""
    with app.app_context():
        db.create_all()

        existing_admin = User.query.filter_by(email=ADMIN_EMAIL).first()

        if existing_admin:
            print(f"Admin already exists: {ADMIN_EMAIL}")
            return existing_admin.id

        admin = User(
            email=ADMIN_EMAIL,
            password_hash=generate_password_hash(ADMIN_PASSWORD),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()

        print(f"Admin created: {ADMIN_EMAIL}")
        return admin.id


if __name__ == "__main__":
    seed_admin()
