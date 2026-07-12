from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Transaction:
    account_id: int

    date: str
    booking_date: str

    transaction_type_id: int

    amount: Decimal

    purpose: str

    counterparty_id: int | None

    category_id: int

    user_comments: str | None
    displayed_name: str | None

    transaction_id: int | None = None
