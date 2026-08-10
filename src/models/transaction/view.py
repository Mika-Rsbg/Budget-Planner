from dataclasses import dataclass
from datetime import date as datetime


@dataclass
class TransactionView:
    account_id: int
    account_name: str
    account_number: str

    booking_date: datetime
    date: datetime

    transaction_type_id: int
    transaction_type_name: str
    transaction_type_number: str

    amount: float

    purpose: str

    counterparty_id: int | None
    counterparty_name: str | None
    counterparty_number: str | None

    category_id: int
    category_name: str

    user_comments: str | None
    displayed_name: str | None

    transaction_id: int | None = None
