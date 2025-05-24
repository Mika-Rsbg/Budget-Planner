import tkinter as tk
import random
import string
import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional, Union
import logging
from gui.accountpage.name_input_page import NameInputDialog
from utils.data.database_connection import DatabaseConnection
from utils.data.date_utils import get_iso_date
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


def get_account_data(db_path: Path = config.Database.PATH,
                     selected_columns: List[bool] = [True, True, True,
                                                     True, True, True,
                                                     True, True]
                     ) -> List[Tuple[int, str]]:
    """
    Retrieves account data from the database.
    Args:
        db_path (Path): Path to the SQLite database file.
        selected_columns (List[bool]): List of booleans indicating which
                                       columns to select.
                                       [AccountID, WidgetPosition, AccountName,
                                       AccountNumber, AccountBalance,
                                       AccountDifference, RecordDate,
                                       ChangeDate]
    Return:
        List of tuples containing account data (AccountID, AccountName).
    Raises:
        Error: If the number of selected columns does not match the expected
               number of columns.
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

    cursor.execute(query)
    account_data = cursor.fetchall()
    DatabaseConnection.close_cursor()
    logger.debug("Account data retrieved successfully.")
    logger.debug(f"Account data: {account_data}")
    return account_data


def delete_account(db_path: Path = config.Database.PATH,
                   account_id: Optional[int] = None) -> None:
    """
    Deletes an account from the database.
    Args:
        db_path (Path): Path to the SQLite database file.
        account_id (int): Account ID of the account to delete.
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


def update_account(db_path: Path = config.Database.PATH,
                   account_id: int | None = None,
                   new_values: List[Union[str, float]] = []) -> None:
    """
    Edits an account in the database after verifying that at least one of the
    values is different from the current database values.
    Args:
        db_path (Path): Path to the SQLite database file.
        account_id (int): Account ID of the account to edit.
        new_values (List[str]): List of new values for the columns in the order
                                [new_WidgetPosition, new_AccountName,
                                new_AccountNumber, new_AccountBalance,
                                new_AccountDifference, new_RecordDate,
                                newChangeDate].
                                If an element is an empty string (""), that
                                column will not be updated.
    Raises:
        Error: If no update is needed or if any database error occurs.
    """
    # Define the column names corresponding to the new values.
    columns = ["i8_WidgetPosition", "str_AccountName", "str_AccountNumber",
               "real_AccountBalance", "real_AccountDifference",
               "str_RecordDate", "str_ChangeDate"]

    if len(columns) != len(new_values):
        logger.error("Wrong number of new values provided."
                     f"Expected {len(columns)}, got {len(new_values)}.")
        raise Error("Wrong number of new values provided.",
                    f"Expected {len(columns)}, got {len(new_values)}.")

    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = DatabaseConnection.get_cursor(db_path)
        # Fetch the current record for comparison
        cursor.execute(
            f"SELECT {', '.join(columns)} FROM "
            "tbl_Account WHERE i8_AccountID = ?",
            (account_id,)
        )
        current_record = cursor.fetchone()
        logger.debug("Current record fetched successfully.")
        # Remove the following logging statement.
        print("Current record:", current_record)
        # Check if the record date is new then the one provided
        if current_record is not None:
            if current_record[5] is not None:
                if current_record[5] < new_values[5]:
                    logger.debug("Record date is older than the one in "
                                 "the database.")
                    raise RecordTooOldError("Record date is older than "
                                            "the one in the database.")
        else:
            logger.exception("No account found with the given ID.")
            raise Error("No account found with the given ID.")
    except sqlite3.Error as e:
        logger.exception(f"Error fetching current account data: {e}")
        raise Error(f"Error fetching current account data: {e}")

    # Build the SET part of the SQL query dynamically only for changed values.
    updates: List[str] = []
    parameters: List[str] = []
    for col, new_val, current_val in zip(columns, new_values, current_record):
        if new_val != "":
            try:
                if new_val != current_val:
                    updates.append(f"{col} = ?")
                    parameters.append(new_val)
            except TypeError:
                logger.exception(
                    f"TypeError: Cannot compare {col} with value {new_val}."
                )
                raise Error(
                    f"TypeError: Cannot compare {col} with value {new_val}."
                )
    print("Updates:", updates)
    print("Parameters:", parameters)
    if not updates:
        logger.debug("No changes detected, update aborted.")
        raise NoChangesDetectedError("No changes detected, update aborted.")

    query = (f"UPDATE tbl_Account SET {', '.join(updates)} "
             "WHERE i8_AccountID = ?")
    parameters.append(account_id)

    try:
        cursor.execute(query, parameters)
        conn.commit()
        logger.debug(f"Account with ID {account_id} updated successfully.")
        print("Account edited successfully.")
    except sqlite3.Error as e:
        logger.exception(f"Error editing account: {e}")
        raise Error(f"Error editing account: {e}")
    finally:
        DatabaseConnection.close_cursor()


