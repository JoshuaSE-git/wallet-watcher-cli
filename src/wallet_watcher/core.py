import datetime as dt
import copy

from typing import List, Set
from _types import Expense
from constants import DATE_FORMAT_STRING


def add_expense(
    id: int,
    description: str,
    amount: float,
    date: str | None = None,
    category: str | None = None,
) -> Expense:
    if not date:
        date = dt.date.today().strftime(DATE_FORMAT_STRING)

    if not category:
        category = "General"

    return Expense(id, date, category, description, amount)


def delete_expense(data: List[Expense], *id: int) -> List[Expense]:
    id_set: Set[int] = set(id)
    filtered_rows: List[Expense] = [
        expense for expense in data if expense.id not in id_set
    ]
    return filtered_rows


def modify_expense(
    data: List[Expense],
    id: int,
    new_date: str | None = None,
    new_category: str | None = None,
    new_description: str | None = None,
    new_amount: float | None = None,
) -> List[Expense]:
    data_copy = [copy.copy(expense) for expense in data]

    for expense in data_copy:
        if expense.id == id:
            if new_date is not None:
                if is_valid_date(new_date, DATE_FORMAT_STRING):
                    expense.date = new_date
                else:
                    raise ValueError(f"Invalid date format {new_date} (use YYYY-MM-DD)")
            if new_category is not None:
                expense.category = new_category
            if new_description is not None:
                expense.description = new_description
            if new_amount is not None:
                expense.amount = new_amount
            return data_copy

    raise ValueError(f"No expense found with ID {id}")


def is_valid_date(date: str, date_format: str) -> bool:
    try:
        dt.datetime.strptime(date, date_format)
    except ValueError:
        return False
    return True
