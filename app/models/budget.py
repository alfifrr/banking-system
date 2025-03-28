from sqlalchemy.sql import func
from app.models import db


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.DateTime(timezone=True), default=func.now())
    end_date = db.Column(db.DateTime(timezone=True), nullable=False)
    remaining_amount = db.Column(db.Numeric(10, 2), nullable=False)

    # FK
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey("transaction_categories.id"), nullable=False
    )

    user = db.relationship("User", backref="budgets")
    category = db.relationship(
        "TransactionCategory",
        foreign_keys=[category_id],
        back_populates="budgets",
    )

    def __repr__(self):
        return f"<Budget {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "amount": float(self.amount),
            "remaining_amount": float(self.remaining_amount),
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "category": self.category.name,
        }
