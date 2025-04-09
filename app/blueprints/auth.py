from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app.blueprints.api import bcrypt

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    try:
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid username or password"}), 401
    except ValueError as e:
        return jsonify({'error': str(e)}), 500

    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)
