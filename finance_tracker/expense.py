"""
expense.py
----------
Defines the Expense class: a single record of money spent.
Handles its own validation so bad data never enters the system.
"""

from datetime import datetime

# Categories allowed in the app. Kept in one place so every module
# (menu, reports, validation) stays in sync.
VALID_CATEGORIES = [
    "Food", "Transport", "Entertainment", "Bills",
    "Shopping", "Health", "Education", "Other"
]

DATE_FORMAT = "%Y-%m-%d"


class ExpenseValidationError(Exception):
    """Raised when expense data fails validation."""
    pass


class Expense:
    """Represents a single expense entry."""

    def __init__(self, date, amount, category, description="", expense_id=None):
        self.date = self._validate_date(date)
        self.amount = self._validate_amount(amount)
        self.category = self._validate_category(category)
        self.description = str(description).strip()
        # expense_id is set by ExpenseManager if not supplied (e.g. when loading from file)
        self.expense_id = expense_id

    # ---------- validation helpers ----------

    @staticmethod
    def _validate_date(date_value):
        if isinstance(date_value, datetime):
            return date_value.strftime(DATE_FORMAT)
        date_str = str(date_value).strip()
        try:
            datetime.strptime(date_str, DATE_FORMAT)
        except ValueError:
            raise ExpenseValidationError(
                f"Invalid date '{date_str}'. Expected format YYYY-MM-DD."
            )
        return date_str

    @staticmethod
    def _validate_amount(amount_value):
        try:
            amount = float(amount_value)
        except (TypeError, ValueError):
            raise ExpenseValidationError(f"Amount '{amount_value}' is not a number.")
        if amount <= 0:
            raise ExpenseValidationError("Amount must be greater than zero.")
        return round(amount, 2)

    @staticmethod
    def _validate_category(category_value):
        category = str(category_value).strip().title()
        if category not in VALID_CATEGORIES:
            raise ExpenseValidationError(
                f"Category '{category_value}' is invalid. "
                f"Choose from: {', '.join(VALID_CATEGORIES)}"
            )
        return category

    # ---------- serialization ----------

    def to_dict(self):
        return {
            "id": self.expense_id,
            "date": self.date,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            date=data["date"],
            amount=data["amount"],
            category=data["category"],
            description=data.get("description", ""),
            expense_id=data.get("id"),
        )

    def __str__(self):
        return (f"[{self.expense_id}] {self.date} | {self.category:<13} | "
                f"₹{self.amount:>10.2f} | {self.description}")

    def __repr__(self):
        return f"Expense({self.to_dict()})"
