from sqlalchemy.sql import func
from app.models import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), default=0.00)
    transaction_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False, default="")
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())

    # FK
    from_account_id = db.Column(
        db.Integer, db.ForeignKey("accounts.id"), nullable=False
    )
    to_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)

    from_account = db.relationship(
        "Account", foreign_keys=[from_account_id], backref="transactions_from"
    )
    to_account = db.relationship(
        "Account", foreign_keys=[to_account_id], backref="transactions_to"
    )

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"

    VALID_TYPES = [DEPOSIT, WITHDRAWAL, TRANSFER]

    def __init__(self, **kwargs):
        super(Transaction, self).__init__(**kwargs)
        if self.transaction_type not in self.VALID_TYPES:
            raise ValueError(
                f"Invalid transaction type. Must be one of {self.VALID_TYPES}"
            )

    # @property
    # def is_valid(self):
    #     if self.amount <= 0:
    #         return False, "Amount must be positive"

    #     if self.transaction_type == self.DEPOSIT:
    #         return True, None

    #     if self.transaction_type == self.WITHDRAWAL:
    #         if self.from_account.balance < self.amount:
    #             return False, "Insufficient funds"

    #     if self.transaction_type == self.TRANSFER:
    #         if not self.to_account_id:
    #             return False, "Transfer requires destination account"
    #         if self.from_account.balance < self.amount:
    #             return False, "Insufficient funds"

    #     return True, None

    def __repr__(self):
        return f"<Transaction {self.id}: {self.transaction_type} Rp. {self.amount}>"

    def to_dict(self):
        return {
            "id": self.id,
            "amount": float(self.amount),
            "transaction_type": self.transaction_type,
            "description": self.description,
            "from_account_id": self.from_account_id,
            "to_account_id": self.to_account_id,
            "created_at": self.created_at.isoformat(),
            "from_account": (
                self.from_account.account_number if self.from_account else None
            ),
            "to_account": self.to_account.account_number if self.to_account else None,
        }
