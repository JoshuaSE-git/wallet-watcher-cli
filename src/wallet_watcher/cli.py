import os
import sys
import csv
import argparse
import wallet_watcher.constants as const
import wallet_watcher.core as core
import wallet_watcher.adapter as adapter
import datetime as dt
from wallet_watcher._types import Expense, ExpenseField
from typing import List, Dict
from decimal import Decimal


def main() -> None:
    initialize_user_data()
    parser = initialize_parsers()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)

    return


def initialize_parsers():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add")
    add_parser.set_defaults(func=handle_add)
    add_parser.add_argument("amount", type=parse_amount)
    add_parser.add_argument("-d", "--date", type=parse_date, default=None)
    add_parser.add_argument("-c", "--category", type=parse_category, default=None)
    add_parser.add_argument("-s", "--description", type=parse_description, default=None)

    delete_parser = subparsers.add_parser("delete")
    delete_parser.set_defaults(func=handle_delete)
    delete_parser.add_argument(
        "-i", "--id", nargs="+", action="extend", type=parse_id, default=None
    )
    delete_parser.add_argument("-d", "--date", type=parse_date, default=None)
    delete_parser.add_argument("-c", "--category", type=parse_category, default=None)
    delete_parser.add_argument("-s", "--description", type=parse_category, default=None)
    delete_parser.add_argument("--min-date", type=parse_date, default=None)
    delete_parser.add_argument("--max-date", type=parse_date, default=None)
    delete_parser.add_argument("--min-amount", type=parse_amount, default=None)
    delete_parser.add_argument("--max-amount", type=parse_amount, default=None)

    edit_parser = subparsers.add_parser("edit")
    edit_parser.set_defaults(func=handle_edit)
    edit_parser.add_argument("-i", "--id", required=True, type=parse_id)
    edit_parser.add_argument("-a", "--amount", type=parse_amount, default=None)
    edit_parser.add_argument("-d", "--date", type=parse_date, default=None)
    edit_parser.add_argument("-c", "--category", type=parse_category, default=None)
    edit_parser.add_argument(
        "-s", "--description", type=parse_description, default=None
    )

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(func=handle_list)
    list_parser.add_argument(
        "-i", "--id", nargs="+", action="extend", type=parse_id, default=None
    )
    list_parser.add_argument("-d", "--date", type=parse_date, default=None)
    list_parser.add_argument("-c", "--category", type=parse_category, default=None)
    list_parser.add_argument("-s", "--description", type=parse_category, default=None)
    list_parser.add_argument("--min-date", type=parse_date, default=None)
    list_parser.add_argument("--max-date", type=parse_date, default=None)
    list_parser.add_argument("--min-amount", type=parse_amount, default=None)
    list_parser.add_argument("--max-amount", type=parse_amount, default=None)

    return parser


def handle_add(args):
    print("in handle_add")
    path = get_os_data_path() + "/wallet-watcher/finances.csv"
    data = adapter.convert_csv_to_expenses(load_csv(path))
    new_expense: Expense = core.add_expense(
        data, args.amount, args.description, args.date, args.category
    )
    new_csv_row: Dict[str, str] = adapter.convert_expense_to_csv_row(new_expense)

    append_csv(path, new_csv_row)

    return


def group_filters(args):
    arg_dict = vars(args)
    print(arg_dict)
    filters = {
        "matching": {
            ExpenseField.ID: args.id,
            ExpenseField.DATE: args.date,
            ExpenseField.CATEGORY: args.category,
            ExpenseField.DESCRIPTION: args.description,
        },
        "range": {
            ExpenseField.DATE: {
                "min": arg_dict["min_date"],
                "max": arg_dict["max_date"],
            },
            ExpenseField.AMOUNT: {
                "min": arg_dict["min_amount"],
                "max": arg_dict["max_amount"],
            },
        },
    }

    return filters


