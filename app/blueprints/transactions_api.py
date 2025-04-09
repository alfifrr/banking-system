from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from decimal import Decimal
from app.models import Transaction, Account, Bill, TransactionCategory, Budget, User, db

transactions_api = Blueprint('transactions_api', __name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=['200 per day', '50 per hour']
)


def validate_transaction_amount(amount_str):
    try:
        amount = Decimal(str(amount_str))
        if amount <= 0:
            return None, "Amount must be positive"
        return amount, None
    except (ValueError, TypeError):
        return None, "Invalid amount format"


@transactions_api.route("/transactions", methods=["GET", "POST"])
@limiter.limit('20 per minute')
@jwt_required()
def create_transaction():
    current_user_id = get_jwt_identity()

    if request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        data = request.get_json()

        # validate fields based on the transaction type
        if data.get("transaction_type") == Transaction.BILL_PAYMENT:
            required_fields = ["account_id", "transaction_type", "bill_id"]
        else:
            required_fields = ["account_id", "amount", "transaction_type"]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # prevent access to another account
        account = Account.query.get(data["account_id"])
        if not account:
            return jsonify({"error": "Account is not found"}), 404
        if str(account.user_id) != current_user_id:
            return jsonify({"error": "Unauthorized access to account"}), 403

        if data["transaction_type"] == Transaction.BILL_PAYMENT:
            if "bill_id" not in data:
                return (
                    jsonify(
                        {"error": "Bill ID (bill_id) is required for bill payments"}
                    ),
                    400,
                )

            # check bill id
            bill = Bill.query.get(data["bill_id"])
            if not bill:
                # get pending bills as helper
                pending_bills = Bill.query.filter_by(
                    user_id=current_user_id, status="pending"
                ).all()

                return (
                    jsonify(
                        {
                            "error": "Bill ID is not found",
                            "details": {
                                "available_pending_bills": [
                                    {
                                        "id": biller.id,
                                        "account_id": biller.account_id,
                                        "biller_name": biller.biller_name,
                                        "amount": float(biller.amount),
                                        "due_date": biller.due_date.isoformat(),
                                    }
                                    for biller in pending_bills
                                ]
                            },
                        }
                    ),
                    404,
                )

            # check bill ownership
            if str(bill.user_id) != current_user_id:
                # get pending bills as helper
                pending_bills = Bill.query.filter_by(
                    user_id=current_user_id, status="pending"
                ).all()

                return (
                    jsonify(
                        {
                            "error": "Unauthorized access to bill",
                            "details": {
                                "available_pending_bills": [
                                    {
                                        "id": biller.id,
                                        "account_id": biller.account_id,
                                        "biller_name": biller.biller_name,
                                        "amount": float(biller.amount),
                                        "due_date": biller.due_date.isoformat(),
                                    }
                                    for biller in pending_bills
                                ]
                            },
                        }
                    ),
                    403,
                )

            # check bill status
            if bill.status != "pending":
                return (
                    jsonify(
                        {
                            "error": "Cannot pay bill",
                            "details": {
                                "bill_id": bill.id,
                                "biller_name": bill.biller_name,
                                "status": bill.status,
                                "reason": f"Bill is already {bill.status}",
                            },
                        }
                    ),
                    400,
                )

            # check correct account for paying
            if bill.account_id != account.id:
                return (
                    jsonify(
                        {
                            "error": "Invalid account for bill payment",
                            "details": {
                                "bill_id": bill.id,
                                "required_account": bill.account.account_number,
                                "provided_account": account.account_number,
                            },
                        }
                    ),
                    400,
                )

            # check for sufficient balance
            if account.balance < bill.amount:
                return (
                    jsonify(
                        {
                            "error": "Insufficient funds",
                            "details": {
                                "account_balance": float(account.balance),
                                "bill_amount": float(bill.amount),
                            },
                        }
                    ),
                    400,
                )
            # auto. assign req. amount for bill payment
            data["amount"] = str(bill.amount)

        # transfer type validation
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

        # check if it's payment type
        if data["transaction_type"] == Transaction.PAYMENT:
            # check for category_id in req. body
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

            # check for active budget in this category
            active_budget = Budget.query.filter(
                Budget.user_id == current_user_id,
                Budget.category_id == category.id,
                Budget.start_date <= datetime.now(),
                Budget.end_date >= datetime.now(),
            ).first()

            # check if there's active budget
            if active_budget:
                # amount = Decimal(str(data["amount"]))
                amount, error = validate_transaction_amount(data["amount"])
                if error:
                    return jsonify({"error": error}), 400

                if amount > active_budget.remaining_amount:
                    return (
                        jsonify(
                            {
                                "error": "Payment exceeds remaining budget.",
                                "details": {
                                    "requested_amount": float(amount),
                                    "available_budget": float(
                                        active_budget.remaining_amount
                                    ),
                                    "category": category.name,
                                    "budget_end_date": active_budget.end_date.isoformat(),
                                },
                            }
                        ),
                        400,
                    )

        try:
            # amount = Decimal(str(data["amount"]))

            # # prevent 0 transaction or below
            # if amount <= 0:
            #     return jsonify({"error": "Amount must be positive"}), 400
            amount, error = validate_transaction_amount(data["amount"])
            if error:
                return jsonify({"error": error}), 400

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
                description=(
                    data.get("description",
                             f"Bill payment: {bill.biller_name}")
                    if data["transaction_type"] == Transaction.BILL_PAYMENT
                    else data.get("description", "")
                ),
                from_account_id=account.id,
                to_account_id=(
                    to_account.id
                    if data["transaction_type"] == Transaction.TRANSFER
                    else None
                ),
                category_id=(
                    bill.category_id
                    if data["transaction_type"] == Transaction.BILL_PAYMENT
                    else (
                        data["category_id"]
                        if data["transaction_type"] == Transaction.PAYMENT
                        else None
                    )
                ),
            )

            # handle balance updates
            if transaction.transaction_type == Transaction.BILL_PAYMENT:
                account.balance -= amount
                bill.status = "paid"
            elif transaction.transaction_type == Transaction.DEPOSIT:
                account.balance += amount
            elif transaction.transaction_type in [
                Transaction.WITHDRAWAL,
                Transaction.PAYMENT,
            ]:
                account.balance -= amount

                if (
                    transaction.transaction_type == Transaction.PAYMENT
                    and active_budget
                ):
                    active_budget.remaining_amount -= amount
            elif transaction.transaction_type == Transaction.TRANSFER:
                account.balance -= amount
                to_account.balance += amount
            else:
                return jsonify({"error": "Invalid transaction type"}), 400

            db.session.add(transaction)
            db.session.commit()

            return jsonify(transaction.to_dict()), 201
        except ValueError as e:
            db.session.rollback()
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


@transactions_api.route("/transactions/<int:transaction_id>", methods=["GET"])
@jwt_required()
def get_transaction_details(transaction_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_account_ids = [account.id for account in user.accounts]

    # get transaction data based on the queried id
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404

    # only allow viewing for currently logged in user accounts
    if (
        transaction.from_account_id not in user_account_ids
        and transaction.to_account_id not in user_account_ids
    ):
        return jsonify({"error": "Unauthorized access to transaction details"}), 403

    return jsonify(transaction.to_dict()), 200


@transactions_api.route("/transactions/categories")
def categories():
    categories = TransactionCategory.query.all()
    return jsonify([category.to_dict() for category in categories]), 200
