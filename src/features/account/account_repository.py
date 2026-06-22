import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional, Union, cast
import logging
from core.database.connection import DatabaseConnection
from shared.date_utils import get_iso_date
import config


logger = logging.getLogger(__name__)


class Error(Exception):
    """General exception class for database errors."""
    pass


class NoChangesDetectedError(Exception):
    """Exception raised when no changes are detected during an update."""
    pass


class NoAccountFoundError(Exception):
    """Exception raised when no account is found."""
    pass


class RecordTooOldError(Exception):
    """Exception raised when the record date is too old."""
    pass


def get_account_data(selected_columns: List[bool] = [True, True, True,
                                                     True, True, True,
                                                     True, True],
                     db_path: Path = config.Database.PATH
                     ) -> List[Tuple[Union[str, float, int], ...]]:
    """
        Retrieves account data from the database based on selected columns.
        Args:
            selected_columns (List[bool]): List of booleans indicating which
                columns to select. [AccountID(int), WidgetPosition(int),
                AccountName(str), AccountNumber(str), AccountBalance(float),
                AccountDifference(float), RecordDate(str), ChangeDate(str)]
            db_path (Path): Path to the SQLite database file.
        Return:
            List of tuples containing account data (AccountID, AccountName).
        Raises:
            Error: If the number of selected columns does not match the
                expected number of columns.
            NoAccountFoundError: If no account data is found in the database.
    """
    cursor = DatabaseConnection.get_cursor(db_path)
    columns = ["i8_AccountID", "i8_WidgetPosition", "str_AccountName",
               "str_AccountNumber", "real_AccountBalance",
               "real_AccountDifference", "str_RecordDate", "str_ChangeDate"]

    if len(columns) != len(selected_columns):
        logger.error("Wrong number of selected columns provided."
                     f"Expected {len(columns)}, got {len(selected_columns)}.")
        raise Error("Wrong number of  values provided."
                    f"Expected {len(columns)}, got {len(selected_columns)}.")

    query = 'SELECT '
    for i, col in enumerate(columns):
        if selected_columns[i]:
            query += f'{col}, '
    query = query[:-2] + ' FROM tbl_Account'

    try:
        cursor.execute(query)
        account_data = cursor.fetchall()
        logger.debug("Account data retrieved successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error querying data: {e}")
        raise Error(f"Error querying data: {e}")
    finally:
        DatabaseConnection.close_cursor()
    if not account_data:
        logger.warning("No account data found.")
    return account_data


def get_total_account_balance(db_path: Path = config.Database.PATH) -> float:
    """
        Retrieve and calculate the total cash balance
        by summing all real account balances.
        Args:
            db_path (Path): Path to the SQLite database file.
        Return:
            float: The total cash balance. Returns 0.0 if no data is found.
        Raises:
            sqlite3.Error: If there is an error
                           executing the query on the database.
    """
    cursor = DatabaseConnection.get_cursor(db_path)

    try:
        cursor.execute(
            """
            SELECT SUM(real_AccountBalance)
            FROM tbl_Account
            """
        )
        total_cash = cast(float, cursor.fetchall()[0][0])
    except sqlite3.Error as e:
        logger.error(f"Error querying data: {e}")
        raise Error(f"Error querying data: {e}")
    finally:
        DatabaseConnection.close_cursor()
    if not total_cash:
        logger.warning("No account data found. total_cash set to 0.0.")
        total_cash = 0.0
    return total_cash


def delete_account(account_id: int,
                   db_path: Path = config.Database.PATH) -> None:
    """
    Deletes an account from the database.
    Args:
        account_id (int): Account ID of the account to delete.
        db_path (Path): Path to the SQLite database file.
    Raises:
        Error: If the account ID is not provided or if any database error
               occurs.
    """
    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        logger.exception(f"Error connecting to database: {e}")
        raise Error(f"Error connecting to database: {e}")
    try:
        cursor.execute(
            '''
            DELETE FROM tbl_Account WHERE i8_AccountID = ?
            ''',
            (account_id,))

        conn.commit()
        logger.debug(f"Account with ID {account_id} deleted successfully.")
        print("Account deleted successfully.")
    except sqlite3.Error as e:
        logger.exception(f"Error deleting account: {e}")
        raise Error(f"Error deleting account: {e}")
    finally:
        DatabaseConnection.close_cursor()


