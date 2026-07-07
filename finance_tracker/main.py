"""
main.py
--------
The user-facing menu system. Wires together ExpenseManager (data),
file_handler (persistence), reports (analysis), and utils (safe input)
into one runnable application.
"""

from finance_tracker.expense_manager import ExpenseManager
from finance_tracker.expense import ExpenseValidationError, VALID_CATEGORIES
from finance_tracker import file_handler
from finance_tracker import reports
from finance_tracker import utils


class FinanceTracker:
    def __init__(self):
        self.manager = ExpenseManager()
        self._load()

    # ---------- persistence helpers ----------

    def _load(self):
        data = file_handler.load_data()
        self.manager.load_from_dict_list(data.get("expenses", []))
        self.manager.budgets = data.get("budgets", {})

    def _save(self):
        if file_handler.save_data(self.manager):
            print("💾 Data saved.")
        else:
            print("⚠️  Data could NOT be saved. Check file permissions.")

    # ---------- main loop ----------

    def run(self):
        print("=" * 60)
        print("          PERSONAL FINANCE TRACKER")
        print("=" * 60)

        menu_actions = {
            "1": self.add_expense,
            "2": self.view_expenses,
            "3": self.search_expenses,
            "4": self.generate_monthly_report,
            "5": self.view_category_breakdown,
            "6": self.set_budget,
            "7": self.export_data,
            "8": self.view_statistics,
            "9": self.backup_restore,
            "10": self.view_trend,
            "11": self.edit_or_delete_expense,
        }

        while True:
            self._print_menu()
            choice = input("\nEnter your choice (0-11): ").strip()

            if choice == "0":
                self._save()
                print("\n" + "=" * 60)
                print("Thank you for using Personal Finance Tracker!")
                print("=" * 60)
                break

            action = menu_actions.get(choice)
            if action:
                try:
                    action()
                except ExpenseValidationError as e:
                    print(f"❌ {e}")
                except KeyboardInterrupt:
                    print("\n(cancelled)")
            else:
                print("Invalid choice! Please enter 0-11.")

    @staticmethod
    def _print_menu():
        print("\n" + "=" * 40)
        print("              MAIN MENU")
        print("=" * 40)
        print("1. Add New Expense")
        print("2. View All Expenses")
        print("3. Search Expenses")
        print("4. Generate Monthly Report")
        print("5. View Category Breakdown")
        print("6. Set/Update Budget")
        print("7. Export Data to CSV")
        print("8. View Statistics")
        print("9. Backup/Restore Data")
        print("10. View Spending Trend")
        print("11. Edit/Delete an Expense")
        print("0. Save & Exit")
        print("=" * 40)

    # ---------- menu actions ----------

    def add_expense(self):
        print("\n--- ADD NEW EXPENSE ---")
        date = utils.prompt_date()
        amount = utils.prompt_amount()
        category = utils.prompt_category()
        description = input("Description (optional): ").strip()
        expense = self.manager.add_expense(date, amount, category, description)
        self._save()
        print(f"✅ Expense added: {expense}")

    def view_expenses(self):
        print("\n--- ALL EXPENSES ---")
        if not self.manager.expenses:
            print("No expenses recorded yet.")
            return
        for exp in self.manager.expenses:
            print(exp)
        print(f"\nTotal: ₹{self.manager.total_spent():,.2f} across {len(self.manager.expenses)} expenses.")

    def search_expenses(self):
        print("\n--- SEARCH EXPENSES ---")
        print("Leave any field blank to skip that filter.")
        keyword = input("Keyword in description: ").strip() or None
        category = input(f"Category ({'/'.join(VALID_CATEGORIES)}): ").strip() or None
        start_date = input("Start date (YYYY-MM-DD): ").strip() or None
        end_date = input("End date (YYYY-MM-DD): ").strip() or None

        results = self.manager.search(keyword=keyword, category=category,
                                       start_date=start_date, end_date=end_date)
        if not results:
            print("No matching expenses found.")
            return
        for exp in results:
            print(exp)
        total = sum(e.amount for e in results)
        print(f"\n{len(results)} result(s), total ₹{total:,.2f}")

    def generate_monthly_report(self):
        print("\n--- MONTHLY REPORT ---")
        year_month = utils.prompt_year_month()
        print(reports.monthly_summary(self.manager, year_month))

    def view_category_breakdown(self):
        print("\n--- CATEGORY BREAKDOWN ---")
        choice = input("Specific month? (y/n): ").strip().lower()
        year_month = utils.prompt_year_month() if choice == "y" else None
        print(reports.category_breakdown(self.manager, year_month))

    def view_trend(self):
        print("\n--- SPENDING TREND ---")
        print(reports.trend_analysis(self.manager))

    def set_budget(self):
        print("\n--- SET/UPDATE BUDGET ---")
        year_month = utils.prompt_year_month()
        amount = utils.prompt_amount("Monthly budget amount: ")
        self.manager.set_budget(year_month, amount)
        self._save()
        print(f"✅ Budget for {year_month} set to ₹{amount:,.2f}")

    def export_data(self):
        print("\n--- EXPORT DATA ---")
        path = file_handler.export_to_csv(self.manager)
        if path:
            print(f"✅ Exported to {path}")
        else:
            print("❌ Export failed.")

    def view_statistics(self):
        print("\n--- STATISTICS ---")
        print(reports.statistics_summary(self.manager))

    def backup_restore(self):
        print("\n--- BACKUP/RESTORE ---")
        print("1. Create backup now")
        print("2. Restore from a backup")
        print("3. List backups")
        choice = input("Choose (1-3): ").strip()
        if choice == "1":
            path = file_handler.backup_before_write()
            print(f"✅ Backup created at {path}" if path else "❌ Nothing to back up yet.")
        elif choice == "2":
            backups = file_handler.list_backups()
            if not backups:
                print("No backups available.")
                return
            for i, b in enumerate(backups, 1):
                print(f"{i}. {b}")
            sel = input("Select backup number to restore: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(backups):
                if utils.confirm("This will overwrite current data. Continue? (y/n): "):
                    if file_handler.restore_backup(backups[int(sel) - 1]):
                        self._load()
                        print("✅ Restored successfully.")
            else:
                print("Invalid selection.")
        elif choice == "3":
            backups = file_handler.list_backups()
            print("\n".join(backups) if backups else "No backups available.")
        else:
            print("Invalid choice.")

    def edit_or_delete_expense(self):
        print("\n--- EDIT/DELETE EXPENSE ---")
        raw_id = input("Enter expense ID: ").strip()
        if not raw_id.isdigit():
            print("❌ Invalid ID.")
            return
        expense_id = int(raw_id)
        exp = self.manager.get_expense(expense_id)
        if exp is None:
            print("❌ No expense with that ID.")
            return
        print(f"Found: {exp}")
        print("1. Edit  2. Delete  3. Cancel")
        choice = input("Choose: ").strip()
        if choice == "1":
            print("Leave a field blank to keep its current value.")
            new_amount = input(f"New amount (current {exp.amount}): ").strip()
            new_category = input(f"New category (current {exp.category}): ").strip()
            new_description = input(f"New description (current '{exp.description}'): ").strip()
            fields = {}
            if new_amount:
                fields["amount"] = new_amount
            if new_category:
                fields["category"] = new_category
            if new_description:
                fields["description"] = new_description
            if self.manager.update_expense(expense_id, **fields):
                self._save()
                print("✅ Expense updated.")
        elif choice == "2":
            if utils.confirm("Delete this expense? (y/n): "):
                self.manager.remove_expense(expense_id)
                self._save()
                print("🗑️  Expense deleted.")
        else:
            print("Cancelled.")


def main():
    tracker = FinanceTracker()
    tracker.run()


if __name__ == "__main__":
    main()
