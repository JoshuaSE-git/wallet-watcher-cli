import datetime as dt

from typing import List, Set
from _types import Expense


def add_expense(
    id: int,
    description: str,
    amount: float,
    date: str | None = None,
    category: str | None = None,
) -> Expense:
    if not date:
        date = dt.date.today().strftime("%Y/%m/%d")

    if not category:
        category = "General"

    return Expense(id, date, category, description, amount)


def delete_expense(data: List[Expense], *id: int) -> List[Expense]:
    id_set: Set[int] = set(id)
    filtered_rows: List[Expense] = list(filter(lambda row: row.id not in id_set, data))
    return filtered_rows


def modify_expense(data, id, new_date, new_category, new_description, new_amount):
    print()
