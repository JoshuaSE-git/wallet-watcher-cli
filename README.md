# 💸 Wallet Watcher CLI

> A lightweight command-line interface for managing personal finances.

## 📦 Installation


## ⚙️ Commands

| Command  | Description                                           |
| -------- | ----------------------------------------------------- |
| `add`    | Add a new expense entry                               |
| `delete` | Delete entries by ID, date, category, or amount range |
| `edit`   | Edit an existing expense by ID                        |
| `list`   | View filtered and sorted expenses                     |
| `undo`   | Undo recent changes (deletions, edits, adds)          |

Use wallet [command] --help to see full options and flag descriptions.

## ▶️ Usage Examples

### ➕ Adding Expenses

```bash
wallet add 10.24
wallet add 10.24 --date "2027-07-08" --category "Food" --desc "Wendys"
wallet add 10.24 --category "Food" --desc "Wendys"
wallet add 10.24 -c "Food" -d "Wendys"
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
wallet edit --id 1 --c "Gaming" --date 2027-05-05 --desc "League"
wallet edit --id 13 --amount 24.67
wallet edit --id 12 --desc "Starbucks"
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
