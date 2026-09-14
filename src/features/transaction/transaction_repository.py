import sqlite3
from pathlib import Path
import logging
from typing import List, Optional
from core.database.connection import DatabaseConnection
import config
from models.transaction.entity import Transaction
from models.transaction.import_view import TransactionImportView


logger = logging.getLogger(__name__)


class Error(Exception):
    """General exception class for database errors."""
    pass


class AlreadyExistsError(Exception):
    """Exception raised when a record already exists."""
    pass


def delete_transaction(db_path: Path = config.Database.PATH):
    pass


def edit_transaction(db_path: Path = config.Database.PATH):
    pass


def get_transaction_data(
        db_path: Path = config.Database.PATH) -> List[Transaction]:
    """Retrieve all transaction records from the database.

    Args:
        db_path (Path): Path to the SQLite database file.

    Returns:
        list[Transaction]: The transactions found in the database.

    Raises:
        Error: If an error occurs while querying the database.
    """
    cursor = DatabaseConnection.get_cursor(db_path)

    try:
        cursor.execute(
            """
            SELECT i8_TransactionID,
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
            FROM tbl_Transaction
            """
        )
        raw_transaction_data = cursor.fetchall()
        logger.debug("Transaction data retrieved successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error querying data: {e}")
        raise Error(f"Error querying data: {e}")
    finally:
        DatabaseConnection.close_cursor()

    transaction_data = []
    for transaction in raw_transaction_data:
        transaction_data.append(
            Transaction(
                transaction_id=transaction[0],
                account_id=transaction[1],
                date=__import__("datetime").date.fromisoformat(transaction[2]),
                booking_date=__import__("datetime").date.fromisoformat(
                    transaction[3]
                ),
                transaction_type_id=transaction[4],
                amount=transaction[5],
                purpose=transaction[6],
                counterparty_id=transaction[7],
                category_id=transaction[8],
                user_comments=transaction[9],
                displayed_name=transaction[10],
            )
        )

    if not transaction_data:
        logger.warning("No transaction data found.")

    return transaction_data


def get_transaction_by_id(
    transaction_id: int,
    db_path: Path = config.Database.PATH
) -> Optional[Transaction]:
    """
    Returns the data of a specific transaction identified by its TransactionID.

    Args:
        transaction_id (int): ID of the transaction.

    Returns:
        Optional[Transaction]:
            The account data if found, otherwise None.
    """
    transaction_data = get_transaction_data(db_path=db_path)

    for transaction in transaction_data:
        if transaction.transaction_id == transaction_id:
            return transaction

    return None


def get_transaction_id(transaction: Transaction | TransactionImportView,
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


def get_transaction_id_gui(transaction: Transaction | TransactionImportView,
                           db_path: Path = config.Database.PATH) -> int | None:
    """Return the database ID of an existing transaction
    for the Import workflow.

    This is a relaxed duplicate check used by the GUI import flow. It matches a
    transaction by ``account``, ``date``, ``transaction type``, ``amount``,
    ``purpose`` and ``counterparty``.
    The returned ID can be used to avoid creating duplicate rows in
    the database.

    Args:
        transaction (Transaction | TransactionImportView):
            Transaction to compare against the database.
        db_path (Path, optional): Path to the SQLite database. Defaults to the
            configured application database path.

    Raises:
        Error: If the database connection cannot be opened
            or the SQL query fails.

    Returns:
        int | None:
            The matching transaction ID,
            or None if no matching record is found.
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
        #         transaction.booking_date.isoformat(), # Entfernt
        #         transaction.transaction_type_id,
        #         transaction.amount,
        #         transaction.purpose,
        #         transaction.counterparty_id,
        #         transaction.category_id # Entfernt
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
            ''',
            (
                transaction.account_id,
                transaction.date.isoformat(),
                transaction.transaction_type_id,
                transaction.amount,
                transaction.purpose,
                transaction.counterparty_id,
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


def transaction_exists(transaction: Transaction | TransactionImportView,
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


def add_transaction(data: Transaction | TransactionImportView,
                    db_path: Path = config.Database.PATH) -> None:
    """
    Insert a transaction into the database after checking for duplicates.

    The duplicate check compares all transaction fields except
    ``displayed_name`` and ``user_comments``.

    Args:
        data (Transaction | TransactionImportView):
            Transaction payload to save.
        db_path (Path, optional): Path to the SQLite database file.

    Raises:
        sqlite3.Error: If the database connection or insert fails.
        AlreadyExistsError: If an equivalent transaction already exists.
        Error: If the repository cannot access the database or persist the
            record.
    """
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
