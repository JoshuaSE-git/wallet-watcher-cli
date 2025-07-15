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
        10,
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
    combo_strategy = core.combine_filters_any(strategy, strategy2)

    new_data: List[Expense] = core.delete_expenses(expense_list, combo_strategy)

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


# wallet delete --max-amount 20.50
def test_delete_expenses_comparison_amount_max(expense_list):
    strategy = core.filter_by_comparison(
        ExpenseField.AMOUNT, Comparator.LESS_THAN_EQUAL, Decimal("20.50")
    )
    new_data: List[Expense] = core.delete_expenses(expense_list, strategy)
    correct_data: List[Expense] = [
        Expense(
            2,
            dt.datetime.fromisoformat("2025-06-01"),
            "Gaming",
            "League",
            Decimal("50.00"),
        ),
    ]

    assert new_data == correct_data


# wallet delete min-amount 20.50
def test_delete_expenses_comparison_amount_min(expense_list):
    strategy = core.filter_by_comparison(
        ExpenseField.AMOUNT, Comparator.GREATER_THAN_EQUAL, Decimal("20.50")
    )
    new_data: List[Expense] = core.delete_expenses(expense_list, strategy)
    correct_data: List[Expense] = [
        Expense(
            1,
            dt.datetime.fromisoformat("2025-06-01"),
            "Food",
            "Wendys",
            Decimal("10.23"),
        ),
    ]

    assert new_data == correct_data


# wallete delete --max-date 2025-06-02
def test_delete_expenses_comparison_date_max(expense_list):
    strategy = core.filter_by_comparison(
        ExpenseField.DATE,
        Comparator.LESS_THAN_EQUAL,
        dt.datetime.fromisoformat("2025-06-02"),
    )
    data = core.delete_expenses(expense_list, strategy)
    correct_data: List[Expense] = [
        Expense(
            3,
            dt.datetime.fromisoformat("2025-06-03"),
            "School",
            "Textbooks",
            Decimal("20.50"),
        ),
    ]

    assert data == correct_data


# wallet delete --min-date 2025-06-02
def test_delete_expenses_comparison_date_min(expense_list):
    strategy = core.filter_by_comparison(
        ExpenseField.DATE,
        Comparator.GREATER_THAN_EQUAL,
        dt.datetime.fromisoformat("2025-06-02"),
    )
    data = core.delete_expenses(expense_list, strategy)
    correct_data = [
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
    ]

    assert data == correct_data


# wallet delete --min-date 2025-06-02 --min-amount 20.00
def test_delete_expenses_comparison_combo(expense_list):
    strategy1 = core.filter_by_comparison(
        ExpenseField.DATE,
        Comparator.GREATER_THAN_EQUAL,
        dt.datetime.fromisoformat("2025-06-02"),
    )
    strategy2 = core.filter_by_comparison(
        ExpenseField.AMOUNT, Comparator.GREATER_THAN_EQUAL, Decimal("20.00")
    )
    strategy = core.combine_filters_any(*[strategy1, strategy2])
    data = core.delete_expenses(expense_list, strategy)
    correct_data = [
        Expense(
            1,
            dt.datetime.fromisoformat("2025-06-01"),
            "Food",
            "Wendys",
            Decimal("10.23"),
        ),
    ]

    assert data == correct_data


# wallet list --id 1 2
def test_list_expenses_matching_id(expense_list):
    strategy = core.filter_by_matching(ExpenseField.ID, *[1, 2])
    data = core.filter_expenses(expense_list, strategy)
    correct_data = [
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
    ]

    assert data == correct_data


# wallet list --category "Food"
def test_list_expenses_matching_category(expense_list):
    strategy = core.filter_by_matching(ExpenseField.CATEGORY, "Food")
    data = core.filter_expenses(expense_list, strategy)
    correct_data = [
        Expense(
            1,
            dt.datetime.fromisoformat("2025-06-01"),
            "Food",
            "Wendys",
            Decimal("10.23"),
        ),
    ]

    assert data == correct_data


# wallet list --date 2025-06-03
def test_list_expenses_matching_date(expense_list):
    strategy = core.filter_by_matching(
        ExpenseField.DATE, dt.datetime.fromisoformat("2025-06-03")
    )
    data = core.filter_expenses(expense_list, strategy)
    correct_data = [
        Expense(
            3,
            dt.datetime.fromisoformat("2025-06-03"),
            "School",
            "Textbooks",
            Decimal("20.50"),
        ),
    ]

    assert data == correct_data


