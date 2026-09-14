from dataclasses import dataclass


@dataclass
class Counterparty:
    id: int

    name: str
    number: str
