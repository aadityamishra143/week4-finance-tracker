"""
file_handler.py
-----------------
Everything that touches the filesystem lives here: loading/saving JSON,
CSV export/import, and backup/restore. Every function uses 'with' so
files are always closed properly, and every risky operation is wrapped
in try/except so a missing file or bad permission never crashes the app.
"""

import json
import csv
import os
import shutil
from datetime import datetime

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "expenses.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backup")
EXPORT_DIR = os.path.join(DATA_DIR, "exports")
BUDGETS_KEY = "budgets"
EXPENSES_KEY = "expenses"


def ensure_data_dirs():
    """Creates the data/, data/backup/, and data/exports/ folders if missing."""
    for folder in (DATA_DIR, BACKUP_DIR, EXPORT_DIR):
        os.makedirs(folder, exist_ok=True)


# ---------- JSON load / save ----------

def load_data(path=DATA_FILE):
    """
    Loads expenses + budgets from a JSON file.
    Returns a dict: {"expenses": [...], "budgets": {...}}
    Never raises -- returns an empty structure on any failure so the
    app can still start with a fresh dataset.
    """
    ensure_data_dirs()
    empty = {EXPENSES_KEY: [], BUDGETS_KEY: {}}

    if not os.path.exists(path):
        return empty

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return empty
            data = json.loads(content)
            data.setdefault(EXPENSES_KEY, [])
            data.setdefault(BUDGETS_KEY, {})
            return data
    except json.JSONDecodeError:
        print(f"⚠️  Warning: '{path}' is corrupted and could not be read as JSON.")
        return _try_restore_from_backup() or empty
    except PermissionError:
        print(f"⚠️  Warning: no permission to read '{path}'.")
        return empty
    except OSError as e:
        print(f"⚠️  Warning: could not read '{path}' ({e}).")
        return empty


def save_data(expense_manager, path=DATA_FILE):
    """
    Saves expenses + budgets to JSON. Makes a timestamped backup first
    so a failed write never destroys the last known-good data.
    Returns True on success, False on failure.
    """
    ensure_data_dirs()
    backup_before_write(path)

    payload = {
        EXPENSES_KEY: expense_manager.to_dict_list(),
        BUDGETS_KEY: expense_manager.budgets,
    }

    try:
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp_path, path)   # atomic-ish swap: avoids half-written files
        return True
    except PermissionError:
        print(f"❌ Error: no permission to write to '{path}'.")
        return False
    except OSError as e:
        print(f"❌ Error: could not save data ({e}).")
        return False


# ---------- backup / restore ----------

def backup_before_write(path=DATA_FILE):
    """Copies the current data file into data/backup/ with a timestamp."""
    if not os.path.exists(path):
        return None
    ensure_data_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"expenses_{timestamp}.json")
    try:
        shutil.copy2(path, backup_path)
        return backup_path
    except OSError as e:
        print(f"⚠️  Warning: could not create backup ({e}).")
        return None


def list_backups():
    ensure_data_dirs()
    files = sorted(os.listdir(BACKUP_DIR), reverse=True)
    return [f for f in files if f.endswith(".json")]


def restore_backup(backup_filename, path=DATA_FILE):
    """Restores a specific backup file over the main data file."""
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    if not os.path.exists(backup_path):
        print(f"❌ Backup '{backup_filename}' not found.")
        return False
    try:
        shutil.copy2(backup_path, path)
        return True
    except OSError as e:
        print(f"❌ Error restoring backup ({e}).")
        return False


def _try_restore_from_backup():
    """Used internally when the main JSON file is corrupted."""
    backups = list_backups()
    if not backups:
        return None
    latest = backups[0]
    print(f"↻ Attempting automatic recovery from backup '{latest}'...")
    try:
        with open(os.path.join(BACKUP_DIR, latest), "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault(EXPENSES_KEY, [])
            data.setdefault(BUDGETS_KEY, {})
            print("✅ Recovered successfully from backup.")
            return data
    except (OSError, json.JSONDecodeError):
        return None


# ---------- CSV export / import ----------

def export_to_csv(expense_manager, filename=None):
    """Exports all current expenses to a CSV file in data/exports/."""
    ensure_data_dirs()
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"expenses_{timestamp}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "date", "amount", "category", "description"])
            for exp in expense_manager.expenses:
                d = exp.to_dict()
                writer.writerow([d["id"], d["date"], d["amount"], d["category"], d["description"]])
        return filepath
    except OSError as e:
        print(f"❌ Error exporting CSV ({e}).")
        return None


def import_from_csv(filepath):
    """
    Reads a CSV file and returns a list of dict rows suitable for
    Expense.from_dict(). Skips rows that fail validation later --
    validation itself happens in ExpenseManager.load_from_dict_list.
    """
    if not os.path.exists(filepath):
        print(f"❌ File '{filepath}' does not exist.")
        return []

    rows = []
    try:
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows
    except OSError as e:
        print(f"❌ Error reading CSV ({e}).")
        return []
    except csv.Error as e:
        print(f"❌ CSV format error ({e}).")
        return []
