from rich import box
from rich.table import Table
from wallet_watcher._types import Expense, ExpenseField
from typing import List


def render_table(
    data: List[Expense],
    title: str = "",
):
    table = Table(title=title, box=box.SIMPLE_HEAVY)

    table.add_column("ID", style="dim", width=4)
    table.add_column("DATE", style="white")
    table.add_column("CATEGORY", style="bold cyan")
    table.add_column("DESCRIPTION", style="white")
    table.add_column("AMOUNT", style="bold green", justify="right")

    for expense in data:
        table.add_row(
            str(expense.id),
            str(expense.date),
            expense.category,
            expense.description,
            "$" + str(expense.amount),
        )

    return table
