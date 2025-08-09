import sqlite3
from datetime import date, timedelta
from pathlib import Path
from logging import getLogger
from collections import defaultdict
from typing import List, Tuple, cast
from utils.data.database_connection import DatabaseConnection
from utils.data.database.account_utils import (
    get_account_data, NoAccountFoundError
)
from utils.data.date_utils import get_iso_date
import config


logger = getLogger(__name__)


class Error(Exception):
    """General exception class for database errors."""
    pass


class ExistingAccountHistoryError(Exception):
    """Exception raised when account history already exists."""
    pass


class NoAccountHistoryFoundError(Exception):
    """Exception raised when no account history is found."""
    pass


def get_total_cash_history(start_date: str, end_date: str,
                           db_path: Path = config.Database.PATH
                           ) -> List[Tuple[float, str]]:
    """
    Retrieves the total cash history for all accounts within a specified date
    range. If no date range is specified, it retrieves the entire history.
    Args:
        start_date (str): Start date in ISO format (YYYY-MM-DD).
        end_date (str): End date in ISO format (YYYY-MM-DD).
        db_path (Path, optional): Path to the SQLite database file.
    Returns:
        List[Tuple[float, str]]: A list of tuples containing the date and total
            cash value for that date.
    Raises:
        NoAccountHistoryFoundError: If no account history is found.
        Error: If an error occurs during the database query or connection.
    """
    try:
        account_data = get_account_data(
            selected_columns=[True, False, True, False, True,
                              False, True, False], db_path=db_path
        )
        # print(account_data)
        all_account_histories = get_balance_history(
            cast(List[int], [account[0] for account in account_data]), db_path
        )
        # print(all_account_histories)
    except NoAccountFoundError as e:
        logger.error(f"No accounts found: {e}")
        raise NoAccountHistoryFoundError("No accounts found.")
    except Error as e:
        logger.error(f"Error retrieving account history: {e}")
        raise NoAccountHistoryFoundError("Error retrieving account history.")

    current_values = defaultdict(float)
    all_dates = set()
    # collect all dates
    for account_history in all_account_histories:
        for _, _, record_date in account_history:
            all_dates.add(record_date)
    # sort all dates
    sorted_dates = sorted(all_dates)
    # build a per-id timeline
    changes = defaultdict(dict)
    for account_history in all_account_histories:
        for acc_id, balance, record_date in account_history:
            changes[acc_id][record_date] = balance
    # calculate totals over time
    result = []
    for record_date in sorted_dates:
        for acc_id in changes:
            if record_date in changes[acc_id]:
                current_values[acc_id] = changes[acc_id][record_date]
        total = sum(current_values.values())
        result.append((record_date, total))

    # filter results by date range
    if start_date or end_date:
        start_date = start_date or "0001-01-01"
        end_date = end_date or "9999-12-31"
        result = [
            (date, value) for date, value in result
            if start_date <= date <= end_date
        ]
    return result


def get_balance_history(account_id: List[int],
                        db_path: Path = config.Database.PATH
                        ) -> List[List[Tuple[int, float, str]]]:
    """
    Retrieves the balance history for the specified account IDs.
    Args:
        account_id (List[int]): List of account IDs to retrieve history for.
        db_path (Path, optional): Path to the SQLite database file.
    Returns:
        List[List[Tuple[int, float, str]]]: A list of lists containing tuples
            with account ID, balance, and record date.
    Raises:
        NoAccountHistoryFoundError: If no balance history is found for the
            specified account IDs.
        Error: If an error occurs during the database query or connection.
    """
    try:
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise Error(f"Error connecting to database: {e}")

    try:
        result: List[List[Tuple[int, float, str]]] = []
        for id in account_id:
            cursor.execute("""
                SELECT i8_AccountID, real_Balance, str_RecordDate
                FROM tbl_AccountHistory WHERE i8_AccountID = ?
                ORDER BY str_RecordDate
            """, (
                id,
            ))
            data = cursor.fetchall()
            result.append(data)
        if any(result):
            logger.debug("Balance history found.")
            # print(result)
            return result
        logger.warning("No balance found.")
        raise NoAccountHistoryFoundError("No balance found.")
    except sqlite3.Error as e:
        logger.error(f"Error retrieving balance: {e}")
        raise Error(f"Error retrieving balance: {e}")
    finally:
        DatabaseConnection.close_cursor()


def get_last_balance(account_id: int,
                     db_path: Path = config.Database.PATH) -> float:
    """
    Retrieves the last balance of the specified account.

    Args:
        db_path (Path, optional): Path to the SQLite database file.
        account_id (int): ID of the account.

    Returns:
        float: The balance found.

    Raises:
        AccountHistoryNotFoundError: If no balance record is found.
        Error: If an error occurs during the database
            query or connection.
    """
    # Determine the first and last day of the previous month.
    today = date.today()
    first_day_this_month = date(today.year, today.month, 1)
    last_day_last_month = first_day_this_month - timedelta(days=1)

    try:
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise Error(f"Error connecting to database: {e}")

    try:
        cursor.execute("""
            SELECT real_Balance FROM tbl_AccountHistory
            WHERE i8_AccountID = ?
            AND str_RecordDate < ?
            ORDER BY str_RecordDate DESC LIMIT 1
        """, (
            account_id,
            last_day_last_month.isoformat()
        ))
        result = cursor.fetchone()
        if result is not None:
            logger.debug("Last balance found.")
            return result[0]

        logger.warning("No balance found.")
        raise NoAccountHistoryFoundError("No balance found.")
    except sqlite3.Error as e:
        logger.error(f"Error retrieving balance: {e}")
        raise Error(f"Error retrieving balance: {e}")
    finally:
        DatabaseConnection.close_cursor()


def add_account_history(account_id: int, balance: float, record_date: str,
                        change_date: str = "", manual_entry: bool = False,
                        db_path: Path = config.Database.PATH) -> None:
    """
    Adds a new account history record to the database for the specified
    account. If the record already exists, raises an error.

    Args:
        account_id (int): ID of the account.
        balance (float): The amount to be recorded.
        record_date (str): Date of the balance record in ISO format
                           (YYYY-MM-DD).
        change_date (str): Date of the change in ISO format (YYYY-MM-DD).
                           If empty, it will be set to the current date.
        manual_entry (bool, optional): For Manual Transaction adding, allows
                                       manual entry without checking for
                                       existing records.
        db_path (Path, optional): Path to the SQLite database file.

    Raises:
        ExistingAccountHistoryError: If an account history record already
            exists for the specified date.
        Error: If an error occurs during the database operation.
    """
    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        raise Error(f"Error connecting to database: {e}")

    if change_date == "":
        change_date = get_iso_date(today=True)

    try:
        cursor.execute(
            '''
            SELECT * FROM tbl_AccountHistory
            WHERE i8_AccountID = ? AND str_RecordDate = ?
            ''',
            (account_id, record_date)
        )
        if cursor.fetchone() is not None and not manual_entry:
            logger.error(
                f"Account history already exists for account ID {account_id} "
                f"on date {record_date}."
            )
            raise ExistingAccountHistoryError(
                "Account history already exists for this date."
            )

        cursor.execute(
            '''
            INSERT INTO tbl_AccountHistory (i8_AccountID, real_Balance,
            str_RecordDate, str_ChangeDate)
            VALUES (?, ?, ?, ?)
            ''',
            (account_id, balance, record_date, change_date)
        )
        conn.commit()
        logger.debug("Account history record created successfully.")
    except sqlite3.Error as e:
        raise Error(f"Error creating account history record: {e}")
    finally:
        DatabaseConnection.close_cursor()
