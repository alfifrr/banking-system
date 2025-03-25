# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from app.models import db
# from app.models.transaction_category import TransactionCategory
# from app.models.budget import Budget
# from decimal import Decimal
# from datetime import datetime
# from app.models.account import Account
# from app.models.bill import Bill

# budget_api = Blueprint("budget_api", __name__)


# @budget_api.route("/budgets", methods=["POST"])
# @jwt_required()
# def create_budget():
#     if not request.is_json:
#         return jsonify({"error": "Missing JSON in request"}), 400

#     data = request.get_json()
#     required_fields = ["name", "amount", "category_id", "start_date", "end_date"]
#     for field in required_fields:
#         if field not in data:
#             return jsonify({"error": f"Missing required field: {field}"}), 400

#     try:
#         current_user_id = get_jwt_identity()

#         category = TransactionCategory.query.get_or_404(data["category_id"])

#         budget = Budget(
#             name=data["name"],
#             amount=Decimal(str(data["amount"])),
#             start_date=datetime.fromisoformat(data["start_date"]),
#             end_date=datetime.fromisoformat(data["end_date"]),
#             user_id=current_user_id,
#             category_id=category.id,
#         )

#         db.session.add(budget)
#         db.session.commit()

#         return jsonify(budget.to_dict()), 201

#     except ValueError as e:
#         return jsonify({"error": str(e)}), 400
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500


# @budget_api.route("/budgets", methods=["GET"])
# @jwt_required()
# def get_budgets():
#     current_user_id = get_jwt_identity()
#     budgets = Budget.query.filter_by(user_id=current_user_id).all()
#     return jsonify([budget.to_dict() for budget in budgets]), 200


# @budget_api.route("/budgets/<int:budget_id>", methods=["PUT"])
# @jwt_required()
# def update_budget(budget_id):
#     current_user_id = get_jwt_identity()
#     budget = Budget.query.get_or_404(budget_id)

#     # Verify ownership
#     if str(budget.user_id) != current_user_id:
#         return jsonify({"error": "Unauthorized access to budget"}), 403

#     if not request.is_json:
#         return jsonify({"error": "Missing JSON in request"}), 400

#     data = request.get_json()

#     try:
#         if "name" in data:
#             budget.name = data["name"]
#         if "amount" in data:
#             budget.amount = Decimal(str(data["amount"]))
#         if "start_date" in data:
#             budget.start_date = datetime.fromisoformat(data["start_date"])
#         if "end_date" in data:
#             budget.end_date = datetime.fromisoformat(data["end_date"])
#         if "category_id" in data:
#             category = TransactionCategory.query.get_or_404(data["category_id"])
#             budget.category_id = category.id

#         db.session.commit()
#         return jsonify(budget.to_dict()), 200

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500


# @budget_api.route("/transactions/categories", methods=["GET"])
# @jwt_required()
# def get_categories():
#     categories = TransactionCategory.query.all()
#     return jsonify([category.to_dict() for category in categories]), 200


# # Bill payment endpoints
# @budget_api.route("/bills", methods=["POST"])
# @jwt_required()
# def create_bill():
#     if not request.is_json:
#         return jsonify({"error": "Missing JSON in request"}), 400

#     data = request.get_json()
#     required_fields = ["biller_name", "amount", "due_date", "account_id", "category_id"]
#     for field in required_fields:
#         if field not in data:
#             return jsonify({"error": f"Missing required field: {field}"}), 400

#     try:
#         current_user_id = get_jwt_identity()

#         # Verify account ownership
#         account = Account.query.get_or_404(data["account_id"])
#         if str(account.user_id) != current_user_id:
#             return jsonify({"error": "Unauthorized access to account"}), 403

#         bill = Bill(
#             biller_name=data["biller_name"],
#             amount=Decimal(str(data["amount"])),
#             due_date=datetime.fromisoformat(data["due_date"]),
#             account_id=data["account_id"],
#             category_id=data["category_id"],
#             user_id=current_user_id,
#         )

#         db.session.add(bill)
#         db.session.commit()

#         return jsonify(bill.to_dict()), 201

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500