# wallet list --amount 20.5 50
def test_list_expenses_matching_amount(expense_list):
    strategy = core.filter_by_matching(
        ExpenseField.AMOUNT, Decimal("20.5"), Decimal("50")
    )
    data = core.filter_expenses(expense_list, strategy)
    correct_data = [
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

    assert data == correct_data


# wallet list --category "Food" "Gaming" --max-amount 20
def test_list_expenses_matching_combo(expense_list):
    strategy1 = core.filter_by_matching(ExpenseField.CATEGORY, *["Food", "Gaming"])
    strategy2 = core.filter_by_comparison(
        ExpenseField.AMOUNT, Comparator.LESS_THAN_EQUAL, Decimal("20")
    )
    strategy = core.combine_filters_all(*[strategy1, strategy2])
    data = core.filter_expenses(expense_list, strategy)
    correct_data = [
        Expense(
            1,
            dt.datetime.fromisoformat("2025-06-01"),
            "Food",
            "Wendys",
            Decimal("10.23"),
        ),
    ]

    assert data == correct_data


# wallet list --min-amount 20 --max-amount 20.5
def test_list_expenses_comparison_amount(expense_list):
    strategy1 = core.filter_by_comparison(
        ExpenseField.AMOUNT, Comparator.GREATER_THAN_EQUAL, Decimal("20")
    )
    strategy2 = core.filter_by_comparison(
        ExpenseField.AMOUNT, Comparator.LESS_THAN_EQUAL, Decimal("20.5")
    )
    strategy = core.combine_filters_all(*[strategy1, strategy2])
    data = core.filter_expenses(expense_list, strategy)
    correct_data = [
        Expense(
            3,
            dt.datetime.fromisoformat("2025-06-03"),
            "School",
            "Textbooks",
            Decimal("20.50"),
        ),
    ]

    assert data == correct_data


# wallet list --min-date 2025-01-01 --max-date 2025-06-01
def test_list_expenses_comparison_date(expense_list):
    strategy1 = core.filter_by_comparison(
        ExpenseField.DATE,
        Comparator.GREATER_THAN_EQUAL,
        dt.datetime.fromisoformat("2025-01-01"),
    )
    strategy2 = core.filter_by_comparison(
        ExpenseField.DATE,
        Comparator.LESS_THAN_EQUAL,
        dt.datetime.fromisoformat("2025-06-01"),
    )
    strategy = core.combine_filters_all(*[strategy1, strategy2])
    data = core.filter_expenses(expense_list, strategy)
    correct_data = [
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
    ]

    assert data == correct_data


# wallet list --min-date 2025-01-01 --max-date 2025-06-01 --category "Food"
# "Gaming" --max-amount 6
def test_list_expenses_combo(expense_list_2):
    strategy1 = core.filter_by_comparison(
        ExpenseField.DATE,
        Comparator.GREATER_THAN_EQUAL,
        dt.datetime.fromisoformat("2025-01-01"),
    )
    strategy2 = core.filter_by_comparison(
        ExpenseField.DATE,
        Comparator.LESS_THAN_EQUAL,
        dt.datetime.fromisoformat("2025-06-01"),
    )
    strategy3 = core.filter_by_matching(ExpenseField.CATEGORY, *["Food", "Gaming"])
    strategy4 = core.filter_by_comparison(
        ExpenseField.AMOUNT, Comparator.LESS_THAN_EQUAL, Decimal("6")
    )
    strategy = core.combine_filters_all(*[strategy1, strategy2, strategy3, strategy4])
    data = core.filter_expenses(expense_list_2, strategy)
    correct_data = [
        Expense(
            1,
            dt.datetime.fromisoformat("2025-04-01"),
            "Food",
            "Arbys",
            Decimal("5.23"),
        ),
        Expense(
            9,
            dt.datetime.fromisoformat("2025-05-09"),
            "Gaming",
            "N/A",
            Decimal("3"),
        ),
    ]

    assert data == correct_data


# wallet delete --min-date 2025-06-01 --max-date 2025-07-01 --category "General"
# "Gaming" --max-amount 1
def test_delete_expenses_combo(expense_list_2):
    strategy1 = core.filter_by_comparison(
        ExpenseField.DATE,
        Comparator.GREATER_THAN_EQUAL,
        dt.datetime.fromisoformat("2025-06-01"),
    )
    strategy2 = core.filter_by_comparison(
        ExpenseField.DATE,
        Comparator.LESS_THAN_EQUAL,
        dt.datetime.fromisoformat("2025-07-01"),
    )

    strategy1_2 = core.combine_filters_all(strategy1, strategy2)
    strategy3 = core.filter_by_matching(ExpenseField.CATEGORY, *["General", "Gaming"])
    strategy4 = core.filter_by_comparison(
        ExpenseField.AMOUNT, Comparator.LESS_THAN_EQUAL, Decimal("1")
    )
    strategy = core.combine_filters_any(*[strategy1_2, strategy3, strategy4])
    data = core.delete_expenses(expense_list_2, strategy)
    correct_data = [
        Expense(
            1,
            dt.datetime.fromisoformat("2025-04-01"),
            "Food",
            "Arbys",
            Decimal("5.23"),
        ),
    ]

    assert data == correct_data


# wallet edit --id 1 --amount 100
def test_modify_expenses_amount(expense_list):
    data = core.modify_expense(expense_list, 1, new_amount=Decimal("100"))
    correct_data = [
        Expense(
            1,
            dt.datetime.fromisoformat("2025-06-01"),
            "Food",
            "Wendys",
            Decimal("100"),
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

    assert data == correct_data


# wallet edit --id 2 --amount 100 --date 2025-06-02 --
def test_modify_expenses_all(expense_list):
    data = core.modify_expense(
        expense_list,
        1,
        new_amount=Decimal("100"),
        new_date=dt.datetime.fromisoformat("2025-06-02"),
        new_category="Gaming",
        new_description="N/A",
    )
    correct_data = [
        Expense(
            1,
            dt.datetime.fromisoformat("2025-06-02"),
            "Gaming",
            "N/A",
            Decimal("100"),
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

    assert data == correct_data


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
            dt.datetime.fromisoformat("2025-04-01"),
            "Food",
            "Arbys",
            Decimal("5.23"),
        ),
        Expense(
            3,
            dt.datetime.fromisoformat("2025-05-09"),
            "General",
            "N/A",
            Decimal("1"),
        ),
        Expense(
            9,
            dt.datetime.fromisoformat("2025-05-09"),
            "Gaming",
            "N/A",
            Decimal("3"),
        ),
        Expense(
            3,
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
            4,
            dt.datetime.fromisoformat("2025-06-03"),
            "School",
            "Textbooks",
            Decimal("2"),
        ),
    ]

    return data
