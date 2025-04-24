from pathlib import Path


class Database:
    """Database configuration class."""
    PATH = Path(__file__).resolve().parent.parent / 'data' / 'database.db'
    """Path to the database file."""
    CASH_ENABLED = True
    """Flag to enable or disable cash functionality."""
    # TABLES = {
    #     'account': {
    #         'name': 'account',
    #         'columns': {
    #             'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    #             'name': 'TEXT NOT NULL',
    #             'number': 'TEXT NOT NULL',
    #             'balance': 'REAL NOT NULL',
    #             'difference': 'REAL NOT NULL'
    #         }
    #     },
    #     'cash': {
    #         'name': 'cash',
    #         'columns': {
    #             'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    #             'amount': 'REAL NOT NULL',
    #             'date': 'TEXT NOT NULL'
    #         }
    #     }
    # }
