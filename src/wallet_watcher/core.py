import copy
import datetime as dt
from typing import List, Union, Tuple, Dict
from decimal import ROUND_HALF_EVEN, Decimal

from wallet_watcher._types import Expense, FilterStrategy, Comparator, ExpenseField
from wallet_watcher.constants import DEFAULT_CATEGORY, DEFAULT_DESCRIPTION, FIELD_MAP


def add_expense(
    data: List[Expense],
    expense_amount: Decimal,
    description: str | None = None,
    date: dt.date | None = None,
    category: str | None = None,
) -> Expense:
    expense_amount = expense_amount.quantize(Decimal(".01"), rounding=ROUND_HALF_EVEN)
    if expense_amount < Decimal("0.01"):
        raise ValueError("Amount must be greater than 0.01")

    if not date:
        date = dt.datetime.today().date()
    if not category:
        category = DEFAULT_CATEGORY
    if not description:
        description = DEFAULT_DESCRIPTION
    id = _get_next_id(data)

    return Expense(id, date, category, description, expense_amount)


def delete_expenses(
    data: List[Expense], filter_strategy: FilterStrategy
) -> Tuple[List[Expense], List[Expense]]:
    modified_data = []
    deleted_data = []

    for expense in data:
        if not filter_strategy(expense):
            modified_data.append(expense)
        else:
            deleted_data.append(expense)

    return modified_data, deleted_data


def filter_expenses(
    data: List[Expense], filter_strategy: FilterStrategy
) -> List[Expense]:
    return [expense for expense in data if filter_strategy(expense)]


def filter_by_matching(
    field: ExpenseField, *values: Union[dt.date, Decimal, str, int]
) -> FilterStrategy:
    value_set = set(values)

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
    start_value: Union[Union[dt.date, Decimal], None] = None,
    end_value: Union[Union[dt.date, Decimal], None] = None,
):
    default_field_ranges = {
        ExpenseField.AMOUNT: {"min": Decimal("-inf"), "max": Decimal("inf")},
        ExpenseField.DATE: {"min": dt.date.min, "max": dt.date.max},
    }

    if start_value is None:
        start_value = default_field_ranges[field]["min"]
    if end_value is None:
        end_value = default_field_ranges[field]["max"]

    min_value = filter_by_comparison(field, Comparator.GREATER_THAN_EQUAL, start_value)
    max_value = filter_by_comparison(field, Comparator.LESS_THAN_EQUAL, end_value)

    return combine_filters_all(min_value, max_value)


def combine_filters_all(*filters: FilterStrategy) -> FilterStrategy:
    def strategy(expense: Expense) -> bool:
        results = []
        for filter_strategy in filters:
            if not filter_strategy(expense):
                results.append(False)
            else:
                results.append(True)

        return all(results)

    return strategy


def combine_filters_any(*filters: FilterStrategy) -> FilterStrategy:
    def strategy(expense: Expense) -> bool:
        results = []
        for filter_strategy in filters:
            if not filter_strategy(expense):
                results.append(False)
            else:
                results.append(True)

        return any(results)

    return strategy


def modify_expense(
    data: List[Expense],
    id: int,
    new_date: dt.date | None = None,
    new_category: str | None = None,
    new_description: str | None = None,
    new_amount: Decimal | None = None,
) -> Tuple[List[Expense], Dict]:
    data = [copy.copy(expense) for expense in data]

    target_expense = None
    for expense in data:
        if expense.id == id:
            target_expense = expense

    if not target_expense:
        raise ValueError(f"No expense found with ID {id}")

    changes = {}
    if new_date is not None:
        changes["date"] = (target_expense.date, new_date)
        target_expense.date = new_date
    if new_category is not None:
        changes["category"] = (target_expense.category[:16], new_category[:16])
        target_expense.category = new_category
    if new_description is not None:
        changes["description"] = (target_expense.description[:16], new_description[:16])
        target_expense.description = new_description
    if new_amount is not None:
        if new_amount < Decimal("0.01"):
            raise ValueError("Amount must be greater than 0.01")
        new_amount = Decimal(new_amount)
        new_amount = new_amount.quantize(Decimal(".01"), rounding=ROUND_HALF_EVEN)
        changes["amount"] = (target_expense.amount, new_amount)
        target_expense.amount = new_amount

    return data, changes


def calculate_total(data: List[Expense]) -> Dict:
    totals = {"total": 0, "category": {}}

    for expense in data:
        totals["total"] += expense.amount
        totals["category"][expense.category] = (
            totals["category"].get(expense.category, 0) + expense.amount
        )

    return totals


def _get_next_id(data: List[Expense]) -> int:
    return max((expense.id for expense in data), default=0) + 1
