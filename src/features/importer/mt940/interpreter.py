import logging
from typing import List, Dict, Tuple
from decimal import Decimal
from gui.app.basewindow import BaseWindow
from features.account import account_repository as account_repository
from features.account import account_service as account_service
from features.counterparty import (counterparty_repository
                                   as counterparty_repository)
from features.transaction import (transaction_typ_repository
                                  as transaction_typ_repository)
from features.importer.mt940.errors import DatabaseMT940Error
from shared.date_utils import get_iso_date
from models.transaction.imported import ImportedTransaction
from models.transaction.entity import Transaction


logger = logging.getLogger(__name__)


def get_account_id(account_number: str,
                   entry: ImportedTransaction, window: BaseWindow) -> int:
    """
    Retrieve the account ID for a given account number.

    If the account does not exist in the database, it will be created
    using MT940 account information and then retrieved again.

    Args:
        account_number (str):
            Account number to look up.
        entry (Dict):
            Parsed MT940 entry containing account metadata
            (e.g. opening balance).
        window (BaseWindow):
            Main application window used for context and account creation flow.

    Returns:
        int:
            Database ID of the account.

    Raises:
        Error:
            If the account cannot be retrieved or created successfully.
    """
    try:
        rti_account_id = account_repository.get_account_id(
            data=[None, account_number, None, None],
            supplied_data=[False, True, False, False]
        )
    except account_repository.NoAccountFoundError:
        logger.warning(
            f"Account {account_number} not found in database."
        )
        account_service.add_account_mt940(
            master=window,
            number=account_number, balance=float(entry.opening_balance)
        )
        rti_account_id = account_repository.get_account_id(
            data=[None, account_number, None, None],
            supplied_data=[False, True, False, False]
        )
    return rti_account_id


def get_tt_id(tt_name: str, tt_number: str) -> int:
    """
    Retrieve the transaction type ID from the database.

    If the transaction type does not exist, it will be created
    and then retrieved again.

    Args:
        tt_name (str):
            Name of the transaction type.
        tt_number (str):
            Identifier number of the transaction type.

    Returns:
        int:
            Database ID of the transaction type.
    """
    try:
        rti_tt_id = transaction_typ_repository.get_transaction_typ_id(
            data=[tt_name, tt_number],
            supplied_data=[True, True]
        )
    except transaction_typ_repository.Error:
        logger.warning(
            f"Transaction type {tt_name} not found in database."
        )
        transaction_typ_repository.add_transaction_typ(
            name=tt_name, number=tt_number
        )
        rti_tt_id = transaction_typ_repository.get_transaction_typ_id(
            data=[tt_name, tt_number],
            supplied_data=[True, True]
        )
    return rti_tt_id


def get_counterparty_id(counterparty_name: str,
                        counterparty_number: str) -> int:
    """
    Retrieve the counterparty ID from the database.

    If the counterparty does not exist, it will be created
    and then retrieved again.

    Args:
        counterparty_name (str):
            Name of the counterparty.
        counterparty_number (str):
            Account number or identifier of the counterparty.

    Returns:
        int:
            Database ID of the counterparty.
    """
    try:
        rti_counterparty_id = counterparty_repository.get_counterparty_id(
            data=[counterparty_name, counterparty_number],
            supplied_data=[False, True]
        )
    except counterparty_repository.Error:
        logger.warning(
            f"Counterparty {counterparty_name} not found in "
            "database."
        )
        counterparty_repository.add_counterparty(
            name=counterparty_name, number=counterparty_number
        )
        rti_counterparty_id = counterparty_repository.get_counterparty_id(
            data=[counterparty_name, counterparty_number],
            supplied_data=[True, True]
        )
    if rti_counterparty_id is None:
        # wird nicht passieren, da None nie eintreten kann
        return -1
    return rti_counterparty_id


