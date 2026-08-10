from dataclasses import dataclass
from datetime import date as datetime


@dataclass
class ImportedTransactionView:
    import_id: int  # different in ImportedTransaction
    reference: str

    account_number: str
    account_id: int  # different in ImportedTransaction

    opening_balance: float

    date: datetime  # different in ImportedTransaction
    booking_date: datetime  # different in ImportedTransaction

    currency: str
    amount: float

    transaction_type_number: str
    transaction_type_name: str

    transaction_type_id: int  # different in ImportedTransaction

    purpose_addition: str
    purpose: str

    counterparty_account_number: str
    counterparty_name: str

    counterparty_id: int | None  # different in ImportedTransaction

    category_id: int  # different in ImportedTransaction

    user_comments: str | None  # different in ImportedTransaction
    displayed_name: str | None  # different in ImportedTransaction

    in_database: bool = False  # different in ImportedTransaction

    transaction_id: int | None = None  # different in ImportedTransaction

    @classmethod
    def empty(cls) -> "ImportedTransactionView":
        return cls(
            import_id=-1,
            reference="",
            account_number="",
            account_id=-1,
            opening_balance=0.0,
            date=datetime(1, 1, 1),
            booking_date=datetime(1, 1, 1),
            currency="",
            amount=0.0,
            transaction_type_number="",
            transaction_type_name="",
            transaction_type_id=-1,
            purpose_addition="",
            purpose="",
            counterparty_account_number="",
            counterparty_name="",
            counterparty_id=-1,
            category_id=-1,
            user_comments=None,
            displayed_name=None
        )
    # TODO: add better default values
