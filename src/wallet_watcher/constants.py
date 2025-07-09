from wallet_watcher._types import ExpenseField

FIELD_NAMES = ["id", "date", "category", "description", "amount"]

FIELD_LIST = []

FIELD_MAP = {
    ExpenseField.AMOUNT: "amount",
    ExpenseField.ID: "id",
    ExpenseField.CATEGORY: "category",
    ExpenseField.DATE: "date",
    ExpenseField.DESCRIPTION: "description",
}


LINUX = "linux"
MACOS = "darwin"
WINDOWS = "win32"

ENV_XDG_DATA_HOME = "XDG_DATA_HOME"
ENV_LOCAL_APPDATA = "LOCALAPPDATA"

PATH_LINUX_DATA = "~/.local/share"
PATH_MACOS_DATA = "~/Library/Application Support"
PATH_WINDOWS_DATA = "~/AppData/Local"

APP_DIR_NAME = "wallet-watcher/"
USER_DATA_FILENAME = "finances.csv"

DATE_FORMAT_STRING = "%Y-%m-%d"

DEFAULT_DESCRIPTION = "N/A"
DEFAULT_CATEGORY = "General"
