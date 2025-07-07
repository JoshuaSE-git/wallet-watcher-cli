import copy
import datetime as dt

from typing import List, Set
from decimal import Decimal
from wallet_watcher._types import Expense, FilterStrategy, Comparator
from wallet_watcher.constants import (
    DEFAULT_CATEGORY,
    DEFAULT_DESCRIPTION,
)


def add_expense(
    data: List[Expense],
    amount: Decimal,
    description: str | None = None,
    date: dt.date | None = None,
    category: str | None = None,
) -> Expense:
    if amount < Decimal("0.01"):
        raise ValueError("Amount must be greater than 0.01")

    if not date:
        date = dt.datetime.today()
    if not category:
        category = DEFAULT_CATEGORY
    if not description:
        description = DEFAULT_DESCRIPTION
    id: int = get_next_id(data)

    return Expense(id, date, category, description, amount)


def get_next_id(data: List[Expense]) -> int:
    return max((expense.id for expense in data), default=0) + 1


def delete_expenses(
    data: List[Expense], filter_strategy: FilterStrategy
) -> List[Expense]:
    return [expense for expense in data if not filter_strategy(expense)]


def filter_expenses(
    data: List[Expense], filter_strategy: FilterStrategy
) -> List[Expense]:
    return [expense for expense in data if filter_strategy(expense)]


def filter_by_id(*filter_ids: int) -> FilterStrategy:
    id_set: Set[int] = set(filter_ids)

    def strategy(expense: Expense) -> bool:
        return expense.id in id_set

    return strategy


def filter_by_category(*categories: str) -> FilterStrategy:
    category_set: Set[str] = set(categories)

    def strategy(expense: Expense) -> bool:
        return expense.category in category_set

    return strategy


def filter_by_price(amount: Decimal, comparator: Comparator = Comparator.EQ):
    def strategy(expense: Expense) -> bool:
        match comparator:
            case Comparator.LT:
                return expense.amount < amount
            case Comparator.LTE:
                return expense.amount <= amount
            case Comparator.GT:
                return expense.amount > amount
            case Comparator.GTE:
                return expense.amount >= amount
            case Comparator.EQ:
                return expense.amount == amount

    return strategy


def combine_filters(*filters: FilterStrategy) -> FilterStrategy:
    def strategy(expense: Expense) -> bool:
        for filter_strategy in filters:
            if not filter_strategy(expense):
                return False
        return True

    return strategy


def modify_expense(
    data: List[Expense],
    id: int,
    new_date: dt.date | None = None,
    new_category: str | None = None,
    new_description: str | None = None,
    new_amount: Decimal | None = None,
) -> List[Expense]:
    data_copy = [copy.copy(expense) for expense in data]

    for expense in data_copy:
        if expense.id == id:
            if new_date is not None:
                expense.date = new_date
            if new_category is not None:
                expense.category = new_category
            if new_description is not None:
                expense.description = new_description
            if new_amount is not None:
                if new_amount < Decimal("0.01"):
                    raise ValueError("Amount must be greater than 0.01")
                expense.amount = new_amount
            return data_copy

    raise ValueError(f"No expense found with ID {id}")
