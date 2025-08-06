import os
import sys
import csv
import argparse
import datetime as dt
from decimal import Decimal
from typing import List, Dict

from rich.console import Console

import wallet_watcher.constants as const
import wallet_watcher.core as core
import wallet_watcher.adapter as adapter
import wallet_watcher.render as render
from wallet_watcher._types import Expense, ExpenseField


def main() -> None:
    initialize_user_data()
    parser = initialize_parsers()
    parsed_args = parser.parse_args()
    console = Console()

    if hasattr(parsed_args, "func"):
        parsed_args.func(parsed_args, console)
    else:
        console.print("[bold green]💰 wallet[/] — Command-line Expense Tracker\n")
        console.print("[bold white]Usage:[/] wallet \\[command] \\[options]\n")
        console.print("[bold white]Common Commands:[/]")
        console.print("  [cyan]add[/]       Add a new expense entry")
        console.print("  [cyan]list[/]      View expenses with optional filters")
        console.print(
            "  [cyan]delete[/]    Remove expenses by ID, category, date, etc."
        )
        console.print("  [cyan]edit[/]      Modify an existing expense")
        console.print("  [cyan]undo[/]      Revert recent changes")
        console.print("  [cyan]summary[/]   Show category breakdown and stats\n")
        console.print("Run '[bold]wallet \\[command] --help[/]' for more info.")


def initialize_parsers():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add")
    add_parser.set_defaults(func=handle_add)
    add_parser.add_argument(
        "amount", type=parse_amount, help="Amount in dollars (e.g. 25.99)"
    )
    add_parser.add_argument(
        "-d",
        "--date",
        type=parse_date,
        default=None,
        help="Date of expense (YYYY-MM-DD)",
    )
    add_parser.add_argument(
        "-c",
        "--category",
        type=parse_category,
        default=None,
        help="Expense category (e.g. 'Food')",
    )
    add_parser.add_argument(
        "-s",
        "--description",
        type=parse_description,
        default=None,
        help="Expense description",
    )

    delete_parser = subparsers.add_parser("delete")
    delete_parser.set_defaults(func=handle_delete)
    delete_parser.add_argument(
        "-i",
        "--id",
        nargs="+",
        action="extend",
        type=parse_id,
        default=None,
        help="One or more Expense IDs to delete",
    )
    delete_parser.add_argument(
        "-d",
        "--date",
        nargs="+",
        action="extend",
        type=parse_date,
        default=None,
        help="Delete by one or more dates",
    )
    delete_parser.add_argument(
        "-c",
        "--category",
        nargs="+",
        action="extend",
        type=parse_category,
        default=None,
        help="Delete by one or more categories",
    )
    delete_parser.add_argument(
        "-s",
        "--description",
        nargs="+",
        action="extend",
        type=parse_description,
        default=None,
        help="Delete by description",
    )
    delete_parser.add_argument(
        "--min-date", type=parse_date, default=None, help="Delete by minimum date range"
    )
    delete_parser.add_argument(
        "--max-date", type=parse_date, default=None, help="Delete by maximum date range"
    )
    delete_parser.add_argument(
        "--min-amount",
        type=parse_amount,
        default=None,
        help="Delete by minimum amount range",
    )
    delete_parser.add_argument(
        "--max-amount",
        type=parse_amount,
        default=None,
        help="Delete by maximum amount range",
    )

    edit_parser = subparsers.add_parser("edit")
    edit_parser.set_defaults(func=handle_edit)
    edit_parser.add_argument(
        "-i", "--id", required=True, type=parse_id, help="ID of target expense"
    )
    edit_parser.add_argument(
        "-a",
        "--amount",
        type=parse_amount,
        default=None,
        help="Modify amount in dollars (e.g. 25.99)",
    )
    edit_parser.add_argument(
        "-d", "--date", type=parse_date, default=None, help="Modify date (YYYY-MM-DD)"
    )
    edit_parser.add_argument(
        "-c", "--category", type=parse_category, default=None, help="Modify category"
    )
    edit_parser.add_argument(
        "-s",
        "--description",
        type=parse_description,
        default=None,
        help="Modify description",
    )

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(func=handle_list)
    list_parser.add_argument(
        "-i",
        "--id",
        nargs="+",
        action="extend",
        type=parse_id,
        default=None,
        help="Filter by one or more IDs",
    )
    list_parser.add_argument(
        "-d",
        "--date",
        nargs="+",
        action="extend",
        type=parse_date,
        default=None,
        help="Filter by one or more dates (YYYY-MM-DD)",
    )
    list_parser.add_argument(
        "-c",
        "--category",
        nargs="+",
        action="extend",
        type=parse_category,
        default=None,
        help="Filter by one or more categories",
    )
    list_parser.add_argument(
        "-s",
        "--description",
        nargs="+",
        action="extend",
        type=parse_description,
        default=None,
        help="Filter by description",
    )

    list_parser.add_argument(
        "--min-date", type=parse_date, default=None, help="Filter by minimum date range"
    )
    list_parser.add_argument(
        "--max-date", type=parse_date, default=None, help="Filter by maximum date range"
    )
    list_parser.add_argument(
        "--min-amount",
        type=parse_amount,
        default=None,
        help="Filter by minimum amount range",
    )
    list_parser.add_argument(
        "--max-amount",
        type=parse_amount,
        default=None,
        help="Filter by maximum amount range",
    )

    list_parser.add_argument(
        "--sort-by",
        choices=["date", "id", "amount"],
        default="date",
        help="Sort by date, id, or amount (default ascending)",
    )
    list_parser.add_argument(
        "--desc", action="store_true", help="Sort in descending order"
    )

    return parser


