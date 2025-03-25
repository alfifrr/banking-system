from app.models import db


class TransactionCategory(db.Model):
    __tablename__ = "transaction_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(255))

    transactions = db.relationship("Transaction", back_populates="transaction_category")

    def __repr__(self):
        return f"<Category {self.name}>"

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}
