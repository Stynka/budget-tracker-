"""Database helpers for the budget tracker.

Uses SQLite, which stores everything in a single file (budget.db).
No server needed — Python has SQLite built in.
"""

import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "budget.db"

CATEGORIES = ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Other"]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't already exist, and seed sample data on first run."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            spent_on TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )

    cur.execute("SELECT COUNT(*) FROM settings WHERE key = 'monthly_budget'")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO settings (key, value) VALUES ('monthly_budget', '2000')"
        )

    cur.execute("SELECT COUNT(*) FROM expenses")
    if cur.fetchone()[0] == 0:
        _seed_sample_data(cur)

    conn.commit()
    conn.close()


def _seed_sample_data(cur):
    """Insert a handful of expenses dated within the current month so the dashboard isn't empty."""
    today = date.today()
    samples = [
        ("Morning coffee", "Food", 4.50, today - timedelta(days=0)),
        ("Groceries", "Food", 62.30, today - timedelta(days=1)),
        ("Uber to office", "Transport", 14.20, today - timedelta(days=1)),
        ("Cinema ticket", "Entertainment", 18.00, today - timedelta(days=3)),
        ("Electricity bill", "Bills", 95.40, today - timedelta(days=4)),
        ("New sneakers", "Shopping", 120.00, today - timedelta(days=5)),
        ("Lunch with friend", "Food", 28.75, today - timedelta(days=6)),
        ("Train pass", "Transport", 55.00, today - timedelta(days=7)),
        ("Spotify", "Entertainment", 11.99, today - timedelta(days=8)),
        ("Internet bill", "Bills", 45.00, today - timedelta(days=9)),
        ("Bookstore", "Shopping", 32.10, today - timedelta(days=10)),
        ("Pharmacy", "Other", 17.80, today - timedelta(days=11)),
    ]
    # Keep dates inside the current month so charts populate immediately.
    safe_samples = [
        (name, cat, amount, (d if d.month == today.month else today).isoformat())
        for name, cat, amount, d in samples
    ]
    cur.executemany(
        "INSERT INTO expenses (name, category, amount, spent_on) VALUES (?, ?, ?, ?)",
        safe_samples,
    )


def add_expense(name: str, category: str, amount: float, spent_on: date):
    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (name, category, amount, spent_on) VALUES (?, ?, ?, ?)",
        (name.strip(), category, float(amount), spent_on.isoformat()),
    )
    conn.commit()
    conn.close()


def delete_expense(expense_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def fetch_expenses(category: str | None = None,
                   start: date | None = None,
                   end: date | None = None):
    """Return rows as a list of dicts, filtered by the sidebar controls."""
    query = "SELECT id, name, category, amount, spent_on FROM expenses WHERE 1=1"
    params: list = []

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if start:
        query += " AND spent_on >= ?"
        params.append(start.isoformat())
    if end:
        query += " AND spent_on <= ?"
        params.append(end.isoformat())

    query += " ORDER BY spent_on DESC, id DESC"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_budget() -> float:
    conn = get_connection()
    row = conn.execute(
        "SELECT value FROM settings WHERE key = 'monthly_budget'"
    ).fetchone()
    conn.close()
    return float(row["value"]) if row else 2000.0


def set_budget(amount: float):
    conn = get_connection()
    conn.execute(
        "UPDATE settings SET value = ? WHERE key = 'monthly_budget'",
        (str(float(amount)),),
    )
    conn.commit()
    conn.close()


def month_total(today: date | None = None) -> float:
    today = today or date.today()
    start = today.replace(day=1).isoformat()
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE spent_on >= ?",
        (start,),
    ).fetchone()
    conn.close()
    return float(row["total"])
