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
    LT = 1
    LTE = 2
    GT = 3
    GTE = 4
    EQ = 5


FilterStrategy: TypeAlias = Callable[[Expense], bool]
