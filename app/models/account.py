from sqlalchemy.sql import func
import random
from app.models import db


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(16), unique=True, nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    # true for first user creation
    is_main = db.Column(db.Boolean, default=False, nullable=False)

    # FK to user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # user = db.relationship("User", backref=db.backref("account", lazy=True))

    def __repr__(self):
        return f"<Account {self.account_number}>"

    def to_dict(self):
        return {
            "id": self.id,
            "account_number": self.account_number,
            "account_type": self.account_type,
            "balance": float(self.balance),
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_main": self.is_main,
        }

    @staticmethod
    def generate_unique_account_number():
        while True:
            account_number = str(random.randint(1000000000000000, 9999999999999999))
            if not Account.query.filter_by(account_number=account_number).first():
                return account_number
