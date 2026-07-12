from typing import List, Tuple, Dict
import logging
from features.account import (account_history_repository
                              as account_history_repository)
from features.transaction import (transaction_repository
                                  as transaction_repository)
import features.account.account_service as account_service
from features.importer.mt940.errors import DatabaseMT940Error
from shared.date_utils import get_iso_date
from models.transaction.entity import Transaction


logger = logging.getLogger(__name__)


def add_transactions(data: List[Transaction]):
    """
    Insert transaction data into the database.

    This function iterates over prepared RTIData entries and attempts
    to insert each transaction into the database. It tracks successful
    inserts and skipped entries (already existing records).

    Args:
        data (List[Transaction]):
            List of transaction objects ready for database insertion.

    Raises:
        DatabaseMT940Error:
            If an unexpected database error occurs during insertion.
    """
    # TODO: update docs
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
            # TODO: add Transaction id addtion to transaction
            # If a transaction is already in the database the the coresponding
            # id should be added to later use it as indicator if the
            # transaction is already in the database
            # This information will be used for selection tools during the
            # import.
            # As this function is used to import the transactions another
            # time to checke if transactions are already in the database should
            # be used.

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
    """
    Insert account history entries into the database.

    This function processes prepared account history data and inserts
    each entry into the database. It tracks how many entries were
    inserted or skipped due to existing records.

    Args:
        data (List[Tuple[int, float, str, str]]):
            List of account history entries in format:
            (account_id, balance, record_date, change_date)

    Raises:
        DatabaseMT940Error:
            If an unexpected database error occurs during insertion.
    """
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
    Update account balances based on the latest account history data.

    This function:
        - Retrieves the last known balance from the database
        - Calculates the difference between old and new balances
        - Updates the account with the new balance and delta value
        - Handles cases where no previous balance exists

    Args:
        latest (Dict[str, Tuple[str, float, int]]):
            Dictionary mapping account numbers to:
            (record_date, balance, account_id)

            Example:
                {
                    "123456789": ("2023-10-01", 1500.75, 1),
                    "987654321": ("2023-10-02", -500.50, 2)
                }

    Raises:
        DatabaseMT940Error:
            If updating the account fails due to database issues.
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
