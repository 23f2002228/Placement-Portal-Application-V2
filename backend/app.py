from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

import config
from models import db
from routes.admin import admin_bp
from routes.auth import auth_bp


# Create and configure the Flask application.
app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.JWT_ACCESS_TOKEN_EXPIRES
app.config["DEBUG"] = config.DEBUG

# Connect Flask extensions to the application.
CORS(app)
db.init_app(app)
jwt = JWTManager(app)

# Add the route groups to the application.
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)


@app.route("/", methods=["GET"])
def test():
    return jsonify({"message": "API is working!"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
