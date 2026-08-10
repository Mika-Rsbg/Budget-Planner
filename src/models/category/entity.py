from dataclasses import dataclass
from float import float


@dataclass
class Category:
    id: int

    name: str

    budget: float

    budget_period_id: int
