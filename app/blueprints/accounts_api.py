from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Account, User, db

accounts_api = Blueprint('accounts_api', __name__)


@accounts_api.route("/accounts", methods=["GET"])
@jwt_required()
def accounts():
    current_user_id = get_jwt_identity()
    # GET
    accounts = Account.query.filter_by(user_id=current_user_id).all()
    return jsonify([account.to_dict() for account in accounts])


@accounts_api.route("/accounts", methods=["POST"])
@jwt_required()
def create_account():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()

    account_type = data.get("account_type")
    if not account_type:
        return jsonify({"error": "Account type is required"}), 400

    if account_type not in ["savings", "checking"]:
        return (
            jsonify({"error": "Invalid account type. Must be savings or checking"}),
            400,
        )

    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        new_account = Account(
            account_number=Account.generate_unique_account_number(),
            account_type=account_type,
            user=user,
            is_main=False,
        )
        db.session.add(new_account)
        db.session.commit()

        return jsonify(new_account.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@accounts_api.route("/accounts/<int:account_id>", methods=["GET"])
@jwt_required()
def account_details(account_id):
    current_user_id = get_jwt_identity()
    account = Account.query.get(account_id)
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    if account.user_id != int(current_user_id):
        return jsonify({"error": "Unauthorized access"}), 403
    return jsonify(account.to_dict()), 200


@accounts_api.route("/accounts/<int:account_id>", methods=["PUT", "DELETE"])
@jwt_required()
def manage_account(account_id):
    current_user_id = get_jwt_identity()
    account = Account.query.get(account_id)
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    # only allows user-owned accounts
    if account.user_id != int(current_user_id):
        return jsonify({"error": "Unauthorized access"}), 403

    if request.method == "PUT":
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        data = request.get_json()

        if "account_type" in data:
            if data["account_type"] not in ["savings", "checking"]:
                return (
                    jsonify(
                        {"error": "Invalid account type. Must be savings or checking"}
                    ),
                    400,
                )
            account.account_type = data["account_type"]

        try:
            db.session.commit()
            return jsonify(account.to_dict()), 200
        except Exception as e:
            db.session.rollback()

    # DELETE
    if account.is_main:
        return jsonify({"error": "Cannot delete main account"}), 403

    try:
        db.session.delete(account)
        db.session.commit()
        return jsonify({"message": "Account deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
