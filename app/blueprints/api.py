from flask import Blueprint, request, jsonify
from app.models.user import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Blueprint("api", __name__)


@api.route("/users", methods=["GET", "POST"])
def users():
    if request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        data = request.get_json()

        # validate fields
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


@api.route("/users/me", methods=["GET", "PUT"])
@jwt_required()
def profile():
    # fetch user id from jwt
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    if request.method == "PUT":
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        data = request.get_json()

        if "password" in data:
            # req curr pwd
            current_password = data.get("current_password")
            if not current_password:
                return jsonify(
                    {"error": "Current password is required to update password"}
                )

            # check for wrong curr password
            if not check_password_hash(user.password_hash, current_password):
                return jsonify({"error": "Current password is incorrect"}), 401

            user.password_hash = generate_password_hash(data["password"])
            data.pop("password")
            data.pop("current_password")

        # check if changed user/email already exist in db
        if "username" in data and data["username"] != user.username:
            if User.query.filter_by(username=data["username"]).first():
                return jsonify({"error": "Username already exists"}), 400
        if "email" in data and data["email"] != user.email:
            if User.query.filter_by(email=data["email"]).first():
                return jsonify({"error": "Email already exists"}), 400

        # update fields
        required_fields = ["username", "email", "first_name", "last_name"]
        for field in required_fields:
            if field in data:
                setattr(user, field, data[field])

        try:
            db.session.commit()
            return jsonify(user.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # GET
    return jsonify(user.to_dict())


@api.route("/health")
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500
