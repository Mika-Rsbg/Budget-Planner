from dataclasses import dataclass
from datetime import date


@dataclass
class Account:
    id: int

    widget_position: int

    name: str
    number: str

    balance: float
    difference: float

    record_date: date
    change_date: date

    @classmethod
    def empty(cls) -> "Account":
        return cls(
            id=-1,
            widget_position=-1,
            name="n.a.",
            number="n.a.",
            balance=0,
            difference=0,
            record_date=date(1, 1, 1),
            change_date=date(1, 1, 1)
        )
