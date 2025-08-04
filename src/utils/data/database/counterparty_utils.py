import sqlite3
from pathlib import Path
import logging
from typing import List, Tuple, Union, Optional
from utils.data.database_connection import DatabaseConnection
import config


logger = logging.getLogger(__name__)


class Error(Exception):
    """General exception class for database errors."""
    pass


def add_counterparty(name: str, number: str,
                     db_path: Path = config.Database.PATH) -> None:
    """
    Adds a counterparty to the database.

    Args:
        name (str): Name of the counterparty.
        number (str): Account Number of the counterparty.
        db_path (Path):  Path to the SQLite database file.
    Raises:
        Error: If an error occurs during the database operation.
    """
    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
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
        logger.debug("Counterparty added successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error inserting data: {e}")
        raise Error(f"Error inserting data: {e}")
    finally:
        DatabaseConnection.close_cursor()


def get_counterparty_id(data: List[Union[str, None]],
                        supplied_data: List[bool] = [False, False],
                        db_path: Path = config.Database.PATH) -> Optional[int]:
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
        logger.error(f"Error connecting to database: {e}")
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
        logger.error(f"Error querying data: {e}")
        raise Error(f"Error querying data: {e}")
    finally:
        DatabaseConnection.close_cursor()

    if result:
        return result[0]
    else:
        logger.warning("No matching counterparty found.")
        raise Error("No matching counterparty found.")


def get_counterparty_data(selected_columns: List[bool] = [True, True, True],
                          db_path: Path = config.Database.PATH
                          ) -> List[Tuple[Union[str, int], ...]]:
    """
    Retrieves counterparty data from the database based on selected columns.
    Args:
        selected_columns (list): A list of booleans indicating which columns
            to retrieve. The order is:
                [i8_CounterpartyID (int), str_CounterpartyName (str),
                 str_CounterpartyNumber (str)].
        db_path (Path): Path to the SQLite database file.
    Returns:
        (list): A list of tuples containing the counterparty data.
    Raises:
        Error: If there is a database error.
    """
    try:
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise Error(f"Error connecting to database: {e}")

    columns = ["i8_CounterpartyID", "str_CounterpartyName",
               "str_CounterpartyNumber"]

    if len(columns) != len(selected_columns):
        logger.error("Wrong number of selected columns provided."
                     f"Expected {len(columns)}, got {len(selected_columns)}.")
        raise Error("Wrong number of values provided."
                    f"Expected {len(columns)}, got {len(selected_columns)}.")

    query = 'SELECT '
    for i, col in enumerate(columns):
        if selected_columns[i]:
            query += f'{col}, '
    query = query[:-2] + ' FROM tbl_Counterparty'

    try:
        cursor.execute(query)
        counterparty_data = cursor.fetchall()
        logger.debug("Counterparty data retrieved successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error querying data: {e}")
        raise Error(f"Error querying data: {e}")
    finally:
        DatabaseConnection.close_cursor()
    if not counterparty_data:
        logger.warning("No counterparty data found.")
    return counterparty_data
