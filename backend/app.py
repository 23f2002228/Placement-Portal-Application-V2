import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash

import config
from extensions import cache
from models import User, db
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.company import company_bp
from routes.notifications import notifications_bp
from routes.student import student_bp


# Create and configure the Flask application.
app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.JWT_ACCESS_TOKEN_EXPIRES
app.config["DEBUG"] = config.DEBUG
app.config.from_mapping({
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_URL": config.REDIS_URL,
    "CACHE_DEFAULT_TIMEOUT": 300,
})

# Connect Flask extensions to the application.
CORS(app)
db.init_app(app)
cache.init_app(app)
jwt = JWTManager(app)

# Add the route groups to the application.
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(company_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(student_bp)


@app.route("/", methods=["GET"])
def test():
    return jsonify({"message": "API is working!"})


def create_default_admin():
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@placementportal.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")

    existing_admin = User.query.filter_by(email=admin_email).first()
    if existing_admin:
        return

    admin = User(
        email=admin_email,
        password_hash=generate_password_hash(admin_password),
        role="admin",
    )
    db.session.add(admin)
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_default_admin()

    app.run(debug=True)
