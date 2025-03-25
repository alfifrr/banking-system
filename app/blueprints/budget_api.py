from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.budget import Budget
from app.models.transaction_category import TransactionCategory
from datetime import datetime, timedelta
from decimal import Decimal

budget_api = Blueprint("budget_api", __name__)


@budget_api.route("/budgets", methods=["POST"])
@jwt_required()
def create_budget():
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400

    data = request.get_json()
    required_fields = ["name", "amount", "category_id", "duration_minutes"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        # name should not empty
        name = data["name"].strip()
        if not name:
            return jsonify({"error": "Budget name cannot be empty"}), 400

        # at least 1 min
        try:
            duration = int(data["duration_minutes"])
            if duration < 1:
                return jsonify({"error": "Duration must be at least 1 minute"}), 400
        except ValueError:
            return jsonify({"error": "Duration must be a valid number"}), 400

        current_user_id = get_jwt_identity()
        amount = Decimal(str(data["amount"]))

        if amount <= 0:
            return jsonify({"error": "Amount must be positive"}), 400

        # check category exists
        category = TransactionCategory.query.get(data["category_id"])
        if not category:
            return jsonify({"error": "Category not found"}), 404

        # Calculate end date
        end_date = datetime.now() + timedelta(minutes=duration)

        budget = Budget(
            name=name,
            amount=amount,
            remaining_amount=amount,
            end_date=end_date,
            user_id=current_user_id,
            category_id=category.id,
        )

        db.session.add(budget)
        db.session.commit()

        return jsonify(budget.to_dict()), 201

    except ValueError as e:
        return jsonify({"error": "Invalid amount format"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
