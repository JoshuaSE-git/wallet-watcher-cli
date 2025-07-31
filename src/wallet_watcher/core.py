import copy
import datetime as dt

from typing import List, Set, Union, Tuple
from decimal import ROUND_HALF_EVEN, Decimal
from wallet_watcher._types import Expense, FilterStrategy, Comparator, ExpenseField
from wallet_watcher.constants import DEFAULT_CATEGORY, DEFAULT_DESCRIPTION, FIELD_MAP


def add_expense(
    data: List[Expense],
    amount: Decimal,
    description: str | None = None,
    date: dt.date | None = None,
    category: str | None = None,
) -> Expense:
    amount = amount.quantize(Decimal(".01"), rounding=ROUND_HALF_EVEN)
    if amount < Decimal("0.01"):
        raise ValueError("Amount must be greater than 0.01")

    if not date:
        date = dt.datetime.today().date()
    if not category:
        category = DEFAULT_CATEGORY
    if not description:
        description = DEFAULT_DESCRIPTION
    id: int = _get_next_id(data)

    return Expense(id, date, category, description, amount)


def delete_expenses(
    data: List[Expense], filter_strategy: FilterStrategy
) -> Tuple[List[Expense], List[Expense]]:
    new_data = []
    deleted_data = []

    for expense in data:
        if not filter_strategy(expense):
            new_data.append(expense)
        else:
            deleted_data.append(expense)

    return new_data, deleted_data


def filter_expenses(
    data: List[Expense], filter_strategy: FilterStrategy
) -> List[Expense]:
    return [expense for expense in data if filter_strategy(expense)]


def filter_by_matching(
    field: ExpenseField, *values: Union[dt.date, Decimal, str, int]
) -> FilterStrategy:
    value_set: Set[Union[dt.date, Decimal, str, int]] = set(values)

    def strategy(expense: Expense) -> bool:
        return getattr(expense, FIELD_MAP[field]) in value_set

    return strategy


def filter_by_comparison(
    field: ExpenseField,
    comparator: Comparator,
    value: Union[dt.date, Decimal, None],
) -> FilterStrategy:
    def strategy(expense: Expense) -> bool:
        match comparator:
            case Comparator.LESS_THAN:
                return getattr(expense, FIELD_MAP[field]) < value
            case Comparator.LESS_THAN_EQUAL:
                return getattr(expense, FIELD_MAP[field]) <= value
            case Comparator.GREATER_THAN:
                return getattr(expense, FIELD_MAP[field]) > value
            case Comparator.GREATER_THAN_EQUAL:
                return getattr(expense, FIELD_MAP[field]) >= value
            case Comparator.EQUAL:
                return getattr(expense, FIELD_MAP[field]) == value

    return strategy


def filter_by_range(
    field: ExpenseField,
    start_val: Union[Union[dt.date, Decimal], None] = None,
    end_val: Union[Union[dt.date, Decimal], None] = None,
):
    default_field_ranges = {
        ExpenseField.AMOUNT: {"min": Decimal("-inf"), "max": Decimal("inf")},
        ExpenseField.DATE: {"min": dt.date.min, "max": dt.date.max},
    }

    if start_val is None:
        start_val = default_field_ranges[field]["min"]

    if end_val is None:
        end_val = default_field_ranges[field]["max"]

    min = filter_by_comparison(field, Comparator.GREATER_THAN_EQUAL, start_val)
    max = filter_by_comparison(field, Comparator.LESS_THAN_EQUAL, end_val)
    return combine_filters_all(min, max)


def combine_filters_all(*filters: FilterStrategy) -> FilterStrategy:
    def strategy(expense: Expense) -> bool:
        tests = []
        for filter_strategy in filters:
            if not filter_strategy(expense):
                tests.append(False)
            else:
                tests.append(True)

        return all(tests)

    return strategy


def combine_filters_any(*filters: FilterStrategy) -> FilterStrategy:
    def strategy(expense: Expense) -> bool:
        tests = []
        for filter_strategy in filters:
            if not filter_strategy(expense):
                tests.append(False)
            else:
                tests.append(True)

        return any(tests)

    return strategy


def modify_expense(
    data: List[Expense],
    id: int,
    new_date: dt.date | None = None,
    new_category: str | None = None,
    new_description: str | None = None,
    new_amount: Decimal | None = None,
) -> Tuple[List[Expense], Expense, Expense]:
    data_copy = [copy.copy(expense) for expense in data]

    for expense in data_copy:
        if expense.id == id:
            before = expense
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
            after = expense
            return data_copy, before, after

    raise ValueError(f"No expense found with ID {id}")


def calculate_total(data: List[Expense]) -> float:
    total = 0
    for expense in data:
        total += expense.amount

    return float(total)


def _get_next_id(data: List[Expense]) -> int:
    return max((expense.id for expense in data), default=0) + 1
