from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from app.models.user import User
from datetime import timedelta

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username or not password:
        return jsonify({"error": "Missing username or password field"}), 400

    user = User.query.filter_by(username=username).one_or_none()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(minutes=15),
        additional_claims={'type': 'access'})
    refresh_token = create_refresh_token(
        identity=str(user.id),
        expires_delta=timedelta(days=30),
        additional_claims={'type': 'refresh'})
    return jsonify(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type='bearer'), 200


@auth.route('/refresh-token', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    jwt_claims = get_jwt()

    if jwt_claims['type'] != 'refresh':
        return jsonify({'error': 'Invalid token type'}), 401

    current_user_id = get_jwt_identity()

    access_token = create_access_token(
        identity=current_user_id,
        expires_delta=timedelta(minutes=15),
        additional_claims={'type': 'access'}
    )

    return jsonify(
        access_token=access_token,
        token_type='bearer'), 200
