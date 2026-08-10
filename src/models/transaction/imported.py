from dataclasses import dataclass
from typing import Tuple


@dataclass
class ImportedTransaction:
    reference: str

    account_number: str

    opening_balance: float
    closing_balance: Tuple[str, str, str]

    date: str
    booking_date: str

    currency: str
    amount: float

    transaction_type_number: str
    transaction_type_name: str

    purpose_addition: str
    purpose: str

    counterparty_account_number: str
    counterparty_name: str
