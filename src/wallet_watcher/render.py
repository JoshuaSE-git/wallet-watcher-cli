from rich.table import Table
from wallet_watcher._types import Expense, ExpenseField
from typing import List
from wallet_watcher.constants import FIELD_NAMES


def render_table(
    data: List[Expense],
    sort_key: ExpenseField = ExpenseField.DATE,
    reverse: bool = False,
    title: str = "",
):
    table = Table(title=title)
    for col in FIELD_NAMES:
        table.add_column(col.upper())

    key_map = {
        ExpenseField.DATE: lambda x: x.date,
        ExpenseField.AMOUNT: lambda x: x.amount,
        ExpenseField.ID: lambda x: x.id,
    }

    sorted_data = sorted(data, key=key_map[sort_key], reverse=reverse)

    for expense in sorted_data:
        table.add_row(
            str(expense.id),
            str(expense.date),
            expense.category,
            expense.description,
            "$" + str(expense.amount),
        )

    return table
