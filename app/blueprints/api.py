from flask import Blueprint, request, jsonify
from app.models.user import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.account import Account
from password_strength import PasswordPolicy, tests
from app.models.transaction import Transaction
from decimal import Decimal
from app.models.transaction_category import TransactionCategory

api = Blueprint("api", __name__)

policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 1 uppercase letters
    numbers=1,  # need min. 1 digits
    special=1,  # need min. 1 special characters
    # nonletters=2,  # need min. 2 non-letter characters (digits, specials, anything)
)


def strength_check(pw):
    test = policy.test(pw)
    if test:
        error_messages = []
        for failed_test in test:
            test_type = failed_test.__class__.__name__

            if test_type == "Length":
                error_messages.append("Password must be at least 8 characters")
            elif test_type == "Uppercase":
                error_messages.append(
                    "Password must contain at least 1 uppercase letter"
                )
            elif test_type == "Numbers":
                error_messages.append("Password must contain at least 1 number")
            elif test_type == "Special":
                error_messages.append(
                    "Password must contain at least 1 special character"
                )
        return error_messages
    return None


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

        # check pw str
        weak_password = strength_check(data["password"])
        if weak_password:
            return (
                jsonify({"error": "Password is too weak", "details": weak_password}),
                400,
            )

        # Check if user already exists
        if User.query.filter_by(username=data["username"]).first():
            return jsonify({"error": "Username already exists"}), 400
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already exists"}), 400

        try:
            # Create new user
            new_user = User(
                username=data["username"],
                email=data["email"],
                password_hash=generate_password_hash(data["password"]),
                first_name=data["first_name"],
                last_name=data["last_name"],
            )
            db.session.add(new_user)

            # also create default savings account
            main_account = Account(
                account_number=Account.generate_unique_account_number(),
                account_type="savings",
                user=new_user,
                is_main=True,
            )
            db.session.add(main_account)

            db.session.commit()

            # show new user and their acc info
            response_data = new_user.to_dict()
            response_data["account"] = main_account.to_dict()
            return jsonify(response_data), 201
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

            # check new pw str
            weak_password = strength_check(data["password"])
            if weak_password:
                return (
                    jsonify(
                        {"error": "Password is too weak", "details": weak_password}
                    ),
                    400,
                )

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


@api.route("/accounts", methods=["GET"])
def accounts():
    # GET
    accounts = Account.query.all()
    return jsonify([account.to_dict() for account in accounts])


@api.route("/accounts", methods=["POST"])
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


@api.route("/accounts/<int:account_id>", methods=["GET"])
def account_details(account_id):
    account = Account.query.get_or_404(account_id)
    return jsonify(account.to_dict()), 200


@api.route("/accounts/<int:account_id>", methods=["PUT", "DELETE"])
@jwt_required()
def manage_account(account_id):
    current_user_id = get_jwt_identity()
    account = Account.query.get_or_404(account_id)

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


@api.route("/transactions", methods=["GET", "POST"])
@jwt_required()
def create_transaction():
    current_user_id = get_jwt_identity()

    if request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        data = request.get_json()

        # validate fields
        required_fields = ["account_id", "amount", "transaction_type"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # prevent access to another account
        account = Account.query.get_or_404(data["account_id"])
        if str(account.user_id) != current_user_id:
            return jsonify({"error": "Unauthorized access to account"}), 403

        # transfer validation
        if data["transaction_type"] == Transaction.TRANSFER:
            if "to_account_number" not in data:
                return (
                    jsonify(
                        {
                            "error": "Destination account number is required for transfers"
                        }
                    ),
                    400,
                )

            to_account = Account.query.filter_by(
                account_number=data["to_account_number"]
            ).first()
            if not to_account:
                return jsonify({"error": "Destination account not found"}), 404

            if account.id == to_account.id:
                return jsonify({"error": "Cannot transfer to yourself"}), 400

        # require category_id for payment
        if data["transaction_type"] == Transaction.PAYMENT:
            if "category_id" not in data:
                return (
                    jsonify(
                        {
                            "error": "Transaction category (category_id) is required for payment"
                        }
                    ),
                    400,
                )

            category = TransactionCategory.query.get(data["category_id"])
            if not category:
                return jsonify({"error": "Invalid transaction category"}), 400

        try:
            amount = Decimal(str(data["amount"]))

            # prevent 0 transaction or below
            if amount <= 0:
                return jsonify({"error": "Amount must be positive"}), 400

            # check balance
            if data["transaction_type"] in [
                Transaction.WITHDRAWAL,
                Transaction.TRANSFER,
                Transaction.PAYMENT,
            ]:
                if account.balance < amount:
                    return jsonify({"error": "Insufficient funds"}), 400

            transaction = Transaction(
                amount=amount,
                transaction_type=data["transaction_type"],
                description=data.get("description", ""),
                from_account_id=account.id,
                to_account_id=(
                    to_account.id
                    if data["transaction_type"] == Transaction.TRANSFER
                    else None
                ),
                category_id=(
                    data["category_id"]
                    if data["transaction_type"] == Transaction.PAYMENT
                    else None
                ),
            )

            # handle balance updates
            if transaction.transaction_type == Transaction.DEPOSIT:
                account.balance += amount
            elif transaction.transaction_type in [
                Transaction.WITHDRAWAL,
                Transaction.PAYMENT,
            ]:
                account.balance -= amount
            elif transaction.transaction_type == Transaction.TRANSFER:
                account.balance -= amount
                to_account.balance += amount
            else:
                return jsonify({"error": "Invalid transaction type"}), 400

            db.session.add(transaction)
            db.session.commit()

            return jsonify(transaction.to_dict()), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    # GET
    user = User.query.get(int(current_user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    # fetch all owned accs for the current logged user
    user_account_ids = [account.id for account in user.accounts]

    # filter all transactions made by current user-owned accs (both as sender and receiver)
    transactions = (
        Transaction.query.filter(
            (Transaction.from_account_id.in_(user_account_ids))
            | (Transaction.to_account_id.in_(user_account_ids))
        )
        .order_by(Transaction.created_at.desc())
        .all()
    )

    return jsonify([transaction.to_dict() for transaction in transactions]), 200


@api.route("/transactions/<int:transaction_id>", methods=["GET"])
@jwt_required()
def get_transaction_details(transaction_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_account_ids = [account.id for account in user.accounts]

    # get transaction data based on the queried id
    transaction = Transaction.query.get_or_404(transaction_id)

    # only allow viewing for currently logged in user accounts
    if (
        transaction.from_account_id not in user_account_ids
        and transaction.to_account_id not in user_account_ids
    ):
        return jsonify({"error": "Unauthorized access to transaction details"}), 403

    return jsonify(transaction.to_dict()), 200


@api.route("/transactions/categories")
def categories():
    categories = TransactionCategory.query.all()
    return jsonify([category.to_dict() for category in categories]), 200


# check db connection
@api.route("/health")
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500
