from typing import TypeAlias, List, Literal, Tuple, Dict
import logging
from features.account import (account_history_repository
                              as account_history_repository)
from features.transaction import (transaction_repository
                                  as transaction_repository)
import features.account.account_service as account_service
from features.importer.mt940.errors import DatabaseMT940Error
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


def add_transactions(data: List[RTIData]):
    # Initialize counters
    number_skipped_transactions = 0
    number_inserted_transactions = 0

    for transaction in data:
        try:
            transaction_repository.add_transaction(
                data=transaction
            )
            number_inserted_transactions += 1
        except transaction_repository.AlreadyExistsError:
            number_skipped_transactions += 1
        except transaction_repository.Error:
            logger.error("Error inserting transaction.")
            raise DatabaseMT940Error("Error inserting transaction.")

    if number_inserted_transactions > 0:
        logger.debug(f"Inserted {number_inserted_transactions} "
                     "transactions into the database.")
    if number_skipped_transactions > 0:
        logger.debug(f"Skipped {number_skipped_transactions} "
                     "transactions because they were already "
                     "in the database.")
    logger.debug("Transactions successfully inserted to database or skipped.")


def add_account_history_entries(data: List[Tuple[int, float, str, str]]):
    number_skipped_ac_his_entries = 0
    number_added_ac_his_entries = 0
    for (account_id, balance, record_date, change_date) in data:
        try:
            account_history_repository.add_account_history(
                account_id=account_id,
                balance=balance,
                record_date=record_date,
                change_date=change_date
            )
            number_added_ac_his_entries += 1
        except account_history_repository.ExistingAccountHistoryError:
            number_skipped_ac_his_entries += 1
        except account_history_repository.Error:
            logger.error("Error inserting account history entry.")
            raise DatabaseMT940Error("Error inserting account history entry.")

    # Log summary after the loop
    if number_skipped_ac_his_entries > 0:
        logger.debug(
            f"Skipped {number_skipped_ac_his_entries} "
            "account history entries because "
            "they were already in the database."
        )
    if number_added_ac_his_entries > 0:
        logger.debug(
            f"Inserted {number_added_ac_his_entries} "
            "account history entries into the database."
        )
    logger.debug("Account history entries successfully inserted to database"
                 "or skipped.")


def update_account_balances(latest: Dict[str, Tuple[str, float, int]]) -> None:
    """
    Update the account balances in the database based on the latest
    account history entries.
    This function retrieves the last balance for each account from the
    database, calculates the difference between the last balance and the
    new balance, and updates the account with the new balance and the
    calculated difference. It also handles cases where the account is not
    found in the database, raising a DatabaseMT940Error if necessary.
    Args:
        latest (Dict[str, Tuple[str, float, int]]): A dictionary containing
            the latest account history entries, where the key is the account
            number and the value is a tuple of (record_date, balance,
            rti_account_id).

            Example:
                {
                    "123456789": ("2023-10-01", 1500.75, 1),
                    "987654321": ("2023-10-02", -500.50, 2)
                }
    Raises:
        DatabaseMT940Error: If there is an error updating the account.
    """
    today = get_iso_date(today=True)
    for account_number, (record_date, balance,
                         rti_account_id) in latest.items():
        try:
            last_balance = account_history_repository.get_last_balance(
                account_id=rti_account_id
            )
        except account_history_repository.NoAccountHistoryFoundError:
            last_balance = 0.0
        logger.debug(
            f"Last balance: {last_balance} and new balance: {balance}")
        difference = round(float(balance) - float(last_balance), 2)
        logger.debug(
            f"Difference between last balance and new balance: {difference}"
        )
        try:
            print("balance", balance, "record_date", record_date,)
            account_service.update_account(
                account_id=rti_account_id,
                new_values=["", "", "", balance, difference,
                            get_iso_date(record_date), today]
            )
            logger.info(
                f"Account {account_number} updated with new balance: {balance}"
            )
            logger.debug("Account balances successfully updated in the "
                         "database.")
        except account_service.NoChangesDetectedError:
            logger.debug(
                f"Account {account_number} already has the same values. "
                "Skipping"
            )
        except account_service.RecordTooOldError:
            logger.info(
                f"Account {account_number} has a balance with a record date "
                "newer than the latest in this bank statement. "
                "Skipping update."
            )
