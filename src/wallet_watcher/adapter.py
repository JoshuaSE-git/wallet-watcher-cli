import datetime as dt

from wallet_watcher._types import Expense
from wallet_watcher.constants import DATE_FORMAT_STRING
from typing import Dict
from decimal import Decimal


def convert_csv_row_to_expense(row: Dict[str, str]) -> Expense:
    return Expense(
        int(row["id"]),
        dt.datetime.strptime(row["date"], DATE_FORMAT_STRING),
        row["category"],
        row["description"],
        Decimal(row["amount"]),
    )


def convert_expense_to_csv_row(expense: Expense) -> Dict[str, str]:
    return {
        "id": str(expense.id),
        "date": expense.date.strftime(DATE_FORMAT_STRING),
        "category": expense.category,
        "description": expense.description,
        "amount": f"{expense.amount:.2f}",
    }
