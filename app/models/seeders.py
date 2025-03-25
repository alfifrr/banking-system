from app.models import db
from app.models.transaction_category import TransactionCategory


def seed_transaction_categories():
    default_categories = [
        {
            "name": "Essential",
            "description": "Basic needs like groceries, utilities, rents, transportations, emergencies",
        },
        {
            "name": "Discretionary",
            "description": "Non-essential spending like entertainments, dine outs, shoppings, subscriptions, fashions, hobbies, charities, celebrations, personal developments",
        },
        {"name": "Financial", "description": "Investments, savings, debts"},
    ]

    for category in default_categories:
        exists = TransactionCategory.query.filter_by(name=category["name"]).first()
        if not exists:
            new_category = TransactionCategory(
                name=category["name"], description=category["description"]
            )
            db.session.add(new_category)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding categories: {str(e)}")
