from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.budget import Budget
from app.models.transaction_category import TransactionCategory
from datetime import datetime, timedelta
from decimal import Decimal, DecimalException

budget_api = Blueprint("budget_api", __name__)


@budget_api.route("/budgets", methods=["GET", "POST"])
@jwt_required()
def budget():
    current_user_id = get_jwt_identity()

    if request.method == "POST":
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

            # check for existing active budget
            existing_budget = Budget.query.filter(
                Budget.user_id == current_user_id,
                Budget.category_id == data["category_id"],
                Budget.end_date > datetime.now(),
            ).first()
            if existing_budget:
                return (
                    jsonify(
                        {
                            "error": f"Active budget already exists for this category until {existing_budget.end_date.isoformat()}"
                        }
                    ),
                    400,
                )

            # at least 1 min
            try:
                duration = int(data["duration_minutes"])
                if duration < 1:
                    return jsonify({"error": "Duration must be at least 1 minute"}), 400
            except ValueError:
                return jsonify({"error": "Duration must be a valid number"}), 400

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

    # GET
    budgets = Budget.query.filter_by(user_id=current_user_id)

    return jsonify([budget.to_dict() for budget in budgets]), 200


@budget_api.route("/budgets/<int:budget_id>", methods=["GET", "PUT"])
@jwt_required()
def budget_detail(budget_id):
    current_user_id = get_jwt_identity()

    budget = Budget.query.get(budget_id)
    if not budget:
        return jsonify({"error": "Budget ID not found"}), 404

    # check ownership
    if str(budget.user_id) != current_user_id:
        return jsonify({"error": "Unauthorized access to budget"}), 403

    if request.method == "PUT":
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400

        data = request.get_json()
        try:
            if "name" in data:
                name = data["name"].strip()
                if not name:
                    return jsonify({"error": "Budget name cannot be empty"}), 400
                budget.name = name

            if "duration_minutes" in data:
                try:
                    duration = int(data["duration_minutes"])
                    if duration < 1:
                        return (
                            jsonify({"error": "Duration must be at least 1 minute"}),
                            400,
                        )

                    budget.start_date = datetime.now()
                    budget.end_date = datetime.now() + timedelta(minutes=duration)
                except ValueError:
                    return jsonify({"error": "Duration must be a valid number"}), 400

            if "category_id" in data:
                new_category = TransactionCategory.query.get(data["category_id"])
                if not new_category:
                    return jsonify({"error": "Category not found"}), 404

                if budget.category_id != new_category.id:
                    existing_budget = Budget.query.filter(
                        Budget.id != budget_id,
                        Budget.user_id == current_user_id,
                        Budget.category_id == new_category.id,
                        Budget.end_date > datetime.now(),
                    ).first()

                    if existing_budget:
                        return (
                            jsonify(
                                {
                                    "error": f"Active budget already exists for {new_category} category"
                                }
                            ),
                            400,
                        )

                budget.category_id = new_category.id

            if "amount" in data:
                try:
                    new_amount = Decimal(str(data["amount"]))
                    if new_amount <= 0:
                        return jsonify({"error": "Amount must be positive"}), 400

                    if new_amount != budget.amount:
                        remaining_percentage = budget.remaining_amount / budget.amount
                        budget.remaining_amount = new_amount * remaining_percentage
                        budget.amount = new_amount

                except ValueError:
                    return jsonify({"error": "Invalid amount format"}), 400
                except DecimalException:
                    return jsonify({"error": "Invalid amount value"}), 400

            db.session.commit()
            return jsonify(budget.to_dict()), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # GET
    return jsonify(budget.to_dict()), 200
