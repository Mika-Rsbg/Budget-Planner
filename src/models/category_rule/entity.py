from dataclasses import dataclass

from models.category_rule.query import (
    Query,
    test_query,
)


@dataclass
class CategoryRule:
    id: int

    name: str

    priority: int

    enabled: bool

    category_id: int

    rule: str

    query: Query | None = None


example_rule = CategoryRule(
    id=1,
    name="Test Query",
    priority=1,
    enabled=True,
    category_id=2,
    rule="",
    query=test_query,
)
