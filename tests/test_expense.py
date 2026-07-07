"""
Unit tests for Expense and ExpenseManager.
Run with:  python -m unittest discover -s tests
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from finance_tracker.expense import Expense, ExpenseValidationError
from finance_tracker.expense_manager import ExpenseManager


class TestExpense(unittest.TestCase):

    def test_valid_expense_creation(self):
        e = Expense("2026-07-01", 250, "Food", "Lunch", expense_id=1)
        self.assertEqual(e.amount, 250.0)
        self.assertEqual(e.category, "Food")

    def test_invalid_date_raises(self):
        with self.assertRaises(ExpenseValidationError):
            Expense("07-01-2026", 100, "Food")

    def test_negative_amount_raises(self):
        with self.assertRaises(ExpenseValidationError):
            Expense("2026-07-01", -50, "Food")

    def test_zero_amount_raises(self):
        with self.assertRaises(ExpenseValidationError):
            Expense("2026-07-01", 0, "Food")

    def test_invalid_amount_type_raises(self):
        with self.assertRaises(ExpenseValidationError):
            Expense("2026-07-01", "abc", "Food")

    def test_invalid_category_raises(self):
        with self.assertRaises(ExpenseValidationError):
            Expense("2026-07-01", 100, "NotACategory")

    def test_category_case_insensitive(self):
        e = Expense("2026-07-01", 100, "food")
        self.assertEqual(e.category, "Food")

    def test_to_dict_and_from_dict_roundtrip(self):
        e1 = Expense("2026-07-01", 99.5, "Bills", "Electricity", expense_id=3)
        data = e1.to_dict()
        e2 = Expense.from_dict(data)
        self.assertEqual(e1.date, e2.date)
        self.assertEqual(e1.amount, e2.amount)
        self.assertEqual(e1.category, e2.category)
        self.assertEqual(e1.expense_id, e2.expense_id)


class TestExpenseManager(unittest.TestCase):

    def setUp(self):
        self.manager = ExpenseManager()

    def test_add_expense_assigns_incrementing_ids(self):
        e1 = self.manager.add_expense("2026-07-01", 100, "Food")
        e2 = self.manager.add_expense("2026-07-02", 200, "Transport")
        self.assertEqual(e1.expense_id, 1)
        self.assertEqual(e2.expense_id, 2)

    def test_remove_expense(self):
        e1 = self.manager.add_expense("2026-07-01", 100, "Food")
        removed = self.manager.remove_expense(e1.expense_id)
        self.assertTrue(removed)
        self.assertEqual(len(self.manager.expenses), 0)

    def test_remove_nonexistent_expense_returns_false(self):
        self.assertFalse(self.manager.remove_expense(999))

    def test_search_by_category(self):
        self.manager.add_expense("2026-07-01", 100, "Food")
        self.manager.add_expense("2026-07-02", 200, "Transport")
        results = self.manager.search(category="Food")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].category, "Food")

    def test_search_by_keyword(self):
        self.manager.add_expense("2026-07-01", 100, "Food", "Pizza night")
        self.manager.add_expense("2026-07-02", 50, "Food", "Groceries")
        results = self.manager.search(keyword="pizza")
        self.assertEqual(len(results), 1)

    def test_total_spent(self):
        self.manager.add_expense("2026-07-01", 100, "Food")
        self.manager.add_expense("2026-07-02", 50.5, "Transport")
        self.assertEqual(self.manager.total_spent(), 150.5)

    def test_category_totals(self):
        self.manager.add_expense("2026-07-01", 100, "Food")
        self.manager.add_expense("2026-07-02", 50, "Food")
        totals = self.manager.category_totals()
        self.assertEqual(totals["Food"], 150)

    def test_budget_status(self):
        self.manager.add_expense("2026-07-01", 100, "Food")
        self.manager.set_budget("2026-07", 500)
        spent, budget, remaining = self.manager.budget_status("2026-07")
        self.assertEqual(spent, 100)
        self.assertEqual(budget, 500)
        self.assertEqual(remaining, 400)

    def test_load_from_dict_list_skips_bad_rows(self):
        data = [
            {"id": 1, "date": "2026-07-01", "amount": 100, "category": "Food", "description": ""},
            {"id": 2, "date": "bad-date", "amount": 100, "category": "Food", "description": ""},
        ]
        self.manager.load_from_dict_list(data)
        self.assertEqual(len(self.manager.expenses), 1)


if __name__ == "__main__":
    unittest.main()
