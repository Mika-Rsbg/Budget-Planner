import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseConnection:
    _instance: Optional[sqlite3.Connection] = None

    @staticmethod
    def get_connection(db_path: Path) -> sqlite3.Connection:
        if DatabaseConnection._instance is None:
            DatabaseConnection._instance = sqlite3.connect(db_path)
        return DatabaseConnection._instance

    @staticmethod
    def close_connection():
        if DatabaseConnection._instance:
            DatabaseConnection._instance.close()
            DatabaseConnection._instance = None
