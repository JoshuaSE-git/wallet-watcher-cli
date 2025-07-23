import datetime as dt

from wallet_watcher._types import Expense
from wallet_watcher.constants import DATE_FORMAT_STRING
from typing import Dict, List
from decimal import Decimal


def convert_csv_row_to_expense(row: Dict[str, str]) -> Expense:
    return Expense(
        int(row["id"]),
        dt.datetime.strptime(row["date"], DATE_FORMAT_STRING).date(),
        row["category"],
        row["description"],
        Decimal(row["amount"]),
    )


def convert_csv_to_expenses(csv: List[Dict[str, str]]) -> List[Expense]:
    ret: List[Expense] = []
    for row in csv:
        ret.append(convert_csv_row_to_expense(row))
    return ret


def convert_expense_to_csv_row(expense: Expense) -> Dict[str, str]:
    return {
        "id": str(expense.id),
        "date": expense.date.strftime(DATE_FORMAT_STRING),
        "category": expense.category,
        "description": expense.description,
        "amount": f"{expense.amount:.2f}",
    }


def convert_expenses_to_csv(expenses: List[Expense]) -> List[Dict[str, str]]:
    ret: List[Dict[str, str]] = []
    for expense in expenses:
        ret.append(convert_expense_to_csv_row(expense))
    return ret
