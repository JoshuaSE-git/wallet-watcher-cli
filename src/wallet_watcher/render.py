from rich.table import Table
from wallet_watcher._types import Expense
from typing import List
from wallet_watcher.constants import FIELD_NAMES


def render_table(data: List[Expense]):
    table = Table()
    for col in FIELD_NAMES:
        table.add_column(col.upper())

    for expense in data:
        table.add_row(
            str(expense.id),
            str(expense.date),
            expense.category,
            expense.description,
            "$" + str(expense.amount),
        )

    return table
