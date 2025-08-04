import sqlite3
from datetime import date, timedelta
from pathlib import Path
from logging import getLogger
from utils.data.database_connection import DatabaseConnection
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
        manuel_entry (bool, optional): For Manuel Transaction adding, allows
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
        if cursor.fetchone() is not None and not manuel_entry:
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
