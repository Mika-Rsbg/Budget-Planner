import sqlite3
from datetime import date, timedelta
from pathlib import Path
from utils.data.database_connection import DatabaseConnection
import config


class Error(Exception):
    """General exception class for database errors."""

    class NoAccountHistoryFoundError(Exception):
        """Exception raised when no account history is found."""
        pass

    class ExistingAccountHistoryError(Exception):
        """Exception raised when account history already exists."""
        pass


def get_last_balance(db_path: Path = config.Database.PATH,
                     account_id: int = None) -> float:
    """
    Retrieves the balance of the specified account from the last month.
    If no record is found in the last month, it checks for one within the
    period of one year before. Raises an error if neither is found.

    Args:
        db_path (Path, optional): Path to the SQLite database file.
        account_id (int): ID of the account.

    Returns:
        float: The balance found.

    Raises:
        AccountHistoryNotFoundError: If no balance record is found for the
                                     last month or within the previous year.
        DatabaseAccountHistoryError: If an error occurs during the database
                                     query or connection.
    """
    # Determine the first and last day of the previous month.
    today = date.today()
    first_day_this_month = date(today.year, today.month, 1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = date(last_day_last_month.year,
                                last_day_last_month.month, 1)

    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        raise Error(f"Error connecting to database: {e}")

    query = """
        SELECT real_Balance FROM tbl_AccountHistory
        WHERE i8_AccountID = ?
            AND str_RecordDate BETWEEN ? AND ?
        ORDER BY str_RecordDate DESC LIMIT 1
    """

    try:
        # Try to get balance from last month
        cursor.execute(query, (
            account_id,
            first_day_last_month.isoformat(),
            last_day_last_month.isoformat()
        ))
        result = cursor.fetchone()
        if result is not None:
            return result[0]

        # If not found, check within the period of one year before
        # (from one year ago up to last month)
        start_date_year_before = first_day_last_month - timedelta(days=365)
        cursor.execute(query, (
            account_id,
            start_date_year_before.isoformat(),
            last_day_last_month.isoformat()
        ))
        result = cursor.fetchone()
        if result is not None:
            return result[0]

        raise Error.NoAccountHistoryFoundError(
            "No balance record found for the last month or within the"
            "previous year."
        )
    except sqlite3.Error as e:
        raise Error(f"Error retrieving balance: {e}")


def add_account_history(db_path: Path = config.Database.PATH,
                        account_id: int = None,
                        balance: float = None,
                        record_date: str = None,
                        change_date: str = None) -> None:
    """
    Adds a new account history record to the database for the specified
    account. If the record already exists, raises an error.

    Args:
        db_path (Path, optional): Path to the SQLite database file.
        account_id (int): ID of the account.
        balance (float): The amount to be recorded.
        record_date (str): Date of the balance record in ISO format
                           (YYYY-MM-DD).
        change_date (str): Date of the change in ISO format (YYYY-MM-DD).
    """
    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        raise Error(f"Error connecting to database: {e}")

    try:
        cursor.execute(
            '''
            SELECT * FROM tbl_AccountHistory
            WHERE i8_AccountID = ? AND str_RecordDate = ?
            ''',
            (account_id, record_date)
        )
        if cursor.fetchone() is not None:
            raise Error.ExistingAccountHistoryError(
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
        print("Account history record created successfully.")
    except sqlite3.Error as e:
        raise Error(f"Error creating account history record: {e}")
