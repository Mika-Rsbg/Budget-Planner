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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CategoryRule):
            return NotImplemented

        return (
            self.id == other.id
            and self.name == other.name
            and self.priority == other.priority
            and self.enabled == other.enabled
            and self.category_id == other.category_id
            and self.rule == other.rule
            and self.query == other.query
        )
