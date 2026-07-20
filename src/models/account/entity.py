from dataclasses import dataclass


@dataclass
class Account:
    id: int

    widget_position: int

    name: str
    number: str

    balance: float
    difference: float

    record_date: str
    change_date: str
