from dataclasses import dataclass


@dataclass
class Expense:
    id: int
    date: str
    category: str | None
    description: str
    amount: float
