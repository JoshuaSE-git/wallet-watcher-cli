import os
import sys
import csv
import argparse
import wallet_watcher.constants as const
import wallet_watcher.core as core
import wallet_watcher.adapter as adapter
import wallet_watcher.render as render
import datetime as dt
from rich.console import Console
from wallet_watcher._types import Expense, ExpenseField
from typing import List, Dict
from decimal import Decimal


def main() -> None:
    initialize_user_data()
    parser = initialize_parsers()
    args = parser.parse_args()
    console = Console()
    if hasattr(args, "func"):
        args.func(args, console)

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
    delete_parser.add_argument(
        "-d", "--date", nargs="+", action="extend", type=parse_date, default=None
    )
    delete_parser.add_argument(
        "-c",
        "--category",
        nargs="+",
        action="extend",
        type=parse_category,
        default=None,
    )
    delete_parser.add_argument(
        "-s",
        "--description",
        nargs="+",
        action="extend",
        type=parse_description,
        default=None,
    )
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
    list_parser.add_argument(
        "-d", "--date", nargs="+", action="extend", type=parse_date, default=None
    )
    list_parser.add_argument(
        "-c",
        "--category",
        nargs="+",
        action="extend",
        type=parse_category,
        default=None,
    )
    list_parser.add_argument(
        "-s",
        "--description",
        nargs="+",
        action="extend",
        type=parse_description,
        default=None,
    )

    list_parser.add_argument("--min-date", type=parse_date, default=None)
    list_parser.add_argument("--max-date", type=parse_date, default=None)
    list_parser.add_argument("--min-amount", type=parse_amount, default=None)
    list_parser.add_argument("--max-amount", type=parse_amount, default=None)

    list_parser.add_argument(
        "--sort-by", choices=["date", "id", "amount"], default="date"
    )
    list_parser.add_argument("--desc", action="store_true")

    return parser


def handle_add(args, console):
    path = get_user_data()
    data = adapter.convert_csv_to_expenses(load_csv(path))
    new_expense: Expense = core.add_expense(
        data, args.amount, args.description, args.date, args.category
    )
    new_csv_row: Dict[str, str] = adapter.convert_expense_to_csv_row(new_expense)

    append_csv(path, new_csv_row)

    console.print()
    console.print("[bold green]✅ Expense Added![/]")
    console.print(f"[bold white]ID:[/]          {new_expense.id}")
    console.print(f"[bold white]Date:[/]        {new_expense.date}")
    console.print(f"[bold white]Category:[/]    [cyan]{new_expense.category}[/]")
    console.print(f"[bold white]Description:[/] {new_expense.description}")
    console.print(
        f"[bold white]Amount:[/]      [bold green]${new_expense.amount:.2f}[/]"
    )
    console.print()


def group_filters(args):
    filters = {
        "matching": {
            ExpenseField.ID: args.id,
            ExpenseField.DATE: args.date,
            ExpenseField.CATEGORY: args.category,
            ExpenseField.DESCRIPTION: args.description,
        },
        "range": {
            ExpenseField.DATE: {
                "min": args.min_date,
                "max": args.max_date,
            },
            ExpenseField.AMOUNT: {
                "min": args.min_amount,
                "max": args.max_amount,
            },
        },
    }

    return filters


def handle_delete(args, console):
    filters = group_filters(args)
    strategies = []
    for match_filter, value in filters["matching"].items():
        if value is not None:
            strategies.append(core.filter_by_matching(match_filter, *value))
    for range_filter, value in filters["range"].items():
        if value["min"] is None and value["max"] is None:
            continue
        strategies.append(
            core.filter_by_range(range_filter, value["min"], value["max"])
        )
    final_strategy = core.combine_filters_any(*strategies)
    path = get_user_data()

    data = adapter.convert_csv_to_expenses(load_csv(path))
    after_data, deleted_data = core.delete_expenses(data, final_strategy)
    csv = adapter.convert_expenses_to_csv(after_data)
    save_csv(path, csv)

    console.print(render.render_table(deleted_data, title="Deleted Expenses"))
    console.print(render.render_table(after_data, title="Remaining Expenses"))

    return


def handle_edit(args, console):
    path = get_user_data()
    data = adapter.convert_csv_to_expenses(load_csv(path))
    after_data, before, after = core.modify_expense(
        data,
        id=args.id,
        new_amount=args.amount if args.amount else None,
        new_date=args.date if args.date else None,
        new_category=args.category if args.category else None,
        new_description=args.description if args.description else None,
    )
    csv = adapter.convert_expenses_to_csv(after_data)
    save_csv(path, csv)

    before_table = render.render_table([before], title="Before")
    after_table = render.render_table([after], title="After")

    console.print(before_table)
    console.print(after_table)

    return


def handle_list(args, console):
    filters = group_filters(args)
    strategies = []
    for match_filter, value in filters["matching"].items():
        if value is not None:
            strategies.append(core.filter_by_matching(match_filter, *value))
    for range_filter, value in filters["range"].items():
        if value["min"] is None and value["max"] is None:
            continue
        strategies.append(
            core.filter_by_range(range_filter, value["min"], value["max"])
        )
    final_strategy = core.combine_filters_all(*strategies)
    path = get_user_data()

    data = adapter.convert_csv_to_expenses(load_csv(path))
    after_data: List[Expense] = core.filter_expenses(data, final_strategy)

    key_map = {
        "date": lambda x: x.date,
        "amount": lambda x: x.amount,
        "id": lambda x: x.id,
    }

    sorted_data = sorted(after_data, key=key_map[args.sort_by], reverse=args.desc)
    console.print(render.render_table(sorted_data))

    total = core.calculate_total(sorted_data)
    entry_count = len(sorted_data)
    total_entries = len(data)
    console.print(f"[bold white]Filtered Total:[/] [bold green]${total:.2f}[/]")
    console.print(
        f"[bold white]Entries:[/] [bold yellow]{entry_count}/{total_entries}[/]"
    )
    console.print()


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
        parsed_date = dt.datetime.strptime(date, const.DATE_FORMAT_STRING).date()
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


def get_user_data() -> str:
    return os.path.join(get_os_data_path(), "wallet-watcher/finances.csv")


def get_os_data_path() -> str:
    user_os: str = sys.platform
    if user_os == const.LINUX:
        return os.environ.get(
            const.ENV_XDG_DATA_HOME, os.path.expanduser(const.LINUX_APPDATA_PATH)
        )
    elif user_os == const.MACOS:
        return os.path.expanduser(const.MACOS_APPDATA_PATH)
    elif user_os.startswith("win"):
        return os.environ.get(
            const.ENV_LOCAL_APPDATA, os.path.expanduser(const.WINDOWS_APPDATA_PATH)
        )
    else:
        raise ValueError("Unsupported Operating System")


def initialize_user_data() -> None:
    app_data_dir_path: str = os.path.join(get_os_data_path(), const.APP_DIRECTORY_NAME)
    os.makedirs(app_data_dir_path, mode=0o700, exist_ok=True)

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
