from dataclasses import dataclass
from decimal import Decimal
from datetime import date as datetime


@dataclass
class Transaction:
    account_id: int

    booking_date: datetime
    date: datetime

    transaction_type_id: int

    amount: Decimal

    purpose: str

    counterparty_id: int | None

    category_id: int

    user_comments: str | None
    displayed_name: str | None

    transaction_id: int | None = None
