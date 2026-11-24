from dataclasses import dataclass

from models.category_rule.query import Query


@dataclass
class CategoryRule:
    id: int

    name: str

    priority: int

    enabled: bool

    category_id: int

    rule: str

    query: Query | None = None
