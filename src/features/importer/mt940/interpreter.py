import logging
from typing import List, Dict, Tuple, Union, Literal, TypeAlias
from gui.app.basewindow import BaseWindow
from features.account import account_repository as account_repository
from features.account import account_service as account_service
from features.counterparty import (counterparty_repository
                                   as counterparty_repository)
from features.transaction import (transaction_typ_repository
                                  as transaction_typ_repository)
from features.importer.mt940.importer import DatabaseMT940Error
from shared.date_utils import get_iso_date


logger = logging.getLogger(__name__)


RTIData: TypeAlias = tuple[
    int,
    str,
    str,
    int,
    str,
    str,
    int,
    Literal[1],
    None,
    None,
]


def get_account_id(account_number: str,
                   entry: Dict, window: BaseWindow) -> int:
    """
    Retrieve the account ID from the database based on the
    provided account number. If the account is not found, it will
    be added to the database.
    Args:
        account_number (str): The account number to look up.
        entry (dict): The entry containing the account information.
        window (BaseWindow): The main application window, used for context.
    Returns:
        int: The account ID from the database.
    Raises:
        Error: If the account is not found
            and cannot be added to the database.
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
            number=account_number, balance=entry['OpeningBalance']
        )
        rti_account_id = account_repository.get_account_id(
            data=[None, account_number, None, None],
            supplied_data=[False, True, False, False]
        )
    return rti_account_id


def get_tt_id(tt_name: str, tt_number: str) -> int:
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
        data: List[Dict[str, Union[str, Tuple[str], int, float]]],
        window: BaseWindow
        ) -> Tuple[List[RTIData],
                   List[Tuple[str, str, str]]]:
    """
    Process the parsed MT940 data and insert it into the database.
    This function iterates through the provided data, retrieves or creates
    necessary database entries for accounts, transaction types, and
    counterparties, and inserts transactions into the database.
    It also collects closing balances for each transaction.
    Args:
        data (List[Dict]): A List of dictionaries containing parsed MT940 data.
        window (BaseWindow): The main application window, used for context.
    Returns:
        List[Tuple[str, str, float]]: A List of tuples containing closing
            balances for each transaction in the format
            (account_number, record_date, balance).
    Raises:
        DatabaseMT940Error: If there is an error inserting transactions into
            the database.
    """
    closing_balance: List[Tuple[str, str, str]] = []

    interpreted_data: List[RTIData] = []

    for entry in data:
        # temp: not ready for the database
        # rti: ready to insert

        temp_account_number = str(entry['Account'])
        rti_account_id = get_account_id(temp_account_number, entry, window)

        temp_date = str(entry['Date'])
        rti_date = get_iso_date(temp_date)

        temp_bookingdate = str(rti_date[:2]) + str(entry['Bookingdate'])
        rti_bookingdate = get_iso_date(temp_bookingdate)

        temp_tt_number = str(entry['TransactionTypeNumber'])
        temp_tt_name = str(entry['TransactionTypeName'])
        rti_tt_id = get_tt_id(temp_tt_name, temp_tt_number)

        rti_amount = str(entry['Amount'])
        rti_purpose = str(entry['Purpose'])

        temp_counterparty_number = str(entry['CounterpartyAccount'])
        temp_counterparty_name = str(entry['CounterpartyName'])
        rti_counterparty_id = get_counterparty_id(
            temp_counterparty_name, temp_counterparty_number
        )

        rti_category_id = 1  # Default category
        rti_user_comments = None  # No user comments
        rti_displayed_name = None  # No displayed name

        # TODO: Add support for category, comments and displayed_name

        # Add the closing balance to the List
        if entry.get('ClosingBalance') is not None:
            closing_balance.append(entry['ClosingBalance'])  # type:ignore

        rti_data = (rti_account_id, rti_date, rti_bookingdate, rti_tt_id,
                    rti_amount, rti_purpose, rti_counterparty_id,
                    rti_category_id, rti_user_comments, rti_displayed_name)

        interpreted_data.append(rti_data)
    return (interpreted_data, closing_balance)


def interpret_account_history_entries(
    closing_balance: List[Tuple[str, str, str]]
) -> Tuple[List[Tuple[int, float, str, str]],
           Dict[str, Tuple[str, float, int]]]:
    """
    Convert closing balances into a format ready for database insertion.

    Args:
        closing_balance (List[Tuple[str, str, str]]):
            List containing:
            (account_number, record_date, balance)

    Returns:
        List[Tuple[int, float, str, str]]:
            List containing:
            (
                account_id,
                balance,
                record_date,
                change_date
            )
    """
    latest: Dict = {}
    interpreted_data: List[Tuple[int, float, str, str]] = []

    today = get_iso_date(today=True)

    for account_number, record_date, balance in closing_balance:
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
