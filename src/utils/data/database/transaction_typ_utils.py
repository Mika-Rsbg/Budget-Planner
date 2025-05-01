import sqlite3
from pathlib import Path
from utils.data.database_connection import DatabaseConnection
import config


class Error(Exception):
    """General exception class for database errors."""
    pass


def add_transaction_typ(db_path: Path = config.Database.PATH,
                        name: str = None, number: str = None) -> None:
    """
    Adds a transaction type to the database.

    Args:
        db_path (Path): Path to the SQLite database file.
        name (str): Name of the transaction type.
        number (str): Number of the transaction type.
    Raises:
        Error: If an error occurs during the database operation.
    """
    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        raise Error(f"Error connecting to database: {e}")

    try:
        cursor.execute(
            '''
            INSERT INTO tbl_TransactionTyp (
                str_TransactionTypName,
                str_TransactionTypNumber
            ) VALUES (?, ?);
            ''',
            (name, number)
        )
        conn.commit()
        print("Transaction type added successfully.")
    except sqlite3.Error as e:
        raise Error(f"Error inserting data: {e}")
    finally:
        DatabaseConnection.close_cursor()


def get_transaction_typ_id(db_path: Path = config.Database.PATH,
                           data: list = ["", ""],
                           supplied_data=[False, False]) -> int:
    """
    Retrieves the transaction type ID from the database based on the provided
    data.

    Args:
        db_path (Path): Path to the SQLite database file.
        data (list): A list containing [Name, Number].
        supplied_data (list of bool): A list indicating which elements in data
                                      should be used in the query.
                                      E.g., [True, False] uses only the Name.

    Returns:
        int: The transaction type ID.

    Raises:
        Error: If there is a database error.
    """
    try:
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        raise Error(f"Error connecting to database: {e}")

    try:
        query = "SELECT i8_TransactionTypID FROM tbl_TransactionTyp WHERE "
        params = []

        conditions = []
        if supplied_data[0]:
            conditions.append("str_TransactionTypName = ?")
            params.append(data[0])
        if supplied_data[1]:
            conditions.append("str_TransactionTypNumber = ?")
            params.append(data[1])

        if not conditions:
            raise Error("No query parameters provided.")

        query += " AND ".join(conditions) + ";"

        cursor.execute(query, params)
        row = cursor.fetchone()
        if row is None:
            raise Error("No matching transaction type found.")
        return row[0]
    except sqlite3.Error as e:
        raise Error(f"Error querying data: {e}")
    finally:
        DatabaseConnection.close_cursor()