def add_account_mt940(db_path: Path = config.Database.PATH,
                      name: Optional[str] = None, number: Optional[str] = None,
                      balance: Optional[float] = None,
                      difference: Optional[float] = None,
                      master: Optional[tk.Tk] = None
                      ) -> None:
    """
    Adds an account to the database while importing an MT940 file.

    Args:
        db_path (Path, optional): Path to the SQLite database file.
        name (str, optional): Name of the account.
        number (str): Number of the account.
        balance (float): Balance of the account.
        difference (float, optional): Difference of the account.
        master (tk.Tk, optional): The parent Tkinter window for the dialog.
    Raises:
        Error: If the account number is not provided or if any database error
               occurs.
    """
    if name is None:
        logger.info("Get name of the new account. To add the new account.")
        dialog = NameInputDialog(master)
        master.wait_window(dialog)
        name = dialog.name
        if not name:
            logger.debug("No name provided. Generating random name.")
            name = ''.join(random.choices(string.ascii_letters, k=8))
            logger.debug(f"Random name generated: {name}")
    if number is None:
        logger.error("add_account_mt940: Account number is required.")
        raise Error("add_account_mt940: Account number is required.")
    if balance is None:
        logger.debug("No balance provided. Setting balance to 0.0.")
        balance = 0.0
    if difference is None:
        logger.debug("No difference provided. Setting difference to 0.0.")
        difference = 0.0
    add_account(db_path, name=name, number=number, balance=balance,
                difference=difference)


def add_account(db_path: Path = config.Database.PATH,
                position: int = None, name: str = None, number: str = None,
                balance: float = None, difference: float = None,
                record_date: str = None, change_date: str = None) -> None:
    """
    Adds an account to the database.

    Args:
        db_path (Path, optional): Path to the SQLite database file.
        position (int, optional): Position of the account in the widget.
        name (str, optional): Name of the account.
        number (str, optional): Number of the account.
        balance (float, optional): Balance of the account.
        difference (float, optional): Difference of the account.
        record_date (str, optional): Date of the record in ISO format.
        change_date (str, optional): Date of the change in ISO format.
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


def get_account_id(db_path: Path = config.Database.PATH,
                   data: List = None,
                   supplied_data=[False, False, False, False]) -> int:
    """
    Retrieves the account ID from the database based on the provided filtering
    criteria.

    Args:
        db_path (Path, optional): Path to the SQLite database file.
        data (List): A list of 4 elements in the order [AccountName,
                     AccountNumber, AccountBalance, AccountDifference].
        supplied_data (List of bool): A list of booleans indicating which
                                      corresponding elements of 'data' to use
                                      as filter criteria. Each True value
                                      corresponds to applying an equality
                                      filter for the respective column.
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


def shift_widget_positions(db_path: Path = config.Database.PATH,
                           account_id: int = None, old_pos: int = None,
                           new_pos: int = None) -> None:
    """
    Shifts the widget positions of accounts in the database to make room
    for a new account or to reorder existing accounts.

    Args:
        db_path (Path): Path to the SQLite database file.
        old_pos (int): The current position of the account to be moved.
        new_pos (int): The new position for the account.

    Raises:
        Error: If the old position is invalid or if any database error occurs.
    """
    if old_pos is None or new_pos is None:
        logger.error("Both old_pos and new_pos must be provided.")
        raise Error("Both old_pos and new_pos must be provided.")

    conn = DatabaseConnection.get_connection(db_path)
    cursor = DatabaseConnection.get_cursor(db_path)

    try:
        # Check if the old and new positions are similar
        if old_pos == new_pos:
            logger.warning("Old position is the same as new position.")
            raise NoChangesDetectedError("No changes detected, "
                                         "update aborted.")
        else:
            # Get the current widget position of the account
            cursor.execute(
                "SELECT i8_WidgetPosition FROM tbl_Account "
                "WHERE i8_AccountID = ?",
                (account_id,)
            )
            temp_current_postion = cursor.fetchall()
            logger.debug("Positon in database before change: "
                         f"{temp_current_postion[0][0]}")
            if temp_current_postion[0][0] == new_pos:
                logger.warning("New position is the same as current position.")
                raise NoChangesDetectedError("No changes detected, "
                                             "update aborted.")
            if temp_current_postion[0][0] != old_pos:
                # raise Error("The current position of the account does not "
                #             "match the provided old position.")
                old_pos = temp_current_postion[0][0]
                logger.debug("Old position updated to current position:"
                             f" {old_pos}")
        # Temporarily offset the positions of the accounts
        cursor.execute(
            """
            UPDATE tbl_Account
            SET i8_WidgetPosition = -i8_WidgetPosition - 1000
            WHERE i8_WidgetPosition BETWEEN ? AND ?
            """,
            (min(old_pos, new_pos), max(old_pos, new_pos)),
        )

        if new_pos < old_pos:
            # Moves up -> everything in between +1
            cursor.execute(
                """
                UPDATE tbl_Account
                SET i8_WidgetPosition = -i8_WidgetPosition - 1000 + 1
                WHERE i8_WidgetPosition BETWEEN -? - 1000 AND -? - 1000
                """,
                (old_pos - 1, new_pos),
            )
        elif new_pos > old_pos:
            # Moves down -> everything in between -1
            cursor.execute(
                """
                UPDATE tbl_Account
                SET i8_WidgetPosition = -i8_WidgetPosition - 1000 - 1
                WHERE i8_WidgetPosition BETWEEN -? - 1000 AND -? - 1000
                """,
                (new_pos, old_pos + 1),
            )

        # Set the new position for the account
        cursor.execute(
            """
            UPDATE tbl_Account
            SET i8_WidgetPosition = ?
            WHERE i8_WidgetPosition = -? - 1000
            """,
            (new_pos, old_pos),
        )
        logger.debug("Widget positions shifted successfully.")
    except sqlite3.IntegrityError as e:
        logger.exception(f"IntegrityError: {e}")
        raise Error(f"IntegrityError: {e}")
    except sqlite3.Error as e:
        logger.exception(f"Error shifting widget positions: {e}")
        raise Error(f"Error shifting widget positions: {e}")
    finally:
        conn.commit()
        DatabaseConnection.close_cursor()
