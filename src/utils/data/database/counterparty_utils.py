import sqlite3
from pathlib import Path
from utils.data.database_connection import DatabaseConnection
import config


class Error(Exception):
    """""General exception class for database errors."""
    pass


def add_counterparty(db_path: Path = config.Database.PATH,
                     name: str = None, number: str = None) -> None:
    """
    Adds a counterparty to the database.

    Args:
        db_path (Path):  Path to the SQLite database file.
        name (str): Name of the counterparty.
        number (str): Account Number of the counterparty.
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
            INSERT INTO tbl_Counterparty (
                str_CounterpartyName,
                str_CounterpartyNumber
            ) VALUES (?, ?);
            ''',
            (name, number)
        )
        conn.commit()
        print("Counterparty added successfully.")
    except sqlite3.Error as e:
        raise Error(f"Error inserting data: {e}")
    finally:
        DatabaseConnection.close_cursor()


def get_counterparty_id(db_path: Path = config.Database.PATH,
                        data: list = ["", ""],
                        supplied_data=[False, False]) -> int:
    """
    Retrieves the ID of a counterparty from the database based on supplied
    search criteria.

    The search is performed using the provided 'data' list, which represents
    [Name, Number].
    The 'supplied_data' list should contain booleans indicating which fields
    in 'data' are valid.

    Args:
        db_path (Path): Path to the SQLite database file.
        data (list): A list containing [Name, Number] of the counterparty.
        supplied_data (list): A list of booleans indicating which elements in
                              'data' are supplied.

    Returns:
        (int or None): The counterparty's ID if found; otherwise, None.

    Raises:
        Error: If there is a database error.
    """
    try:
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        raise Error(f"Error connecting to database: {e}")

    # Build the WHERE clause based on which fields are supplied
    conditions = []
    values = []
    if supplied_data[0]:
        conditions.append("str_CounterpartyName = ?")
        values.append(data[0])
    if supplied_data[1]:
        conditions.append("str_CounterpartyNumber = ?")
        values.append(data[1])

    # If no criteria are provided, return None
    if not conditions:
        return None

    query = ("SELECT i8_CounterpartyID FROM tbl_Counterparty WHERE " +
             " AND ".join(conditions) + " LIMIT 1;")

    try:
        cursor.execute(query, tuple(values))
        result = cursor.fetchone()
    except sqlite3.Error as e:
        raise Error(f"Error querying data: {e}")
    finally:
        DatabaseConnection.close_cursor()

    if result:
        return result[0]
    else:
        raise Error("No matching counterparty found.")
