# 💸 Wallet Watcher CLI

> A lightweight command-line interface for managing personal finances.

## 📦 Installation

Clone the repository and install locally:

```bash
git clone https://github.com/JoshuaSE-git/wallet-watcher-cli
cd wallet-watcher-cli
pip install .
```

Test installation with
```bash
wallet
```

## ⚙️ Commands

| Command  | Description                                           |
| -------- | ----------------------------------------------------- |
| `add`    | Add a new expense entry                               |
| `delete` | Delete entries by ID, date, category, or amount range |
| `edit`   | Edit an existing expense by ID                        |
| `list`   | View filtered and sorted expenses                     |
| `undo`   | Undo recent changes (deletions, edits, adds)          |

| Flags                        | Available Commands              | Description                       |
| ---------------------------- | ------------------------------- | --------------------------------- |
| `--date, -d`                 | `add`, `delete`, `edit`, `list` | Date in YYYY-MM-DD format         |
| `--category, -c`             | `add`, `delete`, `edit`, `list` | Expense category (ex. "Gaming")   |
| `--description, -s`          | `add`, `delete`, `edit`, `list` | Expense description (ex. "Dota2") |
| `--id, -i`                   | `delete`, `edit`, `list`        | Expense id (ex. 1)                |
| `--amount, -a`               | `delete`, `edit`, `list`        | Expense amount (ex. 10.32)        |
| `--min-amount, --max-amount` | `delete`, `list`                | Min/Max amount                    |
| `--min-date, --max-date`     | `delete`, `list`                | Min/Max date                      |

Use wallet [command] --help to see full options and flag descriptions.

## ▶️ Usage Examples

### ➕ Adding Expenses

```bash
wallet add 10.24
wallet add 10.24 --date "2027-07-08" --category "Food" --description "Wendys"
wallet add 10.24 --category "Food" -s "Wendys"
wallet add 10.24 -c "Food" -s "Wendys"
```

### ❌ Deleting Expenses

```bash
wallet delete --id 1 
wallet delete --id 1 5 12 8
wallet delete --category "Food"
wallet delete --date 2027-07-08
wallet delete --min-date 2027-06-01 --max-date 2027-07-01 --category "Food"
wallet delete --min-amount 10.23 --max-amount 23.23
```

### ✏️ Editing Expenses

```bash
wallet edit --id 1 -c "Gaming" --date 2027-05-05 --description "League"
wallet edit -i 13 --amount 24.67
wallet edit --id 12 --s "Starbucks"
```

### 📋 Listing Expenses

```bash
wallet list --day
wallet list --month 2027-07 --category Food --min-amount 5.00
wallet list --year 2027 --sort-by amount --desc
```

## 📁 Project Structure

## ✅ Requirements

- Python 3.12+
- [rich](https://github.com/Textualize/rich) (terminal formatting)

## 📄 License

[MIT License](https://github.com/JoshuaSE-git/wallet-watcher-cli/blob/main/LICENSE) © Joshua Emralino