def add_account(name: str, number: str, balance: float, difference: float,
                record_date: str, position: Optional[int] = None,
                change_date: Optional[str] = None,
                db_path: Path = config.Database.PATH) -> None:
    # FIXME: remove default None
    """
    Adds an account to the database.

    Args:
        name (str): Name of the account.
        number (str): Number of the account.
        balance (float): Balance of the account.
        difference (float): Difference of the account.
        record_date (str): Date of the record in ISO format.
        position (int, optional): Position of the account in the widget.
        change_date (str, optional): Date of the change in ISO format.
        db_path (Path, optional): Path to the SQLite database file.
    Raises:
        Error: If any of the required parameters are missing or if an error
              occurs during the database operation.
    """
    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        logger.exception(f"Error connecting to database: {e}")
        raise Error(f"Error connecting to database: {e}")

    if position is None:
        cursor.execute("SELECT MAX(i8_WidgetPosition) FROM tbl_Account")
        row = cursor.fetchone()

        if row and row[0] is not None:
            position = row[0] + 1
        else:
            position = 0

    if change_date is None:
        change_date = get_iso_date(today=True)

    try:
        cursor.execute(
            '''
            INSERT INTO tbl_Account (i8_WidgetPosition, str_AccountName,
            str_AccountNumber, real_AccountBalance, real_AccountDifference,
            str_RecordDate, str_ChangeDate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (position, name, number, balance, difference, record_date,
             change_date))
        conn.commit()
        logger.debug("Account added successfully.")
    except sqlite3.Error as e:
        logger.exception(f"Error creating account: {e}")
        raise Error(f"Error creating account: {e}")
    finally:
        DatabaseConnection.close_cursor()


def get_account_id(data: List, supplied_data=[False, False, False, False],
                   db_path: Path = config.Database.PATH) -> int:
    """
    Retrieves the account ID from the database based on the provided filtering
    criteria.

    Args:
        data (List): A list of 4 elements in the order [AccountName,
                     AccountNumber, AccountBalance, AccountDifference].
        supplied_data (List of bool): A list of booleans indicating which
            corresponding elements of 'data' to use as filter criteria.
            Each True value corresponds to applying an equality filter
            for the respective column.
        db_path (Path, optional): Path to the SQLite database file.
    Returns:
        int: The account ID (i8_AccountID) of the account matching the
             provided criteria.
    Raises:
        Error: If 'data' is None or does not contain exactly 4
              elements.
        Error: If no filtering criteria are provided
              (i.e., all elements in supplied_data are False).
        NoAccountFoundError: If no matching account is found in the database.
        Error: If an error occurs during the database query.
    """
    if data is None or len(data) != 4:
        raise Error("Data must be provided as a list"
                    "of 4 elements: [Name, Number, Balance, Difference].")
    columns = ["str_AccountName", "str_AccountNumber", "real_AccountBalance",
               "real_AccountDifference"]
    conditions: List = []
    parameters = []
    for col, should_filter, value in zip(columns, supplied_data, data):
        if should_filter:
            conditions.append(f"{col} = ?")
            parameters.append(value)
    if not conditions:
        logger.error("No criteria provided to query account ID.")
        raise Error("No criteria provided to query account ID.")
    # Build the SQL query dynamically based on the provided criteria.
    where_clause = " AND ".join(conditions)
    query = (
        "SELECT i8_AccountID FROM tbl_Account "
        f"WHERE {where_clause}"
    )

    try:
        cursor = DatabaseConnection.get_cursor(db_path)
        cursor.execute(query, parameters)
        result = cursor.fetchone()
        if result is None:
            logger.error("No matching account found.")
            raise NoAccountFoundError("No matching account found.")
        return result[0]
    except sqlite3.Error as e:
        logger.exception(f"Error querying account ID: {e}")
        raise Error(f"Error querying account ID: {e}")
    finally:
        DatabaseConnection.close_cursor()
