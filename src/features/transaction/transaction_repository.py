import sqlite3
from pathlib import Path
import logging
from core.database.connection import DatabaseConnection
import config
from models.transaction.entity import Transaction
from models.transaction.imported_view import ImportedTransactionView


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


def get_transaction_id(transaction: Transaction | ImportedTransactionView,
                       db_path: Path = config.Database.PATH) -> int | None:
    """Find the ID of an existing transaction based on its details.

    Args:
        transaction (Transaction): Transaction object to be checked.
        db_path (Path, optional):  Path to the SQLite database file.

    Raises:
        Error: If there is an error getting the database cursor
            or if there is any error during the SQL-Query.

    Returns:
        int | None: The ID of the existing transaction, or None if not found.
    """

    try:
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        logger.exception(f"Error connecting to database: {e}")
        raise Error(f"Error connecting to database: {e}")

    try:
        # cursor.execute(
        #     '''
        #     SELECT i8_TransactionID
        #     FROM tbl_Transaction
        #     WHERE i8_AccountID=?
        #       AND str_Date=?
        #       AND str_Bookingdate=?
        #       AND i8_TransactionTypeID=?
        #       AND real_Amount=?
        #       AND str_Purpose=?
        #       AND i8_CounterpartyID=?
        #       AND i8_CategoryID=?;
        #     ''',
        #     (
        #         transaction.account_id,
        #         transaction.date.isoformat(),
        #         transaction.booking_date.isoformat(),
        #         transaction.transaction_type_id,
        #         transaction.amount,
        #         transaction.purpose,
        #         transaction.counterparty_id,
        #         transaction.category_id
        #     )
        # )
        cursor.execute(
            '''
            SELECT i8_TransactionID
            FROM tbl_Transaction
            WHERE i8_AccountID=?
              AND str_Date=?
              AND i8_TransactionTypeID=?
              AND real_Amount=?
              AND str_Purpose=?
              AND i8_CounterpartyID=?
              AND i8_CategoryID=?;
            ''',
            (
                transaction.account_id,
                transaction.date.isoformat(),
                transaction.transaction_type_id,
                transaction.amount,
                transaction.purpose,
                transaction.counterparty_id,
                transaction.category_id
            )
        )
        # TODO: add booking_date to query
        # bookingdate always has the year 2020 in the database
        # probably because of a mistake during the import

        row = cursor.fetchone()
        if row:
            return row[0]  # transaction_id

    except sqlite3.Error as e:
        logger.error(f"Error checking for existing transaction: {e}")
        raise Error(f"Error checking for existing transaction: {e}")

    return None


def transaction_exists(transaction: Transaction | ImportedTransactionView,
                       db_path: Path = config.Database.PATH) -> bool:
    """Check if a transaction with the same details
    (except displayed_name and user_comments) exists

    Args:
        transaction (Transaction): Transaction object to be checked.
        db_path (Path, optional):  Path to the SQLite database file.

    Raises:
        Error: If there is an error getting the database cursor
            or if there is any error during the SQL-Query.

    Returns:
        bool: "True" if transacation already exists.
    """
    return get_transaction_id(transaction, db_path) is not None


def add_transaction(data: Transaction | ImportedTransactionView,
                    db_path: Path = config.Database.PATH) -> None:
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
    # TODO: update docs
    account_id = data.account_id
    date = data.date.isoformat()
    booking_date = data.booking_date.isoformat()
    tt_id = data.transaction_type_id
    amount = data.amount
    purpose = data.purpose
    counterparty_id = data.counterparty_id
    category_id = data.category_id
    user_comments = data.user_comments
    displayed_name = data.displayed_name

    try:
        conn = DatabaseConnection.get_connection(db_path)
        cursor = DatabaseConnection.get_cursor(db_path)
    except sqlite3.Error as e:
        logger.exception(f"Error connecting to database: {e}")
        raise Error(f"Error connecting to database: {e}")

    if transaction_exists(data, db_path):
        raise AlreadyExistsError("Transaction already exists.")

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
                booking_date,
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
