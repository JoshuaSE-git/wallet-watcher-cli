from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TypeAlias
from collections.abc import Callable
from enum import Enum


@dataclass
class Expense:
    id: int
    date: date
    category: str
    description: str
    amount: Decimal


class Comparator(Enum):
    LESS_THAN = 1
    LESS_THAN_EQUAL = 2
    GREATER_THAN = 3
    GREATER_THAN_EQUAL = 4
    EQUAL = 5


class ExpenseField(Enum):
    ID = 1
    DATE = 2
    CATEGORY = 3
    AMOUNT = 4
    DESCRIPTION = 5


FilterStrategy: TypeAlias = Callable[[Expense], bool]
