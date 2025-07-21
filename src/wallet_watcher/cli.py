import os
import sys
import csv
import argparse
import wallet_watcher.constants as const
import datetime as dt
from wallet_watcher._types import Expense, ExpenseField, Comparator
from typing import List, Dict
from decimal import Decimal, InvalidOperation


def main() -> None:
    return


def initialize_parsers():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add")
    add_parser.set_defaults(func=handle_add)
    add_parser.add_argument("amount", type=parse_amount)
    add_parser.add_argument("-d", "--date", type=parse_date)
    add_parser.add_argument("-c", "--category", type=parse_category)
    add_parser.add_argument("-s", "--desc", "--description", type=parse_description)

    delete_parser = subparsers.add_parser("delete")
    delete_parser.set_defaults(func=handle_delete)
    delete_parser.add_argument("-i", "--id", nargs="+", action="extend", type=parse_id)
    delete_parser.add_argument("-d", "--date", type=parse_date)
    delete_parser.add_argument("-c", "--category", type=parse_category)
    delete_parser.add_argument("-s", "--desc", "--description", type=parse_category)
    delete_parser.add_argument("--min-date", type=parse_date)
    delete_parser.add_argument("--max-date", type=parse_date)
    delete_parser.add_argument("--min-amount", type=parse_amount)
    delete_parser.add_argument("--max-amount", type=parse_amount)

    edit_parser = subparsers.add_parser("edit")
    edit_parser.set_defaults(func=handle_edit)
    edit_parser.add_argument("-i", "--id", required=True, type=parse_id)
    edit_parser.add_argument("-a", "--amount", type=parse_amount)
    edit_parser.add_argument("-d", "--date", type=parse_date)
    edit_parser.add_argument("-c", "--category", type=parse_category)
    edit_parser.add_argument("-s", "--desc", "--description", type=parse_description)

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(func=handle_list)
    list_parser.add_argument("-i", "--id", nargs="+", action="extend", type=parse_id)
    list_parser.add_argument("-d", "--date", type=parse_date)
    list_parser.add_argument("-c", "--category", type=parse_category)
    list_parser.add_argument("-s", "--desc", "--description", type=parse_category)
    list_parser.add_argument("--min-date", type=parse_date)
    list_parser.add_argument("--max-date", type=parse_date)
    list_parser.add_argument("--min-amount", type=parse_amount)
    list_parser.add_argument("--max-amount", type=parse_amount)


def handle_add(args):
    return


def handle_delete(args):
    return


def handle_edit(args):
    return


def handle_list(args):
    return


def parse_amount(amount: str) -> Decimal:
    return Decimal("0")


def parse_date(date: str) -> dt.date:
    return dt.datetime.now()


def parse_id(id: str) -> int:
    return 0


def parse_category(category: str) -> str:
    return ""


def parse_description(description: str) -> str:
    return ""


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


def load_csv(filepath: str) -> list[dict]:
    with open(filepath, "r", newline="") as csvfile:
        return list(csv.DictReader(csvfile))


def save_csv(filepath: str, data: list[dict]) -> None:
    with open(filepath, "w", newline="") as csvfile:
        csv_writer: csv.DictWriter = csv.DictWriter(csvfile, const.FIELD_NAMES)
        csv_writer.writeheader()
        csv_writer.writerows(data)


def append_csv(filepath: str, data: dict) -> None:
    with open(filepath, "a", newline="") as csvfile:
        csv_writer: csv.DictWriter = csv.DictWriter(csvfile, const.FIELD_NAMES)
        csv_writer.writerow(data)
