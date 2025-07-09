## Adding Expenses

```bash
wallet add 10.24
wallet add 10.24 --date "2027-07-08" --category "Food" --desc "Wendys"
wallet add 10.24 --date 2027-7-08 --category Food --desc Wendys
wallet add 10.24 --category "Food" --desc "Wendys"
wallet add 10.24 -c "Food" -d "Wendys"
```

---

## Deleting Expenses

```bash
wallet delete --id 1 
wallet delete --id 1 5 12 8
wallet delete --category "Food"
wallet delete --date 2027-07-08
wallet delete --min-date 2027-06-01
wallet delete --max-date 2027-08-01
wallet delete --min-date 2027-06-01 --max-date 2027-07-01 --category "Food"
wallet delete --min-amount 10.23 
wallet delete --max-amount 23.23
wallet delete --min-amount 10.23 --max-amount 23.23

```

---

## Editing Expenses

```bash
wallet edit --id 1 --c "Gaming" --date 2027-05-05 --desc "League"
wallet edit --id 13 --amount 24.67
wallet edit --id 12 --desc "Starbucks"
```

---

## Listing Expenses

```bash
wallet list [options]

Filter options:
  --day                Filter to today’s expenses
  --week               Filter to current ISO week
  --month              Filter to current month
  --year               Filter to current year
  --date YYYY-MM-DD    Filter to a specific date
  --month YYYY-MM      Filter to a specific month
  --week YYYY-W##      Filter to a specific ISO week
  --year YYYY          Filter by year

Other filters:
  --category CATEGORY
  --min-amount AMOUNT
  --max-amount AMOUNT
  --desc DESCRIPTION

Sorting:
  --sort-by FIELD      (e.g., amount, date, category)
  --desc               Sort in descending order
```

---

## Undo

```bash
wallet undo
wallet undo --times 3
wallet undo --list
wallet undo --id 5
```
