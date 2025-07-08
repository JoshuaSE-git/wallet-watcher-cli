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
```

--- 

## Listing Expenses
