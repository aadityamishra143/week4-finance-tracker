"""
utils.py
---------
Small reusable helpers for the command-line interface:
safe input prompts that keep re-asking until the user gives valid data.
Keeping these here (instead of duplicating checks in main.py) is what
'modular code structure' means in practice.
"""

from datetime import datetime
from finance_tracker.expense import VALID_CATEGORIES, DATE_FORMAT


def prompt_date(prompt_text="Date (YYYY-MM-DD, blank = today): "):
    while True:
        raw = input(prompt_text).strip()
        if raw == "":
            return datetime.now().strftime(DATE_FORMAT)
        try:
            datetime.strptime(raw, DATE_FORMAT)
            return raw
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD (e.g. 2026-07-07).")


def prompt_amount(prompt_text="Amount: "):
    while True:
        raw = input(prompt_text).strip()
        try:
            amount = float(raw)
            if amount <= 0:
                print("❌ Amount must be greater than zero.")
                continue
            return amount
        except ValueError:
            print("❌ Please enter a valid number.")


def prompt_category(prompt_text=None):
    options = ", ".join(f"{i+1}={c}" for i, c in enumerate(VALID_CATEGORIES))
    prompt_text = prompt_text or f"Category ({options}): "
    while True:
        raw = input(prompt_text).strip()
        if raw.isdigit() and 1 <= int(raw) <= len(VALID_CATEGORIES):
            return VALID_CATEGORIES[int(raw) - 1]
        title_case = raw.title()
        if title_case in VALID_CATEGORIES:
            return title_case
        print(f"❌ Please choose a valid category: {', '.join(VALID_CATEGORIES)}")


def prompt_year_month(prompt_text="Month (YYYY-MM, blank = current month): "):
    while True:
        raw = input(prompt_text).strip()
        if raw == "":
            return datetime.now().strftime("%Y-%m")
        try:
            datetime.strptime(raw, "%Y-%m")
            return raw
        except ValueError:
            print("❌ Invalid format. Please use YYYY-MM (e.g. 2026-07).")


def confirm(prompt_text="Are you sure? (y/n): "):
    return input(prompt_text).strip().lower() in ("y", "yes")


def pause():
    input("\nPress Enter to continue...")