def handle_delete(args):
    filters = group_filters(args)
    strategies = []
    for match_filter, value in filters["matching"].items():
        if value is not None:
            strategies.append(core.filter_by_matching(match_filter, *value))
    for range_filter, value in filters["range"].items():
        strategies.append(
            core.filter_by_range(range_filter, value["min"], value["max"])
        )
    final_strategy = core.combine_filters_any(*strategies)
    path = get_os_data_path() + "/wallet-watcher/finances.csv"

    data = adapter.convert_csv_to_expenses(load_csv(path))
    after_data: List[Expense] = core.delete_expenses(data, final_strategy)
    csv = adapter.convert_expenses_to_csv(after_data)
    save_csv(path, csv)

    return


def handle_edit(args):
    return


def handle_list(args):
    return


def parse_amount(amount: str) -> Decimal:
    parsed_amount: Decimal = Decimal("0")
    try:
        parsed_amount = Decimal(amount)
    except Exception:
        raise argparse.ArgumentTypeError(f"'{amount}' is not a valid amount.")

    return parsed_amount


def parse_date(date: str) -> dt.date:
    parsed_date = dt.datetime.now()
    try:
        parsed_date = dt.datetime.strptime(date, const.DATE_FORMAT_STRING)
    except Exception:
        raise argparse.ArgumentTypeError(
            f"'{date}' is not a valid date (Use YYYY-MM-DD)."
        )

    return parsed_date


def parse_id(id: str) -> int:
    parsed_id = 0
    try:
        parsed_id = int(id)
    except Exception:
        raise argparse.ArgumentTypeError(f"'{id}' is not a valid id.")

    return parsed_id


def parse_category(category: str) -> str:
    if len(category) > 20:
        raise argparse.ArgumentTypeError(
            f"Category must be less than 20 characters: {category}"
        )

    return category


def parse_description(description: str) -> str:
    if len(description) > 50:
        raise argparse.ArgumentTypeError(
            f"Desscription must be less than 50 characters: {description}"
        )

    return description


def get_os_data_path() -> str:
    user_os: str = sys.platform
    if user_os == const.LINUX:
        return os.environ.get(
            const.ENV_XDG_DATA_HOME, os.path.expanduser(const.LINUX_APPDATA_PATH)
        )
    elif user_os == const.MACOS:
        return os.path.expanduser(const.MACOS_APPDATA_PATH)
    elif user_os == const.WINDOWS:
        return os.environ.get(
            const.ENV_LOCAL_APPDATA, os.path.expanduser(const.WINDOWS_APPDATA_PATH)
        )
    else:
        raise ValueError("Unsupported Operating System")


def initialize_user_data() -> None:
    app_data_dir_path: str = os.path.join(get_os_data_path(), const.APP_DIRECTORY_NAME)
    if not os.path.exists(app_data_dir_path):
        os.mkdir(app_data_dir_path, mode=0o600)

    user_data_path: str = os.path.join(app_data_dir_path, const.USER_DATA_FILENAME)
    if not os.path.exists(user_data_path):
        with open(user_data_path, "w", newline="") as csvfile:
            csv_writer: csv.DictWriter = csv.DictWriter(csvfile, const.FIELD_NAMES)
            csv_writer.writeheader()


def load_csv(filepath: str) -> List[Dict[str, str]]:
    with open(filepath, "r", newline="") as csvfile:
        return list(csv.DictReader(csvfile))


def save_csv(filepath: str, data: List[Dict[str, str]]) -> None:
    with open(filepath, "w", newline="") as csvfile:
        csv_writer: csv.DictWriter = csv.DictWriter(csvfile, const.FIELD_NAMES)
        csv_writer.writeheader()
        csv_writer.writerows(data)


def append_csv(filepath: str, data: Dict[str, str]) -> None:
    with open(filepath, "a", newline="") as csvfile:
        csv_writer: csv.DictWriter = csv.DictWriter(csvfile, const.FIELD_NAMES)
        csv_writer.writerow(data)


if __name__ == "__main__":
    main()
