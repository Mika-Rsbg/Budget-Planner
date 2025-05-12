import sqlite3
from pathlib import Path
import logging
from utils.data.database_connection import DatabaseConnection
import config


logger = logging.getLogger(__name__)


class Error(Exception):
    """General exception class for database errors."""
    pass


class AlreadyExistsError(Exception):
    """Exception raised when a record already exists."""
    pass


def get_transaction_dat(db_path: Path = config.Database.PATH):
    pass


def delete_transaction(db_path: Path = config.Database.PATH):
    pass


def edit_transaction(db_path: Path = config.Database.PATH):
    pass


def add_transaction(db_path: Path = config.Database.PATH,
                    data: tuple = None):
    """
    Adds a transaction to the database after checking for duplicates.

    Args:
        db_path (Path, optional): Path to the SQLite database file.
        data (tuple, optional): A tuple containing the transaction data.

    Raises:
        Error: If an error occurs during the database operation or if a
            duplicate is found.
        AlreadyExistsError: If a transaction with the same details already
            exists in the database.
    """
    (account_id, date, bookingdate, tt_id, amount,
     purpose, counterparty_id, category_id, user_comments,
     displayed_name) = data

    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        logger.exception(f"Error connecting to database: {e}")
        raise Error(f"Error connecting to database: {e}")

    try:
        # Check if a transaction with the same details
        # (except displayed_name and user_comments) exists
        cursor.execute(
            '''
            SELECT 1 FROM tbl_Transaction
            WHERE i8_AccountID=?
              AND str_Date=?
              AND str_Bookingdate=?
              AND i8_TransactionTypeID=?
              AND real_Amount=?
              AND str_Purpose=?
              AND i8_CounterpartyID=?
              AND i8_CategoryID=?;
            ''',
            (account_id, date, bookingdate, tt_id, amount, purpose,
             counterparty_id, category_id)
        )
        if cursor.fetchone():
            logger.debug("Transaction already exists.")
            raise AlreadyExistsError("Transaction already exists.")
    except sqlite3.Error as e:
        logger.error(f"Error checking for duplicate transaction: {e}")
        raise Error(f"Error checking for duplicate transaction: {e}")

    try:
        cursor.execute(
            '''
            INSERT INTO tbl_Transaction (
                i8_AccountID,
                str_Date,
                str_Bookingdate,
                i8_TransactionTypeID,
                real_Amount,
                str_Purpose,
                i8_CounterpartyID,
                i8_CategoryID,
                str_UserComments,
                str_DisplayedName
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''',
            (
                account_id,
                date,
                bookingdate,
                tt_id,
                amount,
                purpose,
                counterparty_id,
                category_id,
                user_comments,
                displayed_name
            )
        )
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error creating transaction: {e}")
        raise Error(f"Error creating transaction: {e}")
    finally:
        DatabaseConnection.close_cursor()
