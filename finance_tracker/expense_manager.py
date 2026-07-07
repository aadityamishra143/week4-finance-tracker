"""
expense_manager.py
-------------------
ExpenseManager holds the in-memory list of expenses and provides
add / remove / search / filter operations. It does NOT touch files
directly -- that job belongs to file_handler.py. This separation is
what makes the code modular and easy to test.
"""

from finance_tracker.expense import Expense, ExpenseValidationError


class ExpenseManager:
    def __init__(self):
        self.expenses = []          # list[Expense]
        self._next_id = 1
        self.budgets = {}           # {"YYYY-MM": budget_amount}

    # ---------- core operations ----------

    def add_expense(self, date, amount, category, description=""):
        """Validates and adds a new expense. Returns the created Expense."""
        expense = Expense(date, amount, category, description, expense_id=self._next_id)
        self.expenses.append(expense)
        self._next_id += 1
        return expense

    def remove_expense(self, expense_id):
        """Removes an expense by id. Returns True if something was removed."""
        for i, exp in enumerate(self.expenses):
            if exp.expense_id == expense_id:
                del self.expenses[i]
                return True
        return False

    def get_expense(self, expense_id):
        for exp in self.expenses:
            if exp.expense_id == expense_id:
                return exp
        return None

    def update_expense(self, expense_id, **fields):
        """Update one or more fields of an existing expense."""
        exp = self.get_expense(expense_id)
        if exp is None:
            return False
        new_date = fields.get("date", exp.date)
        new_amount = fields.get("amount", exp.amount)
        new_category = fields.get("category", exp.category)
        new_description = fields.get("description", exp.description)
        updated = Expense(new_date, new_amount, new_category, new_description, expense_id)
        self.expenses[self.expenses.index(exp)] = updated
        return True

    # ---------- search / filter ----------

    def search(self, keyword=None, category=None, start_date=None, end_date=None,
               min_amount=None, max_amount=None):
        """Flexible search: any combination of filters can be supplied."""
        results = self.expenses
        if keyword:
            keyword_lower = keyword.lower()
            results = [e for e in results if keyword_lower in e.description.lower()]
        if category:
            cat = category.strip().title()
            results = [e for e in results if e.category == cat]
        if start_date:
            results = [e for e in results if e.date >= start_date]
        if end_date:
            results = [e for e in results if e.date <= end_date]
        if min_amount is not None:
            results = [e for e in results if e.amount >= min_amount]
        if max_amount is not None:
            results = [e for e in results if e.amount <= max_amount]
        return results

    def get_by_month(self, year_month):
        """year_month like '2026-07'."""
        return [e for e in self.expenses if e.date.startswith(year_month)]

    # ---------- budgets ----------

    def set_budget(self, year_month, amount):
        if amount <= 0:
            raise ExpenseValidationError("Budget must be greater than zero.")
        self.budgets[year_month] = round(float(amount), 2)

    def get_budget(self, year_month):
        return self.budgets.get(year_month)

    def budget_status(self, year_month):
        """Returns (spent, budget, remaining) for a given month, budget may be None."""
        spent = sum(e.amount for e in self.get_by_month(year_month))
        budget = self.get_budget(year_month)
        remaining = None if budget is None else round(budget - spent, 2)
        return spent, budget, remaining

    # ---------- stats ----------

    def total_spent(self):
        return round(sum(e.amount for e in self.expenses), 2)

    def category_totals(self):
        totals = {}
        for e in self.expenses:
            totals[e.category] = round(totals.get(e.category, 0) + e.amount, 2)
        return totals

    def to_dict_list(self):
        return [e.to_dict() for e in self.expenses]

    def load_from_dict_list(self, data_list):
        """Replaces current expenses with data loaded from file storage."""
        self.expenses = []
        max_id = 0
        for item in data_list:
            try:
                exp = Expense.from_dict(item)
                self.expenses.append(exp)
                if exp.expense_id and exp.expense_id > max_id:
                    max_id = exp.expense_id
            except ExpenseValidationError:
                # Skip corrupted rows instead of crashing the whole load
                continue
        self._next_id = max_id + 1
