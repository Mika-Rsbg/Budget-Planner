from dataclasses import dataclass


@dataclass
class Category:
    id: int

    name: str

    budget: float

    budget_period_id: int
