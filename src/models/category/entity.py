from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Category:
    id: int

    name: str

    budget: Decimal

    budget_period_id: int
