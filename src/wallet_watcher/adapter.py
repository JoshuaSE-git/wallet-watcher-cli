import datetime as dt
from typing import Dict, List
from decimal import Decimal

from wallet_watcher._types import Expense
from wallet_watcher.constants import DATE_FORMAT_STRING


def convert_csv_row_to_expense(row: Dict[str, str]) -> Expense:
    return Expense(
        int(row["id"]),
        dt.datetime.strptime(row["date"], DATE_FORMAT_STRING).date(),
        row["category"],
        row["description"],
        Decimal(row["amount"]),
    )


def convert_csv_to_expenses(csv: List[Dict[str, str]]) -> List[Expense]:
    expenses = []
    for row in csv:
        expenses.append(convert_csv_row_to_expense(row))

    return expenses


def convert_expense_to_csv_row(expense: Expense) -> Dict[str, str]:
    return {
        "id": str(expense.id),
        "date": expense.date.strftime(DATE_FORMAT_STRING),
        "category": expense.category,
        "description": expense.description,
        "amount": f"{expense.amount:.2f}",
    }


def convert_expenses_to_csv(expenses: List[Expense]) -> List[Dict[str, str]]:
    csv = []
    for expense in expenses:
        csv.append(convert_expense_to_csv_row(expense))

    return csv
