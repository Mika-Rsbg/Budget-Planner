import logging
from typing import List
from pathlib import Path
import config
from features.transaction.transaction_repository import get_transaction_id
from features.account.account_repository import get_account_by_id
from features.counterparty.counterparty_repository import (
    get_counterparty_by_id
)
from features.transaction.transaction_typ_repository import (
    get_transaction_typ_by_id
)
from features.category.category_repository import get_category_by_id
from models.transaction.entity import Transaction
from models.transaction.view import TransactionView


logger = logging.getLogger(__name__)


def attach_existing_transaction_ids(
        transaction_data: List[Transaction],
        db_path: Path = config.Database.PATH
        ) -> List[Transaction]:
    # TODO: add docs
    updated_transactions: List[Transaction] = []
    for transaction in transaction_data:
        transaction_id = get_transaction_id(transaction, db_path)
        if transaction is not None:
            transaction.transaction_id = transaction_id
        updated_transactions.append(transaction)

    return updated_transactions


def build_transaction_view(transaction: Transaction) -> TransactionView:
    # TODO: add docs
    account_data = get_account_by_id(transaction.account_id)
    assert account_data is not None

    transaction_typ_data = get_transaction_typ_by_id(
        transaction.transaction_type_id
    )

    assert transaction.counterparty_id is not None

    counterparty_data = get_counterparty_by_id(
        transaction.counterparty_id
    )
    assert counterparty_data is not None

    category_data = get_category_by_id(
        transaction.category_id
    )

    assert category_data is not None

    return TransactionView(
        account_id=transaction.account_id,
        account_name=account_data.name,
        account_number=account_data.number,

        date=transaction.date,
        booking_date=transaction.booking_date,

        transaction_type_id=transaction.transaction_type_id,
        transaction_type_name=transaction_typ_data.name,
        transaction_type_number=transaction_typ_data.number,

        amount=transaction.amount,

        purpose=transaction.purpose,

        counterparty_id=transaction.counterparty_id,
        counterparty_name=counterparty_data.name,
        counterparty_number=counterparty_data.number,

        category_id=transaction.category_id,
        category_name=category_data.name,

        user_comments=transaction.user_comments,
        displayed_name=transaction.displayed_name,

        transaction_id=transaction.transaction_id
    )
