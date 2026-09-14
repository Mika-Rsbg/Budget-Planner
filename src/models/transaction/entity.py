from dataclasses import dataclass
from datetime import date as datetime


@dataclass
class Transaction:
    account_id: int

    booking_date: datetime
    date: datetime

    transaction_type_id: int

    amount: float

    purpose: str

    counterparty_id: int | None

    category_id: int

    user_comments: str | None
    displayed_name: str | None

    transaction_id: int | None = None

    @classmethod
    def empty(cls) -> "Transaction":
        return cls(
            account_id=-1,
            booking_date=datetime(1, 1, 1),
            date=datetime(1, 1, 1),
            transaction_type_id=-1,
            amount=float("0"),
            purpose="",
            counterparty_id=None,
            category_id=-1,
            user_comments=None,
            displayed_name=None,
            transaction_id=None,
        )
