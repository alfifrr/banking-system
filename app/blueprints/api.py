from flask import Blueprint, request, jsonify
from app.models.user import User, db
from werkzeug.security import generate_password_hash
from sqlalchemy import text

api = Blueprint("api", __name__)


@api.route("/users", methods=["GET", "POST"])
def users():
    if request.method == "POST":
        data = request.get_json()

        # Validate required fields
        required_fields = ["username", "email", "password", "first_name", "last_name"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Check if user already exists
        if User.query.filter_by(username=data["username"]).first():
            return jsonify({"error": "Username already exists"}), 400
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already exists"}), 400

        # Create new user
        new_user = User(
            username=data["username"],
            email=data["email"],
            password_hash=generate_password_hash(data["password"]),
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify(new_user.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # GET
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


@api.route("/health")
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500
