import os
import sys
import csv
import argparse
import wallet_watcher.constants as const


def main() -> None:
    return


def get_os_data_path() -> str:
    user_os: str = sys.platform
    if user_os == const.LINUX:
        return os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    elif user_os == const.MACOS:
        return os.path.expanduser("~/Library/Application Support")
    elif user_os == const.WINDOWS:
        return os.environ.get("LOCALAPPDATA", os.path.expanduser("~/AppData/Local"))
    else:
        raise ValueError("Unsupported Operating System")


def initialize_user_data() -> None:
    app_data_dir_path: str = os.path.join(get_os_data_path(), "wallet-watcher/")
    if not os.path.exists(app_data_dir_path):
        os.mkdir(app_data_dir_path, mode=0o600)
    user_data_path: str = os.path.join(app_data_dir_path, "finances.csv")
    if not os.path.exists(user_data_path):
        with open(user_data_path, "w", newline="") as csvfile:
            csv_writer = csv.DictWriter(csvfile, const.FIELD_NAMES)
            csv_writer.writeheader()


def load_csv(filepath: str) -> list[dict]:
    with open(filepath, "r", newline="") as csvfile:
        return list(csv.DictReader(csvfile))


def save_csv(filepath: str, data: list[dict]) -> None:
    with open(filepath, "w", newline="") as csvfile:
        csv_writer = csv.DictWriter(csvfile, const.FIELD_NAMES)
        csv_writer.writeheader()
        csv_writer.writerows(data)
