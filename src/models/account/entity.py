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
