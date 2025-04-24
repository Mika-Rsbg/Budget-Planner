import tkinter as tk
import random
import string
import sqlite3
from pathlib import Path
from gui.accountpage.name_input_page import NameInputDialog
from utils.data.database_connection import DatabaseConnection
import config


class Error(Exception):
    """Allgemeine Ausnahmeklasse für Datenbankfehler."""
    pass


def get_account_data(db_path: Path = config.Database.PATH,
                     selected_columns: list[bool] = [True, True, True,
                                                     True, True]
                     ) -> list[tuple]:
    """
    Retrieves account data from the database.
    Args:
        db_path (Path): Path to the SQLite database file.
        selected_columns (list[bool]): List of booleans indicating which
                                       columns to select.
                                       [AccountID, AccountName, AccountNumber,
                                       AccountBalance, AccountDifference]
    Return:
        List of tuples containing account data (AccountID, AccountName).
    """
    conn = DatabaseConnection.get_connection(db_path)
    cursor = conn.cursor()
    columns = ["i8_AccountID", "str_AccountName", "str_AccountNumber",
               "real_AccountBalance", "real_AccountDifference"]
    query = 'SELECT '
    for i, col in enumerate(columns):
        if selected_columns[i]:
            query += f'{col}, '
    query = query[:-2] + ' FROM tbl_Account'

    cursor.execute(query)
    account_data = cursor.fetchall()
    return account_data


def delete_account(db_path: Path = config.Database.PATH,
                   account_id: int = None) -> None:
    """
    Deletes an account from the database.
    Args:
        db_path (Path): Path to the SQLite database file.
        account_id (int): Account ID of the account to delete.
    """
    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        raise Error(f"Error connecting to database: {e}")
    try:
        cursor.execute(
            '''
            DELETE FROM tbl_Account WHERE i8_AccountID = ?
            ''',
            account_id,)

        conn.commit()
        print("Account deleted successfully.")
    except sqlite3.Error as e:
        raise Error(f"Error deleting account: {e}")
    cursor.close()


def edit_account(db_path: Path = config.Database.PATH,
                 account_id: int = None,
                 new_values: list[str] = None) -> None:
    """
    Edits an account in the database.
    Args:
        db_path (Path): Path to the SQLite database file.
        account_id (int): Account ID of the account to edit.
        new_values (list[str]): List of new values for the columns in the order
                                [new_AccountName, new_AccountNumber,
                                new_AccountBalance, new_AccountDifference,
                                new_RecordDate, newChangeDate].
                                If an element is an empty string (""), that
                                column will not be updated.
    """
    if new_values is None or len(new_values) != 6:
        print("Error: new_values must be a list of 6 elements.")
        return

    # Define the column names corresponding to the new values.
    columns = ["str_AccountName", "str_AccountNumber", "real_AccountBalance",
               "real_AccountDifference", "i8_RecordDate", "i8_ChangeDate"]
    # Build the SET part of the SQL query dynamically.
    updates = []
    parameters = []
    for col, new_val in zip(columns, new_values):
        if new_val != "":
            updates.append(f"{col} = ?")
            parameters.append(new_val)

    if not updates:
        print("No values to update.")
        return

    query = (f"UPDATE tbl_Account SET {', '.join(updates)}"
             "WHERE i8_AccountID = ?")
    parameters.append(account_id)

    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        raise Error(f"Error connecting to database: {e}")

    try:
        cursor.execute(query, parameters)
        conn.commit()
        print("Account edited successfully.")
    except sqlite3.Error as e:
        raise Error(f"Error editing account: {e}")
    finally:
        cursor.close()
        DatabaseConnection.close_connection()


def add_account_mt940(db_path: Path = config.Database.PATH,
                      name: str = None, number: str = None,
                      balance: float = None, difference: float = None,
                      master: tk.Tk = None) -> None:
    """
    Adds an account to the database while importing an MT940 file.

    Args:
        db_path (Path, optional): Path to the SQLite database file.
        name (str, optional): Name of the account.
        number (str): Number of the account.
        balance (float): Balance of the account.
        difference (float, optional): Difference of the account.
    """
    if name is None:
        dialog = NameInputDialog(master)
        master.wait_window(dialog)
        name = dialog.name
        if not name:
            print("No name provided. Account creation cancelled.")
            print("Random Name will be used.")
            name = ''.join(random.choices(string.ascii_letters, k=8))
            print("Random name generated:", name)
    if number is None:
        raise Error("add_account_mt940: Account number is required.")
    if balance is None:
        print("No balance provided. Setting balance to 0.0.")
        balance = 0.0
    if difference is None:
        print("No difference provided. Setting difference to 0.0.")
        difference = 0.0
    add_account(db_path, name, number, balance, difference)


def add_account(db_path: Path = config.Database.PATH,
                name: str = None, number: str = None,
                balance: float = None, difference: float = None) -> None:
    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        raise Error(f"Error connecting to database: {e}")

    try:
        cursor.execute(
            '''
            INSERT INTO tbl_Account (str_AccountName, str_AccountNumber,
            real_AccountBalance, real_AccountDifference)
            VALUES (?, ?, ?, ?)
            ''',
            (name, number, balance, difference))
        conn.commit()
        print("Account created successfully.")
    except sqlite3.Error as e:
        raise Error(f"Error creating account: {e}")


def get_account_id(db_path: Path = config.Database.PATH,
                   data=None,
                   supplied_data=[False, False, False, False]) -> int:
    """
    Retrieves the account ID from the database based on the provided filtering
    criteria.

    Args:
        db_path (Path, optional): Path to the SQLite database file.
        data (list): A list of 4 elements in the order [AccountName,
                     AccountNumber, AccountBalance, AccountDifference].
        supplied_data (list of bool): A list of booleans indicating which
                                      corresponding elements of 'data' to use
                                      as filter criteria. Each True value
                                      corresponds to applying an equality
                                      filter for the respective column.
    Returns:
        int: The account ID (i8_AccountID) of the account matching the
             provided criteria.
    Raises:
        DatabaseAccountError: If 'data' is None or does not contain exactly 4
                              elements.
        DatabaseAccountError: If no filtering criteria are provided
                              (i.e., all elements in supplied_data are False).
        DatabaseAccountError: If no matching account is found in the database.
        DatabaseAccountError: If an error occurs during the database query.
    """
    if data is None or len(data) != 4:
        raise Error("Data must be provided as a list"
                    "of 4 elements: [Name, Number, Balance, Difference].")
    columns = ["str_AccountName", "str_AccountNumber", "real_AccountBalance",
               "real_AccountDifference"]
    conditions = []
    parameters = []
    for col, should_filter, value in zip(columns, supplied_data, data):
        if should_filter:
            conditions.append(f"{col} = ?")
            parameters.append(value)
    if not conditions:
        raise Error("No criteria provided to query account ID.")
    query = f"SELECT i8_AccountID FROM tbl_Account WHERE {
        ' AND '.join(conditions)}"

    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        result = cursor.fetchone()
        if result is None:
            raise Error("No matching account found.")
        return result[0]
    except sqlite3.Error as e:
        raise Error(f"Error querying account ID: {e}")
    finally:
        cursor.close()
        DatabaseConnection.close_connection()
