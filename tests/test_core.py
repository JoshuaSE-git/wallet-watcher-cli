import pytest
import datetime as dt
import wallet_watcher.core as core

from wallet_watcher._types import Expense, ExpenseField, Comparator
from wallet_watcher.constants import DEFAULT_CATEGORY, DEFAULT_DESCRIPTION
from decimal import Decimal
from typing import List


def test_add_expense(expense_list):
    new_expense: Expense = core.add_expense(
        expense_list,
        Decimal("5.00"),
        "snack",
        dt.datetime.fromisoformat("2025-06-08"),
        "Food",
    )

    assert new_expense == Expense(
        4, dt.datetime.fromisoformat("2025-06-08"), "Food", "snack", Decimal("5.00")
    )


def test_add_expense_defaults(expense_list):
    new_expense: Expense = core.add_expense(expense_list, Decimal("345"))

    assert new_expense == Expense(
        4,
        dt.datetime.today().date(),
        DEFAULT_CATEGORY,
        DEFAULT_DESCRIPTION,
        Decimal("345"),
    )


def test_add_expense_defaults_2(expense_list_2):
    new_expense: Expense = core.add_expense(
        expense_list_2, Decimal("21"), date=dt.datetime.fromisoformat("2025-06-13")
    )

    assert new_expense == Expense(
        9,
        dt.datetime.fromisoformat("2025-06-13"),
        DEFAULT_CATEGORY,
        DEFAULT_DESCRIPTION,
        Decimal("21"),
    )


def test_add_expense_invalid_amount():
    with pytest.raises(ValueError) as excinfo:
        core.add_expense([], Decimal("0.009"))

    assert excinfo.type is ValueError
    assert "Amount must be greater than 0.01" in str(excinfo.value)


def test_delete_expenses_matching_id(expense_list):
    strategy = core.filter_by_matching(ExpenseField.ID, 2)

    new_data: List[Expense] = core.delete_expenses(expense_list, strategy)

    correct_data: List[Expense] = [
        Expense(
            1,
            dt.datetime.fromisoformat("2025-06-01"),
            "Food",
            "Wendys",
            Decimal("10.23"),
        ),
        Expense(
            3,
            dt.datetime.fromisoformat("2025-06-03"),
            "School",
            "Textbooks",
            Decimal("20.50"),
        ),
    ]

    assert new_data == correct_data


def test_delete_expenses_matching_id_2(expense_list):
    strategy = core.filter_by_matching(ExpenseField.ID, *[2, 1])

    new_data: List[Expense] = core.delete_expenses(expense_list, strategy)

    correct_data: List[Expense] = [
        Expense(
            3,
            dt.datetime.fromisoformat("2025-06-03"),
            "School",
            "Textbooks",
            Decimal("20.50"),
        ),
    ]

    assert new_data == correct_data


def test_delete_expenses_matching_category(expense_list):
    strategy = core.filter_by_matching(ExpenseField.CATEGORY, *["Food", "Gaming"])

    new_data: List[Expense] = core.delete_expenses(expense_list, strategy)

    correct_data: List[Expense] = [
        Expense(
            3,
            dt.datetime.fromisoformat("2025-06-03"),
            "School",
            "Textbooks",
            Decimal("20.50"),
        ),
    ]

    assert new_data == correct_data


def test_delete_expenses_matching_date(expense_list):
    strategy = core.filter_by_matching(
        ExpenseField.DATE, dt.datetime.fromisoformat("2025-06-01")
    )

    new_data: List[Expense] = core.delete_expenses(expense_list, strategy)

    correct_data: List[Expense] = [
        Expense(
            3,
            dt.datetime.fromisoformat("2025-06-03"),
            "School",
            "Textbooks",
            Decimal("20.50"),
        ),
    ]

    assert new_data == correct_data


def test_delete_expenses_no_match(expense_list):
    strategy = core.filter_by_matching(ExpenseField.ID, 999)

    new_data: List[Expense] = core.delete_expenses(expense_list, strategy)

    assert new_data == expense_list


def test_delete_expenses_matching_combo(expense_list):
    strategy = core.filter_by_matching(
        ExpenseField.DATE, dt.datetime.fromisoformat("2025-06-01")
    )
    strategy2 = core.filter_by_matching(ExpenseField.CATEGORY, "Food")
    combo_strategy = core.combine_filters(strategy, strategy2)

    new_data: List[Expense] = core.delete_expenses(expense_list, combo_strategy)

    correct_data: List[Expense] = [
        Expense(
            2,
            dt.datetime.fromisoformat("2025-06-01"),
            "Gaming",
            "League",
            Decimal("50.00"),
        ),
        Expense(
            3,
            dt.datetime.fromisoformat("2025-06-03"),
            "School",
            "Textbooks",
            Decimal("20.50"),
        ),
    ]

    assert new_data == correct_data


@pytest.fixture
def expense_list():
    data: List[Expense] = [
        Expense(
            1,
            dt.datetime.fromisoformat("2025-06-01"),
            "Food",
            "Wendys",
            Decimal("10.23"),
        ),
        Expense(
            2,
            dt.datetime.fromisoformat("2025-06-01"),
            "Gaming",
            "League",
            Decimal("50.00"),
        ),
        Expense(
            3,
            dt.datetime.fromisoformat("2025-06-03"),
            "School",
            "Textbooks",
            Decimal("20.50"),
        ),
    ]

    return data


@pytest.fixture
def expense_list_2():
    data: List[Expense] = [
        Expense(
            1,
            dt.datetime.fromisoformat("2025-06-01"),
            "Food",
            "Wendys",
            Decimal("10.23"),
        ),
        Expense(
            8,
            dt.datetime.fromisoformat("2025-06-01"),
            "Gaming",
            "League",
            Decimal("50.00"),
        ),
        Expense(
            3,
            dt.datetime.fromisoformat("2025-06-03"),
            "School",
            "Textbooks",
            Decimal("20.50"),
        ),
    ]

    return data
