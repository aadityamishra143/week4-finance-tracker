"""
reports.py
-----------
Turns raw expense data into human-readable reports:
monthly summaries, category breakdowns, trend analysis, and
simple text-based bar charts (no external plotting library needed).
"""

from collections import defaultdict


def monthly_summary(expense_manager, year_month):
    """Returns a formatted string summarizing one month (YYYY-MM)."""
    monthly = expense_manager.get_by_month(year_month)
    total = sum(e.amount for e in monthly)
    spent, budget, remaining = expense_manager.budget_status(year_month)

    lines = []
    lines.append("=" * 50)
    lines.append(f"MONTHLY REPORT — {year_month}")
    lines.append("=" * 50)
    lines.append(f"Total expenses recorded : {len(monthly)}")
    lines.append(f"Total spent             : ₹{total:,.2f}")

    if budget is not None:
        status = "OVER BUDGET ⚠️" if remaining < 0 else "within budget ✅"
        lines.append(f"Monthly budget          : ₹{budget:,.2f}")
        lines.append(f"Remaining               : ₹{remaining:,.2f} ({status})")
    else:
        lines.append("Monthly budget          : not set")

    if monthly:
        avg = total / len(monthly)
        lines.append(f"Average per expense     : ₹{avg:,.2f}")

    lines.append("-" * 50)
    lines.append("By category:")
    cat_totals = defaultdict(float)
    for e in monthly:
        cat_totals[e.category] += e.amount
    for cat, amt in sorted(cat_totals.items(), key=lambda x: -x[1]):
        lines.append(f"  {cat:<15} ₹{amt:>10,.2f}")

    lines.append("=" * 50)
    return "\n".join(lines)


def category_breakdown(expense_manager, year_month=None):
    """
    Returns a text bar chart of spending by category.
    If year_month is given, restricts to that month; otherwise all-time.
    """
    expenses = expense_manager.get_by_month(year_month) if year_month else expense_manager.expenses
    totals = defaultdict(float)
    for e in expenses:
        totals[e.category] += e.amount

    if not totals:
        return "No expenses to show."

    max_amount = max(totals.values())
    bar_width = 30  # characters for the longest bar

    lines = []
    title = f"CATEGORY BREAKDOWN{' — ' + year_month if year_month else ' (all time)'}"
    lines.append(title)
    lines.append("=" * len(title))
    for cat, amt in sorted(totals.items(), key=lambda x: -x[1]):
        bar_len = int((amt / max_amount) * bar_width) if max_amount else 0
        bar = "█" * bar_len
        lines.append(f"{cat:<15} ₹{amt:>9,.2f} {bar}")
    return "\n".join(lines)


def trend_analysis(expense_manager, num_months=6):
    """
    Shows total spending for the last `num_months` months that have data,
    as a simple text chart, sorted chronologically.
    """
    monthly_totals = defaultdict(float)
    for e in expense_manager.expenses:
        year_month = e.date[:7]  # 'YYYY-MM'
        monthly_totals[year_month] += e.amount

    if not monthly_totals:
        return "No expense history yet."

    months_sorted = sorted(monthly_totals.keys())[-num_months:]
    max_amount = max(monthly_totals[m] for m in months_sorted)
    bar_width = 30

    lines = ["SPENDING TREND", "=" * 40]
    for m in months_sorted:
        amt = monthly_totals[m]
        bar_len = int((amt / max_amount) * bar_width) if max_amount else 0
        bar = "█" * bar_len
        lines.append(f"{m}  ₹{amt:>9,.2f} {bar}")

    if len(months_sorted) >= 2:
        first, last = monthly_totals[months_sorted[0]], monthly_totals[months_sorted[-1]]
        if first > 0:
            change_pct = ((last - first) / first) * 100
            direction = "up" if change_pct > 0 else "down"
            lines.append("-" * 40)
            lines.append(f"Spending is {direction} {abs(change_pct):.1f}% "
                          f"from {months_sorted[0]} to {months_sorted[-1]}.")
    return "\n".join(lines)


def statistics_summary(expense_manager):
    """Overall statistics across all recorded expenses."""
    expenses = expense_manager.expenses
    if not expenses:
        return "No expenses recorded yet."

    amounts = [e.amount for e in expenses]
    total = sum(amounts)
    avg = total / len(amounts)
    highest = max(expenses, key=lambda e: e.amount)
    lowest = min(expenses, key=lambda e: e.amount)
    cat_totals = expense_manager.category_totals()
    top_category = max(cat_totals.items(), key=lambda x: x[1]) if cat_totals else None

    lines = []
    lines.append("OVERALL STATISTICS")
    lines.append("=" * 40)
    lines.append(f"Total expenses tracked : {len(expenses)}")
    lines.append(f"Total amount spent     : ₹{total:,.2f}")
    lines.append(f"Average expense        : ₹{avg:,.2f}")
    lines.append(f"Highest expense        : ₹{highest.amount:,.2f} ({highest.category}, {highest.date})")
    lines.append(f"Lowest expense         : ₹{lowest.amount:,.2f} ({lowest.category}, {lowest.date})")
    if top_category:
        lines.append(f"Top spending category  : {top_category[0]} (₹{top_category[1]:,.2f})")
    return "\n".join(lines)
