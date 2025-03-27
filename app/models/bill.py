from sqlalchemy.sql import func
from app.models import db


class Bill(db.Model):
    __tablename__ = "bills"

    id = db.Column(db.Integer, primary_key=True)
    biller_name = db.Column(db.String(255), nullable=False)
    due_date = db.Column(db.DateTime(timezone=True), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    status = db.Column(db.String(20), default="pending")

    # FK
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey("transaction_categories.id"), nullable=False
    )

    # relationships
    user = db.relationship("User", backref="bills")
    account = db.relationship("Account", backref="bills")
    category = db.relationship("TransactionCategory", backref="bills")

    VALID_STATUSES = ["pending", "paid", "cancelled"]

    def __repr__(self):
        return f"<Bill {self.biller_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "biller_name": self.biller_name,
            "due_date": self.due_date.isoformat(),
            "amount": float(self.amount),
            "status": self.status,
            "account": self.account.account_number,
            "category": self.category.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