def interpret_transactions(
        data: List[ImportedTransaction],
        window: BaseWindow
        ) -> Tuple[List[Transaction],
                   List[Tuple[str, str, str]]]:
    """
    Convert parsed MT940 transactions into database-ready structures.

    This function:
        - Resolves or creates accounts, transaction types, and counterparties
        - Converts raw MT940 fields into normalized database IDs
        - Builds RTI (Ready-To-Insert) transaction tuples
        - Collects closing balance entries for account history processing

    Args:
        data (List[Dict[str, Union[str, Tuple[str], int, float]]]):
            Parsed MT940 transaction data.
        window (BaseWindow):
            Main application window used for account creation
            and context handling.

    Returns:
        Tuple containing:
            - List[RTIData]:
                Normalized transaction data ready for database insertion.
            - List[Tuple[str, str, str]]:
                Closing balance entries in format:
                (account_number, record_date, balance)
    """
    closing_balance: List[Tuple[str, str, str]] = []

    interpreted_data: List[Transaction] = []

    for entry in data:
        # temp: not ready for the database
        # rti: ready to insert

        temp_account_number = entry.account_number
        rti_account_id = get_account_id(temp_account_number, entry, window)

        temp_date = entry.date
        rti_date = get_iso_date(temp_date)

        temp_bookingdate = str(rti_date[:2]) + entry.booking_date
        rti_booking_date = get_iso_date(temp_bookingdate)

        temp_tt_number = entry.transaction_type_number
        temp_tt_name = entry.transaction_type_name
        rti_tt_id = get_tt_id(temp_tt_name, temp_tt_number)

        rti_amount = str(entry.amount)
        rti_purpose = entry.purpose

        temp_counterparty_number = entry.counterparty_account_number
        temp_counterparty_name = entry.counterparty_name
        rti_counterparty_id = get_counterparty_id(
            temp_counterparty_name, temp_counterparty_number
        )

        rti_category_id = 1  # Default category
        rti_user_comments = None  # No user comments
        rti_displayed_name = None  # No displayed name

        # TODO: Add support for category, comments and displayed_name

        # Add the closing balance to the List
        if entry.closing_balance != ("", "", ""):
            closing_balance.append(entry.closing_balance)

        transaction = Transaction(
            account_id=rti_account_id,
            date=rti_date,
            booking_date=rti_booking_date,
            transaction_type_id=rti_tt_id,
            amount=Decimal(rti_amount),
            purpose=rti_purpose,
            counterparty_id=rti_counterparty_id,
            category_id=rti_category_id,
            user_comments=rti_user_comments,
            displayed_name=rti_displayed_name,
        )
        interpreted_data.append(transaction)

    return (interpreted_data, closing_balance)


def interpret_account_history_entries(
    closing_balance: List[Tuple[str, str, str]]
) -> Tuple[List[Tuple[int, float, str, str]],
           Dict[str, Tuple[str, float, int]]]:
    """
    Convert closing balance entries into database-ready account history data.

    This function:
        - Resolves account IDs for each closing balance entry
        - Converts balances and dates into normalized formats
        - Builds a list of account history records for insertion
        - Tracks the latest balance per account

    Args:
        closing_balance (List[Tuple[str, str, str]]):
            List of closing balance entries in format:
            (account_number, record_date, balance)

    Returns:
        Tuple containing:
            - List[Tuple[int, float, str, str]]:
                Account history entries in format:
                (account_id, balance, record_date, change_date)
            - Dict[str, Tuple[str, float, int]]:
                Latest entry per account:
                account_number -> (record_date, balance, account_id)
    """
    latest: Dict = {}
    interpreted_data: List[Tuple[int, float, str, str]] = []

    today = get_iso_date(today=True)

    for account_number, record_date, balance in closing_balance:
        if (account_number, record_date, balance) == ('', '', ''):
            continue
        try:
            account_id = account_repository.get_account_id(
                data=[None, account_number, None, None],
                supplied_data=[False, True, False, False]
            )
        except account_repository.NoAccountFoundError:
            logger.warning(
                f"Account {account_number} not found in database."
            )
            raise DatabaseMT940Error(
                f"Account {account_number} not found in database. "
                "Even though it was in the MT940 file."
            )

        interpreted_data.append(
            (
                account_id,
                float(balance),
                get_iso_date(record_date),
                today
            )
        )
        if account_number not in latest:
            latest[account_number] = (record_date, balance, account_id)
        elif record_date > latest[account_number][0]:
            latest[account_number] = (record_date, balance, account_id)
    return (interpreted_data, latest)
