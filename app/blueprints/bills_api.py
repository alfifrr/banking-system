from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal
from datetime import datetime
from app.models.account import Account
from app.models.transaction_category import TransactionCategory
from app.models.bill import Bill
from app.models import db

bills_api = Blueprint("bills_api", __name__)


@bills_api.route("/bills", methods=["GET", "POST"])
@jwt_required()
def bill():
    current_user_id = get_jwt_identity()

    if request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        data = request.get_json()
        required_fields = [
            "biller_name",
            "due_date",
            "amount",
            "account_id",
            "category_id",
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        try:
            biller_name = data["biller_name"].strip()
            if not biller_name:
                return jsonify({"error": "Biller name cannot be empty"}), 400

            account = Account.query.get(data["account_id"])
            if not account:
                return jsonify({"error": "Account not found"}), 404
            if str(account.user_id) != current_user_id:
                return jsonify({"error": "Unauthorized access to account"}), 403

            amount = Decimal(str(data["amount"]))
            if amount <= 0:
                return jsonify({"error": "Amount must be positive"}), 400

            # check if said acc has insufficient balance
            if account.balance < amount:
                return (
                    jsonify(
                        {
                            "error": "Insufficient funds",
                            "details": {
                                "account_number": account.account_number,
                                "current_balance": float(account.balance),
                                "required_amount": float(amount),
                            },
                        }
                    ),
                    400,
                )

            try:
                date_str = data["due_date"]
                # Convert string to date and combine with midnight time
                due_date = datetime.strptime(date_str, "%Y-%m-%d").replace(
                    hour=0, minute=0, second=0
                )

                if due_date < datetime.now():
                    return jsonify({"error": "Due date cannot be in the past"}), 400

            except ValueError:
                return (
                    jsonify(
                        {
                            "error": "Invalid date format. Use YYYY-MM-DD format, example: 2025-04-15"
                        }
                    ),
                    400,
                )

            category = TransactionCategory.query.get(data["category_id"])
            if not category:
                return jsonify({"error": "Transaction category not found"}), 404

            bill = Bill(
                biller_name=biller_name,
                due_date=due_date,
                amount=amount,
                user_id=current_user_id,
                account_id=account.id,
                category_id=category.id,
                status="pending",
            )

            db.session.add(bill)
            db.session.commit()

            return jsonify(bill.to_dict()), 201

        except ValueError as e:
            return jsonify({"error": "Invalid amount format"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # GET
    query = Bill.query.filter_by(user_id=current_user_id)

    # sort from the nearest due
    bills = query.order_by(Bill.due_date.asc()).all()

    return jsonify([bill.to_dict() for bill in bills]), 200


@bills_api.route("/bills/<int:bill_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def manage_bill(bill_id):
    current_user_id = get_jwt_identity()
    bill = Bill.query.get(bill_id)
    if not bill:
        return jsonify({"error": "Bill ID not found"}), 404

    if str(bill.user_id) != current_user_id:
        return jsonify({"error": "Unauthorized access to bill"}), 403

    if request.method == "DELETE":
        if bill.status == "paid":
            return jsonify({"error": "Cannot delete a paid bill"}), 400

        try:
            db.session.delete(bill)
            db.session.commit()
            return jsonify({"message": "Bill deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    if request.method == "PUT":
        if bill.status == "paid":
            return jsonify(
                {
                    "error": "Cannot update a paid bill",
                    "details": {
                        "bill_id": bill.id,
                        "biller_name": bill.biller_name,
                        "status": bill.status,
                        "paid_amount": float(bill.amount),
                    },
                }
            )

        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        data = request.get_json()

        try:
            if "biller_name" in data:
                biller_name = data["biller_name"].strip()
                if not biller_name:
                    return jsonify({"error": "Biller name cannot be empty"}), 400
                bill.biller_name = biller_name

            if "amount" in data:
                amount = Decimal(str(data["amount"]))
                if amount <= 0:
                    return jsonify({"error": "Amount must be positive"}), 400

                # check acc balance if the amount has been raised
                if amount > bill.amount:
                    if bill.account.balance < amount:
                        return (
                            jsonify(
                                {
                                    "error": "Insufficient funds",
                                    "details": {
                                        "account_number": bill.account.account_number,
                                        "current_balance": float(bill.account.balance),
                                        "required_amount": float(amount),
                                    },
                                }
                            ),
                            400,
                        )
                bill.amount = amount

            if "due_date" in data:
                try:
                    date_str = data["due_date"]
                    due_date = datetime.strptime(date_str, "%Y-%m-%d").replace(
                        hour=0, minute=0, second=0
                    )
                    if due_date < datetime.now():
                        return jsonify({"error": "Due date cannot be in the past"}), 400
                    bill.due_date = due_date
                except ValueError:
                    return (
                        jsonify(
                            {
                                "error": "Invalid date format. Use YYYY-MM-DD format, example: 2025-04-15"
                            }
                        ),
                        400,
                    )

            if "category_id" in data:
                category = TransactionCategory.query.get(data["category_id"])
                if not category:
                    return jsonify({"error": "Transaction category not found"}), 404
                bill.category_id = category.id

            if "account_id" in data:
                account = Account.query.get(data["account_id"])
                if not account:
                    return jsonify({"error": "Account not found"}), 404
                if str(account.user_id) != current_user_id:
                    return jsonify({"error": "Unauthorized access to account"}), 403
                if account.balance < bill.amount:
                    return (
                        jsonify(
                            {
                                "error": "Insufficient funds in new account",
                                "details": {
                                    "account_number": account.account_number,
                                    "current_balance": float(account.balance),
                                    "required_amount": float(bill.amount),
                                },
                            }
                        ),
                        400,
                    )
                bill.account_id = account.id

            db.session.commit()
            return jsonify(bill.to_dict()), 200

        except ValueError:
            return jsonify({"error": "Invalid amount format"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # GET
    return jsonify(bill.to_dict()), 200


@bills_api.route("/bills/<int:bill_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_bill(bill_id):
    current_user_id = get_jwt_identity()
    bill = Bill.query.get(bill_id)
    if not bill:
        return jsonify({"error": "Bill ID not found"}), 404

    if str(bill.user_id) != current_user_id:
        return jsonify({"error": "Unauthorized access to bill"}), 403

    if bill.status == "paid":
        return (
            jsonify(
                {
                    "error": "Cannot cancel a paid bill",
                    "details": {
                        "bill_id": bill.id,
                        "biller_name": bill.biller_name,
                        "status": bill.status,
                        "paid_amount": float(bill.amount),
                    },
                }
            ),
            400,
        )

    if bill.status == "cancelled":
        return (
            jsonify(
                {
                    "error": "Bill is already cancelled",
                    "details": {
                        "bill_id": bill.id,
                        "biller_name": bill.biller_name,
                        "status": bill.status,
                    },
                }
            ),
            400,
        )

    try:
        bill.status = "cancelled"
        db.session.commit()

        return (
            jsonify({"message": "Bill cancelled successfully", "bill": bill.to_dict()}),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
