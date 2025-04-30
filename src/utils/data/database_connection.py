import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseConnection:
    _instance: Optional[sqlite3.Connection] = None
    _cursor: Optional[sqlite3.Cursor] = None

    @staticmethod
    def get_connection(db_path: Path) -> sqlite3.Connection:
        if DatabaseConnection._instance is None:
            DatabaseConnection._instance = sqlite3.connect(db_path)
        return DatabaseConnection._instance

    @staticmethod
    def get_cursor(db_path: Path) -> sqlite3.Cursor:
        if DatabaseConnection._cursor is None:
            DatabaseConnection._cursor = DatabaseConnection.get_connection(
                db_path
            ).cursor()
        return DatabaseConnection._cursor

    def close_cursor() -> None:
        if DatabaseConnection._cursor:
            DatabaseConnection._cursor.close()
            DatabaseConnection._cursor = None

    @staticmethod
    def close_connection():
        if DatabaseConnection._instance:
            DatabaseConnection.close_cursor()
            DatabaseConnection._instance.close()
            DatabaseConnection._instance = None
