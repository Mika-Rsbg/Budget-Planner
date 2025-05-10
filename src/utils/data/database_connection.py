import sqlite3
from pathlib import Path
from typing import Optional
import logging
import config


logger = logging.getLogger(__name__)


class DatabaseConnection:
    _instance: Optional[sqlite3.Connection] = None
    _cursor: Optional[sqlite3.Cursor] = None

    @staticmethod
    def get_connection(
        db_path: Path = config.Database.PATH
    ) -> sqlite3.Connection:
        """
        Returns a singleton instance of the database connection.
        If the connection does not exist, it creates a new one.
        If the connection already exists, it returns the existing one.

        Args:
            db_path (Path): The path to the database file.
        Returns:
            sqlite3.Connection: The database connection instance.
        """
        if DatabaseConnection._instance is None:
            DatabaseConnection._instance = sqlite3.connect(db_path)
            logging.info(f"Database connection created: {db_path}")
        return DatabaseConnection._instance

    @staticmethod
    def get_cursor(
        db_path: Path = config.Database.PATH
    ) -> sqlite3.Cursor:
        """
        Returns a singleton instance of the database cursor.
        If the cursor does not exist, it creates a new one.
        If the cursor already exists, it returns the existing one.

        Args:
            db_path (Path): The path to the database file.
        Returns:
            sqlite3.Cursor: The database cursor instance.
        """
        if DatabaseConnection._cursor is None:
            DatabaseConnection._cursor = DatabaseConnection.get_connection(
                db_path
            ).cursor()
            logging.debug(f"Database cursor created: {db_path}")
        logging.debug("Database cursor retrieved.")
        return DatabaseConnection._cursor

    def close_cursor() -> None:
        """
        Closes the database cursor if it exists.
        Sets the cursor instance to None after closing.
        """
        if DatabaseConnection._cursor:
            DatabaseConnection._cursor.close()
            DatabaseConnection._cursor = None
            logger.debug("Database cursor closed.")

    @staticmethod
    def close_connection() -> None:
        """
        Closes the database connection if it exists.
        Sets the connection instance to None after closing.
        """
        if DatabaseConnection._instance:
            DatabaseConnection.close_cursor()
            DatabaseConnection._instance.close()
            DatabaseConnection._instance = None
            logger.info("Database connection closed.")