def generate_strategy_list(args):
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

    return strategies


def handle_delete(args, console):
    strategies = generate_strategy_list(args)
    combined_strategy = core.combine_filters_any(*strategies)

    user_data_path = get_user_data_path()
    original_data = adapter.convert_csv_to_expenses(load_csv(user_data_path))
    modified_data, deleted_expenses = core.delete_expenses(
        original_data, combined_strategy
    )
    modified_csv = adapter.convert_expenses_to_csv(modified_data)
    save_csv(user_data_path, modified_csv)

    num_deleted = len(deleted_expenses)
    deleted_amount = core.calculate_total(deleted_expenses)["total"]

    if not num_deleted:
        console.print()
        console.print("[bold yellow]⚠️ No expenses matched the given filters.[/]")
        console.print("[dim]Nothing was deleted.[/]")
        console.print()
        return

    console.print()
    console.print(f"[bold red]🗑️ {num_deleted} expense(s) deleted successfully![/]")
    console.print()
    console.print(render.render_table(deleted_expenses, title="Deleted Expenses"))
    console.print(f"[bold white]Total Removed:[/] [bold red]${deleted_amount:.2f}[/]")
    console.print()


def handle_list(args, console):
    strategies = generate_strategy_list(args)
    combined_strategy = core.combine_filters_all(*strategies)

    key_map = {
        "date": lambda x: x.date,
        "amount": lambda x: x.amount,
        "id": lambda x: x.id,
    }

    user_data_path = get_user_data_path()
    original_data = adapter.convert_csv_to_expenses(load_csv(user_data_path))
    filtered_data = core.filter_expenses(original_data, combined_strategy)

    if not filtered_data:
        console.print()
        console.print("[bold yellow]⚠️ No expenses matched the given filters.[/]")
        console.print(args)
        console.print()
        return

    sorted_data = sorted(filtered_data, key=key_map[args.sort_by], reverse=args.desc)
    expense_summary = core.calculate_total(sorted_data)
    total_expenses = expense_summary["total"]

    console.print(render.render_table(sorted_data))
    console.print(
        f"[bold white]Filtered Total:[/] [bold green]${total_expenses:.2f}[/]"
    )
    console.print(
        f"[bold white]Entries:[/] [bold yellow]{len(sorted_data)}/{len(original_data)}[/]"
    )
    console.print()


def handle_add(args, console):
    user_data_path = get_user_data_path()
    original_data = adapter.convert_csv_to_expenses(load_csv(user_data_path))
    new_expense: Expense = core.add_expense(
        original_data, args.amount, args.description, args.date, args.category
    )
    new_csv_row: Dict[str, str] = adapter.convert_expense_to_csv_row(new_expense)
    append_csv(user_data_path, new_csv_row)

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


def handle_edit(args, console):
    user_data_path = get_user_data_path()
    original_data = adapter.convert_csv_to_expenses(load_csv(user_data_path))

    try:
        modified_data, changes = core.modify_expense(
            original_data,
            id=args.id,
            new_amount=args.amount if args.amount else None,
            new_date=args.date if args.date else None,
            new_category=args.category if args.category else None,
            new_description=args.description if args.description else None,
        )
        modified_csv = adapter.convert_expenses_to_csv(modified_data)
        save_csv(user_data_path, modified_csv)
    except ValueError:
        console.print()
        console.print(f"[bold red]⚠️ No expenses found for id: [cyan]{args.id}[/][/]")
        console.print("[dim]Use 'wallet list' to see expenses.[/]")
        console.print()
        return

    if not changes:
        console.print()
        console.print("[bold yellow]⚠️ No modifications were selected.[/]")
        console.print("[dim]Use '-h' to see options.[/]")
        console.print()
        return

    console.print()
    console.print(f"[bold yellow]✏️ Expense Edited[/] (ID: [bold]{args.id}[/])\n")
    console.print("[bold white]Changed:[/]")
    for field, (old, new) in changes.items():
        style_old = "dim"
        style_new = "bold green" if field == "amount" else "bold cyan"

        if field == "amount":
            old = f"${old}" if not str(old).startswith("$") else old
            new = f"${new}" if not str(new).startswith("$") else new

        console.print(
            f"  [bold]{field.capitalize()}:[/] [{style_old}]{old}[/] ➜ [{style_new}]{new}[/]"
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
            f"Description must be less than 50 characters: {description}"
        )

    return description


def get_user_data_path() -> str:
    return os.path.join(get_os_data_path(), "wallet-watcher/finances.csv")


def get_os_data_path() -> str:
    user_os = sys.platform
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
    app_data_dir_path = os.path.join(get_os_data_path(), const.APP_DIRECTORY_NAME)
    os.makedirs(app_data_dir_path, mode=0o700, exist_ok=True)

    user_data_path = os.path.join(app_data_dir_path, const.USER_DATA_FILENAME)
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
