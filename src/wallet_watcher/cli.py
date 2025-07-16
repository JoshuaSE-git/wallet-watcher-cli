import os
import sys
import csv
import argparse
import wallet_watcher.constants as const
from wallet_watcher._types import Expense, ExpenseField, Comparator
from typing import List, Dict


def main() -> None:
    return


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
