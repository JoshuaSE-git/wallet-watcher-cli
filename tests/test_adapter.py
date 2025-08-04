import datetime as dt
from decimal import Decimal

import wallet_watcher.adapter as adapter
from wallet_watcher._types import Expense


def test_csv_to_expense():
    data = {
        "id": "1",
        "date": "2025-06-01",
        "category": "Gaming",
        "description": "CoD",
        "amount": "59.99",
    }
    expense = adapter.convert_csv_row_to_expense(data)
    correct_expense = Expense(
        1,
        dt.datetime.fromisoformat("2025-06-01").date(),
        "Gaming",
        "CoD",
        Decimal("59.99"),
    )

    assert expense == correct_expense


def test_csv_to_expense_2():
    data = {
        "id": "99",
        "date": "2025-02-18",
        "category": "General",
        "description": "N/A",
        "amount": "1099.00",
    }
    expense = adapter.convert_csv_row_to_expense(data)
    correct_expense: Expense = Expense(
        99,
        dt.datetime.fromisoformat("2025-02-18").date(),
        "General",
        "N/A",
        Decimal("1099.00"),
    )

    assert expense == correct_expense


def test_expense_to_csv():
    data = Expense(
        1,
        dt.datetime.fromisoformat("2025-11-05").date(),
        "Food",
        "McDonalds",
        Decimal("20.2532"),
    )
    csv = adapter.convert_expense_to_csv_row(data)
    correct_csv = {
        "id": "1",
        "date": "2025-11-05",
        "category": "Food",
        "description": "McDonalds",
        "amount": "20.25",
    }

    assert csv == correct_csv


def test_expense_to_csv_2():
    data = Expense(
        10123,
        dt.datetime.fromisoformat("1900-11-15").date(),
        "General",
        "N/A",
        Decimal("2"),
    )
    csv = adapter.convert_expense_to_csv_row(data)
    correct_csv = {
        "id": "10123",
        "date": "1900-11-15",
        "category": "General",
        "description": "N/A",
        "amount": "2.00",
    }

    assert csv == correct_csv
