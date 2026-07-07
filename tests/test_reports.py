"""
Unit tests for reports.py.
Run with:  python -m unittest discover -s tests
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from finance_tracker.expense_manager import ExpenseManager
from finance_tracker import reports


class TestReports(unittest.TestCase):

    def setUp(self):
        self.manager = ExpenseManager()
        self.manager.add_expense("2026-07-01", 300, "Food", "Groceries")
        self.manager.add_expense("2026-07-05", 150, "Transport", "Cab")
        self.manager.add_expense("2026-06-20", 500, "Bills", "Electricity")

    def test_monthly_summary_contains_month(self):
        summary = reports.monthly_summary(self.manager, "2026-07")
        self.assertIn("2026-07", summary)
        self.assertIn("Food", summary)

    def test_monthly_summary_reflects_budget(self):
        self.manager.set_budget("2026-07", 1000)
        summary = reports.monthly_summary(self.manager, "2026-07")
        self.assertIn("Remaining", summary)
        self.assertIn("within budget", summary)

    def test_monthly_summary_over_budget_flag(self):
        self.manager.set_budget("2026-07", 100)
        summary = reports.monthly_summary(self.manager, "2026-07")
        self.assertIn("OVER BUDGET", summary)

    def test_category_breakdown_all_time(self):
        text = reports.category_breakdown(self.manager)
        self.assertIn("Bills", text)
        self.assertIn("Food", text)
        self.assertIn("Transport", text)

    def test_category_breakdown_empty(self):
        empty_manager = ExpenseManager()
        text = reports.category_breakdown(empty_manager)
        self.assertEqual(text, "No expenses to show.")

    def test_trend_analysis_runs(self):
        text = reports.trend_analysis(self.manager)
        self.assertIn("2026-06", text)
        self.assertIn("2026-07", text)

    def test_statistics_summary_empty(self):
        empty_manager = ExpenseManager()
        text = reports.statistics_summary(empty_manager)
        self.assertEqual(text, "No expenses recorded yet.")

    def test_statistics_summary_has_highest_lowest(self):
        text = reports.statistics_summary(self.manager)
        self.assertIn("Highest expense", text)
        self.assertIn("Lowest expense", text)


if __name__ == "__main__":
    unittest.main()
