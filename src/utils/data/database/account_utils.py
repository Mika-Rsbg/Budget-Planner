import sqlite3
from pathlib import Path
import config


class DatabaseAccountError(Exception):
    """Allgemeine Ausnahmeklasse für Datenbankfehler."""
    pass


def get_account_data(db_location: Path = config.Database.PATH,
                     selected_columns: list[bool] = [True, True, True,
                                                     True, True]
                     ) -> list[tuple]:
    """
    Retrieves account data from the database.
    Args:
        db_location (Path): Path to the SQLite database file. Def
        selected_columns (list[bool]): List of booleans indicating which
                                       columns to select.
                                       [AccountID, AccountName, AccountNumber,
                                       AccountBalance, AccountDifference]
    Return:
        List of tuples containing account data (AccountID, AccountName).
    """
    conn = sqlite3.connect(db_location)
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
    conn.close()
    return account_data


def delete_account(db_location: Path = config.Database.PATH,
                   account_id: int = None) -> None:
    """
    Deletes an account from the database.
    Args:
        db_location (Path): Path to the SQLite database file.
        account_id (int): Account ID of the account to delete.
    """
    try:
        conn = sqlite3.connect(db_location)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        raise DatabaseAccountError(f"Error connecting to database: {e}")
    try:
        cursor.execute('''DELETE FROM tbl_Account WHERE i8_AccountID = ?''',
                       (account_id,))
        conn.commit()
        print("Account deleted successfully.")
    except sqlite3.Error as e:
        raise DatabaseAccountError(f"Error deleting account: {e}")
    cursor.close()
    conn.close()


def edit_account(db_location: Path = config.Database.PATH,
                 account_id: int = None,
                 new_values: list[str] = None) -> None:
    """
    Edits an account in the database.
    Args:
        db_location (Path): Path to the SQLite database file.
        account_id (int): Account ID of the account to edit.
        new_values (list[str]): List of new values for the columns in the order
                                [new_AccountName, new_AccountNumber,
                                new_AccountBalance, new_AccountDifference].
                                If an element is an empty string (""), that
                                column will not be updated.
    """
    if new_values is None or len(new_values) != 4:
        print("Error: new_values must be a list of 4 elements.")
        return

    # Define the column names corresponding to the new values.
    columns = ["str_AccountName", "str_AccountNumber", "real_AccountBalance",
               "real_AccountDifference"]
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
        conn = sqlite3.connect(db_location)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        raise DatabaseAccountError(f"Error connecting to database: {e}")

    try:
        cursor.execute(query, parameters)
        conn.commit()
        print("Account edited successfully.")
    except sqlite3.Error as e:
        raise DatabaseAccountError(f"Error editing account: {e}")
    finally:
        cursor.close()
        conn.close()


def create_account(db_location: Path = config.Database.PATH,
                   name: str = None, number: str = None,
                   balance: float = None, difference: float = None) -> None:
    try:
        conn = sqlite3.connect(db_location)
        cursor = conn.cursor()
    except sqlite3.Error as e:
        raise DatabaseAccountError(f"Error connecting to database: {e}")

    try:
        cursor.execute('''
            INSERT INTO tbl_Account (str_AccountName, str_AccountNumber,
            real_AccountBalance, real_AccountDifference)
            VALUES (?, ?, ?, ?)
        ''', (name, number, balance, difference))
        conn.commit()
        print("Account created successfully.")
    except sqlite3.Error as e:
        raise DatabaseAccountError(f"Error creating account: {e}")


if __name__ == '__main__':
    print(get_account_data(config.Database.PATH, [False, True, False,
                                                  False, False]))
