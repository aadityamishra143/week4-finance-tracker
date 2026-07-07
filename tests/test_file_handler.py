"""
Unit tests for file_handler.py.
Uses temporary directories so tests never touch real project data.
Run with:  python -m unittest discover -s tests
"""

import unittest
import sys
import os
import shutil
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from finance_tracker import file_handler
from finance_tracker.expense_manager import ExpenseManager


class TestFileHandler(unittest.TestCase):

    def setUp(self):
        # Redirect all file_handler paths into a temp sandbox for this test only.
        self.tmp_dir = tempfile.mkdtemp()
        self.original_data_dir = file_handler.DATA_DIR
        self.original_data_file = file_handler.DATA_FILE
        self.original_backup_dir = file_handler.BACKUP_DIR
        self.original_export_dir = file_handler.EXPORT_DIR

        file_handler.DATA_DIR = self.tmp_dir
        file_handler.DATA_FILE = os.path.join(self.tmp_dir, "expenses.json")
        file_handler.BACKUP_DIR = os.path.join(self.tmp_dir, "backup")
        file_handler.EXPORT_DIR = os.path.join(self.tmp_dir, "exports")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        file_handler.DATA_DIR = self.original_data_dir
        file_handler.DATA_FILE = self.original_data_file
        file_handler.BACKUP_DIR = self.original_backup_dir
        file_handler.EXPORT_DIR = self.original_export_dir

    def test_load_data_missing_file_returns_empty(self):
        data = file_handler.load_data(file_handler.DATA_FILE)
        self.assertEqual(data["expenses"], [])
        self.assertEqual(data["budgets"], {})

    def test_save_and_load_roundtrip(self):
        manager = ExpenseManager()
        manager.add_expense("2026-07-01", 150, "Food", "Test lunch")
        manager.set_budget("2026-07", 1000)

        success = file_handler.save_data(manager, file_handler.DATA_FILE)
        self.assertTrue(success)

        loaded = file_handler.load_data(file_handler.DATA_FILE)
        self.assertEqual(len(loaded["expenses"]), 1)
        self.assertEqual(loaded["budgets"]["2026-07"], 1000)

    def test_load_corrupted_json_returns_empty_when_no_backup(self):
        file_handler.ensure_data_dirs()
        with open(file_handler.DATA_FILE, "w") as f:
            f.write("{not valid json")
        data = file_handler.load_data(file_handler.DATA_FILE)
        self.assertEqual(data["expenses"], [])

    def test_backup_created_on_save(self):
        manager = ExpenseManager()
        manager.add_expense("2026-07-01", 100, "Food")
        file_handler.save_data(manager, file_handler.DATA_FILE)   # first save, no backup yet (no existing file)
        manager.add_expense("2026-07-02", 200, "Transport")
        file_handler.save_data(manager, file_handler.DATA_FILE)   # second save should back up the first
        backups = file_handler.list_backups()
        self.assertGreaterEqual(len(backups), 1)

    def test_export_to_csv_creates_file(self):
        manager = ExpenseManager()
        manager.add_expense("2026-07-01", 100, "Food", "Snacks")
        path = file_handler.export_to_csv(manager, "test_export.csv")
        self.assertTrue(os.path.exists(path))
        with open(path) as f:
            content = f.read()
        self.assertIn("Food", content)
        self.assertIn("Snacks", content)

    def test_import_from_csv_missing_file_returns_empty(self):
        rows = file_handler.import_from_csv(os.path.join(self.tmp_dir, "nope.csv"))
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
